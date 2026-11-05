# Tasks: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/recorte-excedente.md](contracts/recorte-excedente.md),
[quickstart.md](quickstart.md)

**Tests**: pedidos. O plano tem uma validação por camada, e a constituição exige rastreabilidade.
Cada história começa pelos testes, que falham antes da implementação.

**Caminhos**: relativos à raiz do repositório. `PS` abrevia `backend/processo_seletivo` e `T` abrevia
`backend/tests`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 a US5 da spec

---

## Phase 1: Setup

- [x] T001 **Dispensada pelo usuário em 05/11/2026** (*"esquece a VM"*); o roteiro fica no quickstart, sem execução. Texto original: Rodar o levantamento só de leitura do quickstart, passo 0, no `manage.py shell` da instalação do Cefor, e registrar a saída (contagens e identificadores, nenhum nome) em `specs/122-recortes-alinhados-no-sorteio/verificacao.md`. Sem acesso à VM, a tarefa fica aberta e é dita no PR. **Com publicação excedente, parar e apresentar ao usuário** Edital, marco, origem e quantidade, sem ampliar o escopo (13ª decisão)
- [x] T002 [P] Listar os testes que mudam de expectativa (research R-9): `grep -rn "generalCompetitionModalityId\|lista própria\|divulgar o resultado" backend/tests/`, e registrar em `specs/122-recortes-alinhados-no-sorteio/verificacao.md` cada arquivo, o caso e a expectativa nova, antes de tocar em qualquer um
- [x] T003 [P] Criar o helper de acervo excedente em `T/fixtures_recorte_excedente.py`. Ele grava, por `objects.create` (append-only aceita INSERT), uma relação, um sorteio, um ato e, opcionalmente, uma publicação no recorte da Modalidade apontada, citando uma versão dada. O caminho dos comandos estará fechado depois da US1, e o helper é a única forma de reproduzir o acervo. Registrar o helper em `T/conftest.py` como fixtures `acervo_nascido` e `acervo_tornado`

---

## Phase 2: Foundational (bloqueia todas as histórias)

**Propósito**: o papel do recorte e a origem do registro num lugar só (plan §1).

- [x] T004 [P] Escrever `T/unit/editais/test_papel_do_recorte.py`: ampla nula → `OPERACIONAL`; Modalidade não apontada → `OPERACIONAL`; a apontada → `EXCEDENTE`; identidade fora do Perfil → `AUSENTE`; uma Modalidade chamada "Ampla Concorrência", com código "AC" e **sem** apontamento → `OPERACIONAL` (FR-3894); `exigir_recorte_operacional` levanta `list_is_general_competition_alias` 422 com a frase do contrato §1 e não levanta nos outros papéis
- [x] T005 [P] Escrever em `T/unit/editais/test_papel_do_recorte.py` os casos de `origem_do_registro`: versões [v1 aponta AC] → `NASCIDO`; [v1 sem apontamento, v2 aponta AC] → `TORNADO` com v2; [v1 sem, v2 aponta, v3 retira, v4 aponta] para registro de v1 → `TORNADO` com v2 (T5 da R-11)
- [x] T006 Implementar `papel_do_recorte`, `exigir_recorte_operacional`, `origem_do_registro` e as frases do contrato §1 e §2 em `PS/editais/domain/recortes.py`, definindo `OPERACIONAL` como pertencer a `recortes_do_perfil`. As frases são constantes do módulo, e a docstring diz que esta feature estende a derivação única da `034`

**Checkpoint**: T004 e T005 verdes.

---

## Phase 3: User Story 1 — O sorteio trabalha nos três recortes (P1) 🎯 MVP

**Goal**: a tela e os comandos do sorteio usam os recortes operacionais (FR-3893, FR-3895 a FR-3898).

**Independent Test**: num Edital novo com AC apontada, conduzir o sorteio até o fim e contar três
recortes em cada tela; pedidos diretos no recorte de AC recusados.

### Tests

