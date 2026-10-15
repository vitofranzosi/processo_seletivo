# Inventário documental — auditoria de consolidação de 15/10/2026

**Anexo** da [auditoria de consolidação](../auditoria-de-consolidacao-2026-10-15.md) (§9.1 e §9.5 do
pedido). Base: `main` @ `db428b30`. As datas de documento são as do último commit que o tocou. As
seções 1 a 6 descrevem os documentos **como estavam** na base; a seção 0 diz o que esta auditoria
mudou neles, e a coluna "Atualidade" das linhas alteradas traz o estado **depois** da mudança.

Escopo: documentação de uso e operação. Os achados técnicos de código estão na matriz, e só aparecem
aqui quando contradizem um documento.

## 0. Rastreabilidade documental — o que esta auditoria criou, atualizou e marcou

Revisão de 15/10/2026, contra a `main` em `db428b30`, com a suíte medida (11 297 passando, 11
pulados) e um percurso pelo navegador no `seed_demo`.

| Documento | Ação | O quê | Verificado contra |
|---|---|---|---|
| `doc/auditoria-de-consolidacao-2026-10-15.md` | **criado** | relatório de consolidação (entregável A) | código, specs, git/GitHub, 185 sessões, suíte, navegador |
| `doc/auditoria-de-consolidacao-2026-10-15/matriz-pendencias.md` | **criado** | 172 itens canônicos (B) | idem, item a item |
| `doc/auditoria-de-consolidacao-2026-10-15/rastreabilidade-historica.md` | **criado** | demanda → estado; recuperações das sessões (C) | sessões e specs |
| `doc/auditoria-de-consolidacao-2026-10-15/roadmap-consolidado.md` | **criado** | proposta em ondas (D) | matriz |
| `doc/auditoria-de-consolidacao-2026-10-15/decisoes-pendentes.md` | **criado** | 16 decisões (F) | matriz, achados, respostas literais do usuário |
| `doc/auditoria-de-consolidacao-2026-10-15/inventario-documental.md` | **criado** | este anexo | — |
| `doc/auditoria-de-consolidacao-2026-10-15/capturas/` | **criado** | 4 capturas do percurso de 15/10, com LEIA-ME | navegador |
| `docs/visao-sistema/index.html` + `CHANGELOG-2026-10.md` | **atualizado** | revisão de 15/10: 069–072 entregues, 073 especificada, 8 papéis, "o sistema não está em produção", maturidade recontada, suíte de 15/10 | código da `main`; âncoras e HTML conferidos por parser |
| `doc/manual/00-arquitetura-do-manual.md` | **atualizado** | Revisão 6: oito papéis, H.18 fechada, H.5 fechada em parte, capítulos que faltam (C-06a, C-18a), assistente fora do manual, relação com a Visão do Sistema, G-03 | código e navegador |
| `README.md` | **atualizado** | "O sistema não está em produção", remissão à auditoria; seção Documentação aponta a Visão do Sistema, o manual e o guia; nuance do `DB_RUNTIME_USER` | `config/settings/base.py`, `interface/views.py:628-629` |
| `AGENTS.md` (= `CLAUDE.md`) | **atualizado** | suíte de 15/10 (11 297/11); 94 migrations; `PORTAL_IDENTIDADE_DEMO` não é necessária ao portal; nuance do `DB_RUNTIME_USER` | suíte rodada; `portal/identidade.py:127-134` |
| `backend/.env.example` | **atualizado** | comentário de identidade (o portal não depende de chave) e de `POSTGRES_*` (o `Makefile` as usa) | `portal/identidade.py`, `backend/Makefile` |
| `doc/runbook-base-de-cep.md` | **atualizado** | a recarga forçada passa pelo `manage.py`, porque o `make ceps` sempre usa `--se-mudou` | `backend/Makefile`, `carregar_ceps.py` |
| `doc/roteiro-teste-operacional-assistido-28-2026.md` | **atualizado** | "34 de 34" → "40 de 40", com o sinal de alarme | `seguranca/papeis.py` |
| `specs/066-avisos-complementares/quickstart.md` | **atualizado** | desligar a chave em desenvolvimento exige settings, não variável | `config/settings/development.py` |
| `doc/decisoes-pendentes-da-consolidacao.md` e `doc/auditoria-de-consolidacao-2026-09-26.md` | **marcados como superados** em parte | nota no topo remetendo a esta auditoria; o conteúdo histórico fica | — |
| `doc/implantacao-em-producao-ubuntu.md` | **não alterado, de propósito** | o PR #283, aberto, reescreve 316 linhas dele; as inconsistências (o)–(r) da §5 ficam para depois do merge (GO-42) | — |

## 1. Inventário

Legenda de atualidade: **ATUALIZADO** · **PRECISA DE REVISÃO** · **OBSOLETO** · **REDUNDANTE**.

### 1.1 Documentos de entrada e governança

