# Roteiro de compreensão com elaboradores — fatia 2

**Para quê**: verificar a SC-870 **na interface real**. É a extensão do roteiro da `094`
(`specs/094-previa-da-classificacao/roteiro-de-compreensao.md`), e roda na mesma sessão dele, depois:
as perguntas daqui são sobre um candidato autodeclarado, e pressupõem que a pessoa já entendeu a
jornada e o corte. **Só pessoas o cumprem**: os testes automáticos provam que os números são os do
motor, e não que alguém os entende. A T031 fica aberta até o relato do usuário.

## O ambiente

O mesmo da `094`: o rascunho do Edital 94/2026 criado por
`specs/094-previa-da-classificacao/ambiente-de-compreensao.py`, no sistema da entrada `interface-094`.
O Perfil `TUTOR-EAD` já declara a PcD, com 9 vagas na linha geral e 1 na PcD. **Rode o script de novo
antes de cada pessoa.**

Antes de cada pessoa, depois do script, quem conduz faz no passo **Perfis**, e grava:

1. Em **"Qual delas é a ampla concorrência"**, escolhe *Ampla concorrência (AC)*. O script declara a
   Modalidade AC sem apontá-la como a ampla, e a prévia — como a classificação e a ocupação — a trata
   então como uma reservada sem linha no quadro: a `034` só tira dos recortes a Modalidade apontada
   como a ampla (`FR-503`). É uma armadilha de composição, e não o que se quer testar aqui.
2. Em **reversão**, declara *"A quantidade que ficou sem preencher"*.

Na primeira vez, anota o gabarito:

3. Na etapa **Classificação**, abre a prévia do marco "Classificação para a entrevista", escolhe o
   caso-limite **"Autodeclarado dentro das vagas da ampla"** e anota o gabarito: quem é o
   autodeclarado entre as vagas da ampla, quantas vagas da PcD ficariam sem ocupante, e quantas
   seriam cedidas. O gabarito é o que o painel diz — a equivalência com o caminho oficial é a T011.

## As perguntas da SC-870

Com o caso-limite escolhido e o painel na jornada, aponte para o autodeclarado do gabarito e pergunte,
uma de cada vez, sem explicar nada:

1. **Em que lista essa pessoa ocuparia vaga?** — certo: pela ampla.
2. **A vaga reservada dela continua reservada, ou vai para outro lugar?** — certo: continua na PcD.
3. **Quantas vagas da PcD ficariam sem ocupante?** — o número do gabarito.
4. **Essas vagas iriam para a ampla?** — certo: sim, e quantas, porque o Perfil declara a reversão
   por saldo; e a pessoa deve dizer que é o que a apuração faria, e não um fato.

Depois, troque a reversão para *"Só quando a lista reservada esgota"* no passo Perfis, volte, e
pergunte de novo a 4ª. Certo: nenhuma vaga seria cedida — e, se a pessoa disser por quê, anote se
ela entendeu que a conta inclui quem ocupa pela ampla (é a DP-2 da spec).

## O que registrar

Por pessoa: as quatro respostas, certas ou não; onde ela olhou (jornada, bloco da ocupação, detalhe,
seletor de recorte); se abriu "O que esta prévia simula, e o que não"; e qualquer frase que ela leu
como afirmação de que alguém foi convocado ou aprovado — o painel não pode dizer isso (FR-2335).

**Critério**: ao menos 4 de cada 5 pessoas acertam as quatro. Se não houver cinco elaboradores,
registre quantos houve, e não arredonde o critério.
