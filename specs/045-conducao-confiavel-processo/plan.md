---

description: "Implementation plan — 045 · Condução confiável do Processo vivo"
---

# Implementation Plan: Condução confiável do Processo vivo

**Branch**: `claude/conducao-confiavel-processo-a5a78b` · **Date**: 2026-09-26 · **Spec**: [spec.md](spec.md)

## Summary

A Supervisão para de afirmar mais do que observa. A frase de ausência passa a respeitar o alcance de
quem lê; o recurso aparece desde a interposição; a fase do Evento é derivada, e com isso o `UX-002`
desaparece e o `UX-001` vai para a validação do conteúdo; o sinal que fica diz a quem pedir e conta o
mesmo que a lista para onde leva.

**Nenhuma entidade nova, nenhuma migration, nenhuma capacidade nova.** O catálogo da Atenção
**encolhe** de dez espécies para oito. Quase tudo é **ler a regra que já existe** — a régua do
vencido da `037`, a do período de inscrições, a fonte única de participação da `013`, o mecanismo
único de condução da `037` — no lugar onde ela faltava.

## Technical Context

Python 3.13 · Django 5.2.17 · PostgreSQL. Superfícies: a página do **Processo**, a **Supervisão**, a
**distribuição**, a **validação do conteúdo** do Edital, a **API do rascunho** e três telas de
destino que recebem quem não pode agir (sorteio, ocupação, prévia da divulgação). O
total do `make preparar` continua **`N de 34`**.

| Pergunta | Resposta, medida |
|---|---|
| Entidade nova? | **não** |
| Migration? | **não** — o `choices` do `status` fica com os quatro valores (`data-model.md`) |
| Estado novo calculado? | **não** — a fase é leitura de duas réguas existentes (`R-3`) |
| Espécie nova? | **não** — duas saem (`UX-001`, `UX-002`) |
| Consulta nova? | uma restrição **constante por Etapa** no painel (`R-6`); a contagem de recursos pendentes troca uma consulta por outra (`R-2`) |
| Achado de validação novo? | **um aviso**, código próprio, só no ato de publicação (`R-5`) |
| Contrato de entrada que muda? | a API do rascunho passa a recusar `EM_ANDAMENTO` e `CONCLUIDO` (`R-4`) |
| Casos que cercam o comportamento antigo | ~15 reescritos, 4 apagados mais a tabela-verdade do `UX-002` (`R-8`) — recontar |

**Nenhum `NEEDS CLARIFICATION`.** As decisões de domínio foram tomadas pelo usuário (`D-001` a
`D-003`); as de desenho estão em [research.md](research.md), cada uma com a alternativa descartada.

## Constitution Check

| Princípio | Como se respeita | Onde |
|---|---|---|
| **Negar por padrão** | nenhuma capacidade nova; a frase de ausência não vira canal de vazamento; a condução nomeia permissão, nunca pessoa | `FR-731`, `FR-740`, `R-1` |
| **Nada é excluído** | nenhuma migration; o `choices` do `status` não perde valor; nenhuma decisão anterior é apagada — é marcada | `data-model.md`, `FR-745` |
| **II · Publicação é ato imutável** | o conteúdo publicado não é reescrito; a leitura deixa de considerar a fase declarada | `FR-735`, `FR-737` |
| **II · Uma fonte autoritativa** | a fase sai das datas, e não de um campo que ninguém mantém; a participação sai da fonte única da `013`; a condução, do mecanismo único da `037` | `R-3`, `R-6`, `R-7` |
| **II · Instantes e zona institucional** | a fase recebe o **mesmo** `agora` que a leitura inteira usa, e as réguas já comparam instantes com zona | `R-3` |
| **VI · Completude de jornada** | os cinco percursos de [quickstart.md](quickstart.md), com identidades separadas | `SC-269` a `SC-274` |

**Nenhuma violação.** Nada a justificar em *Complexity Tracking*.

## Phase 0 — o que a medição decidiu

Completa em [research.md](research.md). Cinco coisas que a spec não sabia:

1. **O impedimento da admissibilidade é o mesmo cálculo do julgamento** (`R-2`): admitir confere o
   Resultado atacado, sem Etapa — o alcance que `impedidos_por_recurso` já usa. A `D-002` custa um
   filtro.
2. **A tela não passa pela API** (`R-4`): a recusa da fase mora no domínio, e a tela normaliza o
   valor que só herdou. E o ajudante de teste que publica pela API **engole** o 400 do rascunho.
3. **O aviso precisa de código próprio e só vale na publicação** (`R-5`): com código de impeditivo, a
   Retificação o descarta; na confirmação da Retificação, seria irremediável.
4. **A condução falta em três telas de destino**, e não só no sinal (`R-7`): sorteio e ocupação para
   o Auditor, a prévia para o Publicador diante de ato obsoleto. A peça do recurso, para o Julgador
   impedido, **já** conduz — a análise corrigiu a primeira leitura, que a contava como lacuna.
5. **O `UX-004` e o `UX-005` num Edital encerrado estão certos** (`R-7`): o ato continua possível
   enquanto o Processo não termina. O `UX-065` em recorte sem quadro não está, e ficou registrado.

## Ordem de entrega

