---

description: "Tarefas da 043 — Duplicar Perfil"
---

# Tasks: Duplicar Perfil

**Input**: Design documents from `specs/043-duplicar-perfil/`

**Prerequisites**: [plan.md](./plan.md) · [spec.md](./spec.md) · [research.md](./research.md) ·
[data-model.md](./data-model.md) · [contracts/duplicar-perfil.md](./contracts/duplicar-perfil.md) ·
[quickstart.md](./quickstart.md)

**Tests**: **incluídos**. A Constituição exige cobertura específica de cotas, documentos,
autorização e integridade normativa, e o risco desta feature é o que **erra em silêncio**: uma
referência da cópia apontando a origem atravessa a gravação e só falha na publicação, ou nunca
(`023`, T-005). Os testes da transformação vêm **antes** dela.

**Organization**: uma jornada só (`US1`). As Fases 2 e 3 são a mesma história partida pela
dependência: a transformação e o transporte dos marcos são pré-requisito do fragmento, e têm de estar
provados antes que haja tela.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode ser feita em paralelo com as demais `[P]` da mesma fase — sem dependência
  pendente. Casos do **mesmo** arquivo de teste levam `[P]` entre si porque são escritos juntos, e
  não porque tocam arquivos distintos
- **[Story]**: `US1`; Setup, Foundational e Polish não têm rótulo

**Caminhos**: `backend/processo_seletivo/…` para código, `backend/tests/…` para teste. Banco de teste
próprio desta worktree: `DB_NAME=ps_043`.

---

## Phase 1: Setup

**Purpose**: partir de uma linha de base conhecida. Nada se instala.

- [X] T001 Conferir as dependências com `uv sync --extra dev` em `backend/` e rodar a linha de base dos arquivos que esta feature toca — `backend/tests/unit/editais/test_reaproveitamento.py`, `backend/tests/interface/test_round_trip_do_rascunho.py`, `backend/tests/interface/test_compor.py`, `backend/tests/test_vocabulario_da_composicao.py` e `backend/tests/interface/test_acessibilidade.py` —, registrando a contagem: é contra ela que as regressões desta feature aparecem
- [X] T002 Ler `backend/tests/unit/editais/test_reaproveitamento.py` e anotar **qual** teste cobra a lista fechada de referências de `remapear` — `R-001` apoia o reuso nessa cobrança, e se ela não existir como se supõe, a premissa cai antes de haver código sobre ela

**Checkpoint**: linha de base verde e contada; a premissa de `R-001` conferida.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a transformação origem → cópia, pura, e o transporte dos marcos pela etapa Perfis.
**Nenhuma tela antes desta fase**: é aqui que mora o risco silencioso, e o lugar de prová-lo é sem
banco e sem navegador.

### Testes da transformação ⚠️ — escrever primeiro, e vê-los falhar

- [X] T003 [P] Criar `backend/tests/unit/editais/test_duplicacao.py` com a fixture de um Perfil completo **na forma de `forms.ler_perfis`**: quatro Modalidades com Regra, uma delas declarada ampla concorrência; linha geral e três reservadas; dois fatos; um marco com `stages`, `drawMethod.qualifyingStageId`, regra de corte, janela recursal e dois critérios — um com `stageId`, outro com `factId`; e `classificationInformation`/`callInformation` presentes
- [X] T004 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **identidades novas** para Perfil, Modalidades, Regras, linhas reservadas, fatos, marcos e critérios, sem nenhuma coincidir com a origem; e a linha geral com `identidade_da_linha_geral(<id novo>)` (`FR-640`, `SC-232`)
- [X] T005 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **remapeamento para dentro** — `generalCompetitionModalityId`, o `modalityId` de cada linha reservada e o `factId` do critério apontam a contraparte **da cópia**; `generalCompetitionModalityId` `None` segue `None` (`FR-641`)
- [X] T006 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **preservação para fora** — `stages`, `drawMethod.qualifyingStageId` e o `stageId` do critério **iguais** aos da origem; e uma Etapa que **não** está entre as do Edital estoura `ReferenciaNaoMapeada` (`FR-642`, `R-001`)
- [X] T007 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: referência interna **sem contraparte** — critério citando fato que o Perfil não declara, linha reservada apontando Modalidade de outro Perfil — estoura `ReferenciaNaoMapeada`, e nunca atravessa (`FR-641`)
- [X] T008 [P] Em `backend/tests/interface/test_duplicar_perfil.py` — e não no arquivo unitário, porque a enumeração exige um Perfil **gravado**: **completude contra o contrato** — enumerar as chaves do Perfil **a partir da saída de `forms.perfis_persistidos`** sobre um Perfil gravado com todas as coleções (e as chaves das coleções aninhadas), e não de uma lista escrita no teste nem de `ler_perfis`, que não conhece os campos sem tela, e exigir que cada uma caia numa categoria do [data-model.md](./data-model.md): igual, nova, remapeada, preservada, informada, derivada ou ausente. Uma chave sem categoria reprova (`FR-639`)
- [X] T009 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: Código e Localidade **informados**; campos sem tela **ausentes**; tudo o mais **igual** (`FR-635`, `FR-643`, `SC-233`)
- [X] T010 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **marco derivado × escrito à mão** — código `LP01` e `LP01-2` com denominação *"Classificação final — ⟨denominação⟩"* viram `LP02` e `LP02-2`; código escrito à mão é copiado como está; e o caso de `R-005`/`T-4`: Código da origem mudado **na tela** sem gravar não faz o marco `LP01` gravado parecer escrito à mão (`FR-644`)
- [X] T011 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **identidade vazia** — duas Regras com `id` `""` saem com identidades **distintas** e não nulas (`R-002`)
- [X] T012 [P] Em `backend/tests/unit/editais/test_duplicacao.py`: **a origem não muda** — o dicionário recebido é idêntico, por comparação profunda, antes e depois (`FR-646`)

