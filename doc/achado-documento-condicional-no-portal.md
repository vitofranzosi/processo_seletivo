# Achado — o documento condicional no portal, e o recorte que diverge do Edital publicado

Conferido em 25/09/2026, pela interface, como complemento do
[estudo de esforço de autoria](estudo-esforco-de-cadastro-2026-09-21.md) (§13/E6 e §15): antes de
especificar a exigência documental condicional, ver **o que o portal pede** ao candidato de cada
modalidade.

> **Registro, não escopo.** O que se descreve aqui é o comportamento observado e a pergunta que ele
> deixa para a spec. Priorizar é do usuário.

## Como foi conferido

Dois Editais de teste, compostos pela interface com **datas futuras** (inscrições de 25/09 a
15/10/2026), publicados por duas pessoas, no banco do estudo:

| Edital | Perfis | Documentos exigidos |
|---|---|---|
| **902/2026** | C1 — AC, PcD, PPIQ | identidade (todos, obrigatório) · laudo médico (**C1 · PcD**, obrigatório) · autodeclaração de deficiência (todos, **não obrigatório**, instrução "apenas PcD") · autodeclaração étnico-racial (**C1 · PPIQ**, obrigatório) |
| **903/2026** | C1 — AC, PcD, PPIQ · **C2 — AC, PcD** | os mesmos, trazidos por "Partir de um Edital anterior" do 902 |

Os dois documentos de PcD representam as duas formas de dizer "só para PcD" que o estudo
encontrou: o **recorte** pela Modalidade e o **"facultativo" com a condição na instrução**.

No portal, um candidato entrou pelo código de acesso, que aparece no log do servidor, e abriu a
inscrição. Trocou a modalidade entre AC, PcD e PPIQ e anotou o que cada escolha pede.

**Não se chegou ao envio nem à análise documental.** Enviar exige anexar PDF, e nem o navegador
desta sessão nem o Claude in Chrome, que estava desconectado, puderam fazê-lo. O que está abaixo é o
que o portal **pede**; o que a análise **confere** fica em aberto.

## O que se observou

### 1. Com um Perfil só, o recorte funciona — no portal e no PDF

