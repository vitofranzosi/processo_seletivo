---

description: "Task list for 033 — Navegação por capacidade"
---

# Tasks: Navegação por capacidade

**Input**: Design documents from `specs/033-navegacao-por-capacidade/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: obrigatórios. O Princípio V manda que todo requisito seja rastreável a teste. Aqui há uma
exigência a mais: **todo teste alterado entra na matriz de rastreabilidade com o motivo da
alteração** — é o que separa "corrigir a gramática" de "afrouxar autorização".

**Organization**: por história, na ordem de risco crescente que o plano propõe.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo — arquivo diferente, sem dependência pendente
- **[Story]**: US1, US2, US3, conforme `spec.md`
- Caminhos relativos a `backend/`

---

## ⚠️ O que torna esta feature diferente das outras

**Ela altera testes que passam hoje.** `tests/authorization/` tem **197 casos** e afirma **duas**
doutrinas contraditórias em arquivos vizinhos. Corrigir a gramática obriga a mexer em asserções de
autorização — que é exatamente a forma que tem afrouxar segurança por engano.

A regra é uma só, e vale para toda tarefa abaixo:

| Permitido | Proibido |
|---|---|
| trocar o **status esperado** de `404` para `403` | mudar a asserção de **quem** entra |
| renomear caso cujo nome descreve a resposta antiga | remover caso |
| acrescentar caso novo | afrouxar asserção existente |

**Um caso que passe a esperar sucesso onde esperava recusa derruba a feature, não o teste.**

E a armadilha de sempre deste repositório: toda tarefa diz se o arquivo é **novo** ou **existente**.
Onde diz existente, **acrescente ao fim e não reescreva o topo** — a `030` sobrescreveu
`test_round_trip_do_rascunho.py` e oito regressões sumiram sem a suíte ficar vermelha.

---

## Phase 1: Setup e a medida do "antes"

**Purpose**: sem esta fase, `SC-168` não é verificável e a revisão dirigida não tem contra o que
comparar. **Não é formalidade.**

- [x] T001 Rodar `uv sync --extra dev` em `backend/` e preparar um banco próprio desta worktree com `make preparar DB_NAME=<próprio> POSTGRES_DB=<o mesmo>`, conferindo que a saída termina em `N de M` com `N` diferente de zero
- [x] T002 Registrar em `/tmp/033-autorizacao-antes.txt` a lista de casos de `backend/tests/authorization/` — arquivo, nome do caso e status esperado em cada asserção de recusa. São **197 casos** em 38 arquivos, e este arquivo é o "antes" do cenário 4 do quickstart
- [x] T003 [P] Inventariar em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md` os **75** pontos de `processo_seletivo/interface/views.py` que respondem "não encontrado", classificando cada um como **objeto inexistente**, **escopo institucional** ou **recusa de autorização**, e dizendo, para cada um, se a função em que ele mora **recebe o ator** — a que não recebe não é porta, e `_ato_para_publicar` é o exemplo. Os dois primeiros ficam como estão; o terceiro é a superfície desta feature. **Não parta de nenhuma repartição prévia**: nem "4 e 71", nem "5 e 70" — duas tentativas de estimar esse número já erraram, e é esta tarefa que o conta
- [x] T004 **Parada de escopo — ela disparou.** O enunciado era: **Parada de escopo, obrigatória, logo depois do inventário e antes da fase 2.** Comparar o que T003 encontrou com a superfície que `spec.md` e `plan.md` descrevem. Se houver recusa de autorização fora das portas já identificadas, **pare**: reveja spec, plan e tasks com quem governa o backlog e rode o `analyze` de novo antes de escrever qualquer teste. Crescer a feature em silêncio é o que a `FR-483` existe para impedir, e a implementação começa em T013 — não em T029

  **O que ela encontrou, e o que foi decidido.** O inventário classificou **onze** recusas de autorização em `interface/views.py`, das quais **sete** ficam fora das quatro portas descritas: `criar_edital`, `anexo_do_rascunho`, `reaproveitar`, `supervisao`, `minha_etapa` e as duas telas da Mesa. A decisão de quem governa o backlog, em 2026-09-18, foi **manter o escopo nas quatro e registrar as sete** — cada uma justifica o 404 no próprio comentário, três citam doutrina de spec anterior por identificador, e três misturam escopo e vínculo na mesma resposta, que é trabalho da natureza da `FR-488` e de spec própria. Em consequência: a `SC-165` passa a se recortar às portas desta feature, a `T030` fecha sem código, e o `analyze` roda de novo sobre os três artefatos antes da fase 2

