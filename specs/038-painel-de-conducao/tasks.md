---

description: "Task list — 038 · Painel de condução do Processo vivo"
---

# Tasks: Painel de condução do Processo vivo

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim.** A feature acrescenta quatro espécies a um catálogo cercado por **34 casos**, e
três delas leem números que outra espécie já lê. Requisito sem linha na matriz é requisito que
ninguém sabe se entrou.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: arquivos diferentes, nenhuma dependência aberta. **Ganhou arquivo depois, o `[P]` sai.**
- **NOVO / EXISTENTE**: onde diz existente, **acrescente ao fim; nunca reescreva**. São **34 casos**
  cercando a Supervisão em quatro arquivos que já existem.

---

## Os quatro portões

1. **`T002` roda ANTES de qualquer edição**, e tem **dois** alvos: a contagem da suíte **e o número
   do orçamento de consulta** de
   `tests/integration/supervisao/test_sinais.py::test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas`.
   A quarta espécie acrescenta uma consulta, e o número precisa ser **remedido com justificativa**,
   nunca ajustado até passar.

2. **Esta feature NÃO tem migration.** O total do `make preparar` continua **`N de 33`**. **32** é
   worktree atrás da `main`; **31**, muito atrás. *O portão só serve se distinguir desatualização de
   defeito.*

3. **`T014` decide se a `US2b` existe.** A quarta espécie exige extrair de `interface/views.py` uma
   derivação privada, e a `037` está alterando esse arquivo. **Duas saídas nomeadas**, e uma delas
   não executa a fase.

4. **`T020` reconta os casos alterados, caso a caso.** A `034` previu oito e entregou doze.

---

## Phase 1: Setup e medição do "antes"

- [ ] T001 Preparar a worktree: copiar `backend/.env` do checkout principal (**EXISTENTE lá, ausente aqui** — é gitignorado), trocar `DB_NAME` e `POSTGRES_DB` por nome próprio, rodar `uv sync --extra dev` e `make preparar` em `backend/`, conferindo **`N de 33`** com N diferente de zero
- [ ] T002 Medir e gravar o "antes" em `specs/038-painel-de-conducao/antes-do-painel.md` (**NOVO**): a contagem da suíte (`make test-pg`); **o número do orçamento** do teste nomeado no portão 1; e a contagem dos quatro arquivos que cercam a Supervisão — `tests/interface/test_supervisao.py` (15), `tests/integration/supervisao/test_sinais.py` (13), `test_fronteira.py` (5), `tests/acceptance/test_supervisao_do_processo.py` (1). **Antes de qualquer edição**
- [ ] T003 Confirmar por varredura, em `specs/038-painel-de-conducao/antes-do-painel.md` (**EXISTENTE**, criado em T002), as quatro premissas: a **condição** do `UX-005` é a comissão inteira impedida; o `UX-003` mede **cobertura**; `ESPECIES` tem **seis** e a `FR-024` da `022` diz **cinco**; e a derivação de *ato sem divulgação* vive **só** em `interface/views.py`. **Leia a condição, não a mensagem** — foi lendo mensagem que a spec errou duas premissas

**Checkpoint**: o "antes" está gravado com o orçamento, e as quatro premissas conferidas.

---

## Phase 2: Foundational — **não existe**

Não há entidade a criar, esquema a preparar nem mecanismo que anteceda as histórias. **Inventar uma
fase 2 aqui seria fabricar bloqueio.**

---

## Phase 3: US2a — As três espécies que saem de leitura existente (P2) 🎯 **primeiro entregável**

**Goal**: a Atenção alcança avaliação parada, recurso com julgador e recorte sem ocupação.

**Por que esta fase vem antes da `US1`, embora tenha prioridade menor**: ela vive inteira em
`interface/supervisao.py`, que a `037` **não toca**. A `US1` e a `US2b` mexem em
`interface/views.py`, que ela está alterando. **É ordem de integração, não de valor.**

**Independent Test**: deixar trabalho parado em cada um dos três estados e ver três sinais com
destino que resolve.

