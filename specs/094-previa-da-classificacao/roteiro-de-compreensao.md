# Roteiro de compreensão com elaboradores

**Para quê**: verificar a SC-851 e a SC-848 **na interface real**, e não no protótipo. A pergunta que
orienta o teste é a do usuário, em 19/10: *"se eu configurar este edital com essas avaliações e essas
regras, o que acontecerá com os candidatos ao longo do processo seletivo?"*. Na autorização da
implementação, em 20/10, ele pediu que só os testes técnicos não bastassem como prova de usabilidade:
este roteiro é a outra metade, e **só pessoas o cumprem**. A T039 fica aberta até o relato dele.

*A primeira versão deste roteiro, de 19/10, rodava sobre o protótipo (porta 8094) e as configurações de
exemplo dele. Ela está no histórico do git; esta a substitui, com o Edital de demonstração abaixo e as
respostas que o sistema calcula para ele.*

## O ambiente

O sistema na entrada `interface-094` do `.claude/launch.json` (<http://localhost:8095>), sobre o banco
`ps_094_ui`, com o rascunho do Edital 94/2026 — *Seleção de tutores a distância* — criado por
[`ambiente-de-compreensao.py`](ambiente-de-compreensao.py). A preparação está no
[quickstart](quickstart.md), seção 2. **Rode o script de novo antes de cada pessoa**: ele regrava o
rascunho e desfaz o que a sessão anterior mexeu no cartão.

- Entre por **Acessar ambiente de demonstração** → **Elaborador** (`ana.elaboradora`).
- Abra o Edital 94/2026 → **Elaborar o Edital** → etapa **Classificação**.
- O Perfil é `TUTOR-EAD — Tutor a distância`, com 9 vagas na ampla concorrência e 1 para PcD.
- Há dois cartões de marco. O que interessa primeiro é **"Classificação para a entrevista"**: alvo de
  30, 10 suplentes, todos os empatados progridem, alimenta a Entrevista, admite faixa seguinte e
  desempata pelos meses de experiência.

## Quem, e como

- **Participantes**: ao menos cinco pessoas que compõem Editais e **não** acompanharam o
  desenvolvimento da 094. A equipe inicial prevista é de duas ou três pessoas: se não houver cinco,
  registre quantas houve, e não arredonde o critério.
- **Sem explicação prévia.** Diga só: *"Este é o cartão de uma regra de classificação. O botão
  'Simular classificação' mostra o que ela faria com candidatos fictícios. Pense em voz alta."* Não
  explique marco, faixa, corte, suplente nem apuração.
- **Uma pessoa conduz e outra anota**: o que a pessoa respondeu, onde olhou, quanto tempo levou e se
  abriu "Explorar classificação e desempate" ou "O que esta prévia simula, e o que não".
- **Tempo**: 20 a 25 minutos por pessoa. **Ao menos uma pessoa no celular**, ou na janela estreita: o
  painel cobre a tela ali, e é outra leitura.

## As tarefas

Comece com a tela da etapa Classificação aberta, sem o painel. A pessoa aperta "Simular
classificação" no cartão **"Classificação para a entrevista"**. Para cada pergunta, anote a resposta, e
se ela foi dada **sem abrir** o detalhe.

### Tarefa 1 — A regra como está

1. Quantos candidatos avançariam, e para qual avaliação?
2. Quantos não avançariam? O que acontece com eles depois?
3. O que acontece depois da Entrevista? Já dá para saber quem fica na classificação final?
4. Há alguma coisa com que você se preocuparia antes de publicar?

**Respostas corretas**: 41 dos 48 avançam para a Entrevista — 40 da faixa e 1 a mais pelo empate na
40ª; 5 não avançam nesta faixa, e uma faixa seguinte, emitida depois, pode alcançá-los (2 ficam sem
posição); não, a Classificação final é indeterminada, porque depende das notas da Entrevista; o aviso
das vagas — se as vagas forem apuradas sobre este marco, um empate na 9ª pararia a apuração das 9 vagas.

### Tarefa 2 — Mudar a regra e ver o efeito

No cartão, peça: *"Mude 'Empate na última posição' para 'A faixa para no alvo'."*

5. O que mudou?
6. Por que ninguém avança agora?
7. O que você faria para destravar?

**Respostas corretas**: o corte passou a não poder ser emitido, e ninguém avança (41 → 0); há empate
na 40ª, a última da faixa, e a regra não deixa todos entrarem; julgar o desempate, mudar o desfecho ou
acrescentar um critério que separe os dois.

Peça então: *"Volte para 'Todos os empatados progridem' e mude os suplentes para 0."*

8. O que mudou, e quem foi afetado?

**Resposta correta**: avançam 30 em vez de 41; os candidatos da 31ª à 40ª posição — inclusive os dois
empatados na 40ª — deixam de avançar. Os candidatos fictícios são os mesmos de antes: o painel avisa,
e oferece remontar.

### Tarefa 3 — O empate

Peça: *"Abra 'Explorar classificação e desempate'."*

9. Por que Íris e João estão na mesma posição?
10. Esse empate muda quem vai para a Entrevista?

**Respostas corretas**: o único critério declarado, os meses de experiência, não os separa — a nota da
Prova objetiva e a experiência são iguais; não muda quem vai para a Entrevista (os dois avançam), mas
pararia a apuração das 9 vagas. Aqui é esperado que a pessoa abra o detalhe — a tarefa pede —, e isso é
**aprofundamento**, e não falha.

### Tarefa 4 — O fim do processo

Peça: *"Volte ao processo e simule a Classificação final."* (Antes, devolva os suplentes a 10.)

11. O que esta simulação supõe sobre a Entrevista?
12. Quantos avançariam para a Análise documental? Isso significa que foram aprovados?

**Respostas corretas**: que todos os candidatos fictícios fizeram a Entrevista, quando no Edital real
só quem avançar na Classificação para a entrevista a faria; 20 avançariam — a faixa é de 19 (as 9
vagas do quadro mais 10 suplentes), e o empate na 19ª leva mais um —, e não: falta a Análise
documental, e a ocupação das vagas é outro ato.

## O que observar além das respostas

Pontos que a implementação deixou como estavam no protótipo e que só a leitura de gente diz se
funcionam:

- **O selo da Entrevista na Classificação final** diz "não calculado aqui", e o texto embaixo diz que a
  prévia dá nota fictícia de Entrevista a todos. Anote se alguém lê os dois como contraditórios.
- **O aviso das vagas no marco intermediário** é condicional ("se forem apuradas sobre este marco").
  Anote se alguém conclui que a Classificação para a entrevista apura as vagas.
- **"Não avançariam nesta faixa"** e **"Sem posição"** lado a lado: anote se alguém soma os dois.

## Critérios

| Critério | Passa quando |
|---|---|
| SC-851 | ao menos 4 de cada 5 pessoas acertam as perguntas 1, 3 e 4 sem abrir o detalhe |
| SC-848 | ao menos 4 de cada 5 acertam as perguntas 1, 2, 5, 8 e 9 sem abrir a classificação completa nem a explicação técnica |
| Linguagem | nenhuma pessoa pergunta o que é "marco", "faixa", "corte emitível" ou "apuração" para responder às perguntas 1 a 8 |
| Honestidade | nenhuma pessoa conclui, na pergunta 3 ou na 12, que o resultado final foi simulado |

## O que registrar

Em `specs/094-previa-da-classificacao/validacao-de-uso.md`, para cada pessoa: o perfil (sem nome), o
aparelho, as respostas, o tempo, onde olhou, o que abriu, as palavras que estranhou e a frase que mais
ajudou. Ao fim, os quatro critérios com o resultado, e o que mudar se algum falhar. É a T039, e quem a
fecha é o relato do usuário — não esta sessão.