**Checkpoint**: o "antes" está registrado, e a superfície real da feature está nomeada linha a linha

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: as garantias que valem para as três histórias. Elas precisam existir como rede **antes**
da primeira mudança de comportamento, senão a primeira mudança as quebra em silêncio.

**⚠️ CRITICAL**: nenhuma história começa antes desta fase

- [x] T005 Criar o **arquivo novo** `tests/authorization/test_gramatica_da_recusa.py` prendendo `FR-480` e `FR-487`: Edital de outro escopo institucional responde "não encontrado" **mesmo quando o ator tem a capacidade exigida pela tela**, porque a consulta que o busca filtra por escopo e torna objeto de outra unidade indistinguível de objeto inexistente. É o caso que pega quem remover o filtro da consulta — e nenhum teste de status sozinho o pega
- [x] T006 Acrescentar ao mesmo arquivo o caso de `FR-482`: a URL montada à mão, sem passar pela tela, recebe **a mesma recusa** que a tela daria — retirar o link não é a proteção
- [x] T007 [P] Acrescentar ao **arquivo existente** `tests/authorization/test_publicacao_de_resultado.py` o caso que prende a fronteira do canal: uma recusa no portal do candidato continua **404 uniforme**. O arquivo já registra essa doutrina no docstring; o caso a torna falsificável

**Checkpoint**: as três redes existem e passam sobre o código de hoje

---

## Phase 3: User Story 1 — O Publicador puro chega à divulgação (Priority: P1) 🎯 MVP

**Goal**: `FR-473` a `FR-477`. A tela do Edital passa a oferecer os destinos que **cada ator**
alcança, e a divulgação deixa de ser alcançável só por URL montada à mão.

**Independent Test**: entrar como Publicador puro, sem vínculo de comissão, abrir a tela de um Edital
com ato emitido e chegar à divulgação com **zero URLs digitadas**.

### Tests for User Story 1

- [ ] T008 [P] [US1] Criar o **arquivo novo** `tests/interface/test_destinos_do_edital.py` com o caso de `FR-474` e `SC-164`: ator com a capacidade de publicar resultado e **sem vínculo nenhum** vê, na tela do Edital, o caminho até a divulgação de cada ato emitido
- [ ] T009 [US1] Acrescentar ao mesmo arquivo o caso de `FR-475`, que é a contraprova que mais importa: a presidência **sem** a capacidade de publicar continua vendo **todos** os destinos que vê hoje — nenhum a menos. Monte a lista esperada a partir do comportamento atual, e não da intenção
- [ ] T010 [US1] Acrescentar ao mesmo arquivo os três casos de `FR-473` e `FR-476`: quem preside **e** publica vê a união, **sem destino repetido**; quem não alcança nada não vê o bloco; e quem **julga recursos** continua não vendo — é o defeito que o código já corrigiu, e regredi-lo seria trocar um achado por outro
- [ ] T011 [US1] Acrescentar ao mesmo arquivo as **duas** ausências que não são recusa: marco **sem ato emitido** não oferece divulgação ao Publicador, e **Edital ainda não publicado** não mostra o bloco para ator nenhum. Oferecer caminho que termina em nada é o mesmo defeito com outra roupa; e ausência de bloco não é negativa, é ausência
- [ ] T012 [P] [US1] Acrescentar ao **arquivo existente** `tests/interface/test_publicar_resultado.py` dois casos: o de ponta a ponta — o Publicador puro segue o caminho oferecido e **a tela de divulgação abre**, sem recusa, porque a capacidade dele sempre bastou —, e o de `FR-477`: a tela de ordenação, lida pela presidência, declara **de quem é o ato** de divulgar, e não apenas onde ele mora. O segundo mora aqui, e não em US3, porque **o teste vem antes da implementação**, e quem implementa `FR-477` é T016

### Implementation for User Story 1