| Caminho | Público-alvo | Finalidade | Data / versão | Atualidade | Lacunas | Contradições |
|---|---|---|---|---|---|---|
| `README.md` | quem sobe, avalia ou implanta o sistema; dev | garantias, arquitetura (24 módulos), subir por compose/nativo, dado pessoal, produção, verificação, API, tabela de incrementos | 14/10 (`40909b21`) | **ATUALIZADO** (tabela 001–073 completa, guardada por `tests/test_readme_acompanha_o_codigo.py`; 15/10: passou a apontar a Visão do Sistema, o manual, o guia e esta auditoria, e a dizer que o sistema não está em produção) | (antes de 15/10) não apontava para `doc/manual/`, `docs/visao-sistema/` nem `docs/libras/`; não lista papéis; não diz que `make preparar` cria os 3 modelos de aviso (066) — só o AGENTS diz | `README.md:289-294` (par `TEST_DB_ENGINE` + `DB_USER`) × `backend/Makefile:41-42` ("mexer só no [DB_USER] não muda conexão nenhuma") e `config/settings/base.py:343-346` (`DB_RUNTIME_USER` tem precedência); `README.md:120` (ajuste `POSTGRES_USER` na execução nativa) × `backend/.env.example:39-41` ("Na execução nativa elas não fazem nada") |
| `AGENTS.md` (= `CLAUDE.md`, symlink) | agentes e devs | armadilhas não dedutíveis do código; números vivos da suíte | 14/10 (`7dd29e9d`) | **ATUALIZADO** (15/10: as duas derivas corrigidas) | não é documento de operação institucional | `AGENTS.md:110-111` (par com `DB_USER`) × `Makefile:41-42`; `AGENTS.md:115` "hoje são 90" migrations × 94 arquivos `*/migrations/0*.py` |
| `.specify/memory/constitution.md` | governança | autoridade de engenharia e domínio | v1.2.0, ratificada 27/08, emendada 28/09 | **ATUALIZADO** | **não exige manual** nem documentação de usuário por nome. Exige linguagem ubíqua também em "documentação e interfaces" (princípio I, l. 104-110) e "documentação e contratos atualizados" como critério de conclusão (l. 319-321); o princípio VI (l. 238-253) exige cenário demonstrável pelo canal do ator — que é o que o manual ensinaria | — |

### 1.2 Manual (ver §2)

| Caminho | Público-alvo | Finalidade | Data / versão | Atualidade | Lacunas | Contradições |
|---|---|---|---|---|---|---|
| `doc/manual/00-arquitetura-do-manual.md` (2151 l.) | quem **produz** o manual (não é o manual) | arquitetura: públicos, 19 fases, 31 capítulos + trilhas/tarefas/exceções/referência, conceitos, 89 capturas, estratégia visual HTML, lacunas H.1–H.19, plano de 25 sessões | Revisão 5, 06/10, sobre `4602b04` (cobre 019–058); **Revisão 6, 15/10** | **ATUALIZADO como arquitetura** (R6 registra 059–073); o manual em si continua não produzido | sem capítulo para: Autoridades da unidade (060), avisos aos candidatos e modelos (066), fonte de consulta e piloto do assistente (070/071), Edital em linguagem simples (069), jornada pública nova (072) | ver §5 (a)–(f) |
| `doc/manual/01-inventario-de-capturas-revisado.md` | produtor (coleta) | regras de enquadramento, montagem do certame-exemplo, alterações por captura, §R5 | 06/10 (`5e7a8d56`) | **PRECISA DE REVISÃO** | a tabela de coleta das telas novas (§R5.2) não existe — item 5 da S-00R; telas de 059–072 nem listadas | §3.1/§4 (SS-010 "a tela não existe") superados pelo próprio §R5 (l. 204-205) — o documento mantém as duas versões |
| `doc/manual/piloto/index.html`, `c-03-…`, `c-08-especimen-desempate.html`, `c-12-…`, `c-18-…`, `manual.css`, `manual.js`, `capturas/p-01…p-12.png` | leitor final (protótipo) | fixar o padrão editorial | 08/09 (`f46687af`) | **OBSOLETO como conteúdo**; válido só como padrão editorial (decisão do próprio 00, l. 2070-2072) | — | 16 fases e 10 atos (c-03, index); "o e-mail serve só para o código" e "o rascunho não avisa" (c-12); caixa "⛔ Não utilize" da reavaliação (index) — já listados como vencidos em `01-…:231-246` e nunca corrigidos |
| `doc/manual/piloto/relatorio-s00.md` | produtor | 9 respostas de design + decisões D-1…D-10 | 08/09 | **ATUALIZADO como registro histórico** | — | D-8 (sem tela de "Criar Edital") e D-6 (16 traços) superados pela R5 (`00-…:50-51`, `:1622-1625`) |
| `doc/manual/piloto/ferramentas/LEIA-ME.md` (+ `cdp.mjs`, `smtp.mjs`) | produtor (captura) | roteiro de captura por CDP e caixa SMTP local | 08/09 | **PRECISA DE REVISÃO** (item 4 da S-00R, não feito) | não diz que o seletor pede papéis além do nome | `LEIA-ME.md:36-38` (porta 8033, seletor `main article`) × `.claude/launch.json:55-62` (8033 é `auditoria-e2e`, sem SMTP; a entrada `manual-s00` não existe) — o erro já está registrado em `01-…:250-252` |

