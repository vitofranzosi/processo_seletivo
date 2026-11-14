# Implementation Plan: O alcance da Etapa por Modalidade

**Branch**: `claude/163-alcance-da-etapa` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/163-alcance-da-etapa-por-modalidade/spec.md`

## Summary

A Etapa ganha uma coluna, a lista dos códigos de Modalidade que ela alcança, com `NULL` dizendo
"todas as inscrições". O valor atravessa o caminho que o barema da `146` abriu: gravação do
rascunho, conteúdo publicado (degrau 22), contrato de mutabilidade, Retificação, Revisão e
documento. Um módulo puro novo, `editais/domain/alcance.py`, responde às duas perguntas que todo o
resto faz — *esta Etapa alcança esta Modalidade?* e *quais Modalidades, por identidade, ela alcança
neste conteúdo?* — e a regra de participação da `012` (`resultados/application/prontidao.py`) o
consulta como quarta regra. Como quase toda superfície da operação já lê a participação, a
distribuição, a Mesa, a Ocorrência, a consolidação e os painéis herdam o alcance sem mudar. Os
pontos que leem Resultado sem a participação — o universo da ordem, a Etapa de análise da
publicação das inscrições e o reingresso pendente — mudam um a um.

As decisões técnicas estão em [research.md](research.md) (`T-001` a `T-012`); o modelo, em
[data-model.md](data-model.md); as recusas e as frases, em [contracts/](contracts/); o roteiro, em
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13 (o do `pyproject.toml`), Django 5.2; JavaScript sem build na
composição das Etapas

**Primary Dependencies**: as do projeto; nenhuma nova

**Storage**: PostgreSQL — uma coluna `JSONField` anulável em `EtapaAvaliacao`
(`editais/0029`), com `CheckConstraint` contra a lista vazia. `EtapaAvaliacao` não é append-only:
o `M` da preparação do banco não muda

**Testing**: pytest contra PostgreSQL (`make test-pg`) — unidade para `alcance.py`, para a
participação e para a progressão; integração para publicação, Retificação, distribuição,
consolidação, universo da ordem e publicação das inscrições; interface para a composição, a
Retificação e os painéis; documento pelo compositor

**Target Platform**: o monólito Django — gestão em `/gestao/`, portal, documento PDF

**Project Type**: aplicação web, backend com templates

**Performance Goals**: nenhuma consulta nova nas superfícies com orçamento declarado da `011`, da
`012` e da `015`. O alcance sai do conteúdo publicado que `_anteriores_e_gate` já lê, e vira
condição dentro da consulta que já ia acontecer (T-005)

**Constraints**: CSP sem inline (`091`/`092`); toda classe nova com regra na folha; o vocabulário do
documento nas recusas; `domain` não importa `interface`; publicação imutável (o acervo se recompõe
idêntico, SC-2310); leitura de Resultado pelo manager `vigentes`

**Scale/Scope**: um campo, um degrau, quatro achados de publicação, uma recusa de Retificação, uma
regra de participação e três leitores fora dela

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano o atende | Situação |
|---|---|---|
| **I. Linguagem ubíqua** | "Alcance", "alcançada", "fora do alcance" — o termo do estudo e da L-2; as recusas falam assim | ✅ |
| **II. Imutabilidade e temporalidade** | O alcance é norma publicada, num degrau novo, e o acervo se lê como "todas" sem regravação (T-002). O ato praticado se lê com a versão que citou: a participação já é lida da versão vigente no ato | ✅ |
| **III. Segurança e auditoria** | Nenhuma permissão nova. A recusa de atribuir fora do alcance é do servidor, e não só da tela | ✅ |
| **IV. Regras explícitas e concorrência** | As recusas moram no domínio, com código e mensagem. A Retificação que estreita é recusada, e não aplicada com efeito colateral (clarify de 13/11). Retificação e distribuição se serializam pela linha do Edital (T-008) | ✅ |
| **V. Rastreabilidade e simplicidade** | Um módulo puro e um campo; nenhuma tabela nova; a regra entra no ponto único de participação, e não em cada superfície (T-005). Matriz `rastreabilidade.md` na implementação | ✅ |
| **VI. Jornada demonstrável** | O quickstart monta o Edital de três Perfis da spec pelos helpers dos testes e percorre as cinco histórias | ✅ |

Re-check depois do desenho: sem violação. Um refinamento da spec saiu do desenho: a FR-6964 passou
a impedir também a Etapa restrita **pontuada e enumerada por marco**, porque o universo
classificável manda para "sem posição" quem não tem nota numa Etapa pontuada enumerada (T-006).

## Project Structure

### Documentation (this feature)

```text
specs/163-alcance-da-etapa-por-modalidade/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── recusas.md        # os achados de publicação, a recusa da Retificação e as de operação
│   └── telas-e-documento.md   # composição, Retificação, Revisão, painéis, documento
├── checklists/requirements.md
├── rastreabilidade.md    # escrito na implementação
└── tasks.md              # $speckit-tasks
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── editais/
│   ├── models/etapas.py                 # EtapaAvaliacao.alcance (JSONField, NULL = todas)
│   ├── migrations/0029_alcance_da_etapa.py
│   ├── domain/alcance.py                # NOVO: normalizar, alcanca, modalidades_alcancadas, descrever
│   ├── domain/etapas.py                 # validate_stage: lista vazia, código repetido, tipo
│   ├── domain/validation.py             # quatro achados: código inexistente, papel proibido, denominação
│   ├── domain/mutabilidade.py           # ("stages", "modalityCodes"): retificavel()
│   ├── domain/reaproveitamento.py       # a cópia do Edital leva o alcance
│   ├── application/draft.py             # grava o alcance; aviso de código inexistente
│   └── api/serializers.py               # o campo na API de rascunho
├── publicacoes/
│   ├── application/publish_edital.py    # "modalityCodes" em _stages
│   ├── application/retificacoes.py      # recusa de estreitar sobre Atribuição ou Resultado
│   ├── domain/elevacao.py               # degrau 22: modalityCodes = None
│   ├── domain/alteracoes.py, colecoes.py  # o campo novo nas alterações de Etapa
│   └── infrastructure/pdf.py, apresentacao.py  # a frase do alcance (redações 1, 2 e 3)
├── shared/canonical.py                  # SCHEMA_VERSION = 22
├── resultados/
│   ├── application/prontidao.py         # quarta regra; estado FORA_DO_ALCANCE; gate por alcance
│   └── domain/progressao.py             # anterior_que_alcanca
├── classificacao/application/calculo.py # _universo pela última enumerada que alcança
├── divulgacao/application/inscricoes.py, domain/publicabilidade.py  # análise e reingresso
└── interface/
    ├── forms.py, views.py               # o campo na composição das Etapas
    ├── retificacao.py                   # o alcance entre os CAMPOS_ETAPA
    ├── revisao.py                       # a linha do alcance
    ├── andamento.py                     # "N alcançadas, de M"
    ├── static/interface/alcance.js      # mostra a lista só com "Só as inscrições destas Modalidades"
    ├── static/interface/telas/compor-etapas.css
    └── templates/interface/_etapa.html, _painel_da_etapa (o que já desenha o panorama)

