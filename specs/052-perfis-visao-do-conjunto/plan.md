# Implementation Plan: Perfis de Vaga — a visão do conjunto e um editor por vez

**Branch**: `claude/052-perfis-visao-do-conjunto` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/052-perfis-visao-do-conjunto/spec.md`

## Summary

Uma vista sobre o formulário que já existe. Um script novo lê os cartões de `#perfis`, monta a tabela
e mostra um cartão por vez com o atributo `hidden`; nenhum campo com nome é criado, removido ou
movido, de modo que o envio é o mesmo com a vista e sem ela (`D-001`,
[research](research.md) R-001). O servidor muda em três pontos pequenos: a legenda do cartão passa a
identificar o Perfil; o cartão carrega, em atributos `data-`, as pendências que o têm por objeto e se o
que ele mostra difere do gravado (R-003, R-004); e as frases curtas da linha moram no template, nos
controles, para o script não ter vocabulário próprio (R-005). A ordem da etapa muda para
tabela → conjunto → editor (`UX-120`).

## Technical Context

**Language/Version**: Python 3.12, Django 5 — o monólito existente; JavaScript sem build, como os
demais scripts da interface.

**Primary Dependencies**: nenhuma nova. O script não usa htmx: observa `#perfis` como o
`assistente.js` já faz com o contador.

**Storage**: nenhuma mudança. Sem migration, sem campo, sem rota.

**Testing**: pytest contra PostgreSQL (`make test-pg DB_NAME=ps_052`); `node --test` com o shim de
`tests/javascript/dom.js` para as regras puras do script; e o navegador real, no preview, para o que o
shim não reproduz — foco, `hidden`, validação nativa (R-002).

**Target Platform**: interface Django server-rendered da gestão.

**Project Type**: web — `backend/processo_seletivo/`.

**Performance Goals**: a tabela é montada a partir do DOM já carregado; nenhuma requisição nova. A
comparação com o gravado é feita só quando a tela volta de um envio que não gravou, e é uma leitura a
mais dos Perfis do Edital, a mesma que `escolhas_pendentes` já faz.

**Constraints**: `replace_draft` apaga o que não é reenviado; a CSP proíbe `eval` e script inline;
`FR-428` da `030` (nenhuma ajuda visível no cartão); `test_acessibilidade` exige regra para toda
classe citada e aceita a regra no `estilo_da_pagina`; o teto de bytes da distribuição inclui a folha de
`base.html`, e por isso a regra nova vai para o bloco da página.

**Scale/Scope**: 2 Perfis (78/2026), 7 (28/2026), 16 (140/2025). O teto de mil campos (27 Perfis de
duas Modalidades) continua, fora do escopo.

## Constitution Check

| Princípio | Como esta feature o cumpre |
|---|---|
| I. Linguagem ubíqua | A linha usa as frases da tela e da Revisão (*cadastro reserva limitado*, *por publicação*); a Situação diz *pendência*, o termo do bloco que já existe. |
| II. Imutabilidade | Nada gravado muda: nem campo, nem rota, nem o que se envia (`FR-950`, `SC-350`). |
| III. Auditoria | Nada novo a auditar: não há ato novo. |
| IV. Regras explícitas | A tabela não calcula regra (`FR-947`): a pendência vem do domínio, pelo cálculo que a etapa já faz. Os gestos em lote da `051` mantêm prévia e alcance intactos (`FR-959`). |
| V. Simplicidade | Um script, três atributos de dados, uma função de comparação. Sem componente genérico, sem estado paralelo: a linha é leitura do cartão (`D-004`). |
| VI. Jornada | O cenário demonstrável é o da US1, pelo preview, sem shell: abrir a etapa de 7 Perfis, editar dois, salvar. |

**Gate: passa.** Nenhuma exceção a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/052-perfis-visao-do-conjunto/
├── spec.md
├── plan.md
├── research.md
├── quickstart.md
├── contracts/tela-da-etapa.md
├── rastreabilidade.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/interface/
├── forms.py                     # perfis_alterados(digitados, gravados) — R-004
├── views.py                     # contexto: pendencias_por_perfil, perfis_alterados
├── templates/interface/
│   ├── compor_perfis.html       # a ordem da UX-120, o lugar da tabela, o script, o estilo
│   └── _perfil.html             # legenda, id do cartão, data-pendencias, data-alterado, data-resumo
├── templatetags/interface_extras.py   # legenda_do_perfil — R-006
└── static/interface/
    └── perfis.js                # a vista: tabela, um cartão por vez, invalid, âncora, foco

backend/tests/
├── interface/test_visao_dos_perfis.py   # o que o servidor entrega (TV)
└── javascript/perfis.test.js            # as regras puras do script (TJ)
```

**Structure Decision**: o monólito de sempre; um arquivo de script e um de teste de cada lado.

## Complexity Tracking

Nenhuma violação a justificar.
