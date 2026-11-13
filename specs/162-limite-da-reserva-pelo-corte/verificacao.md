# Verificação: O limite do cadastro de reserva lido do corte

## Ponto de partida (T001)

Medido em 13/11/2026, sobre a `main` em `84cbeeb5`, contra PostgreSQL (`DB_NAME=ps_162`, 4 workers,
`--dist worksteal`), sem o grupo `navegador`:

```text
tests/unit/editais tests/unit/publicacoes tests/integration/editais tests/integration/publicacoes
tests/interface tests/portal tests/unit/portal tests/unit/test_visao_institucional.py
tests/unit/duvidas tests/unit/ocupacao
```

**9582 passando, 2 pulados, sem falha** (221s). `node --test tests/javascript/*.test.js`: **251 de 251**.

## O que mudou no caminho (13/11)

- **A constraint do banco.** `ck_perfil_reserve_limit_compatible` (da `editais/0001`) exigia número em
  todo `LIMITED`, e a primeira medição acusou a gravação nova em 358 casos. A `editais/0028` afrouxa só
  essa metade; os guardiões de contagem de migrations (o geral e o da 022) sobem para 28, com a
  justificativa escrita.
- **O Perfil legado compõe a unidade do corte de antes** (FR-6944 refinada). Os PDFs gravados do
  cenário B da auditoria são legado — "limitado em 15" com alvo 10, 5 suplentes e continuação —, e a
  abertura nova poria "os 15 primeiros" ao lado de um corte que diz outra coisa. Com a regra, eles
  continuam idênticos byte a byte.
- **O `seed_demo`** dá 2 em cada lista (e não 1, como a primeira redação da spec dizia): o alvo fixo
  vale por lista, e o Perfil tem duas listas com 1 vaga cada.
- **A concordância das recusas**: "o corte da Sorteio público" virou "o corte do marco “Sorteio
  público”".

## As fixtures que mudaram, e por quê (T021)

A regra impeditiva nova (FR-6933 a FR-6936) alcança toda fixture que publica Perfil incoerente. Nenhuma
regra foi afrouxada; as fixtures passaram a ser coerentes por um lugar só, `tests/fixtures/snapshot.py::
com_cadastro`, ou a reconstituir o acervo pelo caminho de antes, `tests/fixtures/legado.py::antes_da_162`.

| Arquivo | Mudança |
|---|---|
| `tests/fixtures/snapshot.py` | `com_cadastro(perfil, especie, numero)`: limitado sem continuação e com o excedente que dá o número; ilimitado com continuação |
| `tests/fixtures/legado.py` | `antes_da_162`, `sem_o_numero_digitado`, `devolver_o_numero_digitado`: o acervo publicado antes, com o número no conteúdo e sem a coerência nova |
| `tests/fixtures/corpus.py` | o corpus da `070` é legado, e publica dentro de `antes_da_162` |
| `tests/fixtures/selecao.py` | Docente limitado em 20 pelo corte — com folga para as Retificações dos testes do portal, que levam a linha geral a 8 —; Técnico ilimitado com continuação |
| `tests/integration/portal/test_detalhe_selecao.py` | o caso do "limitado em 0", que a `162` torna impublicável (FR-6936), virou o do número do corte anunciado |
| `tests/unit/portal/test_cadastro_de_reserva_no_portal.py` | novo: portal e assistente (FR-6945, FR-6946) |
| `tests/fixtures/ocupacao.py` | `reserva=` passa por `com_cadastro`, sem mexer no corte do cenário salvo se ele desse zero |
| `tests/portal/test_acompanhamento_pela_situacao.py`, `tests/interface/test_visao_geral.py` | `com_cadastro` nos Perfis com reserva |
| `tests/integration/editais/test_reaproveitamento.py` | o Perfil limitado sem número e com excedente 60; a cópia não leva o número |
| `tests/integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py` | `com_cadastro` nos dois Perfis, e os casos novos da US5 |
| `tests/interface/test_compor.py`, `test_round_trip_do_rascunho.py`, `test_limite_de_campos_da_composicao.py` | o formulário e o rascunho sem o número |
| `tests/interface/test_duplicar_perfil.py`, `test_acessibilidade.py` | o gatilho de recusa era "limitado sem limite", que deixou de ser recusa: virou "vagas negativas"; a asserção da ajuda junto da recusa saiu com o campo que a tinha |
| `tests/interface/test_campos_que_a_escolha_governa.py` | o bloco da opção limitada tem a nota, e não o campo |
| `tests/javascript/perfis.test.js`, `validacao.test.js` | o resumo vem do `data-resumo`; nenhuma espécie pede número (251 → 248 casos: saíram 5, entraram 2) |
| `tests/unit/editais/test_perfis.py` | a recusa do número digitado |
| `tests/migrations/test_migrations.py` | `editais` 27 → 28 nos dois guardiões |

