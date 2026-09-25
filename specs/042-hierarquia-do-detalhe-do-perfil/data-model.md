# Phase 1 — Modelo de dados: a hierarquia do detalhe

**Feature**: `042-hierarquia-do-detalhe-do-perfil` · **Data**: 2026-09-21

> **O delta é pequeno de propósito.** Esta feature muda **forma**. Nenhuma entidade nasce, nenhuma
> fórmula muda, nenhum campo novo é lido do conteúdo publicado — tudo já vem no snapshot desde a
> `041`. O que segue são **duas** adições às formas de leitura, e por que elas moram no módulo.

---

## 1. `Marca` ganha um rótulo curto

```
Marca
  especie:   SEM_PROCURA | DEMANDA_ABAIXO_DA_OFERTA
  mensagem:  a frase, com denominador quando é resumo de Edital
  rotulo:    o rótulo curto, para o Perfil            ← novo
```

| Onde | O que aparece |
|---|---|
| **Edital** | `mensagem` — *"1 de 2 Perfis sem nenhuma inscrição"* |
| **Perfil** | `rotulo` — *"Sem procura"* |

**Dois campos, e não um derivado do outro** (`R-006`). Cortar a frase para obter o rótulo é frágil e
ilegível; expandir o rótulo para obter a frase perderia o denominador, que é a regra que governa
esta página. Os dois nascem juntos, da mesma espécie.

**A regra**: a mesma frase MUST NOT aparecer nas duas granularidades (`FR-628`).

---

## 2. `PerfilDaLinha` ganha a identidade secundária

```
PerfilDaLinha
  …os campos da 041…
  identidade_secundaria: str    ← derivada de codigo, localidade e reserva
```

> `DOC-INFO · Campus Serra · CR limitado a 6`

**Derivada, e mora no módulo** (`FR-582` da `040`, `R-005`). Decidir **quais** partes existem e
**como** se separam é regra; regra em template é a segunda verdade que aquele requisito proíbe. O
template escreve o que receber.

**A composição, parte a parte:**

| Parte | Quando entra | Grafia |
|---|---|---|
| código | quando publicado e distinto da denominação | literal |
| localidade | quando publicada | literal, **como publicada** |
| cadastro de reserva | **só quando há** | *"CR limitado a N"* · *"CR ilimitado"* |

**Vazio quando não há nenhuma das três**, e aí a linha some inteira — não se escreve *"não
informado"* nem *"não há"*.

---

## 3. A regra que muda de forma, e não de conteúdo

| Regra | Antes (`041`) | Agora (`042`) |
|---|---|---|
| cadastro de reserva | **coluna**, com as três espécies escritas | **identidade**; a ausência do metadado representa que não há (`FR-626`) |
| código e localidade | célula de identidade, cada um em `<span>` | a mesma linha secundária |
| colunas da região filha | identidade + **seis** | identidade + **cinco** (`FR-627`) |
| atenção no Perfil | a frase inteira | o rótulo curto (`FR-628`) |

**Nada mais muda.** `vagas_do_conteudo`, `contagens_por_edital`, `perfis_do_edital`, `_marcas`,
`_marcas_do_edital`, `_razao` e `ler` continuam como a `041` os deixou — e é por isso que o teste de
orçamento de consulta dela vale sem alteração.

---

## 4. O que **não** entra

| Ausente | Por quê |
|---|---|
| um tipo para a linha de identidade | é uma `str` derivada; um tipo seria estrutura antes da regra que a consuma |
| um campo para "tem marcador de divulgação" | é decoração de folha, não dado |
| qualquer coisa ligada a `<tbody>` | agrupação é do template: o módulo já devolve uma linha por Edital, e agrupar é desenhar |
