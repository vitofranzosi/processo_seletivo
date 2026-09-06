# Modelo de dados — Publicação de Resultados

Três tabelas, num app novo (T-001). Nenhuma alteração em tabela existente (FR-070).

A separação entre o que é divulgado e o que é individual é **de tabela**, e não de chave dentro de
um mesmo registro (T-010). É o que permite à leitura pública não ter caminho para o dado individual,
em vez de tê-lo e confiar que ninguém o percorre.

---

## `PublicacaoResultado`

O ato institucional de divulgação. Append-only nas três camadas: `save`/`delete` recusam, a trigger
recusa e o papel de runtime não tem `UPDATE` (T-011).

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `edital` | FK → `processos.Edital`, PROTECT | O contêiner normativo, como em `AtoDeOrdenacao` |
| `ato` | FK → `classificacao.AtoDeOrdenacao`, PROTECT | O ato publicado (FR-001). `PROTECT` porque a origem não pode desaparecer sob a publicação |
| `perfil_id` | UUID | Identidade publicada, não FK para elaboração — mesma razão da 015 |
| `marco_id` | UUID | idem; junto com `perfil_id`, é o eixo da cadeia |
| `natureza` | CharField(20), choices | `PRELIMINAR` \| `DEFINITIVA` (T-012) |
| `publicacao_anterior` | FK → `self`, null, PROTECT | A cadeia de sucessão (T-002) |
| `conteudo_publico` | BinaryField | Bytes canônicos **do que foi divulgado**, e nada além (T-003) |
| `conteudo_publico_hash` | CharField(64), indexado | `canonical_sha256` dos mesmos bytes |
| `publicado_por` | CharField(255) | O sujeito autenticado (FR-027) |
| `publicado_em` | DateTimeField | O instante do ato (FR-028) |
| `signatario_id` | UUID | Do catálogo de autoridades, nunca digitado (FR-029) |
| `signatario_nome` | CharField(255) | Persistido: retirar a autoridade do catálogo não altera ato praticado |
| `signatario_cargo` | CharField(255) | idem |

**Constraints**

```text
uq_publicacao_raiz_por_marco     UNIQUE (edital, perfil_id, marco_id)
                                 WHERE publicacao_anterior IS NULL
uq_publicacao_sucessora_unica    UNIQUE (publicacao_anterior)
                                 WHERE publicacao_anterior IS NOT NULL
uq_publicacao_por_ato_natureza   UNIQUE (ato, natureza)
```

A terceira é a resposta à pergunta "o mesmo ato pode ser publicado duas vezes?" (D-007, FR-039):
**pode, uma vez por natureza**. Um preliminar que ninguém contestou vira definitivo sem que exista
ato novo a emitir; exigir a emissão de um sucessor idêntico faria a 015 registrar uma sucessão que
não sucedeu nada. A mesma natureza duas vezes sobre o mesmo ato é duplicidade, e o banco a recusa —
o que dá ao cenário das duas abas uma garantia de banco, e não só de idempotência (T-005).

**Trigger `publicacao_resultado_coerente`** — no `INSERT`, confere contra a linha referenciada, no
molde de `resultado_etapa_coerente`:

- o predecessor pertence ao mesmo `(edital, perfil_id, marco_id)`;
- `PRELIMINAR` não sucede `DEFINITIVA` — a ordem entre naturezas tem sentido único.

O predecessor é outra linha, e por isso a verificação é trigger e não `CheckConstraint`. É a mesma
situação que a 013 resolveu do mesmo jeito.

**Sem coluna de vigência.** Vigente é `sucessoras__isnull=True` (T-002). **Sem coluna de estado**: o
agregado não tem ciclo de vida (FR-046).

**Sem `motivo_da_sucessao`.** A 015 o exige porque suceder um ato de ordenação é decisão da comissão
sobre o mérito. Aqui a sucessão é consequência, e o motivo já está no `motivo_da_sucessao` do ato
que a origina. Duplicá-lo criaria dois lugares para a mesma justificativa.

---

## `SituacaoDivulgada`

