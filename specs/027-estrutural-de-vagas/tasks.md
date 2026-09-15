---

description: "Task list for feature implementation"
---

# Tasks: Estrutural de vagas — uma declaração só

**Input**: Design documents from `specs/027-estrutural-de-vagas/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/estrutural-de-vagas.md](./contracts/estrutural-de-vagas.md)

**Tests**: **obrigatórios**, e não opcionais. O Princípio V exige teste no nível certo e nomeia
cotas, publicação e retificação entre os que exigem cobertura específica; a §5 da spec fecha a
feature em oito invariantes verificáveis. Nenhuma feature anterior abriu exceção; esta não abre.

**Organization**: por user story, para que cada faixa seja demonstrável sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode correr em paralelo — arquivos distintos, sem dependência pendente
- **[Story]**: a que user story a tarefa pertence (`US1` a `US6`)
- Caminho de arquivo exato em toda tarefa

## Path Conventions

Monólito Django. Código em `backend/processo_seletivo/`, testes em `backend/tests/`.

**Nenhuma migration, nenhum degrau de schema, nenhum app novo, nenhum módulo novo.** Se alguma
tarefa abaixo levar você a criar migration ou pacote, a tarefa foi mal lida — a forma publicada não
muda ([contracts/estrutural-de-vagas.md](./contracts/estrutural-de-vagas.md), §5).

**Banco próprio nesta worktree**: `DB_NAME=ps_demo_027`, e **como variável do Make** —
`make DB_NAME=ps_demo_027 …`, nunca `DB_NAME=ps_demo_027 make …`. O `Makefile` faz `include .env`
seguido de `export`, e o comentário dele diz por quê: *"`include` **sobrepõe** variável de
ambiente"*. O prefixo de ambiente é engolido pelo `DB_NAME=ps_demo_016` do `.env`, e a suíte desta
worktree iria derrubar a de outra sem avisar. Fora do `make` — `manage.py` chamado direto — o
prefixo é a forma certa, porque ali não há `include` nenhum.

Suítes paralelas disputam
`test_processo_seletivo` e se derrubam.

---

## Phase 1: Setup

**Purpose**: ter o verde de partida medido antes de mexer no que vai mudá-lo.

- [X] T001 Preparar o banco desta worktree com `cd backend && LC_ALL=pt_BR.UTF-8 make DB_NAME=ps_demo_027 POSTGRES_USER="$USER" preparar` e confirmar `migrate --check` limpo. *A forma `make DB_NAME=…` não é estilo: o prefixo de ambiente é sobreposto pelo `include .env` do `Makefile`, e esta worktree acabaria preparando o `ps_demo_016` de outra pessoa. `preparar` são três passos nesta ordem — provisionar, migrar, provisionar de novo; se a segunda passada disser `0 de N protegidas`, ela não rodou. Migration desaplicada contamina a sessão inteira, com sintoma longe da causa*
- [X] T002 Rodar `make DB_NAME=ps_demo_027 lint check test-pg` em `backend/` e **gravar a contagem de partida** (passaram, pularam) num arquivo de trabalho fora do repositório. *A `T-008` prevê que a `T005` mude o conteúdo publicado de toda fixture que compõe Perfil sem quadro. Sem a contagem de antes, não há como distinguir a queda esperada da regressão — que é exatamente o que a `026` teve de fazer à mão quando onze testes caíram de uma vez*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: a linha geral passa a existir, a conferência passa a ter o que conferir, e o acervo não
fica preso. **Nenhuma user story começa antes desta fase.**

**⚠️ As três armadilhas do plano estão aqui.** Elas não falham em execução: falham em silêncio.

- [X] T003 [P] Escrever `listas_reservadas(perfil)` em `backend/processo_seletivo/editais/domain/perfis.py`, devolvendo as Modalidades declaradas menos a apontada em `generalCompetitionModalityId`, cumprindo a `FR-317`, com teste unitário em `backend/tests/unit/editais/` para os quatro casos: nenhuma Modalidade, só a ampla apontada, ampla apontada mais reservadas, e Modalidades sem ampla apontada. *É o conceito que a feature acrescenta, e ele é uma leitura, não um campo ([data-model.md](./data-model.md), §2). O quarto caso é o que a `FR-325` adverte: sem apontamento, a Modalidade chamada "Ampla concorrência" conta como reservada, e o sistema não tem como saber que não é — casar denominação continua recusado pela `025`*
- [X] T004 Escrever a derivação em `backend/processo_seletivo/editais/domain/perfis.py` como função pura sobre a carga do Perfil: quando `listas_reservadas` é vazio, garantir exatamente uma linha geral com quantidade igual a `immediateVacancies`, **preservando o `id` que chegou** e criando um só quando não houver. *Pura e idempotente porque é o que faz a mesma carga gravada duas vezes produzir o mesmo resumo canônico. Ela reafirma a quantidade em toda gravação, e é isso que cumpre a `FR-322` quando a última lista reservada é removida*
- [X] T005 Aplicar a derivação em `backend/processo_seletivo/editais/application/draft.py`, imediatamente antes do laço que cria `LinhaDoQuadroDeVagas` (~linha 301), e descrever a materialização na descrição de `vacancyTable` em `specs/001-processo-seletivo-editais/contracts/openapi.yaml`. *No command, e não no formulário nem no serializer: é o que faz a `FR-316` valer para o canal de API tanto quanto para a tela. Derivar na emissão do snapshot foi recusado com razão medida — a identidade nasceria a cada emissão e dois snapshots do mesmo conteúdo teriam resumos diferentes (`T-001`). **A forma não muda e a descrição sim**: quem integra por API e hoje envia `vacancyTable` vazio passa a receber uma linha, e a Constituição exige que o contrato diga o que o comportamento faz*
- [X] T006 Escrever o teste da **armadilha 1** em `backend/tests/unit/editais/`: gravar a mesma carga duas vezes e exigir a mesma identidade de linha e o mesmo resumo canônico; gravar o Perfil, gravar **outra etapa** em seguida, e exigir que a linha geral continue com a mesma identidade. *A segunda metade é a travessia que mata em silêncio: `replace_draft` apaga e recria o rascunho inteiro, e quantidade publicável já desapareceu assim antes, por causa de uma visita ao Cronograma. **E a terceira travessia é o reaproveitamento**: `editais/application/reaproveitamento.py` escreve por `replace_draft`, então a derivação o alcança de graça — mas é o caminho mais exposto que existe, porque **todo** Edital reaproveitado hoje vem de um Edital sem quadro. Exija, no mesmo teste, que o Edital criado a partir de outro nasça com linha geral*
- [X] T007 Corrigir a completude em `_coerencia_do_quadro_de_vagas`, `backend/processo_seletivo/editais/domain/validation.py:1632`, descontando a Modalidade apontada como ampla do conjunto que precisa ter linha, com teste que exija a igualdade rodando num Perfil que declara ampla apontada mais uma reservada. *Hoje `set(modalidades) - com_linha` nunca é vazio nesse formato, porque a ampla apontada por norma não tem linha — logo a igualdade da `FR-161` da `025` **nunca roda** no Edital mais comum do acervo. É a lacuna `R-006` que aquela feature registrou, e fechá-la é requisito desta: sem isso a linha geral pode divergir do total em silêncio, que é a divergência que a feature existe para eliminar (`T-002`)*
- [X] T008 Dar a `validate_for_publication` em `backend/processo_seletivo/editais/domain/validation.py:1274` o ato que está sendo conferido, e passá-lo nas **quatro** chamadas: `backend/processo_seletivo/interface/views.py:522` (as pendências do assistente), `publish_edital.py:427` (`submit_edital`) e `publish_edital.py:645` (`publish_edital`, a publicação efetiva) conferem publicação; `backend/processo_seletivo/publicacoes/application/retificacoes.py:526` confere Retificação. O parâmetro MUST ter **publicação como padrão**, para que as 22 chamadas diretas de `backend/tests/` sigam valendo sem edição e para que esquecer de passá-lo erre pelo lado que recusa. *A quarta é a que importa mais e é a mais fácil de perder: `:427` recusa na submissão, e `:645` é a que impede o Edital defeituoso de virar ato. A distinção é do domínio, e não de implementação: publicar Edital novo sem linha geral cria hoje o defeito que a feature remove; retificar Edital publicado antes dela é o único caminho que o acervo tem*
- [X] T009 Acrescentar o achado impeditivo `vacancy_general_row_missing` em `_coerencia_do_quadro_de_vagas`, **produzido apenas no ato de publicação**, para Perfil sem linha geral. *A `FR-323` exige a recusa e proíbe que ela alcance a Retificação do acervo. **Com o teste no mesmo passo**, e o caso é o único em que a recusa dispara depois da `T005`: Perfil que declara lista reservada e tem a caixa da linha geral vazia — quantidade em branco não grava linha, e é por aí que um Perfil ainda pode chegar à publicação sem ela*
- [X] T010 Escrever o teste da **armadilha 2** em `backend/tests/contract/`: retificar **só a descrição** de um Edital publicado sem quadro nenhum e exigir que o ato passe. *`retificacoes.py` afere o conteúdo produzido com `blocking_findings(validate_for_publication(content))`. Escrita sem o recorte do ato, a `T009` bloquearia toda Retificação de todo Edital do acervo — inclusive as que nada têm com vagas. Este teste entra **junto** com a T009, e não depois*

**Checkpoint**: a linha geral existe, a conferência confere, e o acervo continua retificável.

---

## Phase 3: User Story 1 — Compor um Perfil simples sem descobrir que há dois números (P1) 🎯 MVP

**Goal**: quem compõe um Perfil sem lista reservada declara a quantidade uma vez, e o Edital
publicado apura por ela.

**Independent Test**: compor um Perfil sem Modalidade, publicar, abrir a Ocupação — a quantidade a
apurar é a mesma que o documento publica, sem que nada além do total tenha sido digitado.

- [X] T011 [US1] Em `backend/processo_seletivo/interface/forms.py`, na montagem das linhas do quadro do formulário (~linha 760), deixar de oferecer caixa para a linha geral quando o Perfil não tem lista reservada, mantendo **a identidade dela em campo oculto**. *Sem o `id` no formulário, a gravação seguinte criaria outra linha e a Retificação perderia o endereço. O `modalityId` vazio continua sendo a linha geral, e não referência faltando*
- [X] T012 [US1] Em `backend/processo_seletivo/interface/templates/interface/_perfil.html:203`, condicionar a seção `quadro` à existência de lista reservada, deixando o ponto de ancoragem do fora-de-banda sempre presente no cartão. *O ponto tem de existir mesmo com a seção ausente, ou a `T013` não terá onde entregar a seção nova. `UX-040`: o cartão deixa de ter dois campos numéricos para a mesma quantidade*
- [X] T013 [US1] Em `backend/processo_seletivo/interface/views.py:1517` (`fragmento_modalidade`) e em `backend/processo_seletivo/interface/templates/interface/_modalidade_com_linha.html`, entregar **a seção do quadro inteira** quando ela ainda não está desenhada, e só a linha quando já está. *Armadilha 3, e ela tem duas metades. Feita a `T012` como está escrita, a âncora sobrevive e a linha chega — o que não chega é a **seção**: o Perfil que ganha a primeira Modalidade mostra a linha dela sem a linha geral e sem o pedido de repartição, exatamente no ponto em que a US1 se declara pronta. Feita a `T012` sem preservar a âncora, aí sim o `hx-swap-oob` não acha alvo, **não erra**, e a linha se perde — invisível a teste que só confira status 200. É por isso que esta tarefa não fica para a fase seguinte*
- [X] T014 [P] [US1] Teste de interface em `backend/tests/interface/`: Perfil sem Modalidade não desenha bloco de quadro nem segundo campo; gravar e reabrir devolve a linha geral igual ao total; alterar o total e gravar reafirma a linha. *Cobre `FR-316`, `FR-318`, `FR-320` e `UX-040`*
- [X] T015 [P] [US1] Teste de aceitação em `backend/tests/acceptance/`: percorrer `A1`–`A5` do [quickstart.md](./quickstart.md) — compor, publicar e exigir que a Ocupação tenha quantidade declarada a apurar no recorte da ampla concorrência. *É a `SC-105`, e é o que prova que o defeito deixou de nascer. Exija também que o **documento publicado** exiba a linha geral derivada, com a ampla concorrência em primeiro lugar — é a metade da `FR-329` que a Ocupação não prova, e o lugar onde o candidato lê o número (`backend/tests/contract/test_documento_publicado.py` é o guardião vizinho). E, no mesmo percurso, acrescentar uma Modalidade ao Perfil e exigir que a seção do quadro chegue inteira — é a asserção que prova a `T013`, e que um teste de status não faz*

**Checkpoint**: um Edital composto hoje não chega mais à Ocupação sem quantidade.

---

## Phase 4: User Story 2 — Repartir quando a primeira lista reservada aparece (P1)

**Goal**: o bloco do quadro aparece com a primeira lista reservada, já preenchido, e pede a
repartição conferida contra o total.

**Independent Test**: acrescentar a primeira Modalidade a um Perfil e ver o bloco surgir preenchido;
repartir; ver a conferência recusar a soma que não fecha.

- [X] T016 [US2] Fazer a seção nascer com a linha geral preenchida com o total do Perfil, em `backend/processo_seletivo/interface/forms.py` e no fragmento da `T013`. *A `FR-321` pede o bloco "com a linha geral já preenchida"; o valor já está persistido desde a `T004`, e o que falta é exibi-lo*
- [X] T017 [P] [US2] Em `backend/processo_seletivo/interface/templates/interface/_perfil.html` e `_linha_do_quadro.html`, acrescentar a frase visível que explica por que o bloco apareceu agora e tirar do `.oculto` a explicação de que a linha geral é a da ampla concorrência. *`UX-041` e `UX-042`. A frase "Em branco: quantidade não declarada" ser `.oculto` é, nas palavras da auditoria, metade da causa do achado — a microcópia que explicaria a decisão é invisível para quem enxerga*
- [X] T018 [US2] Fazer a tela dizer, depois da gravação que remove a última lista reservada, que a linha geral voltou a ser o total. *`FR-322`. A re-derivação da `T004` sobrescreve um número que alguém digitou; sobrescrever em silêncio seria trocar um defeito por outro*
- [X] T019 [P] [US2] Testes em `backend/tests/interface/` e `backend/tests/unit/editais/`: percorrer `A6`–`A8` e `A12`; exigir que a soma excedente seja recusada em números; exigir que a igualdade **rode** no Perfil com ampla apontada mais reservada. *A última asserção é a que prova a `T007` no cenário real, e não só em unidade*

**Checkpoint**: a repartição é pedida onde o domínio precisa dela, e conferida.

---

## Phase 5: User Story 3 — Ser avisado do que ficará inerte, antes de publicar (P1)

**Goal**: o que ficará sem quantidade a apurar é dito na etapa que resolve, na Revisão e na
confirmação da publicação — em números, e sem bloquear.

**Independent Test**: submeter um Edital com uma lista reservada sem linha e ver a advertência nos
três lugares, com a submissão passando.

- [ ] T020 [P] [US3] Acrescentar a advertência `vacancy_reserved_list_without_row` em `_coerencia_do_quadro_de_vagas`, `backend/processo_seletivo/editais/domain/validation.py:1632` — uma por lista reservada sem linha, dizendo o que o Perfil publica e o que aquele recorte terá a apurar. *`Severity.WARNING`, nunca impeditiva: quadro parcial é legítimo, e a `025` decidiu isso com razão que continua de pé. O caminho `/profiles/id=…/vacancyTable` já cai na etapa `perfis` pela busca de trás para frente de `_destino` — **confirme, não presuma***
- [ ] T021 [P] [US3] Acrescentar a advertência `general_competition_modality_undeclared` em `_ampla_concorrencia_declarada`, `backend/processo_seletivo/editais/domain/validation.py:1050`, para o Perfil que declara Modalidade e não declara qual é a da ampla. *Duas advertências, e não uma, porque os atos que as resolvem são diferentes: uma se resolve escrevendo uma quantidade, a outra escolhendo num campo que já existe. É também a promessa que a `FR-176` da `025` deixou escrita e sem canal*
- [ ] T022 [US3] Em `backend/processo_seletivo/interface/revisao.py:31` (`_perfil`) e em `backend/processo_seletivo/interface/templates/interface/compor_revisao.html`, exibir o total e o quadro **lado a lado** no bloco de cada Perfil, inclusive quando o quadro não cobre todas as listas. *Hoje a Revisão imprime "2 vaga(s) imediata(s)" e só menciona o quadro quando ele existe — é o quinto dos seis pontos em que o sistema podia ter avisado e não avisou (`FR-326`, `UX-043`)*
- [ ] T023 [US3] Fazer a confirmação da publicação repetir as advertências pendentes, em números, em `backend/processo_seletivo/interface/views.py:1885` e no template de confirmação correspondente. *`FR-328`. É o último ponto em que a correção ainda é barata: depois dali, a mesma informação custa uma Retificação*
- [ ] T024 [P] [US3] Testes em `backend/tests/interface/`: percorrer `A9`–`A11`; exigir que as duas advertências sejam distintas; exigir que a Revisão **não** diga que nada está pendente enquanto houver alguma; exigir que a submissão passe assim mesmo. *`FR-324`, `FR-325`, `FR-327`, `SC-106` e `UX-044`. A última asserção é a que impede que a advertência vire recusa por descuido*

**Checkpoint**: nenhum Edital chega à publicação sem que o que ficará inerte tenha sido dito.

---

## Phase 6: User Story 4 — Declarar o quadro de um Edital já publicado (P1)

**Goal**: o acervo tem saída pelo canal do ator, sem que nada mude sozinho.

**Independent Test**: retificar um Edital publicado sem quadro acrescentando a linha geral e ver a
Ocupação apurar — sem shell, sem API, sem banco.

- [ ] T025 [US4] Acrescentar a conferência da `FR-335` em `backend/processo_seletivo/editais/domain/validation.py`: alterar o total de um Perfil publicado que **tem** linha geral e não tem lista reservada exige alterar a linha no mesmo ato, e a recusa diz os dois números; onde o Perfil publicado **não** tem linha geral, o mesmo caso adverte e nomeia o ato que resolve. *As duas metades são necessárias: a recusa impede que a divergência renasça por Retificação, e a advertência impede que o acervo fique preso — é a `T-003` de novo, um nível abaixo*
- [ ] T026 [US4] Em `backend/processo_seletivo/publicacoes/application/retificacoes.py:526` e no template de confirmação da Retificação, exibir os achados **não** impeditivos do conteúdo que o ato produziria. *A informação já é calculada e é descartada por `blocking_findings`. `FR-336`: a conferência da Retificação diz sobre o conteúdo que ela produziria o mesmo que a submissão diz sobre o rascunho*
- [ ] T027 [P] [US4] Teste em `backend/tests/unit/` que fixa a `FR-330`: `linha_do_quadro` em `backend/processo_seletivo/classificacao/application/corte.py:53` continua devolvendo nada para Perfil publicado sem linha, e nenhum leitor infere. *Contrato negativo, e o mais importante da feature: é ele que impede que alguém "conserte" o acervo por interpretação em vez de por ato. A derivação na leitura foi recusada com razão medida — ela conserta zero dos três Editais da demonstração (`D-005`)*
- [ ] T028 [P] [US4] Teste em `backend/tests/contract/` que fixa a `FR-334`: acrescentar linha por Retificação a Edital cuja ordem já foi emitida não altera a ordem, o resultado publicado nem as convocações feitas. *Hoje isso é verdade por construção — `effective_version(at=…)` e efeitos congelados no ato. O teste existe para que uma mudança futura não desfaça a promessa em silêncio, como a `026` fez pela `FR-309`*
- [ ] T029 [US4] Teste de aceitação em `backend/tests/acceptance/`: percorrer `B4`–`B10` do [quickstart.md](./quickstart.md), incluindo a `SC-109` — o ciclo inteiro numa sessão, pelo canal do ator — e a asserção da `SC-110` — o resumo canônico dos Editais que ninguém retificou é idêntico ao de antes da feature. *É a prova de que a `FR-333` foi cumprida: nada foi convertido, preenchido ou reescrito*

**Checkpoint**: os Editais publicados antes da feature têm caminho, e nenhum mudou sozinho.

---

## Phase 7: User Story 5 — Encontrar, no acervo, quem precisa do ato (P2)

**Goal**: quem supervisiona vê quais Editais precisam da Retificação, e quem abre a Ocupação lê o
ato em vez de um beco.

**Independent Test**: semear o acervo no estado de hoje e ver a supervisão nomear os Editais e os
recortes afetados.

- [ ] T030 [P] [US5] Acrescentar a segunda metade da frase na Ocupação: `backend/processo_seletivo/ocupacao/application/emissao.py:85` e `backend/processo_seletivo/interface/templates/interface/ocupacao.html:35`. *A frase continua verdadeira e passa a nomear o ato que declara a quantidade e o Perfil a que ele se aplica (`FR-332`, `UX-045`). O comportamento não muda: apontar o ato não é praticá-lo*
- [ ] T031 [P] [US5] O mesmo na Convocação: `backend/processo_seletivo/convocacao/application/convocar.py:358` e `backend/processo_seletivo/interface/templates/interface/convocacao.html:74`. *"Não há mais quem chamar dentro da faixa que o corte alcançou" é verdadeiro e insuficiente: ele não diz que a causa pode ser um quadro que ninguém declarou*
- [ ] T032 [US5] Acrescentar a sexta espécie de sinal em `backend/processo_seletivo/interface/supervisao.py` — constante, entrada em `ESPECIES` (linha 463), função de detecção e alcance —, com `Medida` de recortes sem quantidade sobre recortes publicados e `Destino` para a Retificação. *`FR-331` e `UX-046`. A detecção lê o conteúdo vigente que a supervisão **já** carregou por Edital: nenhuma consulta nova. Tela nova foi recusada — custa rota, porta, template e teste de autorização para dizer menos (`T-005`)*
- [ ] T033 [US5] Testes em `backend/tests/interface/`: percorrer `B1`–`B3`, fechando a `SC-108`; exigir que o sinal não seja montado para quem não o alcança; exigir que a Ocupação continue recusando apurar. *A supressão por alcance é a regra que a `022` já fixou, e herdá-la é o que dispensa porta nova*

**Checkpoint**: o acervo é visível a quem pode agir sobre ele.

---

## Phase 8: User Story 6 — A demonstração deixa de ensinar o defeito (P2)

**Goal**: os Editais da demonstração publicam quadro e apuram.

**Independent Test**: semear e percorrer, nos três Editais, do documento publicado até a Ocupação com
quantidade a apurar.

- [X] T034 [US6] Em `backend/processo_seletivo/processos/management/commands/seed_demo.py`, declarar `generalCompetitionModalityId` e o `vacancyTable` dos três conjuntos de Perfis: `perfis()` (linha 79) — `DOC-INFO` com geral 1 e PPP 1, `TEC-LAB` com geral 0 derivada — e `perfil_de_sorteio()` (linha 355) — `TEC-EAD` com geral 30 e PPP 10, cumprindo `FR-338` e `FR-339`. *Puxada para a Fase 2 na execução, e a razão é que foi ela quem quebrou o `seed_demo`: os Perfis da demonstração declaram Modalidade sem apontar a ampla, e passaram a não publicar. Quem quebra conserta. A Retificação do seed, que ampliava as vagas de 2 para 3, virou o ato completo — a demonstração passa a ensinar o ato certo a quem for retificar de verdade. Os três casos da feature no mesmo seed: repartição declarada, derivação pura, e o Perfil de sorteio — que é o que a Ocupação e a Convocação percorrem — com quantidade nos dois recortes (`T-010`)*
- [ ] T035 [US6] Estender `backend/tests/integration/test_seed_demo.py`: os três Editais publicam quadro, a Ocupação apura em cada recorte publicado, e a Convocação tem quem chamar. *`SC-107`, e `FR-338` verificada de fora. Hoje a demonstração oficial reproduz o defeito nos três — quem escreveu o sistema caiu na mesma armadilha ao escrever a demonstração dele*

**Checkpoint**: o sistema demonstra o que entrega.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T036 Rodar `make DB_NAME=ps_demo_027 test-pg` em `backend/` e **ler cada queda** contra a contagem da `T002`, decidindo uma a uma se é a mudança esperada da `T005` ou regressão. *Aqui também se verifica a `FR-337` — nenhum campo novo, nenhuma natureza alterada —, porque o guardião do contrato de mutabilidade da `026` reprova quem mexer nisso sem declarar. A `T-008` prevê a conta: toda fixture que compõe Perfil sem quadro passa a publicar linha geral, e os testes que afirmam `vacancyTable: []` ou comparam resumo canônico mudam de valor. Nenhuma queda é silenciada; cada uma é uma decisão anterior reencontrada*
- [ ] T037 [P] Escrever os testes dos oito invariantes da §5 da spec em `backend/tests/unit/` e `backend/tests/contract/`. *Invariante é o que se verifica em qualquer estado do acervo, e não no caminho feliz de um cenário. O oitavo — nenhuma quantidade derivada com outra fonte que o total do Perfil — é o que fecha a `FR-319`, a única proibição desta feature que de outro modo ficaria sem guarda*
- [ ] T038 [P] Escrever `specs/027-estrutural-de-vagas/rastreabilidade.md` ligando cada requisito ao teste que o fecha. *Atenção: `tests/test_citacoes_de_requisito.py` exige que a matriz, **se existir**, cubra `FR-316`–`FR-340`, `SC-104`–`SC-111` e `UX-040`–`UX-046` sem exceção. Matriz incompleta reprova o CI; não começar uma é legítimo, começá-la pela metade não*
- [ ] T039 Percorrer os três percursos do [quickstart.md](./quickstart.md) pela interface, com o servidor local e `INTERFACE_SELETOR_IDENTIDADE=true`. *É o cenário demonstrável que o Princípio VI exige, e ele não é substituível por suíte verde. Sem a variável a `/gestao/` devolve 503; o endereço é `localhost`, porque `127.0.0.1` devolve `DisallowedHost`*
- [ ] T040 Rodar `make DB_NAME=ps_demo_027 lint check test-pg` em `backend/` e `uv run pytest tests/test_citacoes_de_requisito.py`. *`lint` são **dois** passos — `ruff check` e `ruff format --check` —, e rodar só o primeiro declara verde local e quebra no CI. A varredura de citações lê `specs/`, e PR de documentação também quebra o CI*

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências.
- **Foundational (Fase 2)**: depende do Setup. **Bloqueia todas as user stories** — sem a linha
  geral materializada não há o que exibir, conferir, advertir ou apurar.
- **US1 (Fase 3)**: depende da Fase 2. É o MVP.
- **US2 (Fase 4)**: depende da Fase 3, que já entregou o fragmento e a âncora. O que a US2
  acrescenta é o preenchimento, a frase visível e a re-derivação.
- **US3 (Fase 5)**: depende da Fase 2; independente da 3 e da 4 para escrever, e melhor de demonstrar
  depois delas.
- **US4 (Fase 6)**: depende da Fase 2, e só dela. É a faixa do acervo, e não toca a composição.
- **US5 (Fase 7)**: depende da Fase 2. A `T032` fica melhor depois da `T030`/`T031`, que fixam a
  frase que o sinal repete.
- **US6 (Fase 8)**: depende da 2 para existir e da 3–5 para demonstrar.
- **Polish (Fase 9)**: depende de tudo.

### Ordem que não pode inverter

1. `T004` antes de `T005`, e `T005` antes de qualquer tela.
2. `T007` depois de `T003` — a completude precisa do conceito.
3. `T009` e `T010` **juntas**. A exigência sem o teste do acervo é a armadilha 2 solta.
4. `T012` e `T013` **juntas**, e agora adjacentes. Condicionar o bloco sem entregar a seção deixa
   meia tela no cartão; condicionar sem preservar a âncora perde a linha em silêncio.
5. `T034` depois de tudo o que ela demonstra — **salvo se a Fase 2 a quebrar antes**, que foi o que aconteceu: aí ela vem junto, porque suíte vermelha esconde regressão nova.

### Parallel Opportunities

- `T003` isolada na Fase 2; o resto dela é cadeia.
- `T014` e `T015` em paralelo; `T017` e `T019` em paralelo; `T020` e `T021` em paralelo;
  `T027` e `T028` em paralelo; `T030` e `T031` em paralelo; `T037` e `T038` em paralelo.
- US4 e US5 podem correr em paralelo com US1–US3 por pessoas diferentes: tocam arquivos disjuntos.

---

## Parallel Example: User Story 3

```bash
# As duas advertências são de funções diferentes do mesmo módulo, e não se cruzam:
Task: "vacancy_reserved_list_without_row em _coerencia_do_quadro_de_vagas"
Task: "general_competition_modality_undeclared em _ampla_concorrencia_declarada"
```

---

## Implementation Strategy

### MVP (US1)

1. Fase 1 e Fase 2 inteiras — não há atalho, e as três armadilhas estão ali.
2. Fase 3.
3. **Pare e valide**: compor Perfil sem Modalidade, publicar, abrir a Ocupação. Se houver quantidade
   a apurar, o achado P0 deixou de nascer.
4. **E acrescente uma Modalidade ao Perfil**, conferindo que a seção do quadro chega inteira. É o
   que separa o MVP honesto do MVP que parece pronto: a `T012` condiciona o bloco, e sem a `T013`
   o cartão fica pela metade no primeiro gesto que sai do caminho feliz.

### Entrega incremental

1. Fase 2 → a fonte única existe.
2. + US1 → o defeito não nasce mais (MVP).
3. + US2 → a repartição é pedida onde o domínio precisa.
4. + US3 → o que fica inerte é dito antes de custar Retificação.
5. + US4 e US5 → o acervo tem saída e quem pode agir enxerga.
6. + US6 → a demonstração ensina o que o sistema faz.

**As duas metades não são intercambiáveis.** Parar depois da US3 entrega um sistema que não produz
mais Editais quebrados e deixa os sete que já existem inertes para sempre — que é metade do achado,
e a metade que já está publicada.

---

## Notes

- `[P]` = arquivos distintos, sem dependência pendente.
- Nenhuma migration nesta feature. Se uma aparecer, pare e releia a `T-011` da pesquisa.
- Advertência que bloqueia é defeito, e não zelo: a `025` decidiu que quadro parcial é legítimo.
- Nada de conteúdo publicado é reescrito por tarefa alguma. O acervo muda por ato de quem retifica.
