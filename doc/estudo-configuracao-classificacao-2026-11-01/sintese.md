# Síntese — a aposta

**Para quem vai decidir.** Uma página. As evidências estão no
[diário de construção](diario-de-construcao.md), e o que pede decisão está em
[decisoes-para-o-usuario.md](decisoes-para-o-usuario.md).

## O problema, medido

Configurei do zero, pela interface, um edital de 4 Etapas, 2 Perfis e 4 ordens, seguindo o texto
do edital. Em 9 salvamentos o GPS recusou **uma** vez. Em compensação, aceitou **três**
configurações que contrariavam o edital, sem dizer nada:

- **o desempate por idade invertido**, que favorecia o mais jovem;
- **a ordem das Etapas trocada**, com a didática passando a receber todos e a documental vindo
  depois da classificação final;
- **um Perfil "sem pendência" sem classificação final**.

Nenhuma validação pode recusá-las, porque não são inválidas. O operador não sofre com erros: ele
**não vê o que configurou**.

## O que já existe e está fora do lugar

- **O texto.** A Revisão escreve cada ordem com as funções do PDF (`pdf.py`). "Data de nascimento
  mais recente" denuncia o erro, mas fica no passo 9.
- **A jornada.** A prévia desenha Etapa → ordem → Etapa na ordem do certame (`jornada.py`). A
  troca de Etapas ficaria óbvia ali, mas ela só existe dentro do simulador, depois da
  configuração.
- **A ordem da tela é a do banco.** Marcos alfabéticos pelo código, e a Revisão chama a
  classificação final de "1º marco".

## A aposta

**Configurar sobre o trilho do certame, com o texto que será publicado ao lado de cada decisão.**

- O trilho é a jornada que o GPS já calcula, promovida a superfície de edição. As Etapas vêm em
  ordem; cada ordem fica depois da última Etapa que usa, com linhas até as notas que combina; cada
  corte é um portão antes da Etapa que governa. O destino circular fica visível como um portão
  *acima* da ordem que o produz, e o corte que pula uma Etapa, como um portão afastado.
- As perguntas usam a linguagem do edital: "o que acontece depois desta ordem", "se alguém de
  dentro não assumir", "mais velho primeiro". Cada uma grava os campos de sempre.
- O texto ao lado é o do documento, das mesmas funções. **Não há tradutor novo.**
- Mudar a ordem das Etapas mostra antes o que muda (ordens, portões, eliminatórias depois da final),
  calculado só da estrutura e sem prometer quantas pessoas mudam de lugar.
- Três estados, sem semáforo único: **sem resposta** (neutro), **incompleta / inválida** (impede
  a publicação) e **leitura** (é o que a estrutura faz; confira).

Ver em [prototipos/v2/](prototipos/v2/index.html). As 16 capturas estão em
[capturas/rodada2/](capturas/rodada2/).

## Em três passos

| Passo | O quê | Por quê primeiro | Custo |
|---|---|---|---|
| 1 · spec curta | Corrigir a perda de digitação na recomposição (A2); nomear o Perfil na mensagem (A3); ordenar marcos pela jornada (D-3); **mostrar no cartão do marco a frase do documento**, recomposta junto com o cartão; uma pergunta só para média ou soma (D-4); "mais velho / mais novo" (D-5) | Ataca as três configurações aceitas em silêncio com o que já existe; nenhuma regra muda | baixo |
| 2 · redesenho | O trilho como superfície da Classificação, com o inspetor; diferença estrutural antes de reordenar Etapas; leituras (D-6). Projeção servida pelo servidor a partir do conteúdo não salvo, como a prévia já faz | É o que torna relação e consequência visíveis antes de salvar | médio |
| 3 · se o teste pedir | O "texto do edital que se edita", como modo de revisão e de primeira configuração | Promissor para quem pensa pelo texto, mas incerto: frases com campos podem cansar em editais grandes | médio |

## O que não resolve

- Etapas que não valem para todos os Perfis (D-7).
- A dependência temporal do sorteio, que continua na vista própria da rodada 1.
- A densidade com dezenas de Perfis: o trilho é por Perfil e precisa de busca.
- Nada disto foi testado com operadores. As seis tarefas de [avaliacao.md](avaliacao.md) servem ao
  teste, agora com o diário como roteiro.

## Confiança

- **Alta** em que o problema dominante é a configuração errada aceita em silêncio, e em que texto
  e jornada já existem. Ambos estão observados e citados no código.
- **Média** em que o trilho reduz esse problema. É o que o protótipo mostra, mas sem usuários.
- **Baixa** sobre a vista de texto como editor principal.
