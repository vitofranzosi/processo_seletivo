---

description: "Task list — 048 · A Retificação acrescenta o que o contrato já permite"
---

# Tasks: A Retificação acrescenta o que o contrato já permite

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim.** A correlação da spec com a auditoria pede demonstração por achado. A `SC-289` só se
prova retificando de fato, e o teste que devia prová-la hoje não retifica (`R-8`). Além disso, três
testes existentes prendem o comportamento antigo e mudam de premissa (`R-9`).

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Se ganhar arquivo em comum depois, o
  `[P]` sai.**
- **NOVO / EXISTENTE**: onde diz existente, **acrescente, sem reescrever** o que a tarefa não manda
  mudar. Onde a tarefa manda reescrever, ela nomeia o caso.
- Caminhos relativos à raiz do repositório. O código fica em `backend/processo_seletivo/`, abreviado
  `P/`; os testes em `backend/tests/`, abreviado `T/`.

---

## Os seis portões

1. **As guardas novas NÃO entram em `apply_change` nem em `apply_changes`** (`R-1`). Esse motor também
   reproduz atos publicados em `publicacoes/domain/consolidation.py`. Guarda ali julga a história.
2. **Testes focados durante, suíte completa no fecho.** Cada tarefa roda os arquivos que toca e os
   vizinhos que ela nomeia. As guardas desta feature só alcançam o que o ato **faz nascer ou
   acrescenta**, e por isso não há protótipo de medição: o impacto previsto é o do `R-9`.
3. **Esta feature NÃO tem migration.** O `make preparar` continua **`N de 34`**, com N diferente de
   zero.
4. **Nenhum campo de nascimento nasce com valor.** Nada de booleano pré-selecionado, nada de `select`
   sem opção vazia. A `SC-294` é o teste disso, e ele roda em toda história que oferece nascimento.
5. **Toda view nova com `raise Http404` ganha linha no inventário** em
   `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` **no mesmo commit**. Sem ela,
   `T/test_gramatica_das_portas.py` reprova, e só no `test-pg` completo.
6. **Nada de `make test`.** Use `make test-pg`, com `DB_NAME` próprio da worktree. O `lint` são **dois**
   passos, `ruff check` **e** `ruff format --check`. Não edite arquivo durante a suíte.

---

## Phase 1: Setup

