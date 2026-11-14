# Tasks: A habilitação do assistente do Edital pela interface

**Input**: [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[contracts/tela.md](contracts/tela.md), [quickstart.md](quickstart.md)

Quatro fases, uma por commit, na ordem do plano. Cada uma termina com os testes dela verdes contra o
PostgreSQL.

## Fase 1 — O registro (US2, US3, US5)

- [x] T001 Domínio: a permissão, as frentes, as recusas, as faltas da configuração e os requisitos
  `RA-1` a `RA-12` em `duvidas/domain/habilitacao.py` (FR-7510, FR-7533).
- [x] T002 Modelo `HabilitacaoDoAssistente` e a migration `duvidas/0003`, com as constraints e o
  gatilho append-only (FR-7527).
- [x] T003 A tabela em `TABELAS_APPEND_ONLY` (o `M` vai a 66); `duvidas` no guardião de migrations.
- [x] T004 `assistente:habilitar` no Administrador institucional (FR-7510).
- [x] T005 `configuracao_do_servico()`, sem rede (FR-7501, R-6).
- [x] T006 `duvidas/application/habilitacao.py`: as regras de quem atende, a leitura da página e os
  atos, com a trava consultiva, o motivo, a recusa do ato que não muda nada, a de produção e o evento
  na trilha (FR-7504, FR-7514, FR-7517 a FR-7519, FR-7523, FR-7528 a FR-7532).
- [x] T007 A trilha da unidade nomeia o assunto e as duas operações (FR-7529, R-8).
- [x] T008 Testes: `tests/integration/duvidas/test_habilitacao.py` e
  `tests/authorization/test_habilitar_assistente.py` (SC-2452 a SC-2454).

## Fase 2 — Os leitores (US2 a US6)

- [x] T009 A tela do piloto, a entrada e o protótipo leem `piloto_atende`, e a conversa leva a marca
  da habilitação (FR-7515, FR-7525).
- [x] T010 O painel e as rotas da página pública leem `pagina_publica_atende`; o aviso de encerrado
  (FR-7519, FR-7520, FR-7524, UX-813, R-9).
- [x] T011 `avaliar_assistente` deixa de conferir a chave (FR-7509).
- [x] T012 `production.py`: recusa `ASSISTENTE_PILOTO`; serviço e tempo-limite sem depender da chave
  (FR-7505, FR-7506).
- [x] T013 Testes do portal, da gestão e da configuração de produção; as suítes da `071` e da `074`
  sem mudança (SC-2453, SC-2455, SC-2456).

## Fase 3 — A página (US1 a US3)

- [x] T014 As views, as rotas e os templates da página "Assistente do Edital", no molde de Unidades
  (FR-7502, FR-7511, FR-7513, UX-810 a UX-812).
- [x] T015 A seção na barra, ao lado de Unidades.
- [x] T016 A linha da página do Edital na gestão (FR-7522, UX-814).
- [x] T017 Testes da página: configuração sem segredo, sem chamada, recusas (SC-2450).

## Fase 4 — O percurso e a documentação

- [x] T018 O teste de navegador do percurso (SC-2451).
- [x] T019 `CLAUDE.md`/`AGENTS.md`, guia de implantação, `.env.example`, notas na `071` e na `074`,
  README e `rastreabilidade.md` (FR-7536, FR-7537).
- [x] T020 `make lint check test-pg`.
- [x] T021 A demonstração com o serviço real, com capturas (SC-2457).
