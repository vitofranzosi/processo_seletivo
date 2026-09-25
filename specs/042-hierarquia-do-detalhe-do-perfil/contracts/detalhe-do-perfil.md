# Contrato — o detalhe do Perfil

**Feature**: `042-hierarquia-do-detalhe-do-perfil` · **Data**: 2026-09-21

> **Contrato de interface.** Nenhum endpoint, **nenhum parâmetro de consulta novo** e nenhuma chave
> alterada. O que é público para outro agente é a **estrutura**, as **colunas** e as **grafias**.

---

## 1. A rota e os parâmetros não mudam

`GET /gestao/visao-geral`, os mesmos parâmetros da `041` — inclusive `ordem=recentes`, cuja
**chave** é preservada. *Os rótulos dos controles mudam; a chave não, porque trocá-la quebraria
endereços guardados sem ganho nenhum (`R-007`).*

---

## 2. A estrutura: um grupo de linhas por Edital

```text
<tbody>                     ← um por Edital (R-002)
  <tr>                        a linha do Edital, sete colunas
  <tr><td colspan=8>          a expansão, recuada e com régua à esquerda
       <details>              recolhido, com marcador de divulgação
         <summary>            "▸ Mostrar 2 Perfis de vaga"
         <table>              a região filha
</tbody>
```

**`<tbody>` por Edital não é enfeite**: é o que faz o **separador** entre Editais ser do grupo, e
não da linha — e é o que permite régua e recuo **sem** posicionamento e **sem** `:has()`. O caso
vazio tem o seu próprio grupo.

**A segunda `<tr>` e o `<details>` dentro do `<td>` continuam como a `041` os deixou.** Esta feature
não toca no mecanismo.

---

## 3. As colunas: uma de identidade, cinco de dado

| # | Coluna | Conteúdo |
|---|---|---|
| 1 | **Perfil** | a denominação, e abaixo a **identidade secundária** |
| 2 | Vagas imediatas | o número; `0` é zero legítimo |
| 3 | Submetidas | o número; marcado **parcial** com o período aberto |
| 4 | Em preenchimento | o número |
| 5 | Inscr./vaga | a razão, ou `—` com o motivo |
| 6 | Atenção | o **rótulo curto**, ou `—` |

**Seis na tela.** *Cadastro de reserva* **não é coluna** — saiu para a identidade (`FR-627`).

### A identidade secundária

> `DOC-INFO · Campus Serra · CR limitado a 6`

| Parte | Quando aparece |
|---|---|
| código | quando publicado |
| localidade | quando publicada, **como publicada** |
| reserva | **só quando há** — *"CR limitado a N"* ou *"CR ilimitado"* |

**Não havendo reserva, nada é escrito**, e a ausência do metadado é a representação (`FR-626`).
Não havendo nenhuma das três, a linha secundária não existe.

---

## 4. A atenção, uma vez por granularidade

| Onde | O que a tela escreve |
|---|---|
| **Edital** | *"1 de 2 Perfis sem nenhuma inscrição"* · *"2 de 3 Perfis com vaga imediata abaixo da oferta"* — **com** o denominador de cada espécie |
| **Perfil** | *"Sem procura"* · *"Demanda abaixo da oferta"* — rótulo curto |
| um Perfil vigente | a mensagem do próprio Perfil, sem contagem — como a `041` decidiu |

**A mesma frase não aparece nas duas** (`FR-628`).

---

## 5. O controle de expansão

```text
▸ Mostrar 2 Perfis de vaga        (recolhido)
▾ Ocultar 2 Perfis de vaga        (aberto)
```

- O **marcador** é desenhado pela folha, é decorativo, e fica **fora** do nome acessível: quem ouve
  a tela recebe o estado por `open` (`R-001`).
- Os **dois rótulos** vivem no documento, e `details[open]` alterna qual aparece. **Nenhum
  JavaScript**, e nenhum `content` de CSS carregando rótulo de ação (`R-003`).

---

## 6. A subordinação, e o que muda com a largura

| | Desktop | Telefone |
|---|---|---|
| Régua à esquerda | sim | **sim** |
| Recuo | confortável | **mínimo** |
| Região filha mais estreita que a principal | **exigido** | **não exigido** — a moldura da `040` já governa |
| Rolagem da página | — | `scrollWidth` **igual** a `clientWidth`; a tabela rola **dentro** da moldura |

*A medida de 98% foi feita no desktop. Transformá-la em invariante de qualquer largura faria a
feature melhorar o monitor piorando o telefone (`FR-623`, `R-004`).*

---

## 7. Os controles de ordenação

| Controle | Opções | Chave |
|---|---|---|
| **Ordenar por** | Data do Edital · Vagas · Inscrições submetidas · Inscr./vaga | `ordem` — **inalterada** |
| **Ordem** | Decrescente · Crescente | `sentido` — **inalterada** |

**Nenhuma opção de critério embute direção** (`FR-630`). Hoje *"Mais recentes"* combinado com
*"Menor primeiro"* significa *"mais antigos"*, e ninguém lê assim.

---

## 8. O critério da `041` que esta feature substitui

A **`SC-217` da `041`** — *"as **três** espécies de cadastro de reserva são distinguíveis na tela, e
a limitada diz o seu limite"* — descrevia a reserva **como coluna**, com as três escritas.

É substituída pela **`SC-224`**: a espécie deixa de ser coluna, passa à identidade, e a que **não
tem** reserva é representada pela **ausência** do metadado. *Substituir um critério claro por outro
que ainda contivesse a contradição seria pior que não substituir.*