### 1.3 Operação e implantação

| Caminho | Público-alvo | Finalidade | Data / versão | Atualidade | Lacunas | Contradições |
|---|---|---|---|---|---|---|
| `doc/implantacao-em-producao-ubuntu.md` (2849 l.) | TI / implantador | VM Ubuntu: arquitetura, hardening, banco, segredos, serviço, TLS, proxy, e-mail, smoke test, **backup (§18), restore (§19), logs (§20), monitoramento (§21), atualização (§22), rollback (§23), runbook de incidentes (§24), segurança e LGPD (§25)**, gaps B-1/B-2, cheat sheet, go-live | 14/10 (`b6c1cf62`); ensaiado em 29/09 sem nginx/certbot/ufw/systemd | **ATUALIZADO na maior parte; PRECISA DE REVISÃO pontual** | nenhuma `ASSISTENTE_*` nem Ollama (a `073` reconhece; implementação em branch não mergeada); go-live sem "cadastrar autoridades vigentes da unidade" (sem elas a publicação fica indisponível — `doc/pendencias-da-060.md:41-46`); nenhum passo de concessão de papéis/treinamento | `:1554` "três fluxos" × tabela de **quatro** linhas `:1557-1562`; `:99-101` "os únicos jobs são manutenção e backup" × timer funcional `ps-avisos` (`:2191-2212`); go-live `:2842` lista timers sem `ps-avisos` × `:2212`/`:2223`; `:2529-2530` "os únicos comandos são…" omite `avaliar_assistente`, `verificar_servico_de_inferencia` e `excluir_registros_do_piloto` (`duvidas/management/commands/`) — este último é um comando de expurgo |
| `doc/runbook-base-de-cep.md` | operador / TI | carga inicial, job mensal, conferência no deploy, alertas da base de CEP | 17/09 (`fc900d02`); 15/10 | **PRECISA DE REVISÃO** (15/10: a contradição da recarga corrigida; falta o caminho de produção) | escrito só com `make DB_NAME=…` (dev); o caminho de produção (`ps-manage`, timer `ps-ceps`) está só no guia de implantação (§21.4, `:2170`) | `:115-116` "Recarregar, ignorando o resumo igual" com `make … ceps` × `backend/Makefile:93`, que **sempre** passa `--se-mudou` — com o mesmo arquivo, o comando não recarrega nada; idem a promessa da `:119` |
| `doc/troca-do-servico-do-assistente.md` | equipe do piloto (máquina da equipe) | trocar OpenRouter ↔ Ollama sem levar configuração | 14/10 (`36963296`) | **ATUALIZADO** (variáveis conferidas em `config/settings/base.py:225-273`; "produção só aceita ollama" em `production.py:201-207`) | é de desenvolvimento; o Ollama de produção não tem roteiro na `main` | — |
| `doc/roteiro-teste-operacional-assistido-28-2026.md` | observador do teste com o setor | protocolo do teste operacional (DP-18) | 27/09 (`629fa797`), ensaiado em `f6efe0dd`; 15/10 | **PRECISA DE REVISÃO** (15/10: a contagem de tabelas corrigida) | não conta com 060 (Unidades/autoridades), 066 (modelos), 069 (catálogo novo); "quem e quando" (DP-18) segue aberto | `:50` e `:101` "34 de 34" × `AGENTS.md:40` e `seguranca/papeis.py:26` (40 tabelas) |
| `doc/pendencias-da-060.md` | gestão / implantação | o que a 060 deixou fora e o que a implantação precisa fazer à mão | 14/10 | **ATUALIZADO** | é o único lugar que manda cadastrar as autoridades antes da primeira publicação — o guia de implantação não o repete | — |
| `doc/auditoria-configuracoes-do-sistema-2026-10-14.md` | gestão / TI | quais configurações pedem tela e quais ficam na implantação | 14/10 | **ATUALIZADO** (diagnóstico; originou a 073) | — | — |
| `backend/.env.example` | dev / compose | variáveis do ambiente de desenvolvimento, comentadas | 14/10; 15/10 | **ATUALIZADO** (15/10: comentários de identidade e de `POSTGRES_*` corrigidos) | — | (corrigido) `:39-41` × `Makefile:43-46,70-74` (`test-pg` e `provisionar` usam `POSTGRES_USER/PASSWORD` na execução nativa). `AVISOS_AOS_CANDIDATOS=false` (`:74`) é ignorado em dev, porque `config/settings/development.py:11` força `True` — o comentário `:72-73` diz isso, e está certo |

### 1.4 Documentação funcional paralela

