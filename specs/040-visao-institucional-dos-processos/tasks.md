---

description: "Tarefas da 040 — a visão institucional dos Processos Seletivos"
---

# Tasks: A visão institucional dos Processos Seletivos

**Input**: Design documents from `specs/040-visao-institucional-dos-processos/`

**Prerequisites**: [plan.md](./plan.md) · [spec.md](./spec.md) · [research.md](./research.md) ·
[data-model.md](./data-model.md) · [contracts/](./contracts/) · [quickstart.md](./quickstart.md)

**Tests**: **incluídos**, e não por preferência. A Constituição (Princípio V) exige cobertura
específica para autorização e integridade, e a §18 da spec já enumera vinte e dois cenários. Cada
tarefa de teste abaixo nomeia o cenário que ela realiza.

**Organization**: por jornada, nas três prioridades da seção *User Scenarios & Testing* da spec.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivo distinto, sem dependência pendente
- **[Story]**: `US1` · `US2` · `US3`; Setup, Foundational e Polish não têm rótulo

---

## Phase 1: Setup

**Purpose**: deixar a worktree capaz de rodar a suíte contra PostgreSQL. Nada de código de produto.

- [X] T001 Instalar as dependências de desenvolvimento declaradas em `backend/pyproject.toml` com `uv sync --extra dev` — worktree nova não tem `pytest`, e `make test-pg` falha com *"Failed to spawn: pytest"*
- [X] T002 Preparar o banco pelos alvos de `backend/Makefile`, na ordem correta: provisionar papéis, migrar, provisionar de novo — e conferir que a contagem `N de M` **não** começa em `0`
- [X] T003 Conferir `backend/manage.py migrate --check` limpo — migration desaplicada produz `relation ... does not exist` num arquivo sorteado, longe da causa

**Checkpoint**: `make lint check test-pg` verde **antes** de qualquer alteração, para que a linha de base seja conhecida.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a extração compartilhada, a capacidade e as formas de leitura. **Nenhuma jornada pode
começar antes desta fase**, e a T004 é a única que pode quebrar superfície existente.

**⚠️ A ordem T004 → T005 é obrigatória**: a suíte do portal verde é a condição para seguir.

- [X] T004 Extrair `versoes_vigentes(*, editais=None, at=None)` em `backend/processo_seletivo/publicacoes/application/selectors.py`, separando *"qual é a vigente"* de *"o que é público"* — duas consultas, a primeira sem carregar `content` (`R-003`, contrato §5) — **já satisfeita pelo acervo**: a função existe desde a `023`, e a pesquisa (`R-003`) não a viu.
- [~] T005 **Não executada, e a razão é um achado.** `versoes_vigentes` **já existia** (`023`, `FR-004a`) em `backend/processo_seletivo/publicacoes/application/selectors.py`, com a mesma forma de duas consultas e o mesmo critério de desempate — a `T004` estava satisfeita antes de começar, e a `040` é a segunda consumidora. O que sobra é a duplicação **pré-existente** dentro de `selecoes_publicas`, que mistura *qual é a vigente* com *o que é público*: removê-la custaria ou uma consulta a mais na vitrine, ou política de visibilidade dentro do resolvedor compartilhado. **Achado registrado, fora do escopo desta feature.**
- [X] T006 [P] Criar `backend/processo_seletivo/interface/visao_geral.py` com o cabeçalho do módulo declarando a invariante *"este módulo só lê"* e a constante `CONSULTAR = "visao:consultar"` (`R-002`)
- [X] T007 [P] Implementar as formas `Ausencia` e `Numero` em `backend/processo_seletivo/interface/visao_geral.py`, com a invariante `valor is None` ⇔ `ausencia is not None` e `0` sempre valor (data-model §2.1, §2.2)
- [X] T008 Acrescentar `"visao:consultar"` ao papel `gestor` em `backend/processo_seletivo/interface/identidade.py`, escrita **literalmente** e com o comentário da razão — a fronteira de identidade não importa a permissão de quem a consome
- [X] T009 Acrescentar a rota `visao-geral` em `backend/processo_seletivo/interface/urls.py`, de primeiro nível porque a página é do escopo e não de agregado (`R-001`)
- [X] T010 Implementar a view `visao_geral` em `backend/processo_seletivo/interface/views.py` — redirecionar quem não se identificou, `require_permission(ator, visao_geral.CONSULTAR)`, e montagem de contexto apenas, sem derivação

**Checkpoint**: a rota responde `403` a quem não tem a capacidade e `200` vazio a quem tem.

---

## Phase 3: User Story 1 — Quanto ofertamos, e quanta procura recebemos (P1) 🎯 MVP

**Goal**: os quatro números e a tabela de sete colunas do ano corrente, com a gramática da ausência
e do zero legítimo, e o caminho até o Edital.

