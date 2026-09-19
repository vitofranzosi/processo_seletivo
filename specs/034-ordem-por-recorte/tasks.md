---

description: "Task list — 034 · Ordem por recorte em marco computado"
---

# Tasks: Ordem por recorte em marco computado

**Input**: [spec.md](spec.md) · [plan.md](plan.md) · [research.md](research.md) ·
[data-model.md](data-model.md) · [contracts/](contracts/) · [quickstart.md](quickstart.md)

**Tests**: **sim, e são obrigatórios.** A feature cria atos imutáveis e altera **oito** casos que passam
hoje, em três arquivos. A rastreabilidade é verificada por teste neste projeto, e requisito sem linha na matriz é
requisito que ninguém sabe se entrou.

## Format: `[ID] [P?] [Story] Descrição — e o arquivo`

- **[P]**: pode correr em paralelo — **arquivos diferentes e nenhuma dependência de tarefa aberta**.
  Tarefa que **acrescenta** a um arquivo que outra **cria** não é paralela, por mais separadas que
  pareçam.
- **[US1] [US2] [US3]**: a história a que a tarefa pertence. As fases 1, 2 e a de polimento não têm.
- **NOVO / EXISTENTE**: toda tarefa diz o que o arquivo é. Onde diz **EXISTENTE**, acrescente ao fim
  — **nunca reescreva**. A `030` sobrescreveu `test_round_trip_do_rascunho.py` e oito regressões
  sumiram sem a suíte ficar vermelha.

---

## Os três portões

**Estes não são formalidade. Cada um existe porque o projeto já pagou por não tê-lo.**

1. **`T004` é PORTÃO DE ESCOPO, e agora é de reconfirmação.** O tamanho da feature está
   **ratificado** (`D-004`): a `034` alinha classificação e ocupação, e o sorteio fica fora, com a
   divergência registrada. O que a `T004` confere é que a **superfície não mudou** desde a medição —
   se o inventário de `T003` encontrar derivação ou recusa que ela não previu, o escopo reabre, e é
   conversa com quem governa o backlog. **A fase 2 não começa antes de ela fechar.**

2. **`T002` roda ANTES de qualquer alteração.** Ela grava o "antes" dos **oito** casos nomeados. Rodá-la
   depois torna a conferência da entrega impossível de refazer, e a conferência é caso a caso.
3. **`T045` é lida CASO A CASO, e nunca pela contagem.** Um teste pode manter o número de asserções e
   trocar o que afirma. Foi assim que a `033` quase deixou passar um conjunto aceito alargado de
   `403` para `(302, 403, 404)`.

---

## Phase 1: Setup e medição do "antes"

**Purpose**: deixar o ambiente de pé e congelar o estado contra o qual a entrega será conferida.

- [ ] T001 Preparar a worktree: copiar `backend/.env` do checkout principal (**EXISTENTE lá, ausente aqui** — é gitignorado), trocar `DB_NAME` e `POSTGRES_DB` por um nome próprio desta worktree, rodar `uv sync --extra dev` e `make preparar` em `backend/`, conferindo que a saída termina em `N de M` com **N diferente de zero**
- [ ] T002 Medir e gravar o "antes" em `specs/034-ordem-por-recorte/antes-da-ordem-por-recorte.md` (**NOVO**): a contagem da suíte (`make test-pg`); o **estado atual de cada um dos oito casos** que `research.md` `R-5` nomeia — mais a frase de `test_reversao.py`, que não é caso e muda do mesmo jeito —, com o que cada um afirma hoje, citado; **e o retrato do acervo**: por publicação, o resumo do conteúdo canônico, o do documento e o censo dos degraus de elevação. O retrato do acervo é a metade "antes" do cenário 4 do quickstart, e **só existe agora** — depois da primeira edição não há mais "antes" a gravar, e a prova de imutabilidade deixa de ser refazível. **Esta tarefa roda antes de qualquer edição de código**
- [ ] T003 Inventariar por varredura, em `specs/034-ordem-por-recorte/inventario-dos-recortes.md` (**NOVO**): (a) todo ponto que deriva conjunto de recortes, (b) todo ponto que fixa `lista_id` na classificação, (c) todo ponto que lê `generalCompetitionModalityId`. A classificação sai do `if` que decide, **não** da leitura da definição da função — foi o que produziu três medições erradas na `033`
- [ ] T004 **PORTÃO DE ESCOPO — reconfirmação, e não decisão.** O escopo já está **ratificado** (`D-004`, 18/09/2026): a `034` alinha classificação e ocupação, e o sorteio fica fora. O que esta tarefa faz é **conferir que a superfície não mudou** — comparar o inventário de `T003` com a medição de `research.md` `R-3`. **Se bater, siga.** Se o inventário encontrar derivação de recortes ou recusa de emissão que a medição não previu, **pare**: o escopo reabre, e é conversa com quem governa o backlog. Registre a conferência — **e o registro da divergência do sorteio que a `FR-491a` exige**, com o risco dos atos históricos da `021` nomeado — em `specs/034-ordem-por-recorte/inventario-dos-recortes.md` (**EXISTENTE**, criado em T003). **A fase 2 não começa antes desta tarefa fechar**