- [ ] T013 [US1] Reescrever `processo_seletivo/interface/views.py::_marcos_publicados` para derivar **por destino**, e não por porta: cada item passa a carregar para onde leva, e entra se — e só se — o ator alcança aquele destino. O docstring MUST preservar o princípio que ele já declara e registrar por que a derivação por porta única era estreita
- [ ] T014 [US1] Acrescentar o destino de divulgação à derivação, em `processo_seletivo/interface/views.py`, condicionado à capacidade de publicar resultado **e** à existência de ato emitido
- [ ] T015 [US1] Ajustar o bloco de marcos em `processo_seletivo/interface/templates/interface/detalhe.html` para renderizar os destinos que a derivação entregou, sem reintroduzir condição de capacidade no template — a decisão é da view, e duplicá-la criaria duas verdades
- [ ] T016 [US1] Reescrever, em `processo_seletivo/interface/templates/interface/ordenacao.html`, as três frases que mandam o operador a "Consultar ato e proveniência" (`FR-477`), dizendo **de quem é o ato** e não apenas onde ele mora

**Checkpoint**: US1 funciona sozinha. O `ACH-40` fecha, e a segregação de papéis passa a ser executável.

---

## Phase 4: User Story 3 — Quem trava sabe a quem pedir (Priority: P3)

**Goal**: `FR-484` a `FR-486`. O beco vira instrução.

**Independent Test**: entrar como presidência sem a capacidade de publicar, abrir a tela do ato de
classificação e ler o que hoje é *"Você não tem ação disponível sobre este ato"*.

> **Vem antes de US2 de propósito.** É a de menor risco das três, e não depende da gramática da
> recusa: trata da tela que **abre** e não oferece ação, e não da tela que recusa.

### Tests for User Story 3

- [ ] T017 [US3] Acrescentar ao **arquivo existente** `tests/interface/test_publicar_resultado.py` o caso de `FR-484`: na tela do ato, o ator sem ação disponível lê a capacidade que resolve e a instrução de pedir a quem a detém
- [ ] T018 [US3] Acrescentar ao mesmo arquivo a contraprova de `FR-485`: quando o que falta é **vínculo**, a frase nomeia a **presidência daquele Processo** e **não** manda pedir um papel — nenhum papel concede presidência, e mandar pedir o que não resolve é o defeito

### Implementation for User Story 3

- [ ] T019 [US3] Reescrever a frase de `processo_seletivo/interface/templates/interface/ato_ordenacao.html`, hoje *"Você não tem ação disponível sobre este ato."*, seguindo a formulação que `detalhe.html` já pratica em *"Peça a alguém com a permissão de publicar que conclua o ato"* (`FR-486`)
- [ ] T020 [US3] Levar à tela o que falta, a partir da base de autorização que a view já consultou, em `processo_seletivo/interface/views.py` — uma leitura só, nunca uma segunda

**Checkpoint**: US1 e US3 funcionam, cada uma por si. Nenhuma porta foi tocada ainda.

---

## Phase 5: User Story 2 — A recusa se explica (Priority: P2)

**Goal**: `FR-478` a `FR-483`, `FR-487` e `FR-488`. A **base de autorização composta** ganha o
tratamento que a capacidade nomeada já tem, num ponto único — e as quatro portas que improvisaram
passam a usá-lo.

**Independent Test**: entrar como Publicador puro e abrir a tela de **distribuição** do mesmo Edital,
cuja porta é `_etapa_para_distribuir`. Hoje responde "não encontrado"; deve responder recusa
explicada.

> **Por último de propósito**, e com ordem interna que a medição impôs: o ponto único primeiro, a
> separação de escopo e vínculo depois, e só então as portas. Inverter os dois últimos responderia
> recusa explicada para Edital de outra unidade.

### Tests for User Story 2