- [X] T001 Preparar a worktree em `backend/`:
  - copiar `backend/.env` do checkout principal (**gitignorado**) e trocar `DB_NAME` e `POSTGRES_DB` por nome próprio desta worktree (`test_retificacao_048`);
  - rodar `uv sync --extra dev` e `make preparar`, e conferir **`N de 34`**;
  - rodar `manage.py migrate --check`;
  - conferir com `gh pr view` se a `047` (PR #191/#193) foi mesclada. Se foi, rebasear; nenhuma tarefa depende dela.

**Checkpoint**: `N de 34`, `migrate --check` limpo, e os testes de Retificação verdes antes de qualquer edição (`T/interface/test_retificar*.py`, `T/integration/publicacoes/`).

---

## Phase 2: Foundational — as peças que todas as histórias usam

- [X] T002 Extrair de `P/editais/domain/perfis.py` (**EXISTENTE**) duas funções, **sem mudar comportamento** (`R-4`):
  - `validar_modalidade(modalidade, *, codigos_do_perfil)`: código presente e único entre `codigos_do_perfil`, denominação preenchida, e `validate_normative_rule` quando há regra. Vem de `:96-99` e do que `validate_profile` já faz com a Modalidade;
  - `validar_criterio(criterio, *, ordens_do_marco)`: tipo e `whenMissing` no vocabulário de `P/classificacao/domain/desempate.py:25-32` (importação local, como `_validar_regra_de_corte` faz com `faixa`), `stageId` ou `factId` conforme o tipo, e ordem fora de `ordens_do_marco`. Vem de `:332-352`;
  - `validate_profile` e `validate_classification_milestones` passam a usar as **mesmas constantes de frase** (`MODALIDADE_REPETIDA`, `CRITERIO_COM_ORDEM_REPETIDA`, `CRITERIO_SEM_ALVO`, `CRITERIO_SEM_COMPORTAMENTO_NA_AUSENCIA`), e não a chamá-las. *Desvio registrado na implementação*: parte das exigências da composição (código e denominação preenchidos, fundamento com versão, vocabulário do critério) mora no serializer da API, e não em `validate_profile`. Chamar as funções novas dali acrescentaria exigência à composição pela tela, o que seria mudar comportamento. A exceção continua `ProfileValidationError`.
- [X] T003 [P] Casos unitários das duas funções em `T/unit/editais/test_validacao_da_entidade_acrescentada.py` (**NOVO**): cada recusa com a frase exata que a composição já dava, e o caminho feliz. Rodar em seguida `T/unit/editais/test_perfis.py` e `T/unit/editais/test_marco_classificatorio.py`: **verdes sem mudar asserção**.
- [X] T004 Criar em `P/publicacoes/domain/changes.py` (**EXISTENTE**) a função `recusar_janela_que_nasce_sem_recurso(base, resultado)` (`R-1`, `FR-787`, `D-003`): para cada `appealWindow` ausente em `base` e presente em `resultado`, recusa se `admits` não é verdadeiro, com `CampoNaoRetificavel` e a frase do [contrato](contracts/a-retificacao-que-acrescenta.md) §2. Comparar antes e depois, e não cada alteração, fecha também o `REMOVE` + `ADD` no mesmo ato. **Não** chamá-la de `apply_change`/`apply_changes` (portão 1); o docstring diz por quê e cita o `consolidate`. **Só a janela**: a troca de campo não retificável por objeto inteiro é o achado A-6 da spec, e fica fora.
- [X] T005 [P] Casos unitários em `T/unit/publicacoes/test_janela_que_nasce.py` (**NOVO**):
  - nascimento de `appealWindow` com `admits: false`: recusado; com `true`: passa;
  - janela **existente** alterada para `admits: false`, por campo ou por objeto inteiro: passa — não é nascimento, e alterar janela existente segue a regra de hoje (cenário 4 da US3);
  - nascimento de `cutRule` e de `drawMethod`: passam, e não são desta guarda.
- [X] T006 Chamar `recusar_janela_que_nasce_sem_recurso` em `P/publicacoes/application/retificacoes.py` (**EXISTENTE**) nos três pontos do `R-1`:
  - `_apply_declared_changes`, depois de `apply_changes`: recusa;
  - ~~`advertencias_do_ato`~~ — *desvio registrado na implementação*: não é chamada ali. O docstring de `advertencias_do_ato` diz que impeditivo é assunto do ato, e a recusa aparece na elaboração e na publicação; convertê-la em advertência mostraria duas vezes a mesma coisa com severidades diferentes;
  - `publish_retification`, logo depois do `apply_changes` da linha ~690: recusa.
  - A tradução para `invalid_change`/422 é a de `_recusa_de_caminho`, sem mapeamento novo.
- [X] T007 [P] Casos de integração em `T/integration/publicacoes/test_janela_que_nasce_pela_api.py` (**NOVO**):
  - pela API, a Retificação que faz nascer a janela com `admits: false` é recusada com 422 e a razão (cenário 2 da US3);
  - o mesmo nascimento, gravado como ato já publicado **antes** da guarda (escrito direto como `AlteracaoNormativa` publicada, como os testes de consolidação fazem), continua consolidando, e uma Retificação **nova** e legítima do mesmo Edital passa: a guarda não julga a história (portão 1).
- [X] T008 Criar em `P/interface/retificacao.py` (**EXISTENTE**) o registro de nascimento (`R-2`, `FR-803`):
  - `NASCIMENTOS: dict[str, tuple[list, dict]]` — objeto → (campos oferecidos quando ausente, complemento fixo). Nasce **vazio**; as histórias o preenchem;
  - estender `_conferir_que_nada_se_oferece_sem_decisao` com a segunda conferência: todo objeto do registro tem `PODE_PASSAR_A_EXISTIR[(colecao, objeto)] == (True, …)`, e todo campo da lista existe em `mutabilidade.CONTRATO`, com qualquer natureza exceto `DERIVADO` e `ESTRUTURAL`;
  - em `diferencas`, no ramo `nascendo`, mesclar o complemento fixo do objeto **só quando** `_declarou_algo(declarado)` for verdadeiro.
- [X] T009 [P] Casos em `T/contract/test_mutabilidade.py` (**EXISTENTE**, acrescente):
  - a guarda de carga recusa lista de nascimento para objeto que não pode nascer (`competitionModalities/normativeRule`) e para campo fora do contrato. Usar a função da guarda com registro montado no caso, sem monkeypatch de módulo;
  - **o guardião da `SC-290`**: todo objeto com `PODE_PASSAR_A_EXISTIR` verdadeiro tem caminho pela tela — lista de alteração sempre oferecida **ou** entrada em `NASCIMENTOS`. Ele **falha** até a `T015`, e fica marcado `xfail(strict=True)` com a razão *"a 048 fecha em T015"*; a `T015` tira a marca.

**Checkpoint**: validações extraídas e verdes; a guarda da janela no ato; o registro de nascimento vazio, com a guarda de carga. Nenhuma tela mudou ainda.

---

## Phase 3: US5 — O Perfil sem reversão passa a declará-la (P5)

**Goal**: o menor dos nascimentos, e o que prova o caminho pela tela.
**Independent Test**: percurso 6 do [quickstart](quickstart.md).

- [X] T010 [US5] Em `P/interface/retificacao.py` `campos_editaveis`, oferecer `CAMPOS_DA_REVERSAO` **sempre** (tirar a condição `isinstance(perfil.get("vacancyReversion"), dict)`, `:816-817`). O rótulo do vazio já existe e continua. Atualizar o comentário: a reversão deixou de ser o caso *"só quando o objeto existe"*.
- [X] T011 [US5] Reescrever `test_o_campo_nao_aparece_onde_o_objeto_nao_existe` em `T/interface/test_retificar_reversao.py:84-94` (**EXISTENTE**) para a **presença**, com o rótulo do vazio, e ajustar o docstring do módulo (`:13-14`). Acrescentar:
  - deixado em *"Nenhum"*, nada nasce;
  - escolhida a espécie, sai **um** `REPLACE /profiles/id=P/vacancyReversion` com `{kind}`, e o resumo tem a linha *antes* `—` → *depois* a espécie por extenso (`FR-800`);
  - Perfil sem quadro: recusado pela validação da publicação; com linha do quadro acrescentada no mesmo ato: passa.

---

## Phase 4: US3 — O marco sem janela ganha o prazo de recurso (P3)

**Goal**: `FR-786`, `FR-787`, `D-003`.
**Independent Test**: percurso 4 do [quickstart](quickstart.md).

- [X] T012 [US3] Em `P/interface/retificacao.py`:
  - `CAMPOS_DO_NASCIMENTO_DA_JANELA = [("appealWindow/durationDays", "Prazo de recurso, em dias corridos", INTEIRO)]` e a entrada `NASCIMENTOS["appealWindow"] = (…, {"admits": True, "unit": "DIAS_CORRIDOS"})`;
  - `campos_editaveis` oferece esta lista para marco com `appealWindow` nulo ou ausente, e `CAMPOS_DA_JANELA` para marco com janela, como hoje;
  - o rótulo do vazio do `R-10`.
- [X] T013 [US3] Casos em `T/interface/test_retificar_janela_recursal.py` (**EXISTENTE**, acrescente):
  - marco sem janela: a tela oferece **só** o prazo, e nenhum controle *"admite"* (cenário 2 da US3; a recusa pela API é da `T005`/`T007`);
  - com `3`, sai **um** `REPLACE …/appealWindow` com `{admits: true, durationDays: 3, unit: "DIAS_CORRIDOS"}`, e o resumo tem a linha *antes* `—` → *depois* `3` (`FR-800`);
  - em branco, nada nasce;
  - zero é recusado pela validação que já existe;
  - marco **com** janela continua oferecendo os três campos.
- [X] T014 [P] [US3] Caso de integração em `T/integration/recursos/test_janela_nascida_por_retificacao.py` (**NOVO**): Edital publicado com marco sem janela; Retificação publicada que faz nascer a janela; o ato de resultado divulgado **depois** abre a interposição com o prazo declarado. Usar as fixtures de recurso que `T/integration/recursos/` já tem.

---

## Phase 5: US2 — A tela do corte deixa de terminar num beco (P2)

**Goal**: `FR-788` a `FR-790`, `D-002`.
**Independent Test**: percurso 3 do [quickstart](quickstart.md).

- [X] T015 [US2] Em `P/interface/retificacao.py`:
  - `CAMPOS_DO_NASCIMENTO_DO_CORTE`, com os seis campos da regra: `cutRule/targetKind`, `cutRule/targetCount`, `cutRule/surplusCount`, `cutRule/tieOutcome`, `cutRule/governedStage` e `cutRule/continuation`;
  - tipos: escolha, inteiro, inteiro, escolha, escolha e escolha;
  - opções dos vocabulários de `P/classificacao/domain/faixa.py:21-41`, com os **rótulos que a composição usa** no cartão do marco (`P/interface/templates/interface/_marco.html` e `P/interface/forms.py`: procure-os lá e reuse; não redija outros);
  - Etapa governada: as Etapas do conteúdo vigente mais *"Não governa Etapa"* (`SEM_ETAPA_GOVERNADA`);
  - entrada em `NASCIMENTOS["cutRule"]`, sem complemento;
  - `campos_editaveis` oferece a lista de nascimento quando `cutRule` é nulo ou ausente, e `CAMPOS_DO_CORTE` quando existe, como hoje;
  - rótulos do vazio do `R-10`;
  - tirar o `xfail` do guardião da `T009`: com a reversão (`T010`), a janela (`T012`) e o corte, a `SC-290` fecha aqui.
- [X] T016 [US2] Criar em `P/publicacoes/application/retificacoes.py` a função `_recusar_corte_sobre_etapa_com_resultado(edital, base, conteudo)` (`R-3`):
  - para cada marco com `cutRule` ausente na base e presente no conteúdo, pega `faixa.etapa_governada(regra)`;
  - se houver Etapa e `resultados.application.selectors.ha_resultado_em(edital=edital, etapa_id=…)` (importação local), levanta `DomainError` 422 com a frase do contrato §2, nomeando marco e Etapa pelo nome;
  - `_apply_declared_changes` passa a receber `edital`, e `create_retification`/`edit_retification` o passam;
  - chamar também em `publish_retification`, depois do `apply_changes`, sob o `select_for_update` que já existe.
- [X] T017 [P] [US2] Casos de interface em `T/interface/test_retificar_corte.py` (**NOVO**):
  - marco sem regra: os seis campos, com rótulos e vazios;
  - marco com regra: três campos e as exclusões com a razão (inalterado);
  - só a quantidade preenchida: recusa com as mensagens da publicação;
  - regra inteira: **um** `REPLACE …/cutRule`, e a publicação aceita; o resumo tem uma linha por campo declarado, *antes* `—` → *depois* o valor por extenso (`FR-800`);
  - nada preenchido: nada nasce.
- [X] T018 [P] [US2] Casos de integração em `T/integration/publicacoes/test_corte_nascido_por_retificacao.py` (**NOVO**):
  - Etapa governada com Resultado registrado: recusa **na elaboração**, com a frase;
  - Resultado registrado **entre** a confirmação e a publicação: recusa **na publicação**;
  - regra que não governa Etapa: passa mesmo com Resultado em outra Etapa;
  - Etapa sem Resultado: passa, e a tela do corte deixa de recusar por falta de regra.
  - Resultado registrado pelas fixtures de `T/fixtures/comissao.py`.
- [X] T019 [US2] Caso em `T/interface/test_corte.py` (**EXISTENTE**, acrescente ao lado de `:373-386`, sem mudar este): seguir o `href` de *"Retificar o Edital para declarar a regra de corte"* e afirmar que a página de destino oferece `cutRule/targetKind` para **aquele** marco (`FR-790`, `SC-291`). Repetir para o marco ordenado por sorteio (`:455-470`).

---

## Phase 6: US4 — O critério de desempate se corrige, e não só se reduz (P4)

**Goal**: `FR-792` a `FR-794`, `D-004`.
**Independent Test**: percurso 5 do [quickstart](quickstart.md).

- [X] T020 [US4] Em `P/interface/retificacao.py`:
  - `NOVO_CRITERIO` com os campos:
    - `("id", "", OCULTO)`;
    - `("milestone", "Marco", REFERENCIA)`, opções `perfil_id|marco_id` rotuladas *"Perfil — Marco"*;
    - `("type", "O que o critério compara", REFERENCIA)`;
    - `("target", "Etapa ou fato comparado", REFERENCIA)`;
    - `("whenMissing", "Quando o valor não existe", REFERENCIA)`;
    - `("order", "Ordem de aplicação", INTEIRO)`;
  - `opcoes_do_criterio_novo(conteudo)`: os marcos; os tipos e os comportamentos com os **rótulos da composição**; os alvos com Etapas **do marco** e fatos **do Perfil**, prefixados para distinguir;
  - em `diferencas`, depois das linhas do quadro:
    - para cada linha nova, conferir o alvo contra o marco escolhido (Etapa classificatória do Edital, como a composição oferece em `_criterio.html`, ou fato do Perfil dele), senão `ValueError` com o rótulo. *Ajuste na implementação*: a primeira redação dizia "Etapa enumerada pelo marco", e a composição oferece as Etapas classificatórias do Edital; a spec (`FR-793`) foi corrigida para a regra da composição;
    - chamar `validar_criterio` (`T002`) **ao conferir** (`FR-793`, I1 do analyze), com as ordens dos critérios do marco que **continuam** — os vigentes menos os marcados para remover, mais os acrescentados antes no mesmo ato. Remover um critério e acrescentar outro com a mesma ordem passa (percurso 5). `ProfileValidationError` vira `ValueError` com a mesma frase;
    - montar `parameters` (`stageId` ou `factId`) conforme o tipo;
    - emitir `ADD /profiles/id=P/classificationMilestones/id=M/tiebreakers/-` com `{id, order, type, parameters, whenMissing}`;
    - linha de resumo *"Acréscimo"* com o tipo e o alvo.
- [X] T021 [US4] Fragmento `fragmento_retificacao_criterio(request, edital_id)` em `P/interface/views.py`, com escopo de Edital, no molde de `fragmento_retificacao_linha_do_quadro` (`:2611-2639`):
  - URL `fragmento-retificacao-criterio` em `P/interface/urls.py`;
  - template `P/interface/templates/interface/_retificacao_criterio.html` (**NOVO**, no molde de `_retificacao_linha_do_quadro.html` e com o `id` oculto de `_retificacao_anexo.html`);
  - botão *"Acrescentar critério de desempate"* na seção *Perfis de Vaga* de `retificar.html`;
  - reexibição depois do POST (`novas_para_formulario`, `views.py:~3284-3301`, prefixo `criterio`);
  - **a linha no inventário de negativas da `033` no mesmo commit** (portão 5).
- [X] T022 [US4] Em `P/publicacoes/application/retificacoes.py`, para cada critério presente no conteúdo e ausente na base, chamar **de novo** `validar_criterio` — a `T020` o chama ao conferir, e esta cobre a confirmação, a publicação e a API — com as ordens dos **demais** critérios daquele marco, em `_apply_declared_changes` e em `publish_retification`. `ProfileValidationError` vira `DomainError` 422 com a frase (`FR-793`, `R-4`).
- [X] T023 [P] [US4] Casos em `T/interface/test_retificar_criterio.py` (**NOVO**):
  - o botão existe;
  - o fragmento oferece as Etapas classificatórias do Edital e os fatos de cada Perfil;
  - critério completo: **um** `ADD` com identidade estável entre conferir e confirmar, e o resumo tem a linha *"Acréscimo"*, *antes* `—` → *depois* o tipo e o alvo (`FR-800`);
  - ordem repetida, fato de outro Perfil e tipo por Etapa com alvo fato: recusas **ao conferir**, no POST sem `confirmar`;
  - remover um critério e acrescentar outro com a **mesma** ordem: passa;
  - remover um e acrescentar outro no mesmo ato: as duas alterações.
- [X] T024 [P] [US4] Caso em `T/integration/classificacao/test_calculo.py` (**EXISTENTE** — *ajuste na implementação*: o arquivo novo previsto repetiria o cenário com ordem emitida que este já monta; acrescentado ao lado de `test_retificacao_da_regra_obsoleta_sem_resultado_novo`, com um segundo caso que prova a recusa da `T022` pela API): ordem emitida de um marco; Retificação publicada que acrescenta critério; o ato fica **obsoleto e recomputável**, pela mesma causa que a remoção produz (`FR-794`).
- [X] T025 [US4] `T/integration/editais/test_derivacao_nao_alcanca_o_declarado.py:78-99` (**EXISTENTE**): acrescentar `fragmento-retificacao-criterio` ao conjunto exato. A asserção de que **não** há `fragmento-retificacao-marco` continua.

---

## Phase 7: US1 — Um Perfil publicado ganha a Modalidade que faltava (P1) 🎯

**Goal**: `FR-777` a `FR-782`, `D-001`, `D-G5`.
**Independent Test**: percursos 1 e 2 do [quickstart](quickstart.md).

- [X] T026 [US1] Em `P/interface/retificacao.py`:
  - `NOVA_MODALIDADE` com os campos:
    - `("id", "", OCULTO)`;
    - `("profileId", "Perfil", REFERENCIA)`;
    - `code`, `name` e `description` (TEXTO);
    - `foundation` e `version` (TEXTO);
    - `percentage` (DECIMAL);
    - `("general", "É a ampla concorrência deste Perfil", BOOLEANO)`, renderizado como **caixa de marcação**, e não como o `select` Sim/Não: desmarcada não é enviada (portão 4);
    - `("immediateVacancies", "Vagas imediatas", INTEIRO)`;
  - `opcoes_da_modalidade_nova(conteudo)`: os Perfis vigentes;
  - em `diferencas`, antes das linhas do quadro, para cada linha nova:
    - chamar `validar_modalidade` (`T002`) **ao conferir** (`FR-778`, I1 do analyze), com os códigos das Modalidades vigentes do Perfil mais os das acrescentadas antes no mesmo ato. A mesma função dá código repetido, denominação ausente, fundamento sem versão e percentual fora da faixa. `ProfileValidationError` vira `ValueError` com a mesma frase;
    - ampla **e** vagas: `ValueError` com a frase do contrato §2;
    - emitir `ADD /profiles/id=P/competitionModalities/-` com a forma do [data-model](data-model.md): `normativeRule` só se houver fundamento, versão ou percentual, como em `P/interface/forms._modalidades`; opacos `{}`; `effectiveFrom` nulo; `id` da regra novo;
    - se ampla, `REPLACE /profiles/id=P/generalCompetitionModalityId` com o `id` da linha;
    - se houver vagas, `ADD /profiles/id=P/vacancyTable/-` com `modalityId` igual ao `id` da linha;
    - uma linha de resumo por alteração.
- [X] T027 [US1] Fragmento `fragmento_retificacao_modalidade(request, edital_id)` em `P/interface/views.py`, com escopo de Edital, como a `T021`:
  - URL `fragmento-retificacao-modalidade`;
  - template `P/interface/templates/interface/_retificacao_modalidade.html` (**NOVO**);
  - botão *"Acrescentar Modalidade"* em `retificar.html`, **substituindo** a frase *"Modalidades de Concorrência ainda não são definidas por aqui."* (`FR-782`) por ajuda que diga que a Modalidade acrescentada passa a valer para inscrições novas quando a Retificação for publicada;
  - reexibição depois do POST, com prefixo `modalidade`;
  - **a linha no inventário de negativas no mesmo commit**;
  - acrescentar `fragmento-retificacao-modalidade` ao conjunto de `test_derivacao_nao_alcanca_o_declarado.py`;
- [X] T028 [US1] Em `P/publicacoes/application/retificacoes.py`, para cada Modalidade presente no conteúdo e ausente na base, chamar **de novo** `validar_modalidade` — a `T026` o chama ao conferir, e esta cobre a confirmação, a publicação e a API — com os códigos das **demais** Modalidades do Perfil, nos dois pontos da `T022` (`FR-778`).
- [X] T029 [US1] `T/integration/publicacoes/test_enderecamento.py:610-633` (**EXISTENTE**): dar `name` à Modalidade acrescentada pela API, que a `T028` passa a exigir. A asserção de endereçamento não muda, e o docstring do caso ganha uma linha dizendo por quê.
- [X] T030 [P] [US1] Casos em `T/interface/test_retificar_modalidade.py` (**NOVO**):
  - a frase antiga não aparece e o botão aparece;
  - o fragmento oferece os Perfis vigentes;
  - ampla sem vagas: `ADD` da Modalidade e `REPLACE` da ampla, com a mesma identidade nas duas fases;
  - cota com vagas: `ADD` da Modalidade e `ADD` da linha apontando para ela;
  - ampla com vagas: recusa;
  - código repetido e sem denominação: recusas **ao conferir**, no POST sem `confirmar`, com a frase da composição;
  - fundamento sem versão: a frase de `validate_normative_rule`, também ao conferir;
  - cota sem linha no quadro (cenário 6, C1 do analyze): ao confirmar, o aviso da publicação sobre lista reservada sem linha; e, num Perfil cujo corte deriva o alvo do quadro, a recusa `cut_rule_sem_linha_de_quadro`;
  - o resumo lista cada alteração com *antes* em branco.
- [X] T031 [US1] Reescrever `test_modalidade_acrescentada_depois_nao_obsoleta_a_ordem_da_ampla` em `T/integration/classificacao/test_ordem_por_recorte.py:356` (**EXISTENTE**, este caso) para **retificar de fato** (`SC-289`, `R-8`):
  - ordens emitidas para a ampla e para uma cota;
  - Retificação publicada, pela aplicação, que acrescenta outra cota com vagas;
  - as duas ordens continuam vigentes e sem sucessor;
  - `ato_vigente(lista_id=<nova>)` é `None`;
  - o docstring deixa de remeter ao cenário 5.2 da `034`.
- [X] T032 [P] [US1] Caso em `T/integration/inscricoes/test_modalidade_acrescentada_por_retificacao.py` (**NOVO**), para `SC-288` e `FR-781`:
  - Perfil com duas cotas e sem ampla, período aberto;
  - uma inscrição enviada por cota;
  - Retificação publicada que acrescenta a ampla, declarada;
  - a inscrição enviada mantém `modality_id` e a lista exigida;
  - um rascunho novo oferece a ampla, e o envio de não-cotista por ela é aceito;
  - a página pública da seleção (a view de `P/portal/views.py` que renderiza `selecao.html`) mostra a Modalidade acrescentada, pela versão vigente (`FR-797`);
  - a versão anterior continua consultável pela API pública de versões, sem a ampla (`FR-796`);
  - caso-limite *"Rascunho de inscrição aberto"* (C2 do analyze): num Perfil com **uma** Modalidade, rascunho aberto com a Modalidade assumida; Retificação publicada que acrescenta outra; o envio é recusado com `edital_updated` até a pessoa reconhecer a versão, e a Modalidade assumida continua gravada — ela pode trocá-la pela ampla. *Corrigido na implementação*: a redação anterior esperava `modality_required`, e o teste mostrou que a assumida fica gravada; a spec foi corrigida junto.

---

## Phase 8: Fecho

- [X] T033 A `SC-294` em `T/interface/test_retificar.py` (**EXISTENTE**, acrescente): Edital publicado com marco sem janela, marco sem corte e Perfil sem reversão; o POST da tela, com **todos** os campos que o formulário envia, altera só a descrição; o resumo tem **uma** linha e as alterações são **uma**. Montar o POST a partir do formulário renderizado, e não à mão: é o que pega o controle pré-selecionado.
- [X] T034 [P] O `FR-798` em `T/integration/publicacoes/test_documento_da_retificacao_que_acrescenta.py` (**NOVO** — *ajuste na implementação*: pelo caminho da publicação, e não compondo o PDF à mão, porque o requisito é sobre o documento que a Retificação publica): `render_edital_pdf` sobre conteúdo com Modalidade acrescentada, a linha do quadro dela, janela, corte, critério e reversão nascidos mostra os **seis**.
- [X] T035 [P] `specs/048-retificacao-que-acrescenta/rastreabilidade.md` (**NOVO**):
  - uma linha por requisito — `FR-777` a `FR-782`, `FR-784` a `FR-803`, `SC-288` a `SC-292` e `SC-294` —, com arquivo e **caso pelo nome**. `test_citacoes_de_requisito.py` cobra requisito a requisito;
  - **uma linha por caso-limite** da spec, com o caso que o prende; onde não houver caso, *"leitura do diff"*, dizendo o que se lê.
- [X] T036 Percorrer pela tela os percursos 1 a 7 do [quickstart.md](quickstart.md), com identidades segregadas e banco próprio, e registrar o resultado em `specs/048-retificacao-que-acrescenta/percursos.md` (**NOVO**). *Feito sobre o `seed_demo`: os percursos 2, 4, 5 e 6 pela tela, num ato só, com identidades segregadas; o 1, o 3 e o 7 não couberam no Edital do `seed` e estão provados por teste — o registro diz por quê.* Lacuna encontrada é registrada, e não contornada por API.
- [X] T037 Registros de governança:
  - em `doc/decisoes-pendentes-da-consolidacao.md`, na `DP-08`, acrescentar o bloco **"O que foi decidido"** só para o **item 2** — *"a `D-G5` foi para a B-4, executada pela `048`"* —, com a data. O item 1, encerrar a `039`, continua aberto;
  - **as linhas de `RC-37` e `RC-38` em `doc/auditoria-de-consolidacao-2026-09-26.md` ficam para depois do merge**, em PR de documentação próprio, como a `046` fez: *"resolvido pelo #NNN"* antes do merge afirmaria o que ainda não aconteceu.
- [X] T039 *Acrescentada na implementação*: a tela do ato — detalhe da Retificação, onde se homologa e se assina — dizia "—" para o objeto que nasce, porque ele não tem `name` nem `code`. `CAMPO_EM_PORTUGUES` ganhou o nome dos objetos que nascem, e `retificacao_ui.objeto_legivel` os diz por extenso (`FR-800`). Prende: `T/interface/test_retificar_corte.py::test_a_tela_do_ato_diz_a_regra_que_nasce_por_extenso`
- [X] T038 `make lint check test-pg DB_NAME=test_retificacao_048`:
  - `ruff check` **e** `ruff format --check`;
  - zero falhas, e os **11** pulados de sempre;
  - `make preparar` em **`34 de 34`**.

---

## Dependencies & Execution Order

```
Phase 1 (T001)
   ▼
Phase 2  T002 → T003
         T004 → T005 → T006 → T007
         T008 → T009
   ▼  (as três trilhas da Phase 2 são independentes entre si)
US5 (T010–T011)   ← só depende de T008 para o comentário; pode entrar em paralelo com T004–T007
   ▼
US3 (T012–T014)   ← depende de T004–T006 (a janela "não admite" pela API) e T008
   ▼
US2 (T015–T019)   ← depende de T008
   ▼
US4 (T020–T025)   ← depende de T002 (validar_criterio)
   ▼
US1 (T026–T032)   ← depende de T002 (validar_modalidade); reusa o molde de fragmento da US4
   ▼
Fecho (T033–T038)
```

**A ordem não é a das prioridades, e é de propósito** ([plano](plan.md), *Ordem de entrega*). As
guardas vêm antes do que elas protegem: com a janela oferecida antes da `T006`, uma tarefa
intermediária deixaria nascer pela API a janela que não concede.

### Dentro das fases

- `retificacao.py` é tocado por `T008`, `T010`, `T012`, `T015`, `T020` e `T026`. **Nenhuma delas é
  `[P]` entre si.**
- `retificacoes.py` é tocado por `T006`, `T016`, `T022` e `T028`, em sequência.
- `views.py`, `urls.py` e `retificar.html` são tocados por `T021` e `T027`, em sequência.

### Oportunidades de paralelismo

- Os casos de teste marcados `[P]` (`T003`, `T005`, `T007`, `T009`, `T014`, `T017`, `T018`, `T023`,
  `T024`, `T030`, `T032`, `T034`) estão cada um em arquivo próprio e só dependem da tarefa de produção
  da sua fase.
- A trilha `T002–T003` corre em paralelo com `T004–T007`, e as duas com `T008–T009`.

## Estratégia de entrega

**MVP é a US1**, que é o valor, mas ela entra por último, sobre peças já provadas. Se a entrega
precisar parar no meio, o corte natural é **depois da US2**. Nesse ponto já estão prontos:
- as guardas;
- a reversão, a janela e o corte pela tela;
- o beco da tela do corte fechado.

Faltariam o critério e a Modalidade, e o `RC-37` continuaria aberto — dito assim na descrição do PR.

**O que não fazer**:
- pôr guarda no motor de alterações (portão 1);
- afrouxar a guarda de carga para caber o corte, em vez de declarar o nascimento no registro (`FR-803`);
- validar a Modalidade ou o critério sobre o conteúdo inteiro (`R-4`);
- apagar caso para ficar verde sem linha na `rastreabilidade.md`.
