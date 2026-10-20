# Roteiro de compreensão com elaboradores

**Para quê**: verificar a SC-851 e a SC-848 antes de autorizar a interface da 094. A pergunta que
orienta o teste é a do usuário, em 19/10: *"se eu configurar este edital com essas avaliações e essas
regras, o que acontecerá com os candidatos ao longo do processo seletivo?"*

**Com quê**: o protótipo (`prototipo/`, entrada `previa-094` do `.claude/launch.json`), em
<http://localhost:8094/>. Ele roda o motor oficial sobre candidatos fictícios. A tela de composição em
volta é simplificada, e o protótipo diz isso.

## Quem, e como

- **Participantes**: ao menos cinco pessoas que compõem Editais e **não** acompanharam o
  desenvolvimento da 094. A equipe inicial prevista é de duas ou três pessoas: se não houver cinco,
  registre quantas houve, e não arredonde o critério.
- **Sem explicação prévia.** Diga só: *"Este é o cartão de uma regra de classificação. O botão
  'Simular classificação' mostra o que ela faria com candidatos fictícios. Pense em voz alta."* Não
  explique marco, faixa, corte, suplente nem apuração.
- **Uma pessoa conduz e outra anota**: o que a pessoa respondeu, onde olhou, quanto tempo levou e se
  abriu "Explorar classificação e desempate" ou "O que esta prévia simula".
- **Tempo**: 20 a 25 minutos por pessoa.

## As tarefas

Cada tarefa começa numa configuração de exemplo, pelos links do topo do protótipo, e só depois a
pessoa aperta "Simular classificação" no **primeiro** cartão. Para cada pergunta, anote a resposta, e
se ela foi dada **sem abrir** o detalhe.

### Tarefa 1 — Uma regra comum ("População estável (padrão)")

1. Quantos candidatos avançariam, e para qual avaliação?
2. Quantos não avançariam? O que acontece com eles depois?
3. O que acontece depois da Entrevista? Já dá para saber quem fica na classificação final?
4. Há alguma coisa com que você se preocuparia antes de publicar?

**Respostas corretas**: 16 avançam para a Entrevista; 5 não avançam nesta faixa, e uma faixa seguinte
pode alcançá-los; não, a Classificação final é indeterminada, porque depende das notas da Entrevista;
o aviso das vagas — um empate na 10ª pararia a apuração das vagas.

### Tarefa 2 — Mudar a regra e ver o efeito

Na mesma tela, peça: *"Mude 'Empate na última posição' para 'A faixa para no alvo'."*

5. O que mudou?
6. Por que ninguém avança agora?
7. O que você faria para destravar?

**Respostas corretas**: o corte passou a não poder ser emitido, e ninguém avança; há empate na 15ª,
a última da faixa, e a regra não deixa todos entrarem; julgar o desempate ou mudar o desfecho — ou
acrescentar um critério que separe os dois.

Peça então: *"Volte para 'Todos os empatados progridem' e mude os suplentes para 0."*

8. O que mudou, e quem foi afetado?

**Resposta correta**: avançam 11 em vez de 16; os dois empatados na 10ª avançam pelo empate, e Lucas,
Marina, Nuno, Olívia e Paulo deixam de avançar.

### Tarefa 3 — O empate ("Achado, linha 1")

9. Por que João e Karina estão na mesma posição?
10. Esse empate muda quem vai para a Entrevista?

**Respostas corretas**: nenhum critério declarado os separa — as notas, a data de nascimento e o tempo
de serviço são iguais; não muda quem vai para a Entrevista (os dois avançam), mas pararia a apuração das
10 vagas. Aqui é esperado que a pessoa abra o detalhe, e isso deve ser anotado como **aprofundamento**,
e não como falha.

### Tarefa 4 — O fim do processo

Na jornada, peça: *"Simule a Classificação final."*

11. O que esta simulação supõe sobre a Entrevista?
12. Quantos ficariam dentro da faixa? Isso significa que foram aprovados?

**Respostas corretas**: que todos os candidatos fictícios fizeram a Entrevista, quando no Edital real
só quem avançar e for habilitado na Análise documental a faria; 11 ficariam dentro da faixa, e não: a
ocupação das vagas é outro ato.

## Critérios

| Critério | Passa quando |
|---|---|
| SC-851 | ao menos 4 de cada 5 pessoas acertam as perguntas 1, 3 e 4 sem abrir o detalhe |
| SC-848 | ao menos 4 de cada 5 acertam as perguntas 1, 2, 5, 8 e 9 sem abrir a classificação completa nem a explicação técnica |
| Linguagem | nenhuma pessoa pergunta o que é "marco", "faixa", "corte emitível" ou "apuração" para responder às perguntas 1 a 8 |
| Honestidade | nenhuma pessoa conclui, na pergunta 3 ou na 12, que o resultado final foi simulado |

## O que registrar

Em `specs/094-previa-da-classificacao/validacao-de-uso.md`, para cada pessoa: o perfil (sem nome), as
respostas, o tempo, onde olhou, o que abriu, as palavras que estranhou e a frase que mais ajudou. Ao
fim, os quatro critérios com o resultado, e o que mudar se algum falhar. É a T039.
