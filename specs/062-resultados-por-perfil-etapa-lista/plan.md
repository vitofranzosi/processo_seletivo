# Implementation Plan: Resultados divulgados por Perfil, etapa e lista

**Branch**: `claude/062-resultados-por-perfil-etapa-lista` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/062-resultados-por-perfil-etapa-lista/spec.md`

## Summary

Trocar a lista cronológica de vigentes da página pública do Edital por uma árvore Perfil → etapa →
lista, montada em memória a partir do que a página já lê: as vigentes com as cadeias delas
(`historico_publico_do_edital`), o cabeçalho congelado de cada publicação e o conteúdo vigente do
Edital ([D-005](research.md)). Cada lista mostra, na própria linha, nome, natureza, data e prazo de
recurso; o link tem o nome da lista como texto visível e um texto oculto com etapa e Perfil
([D-006](research.md)). O histórico vira um bloco por etapa. Um convite para a situação individual
fecha o bloco, com destino conforme quem lê, e a volta depois da identificação passa a reconhecer a
página do Edital ([D-007](research.md)).

Nenhuma publicação, documento, cadeia ou regra muda, e nenhuma leitura ao banco é acrescentada
([D-011](research.md)).

## Technical Context

**Language/Version**: Python 3.12, Django 5 (templates server-rendered); CSS à mão na folha do
portal

**Primary Dependencies**: nenhuma nova

**Storage**: N/A — nenhuma migration, nenhum modelo; leitura do que já é lido

**Testing**: pytest (`make test-pg`); um arquivo novo, `tests/portal/test_resultados_por_perfil.py`;
três arquivos adaptados à marcação nova ([D-012](research.md)); guardas existentes:
`test_acessibilidade_do_portal.py`, `test_citacoes_de_requisito.py`,
`test_vocabulario_da_composicao.py`

**Target Platform**: navegador atual; 1280 × 900 e 375 px

**Project Type**: monólito web Django — portal público do candidato

**Performance Goals**: custo de consultas da página constante no número de publicações (`SC-448`)

**Constraints**: nome acessível começa pelo texto visível (*Clarifications* 07/10); nada de
natureza ou data acima da linha da lista (`FR-1155`); 375 px sem rolagem horizontal (`UX-153`)

**Scale/Scope**: um template (`portal/selecao.html`), a folha do portal, uma função em
`portal/leitura.py`, a view `selecao`, o ajudante `_de_volta_a_vaga` e uma chave em `_rotulos`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o respeita | Situação |
|---|---|---|
| I. Linguagem ubíqua | Perfil, etapa (marco), lista (Modalidade de cota), natureza: os termos que a página e o documento oficial já usam. A tela não muda o domínio — a árvore é estrutura de leitura. | ✓ |
| II. Imutabilidade e temporalidade | Nenhuma publicação muda. O que foi publicado continua dizendo o nome do dia (D-004); só o título do grupo usa o vigente. Um instante para a página inteira, como hoje. | ✓ |
| III. Segurança e privacidade | O convite usa só as inscrições da própria pessoa, já lidas; sem sessão não há consulta. A volta depois da identificação continua conferida contra o host e só reconhece uma página pública GET (D-007). Nada identifica quem publicou. | ✓ |
| IV. Regras explícitas | Ordem de cada nível declarada (data-model) e o caso de cada convite tabelado. | ✓ |
| V. Rastreabilidade e simplicidade | Uma função pura, sem camada nova; testes por cenário e por invariante do contrato; regressão do #255 preservada. | ✓ |
| VI. Jornada demonstrável | Candidato abre o Edital pelo portal, acha a própria lista e chega à situação — pelo canal dele, sem shell (quickstart §3). | ✓ |

Sem violação; *Complexity Tracking* vazio.

**Re-check depois do desenho**: o contrato e o data-model não introduziram dado novo, rota nova nem
permissão nova; a única mudança fora da tela é o reconhecimento de `portal:selecao` como destino de
volta, coberta pela linha III. ✓

## Project Structure

### Documentation (this feature)

```text
specs/062-resultados-por-perfil-etapa-lista/
├── spec.md
├── plan.md              # este arquivo
├── research.md          # D-005 a D-012
├── data-model.md        # a árvore e as ordens
├── quickstart.md
├── verificacao.md       # medidas no navegador e o total da suíte (T022, T024)
├── contracts/
│   └── bloco-de-resultados.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── divulgacao/application/selectors.py   # _rotulos devolve também `perfil`
├── portal/leitura.py                     # resultados_por_perfil(vigentes, conteudo)
├── portal/views.py                       # selecao: árvore + convite; _de_volta_a_vaga
└── portal/templates/portal/
    ├── selecao.html                      # o bloco reescrito
    └── base.html                         # .oculto e as regras do bloco

backend/tests/portal/
├── test_resultados_por_perfil.py         # novo
├── test_historico_de_resultados.py       # adaptado (D-012)
├── test_prazo_recursal_publico.py        # adaptado (D-012)
└── test_resultado_publico.py             # adaptado (D-012)
```

**Structure Decision**: monólito existente; nenhum diretório novo.

## Complexity Tracking

Nenhuma violação a justificar.
