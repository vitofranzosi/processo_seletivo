# Tasks: Achar, conferir e voltar — o MVP de UX da Retificação

**Input**: `specs/123-ux-da-retificacao/` — spec.md, plan.md, research.md, data-model.md,
contracts/tela-retificar.md, quickstart.md

**Tests**: pedidos pela spec (FR-3946, FR-3949, SC-1173 a SC-1181). Cada história tem os testes
antes da implementação, e eles devem falhar antes dela.

**Caminhos**: relativos à raiz do repositório. `backend/processo_seletivo/` é o código;
`backend/tests/`, os testes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: US1 a US5, as histórias da spec

---

## Phase 1: Setup

**Purpose**: ambiente da worktree e os Editais dos testes.

- [ ] T001 Preparar a worktree: `cd backend && uv sync --extra dev --extra navegador && uv run playwright install chromium`; escolher um `DB_NAME` próprio para o `make test-pg`; registrar a linha de base com `make lint check test-pg` antes de qualquer mudança (números de passados e pulados em `specs/123-ux-da-retificacao/verificacao.md`)
- [X] T002 [P] Criar `backend/tests/fixtures/edital_da_auditoria.py` com `edital_da_auditoria` (2 Perfis — DOC-INFO com 3 vagas e quadro AC 2 + PPP 1, TEC-LAB —, 3 Eventos com o período de inscrições, 3 Etapas, 3 Documentos, 2 Anexos e as Seções do catálogo) e `edital_extenso` (4 Perfis com 2 Modalidades cada e 11 Eventos, ampliados **no rascunho** como faz `doc/auditoria-ux-retificacao-2026-11-05/renderizar-edital-extenso.py`), publicados por `tests/fixtures/publicacao.py`, e registrados como fixtures pytest em `backend/tests/conftest.py` (R-011)
- [X] T003 No mesmo arquivo, o helper `retificacao_publicada(edital, alteracoes, vigencia)` que cria, submete, homologa e publica pela API, e `retificacao_devolvida(edital, alteracoes)` que para em `EM_ELABORACAO` com `return_reason`, como as suítes da `103`; a fixture `retificacao_futura` (Retificação publicada com vigência futura) em `backend/tests/conftest.py` (R-011)

---

## Phase 2: Foundational (bloqueia M2 e M4)

**Purpose**: a conferência de conteúdo extraída e a tradução de caminho em cartão. Nada aqui muda o
que a tela mostra.

**⚠️ CRITICAL**: T004 mexe no caminho de toda criação e edição de Retificação. Termine-o e rode as
suítes de Retificação inteiras antes de T008.