**Checkpoint**: o "antes" está gravado, a superfície está contada, e o tamanho da feature está
decidido por quem pode decidi-lo.

---

## Phase 2: Fundação — a derivação única e o cálculo por recorte

**Purpose**: o que toda história precisa. **Bloqueia US1, US2 e US3.**

- [ ] T005 Criar a derivação única do conjunto de recortes em `backend/processo_seletivo/editais/domain/recortes.py` (**NOVO**), conforme [contracts/recortes-de-um-marco.md](contracts/recortes-de-um-marco.md): ampla primeiro, reservadas na ordem em que o Perfil as declara, **excluída** a Modalidade apontada como ampla. Vive no domínio porque a validação também a consome, e domínio não importa aplicação
- [ ] T006 Fazer `recortes_do_marco` em `backend/processo_seletivo/ocupacao/application/selectors.py` (**EXISTENTE**) consumir a derivação de T005, preservando o rótulo que cada recorte já mostra — a `021` pagou caro por rótulos homônimos
- [ ] T007 Prender a igualdade em `backend/tests/unit/classificacao/test_recortes_do_marco.py` (**NOVO**): as duas listas — a que a classificação deriva e a que a ocupação deriva — são **iguais**, para o mesmo marco (`FR-491`, `SC-172`). Compara listas, e não implementações
- [ ] T008 Fazer `calcular_ordem`, em `backend/processo_seletivo/classificacao/application/calculo.py` (**EXISTENTE**), receber o recorte e filtrar o universo: recorte reservado lê quem se autodeclarou naquela Modalidade; **a ampla continua lendo todos**, inclusive os autodeclarados (`FR-492`, `D-001`). `Inscricao.modality_id` é anulável, e o nulo é o caso normal
- [ ] T009 Prender o universo em `backend/tests/unit/classificacao/test_universo_do_recorte.py` (**NOVO**): o autodeclarado aparece **nas duas** ordens; quem não se autodeclarou aparece **só** na ampla; e Modalidade declarada como ampla **não** produz recorte (`FR-492`, `FR-503`)
- [ ] T010 [P] Prender a não-regressão em `backend/tests/integration/classificacao/test_ordem_sem_reserva_nao_muda.py` (**NOVO**): Perfil **sem** Modalidade reservada produz ordem **idêntica** — mesmas posições e mesma proveniência — à de antes da feature (`FR-493`, `SC-171`). É a rede que impede a feature de alterar Edital que ela não deveria alcançar
- [ ] T011 [P] Ajustar a chamada direta de `calcular_ordem` em `backend/processo_seletivo/processos/management/commands/seed_demo.py` (**EXISTENTE**) para dizer de qual recorte fala. Comando de semeadura que quebra só reclama na próxima vez que alguém semeia
- [ ] T012 Conferir o orçamento de consulta em `backend/tests/performance/` (**EXISTENTE** — acrescentar ao arquivo que cobre a classificação): a leitura por recorte **não** pode virar N+1 sobre o conteúdo publicado. O projeto já reprova leitura de condição de participação por listagem, e o mesmo princípio se aplica aqui. **Esta tarefa não prende requisito nenhum**: ela vem do *Technical Context* do [plan.md](plan.md) e é higiene de engenharia — está dita aqui para não parecer requisito órfão na conferência

