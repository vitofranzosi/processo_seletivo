# Tasks: Minhas atividades

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md) e
[quickstart.md](quickstart.md).

Os caminhos são relativos à raiz do repositório. "M" é `backend/processo_seletivo/`, e "T" é
`backend/tests/`.

**Implementação autorizada pelo usuário em 12/11/2026.** T002, T036 e T037 ficam com a sessão que pediu a implementação e com a validação humana.

**Os testes são pedidos pela spec**, do SC-2271 ao SC-2280. Em cada história, o teste vem antes da
implementação e deve falhar primeiro.

**Incremento A**: Phases 1 a 8. **Incremento B (R-009)**: Phase 9, num PR próprio.

## Phase 1: Setup

- [X] T001 Cortar a branch da implementação a partir da `main`, com `specs/160-minhas-atividades/` já mergeada, e exportar `SPECIFY_FEATURE_DIRECTORY=specs/160-minhas-atividades`; conferir `manage.py migrate --check` e o banco de teste próprio da worktree (`DB_NAME`)
- [ ] T002 [P] *(feitas pela sessão que pediu a implementação)* Capturas "antes" de `/gestao/minhas-etapas` para a presidência, o avaliador e o Gestor, a 1280 px e a 375 px, em `specs/160-minhas-atividades/capturas/antes/`

## Phase 2: Foundational — a leitura (bloqueia todas as histórias)

- [X] T003 [P] Teste unitário, sem banco, das funções puras (FR-6859, FR-6861 a FR-6870) em `T/unit/interface/test_atividades.py`. Com `Providencia` montadas à mão, ele cobre:
  - o filtro da base (R-003);
  - o agrupamento entre Editais, só para o ato sem dígito (R-006, FR-6865); e o das esperas pelo texto inteiro, com a data, em que datas diferentes não se juntam (FR-6870);
  - a ordem *Obsoleto* → *Pendente* → Edital mais antigo → índice de emissão, que ignora `ate` (R-007, FR-6866);
  - a fase (R-008);
  - a linha de avaliação com a frase de `ato_de_avaliar`.
- [X] T004 [P] Expor `ato_de_avaliar(n)` em `M/interface/andamento.py`, usada por `situacoes_da_etapa` e `_avaliar_minhas` no lugar da f-string, sem mudar o texto (R-005)
- [X] T005 Criar `M/interface/atividades.py` com as estruturas `Linha`, `Grupo` e `Atividades` (data-model) e as funções puras:
  - `filtrar_por_base(itens, base, perfis_alocados)`;
  - `linhas_de_avaliacao(atribuicoes, carga)`;
  - `agrupar_entre_editais(linhas)`;
  - `ordenar(grupos)`.

  Usar `providencias.agrupar` sobre `nivel_1.brutas` para manter a ordem de emissão (R-007). Até aqui o T003 passa.
- [X] T006 Em `M/interface/atividades.py` (FR-6854 a FR-6858, FR-6874), a leitura `ler(ator, *, vinculos, atribuicoes, carga, agora=None)`:
  - os Editais presididos e os da conferência, em consultas de número fixo (R-002), reaproveitando `vinculos` de `comissoes_da_pessoa`;
  - `andamento.do_edital` em cada um, e o `None` vira `nao_lidos` (R-004);
  - o filtro, a avaliação pela carga, o agrupamento e a ordem;
  - `preside` e `gestor` (`ator.can(PERMISSAO_SISTEMICA)`).

## Phase 3: US1 — a presidência vê o que é dela (P1) 🎯 MVP

**Goal**: "Para fazer agora" com os atos SUA da presidência de todos os Editais presididos, agrupados e com link.

**Independent Test**: com um certame de `T/fixtures/andamento.py`, a presidente vê na página cada célula SUA de condução do Centro, com o mesmo texto e link, e "Presidência".

- [X] T007 [P] [US1] Teste de coerência em `T/interface/test_minhas_atividades_coerencia.py`, no molde de `T/interface/test_andamento_coerencia.py` (SC-2271, FR-6859, FR-6860). Roda sobre os certames de `T/fixtures/andamento.py` e sobre os cenários de `T/fixtures/treinamento.py` que têm atos da presidência, um cenário por teste. Ele verifica três coisas:
  - toda linha da página é uma célula `grupo == SUA` de `do_edital` do mesmo Edital, com o mesmo `ato` e `url`;
  - toda célula SUA de condução ou conferência (fora `FORMALIZACAO`, `RECURSO`, `PUBLICA`) está na página;
  - o GET de cada link mostra o controle habilitado, como o SC-1230 da `127`.