backend/tests/
├── unit/editais/test_alcance_da_etapa.py
├── unit/resultados/test_participacao_por_alcance.py
├── integration/editais/test_publicacao_do_alcance.py
├── integration/publicacoes/test_retificacao_do_alcance.py
├── integration/resultados/test_operacao_com_alcance.py
├── integration/classificacao/test_universo_com_alcance.py
├── integration/divulgacao/test_inscricoes_com_alcance.py
└── interface/test_composicao_do_alcance.py
```

**Structure Decision**: o monólito existente. Nenhum app novo: o alcance é atributo da Etapa, e a
regra é da participação, que já tem dono em `resultados`.

## Increments

Um PR, três commits, na ordem da dependência:

1. **A — a norma.** Coluna, gravação, validação, degrau 22, mutabilidade, documento, Revisão,
   composição (US1). Sem consumidor, o alcance publicado ainda não muda a operação — e é por isso
   que A e B vão juntos para produção.
2. **B — a operação.** `alcance.py` na participação e na progressão; universo da ordem; publicação
   das inscrições e reingresso; "N alcançadas, de M" (US2, US3, US4).
3. **C — a Retificação.** O campo na tela, a recusa de estreitar, a serialização com a distribuição
   (US5).

## Complexity Tracking

Sem violação a justificar.
