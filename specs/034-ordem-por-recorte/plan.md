# Implementation Plan: Ordem por recorte em marco computado

**Branch**: `claude/spec-034-ordem-por-recorte` | **Date**: 2026-09-18 | **Spec**: [spec.md](spec.md)

**Input**: [specs/034-ordem-por-recorte/spec.md](spec.md)

## Summary

A classificação computada passa a emitir **uma ordem por recorte** quando o Perfil declara reserva de
vagas, seguindo o desenho que a `021` já aplica ao sorteio. Com ela, o corte, a apuração e a
convocação — que **já** são parametrizados por recorte — passam a ter do que se alimentar, e o
`ACH-47` deixa de ser uma admissão escrita na tela.

**A medição mudou o tamanho da feature, e está em [research.md](research.md).** O esquema já
comporta a raiz por lista desde a `021`, e há teste que a exercita com `origem=COMPUTADO`. As nove
chamadas de `ato_vigente` já passam o recorte. A tela de corte já lê `?lista=`. O que falta é a
emissão, o cálculo por recorte, a navegação nas telas — e **uma decisão de escopo** que a medição
levantou e que não é de quem implementa.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2.17; sem dependência nova

**Storage**: PostgreSQL. **Nenhuma migration** — `research.md`, `R-1`

**Testing**: pytest, contra PostgreSQL (`make test-pg`). Linha de base: **7213 passando, 12 pulados**
em `af97d4c`

**Target Platform**: monólito Django, interface administrativa server-side

**Project Type**: web application — `backend/` único

**Performance Goals**: sem meta nova, e uma atenção. O cálculo por recorte multiplica o número de
leituras de um marco pelo número de recortes dele, e o projeto tem orçamento de consulta verificado
por teste — condição de participação tem de sair de coluna e de SQL, nunca de ler o conteúdo
publicado. A leitura por recorte não pode virar N+1 sobre o conteúdo

**Constraints**: publicação é ato imutável; nada do acervo é reescrito; nenhuma capacidade nova

**Scale/Scope**: quatro módulos de aplicação, duas telas, 11 casos de teste alterados — contados por
nome em `research.md`, `R-5`

## Constitution Check

*GATE: passou antes da Phase 0 e foi reavaliado depois da Phase 1.*

| Princípio | Como esta feature responde | Onde |
|---|---|---|
| **II · Imutabilidade e Temporalidade** | é o princípio que a governa. A feature **cria atos**. `FR-504` fixa que o acervo não é reescrito, `D-002` que a regra vale adiante, e a obrigação 1 do contrato da ordem impede revogação por efeito colateral entre recortes | [ordem-por-recorte.md](contracts/ordem-por-recorte.md) |
| **IV · Regras Explícitas e Consistência** | `FR-491` existe por causa dele: três tratamentos divergentes do mesmo fato, em silêncio. O contrato escolhe um e diz por quê | [recortes-de-um-marco.md](contracts/recortes-de-um-marco.md) |
| **VI · Completude de Jornada** | a entrega é jornada inteira e observável: o Edital com cota **chega à convocação**. `SC-169`, cenário 2 do quickstart, pela interface | [quickstart.md](quickstart.md) |
| **I · Linguagem Ubíqua** | nenhum vocabulário novo — recorte, lista de concorrência, ampla concorrência e ordem já são do domínio | `FR-503` |
| **V · Rastreabilidade e Simplicidade** | nenhuma entidade, nenhum campo, nenhuma migration; uma linha muda a resposta do predicado da `032` | [data-model.md](data-model.md) |
| **III · Segurança e Auditoria** | **nenhuma superfície de autorização é tocada.** Nenhum dos 11 casos alterados é de autorização, e isso foi conferido por arquivo | `research.md`, `R-5` |

**Gate: passou.** Nenhuma violação a justificar — a seção *Complexity Tracking* fica vazia e foi
removida.

## O portão que não é formalidade

**A `T004` é parada de escopo, e ela pode fechar antes da implementação começar.**

A medição encontrou **três** tratamentos divergentes da Modalidade declarada como ampla. Dois são
compatíveis; o do sorteio não é — ele lhe dá recorte próprio, e a ocupação não tem linha para
consumir o que for emitido ali.

A primeira redação da `FR-491` exigia que classificação, ocupação **e sorteio** respondessem o mesmo.
Cumpri-la ao pé da letra significa **mudar o sorteio**, que funciona, tem telas em uso e está fora de
escopo — e a `SC-172`, que é o critério que a prende, media só duas listas. **Requisito que o próprio
critério não alcança é requisito que ninguém sabe se entrou**, e foi o `analyze` que pegou.