**Independent Test**: com `seed_demo` aplicado, abrir `/gestao/visao-geral` como `gestor`, obter os
quatro números e a tabela, e conferir cada número contra a tela dona daquele fato.

### Tests for User Story 1 ⚠️

> Escrever antes da implementação, e confirmar que falham.

- [X] T011 [P] [US1] Testes das derivações sem requisição em `backend/tests/unit/test_visao_institucional.py`, cobrindo `T-01`, `T-02`, `T-03`, `T-04`, `T-06`, `T-07` e `T-10` da §18, com `agora=` explícito
- [X] T012 [P] [US1] Testes do Edital misto em `backend/tests/unit/test_visao_institucional.py` — `T-03b` (razão `2,0` e nunca `7,0`) e `T-03c` (o consolidado concorda com a linha), que juntos prendem `D-012`
- [X] T013 [P] [US1] Teste da tela em `backend/tests/interface/test_visao_geral.py` — `T-11` (recorte do ano corrente declarado), `T-15` (a linha leva ao Edital), `SC-208` (nenhum `0` onde há ausência, nenhuma ausência onde há zero), o **termo literal** *"Em preenchimento"*, que é o da tela dona e não *"Rascunhos"* (`FR-586`), e a metade de interface de `SC-213`: no Edital misto, **a linha declara a população usada** na razão — a metade que `T017` prende no cálculo e que some da tela sem nada acusar
- [X] T014 [P] [US1] Teste de autorização em `backend/tests/authorization/test_visao_institucional.py` — `T-12` (`403` explicado a quem não tem a capacidade), `T-19` (escopo alheio não aparece), a **grafia** de `visao:consultar` no padrão do teste que prende `matricula:exportar`, e a **ausência do caminho** em `lista.html` para quem não tem a capacidade — as duas metades de `SC-211`, e a segunda é a que some sem ninguém notar
- [X] T015 [P] [US1] Teste do consolidado em `backend/tests/unit/test_visao_institucional.py` (`T-08`) — num recorte com Editais em fases diferentes, o agregado declara **os três**: quantos publicaram conteúdo (`FR-585`), quantos somandos são parciais (`FR-595`) e quantos ficaram fora da razão (`FR-590`). *Era o único dos vinte e quatro cenários da §18 sem tarefa*
- [X] T016 [P] [US1] Teste de concordância com a tela dona em `backend/tests/interface/test_visao_geral.py` (`SC-207`) — o mesmo Edital lido na visão e na tela de inscrições recebidas devolve o **mesmo** número de submetidas. *É a única verificação automatizada de `FR-582` (fonte única); sem ela a garantia dependia do percurso manual do quickstart*

### Implementation for User Story 1

- [X] T017 [US1] Implementar `Recorte` e o saneamento dos parâmetros em `backend/processo_seletivo/interface/visao_geral.py`, com o ano corrente por omissão e `anos_disponiveis` de `DISTINCT Edital.year` sem abrir snapshot (data-model §2.7, `FR-599`)
- [X] T018 [US1] Implementar a leitura de vagas por Edital em `backend/processo_seletivo/interface/visao_geral.py`, somando `profiles[].immediateVacancies` da versão vigente e devolvendo `Ausencia(NAO_PUBLICADO)` onde não há conteúdo (`FR-587`)
- [X] T019 [US1] Implementar a agregação de inscrições por Edital, **Perfil** e estado em `backend/processo_seletivo/interface/visao_geral.py` — uma consulta, e o total da coluna *Submetidas* saindo da mesma leitura que o numerador (`R-004`)
- [X] T020 [US1] Implementar a razão recortada em `backend/processo_seletivo/interface/visao_geral.py` — numerador só dos Perfis com `immediateVacancies > 0`, e `Ausencia(NAO_APLICAVEL)` quando nenhum tem (`FR-588`, `FR-589`)
- [X] T021 [US1] Implementar `SituacaoDoPeriodo` em `backend/processo_seletivo/interface/visao_geral.py` reusando `periodo_de_inscricoes` do domínio da `009`, com `nao-designado` virando `Ausencia` (data-model §2.4)
- [X] T022 [US1] Implementar `LinhaDoEdital` e `Consolidado` em `backend/processo_seletivo/interface/visao_geral.py`, com os denominadores como **campos** e a contagem de parciais e de fora-da-razão (`FR-585`, `FR-590`, `FR-595`)
- [X] T023 [US1] Criar `backend/processo_seletivo/interface/templates/interface/visao_geral.html` — os quatro números com os denominadores **abaixo** de cada um, e a tabela de sete colunas com cabeçalhos associados
- [X] T024 [P] [US1] Criar `backend/processo_seletivo/interface/templates/interface/_linha_do_edital.html` com a linha e as quatro grafias de ausência escritas por extenso
- [X] T025 [US1] Acrescentar as regras de estilo no `<style>` de `backend/processo_seletivo/interface/templates/interface/base.html` — é onde o CSS deste projeto mora, e não há folha externa (`R-007`)
- [X] T026 [US1] Acrescentar o caminho para a visão geral em `backend/processo_seletivo/interface/templates/interface/lista.html`, condicionado à capacidade — e **não** no cabeçalho de `base.html`, que não depende de papel (`R-001`, `FR-605`)
- [X] T027 [US1] Escrever a declaração do que a página não mede em `backend/processo_seletivo/interface/templates/interface/visao_geral.html` — matrícula efetivada, obsolescência de apuração, as dimensões ausentes e os indicadores ainda não apresentados (`FR-596`)