- [X] T004 Em `backend/processo_seletivo/publicacoes/application/retificacoes.py`, extrair `impeditivos_do_conteudo(content, topologia, situacoes=None)` e `conferir_conteudo(edital, base_content, changes)` (devolve `content`, `recusa`, `impeditivos`), e reescrever `_apply_declared_changes` e `_assert_well_formed` sobre elas, **sem** mudar código, mensagem, status nem ordem das recusas (R-001, R-002, data-model *ConferenciaDoConteudo*)
- [X] T005 [P] Testes de `conferir_conteudo` em `backend/tests/unit/publicacoes/test_conferencia_do_conteudo.py`: mesmos impeditivos que a recusa da criação junta (quadro 3→4 e Evento sem início); a primeira guarda interrompe (critério acrescentado inválido) e deixa `impeditivos` vazio; nenhuma linha gravada em `Retificacao`, `AlteracaoNormativa` nem na trilha; espião em `validate_for_publication` com os mesmos argumentos nomeados na conferência e na criação (FR-3940, FR-3943, SC-1179)
- [X] T006 [P] Em `backend/processo_seletivo/interface/retificacao.py`, `cartao_do_caminho(grupos, caminho)` com os quatro passos de R-004 e `referencias_na_proposta(grupos, alteracoes)` (R-005), sem banco
- [X] T007 [P] Testes de T006 em `backend/tests/unit/interface/test_cartao_do_caminho.py`: exato antes dos descendentes (achado no caminho do Perfil não vai à 1ª Modalidade); descendentes antes do ancestral (`/profiles/id=…/vacancyTable` → 1ª linha do quadro); linha nova pelo mapa `novas`; prefixo em fronteira de segmento (`/profiles/id=A` não casa `/profiles/id=AB`); raiz para os campos de `CAMPOS_RAIZ`, inclusive `/drawMethod`; seção pela inversão de `COLECAO_DO_TIPO`, e nada quando a seção não está na página; `None`; em `referencias_na_proposta`: `ADD` aninhado (linha do quadro, Modalidade, critério) **não** marca o Perfil, `REPLACE` de `generalCompetitionModalityId` marca, `REMOVE` sem cartão exato volta em `remocoes_sem_cartao` (R-004, R-005)
- [ ] T008 Rodar as suítes de Retificação (`tests/interface/test_retificar*.py`, `test_jornada_da_retificacao*.py`, `test_devolucao*.py`, `test_aplicar_a_todos_na_retificacao.py`, `test_retificacao_parada.py`, `tests/integration/publicacoes/`, `tests/contract/test_retificacoes_api.py`, `tests/contract/test_retificar_requerimento.py`, `tests/interface/test_cancelamento_da_retificacao.py`, `tests/interface/test_auditoria_passagem_da_retificacao.py`, `tests/unit/interface/test_retificacao_estrutural.py`, `tests/unit/interface/test_atos_da_retificacao.py` e `tests/test_javascript.py`) com `make test-pg` e confirmar zero falha depois de T004 (FR-3946)

**Checkpoint**: a criação se comporta como antes, e existe uma conferência sem escrita.

---

## Phase 3: User Story 4 — O impeditivo antes de «Criar» (Priority: P1) 🎯 MVP

**Goal**: «Ver o que vai mudar» mostra os impeditivos da criação, com link ao cartão (M4).

**Independent Test**: por cliente HTTP, quadro 3→4 conferido mostra o impeditivo e o link à 1ª linha,
nenhuma Retificação nasce, e «Criar» recusa com as mesmas frases.

### Tests for User Story 4

- [ ] T009 [P] [US4] Em `backend/tests/interface/test_retificar_conferencia_impeditivos.py`: quadro 3→4 na conferência (seção `#impeditivos`, frase, `href="#cartao-<ref da 1ª linha>"`, `Retificacao.objects.count()` inalterado); conjunto de frases da conferência igual ao da recusa de «Criar» para os três formulários de T005; recusa de guarda sozinha; sem impeditivo, sem seção; formulário que só produz advertência (quadro parcial ao acrescentar a primeira Modalidade) não abre a seção (FR-3945); «Criar» continua oferecido e a frase de FR-3944 aparece; «Criar» recusado por conteúdo volta com a recusa no alto (texto de hoje) **e** a seção com links (R-013); impeditivo num Evento acrescentado nesta tela leva a `#cartao-novo-evento-<i>` (SC-1179, D-004, D-009)
- [ ] T010 [P] [US4] No mesmo arquivo: edição — conferência sobre o ato fundido, com uma remoção desfeita que reintroduz o impeditivo (R-003); a validação final — Resultado registrado entre conferir e criar sobre a Etapa que um corte nascido governaria (o seletor `ha_resultado_em` respondendo `False` na conferência e `True` na criação, por `mock.patch`): a criação recusa e nada é gravado; e um espião mostra que a criação chama `conferir_conteudo` de novo depois de uma conferência limpa (SC-1180, FR-3944)
- [ ] T011 [P] [US4] No mesmo arquivo: orçamento — a conferência com proposta no `edital_extenso` faz no máximo 4 consultas de conferência de conteúdo a mais que a mesma conferência com `conferir_conteudo` substituído por um que não faz nada (`django_assert_max_num_queries`, plan *Performance Goals*)

### Implementation for User Story 4

