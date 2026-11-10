# Implementation Plan: O Centro de Controle passa a ser a página do Edital

**Branch**: `claude/138-centro-como-padrao-f6f2a9`, sobre a `main` em `daba322f` | **Date**: 2026-11-10 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/138-centro-como-pagina-do-edital/spec.md`, com D-001 a
D-006.

## Summary

A rota `editais/<id>/` (`interface:detalhe`) passa a ler o Edital uma vez e escolher a composição:
o Centro, quando `andamento.do_edital` devolve andamento; o detalhe, quando não. As duas views de
hoje — `views.detalhe` e `centro_do_edital.centro_do_edital` — já leem as mesmas funções na mesma
ordem (a FR-4705 da `136`); a leitura sai para uma função só, e cada composição vira uma função que
recebe a leitura e desenha. A rota `/centro/` vira um redirecionamento; a página anterior é a
composição do detalhe numa rota nova.

**Onde está o risco**: os ~56 arquivos de teste que abrem `interface:detalhe`. Os que abrem um Edital
publicado esperam o detalhe e passam a receber o Centro. O caminho é o pedido: os que exercitam o
detalhe passam a abrir a página anterior, **sem mudar as asserções**; os que conferem "a página do
Edital publicado" passam a conferir o Centro. A lista sai da suíte, e não de leitura prévia.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration; o `M` do `provisionar` continua 53.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME=ps138`). A porta e a escolha em
`tests/interface/test_centro_do_edital.py`; os atos em `tests/interface/test_centro_como_pagina.py`
(novo); o orçamento em `tests/performance/test_centro_em_escala.py`; os cenários da `134` em
`tests/integration/treinamento/`; a jornada no navegador em `tests/navegador/test_jornada_do_centro.py`.

**Target Platform**: a gestão (`/gestao/editais/<id>/`, `/centro/` e `/pagina-anterior/`).

**Performance Goals**: nenhuma consulta nova na página do Edital publicado além das que o Centro já
fazia; a do não publicado continua a do detalhe. O redirecionamento de `/centro/` não consulta nada.

**Constraints**: nenhuma regra nova de disponibilidade, autorização ou estado (FR-4876); CSP sem
inline; classe nova pede regra na folha; os guardiões de citação, inventário de negativas,
vocabulário, estáticos e acessibilidade.

**Scale/Scope**: `interface/views.py` (a leitura, as duas composições, a página anterior),
`interface/centro_do_edital.py` (a composição do Centro e o redirecionamento), `interface/urls.py`,
`interface/conceitos.py` e `interface/centro.py` (docstrings), `templates/interface/detalhe.html`,
`templates/interface/centro_do_edital.html`, `static/interface/telas/centro.css`, o inventário da
`033`, `tests/test_gramatica_das_portas.py`, e os testes.

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | Nenhum termo novo; "Página anterior" nomeia só a rota de transição. |
| II. Imutabilidade | Nenhuma escrita. O aviso de conteúdo imutável passa ao Centro, com a condução da `037`. |
| III. Segurança | A porta é a do detalhe (`obter_edital`, escopo na consulta); a página anterior a usa; `/centro/` não revela nada, porque responde igual para qualquer identificador. Nenhuma permissão nova. |
| IV. Regras explícitas | A escolha da composição é uma condição só (`andamento is not None`), a mesma que o Centro já usava para mandar ao detalhe. |
| V. Rastreabilidade e simplicidade | Uma leitura, duas composições; nenhum estado, campo nem componente. A página anterior não ganha código próprio além da rota. |
| VI. Completude de jornada | É a feature: quem abre o Edital chega ao Centro, e o ato volta a ele com retorno. |

**Resultado**: passa. Pós-desenho: passa.

## Desenho

### R-001 — A leitura do Edital, uma só

`views._leitura_do_edital(ator, edital)` devolve um `LeituraDoEdital` (dataclass, sem persistência)
com o que as duas composições leem: `participantes`, `pendencias`, `segregacao`, `conjunto`,
`em_curso`, `andamento`, `marcos` (com os destinos já postos em cada Perfil do andamento, como as duas
views faziam), `documentos`, `pode_ver_avisos` e `pode_conversar_com_o_assistente`. A ordem é a de
hoje. A porta (`ator_da_sessao`, `obter_edital`, `raise Http404`) fica **dentro** de cada view, para
que o inventário da `033` continue lendo o 404 na função que o responde.

### R-002 — As duas composições

- `views._desenhar_o_detalhe(request, leitura, *, pagina_anterior=False)`: o `render` de
  `detalhe.html` de hoje, com o contexto de hoje, mais `pagina_anterior`.
- `centro_do_edital.desenhar(request, leitura)`: o `render` de `centro_do_edital.html` de hoje, mais
  `conferencia_do_ato`, `conducao_do_imutavel` e `pode_conversar_com_o_assistente`. Recebe a leitura e
  não importa `views` — o que antes lia de `views` chega pronto —, de modo que `views` pode importá-lo.
  O `conferencia_do_ato` e o `conducao_do_imutavel` são calculados por `views` e entram na leitura,
  para que os dois desenhos usem a mesma função.

`views.detalhe` passa a ser: porta → leitura → `centro_do_edital.desenhar` se há andamento, senão
`_desenhar_o_detalhe`. `views.pagina_anterior`: porta → leitura → `_desenhar_o_detalhe(...,
pagina_anterior=True)`.