| Caminho | Público-alvo | Finalidade | Data / versão | Atualidade | Lacunas | Contradições |
|---|---|---|---|---|---|---|
| `docs/visao-sistema/index.html` (1 MB) + `CHANGELOG-2026-09.md`, `CHANGELOG-2026-10.md` | servidores, gestão, equipe | "Visão do Sistema": tutorial "Monte um processo seletivo", "O que eu consigo configurar?", "Se eu mudar isso…", receitas, referência por assunto, papéis e matriz de permissões, estados, segurança, catálogo de capacidades, FAQ | 10/10 (`cf7e7f68`); **revisão de 15/10** descreve até a 072 sobre `db428b30` | **ATUALIZADO**; **REDUNDANTE em parte** com o manual planejado (DEC-13) | zero menções a 069, 070, 071, 072, 073 e ao papel "Participante do piloto do assistente"; não lido por nenhum teste (CHANGELOG-10 o diz) | é, na prática, o material de uso mais completo e vigente; a arquitetura do manual não o cita, e ele não cita o manual — tutorial, glossário, papéis e FAQ estão planejados nos dois lugares |
| `docs/libras/README.md` | pesquisa | estudo de viabilidade de Libras | rodada 4, 11/10 | **ATUALIZADO** (estudo; nada implementado) | — | — |

### 1.5 Quickstarts das specs recentes

Todos são **roteiros de validação** para quem desenvolve ou valida a feature (princípio VI), e não
material de operação institucional.

| Caminho | Público-alvo | Finalidade | Data | Atualidade | Lacunas | Contradições |
|---|---|---|---|---|---|---|
| `specs/066-avisos-complementares/quickstart.md` | validador | avisos, despacho, modelos, chave | 09/10; 15/10 | **ATUALIZADO** (15/10: a nota sobre a chave em desenvolvimento) | — | `:99-102` §5a.1 "Desligar `AVISOS_AOS_CANDIDATOS` e reiniciar" × `config/settings/development.py:11`, que força `True`: pela variável de ambiente, em dev, a chave não desliga |
| `specs/069-edital-linguagem-simples/quickstart.md` | dev / validador | validar o Edital em linguagem simples (bancos de antes/depois, motores de renderização) | 12/10 | **ATUALIZADO** | — | — |
| `specs/070-fonte-de-consulta-do-edital/quickstart.md` | validador + setor | suíte e percurso pela gestão | 12/10 | **ATUALIZADO** | Editais 91/92 só pelo ajudante de testes | — |
| `specs/071-piloto-assistente-do-edital/quickstart.md` | equipe do piloto | roteiros A–E (suíte, OpenRouter, sessão com o setor, Ollama na L4, exclusão) | 14/10 | **ATUALIZADO**; D e C dependem da L4 | — | — |
| `specs/072-jornada-publica-do-portal/quickstart.md` | dev | verificação técnica e validações humanas pendentes (SC-605, FR-1627) | 13/10 | **PRECISA DE REVISÃO** | depende de banco `ps_ux_conversao` e da entrada `ux-conversao` (porta 8077) "acrescentada só durante a sessão" — não versionada, irreprodutível por terceiros | — |
| `specs/073-configurar-e-verificar-implantacao/` | TI | spec Draft, **sem plan, tasks nem quickstart** na `main` | 14/10 | **ATUALIZADO para a main** | a implementação (seção §10.4 do guia, recusa do SMTP sem servidor) está na branch **não mergeada** `claude/073-configurar-e-verificar` (`20ec4daf`, "implementada com validação operacional pendente", 7 commits à frente) | — |

### 1.6 Ajuda dentro da interface

| Onde | O que existe | Lacunas |
|---|---|---|
| Gestão — "Como preencher estes campos" (`<details class="como-preencher">`) | `compor_perfis.html:26`, `compor_etapas.html:30`, `compor_inscricao.html:56,117`, `compor_anexos.html:21`, `_como_preencher_o_marco.html:17` (Classificação), `_duplicar_perfil.html` | os passos **Identificação, Cronograma, Conteúdo e Revisão** não têm (contagem 0 em `compor_identificacao/cronograma/conteudo/revisao.html`) |
| Gestão — "Termos desta tela" (glossário local) | `marco.html:25`, `ordenacao.html:22`, `corte.html:27`, `corte_historico.html:25`, `ocupacao.html:21`, `convocacao.html:20`, `sorteio.html:20`, `matriculas.html:23` | nenhum glossário global; nenhum link da gestão para manual ou ajuda |
| Gestão — recusa explicada | `recusa.html`, `lista.html`: "Peça acesso a quem administra o sistema no Cefor" | não existe documento que diga quem administra e como se concede papel |
| Gestão — assistente de dúvidas | `duvidas.html` (070, "validação interna"), `assistente.html` e `prototipo_do_assistente.html` (071) | só piloto; não é ajuda do sistema, é sobre o Edital |
| Portal | `_ajuda_da_acao.html` (o que falta para enviar), `_atendimento.html` (canal `PORTAL_ATENDIMENTO`), finalidade de nome e CPF em `meus_dados.html:15` (072, FR-1627, validação pendente) | sem FAQ, sem página de ajuda, sem aviso de privacidade/termo de uso |

---

## 2. Estado do manual

### 2.1 O que existe

- **Planejamento, em Markdown:** `00-arquitetura-do-manual.md` (Revisões 1–5; a R5 de 06/10 sobre
  `4602b04`) e `01-inventario-de-capturas-revisado.md` (S-00 + §R5).
