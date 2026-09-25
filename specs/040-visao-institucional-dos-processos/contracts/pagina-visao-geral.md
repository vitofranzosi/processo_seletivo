# Contrato — a página `/gestao/visao-geral`

**Feature**: `040-visao-institucional-dos-processos` · **Data**: 2026-09-21

> **Contrato de interface, e não de API.** Esta feature não expõe endpoint: a Constituição pede
> contratos explícitos para APIs, e aqui o que é público para outro agente é **a rota, os parâmetros
> de consulta e as grafias que a tela garante**. É esse conjunto que um teste prende e que uma
> mudança futura não pode quebrar em silêncio.
>
> **Nenhuma entidade de persistência atravessa a fronteira** — o contexto do template recebe as
> formas de leitura do `data-model.md`, e não modelos.

---

## 1. A rota

| | |
|---|---|
| Método | `GET` |
| Caminho | `/gestao/visao-geral` |
| Nome | `interface:visao-geral` |
| Corpo | nenhum — a página não escreve nada |

**`GET` e só `GET`.** A página não tem `POST`, e a ausência é garantia: um módulo de leitura que
ganha verbo de escrita deixou de ser o que a `FR-582` descreve.

---

## 2. Os parâmetros de consulta

Todos opcionais. Todos **saneados**: valor fora do conjunto aceito vira o padrão e nunca alcança a
consulta — o padrão de `portal/leitura.py::consulta_da_vitrine`.

| Parâmetro | Valores aceitos | Padrão | Requisito |
|---|---|---|---|
| `ano` | um inteiro presente em `Edital.year` do escopo, ou `todos` | **o ano corrente** | `FR-597`, `FR-599` |
| `situacao` | um dos seis `Edital.Status` | vazio — todas | `FR-597` |
| `periodo` | `futuro` · `aberto` · `encerrado` · `nao-designado` | vazio — todos | `FR-597` |
| `busca` | texto; casa título do Processo, código institucional e número do Edital | vazio | `FR-597` |
| `ordem` | chave do conjunto `ORDENS` | a ordem natural do Edital | `FR-601` |

**A ordem de aplicação é parte do contrato** (`FR-598`):

```text
escopo → ano → situação → busca        ← relacionais, ANTES de materializar
        ↓
  versões vigentes materializadas       ← um snapshot por Edital do conjunto já reduzido
        ↓
período                                 ← depende do conteúdo, DEPOIS
        ↓
ordem
```

**Inverter isso quebra o contrato**, e não só o desempenho: aplicar `periodo` antes seria impossível
— a situação do período mora no snapshot.

---

## 3. O que a página garante

### 3.1 Os quatro números, com os denominadores

O consolidado apresenta **quatro** números principais — Editais, Vagas publicadas, Inscrições
submetidas, Inscr./vaga — e **os denominadores acompanham o número que explicam**, nunca como
números concorrentes (`FR-585`).

### 3.2 As sete colunas

`Processo / Edital` · `Situação` · `Período` · `Vagas` · `Submetidas` · `Em preenchimento` ·
`Inscr./vaga`. Cada linha leva ao Edital (`FR-600`).

### 3.3 A gramática da ausência e do zero

| Situação | O que a página escreve |
|---|---|
| a fonte produziu zero | `0` |
| métrica não se aplica ao objeto | `—` · *"não se aplica: …"* |
| a fase não chegou | `—` · *"ainda não …"* |
| o Edital não tem conteúdo vigente | `—` · *"sem conteúdo publicado"* |
| o número existe e vai mudar | o número · **parcial** · o motivo |

**Duas garantias simétricas** (`FR-591`): **nenhum** `0` onde há ausência, e **nenhuma** ausência
onde a fonte produziu zero.

### 3.4 A declaração do que não se mede

Texto visível, sempre presente (`FR-596`, `SC-212`), nomeando: **matrícula efetivada** — não medida,
sem fonte canônica —; **obsolescência de apuração** — reportada pela Supervisão do Processo —; as
**dimensões que o domínio não tem**; e **os indicadores que esta entrega ainda não apresenta**.

### 3.5 Ausência de dado pessoal

Nenhum nome, CPF, e-mail, telefone ou identificador de pessoa — em texto, em atributo ou em URL
(`FR-584`). **Verificável por varredura do HTML renderizado** com inscrições submetidas presentes
(`SC-210`).

---

## 4. As respostas

| Situação | Status | Corpo |
|---|---|---|
| ator identificado e com `visao:consultar` | `200` | a página |
| ninguém identificado | `302` | para `interface:identificar` |
| identificado sem `visao:consultar` | `403` | `interface/recusa.html`, pelo middleware de recusa |
| escopo institucional alheio | — | não ocorre: o escopo **filtra**, e o resultado é um recorte vazio, nunca um 404 |

**A última linha é decisão, e não omissão.** Em telas de objeto, escopo alheio devolve 404 para que
objeto inexistente e objeto de outra unidade sejam indistinguíveis (`FR-480` da `033`). Aqui não há
objeto endereçado: a página é uma listagem, e listagem de escopo alheio simplesmente não existe —
o ator vê o **seu** escopo, sempre.

**A recusa é do servidor.** Esconder o caminho em `lista.html` não a substitui: quem montar a URL à
mão recebe o mesmo `403` (`FR-605`, e `FR-482` da `033`).

---

## 5. O contrato interno que esta feature altera

`publicacoes.application.selectors.versoes_vigentes(*, editais=None, at=None)` — **nova**, extraída
de `selecoes_publicas` (`R-003`).

| | |
|---|---|
| Devolve | a `VersaoConsolidada` vigente de cada Edital pedido, em **duas** consultas |
| `editais` | restringe o conjunto; `None` mantém o comportamento de varrer o escopo |
| `at` | o instante da vigência; `None` é agora |
| **Não** decide | visibilidade pública — quem exclui o cancelado é `selecoes_publicas`, e continua sendo |

**`selecoes_publicas` passa a consumi-la e mantém o comportamento observável**, inclusive a exclusão
do Edital cancelado. É a primeira coisa a implementar, e a suíte do portal verde é a condição para
seguir (plano, fase 1).