### R-003 — O endereço do Centro

`centro_do_edital.centro_do_edital` vira um redirecionamento (302) para
`reverse("interface:detalhe")` mais `?` e `request.META["QUERY_STRING"]` quando houver. Sem
`ator_da_sessao` nem `obter_edital` (D-003). A linha 39 do inventário da `033` ganha a nota de que,
desde a `138`, a função não responde 404; o módulo continua em `MODULOS_DE_VIEW`, para que um 404
futuro não escape. `views._proximo_nesta_lista` passa a montar `interface:detalhe`.

### R-004 — O retorno do ato no Centro

O Centro desenha, dentro do cabeçalho e logo depois do `<h1>`, o mesmo
`<p class="sucesso" role="status">Ato registrado: {{ request.GET.ato|rotulo_do_ato }}.</p>` e o
`{% include "interface/_conferencia_do_ato.html" %}` do detalhe. As classes `sucesso` e
`conferencia-do-ato` já estão na folha comum. O teste pratica os sete atos de `atos.ATOS` pela
interface (POST na tela de confirmação) e confere a página de chegada.

### R-005 — A marca de validação sai

- `detalhe.html`: sai o `<p class="ajuda"><a …>Abrir o Centro de Controle do Edital (em
  validação)</a></p>` e o comentário que o explica.
- `centro_do_edital.html`: sai a faixa `cc-em-validacao`; o caminho termina em
  `<span aria-current="page">Edital N/AAAA</span>`; o título é `Edital N/AAAA`; o comentário de topo
  deixa de falar em validação.
- `centro.css`: sai a regra `.cc-em-validacao`.
- `conceitos.py` e `centro.py`: as docstrings deixam de dizer "provisórios", e citam a decisão do
  usuário; o teste `test_os_conceitos_se_declaram_provisorios` vira o inverso.

### R-006 — O que só o detalhe oferecia, no Centro

No cartão "Ações e consultas do Edital", na lista simples que já tem os avisos e a comissão: "Respostas
do assistente de dúvidas (validação interna)" e, sob a condição de hoje, "Conversar com o assistente
(piloto)". Abaixo das ações, o `<p class="imutavel em-uma-linha">` do detalhe, com a condução (a regra
mora em `telas/andamento.css`, que o Centro já carrega). No cartão "Quem atuou", cada `dd` ganha
`<span class="cc-fraco">` com a data e hora, e a unidade da autoridade entra como mais um par; sai o
link "Autoridade, unidade e datas".

### R-007 — A página anterior

Rota `editais/<uuid:edital_id>/pagina-anterior/`, nome `interface:pagina-anterior`. No detalhe, com
`pagina_anterior`, o caminho vira `… › <a href="{% url 'interface:detalhe' %}">Edital N/AAAA</a> ›
<span aria-current="page">Página anterior</span>`; sem ele, o de hoje. O link único fica no fim da
seção "Administração e histórico" do Centro, num `<p class="cc-fraco cc-pagina-anterior">`, com regra
própria na folha do Centro. Uma linha nova no inventário da `033` para `pagina_anterior`, com a classe
do detalhe.

### R-008 — Os testes do detalhe

Depois da implementação, rodar a suíte e repartir as falhas:

1. o teste exercita o detalhe de um Edital publicado (o cartão "O que fazer agora", o andamento da
   seleção, a trilha de 127): trocar `interface:detalhe` por `interface:pagina-anterior`, sem mexer na
   asserção;
2. o teste confere "a página do Edital publicado" (um link, um texto que o Centro também mostra):
   conferir no Centro;
3. o teste do Centro que abria `/centro/`: abrir a página do Edital.

A repartição fica em `verificacao.md`, com a contagem.

## Project Structure

### Documentation (this feature)

```text
specs/138-centro-como-pagina-do-edital/
├── spec.md · plan.md · tasks.md · quickstart.md
├── checklists/requirements.md
└── verificacao.md   (na implementação)
```

### Source Code

```text
backend/processo_seletivo/interface/
├── views.py                 # LeituraDoEdital, _leitura_do_edital, _desenhar_o_detalhe, detalhe, pagina_anterior
├── centro_do_edital.py      # desenhar (a composição) e centro_do_edital (o redirecionamento)
├── urls.py                  # pagina-anterior
├── conceitos.py · centro.py # docstrings
├── templates/interface/detalhe.html            # sem o botão; o caminho da página anterior
├── templates/interface/centro_do_edital.html   # sem a faixa; retorno do ato; o que só o detalhe tinha; o link
└── static/interface/telas/centro.css           # sem .cc-em-validacao; .cc-pagina-anterior
specs/033-navegacao-por-capacidade/inventario-das-negativas.md   # pagina_anterior; nota na linha 39
backend/tests/
├── interface/test_centro_como_pagina.py   # novo: a escolha, os sete atos, o redirecionamento, a página anterior
└── (os que a suíte apontar, R-008)
```

**Structure Decision**: tudo na `interface`, onde as duas views já moram. Nenhum módulo novo de
produção.

## Os incrementos e os PRs

Um PR só, com a spec, o plano, as tarefas e a implementação; o merge é do usuário.

## Complexity Tracking

Nenhuma violação.
