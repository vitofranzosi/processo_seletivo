# Implementation Plan: A convocação depois do envio, e um nome só para o documento reenviado

**Branch**: `claude/154-plano-e-tarefas` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: `specs/154-convocacao-depois-do-envio/spec.md`, mergeada pelo PR #479. Plano sobre a
`main` em `d1ec1e0a`, **depois** do PR #477, que já tinha mexido em `interface/conducao_da_convocacao.py`,
`interface/andamento.py`, `interface/views.py` e `interface/templates/interface/convocacao.html`.

**Decisões**: todas do usuário (as oito dos achados 20 e 23 e as D-001 a D-006), e nenhuma se
reabre. Os `R-` de [research.md](research.md) dizem onde e como cada requisito se cumpre no código, e
o que o plano escolheu dentro da latitude da spec (R-009 e R-012 registram as duas escolhas de
texto que um revisor pode querer ver).

## Summary

Revisão de texto e de condição de exibição, sem estado novo. Duas mudanças:

1. **A convocação depois do envio** (achado 20 do estudo). A projeção das obrigações da `118`
   (`portal/obrigacoes.py`) passa a dizer se há **providência pendente** — ter tarefa da FR-3726 da
   `118` —, e três coisas passam a depender disso: o título (*"Acompanhe sua convocação"* sem
   providência), a advertência do não atendimento (só com providência) e, com todos os obrigatórios
   conferidos, a frase da conferência terminada no lugar da frase de conclusão. O prazo e a ressalva
   não mudam de condição. Na chamada que não pede documento, uma função pura sobre a política do
   Requerimento faz o mesmo para o Requerimento pedido na chamada (D-006).
2. **Um nome só para o reenviado** (achado 23 do estudo). Um módulo de vocabulário novo,
   `convocacao/domain/vocabulario_dos_documentos.py`, guarda *"Reenviado — aguardando nova
   conferência"* e a contagem no singular e no plural; o portal, a página de documentos, a condução,
   o passo da chamada e a exclusão do aviso de pendência leem dali. O identificador interno
   `COMPLEMENTADO` fica (R-007).

## Technical Context

**Language/Version**: Python 3.13, Django 5 (monólito)
**Primary Dependencies**: as de hoje; nenhuma nova
**Storage**: PostgreSQL; **nenhuma migration**, nenhum modelo, nenhuma tabela append-only nova (58
continuam sendo 58)
**Testing**: pytest contra PostgreSQL (`make test-pg`); unitários puros da projeção e do passo;
cliente de teste do Django nas telas; Playwright nos dois passeios da `121` e da `115`, que pulam sem o
grupo `navegador`
**Target Platform**: o portal do candidato e a gestão (`/gestao/`), sob a CSP da `091`/`092` — nenhum
estilo nem script no template
**Performance Goals**: nenhuma consulta nova; os guardiões de `tests/performance/` não mudam de número
(R-016)
**Constraints**: nada publicado ou gravado muda (FR-6215); a mensagem da convocação não muda; a regra
mora na projeção, e o template só a coloca no lugar (FR-3751 da `118`)
**Scale/Scope**: duas telas do portal, duas da gestão, uma exclusão do aviso; ~9 arquivos de produto,
~14 de teste

## Constitution Check

*GATE: antes da Fase 0 e de novo depois do desenho.*

- **II. Integridade normativa e imutabilidade**: nada é gravado; a trilha do gesto do aviso guarda o
  motivo em texto, e o registro antigo fica com o texto do dia (R-011, FR-6215, SC-2005). Nenhuma
  migration, nenhum `UPDATE` em dado gravado.
- **I. Linguagem ubíqua**: o achado 23 é justamente o mesmo fato com três nomes; o plano dá **uma**
  fonte ao nome (R-006), e o teste prende a identidade, e não seis cópias.
- **IV. Regras explícitas**: a providência pendente é uma derivação, num lugar só (R-001); nenhuma
  máquina de estados nova (decisão de vocabulário da `118`; FR-6216).