- [X] T012 [US4] Em `backend/processo_seletivo/interface/views.py`, `_compor_retificacao` recebe `proposta(todas)` (R-003): `retificar` passa `todas` sobre a projeção da base; `retificacao_editar` passa a fusão (`fundir(projecao_da_base, existentes, todas, desfeitas=desfeitas)[0]`), com o `ValueError` da fusão virando recusa
- [X] T013 [US4] Em `_compor_retificacao`, no ramo da conferência (POST sem `confirmar`, proposta não vazia, sem recusa anterior) **e** quando `gravar` recusa por conteúdo (R-013), chamar `conferir_conteudo` e montar a lista `impeditivos` de `{mensagem, destino}` com `cartao_do_caminho` e o mapa `novas` (data-model *Impeditivo na tela*); as recusas que não são de conteúdo não abrem a seção (FR-3941)
- [X] T014 [US4] Em `backend/processo_seletivo/interface/templates/interface/retificar.html`, a seção `#impeditivos` antes do resumo, como em contracts §1.2, com "Gravar a Retificação" na edição
- [X] T015 [P] [US4] Em `backend/processo_seletivo/interface/static/interface/telas/retificar.css`, as regras de `.impeditivos` e dos links dela, sem estilo inline (FR-3947)

**Checkpoint**: T009–T011 passam; a criação continua recusando como antes.

---

## Phase 4: User Story 2 — Conferir e voltar sem perder o que fez (Priority: P1)

**Goal**: dois estados de marca, a barra com duas frases, e o caminho do resumo ao campo (M2).

**Independent Test**: por HTTP, os cartões certos com `data-na-proposta` e as referências no resumo;
no JS, as frases da barra; no navegador, o cenário D.

### Tests for User Story 2

- [ ] T016 [P] [US2] Em `backend/tests/interface/test_retificar_busca_marca_base.py`: `data-na-proposta` nos cartões certos na criação (três alterações em três seções; remoção marcada; gesto de aplicar aos demais com dois destinos; linha nova de Evento; linha do quadro e Modalidade acrescentadas marcam a linha nova e **não** o Perfil, salvo pelo `REPLACE` da ampla; troca de arquivo conta um cartão); no GET e no POST da edição (devolvida com duas Alterações e a remoção de uma Modalidade → `data-proposta-cartoes="2"`, `data-proposta-remocoes="1"`, igual ao bloco «Remoções já declaradas», e o Perfil da Modalidade removida sem marca, SC-1177); `data-modo="edicao"` e `data-enviado` onde devem estar, depois de `data-conferido`; `data-proposta` em `nao-conferida`, `conferida` e `recusada` (sem marca na recusada, D-008); cada linha do resumo com `href="#c-<ref>"` ou `#cartao-<ref>`; o HTML sem caminho normativo (procurar `/profiles/` e `id=` fora de atributos de referência) — FR-3927 a FR-3934
- [X] T017 [P] [US2] Em `backend/tests/javascript/retificacao.test.js`: a tabela de frases de contracts §1.5 em cada estado de `data-proposta`, com e sem `data-proposta-remocoes`, na criação e na edição; «Só o que eu alterei» mostra cartões com `data-na-proposta` ou `data-alterado`; campo que volta ao valor da base depois da conferência fica com os dois selos; atualizar o caso de `:162` para "Nenhuma alteração nova desde a última conferência" (R-010)

### Implementation for User Story 2

