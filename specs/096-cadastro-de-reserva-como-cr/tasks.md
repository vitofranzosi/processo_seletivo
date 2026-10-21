# Tasks: Cadastro de reserva sem vaga imediata impresso como CR

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/celula-de-vagas-e-nota.md](contracts/celula-de-vagas-e-nota.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos. Cada `FR-`, `SC-` e caso-limite da spec tem teste, e o teste vem **antes** do
código: cada fase de testes roda e falha contra o código anterior antes da implementação dela
(Constituição, Princípio V).

**Caminhos**: relativos à raiz do repositório; `backend/` é o projeto Django.

**Testes que mudam de propósito**: os guardiões de bytes do cenário B e o teste da `FR-136` no
portal. Cada um é atualizado **na tarefa que muda o comportamento**, com a razão no commit, e nunca
para "fazer passar".

**Bancos**: `DB_NAME=ps096` para a suíte (`TEST_DB_ENGINE=postgresql DB_USER=$(whoami)
DB_RUNTIME_USER=$(whoami)`); `ps_096_b` para a validação pelo fluxo real, novo e com dados fictícios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: a história da spec (US1 a US5)

---

## Phase 1: Setup

- [X] T001 Medir o ponto de partida: `uv run pytest -q` contra PostgreSQL (variáveis acima) sobre `tests/unit/editais tests/unit/publicacoes tests/contract tests/integration/publicacoes tests/integration/portal`; verde, e o total registrado num `specs/096-cadastro-de-reserva-como-cr/verificacao.md` novo, seção "Ponto de partida"
- [X] T002 [P] Conferir as premissas do `SC-901` e registrá-las em `verificacao.md`: o snapshot congelado do cenário A (`doc/auditoria-edital-pdf-2026-10-08/snapshots/A-conteudo-publicado.json`) e a fixture de contrato (`backend/tests/contract/fixtures/snapshot_publicado.json`) não têm Perfil com 0 vaga e cadastro `LIMITED`/`UNLIMITED`; o B tem 16 (medido em 21/10: A 0 de 4, B 16 de 18, contrato 0 de 1). Se alguma contagem divergir, parar e rever o `SC-901` com o usuário

---

## Phase 2: Foundational — o predicado, a célula e a nota

Bloqueia todas as histórias do documento (US1, US2, US3, US5). A US4, do portal, não depende desta fase.

### Testes (primeiro; falham por `ImportError`/`AttributeError`/`TypeError`)

- [X] T003 [P] Em `backend/tests/unit/editais/test_cadastro_sem_vaga_imediata.py` (novo), `quadro.cadastro_sem_vaga_imediata` pela tabela-verdade de [data-model.md](data-model.md) (`FR-2402`, `D-005`): verdadeiro com total 0 sem quadro e `LIMITED`; com total 0, quadro todo em 0 e `UNLIMITED`; falso com total 0 e uma linha positiva (o caso-limite incoerente); com total 0 e `NONE`, `reserveType` ausente ou desconhecido; com total 3 e `LIMITED`; com `immediateVacancies` `False`, `True`, `"0"` ou ausente; com `perfil` que não é `dict`
- [X] T004 [P] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_como_cr.py` (novo), as peças do compositor ([contracts/celula-de-vagas-e-nota.md](contracts/celula-de-vagas-e-nota.md) §1 e §2): `pdf.vagas_impressas` devolve `"CR"` para o Perfil do predicado, `"0"` para 0 com `NONE`, `"0"` para o incoerente e `"7"` para 7 com cadastro (`FR-2408`); `pdf.nota_da_sigla(perfis)` devolve `"CR: cadastro de reserva."` quando algum Perfil é `CR`, e `None` quando nenhum é; `pdf.SIGLA_DO_CADASTRO == "CR"` e `pdf.NOTA_DO_CADASTRO == "CR: cadastro de reserva."`
- [X] T005 [P] No mesmo arquivo, `_tabela(..., nota=...)`: compor um documento com uma tabela com nota e conferir, pelo `texto_de` de `tests/unit/publicacoes/test_pdf.py`, que a nota sai **depois** da última linha da grade, em `CORPO_TABELA`; que `nota=None` dá os mesmos itens de antes; e que a nota não marca `junto` (`D-007`, corrigido na implementação: o paginador não leva a grade com a linha seguinte)
- [X] T006 Rodar T003 a T005: falham pelas razões esperadas, e nenhum por outra

### Implementação

- [X] T007 [P] Em `backend/processo_seletivo/editais/domain/quadro.py`, `cadastro_sem_vaga_imediata(perfil)` ao lado de `sem_vaga_imediata`, com docstring que diga por que não é o mesmo predicado (o acervo sem quadro, `D-005`) e por que recusa `bool`
- [X] T008 Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `SIGLA_DO_CADASTRO`, `NOTA_DO_CADASTRO`, `vagas_impressas(perfil)` e `nota_da_sigla(perfis)`, perto de `_reserva` e `frase_do_cadastro`; e `_tabela` ganha `nota=None`, escrita depois da grade com `tamanho=CORPO_TABELA`, `recuo=recuo`, `antes=ANTES_DE_LINHA`, com comentário do porquê do corpo (`CORPO_NOTA` é o do rodapé técnico) e de a nota não ir `junto` (`D-007`)
- [X] T009 Rodar T003 a T005: verdes; rodar `tests/contract/test_documento_publicado.py` e os guardiões de bytes: verdes, porque nada chama a nota ainda

**Checkpoint**: as peças existem; o documento ainda não muda.

---

## Phase 3: User Story 1 — A tabela de Perfis (P1) 🎯 MVP

**Goal**: na apresentação plana com dois ou mais Perfis, a coluna "Vagas" diz `CR` nos Perfis de
cadastro de reserva sem vaga, com a nota abaixo da tabela e o total pela soma das vagas.

**Independent Test**: compor o cenário B na apresentação plana e contar `CR`, `0` e a nota na tabela
"Perfis de vaga".

### Testes

- [X] T010 [P] [US1] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_como_cr.py`, a tabela de Perfis composta de snapshots mínimos, nas redações 1 e 2 (os seis cenários de aceitação da US1): `LIMITED` → `CR`; `UNLIMITED` → `CR`; a nota logo abaixo da tabela com `CR` (`FR-2403`, `FR-2406`); com Perfis `CR` e com vaga, a linha de total soma só as vagas e sai (`FR-2407`); com todos `CR`, sem linha de total; sem nenhum `CR`, a tabela sai sem nota e com os mesmos bytes de antes (`FR-2409`)
- [X] T011 [P] [US1] No mesmo arquivo, os casos-limite da tabela: o Perfil com 0 e `NONE` sai `0` ao lado de Perfis `CR`, e a nota sai pelos outros; o incoerente sai `0`; o Perfil com 0 e cadastro limitado em 0 sai `CR`; a numeração das "Tabela N" e `pdf.tabelas_do_documento(snapshot)` são as mesmas com e sem `CR` (`FR-2410`, `D-008`)
- [X] T012 [US1] Rodar T010 e T011: falham porque a célula ainda diz `0` e a nota não sai

### Implementação

- [X] T013 [US1] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `_quadro_de_perfis` passa a usar `vagas_impressas(perfil)` na coluna de vagas e `nota=nota_da_sigla(perfis)` em `_tabela`; o comentário da linha de total ganha uma frase: o `CR` vale zero na soma (`FR-2407`). Rodar T010 e T011: verdes

**Checkpoint**: a tabela de Perfis da apresentação plana diz `CR`. Os guardiões de bytes do B
**falham** a partir daqui, de propósito, até a Phase 8.

---

## Phase 4: User Story 2 — O Edital de um Perfil só (P1)

**Goal**: na ficha do Perfil único, o par "Vagas imediatas" diz `CR`, com a nota depois dos pares.

**Independent Test**: compor um Edital de um Perfil só, com 0 vaga e cadastro de reserva, e ler a
ficha.

### Testes

- [X] T014 [P] [US2] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_como_cr.py`, o Edital de um Perfil só nas duas redações da apresentação plana: com 0 vaga e cadastro, `Vagas imediatas: CR` e a nota logo depois do último par (`FR-2404`, `FR-2406`); com 3 vagas, `Vagas imediatas: 3` e sem nota; com 0 e `NONE`, `Vagas imediatas: 0` e sem nota
- [X] T015 [US2] Rodar T014: falha

### Implementação

- [X] T016 [US2] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `_perfil_unico` usa `vagas_impressas(perfil)` no par e escreve `nota_da_sigla([perfil])`, quando houver, logo depois de `_pares`, dentro do mesmo `composicao.bloco()`, com os mesmos parâmetros da nota de `_tabela`, depois de `prender_a_ultima_linha` (o último par é texto, e pode levá-la). Rodar T014: verde; rodar `tests/contract/test_documento_publicado.py`: verde **sem** tocar a fixture (`SC-901`)

---

## Phase 5: User Story 3 — A apresentação por perguntas (P2)

**Goal**: na apresentação por perguntas, as tabelas de Perfis avulsos e de grupo dizem `CR`, com a
nota em cada tabela que tiver `CR`; a tabela por lista e o resumo não mudam.

**Independent Test**: compor o cenário B por perguntas e contar `CR`, `0` e as notas de cada tabela.

### Testes

- [X] T017 [P] [US3] Em `backend/tests/unit/publicacoes/test_cadastro_de_reserva_como_cr.py`, por `tests.unit.publicacoes.cenarios_da_auditoria.por_perguntas("B")`: nenhuma tabela de Perfis traz `0` para Perfil com cadastro; 16 células `CR`; uma nota por tabela com `CR`, e nenhuma nas outras (`FR-2405`, `FR-2406`); a tabela por lista de concorrência continua só com TD-ADM e TD-INFO-EDU; a linha "Vagas" do resumo continua com o texto de hoje (os três cenários de aceitação da US3)
- [X] T018 [P] [US3] No mesmo arquivo, um snapshot mínimo por perguntas com um Perfil só, `CR`: "Não há vagas imediatas.", a tabela "Perfis" com `CR` e a nota
- [X] T019 [US3] Rodar T017 e T018: falham

### Implementação

- [X] T020 [US3] Em `backend/processo_seletivo/publicacoes/infrastructure/apresentacao.py`, `_vagas_em_partes` usa `composicao_pdf.vagas_impressas(perfil)` na coluna de vagas imediatas das tabelas de avulsos e de grupo, e passa `nota=composicao_pdf.nota_da_sigla(...)` com os Perfis de cada tabela; `_total`, `com_vaga` e a escolha entre `_matriz_de_vagas` e `_vagas_em_partes` ficam como estão (`D-006`). Rodar T017 e T018: verdes

---

## Phase 5b: User Story 6 — A prévia reserva o fecho (P1)

*Acrescentada na implementação, por decisão do usuário em 21/10/2026 (D-012).* A nota empurrou o
cenário B uma linha, e o guardião da `008` (`test_documento_publicado.py`, `consolidado-B`) reprovou:
a última seção saltava com o fecho só no publicado.

**Goal**: a prévia pagina o corpo normativo como o publicado, reservando o espaço real do fecho.

**Independent Test**: o B em prévia e em publicado, três composições por três autoridades, página a
página.

- [X] T040 [US6] Em `backend/tests/unit/publicacoes/test_previa_reserva_o_fecho.py` (novo), a regressão do B (`SC-904`, `FR-2418`): corpo normativo página a página e sumário iguais em B plano, por perguntas e variante, com as autoridades "só o cargo", "nome, cargo e ato" e a do contrato; e a prova de que, sem a reserva, o B plano com a autoridade do contrato diverge
- [X] T041 [US6] No mesmo arquivo, a reserva (`FR-2419` a `FR-2421`): a mesma geometria do fecho real em A e B; nenhuma linha vazia onde o fecho tem texto; a mais alta entre várias, em qualquer ordem; sem prevista, o fecho sem nome nem cargo; a prévia sem nome, ato, "Autoridade responsável", "SHA-256" nem o resumo de medida, e com o aviso; o publicado recusa `fechos_previstos`
- [X] T042 [US6] Em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, `render_edital_pdf(fechos_previstos=())`, recusado no publicado; `DATA_DE_MEDIDA`, `RESUMO_DE_MEDIDA`, `FECHO_NA_PUBLICACAO`, `_fecho_medido` e `_reservar_o_fecho` (`D-013`); a prévia passa `fecho_reservado` a `com_o_fecho` no lugar de `None`
- [X] T043 [US6] Em `backend/processo_seletivo/publicacoes/application/contexto_do_ato.py`, `fechos_previstos(unidade, data)`, pelas autoridades vigentes; `backend/processo_seletivo/interface/views.py::previa_documento` as passa com a data de hoje no fuso institucional
- [X] T044 [US6] Em `backend/tests/contract/test_documento_publicado.py`, o `documento` da prévia passa a autoridade da fixture como prevista, e `corpo_normativo` reconhece `Fecho do ato: ` como começo do fecho; os testes continuam exigindo a mesma paginação (o `consolidado-B` volta ao verde sem afrouxar nada)
- [X] T046 [US6] Em `backend/tests/unidades/test_previa_mede_o_fecho.py` (novo), as previstas são as vigentes na data (nem a encerrada nem a futura), e a tela da prévia mede por elas sem imprimir nome, cargo nem ato (`FR-2420`, `FR-2421`)
- [X] T045 [US6] Registrar a decisão: a User Story 6, `FR-2418` a `FR-2421`, `SC-904`, o caso-limite das várias autoridades e a D-012 na spec; `D-013` na research; o plano, o contrato §6 e esta fase

---

## Phase 6: User Story 4 — O portal (P2)

**Goal**: o bloco do Perfil de cadastro de reserva sem vaga diz a oferta por extenso, sem o número e
sem a sigla.

**Independent Test**: abrir a página da seleção com um Perfil `CR` e um com vaga, e ler os dois
blocos.

Independente das Phases 2 a 5: toca só o portal.

### Testes

- [X] T021 [US4] Em `backend/tests/integration/portal/test_detalhe_selecao.py`, o teste da `FR-136` (o que hoje afirma `"0 vagas imediatas agora" in segunda_vaga`) muda de propósito: continua afirmando `reserva-primeiro`, `<strong>Cadastro reserva</strong>`, a ausência de `<strong>0</strong>` e o convite; passa a afirmar que `"0 vaga"` e `"CR"` não aparecem no bloco; a docstring cita `FR-2414`, `FR-2415` e a decisão D-004 desta feature, e diz que o trecho da `FR-136` que afirmava o zero foi revisto (`D-010`)
- [X] T022 [P] [US4] No mesmo arquivo, um teste novo: no mesmo Edital, o bloco do Perfil com vaga continua com o número em destaque e a reserva como hoje (`FR-2416`); e nenhum bloco da página contém `CR` (`FR-2415`)
- [X] T023 [US4] Rodar T021 e T022: T021 falha pelo `0 vaga`; T022 passa (prende o que não pode mudar)

### Implementação

- [X] T024 [US4] Em `backend/processo_seletivo/portal/templates/portal/selecao.html`, no ramo `{% if perfil.oferta %}`, sai o `<span class="reserva">` com "vagas imediatas agora"; o `{% comment %}` do bloco ganha uma frase: desde a `096` o zero não é dito, e por quê (`FR-2414`). A folha `backend/processo_seletivo/portal/static/portal/portal.css` não muda: `.vagas-numero .reserva` continua usada pelo ramo com vaga (conferido em 21/10). Rodar T021, T022 e `tests/portal`: verdes

---

## Phase 7: User Story 5 — A Retificação (P3)

**Goal**: o consolidado aplica a regra ao estado vigente; a tela de homologação guarda os números.

**Independent Test**: retificar as vagas imediatas de um Perfil de cadastro de reserva e ler o
consolidado e a tela de homologação.

### Testes

- [X] T025 [P] [US5] Em `backend/tests/integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py` (novo), pelo caminho da publicação: um Edital com P2 só de cadastro (0, `LIMITED`) e P3 com vaga e cadastro; o original já sai com P2 em `CR` e a nota; a Retificação de P2 de 0 para 2 dá `2` e tira a nota (`FR-2411`); a de P3 de 1 para 0 dá `CR` e a nota; nos dois, a tela de homologação (`_alteracoes_legiveis`) diz o antes e o depois com os números (`FR-2412`, `D-003`). *Feito com uma correção:* sem lista reservada, o total e a linha geral derivada mudam no mesmo ato (027), e a Retificação leva os dois
- [X] T026 [P] [US5] No mesmo arquivo, o documento já publicado: os bytes e o resumo do documento da publicação original são os mesmos depois da Retificação, e continuam dizendo `CR` (`FR-2413`)
- [X] T027 [US5] Rodar T025 e T026: verdes se as Phases 3 e 4 já entraram (o consolidado usa o compositor). Se T025 falhar, a causa é um caminho do consolidado que não passa por `_quadro_de_perfis`, e ele precisa entrar na Phase 3

---

## Phase 8: Os bytes do cenário B

Depende das Phases 3, 4 e 5: o documento final precisa existir.

- [ ] T028 Em `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_096.py` (novo), o guardião de diferença (`D-009`, `SC-900`): para `B-plana`, `B-publicado` e `B-variante`, o texto corrido do PDF da `069` (`specs/069-edital-linguagem-simples/demonstracao/`), transformado **só** por (a) cada célula de vagas `0` de um dos 16 Perfis de tutor presencial trocada por `CR` e (b) uma nota `CR: cadastro de reserva.` depois de cada tabela com `CR`, é igual ao texto do composto agora; neutralizar só o rodapé de página e o cabeçalho repetido, como `test_documento_da_auditoria_depois_da_067.py`; e o texto de `A-plana` e `A-publicado` é idêntico ao da `069`. Docstring: por que os PDFs da `069` não são regravados
- [ ] T029 Gravar `specs/096-cadastro-de-reserva-como-cr/demonstracao/B-plana-096.pdf`, `B-publicado-096.pdf` e `B-variante-096.pdf` pelas mesmas chamadas dos guardiões (`congelado`, unidade, autoridade e data fixas; `por_perguntas` e `variante_de_b` de `cenarios_da_auditoria.py`)
- [ ] T030 Em `backend/tests/unit/publicacoes/test_itens_do_documento.py`, o guardião de bytes passa a esperar o B de `specs/096-…/demonstracao/` e continua esperando o A de `specs/069-…/demonstracao/` (o A não muda: `SC-901`); o comentário da sequência 067 → 068 → 069 ganha o parágrafo da `096`
- [ ] T031 Em `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py`, `test_o_documento_sai_com_os_bytes_gravados` passa a ler o B da `096` e o A da `069`; os demais testes do arquivo, que comparam os PDFs gravados entre si, ficam como estão
- [ ] T032 Rodar `tests/unit/publicacoes` inteiro: verde. *Já atualizados de propósito na Phase 3 e na 5:* `test_equivalencia_da_consolidacao.py` (a nota não é frase de Perfil) e `test_perfil_sem_vaga_imediata.py` (a nota não é regra de reserva no cadastro, decisão 003 da `067`). Se `test_equivalencia_da_consolidacao.py`, `test_consolidacao_por_perfil.py` ou `test_perfil_sem_vaga_imediata.py` reprovarem, ler a asserção: se prende o `0` de um Perfil `CR`, atualizar de propósito, com a razão no commit; se prende outra coisa, a implementação está errada

---

## Phase 9: Polish, fluxo real e verificação

- [ ] T033 O cenário B pelo fluxo real ([quickstart.md](quickstart.md) §2), num banco novo `ps_096_b` (`make preparar DB_NAME=ps_096_b`): publicar pelo roteiro `cenario_b_corrigido.py` da auditoria; `pdftotext -layout` do PDF publicado; contar 16 `CR`, 0 `0` em tutor presencial, a soma no total e as notas (`SC-900`); registrar em `verificacao.md`
- [ ] T034 Páginas do B por CoreGraphics (não `pdftoppm`, que perde o negrito): a tabela de Perfis com a nota, na plana e por perguntas; gravar as escolhidas em `specs/096-cadastro-de-reserva-como-cr/demonstracao/`
- [ ] T035 Portal e gestão pelo navegador, com o banco de T033 ([quickstart.md](quickstart.md) §3 e §4): o bloco de um tutor presencial sem `0 vaga` e sem `CR`; o de um tutor a distância com o número; a etapa Perfis e a Revisão com `0`; a prévia com `CR` (`FR-2417`); capturas a 1280 e 375 px em `demonstracao/`
- [ ] T036 [P] `specs/096-cadastro-de-reserva-como-cr/rastreabilidade.md`: cada `FR-`, `SC-`, decisão e caso-limite com o teste que o prende (modelo da `067`); o caso-limite do assistente e o do limite 0 como fora do escopo, apontando para o registro
- [ ] T037 [P] Registrar os dois achados que a spec deixou fora, sem corrigi-los: o cadastro limitado em 0, que o domínio aceita, e o assistente, que lê o `0` do conteúdo publicado. Uma nota curta em `doc/achados-editais-externos.md`, abaixo do P-2, dizendo também que o `CR` da amostra foi atendido pela `096`
- [ ] T038 [P] `README.md`: a linha da `096` na tabela de incrementos passa de "Especificada" ao estado real; `verificacao.md` completo, e o status da spec para "Implementada"
- [ ] T039 (`SC-903`) `cd backend && make lint check` e a suíte completa contra PostgreSQL com `DB_NAME=ps096`; registrar o total e os pulados em `verificacao.md`; se os números de `AGENTS.md` mudarem, atualizá-los

---

## Dependencies & Execution Order

- **Setup (1)** → **Foundational (2)** → US1, US2, US3, US5.
- **US1 (3)** depende só da Phase 2; é o MVP.
- **US2 (4)** e **US3 (5)** dependem da Phase 2, e não de US1; tocam funções diferentes.
- **US4 (6)** não depende de nada: só o portal. Pode ir a qualquer momento depois do Setup.
- **US5 (7)** depende de US1 e US2: o consolidado passa pelo mesmo compositor.
- **Bytes (8)** depende de US1, US2 e US3: os PDFs esperados só se gravam depois do documento final.
- **Polish (9)** depende de tudo.

US1, US2 e US3 tocam `pdf.py` e `apresentacao.py` em funções diferentes. Feitas em sequência, cada
commit tem um documento coerente. Os guardiões de bytes do B ficam vermelhos entre a Phase 3 e a
Phase 8, de propósito, e nenhum commit intermediário vai para o CI sem a Phase 8.

## Parallel Example

```text
# Fase 2: T003, T004 e T005 juntos; depois T007 em paralelo com T008.
# US1: T010 e T011 juntos.
# US4 inteira em paralelo com US1–US3 (arquivos do portal só).
# US5: T025 e T026 juntos.
# Polish: T036, T037 e T038 juntos.
```

## Implementation Strategy

1. **MVP**: Setup, Foundational e US1. A tabela de Perfis é o que o candidato lê primeiro, e o caso
   que a equipe publica.
2. US2 e US3 completam o documento nas outras composições; US4 tira o zero do portal.
3. US5 confirma a Retificação sobre o compositor final.
4. A Phase 8 fecha os bytes, e a Phase 9 leva o cenário pelo fluxo real e pela interface.

**Um PR só.** A feature é pequena, e os guardiões do B só voltam ao verde na Phase 8. Dividir em dois
PRs deixaria o primeiro vermelho no CI.