**Checkpoint**: a `US1` entra em produção sozinha. É o MVP.

---

## Phase 4: User Story 2 — Onde a procura faltou (P2)

**Goal**: as duas marcas de atenção, derivadas por aritmética sobre colunas já apresentadas.

**Independent Test**: semear um Edital com período encerrado e zero submetidas e outro com razão
menor que 1; identificar os dois lendo o texto, **sem** usar cor.

### Tests for User Story 2 ⚠️

- [X] T028 [P] [US2] Testes das marcas em `backend/tests/unit/test_visao_institucional.py` — `T-05` (sem procura), a marca de demanda abaixo da oferta, e o caso **sem marca** do período aberto com zero submetidas
- [X] T029 [P] [US2] Teste de legibilidade sem cor em `backend/tests/interface/test_visao_geral.py` (`T-17`) — a marca aparece no texto visível, e não só numa classe de estilo

### Implementation for User Story 2

- [X] T030 [US2] Implementar `Marca` e as duas espécies em `backend/processo_seletivo/interface/visao_geral.py` — sem identificador de catálogo, sem destino próprio e sem severidade (data-model §2.5, `D-007`)
- [X] T031 [US2] Apresentar as marcas em `backend/processo_seletivo/interface/templates/interface/_linha_do_edital.html`, em texto, com a cor como reforço e nunca como único meio

**Checkpoint**: a tabela responde *"quais merecem atenção?"* sem subsistema de alertas.

---

## Phase 5: User Story 3 — Recortar o período e o portfólio (P3)

**Goal**: os filtros além do padrão, a busca e a ordenação.

**Independent Test**: com Editais de dois anos no acervo, trocar o ano e verificar que consolidado e
tabela mudam juntos; ordenar por Inscr./vaga nos dois sentidos e verificar onde as ausências ficam.

### Tests for User Story 3 ⚠️

- [X] T032 [P] [US3] Teste da ordenação com ausências em `backend/tests/unit/test_visao_institucional.py` (`T-09`) — ao fim **nos dois sentidos**, o que `reverse=True` sobre a mesma chave não produz (`R-008`)
- [X] T033 [P] [US3] Testes dos filtros em `backend/tests/interface/test_visao_geral.py` — `T-13` (consolidado e tabela mudam juntos), `T-14` (situação do período aplicada **depois** da materialização) e o saneamento de parâmetro inválido

### Implementation for User Story 3

- [X] T034 [US3] Implementar os filtros relacionais — ano, situação e busca — aplicados **antes** da materialização das versões, em `backend/processo_seletivo/interface/visao_geral.py` (`FR-598`)
- [X] T035 [US3] Implementar o filtro por situação do período, aplicado **depois**, sobre o conjunto já reduzido, em `backend/processo_seletivo/interface/visao_geral.py` (`FR-598`)
- [X] T036 [US3] Implementar a ordenação com chave em tupla `(valor is None, valor)` em `backend/processo_seletivo/interface/visao_geral.py`, e o conjunto `ORDENS` saneado no padrão de `portal/leitura.py` (`FR-601`)
- [X] T037 [US3] Apresentar os controles de filtro, busca e ordenação em `backend/processo_seletivo/interface/templates/interface/visao_geral.html`, com rótulos associados e o recorte aplicado declarado em texto

**Checkpoint**: a página serve à análise de qualquer período do acervo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: as garantias que atravessam as três jornadas, e os guardiões que só falham se alguém
esquecer.