- **Piloto editorial S-00, em HTML estático** (08/09): `index.html` + **3 páginas** (C-03, C-12, C-18)
  + **1 bloco-espécime** (C-08, só o desempate), `manual.css`, `manual.js`, **12 capturas** `p-01…p-12`,
  ferramentas Node (`cdp.mjs`, `smtp.mjs`). O próprio index diz: *"Isto é um piloto, não o manual."*
- **Nenhum capítulo em versão definitiva.** Nenhuma sessão de produção rodou depois do piloto
  (`00-…:33-34`). Da S-00R (reconciliação) só a metade documental foi feita; os itens 2–5 seguem "a
  fazer" (`00-…:2060-2068`): recapturar o espécime de C-08, regerar o "onde estou" para 19 fases,
  corrigir o LEIA-ME, transformar §R5 em tabela de coleta. Sessões S-01 a S-19 (25 no total): **não
  iniciadas**.
- **Capturas:** 12 do piloto em `doc/manual/piloto/capturas/` — `p-01, p-06, p-08, p-09, p-10`
  vencidas, `p-07` em parte (`01-…:225-229`); `p-05` mostra CPF com DV válido. Do acervo definitivo
  (89 `SS-NNN` + telas novas sem número, §R5.2): **zero coletadas**.

### 2.2 Capítulo a capítulo

| Parte | Código | Título | Estado |
|---|---|---|---|
| 1 | C-01 | O que este sistema faz | planejado |
| 1 | C-02 | As duas portas | planejado |
| 1 | C-03 | O ciclo completo em um mapa | **escrito no piloto** — vencido (16 fases/10 atos; R5 pede 19) |
| 1 | C-04 | Quem faz o quê | planejado (bloco obrigatório "duas ou três pessoas") |
| 1 | C-05 | Seis ideias | planejado |
| 1 | C-22 | A Visão Geral da instituição (R5) | planejado |
| 2 | C-06 | Abrir o Processo, criar Editais, partir de anterior | planejado |
| 2 | C-07 | Elaborar I — identificação, Perfis, quadro, cronograma | planejado |
| 2 | C-08 | Elaborar II — Etapas, marcos, desempate, sorteio, corte, recurso | **só bloco-espécime** (desempate) — vencido (tela da 053) |
| 2 | C-09 | Elaborar III — inscrição, Requerimento, anexos, conteúdo, revisão | planejado |
| 2 | C-10 | Submeter, homologar e publicar | planejado |
| 2 | C-11 | O período de inscrições visto de dentro | planejado |
| 2 | C-11a | Acompanhar o certame (R5) | planejado |
| 2 | C-12 | Inscrever-se — manual do candidato | **escrito no piloto** — vencido (059, 062, 063, 066, 072 posteriores) |
| 2 | C-13 | Comissão e alocação | planejado |
| 2 | C-14 | Distribuir | planejado |
| 2 | C-15 | Avaliar — manual do avaliador | planejado |
| 2 | C-16 | Consolidar | planejado |
| 2 | C-17 | Classificar | planejado |
| 2 | C-17a | Sorteio público (R5) | planejado |
| 2 | C-17b | Corte (R5) | planejado |
| 2 | C-18 | Divulgar o resultado | **escrito no piloto** — vencido (autoridade da 060, portas novas, aviso da 066) |
| 2 | C-19 | Recursos | planejado |
| 2 | C-20 | Refazer e republicar | planejado |
| 2 | C-20a | Ocupação (R5) | planejado |
| 2 | C-20b | Convocação (R5) | planejado |
| 2 | C-20c | Requerimento de Matrícula (R5) | planejado |
| 2 | C-20d | Exportar para matrícula (R5) | planejado |
| 2 | C-21 | Encerrar o certame | planejado |
| 2 | C-21a | Retificar (R5) | planejado |
| 3 | T-01…T-09 | Trilhas: Gestor, Elaborador, Homologador, Publicador, Presidente, Avaliador, Julgador, Candidato, Exportador | planejadas |
| 4 | R-01…R-14 | Tarefas frequentes | planejadas (R-02 não reconferida) |
| 5 | X-01…X-13 | Situações excepcionais | planejadas |
| 6 | G-01…G-05 | Glossário, mapa de telas, o que não faz, FAQ, nota para administradores | planejados |

**Total:** 31 capítulos principais (6 + 25) + 9 trilhas + 14 tarefas + 13 situações + 5 de referência.
Escritos: 3 páginas e 1 espécime, todos de piloto e vencidos. **Sem capítulo previsto** para o que
entrou depois da R5: Autoridades da unidade (060), avisos e modelos de aviso (066), assistente de
dúvidas/piloto (070/071), o documento em linguagem simples (069) e a jornada pública nova (072).

### 2.3 Convenções fixadas

- **Formato:** HTML estático próprio (`manual.css` + `manual.js`), uma página por capítulo
  `c-NN-slug.html`; planejamento em Markdown. **Não** é Markdown publicado nem gerador de site.