- [x] T007 [P] [US1] Escrever `T/integration/sorteios/test_recorte_excedente_recusado.py`: `publicar_relacao` com `lista_id` de AC recusa com o código, sem gravar relação nem `RegistroAuditoria`; `constituir_sorteio` sobre uma relação de AC já congelada (do `acervo_nascido`, sem sorteio) recusa com o código (FR-3898, T6); o pedido repetido com a chave de idempotência de um aceito antes devolve o desfecho anterior; a emissão computada pedida com AC grava na ampla (FR-3900); suceder uma relação de AC com motivo e constituir sorteio com `sorteio_anterior_id` de AC são recusados (D-006); FR-3897, SC-1169
- [x] T008 [P] [US1] Escrever em `T/interface/test_recortes_alinhados.py` a tela do sorteio: três recortes, ampla primeiro, nenhum bloco de AC, a frase da FR-3895; a prévia do sorteio (`098`) sem a frase *"ganha uma lista própria"*; `marcos_sorteados_em_todos_os_recortes` responde "sorteado" com os três sorteados e AC sem nada (FR-3896); casos-limite: apontamento para Modalidade sem inscrito (sem bloco, com a frase) e Perfil sem apontamento (a Modalidade "AC" é recorte como as outras)

### Implementation

- [x] T009 [US1] Em `PS/sorteios/application/previa.py`, `recortes_do_marco`: montar `listas` de `recortes_do_perfil`, preservando o rótulo da ampla de hoje, e devolver ao lado `registros_excedentes` (vazio por enquanto; T029 o preenche)
- [x] T010 [US1] Chamar `exigir_recorte_operacional` em `PS/sorteios/application/relacao.py`, `publicar_relacao`, logo depois de `effective_version` e antes de `exigir_metodo`, dentro da trava
- [x] T011 [US1] Chamar `exigir_recorte_operacional` em `PS/sorteios/application/sorteio.py`, `constituir_sorteio`, depois de ler a relação e antes de `_recusar_o_que_nao_pode_sortear`, sobre a versão vigente
- [x] T012 [P] [US1] Reescrever em `PS/interface/previa_do_sorteio.py`, `_frases_da_semente`, a frase da Modalidade apontada: ela não tem sorteio próprio, porque a ampla já reúne todos os inscritos (FR-3895)
- [x] T013 [US1] Em `PS/interface/templates/interface/sorteio.html` e na view do sorteio (`PS/interface/views.py`, em torno da linha 10923), mostrar a frase da FR-3895 quando o Perfil aponta uma Modalidade, e garantir que nenhum botão de congelar, sortear ou publicar seja desenhado para lista fora dos recortes operacionais
- [x] T014 [US1] Atualizar os testes do sorteio e da prévia do sorteio listados no T002 que esperavam o bloco de AC, citando esta spec no commit

**Checkpoint**: T007 e T008 verdes; a US1 está entregue sozinha.

---

## Phase 4: User Story 2 — Quem divulga encontra cada recorte pelo nome (P1)

**Goal**: um caminho de divulgação por marco, o quadro levando à prévia, e a divulgação do excedente
recusada (FR-3899, FR-3901, FR-3906 a FR-3908).

**Independent Test**: com `paula.publicadora` (papel `publicador`, sem comissão), da página do Edital à
prévia de cada recorte em dois cliques; o marco sem ato sem caminho.

### Tests

- [x] T015 [P] [US2] Escrever em `T/interface/test_recortes_alinhados.py`: a página do Edital com três atos operacionais e um excedente mostra **um** *divulgar o resultado* por marco, para `interface:marco#divulgacao`; com `paula.publicadora` o caminho leva ao quadro, e cada célula de divulgação *falta* leva à prévia do ato vigente daquele recorte, em dois cliques a partir da página (SC-1167); *feito* leva a Resultados divulgados; marco sem ato não mostra o caminho (FR-476 da `033`); marco por classificação computada recebe o mesmo caminho único (caso-limite); a contagem de consultas da página do Edital não cresce
- [x] T016 [P] [US2] Escrever em `T/integration/sorteios/test_recorte_excedente_recusado.py`: `publicar_resultado` sobre o ato do `acervo_nascido` recusa com o código, sem gravar publicação; uma publicação excedente gravada antes continua sem sucessora e com o mesmo documento (FR-3899)
- [x] T017 [P] [US2] Escrever em `T/interface/test_recortes_alinhados.py` três das quatro portas: tela do sorteio, tela do ato (`ato_ordenacao.html`) e prévia aberta por endereço direto não oferecem publicar o ato excedente (a quarta, o destino da Supervisão, é provada na T024, porque fecha com a T025); a prévia mostra a frase da origem no lugar do botão (FR-3901, FR-3904)

