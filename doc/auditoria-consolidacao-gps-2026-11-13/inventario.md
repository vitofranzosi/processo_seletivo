# Inventário — rastreabilidade das frentes

*Base: `origin/main` em `33546564`, 13/11/2026. "Fora da `main`" quer dizer que há patch fora da
`main` (`git cherry`), conferido também pelo conteúdo. Os links são do repositório
`vitofranzosi/processo_seletivo`.*

Legenda das ações: **ENCERRAR** — nada a fazer; **CONSOLIDAR** — uma ação pequena e objetiva;
**PRESERVAR** — guardar, ainda não encerrar; **INVESTIGAR** — falta evidência para decidir.

## 1. Frentes funcionais recentes (jornada final, convocação e operação)

| Frente | Spec | Branch | PR | Estado na `main` | Pendência | Classificação | Ação |
|---|---|---|---|---|---|---|---|
| Centro de Controle e jornada guiada | 127, 135, 136, 138, 139 | várias, todas integradas | [#415](https://github.com/vitofranzosi/processo_seletivo/pull/415) [#416](https://github.com/vitofranzosi/processo_seletivo/pull/416) [#440](https://github.com/vitofranzosi/processo_seletivo/pull/440) [#442](https://github.com/vitofranzosi/processo_seletivo/pull/442) [#447](https://github.com/vitofranzosi/processo_seletivo/pull/447) [#451](https://github.com/vitofranzosi/processo_seletivo/pull/451) | implementada | o `**Status**` diz "Draft" em 135, 136, 138 e 139 | CONCLUÍDA | ENCERRAR (status em P2) |
| Página do Processo | 147 (137 reservada e não usada) | `gps-processo-seletivo-ui-ux-a59d79` | [#466](https://github.com/vitofranzosi/processo_seletivo/pull/466) | implementada | o status omite a implementação | CONCLUÍDA | ENCERRAR |
| Minhas atividades | 160 | `160-implementacao` | [#506](https://github.com/vitofranzosi/processo_seletivo/pull/506) [#508](https://github.com/vitofranzosi/processo_seletivo/pull/508) [#511](https://github.com/vitofranzosi/processo_seletivo/pull/511) [#512](https://github.com/vitofranzosi/processo_seletivo/pull/512) | implementada | as capturas T002/T036 (UX-714) estão fora do git, em `gps-candidate-auth-ui-2db0c1`; SC-2281 é validação humana | CONCLUÍDA | PRESERVAR as capturas (P0-9) |
| Quem faz o quê | 161 | `161-quem-faz-o-que` | [#519](https://github.com/vitofranzosi/processo_seletivo/pull/519) | só a spec | plano, tarefas e código; as quatro decisões já foram tomadas | INCOMPLETA | ENCERRAR a sessão; a spec continua como próximo trabalho |
| Autonomia operacional (estudo) | — | `operation-vs-task-execution-5e2d5c` | — | ausente | 1 commit **só local** (`c7232947`, 265 linhas, 13/11) | PENDENTE DE MERGE | CONSOLIDAR (P0-3) |
| Modelo centrado no trabalho (estudo) | origem da 160 | `gps-work-centered-model-4c557f` | — | o conteúdo commitado é **idêntico** ao `doc/estudo-minhas-atividades-2026-11-12/` da `main` | só as capturas, fora do git | SUBSTITUÍDA, menos as capturas | PRESERVAR as capturas, depois ENCERRAR |
| Conferência antes de convocar | 140 | `140-conferencia-ao-convocar-d54ffb` | [#448](https://github.com/vitofranzosi/processo_seletivo/pull/448) | implementada | `tasks.md` com 0/13 marcadas e status "Draft" | CONCLUÍDA | ENCERRAR (status em P2) |
| Sucessora espera o reabilitado | 141 | `141-sucessora-espera-reabilitado-af020a` | [#449](https://github.com/vitofranzosi/processo_seletivo/pull/449) | implementada | status "Draft" | CONCLUÍDA | ENCERRAR |
| Jornada do sorteio, sorteio no cartão | 142, 145 | integradas | [#452](https://github.com/vitofranzosi/processo_seletivo/pull/452) [#459](https://github.com/vitofranzosi/processo_seletivo/pull/459) | implementada | status "Draft" na 142 | CONCLUÍDA | ENCERRAR |
| Convocação e documentos | 143 | integrada | [#453](https://github.com/vitofranzosi/processo_seletivo/pull/453) | implementada | status "Draft" | CONCLUÍDA | ENCERRAR |
| Barema da Etapa | 146 | `146-barema-incremento-c`, `competent-euclid-c9882c`, `gps-barema-investigation-1750ab` | [#460](https://github.com/vitofranzosi/processo_seletivo/pull/460)–[#463](https://github.com/vitofranzosi/processo_seletivo/pull/463) | A, B e C implementados | P-1 a P-7 são institucionais | CONCLUÍDA | ENCERRAR |
| Publicação das inscrições | 148 | `148-listas-code-review`, `gps-inscricoes-publicacao-93355f` | [#469](https://github.com/vitofranzosi/processo_seletivo/pull/469) [#507](https://github.com/vitofranzosi/processo_seletivo/pull/507) [#510](https://github.com/vitofranzosi/processo_seletivo/pull/510) | implementada | checkboxes T021 e T032 desatualizados | CONCLUÍDA | ENCERRAR |
| Publicação de convocados / convocar e publicar | 149, 159 | `convocar-e-publicar` | [#470](https://github.com/vitofranzosi/processo_seletivo/pull/470) [#503](https://github.com/vitofranzosi/processo_seletivo/pull/503) [#504](https://github.com/vitofranzosi/processo_seletivo/pull/504) | implementada | status "Em implementação" | CONCLUÍDA | ENCERRAR |
| Envio de vários documentos | 150 | `150-implementacao`, `150-us5-mesmo-arquivo`, `150-envio-unico-dos-documentos` | [#471](https://github.com/vitofranzosi/processo_seletivo/pull/471) [#483](https://github.com/vitofranzosi/processo_seletivo/pull/483) [#496](https://github.com/vitofranzosi/processo_seletivo/pull/496) [#509](https://github.com/vitofranzosi/processo_seletivo/pull/509) [#516](https://github.com/vitofranzosi/processo_seletivo/pull/516) | US1–US5 implementadas | fechamento: T035 (jornada "4 escolhidos, 1 recusado"), T038, T041 (`rastreabilidade.md`) e T042 (matriz do SC-1801); T040 é humana | INCOMPLETA (só o fechamento) | registrar; não bloqueia a limpeza |
| Prevenção nos atos irreversíveis | 152 | `152-conferencias`, `152-desfecho-que-cabe-362ce1` | [#489](https://github.com/vitofranzosi/processo_seletivo/pull/489) [#502](https://github.com/vitofranzosi/processo_seletivo/pull/502) [#520](https://github.com/vitofranzosi/processo_seletivo/pull/520) | US1, US3, US4, US5 e US6 | **US2** (ciência do prazo no indeferimento, T012–T015) — só existe a fundação; também T034, T037 e T038 | INCOMPLETA | registrar; status "Draft" defasado |
| Formalização na jornada | 153 | `153-formalizacao-implementacao` | [#476](https://github.com/vitofranzosi/processo_seletivo/pull/476) [#486](https://github.com/vitofranzosi/processo_seletivo/pull/486) | implementada | status "Em implementação" | CONCLUÍDA | ENCERRAR |
| Convocação depois do envio | 154 | `154-implementacao`, `154-us3-nome-do-reenviado` | [#479](https://github.com/vitofranzosi/processo_seletivo/pull/479) [#484](https://github.com/vitofranzosi/processo_seletivo/pull/484) [#497](https://github.com/vitofranzosi/processo_seletivo/pull/497) [#514](https://github.com/vitofranzosi/processo_seletivo/pull/514) | US1 e US3 | **US2 inteira** (T016–T020), T036–T038 | INCOMPLETA | registrar; status "sem código" defasado |
| Destinação da vaga sem concorrente | 155 | `155-implementacao` (mínima); `155-destinacao-completa` e tag `155-destinacao-completa` (completa) | [#482](https://github.com/vitofranzosi/processo_seletivo/pull/482) [#491](https://github.com/vitofranzosi/processo_seletivo/pull/491) [#495](https://github.com/vitofranzosi/processo_seletivo/pull/495) | entrega mínima (vaga não preenchida, desfazimento) | 33 tarefas "(próxima entrega)" de propósito; T047–T050 dependem da D-015. A versão completa (`091f2346`) é **ancestral** da `main`, mas foi retirada da árvore; a migration 0005 tem lá outro nome | INCOMPLETA / BLOQUEADA (D-015) | PRESERVAR a branch e a tag, que as specs citam |
| Comunicação do desfecho | 156 | `156-textos-sem-jargao-b3b945` (sessão rodando) | spec [#485](https://github.com/vitofranzosi/processo_seletivo/pull/485) [#488](https://github.com/vitofranzosi/processo_seletivo/pull/488) [#493](https://github.com/vitofranzosi/processo_seletivo/pull/493); código [#525](https://github.com/vitofranzosi/processo_seletivo/pull/525) aberto | só a spec (0/54) | o #525 traz as fases 1–3 e a US2 (14 tarefas); faltam US1, US3–US8 e o fechamento; a T023 esbarra na FR-3740 da 118 | PENDENTE DE MERGE (#525) / INCOMPLETA | manter a sessão aberta (P1-2) |
| Conferência com o documento à vista | 157 | `157-implementacao` | [#481](https://github.com/vitofranzosi/processo_seletivo/pull/481) [#494](https://github.com/vitofranzosi/processo_seletivo/pull/494) | implementada | status "Draft"; leitor de tela, celular real e tempo medido são humanos | CONCLUÍDA | ENCERRAR |
| Passagem entre cotas | 158 | `158-passagem-entre-cotas` | [#492](https://github.com/vitofranzosi/processo_seletivo/pull/492) ([#490](https://github.com/vitofranzosi/processo_seletivo/pull/490) fechado) | só a spec | P-1 a P-8 sem resposta | BLOQUEADA (decisão sua) | ENCERRAR a sessão; a spec espera |
| Jornada final (estudos) | — | `teste-aberto-por-voce`, `textos-da-jornada-final`, `jornada-final-*` | [#472](https://github.com/vitofranzosi/processo_seletivo/pull/472) [#477](https://github.com/vitofranzosi/processo_seletivo/pull/477) [#499](https://github.com/vitofranzosi/processo_seletivo/pull/499) [#517](https://github.com/vitofranzosi/processo_seletivo/pull/517) | estudo de 11/11 na `main` | a reavaliação de 12/11 (16 MB, 40 imagens e o `contexto-para-outro-agente.md`) está **fora do git, por decisão sua**; o contexto diz, por engano, que o #492 não foi mergeado | CONCLUÍDA, menos o estudo de 12/11 | PRESERVAR (P0-10) |
| Designação pela presidência | 117 (revista) | `117-designacao-pela-presidencia-9d4f1c` | [#501](https://github.com/vitofranzosi/processo_seletivo/pull/501) | implementada | o achado que pedia a mudança está fora do git e foi resolvido pelo #501; o **tutorial da formalização** da equipe, também fora do git, ainda diz que só a gestão de acessos designa | CONCLUÍDA | PRESERVAR o tutorial (P0-8) |
| Cenários de treinamento | 134-cenarios | `134-*` | [#436](https://github.com/vitofranzosi/processo_seletivo/pull/436) [#438](https://github.com/vitofranzosi/processo_seletivo/pull/438) [#500](https://github.com/vitofranzosi/processo_seletivo/pull/500) [#513](https://github.com/vitofranzosi/processo_seletivo/pull/513) [#518](https://github.com/vitofranzosi/processo_seletivo/pull/518) [#522](https://github.com/vitofranzosi/processo_seletivo/pull/522) | implementada (C01–C17, `--dias-atras`) | T017 (operação) e T018 (humana); a faixa FR-4601+ colide com a `134-aviso` | CONCLUÍDA | ENCERRAR; a colisão vai para P2 |
| Guia "GPS por Dentro" | 133-guia (POC) | `codex/133-guia-visual-conceitos` (checkout principal) | [#433](https://github.com/vitofranzosi/processo_seletivo/pull/433) | guia mergeado | o checkout principal tem a versão "autocontida", fora do git (gerador, HTML de 3,9 MB, README e verificador modificados); a spec não tem status e reusa FR-001 a FR-009 | CONCLUÍDA, com resto local | CONSOLIDAR (P0-11) |
| Vitrine paginada | — (sem spec) | `selective-process-discovery-ux-2cf327` | [#524](https://github.com/vitofranzosi/processo_seletivo/pull/524) aberto | ausente | CI verde, mescla limpo; acrescenta a entrada `vitrine-paginada` ao `launch.json` | PENDENTE DE MERGE | decisão sua (P1-1) |
| UX da Retificação | 123 | `123-implementacao` (worktree `upbeat-haslett-9d4178`) | spec [#409](https://github.com/vitofranzosi/processo_seletivo/pull/409) | só a spec, status "só documental" | **21 arquivos modificados e 8 novos, sem commit** (06/11): T002–T007, T012–T015 e T017; 492 commits atrás da `main` | INCOMPLETA | PRESERVAR (P0-1) |
| Cronograma no PDF | 144 | `144-a-visibilidade-no-pdf` | [#454](https://github.com/vitofranzosi/processo_seletivo/pull/454) [#456](https://github.com/vitofranzosi/processo_seletivo/pull/456) | incremento A | B (ordenar por início) e C (prévia) não começaram; não há branch | INCOMPLETA | registrar; status correto |

## 2. Frentes anteriores com pendência ou estado a esclarecer

| Frente | Spec | Branch | PR | Estado na `main` | Pendência | Classificação | Ação |
|---|---|---|---|---|---|---|---|
| Ordem por recorte, instrução do recurso, painel de condução | 034, 036, 038 | — | [#138](https://github.com/vitofranzosi/processo_seletivo/pull/138) [#142](https://github.com/vitofranzosi/processo_seletivo/pull/142) [#149](https://github.com/vitofranzosi/processo_seletivo/pull/149) | implementadas | `tasks.md` com 0 marcadas e status "Draft" | CONCLUÍDA | ENCERRAR (status em P2) |
| Consolidação do resultado da Etapa | 013 | — | [#25](https://github.com/vitofranzosi/processo_seletivo/pull/25) [#26](https://github.com/vitofranzosi/processo_seletivo/pull/26) [#35](https://github.com/vitofranzosi/processo_seletivo/pull/35) | implementada | T063 (375 px) provavelmente perdeu o sentido com as telas refeitas | CONCLUÍDA | ENCERRAR |
| Exportação de matrículas | 031 | — | [#127](https://github.com/vitofranzosi/processo_seletivo/pull/127) [#130](https://github.com/vitofranzosi/processo_seletivo/pull/130) | implementada | Q-1 a Q-3 e Q-7 com o Registro Acadêmico; importação real (SC-143) | BLOQUEADA (externa) | manter |
| Frontend administrativo | 002 | — | — | entregue | T053–T055, T057 e T059 são institucionais; T056 (LDAP) foi substituída pela 106; T058 foi resolvida pelas 091/092 | INCOMPLETA (institucional) | manter |
| Catálogo de modalidades | 039 | — | [#175](https://github.com/vitofranzosi/processo_seletivo/pull/175) (só a spec) | nunca implementada, e contrariada pela 043/044 | encerramento formal: item 1 da DP-08 | BLOQUEADA (decisão sua) | manter |
| Leitura do não publicado | 112 | — | [#359](https://github.com/vitofranzosi/processo_seletivo/pull/359) (só a spec) | não implementada | pendências de produto | BLOQUEADA (decisão sua) | manter |
| Kit e templates de divulgação | 111, 119 | `119-*` (6 worktrees), `dreamy-mendel`, `silly-leavitt`, `sweet-rosalind` | [#361](https://github.com/vitofranzosi/processo_seletivo/pull/361) [#364](https://github.com/vitofranzosi/processo_seletivo/pull/364) [#377](https://github.com/vitofranzosi/processo_seletivo/pull/377) [#378](https://github.com/vitofranzosi/processo_seletivo/pull/378) [#382](https://github.com/vitofranzosi/processo_seletivo/pull/382)–[#393](https://github.com/vitofranzosi/processo_seletivo/pull/393) | implementados | status "Não implementada"; as imagens dos PRs estão nas branches órfãs `claude/119-*-previas` | CONCLUÍDA | ENCERRAR as worktrees; PRESERVAR as `-previas` |
| Prévia da classificação | 094 | — | [#316](https://github.com/vitofranzosi/processo_seletivo/pull/316) [#317](https://github.com/vitofranzosi/processo_seletivo/pull/317) [#320](https://github.com/vitofranzosi/processo_seletivo/pull/320) | fatia 1 implementada | status "implementação não iniciada"; T039 é humana | CONCLUÍDA (fatia 1) | ENCERRAR |
| Configuração da classificação (estudo) | — | `gps-classification-config-ux-294027` | — | ausente | 5 commits **só locais** (01/11): o estudo da rodada 2 e scripts. O teste A11 da branch foi superado pela versão da `main` (`a74642ba`, `70bb4012`) | INDETERMINADA | CONSOLIDAR ou descartar (P0-4) |
| Revisão dos cronogramas (estudo) | — (depois da 101) | `estudo-visualizacao-cronogramas-1950cd` | — | ausente | 6 commits **só locais** (01/11), 81 arquivos, protótipo e relatório; nenhuma spec o cita | INDETERMINADA | CONSOLIDAR ou descartar (P0-5) |
| Documentos da convocação sem forma no PDF (achado) | — | `edital-pdf-formatting-3963ad` | — | ausente | 1 commit **só local** (12/11); a `main` não tem tratamento desse trecho | INDETERMINADA | CONSOLIDAR (P0-6) |
| Remissão a anexo clicável (estudo de 19/10) | — | worktree destacada `edital-clickable-annexes-0c0d80` | — | ausente | um `.md` de 36 KB, fora do git | INDETERMINADA | PRESERVAR ou descartar (P0-10) |
| Revisão final da 104 | 104 | worktree destacada `silly-cerf-78b884` | — | spec mergeada | 3 PDFs de relatório e 1 captura, fora do git (6 MB) | DESCARTÁVEL, se os PDFs forem só derivados | decisão sua (P0-10) |
| Filme de apresentação | — | worktree destacada `processo-seletivo-video-519ad6` | — | ausente (o #286 é o filme de **lançamento**, outro) | `video/` fora do git: cerca de 42 MB de fonte e 19 GB de `out/` renderizado | INDETERMINADA, com valor | PRESERVAR (P0-2) |

## 3. Branches com conteúdo fora da `main` ou com papel de referência

| Branch | Onde | Conteúdo exclusivo | Por que existe | Ação |
|---|---|---|---|---|
| `claude/156-textos-sem-jargao-b3b945` | local e remota | 2 commits | o #525, aberto | manter |
| `claude/selective-process-discovery-ux-2cf327` | local e remota | 1 commit | o #524, aberto | manter |
| `claude/operation-vs-task-execution-5e2d5c` | **só local** | 1 commit | auditoria de 13/11 | P0-3 |
| `claude/gps-classification-config-ux-294027` | **só local** | 5 commits | estudo de 01/11 | P0-4 |
| `claude/estudo-visualizacao-cronogramas-1950cd` | **só local** | 6 commits | estudo de 01/11 | P0-5 |
| `claude/edital-pdf-formatting-3963ad` | **só local** | 1 commit | achado de 12/11 | P0-6 |
| `claude/gps-work-centered-model-4c557f` | **só local** | 4 commits, mas conteúdo idêntico ao da `main` | estudo da 160 | ENCERRAR depois de P0-9 |
| `claude/achado-jornada-do-candidato-na-convocacao` | só local (a remota sumiu) | 1 commit, superado pelo [#375](https://github.com/vitofranzosi/processo_seletivo/pull/375) | o comentário do #374 pede preservá-la "como referência histórica" | decisão sua (P2) |
| `claude/intelligent-robinson-4466a5` | local e remota | 1 patch, superado pelo [#488](https://github.com/vitofranzosi/processo_seletivo/pull/488) | o #487, fechado | ENCERRAR (P2) |
| `claude/155-destinacao-completa` e tag `155-destinacao-completa` | local, remota e tag | nada fora do histórico, mas fora da árvore | as specs 155 (`plan.md`, `data-model.md`, `rastreabilidade.md`) a citam | PRESERVAR |
| `claude/119-{fic,libras,3c-uab,internos,tmd}-previas` | só remotas, órfãs | 3 a 6 PNG cada | os corpos dos PRs #386, #387, #391, #392 e #393 linkam imagens pelo SHA destes commits | PRESERVAR, ou aceitar imagens quebradas |
| `001-decisoes-pendentes` | só remota | 1 commit (19/10), cerca de 109 arquivos em `doc/saneamento-2026-10-16/` | **Vito Franzosi** | não tocar; perguntar a ele |
| `002-inserir-documentacao-sistema` | só remota | 3 patches, e o [#329](https://github.com/vitofranzosi/processo_seletivo/pull/329) fechado | **Vito Franzosi** | não tocar; perguntar a ele |

## 4. Specs com `**Status**` que contradiz a realidade

São 34 linhas de status a corrigir, sem efeito funcional. O README da raiz já está correto para
todas:

- **Concluídas que dizem "Draft", "só documental" ou "não implementada":** 013, 034, 036, 038, 094,
  110, 111, 117, 119, 120, 122, 128, 129, 133-jornada, 135, 136, 138, 139, 140, 141, 142, 143 e
  157.
- **Concluídas que dizem "PR aberto" ou "aguardando merge":** 064, 088, 090 e 134-aviso.
- **Concluídas que dizem "Em implementação" ou "Especificada":** 127, 149, 153 e 159.
- **Sem status:** 133-guia.
- **Omite a implementação:** 147.
- **Incompletas com status defasado:** 152 ("Draft") e 154 ("sem código").

**Identificadores duplicados.**

- `134-aviso-de-pendencia-documental` (23 FRs) e `134-cenarios-de-treinamento` (20 FRs) começam,
  ambas, em **FR-4601**. A sobreposição alcança `production.py:126`, `test_configuracao_producao.py`,
  `test_ambiente.py` e `test_situacoes_de_mensagem.py`.
- `133-guia-visual-conceitos` define FR-001 a FR-009, os mesmos da 001.
- O guardião `test_citacoes_de_requisito.py` não cobra unicidade.

**Números não usados.** O 137 foi reservado ("O Processo agrega os Editais") e não tem pasta; o
escopo provavelmente foi absorvido pela 147, mas isso é inferência. O 151 foi reservado e
abandonado (a spec dele virou a 153).

## 5. Sessões do app sem PR mergeado

Das 77 sessões não arquivadas deste projeto, 65 têm o PR mergeado. As outras 12:

| Sessão | Situação |
|---|---|
| [156 MVP: textos do desfecho sem jargão](#local_1b0e8e48-4586-4e59-b005-1adabad1c5a3) | **rodando**; #525 aberto |
| [UI/UX melhorias para descoberta de processos seletivos](#local_fa68cc00-d769-46ff-afe2-34dfeec11344) | #524 aberto |
| [Operação versus execução de tarefas](#local_3051c591-417a-4f7e-81e1-ac1a7a9f49e9) | commit só local (P0-3) |
| [Modelo centrado no trabalho para GPS](#local_bc61eab2-2620-4515-b1e4-dd5fb09cc5c5) | capturas fora do git (P0-9) |
| [Formatação do edital em PDF](#local_fc8cb1aa-b319-4641-8970-061fbfebed0c) | commit só local (P0-6) |
| [Visão da secretaria acadêmica na entrega de documentos](#local_f1239b91-d261-4585-b916-b450bb756c99) | tutorial fora do git (P0-8) |
| [UX e redesenho da configuração de classificação GPS](#local_da9a0009-84e9-465e-a609-dbf00c002c62) | commits só locais (P0-4) |
| [Estudo visualização cronogramas editais](#local_d7402cdb-9b80-4f55-81ad-ae8037870c23) | commits só locais (P0-5) |
| [Spec da passagem da vaga entre cotas](#local_a4cef7e7-8f1d-474a-a9b2-1f8a764bc0c8) | #490 fechado, substituído pelo #492; nada a fazer |
| [Verificação do sistema](#local_18918917-bf27-404d-927a-6278a6f1486a) | branch integrada, sem trabalho próprio |
| [Publicação de lista em edital sem sorteio](#local_70140e35-f5ff-41b1-8175-cc0213ca8723) | branch integrada, sem trabalho próprio |
| [Estudo visual das etapas de avaliação](#local_1bf68526-de5a-4b90-bf15-67c4343cc4f6) | branch integrada, sem trabalho próprio |

Limitação: os históricos das sessões não foram lidos. Uma sessão sem PR pode ter conversado
decisões que não deixaram arquivo. As worktrees em HEAD destacado sem sessão ativa
(`edital-clickable-annexes`, `processo-seletivo-video`, `silly-cerf`, `pr-merges-cleanup`,
`sistema-selecao`, `sistema-subindo` e `gps-kit-divulgacao-viabilidade`) foram julgadas só pelo
conteúdo do disco.

## Apêndice — as 72 worktrees integradas, limpas e sem commit exclusivo

> **Correção de 13/11, na limpeza:** 13 destas tinham uma modificação local no
> `.claude/launch.json` (entrada de preview) que o contador da auditoria não viu. Os diffs foram
> salvos antes da remoção, em `~/Projetos/processo-seletivo-preservacao-2026-11-13/launch-json-locais/`.

Todas têm o HEAD contido na `main` (`git rev-list origin/main..HEAD` vazio) e `git status` limpo. A
coluna "Atrás da `main`" é o número de commits.

| Worktree | Branch | Último commit | Atrás da `main` | PR | Sessão |
|---|---|---|---|---|---|
| `sistema-selecao-f933f9` | `DETACHED` | `b4a1abf4` 2026-10-12 | 1070 | — | — |
| `sistema-subindo-b42f0f` | `DETACHED` | `6fc3a85a` 2026-10-16 | 1005 | — | — |
| `pr-merges-cleanup-d95de5` | `DETACHED` | `14efe941` 2026-10-21 | 838 | — | — |
| `gps-audit-enrollment-docs-253134` | `claude/gps-audit-enrollment-docs-253134` | `25ff20d7` 2026-11-03 | 663 | [#367](https://github.com/vitofranzosi/processo_seletivo/pull/367) | GPS auditoria funcional e arquitetural |
| `119-3d-aperfeicoamento-6b2412` | `claude/119-3d-aperfeicoamento` | `671af707` 2026-11-04 | 566 | [#389](https://github.com/vitofranzosi/processo_seletivo/pull/389) | Spec 119, incremento 3d: Aperfeiçoamento |
| `a11-edital-encerramento-diagnostico-a392fa` | `claude/beautiful-einstein-dd75ba` | `be8b69cb` 2026-11-04 | 574 | [#385](https://github.com/vitofranzosi/processo_seletivo/pull/385) | Corrigir convocação por sucessão pela gestão |
| `dreamy-mendel-47e5d4` | `claude/119-templates-de-divulgacao` | `234e69bf` 2026-11-04 | 600 | [#378](https://github.com/vitofranzosi/processo_seletivo/pull/378) | Spec: templates de divulgação por família e formato |
| `edital-concurso-numero-errado-b45d55` | `claude/vigorous-easley-507187` | `2b770ddf` 2026-11-04 | 603 | [#381](https://github.com/vitofranzosi/processo_seletivo/pull/381) | Recusar o Requerimento com o Processo encerrado (029) |
| `exciting-williams-195be7` | `claude/busy-hofstadter-5f006e` | `33a92518` 2026-11-04 | 585 | [#384](https://github.com/vitofranzosi/processo_seletivo/pull/384) | Implementar a spec 118 (jornada do convocado) |
| `gps-kit-divulgacao-viabilidade-63c68e` | `DETACHED` | `a3e23b1f` 2026-11-04 | 567 | [#361](https://github.com/vitofranzosi/processo_seletivo/pull/361) | GPS Kit de Divulgação — Estudo de Viabilidade |
| `hopeful-feistel-13dbd9` | `claude/hopeful-feistel-13dbd9` | `9cedcc6b` 2026-11-04 | 624 | [#375](https://github.com/vitofranzosi/processo_seletivo/pull/375) | Revisão UX da jornada do candidato convocado |
| `silly-leavitt-454b8e` | `claude/119-incremento-3a-fic` | `83d2ec78` 2026-11-04 | 565 | [#387](https://github.com/vitofranzosi/processo_seletivo/pull/387) | Spec 119, incremento 3a: família FIC |
| `sweet-blackwell-dc658d` | `claude/requerimento-com-processo-encerrado` | `d3847845` 2026-11-04 | 602 | [#380](https://github.com/vitofranzosi/processo_seletivo/pull/380) | Spec SDD: jornada consolidada do candidato convocado |
| `sweet-rosalind-1204e0` | `claude/119-incremento-2` | `2314344f` 2026-11-04 | 568 | [#383](https://github.com/vitofranzosi/processo_seletivo/pull/383) | Spec 119: incremento 1 (motor generalizado) |
| `119-3b-libras-346e17` | `claude/119-3b-libras-346e17` | `d93e575b` 2026-11-05 | 545 | [#391](https://github.com/vitofranzosi/processo_seletivo/pull/391) | Spec 119, incremento 3b: Libras e a Inter |
| `119-3c-uab-f69ce3` | `claude/119-3c-uab-f69ce3` | `710cde2c` 2026-11-05 | 548 | [#386](https://github.com/vitofranzosi/processo_seletivo/pull/386) | Spec 119, incremento 3c: família UAB |
| `119-3e-internos-f3857e` | `claude/119-3e-internos-f3857e` | `4c4e9702` 2026-11-05 | 544 | [#393](https://github.com/vitofranzosi/processo_seletivo/pull/393) | Spec 119, incremento 3e: Internos |
| `119-3f-tmd-332ce2` | `claude/119-3f-tmd-332ce2` | `2f700458` 2026-11-05 | 544 | [#392](https://github.com/vitofranzosi/processo_seletivo/pull/392) | Spec 119, incremento 3f: TMD |
| `beautiful-herschel-1c10b5` | `claude/121-plano` | `fa22b587` 2026-11-05 | 523 | [#399](https://github.com/vitofranzosi/processo_seletivo/pull/399) | Spec do incremento 1 da convocação |
| `classification-links-review-bade10` | `claude/classification-links-review-bade10` | `26f14041` 2026-11-05 | 524 | [#398](https://github.com/vitofranzosi/processo_seletivo/pull/398) | Links de classificação confusos |
| `documentacao-kit-divulgacao-6c98e7` | `claude/achado-comunicacao-ao-convocado` | `c78fdb8b` 2026-11-05 | 513 | [#401](https://github.com/vitofranzosi/processo_seletivo/pull/401) | Documentação e kit de divulgação |
| `estudo-visual-avaliacao-f57463` | `claude/estudo-visual-avaliacao-f57463` | `21b728af` 2026-11-05 | 533 | — | Estudo visual das etapas de avaliação |
| `gps-edital-retificacao-ux-5a7690` | `claude/gps-edital-retificacao-ux-5a7690` | `e9669f6c` 2026-11-05 | 509 | [#406](https://github.com/vitofranzosi/processo_seletivo/pull/406) | GPS edital retificação UX |
| `intelligent-almeida-3bdc3e` | `claude/121-implementacao` | `c3bae38c` 2026-11-05 | 506 | [#404](https://github.com/vitofranzosi/processo_seletivo/pull/404) | Implementar a spec 121, incremento 1 |
| `jolly-hermann-9a51d1` | `claude/jolly-hermann-9a51d1` | `b474057f` 2026-11-05 | 542 | [#394](https://github.com/vitofranzosi/processo_seletivo/pull/394) | Estudo: convocação — portal, e-mail e acesso |
| `gps-processos-seletivos-diagnostico-d9db4f` | `claude/gps-processos-seletivos-diagnostico-d9db4f` | `02329ceb` 2026-11-06 | 438 | [#420](https://github.com/vitofranzosi/processo_seletivo/pull/420) | GPS Processos Seletivos página diagnóstico |
| `interesting-antonelli-d15d99` | `claude/interesting-antonelli-d15d99` | `0941c03c` 2026-11-06 | 426 | [#422](https://github.com/vitofranzosi/processo_seletivo/pull/422) | Planejar e implementar a spec 129 (lista de Processos) |
| `silly-engelbart-07c8f4` | `claude/silly-engelbart-07c8f4` | `1555ada2` 2026-11-06 | 430 | [#421](https://github.com/vitofranzosi/processo_seletivo/pull/421) | Advertir providências ao encerrar o Processo |
| `edital-control-center-ux-4be677` | `claude/edital-control-center-ux-4be677` | `6d64f17d` 2026-11-09 | 362 | [#439](https://github.com/vitofranzosi/processo_seletivo/pull/439) | Centro de Controle do Edital — UI/UX |
| `126-orientacao-p0-307906` | `claude/vaga-card-participants-access-e55d90` | `be47fee9` 2026-11-10 | 290 | [#459](https://github.com/vitofranzosi/processo_seletivo/pull/459) | Acesso a participantes no cartão de vaga |
| `140-conferencia-ao-convocar-d54ffb` | `claude/140-conferencia-ao-convocar-d54ffb` | `a8b60663` 2026-11-10 | 336 | [#448](https://github.com/vitofranzosi/processo_seletivo/pull/448) | Spec 140: conferência antes de convocar (M-04) |
| `141-sucessora-espera-reabilitado-af020a` | `claude/141-sucessora-espera-reabilitado-af020a` | `880c5b36` 2026-11-10 | 338 | [#449](https://github.com/vitofranzosi/processo_seletivo/pull/449) | Spec 141: sucessora e corte esperam o reabilitado (F-2) |
| `cadastro-processos-seletivos-42ad72` | `claude/resize-date-time-fields-00adf4` | `49de8beb` 2026-11-10 | 295 | [#457](https://github.com/vitofranzosi/processo_seletivo/pull/457) | Redimensionar campos de data/hora |
| `gps-jornada-operacional-b991ed` | `claude/gps-barema-investigation-1750ab` | `0acb44fd` 2026-11-10 | 280 | [#460](https://github.com/vitofranzosi/processo_seletivo/pull/460) | GPS barema investigation and specification |
| `gps-schedule-config-preview-991e36` | `claude/144-a-visibilidade-no-pdf` | `24659deb` 2026-11-10 | 296 | [#456](https://github.com/vitofranzosi/processo_seletivo/pull/456) | GPS cronograma — configuração e prévia |
| `convocacao-validation-message-7ea376` | `claude/convocacao-validation-message-7ea376` | `bb9af999` 2026-11-11 | 256 | [#473](https://github.com/vitofranzosi/processo_seletivo/pull/473) | Mensagem de validação na convocação |
| `draft-save-error-b64ca5` | `claude/competent-euclid-c9882c` | `e59da15f` 2026-11-11 | 276 | [#461](https://github.com/vitofranzosi/processo_seletivo/pull/461) | Spec 146: implementar o incremento A do barema |
| `eager-snyder-f9441b` | `claude/153-formalizacao-implementacao` | `dceb3eb9` 2026-11-11 | 200 | [#486](https://github.com/vitofranzosi/processo_seletivo/pull/486) | Spec: formalização na jornada guiada (UX-05) |
| `gps-corte-conferencia-ui-53d962` | `claude/gps-corte-conferencia-ui-53d962` | `febe05b2` 2026-11-11 | 263 | [#468](https://github.com/vitofranzosi/processo_seletivo/pull/468) | GPS UI/UX — Corte e Conferência |
| `gps-inscricoes-publicacao-93355f` | `claude/gps-inscricoes-publicacao-93355f` | `b67c70f1` 2026-11-11 | 252 | [#469](https://github.com/vitofranzosi/processo_seletivo/pull/469) | GPS: Publicação e homologação de inscrições |
| `gps-processo-seletivo-ui-ux-a59d79` | `claude/gps-processo-seletivo-ui-ux-a59d79` | `824d6967` 2026-11-11 | 260 | [#466](https://github.com/vitofranzosi/processo_seletivo/pull/466) | GPS Processo Seletivo UI/UX revisão |
| `gps-ui-ux-polish-three-screens-fa56bf` | `claude/gps-ui-ux-polish-three-screens-fa56bf` | `433d2548` 2026-11-11 | 254 | [#467](https://github.com/vitofranzosi/processo_seletivo/pull/467) | GPS UI/UX polish — três telas operacionais |
| `inspiring-neumann-1ec350` | `claude/158-passagem-entre-cotas` | `00fb6280` 2026-11-11 | 158 | [#492](https://github.com/vitofranzosi/processo_seletivo/pull/492) [#490](https://github.com/vitofranzosi/processo_seletivo/pull/490) | Spec da passagem da vaga entre cotas |
| `lista-edital-sem-sorteio-26e66c` | `claude/lista-edital-sem-sorteio-26e66c` | `d3e98a89` 2026-11-11 | 264 | — | Publicação de lista em edital sem sorteio |
| `operacoes-sem-inscricao-5cc79a` | `claude/caixas-na-largura-da-pagina` | `d0ae337c` 2026-11-11 | 263 | [#465](https://github.com/vitofranzosi/processo_seletivo/pull/465) | Operações sem inscrição em modalidade |
| `sharp-gould-0f18b2` | `claude/sharp-gould-0f18b2` | `40b6e58d` 2026-11-11 | 212 | [#479](https://github.com/vitofranzosi/processo_seletivo/pull/479) | Spec de revisão: achados 20 e 23 do portal |
| `stoic-newton-ea19a6` | `claude/152-plano-e-tarefas` | `2c8ac5d1` 2026-11-11 | 209 | [#480](https://github.com/vitofranzosi/processo_seletivo/pull/480) | Spec: prevenção nos atos da convocação |
| `test-protocol-review-043860` | `claude/test-protocol-review-043860` | `8f7a2084` 2026-11-11 | 231 | [#474](https://github.com/vitofranzosi/processo_seletivo/pull/474) | Revisão do protocolo de testes |
| `vibrant-varahamihira-11a2d7` | `claude/146-barema-incremento-c` | `d22060e2` 2026-11-11 | 268 | [#463](https://github.com/vitofranzosi/processo_seletivo/pull/463) | Spec 146: implementar os incrementos B e C do barema |
| `117-designacao-pela-presidencia-9d4f1c` | `claude/117-designacao-pela-presidencia-9d4f1c` | `38097b6d` 2026-11-12 | 88 | [#501](https://github.com/vitofranzosi/processo_seletivo/pull/501) | 117: a presidência também designa a formalização |
| `134-treino-da-formalizacao-b5bbbc` | `claude/134-treino-da-formalizacao-b5bbbc` | `54a36e8b` 2026-11-12 | 70 | [#500](https://github.com/vitofranzosi/processo_seletivo/pull/500) | 134: cenário com o setor de formalização pronto |
| `candidate-document-upload-issue-99ca4c` | `claude/150-envio-unico-dos-documentos` | `b401c65b` 2026-11-12 | 45 | [#509](https://github.com/vitofranzosi/processo_seletivo/pull/509) | Upload múltiplo de documentos na convocação |
| `candidato-convocado-ui-polish-26c7f8` | `claude/candidato-convocado-ui-polish-26c7f8` | `32895b44` 2026-11-12 | 88 | [#505](https://github.com/vitofranzosi/processo_seletivo/pull/505) | Candidato Convocado UI/UX Polish |
| `confident-borg-92ee89` | `claude/157-implementacao` | `9a0a6004` 2026-11-12 | 133 | [#494](https://github.com/vitofranzosi/processo_seletivo/pull/494) | Spec 157: visualizador ao lado na conferência |
| `elegant-robinson-e66ed2` | `claude/155-implementacao` | `564dee0a` 2026-11-12 | 110 | [#495](https://github.com/vitofranzosi/processo_seletivo/pull/495) | Spec 155: vaga de cota sem concorrente |
| `gps-candidate-auth-ui-7eeb4b` | `claude/gps-candidate-auth-ui-7eeb4b` | `699931d7` 2026-11-12 | 97 | [#498](https://github.com/vitofranzosi/processo_seletivo/pull/498) | GPS candidato autenticação UI/UX |
| `gps-public-convocacoes-db0f9b` | `claude/convocar-e-publicar` | `e64facf4` 2026-11-12 | 71 | [#504](https://github.com/vitofranzosi/processo_seletivo/pull/504) | GPS convocações públicas nativas |
| `intelligent-robinson-4466a5` | `claude/156-plano-e-tarefas` | `08e4ba1c` 2026-11-12 | 149 | [#493](https://github.com/vitofranzosi/processo_seletivo/pull/493) | Spec 156: comunicação do desfecho ao candidato |
| `lista-inscritos-modalidade-766f6f` | `claude/148-listas-code-review` | `57679fe6` 2026-11-12 | 46 | [#510](https://github.com/vitofranzosi/processo_seletivo/pull/510) | Publicação da lista de inscritos por modalidade |
| `lote-1-jornada-final-4349c7` | `claude/154-us3-nome-do-reenviado` | `3b961279` 2026-11-12 | 29 | [#514](https://github.com/vitofranzosi/processo_seletivo/pull/514) | Lote 1 da jornada final: 23, V-N01 e 11 |
| `lote-1-vn01` | `claude/designar-sem-quem-ja-esta-designado` | `39b1ea2c` 2026-11-12 | 29 | [#515](https://github.com/vitofranzosi/processo_seletivo/pull/515) | — |
| `magical-shaw-8287f0` | `claude/152-conferencias` | `cb8e0b46` 2026-11-12 | 90 | [#502](https://github.com/vitofranzosi/processo_seletivo/pull/502) | Implementar a 152: atalho do indeferimento (MVP) |
| `strange-williamson-c2de4b` | `claude/160-implementacao` | `cd64a2a5` 2026-11-12 | 45 | [#511](https://github.com/vitofranzosi/processo_seletivo/pull/511) | Spec: Minhas atividades (entrega 1) |
| `sweet-tesla-217cc9` | `claude/154-implementacao` | `c8148215` 2026-11-12 | 100 | [#497](https://github.com/vitofranzosi/processo_seletivo/pull/497) | Plano e tarefas da spec 154 |
| `system-check-4e0845` | `claude/system-check-4e0845` | `0907eac8` 2026-11-12 | 108 | — | Verificação do sistema |
| `unruffled-lamport-1394f8` | `claude/150-implementacao` | `3b17e032` 2026-11-12 | 105 | [#496](https://github.com/vitofranzosi/processo_seletivo/pull/496) | Plano e tarefas da spec 150 (achados 01 e 11) |
| `152-desfecho-que-cabe-362ce1` | `claude/152-desfecho-que-cabe-362ce1` | `68a74df5` 2026-11-13 | 7 | [#520](https://github.com/vitofranzosi/processo_seletivo/pull/520) | Achado 12: desfecho conforme a natureza do Edital |
| `agitated-antonelli-fdec49` | `claude/134-dias-atras-nos-cenarios` | `9e8829b8` 2026-11-13 | 2 | [#522](https://github.com/vitofranzosi/processo_seletivo/pull/522) (mergeado durante a auditoria) | A forma como este edital de |
| `intelligent-einstein-1d7b69` | `claude/161-quem-faz-o-que` | `6a7f7841` 2026-11-13 | 8 | [#519](https://github.com/vitofranzosi/processo_seletivo/pull/519) | Spec da entrega 2: 'Quem faz o quê' |
| `lote-1-us5-150` | `claude/150-us5-mesmo-arquivo` | `4aff422f` 2026-11-13 | 18 | [#516](https://github.com/vitofranzosi/processo_seletivo/pull/516) | — |
| `merge-order-950a2a` | `DETACHED` | `99f298de` 2026-11-13 | 0 | [#450](https://github.com/vitofranzosi/processo_seletivo/pull/450) | Ordem de merges |
| `unruffled-kare-050ce7` | `claude/134-frentes-de-trabalho-nos-cenarios` | `f9ac54ac` 2026-11-13 | 28 | [#518](https://github.com/vitofranzosi/processo_seletivo/pull/518) [#513](https://github.com/vitofranzosi/processo_seletivo/pull/513) | Cenários de treinamento para 'Quem faz o quê' |
