# Lote 7 — Achados avulsos e o registro de decisões conscientes

**Base:** `bb774d9` (= `origin/main` de 25/09/2026). Leitura de código, testes, specs e `doc/`; `gh` só leitura
(issue #117, lista de PRs). Nada foi executado (sem suíte, sem servidor, sem manage.py).
Datas de referência: auditoria em 25–26/09/2026.

**Atualização de 26/09:** depois da auditoria, a 044 entrou na `main` pelo #173 (`47876ad`), o achado
do `ValorDeFato` pelo #171, e a correção dele pelo #183 (`8e7c698`). Foram revistas as decisões nº 19 e
nº 21, o resumo das decisões com trabalho não executado, o NOVO-2 e a incerteza 2. As contagens da
Parte 1 não mudam: nenhum dos seus itens era da 044.

---

## Parte 1 — Achados avulsos

### achado-atribuicoes-repetidas-por-polo — o Edital declara as atividades uma vez; o sistema as guarda uma vez por polo
- Origem: `doc/achado-atribuicoes-repetidas-por-polo.md` (15/09/2026)
- Problema original: `duties`/`workload`/`compensation` (e requisitos comuns) moram em `PerfilVaga`, cuja identidade é o código-polo. Um Edital de 16 polos exige 16 cópias do mesmo texto: 16× na digitação, 16 blocos no PDF, 16 Alterações iguais numa Retificação, sem nada que confira a igualdade (tensão com o Princípio II). Defeito separável: o cabeçalho "Dos candidatos ao perfil Tutor Presencial:" repetido 9× e indistinguível.
- Recomendação original: cinco caminhos, sem escolher — (1) a Função como objeto normativo compartilhado; (2) "copiar de outro Perfil"; (3) agrupar na renderização (desaconselhado, inferência por igualdade de string); (4) polo como dimensão própria (P-5); (5) deixar como está. O cabeçalho "se conserta sozinho" incluindo o código.
- Rastro posterior: AX-13 (15/09, `auditoria-granularidade-normativa` §AX-13) registra o cabeçalho corrigido em `c0403a9`; AX-5/AX-6/AX-7 retomam o eixo e mostram divergência já acontecendo em regra executável; estudo de esforço 21/09 §6.2/§8/§13 E1 e E2 mede ~430 de ~530 interações sem informação nova no 140/2025; convergência 20/09 §16 ("Organização por Perfil/polo — pergunta aberta") e §21 ("Não abstrair polo antes de ter o Edital real de múltiplos polos na mão"); `decisao-recorte-documental.md` D5 (25/09) separa lote (tela) de mover propriedade para o Edital (E2) e **não decide E2**; 043 (25/09) implementa o caminho 2.
- Specs relacionadas: 043 (Duplicar Perfil, implementada em `0479f4e`); 044 (recorte documental, só spec na main); 026 (mutabilidade).
- Implementação encontrada: (a) cabeçalho: `_rotulo_do_perfil` compõe `LP01 — Tutor Presencial`; (b) caminho 2: operação Duplicar Perfil na etapa Perfis; (c) caminhos 1/4: nada.
- Evidência no código atual: `backend/processo_seletivo/publicacoes/infrastructure/pdf.py:1940-1952` (`_rotulo_do_perfil`, docstring cita o 140/2025) e `:1964-1990` (`_nomes_do_alcance`/`_titulo_do_grupo` usam o rótulo com código); `backend/processo_seletivo/interface/urls.py:111-113` (rota `fragmentos/perfil/<indice>/duplicar`); `backend/processo_seletivo/editais/models/perfis.py:33-35` (`duties`, `workload`, `compensation` continuam no Perfil); `backend/processo_seletivo/interface/retificacao.py:63,81` (`CAMPOS_PERFIL` com `duties` aplicado a cada Perfil); `backend/processo_seletivo/editais/domain/mutabilidade.py:244` (`("profiles","duties"): retificavel()`). `specs/043-duplicar-perfil/spec.md` §2 declara que "não reduz o documento publicado" e "não é mover conteúdo para o nível do Edital"; §5 registra TF-1 (propagação em massa) como futuro.
- Estado atual: **PARCIALMENTE RESOLVIDO**
- Ainda faz sentido?: parcialmente. O custo de **digitar** caiu (043) e o cabeçalho foi corrigido. O que resta — o PDF repetido e a Retificação em N cartões sem conferência de igualdade — é real, mas a solução estrutural (E2/Função/polo) é decisão de produto aberta e cara; a própria amostra mostra que nenhum Perfil diverge dos irmãos (estudo §13 E2), o que favorece "aplicar a todos" (TF-1) antes de um objeto novo. Observação: a condição da §21 da convergência ("ter o Edital real de múltiplos polos na mão") já está satisfeita — o estudo de 21/09 cadastrou o 140/2025 e o 28/2026.
- Lacuna residual: 16 cópias independentes do mesmo texto normativo; Retificação de texto comum = N Alterações; PDF de 27 p. com 34 tabelas (estudo §9-bis); nenhuma verificação de igualdade entre cópias. A 043 torna as cópias mais baratas de produzir — o risco de divergência que o achado previa aumenta, não diminui.
- Grupo do resíduo: **B**
- Impacto atual: Editais multipolo (4 de 5 da amostra) publicam documentos longos e caros de retificar; divergência silenciosa possível após Retificação parcial.
- Próxima ação sugerida: criar spec (decisão E2 do usuário primeiro; TF-1 da 043 é o candidato mais barato)
- Relações: AX-5, AX-6, AX-7, AX-13 (granularidade 15/09); P-5 (`achados-editais-externos.md`); estudo 21/09 §13 E1/E2, frente 2 e frente 4 da §15; convergência §16 "Organização por Perfil/polo"; ACH-60. Sintoma (texto repetido) → causa estrutural (granularidade única = código-polo).
- Confiança: alta — código e specs lidos; o que falta é decisão, não evidência.

### achado-duas-avaliacoes-sem-regra-de-combinacao — Etapa com `evaluationsPerRegistration` > 1 publica ato que não se consolida
- Origem: `doc/achado-duas-avaliacoes-sem-regra-de-combinacao.md` (21/09/2026)
- Problema original: o campo "Avaliações por inscrição" é oferecido sem teto e sem aviso; a validação de publicação (032) não o conhece; o Edital publica (ato imutável); a distribuição atribui 2 e dois avaliadores trabalham; a consolidação recusa a **Etapa inteira** com `REGRA_DE_COMBINACAO_AUSENTE` — e não existe campo para declarar a combinação. A saída (Retificar para 1) cai no segundo beco ("há 2 avaliações concluídas onde o Edital prevê uma").
- Recomendação original: (1) ensinar a 032 o campo — recusar ou avisar na publicação; (2) o `como-preencher` da etapa dizer o que > 1 produz; (3) só se a instituição usa dupla leitura, spec de regra de combinação publicada. **Não** afrouxar a recusa da consolidação.
- Rastro posterior: preâmbulo de 21/09 do relatório longitudinal (item 1, "aberto"); nenhum commit posterior tocou o tema (`git log` de `validation.py`, `_etapa.html`, `compor_etapas.html`).
- Specs relacionadas: 012 (FR-007/D-007, o campo), 013 (FR "combinação de duas ou mais avaliações… fora de escopo", `specs/013-consolidacao-resultado-etapa/spec.md:680`), 032 (executabilidade antes de publicar — escopo é marco classificatório, FR-457…472), 012-013 (formas de conclusão).
- Implementação encontrada: nenhuma das três direções.
- Evidência no código atual: `backend/processo_seletivo/interface/templates/interface/_etapa.html:157-167` — `<input type="number" min="1">`, ajuda oculta só "Vazio: uma avaliação por inscrição."; `compor_etapas.html` (`como-preencher`) não menciona o campo; `backend/processo_seletivo/editais/domain/validation.py:234` — única conferência é `Campo("evaluationsPerRegistration", int, admite_nulo=True, minimo=1)`; `backend/processo_seletivo/editais/domain/etapas.py:42-48` só recusa < 1; `backend/processo_seletivo/resultados/domain/regra.py:71-76` devolve `REGRA_DE_COMBINACAO_AUSENTE` para `previstas > 1`; `backend/processo_seletivo/resultados/application/prontidao.py:94` (o segundo beco); `backend/processo_seletivo/avaliacoes/application/distribuicao.py:622` (distribuição honra o campo). Teste que prende a recusa: `backend/tests/integration/resultados/test_prontidao.py:67` (`test_etapa_de_leitura_multipla_impede_a_etapa_inteira`). Nenhum teste cobre aviso na publicação.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, na forma barata. Uma nuance que o achado não viu: o briefing de 03/09 (`doc/briefing-revisao-012-013-formas-de-conclusao.md`, "A última pergunta") recusou, para a Etapa decisória não eliminatória, "proibir na elaboração o que o Edital poderia legitimamente publicar". Pelo mesmo critério, a saída coerente é **aviso** na Revisão/validação (não impeditivo), ou retirar o campo da tela enquanto não houver regra de combinação — não um IMPEDE que proíba norma legítima. A direção 3 (regra de combinação como norma) só se justifica com Edital real de dupla leitura na mão.
- Lacuna residual: nada avisa, antes do ato imutável, que o valor > 1 torna a Etapa inconsolidável; o trabalho de avaliadores é gasto antes de o sistema dizer que não sabe usá-lo.
- Grupo do resíduo: **A** (a direção 1/2 — fluxo oferecido pela tela que produz Edital publicado inexequível, contra o propósito escrito da 032); a direção 3 é **C** até haver evidência.
- Impacto atual: baixo em frequência (padrão é vazio = 1), alto em severidade quando ocorre (S3/S4: Edital publicado cuja Etapa não conclui).
- Próxima ação sugerida: corrigir (aviso na validação + microcópia no `como-preencher` da etapa Etapas)
- Relações: item 1 do preâmbulo do longitudinal 19/09 (21/09); mesma família de D-G5 (Edital publicado sem conserto); **ver NOVO-1** — os dois impedimentos irmãos em `regra.py` têm o mesmo defeito de momento.
- Confiança: alta — código atual confirma cada elo da cadeia.

### achado-etapa-governada-nao-remapeada — a cópia de Edital levava `cutRule.governedStage` do Edital anterior
- Origem: `doc/achado-etapa-governada-nao-remapeada.md` (25/09/2026)
- Problema original: `reaproveitamento.remapear` trocava `stages[]`, `drawMethod.qualifyingStageId`, `tiebreakers[].parameters.stageId`, mas não `cutRule.governedStage`; a cópia gravava referência a Etapa do Edital de origem e a publicação acusava `cut_rule_com_etapa_inexistente`. A varredura negativa estava cega porque nenhuma fixture declarava regra de corte.
- Recomendação original: trocar o campo exceto o sentinela `SEM_ETAPA_GOVERNADA` e o vazio; pôr regra de corte nas fixtures; para a 043, mapear Etapa → ela mesma. Fica registrado (não escopo): rascunhos já copiados; a varredura genérica "campos do conteúdo publicado × campos da fixture".
- Rastro posterior: fix `643e865` (PR #169, 25/09 21:44) e teste da 043 `de123ea` (25/09 22:56).
- Specs relacionadas: 023 (reaproveitar), 014 (campo), 043 (duplicar reusa `remapear`).
- Implementação encontrada: troca implementada com exceção do sentinela; fixtures de unidade e integração passaram a declarar regra de corte; 043 com testes dos dois lados.
- Evidência no código atual: `backend/processo_seletivo/editais/domain/reaproveitamento.py:164-183` (troca com exceção de `None`, `""` e `faixa.SEM_ETAPA_GOVERNADA`); testes `backend/tests/unit/editais/test_reaproveitamento.py:396` (`test_a_etapa_que_o_corte_alimenta_aponta_a_etapa_do_destino`), `:417` (`test_o_corte_que_nao_governa_etapa_continua_sem_governar`), `:241` (varredura negativa, agora com fixture que declara corte); `backend/tests/integration/editais/test_reaproveitamento.py:629` (`test_o_corte_governa_etapa_do_destino`); `backend/tests/unit/editais/test_duplicacao.py:289-306` (Etapa do Edital mapeia para si; alheia estoura; `NONE` atravessa).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não para a instância. A **classe** (campo novo de identidade que entra na forma e não no remapeamento/fixture) continua sem guarda genérico — o próprio achado a deixou como "registro, e não prioridade".
- Lacuna residual: varredura genérica ausente (C); rascunhos copiados antes de 25/09 com referência errada — protegidos pelo impeditivo da publicação e corrigíveis pela tela (sem ação necessária).
- Grupo do resíduo: C
- Impacto atual: nenhum para cópias novas.
- Próxima ação sugerida: nenhuma (opcional: varredura genérica de identidades no remapeamento)
- Relações: mesma classe de `doc/achado-ampla-declarada-nao-remapeada.md` (fora do meu lote).
- Confiança: alta — código e três testes conferidos.

### achado-faixa-de-sucesso-do-sorteio — a tela do sorteio anunciava sempre o mesmo ato
- Origem: `doc/achado-faixa-de-sucesso-do-sorteio.md` (10/09/2026)
- Problema original: os quatro comandos (publicar relação, observar, constituir, anular) gravavam no mesmo lugar da sessão e a tela tinha uma frase ("Relação publicada e congelada…") e um prefixo de erro ("Não foi possível publicar:") para todos. Nenhum teste cobria observar/sortear/anular.
- Recomendação original: uma frase por desfecho (discriminador ou chaves distintas) e asserção de tela para os quatro caminhos.
- Rastro posterior: é o E-01/E-02 de `doc/descoberta-rito-do-sorteio-2026-09-10.md`; corrigido no PR #97 no mesmo dia (desfecho acrescentado no próprio achado, l. 8-18).
- Specs relacionadas: 021 (Phase 12).
- Implementação encontrada: faixas de erro e sucesso por tipo de comando; teste de tela para os quatro.
- Evidência no código atual: `backend/processo_seletivo/interface/templates/interface/sorteio.html` — comentário "Cada comando responde pelo que ele fez" e ramos `erro.tipo == "ocorrencia" | "sorteio" | "anulacao"`; `backend/tests/interface/test_console_do_sorteio.py:87` (`test_a_faixa_de_desfecho_diz_o_que_o_comando_fez`), `:118` (`test_a_recusa_nomeia_o_comando_que_falhou`), `:134` (duplo clique, E-03).
- Estado atual: **RESOLVIDO**
- Ainda faz sentido?: não.
- Lacuna residual: nenhuma
- Grupo do resíduo: —
- Impacto atual: nenhum.
- Próxima ação sugerida: nenhuma
- Relações: DUPLICADO de E-01/E-02 (rito do sorteio, 10/09).
- Confiança: alta.

### achado-fonte-real-do-sorteio-sem-gatilho — o teste que prova a fonte externa não roda em lugar nenhum
- Origem: `doc/achado-fonte-real-do-sorteio-sem-gatilho.md` (10/09/2026)
- Problema original: o E2E contra o serviço real da Caixa (`test_o_percurso_inteiro_da_presidencia_contra_a_fonte_real`) está corretamente fora do caminho crítico, atrás de `SORTEIO_E2E_FONTE_REAL`, mas nenhuma rotina o executa. O contrato com a fonte — a única parte do sorteio que o repositório não controla — não é observado; se a Caixa mudar o formato, descobre-se no dia do sorteio. Também: o `AGENTS.md` dizia "1 pulado".
- Recomendação original: decidir (1) onde vive o gatilho (workflow agendado próprio), (2) o que a falha significa e a quem chega (indisponibilidade × mudança de formato), (3) a âncora (extração congelada testa formato; a última testa disponibilidade), (4) atualizar a contagem de pulados.
- Rastro posterior: D-G3 (19/09, `reavaliacao-ux-2026-09-18.md` §14-bis) torna a fonte pública externa **obrigatória prospectivamente** — o que aumenta o peso do contrato com a fonte. `CLAUDE.md`/`AGENTS.md` hoje nomeiam o pulado deliberado (item 4 atendido).
- Specs relacionadas: 021 (FR-076, R-005), 035 (sorteio executável).
- Implementação encontrada: item 4 apenas.
- Evidência no código atual: `.github/workflows/backend.yml` — gatilhos só `push` (main) e `pull_request`; nenhum `schedule`, nenhuma menção a `SORTEIO_E2E_FONTE_REAL` (grep vazio também em `backend/Makefile`); `backend/tests/interface/test_sorteio_com_a_fonte_de_producao.py:48-52` (skipif pela chave) e `:59` (âncora `SORTEIO_E2E_CONCURSO` = `6098`); `CLAUDE.md:74-77` (os 11 pulados, este entre eles). Adaptador único: `backend/processo_seletivo/sorteios/infrastructure/fontes/loteria_federal.py:25`.
- Estado atual: **NÃO IMPLEMENTADO** (item 4 resolvido; itens 1–3 não)
- Ainda faz sentido?: sim. Com a D-G3, todo sorteio futuro depende deste contrato, e um workflow agendado que não bloqueia merge é barato e é a prática padrão para teste de contrato com terceiro. Não é overengineering: é uma execução periódica de um teste que já existe.
- Lacuna residual: nenhuma observação periódica do contrato com a Caixa; última medição registrada: 10/09/2026.
- Grupo do resíduo: **B**
- Impacto atual: risco latente de falha descoberta no dia de um sorteio real, com transmissão aberta (mitigado pela recusa clara "Não foi possível obter os números na fonte").
- Próxima ação sugerida: criar workflow agendado (não bloqueante) — decisão de frequência e de destino da falha é do usuário
- Relações: D-G3; E-06/E-10 do rito do sorteio (robustez do adaptador, já corrigidos).
- Confiança: alta.

### achado-grade-dos-cartoes — as linhas de campo não compartilham colunas
- Origem: `doc/achado-grade-dos-cartoes.md` (08/09/2026)
- Problema original: `.campos` é `flex` com repartição por linha, então as divisões internas não coincidem entre linhas (irregularidade visual, "perceptível, e não errada").
- Recomendação original: grade de 12 colunas com `span` por campo; custo: 107 campos em 13 templates e decisão de conteúdo sobre campo sozinho. Explicitamente "não é defeito, e não vira escopo".
- Rastro posterior: nenhum documento posterior retoma (grep vazio em `doc/` e `specs/`).
- Specs relacionadas: nenhuma.
- Implementação encontrada: nenhuma; o arranjo continua flex.
- Evidência no código atual: `backend/processo_seletivo/interface/templates/interface/base.html:599-612` — `.campos{display:flex;gap:1rem;flex-wrap:wrap}`, `.campo{flex:1 1 200px…}`, `.campo.curto{flex:0 1 auto;min-width:9.5rem}`, `.campo.largo{flex:2 1 320px}`; 17 templates usam `class="campos`.
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: não como prioridade. É cosmético, o próprio achado o declara não-defeito, e as revisões de UX de 13/09 a 21/09 não o reencontraram como fricção.
- Lacuna residual: irregularidade visual entre linhas.
- Grupo do resíduo: C
- Impacto atual: estético.
- Próxima ação sugerida: nenhuma
- Relações: —
- Confiança: alta.

### achado-suite-em-sqlite — a suíte no modo padrão falha, e o CI não enxerga *(dívida de teste/ferramenta)*
- Origem: `doc/achado-suite-em-sqlite.md` (09/09/2026)
- Problema original: `make test` (o que o README mandava rodar) cai para SQLite e fecha vermelho (21 falhas em 09/09) em casos que deveriam ser pulados; o CI só roda PostgreSQL, então o modo padrão apodrece sem sinal; quem chega não distingue "o projeto está assim" de "montei errado".
- Recomendação original: (1) marcar os casos para pular fora do PostgreSQL; (2) exigir PostgreSQL e eliminar o modo SQLite; (3) rodar os dois modos no CI. Nenhum escolhido.
- Rastro posterior: `CLAUDE.md`/`AGENTS.md` (medição de 21/09: **35 falham, ~7326 passam, 243 pulados**, repartidos em 14/9/11 por causa, e instrução "não investigue por este caminho"); README passou a mandar `make test-pg`; memória do usuário `postgres-test-role-inexistente.md`.
- Specs relacionadas: nenhuma (ferramenta).
- Implementação encontrada: só mitigação documental. Nenhum dos três caminhos.
- Evidência no código atual: `backend/config/settings/test.py:5-6` (fallback para SQLite em memória quando `TEST_DB_ENGINE != postgresql`); `backend/Makefile:33-34` (`test:` = `uv run pytest`, sem banco) e `:36-44` (`test-pg`); `.github/workflows/backend.yml` job `test` com `TEST_DB_ENGINE: postgresql` fixo; `README.md:206-214` e `CLAUDE.md:52-72`.
- Estado atual: **NÃO IMPLEMENTADO** (dívida de teste/ferramenta; mitigada por documentação)
- Ainda faz sentido?: parcialmente. Como defeito de produto, não (nenhuma das três causas é do produto). Como ferramenta, o caminho 2 é quase de graça — o alvo `test` recusar sem PostgreSQL, ou virar `test-pg` — e elimina a armadilha que a documentação hoje precisa explicar em três lugares. O número cresceu 21 → 33 → 35, o que mostra que a dívida aumenta a cada SQL de PostgreSQL novo.
- Lacuna residual: alvo `make test` continua existindo e continua vermelho por motivo alheio; contagens divergentes entre os documentos (ver NOVO-3).
- Grupo do resíduo: C
- Impacto atual: atrito no primeiro dia de quem chega; zero efeito em produção ou CI.
- Próxima ação sugerida: corrigir (decisão do usuário entre os caminhos 1 e 2; recomendo 2)
- Relações: mesma família de `achado-teste-com-data-em-utc` ("verde que não corresponde a verde nenhum").
- Confiança: alta nos fatos de código; as contagens citadas são as de `CLAUDE.md` (21/09), não medidas por mim.

### achado-teste-com-data-em-utc — teste comparava data em UTC com data na tela *(dívida de teste)*
- Origem: `doc/achado-teste-com-data-em-utc.md` (11/09/2026)
- Problema original: `timezone.now()` (UTC) formatado com `strftime` e comparado com a tela (fuso institucional) falhava entre 21h e 24h de Brasília. A instância foi corrigida em `a6443f5`; a classe ficou aberta, e uma dúzia de testes só acerta por efeito colateral do `tzset()` do Django (`.astimezone()` sem argumento).
- Recomendação original: (1) CI com `TZ=UTC` e execução agendada dentro da janela; (2) congelar relógio por fixture; (3) varredura que proíba `strftime` sobre instante não convertido; (4) deixar como está.
- Rastro posterior: nenhum documento posterior.
- Specs relacionadas: nenhuma.
- Implementação encontrada: só a instância.
- Evidência no código atual: `backend/tests/integration/portal/test_historico_publico.py:133` usa `localtime(daqui_a_quinze)` (a instância corrigida); seguem 7 usos de `.astimezone()` sem argumento, p.ex. `backend/tests/interface/test_publicacoes_do_marco.py:62`, `backend/tests/interface/test_legibilidade_da_classificacao.py:284,316,360`, `backend/tests/portal/test_resultado_publico.py:68`, `backend/tests/integration/portal/test_acompanhamento.py:57`, `backend/tests/acceptance/test_us_publicacao_de_resultado.py:118`; nenhuma dependência de congelamento de relógio (sem `freezegun`/`time_machine`); `.github/workflows/backend.yml` sem `schedule` e sem `TZ`. Os testes de convocação usam `timezone.localtime(...)` corretamente (`backend/tests/interface/test_convocacao.py:121`).
- Estado atual: **PARCIALMENTE RESOLVIDO** (instância corrigida; classe desprotegida)
- Ainda faz sentido?: parcialmente. O caminho 3 (varredura estreita) é barato e segue o padrão de `tests/test_citacoes_de_requisito.py`; o caminho 1 custa uma execução diária e poderia dividir o workflow agendado com o E2E da fonte real. Não é prioridade de produto.
- Lacuna residual: a próxima asserção escrita em UTC volta a reprovar só em push noturno; 7 testes dependem do `tzset` implícito.
- Grupo do resíduo: C
- Impacto atual: flakiness ocasional de CI; nenhum efeito em produção (o produto formata por `TIME_ZONE`, conforme Princípio II "instantes… sem dependência do fuso do servidor").
- Próxima ação sugerida: nenhuma agora (opcional: varredura estreita)
- Relações: família de `achado-suite-em-sqlite`; poderia compartilhar o workflow agendado de `achado-fonte-real-do-sorteio-sem-gatilho`.
- Confiança: alta.

### Issue #117 — `advertencias_do_ato` filtra por código, não pelo par (código, caminho)
- Origem: issue GitHub #117 (aberta por saymoncastro na revisão do PR #116, spec 027; estado OPEN, 0 comentários)
- Problema original: a subtração dos impeditivos da lista de advertências da Retificação é por `code`; se algum dia um mesmo código for impeditivo num Perfil e advertência em outro, a advertência do segundo some em silêncio e nenhum teste falha.
- Recomendação original: chave `(code, path)`, ou comentário registrando por que o caminho não entra.
- Rastro posterior: `0f36374` (028) acrescentou achados condicionados ao ato e comentou a chamada, sem mudar a chave.
- Specs relacionadas: 027 (FR-336), 028.
- Implementação encontrada: nenhuma mudança na chave; há comentário sobre o **ato** omitido, não sobre o caminho.
- Evidência no código atual: `backend/processo_seletivo/publicacoes/application/retificacoes.py:583-588` — `impeditivos = {item.code for item in blocking_findings(validate_for_publication(content))}` e filtro `if item.code not in impeditivos`; comentário `:577-582` justifica o ato, não o caminho. **A premissa ainda vale hoje**: varri por AST os 71 códigos emitidos em `backend/processo_seletivo/editais/domain/validation.py` (construções `ValidationFinding(...)` e `_impeditivo(...)`, `:448`) — nenhum código tem severidade dupla, e só 10 são `WARNING` (`general_competition_modality_undeclared`, `vacancy_reserved_list_without_row`, `vacancy_table_absent_in_archive`, `vacancy_row_percentage_divergence`, `description_missing`, `registration_period_missing`, `schedule_event_in_past`, `schedule_event_year_mismatch`, `milestone_without_cut_rule`, `attachment_duplicate_label`).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: sim, como endurecimento barato. Atenção: a **D-G1** (FR-461 impeditiva) quando executada vai mudar a severidade de `milestone_without_cut_rule` — se for feita por ato (impeditivo na publicação, aviso na Retificação), o caso da issue passa a existir de verdade. Vale fazer junto com a D-G1.
- Lacuna residual: dependência implícita de "um código, uma severidade", sem guarda que a declare.
- Grupo do resíduo: C (vira B se a D-G1 for executada com severidade condicionada)
- Impacto atual: nenhum hoje.
- Próxima ação sugerida: corrigir junto com a D-G1 (ou acrescentar teste que prenda "cada código tem uma severidade")
- Relações: D-G1.
- Confiança: alta para o estado do código; média para a varredura (achados montados fora de `validation.py` não foram varridos — a função chama só `validate_for_publication`).

### Status: Draft — specs implementadas seguem com `Status: Draft` *(higiene documental)*
- Origem: `doc/relatorio-longitudinal-produto-001-a-037-2026-09-19.md`, preâmbulo de 21/09, item 7 (e §17 do corpo, l. 789)
- Problema original: 32 de 39 pastas com `**Status**: Draft`, três sem linha de Status, só 003/004 declarando conclusão, 031 implementada dizendo "pronta para implementação".
- Recomendação original: implícita — corrigir o estado declarado.
- Rastro posterior: nenhum.
- Specs relacionadas: todas.
- Implementação encontrada: nenhuma; o número cresceu.
- Evidência no código atual: medido hoje com `grep -m1 '^\*\*Status' specs/*/spec.md` — **44** pastas; **38** dizem literalmente `**Status**: Draft` (inclusive a 043, implementada em `0479f4e`, e as 040–042, implementadas em `7ac2c76`); a 044 é o único Draft correto na main. Três sem linha `**Status**` (usam outro rótulo): `specs/012-013-revisao-formas-de-conclusao/spec.md:3` ("emenda aprovada, plano em execução"), `specs/016-ocupacao-de-vagas/spec.md:5` ("pronta para `$speckit-plan`"), `specs/019-convocacao-chamada-suplencia/spec.md:6` ("Pronta para replanejamento") — todas implementadas (`4d71fc0`, `3dcaa90`). `specs/031-exportacao-de-matriculas/spec.md` diz "pronta para implementação" e foi implementada (`24aa3b4`). Só 003 ("Concluída") e 004 ("Implementada") estão certas. Ou seja: **41 de 44** declaram estado que não corresponde ao código. Nenhum teste nem ferramenta lê o campo (`.specify/templates/spec-template.md:7` o cria como `Draft`; grep em `backend/tests` vazio).
- Estado atual: **NÃO IMPLEMENTADO**
- Ainda faz sentido?: parcialmente. É higiene, não dívida de produto: nada consome o campo, e o estado real é recuperável por `git log --grep="(NNN)"`. O custo real é de leitura — um auditor (ou agente) que confie no Status erra 41 vezes em 44, e o próprio briefing deste lote teve de avisar isso. Um índice único (ou a linha corrigida no merge) resolveria; o risco de overengineering está em criar ferramenta para isso.
- Lacuna residual: não há registro confiável, dentro de `specs/`, de quais features estão implementadas.
- Grupo do resíduo: C
- Impacto atual: confusão de leitura; nenhum efeito funcional.
- Próxima ação sugerida: corrigir (edição em lote dos cabeçalhos, decisão do usuário sobre a convenção)
- Relações: nenhuma.
- Confiança: alta (medição direta).

---

## Parte 2 — Registro de decisões conscientes

Para classificar achados de outros lotes. A coluna que importa é **"Recusa / adia / redireciona"**:
recomendação que cai ali é `CONTRADITO POR DECISÃO POSTERIOR` (se a decisão é posterior ao achado) ou
`SUPERADO` (se a decisão tornou a pergunta irrelevante). "Honra?" é checagem pontual no código de `bb774d9`.

### 2.0 Filtros da Constituição (`.specify/memory/constitution.md`) — tornam recomendações inadmissíveis
| Princípio | Onde | Recomendação que ele veda |
|---|---|---|
| Publicação imutável; Retificação não reescreve publicação anterior | §II, l. 65-69 | "corrigir"/editar Edital publicado; migrar snapshot publicado; regenerar PDF publicado |
| Única fonte autoritativa; PDF deriva do estruturado | §II l. 59-63; Restrições l. 211-213 | publicar norma estruturada como binário/anexo quando há forma estruturada; duas fontes da mesma informação |
| Regras atuais não substituem históricas | §II l. 71-75 | ler `effective_version` para ato já praticado; recalcular inscrição antiga com recorte novo |
| Cancelamento é ato, nunca exclusão; auditoria não se altera | Restrições l. 215; §III l. 103-105 | qualquer "apagar", hard delete, migration que remove dado normativo |
| Negar por padrão; permissão explícita e específica | §III l. 86-90 | conceder capacidade "por simetria"; pendurar julgamento de recurso num papel existente |
| Regra que afeta direito reside no domínio/backend | §IV l. 112-116 | resolver regra só no front; inferir norma por convenção de tela |
| Cotas por Perfil | Restrições l. 197-200 | mover Modalidade/cota para o nível do Edital (decisão-recorte D1/D5 e 043 §2 citam) |
| Solução mais simples; nada de estrutura antes da regra | §V l. 149 | entidades novas sem Edital real que as consuma (Ocorrência própria, polo, barema antes da hora) |
| Capacidade sem interface não está entregue | §VI l. 163-170 | declarar feature pronta só por API/teste |

Nuance registrada pelo usuário (memória `constituicao-preserva-valor-nao-campo.md`): a Constituição preserva **o valor publicado**, não **o campo no modelo de autoria**. Recomendação de depreciar/renomear campo de autoria **não** é vetada pela imutabilidade.

### 2.1 Decisões datadas

| # | Decisão · data · onde | O que decidiu | Recusa / adia / redireciona | Honra? (código) | Trabalho criado ainda não executado |
|---|---|---|---|---|---|
| 1 | **Conclusão decisória** · 03/09 · `doc/decisao-012-conclusao-decisoria.md` | Conclusão = "completa segundo a forma que a Etapa publicou": `PONTUADA` (nota) ou `DECISORIA` (sentido `FAVORAVEL/DESFAVORAVEL`); rótulo vem da Etapa publicada; forma gravada na linha | **Recusa** deferido=1/indeferido=0; enum com os pares de rótulo; chamar o campo de `decisão`. **Adia** conceito ordinal (A/B/C) até um Edital o usar. **Mantém recusado** barema (§21 da 012) | Sim — `backend/processo_seletivo/avaliacoes/models.py:196-218` (`forma`, `sentido`, `ck_conclusao_completa_por_forma`) | Nenhum |
| 2 | **Briefing 013 + revisão 012–013 (D-008)** · 03/09 · `doc/briefing-013-resultado-da-etapa.md`, `doc/briefing-revisao-012-013-formas-de-conclusao.md` | Seis invariantes do Resultado (I-1…I-6); Etapa decisória **não** eliminatória cai em `REGRA_INSUFICIENTE`; `eliminatory` é o que dá consequência à decisão | **Recusa** `DESFAVORAVEL` sempre eliminar; **recusa exigir `eliminatory` na elaboração** ("proibir na elaboração o que o Edital poderia legitimamente publicar é a mesma invenção"); V1 sem consolidação parcial, nota assumida, quórum reduzido ou autorização excepcional da presidência; classificação editorial de Edital **fora** do snapshot (só a natureza do processo é normativa) | Sim — `backend/processo_seletivo/resultados/domain/regra.py:57-95` | Lacunas registradas sem spec: heteroidentificação (zero ocorrências no código, confirmado no longitudinal 21/09 item 2), campus como entidade (`PerfilVaga.locality` segue texto, `editais/models/perfis.py:24`), semântica discente, Gov.br |
| 3 | **Decisões pré-vertical D-1…D-4** · 04/09 · `doc/decisoes-pre-vertical.md` | D-1 Resultado por `OCORRENCIA` sem Avaliação; D-2 o Edital declara fatos do candidato, congelados na submissão (DATA e INTEIRO); D-3 `maxInscricoesPorCandidato` anulável, conta só submetidas; D-4 barema **fora do primeiro vertical** (apuração externa) | D-1 **recusa** entidade própria de Ocorrência e ausência como conclusão decisória. D-2 **recusa** construtor de formulário; terceiro tipo só com Edital que o exija. D-3 **recusa** `unique(identidade, edital)` e política multi-eixo; teto reduzido não invalida inscrição. D-4 **adia** barema (não recusa para sempre) | Sim — `resultados/models.py:56` (`OCORRENCIA`); `inscricoes/application/submissao.py` (teto); zero ocorrências de "barema" em `backend/processo_seletivo/` | D-4: spec de barema "depois" nunca aberta — é o que AX-4, estudo §13 E11 e longitudinal item 3 cobram. **Não** classificar esses achados como CONTRADITOS: D-4 só adiou |
| 4 | **Decisão C da 018** · 06/09 · `doc/descoberta-018-decisao-c-superacao-de-resultado.md` §1 | Recurso deferido supera `ResultadoEtapa` por **sucessor append-only**; origem `RECURSO`; efeito atômico ao deferimento que declara o resultado; reavaliação ordenada não cria sucessor | **Recusa** anular/marcar/apagar o Resultado; Avaliação sintética; estado "deferido aguardando aplicação"; restringir recurso a antes da consolidação como regra geral; separar julgar de executar sem exigência institucional | Sim — `resultados/models.py:72` (`RECURSO`), `:133` (superado não é alterado) | Nenhum |
| 5 | **Escopo institucional do Recurso (7 decisões)** · 06/09 · `doc/decisao-018-escopo-institucional-do-recurso.md` §11 | 1B (resultado divulgado **e** Resultado individual da Etapa); 2A (só o titular); 3A janela estruturada por marco; 4B capacidade `recurso:julgar` com impedimento que bloqueia quem avaliou/consolidou/emitiu/publicou; 5A sem *reformatio in pejus*; 6A progressão retroativa plena com guarda; 7B definitividade impedida com recurso pendente | **Recusa** na V1: terceiro interessado e procurador (sem notificação/representação); presidência julgar por vínculo; comissão recursal própria; piora com ou sem contraditório; efeito limitado à Etapa. Representação futura só como interposição **registrada pela instituição**, nunca login delegado | Sim — `recursos/domain/pejus.py:1`, `recursos/application/julgar.py:263-276`, `recursos/domain/elegibilidade.py:25-69`, `interface/identidade.py:81-83` (papel `julgador` próprio) | Nenhum na V1 |
| 6 | **Presidência única + equipe de 2–3** · 08/09 · `doc/descoberta-conducao-por-presidencia-unica.md`; memória `equipe-inicial-de-duas-ou-tres-pessoas.md` | Descoberta não decide; o usuário informou: operação inicial de **2–3 pessoas acumulando papéis**. Piso técnico = 2 identidades, com o julgador fora da cadeia de avaliação e divulgação; "a saída é institucional, não técnica" (decisão 018 §5) | **Redireciona** qualquer proposta que pressuponha seis pessoas; **recusa implícita** de afrouxar segregação (FR-021 ternária) ou o impedimento recursal para caber na equipe pequena | Sim — segregação ternária em `publicacoes/application/publish_edital.py` (citada em `:574` na descoberta); manual `doc/manual/00-arquitetura-do-manual.md:123` (§A.3, as duas configurações) | Pergunta 3 da descoberta (avisar **antes** que não haverá julgador elegível) segue sem decisão: hoje só há o sinal pós-fato `UX-005` em `interface/supervisao.py:1084-1196` |
| 7 | **Escopo sorteio e anexos** · 07/09 · `doc/descoberta-escopo-sorteio-e-anexos.md` | Anexo como **arquivo** (forma 1) fecha o ciclo; campo de anexo só é legítimo quando uma regra publicada o consome (critério do `FatoDeclarado`) | **Recusa** anexo como formulário com campos ("construtor de formulários por outro caminho", recusa da 009); expectativa de pontuação vai para o barema, não para anexos; quadro de vagas como binário = "bifurcação do acervo" (desaconselhado) | Sim — anexo **acompanha** e não integra o PDF: `publicacoes/infrastructure/pdf.py:1993-2003` (020, FR-027/027a) | Nenhum |
| 8 | **Rito do sorteio** · 10/09 · `doc/descoberta-rito-do-sorteio-2026-09-10.md` §N | P0 (E-01…E-07, E-10, E-12, E-19) corrigidos no mesmo dia; lacuna restante é de "rito e narrativa" | **Recusa** tocar chave, ordem, semente ou manifesto; qualquer estado novo entre sortear e publicar; campo de semente, simulação, refazer, editar relação, escolher ocorrência; integração com API de vídeo (guardar endereço ≠ integrar) | Sim — nenhum campo de semente na tela; `sorteios/infrastructure/fontes/` só tem adaptador externo | P1/P2 (E-13…E-18, E-20…E-22) fora do meu lote; a própria descoberta questiona `LIMITE_DA_CADEIA = 5` (`sorteios/domain/substituicao.py:36`, inalterado) |
| 9 | **Encadeamento L-1 e arco 014/016/019** · 10/09 · `doc/decisao-encadeamento-l1-e-o-arco-operacional.md` §4 | L-1 (quantidade por modalidade) precede a 016, não bloqueia a 014; recomendação de forma **estruturada** (Q-2) | **Recusa** "a 019 reabre a 018" (ela consome ou propõe revisão formal); **recusa** tratar o quadro binário como entrega da L-1; não prioriza nada | Sim — quadro estruturado `editais/models/perfis.py:126` (`LinhaDoQuadroDeVagas`, 025/027); Q-1 fechada pela decisão de fronteira da 014 (`specs/016-ocupacao-de-vagas/spec.md:10-12`); 019 escolheu opção B para a progressão retroativa (`specs/019-convocacao-chamada-suplencia/spec.md:183-189`) | Nenhum |
| 10 | **Contrato de mutabilidade normativa** · 13–14/09 · `doc/decisao-mutabilidade-normativa.md` | Invariante de arquitetura: **nenhum campo normativo publicado sem decisão explícita** entre retificável / não retificável (com razão **normativa**) / derivado / identidade-estrutural; guardião que falha nos dois sentidos | **Recusa** "completude da Retificação" (pôr todos os campos na tela); exclusão por argumento técnico; **recusa** retificar campo derivado ou estrutural (convergência §21: não pôr `scheduleEventId`/`status` na Retificação) | Sim — `editais/domain/mutabilidade.py:121-133` (naturezas), `backend/tests/contract/test_mutabilidade.py` | Nenhum (o guardião cobra cada campo novo) |
| 11 | **Requerimento de Matrícula** · 16/09 · `doc/descoberta-029-requerimento-de-matricula.md` §4 | Feature própria (não estende a Inscrição); gatilho = convocação vigente; dois momentos; endereço no Requerimento com cópia para a frente; IBGE sim; base local de CEP; retirada do Anexo assinado é **decisão de cada Edital**; renda em faixa da **soma familiar** (divergência per capita nomeada, não corrigida); e-mail exportado = o da credencial | **Recusa** lat/long; os 8 campos "questionáveis" (foto, tipo sanguíneo, nº de filhos…, FR-382); **adia** nome social/identidade de gênero para spec própria; **adia** a planilha para a 031 | Sim — `requerimentos/models.py:145` (`renda_familiar_faixa`), `:159` (`codigo_ibge`) | Spec de nome social/identidade de gênero **não existe** (grep: só citada em `specs/029…/spec.md`) |
| 12 | **D-G1** · 19/09 · `doc/reavaliacao-ux-2026-09-18.md` §14-bis | FR-461 passa a ser **impeditiva**: todo marco declara regra de corte **ou** que não governa Etapa | Contradiz qualquer recomendação de manter como aviso | **Não** — `editais/domain/validation.py:1705-1747` ainda `Severity.WARNING` (`milestone_without_cut_rule`, docstring "Aviso, e não impedimento") | **Sim**: spec curta não feita (convergência §16 já registrava "não executada") |
| 13 | **D-G2** · 19/09 · idem | Fronteira 403/404 por critério: 404 para inexistência/fora do escopo/enumeração; 403 para objeto visível sem capacidade. `criar_edital`, `reaproveitar`, `supervisao` → 403; `anexo_do_rascunho`, `minha_etapa`, `inscricao_da_mesa`, `documento_da_mesa` → 404 | **Recusa** troca em bloco (convergência §21 repete) | **Não** — `interface/views.py:400-403` (`criar_edital`: `raise Http404` sem capacidade, comentário antigo), `:4020-4021` (`supervisao`); `reaproveitar` `:1438+` idem | **Sim**: spec das recusas não feita |
| 14 | **D-G3** · 19/09 · idem | O Cefor passa a declarar **fonte pública externa**; o produto **não acomoda** semente própria publicada depois; vale prospectivamente e **inclusive para reaproveitados**; acervo intocado | **Recusa** "sorteio com semente do próprio sistema" como equivalente auditável; torna CONTRADITA qualquer recomendação de acomodar o §6.2 do 78/2026 ou o §8.2 do 28/2026 | Parcial — o produto só tem fonte externa (`sorteios/infrastructure/fontes/__init__.py:68-95`); a regra do reaproveitamento **não existe** (estudo 21/09 §5.3: a cláusula antiga viaja em texto livre) | **Sim**: spec (regra do reuso) não feita |
| 15 | **D-G4** · 19/09 · idem | Peso continua **da Etapa**; pergunta encerrada | **Recusa** mover peso para o par marco×Etapa sem Edital real | Sim — `editais/domain/validation.py:227` (`weight` na Etapa) | Nenhum |
| 16 | **D-G5** · 19/09 · idem | Retificação **passa a acrescentar** Modalidade de Concorrência, com cinco restrições (preservar versões, efeito só pela nova, validar dependentes, não reescrever inscrições/ordens, recorte novo sem ordem própria) | — | **Não** — `interface/retificacao.py:449-482` só tem `NOVO_PERFIL`, `NOVA_LINHA_DO_QUADRO`, `NOVO_EVENTO`, `NOVO_ANEXO` | **Sim**: spec "não pequena" não feita |
| 17 | **"O que não fazer"** · 20/09 · `doc/auditoria-de-convergencia-pos-038-2026-09-20.md` §21 | Sete vetos de método | Não pôr `scheduleEventId`/`status` na Retificação (mascararia N-06); não trocar 404→403 em bloco; não silenciar `UX-001`/`UX-002`; não fundir avisos de validação com sinais de Atenção sem critério; **não modelar responsável individual** (N-04 pede a capacidade a pedir); **não abstrair polo** antes do Edital real multipolo; não tratar teste verde como fluxo compreensível | — (vetos) | Nota: a condição do veto do polo ("Edital real na mão") foi satisfeita pelo estudo de 21/09 (140/2025, 28/2026) — o veto não caiu, mas deixou de ser razão para adiar a **decisão** E2 |
| 18 | **Sem carga retroativa** · 25/09 · `doc/decisao-sem-carga-retroativa.md`; memória `sem-cadastro-retroativo-de-edital.md` | O produto **não terá** fluxo de carga de Editais encerrados; amostra histórica é só amostra | **Recusa** spec de "registro de Edital já executado"; o IMPEDE "o período de inscrições encerrou" é correto. Estudos futuros compõem com **datas futuras**. Não atribuir à D-G3 | Sim — `editais/domain/validation.py:2055-2096` (`registration_period_closed`, impeditivo) | Nenhum. Consequência aceita: a primeira oferta de cada família é sempre composta do zero |
| 19 | **Recorte do documento exigido (D1–D5)** · 25/09 · `doc/decisao-recorte-documental.md` "O que foi decidido" | D1 identidade transversal pelo **código** da Modalidade + IMPEDE de coerência só da denominação; D1a a ampla não pode ser recorte transversal; D2 condição sobre o candidato = opção 1 (informativa); D3 sem exceção negativa; D4 **congelar na inscrição** a lista exigida com a razão; D5 a primeira spec é só o recorte transversal + lista gravada | **Recusa** categoria declarada no Edital (opção B); lote como solução do recorte (C); coerência sobre percentual/fundamento; exceção negativa; mover Modalidade para o Edital; **adia** condição autodeclarada (opção 2) para spec própria com avaliação LGPD; **redireciona** "aplicar a todos" para outra spec | Sim — `01d9163` recusa "Todos os Perfis"+modalidade de um só; `a2b1e1f` fez as correções de D2 (instrução na Mesa, facultativo na Revisão); a **044 entrou na main pelo #173** em 26/09 (D1, D1a, D3, D4 e D5) | **Sim**: (a) ~~mesclar a 044~~ feito pelo #173; (b) "O que mudou" listar mudança de recorte — pendente em `publicacoes/domain/alteracoes.py:89-95` (sem `profileId`/`modalityId`; `alteracao_legivel` devolve `None` e a linha some), e a própria branch da 044 diz que "continuam fora: a correção deles é da fila das diretas"; (c) spec da opção 2 |
| 20 | **Duplicar Perfil — recorte** · 25/09 · `specs/043-duplicar-perfil/spec.md` Clarifications e §4/§5 | 043 = só duplicar; cópia não guarda vínculo com a origem (D-005/D-006); Documentos Exigidos restritos à origem **não** são copiados (avisa quantos, FR-645) | **Adia** propagação em massa (TF-1: "aplicar Modalidades/marco a todos") e redução documental (TF-2); **recusa** mover conteúdo para o Edital (E2) nesta spec | Sim — `interface/urls.py:111-113`; `tests/unit/editais/test_duplicacao.py` | TF-1 e TF-2 registrados, sem spec |
| 21 | **ValorDeFato: gatilho depois da 044** · 25/09 · memória `valor-de-fato-corrigir-depois-da-044.md`; PR #171 (aberto, `doc/achado-valor-de-fato-sem-gatilho.md`) | `inscricoes_valordefato` ganha gatilho `BEFORE UPDATE OR DELETE` e guarda de modelo como `inscricoes/0006`, **só depois** da migration `0005` da 044 estar na main; escopo só `ValorDeFato` | **Adia** a correção; **recusa** incluir `PosicaoNaOrdem`, `RevisaoEdital`, `GeracaoDeArquivo` (só registradas) | Sim — **feito pelo #183** em 26/09, depois de a `0005` entrar com o #173: `inscricoes/migrations/0006_valor_de_fato_append_only.py` e `ValorDeFato.save`/`delete`; as três tabelas recusadas continuam como estavam | Nenhum |
| 22 | **Quick win pode contrariar FR** · 25/09 · memória `quick-win-pode-contrariar-fr.md` | Quatro itens do §12 do estudo de esforço **não** foram implementados por contrariarem FR escrito | Torna CONTRADITOS (por FR vigente, decisão de não implementar sem decisão do usuário): copiar a Descrição no reuso (FR-007 da 023); imprimir o método do sorteio uma vez (FR-465/466 da 032); ancorar a regra do ano no certame (FR-344); esconder Casas decimais/Arredondamento no sorteio (campo obrigatório) | Sim — os demais itens entraram em `8e4bc06`, `7b04cb3`, `d0352f5` | Registrar a decisão no próprio estudo, se ainda não estiver |
| 23 | **Registrar a decisão, não tomá-la** · recorrente (memória `registrar-decisao-nao-tomar.md`, CLAUDE.md "Governança é do usuário") | Achado encontrado numa feature não vira escopo da seguinte; poder novo (permissão, alcance) não se infere por simetria | **Recusa** conceder capacidade por simetria (ex.: `retificacao:cancelar` ao Gestor — o usuário fechou "só em `EM_ELABORACAO`, com devolução antes") | — (regra de processo) | — |
| 24 | **Diretoria como papel próprio** · 040 (registrada como pendente) · comentário em `interface/identidade.py:66-70` | O panorama institucional vai ao Gestor | **Adia** papel próprio de Diretoria — "decisão institucional, não técnica", pendente na spec da 040 | — | Decisão pendente do usuário |
| 25 | **Certame do manual montado à mão** · 08/09 (S-00) · memória `seed-demo-nao-produz-certame-do-manual.md` | O `seed_demo` não é o certame-exemplo do manual; capturas são montadas pela interface | **Redireciona** recomendações de "consertar o seed para o manual" | — | Nenhum |

### 2.2 Uso rápido — que decisão contradiz qual tipo de recomendação
- "Registrar Edital histórico / carga retroativa / publicar Edital com inscrição encerrada" → **#18** (CONTRADITO).
- "Aceitar semente gerada pelo próprio sistema" → **#14 D-G3** (CONTRADITO).
- "Mover peso para marco×Etapa" → **#15 D-G4** (CONTRADITO/SUPERADO).
- "Trocar todas as 404 por 403" → **#13 D-G2** e **#17** (CONTRADITO); as três específicas de D-G2 continuam devidas.
- "Pôr `scheduleEventId`/`status` na Retificação"; "todos os campos na tela de Retificação" → **#10** e **#17** (CONTRADITO).
- "Nomear responsável individual no painel" → **#17** e decisão da 038 (convergência §16) (CONTRADITO).
- "Modalidade/cota no nível do Edital" → Constituição (Cotas por Perfil) + **#19 D1/D5** (inadmissível). "Requisitos/carga/atribuições no Edital (E2)" → **não decidido** (nem #19 nem #20 decidem): continua aberto, não contraditado.
- "Documento por categoria declarada no Edital" / "exceção negativa" → **#19** (CONTRADITO).
- "Coletar sexo/idade/vínculo para decidir documento" → **#19 D2** (adiado; opção 2 em spec própria com LGPD).
- "Anexo como formulário estruturado" → **#7** (CONTRADITO), salvo campo que uma regra publicada consuma.
- "Barema/ficha de avaliação estruturada" → **#3 D-4** só **adiou** (não contraditar; é resíduo aberto).
- "Terceiro/procurador recorre", "presidência julga", "recurso pode piorar" → **#5** (CONTRADITO na V1).
- "Afrouxar segregação para equipe pequena" → **#5/#6** (CONTRADITO; saída institucional).
- "Afrouxar recusas da consolidação (média por padrão, escolher avaliação)" → **#1/#2** (CONTRADITO). "Exigir `eliminatory` de toda Etapa decisória na elaboração" → **#2** (CONTRADITO).
- "Quatro quick wins do §12 do estudo" (Descrição no reuso, método uma vez, regra do ano, esconder arredondamento) → **#22** (CONTRADITO por FR).
- "Aplicar em lote / propagar" → **#20** adiou para TF-1 (resíduo aberto, não contraditado).

---

## Tabela-resumo (Parte 1)

| ID | Título | Estado | Grupo | Próxima ação |
|---|---|---|---|---|
| achado-atribuicoes-repetidas-por-polo | texto comum copiado por polo (Princípio II) | PARCIALMENTE RESOLVIDO (cabeçalho `c0403a9`; digitação pela 043) | B | criar spec — antes, decisão E2 do usuário; TF-1 da 043 é o passo barato |
| achado-duas-avaliacoes-sem-regra-de-combinacao | `evaluationsPerRegistration` > 1 publica Etapa inconsolidável | NÃO IMPLEMENTADO | A (aviso/microcópia); C (regra de combinação) | corrigir — aviso na validação + `como-preencher`; não IMPEDE (ver D-008) |
| achado-etapa-governada-nao-remapeada | `cutRule.governedStage` não remapeado na cópia | RESOLVIDO (`643e865`, `de123ea`) | C (só a classe) | nenhuma |
| achado-faixa-de-sucesso-do-sorteio | faixa única para quatro comandos | RESOLVIDO (PR #97; = E-01/E-02) | — | nenhuma |
| achado-fonte-real-do-sorteio-sem-gatilho | E2E da fonte real sem execução periódica | NÃO IMPLEMENTADO (só a contagem de pulados foi atualizada) | B | criar workflow agendado não bloqueante |
| achado-grade-dos-cartoes | colunas não coincidem entre linhas | NÃO IMPLEMENTADO | C | nenhuma |
| achado-suite-em-sqlite | modo padrão da suíte vermelho, CI cego *(ferramenta)* | NÃO IMPLEMENTADO (mitigado por documentação) | C | corrigir (fazer `make test` exigir PostgreSQL) |
| achado-teste-com-data-em-utc | classe de asserção de data em UTC *(teste)* | PARCIALMENTE RESOLVIDO (instância `a6443f5`) | C | nenhuma (opcional: varredura) |
| Issue #117 | `advertencias_do_ato` subtrai por código | NÃO IMPLEMENTADO (premissa ainda vale) | C (B se D-G1 condicionar severidade ao ato) | corrigir junto com a D-G1 |
| Status: Draft | 41 de 44 specs com estado declarado errado *(higiene)* | NÃO IMPLEMENTADO (piorou: 32/39 → 38/44 Draft) | C | corrigir cabeçalhos (convenção é do usuário) |

## Contagens por estado (Parte 1, 10 itens)

| Estado | Qtde |
|---|---|
| RESOLVIDO | 2 |
| RESOLVIDO POR OUTRO CAMINHO | 0 |
| PARCIALMENTE RESOLVIDO | 2 |
| NÃO IMPLEMENTADO | 6 |
| IMPLEMENTADO, MAS NÃO VALIDADO | 0 |
| SUPERADO / OBSOLETO | 0 |
| DUPLICADO / ABSORVIDO | 0 (a faixa do sorteio é duplicata de E-01/E-02, mas foi classificada pelo estado: resolvida) |
| CONTRADITO POR DECISÃO POSTERIOR | 0 |

Resíduos: A = 1 · B = 2 · C = 6 · — = 1.

Decisões (Parte 2): 25 registradas. Com trabalho criado **não executado**: D-G1, D-G2, D-G3 (regra do reuso), D-G5, recorte documental ("O que mudou" do recorte + opção 2; a 044 entrou pelo #173), D-4 (barema adiado), nome social (029), TF-1/TF-2 (043), pergunta 3 da presidência única, papel de Diretoria (040).

## Achados NOVOS encontrados de passagem

- **NOVO-1 — os dois impedimentos irmãos da regra também só aparecem depois da publicação.** `resultados/domain/regra.py:57-95` põe três impedimentos da **Etapa inteira** lado a lado: prever > 1 avaliação (o achado de 21/09), Etapa **pontuada eliminatória sem nota mínima** e Etapa **decisória não eliminatória**. A validação de publicação não confere nenhum dos três: `editais/domain/validation.py:228` só tipa `eliminatory`, e nenhum ponto de `editais/` ou `publicacoes/` chama `impedimento_da_regra` (só `resultados/application/prontidao.py:504` e `recursos/domain/consequencia.py:71`). O escopo da 032 (FR-457…472) é o marco classificatório, não a Etapa. Um Edital com Etapa eliminatória pontuada sem nota mínima publica e só se descobre inconsolidável na prontidão. Ressalva: para a decisória não eliminatória, o briefing de 03/09 recusou exigir `eliminatory` na elaboração — um **aviso** na Revisão é compatível com essa decisão; um IMPEDE não. Grupo A/B (mesmo mecanismo do achado de 21/09, que só olhou um dos três). Confiança média-alta: li o código, não conferi a tela da Revisão no navegador.
- **NOVO-2 — a 044 está implementada, mas fora da main e sem PR.** `origin/claude/044-recorte-transversal-documental` tem 8 commits (`bccfda0` → `56649d4`, este de 25/09 23:28, cinco minutos depois do merge do #168 às 23:23) com a implementação completa (migration `inscricoes/0005_item_da_lista_exigida.py`, `modalityCode`, lista gravada no envio, Retificação). O #168 mesclou só spec/plano/tarefas, e a lista de PRs abertos tem só #171 e #172. Consequência: a correção do `ValorDeFato` (memória de 25/09) espera "o merge da 044 (#168)" — a condição literal (#168 mesclado) está satisfeita, mas a real (migration `0005` na main) não. O briefing deste lote ("a 044 está só especificada") vale só para a main. **Desfecho (26/09):** a 044 entrou pelo #173, e a correção do `ValorDeFato` veio no #183.
- **NOVO-3 — contagens da suíte divergem entre os documentos.** `README.md:206-214` diz 201 pulados / 33 falhas no SQLite e "5402 passando e 2 pulados" no PostgreSQL; o comentário de `backend/Makefile:36-37` diz 182 / 21; `CLAUDE.md:52-72` (21/09) diz 243 / 35 e 7594 / 11. Higiene (C), mas é justamente o sinal que o `CLAUDE.md` pede para vigiar ("desconfie se mudarem").

## Incertezas que exigem validação humana

1. **Dupla leitura existe no Cefor?** Decide a severidade do achado de duas avaliações e se a direção 3 (regra de combinação como norma) merece spec. Também: aviso (compatível com a D-008 do briefing de 03/09) ou IMPEDE?
2. **A 044 da branch vai para a main, e por qual PR?** Isso destrava a correção do `ValorDeFato` e a D4 do recorte documental. Confirmar se a memória "depois do merge do #168" quis dizer a implementação. **Respondida em 26/09:** pelo #173, e a correção do `ValorDeFato` veio depois, no #183.
3. **Decisão E2** (onde mora o conteúdo comum aos Perfis: atribuições, carga, remuneração, requisitos) continua sem dono: nem a decisão do recorte documental (D5) nem a 043 a tomam. O veto "não abstrair polo sem Edital real" (convergência §21) já tem o Edital real.
4. **Workflow agendado para a fonte real:** frequência, âncora (extração congelada × última) e destino da falha são escolhas do usuário.
5. **Convenção de `Status` nas specs:** manter o campo (e corrigir 41 cabeçalhos) ou abandoná-lo por um índice único.
6. **NOVO-1:** conferir na tela da Revisão se algum aviso cobre "eliminatória sem nota mínima" (li o código; não abri o navegador).
7. **Contagens do modo SQLite:** não as medi; as citadas são do `CLAUDE.md` de 21/09.
8. **Issue #117:** a varredura de severidade dupla cobriu só `editais/domain/validation.py` (a função só chama `validate_for_publication`, então deve bastar), e deve ser refeita quando a D-G1 for executada.
