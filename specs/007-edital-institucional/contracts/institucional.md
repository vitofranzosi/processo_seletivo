# Contrato — Forma canônica v3 e fronteira de apresentação

**Feature**: 007 — Edital Institucional | **Data**: 2026-08-30

Dois contratos, e a fronteira entre eles é o assunto desta feature. O primeiro é **o que o conteúdo
publicado carrega**; o segundo é **o que o documento imprime**. Nenhuma regra do segundo pode
atravessar para o primeiro (FR-001).

---

## Contrato A — Conteúdo publicado, versão canônica 3

### A.1 Raiz

| Chave | Tipo | Presença | Origem | Novo em v3 |
|---|---|---|---|---|
| `schemaVersion` | inteiro | sempre | constante `SCHEMA_VERSION` | valor muda para `3` |
| `editalId` | string UUID | sempre | `Edital.id` | não |
| `processoId` | string UUID | sempre | `Edital.processo_id` | não |
| `processoCode` | string | sempre | `ProcessoSeletivo.institutional_code` | **sim** |
| `processoTitle` | string | sempre | `ProcessoSeletivo.title` | **sim** |
| `number` | inteiro | sempre | `Edital.number` | não |
| `year` | inteiro | sempre | `Edital.year` | não |
| `title` | string | sempre | `Edital.title` | não |
| `description` | string | sempre | `Edital.description` | não |
| `profiles` | lista | sempre | ver A.2 | forma muda |
| `schedule` | lista | sempre | — | não |
| `stages` | lista | sempre | — | não |
| `sections` | lista | sempre | dez itens | quantidade e `order` mudam |

### A.2 `profiles[*]` — campos novos

| Chave | Tipo | Presença | Ausência se exprime por | Origem |
|---|---|---|---|---|
| `duties` | string | **sempre** | `""` | `PerfilVaga.duties` |
| `workload` | string | **sempre** | `""` | `PerfilVaga.workload` |
| `compensation` | string | **sempre** | `""` | `PerfilVaga.compensation` |

**Regra de ausência (FR-014):** string sempre presente com `""`. Nunca `null`. Nunca chave omitida.

*Precedente: `description` e `locality` no mesmo objeto já são strings sempre presentes;
`reserveLimit` é `null` por ser numérico. A convenção existe — esta feature a segue.*

### A.3 `sections` — ordem final

`apresentacao` 1 · `disposicoes-preliminares` 2 · `requisitos-gerais` 3 · `inscricao` 4 ·
`perfis` 5 · `etapas` 6 · `classificacao` 7 · `cronograma` 8 · `recursos` 9 ·
`disposicoes-finais` 10.

A forma de cada item é a da v2 e não muda: textual carrega `content`, gerada carrega `source` e
nunca `content`.

### A.4 Invariantes do contrato A

1. **Determinismo de forma.** Dois snapshots de versão 3 do mesmo conteúdo têm exatamente o mesmo
   conjunto de chaves, em qualquer nível (FR-017, FR-019 da suíte).
2. **Suficiência.** Um snapshot de versão 3 basta, sozinho, para compor o documento — nenhuma
   consulta ao banco (FR-004, SC-002a).
3. **Decimais canônicos.** `percentage`, `weight` e `minimumScore` permanecem em quatro casas com
   ponto (`"20.0000"`). Nenhuma regra de apresentação os altera (FR-001).
4. **Endereçamento inalterado.** `COLECOES_COM_CHAVE`, `COLECOES_ATOMICAS` e `LISTAS_DE_CONTROLE`
   não mudam. Nenhuma coleção-raiz nasce (FR-020).
5. **Recusa de versão divergente.** Conteúdo-base de versão diferente da vigente continua sendo
   recusado na consolidação, sem conversão (FR-019).

### A.5 Fronteira pré-existente, declarada

A gramática não protege escalares da raiz: `/editalId`, `/processoId` e `/schemaVersion` já são
endereçáveis por Retificação hoje — só `applied_publications` é recusado, por
`_recusar_controle_interno`. `processoCode` e `processoTitle` herdam essa exposição **sem ampliá-la
de classe**, e a tela de Retificação não os oferece, como já não oferece os três atuais. Corrigir
exigiria alterar a gramática, o que P-005 proíbe nesta feature.

---

## Contrato B — Apresentação no documento