- **III. Negar por padrão**: nenhuma rota, permissão ou porta nova; as telas são as de hoje.
- **V. Rastreabilidade e simplicidade**: cada FR, SC e caso-limite ganha linha em
  `rastreabilidade.md` na implementação; os testes que mudam de expectativa citam o requisito da
  `154` (R-014). A citação dos achados é *"achado NN do estudo"*, nunca com o prefixo do estudo, que
  o guardião de citação leria como requisito de experiência inexistente.
- **VI. Completude de jornada**: o quickstart refaz as três capturas do estudo (SC-2006).

Sem violação. Pós-desenho: igual — o desenho não acrescentou estado, rota nem consulta.

## O desenho

### 1. A projeção — `portal/obrigacoes.py`

- `Obrigacoes.providencia_pendente` e `Obrigacoes.conferencia_terminada` (R-001, R-002).
- `_aberta` escolhe a frase de conclusão entre a de hoje e a da conferência terminada; o campo
  `frase_de_conclusao` passa a ser a fonte de `resumo_do_que_falta`, da ação do acompanhamento e da
  confirmação do envio (R-002).
- `Obrigacoes.titulo`: *"Acompanhe sua convocação"* na chamada aberta sem providência (R-003).
- `Obrigacoes.cabe_a_consequencia` (R-004).
- `providencia_pendente_sem_documento(disponibilidade)` para o ramo sem projeção (R-005).
- `texto_do_item`, ramo `ITEM_COMPLEMENTADO`: D-003 e D-005 (R-012).

### 2. O vocabulário — `convocacao/domain/vocabulario_dos_documentos.py` (novo)

`REENVIADO`, `reenviado_em_frase()` e `reenviados(n)` (R-006). Puro, sem Django.

### 3. O portal — `portal/situacao.py`, `portal/views.py` e templates

- `situacao.py`, `_acao_das_obrigacoes`: a `consequencia` só com `obrigacoes.providencia_pendente`;
  o `prazo` como hoje (R-004).
- `situacao.py`, `_acao_da_convocacao`: a `consequencia` só com
  `providencia_pendente_sem_documento(politica)` (R-005).
- `views.py`, `_chamada_da_tela`, ramo sem projeção: o título sem providência (R-005).
- `_chamada_da_convocacao.html`: `{% if o.prazo %}` da consequência vira `{% if o.cabe_a_consequencia %}`;
  o comentário do template diz por quê (achado 20 do estudo, FR-6209).
- `acompanhamento.html` não muda: ele já só mostra `acao.consequencia` quando vem preenchida.

### 4. A gestão — `interface/views.py`, `interface/conducao_da_convocacao.py` e templates

- `views.py`: `ROTULO_DO_ITEM["COMPLEMENTADO"]` = `REENVIADO` (R-010).
- `conducao_da_convocacao.py`: a frase do passo `REENVIADO` e `frase_da_pendencia` (R-009).
- `convocacao_documentos.html`: a contagem do resumo (R-008).
- `convocacao.html`: a contagem da linha documental do cartão (R-008) — a única linha deste
  template que o plano toca.
- As duas contagens saem de um filtro novo, `reenviados`, em `interface/templatetags/interface_extras.py`,
  que só chama `vocabulario_dos_documentos.reenviados(n)`: `{{ c.complementados|reenviados }}`. A
  alternativa — o filtro `plural` do projeto com as duas formas escritas em cada template —
  reescreveria o nome em dois lugares, que é o que a R-006 evita.

### 5. Os avisos — `avisos/application/pendencias.py`

`COMPLEMENTADA` com o texto novo, montado do vocabulário (R-011). Antes de mudar, a busca que confirma
que nenhum leitor compara o motivo gravado com a constante.

### 6. Os testes

- **Unitários da projeção** (`tests/unit/portal/test_obrigacoes_da_convocacao.py`): a tabela de decisão
  inteira de [data-model.md](data-model.md), linha a linha, mais a confirmação do envio em Tc.
- **Unitários do passo** (`tests/unit/interface/test_conducao_da_convocacao.py`): singular, plural e
  `frase_da_pendencia`.
- **Unitário do vocabulário** (novo, `tests/unit/convocacao/test_vocabulario_dos_documentos.py`): o
  travessão U+2014, as três formas, e a identidade entre o rótulo e as formas derivadas (SC-2004).