- [X] T038 [P] Teste do orçamento de consulta em `backend/tests/performance/test_visao_institucional.py` (`T-20`) — **igualdade** de contagem entre 3 e 60 Editais, com `CaptureQueriesContext`, e não um teto absoluto (`R-010`, `SC-209`)
- [X] T039 [P] Teste da contagem de snapshots em `backend/tests/performance/test_visao_institucional.py` (`T-21`, `T-22`) — o recorte de um ano com 3 Editais abre **3** conteúdos num acervo de 60, e o seletor de anos abre **zero**
- [X] T040 [P] Varredura do HTML renderizado em `backend/tests/interface/test_visao_geral.py` (`T-16`, `SC-210`) — com inscrições submetidas presentes, **nenhum** nome, CPF, e-mail ou telefone; e **nenhum rótulo de contagem** dizendo *candidatos* ou *pessoas*, porque o que a página conta é **inscrição** (`FR-593`)
- [X] T041 [P] Teste da declaração do que não se mede em `backend/tests/interface/test_visao_geral.py` (`T-18`, `SC-212`)
- [X] T042 Conferir se a prosa visível de `visao_geral.html` e `_linha_do_edital.html` usa *recorte*, *geração* ou *faixa*; se usar, acrescentar a tela a `TELAS` em `backend/tests/test_vocabulario_da_composicao.py` **no mesmo commit** e definir o termo em `<dfn>` — a lista é literal e a tela escapa da regra em silêncio (`R-006`)
- [X] T043 Conferir o comportamento em largura de telefone de `backend/processo_seletivo/interface/templates/interface/visao_geral.html` — período, em preenchimento e razão recolhem; Processo/Edital, situação, vagas e submetidas ficam
- [X] T044 Percorrer os dezessete passos de `specs/040-visao-institucional-dos-processos/quickstart.md` pela interface, com o servidor de `backend/` e `INTERFACE_SELETOR_IDENTIDADE=true` — é o cenário demonstrável que o Princípio VI exige (`SC-206`)
- [X] T045 Escrever `specs/040-visao-institucional-dos-processos/rastreabilidade.md` cobrindo **cada** `FR-581` a `FR-605` e `SC-206` a `SC-214` — o guardião cobra requisito a requisito, sem tolerância para sufixo de letra
- [X] T046 Rodar os alvos de `backend/Makefile` com `cd backend && make lint check test-pg` — `lint` são **dois** passos, e `test-pg` e não `test`; não editar arquivo durante a execução — **7535 passaram, 11 puladas, 0 falharam** (11m31s, 3ª execução). As duas primeiras acusaram quatro regressões minhas, todas pegas por guardiões já existentes.

---

## Dependencies & Execution Order

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational)  ← T004 → T005 em série; T006/T007 em paralelo
   ↓
Phase 3 (US1) 🎯 MVP ─────────────┐
   ↓                              │  US2 e US3 dependem da tabela da US1;
Phase 4 (US2)                     │  entre si são independentes e podem
Phase 5 (US3)  ← independentes ───┘  ser feitas em qualquer ordem
   ↓
Phase 6 (Polish)
```

**A única dependência dura fora da ordem de fases** é `T004 → T005`: a extração só está correta
quando a suíte do portal continua verde, e seguir sem isso arrisca a superfície pública.

**US2 e US3 não dependem uma da outra.** As duas dependem da `US1` porque operam sobre a tabela que
ela cria — `US2` sobre as colunas, `US3` sobre o conjunto.

### Paralelismo por fase

| Fase | Podem correr juntas |
|---|---|
| 2 | `T006`, `T007` — arquivos distintos, sem dependência |
| 3 | `T011`, `T012`, `T013`, `T014`, `T015`, `T016` (os seis testes) · `T024` com `T023` |
| 4 | `T028`, `T029` |
| 5 | `T032`, `T033` |
| 6 | `T038`, `T039`, `T040`, `T041` |

---

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3.** Vinte e sete tarefas — `T001` a `T027` —, e a página entra em produção
respondendo as quatro perguntas de `SC-206`. `US2` e `US3` são incrementos que não pedem retrabalho:
a `US2` acrescenta um campo à linha, e a `US3` acrescenta parâmetros ao recorte que já existe.

**O que esta feature deliberadamente não faz**, e que não deve aparecer em tarefa nenhuma:
classificados, convocados, ocupação, requerimentos, pessoas distintas e a série por ano — definidos
na §9 da spec e registrados em `D-011`. Três deles ainda dependem de decisão do usuário (`G-003`,
`G-012`, `G-013`).

**A ordem de risco**, para quem for escolher por onde começar: a `T004`/`T005` é a única que pode
quebrar o que já funciona; a `T019`/`T020` é a que erra silenciosamente, produzindo número correto e
institucionalmente falso; e a `T042` é a que **não falha** quando esquecida.

**As duas tarefas que a análise cruzada de 21/09 acrescentou** são `T015` e `T016`, e valem a nota:
a primeira fechava o único cenário da §18 sem tarefa; a segunda é a **única** verificação
automatizada de que a visão e a tela dona dizem o mesmo número. Antes delas, `FR-582` — a fonte
única, que é a tese arquitetural desta feature — dependia inteiramente do percurso manual.
