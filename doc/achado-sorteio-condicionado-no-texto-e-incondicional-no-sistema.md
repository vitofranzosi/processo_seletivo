# Achado — o sorteio condicionado no texto e incondicional no sistema

Encontrado em 12/10/2026, na [análise de linguagem simples](analise-edital-linguagem-simples-2026-10-12.md)
(§4.2 e [conferência de equivalência](analise-edital-linguagem-simples-2026-10-12/equivalencia.md), achado 3),
ao comparar, frase a frase, o PDF do cenário A da auditoria de 08/10 com a proposta do lote 1.

> **Registro, não escopo.** Não entra na feature de apresentação que nasceu da mesma análise: lá, o
> texto do Elaborador sai como ele o escreveu. Priorizar é do usuário.

## O que o documento diz

No cenário A, a seção "Critérios de Classificação", texto livre do Elaborador:

> Havendo mais inscritos que vagas, a ordem de classificação será definida por sorteio eletrônico [...]

E o marco do mesmo Edital, frase gerada pelo sistema:

> Habilitação: participam todas as inscrições submetidas

**As duas frases não se contradizem.** A primeira diz **quando** há sorteio; a segunda, **quem**
participa quando ele acontece. A primeira versão da análise as chamou de contraditórias, e estava
errada.

## O que o sistema faz

O sistema **sorteia sempre**, independentemente do número de inscritos:

- um marco por sorteio não tem outra fonte de ordem — a emissão por cálculo é recusada com
  `ordering_milestone_is_drawn` (`classificacao/application/emissao.py:231-258`);
- o corte e a convocação exigem o ato de ordenação (`classificacao/application/corte.py:94-101`;
  `convocacao/application/convocar.py:97-105`);
- a relação só é recusada quando vazia (`sorteios/application/relacao.py:93-99`). Pela 021,
  casos-limite: "A ordem de um é legítima; a de nenhum é recusada";
- a ordem cobre todos e nunca é truncada pelo número de vagas (`sorteios/application/sorteio.py:289-298`).

Nenhuma spec, validação ou código condiciona o sorteio a haver mais inscritos que vagas.

## A divergência

Com menos inscritos que vagas, o **resultado prático é o mesmo**: todos ficam dentro do corte, que leva
as vagas da lista mais os suplentes (`classificacao/domain/faixa.py:143`). Mas a **norma escrita promete
algo que o sistema não faz**: que, nesse caso, não haveria sorteio. O candidato que lê o Edital espera
não haver sorteio; o sistema publica uma relação, sorteia e publica a ordem.

Há ainda uma ambiguidade de nível: o texto conta inscritos e vagas sem dizer se no Perfil (o polo) ou em
cada lista de concorrência. O sistema sorteia e corta **por lista**.

**A condição vem de Edital real.** O Edital 78/2026 do Cefor a tem: "Sorteio eletrônico, só se houver
mais inscritos que vagas" (`doc/reavaliacao-pos-consolidacao-2026-09-27/anexo-E-estrutura-dos-editais.md:29`).
Ela nunca foi modelada.

## Perguntas para quem decide

1. **Retirar a condição do texto**, aceitando que o sistema sorteia sempre, e orientar o Elaborador
   (guia de redação) a não escrevê-la?
2. **Modelar a condição** — o marco declararia "sortear só se a demanda exceder as vagas da lista" —,
   com o que isso implica para a relação, a ordem, o corte e a convocação quando não houver sorteio?
3. Em qualquer dos dois: **aviso na Revisão** quando o texto de uma seção textual condicionar o sorteio
   que o marco declara incondicional? (Heurística de texto, que só pode alimentar aviso — a mesma
   natureza do aviso de recurso da 067.)