- **Anatomia fixa** (relatório S-00 §1.1): breadcrumb → código/parte → título → resumo → "onde estou"
  (só Parte 2, gerado de `data-fase`) → 👤 → 🕒 → corpo (prosa antes de passos) → ✅ → rodapé.
- **Sete callouts, e só sete** (👤 🕒 💡 ⚠️ ⛔ 🔎 ✅) + bloco "Limitação conhecida desta versão" (sem
  emoji) + bloco "por trás disto". Acento único violeta `#5b3a8f`.
- **Capturas:** viewport 1 000 px (celular 375), recorte por fronteira de elemento, PNG a 2×,
  anotação por CSS com coordenadas emitidas pelo roteiro (`data-alvos`), marcadores na ordem de
  leitura; certame-exemplo próprio (Auxiliar de Biblioteca, elenco Gustavo/Elena/Wagner/Paula/Paulo/
  Alice/Otávio/Júlia/Aurora) montado à mão, porque `seed_demo` não o produz e seu elenco colide.
- **Vocabulário:** "imutável", nunca "definitivo"; rótulos exatamente os da tela; nenhum
  identificador técnico no corpo; vocabulário técnico só em `G-05`.
- **Régua de densidade:** 4–20 linhas entre capturas; 850–1 150 palavras por página da Parte 2;
  ≤ 1 caixa por 100 palavras.

### 2.4 O que o `relatorio-s00.md` conclui

As nove perguntas do gate têm resposta: anatomia fixa; régua de densidade; recorte como padrão e tela
inteira só quando o assunto é a tela; retângulo CSS violeta sem número para alvo único e `①②③` na
ordem de leitura; os sete callouts sobreviveram e faltou um **bloco** (não um oitavo callout); "onde
estou" como barra + uma linha de texto; tom "nomear a regra, dizer o efeito, dar a saída"; em 375 px
o que é largo rola dentro da moldura, nada some; C-08 é legível com prosa antes de procedimento e
marcadores numerados. Registra D-1…D-10, das quais D-7 (viewport) e D-8 (sem tela de criar Edital)
contrariavam a arquitetura; D-8 caiu em 16/09.

### 2.5 Decisão do usuário sobre formato e ferramenta

- **Registrada:** "Arquitetura aprovada, com quatro ajustes de direção" (Revisão 2, `00-…:6-13`) —
  inclui o piloto antes da coleta e a separação operação × referência; a equipe inicial de duas a
  três pessoas (Revisão 3, `00-…:15-21`). O formato HTML está na §G ("Estratégia visual do HTML") da
  arquitetura aprovada.
- **Não encontrada:** registro explícito de que o usuário **aprovou o piloto S-00**, que é o gate da
  S-01 (`00-…:2023-2025`). A R5 afirma que "o padrão editorial que o piloto fixou continua valendo"
  (`00-…:2056`) sem citar aprovação. Nenhuma decisão sobre ferramenta de publicação (hospedagem,
  geração de PDF, versão impressa) nem sobre a relação com `docs/visao-sistema/`.

---

## 3. Papéis planejados × reais

Fonte do código: `interface/identidade.py:20-125` (`PAPEIS`, rótulos exibidos no seletor e no topo,
`contexto_identidade`), bases por vínculo em `comissoes/domain/autorizacao.py:23` e
`avaliacoes/application/mesa.py:43`, rótulos humanos em `interface/templatetags/interface_extras.py:126-129`.

| Manual (§A.1, R5 de 06/10) | Código (rótulo exibido) | Permissões no código | Divergência |
|---|---|---|---|
| Elaborador | Elaborador | `edital:elaborar/submeter`, `retificacao:elaborar/submeter` | — |
| Homologador | Homologador | `edital:homologar`, `retificacao:homologar` | o manual diz também "devolver e revogar homologação" — mesmas permissões |
| Publicador | Publicador | `edital:publicar`, `retificacao:publicar`, `resultado:publicar`, **`aviso:enviar`** | manual não tem o aviso aos candidatos (066) |
| Gestor | Gestor | `inscricao:consultar`, `processo:*`, `edital:criar/encerrar/cancelar`, `retificacao:cancelar`, `comissao:gerir`, `visao:consultar`, **`autoridade:gerir`**, **`aviso:enviar`** | manual não tem "manter as autoridades da unidade" (060) nem "avisar candidatos" (066); README:438 e o quickstart da 070 dizem "Gestor da unidade", que não é rótulo de papel |
| Julgador de recursos | Julgador de recursos | `recurso:julgar` | — |
| Auditor | Auditor | `auditoria:consultar` (as telas de leitura aceitam essa permissão: `interface/acoes.py:156,318`, `interface/views.py:4779,6554,7988,8608`) | — |
| Exportador de matrículas | Exportador de matrículas | `matricula:exportar` | — |
| — | **Participante do piloto do assistente** (071) | `assistente:piloto` | **papel real ausente do manual** e de `docs/visao-sistema` (0 menções) |
| Presidência da comissão (vínculo, `comissao:presidir`) | "presidência desta comissão" | base por vínculo | — |
| Avaliador / membro (vínculo, `avaliacao:atribuida`) | base da Mesa | base por vínculo | — |
| Candidato, Público anônimo | portal, sem papel | titularidade | — |

