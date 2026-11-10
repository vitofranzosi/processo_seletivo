# Implementation Plan: Centro de Controle do Edital

**Branch**: `claude/136-centro-de-controle-0cb557` | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/136-centro-de-controle-do-edital/spec.md`

## Summary

Uma página nova, `/gestao/editais/<id>/centro/`, que lê o `Andamento` da `127` e o reorganiza em
quatro camadas: onde estamos e o mapa das oito macrofases; o que fazer agora e o detalhe da fase
consultada; onde cada lista está; administração e histórico. A composição é **pura** — recebe o
`Andamento` já derivado e devolve estruturas de apresentação —, e os textos moram num módulo de
conceitos marcado como provisório. A view chama exatamente as funções que `views.detalhe` já chama,
na mesma ordem, e o detalhe ganha um link de ida e nada mais.

## Technical Context

**Language/Version**: Python 3.12, Django 5 (o monólito do GPS).

**Primary Dependencies**: as do projeto; nenhuma nova. Playwright (grupo opcional `navegador`) só para
a jornada no navegador.

**Storage**: PostgreSQL; **nenhuma escrita**, nenhuma migration.

**Testing**: pytest contra PostgreSQL (`make test-pg`); funções puras com objetos da `127` montados à
mão; integração com os cenários de treinamento da `134` (`carregar_cenarios_de_treinamento`); um caso
de navegador em `tests/navegador/`.

**Target Platform**: a área de gestão (`/gestao/`), navegador comum, de 375 px a 1440 px.

**Project Type**: web, servidor renderiza HTML.

**Performance Goals**: o número de consultas do Centro não cresce com inscrições (FR-4744); o teto é
o do detalhe na mesma situação mais uma folga pequena, porque o Centro chama as mesmas funções.

**Constraints**: CSP em recusa (sem `style=`, `<style>`, `<script>`); toda classe citada no template
com regra numa folha que o guardião lê; o `raise Http404` da view nova entra no inventário da `033`
e o módulo entra em `MODULOS_DE_VIEW`; a página não usa «recorte», «geração» nem «faixa» em texto do
template (a varredura de vocabulário é por lista literal, e a tela não entra nela por não usar os
termos); **nenhuma linha de `andamento.py` nem de `providencias.py` muda** (a `135` as edita em
paralelo).

**Scale/Scope**: três módulos novos (`interface/centro.py`, `interface/conceitos.py`,
`interface/centro_do_edital.py`), um template (`interface/centro_do_edital.html`), uma folha
(`interface/telas/centro.css`), uma rota, um link no `detalhe.html`, a linha do inventário, e os
testes.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | O nome simples vem **antes** do termo do GPS, e o termo continua à vista ("no GPS: congelar a relação"). Nenhum termo do domínio é trocado; os nomes das fases são de apresentação e provisórios (D-006). |
| II. Imutabilidade | Nada é escrito. Publicado só se corrige por Retificação, e a página o diz na fase Edital. |
| III. Segurança | A porta é a do detalhe (`obter_edital`, escopo institucional). Nenhuma permissão nova. O detalhe por lista só para quem via a matriz (D-007). O link de ato só para quem o pratica — é a providência da `127` que decide (`url` vazia para quem não é "sua"). |
| IV. Regras explícitas | Nenhuma regra de disponibilidade: a Conclusão não diz que o Edital pode ser encerrado (FR-4714); o destaque é regra de apresentação dita na tela (D-005); a recusa continua do domínio. |
| V. Rastreabilidade e simplicidade | Spec, plano, tarefas, matriz; nenhuma fila, estado ou tabela. A composição é pura e testável sem banco. |
| VI. Completude de jornada | É o propósito: o trabalho depois da publicação ganha um mapa e um lugar. |

**Gate**: passa. Nenhuma violação a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/136-centro-de-controle-do-edital/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # R-001 a R-010
├── data-model.md        # as estruturas de apresentação
├── contracts/
│   └── pagina.md        # a rota, o contexto e as marcas do HTML que os testes prendem
├── quickstart.md        # como conferir no navegador
├── tasks.md
├── rastreabilidade.md   # na implementação
└── checklists/requirements.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── conceitos.py               # NOVO — nomes simples, grupos, frases; provisórios
├── centro.py                  # NOVO — a composição pura sobre o Andamento
├── centro_do_edital.py        # NOVO — a view (porta do detalhe, mesmas funções)
├── urls.py                    # + a rota `centro-do-edital`
├── templates/interface/
│   ├── centro_do_edital.html  # NOVO — as quatro camadas
│   └── detalhe.html           # + o link de ida (uma linha)
└── static/interface/telas/
    └── centro.css             # NOVO — o mapa, as marcas, o roteiro, a grade

backend/tests/
├── unit/interface/test_centro_composicao.py      # agregar, juntar, destaque, onde, fases
├── interface/test_centro_do_edital.py            # rota, porta, links, aria-current, fixtures
├── integration/treinamento/test_centro_nos_cenarios.py  # C06, C08, C12 × 4 papéis; coerência
├── performance/test_centro_em_escala.py          # orçamento de consultas
├── navegador/test_jornada_do_centro.py           # dobra, 375 px, CSP, teclado
└── test_gramatica_das_portas.py                  # + o módulo em MODULOS_DE_VIEW

specs/033-navegacao-por-capacidade/inventario-das-negativas.md  # + a linha da view
```

**Structure Decision**: a view vai num módulo próprio, como `relatorio.py` e `avisos.py`, e não no
`views.py` de doze mil linhas: o Centro é uma página de leitura com dependências claras, e o módulo
próprio é o que a 138 vai trocar de lugar quando virar o padrão. As funções auxiliares do detalhe
(`_documentos_publicados`, `_marcos_publicados`, `_pendencias`, `_pode_ver_avisos`) são importadas
de `views`, e não copiadas: duas cópias divergiriam na primeira mudança (R-003).

## Phase 0 — Research

Em [research.md](research.md). Nenhum `NEEDS CLARIFICATION` ficou aberto.

## Phase 1 — Design

- [data-model.md](data-model.md): `Macrofase`, `PassoDoRoteiro`, `ItemDeProvidencia`, `ListaNoCentro`,
  `PerfilNoCentro`, `Destaque`, `Centro`; as regras de agregação.
- [contracts/pagina.md](contracts/pagina.md): a rota, as respostas, o contexto do template e as marcas
  do HTML que os testes prendem.
- [quickstart.md](quickstart.md): a conferência dos C06, C08 e C12 com dois papéis.

**Re-avaliação da Constitution Check depois do desenho**: continua passando. O desenho não acrescentou
leitura de banco além das funções do detalhe, nem regra.

## Complexity Tracking

Nenhuma violação.
