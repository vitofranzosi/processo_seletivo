# Validação com a equipe: roteiro, gabarito e registro

*A US4 da spec (D-007, D-008, FR-7735 a FR-7739). É conferência, e não teste formal: duas ou três
pessoas não sustentam estatística, e este registro não finge que sustentam. **As sessões ainda não
aconteceram**; elas são a tarefa T042, que é de quem conduz.*

## Antes da sessão

1. **Os bancos, um por tarefa.** De `backend/`, com o grupo `navegador`:
   `PILOTO_DS_BANCO=<pasta> PYTEST_ADDOPTS="tests/navegador/test_banco_da_validacao_do_piloto.py" make test-pg PYTEST_WORKERS=0`
   grava `lista.dump`, `v3.dump`, `v4.dump`, `v5.dump` e `v6.dump` (há uma cópia de 15/11 na pasta
   de notas das sessões deste trabalho, em `piloto-172-bancos/`).
2. **Antes de cada tarefa**, `sh ../doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh <tarefa> <pasta>`
   restaura o banco dela em `ps_piloto_validacao` e prepara a worktree da `main`. V1 e V2 usam
   `lista`.
3. **As duas versões no ar, sobre o mesmo banco**: `piloto-antiga` (porta 8172, a `main`) e
   `piloto-nova` (porta 8173, a branch do piloto), do `.claude/launch.json`. Reinicie as duas a cada
   troca de banco.
4. Este roteiro impresso, sem a coluna do gabarito, e uma cópia do registro para cada pessoa.

**Um desvio da spec, registrado:** a FR-7737 pedia registros diferentes na segunda versão. As
fixtures supõem banco vazio, e cada estado nasce num banco só; as duas versões mostram os mesmos
registros. O que reduz o efeito de lembrança é a ordem alternada, e quem conduz registra, na coluna
"Hesitação", quando a pessoa disser que já viu aquela tela.

## Como conduzir

- **Metade começa pela versão antiga, metade pela nova.** P1 antiga→nova, P2 nova→antiga, P3
  antiga→nova.
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

| Tarefa | Tela e estado | Banco | Identidade | O que se pede |
|---|---|---|---|---|
| V1 | Lista de Processos, busca (L-05) | `lista` | `gabi.gestora`, gestor e elaborador | Ache o Processo do Edital 90/2026 pela busca e diga em que situação ele está. |
| V2 | Lista de Processos (L-01) | `lista` | `gabi.gestora`, gestor e elaborador | Ache a ação que é sua agora e diga onde ela leva. |
| V3 | Confirmação de Encerrar, com impedimento (C-09) | `v3` | `gabi.gestora`, gestor | O que acontece se você confirmar? Alguma coisa impede este ato? Dá para desfazer depois? |
| V4 | Confirmação de Homologar, por quem elaborou (C-03) | `v4` | `ana.elaboradora`, homologador | O que muda na publicação depois de homologar? |
| V5 | Ocupação, Edital que admite a faixa seguinte (O-07) | `v5` | `carlos`, gestor | Quantas vagas faltam ocupar na ampla concorrência? O que você faria para preenchê-las? |
| V6 | Conferência do acréscimo (K-01) | `v6` | `carlos`, gestor | Abra a Ocupação do Edital, preencha o acréscimo (origem e fundamento do roteiro) e confira. Quem a ordem alcança? O que este ato emite? Se estiver errado, como se desfaz? |

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
| V6 | quem alcança | "Candidata 601, na 1ª posição da ordem" |
| V6 | o que emite | "A apuração seguinte será emitida por este ato, em seu nome" |
| V6 | desfazer | "O acréscimo não se apaga. Se estiver errado, desfaça-o por outro ato, com motivo." |
| V6 | a origem certa | **Prevenção de erro:** a pessoa confere, na conferência, a origem e o fundamento que escreveu antes de chegar ao botão |

## O registro

Uma tabela por pessoa. "Acerto" é certo, parcial ou errado, pelo gabarito. O tempo é diagnóstico,
sem valor de aprovação (SC-2607).

### P1 (antiga → nova)

| Tarefa | Versão | Banco | Resposta, nas palavras da pessoa | Acerto | Notou o impedimento antes do botão? | Hesitação | Tempo |
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
