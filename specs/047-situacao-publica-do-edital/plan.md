---

description: "Implementation plan — 047 · Situação pública e histórico oficial do Edital em execução"
---

# Implementation Plan: Situação pública e histórico oficial do Edital em execução

**Branch**: `claude/spec-047-public-projection-8dd4b1` · **Date**: 2026-09-26 · **Spec**: [spec.md](spec.md)

## Summary

A página pública do Edital passa a dizer quatro coisas que o domínio já sabe e ela cala ou contradiz:

- o **desfecho** do Edital ou do Processo, que vence a marca do período;
- a **fase** de cada Evento, pela régua única da `045`, com o cancelado dito cancelado;
- o **prazo recursal** de cada resultado vigente, pela mesma conta que a interposição aplica;
- o **caminho** até toda publicação de resultado já divulgada.

Acrescenta uma quinta, derivada das anteriores: **o que está em andamento e o que vem depois**.

**Nenhuma entidade nova, nenhuma migration, nenhuma escrita.** Três funções mudam de casa ou de
forma para ter um leitor a mais:
- a fase do Evento sai da gestão para o domínio (`R-1`);
- o ramo *publicação* da janela recursal vira função pública de `recursos` (`R-5`);
- a lista de marcos pendentes perde a dependência de `Edital` (`R-4`).

Dois selectors nascem: desfechos e histórico público dos resultados. O resto é portal.

## Technical Context

Python 3.13 · Django 5.2 · PostgreSQL. Superfícies:
- no **portal**: vitrine, página da seleção, página do resultado e o cronograma do acompanhamento;
- na **gestão**: o pulso, que passa a importar a fase do novo endereço e não muda de comportamento.

O total do `make preparar` continua **`N de 34`**.

| Pergunta | Resposta, medida |
|---|---|
| Entidade nova? | **não** |
| Migration? | **não** |
| Estado novo, persistido ou calculado? | **não**: desfecho, fase, janela e histórico são leituras de registros existentes (`data-model.md`) |
| Escrita? | **não**: `test_leitura_sem_escrita.py` continua valendo |
| Endereço novo? | **não** |
| Consulta nova? | constante por página: atos de desfecho (só se houver estado final), histórico em lugar de vigentes, cadeia da publicação (`R-7`) |
| Contrato de API que muda? | **não** |
| Testes existentes que mudam de expectativa | **nenhum** medido (`R-8`); os casos novos cobrem os quatro fatos e as bordas |

**Nenhum `NEEDS CLARIFICATION`.** As duas decisões de domínio foram respondidas (*Clarifications* da
spec). As de desenho estão em [research.md](research.md), cada uma com a alternativa descartada.

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **I · Identificadores estáveis** | nenhum endereço novo; cada publicação continua no seu endereço | contrato, *O que não muda* |
| **II · Uma fonte autoritativa** | a fase sai de uma régua só, e não de duas; a janela, da mesma função que a interposição usa; o desfecho, do estado e do ato. Nenhum texto de situação é mantido à mão | `R-1`, `R-2`, `R-5`; `FR-774` |
| **II · Publicação imutável e histórica** | nada é reescrito; o histórico de resultados passa a ser alcançável, e não apenas preservado | `FR-772`, `FR-773` |
| **II · Instantes e zona institucional** | o portal deixa de comparar a data em UTC; todas as réguas recebem o mesmo `agora` | `R-1`; `D-004` |
| **III · Minimização** | nem o motivo nem o autor do ato administrativo são lidos para a página; nada individual entra | `FR-764`, `FR-776`; `data-model.md` |
| **V · Simplicidade** | nenhuma página de Processo, nenhum enum de situação, nenhuma linha do tempo unificada | `D-001`, `D-002`, `D-007` |
| **VI · Jornada** | sete percursos pelo portal sem identificação, e pela gestão para produzir os estados | [quickstart.md](quickstart.md) |