- [X] T018 [US2] Em `backend/processo_seletivo/interface/retificacao.py`, `diferencas` acrescenta `cartao` e `campo` a cada item do resumo — nos ramos de nascimento, arquivo, lista de texto e remoção; nas linhas novas, com `_linhas_novas` devolvendo o índice; nas linhas da Modalidade nova e no vínculo automático do Documento ao remover Anexo, por `cartao_do_caminho` sobre o `targetPath` — e devolve o mapa `novas` (R-006, data-model *Item do resumo*)
- [X] T019 [US2] Em `backend/processo_seletivo/interface/views.py`, calcular a *Proposta* (data-model) com `referencias_na_proposta` sobre `proposta(todas)` — que já inclui as alterações dos gestos —; no GET da edição, sobre `alteracoes_declaradas(item)`; passar `cartoes_na_proposta`, `estado_da_proposta`, `remocoes_na_proposta` ao template
- [X] T020 [US2] Em `backend/processo_seletivo/interface/templates/interface/_retificacao_linha.html`, `data-na-proposta` e o selo `<span class="na-proposta">na proposta</span>` na legenda; nos seis fragmentos de linha nova (`_retificacao_perfil.html`, `_retificacao_evento.html`, `_retificacao_anexo.html`, `_retificacao_linha_do_quadro.html`, `_retificacao_modalidade.html`, `_retificacao_criterio.html`), `id="cartao-novo-<prefixo>-<indice>"` e a mesma marca quando a linha está na proposta
- [X] T021 [US2] Em `retificar.html`, os atributos `data-modo`, `data-enviado` e `data-proposta*` no formulário, **depois** de `data-conferido`, e a coluna de «Ir ao campo» / «Ir ao cartão» no resumo, com nome acessível (contracts §1.3, FR-3948)
- [X] T022 [US2] Em `backend/processo_seletivo/interface/static/interface/retificacao.js`, `recontar()` compõe as duas frases (contracts §1.5), com a `span.contagem` continuando o primeiro filho da barra e a `span.estado-da-proposta` depois dela (R-007); `aplicar()` considera `data-na-proposta`; `irAoCampo(ref)` desesconde cartão e seção, rola e foca o controle, e é usado pelos links do resumo; atualizar o comentário de cabeçalho com o porquê dos dois estados
- [X] T023 [P] [US2] Em `retificar.css`, `.na-proposta`, `[data-na-proposta]`, `.estado-da-proposta` e `.ir-ao-campo`, distintos de `[data-alterado]` e com contraste AA, sem quebra a 375 px

**Checkpoint**: T016–T017 passam; a conferência e a edição mostram o que o ato contém.

---

## Phase 5: User Story 3 — De que versão é o «antes» (Priority: P1)

**Goal**: a frase da base nas cinco telas, e "Vigente hoje" fora (M3).

**Independent Test**: por HTTP, as três situações de vigência e as cinco telas.

### Tests for User Story 3

- [ ] T024 [P] [US3] Em `backend/tests/interface/test_retificar_busca_marca_base.py`: com `retificacao_publicada` de vigência futura, as cinco telas (Retificar, detalhe, homologar, devolver, publicar) dizem "ainda não vigora: passa a vigorar em <data>" e nenhuma contém "Vigente hoje"; sem Retificação futura, "vigora desde"; edição com base sucedida, "vigorou a partir de … e já não é a versão em vigor" e a coluna «No rascunho»; a lista "Publicação original de … e as Retificações nº 2 (…) e nº 3 (…)", com a numeração do detalhe do Edital (`publication_order`, D-006); base com início exatamente no instante da tela → "vigora desde"; base rematerializada com o mesmo início futuro → "já não é a versão em vigor"; nenhuma coluna nem botão novo nas cinco telas além da frase (FR-3939); o modo somente leitura com "Conteúdo da versão-base"; `input[name=base]` com o mesmo valor que `_ultima_versao_publicada` devolvia como `_versao_vigente` (FR-3935 a FR-3939, SC-1178)
- [X] T025 [P] [US3] Atualizar `backend/tests/interface/test_acoes.py:154` para "Conteúdo da versão-base" (R-010)

### Implementation for User Story 3

- [X] T026 [US3] Em `backend/processo_seletivo/interface/views.py`, renomear `_versao_vigente` → `_ultima_versao_publicada` (só o uso de `_base_da_composicao`; não tocar o homônimo de `inscricoes/`), e passar `versao_base` às telas de Retificar, detalhe e confirmação
- [X] T027 [US3] Em `backend/processo_seletivo/interface/retificacao.py`, `descrever_versao_base(versao, agora)` (R-009, data-model *DescricaoDaVersaoBase*), com as publicações aplicadas sem revisão, `numero = publication_order` (D-006), e a situação por `effective_version(edital_id=…, at=agora)` e pela rematerialização com o mesmo `valid_from`
- [X] T028 [US3] Criar `backend/processo_seletivo/interface/templates/interface/_versao_base.html` com as frases de contracts §1.1, no fuso institucional
- [X] T029 [US3] Em `retificar.html`: o fragmento no «Como funciona» (criação e edição) e acima da tabela; os textos literais de R-010 e de contracts §1.1, §2 e §3 (criação, edição, somente leitura); colunas «Na versão-base» / «No rascunho» (D-007)
- [X] T030 [US3] Em `backend/processo_seletivo/interface/templates/interface/retificacao_detalhe.html` e `retificacao_confirmar.html`, o fragmento prefixado por "«Antes» é o conteúdo da versão-base desta Retificação." antes de cada tabela com «Antes» (contracts §4)
- [X] T031 [P] [US3] Em `retificar.css` (e na folha da tela de confirmação, se a classe do fragmento for usada fora de Retificar), a regra de `.versao-base`