### Implementação da transformação

- [X] T013 Criar `backend/processo_seletivo/editais/domain/duplicacao.py` com `duplicar_perfil(perfil, *, codigo, localidade, etapas_do_edital, codigo_gravado_da_origem=None, nome_gravado_da_origem=None, nova=uuid.uuid4)`, pura, sem banco: identidade prévia para os vazios (`R-002`); mapa de `reaproveitamento.mapa_de_identidades` **mais** `{etapa: etapa}` para as Etapas do Edital; `reaproveitamento.remapear` sobre `{"profiles": [perfil]}`; linha geral por `perfis.identidade_da_linha_geral`; Código e Localidade; remoção de `reaproveitamento.CAMPOS_SEM_TELA`. Docstring no tom do repositório: por que reusa `remapear`, e por que as Etapas mapeiam para si mesmas (`R-001`)
- [X] T014 Implementar em `backend/processo_seletivo/editais/domain/duplicacao.py` a re-derivação da identidade do marco por `marcos.identidade_derivada`, código e denominação avaliados **separadamente**, contra o digitado **e** o gravado da origem, com `codigos_em_uso` acumulado na ordem dos marcos (`FR-644`, `R-005`)

### O transporte dos marcos pela etapa Perfis

- [X] T015 [P] Teste de travessia em `backend/tests/interface/test_duplicar_perfil.py`: um POST da etapa Perfis com um Perfil **novo** carregando `perfil-<i>-marcosEmTransito` grava o Perfil **com** os marcos; e um Perfil **já gravado** que carregue o campo continua com os marcos gravados — a preservação vence (`R-003`)
- [X] T016 [P] Teste de **recusa** em `backend/tests/interface/test_duplicar_perfil.py`: o mesmo POST com um erro em **outro** Perfil é recusado, e a tela devolvida traz o campo em trânsito da cópia **com o mesmo JSON** — é aqui que os marcos sumiriam sem aviso (`FR-650`, `T-1`)
- [X] T017 [P] Teste de JSON inválido em `backend/tests/interface/test_duplicar_perfil.py`: `perfil-<i>-marcosEmTransito` malformado é recusa **com mensagem no Perfil**, e não 500
- [X] T018 Fazer `ler_perfis` ler `perfil-<i>-marcosEmTransito` em `backend/processo_seletivo/interface/forms.py` — quando presente, `classificationMilestones` vem do JSON; ausente, o comportamento de hoje. Comentário marcando-o como a **quinta** travessia dos marcos, ao lado das quatro que o código já nomeia (`R-003`)
- [X] T019 Fazer `_reexibir_perfis` devolver o campo em trânsito em `backend/processo_seletivo/interface/views.py` — `marcos_em_transito` com o JSON de `classificationMilestones` quando não vazio
- [X] T020 Emitir o campo oculto em `backend/processo_seletivo/interface/templates/interface/_perfil.html` **só** quando `perfil.marcos_em_transito` existir — cartão de Perfil gravado nunca o emite
- [X] T021 Conferir que `backend/tests/interface/test_round_trip_do_rascunho.py` continua verde e **não** precisa conhecer o campo em trânsito: ele não é campo do contrato, é transporte de tela (data-model, *O campo em trânsito*)

**Checkpoint**: `duplicar_perfil` provada sem banco; um Perfil novo com marcos em trânsito grava com
eles e sobrevive à recusa. Ainda não há botão.