### Implementation

- [x] T018 [US2] Chamar `exigir_recorte_operacional` em `PS/divulgacao/application/publicar.py`, `publicar_resultado`, depois de ler o ato, sobre a versão vigente
- [x] T019 [US2] Em `PS/interface/views.py`: `_marcos_publicados` deixa de chamar `atos_vigentes_por_marco`; `_destinos_do_marco` recebe se o marco tem ordem pelo `resumo["ordem"]` e acrescenta um único destino *divulgar o resultado* para `reverse("interface:marco", …) + "#divulgacao"` quando o ator divulga. Atualizar as docstrings, que contam a história do ACH-40, com o motivo da troca
- [x] T020 [P] [US2] Acrescentar `id="divulgacao"` à parte de divulgação do quadro e dos gestos em `PS/interface/templates/interface/marco.html`
- [x] T021 [US2] Em `PS/interface/conducao_do_marco.py`, `_celula_da_publicacao`: a célula *falta* (com ato) e *obsoleto* apontam para `interface:previa-de-publicacao` do ato vigente quando o ator divulga; *feito* continua em `publicacoes-do-marco` (contrato §5)
- [x] T022 [US2] Em `PS/interface/acoes.py` e `PS/interface/templates/interface/previa_de_publicacao.html` (e na view da prévia), para ato de papel vigente `EXCEDENTE`: nenhuma ação de publicar, e a frase da origem (`origem_do_registro`) no lugar do botão
- [x] T023 [US2] Atualizar `T/interface/test_destinos_do_edital.py`: `_divulgacao` passa a ser o caminho do quadro, e o teste do Publicador puro segue até a prévia pelo quadro; o docstring cita a FR-474 da `033` e a FR-3907

**Checkpoint**: T015 a T017 verdes.

---

## Phase 5: User Story 3 — A Supervisão cobra só o que existe (P1)

**Goal**: os três sinais sobre os recortes operacionais, também no sorteio (FR-3909, FR-3910).

**Independent Test**: com `acervo_nascido` e os três recortes divulgados e apurados, nenhum sinal do
marco.

- [x] T024 [P] [US3] Escrever `T/integration/supervisao/test_sinais_sem_recorte_excedente.py`: com `acervo_nascido`, nenhum `UX-004`, `UX-065` nem `UX-066` sobre AC, para a presidência e para `paula.publicadora`; nenhum sinal oferece a prévia do ato excedente, que é a quarta porta da FR-3901; um ato operacional não divulgado continua gerando `UX-066` com destino na prévia dele (FR-3910); Edital encerrado ou cancelado continua sem sinal (caso-limite); o orçamento de consulta da Supervisão não cresce; SC-1168
- [x] T025 [US3] Em `PS/interface/supervisao.py`, `listas_do_marco`: retirar o ramo `sorteia` e devolver os recortes de `recortes_do_perfil` para todo marco; reescrever a docstring citando esta feature no lugar da decisão de escopo do sorteio da `034`

**Checkpoint**: T024 verde.

---

## Phase 6: User Story 4 — O acervo excedente continua consultável e explicado (P2)

**Goal**: a seção de histórico, a marca nas listas e o relatório (FR-3902 a FR-3905, FR-3916).

**Independent Test**: com `acervo_nascido` e `acervo_tornado`, percorrer tela do sorteio, tela do ato,
Resultados divulgados, relatório do Edital e páginas públicas de verificação.