Vive em `publicacoes/infrastructure/humano.py` e no compositor. **Nada aqui altera o contrato A.**

### B.1 Decimal para leitura (FR-003)

Entrada: a string canônica de quatro casas. Saída: pt-BR, zeros à direita descartados.

| Canônico | Impresso | Contexto |
|---|---|---|
| `"20.0000"` | `20%` | percentual da Regra Normativa |
| `"12.5000"` | `12,5%` | percentual da Regra Normativa |
| `"7.2500"` | `7,25%` | percentual da Regra Normativa |
| `"2.0000"` | `peso 2` | peso da Etapa |
| `"0.5000"` | `peso 0,5` | peso da Etapa |
| `"60.0000"` | `nota mínima 60` | nota mínima da Etapa |

Regras: vírgula como separador decimal; zeros à direita removidos; sem casa decimal quando não há
parte fracionária; sem separador de milhar (os três valores não o alcançam).

### B.2 O que não é impresso (FR-002)

| Dado | Tratamento |
|---|---|
| `schedule[*].status` | **Não composto.** Não é conteúdo de Edital (D-002) |
| `editalId`, `processoId` | **Não compostos** em nenhuma seção destinada ao leitor (FR-004) |

`reserveType` continua traduzido pelo mapa `RESERVA` existente — descreve a vaga, não a gestão.

### B.3 Declaração de integridade (FR-004)

Preservada, e passa a identificar institucionalmente:

| Linha | Antes | Depois |
|---|---|---|
| Afirmação de derivação | presente | **presente, inalterada** |
| Identificação do Edital | `Identificador do Edital: <uuid>` | `Edital <number>/<year>` |
| Identificação do Processo | `Processo Seletivo: <uuid>` | `Processo Seletivo <processoCode> — <processoTitle>` |
| Versão do schema | presente | **presente, inalterada** |
| SHA-256 do conteúdo | presente | **presente, inalterado** |

O SHA-256 permanece porque é o que a declaração prova. O UUID sai porque não prova nada a quem lê.

### B.4 Modo de prévia

Inalterado. `MODO_PREVIA` continua omitindo a seção de integridade inteira e continua não lendo
`content_hash`. As regras B.1 e B.2 valem nos dois modos — legibilidade não é privilégio do
documento publicado.

---

## Contrato C — Interface administrativa

Não é API; é o que a interface promete a quem a opera. Verificável por teste de interface.

| Promessa | Requisito |
|---|---|
| O conjunto de ações de um Edital é calculado num único lugar, e a mensagem de ausência deriva dele | FR-023 |
| Ação cuja recusa é previsível aparece desabilitada, com o motivo alcançável por leitor de tela | FR-024 |
| Ação de retificar não é oferecida sem `retificacao:elaborar`; alcançada por URL, a tela é de leitura | FR-026 |
| Recusa de unicidade `(escopo, número, ano)` responde `edital_identifier_conflict` | FR-022 |
| Depois de submeter e de homologar, a tela nomeia a situação e o papel do próximo ato | FR-028 |
| Campo obrigatório é marcado na etiqueta e exposto a tecnologia assistiva | FR-032 |
| Recusa aparece em resumo com âncora **e** junto do campo, com vínculo programático | FR-033 |
| Botão de ordem desabilitado nas pontas; cada linha exibe sua posição | FR-035 |
| Opção de Evento exibe a data que a Etapa herda | FR-036 |
| Remover linha com conteúdo ou filhos pede confirmação; linha vazia não | FR-038 |
| Autoridade signatária é escolhida em lista; nenhum identificador é digitado | FR-039 |
| Etapa nunca gravada é "pronta para revisar"; gravada é "concluída"; distinção não depende de cor | FR-040 |
| Confirmação de ato usa o rótulo humano de `atos.ATOS` | FR-041 |
| Auditoria de gravação de rascunho nomeia a área alterada | FR-042 |

### C.1 Erro de domínio afetado

| Código | Situação | Antes | Depois |
|---|---|---|---|
| `institutional_identifier_conflict` | `(escopo, código institucional)` do Processo já usado | 409 | **inalterado** |
| `edital_identifier_conflict` | `(escopo, número, ano)` do Edital já usado | existia só em `create_edital` | **passa a ser devolvido também por `create_process_with_first_edital`** |

Nenhum código de erro novo é criado (FR-022).