- [X] T008 [P] [US1] Testes de jornada em `T/interface/test_minhas_atividades.py` (FR-6861, FR-6863, FR-6874):
  - a presidente vê as linhas, com "Presidência";
  - o ato praticado some na leitura seguinte;
  - um Edital forçado a falhar (`_Leitor.andamento` levantando, por monkeypatch) é dito, com link, os outros continuam, e a frase de "nada" não aparece (SC-2276);
  - Processo encerrado e Edital não publicado não são lidos (FR-6855);
  - a presidente que também tem `resultado:publicar` não vê "Publicar o resultado" em "Para fazer", e a nota de cobertura diz onde ele está (FR-6862, D-004);
  - quem preside e está alocado à conferência no mesmo Edital tem uma linha só.
- [X] T009 [P] [US1] Teste do agrupamento com dois Editais iguais em `T/interface/test_minhas_atividades.py`: a mesma "ordem de lista vazia" vira uma linha com "Ver os 2" e dois links; "Convocar 3 titulares" em dois Editais são duas linhas (SC-2275).
- [X] T010 [US1] `minhas_etapas` em `M/interface/views.py` chama `atividades.ler(...)` com os `vinculos`, as `atribuicoes` e a `carga` que já lê, e põe `atividades` no contexto.
- [X] T011 [US1] (FR-6867) Parcial novo `M/interface/templates/interface/_atividade.html`: uma linha ou um grupo, com a situação em palavra, o ato, o lugar, a fase, a base e o botão ou `details.editais-do-grupo` (contrato, seção 1; UX-713, UX-715).
- [X] T012 [US1] Em `M/interface/templates/interface/minhas_etapas.html` (FR-6883: as seções nomeadas pela relação):
  - a seção "Para fazer agora", com a contagem no título (UX-711);
  - o aviso dos não lidos;
  - a nota de cobertura (FR-6871, FR-6872), por uma constante de `atividades.py`;
  - os cartões e "Comissões que você integra", depois (FR-6875).
- [X] T013 [US1] Regras das classes novas em `M/interface/static/interface/telas/minhas-etapas.css`: sem `nowrap` que alargue o cartão, e o botão abaixo do texto a 375 px (UX-714). Fechar `@media` com `;` antes de `}}`, como pede `test_estaticos`.

**Checkpoint**: a presidência tem a página; T007 a T009 passam.

## Phase 4: US2 — o avaliador, sem a derivação (P1)

**Goal**: a avaliação pela carga, com "Alocação", e nenhuma chamada à derivação para quem não preside.

**Independent Test**: um membro alocado vê "Avaliar N inscrições" com o link da Mesa, e um espião em `do_edital` conta zero.

- [X] T014 [P] [US2] Testes em `T/interface/test_minhas_atividades.py` (FR-6864):
  - o membro vê "Avaliar N inscrições", com "Alocação" e o link da Mesa;
  - o N é o do cartão;
  - o membro sem pendência lê a frase da FR-6873 e a nota de cobertura.
- [X] T015 [P] [US2] Teste de custo em `T/performance/test_minhas_atividades_em_escala.py` (R-012, SC-2272, FR-6856, FR-6877):
  - o membro com 1 e com 11 comissões tem o mesmo número de consultas;
  - um espião em `andamento.do_edital` registra zero chamadas.
- [X] T016 [US2] Na coerência (T007), o caso do avaliador num Edital presidido por outra pessoa. A linha de avaliação corresponde à célula `AVALIAR` do Centro pela Etapa e pelo link, e pelo texto quando a Etapa não tem `carentes` (D-010).
- [X] T017 [US2] Na terceira seção de `minhas_etapas.html`, o título "Suas Etapas de avaliação · N" e os estados vazios revistos: quem preside e os demais (FR-6876; a FR-2827 da `104`). Atualizar a asserção do texto do estado vazio em `T/interface/test_acoes_disponiveis.py`, `T/acceptance/test_comissao_e_alocacao.py` e `T/authorization/test_acesso_a_etapa.py`.

## Phase 5: US3 — o Gestor (P1)

**Goal**: a condução só onde o Gestor preside; a conferência só nos Perfis alocados.

**Independent Test**: o Gestor que preside um Processo vê os atos dele, e o que não preside vê zero.

- [X] T018 [P] [US3] Testes em `T/interface/test_minhas_atividades.py` (SC-2273, FR-6858):
  - o Gestor que preside vê os atos do Processo dele, com "Presidência";
  - o Gestor sem presidência vê zero atos de condução, e o espião conta zero chamadas à derivação;
  - a nota diz "O que você pode fazer por permissão de gestão…".