**Checkpoint**: existe **uma** resposta para "quais são os recortes deste marco", e o cálculo sabe
falar de um recorte. Nada ainda emite.

---

## Phase 3: US1 — A ordem do recorte reservado passa a existir (P1) 🎯 MVP

**Goal**: quem conduz o certame emite a ordem de cada recorte, com raiz, sucessão e proveniência
próprias.

**Independent Test**: num Edital 7/1/2, emitir a ordem do recorte reservado; o ato nasce com a lista
daquele recorte, o vigente do outro recorte não foi tocado, e a ordem da ampla continua idêntica.

- [ ] T013 [US1] Fazer `emitir_ordem`, em `backend/processo_seletivo/classificacao/application/emissao.py` (**EXISTENTE**), receber o recorte: a busca do vigente deixa de fixar `lista_id=None`, e o ato nasce com a lista daquele recorte (`FR-490`). O comentário que hoje declara *"só o sorteio emite por lista"* muda junto — comentário que sobrevive à decisão que ele explica passa a mentir
- [ ] T014 [US1] Tornar a confirmação do cálculo específica do recorte em `backend/processo_seletivo/classificacao/application/emissao.py` (**EXISTENTE**, mesma função de T013): a assinatura da proposta distingue os recortes, de modo que a leitura feita em A não confirme a emissão em B (`FR-495`)
- [ ] T015 [US1] Fazer `backend/processo_seletivo/classificacao/application/selectors.py` (**EXISTENTE**) devolver a proposta e o vigente **do recorte pedido**, mantendo a ampla como padrão para quem não pergunta — é o que a `021` fez em `ato_vigente` e deu certo
- [ ] T016 [US1] Prender o não-atravessamento em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**NOVO**): emitir no recorte reservado **não** obsoleta nem sucede a ordem da ampla, e vice-versa (`FR-494`, obrigação 1 do [contrato da ordem](contracts/ordem-por-recorte.md))
- [ ] T017 [US1] Prender a confirmação cruzada em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, criado em T016 — **acrescente**): confirmar no recorte A e tentar emitir no B é **recusado**
- [ ] T018 [US1] Prender o universo emitido em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, acrescente): a ordem da ampla contém os autodeclarados; a do recorte reservado contém **só** eles (`D-001`)
- [ ] T019 [US1] Prender a leitura pura em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, acrescente): abrir a tela de três recortes, repetidamente, **não** constitui ato algum (`FR-496`)
- [ ] T020 [US1] Prender a contraprova do sorteio em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, acrescente): marco que ordena por sorteio **continua indo pelo caminho do sorteio**, e a emissão computada não o alcança. É o cenário de aceitação 4 da `US1`, e sem esta tarefa ele não era prendido por nada — a `033` entregou uma história que não podia satisfazer o próprio teste de aceitação, e foi assim que isso apareceu
- [ ] T021 [US1] Implementar a ordem vazia do recorte sem nenhum autodeclarado (`FR-492a`, já decidido na spec — a tabela de `research.md` `R-8` é o caminho da decisão, não a decisão em aberto): emitível por quem conduz, **nunca automática**, e a tela diz que ninguém concorreu ali em vez de parecer pendência. Toca `backend/processo_seletivo/classificacao/application/emissao.py` e `backend/processo_seletivo/interface/templates/interface/ordenacao.html` (**EXISTENTE**), e é prendida por teste de **ato vazio emitido** e de **mensagem da tela** em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, acrescente)
- [ ] T022 [US1] Prender por teste os **dois** casos de borda, em `backend/tests/integration/classificacao/test_ordem_por_recorte.py` (**EXISTENTE**, acrescente): (a) **Retificação que acrescenta Modalidade depois de a ordem da ampla já ter sido emitida** — o recorte novo nasce sem ordem e **a ordem da ampla continua vigente** (`FR-494a`); é regra de vigência de ato imutável, e por isso está na spec e não aqui; (b) **empate residual que atravessa a fronteira do alvo em dois recortes** — o julgamento do empate vale para as **duas** ordens. Se algum dos dois se comportar de outro jeito, **pare e pergunte**: é sinal de que a regra escrita não é a regra do código
- [ ] T023 [US1] Fazer o documento do ato nomear **o recorte** em `backend/processo_seletivo/publicacoes/infrastructure/pdf.py` (**EXISTENTE**) — `FR-506`. Sem isso, dois documentos do mesmo marco são indistinguíveis
- [ ] T024 [US1] Prender o documento em `backend/tests/unit/publicacoes/test_pdf_classificacao.py` (**EXISTENTE** — **acrescente ao fim**): o documento do recorte reservado o nomeia, e o da ampla continua saindo exatamente como saía