**Nenhuma violação.** Nada a justificar em *Complexity Tracking*.

## Phase 0 — o que a medição decidiu

Completa em [research.md](research.md). Quatro coisas que a spec não sabia:

1. **A spec estava errada sobre a norma do prazo** (`R-5`). A interposição lê a janela da versão
   **vigente**, e não da citada pelo ato. A spec foi emendada: a página diz o que a operação aplica,
   e a divergência vigente × citada ficou registrada para o domínio de recursos.
2. **A régua da `045` mora em `interface/`** (`R-1`), onde o portal não pode lê-la sem importar a
   gestão. Ela desce para `editais/domain`, que já depende do período de inscrições.
3. **A vitrine agrupa só pelo período** (`R-3`). Um Edital encerrado antes do fim do período ficaria
   em *"Inscrições abertas"*. O desfecho também decide o grupo.
4. **`historico_do_marco` não serve ao público** (`R-6`). Não filtra a lista, e traz o ato com o
   autor.

## Phase 1 — desenho

- [data-model.md](data-model.md): o que é lido, de onde, e a precedência do desfecho.
- [contracts/a-pagina-publica-depois-da-047.md](contracts/a-pagina-publica-depois-da-047.md): o que
  a página afirma, em que condição, e o que ela nunca diz.
- [quickstart.md](quickstart.md): os sete percursos.

### Ordem sugerida

1. **Régua única** (US2). Mover a fase para `editais/domain/fase_do_evento.py`, reimportar na
   `supervisao`, trocar `_situacao_do_evento` no portal e acrescentar a classe `cancelado`. Vem
   primeiro porque US3 depende dela e porque é refatoração com rede de testes existente.
2. **Desfecho** (US1). Selector `desfechos`, `situacao_publica`, marca e faixa do período, grupo da
   vitrine.
3. **Agora e próximo** (US3). `marcos_pendentes` no módulo novo e o bloco no cabeçalho.
4. **Prazo recursal** (US4). Extrair `janela_da_publicacao_divulgada`, religar
   `_janelas_pertinentes`, e mostrá-la no resultado e na lista de vigentes.
5. **Histórico** (US5). `historico_publico_do_edital`, o bloco *Publicações anteriores* e as
   anteriores na página do resultado.
6. **Fechamento**: contagem de consultas da vitrine (`R-7`), rastreabilidade com uma linha por `FR-`,
   `SC-` e caso-limite, e os percursos pelo navegador.

## Project Structure

```text
specs/047-situacao-publica-do-edital/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/a-pagina-publica-depois-da-047.md
├── checklists/requirements.md
└── tasks.md                      # /speckit-tasks

backend/processo_seletivo/
├── editais/domain/fase_do_evento.py        # novo: régua da fase e marcos pendentes (R-1, R-4)
├── interface/supervisao.py                 # reimporta; comportamento inalterado
├── processos/application/selectors.py      # desfechos(editais) (R-2)
├── recursos/application/selectors.py       # janela_da_publicacao_divulgada (R-5)
├── recursos/application/interpor.py        # _janelas_pertinentes passa a chamá-la
├── divulgacao/application/selectors.py     # historico_publico_do_edital (R-6)
└── portal/
    ├── leitura.py                          # cronograma pela régua; situacao_publica; agora e próximo
    ├── views.py                            # vitrine, selecao, resultado
    └── templates/portal/
        ├── selecao.html  _periodo.html  _cronograma.html  _cartao_da_selecao.html
        └── resultado.html

backend/tests/
├── unit/editais/test_fase_do_evento.py
├── integration/portal/                     # desfecho, agora e próximo, prazo, histórico
└── portal/                                 # consultas da vitrine; página do resultado
```

**Structure Decision**: o monólito Django existente. O portal ganha leitores, e não lógica. Toda
regra lida mora no domínio que já a possuía, ou desce para ele (`R-1`).

## Complexity Tracking

Nenhuma violação a justificar.