Na inscrição do 902, a escolha da modalidade é gravada na hora (*"Escolha guardada. A lista de
documentos foi atualizada."*) e a lista muda:

| Modalidade | Obrigatórios | Facultativo |
|---|---|---|
| AC | identidade | autodeclaração de deficiência |
| **PcD** | identidade · **laudo médico** | autodeclaração de deficiência |
| **PPIQ** | identidade · **autodeclaração étnico-racial** | autodeclaração de deficiência |

O cartão público da vaga antecipa o mesmo: *"Se concorrer em Pessoas com Deficiência, também:
Laudo médico (PcD)"*. E o PDF publicado agrupa corretamente:

```
De todos os candidatos:
    a) Documento de identidade
    b) Autodeclaração de deficiência — Apenas para quem concorre na modalidade PcD. (facultativo)
Dos candidatos concorrentes na modalidade Pessoas com Deficiência:
    a) Laudo médico (PcD)
Dos candidatos concorrentes na modalidade Pretos, Pardos, Indígenas e Quilombolas:
    a) Autodeclaração étnico-racial
```

**O produto já sabe exigir documento por modalidade.** O portal pede o laudo só ao candidato PcD, e
como obrigatório. O que falta não é o conceito: é o alcance do recorte (§3).

### 2. O "facultativo com instrução" erra nas três modalidades

A autodeclaração de deficiência, declarada para todos e não obrigatória, aparece:

- **para o candidato AC e para o PPIQ**, como documento que ele pode mandar;
- **para o candidato PcD, como dispensável**: *"Você poderá enviar a inscrição depois de anexar os
  2 documentos que faltam"* — identidade e laudo, sem ela;
- **no cartão público, sem marca nenhuma**, na lista de *"4 documentos que serão pedidos"* a todos.

É o caminho que o estudo usou no 140/2025, e o portal confirma o custo: o documento que o Edital
exige do PcD não é exigido de ninguém, e é oferecido a quem não precisa dele.

### 3. Com dois Perfis, o PDF e o portal dizem coisas diferentes

No 903, o laudo ficou com o recorte **"Todos os Perfis" + "C1 · PcD"**. O reuso o trouxe assim do
902, e nada o questionou. A Revisão tem cinco avisos, e nenhum é sobre isso.

| Onde | O que diz sobre o laudo |
|---|---|
| **PDF publicado** | *"Dos candidatos concorrentes na modalidade Pessoas com Deficiência: a) Laudo médico (PcD)"* — sem Perfil |
| **Portal, cartão do C1** | *"Se concorrer em Pessoas com Deficiência, também: Laudo médico (PcD)"* |
| **Portal, cartão do C2** | *"2 documentos que serão pedidos: Documento de identidade, Autodeclaração de deficiência"* — **sem laudo** |
| **Portal, inscrição no C2 como PcD** | *"0 de 1 documento obrigatório"* — só a identidade; *"Você poderá enviar a inscrição depois de anexar o documento que falta"* |

**O Edital publicado exige o laudo de todo candidato PcD. O portal o exige só no C1.** Um candidato
do C2 concorre à reserva de PcD com a identidade e nada mais, e o sistema não o impede.

É pior que o "facultativo" do §2. Lá, o documento publicado pelo menos diz o que o portal faz. Aqui,
o ato normativo e a regra aplicada divergem, e o operador não recebe sinal nenhum.

## Por que acontece (código consultado depois)

- **Portal.** `editais/domain/documentos.py::aplicaveis` compara `modalityId` por **identidade
  exata**. Cada Perfil tem as suas próprias Modalidades, com identidades próprias; o PcD do C1 e o
  PcD do C2 são objetos distintos. Um recorte para "C1 · PcD" nunca alcança o C2.
- **PDF.** `publicacoes/infrastructure/pdf.py::_titulo_do_grupo`, quando o Perfil é "Todos", imprime
  *"Dos candidatos concorrentes na modalidade {nome}"* — usando o **nome** da Modalidade, que é igual
  nos dois Perfis.

O gerador lê o recorte **pelo nome**, e o portal o aplica **pela identidade**. Com um Perfil, as duas
leituras coincidem. Com mais de um, deixam de coincidir.

## O que isso muda para a spec

1. **O desenho pode ser menor do que o estudo supunha.** O portal já exige documento por modalidade,
   e o PDF já agrupa por modalidade. O que falta é um recorte que valha **para a Modalidade em todos
   os Perfis**, e não para um par *(Perfil, Modalidade)*. O código, ou alguma categoria estável da
   Modalidade, é o candidato natural, porque já é igual entre Perfis. Com isso, as 112 linhas do
   140/2025 viram 7, e o estado "facultativo com instrução" deixa de ser necessário para os casos de
   modalidade.
2. **Enquanto a spec não vem, há uma divergência publicável hoje.** Nada impede que um Edital com
   mais de um Perfil saia com recorte "Todos os Perfis + Modalidade de um Perfil", e o reuso a
   produz sozinho. Uma validação que recuse, ou um aviso na Revisão, fecharia o caso sem decidir o
   desenho. É candidata à fila de correções diretas.
3. **As condições sobre o candidato continuam sem forma.** Sexo e idade para o serviço militar,
   vínculo de servidor: nada aqui muda o que o estudo registrou.

## O que ficou em aberto

- **Envio e análise documental.** Não se verificou se a análise vê o laudo como obrigatório para o
  PcD, nem o que ela mostra quando ele falta. Exige anexar arquivo: com o Claude in Chrome
  conectado, ou feito à mão.
- **O recorte "C1" + "C1 · PcD"**, isto é, com o Perfil declarado. Não foi testado; pela leitura do
  código, ele não diverge, porque o PDF passa a nomear o Perfil.