- [ ] T004 [US2a] Acrescentar a espécie de **avaliação parada** (`UX-063`) em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE** — acrescente ao fim do bloco de espécies), `FR-560`. Leia `completas − avaliadas` de `resumo_da_etapa`, que o `UX-003` **já chama**: é segunda leitura do mesmo retorno, e **não** consulta nova (`FR-557`)
- [ ] T005 [US2a] Partir a condição do recurso em **dois desfechos, num ato só**, em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**, o mesmo arquivo de T004), `FR-561`. Todos os membros impedidos continua sendo o `UX-005`; **ao menos um livre** é a espécie nova (`UX-064`). **Os dois partem do mesmo cálculo** — `recursos_do_edital(AGUARDANDO_JULGAMENTO)` e `impedidos_por_recurso`, que o `UX-005` já chama. Implementados em lugares separados, uma mudança na regra de impedimento moveria um e não o outro
- [ ] T006 [US2a] Acrescentar a espécie de **recorte com ordem e sem ocupação** (`UX-065`) em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**), `FR-563`: `ato_vigente` não nulo **e** `apuracao_vigente` nulo. **Atenção ao custo, que é real**: a Supervisão já lê `ato_vigente` para o `UX-004`, mas **não importa nada de `ocupacao`** — esta é a única das três que **acrescenta consulta**, uma por recorte. Faça-a na forma que a `034` adotou, uma leitura por recorte e não visita por lista, e leve o número à `T021`
- [ ] T007 [US2a] Escrever as três mensagens e os três destinos em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**), conforme [contracts/as-quatro-especies.md](contracts/as-quatro-especies.md). **Nenhuma nomeia pessoa** (`FR-564`): o produto não liga identidade a papel, e o `UX-005` já registra a razão por escrito
- [ ] T008 [US2a] Prender as três em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE** — acrescente ao fim; os 13 casos permanecem): cada uma dispara no seu estado e some quando ele se resolve
- [ ] T009 [US2a] **CONTRAPROVA OBRIGATÓRIA — a fronteira com o `UX-003`**, em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE**, o mesmo de T008): Etapa **sem distribuição** dispara o `UX-003` e **não** a nova; Etapa **distribuída e parada** dispara a nova e **não** o `UX-003`. Se as duas dispararem pelo mesmo Edital e Etapa, **a condição da nova está frouxa**
- [ ] T010 [US2a] **CONTRAPROVA OBRIGATÓRIA — um fato, um sinal**, em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE**): a **mesma peça** com todos impedidos dá `UX-005` e **não** a nova; com um livre dá a nova e **não** o `UX-005`. **Nunca as duas**

**Checkpoint**: três dos quatro estados da cauda sinalizam, e a `037` não foi tocada.

---

## Phase 4: US1 — O Processo diz onde cada Edital está (P1)

**Goal**: o pulso e a Atenção aparecem na página do Processo, lidos e não recalculados.

**Depende da `037`** — `processo_detalhe` vive em `backend/processo_seletivo/interface/views.py`, que
ela está alterando. Integre a `main` antes.

**Independent Test**: abrir um Processo com Editais vivos e ler, por Edital, o que hoje só a
Supervisão mostra.

- [ ] T011 [US1] Levar pulso e sinais à página do Processo em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**, `processo_detalhe`), `FR-556` e `FR-557`. **Leia as mesmas funções que a Supervisão chama** — `pulso(processo)` e `sinais(processo, ator)` —, sem recalcular: duas telas com o mesmo número calculado duas vezes é a segunda verdade que a `FR-557` proíbe
- [ ] T012 [US1] Exibi-los em `backend/processo_seletivo/interface/templates/interface/processo_detalhe.html` (**EXISTENTE**), `FR-558` e `FR-559`: destino **só a quem o alcança**, e a ausência de todos os sinais em **uma linha declarada** — nunca seção vazia por espécie
- [ ] T013 [US1] Prender a `US1` em `backend/tests/interface/test_supervisao.py` (**EXISTENTE** — acrescente ao fim; os 15 casos permanecem): o Processo mostra o pulso e os sinais; **diz o mesmo que a Supervisão** sobre o mesmo Edital; não oferece destino a quem não o alcança; e a ausência é uma linha

**Checkpoint**: a página do Processo para de ser uma lista com dois atos terminais.

---

## Phase 5: US2b — A quarta espécie, por extração (P2)

