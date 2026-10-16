---
description: "Tarefas da 074 — o assistente na página do Edital, no desenvolvimento local"
---

# Tasks: O assistente na página do Edital, no desenvolvimento local

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Caminhos**: relativos a `backend/` quando começam por `processo_seletivo/`, `config/` ou `tests/`.

## Phase 1: A chave

- [X] T001 `ASSISTENTE_NA_PAGINA_DO_EDITAL` em `config/settings/base.py`, desligada por padrão (FR-1680)
- [X] T002 A recusa em `config/settings/production.py` e o caso em `tests/test_configuracao_producao.py` (FR-1683)

## Phase 2: User Story 1 — o painel na página da seleção (P1) 🎯

- [X] T003 Em `processo_seletivo/interface/prototipo_do_assistente.py`, o contexto do painel e os envios recebem a conversa, as rotas e o destino; as views do protótipo passam a chamá-los, sem mudar o comportamento (FR-1681)
- [X] T004 Os envios do fragmento vêm de `rotas`, e o selo da página pública, em `interface/prototipo_do_assistente.html`
- [X] T005 `processo_seletivo/portal/assistente.py`: o painel para a página e as rotas `perguntar`, `sugestao` e `nova`, com chave de sessão própria (FR-1680, FR-1682, FR-1685)
- [X] T006 `views.selecao` renderiza o painel com a chave ligada e marca a resposta como privada; o protótipo pede a página sem ele (FR-1682)
- [X] T007 As três rotas em `processo_seletivo/portal/urls.py`
- [X] T008 Testes em `tests/portal/test_assistente_na_pagina.py`: desligada, nem painel nem rota; ligada, o percurso sem identidade, a escolha da opção, a pergunta livre com o histórico, a separação por sessão, Edital e protótipo, e o Edital sem página pública (SC-640 a SC-642)
- [X] T009 Os testes do protótipo (`tests/interface/test_prototipo_do_assistente.py`) passam sem alteração

## Phase 3: Fechamento

- [X] T010 Entrada `assistente-074` em `.claude/launch.json`, banco `ps_074_local` com o corpus do piloto, e o percurso no navegador pelas sugestões (quickstart)
- [X] T011 Pendências da implantação registradas na spec (FR-1684); a nota no `FR-1462` da `071`; README e AGENTS
- [X] T012 `make lint check test-pg`
- [X] T014 A revisão de código (oito achados): a chave fixada na suíte, o teto de conversas por sessão (FR-1685), a conversa criada no primeiro envio, o painel num módulo sem ciclo (`interface/painel_do_assistente.py`), o guardião do `FR-1462` rota a rota e o teste da simulação sobre a página inteira
- [ ] T013 **Do responsável pelo produto.** A pergunta livre com o modelo real, pela página (quickstart, passo 4): ela sai para o OpenRouter e custa, e por isso o agente não a fez