---

## Phase 3: User Story 1 — Duplicar um Perfil e mudar só o que muda (Priority: P1) 🎯 MVP

**Goal**: junto ao cartão de um Perfil, *Duplicar este Perfil* pede Código e Localidade e insere, logo
abaixo, a cópia completa — gravada quando a etapa for gravada.

**Independent Test**: compor pela interface um Perfil completo, duplicá-lo três vezes — uma delas a
partir de uma cópia não gravada —, gravar, submeter, homologar e publicar; o documento publicado traz
quatro Perfis com o conteúdo da origem, os Códigos e Localidades informados, e nenhuma identidade de
um Perfil no conteúdo de outro.

### Tests for User Story 1 ⚠️

- [X] T022 [P] [US1] Criar `backend/tests/authorization/test_duplicar_perfil.py`: sem `edital`, 404; Edital de outra unidade, 404; ator sem `edital:elaborar`, 403; Edital fora da elaboração, 403; identidade de origem que é de **outro** Edital não é lida — nenhum marco nem contagem de documento dele aparece na resposta (`FR-648`, `R-006`)
- [X] T023 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: sucesso devolve o cartão com os campos da origem, o Código e a Localidade informados e um **índice novo** diferente de todos os da tela; e o HTML traz `autofocus` no primeiro campo editável e a região `role="status"` — o comportamento do foco no navegador continua verificado à mão na demonstração (cenário 1, `FR-637`)
- [X] T024 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: Código **vazio** e Código **igual** ao de outro Perfil da tela — inclusive de um Perfil ainda não gravado — devolvem `200` com `HX-Retarget` para o diálogo, `HX-Reswap: outerHTML` e a mensagem **no campo**; nenhum cartão. **Localidade vazia** não é recusa, e a cópia sai com Localidade vazia, não a da origem (`FR-635`, contrato)
- [X] T025 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`, os **dois** casos de origem com erro, que a spec distingue: valor **ilegível** (`dez` em vagas) recusa no diálogo, sem cartão; erro **de regra** (percentual acima de 100) cria a cópia com o erro, e a gravação da etapa o recusa apontando o campo da cópia (casos-limite da spec, contrato)
- [X] T026 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: a cópia parte do **digitado** — um valor mudado no formulário e não gravado aparece na cópia; e os marcos vêm do **gravado** da origem (`FR-636`, cenário 5)
- [X] T027 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **cadeia sem gravar** — duplicar uma cópia não gravada leva os marcos em trânsito dela, com os fatos remapeados de novo (cenário 7)
- [X] T028 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **avisos** — a região `role="status"` diz quantos marcos a cópia leva (`FR-650`) e quantos Documentos Exigidos restritos à origem **não** foram replicados, contando os recortados pelo Perfil **e** por Modalidade dele; documento de escopo *Todos os Perfis* não conta; origem não gravada conta zero e o aviso não aparece (`FR-645`, `SC-236`, `R-010`)
- [X] T029 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: o fragmento **não grava** — revisão do Edital, contagem de Perfis, de Documentos Exigidos e de eventos de auditoria iguais antes e depois (`FR-638`, `FR-645`)
- [X] T030 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **origem intacta nos três desfechos** — duplicar e gravar, duplicar e gravar sem o cartão da cópia, e não gravar — o conteúdo gravado da origem é o mesmo que sem a duplicação (`FR-646`, `SC-234`, cenário 6)
- [X] T031 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **ponta a ponta sem navegador** — gravar a etapa com três cópias **devolvidas pelo fragmento** e varrer o conteúdo canônico (`edital_snapshot`, o mesmo de que a publicação deriva; a publicação em si é percorrida na demonstração, T046): zero identidades compartilhadas entre Perfis e zero referências de um Perfil a Modalidade ou fato de outro; cada cópia difere da origem só em identidades, Código, Localidade e identidade derivada do marco (`SC-232`, `SC-233`)
- [X] T032 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **gravação continua autoridade** — forjar no POST da etapa duas cópias com o mesmo Código é recusado por `validate_profiles`, como para qualquer Perfil (`FR-647`)
- [X] T033 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: **orçamento de consultas** do fragmento — contagem **igual** entre um Edital de 2 Perfis e um de 16, e **cinco** consultas além da sessão e do Edital (plano, *Performance Goals*, corrigido pela medida)
- [X] T034 [P] [US1] Em `backend/tests/interface/test_duplicar_perfil.py`: *Duplicar este Perfil* **não** aparece na etapa Perfis em modo de leitura, nem em Retificação (`FR-648`, `FR-649`, cenário 9)

### Implementation for User Story 1

- [X] T035 [US1] Acrescentar a rota `fragmentos/perfil/<str:indice>/duplicar` (`name="fragmento-perfil-duplicado"`) em `backend/processo_seletivo/interface/urls.py`, ao lado das demais rotas de fragmento do Perfil
- [X] T036 [US1] Implementar `fragmento_perfil_duplicado(request, indice)` em `backend/processo_seletivo/interface/views.py`, `GET`: `edital` obrigatório; `_edital_do_fragmento`; `pode_compor` ou 403; `ler_perfis(request.GET)` e a origem pelo `perfil-<indice>-id`; os marcos da origem — do trânsito, ou de `forms._marco_persistido` sobre `edital.perfis.filter(pk=…)`; as Etapas do Edital; `duplicar_perfil`; `_reexibir_perfis([copia])` com índice novo por `_indice_de_linha`. Docstring com as decisões `R-003`, `R-004` e `R-006`
- [X] T037 [US1] Implementar em `backend/processo_seletivo/interface/views.py` a recusa do diálogo — Código vazio, Código já na tela, origem ilegível, `ReferenciaNaoMapeada` — como `200` com `HX-Retarget`/`HX-Reswap`, registrando no log o detalhe da `ReferenciaNaoMapeada` com o `correlation_id`, e nunca na resposta (contrato)
- [X] T038 [US1] Implementar em `backend/processo_seletivo/interface/views.py` a contagem de Documentos Exigidos gravados recortados pela origem ou por Modalidade gravada dela (`R-010`)
- [X] T039 [US1] Criar `backend/processo_seletivo/interface/templates/interface/_duplicar_perfil.html`: o `<details>` *Duplicar este Perfil*, os campos `Código do novo Perfil` e `Localidade do novo Perfil` com `form="duplicar-<indice>"` e rótulos associados, a mensagem de erro no campo com `aria-describedby`, e o botão `type="button"` com `hx-get`, `hx-include` (fieldset da origem, `#perfis [name^='perfil-'][name$='-code']`, os dois campos por seletor), `hx-target="closest fieldset"` e `hx-swap="afterend"` (`R-007`, contrato)
- [X] T040 [US1] Incluir o diálogo em `backend/processo_seletivo/interface/templates/interface/_perfil.html` junto de *Remover este Perfil*, **só** quando `editavel` for verdadeiro — a variável que `compor_perfis.html` já usa para o modo de leitura, e que o `include` herda —, e acrescentar ao cartão a região `role="status"` com as três frases do contrato e `autofocus` no primeiro campo editável quando o cartão vier da duplicação (`FR-637`, `FR-645`, `FR-650`, `R-009`). A Retificação desenha `_retificacao_perfil.html`, e não este: conferido em 25/09
- [X] T041 [US1] Fazer o cartão acrescentado por *Acrescentar Perfil* oferecer *Duplicar* também: o botão de `backend/processo_seletivo/interface/templates/interface/compor_perfis.html` passa `?edital=<id>` a `fragmento-perfil`, e `fragmento_perfil` em `backend/processo_seletivo/interface/views.py` resolve o Edital por `_edital_do_fragmento` e entrega `edital` e `editavel = pode_compor(edital, ator)` ao cartão; sem `edital`, o cartão nasce sem o diálogo, como hoje. `fragmento_perfil_duplicado` entrega o mesmo par, para que a cópia seja duplicável (cenário 7). Teste em `backend/tests/interface/test_duplicar_perfil.py`: o cartão novo traz o diálogo, e o de ator sem permissão não

