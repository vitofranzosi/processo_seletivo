# Implementation Plan: Minhas atividades

**Branch**: `claude/160-plano-e-tarefas` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: a spec da `160`, com D-001 a D-010, e as três decisões do estudo que o usuário tomou em
12/11/2026 (6ª: pouso na Lista; 7ª: formalização fora; 8ª: uma requisição, teto por Edital).

**Implementação**: não autorizada. Este plano é para o usuário ler antes de decidir.

## Summary

O plano tem três peças.

**1. A leitura.** Um módulo de leitura, `interface/atividades.py`, reúne para a pessoa o que a
derivação da `127` já marca como SUA, Edital por Edital (R-001). Os Editais vêm:
- da presidência lida no vínculo (R-002);
- da alocação à conferência, só nos Perfis alocados.

Para quem não preside, a derivação não roda: a avaliação vem da carga que a página já calcula, com a
frase do andamento e o número da Mesa (R-005, D-010). O módulo filtra pela base (R-003), agrupa o mesmo
ato sem número entre Editais (R-006) e ordena sem usar a data (R-007). Ele também rotula a fase do
Centro (R-008) e guarda os Editais que não puderam ser lidos (R-004).

**2. A página.** A view `minhas_etapas` passa a desenhar três seções e a nota de cobertura, e o nome
visível vira "Minhas atividades" em toda a gestão (R-011). Na Lista, a nota da faixa aponta para a
página (R-010).

**3. O segundo incremento.** A versão vigente passa a ser lida uma vez por requisição, nesta página e
no Centro (R-009).

**Onde está o risco.**
- **Coerência.** A página só não diverge do Centro se não tiver regra própria. O teste de coerência,
  que estende o SC-1230 da `127`, é a guarda.
- **Custo da presidência.** É linear e não tem otimização barata além da R-009.

## Technical Context

**Language/Version**: Python 3.13 · **Primary Dependencies**: Django; nenhuma nova

**Storage**: PostgreSQL, só leitura. Nenhuma migration e nenhuma tabela; o `M` do `provisionar` não
muda.

**Testing**: pytest contra PostgreSQL (`make test-pg`).
- Funções puras em `tests/unit/interface/test_atividades.py`, sem banco.
- Jornadas por `Client` em `tests/interface/test_minhas_atividades.py`.
- Coerência com o Centro em `tests/interface/test_minhas_atividades_coerencia.py`, no molde de
  `test_andamento_coerencia.py`.
- Custo em `tests/performance/test_minhas_atividades_em_escala.py` (R-012).
- Os 11 arquivos que fixam o nome visível (R-011) e os 2 da nota da faixa (R-010).

**Target Platform**: `/gestao/`:
- "Minhas atividades" (`/gestao/minhas-etapas`);
- a Etapa e a Mesa, só a trilha;
- a Lista, só a nota da faixa e o link;
- o Centro de Controle, só a R-009.

**Performance Goals**:
- Membro: número constante de consultas, qualquer que seja o número de comissões, e zero chamadas à
  derivação (FR-6877).
- Presidência: no máximo `TETO_POR_EDITAL` consultas por Edital presidido, medido na tarefa (FR-6878,
  R-012).
- R-009: −19% para a presidência, medido no estudo, com os mesmos itens.

**Constraints**:
- CSP sem estilo nem script embutido.
- Toda classe nova com regra na folha da tela (`telas/minhas-etapas.css`).
- `details` nativo para as seções recolhidas e os grupos.
- Nenhum `raise Http404` novo.
- A barra lateral continua sem consulta (a FR-1715 da `076`).
- A Lista continua sem a derivação (a FR-2806 da `104`).

**Scale/Scope**:
- Um módulo novo (`atividades.py`).
- Edições em `views.py` (`minhas_etapas`, `lista` só no contexto do link), `navegacao.py`,
  `trabalho.py` (a constante) e `andamento.py` (uma função pública para a frase da avaliação).
- `publicacoes/application/selectors.py` e o Centro, no segundo incremento.
- Quatro templates, `_acoes_disponiveis.html` e uma folha.
- Dois documentos: o guia da equipe e o manual.

## Constitution Check

*GATE: passa antes da Phase 0; reconferido depois do desenho.*

| Princípio | Como é atendido |
|---|---|
| I. Linguagem ubíqua | A página não escreve frase própria para ato da derivação (FR-6859). "Atividade" é o nome da página, e não um conceito novo de domínio: não colide com termo da gestão (D-001). |
| II. Integridade normativa e temporalidade | Nada publicado muda. A R-009 só memoriza a versão **vigente** do instante da requisição; a leitura de um ato histórico, com outro `at`, passa direto. |
| III. Segurança, dados e auditoria | Nenhuma permissão nova, e o escopo do ator em toda consulta. A página só leva à tela do ato, que verifica pela porta de sempre (FR-6884). O Gestor não ganha visão nova: lê menos do que o Centro já lhe mostra. |
| IV. Regras explícitas | "Sua" é a regra única de `_Leitor.e_sua`. A página filtra a base pelo caminho por que leu o Edital (R-003), e não decide se a pessoa pratica o ato. |
| V. Qualidade, rastreabilidade e simplicidade | Spec, plano, tarefas e, na implementação, matriz e verificação. Nenhuma fila, tarefa, estado ou cache entre requisições (FR-6884, D-009). |
| VI. Completude de jornada | É o propósito: o trabalho que já tem porta, um Edital por vez, passa a ter porta na página pessoal. |

**Resultado**: passa. Reconferido depois do desenho: passa, sem exceção a justificar.

## Project Structure

### Documentation (this feature)

```text
specs/160-minhas-atividades/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md
├── contracts/telas.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── interface/atividades.py                     # novo: a leitura e as funções puras (R-001)
├── interface/andamento.py                      # ato_de_avaliar(n), pública (R-005)
├── interface/trabalho.py                       # FORA_DA_FAIXA diz onde está cada coisa (R-010)
├── interface/navegacao.py                      # o rótulo da seção (R-011)
├── interface/views.py                          # minhas_etapas; o Centro abre o contexto da R-009
├── publicacoes/application/selectors.py        # versao_vigente_da_requisicao (R-009)
├── interface/templates/interface/
│   ├── minhas_etapas.html                      # três seções, cobertura, não lidos
│   ├── _atividade.html                         # novo: uma linha ou um grupo
│   ├── minha_etapa.html · mesa_inscricao.html  # trilha
│   ├── lista.html                              # "Ver minhas atividades"
│   └── _acoes_disponiveis.html                 # link depois da nota
└── interface/static/interface/telas/minhas-etapas.css
backend/tests/
├── unit/interface/test_atividades.py
├── interface/test_minhas_atividades.py
├── interface/test_minhas_atividades_coerencia.py
└── performance/test_minhas_atividades_em_escala.py
doc/
├── cenarios-de-treinamento/guia-da-equipe.md
└── manual/00-arquitetura-do-manual.md
```

**Structure Decision**: o monólito de sempre. O módulo novo fica em `interface/`, ao lado de
`trabalho.py` e `andamento.py`, porque é leitura de apresentação sobre duas derivações dali.

## Incrementos

1. **A — a página.** O nome, a leitura, as seções, a cobertura, a nota da Lista, a coerência e o
   custo sem a R-009. É entregável sozinho e cumpre todo FR, exceto a FR-6879.
2. **B — a versão vigente uma vez (R-009).** A FR-6879 e o SC-2280, na página e no Centro. Fica para
   um PR próprio, porque atravessa features que chamam `effective_version` direto.

## Complexity Tracking

Nenhuma violação.
