# Contrato — a expansão do Perfil na Visão Geral

**Feature**: `041-perfil-na-visao-institucional` · **Data**: 2026-09-21

> **Contrato de interface.** Esta feature não expõe endpoint e **não acrescenta parâmetro de
> consulta**: a expansão é estado do navegador, não do servidor. O que é público para outro agente
> é a **estrutura**, as **grafias** e o que a página **declara** quando a soma não fecha.

---

## 1. A rota não muda

`GET /gestao/visao-geral`, a mesma capacidade `visao:consultar`.

**A expansão não tem parâmetro** — abrir e fechar não recarrega, e não há `?expandir=`: é estado do
navegador, não do servidor.

**Um parâmetro novo, e só um**: `atencao=1`, o filtro *Somente com atenção* (`FR-621`). Ele é o
**terceiro** degrau da ordem que a `FR-598` da `040` fixou:

```text
escopo → ano → situação → busca     ← relacionais, ANTES de materializar
       ↓
  versões vigentes materializadas
       ↓
período · atenção                    ← dependem do conteúdo, DEPOIS
       ↓
ordem
```

---

## 2. A estrutura

Cada Edital com conteúdo publicado ocupa **duas linhas** da tabela:

```text
<tr>                       ← a linha do Edital, as sete colunas da 040
<tr><td colspan=8>
     <details>             ← recolhido por padrão (FR-606)
       <summary>            "3 Perfis"
       <table>              ← a tabela dos Perfis, com <caption> e <th scope="col">
```

**O controle é o `<summary>`, e não a linha** (`FR-620`). A linha do Edital continua levando ao
Edital — é a `FR-600` da `040` —, e uma linha que alternasse a expansão faria as duas coisas
disputarem o mesmo clique. O controle tem nome acessível próprio, nomeando o Edital, e declara o seu
estado.

**O `<details>` fica dentro do `<td>`, e nunca solto na `<tr>`.** Filhos de `<tr>` são `<td>` e
`<th>`, e nada mais: pôr o `<details>` direto na linha produz HTML que cada navegador reparenteia à
sua maneira. **Nenhum teste deste repositório cobre estrutura de tabela** (`R-007`) — por isso esta
é a primeira cláusula do contrato, e por isso ela tem caso próprio.

**Edital sem conteúdo publicado não recebe a segunda linha**: não há Perfil a expandir.

---

## 3. As colunas da expansão

`Perfil` · `Localidade` · `Vagas imediatas` · `Cadastro de reserva` · `Submetidas` ·
`Em preenchimento` · `Inscr./vaga` · `Atenção`

| Coluna | Grafia |
|---|---|
| **Perfil** | a denominação publicada, com o **código** ao lado — nunca em coluna própria; o código sozinho quando não houver denominação (`FR-607`) |
| **Localidade** | como publicada; **nada** quando o Perfil não a declara — *"não informada"* afirmaria uma omissão que o Edital pode nunca ter tido |
| **Vagas imediatas** | o número. `0` é **zero legítimo** num Perfil de cadastro de reserva |
| **Cadastro de reserva** | *"não há"* · *"limitado a N"* · *"ilimitado"* — as **três**, nunca duas |
| **Submetidas** | o número; marcado **parcial** com o período aberto |
| **Inscr./vaga** | a razão, ou `—` com *"não se aplica: não há vaga imediata"* |
| **Atenção** | as marcas do Perfil, em texto, legíveis sem cor |

---

## 4. O que a página declara quando a soma não fecha

Havendo inscrição cujo Perfil **saiu da versão vigente**, a expansão declara, em texto:

> *"N inscrições foram para Perfis que a versão vigente não tem mais — elas contam no total do
> Edital e não aparecem acima."*

**A diferença é dita, não escondida** (`FR-613a`). Um total que não fecha com as partes, sem
explicação, é pior que qualquer um dos dois números sozinho. Na ausência da diferença, a frase não
existe — ressalva que só aparece quando há ressalva, como a `040` aprendeu.

**E é dita em texto, nunca em linha.** O sistema **não** cria *"Outros"*, *"Removidos"* nem *"Sem
Perfil"* na tabela para acomodá-las: isso inventaria na tela um Perfil que o Edital nunca publicou.
Fazer a conta fechar assim é pior que não fechar.

---

## 5. A marca do Edital

**Cada espécie declara o seu próprio denominador**, porque eles são conceitualmente distintos
(`FR-614`):

| Espécie | Denominador | O que a linha escreve |
|---|---|---|
| **sem procura** | **todos** os Perfis vigentes | *"2 de 4 Perfis sem nenhuma inscrição"* |
| **demanda abaixo da oferta** | só os que **publicam vaga imediata** | *"1 de 3 Perfis com vaga imediata abaixo da oferta"* |
| qualquer uma, com **um** Perfil vigente | — | a mensagem do próprio Perfil, sem contagem |
| nenhuma espécie | — | `—` |

**As duas contam separado**, e as duas podem aparecer na mesma linha.

*"2 de 5" num Edital em que só três Perfis publicam vaga é aritmeticamente verdadeiro e
institucionalmente enganoso: dois dos cinco não tinham como estar abaixo de coisa nenhuma.*

---

## 6. Operação

- Abre e fecha **por teclado** — é `<details>`, e o comportamento é do navegador (`FR-619`).
- O estado é declarado no elemento (`open`), que é o que o leitor de tela anuncia.
- **Sem JavaScript**, sem requisição, sem parâmetro.

O filtro *Somente com atenção* é o oposto: ele **é** parâmetro, recarrega, e move consolidado e
tabela juntos — como os demais filtros da `040`.

---

## 7. O requisito da `040` que esta feature substitui

A **`FR-602` da `040`** — *"a tabela MUST marcar duas situações, derivadas por aritmética sobre os
números que ela já apresenta"* — calculava as marcas **sobre o agregado do Edital**.

Ela é substituída pela `FR-613` mais a `FR-614`: as mesmas duas espécies, calculadas **no Perfil**,
com a linha resumindo. **O conjunto de Editais marcados muda** — um com razão global acima de 1 e um
Perfil vazio passa a receber marca —, e é por isso que a substituição é escrita e não deslizada.