A situação de **uma** pessoa naquela divulgação. Uma linha por participante considerado pelo ato,
inclusive quem não recebeu posição. Append-only, como a publicação.

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `publicacao` | FK → `PublicacaoResultado`, CASCADE | A projeção pertence ao ato que a congelou |
| `inscricao` | FK → `inscricoes.Inscricao`, PROTECT | Por onde a Área do Candidato a alcança |
| `situacao` | CharField(20), choices | `CLASSIFICADA` \| `SEM_POSICAO` |
| `posicao` | PositiveIntegerField, null | Nula quando `SEM_POSICAO` |
| `compartilhada` | BooleanField | O empate residual, congelado como foi divulgado |
| `pontuacao` | CharField(32) | Já na apresentação institucional (`185,00`); texto, não decimal |
| `motivo` | TextField, blank | O motivo da não classificação, quando houver |

**Constraints**: `UNIQUE (publicacao, inscricao)`. **Índice**: `(inscricao)` — é por ele que o
acompanhamento encontra a linha da pessoa, sem varrer publicação.

`CASCADE` na publicação e `PROTECT` na Inscrição: as linhas são partes da publicação e não têm vida
sem ela; a Inscrição, ao contrário, não pode desaparecer sob a divulgação que a nomeia. Na prática
nada é apagado — a publicação é append-only, e o `CASCADE` descreve a pertinência, não uma operação
que exista.

**Por que tabela, e não uma chave dentro do conteúdo congelado.** Guardar as duas projeções no mesmo
`BinaryField` faria toda leitura pública carregar também o individual, e a fronteira passaria a
depender do template não renderizar o que a view já tem em mãos. Com a separação, `portal.views.resultado`
lê `conteudo_publico` e **não tem consulta** que alcance `SituacaoDivulgada` (T-013). E o
`conteudo_publico_hash` passa a ser o resumo do que foi divulgado — que é o que a SC-004 afirma —, e
não de um objeto que mistura público e privado.

**Isto não é segunda fonte de verdade** (FR-058): as duas projeções nascem na mesma transação, do
mesmo ato imutável, e a linha individual aponta para a publicação que a originou. O que a FR-058
proíbe é uma fonte **viva**, que mudasse com o ato enquanto a publicação permanece histórica — e
esta é congelada como a outra.

---

## `DocumentoDoResultado`

Os bytes do documento oficial, no molde de `DocumentoPublicado`.

| Campo | Tipo | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `publicacao` | OneToOne → `PublicacaoResultado`, PROTECT | |
| `bytes` | BinaryField | |
| `content_type` | CharField(100), default `application/pdf` | |
| `documento_hash` | CharField(64), indexado | Integridade, **não** unicidade: dois documentos idênticos são legítimos |

Tabela própria, e não coluna anulável na publicação: até a F4 as publicações nascem sem documento
(T-007), e a ausência de linha representa isso sem deixar coluna a limpar depois.

---

## O conteúdo divulgado

`conteudo_publico` guarda os bytes de `canonical_bytes(...)`. A forma completa está em
[contracts/conteudo.md](./contracts/conteudo.md); o essencial:

```text
{
  "versao_do_formato": 1,
  "cabecalho": { titulo, natureza_rotulo, processo, edital, perfil, marco,
                 publicado_em, signatario_nome, signatario_cargo, ato },
  "posicoes": [ { posicao, compartilhada, candidato, protocolo,
                  modalidade, pontuacao } ]
}
```

Não contém identificador de inscrição, CPF, e-mail, `identity_subject`, nem qualquer valor vindo de
`PosicaoNaOrdem.desempate` (FR-018 a FR-020). `compartilhada` diz o empate residual; nenhum
desempate é inventado (FR-014). Todo rótulo já vem resolvido — nada na renderização traduz enum nem
resolve identificador (FR-013).

---

## O que esta feature lê e não altera

| Agregado | O que lê | Onde |
|---|---|---|
| `AtoDeOrdenacao` | `edital`, `perfil_id`, `marco_id`, `versao`, `emitido_em`, cadeia | composição e publicabilidade |
| `PosicaoNaOrdem` | `posicao`, `pontuacao_combinada`, `modalidade_id`, `consequencia`, `motivo`, `empate_residual` | composição. **`desempate` não é lido** (FR-020) |
| `Inscricao` | `nome`, `protocolo` | composição, uma vez |
| `VersaoConsolidada` | `content` do ato, para rótulos | composição, uma vez |
| `ProcessoSeletivo` | a linha, para `select_for_update` | serialização com a emissão (T-005) |
| Catálogo de autoridades | nome, cargo, identificador | escolha na prévia |

Depois de composto o conteúdo, nenhum desses é lido de novo por nenhuma leitura pública desta
feature (T-013).
