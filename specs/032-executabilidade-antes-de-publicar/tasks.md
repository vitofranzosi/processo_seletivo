---

description: "Task list for 032 — Executabilidade antes de publicar"
---

# Tasks: Executabilidade antes de publicar

**Input**: Design documents from `specs/032-executabilidade-antes-de-publicar/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: obrigatórios. Não é opção neste repositório — o Princípio V manda que todo requisito seja
rastreável a teste, e `tests/test_citacoes_de_requisito.py` reprova `FR-` que nenhuma spec define.
Em cada história os testes vêm **antes** da implementação e devem falhar primeiro.

**Organization**: por história, na ordem de risco crescente que o plano propõe.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo — arquivo diferente, sem dependência pendente
- **[Story]**: US1, US2, US3, conforme `spec.md`
- Caminhos relativos a `backend/`

---

## ⚠️ Duas armadilhas que já custaram caro neste repositório

**Arquivo de teste da tarefa pode já existir.** Na `030`, `tests/interface/test_round_trip_do_rascunho.py`
foi **sobrescrito** em vez de estendido, e oito regressões sumiram sem que a suíte ficasse vermelha —
o arquivo existia desde a `014`. Toda tarefa abaixo diz se o arquivo é **novo** ou **existente**;
onde diz existente, **acrescente ao fim e não reescreva o topo**.

**Recusar na gravação do rascunho derruba a suíte inteira.** A `030` tentou e caiu 759 testes, porque
tornava ilegal todo payload que o repositório já produz. O recorte por `ato` não é polimento final:
é a primeira linha de cada regra impeditiva.

---

## Phase 1: Setup

**Purpose**: ambiente da worktree e a medida do "antes", sem a qual `SC-161` não é verificável

- [X] T001 Rodar `uv sync --extra dev` em `backend/` e preparar um banco próprio desta worktree com `make preparar DB_NAME=<próprio> POSTGRES_DB=<o mesmo>`, conferindo que a saída termina em `N de M` com `N` diferente de zero
- [X] T002 Registrar a contagem de partida da suíte — `make test-pg` — no rascunho de `specs/032-executabilidade-antes-de-publicar/rastreabilidade.md`, para que o delta final seja legível
- [X] T003 [P] Semear o acervo com `make seed` e gravar o conteúdo canônico e o resumo criptográfico de **cada** versão publicada em `/tmp/032-acervo-antes.json`, fora do repositório — é o "antes" que o cenário 4 do quickstart compara, e sem ele `SC-161` não é verificável

**Checkpoint**: ambiente de pé, e a medida do acervo capturada antes de qualquer mudança

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: as três invariantes que valem para **todas** as histórias — não alcançar o rascunho, não
alcançar a Retificação do acervo, não mexer no já publicado. Elas precisam existir como rede
**antes** da primeira regra nova, senão a primeira regra as quebra em silêncio.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase

- [X] T004 Acrescentar ao **arquivo existente** `tests/interface/test_round_trip_do_rascunho.py` o caso que prende `FR-459`: rascunho com Perfil sem marco, marco sem corte e marco de sorteio sem método continua sendo **gravado** sem recusa — acrescente ao fim, com constantes próprias, e não reescreva os 11 casos que já estão lá
- [X] T005 [P] Criar o **arquivo novo** `tests/integration/editais/test_acervo_inexecutavel_continua_retificavel.py` prendendo `FR-460`: Retificação de Edital do acervo sem marco, sem método de sorteio e com reserva em marco computado continua sendo aceita — espelhe a forma de `test_acervo_sem_quadro_continua_retificavel.py`, que já existe ao lado
- [X] T006 [P] Acrescentar ao **arquivo existente** `tests/integration/publicacoes/test_elevacao_de_versao.py` o caso que prende `FR-469` e `SC-161`: nenhum degrau novo, e conteúdo e resumo de toda versão do acervo idênticos

**Checkpoint**: as três redes de proteção existem e passam sobre o código de hoje

---

## Phase 3: User Story 1 — A Revisão recusa o Edital que não vai funcionar (Priority: P1) 🎯 MVP

**Goal**: `FR-457` a `FR-463`. O Edital que não classifica ninguém para de ser publicável, e quem
deixa o corte em branco lê a consequência real na etapa em que decide.

**Independent Test**: reencenar o Edital 03/2026 da auditoria — um Perfil, nenhum marco — e conferir
que a Revisão recusa nomeando o Perfil e levando à etapa Classificação; e montar um marco sem corte,
conferindo o aviso na Revisão e a frase na composição.

### Tests for User Story 1

- [X] T007 [P] [US1] Criar o **arquivo novo** `tests/unit/editais/test_executabilidade.py` com o caso de `FR-457`: snapshot cujo Perfil traz `classificationMilestones` vazio produz `profile_without_milestone` como `BLOCKING_ERROR`, com `path` terminando em `/classificationMilestones`
- [X] T008 [P] [US1] Acrescentar ao mesmo `tests/unit/editais/test_executabilidade.py` os dois casos de `FR-461`: marco **sem** `cutRule` produz `milestone_without_cut_rule` como `WARNING`; e — a contraprova que importa — marco cuja `cutRule` declara **não governar Etapa alguma** (`FR-224` da `014`, o caso do Edital 69/2026) **não** produz achado nenhum
- [X] T009 [P] [US1] Acrescentar ao mesmo arquivo o caso de `FR-459`: com `ato=ATO_DE_RETIFICACAO`, nenhum dos dois achados é emitido
- [X] T010 [P] [US1] Acrescentar ao **arquivo existente** `tests/interface/test_hardening_pos_auditoria.py` o caso de `FR-458` para os **dois** achados que US1 cria: um Edital com Perfil sem marco **e** com marco sem regra de corte mostra as **duas** pendências na Revisão — não a primeira —, cada uma com caminho de volta para a etapa `classificacao`, e não para `perfis`. Isso também prende o Edge Case "mais de um achado no mesmo Edital"
- [X] T011 [P] [US1] Acrescentar ao **arquivo existente** `tests/interface/test_metodo_do_marco.py` o caso de `FR-462`: o cartão do marco com o corte em branco declara que sem corte não há convocação — e não apenas que a Etapa seguinte recebe todos os habilitados
- [X] T012 [P] [US1] Acrescentar ao **arquivo existente** `tests/interface/test_ocupacao.py` o caso de `FR-463`: com marco sem `cutRule`, a tela não renderiza o botão "Pedir a faixa seguinte com este déficit" e traz, no lugar dele, a razão

### Implementation for User Story 1

- [X] T013 [US1] Implementar `_perfil_sem_marco(snapshot, *, ato)` em `processo_seletivo/editais/domain/validation.py`, com `if ato != ATO_DE_PUBLICACAO: return []` na primeira linha, seguindo `_forma_da_ordem_declarada` como modelo
- [X] T014 [US1] Implementar `_marco_sem_regra_de_corte(snapshot, *, ato)` em `processo_seletivo/editais/domain/validation.py`, distinguindo ausência de `cutRule` de `cutRule` que declara não governar Etapa alguma, e registrando no docstring por que a distinção existe
- [X] T015 [US1] Ligar as duas em `validate_for_publication`, em `processo_seletivo/editais/domain/validation.py`, ao lado de `_coerencia_dos_marcos`
- [X] T016 [US1] Acrescentar `faixaDisponivel` à leitura de cada recorte em `processo_seletivo/ocupacao/application/selectors.py`, sem tocar em `estado` — campo aditivo, conforme `data-model.md`
- [X] T017 [US1] Condicionar o bloco "Pedir a faixa seguinte com este déficit" em `processo_seletivo/interface/templates/interface/ocupacao.html` e escrever a razão no lugar do botão — não `disabled`, não alerta depois do clique
- [X] T018 [US1] Reescrever a consequência da ausência de corte em `processo_seletivo/interface/templates/interface/_marco.html`, nomeando a convocação; a explicação longa vai para o `como-preencher` da etapa, e não para dentro do cartão

**Checkpoint**: US1 funciona sozinha. O Edital 03/2026 não passa mais, e o corte em branco avisa.

---

## Phase 4: User Story 2 — O documento publicado carrega o método do sorteio (Priority: P2)

**Goal**: `FR-464` a `FR-469`. O documento diz como a ordem nasce e publica o método inteiro do
sorteio; o marco que sorteia para de imprimir combinação de pontuações; e quem sorteia sem método
não publica.

**Independent Test**: publicar um Edital de sorteio e ler o documento gerado — as três grafias de
`Método:` e os sete campos, conferíveis por terceiro sem acesso ao sistema.

### Tests for User Story 2

- [X] T019 [P] [US2] Acrescentar ao **arquivo existente** `tests/unit/publicacoes/test_pdf_classificacao.py` os casos de `FR-464` e `FR-465`: a seção do marco imprime `Ordem` e os sete campos do método, com os rótulos de `CAMPOS_DO_METODO`
- [X] T020 [P] [US2] Acrescentar ao mesmo arquivo os três casos de `FR-466`: `Método: comum a este Edital`, `próprio deste marco — diverge do comum deste Edital` e `próprio deste marco`, conforme `contracts/marco-no-documento.md`
- [X] T021 [P] [US2] Acrescentar ao mesmo arquivo os dois casos de `FR-468` e do acervo: marco que sorteia **não** imprime `Combinação` nem `Normalização`; marco do acervo sem `orderProduction` sai **exatamente** como hoje, sem o par `Ordem`
- [X] T022 [P] [US2] Acrescentar a `tests/unit/editais/test_executabilidade.py` o caso de `FR-467`: marco que ordena por sorteio sem método próprio e sem método comum produz `drawn_milestone_without_method` como `BLOCKING_ERROR`; o caso que o separa de `draw_method_invalid` — método pela metade continua sendo o achado antigo; e o caso de `FR-459` para este achado — com `ato=ATO_DE_RETIFICACAO` ele **não** é emitido, porque `orderProduction` ausente é o estado legítimo de todo marco do acervo
- [X] T023 [P] [US2] Criar o **arquivo novo** `tests/integration/publicacoes/test_sorteio_no_documento.py` prendendo `SC-158`: publicar um Edital de sorteio pelo caminho de publicação e extrair do documento a ocorrência que fixará a semente e a regra de substituição

### Implementation for User Story 2

- [X] T024 [US2] Implementar `_metodo_do_marco(snapshot, perfil, marco)` em `processo_seletivo/publicacoes/infrastructure/pdf.py`, resolvendo por `marcos.metodo_que_governa` e rotulando por `CAMPOS_DO_METODO` — uma leitura só, nunca uma segunda resolução local
- [X] T025 [US2] Acrescentar o par `Ordem` à seção do marco em `processo_seletivo/publicacoes/infrastructure/pdf.py::_marcos`, omitindo-o quando o marco do acervo não declara `orderProduction`
- [X] T026 [US2] Acrescentar o bloco `Sorteio` e a linha `Método:` em `processo_seletivo/publicacoes/infrastructure/pdf.py::_marcos`, na ordem que `contracts/marco-no-documento.md` fixa
- [X] T027 [US2] Condicionar `Combinação` e `Normalização` a `marcos.marco_ordena_por_sorteio` em `processo_seletivo/publicacoes/infrastructure/pdf.py::_marcos`
- [X] T028 [US2] Implementar `_metodo_do_sorteio_publicavel(snapshot, *, ato)` em `processo_seletivo/editais/domain/validation.py` e ligá-la em `validate_for_publication`, com o mesmo recorte por ato

**Checkpoint**: US1 e US2 funcionam, cada uma por si. O Edital 04/2026 publica a norma que faltava.

---

## Phase 5: User Story 3 — A reserva sem via de apuração deixa de ser silenciosa (Priority: P3)

**Goal**: `FR-470` a `FR-472`. O aviso nomeia a causa antes da publicação, e as ações que sempre
falham somem da ocupação.

**Independent Test**: montar o quadro 7/1/2 da auditoria num marco que ordena por pontuação, ver o
aviso na Revisão sem impedimento, publicar, e conferir que a ocupação não oferece apurar os recortes
reservados.

### Tests for User Story 3

- [X] T029 [P] [US3] Acrescentar a `tests/unit/editais/test_executabilidade.py` três casos: `FR-470` — linha de quadro com `modalityId` não nulo e quantidade maior que zero, em Perfil cujo marco não sorteia, produz `reserved_row_without_ordering` como `WARNING` e **não** como impedimento; `FR-471` — a **mensagem** nomeia a causa, citando que a ordem daquele marco é emitida em lista única, e não repete o sintoma *"Este recorte não tem ordem emitida"* que a auditoria leu no dia da apuração; e `FR-459` — com `ato=ATO_DE_RETIFICACAO` o aviso não é emitido sobre Edital do acervo
- [X] T030 [P] [US3] Acrescentar ao mesmo arquivo as duas contraprovas: Perfil cujo marco **sorteia** não recebe achado; e a grafia-armadilha — a Modalidade declarada como ampla concorrência, apontada por `generalCompetitionModalityId`, **não** é lida como reserva, porque o recorte da ampla é o `NULL` da linha geral
- [X] T031 [P] [US3] Acrescentar ao **arquivo existente** `tests/interface/test_ocupacao.py` o caso de `FR-472`: os recortes reservados não renderizam "Apurar a ocupação deste recorte" e trazem a razão; o recorte da ampla continua renderizando e funcionando

### Implementation for User Story 3

- [X] T032 [US3] Implementar `emite_ordem_no_recorte(conteudo, *, perfil_id, marco_id, lista_id)` em `processo_seletivo/editais/domain/marcos.py` — **uma função só**, consumida pela validação e pelo selector, pela mesma razão que levou a `029` a criar `chamada_em_aberto`: dois predicados divergiriam na primeira mudança. O docstring MUST registrar as duas coisas que a escolha do módulo custa: que um fato de **emissão** passa a morar no módulo de **conteúdo normativo** — a regra real vive em `classificacao/application/emissao.py`, que fixa `lista_id=None` porque só o sorteio emite por lista —, e que pô-lo em `classificacao` inverteria a direção de dependência, porque `editais/domain/validation.py` também o consome e domínio não importa aplicação. `classificacao/application/emissao.py` já importa `editais.domain.marcos`, então a aresta não é inédita
- [X] T033 [US3] Emitir o aviso em `_coerencia_do_quadro_de_vagas`, em `processo_seletivo/editais/domain/validation.py`, ao lado de `vacancy_reserved_list_without_row` e no mesmo tom
- [X] T034 [US3] Acrescentar `apuravel` à leitura de cada recorte em `processo_seletivo/ocupacao/application/selectors.py`, consumindo `emite_ordem_no_recorte`. **É a primeira dependência de `ocupacao` sobre `editais`** — conferido em 18/09/2026: hoje o módulo importa `classificacao`, `publicacoes` e `resultados`, e nada de `editais`. A aresta é legítima na direção em que vai, e ninguém depende de `ocupacao`; registre-a no comentário do import, para que a próxima pessoa saiba que ela foi deliberada e não acidental
- [X] T035 [US3] Condicionar o botão "Apurar a ocupação deste recorte" em `processo_seletivo/interface/templates/interface/ocupacao.html` e escrever a razão no lugar dele, nomeando a causa e não o sintoma

**Checkpoint**: as três histórias funcionam. O `ACH-47` sai **nomeado**, e a spec já diz que ele não sai resolvido.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T036 Escrever `specs/032-executabilidade-antes-de-publicar/rastreabilidade.md` com uma linha por `FR-` e por `SC-`: onde foi feito e onde é verificado — é o Princípio V, e requisito sem linha aqui é requisito que ninguém sabe se entrou
- [X] T037 [P] Conferir o implementado contra `specs/032-executabilidade-antes-de-publicar/contracts/achados-de-executabilidade.md` e `contracts/marco-no-documento.md`, corrigindo **o artefato** quando o código estiver certo e o contrato errado, e dizendo qual dos dois mudou
- [X] T038 Percorrer os cenários 1 a 3 de `quickstart.md` pela interface administrativa, com o banco próprio desta worktree — sem shell e sem banco, que é o que o Princípio VI cobra
- [X] T039 Percorrer o cenário 4 de `quickstart.md`: comparar conteúdo e resumo de cada versão do acervo com o que T003 registrou
- [X] T040 Rodar `make lint check test-pg` em `backend/` e registrar em `rastreabilidade.md` a contagem final contra a de T002 — `lint` são dois passos, `ruff check` **e** `ruff format --check`
- [X] T041 Varrer as quatro regras novas contra a amostra real de `doc/avaliacao-de-capacidade-editais-2026-09-12.md`, Edital a Edital, e registrar quais disparariam — checklist, analyze e o teste de citações ficam verdes com regras que se contradizem, e só a varredura manual pega
- [X] T042 Acrescentar ao **arquivo existente** `tests/interface/test_hardening_pos_auditoria.py` o caso que fecha `SC-159`: um Edital que dispara os **quatro** achados da família mostra os quatro na Revisão, cada um com caminho de volta para a etapa certa — `classificacao` para os três do marco, `perfis` para o do quadro. Mora aqui, e não dentro de uma história, porque só existe depois das três: pô-lo em US1 criaria dependência entre histórias que deveriam ser entregáveis isoladas

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende da Phase 1 — **bloqueia as três histórias**
- **US1 (Phase 3)**, **US2 (Phase 4)**, **US3 (Phase 5)**: dependem da Phase 2; entre si, independentes
- **Polish (Phase 6)**: depende das histórias que forem entregues

### User Story Dependencies

- **US1 (P1)**: independente. É o MVP
- **US2 (P2)**: independente de US1. Toca `pdf.py` e `validation.py`, sem colidir com os arquivos de US1 exceto em `validation.py` — ver conflitos abaixo
- **US3 (P3)**: independente. Compartilha `ocupacao.html` e `selectors.py` com US1 — ver conflitos abaixo

### Conflitos reais de arquivo (por isso nem tudo é [P])

| Arquivo | Quem toca | Consequência |
|---|---|---|
| `editais/domain/validation.py` | T013, T014, T015 (US1), T028 (US2), T033 (US3) | serializar; cada um acrescenta função própria, e só `validate_for_publication` é editada por mais de um |
| `interface/templates/interface/ocupacao.html` | T017 (US1), T035 (US3) | blocos diferentes do mesmo arquivo; serializar |
| `ocupacao/application/selectors.py` | T016 (US1), T034 (US3) | dois campos aditivos na mesma leitura; serializar |
| `tests/unit/editais/test_executabilidade.py` | T007, T008, T009 (US1), T022 (US2), T029, T030 (US3) | arquivo novo, criado em T007; os demais **acrescentam** |
| `tests/unit/publicacoes/test_pdf_classificacao.py` | T019, T020, T021 (US2) | arquivo existente de 398 linhas; acrescentar ao fim |
| `tests/interface/test_ocupacao.py` | T012 (US1), T031 (US3) | arquivo existente de 427 linhas; acrescentar ao fim |
| `tests/interface/test_hardening_pos_auditoria.py` | T010 (US1), T042 (polish) | arquivo existente de 640 linhas; T042 fecha o que T010 só alcança para US1 |

### Within Each User Story

- Testes primeiro, e **falhando**, antes de qualquer implementação
- Domínio antes de aplicação; aplicação antes de interface
- A primeira linha de toda regra impeditiva é o recorte por `ato`

---

## Parallel Example: User Story 1

```bash
# Os testes de US1 tocam arquivos diferentes e podem ser escritos juntos:
Task: "T007 profile_without_milestone em tests/unit/editais/test_executabilidade.py"
Task: "T010 a Revisão leva à Classificação em tests/interface/test_hardening_pos_auditoria.py"
Task: "T011 a consequência do corte no cartão em tests/interface/test_metodo_do_marco.py"
Task: "T012 a faixa sem corte em tests/interface/test_ocupacao.py"

# T008 e T009 acrescentam ao arquivo que T007 cria: dependem dele, e não são [P] entre si.
```

---

## Implementation Strategy

### MVP First (US1)

1. Phase 1 e Phase 2 — ambiente e as três redes de proteção
2. Phase 3 — US1
3. **PARE e VALIDE**: cenário 1 do quickstart, e a contraprova do 69/2026 do cenário 3
4. US1 sozinha já fecha `ACH-49` e `ACH-46`, que é a metade do valor da feature

### Incremental Delivery

1. Setup + Foundational → rede de proteção de pé
2. US1 → `ACH-49` e `ACH-46` fechados → validar → demonstrar
3. US2 → `ACH-50` fechado, e capacidade nova para quem está fora da instituição → validar
4. US3 → `ACH-47` nomeado → validar

---

## Notes

- `[P]` = arquivos diferentes, sem dependência pendente
- Commitar a cada tarefa ou grupo lógico; **não** editar arquivo do projeto enquanto `test-pg` roda — template criado ou apagado no meio da suíte produz falha que não é do diff
- Todo arquivo marcado **existente** é para acrescentar, nunca para reescrever
- A `FR-469` não tem tarefa de implementação: ela é conferência, e T006 e T039 são a prova