**Checkpoint**: a `US1` entra em produção sozinha. É o MVP — e é a feature inteira.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T042 [P] Acessibilidade em `backend/tests/interface/test_acessibilidade.py` (ou o arquivo de acessibilidade da composição que já cobre `_perfil.html`): os dois campos do diálogo têm rótulo, a mensagem de erro é associada ao campo, a região de anúncio é `role="status"`, e o botão é `type="button"` — confirmando que o parcial novo é alcançado pela resolução de `include` do guardião (`FR-637`)
- [X] T043 [P] Conferir que `backend/tests/test_vocabulario_da_composicao.py` alcança `_duplicar_perfil.html` pela resolução de `include` a partir de `compor_perfis.html`; se não alcançar, acrescentá-lo à lista **no mesmo commit** — a lista é literal, e a tela escapa em silêncio (`T-6`)
- [X] T044 [P] Conferir que os campos do diálogo **não** entram no rascunho local nem na gravação da etapa: um POST de gravação da etapa não traz `duplicar-*`, e `static/interface/rascunho.js` não os lê, por estarem fora de `form.elements` (`R-007`). **Não** em `backend/tests/javascript/rascunho.test.js`: o shim `dom.js` monta `form.elements` com todos os filhos da linha e não modela o atributo `form` — o teste provaria o shim. A marcação que produz a exclusão é presa em `backend/tests/interface/test_duplicar_perfil.py`, e a exclusão pelo navegador é conferida na demonstração (T046)
- [X] T045 Escrever `specs/043-duplicar-perfil/rastreabilidade.md` cobrindo **cada** `FR-634` a `FR-650` e `SC-230` a `SC-236` com o teste ou o passo de demonstração que o prende, e **uma linha por caso-limite** da spec — eles não têm identificador, e nenhuma ferramenta os cobra
- [X] T046 Percorrer pela interface a demonstração do [quickstart.md](./quickstart.md) §3, com o papel de quem elabora, até o documento publicado (`SC-235`). O foco e o anúncio de `FR-637` são verificados **aqui**, com teclado, e não por teste automatizado — seria testar o htmx, não o produto
- [X] T047 Medir pelo [quickstart.md](./quickstart.md) §4 a etapa Perfis do conteúdo do 140/2025, com datas futuras, e registrar a contagem por Perfil em `specs/043-duplicar-perfil/rastreabilidade.md` — critério: total ≤ 150 e média por cópia ≤ 8 (`SC-230`, `SC-231`); a economia na Classificação é relatada à parte (`R-011`)
- [X] T048 Rodar `cd backend && make lint check test-pg DB_NAME=ps_043` — `ruff check` **e** `ruff format --check` —, e `uv run pytest tests/test_citacoes_de_requisito.py` antes de empurrar: a matriz de rastreabilidade é cobrada requisito a requisito

