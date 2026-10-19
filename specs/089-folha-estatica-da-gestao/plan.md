# Implementation Plan: A folha comum da gestão em arquivo estático, sem mudar regra nenhuma

**Branch**: `claude/folha-estatica-089-1fcd9d` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

## Summary

As regras do `<style>` do `interface/base.html` vão, na mesma ordem e byte a byte, para
`interface/static/interface/gestao.css`; os tokens de `shared/templates/shared/_tokens.css.html` vão
para `shared/static/shared/tokens.css`, e o parcial sai. As quatro páginas que incluíam os tokens — a
base da gestão, a da página de acesso, a do portal e o `404.html` — passam a carregá-los por `<link>`;
a base da gestão carrega também a folha comum, e fica com um `<style>` que só tem o
`{% block estilo_da_pagina %}`. Os `{% comment %}` da folha viram `/* */` junto da regra. O endereço de
cada folha leva `?v=` com o resumo do conteúdo, por uma tag de modelo sem dependência nova. Os
guardiões que liam a folha no modelo passam a ler o arquivo estático, ou a folha que a página
renderizada carrega, e cada um é provado por mutação. Nenhuma migration, permissão, view, endereço de
tela, consulta, classe ou regra nova.

## Technical Context

**Language/Version**: Python 3.13, Django 5, PostgreSQL (nada de banco muda).

**Primary Dependencies**: `django.contrib.staticfiles` (já instalado). Nenhuma dependência nova.

**Storage**: N/A.

**Testing**: pytest (`make test-pg`); os guardiões de folha em `tests/interface/` e
`tests/portal/`; a prova visual pelo inventário de `doc/inventario-visual-da-gestao-2026-10-16/`.

**Target Platform**: o runserver local (`DEBUG=True`, estáticos servidos pelo `staticfiles`) e o
caminho de produção do guia (`doc/implantacao-em-producao-ubuntu.md`), em que o nginx serve os
diretórios `static/` da release por `alias`, com `Cache-Control: no-cache`, sem `collectstatic` (não
há `STATIC_ROOT`, lacuna I-3 do guia).

**Project Type**: monólito web Django, interface por modelos.

**Performance Goals**: cada resposta HTML da gestão perde as regras comuns (≈ 53 KB); a folha comum
viaja uma vez por sessão do navegador e é revalidada (304) dali em diante.

**Constraints**: zero mudança visual; a cascata na mesma ordem; nenhum guardião enfraquecido; o teto
de 120.000 bytes da Distribuição fica; nada de CSP.

**Scale/Scope**: 1 folha de 1.471 linhas (≈ 930 regras, 162 comentários), 4 páginas-base, os
guardiões listados no R-005 da pesquisa.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Negar por padrão (III, IV)**: os estáticos já são públicos e não passam por autorização; a folha e
  os tokens não carregam dado nenhum. Nenhuma view, permissão ou escopo muda.
- **Imutabilidade e preservação (II)**: nenhum dado normativo, nenhuma tabela, nenhum documento
  publicado muda; os PDFs oficiais não são montados a partir destes modelos.
- **Linguagem ubíqua (I)**: nomes em português (`gestao.css`, `tokens.css`, a tag `estatico`).
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: mover sem mudar. A única peça nova de código é a tag de versão (R-003),
  porque sem ela o passo troca peso por cache velho.
- **Completude de jornada (VI)**: o inventário inteiro é refeito antes e depois, nos dois estados da
  barra, e comparado pixel a pixel contra a linha de ruído; mais a página de acesso, duas telas do
  portal e a página de erro.

Sem violação a justificar. Reavaliado depois do desenho: igual.

## Project Structure

### Documentation (this feature)

```text
specs/089-folha-estatica-da-gestao/
├── spec.md
├── plan.md
├── research.md          # R-001..R-008: decisões e o inventário dos guardiões
├── quickstart.md        # o roteiro da prova
├── rastreabilidade.md   # requisito → onde é provado
├── tasks.md
└── checklists/requirements.md
```

`data-model.md` e `contracts/` não se aplicam: não há entidade nem interface externa nova. O endereço
versionado da folha não é contrato — ninguém fora do sistema o pede.

### Source Code

| Peça | Mudança |
|---|---|
| `backend/processo_seletivo/interface/static/interface/gestao.css` | novo: as regras do `<style>` da base, na ordem, e os comentários como `/* */` (R-001, R-002) |
| `backend/processo_seletivo/shared/static/shared/tokens.css` | novo: o conteúdo de `_tokens.css.html`, com o comentário do topo como `/* */` (R-001) |
| `backend/processo_seletivo/shared/templates/shared/_tokens.css.html` | sai (D-001) |
| `backend/processo_seletivo/shared/estaticos.py` | novo: a tag `{% estatico 'caminho' %}`, que devolve `static(caminho)?v=<resumo>` (R-003) |
| `backend/config/settings/base.py` | `STATICFILES_DIRS` com `shared/static`, como o `DIRS` dos modelos; a biblioteca `estaticos` em `TEMPLATES.OPTIONS.libraries` (R-001, R-003) |
| `interface/templates/interface/base.html` | `<link>` dos tokens e da folha; o `<style>` só com o bloco e o comentário dele (R-004) |
| `interface/templates/interface/base_de_acesso.html`, `portal/templates/portal/base.html`, `shared/templates/404.html` | `<link>` dos tokens antes do `<style>`; o `{% include %}` sai |
| `backend/tests/…` | os guardiões repontados (R-005); um módulo de apoio que monta "a folha que a página aplica" |
| `doc/implantacao-em-producao-ubuntu.md` | o `location` de `/static/shared/`, a nota da versão no endereço e a linha da lista de verificação (R-006) |
| `doc/inventario-visual-da-gestao-2026-10-16/pixels.py` e `depois-da-089/` | a comparação pixel a pixel contra a linha de ruído; o inventário de antes, o de ruído e o de depois, nos dois estados da barra (R-007) |

## Ordem

1. Esperar o merge do PR #305 e trazer a `main` (`git merge origin/main`).
2. Medir antes: o peso das respostas (R-008), o inventário nos dois estados da barra, duas vezes (a
   segunda é a linha de ruído), a página de acesso, o portal e o 404.
3. Mover — um script de conversão, guardado na pesquisa, gera os dois `.css` a partir do modelo;
   a equivalência das regras é conferida por outro script que extrai as regras dos dois lados.
4. Repontar os guardiões, um a um, e provar cada um por mutação.
5. Medir depois e comparar; `make lint check test-pg`.

## Verificação

`cd backend && make lint check test-pg DB_NAME=ps_089 POSTGRES_USER=$USER` com
`LC_ALL=pt_BR.UTF-8`; o roteiro do [quickstart](quickstart.md): inventário e pixels, o portal e a
página de erro, o navegador a 1280 e a 375 px, o cache da segunda página e a edição da folha no
runserver.