**Checkpoint**: T024–T025 passam.

---

## Phase 6: User Story 1 — Achar o campo pelo nome do assunto (Priority: P1)

**Goal**: a busca por campo, com a lista e «Ir ao campo» (M1).

**Independent Test**: no JS, as regras; no navegador, «vagas», «remuneração», «prazo», «requisito».

### Tests for User Story 1

- [X] T032 [P] [US1] Em `backend/tests/javascript/retificacao.test.js`: normalização de caixa e acento; várias palavras no mesmo campo, com ao menos uma no rótulo ou valor; termo que só casa com o nome do cartão dá um resultado de cartão, e não um por campo («vagas» não lista a «Lista de concorrência»); «Ir ao cartão» foca o 1º campo; «prazo recursal» não acha «Prazo em dias» (FR-3925, D-003); 1 caractere não filtra; elegibilidade — texto longo, lista de texto, número, data, Sim/Não e arquivo fora pelo valor e dentro pelo rótulo; o valor digitado depois do carregamento é o buscado; teto de 25 e "Mostrando 25 de N resultados — refine a busca"; Enter não envia e foca o 1º resultado; `irAoCampo` desesconde e foca; campo de cartão escondido por «Só o que eu alterei» fora da lista; linha nova fora da lista e sempre visível; nenhum elemento da caixa com `name` (FR-3917 a FR-3926)
- [ ] T033 [P] [US1] Em `backend/tests/interface/test_retificar_busca_marca_base.py`: a lista esperada de SC-1174 computada da `edital_da_auditoria` pelas regras de FR-3917/FR-3918 sobre o HTML servido (legenda, rótulo, valor elegível) — e zero campos de texto longo achados pelo valor

### Implementation for User Story 1

- [X] T034 [US1] Em `retificacao.js`, `montarFiltro()` monta o índice por campo e a lista `ol.resultados-da-busca`; `aplicar()` com normalização, palavras, os dois tipos de resultado (campo e cartão), limiar 2, elegibilidade, teto 25 e a frase de contagem; Enter foca o 1º resultado; o novo `placeholder` (R-008, contracts §1.6)
- [X] T035 [P] [US1] Em `retificar.css`, `.resultados-da-busca` e filhos (`.onde`, `.rotulo`, `.valor`), quebrando linha a 375 px, sem largura fixa

**Checkpoint**: T032–T033 passam.

---

## Phase 7: User Story 5 — As Retificações de hoje continuam (Priority: P1)

**Goal**: regressão e jornada completa no navegador.

**Independent Test**: as suítes existentes verdes; a jornada de navegador inteira.

- [ ] T036 [US5] Criar `backend/tests/navegador/test_jornada_da_retificacao_123.py` com a `Tela` de `test_jornada_dos_documentos_da_convocacao.py` e os sete casos de R-012 (cenários A–C pela busca, B com impeditivo, D com marca persistente, edição da devolvida, G com base futura nas cinco telas, E no `edital_extenso` a 1280 e a 375 com rolagem lateral zero, e o percurso só pelo teclado), contando ações como o roteiro da auditoria e terminando cada caso com `violacoes == []` (FR-3949, SC-1173 a SC-1179, SC-1181)
- [ ] T037 [US5] No mesmo arquivo, o caso de regressão ponta a ponta: Retificação múltipla criada pela tela, submetida, homologada e publicada, com o conteúdo consolidado comparado ao que a mesma lista de Alterações produz pela API (US5, cenário 2)
- [ ] T038 [US5] Rodar `make lint check test-pg` completo; conferir que só os dois textos de R-010 mudaram em asserção existente e registrar os números em `specs/123-ux-da-retificacao/verificacao.md`, com a comparação de pulados por arquivo e motivo contra a linha de base de T001 (FR-3946, SC-1181)

