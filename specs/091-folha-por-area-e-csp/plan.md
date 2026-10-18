# Implementation Plan: A folha da gestão por área, o estilo de cada tela em arquivo, e a política de segurança de conteúdo

**Branch**: `claude/folha-por-area-e-csp-091-cce475` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

O `interface/static/interface/gestao.css` da `089` se divide em sete arquivos por área em
`interface/static/interface/gestao/`, carregados por `<link>` de uma lista só, na ordem de carga; uma
regra só troca de ordem com outra quando a prova do R-003 mostra que elas não disputam propriedade em
elemento nenhum, e as duplicadas saem com a mesma prova. Os cinco parciais `_estilo_*` e o estilo
próprio de cada tela viram arquivos em `interface/static/interface/telas/`, carregados pelo
`{% block estilo_da_pagina %}`, agora com `<link>`s no `<head>`; o `<style>` sai das bases da gestão e
da página de acesso, o do `404.html` vai para `shared/erro.css`, o do fragmento do protótipo para
arquivo. Os quatro `style=""` da gestão viram classe. Um middleware do projeto põe a
`Content-Security-Policy` em todo HTML sob `/gestao/` e a mesma política em modo de observação no resto
do HTML; o htmx é configurado por `<meta>` para não injetar estilo nem avaliar código. Nenhuma
migration, permissão, view, endereço, consulta ou texto muda.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2.17 (sem o middleware de CSP, que chega na 6.0),
PostgreSQL (nada de banco muda).

**Primary Dependencies**: `django.contrib.staticfiles` e a tag `estatico` da `089`. Nenhuma dependência
nova.

**Storage**: N/A.

**Testing**: pytest (`make test-pg`); os guardiões de folha em `tests/interface/` e `tests/portal/`,
pelo apoio `tests/interface/folha.py`; a prova visual e de console pelo inventário de
`doc/inventario-visual-da-gestao-2026-10-16/`, com Chrome sem cabeça.

**Target Platform**: o runserver local (`DEBUG=True`, estáticos pelo `staticfiles`) e o caminho de
produção do guia (`doc/implantacao-em-producao-ubuntu.md`): nginx servindo os `static/` da release por
`alias`, `immutable` para o que tem `?v=`.

**Project Type**: monólito web Django, interface por modelos.

**Performance Goals**: a visão geral perde ≈ 12 KB de HTML; as demais telas ganham no máximo 1 KB de
`<link>`; na primeira visita, os sete arquivos da folha comum em paralelo; daí em diante, cache.

**Constraints**: zero mudança visual; nenhum guardião enfraquecido; o teto de 120.000 bytes da
Distribuição fica; sem dependência nova; `.claude/launch.json` intocado.

**Scale/Scope**: 1 folha de 1.471 linhas, 7 arquivos de área; 27 modelos com bloco de estilo e 5
parciais; 1 fragmento; 1 página de erro; 4 atributos `style`; 31 arquivos de teste candidatos a
guardião (R-010).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Negar por padrão (III, IV)**: a política é a forma de "negar por padrão" do navegador — nada
  embutido, só a própria origem. Nenhuma view, permissão ou escopo muda; os estáticos já são públicos
  e não carregam dado.
- **Imutabilidade e preservação (II)**: nenhum dado normativo, tabela ou documento publicado muda; os
  PDFs oficiais não saem destes modelos.
- **Linguagem ubíqua (I)**: nomes em português (`gestao/moldura.css`, `telas/visao-geral.css`,
  `PoliticaDeConteudoMiddleware`, `folhas_da_gestao`).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: a peça nova de produção é um middleware de uma constante e três ramos, e uma
  tag de inclusão; o resto é mover. As ferramentas de prova ficam na pasta do inventário, fora do
  produto.
- **Completude de jornada (VI)**: o inventário inteiro antes e depois, nos dois estados da barra, com o
  console de cada tela; a página de acesso, a de erro e duas do portal.

