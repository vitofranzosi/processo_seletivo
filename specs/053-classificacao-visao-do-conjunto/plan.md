# Implementation Plan: Classificação — a visão do conjunto e um Perfil por vez

**Branch**: `claude/053-classificacao-visao-do-conjunto` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/053-classificacao-visao-do-conjunto/spec.md`

## Summary

A vista da `052`, sobre o formulário da etapa Classificação. O que as duas telas fazem igual sai do
`perfis.js` para um `vista-do-conjunto.js`, e cada tela declara só o que a linha lê ([research](research.md)
R-001): o `perfis.js` continua com o que tinha, e um `classificacao.js` novo lê os marcos do cartão do
Perfil. Nenhum campo com nome é criado, removido ou movido: o envio é o mesmo com a vista e sem ela.

O servidor muda em cinco pontos pequenos, todos de leitura ou de apresentação:

1. o cartão do Perfil ganha `id`, legenda identificadora (o filtro da `052`) e, em atributos `data-`,
   as pendências (R-008), a origem (R-004) e se o que ele mostra difere do gravado (R-005);
2. a etapa passa a mostrar o bloco de pendências das demais etapas (`D-005`, R-008);
3. a recusa do servidor sobre marco ou critério ganha âncora (`D-006`, R-006) — e, para isso, a
   validação do marco na composição passa a dizer de que marco ou critério é a recusa, e em que campo,
   como a da Retificação já dizia; nenhuma mensagem e nenhuma regra mudam;
4. o formulário declara o rascunho local das demais etapas (`D-007`, R-009);
5. os controles que a linha lê levam as frases curtas em `data-resumo-*` (R-003), e a etapa muda de
   ordem: tabela → método comum → cartões (`UX-127`, R-010).

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente; JavaScript sem build, como os
demais scripts da interface.

**Primary Dependencies**: nenhuma nova. O script não usa htmx: observa a lista dos cartões, como o da
`052`.

**Storage**: nenhuma mudança. Sem migration, sem campo, sem rota de gravação.

**Testing**: pytest contra PostgreSQL (`make lint check test-pg DB_NAME=ps_053`); `node --test` com o
shim de `tests/javascript/dom.js` para as regras puras; o navegador real, no preview, para o que o shim
não reproduz — foco, `hidden`, `details`, validação nativa, fragmento do endereço.

**Target Platform**: interface Django server-rendered da gestão.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: a tabela é montada a partir do DOM já carregado. A origem pede o snapshot do
Edital, que a etapa já monta para as pendências — passa a montá-lo uma vez para as duas (R-004) — e
uma consulta aos registros do gesto. A comparação com o gravado só roda quando a tela volta de um
envio que não gravou.

**Constraints**: `replace_draft` apaga o que não é reenviado; a CSP proíbe `eval` e script inline;
`FR-428` da `030` (nenhuma ajuda visível no cartão) e o princípio de `required` fora dos blocos que
fecham (`test_acessibilidade_da_classificacao.py`); `test_acessibilidade` exige regra para toda classe
citada; o teto de bytes da distribuição inclui a folha de `base.html`; a `051` prende a marcação exata
de opções; `test_aplicar_a_todos.py` e `test_padroes_da_composicao.py` não podem mudar de resultado.

**Scale/Scope**: 2 Perfis (78/2026), 7 (28/2026 e 14/2026, este com 2 marcos cada), 16 (140/2025). O teto
de mil campos continua, fora do escopo (`DP-21`).

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | As frases da linha são as dos resumos dos blocos do cartão e da Revisão; a origem é a frase da Revisão; a situação diz *pendência*, o termo do bloco. |
| II. Imutabilidade | Nada gravado muda: nem campo, nem rota, nem o que se envia (`FR-968`, `SC-358`). |
| III. Auditoria | Nada novo a auditar. A origem é **lida** da trilha do gesto, como a Revisão já lê. |
| IV. Regras explícitas | A tabela não calcula regra (`FR-963`); a origem sai do cálculo da Revisão, e a pendência do domínio. O gesto da `051` fica intacto (`FR-978`). |
| V. Simplicidade | O código comum sai de uma tela para as duas, sem componente genérico; o servidor ganha três funções pequenas e dois ramos. |
| VI. Jornada | O cenário demonstrável é o da US2, pelo preview: aplicar o marco a 7 Perfis e conferir na tabela. |

**Gate: passa.** Nenhuma exceção a justificar. Duas decisões de escopo foram tomadas pela régua do
pedido — *o menor escopo que não deixe o operador pior que hoje* — e estão em `D-005` e `D-007`.

## Project Structure

### Documentation (this feature)

```text
specs/053-classificacao-visao-do-conjunto/
├── spec.md
├── plan.md
├── research.md
├── quickstart.md
├── contracts/tela-da-etapa.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

Sem `data-model.md`: nenhuma entidade nova, nenhum campo. O que a spec chama de entidade — linha,
origem, situação — é leitura, descrita no [contrato](contracts/tela-da-etapa.md).

### Source Code (repository root)

```text
backend/processo_seletivo/editais/domain/
└── perfis.py                    # validate_classification_milestones: campo e identidade na recusa — R-006

backend/processo_seletivo/interface/
├── origens.py                   # origem_dos_marcos(perfis, alcance) — R-004
├── views.py                     # contexto da etapa; _marcos_alterados; _recusa da Classificação; _pendencias(snapshot=)
├── templates/interface/
│   ├── compor_classificacao.html  # pendências, a ordem da UX-127, id dos cartões, rascunho, scripts, estilo
│   ├── compor_perfis.html         # o estilo passa a vir do include; o script comum
│   ├── _estilo_da_vista.html      # as regras da vista, de uma fonte — R-011
│   ├── _marco.html                # data-resumo-* na forma, no corte, no recurso; marca do bloco do método
│   └── _criterio.html             # data-resumo-* no tipo
└── static/interface/
    ├── vista-do-conjunto.js       # o que as duas telas fazem igual — R-001
    ├── perfis.js                  # só o que a linha dos Perfis lê
    ├── classificacao.js           # só o que a linha da Classificação lê
    └── rascunho.js                # a lista de escolha múltipla guardada opção por opção (achado do percurso)

backend/tests/
├── interface/test_visao_da_classificacao.py   # o que o servidor entrega (TC)
├── interface/test_visao_dos_perfis.py         # o guardião do script passa a varrer os três
├── interface/test_rascunho_local.py           # a Classificação entra na lista das etapas
└── javascript/classificacao.test.js           # as regras puras da linha (TJC)
```

**Structure Decision**: o monólito de sempre; um script comum e um por tela.

## Complexity Tracking

Nenhuma violação a justificar.
