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

## Pendente

- [ ] T017 Carga na homologação compartilhada, pelo administrador, depois do ensaio.
- [ ] T018 SC-1456 (humano): uma pessoa da comissão percorre um cenário só com o guia.