---

## Phase 8: Polish & Cross-Cutting

- [ ] T039 [P] Varrer `retificar.html`, os fragmentos e `retificacao.js` por `style=`, `<style>`, `<script>` inline e `on*=`; conferir que toda classe nova tem regra (os guardiões de acessibilidade e de estáticos passam) (FR-3947)
- [ ] T040 [P] Percorrer `specs/123-ux-da-retificacao/quickstart.md` §2 no Edital do demo, com capturas em `specs/123-ux-da-retificacao/capturas/` (Princípio VI)
- [ ] T041 Fazer a medição E1–E3 de quickstart §3 no Edital ampliado, registrar em `doc/medicao-retificacao-123-<data>/` e apresentar ao usuário a recomendação da regra (FR-3950, SC-1182)
- [ ] T042 [P] Atualizar a linha da `123` na tabela de incrementos do `README.md` e a Visão do Sistema, se o incremento for mergeado

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (1)**: sem dependência.
- **Foundational (2)**: depende de T001; T004 → T008 antes de qualquer fase de história que use a
  conferência (US4) ou a localização (US2, US4).
- **US4 (3)**: depende de T004–T008.
- **US2 (4)**: depende de T006; T019 depende de T012 (a função `proposta`).
- **US3 (5)**: independe das outras; pode correr ao lado da 3 e da 4 em outro arquivo, mas toca
  `retificar.html` e `views.py` — serializar com elas se houver uma pessoa só.
- **US1 (6)**: independe do servidor; só `retificacao.js` e a folha. Compartilha `retificacao.js` com
  T022: fazer T022 antes de T034.
- **US5 (7)**: depende de todas.
- **Polish (8)**: depende de US5.

### User Story Dependencies

- US4 é o MVP porque é a que mexe no caminho da criação: com ela pronta, o risco maior do incremento
  está provado.
- US2 usa `cartao_do_caminho` e a `proposta` de US4.
- US3 e US1 são independentes.

### Parallel Opportunities

- T002 e T003 (mesmo arquivo, mas funções distintas; uma pessoa só).
- T005, T006 e T007 em paralelo depois de T004 estar escrita.
- Os testes de cada história ([P]) em paralelo entre si.
- T015, T023, T031 e T035 tocam a mesma folha: [P] em relação ao código, mas serialize as edições
  da folha entre si.

## Parallel Example: User Story 4

```bash
# depois de T008 verde:
Task: "T009 conferência com impeditivo em tests/interface/test_retificar_conferencia_impeditivos.py"
Task: "T010 edição e validação final no mesmo arquivo"   # mesma pessoa, mesmo arquivo
Task: "T015 regras de .impeditivos em retificar.css"
```

## Implementation Strategy

### MVP First (User Story 4)

1. Phase 1 e Phase 2 (T001–T008), com a suíte de Retificação verde depois da extração.
2. Phase 3 (US4). **Parar e validar**: o impeditivo do quadro aparece na conferência e a criação
   continua recusando.

### Incremental Delivery

US4 → US2 (marca e volta) → US3 (base) → US1 (busca) → US5 (jornada e regressão) → Polish. Cada
história é um commit testável; o PR de implementação leva todas, porque o revisor aprovou o MVP como
um só.

## Notes

- **Nada de regra nova.** Se uma tarefa parecer pedir validação que `validation.py` não tem, pare: é a
  1ª pergunta da auditoria, e é do usuário.
- **Testes que afirmam texto** só mudam os dois de R-010, e para o texto novo.
- Editar arquivo durante a suíte falseia o resultado: não edite com `make test-pg` rodando.