- [ ] T021 [US2] Acrescentar a `tests/authorization/test_gramatica_da_recusa.py` os casos de `FR-478` e `FR-479`, **nas quatro portas que erram** — a do marco, a da consulta de Etapa, a da gestão do Processo e a da distribuição: ator que não satisfaz **nenhuma** das bases aceitas recebe recusa explicada, e não "não encontrado". Inclua a porta do marco com ator que tem **só** `auditoria:consultar` negada: lá a recusa é por capacidade pura e hoje também responde "não encontrado"
- [ ] T022 [US2] Acrescentar ao mesmo arquivo os casos de `FR-481` e `FR-489`: a recusa **nomeia as bases que teriam servido** — a permissão de gerir a comissão **e** a presidência daquele Processo, quando as duas serviriam — e declara que nada foi alterado. E os **dois** pares que prendem `FR-489`, um em cada porta com modo: em `_edital_para_classificar`, uma chamada padrão e outra com `somente_gestao=True`; em `_edital_para_publicar`, uma com `consulta=True` e outra sem. Nos dois casos as frases têm de ser **diferentes** — se forem iguais, o conjunto de bases virou constante e a recusa mente numa das chamadas
- [ ] T023 [US2] Acrescentar ao mesmo arquivo o caso de `FR-488`, que é o que impede o vazamento na porta travada: na **distribuição**, ator de outro escopo institucional continua recebendo "não encontrado" **depois** da mudança, enquanto ator do mesmo escopo sem vínculo passa a receber recusa explicada. Hoje as duas condições compartilham um `if`, e este caso é o que prova que foram separadas
- [ ] T024 [US2] Alterar, no **arquivo existente** `tests/authorization/test_distribuicao.py`, os casos `test_quem_apenas_atua_na_etapa_nao_distribui`, `test_quem_nao_tem_vinculo_nenhum_recebe_inexistente` e `test_a_distribuicao_por_post_tambem_e_recusada`: **só o status esperado** muda, de `404` para `403`. A asserção de que aquele ator **não entra** fica idêntica. Renomeie o segundo, cujo nome afirma a doutrina antiga
- [ ] T025 [US2] Conferir, um a um, os demais casos de `tests/authorization/` que esperam `404` por recusa de autorização, usando `/tmp/033-autorizacao-antes.txt` de T002, e alterar **apenas** os que a mudança de fato alcança — deixando registrado, na matriz, cada um que mudou e por quê
- [ ] T026 [US2] Acrescentar ao **arquivo existente** `tests/authorization/test_distribuicao.py` o caso que `FR-480` exige e que o arquivo já tem em `test_escopo_institucional_divergente_e_inexistente`: conferir que ele **continua** `404` depois da mudança, e não o alterar

### Implementation for User Story 2

- [ ] T027 [US2] Criar o **ponto único de recusa por base de autorização** em `processo_seletivo/seguranca/application/authorization.py`, ao lado de `require_permission` e com a mesma forma: recusa explicada com status 403, nomeando **as bases que teriam servido** — e não apenas uma. **O conjunto de bases é parâmetro, e não constante da porta** (`FR-479`, `FR-489`): `_edital_para_classificar` tem dois modos, e com `somente_gestao=True` — ao menos **seis** chamadas — a capacidade de auditoria **não** serve. Uma função que assuma conjunto fixo nasce mentindo em metade dos casos. A peça-espelho já existe: `pode_gerir_comissao` devolve uma `Base` que nomeia o que autorizou. **Mora na camada de segurança, e não em `interface`** — foi a ausência desse ponto que produziu quatro improvisos idênticos, e criá-lo em `interface` produziria o quinto
- [ ] T028 [US2] **Separar escopo de base** em `processo_seletivo/interface/views.py::_etapa_para_distribuir`, hoje `if edital is None or pode_gerir_comissao(...) is None: raise Http404` (`FR-488`). São duas condições e duas respostas; enquanto compartilharem um `if`, mudar o status vaza a existência de Editais de outra unidade. **Esta tarefa vem antes de T029**
- [ ] T029 [US2] Fazer as **quatro portas erradas** consumirem o ponto único de T027, em `processo_seletivo/interface/views.py`: `_edital_para_classificar`, `_etapa_para_auditar`, `_processo_para_gerir` e `_etapa_para_distribuir`. Cada docstring MUST deixar de afirmar *"tudo que o ator não alcança responde 404"* e passar a citar a doutrina única. **As duas portas já corretas — a da divulgação e a do recurso — não são tocadas**
- [ ] T030 [US2] **Fecha sem código, pela decisão de T004.** O inventário classificou **sete** recusas de autorização fora das quatro portas — `criar_edital`, `anexo_do_rascunho`, `reaproveitar`, `supervisao`, `minha_etapa` e as duas telas da Mesa. A decisão de governança de 2026-09-18 foi **mantê-las fora**: cada uma justifica o 404 no próprio comentário, três citam doutrina de spec anterior por identificador, e três misturam escopo e vínculo na mesma resposta — separá-las é trabalho da natureza da `FR-488`, e de spec própria. O que esta tarefa entrega é o **registro**: as sete nomeadas no inventário, e a `SC-165` recortada às portas desta feature, como a `FR-476` já se recortava
- [ ] T031 [US2] Enriquecer o `detail` da recusa em `processo_seletivo/interface/views.py::_edital_para_publicar`, hoje *"A operação não é permitida."*, para nomear o que falta (`FR-481`) — **recebendo o conjunto de quem chama**, como T027 (`FR-489`). Esta porta **também tem modo**: com `consulta=True` a capacidade de auditoria serve, sem ele não serve. O status dela já está certo desde sempre e a mensagem genérica de hoje nunca mente porque não nomeia nada — **é justamente ao nomear que ela passa a poder mentir**. A única porta que não precisava de conserto é a que esta tarefa pode quebrar