---

## Dependencies & Execution Order

```text
Phase 1 (Setup)
   │
Phase 2 (Foundational)
   ├── T003–T012 testes da transformação ──► T013 ► T014
   └── T015–T017 testes de travessia ─────► T018 ► T019 ► T020 ► T021
   │
Phase 3 (US1)
   ├── T022–T034 testes ──► T035 ► T036 ► T037 ► T038
   └──────────────────────► T039 ► T040 ► T041
   │
Phase 4 (Polish) — T042–T044 em paralelo; T045 ► T046 ► T047 ► T048
```

- **T013 depende de T002**: se a cobrança da lista fechada de `remapear` não existir como `R-001`
  supõe, a decisão de reuso volta para o plano antes de haver código.
- **T036 depende de T014 e T018**: o fragmento chama `duplicar_perfil` e o cartão que ele devolve só
  grava com marcos se o transporte já existir.
- **T040 depende de T039**: o cartão inclui o diálogo; **T041 depende de T040 e T036**: o cartão
  acrescentado e a cópia só oferecem o diálogo se ele existir no cartão.
- **T047 depende de T046**: medir sobre uma jornada que ainda não fecha de ponta a ponta mediria o
  atrito errado.

### Parallel Opportunities

- **Fase 2**: T003–T012 são casos do mesmo arquivo novo, escritos juntos; T015–T017 noutro arquivo,
  em paralelo com eles.
- **Fase 3**: T022 (autorização) e T023–T034 (interface) em arquivos distintos, em paralelo.
- **Fase 4**: T042, T043 e T044 tocam arquivos distintos.

### Parallel Example: User Story 1

```text
Em paralelo:
  T022 backend/tests/authorization/test_duplicar_perfil.py
  T023–T034 backend/tests/interface/test_duplicar_perfil.py
Depois, em série: T035 → T036 → T037 → T038, e T039 → T040 → T041.
```

---

## Implementation Strategy

**MVP = a feature inteira.** Uma história, e ela não se parte: sem o transporte dos marcos a cópia
grava incompleta, e sem o diálogo não há jornada.

1. **Fase 2 primeiro, e com os testes vermelhos antes do código.** A transformação é pura: prova-se
   em segundos, sem banco. Se ela passar, o resto é transporte e tela.
2. **O teste de recusa (T016) antes de qualquer tela.** É o único ponto em que a cópia perde dado sem
   que nada acuse.
3. **Fase 3** contra o [contrato](./contracts/duplicar-perfil.md), com a autorização testada antes
   da view existir.
4. **Fase 4 fecha com a medição.** `SC-230` e `SC-231` são o motivo da feature; sem a contagem, ela
   não está concluída.

**Commits**: um por fase, no mínimo; o template e a lista de vocabulário no **mesmo** commit (`T043`);
a matriz de rastreabilidade antes do push.