### Tests

- [x] T026 [P] [US4] Escrever em `T/interface/test_recortes_alinhados.py` (FR-3903, FR-3904): a tela do sorteio mostra a seção de histórico depois dos recortes, com a frase de **nascido** para `acervo_nascido` e a de **tornado** com o número da Retificação para `acervo_tornado`, sem nenhum botão; Resultados divulgados marca a publicação excedente; Edital sem marco por sorteio não mostra a seção; ator que não alcança o marco não vê o registro; o orçamento de consulta da tela do sorteio é medido e fixado
- [x] T027 [P] [US4] Escrever em `T/interface/test_recortes_alinhados.py` o relatório do Edital: três linhas de lista; a publicação excedente numa linha marcada *fora da operação atual*, fora do *definitivo em todas*; o ato excedente não divulgado ausente (FR-3916)
- [x] T028 [P] [US4] Escrever em `T/portal/test_recorte_excedente_publico.py`: as páginas públicas de verificação da relação, do sorteio e do resultado do acervo devolvem o mesmo conteúdo antes e depois da mudança, comparado depois de normalizar os identificadores de sessão e CSRF (FR-3905, SC-1170); e o portal não muda (FR-3915): o bloco de sorteio da página pública do Edital (`portal/test_sorteio_na_pagina_do_edital.py` como molde) e o acompanhamento de quem está numa publicação excedente devolvem o mesmo conteúdo antes e depois

### Implementation

- [x] T029 [US4] Em `PS/sorteios/application/previa.py`, preencher `registros_excedentes`: relações, sorteios, atos e publicações do marco com papel vigente `EXCEDENTE`, uma consulta por espécie, com `origem_do_registro` sobre as versões do Edital lidas uma vez
- [x] T030 [US4] Desenhar a seção de histórico em `PS/interface/templates/interface/sorteio.html`, só de consulta, com a frase de cada registro e o link para a tela de cada um; estilo, se precisar, em folha (CSP)
- [x] T031 [P] [US4] Marcar a publicação excedente com a frase da origem em `PS/interface/templates/interface/publicacoes_do_marco.html` e na view dela, e na tela do ato (`ato_ordenacao.html`)
- [x] T032 [P] [US4] Em `PS/interface/relatorio_do_edital.py`: linhas de lista pelos recortes operacionais; publicação excedente numa linha marcada e fora de `definitivo_em_todas`; ato excedente não divulgado fora

**Checkpoint**: T026 a T028 verdes.

---

## Phase 7: User Story 5 — A Retificação do apontamento não reabilita nem condena em silêncio (P2)

**Goal**: a causa `papel_do_recorte` e a matriz temporal (FR-3911 a FR-3913).

**Independent Test**: T1 a T7 da research R-11.

- [x] T033 [P] [US5] Escrever `T/integration/classificacao/test_recortes_alinhados_temporal.py` com T1 a T7 da R-11, um teste por linha, cada um com uma Retificação real do apontamento pelo helper dos testes de Retificação; em T2 e T3, a prévia do ato antigo recusa por obsolescência com a causa `papel_do_recorte`, e congelar relação nova de AC com motivo é aceito
- [x] T034 [US5] (FR-3912) Em `PS/classificacao/application/selectors.py`: acrescentar a divergência `papel_do_recorte` (contrato §3) em `_divergencias_do_sorteio` e no ramo computado de `estado_do_marco`, quando o papel na versão do ato difere do papel na vigente e o vigente é `OPERACIONAL`
- [x] T035 [US5] Confirmar que `PS/interface/supervisao.py`, `candidato_a_obsoleto`, admite o ato de papel mudado (versão citada diferente da vigente) e que a condução do marco mostra *obsoleto*; se não admitir, acrescentar o caso ao filtro barato sem novo recálculo

**Checkpoint**: T033 verde.

---

## Phase 8: Polish & Cross-Cutting

