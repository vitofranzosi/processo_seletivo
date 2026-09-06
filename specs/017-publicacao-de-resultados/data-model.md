# Modelo de dados — Publicação de Resultados

Duas tabelas, num app novo (T-001). Nenhuma alteração em tabela existente (FR-068).

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
| `conteudo` | BinaryField | Bytes canônicos da projeção congelada (T-003) |
| `conteudo_hash` | CharField(64), indexado | `canonical_sha256` do mesmo material |
| `publicado_por` | CharField(255) | O sujeito autenticado (FR-026) |
| `publicado_em` | DateTimeField | O instante do ato (FR-027) |
| `signatario_id` | UUID | Do catálogo de autoridades, nunca digitado (FR-028) |
| `signatario_nome` | CharField(255) | Persistido: retirar a autoridade do catálogo não altera ato praticado |
| `signatario_cargo` | CharField(255) | idem |

**Constraints**

```text
uq_publicacao_raiz_por_marco     UNIQUE (edital, perfil_id, marco_id)
                                 WHERE publicacao_anterior IS NULL
uq_publicacao_sucessora_unica    UNIQUE (publicacao_anterior)
                                 WHERE publicacao_anterior IS NOT NULL
```

**Índices**: `(edital, perfil_id, marco_id)` para o histórico; `conteudo_hash` para conferência.

**Sem coluna de vigência.** Vigente é `sucessoras__isnull=True` (T-002). Sem coluna de estado: o
agregado não tem ciclo de vida (FR-044).

**Sem `motivo_da_sucessao`.** A 015 o exige porque suceder um ato de ordenação é decisão da
comissão sobre o mérito. Aqui a sucessão é consequência: existe ato novo, publica-se o ato novo, e o
motivo já está registrado no `motivo_da_sucessao` do ato que a origina. Duplicá-lo criaria dois
lugares para a mesma justificativa.

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

## O conteúdo congelado

`conteudo` guarda os bytes de `canonical_bytes(...)` de um objeto com duas faces (T-010). A forma
completa está em [contracts/conteudo.md](./contracts/conteudo.md); o essencial:

```text
{
  "cabecalho": { titulo, natureza_rotulo, edital, processo, marco, perfil,
                 publicado_em, signatario_nome, signatario_cargo, ato },
  "publico":   [ { posicao, compartilhada, candidato, protocolo,
                   perfil, modalidade, pontuacao } ],
  "individual": { "<inscricao_id>": { situacao, posicao, pontuacao, motivo } }
}
```

- **`publico`** é o que a página e o documento renderizam. Não contém identificador de inscrição,
  CPF, e-mail, `identity_subject`, nem qualquer valor de fato usado no desempate (FR-018 a FR-020).
  `compartilhada` diz o empate residual; nenhum desempate é inventado (FR-014).
- **`individual`** é interno e nunca atravessa a fronteira pública. Ele existe para a FR-058: quem
  foi considerado e não recebeu posição não aparece em `publico` (FR-017), mas encontra a sua
  situação e o motivo na própria Área.
- **Todo rótulo já vem resolvido** — nome de perfil, de marco, de modalidade, e o texto da natureza
  (T-012). Nada na renderização traduz enum nem resolve identificador.

**Por que os dois lados no mesmo objeto**: é o que torna a FR-056 literal. O resumo do candidato e a
lista pública são duas vistas sobre os mesmos bytes, congelados no mesmo instante, cobertos pelo
mesmo resumo criptográfico. Separá-los em duas colunas ou duas tabelas criaria a possibilidade de
divergirem.

---

## O que esta feature lê e não altera

| Agregado | O que lê | Onde |
|---|---|---|
| `AtoDeOrdenacao` | `edital`, `perfil_id`, `marco_id`, `versao`, `emitido_em`, cadeia | composição e publicabilidade |
| `PosicaoNaOrdem` | `posicao`, `pontuacao_combinada`, `modalidade_id`, `consequencia`, `motivo`, `empate_residual` | composição. **`desempate` não é lido** (FR-020) |
| `Inscricao` | `nome`, `protocolo` | composição, uma vez |
| `VersaoConsolidada` | `content` do ato, para rótulos | composição, uma vez |
| Catálogo de autoridades | nome, cargo, identificador | escolha na prévia |

Depois de composto o conteúdo, nenhum desses é lido de novo por nenhuma leitura desta feature
(T-013).
