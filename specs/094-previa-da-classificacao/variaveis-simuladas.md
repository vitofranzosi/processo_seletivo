# O que a prévia simula, e o que não

**Terceira rodada, 19/10/2026.** O usuário perguntou se o simulador considera todas as variáveis do
Edital. **Não considera**, e esta matriz diz exatamente quais. Ela foi conferida no código da `main` em
`745f115f`: os campos do cartão em `interface/templates/interface/_marco.html` e `_criterio.html`, a
leitura do motor em `classificacao/domain/` e a progressão em
`resultados/application/prontidao.py`.

Vale para a **implementação especificada**. O protótipo lê os mesmos campos, mas com um leitor próprio e
com Etapas, fatos e vagas editáveis para a avaliação (D-010); ele não prova a integração com o
formulário real.

## 1. Campos do próprio marco, ainda não salvos — recálculo imediato

Lidos do formulário a cada alteração, por `marco_do_formulario` + htmx (D-002), sem gravar.

| Campo do cartão | Usado pela prévia | Efeito |
|---|---|---|
| Como a ordem é produzida (`orderProduction`) | Sim | só pela pontuação; por sorteio o botão some (D-007) |
| Etapas que entram (`stages`) | Sim | quais notas se combinam; a última define a Etapa do marco |
| Combinação (`operation`) e normalização | Sim | `combinar` |
| Casas decimais e arredondamento (`scale`, `mode`) | Sim | `combinar`; arredondar pode criar empate |
| Critérios de desempate (ordem, tipo, o que compara, valor ausente) | Sim | `ordenar` |
| Quantos progridem (`cutTargetKind`), alvo, suplentes | Sim | `faixa.calcular` |
| Desfecho do empate (`cutTieOutcome`) | Sim | `faixa.calcular`; não declarado, mostra os dois |
| Etapa que o corte alimenta (`cutGovernedStage`) | Sim | o nome da Etapa seguinte na jornada |
| Faixa seguinte (`cutContinuation`) | Sim | o que acontece a quem não avança |
| Código e denominação | Só para nomear | — |
| Recurso contra o resultado (`appeal*`) | **Não** | recurso, prazo e deferimento não são simulados |
| Método do sorteio (`draw*`) | **Não** | fora da fatia 1 |

## 2. Campos gravados em outros passos — lidos do rascunho salvo

Lidos do snapshot do rascunho (`edital_snapshot`) a **cada** pedido da prévia. Eles não estão na tela da
Classificação, e por isso só entram depois de gravados no passo deles. Voltando à Classificação, o
próximo recálculo já os lê.

| Campo | Passo | Usado | Efeito |
|---|---|---|---|
| Peso da Etapa | Etapas | Sim | `combinar` |
| Forma da Etapa (decisória ou com nota) | Etapas | Sim | a decisória é porta, e não parcela |
| Ordem e nome da Etapa | Etapas | Sim | a Etapa do marco; a sequência e os nomes da jornada |
| Etapa classificatória | Etapas | Indireto | só Etapas classificatórias podem ser enumeradas |
| Fatos declarados (tipo data ou inteiro) | Perfis | Sim | os valores fictícios que os critérios comparam |
| Linha geral do quadro de vagas | Perfis | Sim | o alvo "do quadro" e a fronteira das vagas |
| Linhas do quadro por Modalidade, Modalidades, ampla declarada | Perfis | **Não** | fatia 2 |
| Reversão de vagas (`vacancyReversion`) | Perfis | **Não** | fatia 2 |
| Cadastro de reserva (`reserveType`, `reserveLimit`) | Perfis | **Não** | DP-4 |
| Forma de convocação (`callForm`) | Perfis | **Não** | convocação não é simulada |
| Datas do Cronograma | Cronograma | **Não** | a prévia não tem tempo |

## 3. Outros marcos do mesmo Perfil — contexto, e não cálculo

| O que se lê de outro marco | Usado | Para quê |
|---|---|---|
| Nome, Etapas enumeradas, Etapa governada, se corta | Sim | **só para desenhar a jornada** (D-015) |
| O resultado dele (quem avançou no corte dele) | **Não** | não se encadeiam resultados entre marcos |

**A consequência que importa.** No sistema real, quem participa de uma Etapa passa por três regras
(`restringir_a_participantes`, e a 014 para o corte): (1) quem foi eliminado numa Etapa anterior não
participa; (2) quando a Etapa imediatamente anterior pode habilitar, só o habilitado nela participa; (3)
quem ficou fora do corte que governa a Etapa não participa. A prévia **não** aplica essas regras entre
marcos: todos os candidatos fictícios participam do marco simulado (spec, Assumptions). Simular a
Classificação final, que enumera a Entrevista, dá nota fictícia de Entrevista também a quem, no Edital
real, não teria chegado a ela. A jornada (FR-2249) diz isso no ponto em que acontece.

## 4. Regras ainda não contempladas

| Regra | Onde está no sistema | Situação |
|---|---|---|
| Concorrência reservada, PPI, PcD, ampla como universo inteiro | `034`, `016` | fatia 2 (D-008) |
| Concorrência concomitante | `016`, FR-252 | fatia 2 |
| Ocupação completa: chamadas, desistências, efeitos, movimentos | `016`, `019` | fatia 2; a prévia só antecipa uma recusa da apuração (D-006) |
| Reversão de vagas | `016` | fatia 2 |
| Encadeamento entre marcos (participantes da Etapa seguinte) | `012`, `014` | evolução posterior (R-014) |
| Notas fictícias de Etapas posteriores ao corte | — | evolução posterior; hoje a jornada diz "indeterminado" |
| Sorteio | `021` | fora (D-007) |
| Recurso e superação de Resultado | `018` | fora |
| Retificação | `048` | fora (D-009) |
| Eliminação por nota mínima numa Etapa com nota | consolidação, `013` | **não simulada**: os candidatos fictícios são habilitados, exceto o eliminado plantado |

## 5. O que se pode e o que não se pode afirmar

- **Pode**: que a ordem, as posições, os empates, o corte e a recusa do corte são os que o motor oficial
  produziria **para esses candidatos fictícios, nesse marco**, com a configuração digitada e o que está
  gravado nos outros passos.
- **Não pode**: que o Edital inteiro foi simulado; que quem avança no corte será aprovado; que a
  ocupação das vagas será a mostrada; que pesos ou vagas alterados em outra tela entram antes de serem
  gravados.