- [X] T019 [P] [US3] Teste em `T/interface/test_minhas_atividades.py` (FR-6857): o Gestor alocado à conferência de **um** Perfil, sem presidir, vê só a conferência daquele Perfil, com "Alocação", e nenhum outro ato do Edital. Montar a alocação pelo comando da `115`.
- [X] T020 [US3] Em `atividades.ler`, a frase do Gestor na cobertura, e o filtro por `perfil_id` nos Editais lidos pela conferência (R-003), se o T019 o acusar.

## Phase 6: US4 — as esperas (P2)

**Goal**: "Em espera" recolhida, com a data dita pela origem e o *Impedido* com quem resolve.

**Independent Test**: num Edital com prazo de recurso em curso, a espera está na seção fechada, e não em "Para fazer".

- [X] T021 [P] [US4] Testes em `T/interface/test_minhas_atividades.py` (SC-2277, FR-6868 a FR-6870):
  - a espera está em `details.em-espera` fechado, e nunca em "Para fazer";
  - toda data vem com a origem;
  - nenhum texto da página diz "atrasado" ou "seu prazo";
  - o *Impedido* diz quem resolve;
  - "Publicar o resultado definitivo" esperando o prazo de recurso, com a mesma data em dois Editais, é uma linha só, e com datas diferentes são duas;
  - os Editais lidos só pela conferência não têm espera.
- [X] T022 [US4] A seção "Em espera nos seus Editais" em `minhas_etapas.html`: `details` com `summary` e contagem (UX-712), e o parcial `_atividade.html` no modo espera, sem link de ato. Se algum texto de espera da derivação não disser a origem da data, registrar como achado em `specs/160-minhas-atividades/verificacao.md`, sem mudar a frase da `127`.

## Phase 7: US5 — o nome muda, o caminho fica (P2)

**Goal**: "Minhas atividades" em toda a gestão, com o mesmo endereço.

**Independent Test**: nenhuma tela da gestão diz "Minhas Etapas", e `/gestao/minhas-etapas` e a Mesa respondem como antes.

- [X] T023 [P] [US5] Teste em `T/interface/test_minhas_atividades.py` (SC-2278, FR-6852):
  - as telas da barra, a página, a Etapa e a Mesa não contêm "Minhas Etapas" e contêm "Minhas atividades";
  - `reverse("interface:minhas-etapas") == "/gestao/minhas-etapas"`;
  - as rotas da Mesa respondem 200 ao avaliador alocado.
- [X] T024 [US5] O rótulo da `Secao` em `M/interface/navegacao.py`; o título, o `h1` e a trilha em `minhas_etapas.html`; as trilhas em `minha_etapa.html` e `mesa_inscricao.html`; "Ver minhas atividades" em `lista.html` (R-011, FR-6851).
- [X] T025 [US5] Atualizar a asserção do nome visível nos 11 arquivos de R-011, e só ela (a rota fica): `T/interface/test_politica_de_conteudo.py`, `test_paineis_e_telas_de_apoio.py`, `test_decisoes_da_etapa_4.py`, `test_andamento_do_edital.py`, `test_caminho_ate_a_mesa.py`, `test_lista.py`, `test_shell_da_gestao.py`, `test_telas_de_uso_diario.py`, `test_auditoria_passagem_da_retificacao.py`, `T/integration/resultados/test_carga_nas_etapas.py` e `T/authorization/test_acesso_a_etapa.py`.
- [X] T026 [P] [US5] "Minhas atividades" em `doc/cenarios-de-treinamento/guia-da-equipe.md` e `doc/manual/00-arquitetura-do-manual.md`. O guia passa a mandar a presidência começar pela página, sem abrir Edital por Edital (FR-6853). As specs e os estudos antigos ficam.

## Phase 8: US6 — a nota da faixa da Lista (P3)

**Goal**: a nota aponta para a página, sem número, e a Lista não paga a derivação.

**Independent Test**: a nota, com itens e vazia, tem o link; o teste de custo da Lista passa sem mudar o orçamento.

- [X] T027 [P] [US6] Testes em `T/interface/test_organizacao_da_lista.py` (SC-2279, FR-6880, FR-6881):
  - as famílias de `FAMILIAS` passam a dizer onde está cada uma;
  - a nota e a frase vazia contêm `FORA_DA_FAIXA` e o link `a.para-minhas-atividades`;
  - a faixa não tem contagem da página.

  Conferir também `T/unit/interface/test_trabalho_do_ator.py`, se ele fixar a frase.
- [X] T028 [US6] `FORA_DA_FAIXA` em `M/interface/trabalho.py` passa a dizer onde está cada família (R-010). O link vem depois da constante em `M/interface/templates/interface/_acoes_disponiveis.html`, e a regra dele em `telas/lista.css`.
- [X] T029 [US6] Rodar `T/performance/test_trabalho_em_escala.py` e `T/performance/test_lista_em_escala.py` sem mudar os tetos (FR-6882).