**Checkpoint**: as três histórias funcionam, e nenhum ator passou a alcançar o que não alcançava.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T032 **O cenário 4 do quickstart, lido caso a caso.** Comparar `tests/authorization/` com `/tmp/033-autorizacao-antes.txt` de T002: zero casos removidos, zero casos que passaram a esperar sucesso onde esperavam recusa, e toda asserção sobre **quem** entra intacta. **Não conferir pela contagem** — um caso pode manter o número de asserções e trocar o ator, e a suíte fica verde
- [ ] T033 Escrever `specs/033-navegacao-por-capacidade/rastreabilidade.md` com uma linha por `FR-` e por `SC-` — e, além disso, uma linha por **teste alterado**, com o motivo. É o que separa correção de gramática de afrouxamento de autorização
- [ ] T034 [P] Conferir o implementado contra `contracts/gramatica-da-recusa.md` e `contracts/destinos-da-tela-do-edital.md`, corrigindo **o artefato** quando o código estiver certo e o contrato errado, e dizendo qual dos dois mudou
- [ ] T035 Percorrer os cenários 1 a 3 de `quickstart.md` pela interface administrativa, com o seletor de identidade, medindo `SC-167`: nenhum dos seis papéis vê caminho que não abre, e nenhum deixa de ver um que abria
- [ ] T036 Rodar `make lint check test-pg` em `backend/` e registrar em `rastreabilidade.md` a contagem final — `lint` são dois passos, `ruff check` **e** `ruff format --check`
- [ ] T037 Criar o **arquivo novo** `tests/test_gramatica_das_portas.py` afirmando, para cada porta de autorização registrada, a taxonomia do contrato: escopo institucional responde "não encontrado"; capacidade e vínculo respondem recusa explicada; e toda recusa nomeia o que falta (`SC-165`, `SC-166`, `FR-481`)
- [ ] T038 Acrescentar ao mesmo arquivo o **detector de novidade**, que é o que faltava para o critério valer amanhã: ancorado no inventário de T003, ele falha quando aparece em `processo_seletivo/interface/views.py` um ponto de "não encontrado" que **não está registrado** — obrigando quem o escreveu a classificá-lo. **Não copie a forma de `tests/test_vocabulario_da_composicao.py`**: aquele teste usa lista literal e diz por quê no próprio comentário — *"uma lista calculada passaria a ignorar a tela que deixasse de usar o termo"* —, e para o problema dele isso está certo. Aqui é o inverso: o que precisa ser detectado é a porta que **aparece depois**, e lista literal nunca a vê. O custo é real e é o ponto: todo `raise Http404` novo passa a exigir uma linha no inventário
- [ ] T039 Acrescentar ao mesmo arquivo a asserção de `FR-486`, que as duas anteriores **não** cobrem: todas as mensagens desta família usam a **formulação canônica** — a mesma que `detalhe.html` já pratica —, e não uma segunda redação para a mesma coisa. Verificar a taxonomia e verificar a formulação são coisas diferentes, e só a segunda fecha a `FR-486`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências. **T002 e T003 bloqueiam tudo o que vem depois** — sem o "antes", `SC-168` não se verifica e a superfície da feature não está medida
- **T004 é portão, não tarefa.** Nenhuma tarefa da fase 2 em diante começa antes de ela concluir. Se o inventário mudar o escopo, o ciclo volta para spec/plan/tasks e roda o `analyze` de novo
- **Foundational (Phase 2)**: depende da Phase 1 inteira — bloqueia as três histórias
- **US1 (Phase 3)** e **US3 (Phase 4)**: independentes entre si
- **US2 (Phase 5)**: independente das outras duas em arquivo, deliberadamente última em ordem, e com **ordem interna obrigatória** — T027 (o ponto único) → T028 (separar escopo de base na porta travada) → T029 (as quatro portas passam a consumi-lo). Inverter T028 e T029 responderia recusa explicada para Edital de outra unidade
- **Polish (Phase 6)**: depende do que for entregue; **T032 é obrigatória se US2 entrar**, e **T038 só é escrevível depois de T003**, porque é o inventário que lhe dá a âncora

