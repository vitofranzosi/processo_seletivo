# Tarefas: cenários de treinamento e homologação

**Spec**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md)

## Fase 1 — Investigação

- [x] T001 Auditar `seed_demo`, fixtures, fontes do sorteio, papéis do seletor, finalização e o guia
  de implantação; registrar o diagnóstico no [plano](plan.md).

## Fase 2 — Base (FR-4601 a FR-4617)

- [x] T002 App `treinamento`, manifesto `CenarioDeTreinamento` e a migration `0001`.
- [x] T003 Chave `CENARIOS_DE_TREINAMENTO` na base, recusada em `production.py`; barreiras em
  `ambiente.py`.
- [x] T004 Identificadores derivados, CPF calculado, pessoa fictícia (FR-4630 a FR-4632).
- [x] T005 Retrato por introspecção e as situações da verificação.
- [x] T006 Serviço: planejar, carregar, verificar, restaurar; os quatro comandos.

## Fase 3 — Prova de conceito (C04, C07, C11)

- [x] T007 Montagem sobre os comandos da aplicação (FR-4640 a FR-4643).
- [x] T008 C04 (notas), C07 (sorteio) e C11 (entrega documental).
- [x] T009 Preservação linha a linha sobre o banco do `seed_demo`, idempotência, independência,
  restauração do C07 com o sorteio feito pela tela, falha no meio, conflito, propriedade
  (SC-1451 a SC-1454).

## Fase 4 — Catálogo completo (FR-4650 a FR-4655)

- [x] T010 C01 a C15, cada um com a próxima ação executada na suíte (SC-1455).
- [x] T011 Recusa de permissão nas ações (presidência × avaliação, elaboração × publicação).
- [x] T012 Autoridade só já usada, sem `--autoridade` (FR-4616), achado pela suíte.
- [x] T013 `treino.` fora das sugestões da página de acesso da demonstração.

## Fase 5 — Documentação

- [x] T014 [Guia da equipe](../../doc/cenarios-de-treinamento/guia-da-equipe.md), com o roteiro de
  cada cenário.
- [x] T015 [Manual de operação](../../doc/cenarios-de-treinamento/manual-de-operacao.md): backup,
  ensaio, carga, verificação, restauração.
- [x] T016 Linhas do README (módulo e incremento); [verificação](verificacao.md).

## Fase 6 — Revisão de código

- [x] T019 Os dez achados da revisão de 09/11, registrados na [verificação](verificacao.md).

## Fase 7 — Sorteio com cota

- [x] T020 C06 e C07 com a cota PPP: Perfil com o quadro 3 + 1, três cotistas, autodeclaração na
  convocação, duas relações congeladas no C07 (FR-4656, D-008).

## Fase 8 — Provisionamento da formalização (revisão de 12/11/2026)

- [x] T021 Revisar a FR-4615, a FR-4650 e a SC-1455, com a redação anterior; FR-6720 a FR-6729,
  SC-2210 a SC-2212, D-009 e D-010.
- [x] T022 Passos de `construcao.py`: `treino.acessos`, a identidade, o aceite, a definição, o
  vínculo e a designação (FR-6721 a FR-6724, FR-6728).
- [x] T023 C16 e C17 no catálogo; a pré-visualização da identidade e do vínculo (FR-6720, FR-6725).
- [x] T024 A restauração revoga as designações da rodada anterior (FR-6726).
- [x] T025 Testes: a exportação pela tela e o Centro no C16 (SC-2210); a lista do setor e o Centro no
  C17 (SC-2211); pessoa e vínculos contados na carga, na segunda carga e na restauração (SC-2212);
  a contagem dos dezessete (SC-1455).
- [x] T026 Guia da equipe e manual de operação: as fichas do C16 e do C17, a entrada como
  `treino.formalizacao`, e a dependência do exercício de designar.
- [x] T027 Verificação no navegador num banco novo; registro na [verificação](verificacao.md).

- [x] T028 Revisão do #500: a restauração revoga as designações de todos os Editais do Processo,
  também do encerrado e em qualquer cenário, e a pré-visualização as conta (FR-6726); a pessoa
  suspensa com vínculo é recusada, e a criação simultânea não vira `ERRO` (FR-6721); a
  pré-visualização acumula o provisionamento do plano (FR-6725).
- [ ] T029 Depois do merge da revisão da `117` (presidência designa): o C17 pela presidência, e as
  identidades `treino.*` só contadas e oferecidas nos Editais de treinamento.

## Pendente

- [ ] T017 Carga na homologação compartilhada, pelo administrador, depois do ensaio.
- [ ] T018 SC-1456 (humano): uma pessoa da comissão percorre um cenário só com o guia.
