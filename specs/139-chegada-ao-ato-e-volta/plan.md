# Implementation Plan: A providência chega ao ato, e o ato volta ao Centro

**Branch**: `claude/139-chegada-e-volta-2ea891`, sobre a `main` em `4ae78556` | **Date**: 2026-11-10 |
**Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/139-chegada-ao-ato-e-volta/spec.md`, com D-001 a D-004.

## Summary

Duas pontas da mesma passagem, sobre mecanismos que já existem:

1. **A ida (G2, M-02).** O endereço das providências do sorteio e da convocação, montado em
   `interface/andamento.py`, ganha um fragmento: o recorte da lista, a ocorrência, os recortes, as
   chamadas, a chamada pronta, a seção do ato. A tela do sorteio ganha um id por recorte, da mesma
   função que monta o fragmento. O caminho comum de duas listas juntadas, em
   `interface/providencias.py`, passa a comparar o endereço sem o fragmento e a juntar os fragmentos
   na seção comum.
2. **A volta (G1, M-01 e M-07).** O bloco do próximo passo (`views._proximo_nesta_lista` e o parcial
   `_proximo_nesta_lista.html`) leva o endereço do Centro e o desenha numa linha no fim; cada item de
   "Ainda neste marco" com endereço vira link. O endereço do item já é vazio quando o item não é da
   pessoa — a regra é a de hoje.

**Onde está o risco**: o caminho comum da `127` (duas listas da mesma tela) comparava o endereço
inteiro, e um fragmento diferente por lista o desviaria para a condução do marco; e as expectativas
dos testes que comparam o endereço exato.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration; o `M` do `provisionar` continua 53.

**Testing**: pytest contra PostgreSQL (`make test-pg`, `DB_NAME=ps139`). Regras puras em
`tests/unit/interface/`; os cenários da `134` em `tests/integration/treinamento/`, pelo gerador
(`carregar`); a tela em `tests/interface/test_andamento_transicoes.py`.

**Target Platform**: o Centro (`/gestao/editais/<id>/centro/`), o detalhe do Edital, e as seis telas
com o bloco do próximo passo.

**Performance Goals**: nenhuma consulta nova. O número da chamada pronta sai da mesma leitura
documental que já conta as prontas; o endereço do Centro é um `reverse`.

**Constraints**: a derivação escolhe a mesma providência (FR-4767); a migalha não muda; nenhuma frase
da quinta decisão em aberto do estudo; CSP sem inline (FR-4771); a sessão paralela de triagem dos
achados F-1 a F-3 pode tocar `andamento.py` — esta spec toca só `_sorteio`, `_documentos`,
`_convocacao` e `situacoes_da_convocacao`, e o PR diz isso.

**Scale/Scope**: edições em `interface/andamento.py`, `interface/providencias.py`,
`interface/views.py` (`_proximo_nesta_lista`), `templatetags/interface_extras.py` (um filtro),
`templates/interface/_proximo_nesta_lista.html`,
`templates/interface/sorteio.html` (o id do recorte) e `static/interface/gestao/telas.css` (uma
regra).

## Constitution Check

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | Nenhuma palavra nova na tela além de "Voltar ao Centro de Controle do Edital", o nome que o Centro já usa. |
| II. Imutabilidade | Nada publicado muda; nenhuma escrita. |
| III. Segurança | Nenhuma permissão nova. O item de outro papel continua sem endereço (FR-4769); o Centro tem a porta do escopo do Edital, a mesma das seis telas. |
| IV. Regras explícitas | A âncora do recorte sai de uma função só, usada pela derivação e pela tela (FR-4762). |
| V. Rastreabilidade e simplicidade | Nenhum estado, campo, rota ou componente; nenhum framework de jornada (o "o que não fazer" do plano do estudo). |
| VI. Completude de jornada | É a feature: a jornada Centro → ato → Centro passa a fechar. |

**Resultado**: passa. Pós-desenho: passa.

## Desenho

### R-001 — Onde o fragmento nasce

No `_sorteio` do leitor, a função `url(lista)` já monta o endereço por lista; ela passa a acrescentar
`#recorte-<lista>` (a ampla, `#recorte-ampla`), e a semente usa `#titulo-ocorrencia`. A semente
impedida — a leitura dos recortes recusada — vai a `#titulo-recortes`. A âncora do recorte é
`andamento.ancora_do_recorte(lista_id)`, que a tela do sorteio lê pelo filtro `ancora_do_recorte`
(`interface_extras`), para que a derivação e a tela não escrevam a mesma regra duas vezes. A view do
sorteio não muda.

Na convocação, `situacoes_da_convocacao` (pura) recebe o endereço sem fragmento, como hoje, e põe a
âncora de cada providência: `#titulares`, `#pendentes`, `#vencidos`, `#chamada-N` ou `#chamadas`,
`#fila`, `#chamadas` para a resposta aguardada. O impedimento e o *Feito* ficam sem fragmento: não há
ato a alcançar. O `N` sai de `_documentos`, que já percorre as linhas na ordem da leitura do recorte —
a mesma que a tela enumera sem `?ordem=`: a posição da primeira pronta, contando todas as linhas.

### R-002 — O caminho comum de duas listas

`providencias._juntar` comparava `_sem_lista(url)` (o endereço até o `?`). Passa a comparar até o `?`
ou o `#`. Com a mesma tela e endereços diferentes, o resultado é a tela sem lista **com** a âncora
comum: a mesma, se iguais; a seção que reúne as duas, se ambas são de recorte (`#titulo-recortes`)
ou de chamada (`#chamadas`); nenhuma, se não. A tabela das seções comuns mora em `andamento.py`, ao
lado de quem cria as âncoras.

### R-003 — O bloco do próximo passo

`_proximo_nesta_lista` devolve, além de `desta` e `outras`, `centro`: o endereço do Centro do Edital.
O parcial desenha `<p class="retorno-ao-centro">` depois do último parágrafo do bloco. Em
`outras`, o item com `url` vira `<a>` com o mesmo texto; o `url` do item já é vazio quando ele não é
da pessoa. A regra `.retorno-ao-centro` entra em `telas.css`, ao lado das do bloco.

## Project Structure

### Documentation (this feature)

```text
specs/139-chegada-ao-ato-e-volta/
├── spec.md · plan.md · tasks.md
├── checklists/requirements.md
└── verificacao.md   (na implementação)
```

### Source Code

```text
backend/processo_seletivo/interface/
├── andamento.py            # ancora_do_recorte, ancora_comum, os fragmentos do sorteio e da convocação
├── providencias.py         # _juntar compara sem o fragmento e junta na seção comum
├── views.py                # _proximo_nesta_lista leva o endereço do Centro
├── templatetags/interface_extras.py               # o filtro ancora_do_recorte
├── templates/interface/_proximo_nesta_lista.html   # o retorno e os links de "Ainda neste marco"
├── templates/interface/sorteio.html                # id por article.recorte
└── static/interface/gestao/telas.css               # .retorno-ao-centro
backend/tests/
├── unit/interface/test_chegada_ao_ato.py                 # as âncoras, puras
├── interface/test_andamento_transicoes.py                # o retorno e os links nas telas
└── integration/treinamento/test_chegada_e_volta_nos_cenarios.py   # C06 e C12
```

**Structure Decision**: tudo na `interface`, onde a derivação, o agrupamento e o bloco já moram.
Nenhum módulo novo de produção.

## Os incrementos e os PRs

Um PR só, com a spec, o plano, as tarefas e a implementação; o merge é do usuário.

## Complexity Tracking

Nenhuma violação.
