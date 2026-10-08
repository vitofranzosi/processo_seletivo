# Implementation Plan: Detecção de conflitos de numeração no Edital

**Branch**: `claude/065-conflitos-de-numeracao` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/065-conflitos-de-numeracao/spec.md`, e
[insumos-para-o-plano.md](insumos-para-o-plano.md)

## Summary

O número que quem elabora digita no começo de um parágrafo de seção textual passa a ser conferido
contra o número com que a seção sai no documento (`054`, `FR-985`); o conflito comprovado impede a
submissão e a publicação do Edital (`D-001`) e é só aviso na Retificação (`D-002`). As remissões
internas de todo texto livre impresso são cruzadas com os itens que o documento imprime, e a
ambígua, a sem destino e a suspeita viram avisos (`D-003`).

A mudança é **uma validação a mais, sem estado**: um módulo puro reconhece números e remissões
(`D-005`, `D-010`); o compositor ganha uma função que diz, pela regra que ele mesmo usa, quais itens
o documento imprime (`D-004`), sem mudar uma linha da composição (`D-014`); a validação cruza os dois
e escreve a mensagem; a interface leva o achado ao campo da seção (`D-008`). Nada renumera texto,
nada muda no PDF, nenhum Edital publicado é reavaliado.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: nenhuma nova. O reconhecimento é feito com a biblioteca padrão.

**Storage**: nenhuma mudança — nenhum modelo, campo ou migration (`FR-1220`).

**Testing**: pytest contra PostgreSQL (`make test-pg`, com `DB_NAME` próprio da worktree); testes de
unidade do reconhecimento com um conjunto de prova de casos legítimos; integração da submissão, da
publicação e da Retificação; interface da etapa Conteúdo e da Revisão; o guardião dos itens do
documento; e os bytes do documento.

**Target Platform**: o monólito Django; a interface administrativa (`/gestao/`).

**Project Type**: aplicação web (monólito).

**Performance Goals**: nenhuma consulta nova (`D-015`): as conferências são funções do snapshot que a
Revisão, a submissão e a publicação já montam. Uma passada linear sobre o texto.

**Constraints**: o documento sai com os mesmos bytes (`FR-1219`); nenhum código de aviso coincide com
o de um impeditivo (`D-006`); nenhuma superfície afirma remissão correta (`FR-1209`).

**Scale/Scope**: o maior Edital medido — o cenário B — tem 18 Perfis, 22 seções e 11 seções textuais.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre | Situação |
|---|---|---|
| I. Linguagem ubíqua | "seção", "subitem", "remissão", "parágrafo" com o sentido do Edital; nenhum termo novo de domínio; as mensagens não usam código interno (`UX-159`) | ✅ |
| II. Integridade normativa, imutabilidade | nenhum Edital publicado é recomposto nem reavaliado (`FR-1218`, `D-013`); o documento não muda (`FR-1219`, `D-014`); o número conferido é o da regra única (`D-004`) | ✅ |
| III. Segurança e auditoria | nenhuma permissão nova; a validação roda nos atos que já exigem permissão e já auditam; nenhum dado pessoal | ✅ |
| IV. Regras explícitas | a regra mora no domínio e é verificada no backend, nas três portas (Revisão, submissão, publicação); o impeditivo bloqueia como os demais; nada é inferido em nome de quem elabora — o sistema não renumera (`FR-1203`) | ✅ |
| V. Qualidade, rastreabilidade, simplicidade | módulo puro testável; guardião contra a segunda regra; casos-limite com teste próprio na matriz; nenhuma dependência nova | ✅ |
| VI. Jornada demonstrável | quem elabora escreve na etapa Conteúdo, vê o achado, segue o link até a seção, tem a submissão recusada e corrige — tudo pela interface administrativa ([quickstart.md](quickstart.md) §6) | ✅ |

**Re-check depois do desenho (Fase 1):** sem violação. A importação adiada do compositor pela
validação (`D-004`) é a única escolha fora do padrão da casa, e é justificada pela regra única da
`054`; não há teste de camadas que ela contrarie.

## Project Structure

### Documentation (this feature)

```text
specs/065-conflitos-de-numeracao/
├── spec.md
├── insumos-para-o-plano.md
├── plan.md
├── research.md            # D-004 a D-016
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── achados-de-numeracao.md
│   └── itens-do-documento.md
├── checklists/requirements.md
└── tasks.md               # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/domain/
│   ├── numeracao_digitada.py         # NOVO — reconhecimento puro (D-005, D-010)
│   └── validation.py                 # duas conferências registradas em validate_for_publication (D-006, D-007, D-011)
├── publicacoes/infrastructure/
│   └── pdf.py                        # função dos itens do documento; composição intocada (D-004, D-014)
└── interface/
    ├── views.py                      # CODIGOS_DO_TEXTO_DA_SECAO e âncora por seção (D-008)
    └── templatetags/interface_extras.py  # RESUMO_DAS_REPETIDAS para as remissões (D-016)

backend/tests/
├── unit/editais/test_numeracao_digitada.py           # NOVO — formas e conjunto de prova (SC-464)
├── unit/editais/test_conflito_de_numeracao.py         # NOVO — achados no snapshot (FR-1198..1217)
├── unit/publicacoes/test_itens_do_documento.py        # NOVO — o guardião (D-004)
├── integration/publicacoes/test_numeracao_na_publicacao.py   # NOVO — submissão, publicação, Retificação, Edital publicado
├── interface/test_numeracao_na_revisao.py             # NOVO — etapa Conteúdo, Revisão, link, recusa
└── contract/ (fixture de bytes)                       # inalterada — prova de FR-1219
```

**Structure Decision**: monólito existente; um módulo de domínio novo, uma função nova no compositor
e duas conferências na validação. Nenhum app, modelo ou rota nova.

## Fases de implementação (para o `$speckit-tasks`)

1. **Reconhecimento puro** (`numeracao_digitada.py`) com o conjunto de prova — independente de tudo.
2. **Itens do documento** em `pdf.py` e o guardião — independente do passo 1.
3. **Conflito de numeração** em `validation.py` (User Story 1, impeditivo na publicação, código
   próprio na Retificação).
4. **Remissões** em `validation.py` (User Story 2).
5. **Interface**: destino por seção, resumo das repetidas (User Stories 1 a 3).
6. **Integração**: submissão, publicação, Retificação, Edital publicado, bytes (User Stories 3 e 4).
7. **Validação com os cenários A e B** ([quickstart.md](quickstart.md)), README, rastreabilidade,
   `make lint check test-pg`.

## Riscos

| Risco | Mitigação |
|---|---|
| Segunda regra de numeração (contagem de tabelas, subseções comuns) | `D-004`: função no compositor + guardião que compõe de verdade |
| Falso positivo impeditivo trava Edital certo | definição estreita (`D-010`), conjunto de prova (`SC-464`), revisão manual sobre a amostra real ([insumos](insumos-para-o-plano.md) §3, passo 7) |
| Aviso da Retificação some na confirmação | código próprio (`D-006`) e teste da confirmação |
| Mudança acidental de bytes no PDF | nenhuma linha da composição muda; fixture inalterada; render dos conteúdos congelados |
| Orçamento de consulta da Revisão | nenhuma consulta nova (`D-015`); os testes de orçamento existentes ficam como estão |
| Suítes paralelas disputam o banco de teste | `DB_NAME` próprio da worktree |

## Complexity Tracking

Sem violações a justificar.
