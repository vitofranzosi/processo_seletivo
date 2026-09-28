# Decisão — sem carga retroativa de Editais encerrados

Tomada pelo usuário em 25/09/2026, na revisão do
[estudo de esforço de autoria](estudo-esforco-de-cadastro-2026-09-21.md). Registro, não escopo:
nenhuma feature em curso muda por causa deste documento.

## A decisão

**O produto não terá fluxo de carga retroativa de Editais já encerrados.** A avaliação de Editais
históricos serve como amostra normativa e de complexidade, não como cenário operacional suportado.

## Por que foi preciso tomá-la agora

O estudo cadastrou cinco Editais reais, já encerrados, e para publicá-los precisou falsear a data
de encerramento das inscrições: o sistema recusa, com razão, publicar um Edital que não receberá
inscrição alguma. A primeira versão do estudo leu essa recusa como lacuna do produto e propôs uma
spec de "registro de Edital já executado". Esta decisão encerra a proposta.

## O que ela não decide

Não é a D-G3. A D-G3 decidiu que o sorteio declara fonte pública externa **prospectivamente**, sem
reescrever a norma dos Editais antigos. Ela não tratava de oferecer ou não um fluxo de registro
histórico; esta decisão trata.

## Consequências

- O IMPEDE *"o período de inscrições encerrou"* é comportamento correto, não defeito.
- Como o reuso exige Edital de origem publicado, **a primeira oferta de cada família é sempre
  composta do zero**. O custo de autoria medido no estudo é pago ao menos uma vez por família.
- Estudos futuros de autoria compõem Editais com **datas futuras**, inspirados nos reais, em vez de
  transcrever os antigos com data falseada.