## O que fica para depois

- **T046, o roteiro manual** (`quickstart.md`, passos 2 a 5) num banco de demonstração novo: não
  rodou nesta sessão.
- **SC-2304, humano**: pendente.
- **A Visão do Sistema** (`docs/visao-sistema/`): no merge, como as anteriores — o item "O limite do
  cadastro de reserva não é aplicado" sai de "O que ainda precisa evoluir", e a tabela "Onde ele
  aparece" do cadastro de reserva passa a dizer que o número vem do corte.
- **Rascunho submetido antes do deploy e publicado depois**: se o rascunho guardava o número, o
  conteúdo recomposto na publicação já não o leva, e o resumo difere do da revisão homologada — a
  publicação recusa com `homologated_revision_changed`, e o caminho é submeter de novo.

## A verificação inteira (T047)

Medida em 13/11/2026 contra PostgreSQL (`DB_NAME=ps_162`, 4 workers, `--dist worksteal`), sem os grupos
`navegador` e `assistente`, uma suíte só no cluster:

- `ruff check` e `ruff format --check`: limpos;
- `manage.py check`: sem problemas; `makemigrations --check`: nenhuma mudança;
- `node --test tests/javascript/*.test.js`: **248 de 248**;
- `pytest tests`: **19561 passando, 24 pulados, sem falha** (585s).

Os 24 pulados são todos deliberados e nenhum é desta feature: 11 arquivos de jornada no navegador (sem
o grupo `navegador`), 10 pares termo × template da varredura de vocabulário, a contagem real de
tokens (sem o grupo `assistente`), a recusa por vendor e o E2E contra a Caixa.

A medição anterior, antes das últimas correções de fixture, deu 19553 passando e 7 falhas, todas da
mesma causa — a Retificação dos testes do portal levava o número do Docente a zero, que a FR-6951
recusa; a fixture ganhou folga.

## Code review (13/11)

Oito achados; sete corrigidos, um registrado:

| Achado | Desfecho |
|---|---|
| O limitado com continuação só era recusado na publicação, e o corte **nasce** por Retificação (`PODE_PASSAR_A_EXISTIR`) | corrigido: vale também na Retificação, fora do legado (FR-6933 e T-004 revistas) |
| O assistente dizia "limitado a None" no limitado sem corte | corrigido: "não declarado", como antes |
| O portal dizia "1 pessoas" na frase por lista | corrigido |
| A frase das listas estava escrita em quatro lugares | corrigido: `cadastro_de_reserva.frase_das_listas` |
| O nome do marco em frase estava refeito em três lugares | corrigido: `cadastro_de_reserva.nome_do_marco` |
| A coerência do cadastro era chamada de dentro da do quadro de vagas | corrigido: `_coerencia_dos_cadastros`, direto em `validate_for_publication` |
| O ramo da nota do Perfil gravado na recusa não tinha teste | corrigido: `test_a_recusa_devolve_a_nota_do_perfil_gravado` |
| `do_perfil` recalculado várias vezes por Perfil na composição do PDF | registrado: a recomputação redundante de `marcos_que_convocam` saiu de `frases_do_corte`; passar um `Cadastro` pelos seis pontos de chamada custaria mais do que os microssegundos que poupa |

Depois das correções: `ruff check` e `ruff format --check` limpos; `pytest tests` contra PostgreSQL
com **19564 passando, 24 pulados, sem falha** (567s).
