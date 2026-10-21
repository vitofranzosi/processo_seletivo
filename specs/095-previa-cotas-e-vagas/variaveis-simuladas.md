# O que a fatia 2 passa a ler e a simular

Diferença sobre a matriz da `094` (`specs/094-previa-da-classificacao/variaveis-simuladas.md`, no PR
#316). Conferido no código da `main` em `e7e22b89`: o passo Perfis em
`interface/templates/interface/_perfil.html`, a derivação em `editais/domain/recortes.py`, a leitura
da linha em `classificacao/application/corte.py` e a ocupação em `ocupacao/`.

## 1. Campos gravados no passo Perfis que passam a ser lidos

| Campo | Na `094` | Na `095` | Efeito |
|---|---|---|---|
| Modalidades declaradas (`competitionModalities`) | não | **sim** | um recorte por reservada (FR-2301) |
| Modalidade apontada como ampla (`generalCompetitionModalityId`) | só para achar a linha geral | **sim** | não vira recorte; lê a linha geral |
| Linhas do quadro por Modalidade (`vacancyTable`) | só a geral | **todas** | alvo do quadro e ocupação de cada recorte |
| Reversão de vagas (`vacancyReversion`) | não | **sim** | quantidade cedida, ou "não reverte" (FR-2326) |
| Percentual, cálculo, arredondamento e distribuição da regra normativa | não | **não** | fundamentam a cota e não a calculam (decisão 003 da `016`) |
| Regras de chamada (`callRules`) | não | **não** | a cascata entre recortes é alvo derivado da `014`, não construído |
| Cadastro de reserva, forma de convocação | não | **não** | como na `094` |

Lidos do rascunho **gravado**: mudar uma Modalidade, uma linha ou a reversão só entra na prévia depois
de gravar o passo Perfis.

## 2. Campos do cartão do marco, agora por recorte

| Campo | Efeito por recorte |
|---|---|
| Alvo fixo (`targetCount`) | o **mesmo** número em todo recorte (FR-2307) |
| Alvo do quadro | a linha de cada recorte; sem linha, corte não apurável no recorte (FR-2308) |
| Suplentes (`surplusCount`) | o **mesmo** número em todo recorte |
| Desfecho do empate | avaliado em cada recorte; recusa num não impede os outros (FR-2309) |
| Etapa governada e continuação | as mesmas para todos; a Etapa recebe a união das faixas (FR-2311) |

## 3. Regras que passam a ser simuladas, e como

| Regra | Onde está no sistema | Na prévia |
|---|---|---|
| Ampla como universo inteiro | `034`, `FR-492`, `FR-493` | sim |
| Ordem e corte por Modalidade reservada | `034`, `FR-490` | sim |
| Concorrência concomitante | `016`, `FR-252` a `FR-254` | sim, sempre, sem controle |
| As quatro quantidades da apuração | `016`, `019` | sim, numa rodada, sob hipóteses (D-002) |
| Reversão por saldo e por esgotamento | `016`, decisão 007 | sim, a quantidade que a apuração cederia |
| Participação na Etapa pela faixa da ampla **ou** da Modalidade | `014`, `prontidao._dentro_da_faixa` | sim, a união por pessoa (R-008) |

## 4. O que continua fora

| Regra | Por quê |
|---|---|
| Chamadas, aceites, desistências, efeitos de convocação | `019`; exigiriam simular a convocação |
| Faixa seguinte por déficit | encadeamento de atos (D-002); a prévia diz quantos ficaram além da faixa |
| A apuração da ampla refeita com as vagas recebidas | D-002 |
| Movimentos de vaga anteriores | não existem na composição |
| Remanejamento entre Perfis | a reversão não alcança outro Perfil (`FR-246` da `016`) |
| Sorteio por lista | decisão 007 da `094` |
| Habilitação diferente por recorte | a habilitação é da pessoa (spec, Assumptions) |

## 5. O que se pode e o que não se pode afirmar

- **Pode**: que a ordem, a faixa, quem ocuparia pela ampla, as quatro quantidades e a quantidade cedida
  de cada recorte são as que o motor oficial produziria **para esses candidatos fictícios, nesse
  marco, na primeira apuração**, com todos habilitados e sem convocação.
- **Não pode**: que alguém seria convocado ou ocuparia a vaga; que a vaga sem ocupante ficará sem
  ocupante depois de faixas seguintes; que a reversão é a leitura certa da norma do Edital (DP-1,
  DP-2); que a ampla terá, depois da reversão, os titulares que teria com as vagas recebidas.