A `FR-491` passou a obrigar **classificação e ocupação**, e a `FR-491a` passou a obrigar o
**registro** da divergência do sorteio. A pergunta que sobra — *ampliar a `FR-491` para alcançá-lo?*
— é a que a `T004` leva a quem governa o backlog, e não decisão de quem implementa. **Qualquer que
seja a resposta, a `T004` emenda a `spec.md`**: a `T044` vai afirmar na rastreabilidade que as duas
foram cumpridas, e afirmação sem o requisito correspondente é a rastreabilidade mentindo.

Enquanto a `T004` não fechar, a fase 2 não começa.

## Estrutura da entrega

### Documentação (esta feature)

```text
specs/034-ordem-por-recorte/
├── spec.md
├── plan.md                    # este arquivo
├── research.md                # Phase 0 — a medição
├── data-model.md              # Phase 1
├── quickstart.md              # Phase 1
├── contracts/
│   ├── recortes-de-um-marco.md
│   └── ordem-por-recorte.md
├── checklists/requirements.md
└── tasks.md                   # produzido pelo /tasks
```

### Código (raiz do repositório)

```text
backend/processo_seletivo/
├── classificacao/application/
│   ├── calculo.py             # recebe o recorte; filtra o universo por modalidade
│   ├── emissao.py             # deixa de fixar lista nula; assinatura por recorte
│   └── selectors.py           # a proposta e o vigente, por recorte
├── editais/domain/
│   ├── recortes.py            # NOVO — a derivação única do conjunto de recortes
│   └── marcos.py              # a resposta de `emite_ordem_no_recorte`
├── ocupacao/application/selectors.py   # consome a derivação única
└── interface/
    ├── views.py               # ordenação lê o recorte; as duas telas navegam
    └── templates/interface/
        ├── ordenacao.html
        └── corte.html

backend/tests/
├── unit/classificacao/        # o universo de cada recorte
├── integration/classificacao/ # emissão, sucessão e não-atravessamento
├── integration/ocupacao/      # a cauda consumindo a ordem nova
└── interface/                 # a navegação entre recortes
```

**Structure Decision**: monólito Django existente, `backend/` único. A feature não cria módulo: ela
muda quatro arquivos de aplicação, um de domínio e duas telas. A derivação única dos recortes é o
único artefato novo, e vive no domínio porque a validação também a consumirá — domínio não importa
aplicação, e a `032` já registrou essa direção de dependência ao colocar `emite_ordem_no_recorte` em
`editais/domain`.

## Riscos, e o que responde por cada um

| Risco | Por que é real | O que responde |
|---|---|---|
| **A ordem da ampla mudar sem querer** | o mesmo cálculo passa a receber um parâmetro; o padrão errado altera todo Edital do acervo | `FR-493` e a contraprova do cenário 1; a suíte inteira é a rede, porque quase todo teste de classificação passa por ali |
| **Revogação por efeito colateral entre recortes** | as três ordens nascem do mesmo cálculo, e tratá-las como uma é o caminho natural | obrigação 1 do contrato da ordem; teste de que suceder num recorte não obsoleta os outros |
| **Confirmação cruzada entre recortes** | a assinatura hoje é do marco | `FR-495`; teste que confirma em A e tenta emitir em B |
| **A derivação divergir de novo** | já divergiu três vezes, em três módulos | `SC-172` compara as duas listas; é igualdade, não inspeção |
| **O aviso da `032` sobreviver** | ele e a tela pendem do mesmo predicado, e é fácil mudar um só | `FR-500`; os dois consumidores estão contados em `research.md`, `R-4` |
| **O predicado sobreviver vazio** | depois de aposentar o aviso ele responde sempre sim, e continua parecendo um guarda | `FR-501a`, com a ordem `T033 → T034 → T035`; a tarefa manda **medir antes de remover** |
| **A tela do acervo ficar com metade da `FR-504`** | comparar conteúdo, resumo e documento prova que nada foi reescrito, e não prova que a tela explica o que o operador vê | `T032`, com teste sobre Edital antigo de ordem única |
| **Conferência por contagem** | 11 casos mudam, e um deles pode trocar o que afirma sem mudar o número | conferência caso a caso contra a lista nomeada, como a `033` fez |
| **`seed_demo` quebrar em silêncio** | ele chama `calcular_ordem` direto, e só reclama na próxima semeadura | `research.md`, `R-9`, e tarefa própria |

## O que fica fora, e onde está dito

A spec tem a lista inteira. Os dois que mais convidam a escorregar:

- **A derivação de recortes do sorteio** — `research.md`, `R-3`. É a parada de escopo.
- **O link do corte condicionado à regra de corte** — parte (c) da melhoria 13.1, e explicitamente
  fora desde a `033`.
