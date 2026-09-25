# Quickstart — validar a hierarquia do detalhe

**Feature**: `042-hierarquia-do-detalhe-do-perfil` · **Data**: 2026-09-21

O cenário que o **Princípio VI** exige. Esta feature é **perceptiva**: a `SC-222` é leitura humana,
e nenhum teste a substitui. O que os números abaixo fazem é prender as **consequências** dela.

> Guia de validação. As formas estão em [data-model.md](./data-model.md); as garantias, em
> [contracts/detalhe-do-perfil.md](./contracts/detalhe-do-perfil.md).

---

## 1. As medidas de **antes**, para comparar contra

Tiradas na `041` em 21/09, com o `seed_demo` aplicado. **Anote as suas antes de mudar qualquer
coisa** — a máquina e a fonte variam, e o que importa é a diferença.

| Medida | Antes |
|---|---|
| Largura da tabela filha | **781 px** |
| Largura da tabela principal | **797 px** — a filha ocupa **98%** |
| Cabeçalho filho | `12,16 px` · peso `600` |
| Cabeçalho principal | `13,12 px` · peso `600` |
| `<tbody>` na tabela principal | **1** |
| Recuo da célula de expansão | **8 px** |
| Marcador do `<summary>` | **nenhum** — `display:inline-block` o apaga |

Para relê-las a qualquer momento, no console do navegador:

```js
const f=document.querySelector('.tabela-de-perfis'), p=document.querySelector('.tabela-da-visao');
({ filha: f.getBoundingClientRect().width, principal: p.getBoundingClientRect().width,
   cabFilho: getComputedStyle(f.querySelector('thead th')).fontSize,
   cabPai: getComputedStyle(p.querySelector('thead th')).fontSize,
   grupos: document.querySelectorAll('.tabela-da-visao>tbody').length })
```

---

## 2. Subir

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true make runserver
```

`http://localhost:8000/gestao/visao-geral` — **`localhost`**, e como **Gestor**. O `seed_demo`
basta: ele produz Editais de um e de dois Perfis, com as três espécies de reserva.

---

## 3. O percurso

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 1 | Olhar a tabela com tudo recolhido | cada Edital é um **grupo**: a linha e a expansão sem borda entre elas, e a borda separando os Editais | `R-002` |
| 2 | Ler o controle de expansão | **"▸ Mostrar 2 Perfis de vaga"** — com marcador, e não uma caixa solta | `FR-629` · `R-001` |
| 3 | Expandir | o rótulo vira **"▾ Ocultar…"**, sem recarregar a página | `FR-622` · `R-003` |
| 4 | Olhar a região aberta | **recuada**, com régua à esquerda, e **mais estreita** que a tabela principal | `FR-623` · `SC-223` |
| 5 | Comparar os dois cabeçalhos | o filho é visivelmente **menos dominante** | `FR-624` · `SC-223` |
| 6 | Contar as colunas da região filha | **seis**: identidade + cinco de dado. **Nenhuma** é cadastro de reserva | `FR-627` · `SC-224` |
| 7 | Ler um Perfil **com** reserva | a espécie e o limite estão na identidade: `DOC-INFO · Campus Serra · CR limitado a 6` | `FR-626` |
| 8 | Ler um Perfil **sem** reserva | **nada** é escrito sobre reserva — nem *"não há"* | `FR-626` · `SC-224` |
| 9 | Ler um Perfil sem código e sem localidade | a linha secundária **não existe** | `FR-626` |
| 10 | Comparar a atenção do Edital com a do Perfil | o Edital **resume com denominador**; o Perfil usa **rótulo curto**; a frase não se repete | `FR-628` · `SC-225` |
| 11 | Ler os controles de ordenação | **Ordenar por**: Data do Edital · Vagas · Inscrições submetidas · Inscr./vaga; **Ordem**: Decrescente · Crescente. Nenhuma opção de critério embute direção | `FR-630` · `SC-227` |
| 12 | Trocar critério e direção | a tabela reordena, e a **chave da URL** continua `ordem=` e `sentido=` | `R-007` |
| 13 | Abrir e fechar **só com o teclado** | continua funcionando — `<details>` nativo | `FR-622` · `SC-226` |
| 14 | Ver o código-fonte | **zero** `<script>` novo, e o `<details>` segue dentro do `<td>` | `SC-226` |
| 15 | Inspecionar a legenda da tabela filha | está no documento e **não** é desenhada | `FR-625` |

### O que a `SC-222` pede, e que nenhum número entrega

| # | Ação | O que julgar |
|---|---|---|
| 16 | Expandir um Edital, ler a região, e seguir para o próximo | **Você continuou sentindo que está na tabela de Editais, com uma linha aberta — ou entrou noutro lugar e voltou?** É a pergunta da feature, e a resposta é sua |

### No telefone

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 17 | Repetir em 375 px | a régua continua; o recuo encolhe; a leitura das métricas **não piora** em relação à `041`; `documentElement.scrollWidth` continua igual a `clientWidth` | `FR-623` · `R-004` |

---

## 4. A verificação automatizada

```bash
cd backend && make lint check test-pg
```

**`test-pg`, e não `test`.** **`lint` são dois passos.** E **não edite arquivo durante a execução**.

### Os guardiões que esta feature aciona

```bash
cd backend && uv run pytest tests/interface/test_visao_geral.py tests/unit/test_visao_institucional.py tests/interface/test_acessibilidade.py tests/interface/test_larguras.py tests/performance/test_visao_institucional.py -q
```

O de **orçamento de consulta** vale sem alteração — esta feature não toca leitura nenhuma, e se ele
mudar de número é sinal de que o plano saiu do problema.

O de **classes órfãs** alcança a folha da página, inclusive num parcial, porque resolve `include`
transitivamente desde a `041`. Classe nova sem regra falha ali.

---

## 5. O critério de pronto

A `SC-222`, dita como ela é:

> Quando o usuário expande um Edital, deve continuar percebendo que está lendo **a mesma linha do
> portfólio, agora aprofundada** — e não que entrou em uma segunda tabela independente.

E as três consequências que se medem: **filha mais estreita** que a principal, **cabeçalho menor**,
e **seis colunas**, nenhuma delas cadastro de reserva.
