# Implementation Plan: O shell da gestão

**Branch**: `claude/great-grothendieck-2155ee` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

## Summary

Pôr em volta das 59 telas que estendem `interface/base.html` uma moldura do conceito A: barra lateral
branca com as seções em *Trabalho* e *Unidade*, a seção atual em verde-claro com filete, a pessoa e
"Sair" no pé, e um cabeçalho de contexto com o caminho e "Trocar identidade". No celular a barra
recolhe. O caminho do topo para na seção: o resto é a trilha que 54 telas já têm (R-004). Nenhuma
tela muda de conteúdo; nenhuma migration; nenhuma permissão nova. A barra é
derivada das capacidades que já estão na sessão, pelos mesmos predicados que condicionam os botões
da lista — que passam a morar num lugar só.

## Technical Context

Django 5 sobre PostgreSQL. A identidade chega aos templates pelo processador de contexto de
`interface/identidade.py`; a moldura chega pelo mesmo caminho, num processador próprio. Frente sem
dependência nova: regras na folha inline do `base.html`, o `popover` nativo do navegador para o
painel do celular (R-005), e — desde a emenda da barra retrátil (US5, DP-6) — um script estático
curto, `static/interface/shell.js`, que guarda a escolha no navegador (R-009). A linha de base visual é o inventário de 16/10
(`doc/inventario-visual-da-gestao-2026-10-16/resultados.json`), refeito depois da `075`.

Detalhes e alternativas descartadas em [research.md](research.md).

## Constitution Check

- **Negar por padrão (III, IV)**: a barra só oferece o destino que a capacidade abre; nenhuma
  verificação sai do servidor, e o conjunto de pares (identidade, tela) que abre não muda
  (`FR-1721`; `FR-482` e `FR-483` da `033`). Um teste compara, papel a papel, os itens da barra com
  a resposta real de cada destino.
- **Linguagem ubíqua (I)**: os rótulos são os que as telas já usam — Processos Seletivos, Minhas
  Etapas, Visão Geral, Autoridades da unidade, Modelos de aviso. Presidência continua vínculo; a
  barra não a transforma em seção.
- **Rastreabilidade (V)**: requisitos em `spec.md`, matriz em `rastreabilidade.md`, cobrada por
  `tests/test_citacoes_de_requisito.py`.
- **Simplicidade (V)**: sem middleware, sem decorator, sem biblioteca, sem script; um módulo de
  navegação e o `base.html`. A folha comum ganha regras, e não é reescrita.
- **Completude de jornada (VI)**: a moldura é provada no navegador e pelo inventário visual
  inteiro, a 1280 e a 375 px.

Sem violação a justificar.

## Design

| Peça | Mudança |
|---|---|
| `interface/navegacao.py` (novo) | os itens da barra — rótulo, rota, grupo e predicado sobre o ator —, a seção atual pelo prefixo do caminho, e `contexto_da_navegacao(request)`, o processador de contexto |
| `config/settings/base.py` | o processador novo na lista de `context_processors` |
| `interface/views.py::lista` | `pode_ver_visao`, `pode_gerir_autoridades` e `pode_gerir_modelos` passam a vir dos predicados de `navegacao.py` (R-002); a tela não muda |
| `interface/templates/interface/base.html` | a moldura (R-006) quando há identidade, com o botão "Seções" e o painel `popover`; o `header.topo` de hoje, só com a marca, quando não há; as regras novas na folha, junto das do cabeçalho; impressão sem barra nem caminho; na emenda, os dois estados da tela larga, o sprite de sete ícones, o avatar e o controle de recolher |
| `interface/static/interface/shell.js` (novo, emenda) | o estado inicial, a troca e a memória da barra retrátil (R-009) |
| `tests/javascript/shell.test.js` (novo, emenda) | as regras do script, pelo `node --test` que `tests/test_javascript.py` já roda |

**A folha.** As regras novas entram num trecho próprio, logo depois das de `header.topo`, e a prosa
que as explica vai em `{% comment %}` do Django, que não é servido. Nenhuma regra existente muda,
exceto as de `header.topo .identidade`, que saem com o elemento que estilizavam. Toda classe nova
tem regra; nenhum seletor termina em porcentagem; nenhum cita `checkbox`.

**O que fica igual.** O link de salto continua o primeiro elemento do `body` e aponta para
`#conteudo`; `main#conteudo` continua com `tabindex="-1"`; o formulário de sair continua um POST
para `interface:sair`; a lista continua com os seus botões (DP-1).

## Decisões do responsável pelo produto

DP-1 (as cinco seções), DP-2 (sem chave) e DP-3 (estouros registrados), tomadas em 16/10 nas
propostas da spec; DP-4 (a barra no topo da Alocação), quando o inventário mostrou o conflito com a
`057`; DP-5 (a barra retrátil entra nesta feature) e DP-6 (script com `localStorage`, e o guardião
da Visão Geral restrito ao conteúdo), com o pedido da emenda.

## Testes que mudam, e por quê

A varredura dos guardiões que leem o cabeçalho não achou teste que a moldura reprove por desenho —
nenhuma contagem de `nav`, `button`, `aria-current` ou "Sair" na página inteira, nenhuma
asserção sobre o `title`. Os que poderiam reprovar dependem de escolhas que o desenho já evita
(R-005, R-006):

| Guardião | O que ele exige, e como a moldura atende |
|---|---|
| `test_visao_geral.py` (`"<script" not in corpo`) | na primeira versão, nenhum script; desde a emenda (DP-6), o guardião olha o conteúdo da tela, que é o que a `SC-226` da `042` protege |
| `test_tela_de_autoridades.py`, `authorization/test_visao_institucional.py` | o link só com a capacidade — os mesmos predicados da lista |
| `test_acessibilidade.py` (salto, `main`, controles nativos, botão com peso, classe sem regra, modificador órfão) | `main` intacto; item atual por `[aria-current]`; o botão com `type="button"` e classe |
| `test_larguras.py` (sem px, `.marca` com escopo, o `@media` de 40rem da Visão Geral) | `rem`; `.barra .marca`; o ponto de 64rem que a folha já usa |
| `test_estaticos.py` (sintaxe de template no HTML servido) | cada `@media` fecha em linha própria; nenhuma declaração final em porcentagem |
| `performance/test_escala_da_mesa.py` (120 000 bytes) | medido antes (83 781) e depois |
| contagens de consulta (`test_instrucao_na_peca.py`, `test_comissao_em_escala.py` e outros) | a barra lê a sessão, sem consulta |

Se algum reprovar mesmo assim, a correção é na moldura, e não no guardião.

## Verificação

`make lint check test-pg` com `DB_NAME` próprio; o percurso do [quickstart](quickstart.md) no
navegador, a 1280 e a 375 px; o inventário visual refeito com a moldura e comparado tela a tela com
o `resultados.json` da linha de base.