**Checkpoint**: **este é o MVP.** A ordem por recorte existe, não atravessa, e o documento a nomeia.
A cauda já sabe consumi-la — `research.md` `R-7` contou as nove chamadas.

---

## Phase 4: US2 — As telas levam quem conduz a cada recorte (P2)

**Goal**: a ordenação sabe ler o recorte, e as duas telas oferecem caminho entre eles.

**Independent Test**: abrir a ordenação de um marco com três recortes, seguir o caminho oferecido —
o `href` lido da própria página — e chegar ao recorte pedido.

**Depende de US1**: não há recorte a navegar antes de haver recorte.

- [ ] T025 [US2] Fazer `ordenacao`, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**), ler o recorte de `?lista=`, como `corte` no mesmo arquivo já faz — a rota do corte declara esse padrão por escrito, e inventar um segundo seria criar duas gramáticas para a mesma coisa
- [ ] T026 [US2] Derivar os destinos dos demais recortes do marco em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**) e passá-los ao template — a decisão é da view, e **não** do template. É a lição da `033`: repetir a derivação no template cria duas verdades sobre a mesma lista, e elas divergem na primeira mudança
- [ ] T027 [US2] Acrescentar a navegação entre recortes em `backend/processo_seletivo/interface/templates/interface/ordenacao.html` (**EXISTENTE**): a tela nomeia o recorte em que se está e oferece os outros (`FR-497`)
- [ ] T028 [US2] Acrescentar a mesma navegação em `backend/processo_seletivo/interface/templates/interface/corte.html` (**EXISTENTE**) — a tela já **recebe** o recorte e não oferece caminho entre eles
- [ ] T029 [US2] Substituir, no caminho do corte e da ordenação, a resposta de recorte sem ordem: dizer **o que falta e onde se faz**, em lugar de *"não há o que cortar"* (`FR-498`). Toca `backend/processo_seletivo/interface/views.py` e os dois templates (**EXISTENTE**)
- [ ] T030 [US2] Responder objeto inexistente para recorte que não corresponde a Modalidade alguma do Perfil, em `backend/processo_seletivo/interface/views.py` (**EXISTENTE**) — `FR-499`. Recorte vazio e recorte inexistente são coisas diferentes, e confundi-las esconde erro de digitação
- [ ] T031 [US2] Prender a navegação em `backend/tests/interface/test_navegacao_entre_recortes.py` (**NOVO**): a tela nomeia o recorte; o caminho para o recorte reservado é **lido da página** e abre com 200; recorte inexistente responde 404; e o recorte sem ordem diz o que falta
- [ ] T032 [US2] Fazer a tela do marco dizer **o que é** a ordem única histórica de um Edital que emitiu antes desta feature, em `backend/processo_seletivo/interface/views.py` e `backend/processo_seletivo/interface/templates/interface/ordenacao.html` (**EXISTENTE**) — é a metade da `FR-504` que a conferência do acervo não alcança: comparar conteúdo e resumo prova que nada foi reescrito, e **não** prova que a tela explica o que o operador está vendo. Prenda em `backend/tests/interface/test_navegacao_entre_recortes.py` (**EXISTENTE**, acrescente) com um Edital antigo, com reserva e ordem única: a tela mostra a ordem que foi emitida, diz que ela é anterior à ordem por recorte, e **não** oferece correção que a imutabilidade não permite

**Checkpoint**: o percurso do cenário 1 do quickstart fecha sem endereço digitado.

---

## Phase 5: US3 — O produto para de avisar sobre o que resolveu (P3)

