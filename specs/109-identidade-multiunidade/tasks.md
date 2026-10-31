# Tasks: Identidade institucional preparada para mais de uma unidade (109)

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [inventario.md](inventario.md)

Caminhos relativos a `backend/`. `[P]` pode correr em paralelo com a anterior.

## Fase 1 — Resolvedor e registro

- [x] T001 Capturar, na `main`, o texto das superfícies do Cefor que a SC-1031 compara (molduras,
  frases de acesso, cinco mensagens), para a verificação. FR-3217, SC-1031
- [x] T002 `Unidade.atendimento` (texto até 255, padrão vazio) e a migration que só o acrescenta.
  FR-3211
- [x] T003 Sincronização: `atendimento` opcional no arquivo, uma linha, até 255, na trilha; o
  `unidades.json` do Cefor sem mudança. FR-3211, FR-3217, FR-3218
- [x] T004 `unidades/application/identificacao.py`: `da_unidade`, `da_implantacao`, `do_ato`, o
  canal com a recaída (`Identificacao.canal`) e a subconsulta do canal para o orçamento das dúvidas. FR-3201, FR-3202,
  FR-3203, D-001, D-002, D-007

## Fase 2 — Molduras

- [x] T005 Contexto dos templates: `identificacao_da_gestao` pelo escopo do ator e
  `identificacao_publica` pela implantação. FR-3204, FR-3206, FR-3219
- [x] T006 `interface/base.html` e `base_de_acesso.html`: título, marca da barra, topo. FR-3204,
  FR-3206, D-005
- [x] T007 [P] `lista.html`, `minhas_etapas.html`, `recusa.html`, `erros.py`: a unidade ativa.
  FR-3205
- [x] T008 [P] `portal/base.html`, `shared/404.html`: a implantação; a página pública da seleção com
  a unidade do ato. FR-3206, FR-3207, FR-3208

## Fase 3 — Mensagens e atendimento

- [x] T009 Aviso: assinatura e canal da unidade do Edital no congelamento e no rodapé visível.
  FR-3209, FR-3212, FR-3216, D-006
- [x] T010 [P] Convocação: mensagem e tela do candidato. FR-3209, FR-3212
- [x] T011 [P] Comprovante por e-mail com a unidade da Publicação da versão aceita. FR-3209, D-004
- [x] T012 [P] Código de acesso e mudança de credencial pela implantação; telas da conta com o
  global. FR-3210, FR-3214
- [x] T013 [P] Dúvidas: canal do Edital, da unidade, global. FR-3213
- [x] T014 Produção continua exigindo `PORTAL_ATENDIMENTO`; nada de correio por unidade. FR-3215

## Fase 4 — Os cenários e a comparação

- [x] T015 `tests/unidades/test_identificacao_multiunidade.py`: os oito cenários da §6 do pedido com
  o Cefor e o `campus-a`. SC-1032, SC-1033, FR-3219
- [x] T016 Comparar as superfícies do Cefor com a captura de T001. SC-1031, FR-3217
- [x] T017 Guardião: nenhum template ou mensagem desta lista escreve a sigla de uma unidade. SC-1035
- [x] T018 `make lint check test-pg` com `DB_NAME` próprio; listar os testes existentes que mudaram.
  SC-1034

## Fase 5 — Documentação

- [x] T019 Comentário do `PAPEIS`. FR-3220
- [x] T020 `doc/pendencias-da-auditoria-institucional-2026-10-30.md`. FR-3221
- [x] T021 [P] Linha da `109` no README; `verificacao.md`.
- [x] T022 [P] `quickstart.md`: o cenário demonstrável num banco descartável, pelo canal de cada
  ator (spec, §Cenário demonstrável).

## Dependências

T002 → T003 → T004 → (T005 → T006, T007, T008) e (T009 a T014) → T015 a T018. A Fase 5 não depende
do código, salvo T021.