- [x] T036 [P] Acrescentar as telas com frase nova (sorteio, prévia do sorteio, prévia de publicação, Resultados divulgados, tela do ato) à lista literal de `T/test_vocabulario_da_composicao.py` (ou ao arquivo da varredura que a contém), e ajustar as frases se a varredura acusar termo
- [x] T037 [P] Escrever `T/navegador/test_jornada_dos_recortes.py` com a jornada da SC-1165 (quickstart, passo 2), presidência e Publicador puro, sobre `acervo_nascido`
- [x] T038 [P] Escrever em `T/interface/test_recortes_alinhados.py` a prova da SC-1166: sobre um Edital com AC apontada e `acervo_nascido`, contar os recortes operacionais na tela do sorteio, no quadro da condução, no resumo da página do Edital, na tela da ocupação, na Supervisão e no relatório do Edital, e exigir três em todas
- [x] T039 Escrever `specs/122-recortes-alinhados-no-sorteio/rastreabilidade.md`: uma linha por FR-3893 a FR-3916 e SC-1165 a SC-1171, uma por caso-limite da spec e uma por caso temporal T1 a T7, cada uma com o teste que a prende
- [ ] T040 Percorrer à mão a jornada da SC-1165 (quickstart, passo 2) num banco de demonstração com acervo excedente, com a presidência e o Publicador puro, e registrar em `specs/122-recortes-alinhados-no-sorteio/verificacao.md` o que se viu em cada passo, com capturas
- [x] T041 Atualizar a linha da `122` na tabela de incrementos do `README.md` para implementada, e a Visão do Sistema, se a página do Edital ou a tela do sorteio estiverem descritas lá *(A Visão do Sistema se atualiza no merge, como o usuário pediu em 04/11.)*
- [x] T042 Rodar `cd backend && uv run python manage.py makemigrations --check --dry-run` (nenhuma migration nasce, FR-3914) e `cd backend && make lint check test-pg` e registrar em `specs/122-recortes-alinhados-no-sorteio/verificacao.md` o total, os pulados e o tempo; uma falha do teste de tempo da ocupação se mede isolada antes de ser tratada como regressão (CLAUDE.md)

---

## Dependencies & Execution Order

- **Setup (T001–T003)**: T001 foi dispensada pelo usuário em 05/11/2026 e não bloqueia mais nada. T003 bloqueia todo teste que usa acervo.
- **Foundational (T004–T006)**: bloqueia todas as histórias.
- **US1 (T007–T014)**: depende da Foundational. É o MVP: fecha a origem do defeito.
- **US2 (T015–T023)**: depende da Foundational. A prévia do T022 usa a frase da origem (T006).
- **US3 (T024–T025)**: depende da Foundational; independente de US1 e US2.
- **US4 (T026–T032)**: depende de T009 (US1), que cria `registros_excedentes`.
- **US5 (T033–T035)**: depende da Foundational e, para T2 e T3, das recusas da US1 (T010).
- **Polish**: depois das histórias. T038 depende de US1 a US4; T040, de todas.
- **T024 (US3)** prova a quarta porta da FR-3901, e por isso a FR-3901 só fecha com US2 **e** US3.

### Parallel Opportunities

- T002 e T003; T004 e T005.
- Depois da Foundational, US1, US2 e US3 tocam arquivos diferentes, salvo `T/interface/test_recortes_alinhados.py`, em que cada história escreve uma classe própria.
- Dentro da US4: T027, T028, T031 e T032.

### Parallel Example: User Story 2

```text
T015  T/interface/test_recortes_alinhados.py (página do Edital e quadro)
T016  T/integration/sorteios/test_recorte_excedente_recusado.py (recusa de divulgar)
T020  PS/interface/templates/interface/marco.html (âncora)
```

## Implementation Strategy

1. **MVP = Setup + Foundational + US1.** O sorteio deixa de produzir a lista excedente: nenhum Edital novo cria acervo.
2. **US2 e US3**, que são o que o operador vê: um caminho por marco e a Supervisão sem cobrança.
3. **US4 e US5**, o acervo e a temporalidade.
4. **Polish**, com a suíte inteira contra PostgreSQL antes do PR de implementação.