**Goal**: o aviso da `032` e a frase da ocupação saem de onde deixaram de ser verdade.

**Independent Test**: a Revisão do Edital 7/1/2 não produz mais o aviso da reserva, e a ocupação do
recorte reservado oferece a apuração.

**Depende de US1**: aposentar o aviso antes de a via existir faria o produto calar sobre um problema
que ainda tem.

- [ ] T033 [US3] Mudar a **resposta** de `backend/processo_seletivo/editais/domain/marcos.py::emite_ordem_no_recorte` (**EXISTENTE**) — `FR-500`. Os consumidores são **dois** — a validação e o selector da ocupação —, contados em `research.md` `R-4`; **a emissão não o consome, porque é a fonte que ele espelha**. Acrescente em `backend/tests/unit/editais/test_marcos.py` (**EXISTENTE**) o teste que prova que os dois dizem a mesma coisa: espelho que se descola da fonte é a Revisão avisando sobre um recorte que a tela oferece. **Esta tarefa parece desfeita por T036, e não é**: a `FR-501a` manda **medir antes de remover**, e se a medição mostrar que o predicado ainda varia, ele fica — e fica correto por causa desta tarefa. Enquanto o predicado existir, é a `FR-500` que o governa
- [ ] T034 [US3] **Aposentar** o aviso `reserved_row_without_ordering` em `backend/processo_seletivo/editais/domain/validation.py` (**EXISTENTE**) — `FR-501`, já decidido na spec. Não sobra caso: todo marco ou sorteia, e o sorteio sempre emitiu por lista, ou é computado, e o computado passa a emitir. Registre em `specs/034-ordem-por-recorte/research.md` (**EXISTENTE**, acrescente ao fim) a varredura que confirma que não sobrou nenhum — se sobrar, **pare**: a `FR-501` está errada e é conversa de spec
- [ ] T035 [US3] Retirar de `backend/processo_seletivo/interface/templates/interface/ocupacao.html` (**EXISTENTE**) a frase que manda apurar fora do sistema, e **as duas ramificações em `recorte.apuravel`** que a governam (`FR-502`). A frase deixou de ser verdade, e frase verdadeira que virou falsa é pior do que frase ausente. **Esta tarefa vem antes de T036, e a ordem não é preferência**: o mecanismo de template trata variável ausente como **falsa**, de modo que remover o campo primeiro esconderia a ação de apurar e exibiria a frase para todos — o inverso da feature, sem erro e sem teste vermelho
- [ ] T036 [US3] Remover `emite_ordem_no_recorte`, o campo `apuravel` derivado dele e o teste de igualdade criado em T033, em `backend/processo_seletivo/editais/domain/marcos.py`, `backend/processo_seletivo/ocupacao/application/selectors.py` e `backend/tests/unit/editais/test_marcos.py` (**EXISTENTE**) — `FR-501a`. Depois de T034 o predicado responde **sempre sim**, e guarda que nunca reprova é pior do que guarda nenhum: o próximo a ler o código confia nele. **Só depois de T035**, que é quem tira a tela de cima dele. **Meça antes de remover**: se ele ainda variar por alguma razão não prevista na spec, escreva a razão e **não** remova — e diga isso em `specs/034-ordem-por-recorte/research.md` (**EXISTENTE**, acrescente ao fim)
- [ ] T037 [US3] Atualizar os **cinco** casos de `backend/tests/unit/editais/test_executabilidade.py` (**EXISTENTE** — altere **só** os cinco, nomeados em `research.md` `R-5`). Os outros cinco **permanecem**, e um deles — `…a_modalidade_declarada_como_ampla_nao_e_lida_como_reserva` — passa a ser a contraprova da derivação única
- [ ] T038 [US3] Atualizar os **dois** casos de `apuravel` em `backend/tests/interface/test_ocupacao.py` (**EXISTENTE**) e o caso do hardening em `backend/tests/interface/test_hardening_pos_auditoria.py` (**EXISTENTE**) — **depois de T035**, e afirmando o que a tela **faz**, não o que o campo vale: com o campo removido, um teste que ainda o mencionasse estaria prendendo um estado que não existe mais. **Os três casos vizinhos, da família do corte (`FR-463`), NÃO mudam** — estão nomeados porque a semelhança convida ao erro
- [ ] T039 [US3] Corrigir, em `backend/tests/integration/ocupacao/test_reversao.py` (**EXISTENTE**), a frase que justifica o helper construído à mão: *"o caminho do ator não a alcança em certame computado"* deixou de ser verdade. **Não apague o helper** — ele é chamado por seis casos, e trocá-lo mudaria o que eles exercitam

