# Modelo — e a razão de ele não mudar

## Nenhuma entidade nova, nenhuma migration

As quatro histórias mexem em **onde** e **quando** a informação aparece. Nenhuma cria conceito,
nenhuma persiste estado, nenhuma toca conteúdo publicado.

| História | O que muda | Espécie |
|---|---|---|
| `US1` | a lista de destinos do marco, e o caminho anexado à recusa | derivação e prosa |
| `US2` | duas frases, produzidas pelo mecanismo existente | prosa |
| `US3` | um predicado de domínio, e a escolha do instante que o acompanha | calibragem |
| `US4` | um rótulo, um campo no que já é montado, e uma frase derivada | prosa e contexto |

**O total do `make preparar` continua `N de 32`.** A 32ª tabela veio da `036`; esta feature não
acrescenta nenhuma. Se a saída disser 31, a worktree está atrás da `main`, e não é defeito daqui.

---

## O peso continua sendo da Etapa, e a razão é o conteúdo publicado

O peso é campo **da Etapa** — é assim que o conteúdo o publica, e é assim que a regra de combinação o
lê. Movê-lo para o par marco×Etapa significaria:

1. migration sobre conteúdo **já publicado**, que a Constituição manda preservar no valor;
2. decidir o que acontece com Editais vigentes cujo peso foi publicado no lugar antigo;
3. um controle por Etapa no cartão que a auditoria acusa de ter **28**.

Nada disso cabe nesta feature, e o primeiro item sozinho já a tiraria da faixa de risco que ela
declara. Fica em `D-003`, **registrado como achado e não como escopo**.

---

## O que o cartão do marco precisa receber, e que não é controle

Hoje o cartão itera a lista de Etapas classificatórias com **identificador e rótulo**. Para nomear as
Etapas enumeradas sem peso, ela passa a carregar também **se aquela Etapa tem peso declarado**.

É **um campo a mais no que já é montado** — não uma consulta nova, não um controle novo, e por isso
a `FR-551a` continua satisfeita. O cartão já se reconstrói a cada mudança da seleção, e é esse ciclo
que dá o *"no momento em que enumera"* sem inventar tela.

---

## O que a montagem das pendências precisaria receber, e que é assinatura

Para dizer **a quem pedir**, a montagem das pendências precisa conhecer as permissões de quem lê — e
hoje ela recebe só o Edital e o instante.

**Isto é mudança de assinatura, com chamadores a encontrar**, e é a única parte desta feature que não
é prosa. Por isso a `FR-542b` manda **percorrer antes**: se o achado já estiver fechado por outra
razão, esta mudança não precisa existir.