Sem violação a justificar. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/091-folha-por-area-e-csp/
├── spec.md
├── plan.md
├── research.md          # R-001..R-013: levantamento, áreas, prova de ordem, política
├── quickstart.md        # o roteiro da prova
├── rastreabilidade.md   # requisito → onde é provado
├── tasks.md
└── checklists/requirements.md
```

`data-model.md` não se aplica: não há entidade. `contracts/` também não: o cabeçalho da política é
o contrato com o navegador, e está no R-008, testado pela suíte.

### Source Code

| Peça | Mudança |
|---|---|
| `interface/static/interface/gestao/{base,moldura,componentes,formularios,tabelas,telas,impressao}.css` | novos: as regras do `gestao.css` por área, com os comentários (R-002, R-003) |
| `interface/static/interface/gestao.css` | sai (D-002) |
| `interface/static/interface/telas/*.css` | novos: um por parcial e um por tela com regras próprias, mais o do fragmento do protótipo (R-006) |
| `interface/templates/interface/_estilo_*.html` | saem (FR-2095) |
| `shared/static/shared/erro.css` | novo: o `<style>` do `404.html` |
| `shared/estaticos.py` | `FOLHAS_DA_GESTAO`, a tag `{% folhas_da_gestao %}`, e a verificação de sistema estendida a todo `{% estatico %}` dos modelos (R-004, R-006) |
| `shared/politica_de_conteudo.py` | novo: a política e o `PoliticaDeConteudoMiddleware` (R-008) |
| `config/settings/base.py` | o middleware, primeiro da lista |
| `interface/templates/interface/base.html`, `base_de_acesso.html` | `<link>`s no lugar do `<style>`; o bloco no `<head>`; o `<meta>` do htmx; a classe do `<svg>` |
| os 27 modelos com bloco, o fragmento do protótipo, `minhas_etapas.html`, `_serie_de_inscricoes.html`, `404.html`, `portal/base.html` (só o `<meta>` do htmx) | `<link>` no bloco; classe no lugar de `style` |
| `backend/tests/…` | os guardiões repontados (R-010); `tests/interface/test_politica_de_conteudo.py` e os guardiões novos |
| `doc/implantacao-em-producao-ubuntu.md` | a nota da política e a linha da lista de verificação; `location` não muda (`/static/interface/` já cobre os subdiretórios) |
| `doc/inventario-visual-da-gestao-2026-10-16/` | `ordem.py`, `areas.py`, `duplicadas.py`, `mutacoes.py`, a leitura de violações no `capturar.py`, `estilos.py` como conjunto; `depois-da-091/` |

## Ordem

0. **Esperar o merge do PR #307** (`gh pr view 307 --json state`), e `git merge origin/main`.
1. Medir antes: peso (R-012), inventário nos dois estados da barra mais pares de ruído, as bases, a
   impressão, e o console — no antes as violações não existem, porque não há política; o script de
   console é exercitado contra uma página com política plantada.
2. **B e C primeiro**, que não mudam a ordem de nada: parciais, blocos, fragmento, página de erro e
   `style=""` para arquivo e classe. Repontar os guardiões que liam modelos de tela.
3. **A**: `areas.py` classifica as regras; `ordem.py` prova as trocas; `duplicadas.py` lista e prova;
   os sete arquivos; `FOLHA_COMUM` repontado; mutações.
4. **D**: o middleware, o `<meta>` do htmx, os guardiões de embutido, o teste de cabeçalho; o guia.
5. Medir depois e comparar — inventário, pixels, regras aplicadas como conjunto, impressão, console;
   `make lint check test-pg`.
6. `/code-review` no PR, sem `--comment`; corrigir os achados confirmados.

## Verificação

`cd backend && make lint check test-pg DB_NAME=ps_091 POSTGRES_USER=$USER` com
`LC_ALL=pt_BR.UTF-8`, depois de `uv sync --extra dev --extra assistente`; o roteiro do
[quickstart](quickstart.md).