**Checkpoint**: o produto afirma **uma** coisa sobre a reserva em marco computado.

---

## Phase 6: Polimento e conferência

- [ ] T040 Percorrer o **cenário 1** de `specs/034-ordem-por-recorte/quickstart.md` (**EXISTENTE**) pela interface administrativa, com o seletor de identidade ligado — inclusive a contraprova do Edital sem reserva —, e registrar o observado para a T047
- [ ] T041 Percorrer o **cenário 2** de `specs/034-ordem-por-recorte/quickstart.md` (**EXISTENTE**) — a cauda inteira, do corte à convocação, nos três recortes. **É o `SC-169`, e é o que decide se a feature entra.** Se qualquer passo exigir shell, banco ou endereço digitado, o critério não fechou. Confira no mesmo percurso a `SC-170`: **toda** ação de apurar que a tela apresentar tem de concluir, e todo recorte sem ação tem de apresentar a razão no lugar do botão
- [ ] T042 [P] Percorrer o **cenário 3** de `specs/034-ordem-por-recorte/quickstart.md` (**EXISTENTE**) — a Revisão sem o aviso, a contraprova do marco que sorteia, e o Edital do acervo intocado
- [ ] T043 [P] Percorrer o **cenário 4** de `specs/034-ordem-por-recorte/quickstart.md` (**EXISTENTE**): exportar o acervo **agora** e compará-lo com o retrato gravado em T002 — idênticos, e o censo dos degraus de elevação sem degrau novo (`FR-504`, `SC-173`). **Esta tarefa não grava o "antes"**: quem o grava é T002, e é por isso que ela vive na fase 1
- [ ] T044 Percorrer o **cenário 5** de `specs/034-ordem-por-recorte/quickstart.md` (**EXISTENTE**) — o recorte em que ninguém concorreu (`FR-492a`), a Modalidade que chega por Retificação depois das ordens emitidas (`FR-494a`) e o Edital do acervo com ordem única (`FR-504`). Os três têm teste e nenhum tinha percurso; são obrigações que o operador **vê**, e o Princípio VI é percurso. **Esta tarefa não é paralela**, embora os outros percursos sejam: o `5.2` **retifica**, e Retificação cria versão publicada — o censo do cenário 4 conta publicações, e uma a mais o reprovaria por um motivo que não é o diff
- [ ] T045 Conferir **caso a caso** os oito testes alterados — **depois de todos os percursos**, porque é o último estado que se confere, e percurso que ache defeito muda o estado contra o "antes" gravado em `specs/034-ordem-por-recorte/antes-da-ordem-por-recorte.md` (**EXISTENTE**, criado em T002), e registrar ali mesmo a comparação. **Nunca pela contagem**: um caso pode manter o número de asserções e trocar o que afirma. Alargar um conjunto aceito é enfraquecer a asserção, e a suíte fica verde do mesmo jeito
- [ ] T046 Varrer os **doze Editais da amostra real** de `doc/avaliacao-de-capacidade-editais-2026-09-12.md` (**EXISTENTE**, leitura) e registrar, em `specs/034-ordem-por-recorte/varredura-da-amostra.md` (**NOVO**), quais avisos da família da `032` ainda disparam em cada um e quais deixaram de disparar (`SC-174`). A `032` fez essa varredura e foi ela que confirmou a decisão de tratar por aviso — checklist, `analyze` e o teste de citações ficam verdes com regras que se contradizem, e só a leitura Edital a Edital não fica
- [ ] T047 Escrever `specs/034-ordem-por-recorte/rastreabilidade.md` (**NOVO**), citando a varredura de T046: uma linha por `FR-`, uma por `SC-` — e **uma por teste alterado, com o motivo**. É o que separa fechar o `ACH-47` de afrouxar a ordem. Registre aqui, nomeadamente, a conferência das **três** proibições da `FR-505` que nenhum comando prova — nenhuma capacidade nova, nenhum papel novo, nenhuma regra de autorização nova —, por leitura do diff; a quarta é a de T048
- [ ] T048 Rodar `cd backend && make lint check test-pg` e registrar a contagem final em `specs/034-ordem-por-recorte/rastreabilidade.md` (**EXISTENTE**, criado em T047). `test-pg` e **nunca** `test`; `lint` são **dois** passos. **Não edite arquivo do projeto enquanto a suíte roda**. O `make check` inclui `makemigrations --check`, e **ele é o guarda de uma das quatro proibições da `FR-505`** — a da migration, que é a `SC-175`. Registre o resultado dele com esse nome, e **só com esse**: as outras três — capacidade nova, papel novo, regra de autorização nova — ele não prova, e são conferidas em T047

