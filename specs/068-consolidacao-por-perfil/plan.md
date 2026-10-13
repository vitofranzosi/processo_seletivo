# Implementation Plan: O que se repete por Perfil sai uma vez no Edital em PDF

**Branch**: `claude/068-consolidacao-por-perfil` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/068-consolidacao-por-perfil/spec.md`

## Summary

Com dois ou mais Perfis, a seção de Perfis do documento passa a ter, logo depois da tabela de
Perfis, uma **tabela de vagas** Perfil × lista e as **tabelas de modalidades** agrupadas; abaixo
delas, as frases de reversão e de convocação uma vez; e, depois do último Perfil, junto das
atribuições comuns da `064`, as **subseções comuns** de requisitos e de marcos classificatórios. O
Perfil agrupado remete a elas, e o método comum do sorteio sai uma vez no documento.

A mudança é **do compositor**, como a `064`: uma função pura calcula, a partir do snapshot, o
**plano de consolidação** — os grupos de cada matéria, o número de cada subseção comum, a ordem das
listas, o lugar do método comum (R-001); `_perfis` compõe por ele; `itens_do_documento` e
`tabelas_do_documento` leem o mesmo plano (R-009). A identidade de dois blocos é a do que a
composição escreveria: compõe-se cada bloco numa `Composicao` de rascunho e comparam-se os itens
(R-002). O Edital de um Perfil não passa por nada disso e sai com os mesmos bytes (R-003).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: nenhuma nova. O renderizador de PDF é próprio
(`publicacoes/infrastructure/pdf.py`).

**Storage**: nenhuma mudança. Documentos publicados não são regerados.

**Testing**: pytest contra PostgreSQL (`make DB_NAME=ps068 test-pg`); os cenários da auditoria
compostos a partir dos snapshots congelados (`tests/unit/publicacoes/cenarios_da_auditoria.py`) e
pelo fluxo real (`doc/auditoria-edital-pdf-2026-10-08/cenarios/`).

**Target Platform**: o monólito Django; o documento é lido em qualquer leitor de PDF.

**Project Type**: aplicação web (monólito).

**Performance Goals**: compor um Edital de 18 Perfis não fica perceptivelmente mais lento. O plano
compõe cada bloco uma vez a mais, num rascunho sem paginação — linear no número de Perfis. A
conferência de remissões da `065` chama `itens_do_documento` na Revisão; o custo extra é o mesmo, e
nenhuma consulta ao banco é acrescentada.

**Constraints**: Edital de um Perfil com os mesmos bytes (FR-1356); prévia e publicado quebram nas
mesmas páginas; números dos Perfis e das subseções de atribuições comuns da `064` intocados
(FR-1359); nenhuma frase gerada muda de texto, salvo as aberturas que a consolidação exige.

**Scale/Scope**: Editais de até algumas dezenas de Perfis; o cenário B tem 18.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature o atende | Resultado |
|---|---|---|
| **I. Linguagem ubíqua** | As frases novas são as de um Edital — "Marcos classificatórios comuns aos Perfis …", "os descritos no item 5.6", "Nos Perfis A e B, …" — e reusam os rótulos que o documento já imprime; nenhum termo novo do sistema entra no ato ([contrato](contracts/documento.md)). | ✅ |
| **II. Integridade normativa e imutabilidade** | O documento continua derivado só da versão; conteúdo, impressão digital e documentos guardados não mudam (FR-1341, FR-1358). A equivalência por Perfil (FR-1353) é provada por teste — no rascunho sintético e nos dois cenários da auditoria. A frase que aplica os marcos a cada Perfil separadamente (FR-1347) existe para que a consolidação não crie regra. | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão, rota, ator ou registro novo. | ✅ (não se aplica) |
| **IV. Regras explícitas** | A regra de identidade é uma e escrita (FR-1340, D-003); o agrupamento derivado é **dito no documento** — cada título e cada frase nomeia os códigos a que se aplica, e a remissão diz onde está o texto. Nenhuma configuração, nenhuma decisão manual. | ✅ |
| **V. Rastreabilidade e simplicidade** | Um plano puro, lido pela composição e pelas funções de itens e tabelas da `065` — a mesma regra, e não duas (R-009). Emenda declarada à `008` (FR-016, FR-018, FR-019, FR-021) e à `064` (FR-1197) e à `025` (FR-169), anotadas lá. Rastreabilidade FR → teste em `rastreabilidade.md`. | ✅ |
| **VI. Jornada e valor demonstrável** | Os cenários A e B pelo fluxo real, antes e depois, com páginas, diff de texto e páginas renderizadas (quickstart). | ✅ |

**Reavaliação depois do desenho (Phase 1)**: sem mudança. O desenho não introduziu persistência,
contrato de API nem caminho paralelo de composição; a prévia, a Publicação e a Retificação seguem
chamando o mesmo `render_edital_pdf`.

## Componentes afetados

| Componente | O que muda |
|---|---|
| `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` | **Plano de consolidação** (função pura sobre o snapshot grafado); `_perfis` compõe por ele com dois ou mais Perfis: tabela de vagas, tabelas de modalidades, frases, remissões e subseções comuns; `_marcos` ganha o deslocamento de recuo e a remissão do método comum; `_tabela` aceita legenda em linhas que não partem código; um auxiliar de frase com códigos inseparáveis; `itens_do_documento` e `tabelas_do_documento` leem o plano. O caminho de um Perfil fica como está. |
| `backend/processo_seletivo/editais/domain/validation.py` | `_DESCRICAO_DO_ITEM` ganha as duas naturezas novas — sem isso, a conferência de remissões cai com `KeyError` no primeiro Edital consolidado. |
| `backend/tests/unit/publicacoes/test_consolidacao_por_perfil.py` | **Novo.** Identidade, tabela de vagas, modalidades, frases, subseções comuns, método uma vez, Edital de um Perfil, paginação. |
| `backend/tests/unit/publicacoes/test_equivalencia_da_consolidacao.py` | **Novo.** A prova da equivalência por Perfil (FR-1353, SC-513): reconstrução das frases normativas de cada Perfil no documento de depois, comparada com o bloco do Perfil no de antes — nos cenários A e B e nos sintéticos. |
| `backend/tests/unit/publicacoes/test_itens_do_documento.py` | Casos novos no guardião da `065` (grupos de requisitos, de marcos, de modalidades; Perfil sem quadro); os bytes esperados dos cenários passam a ser os de `specs/068-…/demonstracao/`. |
| `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_068.py` | **Novo**, no molde do da `067`: o texto de agora é o de antes transformado **só** pelas mudanças pretendidas. |
| `backend/tests/contract/test_documento_publicado.py` | Prévia × publicado com consolidação; a fixture byte a byte (um Perfil) **não** é regerada. |
| `backend/tests/integration/publicacoes/test_retificacoes.py` | Retificação que desfaz um grupo de marcos (US4). |
| Testes que afirmam o bloco por Perfil num documento de vários Perfis | Conferidos pela suíte; ver *Testes existentes expostos*. |
| `specs/008-…`, `specs/025-…`, `specs/064-…` | Nota de emenda junto dos FRs alcançados. |
| `specs/068-…/rastreabilidade.md`, `verificacao.md`, `demonstracao/` | **Novos**, no molde da `065`/`067`. |

**Preservados, e conferidos por teste**: modelos e migrations; `edital_snapshot`; `numeracao()`;
`_Numerador`; o portal, a Revisão e a Retificação (telas); `publish_edital`, `retificacoes` e
`DocumentoPublicado`; a fixture `documento_publicado_v1.pdf`.

## Testes existentes expostos à mudança

Por `grep`, nove arquivos afirmam blocos que mudam de lugar — `test_perfil_sem_vaga_imediata.py`
(17 ocorrências), `test_compor_quadro.py` (10), `test_documento_publicado.py` (7),
`test_pdf_classificacao.py` (6), `test_us1_declaracao_unica_de_vagas.py` (3), o da `067` (2),
`test_atribuicoes_consolidadas.py`, `test_hardening_pos_auditoria.py`, `test_compor_classificacao.py`.
A suíte completa é a medida. **A regra para cada falha**: se o teste afirma o bloco de um Perfil
num documento de vários Perfis, ou ele passa a afirmar a forma consolidada — a mesma informação, no
lugar novo, com a mesma força —, ou o cenário passa a ter Perfis diferentes, para continuar medindo o
bloco por Perfil. **Nunca** se afrouxa a asserção, e cada caso é registrado em `verificacao.md`.

## Consequência com a `066`

A `066-avisos-complementares` (PR #269, aberto) toca `publicacoes_do_marco.html` e a spec da `017`, e
não o compositor nem `validation.py` naquilo que esta feature muda. A faixa desta (`FR-1340`,
`SC-510`) fica acima do teto dela. Depois do merge de qualquer uma, a outra atualiza a
branch e roda `test_citacoes_de_requisito.py`.

## Project Structure

### Documentation (this feature)

```text
specs/068-consolidacao-por-perfil/
├── spec.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-012
├── data-model.md         # nenhuma entidade; o plano de consolidação, transitório
├── contracts/
│   └── documento.md      # a forma e as frases do documento
├── quickstart.md         # cenários A e B pelo fluxo real, antes e depois
├── checklists/requirements.md
├── tasks.md              # /speckit-tasks
├── rastreabilidade.md    # na implementação
├── verificacao.md        # na implementação
└── demonstracao/         # PDFs e páginas de antes e depois
```

### Source Code (repository root)

```text
backend/
├── processo_seletivo/
│   ├── publicacoes/infrastructure/pdf.py        # plano de consolidação e composição
│   └── editais/domain/validation.py             # duas naturezas de item
└── tests/
    ├── unit/publicacoes/
    │   ├── test_consolidacao_por_perfil.py              # novo
    │   ├── test_equivalencia_da_consolidacao.py         # novo
    │   ├── test_documento_da_auditoria_depois_da_068.py # novo
    │   └── test_itens_do_documento.py                   # casos e bytes esperados
    ├── contract/test_documento_publicado.py
    └── integration/publicacoes/test_retificacoes.py
```

**Structure Decision**: o monólito existente; nenhum diretório de código novo.

## Complexity Tracking

Nenhuma violação a justificar. O plano de consolidação é a única peça nova, e existe para que a
composição e a conferência de remissões da `065` leiam a mesma regra.