```
US1 — a ausência respeita o alcance           ← views.py (1 função) + 2 templates; não espera nada
US2 — o recurso aparece desde que chega       ← supervisao.py (sinais_do_recurso) + acoes.py
US3 — o Cronograma deixa de produzir alarme   ← a de maior churn de teste
   │   a. conferir o PUT em levar_a_publicacao   (antes de qualquer recusa existir)
   │   b. fase derivada + pulso sem "declarado"
   │   c. recusa no domínio + normalização na tela + fixtures sem status_do_periodo
   │   d. aviso da Etapa sem Evento
   │   e. UX-001 e UX-002 saem; guarda do catálogo lê a FR-744; marcas na 022 e na 038
   ▼
US4 — o sinal que fica diz o que conta e a quem pedir   ← depende da US3: só o UX-046 leva à Retificação
       a. condução no sinal (UX-046) e nas três telas
       b. UX-046 fora da Atenção em Edital parado
       c. cobertura sobre participantes + filtro "carente"
       d. unidade na medida
```

**A ordem das fases é a das prioridades**, e desta vez as duas coincidem: nenhuma outra feature está
tocando estes arquivos. O PR #179 altera `interface/retificacao.py`, que esta feature não toca.

**A `US3` se parte em cinco passos por risco, e não por tamanho.** O passo *a* existe porque a recusa
do passo *c* seria engolida pelo ajudante de teste e reapareceria como falha de submissão com causa
enganosa. O passo *e* vem por último porque é o que mais apaga teste, e deve apagar só o que os
passos anteriores já tornaram falso.

## Riscos, medidos

| Risco | Onde | Como se fecha |
|---|---|---|
| a recusa da fase quebrar fixtures em bloco, com causa enganosa | `R-4`, `R-8` — `edital_c` publica com `EM_ANDAMENTO` pela API | o passo *a* da `US3` confere o `PUT` antes; o parâmetro `status_do_periodo` sai das fixtures, porque o `UX-002` que ele evitava deixa de existir |
| o guarda do catálogo ficar vermelho pelo texto riscado da `022` | `R-8` | o teste passa a ler a `FR-744`; o bloco da `022` ganha a nota, sem perder a tabela de 19/09 |
| o painel e a distribuição contarem participantes diferentes | `R-6` — duas formas da mesma regra (panorama × consulta restrita) | um teste compara os dois denominadores no mesmo cenário, com eliminada antes, aguardando a anterior e fora do corte |
| o orçamento de consulta do painel | `test_fronteira.py`, `test_sinais.py` — relativos à população | a restrição é constante por Etapa; os orçamentos continuam valendo. O teto absoluto (`<= 6`) é o da distribuição, que já tem o panorama na mão |
| a frase de ausência vazar | `R-1` | escolhida antes de montar sinal, só do alcance; o teste compara o HTML do mesmo leitor com e sem condição fora do alcance |
| o aviso aparecer onde não tem remédio | `R-5` | só no ato de publicação |
| contar os casos alterados pelo nome do arquivo | `R-8` | recontar caso a caso; a `034` previu oito e entregou doze |

## Phase 1 — desenho

| Artefato | O que decide |
|---|---|
| [data-model.md](data-model.md) | que não há modelo a mudar; o que muda de **sentido** — o `status` responde só *cancelado ou não* —; de onde cada medida passa a ler |
| [contracts/a-atencao-depois-da-045.md](contracts/a-atencao-depois-da-045.md) | as duas frases de ausência; as oito espécies com condição, mensagem, medida, destino e condução; o aviso; a fase |
| [quickstart.md](quickstart.md) | cinco percursos com identidades separadas — o cenário F da proposta |

**Constitution Check, depois do desenho**: sem mudança. O desenho não acrescentou entidade, capacidade
nem estado, e o único contrato de entrada que muda (a API do rascunho) muda na direção de **uma**
fonte.

## Project Structure

### Documentação (esta feature)

```text
specs/045-conducao-confiavel-processo/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── a-atencao-depois-da-045.md
├── checklists/
│   └── requirements.md
├── antes-da-conducao.md  # T002 — o "antes", e o resultado dos percursos (T035)
├── rastreabilidade.md    # T037
└── tasks.md              # /speckit-tasks — ainda não
```

### Código tocado

```text
backend/processo_seletivo/
├── interface/
│   ├── supervisao.py                 # ausência, recurso, fase no pulso, catálogo, condução, medida
│   ├── views.py                      # processo_detalhe e supervisao (ausência); telas com condução
│   ├── acoes.py                      # contagem de recursos pendentes
│   ├── forms.py                      # normalização do status herdado
│   ├── templatetags/interface_extras.py   # agrupar o aviso repetido
│   └── templates/interface/
│       ├── processo_detalhe.html · supervisao.html · _sinal.html
│       ├── distribuicao.html · sorteio.html · ocupacao.html
│       └── previa_de_publicacao.html
├── editais/
│   ├── domain/calendario.py          # fase()
│   ├── domain/validation.py          # stage_without_schedule_event
│   ├── application/draft.py          # a recusa da fase declarada
│   └── api/serializers.py            # os dois valores aceitos
└── avaliacoes/application/selectors.py   # resumo sobre participantes; filtro "carente"

specs/022-supervisao-do-processo/spec.md   # marcas de substituição (FR-745)
specs/038-painel-de-conducao/spec.md       # idem
```

## Complexity Tracking

Nenhuma violação a justificar.