Conclusão: **sete papéis planejados contra oito reais**; nomes iguais nos sete comuns. O manual também
está atrás nas permissões de dois papéis (Publicador e Gestor). Os públicos do manual (§A.2, nove + o
Auditor) e as trilhas T-01…T-09 não têm trilha para o participante do piloto, nem para quem mantém as
autoridades da unidade e os modelos de aviso.

---

## 4. Documentos ausentes para a operação institucional

Conferi se existiam com outro nome antes de declarar a ausência.

| Documento | Situação | Onde está o que existe |
|---|---|---|
| Manual do gestor, elaborador, homologador, publicador, presidência, julgador, exportador | **AUSENTE** (só planejado) | arquitetura em `doc/manual/00-…`; cobertura funcional parcial e vigente até a 068 em `docs/visao-sistema/index.html` (tutorial "Monte um processo seletivo", papéis, FAQ) |
| Manual do avaliador (C-15) | **AUSENTE** | só ficha em `00-…:921-937` |
| Manual do candidato / ajuda do portal / FAQ do candidato | **AUSENTE** em versão vigente | piloto C-12 de 08/09, vencido; portal sem página de ajuda |
| Aviso de privacidade / termo de uso para o candidato | **AUSENTE** | só a frase de finalidade de nome e CPF (`portal/templates/portal/meus_dados.html:15`), com validação pendente (072, FR-1627) |
| Política de retenção e descarte (LGPD) | **AUSENTE** — bloqueador B-2 | precondição em `README.md:222-224`; implicações operacionais em `implantacao…:2483-2498`; nenhum expurgo exceto o do piloto (`excluir_registros_do_piloto`) |
| RIPD / registro das operações de tratamento | **AUSENTE** | — (a base legal da 060 também aguarda o encarregado: `pendencias-da-060.md:47-51`) |
| Guia de administração de acessos (quem concede e revoga papéis, revisão por Processo) | **AUSENTE** | uma linha em `implantacao…:2489,2495`; depende de B-1; a tela de recusa manda procurar "quem administra o sistema no Cefor" sem que isso esteja definido |
| Procedimento do atendimento (canal `PORTAL_ATENDIMENTO`, correção de CPF "só pelo atendimento") | **AUSENTE** | o manual afirma que o CPF passa a ser corrigido pelo atendimento (`00-…:419`), e não encontrei tela nem procedimento para isso (grep sem resultado) |
| Backup e restauração | **EXISTE** | `implantacao…` §18–19 (ensaiado `pg_dump`/restore em 29/09; restic/systemd não ensaiados) |
| Monitoramento | **EXISTE** | `implantacao…` §21 |
| Resposta a incidentes | **EXISTE em parte** | runbook técnico `implantacao…` §24; incidente com dado pessoal é um parágrafo (`:2440-2448`) — falta o plano (papéis, prazos, comunicação à ANPD e aos titulares) |
| Contingência de negócio do certame (correio fora do ar no último dia, erro em Edital publicado, julgador impedido) | **AUSENTE** | previsto como Parte 5 do manual (X-01…X-13), não escrito |
| Plano de capacitação / treinamento | **AUSENTE** | — |
| Cadastro das autoridades antes da primeira publicação | **EXISTE fora do guia** | `doc/pendencias-da-060.md:41-46`; não está no go-live (`implantacao…:2775-2849`) |
| Ollama de produção (instalar, configurar, verificar) | **AUSENTE na main** | spec 073 (Draft); implementação em `claude/073-configurar-e-verificar`, não mergeada |

---

## 5. Contradições encontradas, com evidência

### Manual × código

- **(a) A convocação no portal.** `doc/manual/00-arquitetura-do-manual.md:1152-1154`, `:1172`, `:1909` e
  `:1944-1951` (H.18: "o portal não leva à convocação nem ao Requerimento") × a 059:
  `portal/templates/portal/inscricoes.html:45` (link `portal:convocacao`),
  `portal/templates/portal/_convocacao_da_inscricao.html:25` ("Ver convocação"),
  `portal/templates/portal/_chamado_do_requerimento.html:18` ("Preencher Requerimento de Matrícula").
  O item 2 do backlog do manual está fechado no produto.