- [ ] T014 [US2b] **DECIDE SE ESTA FASE EXISTE.** Confira se a `037` está na `main` — `git log --oneline -1` deve alcançá-la. **Duas saídas**: (a) **está** → siga para a `T015`; (b) **não está** → **registre em `specs/038-painel-de-conducao/antes-do-painel.md` (EXISTENTE) que a quarta espécie fica para depois, com a razão**, e a fase **não é executada**. É a `FR-567`: o que não está pronto fica registrado, não implementado às pressas
- [ ] T015 [US2b] **Extrair**, e nunca reescrever, a derivação de *ato vigente sem divulgação vigente* (`UX-066`) de `backend/processo_seletivo/interface/views.py` (**EXISTENTE**) para onde a Supervisão e a tela de destino a alcancem, `FR-557`. **Reescrevê-la no sinal criaria a segunda verdade** que este projeto passou a semana removendo. O que a tela já faz com ela **não muda**
- [ ] T016 [US2b] Acrescentar a espécie e prendê-la em `backend/processo_seletivo/interface/supervisao.py` (**EXISTENTE**) e `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE**), `FR-562`: ato emitido e não divulgado dispara, levando à publicação daquele resultado; divulgado, não dispara

**Checkpoint**: os quatro estados da cauda sinalizam — ou três, com o quarto registrado. **A `SC-198` é conferida contra o que foi decidido**, e não contra um número fixo.

---

## Phase 6: US3 — O catálogo volta a ser verdade (P3)

- [ ] T017 [US3] **Emendar a `FR-024`** em `specs/022-supervisao-do-processo/spec.md` (**EXISTENTE**), `FR-565`. **Substituir não é acrescentar**: hoje ela diz *"exclusivamente os sinais definidos em `UX-001` a `UX-005`"*, e o produto tem seis — a `027` acrescentou o `UX-046` sem revisá-la. A emenda nomeia as **dez** espécies vigentes — `UX-001` a `UX-005`, `UX-046`, e `UX-063` a `UX-066` desta feature — e **diz que substitui**. Se a `T014` apontou a saída (b), o `UX-066` **não** entra na emenda, e a razão fica escrita ali. É a lição que a `D-G2` registrou: decisão nova que não endereça a anterior deixa duas verdades no repositório
- [ ] T018 [US3] Prender a contagem em `backend/tests/acceptance/test_supervisao_do_processo.py` (**EXISTENTE** — acrescente; o caso que existe permanece): as espécies que o produto apresenta e as que o requisito nomeia são **a mesma lista** (`SC-200`)

---

## Phase 7: Polimento e conferência

- [ ] T019 Percorrer os **cinco cenários** de `specs/038-painel-de-conducao/quickstart.md` (**EXISTENTE**) pela interface — inclusive as **três contraprovas**. São o `SC-196`, o `SC-197`, o `SC-198` e o `SC-199`: o Processo conduz, diz o mesmo que a Supervisão, os quatro estados sinalizam, e **nenhuma mensagem nomeia pessoa**. Se a `T014` apontou a saída (b), o passo 2 do cenário 4 **não é percorrível**: registre, não contorne
- [ ] T020 Conferir **caso a caso** os testes alterados contra o "antes" de `specs/038-painel-de-conducao/antes-do-painel.md` (**EXISTENTE**), e **recontar**. Confira que os vizinhos permaneceram — 15, 13, 5 e 1
- [ ] T021 **Remedir o orçamento de consulta** em `backend/tests/integration/supervisao/test_sinais.py` (**EXISTENTE**, o caso que já existe): **duas** das três espécies da `US2a` — avaliação (`UX-063`) e recurso (`UX-064`) — **não podem acrescentar consulta**, porque leem retorno que outra espécie já busca. A do **recorte** (`UX-065`) acrescenta **uma por recorte**, e a quarta (`UX-066`) o que a extração trouxer. O número novo entra **com a justificativa escrita ao lado**, espécie por espécie. *Ajustar o número até passar é o modo de perder a guarda sem removê-la*
- [ ] T022 Escrever `specs/038-painel-de-conducao/rastreabilidade.md` (**NOVO**) — uma linha por `FR-`, uma por `SC-`, uma por teste alterado com o motivo, e **o que a `T014` decidiu** — e rodar `cd backend && make lint check test-pg`, registrando a contagem final. `test-pg` e **nunca** `test`; `lint` são **dois** passos. **Rode a suíte inteira**: a varredura deste repositório lê o comentário do template. As promessas que se conferem **lendo o diff** são as da `FR-566`: nenhuma capacidade de autorização nova, nenhuma ajuda instrucional nos cartões, nenhum conteúdo publicado reescrito, nada apagado

---

## Dependências

```
Phase 1 (T001–T003)
      │
      ├──► US2a (T004–T010)   🎯 primeiro entregável — só supervisao.py
      │
      ├──► US1  (T011–T013)   ← depende da 037 (views.py)
      │
      └──► US2b (T014–T016)   ← T014 decide se existe; depende da 037
                 │
                 └──► US3 (T017–T018) ──► Polimento (T019–T022)
```

**A ordem das fases não é a das prioridades, e a razão é de integração.** A `US1` é `P1` e entrega
mais valor; a `US2a` vem antes porque **não encosta no arquivo que a `037` está alterando**.

### Dentro das fases

- **T004 → T005 → T006 → T007** são o **mesmo arquivo**, e nenhuma leva `[P]`.
- **T005** é **um ato só**: partir a condição do `UX-005` em dois desfechos separadamente faz os dois
  sinais divergirem na primeira mudança da regra de impedimento.
- **T008 → T009 → T010** são o mesmo arquivo; as contraprovas vêm depois do caso simples.
- **T011 → T012** — a view lê, o template exibe.
- **T014 → T015 → T016** — a decisão, a extração, a espécie.
- **T017 → T018** — o requisito antes do teste que o confere.
- **T020 e T021 depois de todos os percursos**.

### Oportunidades de paralelismo

**Uma.** A `US2a` e a `US1` tocam arquivos diferentes — `supervisao.py` e `views.py` — e poderiam
correr juntas **se a `037` já tivesse entrado**. Enquanto ela não entra, a `US2a` corre sozinha.
Nenhuma tarefa leva `[P]`, porque dentro de cada fase há cadeia.

---

## Estratégia de entrega

**Primeiro entregável**: a `US2a`. Três dos quatro estados da cauda, sem esperar ninguém.

**Depois**: `US1` e `US2b`, quando a `037` entrar. **Se ela demorar**, a `US2a` mais a `US3` já
entregam valor e fecham a dívida do catálogo.

**O que não se faz**: implementar a quarta espécie reescrevendo a derivação em vez de extraí-la.
Seria mais rápido hoje e seria a segunda verdade amanhã.