---

## Dependências

```
Phase 1 (T001–T004) ──► T004 é PORTÃO DE ESCOPO ──► Phase 2 (T005–T012)
                                                          │
                                                          ▼
                                                    US1 (T013–T024)  🎯 MVP
                                                       │        │
                                              ┌────────┘        └────────┐
                                              ▼                          ▼
                                        US2 (T025–T032)            US3 (T033–T039)
                                              └────────┬─────────────────┘
                                                       ▼
                                             Polimento (T040–T048)
```

**US2 e US3 são independentes entre si** e podem correr em paralelo depois da US1 — tocam arquivos
diferentes: US2 vive em `interface/`, US3 em `editais/domain`, `validation.py` e nos testes.

### Dentro das fases

- **T016 → T017 → T018 → T019 → T020 → T021 → T022** são o mesmo arquivo, criado em T016 — **sete
  tarefas, e não seis**. A `T021` entrou na conta porque ela também acrescenta ali: os testes de ato
  vazio e de mensagem da tela. **Nenhuma leva `[P]`**, e é a regra que a `033` viu ser quebrada
  exatamente assim. O grupo cresceu de quatro para sete ao longo de três passadas de `analyze`, e a
  cada vez alguém teve de lembrar de recontá-lo — na quarta, ninguém tinha.
- **T013 → T014** são a mesma função.
- **T033 → T034 → T035 → T036** — e **cada seta é por um motivo diferente**. O aviso só se aposenta
  depois de o predicado mudar de resposta. A tela só sai de cima do campo depois de o aviso sair. E o
  campo só se remove depois de a tela ter saído de cima dele: **o mecanismo de template trata
  variável ausente como falsa**, de modo que inverter T035 e T036 esconde a ação de apurar e exibe a
  frase do "fora do sistema" para todos — sem erro, sem exceção e sem teste vermelho, porque os
  testes só são ajustados em T038. É o defeito mais caro desta lista e o único que não deixa rastro.
- **T036 → T038** — a remoção de `apuravel` muda **como** os dois casos da tela são atualizados: com
  o campo de pé, eles trocam de expectativa; sem ele, eles deixam de falar de campo nenhum. Escrever
  T038 antes de T036 produz um teste que passa e que prende o estado intermediário.

### Oportunidades de paralelismo

| Tarefas | Por que podem |
|---|---|
| T010 · T011 | arquivos diferentes, nenhuma dependência aberta |
| T042 · T043 | percursos independentes, um sem banco e outro só de leitura |
| — | **T044 fica de fora**: o cenário 5 retifica, e Retificação acrescenta publicação ao censo que T043 conta |
| US2 inteira · US3 inteira | módulos disjuntos, depois que a US1 fecha |

---

## Estratégia de entrega

**MVP = fase 1 + fase 2 + US1.** Fecha o primeiro elo do `ACH-47` — a ordem do recorte reservado
passa a existir, com o documento a nomeando — e a cauda já sabe consumi-la.

**Se algo travar, entregue o MVP inteiro e diga o que ficou.** A ordem parcial é útil; meia ordem
não é.

**A US3 não deve ser adiada indefinidamente.** Enquanto ela não entra, o produto avisa sobre um
problema que já resolveu — e quem lê o aviso primeiro é o operador.