- **Telas** (`tests/interface/test_portal_convocacao.py`, `test_portal_documentos_da_convocacao.py`,
  `test_portal_jornada_consolidada.py`, `tests/portal/test_acompanhamento_pela_situacao.py`): os
  cenários das SC-2000 a SC-2003, contando ocorrências da advertência (zero ou exatamente uma).
- **Falsas conclusões** (novo, `tests/interface/test_convocacao_depois_do_envio.py`): FR-6207 sobre o
  HTML renderizado de cada cenário sem desfecho (R-013).
- **Varredura** (`tests/test_vocabulario_dos_documentos_da_convocacao.py`): os nomes antigos da
  FR-6214 (R-013).
- **Gravado não muda** (`tests/integration/avisos/test_aviso_de_pendencia.py`): um gesto registrado
  com o texto antigo continua lido com ele (SC-2005).
- Os demais da R-014, conferidos um a um.

## Onde os arquivos se cruzam com as specs em paralelo

Detalhe em [research.md, R-015](research.md). Em resumo:

- **`152`** (plano no PR #480): divide com esta `interface/conducao_da_convocacao.py` (ela, o passo
  vencido sem apresentação; esta, o passo `REENVIADO` e a frase do reenvio), `interface/views.py`
  (ela, as views de convocar, corte e desfecho; esta, só `ROTULO_DO_ITEM`) e `convocacao.html` (ela,
  o cartão e o desfecho; esta, só a contagem da linha documental). Regiões disjuntas; quem entrar
  depois refaz o merge. Esta **não** toca `convocacao/application/documentos.py`, que a `152` altera.
- **`153`** (spec no #476): a jornada guiada da formalização. Sem arquivo em comum com este plano.
- **`150`** (spec, sem plano): a confirmação de vários envios precisa ler a mesma
  `frase_de_conclusao` da projeção (R-002), ou Tc volta a dizer *"ainda vai concluir a análise"*.
  Nota para o plano dela.
- **PR #477** (mergeado): este plano parte da `main` depois dele; nenhuma linha que ele tocou é
  alterada aqui, salvo vizinhança em `conducao_da_convocacao.py`.

## Project Structure

### Documentation (this feature)

```text
specs/154-convocacao-depois-do-envio/
├── spec.md               # PR #479
├── checklists/requirements.md
├── plan.md               # este arquivo
├── research.md           # R-001 a R-016
├── data-model.md         # as derivações e a tabela de decisão
├── contracts/telas.md    # o que cada superfície diz, por cenário
├── quickstart.md         # testes e percurso no navegador
└── tasks.md              # /speckit-tasks
```

### Source Code

```text
backend/processo_seletivo/
├── convocacao/domain/vocabulario_dos_documentos.py   # novo: REENVIADO, reenviado_em_frase, reenviados
├── portal/
│   ├── obrigacoes.py                                  # providência, conferência terminada, título, consequência, cartão do reenviado
│   ├── situacao.py                                    # a consequência nas duas montagens da ação
│   ├── views.py                                       # o título do ramo sem documento
│   └── templates/portal/_chamada_da_convocacao.html   # a condição da consequência
├── interface/
│   ├── views.py                                       # ROTULO_DO_ITEM
│   ├── conducao_da_convocacao.py                      # o passo REENVIADO; frase_da_pendencia
│   ├── templatetags/interface_extras.py               # o filtro reenviados
│   └── templates/interface/
│       ├── convocacao_documentos.html                 # a contagem do resumo
│       └── convocacao.html                            # a contagem da linha documental
└── avisos/application/pendencias.py                   # COMPLEMENTADA

backend/tests/
├── unit/convocacao/test_vocabulario_dos_documentos.py # novo
├── interface/test_convocacao_depois_do_envio.py       # novo: FR-6207 renderizado
└── (os da R-014, alterados)
```

**Structure Decision**: o monólito de sempre; um módulo de domínio novo, puro, ao lado de
`vocabulario_do_canal.py`.

## Complexity Tracking

Sem violação da Constituição a justificar.
