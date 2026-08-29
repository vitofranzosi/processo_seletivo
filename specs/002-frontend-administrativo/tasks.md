---
description: "Tarefas de implementação da Interface Administrativa"
---

# Tasks: Interface Administrativa de Processos Seletivos e Editais

**Input**: artefatos em `/specs/002-frontend-administrativo/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Nota sobre a ordem.** O `plan.md` prevê este documento na Fase 2, antes da implementação. Não foi
o que aconteceu: as seis histórias foram implementadas primeiro e esta lista veio depois. As
tarefas marcadas `[X]` foram reconstruídas a partir do que existe no código; as `[ ]` são trabalho
real que resta. Uma lista que marcasse tudo como feito não valeria a pena existir.

## Formato: `[ID] [P?] [Story] Descrição`

- **[P]**: executável em paralelo sem conflito de arquivo
- **[Story]**: história rastreada (`US1` a `US6`)

---

## Phase 1: Setup

- [X] T001 Criar o app `interface` em backend/processo_seletivo/interface/
- [X] T002 Habilitar o motor de templates e o context processor de identidade em backend/config/settings/base.py
- [X] T003 Montar as rotas sob `/gestao/` em backend/config/urls.py e backend/processo_seletivo/interface/urls.py
- [X] T004 [P] Servir o HTMX 2.0.4 pelo próprio projeto em backend/processo_seletivo/interface/static/interface/
- [X] T005 [P] Criar a folha de estilo em backend/processo_seletivo/interface/templates/interface/base.html

---

## Phase 2: Foundational

**⚠️ Nenhuma história funciona sem esta fase.**

- [X] T006 Criar a fronteira de identidade — papéis, sessão e context processor — em backend/processo_seletivo/interface/identidade.py
- [X] T007 Proteger o seletor de identidade por `INTERFACE_SELETOR_IDENTIDADE`, devolvendo 503 quando ausente
- [X] T008 Converter `DomainError` em página, e não em 500, em backend/processo_seletivo/interface/erros.py
- [X] T009 [P] Criar os filtros de apresentação — situação, plural, dicionário — em backend/processo_seletivo/interface/templatetags/interface_extras.py
- [X] T010 [P] Criar as fixtures de identidade e composição em backend/tests/interface/conftest.py

---

## Phase 3: US1 — Entrar e enxergar o próprio trabalho (P1)

**Rastreia**: FR-001 a FR-004, FR-025, FR-026

- [X] T011 [US1] Tela de identificação com papéis e suas permissões
- [X] T012 [US1] Lista de Processos e Editais do escopo, com situação e contadores
- [X] T013 [US1] Oferecer apenas ações que o ator pode praticar, via `disponiveis`
- [X] T014 [US1] Testes de escopo, papéis e ações oferecidas em backend/tests/interface/test_lista.py

---

## Phase 4: US2 — Montar um Edital sem assistência (P1)

**Rastreia**: FR-005 a FR-009, FR-019, FR-020

- [X] T015 [US2] Assistente em quatro etapas, com identificação somente leitura
- [X] T016 [US2] Leitura de linhas indexadas de Perfil e Evento em backend/processo_seletivo/interface/forms.py
- [X] T017 [US2] Fragmentos HTMX de acrescentar e remover linha
- [X] T018 [US2] Preservar o digitado quando o domínio recusa — `_ler_etapa` antes de `_gravar_etapa`
- [X] T019 [US2] Mostrar achados de validação por severidade antes de submeter
- [X] T020 [US2] Interpretar instantes no fuso institucional, e não em UTC
- [X] T021 [US2] Testes de composição e wizard em backend/tests/interface/test_compor.py
- [X] T022 [US2] Rascunho local no navegador em backend/processo_seletivo/interface/static/interface/rascunho.js: guarda por Edital, etapa e pessoa; oferece restaurar em vez de sobrescrever em silêncio; descarta quando o conteúdo guardado coincide com o renderizado pelo servidor
- [X] T023 [US2] Distinguir na tela o enviado do que só existe no navegador: aviso ao reabrir com preenchimento pendente, e marcador "alterações ainda não enviadas" enquanto houver diferença
- [X] T024 [US2] Testes do contrato entre template e script em backend/tests/interface/test_rascunho_local.py, e verificação do ciclo completo no navegador com a sessão expirada no banco

---

## Phase 5: US3 — Conduzir o Edital até a publicação (P1)

**Rastreia**: FR-010 a FR-014, FR-021, FR-022

- [X] T025 [US3] Tabela de atos do Edital com consequências, permissão e situação exigida
- [X] T026 [US3] Tela de confirmação dizendo o que o ato provoca antes de praticá-lo
- [X] T027 [US3] Pedir fundamento na homologação e Autoridade Signatária na publicação
- [X] T028 [US3] Comunicar a segregação de funções antes da tentativa
- [X] T029 [US3] Chave de idempotência nascendo na tela, para confirmar duas vezes não praticar dois atos
- [X] T030 [US3] Não oferecer "Confirmar" quando a recusa é certa — permissão, situação, pendência impeditiva ou segregação
- [X] T031 [US3] Testes de fluxo e segregação em backend/tests/interface/test_fluxo.py

---

## Phase 6: US4 — Retificar com clareza do efeito (P2)

**Rastreia**: FR-015, FR-016, FR-027

- [X] T032 [US4] Composição por diferença sobre o conteúdo vigente em backend/processo_seletivo/interface/retificacao.py
- [X] T033 [US4] Resumo legível de cada alteração, com antes e depois
- [X] T034 [US4] Tabela de atos da Retificação e sua tela de confirmação
- [X] T035 [US4] Recusar retificação de Edital não publicado com a razão, e não com 404
- [X] T036 [US4] Testes de retificação em backend/tests/interface/test_retificar.py
- [ ] T037 [US4] **Permitir acrescentar e remover Perfil e Evento por Retificação.** O domínio suporta `ADD` e `REMOVE`; a tela só edita campos de valor. Um Edital publicado não pode ganhar nem perder um Perfil pela interface

---

## Phase 7: US5 — Registrar o desfecho (P2)

**Rastreia**: FR-017, FR-018

- [X] T038 [US5] Detalhe do Processo com ciclo de vida e atos disponíveis
- [X] T039 [US5] Mostrar o que impede o cancelamento — Editais em aberto — antes da tentativa
- [X] T040 [US5] Distinguir encerrar de cancelar no peso visual: interromper não é concluir
- [X] T041 [US5] Testes de desfecho em backend/tests/interface/test_processo.py

---

## Phase 8: US6 — Consultar a trilha de auditoria (P3)

**Rastreia**: FR-028

- [X] T042 [US6] Tela da trilha, do ato mais recente ao mais antigo, com autoria e transição
- [X] T043 [US6] Traduzir operação e agregado para linguagem lida por quem responde questionamento
- [X] T044 [US6] Exigir permissão explícita e não expor conteúdo normativo nem chave de idempotência
- [X] T045 [US6] Testes de auditoria em backend/tests/interface/test_auditoria.py
- [X] T046 [US6] Teste estrutural: toda operação auditada tem rótulo na trilha

---

## Phase 9: Acessibilidade

**Rastreia**: FR-024, SC-003, SC-009

- [X] T047 Estrutura semântica: um `h1` por tela, `lang="pt-BR"`, landmarks, rótulo em todo campo
- [X] T048 Link de salto para o conteúdo, focalizável de fato
- [X] T049 Paleta em conformidade com WCAG 2.1 AA, com tokens separados por papel
- [X] T050 Reposicionar o foco depois das trocas do HTMX, ao acrescentar e ao remover
- [X] T051 Testes de contraste, link de salto e marcação nativa em backend/tests/interface/test_acessibilidade.py
- [X] T052 Verificação com axe-core em 11 telas, registrada em accessibility.md
- [ ] T053 **Verificar com leitor de tela** — NVDA ou VoiceOver — com pessoa usuária real. Nenhuma automação substitui, e o axe cobre por volta de um terço dos critérios
- [ ] T054 **Executar o ASES**, avaliador do Governo Federal, para verificação oficial de eMAG 3.1
- [ ] T055 [P] Alto contraste e modo daltonismo (FR-024), que viriam do design system do SUAP (depende de T057)

---

## Phase 10: Pendências de decisão externa

- [ ] T056 **Integrar a autenticação institucional (LDAP).** Só `ator_da_sessao` muda; a fronteira existe para isso. **Enquanto não for feito, esta feature não é implantável em produção** — o adaptador atual aceita qualquer identidade declarada
- [ ] T057 **Confirmar a obtenção e a licença do design system do SUAP** com quem o administra no Ifes. Sem isso, o CSS próprio permanece e os três temas não existem. Ver research.md §1
- [ ] T058 **Definir a política de CSP** e, se ela proibir `unsafe-eval`, mover a geração do índice de linha do `hx-vals='js:{...}'` para o servidor. Ver research.md §2
- [ ] T059 **Medir SC-001, SC-002 e SC-008** com servidores do Cefor: 15 minutos para montar um Edital, 90% concluindo na primeira tentativa. Nunca medidos; é o que esta entrega serve para permitir

---

## Lacunas herdadas da 001

Não são tarefas desta feature. Estão aqui porque aparecem na interface e alguém vai perguntar.

- **Título e descrição do Edital não são editáveis depois da criação.** Não existe command para
  isso, e por isso a etapa de identificação do assistente é somente leitura. Resolver é evolução da
  001, não código de interface — como o plano exige.
- **`ETAPAS_SEM_BACKEND`**: o mesmo ponto, com o nome que o plano lhe deu.

---

## Dependências

- Setup (T001–T005) → Foundational (T006–T010) → todas as histórias
- US1 a US6 são independentes entre si depois da Fase 2
- T055 depende de T057
- T053, T054, T056, T058 e T059 não dependem de código: dependem de decisão ou de pessoas

## Situação

**51 de 59 tarefas concluídas.** As 8 restantes são: uma lacuna de cobertura da Retificação
(T037), três de acessibilidade que dependem de ferramenta, de pessoa ou do design system (T053,
T054, T055), e quatro decisões que não são minhas de tomar (T056 a T059).