### Conflitos reais de arquivo — e o que `[P]` significa aqui

`[P]` é **arquivo diferente e sem dependência pendente**. Acrescentar a um arquivo que outra tarefa
da mesma fase cria ou edita **não** é paralelo, por mais que as duas tarefas sejam independentes em
conteúdo. As tarefas abaixo são sequenciais dentro de cada linha.

| Arquivo | Ordem obrigatória | Consequência |
|---|---|---|
| `interface/views.py` | T013 → T014 (US1) → T020 (US3) → **T028 → T029** → T030 → T031 (US2) | cada história mexe em função própria; a leitura da base de autorização é compartilhada entre T020 e T029. **T028 antes de T029 não é preferência: é o que impede o vazamento** |
| `tests/authorization/test_gramatica_da_recusa.py` | T005 cria → T006 → T021 → T022 → T023 | nenhuma delas é `[P]` entre si |
| `tests/interface/test_destinos_do_edital.py` | T008 cria → T009 → T010 → T011 | idem |
| `tests/interface/test_publicar_resultado.py` | T012 (US1) → T017 → T018 (US3) | arquivo existente de 339 linhas; acrescentar ao fim, em ordem |
| `tests/authorization/test_distribuicao.py` | T024 → T026 (US2) | arquivo existente de 85 linhas; T024 **altera** casos, T026 confere que um **não** mudou |
| `tests/test_gramatica_das_portas.py` | T037 cria → T038 → T039 | idem |
| `seguranca/application/authorization.py` | T027 (US2), sozinha | o ponto único de recusa por base composta; **nenhuma porta o consome antes de T029** |

**As que sobram como `[P]` são só estas**, e cada uma está num arquivo que mais ninguém toca na mesma
fase: T003, T007, T008, T012 e T034.

### Within Each User Story

- Testes primeiro, e **falhando**, antes de qualquer implementação
- View antes de template: a decisão é da view, e duplicá-la no template criaria duas verdades
- Em US2, a ordem de avaliação — escopo, depois capacidade e vínculo — é a primeira linha da porta

---

## Parallel Example: User Story 1

```bash
# T009, T010 e T011 acrescentam ao arquivo que T008 cria: dependem dele.
# O que roda junto é T008 com T012, que são arquivos diferentes:
Task: "T008 o Publicador puro vê a divulgação em tests/interface/test_destinos_do_edital.py"
Task: "T012 o caminho oferecido abre a tela em tests/interface/test_publicar_resultado.py"
```

---

## Implementation Strategy

### MVP First (US1)

1. Phase 1 e Phase 2 — o "antes" e as três redes
2. Phase 3 — US1
3. **PARE e VALIDE**: cenário 1 do quickstart, nos dois sentidos — o Publicador ganha caminho, e a presidência não perde nenhum
4. US1 sozinha fecha o `ACH-40`, que é o `P0` desta família, **sem tocar em nenhuma porta de autorização**

### Incremental Delivery

1. Setup + Foundational → rede de proteção de pé
2. US1 → `ACH-40` fechado → validar → demonstrar
3. US3 → `ACH-38` fechado → validar
4. US2 → `ACH-35` fechado → **validar com T032, caso a caso**

---

## Notes

- `[P]` = arquivos diferentes, sem dependência pendente
- Commitar a cada tarefa ou grupo lógico; **não** editar arquivo do projeto enquanto `test-pg` roda
- Todo arquivo marcado **existente** é para acrescentar, nunca para reescrever
- Nenhuma tarefa cria capacidade, papel ou migration. Se a necessidade aparecer, **pare e pergunte**:
  é sinal de que o escopo escorregou para o que a `FR-483` proíbe
