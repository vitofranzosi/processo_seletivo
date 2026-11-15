# Validação com a equipe: roteiro, gabarito e registro

*A US4 da spec (D-007, D-008, FR-7735 a FR-7739). É conferência, e não teste formal: duas ou três
pessoas não sustentam estatística, e este registro não finge que sustentam. **As sessões ainda não
aconteceram**; elas são a tarefa T042, que é de quem conduz.*

## Antes da sessão

1. Os dois bancos montados por `doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh`
   e os dois servidores no ar: `piloto-antiga` (porta 8167, a `main`) e `piloto-nova` (porta 8168,
   a branch do piloto), cada um sobre o seu banco (quickstart §4).
2. Este roteiro impresso, sem a coluna do gabarito.
3. Uma cópia do registro, abaixo, para cada pessoa.

## Como conduzir

- **Metade começa pela versão antiga, metade pela nova.** P1 antiga→nova, P2 nova→antiga, P3
  antiga→nova.
- **Na segunda versão, a tarefa usa o Edital ou o Processo da duplicata** (coluna "Registro"), que
  está no mesmo estado com outros dados, para que a segunda resposta não seja lembrança da
  primeira.
- **Quem conduz não explica a tela.** Lê a tarefa, anota o que a pessoa diz com as palavras dela,
  onde ela para, volta ou rola à procura, e não corrige.
- **Ninguém confirma ato nenhum.** As perguntas são feitas antes do botão. Os bancos são cópias,
  mas o hábito de não clicar para ver o que acontece é o que se quer observar.
- **No fim de cada versão**, uma pergunta só: *"o que você leu nesta tela, e o que você pulou?"*. É a
  evidência que a decisão 5 do roadmap do estudo espera.
- **A pessoa entra no registro por código** (P1, P2, P3), nunca pelo nome (FR-7739).

## As seis tarefas

O gabarito é a frase da própria tela, copiada do "antes" de 15/11. As duas versões têm o mesmo texto
(é o que a comparação provou), e por isso o gabarito é um só.

| Tarefa | Tela e estado | Registro (antiga / nova) | Identidade | O que se pede |
|---|---|---|---|---|
| V1 | Lista de Processos, busca (L-05) | "Seleção cancelada" / "Seleção cancelada B" | `gabi.gestora`, gestor e elaborador | Ache o Processo do Edital 90/2026 pela busca e diga em que situação ele está. |
| V2 | Lista de Processos (L-01) | o mesmo banco | `gabi.gestora`, gestor e elaborador | Ache a ação que é sua agora e diga onde ela leva. |
| V3 | Confirmação de Encerrar, com impedimento (C-09) | Edital 1161 / o da duplicata | `gabi.gestora`, gestor | O que acontece se você confirmar? Alguma coisa impede este ato? Dá para desfazer depois? |
| V4 | Confirmação de Homologar, por quem elaborou (C-03) | Edital 01 / o da duplicata | `ana.elaboradora`, homologador | O que muda na publicação depois de homologar? |
| V5 | Ocupação, Edital que admite a faixa seguinte (O-07) | o Edital "tela-016-continua" / o da duplicata | `carlos`, gestor | Quantas vagas faltam ocupar na ampla concorrência? O que você faria para preenchê-las? |
| V6 | Conferência do acréscimo (K-01) | o Edital "interface-097" / o da duplicata | `carlos`, gestor | Quem a ordem alcança? O que este ato emite? Se estiver errado, como se desfaz? E: há dois Editais com quadro de reserva na Lista; acrescente a vaga **no do Edital nº ...** (o certo é o da tarefa) |

## O gabarito

| Tarefa | Pergunta | O que conta como certo (a frase da tela) |
|---|---|---|
| V1 | situação | o selo "Cancelado", e a frase "1 está encerrado ou cancelado: a situação de cada um está ao lado do nome" |
| V2 | a ação | o item da faixa "Ações disponíveis para você" (continuar a elaboração do Edital em elaboração) |
| V3 | o que acontece | "O Edital passa a Encerrado e deixa de receber inscrição e Retificação." |
| V3 | o que impede | "Antes de encerrar, resolva 1 pendência." e "1 recurso aguarda decisão. Peça a quem julga recursos." **Prevenção de erro:** a pessoa diz que não dá para encerrar agora antes de procurar o botão (que não existe neste estado) |
| V3 | desfazer | "Este ato não pode ser desfeito" |
| V4 | a publicação | "Depois de homologar, você não poderá publicar esta revisão." e "a publicação precisará de outra autoridade" |
| V5 | quantas | "3 A ocupar" |
| V5 | o que fazer | "Pedir a faixa seguinte com este déficit", e "a faixa anterior não é revogada" |
| V6 | quem alcança | "Candidata 601, na 1ª posição da ordem" (o nome da duplicata é outro) |
| V6 | o que emite | "A apuração seguinte será emitida por este ato, em seu nome" |
| V6 | desfazer | "O acréscimo não se apaga. Se estiver errado, desfaça-o por outro ato, com motivo." |
| V6 | o Edital certo | **Prevenção de erro:** a pessoa confere, na conferência, o Edital e a origem antes de chegar ao botão |

## O registro

Uma tabela por pessoa. "Acerto" é certo, parcial ou errado, pelo gabarito. O tempo é diagnóstico,
sem valor de aprovação (SC-2607).

### P1 (antiga → nova)

| Tarefa | Versão | Registro | Resposta, nas palavras da pessoa | Acerto | Notou o impedimento antes do botão? | Hesitação | Tempo |
|---|---|---|---|---|---|---|---|
| V1 | antiga | | | | — | | |
| V1 | nova | | | | — | | |
| V2 | antiga | | | | — | | |
| V2 | nova | | | | — | | |
| V3 | antiga | | | | | | |
| V3 | nova | | | | | | |
| V4 | antiga | | | | — | | |
| V4 | nova | | | | — | | |
| V5 | antiga | | | | — | | |
| V5 | nova | | | | — | | |
| V6 | antiga | | | | | | |
| V6 | nova | | | | | | |

**O que leu e o que pulou** — antiga: · nova:

### P2 (nova → antiga)

*(a mesma tabela)*

### P3 (antiga → nova)

*(a mesma tabela)*

## A conta, depois das sessões

- **SC-2606**: para V3, V4 e V6, a proporção de respostas certas na nova é igual ou maior que na
  antiga; e, em V3 e V6, as vezes em que a pessoa procurou o botão sem ter notado o impedimento ou o
  Edital não são mais numerosas na nova.
- **SC-2607**: para V1, V2 e V5, a proporção de acerto na nova é igual ou maior.
- O que cada pessoa disse que lê e que pula vai, sem resumo, para o relatório.
