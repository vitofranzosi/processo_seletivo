# Tasks: O desfecho da convocação comunicado ao candidato (156)

**Input**: [spec.md](spec.md) (revista no PR #488), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas-e-comandos.md](contracts/telas-e-comandos.md).

**Antes da T001**: a revisão da spec (PR #488) precisa estar na `main`; conferir com
`git log origin/main` e o texto da spec. A implementação parte da `main` atualizada, numa worktree
própria, com `DB_NAME` próprio.

**Testes**: o repositório prova cada requisito por teste (Princípio da rastreabilidade); cada fase
traz os seus. Caminhos relativos a `backend/`.

## Formato: `[ID] [P?] [Story] Descrição`

- **[P]**: paralelizável (arquivos diferentes, sem dependência de tarefa aberta)
- **[USn]**: a história da spec (US1 aceite; US2 desfechos; US3 convocação aberta; US4 contato;
  US5 pedido; US6 homologação; US7 aviso; US8 mensagem)

---

## Fase 1 — Preparação

- [x] T001 Conferir na `main` a revisão da 156 (#488) e partir dela; anotar o estado da `152`, da `154` e
  da `150` (PRs e branches) no rascunho do PR — R-015
  *(13/11: a revisão #488, a `152` #489/#520, a `154` #497 e o #499 estão na `main` em `761914c1`, de onde esta implementação parte.)*
- [x] T002 [P] Acrescentar `portal/desfecho.py` às listas literais das varreduras
  (`tests/test_vocabulario_da_convocacao.py`, `tests/test_vocabulario_dos_documentos_da_convocacao.py`,
  `tests/test_vocabulario_do_requerimento.py`) e `avisos/domain/desfecho.py` a
  `tests/test_vocabulario_do_aviso.py` (`DA_066`) — R-001, FR-6403
  *(13/11: só a parte do portal — `portal/desfecho.py` nas três, e `_fundamento_do_ato.html` na da convocação. `avisos/domain/desfecho.py` entra em `DA_066` com a T044, que o cria.)*

---

## Fase 2 — Fundação (bloqueia as histórias)

- [x] T003 Criar `processo_seletivo/portal/desfecho.py` com a assinatura das funções puras
  (`frase_do_desfecho`, `frase_da_convocacao`, `proximo_passo`, `caminho_para_recorrer`) e os textos
  das FR-6406, FR-6407, FR-6442; sem banco nem relógio — R-001
  *(13/11: `frase_do_desfecho`, `do_desfecho` e `fundamento_do_registro`, com as FR-6406 e FR-6407. `frase_da_convocacao` (FR-6442) entrou com a T023; `proximo_passo` e `caminho_para_recorrer` esperam a T016 e a T017: sem quem os chame, seriam código morto.)*
- [x] T004 [P] Criar `portal/templates/portal/_fundamento_do_ato.html` (`<details class="fundamento-do-ato">`
  com `<summary>` parametrizado) e a regra `.fundamento-do-ato` em `portal/static/portal/portal.css` —
  FR-6400, UX-621, R-002
- [x] T005 [P] Acrescentar `desfechos__atestado` ao `prefetch` de `vigentes_por_inscricao`
  (`convocacao/application/selectors.py`), para a frase da inércia sem consulta — R-002
  *(13/11: por `Prefetch` com `select_related`, para não somar consulta.)*
- [x] T006 Testes de unidade de `portal/desfecho.py`: uma frase por espécie de desfecho e de convocação;
  nenhuma com os termos da FR-6403, com *"homologa"*, *"dentro das vagas"* ou *"matrícula"* como
  próximo passo; no máximo duas frases antes do próximo passo (`tests/unit/portal/test_frases_do_desfecho.py`)
  — FR-6406, FR-6407, FR-6408, FR-6442, UX-620
  *(13/11: sem o próximo passo, que é da T018.)*

---

## Fase 3 — US2: quem perdeu a vaga entende por quê (P1) 🎯

**Teste independente**: as sete espécies na tela da convocação e no acompanhamento, com a frase simples
e o fundamento recolhido; nenhum termo técnico fora dele.

- [x] T007 [US2] `portal/situacao.py`: o porquê do desfecho vira a frase simples, e o fundamento vai a um
  campo novo de `Linha` para o template recolher; `situacao_da_inscricao` continua sem consulta —
  FR-6400, FR-6401, FR-6402, FR-1172 da `063` revista
- [x] T008 [US2] `portal/templates/portal/acompanhamento.html`: o porquê com `_fundamento_do_ato.html` —
  FR-6400
- [x] T009 [US2] `portal/templates/portal/_chamada_da_convocacao.html` (ramo decidido) e
  `convocacao.html` (sem documento): *"Resultado registrado: ‹rótulo›"*, a frase simples e o
  fundamento recolhido, no lugar de *"Registrado em …: ‹fundamento›"* — FR-6400, FR-6405, FR-6406
- [x] T010 [US2] `portal/views.py` (`convocacao`): passar o vencimento, a espécie do atestado e o que a
  frase pede às funções de `desfecho.py` — FR-6406, FR-6407
- [x] T011 [US2] *"Chamada: 1ª chamada, para vaga inicial"* no lugar de *"Espécie: …"* em `convocacao.html`,
  `_convocacao_da_inscricao.html` e `_obrigacoes_da_convocacao.html`; e o rótulo da FR-1172 na lista
  "Minhas inscrições" (`views._item_da_lista`) — FR-6403, FR-6405, R-005
  *(13/11: e, até a T017, `obrigacoes.ACEITE` fica só com *"Os próximos passos são os que o Edital indica."* — o que o registro não é passou para a frase simples, e repeti-lo na mesma tela era dizer duas vezes.)*
- [ ] T012 [US2] Indeferimento: o caminho para a seção de recursos quando o plano do documento a mostra
  (FR-6414) — **fazer depois da T016** (US1), que dá a leitura da seção
- [x] T013 [US2] Ajustar os testes que asseriam a forma antiga (`tests/unit/portal/test_situacao_da_inscricao.py`,
  `tests/interface/test_portal_convocacao.py` SC-1150, `tests/interface/test_portal_jornada_consolidada.py`,
  `tests/interface/test_portal_caminho_da_convocacao.py`) e acrescentar um caso por espécie
- [x] T014 [US2] Varredura nova `tests/test_vocabulario_do_desfecho.py`: renderizar o portal nas sete
  espécies e nas três de convocação, tirar o conteúdo dos `<details>` e reprovar os termos da FR-6403
  — SC-2120
  *(13/11: as sete espécies, nas duas telas e nos dois ramos da convocação, e as três espécies de convocação, com a T023.)*
- [x] T015 [US2] Orçamento de consultas: `TestCusto` da `063` e os custos de
  `test_portal_jornada_consolidada.py` sem consulta nova por item — R-002
  *(13/11: `TestCusto` da `063` e os custos da jornada consolidada passam sem mudança.)*

---

## Fase 4 — US1: quem foi aceito sabe onde está o próximo passo (P1)

**Teste independente**: aceite num Edital com a seção da matrícula e num sem ela; nada presume
matrícula.

- [ ] T016 [US1] Leitura da seção aplicável: a partir do snapshot da versão vigente, pelo plano do
  documento (`publicacoes/infrastructure/apresentacao.plano`), devolver o título publicado da seção de
  chave `matricula` (ou da apresentada *"Como será a matrícula?"*) e da de `recursos`, ou vazio
  (`portal/views.py` ou um leitor em `portal/desfecho.py` que receba o plano) — FR-6411, FR-6414, R-003
- [ ] T017 [US1] `portal/obrigacoes.py`: `ACEITE` passa à frase da FR-6406; `portal/situacao.py`
  (`frase_do_aceite`, `_acao_do_desfecho`) e os templates mostram o próximo passo: *"O Edital explica o
  que vem depois em «‹título›»."* com o caminho `portal:selecao#documentos-titulo`, ou *"Consulte o
  Edital publicado para saber o que vem depois."*, e *"Se tiver dúvida, fale com ‹contato›."* — FR-6410
  a FR-6413, FR-3750 da `118` revista
- [ ] T018 [US1] Testes: aceite e regularização com e sem a seção; nenhuma frase com *disponibilizad*,
  *encaminhad*, *formalizad* ou matrícula como próximo passo (`tests/interface/test_portal_proximo_passo.py`)
  — FR-6413, SC-2129, US1

---

## Fase 5 — US4: o contato é o da unidade, ou nenhum (P1)

**Teste independente**: com canal da unidade, só com o da instalação, e sem nenhum.

- [ ] T019 [P] [US4] `portal/templates/portal/_atendimento_da_convocacao.html` (o canal como link, ou
  nada) e o uso dele em `_obrigacoes_da_convocacao.html` e `convocacao.html`; `obrigacoes.frase_do_atendimento("")`
  devolve vazio; `situacao.py:651` passa o canal; o acompanhamento lê o canal no desfecho de aceite,
  regularização e no vencido — FR-6415, FR-6416, R-004
- [ ] T020 [P] [US4] `convocacao/application/comunicar.py` sem o padrão *"a comissão do certame"*, e os
  quatro modelos de mensagem com *"Em caso de dúvida, fale com ‹canal›."* só com canal — FR-6416,
  FR-3883 da `121` revista
- [ ] T021 [US4] `treinamento/`: registrar o canal fictício na unidade dos cenários, pelo comando de
  edição do registro, com motivo e trilha, só com `CENARIOS_DE_TREINAMENTO` — FR-6417, R-014
- [ ] T022 [US4] Testes: as três situações de canal nas telas da convocação e do resultado e nas
  mensagens; as outras telas do portal mantêm a frase genérica (`tests/interface/test_portal_contato.py`,
  `tests/unidades/test_identificacao_multiunidade.py` ajustado) — SC-2122

---

## Fase 6 — US3: a convocação aberta diz por que a pessoa foi chamada (P2)

- [x] T023 [US3] `convocacao.html` e `_obrigacoes_da_convocacao.html`: a frase da FR-6442 antes do
  fundamento da convocação, recolhido sob *"Fundamento da convocação"*, com o nome da lista lido sem
  consulta nova — FR-6400, FR-6442
  *(13/11: feita antes da US2 terminar, porque o fundamento da convocação é o primeiro exemplo do achado 18 e a SC-2120 o varre. Esbarrava na FR-3740 da `118` — o bloco "Sobre esta convocação" sem `details` —, que o usuário decidiu rever pela `156` em 13/11: a revisão está na `118`, e a FR-6441 e o quadro das revisões a listam.)*
- [x] T024 [US3] Testes por espécie de convocação, com o complemento dentro do recolhido — US3
  *(13/11: as três frases em `test_frases_do_desfecho.py`; na tela, as três espécies com o fundamento derivado da `050` só dentro do recolhido, em `test_vocabulario_do_desfecho.py`.)*

---

## Fase 7 — US8: o e-mail da convocação diz o prazo como ele é (P2)

- [x] T025 [P] [US8] `convocacao/templates/convocacao/mensagem/{inicial,correcao}.{txt,html}`: o prazo sem
  *"contado do envio desta mensagem"* — FR-6428, D-014
  *(13/11: no HTML, o parágrafo da cláusula sai e o ponto final entra dentro do negrito — a SC-1159 compara frase a frase, e `</strong>.` viraria "até ‹data› .".)*
- [x] T026 [US8] Ajustar `tests/unit/convocacao/test_mensagem.py` e
  `tests/integration/convocacao/test_mensagem_da_convocacao.py` (SC-1159 continua frase a frase) — SC-2128
  *(13/11: também `test_reenvio_nao_reinicia_prazo.py`, que compara a linha do prazo das duas mensagens e passa a compará-la inteira — cortava na primeira vírgula, logo depois do dia da semana.)*

---

## Fase 8 — US5: o pedido de desistência pelo portal (P2)

**Teste independente**: pedir, enviar documento com o pedido pendente, cancelar e pedir de novo; nenhum
desfecho; prazo igual.

- [ ] T027 [US5] Modelos `PedidoDeDesistencia` e `CancelamentoDoPedidoDeDesistencia` em
  `convocacao/models.py` (append-only, sem motivo) e a migration `convocacao/migrations/0008_pedido_de_desistencia.py`
  com os gatilhos, no molde da `0007` — data-model, R-007
- [ ] T028 [US5] `seguranca/papeis.py` (`TABELAS_APPEND_ONLY`, 60) e os guardiões: `tests/seguranca/test_homologacao_preservada.py`,
  `tests/unit/convocacao/test_append_only.py`, `TRIGGERS_POR_APP` em `tests/migrations/test_migrations.py`;
  o número no README, no `CLAUDE.md` e no `doc/implantacao-em-producao-ubuntu.md`
- [ ] T029 [US5] `convocacao/application/desistencia.py`: `pedir_desistencia`, `cancelar_pedido_de_desistencia`,
  `estado_do_pedido`, `pedidos_pendentes(chamadas)`, com a trava do Processo `FOR SHARE` e da Inscrição
  `FOR UPDATE`, a chave de idempotência e a idempotência pelo estado, e a trilha sem endereço — FR-6419, FR-6420, FR-6422, FR-6423,
  R-008
- [ ] T030 [US5] Portal: rotas `portal:desistir` e `portal:cancelar-desistencia` (`portal/urls.py`), as
  views (`portal/views.py`) e `portal/templates/portal/desistir.html`; na convocação, *"Desistir desta
  convocação"* como link secundário no fim, ou a frase do pedido pendente com *"Cancelar o pedido de
  desistência"*; os envios continuam oferecidos — FR-6418, FR-6419, FR-6421, FR-6422, UX-622
- [ ] T031 [US5] Regras da folha do portal para as classes novas (`portal/static/portal/portal.css`) e os
  guardiões de classe e de largura
- [ ] T032 [US5] Testes de integração contra PostgreSQL (`tests/integration/convocacao/test_pedido_de_desistencia.py`):
  pedido, recusas, duplo clique, cancelamento, recusa depois do desfecho, envio de documento e do
  Requerimento com o pedido pendente, prazo igual, sucessão da convocação, concorrência com o desfecho
  — SC-2123, SC-2130
- [ ] T033 [US5] Testes de interface do portal (`tests/interface/test_portal_desistencia.py`): a confirmação
  com a ciência, a página com o pedido pendente, o cancelamento, a recusa de inexistente para outra
  pessoa — US5

---

## Fase 9 — US6: a comissão homologa o pedido (P2)

**Teste independente**: pedido pendente → atalho → desistência expressa citando o protocolo; outro
desfecho sem ciência recusado; lote sem a pessoa.

- [ ] T034 [US6] `convocacao/application/desfechar.py`: `ciencia_do_pedido` e a recusa
  `pedido_de_desistencia_pendente` em `registrar`; o declarado com o pedido encerrado — FR-6425
- [ ] T035 [US6] `convocacao/domain/alcance.py` e `convocacao/application/fluxo.py`: o lote deixa de fora
  as chamadas com pedido pendente (`fora["pedidoDeDesistencia"]`) — FR-6426, FR-878 da `050` revista
- [ ] T036 [US6] `interface/conducao_da_convocacao.py`: o passo `PEDIDO_DE_DESISTENCIA` logo depois de
  `DESFECHADA` — FR-6443
- [ ] T037 [US6] `interface/templates/interface/convocacao.html` e `interface/views.py`: a linha do pedido
  no cartão, o atalho *"Registrar a desistência pedida"* (espécie fixa, fundamento derivado, pela
  conferência do texto), a marca de ciência do pedido no formulário do desfecho, *"Ficam de fora…"* do
  lote — FR-6424, FR-6425, FR-6426, D-016
- [ ] T038 [US6] `interface/conferencia_do_texto.py` e `_conferir_o_texto.html`: a prévia nas duas
  camadas — FR-6404, FR-3993 da `125` revista
- [ ] T039 [US6] `interface/andamento.py` (`situacoes_da_convocacao` e os fatos de `_Leitor._convocacao`):
  a providência *"Registrar a desistência pedida pelo portal"* com a contagem — FR-6427
- [ ] T040 [US6] `processos/application/pendencias_do_edital.py`, `interface/encerramento.py` (`DA_099`,
  `TIPOS_NO_PROCESSO`) e `interface/relatorio_do_edital.py`: a advertência dos pedidos pendentes — FR-6444,
  D-017
- [ ] T041 [US6] Testes: integração do desfecho com pedido (`tests/integration/convocacao/test_homologacao_do_pedido.py`),
  do lote, do índice e do "O que fazer agora", e os guardiões da advertência
  (`tests/unit/interface/test_advertencia_do_processo.py`,
  `tests/interface/test_advertencia_do_encerramento_do_processo.py`) — SC-2123, SC-2124

---

## Fase 10 — US7: o aviso do desfecho, atrás das duas chaves (P3)

**Teste independente**: com as duas chaves ligadas, a opção marcada grava e o despacho envia; com
qualquer uma desligada, a opção some, o POST é recusado e o despacho não envia.

- [ ] T042 [US7] `config/settings/base.py`, `development.py` e `test.py`: `AVISOS_DE_DESFECHO`; e
  `avisos/application/comando.py`: `envio_do_desfecho_habilitado()` — FR-6437, R-012
- [ ] T043 [US7] `avisos/domain/nomes.py` (`DESFECHO`, rótulo da origem), `avisos/models.py`
  (`DestinatarioDoAviso.desfecho`) e `avisos/migrations/0003_origem_desfecho.py`, no molde da `0002` —
  data-model, R-011
- [ ] T044 [P] [US7] `avisos/domain/desfecho.py`: assunto, corpo neutro, instrução de acesso por código,
  contato quando houver, rodapé fixo, escapado — FR-6433, FR-6434, FR-6435; e
  `tests/unit/avisos/test_texto_do_desfecho.py` — SC-2127 (sem espécie, nome, CPF, protocolo)
- [ ] T045 [US7] `avisos/application/desfechos.py`: `gravar` (na transação do desfecho, um aviso por
  pessoa, sem endereço não grava) e `motivo_para_nao_enviar` (sucedida ou desfecho que deixou de ser o
  vigente) — FR-6431, FR-6432, FR-6436
- [ ] T046 [US7] `convocacao/application/desfechar.py` e `fluxo.py`: `avisar` com a recusa
  `aviso_envio_desabilitado` antes de gravar, e o declarado `aviso` — FR-6430, FR-6438
- [ ] T047 [US7] `avisos/application/despacho.py`: a releitura da origem nova, a trilha de cada envio para
  `PENDENCIA` e `DESFECHO`, a origem `DESFECHO` fora da seleção com `AVISOS_DE_DESFECHO` desligada,
  `REVISAO_DA_FR_084_PELA_156`; e `comando.base_do_aviso`, `confirmar` (sem reenvio pela tela da
  `066`), `aviso.html` e `avisos_do_edital.html` com a origem nova — FR-6432, FR-6438
- [ ] T048 [US7] Gestão: a opção *"Avisar a pessoa por e-mail"* desmarcada, ou desabilitada sem endereço,
  com a ajuda da UX-623, no formulário do desfecho, no atalho e no lote; a mensagem *"Desfecho
  registrado. Aviso solicitado."*; o estado do aviso no cartão (`interface/conducao_da_convocacao.py`
  `avisos_por_raiz` sem origem fixa e `anotar` com a convocação desfechada) — FR-6430, FR-6436, FR-6445,
  UX-623
- [ ] T049 [US7] Guarda da FR-084: seis situações, três no despacho, e o teste da revisão da `156`
  (`tests/test_situacoes_de_mensagem.py`) — FR-6429, R-013
- [ ] T050 [US7] Testes de integração (`tests/integration/avisos/test_aviso_do_desfecho.py`): gravação,
  recusa com cada chave desligada, despacho que envia, interrompe e pula, janela, sem endereço, trilha
  sem endereço, orçamento de consultas do cartão, e as telas do portal iguais com a habilitação ligada e
  desligada — FR-6439, SC-2125, SC-2126, SC-2127, SC-2131

---

## Fase 11 — Fechamento

- [ ] T051 Integrar o que da `152`, da `154` e da `150` já estiver na `main`, resolvendo conflitos sem
  perder requisito de nenhuma; registrar no PR onde os arquivos se cruzam — R-015
- [ ] T052 `cd backend && make lint check test-pg` com `DB_NAME` próprio, e o provisionamento `N de 60`
- [ ] T053 Verificação no navegador pelo [quickstart](quickstart.md): aceite, desistência e não
  atendimento a 390 px e em tela larga; o cartão com o pedido; o aviso no terminal do `despachar_avisos`
- [ ] T054 README (linha da 156 e a contagem de tabelas protegidas); `doc/implantacao-em-producao-ubuntu.md`
  com `AVISOS_DE_DESFECHO` desligada e as pendências PI-1 a PI-6 como condição de ligá-la, sem afirmar
  quem valida nem se o pedido existe (FR-6440); `verificacao.md` com as evidências, e o PR com dependências e pendências (PI-1 a PI-6, SC-2121) explícitas, sem merge

---

## Dependências

- **Fase 2** antes de todas as histórias.
- **US2** antes da **US1** (a US1 reusa o porquê em duas camadas) e da **US3** (o mesmo `<details>`);
  a exceção é a T012, que espera a T016.
- A **FR-6441** (as revisões nas specs de origem) está cumprida no PR #488, e não tem tarefa.
- **US4** é independente; a T020 e a T025 tocam os mesmos modelos de mensagem, e se fazem em sequência.
- **US5** antes da **US6** (a homologação lê o pedido).
- **US7** depende da **US6** só na T046 e na T048 (o atalho e o lote também oferecem a opção).
- **Fase 11** por último.

## Paralelismo

- T002, T004 e T005 entre si.
- Dentro da US4, T019 e T020.
- T044 com qualquer tarefa fora de `avisos/`.
- US4, US8 e o começo da US5 (T027 a T029) podem andar ao lado da US2.

## Estratégia

1. **MVP**: Fases 1 e 2, US2 e US1 — o achado 18 e a parte de portal do achado 07, sem migration.
2. US4 e US8 — contato e mensagem.
3. US5 e US6 — o achado 17, com as duas tabelas novas.
4. US7 — o aviso, implementado e desligado; ligá-lo em produção depende de PI-1 a PI-6.