## Phase 9: Incremento B — a versão vigente uma vez por requisição (FR-6879, R-009)

- [X] T030 [P] Teste em `T/unit/publicacoes/test_versao_da_requisicao.py`:
  - dentro de `versao_vigente_da_requisicao()`, duas chamadas com o mesmo `edital_id` e `at` `None` (ou o instante de abertura) fazem uma consulta;
  - com outro `at`, consultam de novo;
  - fora do contexto, nada é memorizado.
- [X] T031 `versao_vigente_da_requisicao()` com `contextvars` em `M/publicacoes/application/selectors.py`, e `effective_version` consultando a memória só nesse caso (R-009).
- [X] T032 Abrir o contexto em volta da montagem em `minhas_etapas` e na view do detalhe do Edital (o Centro), em `M/interface/views.py`, só em GET.
- [X] T033 Teste em `T/performance/test_minhas_atividades_em_escala.py` e `T/performance/test_andamento_em_escala.py` (SC-2280):
  - os itens da página e do Centro são os mesmos com e sem o contexto;
  - o custo por Edital presidido cai;
  - baixar `TETO_POR_EDITAL` e os tetos do Centro para o medido, com folga.

## Phase 10: Polish

- [X] T034 (FR-6878) Medir na tarefa o custo da presidência com 0 e 1 Edital presidido, em `certame_s1` e em `certame_p1`, e fixar `TETO_POR_EDITAL` com folga de ~20% em `T/performance/test_minhas_atividades_em_escala.py` (R-012, SC-2274). O número medido vai para `verificacao.md`.
- [X] T035 [P] `specs/160-minhas-atividades/rastreabilidade.md`, com uma linha por identificador em negrito da spec, FR-6851 a FR-6884, SC-2271 a SC-2281 e UX-711 a UX-715, cada um com o teste ou a tarefa que o cobre (`test_a_matriz_de_rastreabilidade_cobre_todo_requisito_da_feature`)
- [ ] T036 [P] *(feitas pela sessão que pediu a implementação)* Capturas "depois", nas mesmas identidades e larguras do T002, em `specs/160-minhas-atividades/capturas/depois/`. Medir a 375 px que não há rolagem horizontal (UX-714).
- [ ] T037 *(pendente: o quickstart nos cenários de treinamento e o SC-2281, humano)* O quickstart inteiro num banco com os cenários de treinamento: a presidência lê os seus atos em menos linhas do que atos (SC-2275). Os achados vão para `specs/160-minhas-atividades/verificacao.md`. O SC-2281 fica pendente, como humano.
- [X] T038 `cd backend && make lint check test-pg`. Os dois passos do lint, a suíte inteira contra PostgreSQL e uma suíte de cada vez no cluster. A linha da `160` no `README.md` diz o estado.

## Dependencies & Execution Order

- **Phase 1** → **Phase 2** (T003 a T006) bloqueia tudo.
- **US1** (Phase 3) vem primeiro: cria a view, o parcial e a seção que as outras histórias estendem.
- **US2** e **US3** dependem só da US1, e podem andar juntas: os testes estão em arquivos ou casos diferentes, e o código em funções diferentes de `atividades.py`.
- **US4** depende da US1, pelo parcial e pelo template.
- **US5** independe da leitura. Pode correr junto da US1, mas toca `minhas_etapas.html`; feita depois da US1, evita conflito.
- **US6** independe das outras: toca `trabalho.py` e a Lista.
- **Phase 9** depende do incremento A mergeado.
- **Polish** por último. O T034 precisa da US1 e da US2; o T035, de todos.

## Parallel Examples

- Phase 2: T003 e T004 juntos (arquivos diferentes); depois T005 e T006.
- US1: T007, T008 e T009 juntos (os testes primeiro); depois T010 → T011 → T012 → T013.
- US2 e US3 juntas: T014, T015, T018 e T019.
- US5 e US6 juntas: T023, T026 e T027.

## Implementation Strategy

1. **MVP = Phases 1, 2 e 3**: a presidência já tem a página, e é onde está o ganho medido (20 atos em 11 Editais que hoje não aparecem em lugar nenhum).
2. Em seguida, a US2 e a US3: o custo do membro e o recorte do Gestor, sem os quais a página não pode ir para todos.
3. Depois, a US4, a US5 e a US6: as esperas, o nome e a Lista. Com elas, o incremento A fecha num PR.
4. O incremento B (Phase 9), num PR próprio, quando o A estiver na `main`.
