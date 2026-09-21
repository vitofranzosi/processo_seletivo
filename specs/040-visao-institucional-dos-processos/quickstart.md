# Quickstart — validar a visão institucional

**Feature**: `040-visao-institucional-dos-processos` · **Data**: 2026-09-21

O cenário de ponta a ponta que o **Princípio VI** exige e que `SC-206` descreve: executável **pela
interface administrativa**, sem shell de banco e sem canal alheio ao ator.

> Este é um guia de validação. O detalhe das formas está em [data-model.md](./data-model.md); o das
> garantias, em [contracts/pagina-visao-geral.md](./contracts/pagina-visao-geral.md).

---

## 1. Pré-requisitos

**Banco próprio para esta worktree.** Suítes e servidores paralelos disputam o mesmo banco e se
derrubam.

```bash
cd backend && make migrate && make provisionar-papeis
```

A saída do provisionamento informa `N de M`. **Se o primeiro número vier `0`, a segunda passada não
rodou** — e a ordem correta é provisionar, migrar, provisionar de novo.

**Dependências de desenvolvimento**, numa worktree nova:

```bash
cd backend && uv sync --extra dev
```

---

## 2. Semear o cenário

`seed_demo` produz dois Editais — um com prazo aberto e um com resultado divulgado —, que é
exatamente a mistura de fases que `SC-207` e `FR-595` exercitam.

```bash
cd backend && make seed-demo
```

**Para o caso que `SC-213` cobra** — um Edital com um Perfil de vagas imediatas e outro
exclusivamente de cadastro de reserva — monte-o **pela interface**, na composição de Perfis: o
elenco do `seed_demo` não o produz.

**Para o caso de `SC-208`** basta o que já existe: um Edital em elaboração (vagas ausentes) e um
publicado sem inscrição (submetidas `0`).

---

## 3. Subir o servidor

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true make runserver
```

Sem a variável, `/gestao/` devolve **503**. O seletor de identidade só existe fora de produção, e
produção recusa subir com ele ligado.

Abra `http://localhost:8000/gestao/` — **`localhost`, e não `127.0.0.1`**: o padrão de
`ALLOWED_HOSTS` é só o primeiro, e o segundo devolve `DisallowedHost`.

Identifique-se como **`gestor`**.

---

## 4. O percurso a validar

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 1 | Na lista de Processos, achar o caminho para a visão geral | o link existe para o `gestor` | `FR-605` |
| 2 | Abrir a página **sem parâmetro** | recorta pelo **ano corrente** e **declara o recorte** na tela | `FR-599` · `SC-214` |
| 3 | Ler os quatro números | Editais · Vagas publicadas · Submetidas · Inscr./vaga — com os denominadores **abaixo** de cada um | `FR-585` |
| 4 | Ler a tabela | sete colunas; o Edital em elaboração mostra `—` em Vagas, e não `0` | `FR-594` · `SC-208` |
| 5 | Achar o Edital publicado sem inscrição | mostra `0` em Submetidas — **zero legítimo** — e a marca *sem procura* | `FR-591` · `FR-602` |
| 6 | Achar o Edital só com cadastro de reserva | Vagas `0`, Inscr./vaga `—`, demanda legível | `FR-589` · `SC-213` |
| 7 | No Edital **misto**, conferir a razão | usa **só** a demanda do Perfil com vaga imediata, e a linha declara a população | `FR-588` · `SC-213` |
| 8 | Conferir o consolidado contra a linha | concordam; o consolidado diz quantos Editais ficaram fora da razão | `FR-590` |
| 9 | Ler o Edital com inscrições abertas | Submetidas marcada **parcial**, com o motivo; o consolidado diz quantos somandos são parciais | `FR-595` |
| 10 | Ordenar por *Inscr./vaga*, nos dois sentidos | as ausências ficam **ao fim** nas duas | `FR-601` |
| 11 | Filtrar por *situação do período* = aberto | o resultado é correto, e o filtro é aplicado **depois** da materialização — sobre o conjunto que ano, situação e busca já reduziram | `FR-598` |
| 12 | Clicar numa linha | chega ao Edital daquela linha | `FR-600` |
| 13 | Ler a declaração da página | nomeia matrícula efetivada, obsolescência de apuração e os indicadores ainda não apresentados | `FR-596` · `SC-212` |
| 14 | Abrir um Edital pela visão e voltar | os números da tela dona batem com os da visão | `SC-207` |

### A verificação de autorização

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 15 | Sair, entrar como **`elaborador`** | **não** vê o caminho na lista de Processos | `FR-605` |
| 16 | Colar `/gestao/visao-geral` na barra | **403** com recusa explicada — nunca 404, nunca 500 | `FR-604` · `SC-211` |

### A verificação de privacidade

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 17 | Ver o código-fonte da página, com inscrições submetidas presentes | nenhum nome, CPF, e-mail, telefone ou identificador de pessoa | `FR-584` · `SC-210` |

---

## 5. A verificação automatizada

```bash
cd backend && make lint check test-pg
```

**`test-pg`, e não `test`.** Sem o par `TEST_DB_ENGINE=postgresql` **e** o usuário do banco, a suíte
cai para SQLite em silêncio e dezenas de casos falham por razões que não são do produto.

**`lint` são dois passos** — `ruff check` **e** `ruff format --check`. Rodar só o primeiro declara
verde local e quebra no CI.

**Não edite arquivo durante a execução**: template criado ou apagado no meio de `test-pg` produz
falha que não é do diff.

### Os quatro arquivos desta feature

```bash
cd backend && uv run pytest \
  tests/unit/test_visao_institucional.py \
  tests/interface/test_visao_geral.py \
  tests/authorization/test_visao_institucional.py \
  tests/performance/test_visao_institucional.py -q
```

### O guardião que um PR de documentação também aciona

```bash
cd backend && uv run pytest tests/test_citacoes_de_requisito.py -q
```

Ele varre `specs/**/*.md` e `backend/**/*.{py,html,js}` e falha se alguma citação `FR-`, `SC-`,
`UX-` ou `D-` apontar para identificador que nenhuma spec define.

### E o que só falha se alguém esquecer

Se a prosa visível da página usar **recorte**, **geração** ou **faixa**, a tela precisa entrar na
lista literal de `tests/test_vocabulario_da_composicao.py` **no mesmo commit** e definir o termo em
`<dfn>`. A lista não é `glob`: sem a linha, a tela escapa da regra **em silêncio**, e nenhuma falha
aparece (`R-006`).

---

## 6. O critério de pronto

`SC-206` está satisfeito quando estas quatro perguntas são respondidas **na primeira tela**, sem
abrir Processo nenhum:

> *Quantos Editais tivemos no período? Quantas vagas ofertamos? Quanta procura recebemos? Quais
> ficaram sem ninguém?*

E quando a própria página diz, em texto, **o que ela não responde**.