- **(b) Os avisos aos candidatos.** `00-…:1049-1050` (C-18: "nenhum candidato é notificado de
  resultado"), `:1253-1254` (G-03: "nunca de resultado, Retificação ou prazo") e `:1797-1801` (H.5) ×
  a 066: `interface/urls.py:475-486` (`aviso-do-resultado`, `aviso-da-chamada`),
  `interface/identidade.py:42,92` (`aviso:enviar`). Ressalva para o texto: em produção a chave fica
  desligada (`config/settings/base.py:203`) até a validação de LGPD.
- **(c) Quantos papéis.** `00-…:43` e `:94` ("São sete") × `interface/identidade.py:117-124` (oitavo
  papel, da 071).
- **(d) O Gestor e as autoridades.** `00-…:101` (o que o Gestor pode) e C-10 ("publicar com
  autoridade signatária", `:799`) × `interface/identidade.py:89` (`autoridade:gerir`), rota
  `interface/urls.py:23` (`autoridades`) e `doc/pendencias-da-060.md:41-46` (sem autoridade vigente, a
  publicação fica indisponível). Nenhum capítulo, captura ou conceito do §E para isso.
- **(e) O README envelheceu de novo no manual.** `00-…:79-83` ("7 dos 17 apps") e `:1938-1940` ("a
  tabela de módulos repete 14 linhas") × `README.md:34-59` (24 módulos = 24 apps de
  `backend/processo_seletivo/`, sem repetição, desde `4705a614`, 10/10).
- **(f) O Conteúdo do Edital.** `00-…:776` ("22 seções fixas, numeradas como sairão no documento")
  × `editais/domain/secoes.py:134-161` (`CATALOGO = CATALOGO_DA_069`: títulos e ordem novos) e
  `:276+` (`APRESENTACAO`, que reúne chaves em subseções). As chaves continuam 22, mas a numeração no
  documento mudou para os Editais novos. A captura SS-021 e a ficha de C-09 precisam ser conferidas.
- **(g) O piloto não foi corrigido.** O próprio `01-…:231-246` lista os trechos vencidos de C-03, C-12,
  C-18, C-08 e do index (16 fases, "o e-mail serve só para o código", "o rascunho não avisa", a caixa
  "Não utilize"), e eles continuam nas páginas de `doc/manual/piloto/`.
- **(h) As ferramentas de captura.** `doc/manual/piloto/ferramentas/LEIA-ME.md:36-38` (porta 8033,
  `main article`) × `.claude/launch.json:55-62` (8033 = `auditoria-e2e`, sem SMTP; não há
  `manual-s00`).

### Operação × código

- **(i) Recarga da base de CEP.** `doc/runbook-base-de-cep.md:115-116,119` × `backend/Makefile:93`
  (`--se-mudou` sempre).
- **(j) Quem usa `POSTGRES_*`.** `backend/.env.example:39-41` × `backend/Makefile:43-46,70-74` e
  `README.md:120,289`.
- **(k) O par da suíte.** `AGENTS.md:110-111` e `README.md:289-294` (`DB_USER`) ×
  `backend/Makefile:41-42` e `config/settings/base.py:343-346` (`DB_RUNTIME_USER` tem precedência).
  O comando do README funciona só com `DB_RUNTIME_USER` fora do ambiente.
- **(l) Tabelas protegidas.** `doc/roteiro-teste-operacional-assistido-28-2026.md:50,101` ("34 de
  34") × `seguranca/papeis.py:26` (40 tabelas) e `AGENTS.md:40`.
- **(m) Migrations.** `AGENTS.md:115` ("hoje são 90") × 94 arquivos `*/migrations/0*.py`.
- **(n) Desligar os avisos em dev.** `specs/066-avisos-complementares/quickstart.md:99-102` ×
  `config/settings/development.py:11`.

### Inconsistências internas do guia de implantação

- **(o)** `doc/implantacao-em-producao-ubuntu.md:1554` ("três fluxos") × a tabela de quatro linhas
  logo abaixo (`:1557-1562`).
- **(p)** `:99-101` ("os únicos jobs são manutenção e backup") × o timer funcional `ps-avisos`
  (`:2191-2212`).
- **(q)** O go-live `:2842` ("Timers ativos: ps-backup, ps-verificar, ps-limpeza, (ps-ceps), certbot")
  × `:2212` e `:2223`, que habilitam e conferem `ps-avisos`.
- **(r)** `:2529-2530` ("os únicos comandos são…") × `duvidas/management/commands/`
  (`avaliar_assistente`, `excluir_registros_do_piloto`, `verificar_servico_de_inferencia`).

---

## 6. A tabela de incrementos do README

- **Está completa até a 073.** São 74 linhas (001–073 mais `012-013`) contra 74 pastas em `specs/`, sem
  pasta faltando. O teste `tests/test_readme_acompanha_o_codigo.py` a mantém assim. A 039 aparece
  marcada como "só especificada, não implementada".
- **A linha da 073** diz "especificada", o que é verdade na `main`: só há `spec.md` e `checklists/`.
  Porém a implementação existe na branch **não mergeada** `claude/073-configurar-e-verificar`
  (`20ec4daf`, 14/10, "implementada com validação operacional pendente"). No merge, a linha muda, e o
  guia de implantação ganha a §10.4.
- **Não há 074** na `main` nem em nenhuma ref commitada. Ela existe só como pasta **não rastreada** na
  worktree `.claude/worktrees/assistente-pagina-edital-local-d6f44f/specs/074-assistente-na-pagina-do-edital-local/`
  (`spec.md`, `plan.md`, `tasks.md`, `quickstart.md`, `rastreabilidade.md`). A branch dessa worktree
  está em `bc6dd96b` e tem `README.md`, `AGENTS.md` e as settings modificados e não commitados.
- **As linhas da 071 e da 072 declaram as pendências humanas** (a L4, o setor, o SC-605 e o FR-1627),
  de acordo com os quickstarts.
