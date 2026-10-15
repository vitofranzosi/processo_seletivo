# Rastreabilidade histórica — da demanda ao estado atual (15/10/2026)

**Entregável C** da [auditoria de consolidação](../auditoria-de-consolidacao-2026-10-15.md).
**Data:** 15/10/2026. **Base:** `main` @ `db428b30` (merge do #282, 14/10). O PR #283 (implementação da
`073`) estava aberto e não entra na base. Os IDs de pendência (`ED-`, `CA-`, `AV-`, `GO-`, `AS-`, `PV-`) são
os canônicos da [matriz de pendências](matriz-pendencias.md); quando um registro foi fundido em outro, cito o
canônico. As decisões que só uma pessoa pode tomar estão em [decisões pendentes](decisoes-pendentes.md).

## Fontes

- **Sessões do agente de desenvolvimento**: 185 sessões, de 28/08 (dia do primeiro commit do repositório,
  `36e71168`) a 15/10, lidas em dez lotes. Cada sessão é citada pelo id de 8 caracteres e pela data de
  início. A retenção local cobre o projeto inteiro: não há período sem sessão.
- **Respostas às perguntas estruturadas**: 111 respostas literais do usuário, recuperadas à parte. Elas
  confirmam ou corrigem as decisões que os lotes marcaram como "inferidas" pelo relato do agente.
- **Repositório**: `README.md` (tabela de incrementos 001–073), `specs/*/spec.md`,
  `doc/auditoria-de-consolidacao-2026-09-26.md` (unidades RC-1 a RC-160),
  `doc/decisoes-pendentes-da-consolidacao.md` (DP-01 a DP-21), achados e auditorias em `doc/`, e o histórico
  do git (data do primeiro commit de cada pasta de spec).
- **GitHub**: 282 PRs (279 mesclados, 2 fechados, 1 aberto) e uma issue (#117).
- **Consolidações por área** que deram origem à matriz, conferidas contra a `main` em 15/10.

## Como ler

- "Usuário" quer dizer o responsável pelo produto, nas próprias palavras. "(colado)" marca texto que o usuário
  colou de um parecer externo e adotou ao mandar aplicar. "(pergunta)" marca resposta a pergunta estruturada.
  "Sugestão do agente, sem aprovação" quer dizer que nenhuma fala do usuário a confirma.
- Citações têm no máximo 25 palavras e mantêm a grafia original, erros de digitação inclusive.
- `ps/` = `backend/processo_seletivo/`; `t/` = `backend/tests/`.
- **Nenhuma linha está em IMPLEMENTADO E VALIDADO.** O sistema nunca operou com usuário real: em 14/10 o
  usuário disse que ele existe só na sua máquina. Implementação com teste verde, quando a spec pedia pessoa,
  fica em IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE.

## Limitações das fontes

- **Digestos truncados.** O digesto guarda só a última fala do assistente em cada turno e corta mensagens
  longas no meio. Pareceres colados, prompts de implementação e relatórios de análise chegaram incompletos;
  onde a decisão dependia do trecho perdido, ela foi reconstruída pela fala seguinte do agente e está marcada.
- **Respostas de formulário recuperadas à parte.** As respostas às perguntas estruturadas não aparecem nos
  digestos. As 111 recuperadas confirmam a maior parte; as que faltam (por exemplo, a T055 da `022` e o escopo
  do tutorial de setup) ficam como relato do agente.
- **Sessões sem conteúdo.** Das 187 transcrições de outras sessões, duas não tinham nenhuma fala aproveitável e ficaram fora dos digestos (185). Outras são só
  operacionais (subir ou derrubar o ambiente: `d37bc666`, `92333a1d`, `901b08a6`).
- **Replays.** Digestos longos repetem trechos inteiros depois de retomada de contexto: `8f779c78`
  (linhas ~991–1462), `8f427c86` (1320–2347), `3bd46d67` (dois blocos, verificados por `diff`) e `46626552`
  (534–965). Em dois pontos da `3bd46d67` a "fala final" é um resto antigo, e a resposta real se perdeu.
- **Conselheiro externo.** Desde a primeira semana, e quase sempre a partir de 26/09, muitas falas do usuário
  são pareceres de outro assistente ou revisor colados com "avalie e avance" ou "Pode responder:". Várias trazem
  "Decidi…" escrito pelo agente e colado pelo usuário (DP-14, DP-16, DP-21, relação do sorteio, RC-137).
  Foram tratadas como decisão do usuário, porque ele as enviou, mas a autoria do texto não é dele.
- **Datas.** O início das sessões está em UTC; sessões que começam à noite aparecem no dia seguinte. Sessões
  longas (`533156c5`, `3bd46d67`, `183ba11d`, `2bc3c441`, `7bf91059`) atravessam vários dias, e as datas
  intermediárias são inferidas de âncoras no texto.

---

## 1. As fases do desenvolvimento

O período de cada fase vem do primeiro e do último commit das pastas de spec na `main`, conferido no git.

### Fase 1 — Fundação (001–005)

| | |
|---|---|
| Período | 28/08 a 30/08 |
| Demanda | `0b03a4b5` (28/08): clonar o repositório, subir o ambiente, avançar a `001` e depois o frontend. `75d0dcc9` (29/08): parecer de segurança colado — "avalie e avance - proponha spec se julgar necessário." |
| Decisões de direção | 002 só administrativa; login LDAP, mas adiado; Django + HTMX no mesmo projeto; eMAG e WCAG ("os dois."); merges por merge commit; a `004` sem compatibilidade histórica porque "O sistema não está em produção" |
| Specs | `001` backend do ciclo normativo · `002` interface administrativa · `003` integridade · `004` endereçamento estável · `005` integridade do snapshot |
| PRs | #1 a #7 (#1 e #2 absorvidos no #3) |
| Estado | implementadas; a `002` tem 7 tarefas abertas (T053–T059), entre elas o LDAP (T056), que bloqueia produção (GO-01) |

### Fase 2 — Elaboração e publicação do Edital (006–008)

| | |
|---|---|
| Período | 30/08 a 31/08 |
| Demanda | `8f779c78` (30/08): diagnóstico "produto × trabalho do usuário" (colado). `71daf8d4` (30/08): o PDF ainda parecia relatório |
| Decisões de direção | Constituição 1.1.0 e 1.1.1 com o princípio VI (jornada demonstrável); uma spec 006 em fatias; nada de "copiar edital existente" agora; a `007` é a última de autoria antes do candidato; a `008` "exclusivamente documental" |
| Specs | `006` elaboração completa · `007` Edital institucional · `008` composição institucional do PDF |
| PRs | #8 a #16 |
| Estado | implementadas e depois emendadas (054, 060, 064, 068); a elaboração nunca foi feita por quem elabora (GO-31) |

### Fase 3 — Candidato (009–010)

| | |
|---|---|
| Período | 30/08 a 01/09 |
| Demanda | `29bde0c2` (30/08): "Fazer a inscrição ser tão simples que o sistema não se torne motivo de abandono." |
| Decisões de direção | comprovante em PDF gerado no servidor; acesso por código no e-mail, sem senha; CPF informado uma vez; retenção como precondição de dado real (01/09); Mailpit nos testes; roadmap 008–014 (depois refeito); "uma spec em cada sessão" |
| Specs | `009` inscrição e documentos · `010` área do candidato e acesso sem senha |
| PRs | #17, #18, #20 |
| Estado | implementadas; a jornada nunca foi percorrida por pessoa de fora (CA-15); retenção sem política (GO-19) |

### Fase 4 — Avaliação e resultado (011–018)

| | |
|---|---|
| Período | 31/08 a 12/09 (011–013, 015, 017 e 018 até 07/09; a 014 em 11/09 e a 016 em 12/09) |
| Demanda | `e790da97` (31/08): proposta da "Mesa", freada porque "o roadmap mudou". `dddb9cca` (01/09): comissão. `eeca206a` (03/09): leitura dos Editais 35, 14 e 57 e o "norte do arco". `533156c5` (03/09): auditoria E2E exploratória |
| Decisões de direção | comissão "deliberadamente estreita"; distribuição é ato com autoria; barema fora; ato histórico não se reescreve, é superado; nome + protocolo sem CPF na divulgação; as sete recomendações do recurso; o alvo são os editais menores; sorteio depois |
| Specs | `011` comissão · `012` mesa · `012-013` formas de conclusão · `013` resultado da Etapa · `014` corte · `015` classificação · `016` ocupação · `017` publicação de resultados · `018` recursos |
| PRs | #19, #21, #22, #24–#52, #105, #108 |
| Estado | implementadas; nunca exercidas com a comissão (GO-31); julgador elegível em equipe pequena (AV-03) e reabilitado antes do marco (AV-04) abertos |

### Fase 5 — Convocação, matrícula e o que os Editais reais pediam (019–031)

| | |
|---|---|
| Período | 07/09 a 18/09 |
| Demanda | `8af9d708` (07/09): sistema contra sete Editais anexos (anexos e sorteio). `0c26b370` e `211d74e8` (09/09): supervisão e reaproveitamento. `1ef93809` e `cf89cfc1` (10/09): portal e quadro de vagas. `485d14d4` (12/09): convocação. `ae3ad7c8` (13/09): auditoria de UX. `8f427c86` (16/09): Requerimento e exportação. `3bd46d67` (16/09): reauditoria |
| Decisões de direção | sorteio no rito atual, com transmissão, "usando o proprio sistema"; anexo é arquivo PDF, nunca formulário; quadro de vagas estruturado; contrato de mutabilidade; equipe de 2–3 pessoas (08/09); manual em piloto antes do acervo (08/09); nome social em spec própria (16/09) |
| Specs | `019` convocação · `020` anexos · `021` sorteio · `022` supervisão · `023` reaproveitar · `024` portal · `025` quadro · `026` mutabilidade · `027` estrutural de vagas · `028` cronograma vencido · `029` Requerimento · `030` composição que se explica · `031` exportação ao Registro Acadêmico |
| PRs | de #53 a #130, com os da fase 4 (#105, #108) e os da fase 6 (#126, #128, #129) no meio |
| Estado | implementadas; as três integrações (Caixa, Registro Acadêmico, CEP) sem validação operacional (AS-24, AV-09, GO-29); manual não produzido (GO-43) |

### Fase 6 — Consolidação e condução (032–054)

| | |
|---|---|
| Período | 18/09 a 29/09 |
| Demanda | `3bd46d67` (~18–20/09): reavaliação e specs a partir dos achados. `0b4d88f5` (21/09): visão gerencial. `183ba11d` (21–25/09): estudo de esforço com cinco Editais reais. `2bc3c441` (26–29/09): auditoria de consolidação de 26/09 e a "ordem de 27/09" |
| Decisões de direção | D-G1 a D-G5 (19/09); "genérico o suficiente" para alunos e bolsistas (19/09); sem carga retroativa (21–25/09); recorte documental D1–D5 (25/09); DP-05 = B (26/09); PDF do sistema como documento oficial, E10 = B, emenda 1.2.0 (28/09); 049–051 antecipadas ao piloto (28/09) |
| Specs | `032`–`038` (executabilidade, navegação, ordem por recorte, sorteio executável, instrução do recurso, becos, painel) · `039` só registro · `040`–`042` visão institucional · `043` duplicar Perfil · `044` recorte documental · `045`–`048` · `049`–`053` · `054` Edital como ato oficial |
| PRs | #126, #128, #129, de #131 a #235 e de #237 a #239 |
| Estado | implementadas, exceto a `039`; o teste operacional assistido (DP-18) nunca aconteceu (GO-31); a `039` nunca foi encerrada (ED-46) |

### Fase 7 — Polish (055–058)

| | |
|---|---|
| Período | 30/09 a 01/10 |
| Demanda | `67654248` (30/09): auditoria de polish de UI. `6a1abfb7` (30/09): tutorial de implantação em Ubuntu (#236) |
| Decisões de direção | execução por prompts autônomos, lote a lote; teto de 120.000 caracteres na folha; metas parciais aceitas e registradas |
| Specs | `055` folha · `056` assistente de composição · `057` telas de operação · `058` resíduos |
| PRs | #236, #240 a #249 |
| Estado | implementadas; as telas da condução ficaram fora da série (AV-31) |

### Fase 8 — Acesso, unidades e o ato oficial (059–068)

| | |
|---|---|
| Período | 06/10 a 09/10 |
| Demanda | `6ef6d5ee` (06/10): ambiente para o coordenador, que revelou o H.18. `a1ccd396` (06/10): assinatura do Edital e os 25 campi. `de1d85f6` (06/10): corte obsoleto. `288c08d9` (07/10): resultados divulgados confusos. `cab5c781` e `fba18c90` (08/10): auditoria do PDF. `713f5a59` (09/10): notificações, a pedido do setor |
| Decisões de direção | multiunidade já, antes de haver dado; assinatura fora do sistema; Gestor cadastra autoridades; situação do candidato nunca inferida da posição; correções do PDF em lotes pequenos; quarta situação da FR-084 |
| Specs | `059` acesso à convocação · `060` unidades e autoridades · `061` corte após recurso · `062`–`063` resultados e acompanhamento · `064`–`068` PDF · `066` avisos complementares |
| PRs | #250 a #272 |
| Estado | implementadas; autoridades do Cefor não cadastradas e assinatura sem resposta (ED-04); avisos desligados em produção até a LGPD (CA-05) |

### Fase 9 — Linguagem simples, assistente, jornada pública e implantação (069–074)

| | |
|---|---|
| Período | 11/10 a 14/10 |
| Demanda | `9526cf31` (11/10): Editais em Libras. `46626552` (12/10): Edital em linguagem simples. `84c96e5f` (12/10): auditoria do assistente de dúvidas. `34ab2a4e` (12/10): UX e conversão da jornada pública. `7bf91059` (12–14/10): piloto do assistente. `f55c52a5` (14/10): configurações. `e76c2efd` (14/10): assistente na página, só local |
| Decisões de direção | Libras só como estudo; o próprio ato oficial em linguagem simples; assistente público, sem login, em fases A → B → C; Q1–Q9 da jornada; Ollama da L4 como destino; interface de configuração só depois da autenticação; premissa "o sistema existe apenas no meu computador" (14/10) |
| Specs | `069` linguagem simples · `070` Fase A · `071` Fase B · `072` jornada pública · `073` configurar e verificar (implementação no #283) · `074` só numa worktree |
| PRs | #273 a #282; #283 aberto |
| Estado | nenhuma validação humana feita; a `074` não tem commit (GO-46); os dois vídeos não têm cópia (GO-47) |

---

## 2. Matriz demanda → estado

Uma linha por demanda ou decisão de peso, em ordem aproximada de data. A última coluna remete à matriz; "resolvido"
quer dizer que nada daquela linha continua aberto.

| # | Demanda (origem e data) | Decisão | Spec | Implementação | Testes | Estado atual | Item |
|---|---|---|---|---|---|---|---|
| 1 | Público da interface — `0b03a4b5`, 28/08 | usuário (pergunta): "Só administrativo (Recomendado)" | `002` spec:15, :348 | `ps/interface/` | `t/interface/test_fluxo.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-31 (o candidato veio pela 009/010) |
| 2 | Login institucional — `0b03a4b5`, 28/08 | usuário (pergunta): "LDAP"; na mesma sessão: "toda parte te autenticacao e autorizacao pode ser feito depois?"; `e790da97` (31/08): "gate de produção da jornada da comissão" | `002` spec:18, :369, T056 | inexistente; só o seletor `ps/interface/identidade.py`, recusado em `config/settings/production.py:90-94` | `t/test_configuracao_producao.py` (só a recusa) | ESPECIFICADO E NÃO IMPLEMENTADO | GO-01 |
| 3 | Abordagem da interface — `0b03a4b5`, 28/08 | usuário (pergunta): "Django + HTMX, no mesmo projeto (Recomendado)"; padrão visual: o design system do SUAP | `002` plan.md:76, :113 | `ps/interface/templates/`; CSS próprio (o SUAP nunca foi obtido, T057) | `t/interface/`, `t/javascript/` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-04 (CSP, T058) |
| 4 | Acessibilidade — `0b03a4b5`, 28/08 | usuário: "os dois." (eMAG 3.1 e WCAG 2.1 AA) | `002` FR-024/025; T053, T054 | marcação e folha | `t/interface/test_acessibilidade.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | CA-14; ED-11 (o PDF) |
| 5 | Retificação aplicada no Perfil errado — `75d0dcc9`, 29/08 | usuário: Q1 por `id=<uuid>`; "O sistema não está em produção e não há dados persistidos a preservar." | `003`, `004`, `005` | #5, #6, #7 | `t/contract/`, `t/integration/test_database_permissions.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | resolvido |
| 6 | "Produto × trabalho do usuário" (colado) — `8f779c78`, 30/08 | usuário: "commite a spec e emende a constituição"; "aprovada a 1.1.1" | Constituição 1.1.0/1.1.1 (princípio VI); `006` | #8, #9, #10 | `t/interface/test_fluxo.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-31 |
| 7 | Fechar a autoria antes do candidato — `8f779c78`, 30/08 | usuário: "A 007 deve ser a última feature dedicada à autoria antes de avançarmos para a jornada do candidato." | `006`, `007` | #11 a #15 | `t/interface/test_fluxo.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-31 |
| 8 | Etapas por Edital ou por Perfil — `8f779c78`, 30/08 | usuário (pergunta): "Por Edital agora (Recomendado)"; `3bd46d67` (20/09): "Mantém junto, como está (Recomendado)" | `006`; `039` (registro) | `ps/editais/models/etapas.py:11-24` | nenhum do alcance | IDENTIFICADO E NÃO ESPECIFICADO | ED-09 |
| 9 | PDF que parecesse Edital — `71daf8d4`, 30/08 | usuário: "uma última spec curta sobre autoria, exclusivamente documental, e depois congelaria essa frente" | `008` → `054`, `064`–`069` | #16; `ps/publicacoes/infrastructure/pdf.py` | `t/contract/` (fixture byte a byte) | PARCIALMENTE IMPLEMENTADO | ED-26, ED-11 |
| 10 | Inscrição sem abandono — `29bde0c2`, 30/08 | usuário: "Fazer a inscrição ser tão simples que o sistema não se torne motivo de abandono." | `009` | #17 | `t/acceptance/test_jornada_do_candidato.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | CA-15 |
| 11 | Comprovante confiável — `29bde0c2`, 30/08 | usuário: "Reabra a decisão. Parece fazer sentido emitir o comprovante em pdf gerado no servidor." | `009` FR-063 | `ps/portal/templates/portal/comprovante.html` | `t/contract/test_comprovante_e_divulgacao_byte_a_byte.py` | IDENTIFICADO E NÃO ESPECIFICADO ("?" fora do cp1252) | CA-25 |
| 12 | Acesso sem senha — `29bde0c2`, 30/08; `c7194461`, 01/09 | usuário: "Login por código no e-mail — Acho uma escolha muito boa para UX."; "e-mail → código de uso único → sessão autenticada" | `010` FR-082, FR-083 | `ps/identidade/application/desafio.py`, `mensagem.py` | `t/integration/identidade/test_desafio.py` | BLOQUEADO (correio de produção; falha silenciosa) | GO-25 |
| 13 | E-mail como canal único do candidato — `c7194461`, 01/09 | usuário: "corrija os dois graves e os quatro altos" (o recibo de inscrição entra); revisões em 12/09 (`019`) e 09/10 (`066`) — ver §4 | `010` FR-084 (spec:548) | `ps/inscricoes/application/mensagem.py`, `ps/avisos/` | `t/test_situacoes_de_mensagem.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | CA-21, CA-05, GO-25 |
| 14 | Retenção como precondição de dado real — `c7194461`, 01/09 | usuário: "A área candidata não entra em produção com dados reais enquanto a política institucional de retenção/descarte aplicável não estiver definida." | `010` spec:69 (PC-004); `009` FR-076; `012` FR-057 | inexistente; só `excluir_registros_do_piloto` (071) | — | BLOQUEADO | GO-19 |
| 15 | Identidade do candidato — `c7194461`, 01/09 | usuário: "eu não perpetuaria a dependência `subject = HMAC(SECRET_KEY, CPF)` para novas identidades." | `010` FR-007 | `ps/identidade/` | `t/authorization/test_eixos_de_identidade.py` | ADIADO FORMALMENTE (verificação externa, gov.br) | CA-18 |
| 16 | Comissão de até 50 avaliadores — `dddb9cca`, 01/09 | usuário: "A 011 deve ser deliberadamente estreita"; "tem que ser fácil, simples, óbvio" | `011` | #19; `ps/comissoes/` | `t/acceptance/test_comissao_e_alocacao.py` | IDENTIFICADO E NÃO ESPECIFICADO (sem Perfil nem polo) | AV-12, GO-08 |
| 17 | Mesa de avaliação — `ea8c1d68`, 01/09 | usuário: "A distribuição das inscrições é ato administrativo com autoria, e não efeito colateral de um algoritmo." | `012` | #21; `ps/avaliacoes/` | `t/acceptance/test_mesa_de_avaliacao.py` | PARCIALMENTE IMPLEMENTADO (identificar a inscrição) | AV-40, GO-31 |
| 18 | Barema estruturado — `eeca206a`, 03–04/09 | usuário: "Eu não reabriria a 012 para colocar barema estruturado."; (pergunta) "Apuração externa por ora (Recomendado)" | fora em `012`–`015`, `020`, `030`; DP-10 | inexistente | — | ADIADO FORMALMENTE | AV-10 |
| 19 | Atos que mudam depois — `eeca206a`, 03/09 | usuário: "Atos administrativos históricos não são reescritos; podem ser superados por atos posteriores explicitamente relacionados." | decisão C (#45); `018` | manager `vigentes` em `ps/resultados/` | `t/test_vigencia_do_resultado.py` | IDENTIFICADO E NÃO ESPECIFICADO (corrigir sem recurso) | AV-15 |
| 20 | Retificar documento exigido (E2E-004) — `533156c5`, 03/09 | usuário: "Registrar E2E-004 e E2E-021 como pendências explícitas, sem puxá-las para a 013."; `eeca206a`: "implementa só a edição dos existentes" | #28, #32 | edição dos existentes na tela de Retificação | testes do #32 | PARCIALMENTE IMPLEMENTADO | ED-08 |
| 21 | Sorteio — `eeca206a`, 03/09; `8af9d708`, 07/09; `c1e1e429`, 10/09 | usuário: "O SORTEIO, PENSO QUE SERIA IMPLEMENTADO POSTERIORMENTE"; "transmissão ao vivo no youtube, porém, já usando o proprio sistema"; "preservar… a maneira como a equipe já trabalha hoje" | `021`, `035` | #79, #82, #83, #97, #139; `ps/sorteios/` | `t/integration/sorteios/test_falha_de_acesso_a_fonte.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | AV-07, AS-24, AV-39 |
| 22 | Classificação — `cc7bd83d`, 04/09 | usuário: "Q2: A. Emitir com posições compartilhadas e empate residual explícito."; "Até 3 segundos." | `015` | #36 | `t/acceptance/test_ordenacao.py`, `t/performance/test_ordenacao.py` | IDENTIFICADO E NÃO ESPECIFICADO (expressividade do desempate) | AV-37 |
| 23 | Publicar resultados — `57355798`, 06/09 | usuário: "eu adotaria nome + protocolo, sem CPF" | `017` D-001 | #41, #42; `ps/divulgacao/` | `t/contract/test_conteudo_divulgado.py` | IDENTIFICADO E NÃO ESPECIFICADO (modalidade de cota ao lado do nome) | CA-06 |
| 24 | Recursos — `b863c7e1` e `711f5b8c`, 06/09 | usuário: "Aceito as sete recomendadas; commite e abra o PR"; (pergunta) "Só DIAS_CORRIDOS (Recomendada)"; anexos "Não, na V1 (Recomendada)" | `018`, `036` | #46 a #50, #142 | `t/acceptance/test_us_recursos.py` | IDENTIFICADO E NÃO ESPECIFICADO (julgador elegível; DP-09) | AV-03, AV-16 |
| 25 | Anexos do Edital — `8af9d708`, 07/09 | usuário: "Anexo como arquivo ... O sistema nunca lê os campos ... NAO É CONSTRUTOR DE RELATÓRIOS." | `020` | #54, #58 | `t/acceptance/test_us_anexos.py` | IDENTIFICADO E NÃO ESPECIFICADO (anexo não diz a que serve) | ED-38, CA-30 |
| 26 | Equipe pequena — `268367ba`, 08/09 | usuário: "são duas ou no máximo três pessoas... só preocupado com esses vários papeis" | manual §A.3 (`doc/manual/00-arquitetura-do-manual.md:171`); `doc/descoberta-conducao-por-presidencia-unica.md` (#74) | segregação em `ps/publicacoes/application/publish_edital.py:705-710` | `t/interface/test_bastao.py` | IDENTIFICADO E NÃO ESPECIFICADO (três perguntas de governança) | AV-03 |
| 27 | Manual de operação — `268367ba`, 08/09 | usuário: "S-01 não começa enquanto S-00 não aprovar o padrão e revisar o inventário"; arquitetura aprovada com ajustes | `doc/manual/00-arquitetura-do-manual.md` (#75; R5 em #250) | só o piloto `doc/manual/piloto/` (#109) | — | ESPECIFICADO E NÃO IMPLEMENTADO | GO-43 |
| 28 | Supervisão — `0c26b370`, 09/09 | usuário: "acho importante ter a informação das inscrições realizadas até o momento.." | `022` → `038`, `045` | #81, #84, #149, #187 | `t/acceptance/test_supervisao_do_processo.py` | PARCIALMENTE IMPLEMENTADO | GO-13 |
| 29 | Reaproveitar Edital — `211d74e8`, 09/09 | usuário: "Eu evitaria chamar a feature de 'importar edital'"; questionou o estado `REAPROVEITADA` | `023`, `028` | #86, #90, #118 | `t/integration/editais/test_reaproveitamento.py` | PARCIALMENTE IMPLEMENTADO | ED-34 |
| 30 | Quadro de vagas — `cf89cfc1`, 10/09; `c9ff00d8` | usuário: "Decisão 1: forma estruturada."; "A quantidade publicada no quadro é a fonte autoritativa."; (pergunta) "A — só vagas imediatas" | `025`, `027` | #94, #96, #99, #101, #102, #116 | `t/integration/publicacoes/test_quadro_na_publicacao.py` | ADIADO FORMALMENTE (fora da página pública, Q8) | CA-10 |
| 31 | Corte e progressão — `67bf3671`, 11/09 | usuário: "A próxima spec deveria ser a 014 — Corte e progressão entre Etapas."; (pergunta) I1, I2, A1, U1 | `014`, `061` | #105, #257 | `t/integration/classificacao/test_corte_apos_recurso.py` | IDENTIFICADO E NÃO ESPECIFICADO (reabilitado antes do marco) | AV-04 |
| 32 | Ocupação de vagas — `73960a45`, 12/09 | usuário (pergunta): "É da 014 (alvo derivado)"; "Duas espécies declaradas"; "Ato append-only por recorte" | `016` | #108 | `t/integration/ocupacao/` | IDENTIFICADO E NÃO ESPECIFICADO (reversão retificada) | ED-41 |
| 33 | Convocação — `485d14d4`, 12/09 | usuário: "Para dias úteis, a comissão informa o vencimento explícito. Nada de criar calendário de feriados." | `019`, `050`, `059` | #110, #111, #222, #251 | `t/integration/convocacao/test_reenvio_nao_reinicia_prazo.py` | PARCIALMENTE IMPLEMENTADO (artefatos da 019 atrás do código) | AV-48, AV-23, CA-23 |
| 34 | Campo novo no conteúdo publicado — `ae3ad7c8`, 13/09 | usuário: "Nenhum novo campo normativo pode entrar no conteúdo publicado sem uma decisão explícita sobre sua retificabilidade." | `026`; `doc/decisao-mutabilidade-normativa.md` | #112, #114; `ps/editais/domain/mutabilidade.py` | `t/contract/test_mutabilidade.py` | IDENTIFICADO E NÃO ESPECIFICADO (objeto inteiro) | ED-12, ED-47 |
| 35 | Modelo Oferta (atribuições repetidas por polo) — `ae3ad7c8`, 16/09 | usuário: "Não permitir sobrescrita de atribuições no Perfil ou na Oferta." — sem registro em `doc/` | `064`, `068` só no PDF | `ps/publicacoes/infrastructure/pdf.py` | `t/unit/publicacoes/test_atribuicoes_consolidadas.py` | PARCIALMENTE IMPLEMENTADO | ED-31 |
| 36 | Requerimento de Matrícula — `de544cbf`, 12/09; `8f427c86`, 16/09 | usuário: "'Hoje o edital exige' não é a mesma coisa que 'isso pertence conceitualmente à seleção'."; renda "b. Renda Familiar."; FR-372: sugestão do agente, sem aprovação | `029`; `doc/descoberta-029-requerimento-de-matricula.md` | #123; `ps/requerimentos/` | `t/test_dado_sensivel_do_requerimento.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | CA-07 |
| 37 | Nome social — `8f427c86`, 16/09 | usuário: "Gostaria de retificar a pergunta anterior - resposta B. Não nesta feature, e vira spec própria." | `029` spec:114-120 (lacuna nomeada); a spec própria nunca foi aberta | inexistente | — | ADIADO FORMALMENTE | CA-19 |
| 38 | Exportação ao Registro Acadêmico — `8f427c86`, 16–17/09 | usuário: "tem dados que são externos, portanto, podem ficar vazios na planilha"; "consegue torná-lo pronto para implementação?" | `031` | #125, #127, #130; `ps/matriculas/` | `t/integration/matriculas/test_geracao.py` | BLOQUEADO (importação real, SC-143) | AV-09 |
| 39 | Base de CEP — `8f427c86`, 16/09 | usuário: "carga inicial no provisionamento e atualização por job agendado."; "deve existir o job mensal e o alerta de falha/desatualização." | `029`; `doc/runbook-base-de-cep.md` | `carregar_ceps` | `t/integration/requerimentos/test_carregar_ceps.py` | ESPECIFICADO E NÃO IMPLEMENTADO (job e alerta) | GO-29 |
| 40 | D-G1 — `3bd46d67`, ~19/09 (#143) | usuário: "O que deve ser obrigatório não é existir corte, mas existir uma declaração explícita" | `032` → `046` D-002 | #188 | `t/unit/editais/` (executabilidade) | DESCARTADO OU SUBSTITUÍDO (pela 046, 26/09) | resolvido |
| 41 | D-G2 — `3bd46d67`, ~19/09 | usuário: "Não ratifico nem corrijo as sete recusas em bloco." | `033`; DP-07 | inexistente | — | ADIADO FORMALMENTE | ED-40 |
| 42 | D-G3 — `3bd46d67`, ~19/09 | usuário: "O Cefor deve passar a declarar a fonte pública externa do sorteio." | `035`, `046` | #139, #188 | `t/integration/sorteios/test_fonte_fora_de_producao.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | AS-24 |
| 43 | D-G4 — `3bd46d67`, ~19/09 | usuário: "O peso continua sendo da Etapa… Registre essa decisão como encerrada" | — (o modelo já era esse) | — | — | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | resolvido |
| 44 | D-G5 — `3bd46d67`, ~19/09 | usuário: "A Retificação deve poder acrescentar Modalidade."; `b53bd3c2` (26/09, colado): "permitir acrescentar qualquer Modalidade, inclusive cota" | `039` (registro) → `048` | #197 | `t/integration/publicacoes/test_documento_da_retificacao_que_acrescenta.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | ED-30 (resíduos) |
| 45 | Alunos e bolsistas — `3bd46d67`, ~19/09 | usuário: "o sistema deve ser genérico o suficiente para permitir editais tanto de alunos quando de bolsistas" — sem registro em `doc/` | orienta `054` e `069`; estudo Q4 da `072` | catálogo em `ps/editais/domain/secoes.py` | `t/unit/editais/test_catalogo_da_054.py` | ADIADO FORMALMENTE (estudo Q4) | ED-28 |
| 46 | Visão gerencial e Diretoria — `0b4d88f5`, 21/09 | usuário: "capacidade própria, inicialmente no gestor, sem inventar o papel diretoria." | `040`–`042` | #157 | `t/authorization/test_visao_institucional.py` | IDENTIFICADO E NÃO ESPECIFICADO (a spec ainda dá G-010 como aberta) | GO-14, GO-41 |
| 47 | Editais antigos — `183ba11d`, 21/09 | usuário: "acho que não faz sentido cadastrar editais antigos - com data retroativa" (decisão nova, registrada em 25/09) | `doc/decisao-sem-carga-retroativa.md` (#158) | IMPEDE de inscrições encerradas mantido (`028`) | — | DESCARTADO OU SUBSTITUÍDO (a carga retroativa) | resolvido; estudos com datas futuras (GO-31) |
| 48 | Recorte documental e Duplicar Perfil — `183ba11d`, 25/09 | usuário: "sim, abre a spec do Duplicar Perfil"; "aceito as recomendações, prepara a sessão da spec" | `043`, `044`; `doc/decisao-recorte-documental.md` | #168, #170, #173 | `t/interface/test_duplicar_perfil.py`, `t/integration/inscricoes/test_recorte_transversal.py` | PARCIALMENTE IMPLEMENTADO (140/2025 nunca recomposto) | GO-31, ED-47 |
| 49 | Cadastro de reserva no piloto — `3f708cd8`, 26/09 | usuário (colado): "Eu seguiria pela opção B no piloto atual." | DP-05 (`doc/decisoes-pendentes-da-consolidacao.md:308`) | aviso `reserve_only_convocation_external` (`ps/editais/domain/validation.py:3338`) | `t/unit/publicacoes/test_perfil_sem_vaga_imediata.py` | ADIADO FORMALMENTE | ED-29, AV-22 |
| 50 | A ordem de 27/09 e o piloto — `2bc3c441`, 27–28/09 | usuário: "Sim — agora eu acho que fechou muito bem" (colado); "Queria começar o piloto já com todas otimizações possíveis no operacional." | `049`, `050`, `051` | #222, #223, #226, #231 | `t/interface/test_aplicar_a_todos.py`, `t/interface/test_conducao_do_marco.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-31 |
| 51 | Teste operacional assistido — `2bc3c441`, `0c08f827`, 27/09 | nenhuma decisão sobre quem e quando (DP-18) | `doc/roteiro-teste-operacional-assistido-28-2026.md` (#208) | — | — | ESPECIFICADO E NÃO IMPLEMENTADO | GO-31 |
| 52 | PDF do sistema como documento oficial — `2bc3c441`, 28/09 | usuário: "sim, o PDF vai ser o documento oficial" | DP-20; `054`, `064`–`069` | `ps/publicacoes/infrastructure/pdf.py` | `t/unit/publicacoes/test_fecho_e_normas_da_054.py` | BLOQUEADO (assinatura e nome, com o Cefor) | ED-04 |
| 53 | E10 = B (transcrição) — `183ba11d`, 21/09; `2bc3c441`, 28/09 | usuário: "aceito as recomendações da tabela, exceto 1 e 5." (E10 = B em `doc/decisoes-pendentes-da-consolidacao.md:1390`) | DP-20; #220 | avisos na Revisão, `ps/interface/revisao.py` | `t/unit/publicacoes/test_fecho_e_normas_da_054.py` | PARCIALMENTE IMPLEMENTADO (sem roteiro do homologador) | ED-02 |
| 54 | Pedido de produção à TI — `2bc3c441`, 28/09 | usuário: "sinceramente, não vejo relevancia nisso neste momento. são aspectos para implantação em produção." | `doc/decisoes-pendentes-da-consolidacao.md:603`; guia `doc/implantacao-em-producao-ubuntu.md` (#236) | — | — | ADIADO FORMALMENTE | GO-22 |
| 55 | Candidato não chega à convocação (H.18) — `6ef6d5ee`, 06/10 | usuário (colado): "Eu abriria uma feature pequena… 059" | `059` | #251 | `t/interface/test_portal_caminho_da_convocacao.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | resolvido |
| 56 | Assinatura e 25 campi — `a1ccd396`, 06/10 | usuário: "TENHO RECEIO DE DEIXAR ISSO PARA DEPOIS… HOJE O SISTEMA NÃO INICIOU A OPERAR"; "assinatura dentro do sistema não faz sentido.." | `060` | #254; `ps/unidades/models.py:59-83` | `t/unidades/test_criacao_exige_unidade.py`, `t/authorization/test_gerir_autoridades.py` | BLOQUEADO (uma unidade só; marca fixa) | ED-43, ED-04 |
| 57 | Situação do candidato — `288c08d9`, 07/10 | usuário (colado): "Situação pessoal nunca é inferida da posição isoladamente." | `062`, `063` | #260, #263 | `t/portal/test_acompanhamento_pela_situacao.py` | IDENTIFICADO E NÃO ESPECIFICADO (custo por publicação; resíduos) | CA-33, CA-34 |
| 58 | PDF confiável — `cab5c781` e `fba18c90`, 08/10 | usuário: "ACHO QUE PODEMOS FOCAR NOS PERFIS PRIMEIRO."; (colado) "começar pela confiabilidade do conteúdo publicado, em lotes pequenos" | `064`, `065`, `067`, `068` | #264, #266, #268, #270 | `t/unit/editais/test_conflito_de_numeracao.py`, `t/unit/publicacoes/test_atribuicoes_consolidadas.py` | PARCIALMENTE IMPLEMENTADO | ED-25, ED-26 |
| 59 | Avisar os candidatos de cada resultado e chamada — pedido do setor, `713f5a59`, 09/10 | usuário (colado): "Revisão da FR-084 — Aprovar, incluindo uma quarta situação de envio"; "eu não permitiria excluir individualmente destinatários no MVP." | `066` | #267, #269; `despachar_avisos` | `t/integration/avisos/test_autorizacao.py`, `t/test_avisos_sem_correio_real.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE (desligado em produção até a LGPD) | CA-22, CA-05 |
| 60 | Convocar para heteroidentificação e entrevista — `713f5a59`, 09/10 | usuário (colado): o MVP dos avisos "não encerra o atendimento à demanda" | `doc/registro-convocacao-para-etapas-2026-10-09.md` | inexistente | — | IDENTIFICADO E NÃO ESPECIFICADO | ED-10 |
| 61 | Editais em Libras — `9526cf31`, 11/10 | usuário: "Não utilizar avatar para tradução. Não declarar traduções para Libras como concluídas." | estudo `docs/libras/` (#273) | inexistente, por decisão | ferramentas do estudo | IDENTIFICADO E NÃO ESPECIFICADO | ED-44 |
| 62 | Edital em linguagem simples — `46626552`, 12/10 | usuário (colado): "Concordo com a direção principal: melhorar o próprio edital oficial, aproveitando o gerador atual." | `069` | #275 | `t/unit/publicacoes/test_apresentacao_por_perguntas.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE (SC-517) | ED-03, ED-27 |
| 63 | Assistente de dúvidas, Fase A — `84c96e5f`, 12/10 | usuário: "O assistente será inicialmente público, sem login e sem acesso a inscrições individuais." | `070` | #274; `ps/duvidas/` | `t/unit/duvidas/test_fontes.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE (T046) | AS-01, AS-02 |
| 64 | Assistente, Fase B — `7bf91059`, 12–14/10 | usuário: "DP-1: C — sessões acompanhadas na máquina da equipe."; "O sistema usará a L4 local."; "simplifique o FR-1507, deixe só o limite da chave" | `071` | #278, #279, #280 | `t/integration/duvidas/test_avaliar_assistente.py`, `t/interface/test_prototipo_do_assistente.py` | BLOQUEADO (sem acesso à L4) | AS-07, AS-08, AS-09 |
| 65 | Assistente na página de cada seleção — `e76c2efd`, 14/10 | usuário: "Ajuste a premissa: o sistema existe apenas no meu computador."; "Não condicione essa entrega à autenticação institucional, à 073, à avaliação na L4" | `074`, só na worktree `assistente-pagina-edital-local-d6f44f` | `portal/assistente.py` (sem commit) | testes na worktree (13/14 tarefas) | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-46 |
| 66 | Jornada pública — `34ab2a4e`, 12/10 | usuário (colado): Q1–Q9, como "Q1 — Instrumentação — Não incluir; validar por percursos conduzidos." | `072` spec:65-73 | #276, #277 | `t/acceptance/portal/test_jornada_publica.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE (SC-605, FR-1627) | CA-01, CA-02, CA-13 |
| 67 | Ifes Ads (campanhas geradas por programa) — `34ab2a4e`, 12/10 | sugestão do agente, sem aprovação ("Nada disso deve ser implementado agora", `doc/auditoria-ux-conversao-2026-10-12/jornada-publica.md:78-83`); o usuário o tirou do escopo do assistente (`84c96e5f`) | — | inexistente | — | IDENTIFICADO E NÃO ESPECIFICADO (ideia, §5) | — |
| 68 | Configurações da implantação — `f55c52a5`, 14/10 | usuário: recusou "nenhuma interface" — "deixando a interface como evolução concreta após a autenticação administrativa."; "Aprovo o recorte da 073." | `073` | #281, #282; #283 aberto | `t/unit/test_configuracao_de_correio.py` | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE (PR aberto) | GO-26, GO-27, GO-28 |
| 69 | Reaproveitar documentos entre inscrições — `59745df3`, 07/10 | usuário: "to achando que não compensa, né?" — sem registro em `doc/` | — | inexistente | — | ADIADO FORMALMENTE | CA-35 |
| 70 | Filmes de lançamento e institucional — `c2cdae9c`, `3f0ce9aa`, 14/10 | usuário: "NAO USE REMOTION."; "o assistente de dúvidas com IA existe como piloto interno" | — | `filme-de-lancamento/` e `video/`, só nas worktrees | — | IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE | GO-47 |

**Leitura de conjunto.** Das 70 linhas, 22 estão em IMPLEMENTADO SEM VALIDAÇÃO SUFICIENTE, 10 em
PARCIALMENTE IMPLEMENTADO, 17 em IDENTIFICADO E NÃO ESPECIFICADO, 9 em ADIADO FORMALMENTE, 6 em BLOQUEADO,
4 em ESPECIFICADO E NÃO IMPLEMENTADO e 2 em DESCARTADO OU SUBSTITUÍDO. As implementadas sem validação esperam
quase todas a mesma coisa: uma pessoa do setor, da TI, do Cefor ou do encarregado de dados. Os seis itens que
a matriz trata como "P0 para a implantação" nascem de seis destas linhas — a 2 (LDAP), a 12 (correio), a 14
(retenção), a 52 (assinatura do ato), a 54 (pedido à TI) e a 62 (frases da `069`) —, e nenhuma delas é
trabalho de código que se possa começar sem uma resposta de fora.

---

## 3. Itens recuperados das sessões que não constavam do planejamento

Só entra aqui o que não está em spec, `doc/` ou plano, ou está apenas como menção solta, sem dono nem
tarefa. A busca no repositório foi literal (`git grep` em `doc/`, `specs/`, `README.md` e `AGENTS.md` da
`main`). "Não entra" quer dizer que o item ficou fora da matriz, e o motivo está ao lado.

### (a) Compromissos e pendências declarados ao fim de sessões

| Sessão | Citação | O que se perdeu | Onde está agora |
|---|---|---|---|
| `7bf91059` (14/10) | "Confirme só que você apagou a antiga no painel do OpenRouter." | A chave apareceu inteira numa captura colada na conversa. Nenhum documento registra o pedido nem a confirmação | GO-09 |
| `e76c2efd` (14/10) | "Faço o commit e abro o PR?" | A `074` inteira — spec, código, testes e a emenda do FR-1462 da `071` — vive só numa worktree, sem commit; a pergunta ficou sem resposta | GO-46 |
| `c2cdae9c` (14/10) | "Ninguém ouviu a trilha… Ouça antes de exibir" | Filme de lançamento sem commit nem cópia, com a trilha só medida | GO-47 |
| `3f0ce9aa` (14/10) | "A marca oficial entra na cena 23 quando você tiver o arquivo autorizado." | Vídeo institucional de 19 GB sem cópia; a pergunta "Commito a pasta video/?" ficou sem resposta | GO-47 |
| `0d6d25cc` (29/09) | usuário: "corrija as 8 unidades antes do piloto" | A ordem ficou sem resposta. As oito (RC-09, RC-10, RC-11, RC-47, RC-74, RC-122, RC-147, RC-152) estão na auditoria de 26/09 (`:430`) como "antes do piloto", mas nada registra que o usuário mandou corrigi-las | ED-07, ED-20, ED-21, CA-10, AS-24 |
| `84c96e5f` (12/10) | usuário: "Vou fazer a revisão antes do merge" | O #274 entrou em 13/10 com a T046 aberta. A spec guarda a tarefa, não o compromisso de fazê-la antes | AS-01 |
| `6ef6d5ee`, `b7a52f82` (06/10) | "O manual e a S-00R ficam para a próxima sessão, após a integração da 059." | Nenhuma sessão posterior voltou ao manual; a 059 entrou no mesmo dia | GO-43 |
| `2acf27b6` (10/09) | "Três consequências operacionais que valem checar com a comissão" | A mudança do rito do sorteio (relação congelada antes do dia, anular custa Retificação, método declarado pelo elaborador) nunca foi validada com a comissão | AV-07 |
| `7bf91059` (14/10) | "Mantenha a validação do teclado em aparelho real como pendência explícita" | Teclado virtual em celular real, o caso do candidato indígena (CB-18) e a continuação "Preciso enviar todos?" ficaram só no corpo do PR #280 | AS-10, AS-14 |
| `901b08a6` (12/10) | "Desfaço quando você terminar de olhar." | A entrada `selecao` no `launch.json` e o `.env` copiado continuam na worktree `sistema-selecao-f933f9` | GO-48 |

### (b) Follow-ups propostos pelo agente e nunca iniciados

| Sessão | Citação | O que se perdeu | Onde está agora |
|---|---|---|---|
| `df245428` (09/09) | "nenhum job periódico, nenhuma rotina, nada que o rode" | O E2E contra a Caixa virou achado (`doc/achado-fonte-real-do-sorteio-sem-gatilho.md`), nunca tarefa; não roda desde 10/09, e o piloto é por sorteio | AS-24 |
| `3bd46d67` (~18/09) | "O Requerimento da 029 continua sem auditoria de UX" | A auditoria de UX do Requerimento (029) e da exportação (031) nunca foi pedida | CA-07, AV-31, CA-15 |
| `3bd46d67` (~19/09) | "não merecem uma spec cada: merecem uma varredura só, com uma lista e um PR" | A varredura única de microcópia (ACH-28/29, 17, 03/15, 21/23 e outros) não foi aberta; a série de polish (055–058) cobriu outra lista | não entra como item próprio: os ACH restantes não foram reconferidos um a um (§6) |
| `59745df3` (07/10) | "Quer que eu escreva esse registro em doc/?" | A decisão de não reaproveitar documentos agora, e o gatilho (inscrições em vários Perfis no piloto), não foram escritos | CA-35 |
| `ae3ad7c8` (16/09) | "Se quiser o alívio já, é um PR pequeno" | "Natureza do Edital" (aluno × bolsista) para esconder campos de emprego na autoria | ED-28 (ideia, §5) |
| `84c96e5f` (12/10) | "Quer que eu mande para ela esses pontos como requisitos" | Meta de tempo, modo de raciocínio, limite de resposta e escolha de Perfil para a `071`; só a medição na L4 virou tarefa (T058–T060) | AS-07 |
| `6ef6d5ee` (06/10) | "Ajuda dentro do sistema. Fica para quando houver a massa mínima de capítulos" | Link "Ajuda" em `/ajuda/` e ajuda contextual por tela | ideia de GO (§5) |
| `3bd46d67` (~20/09) | "eu só prometo depois de medir o risco dos papéis globais, não antes" | Paralelizar a suíte (xdist) depois de isolar os papéis do cluster | ideia de GO (§5) |
| `d8beef33` (29/09) | "Posso corrigir num PR pequeno a partir da main … Você decide." | A cópia do Duplicar aparece depois da origem e salta de posição ao salvar | ED-21 |
| `8f427c86` (16/09) | "Carregar uma amostra de algumas centenas no seed resolveria, se valer a pena." | O `seed_demo` não carrega CEP, e a demonstração mostra só o caminho degradado | GO-29 |
| `ac086e7a` (08/09) | "Posso varrer as demais classes genéricas da folha e registrar" | `.documento` e `.selecao` vazaram entre componentes; as demais classes genéricas não foram varridas | não entra: nenhuma fonte posterior registra outro vazamento |
| `0b03a4b5` (28/08) | "Contadores no cronograma — total, públicos, internos, pendências." | Contadores, linha do tempo e reordenação de Eventos trazidos do mockup inicial | não entra: sem demanda posterior; o mockup deixou de ser referência |

### (c) Decisões do usuário nunca registradas em documento

| Sessão | Citação | O que se perdeu | Onde está agora |
|---|---|---|---|
| `ae3ad7c8` (16/09) | "Não permitir sobrescrita de atribuições no Perfil ou na Oferta." | As posições sobre o modelo Oferta (Oferta referencia declarações tipadas; `id` estável; Grupos 1/2/3 fora) — nenhuma busca em `doc/` ou `specs/` as encontra | ED-31 |
| `e76c2efd` (14/10) | "Ajuste a premissa: o sistema existe apenas no meu computador." | A premissa que reordena todas as prioridades só existia na `074` sem commit e na atualização não commitada da Visão do Sistema | registrada agora nesta auditoria (matriz, roadmap e [decisões pendentes](decisoes-pendentes.md)); GO-46 |
| `3bd46d67` (~19/09) | "o sistema deve ser genérico o suficiente para permitir editais tanto de alunos quando de bolsistas" | O princípio de produto que recusou Curso/Polo/Turma como entidades e orientou a 039 | ED-28, GO-40 |
| `59745df3` (07/10) | "to achando que não compensa, né?" | O adiamento do reaproveitamento de documentos e o gatilho para retomá-lo | CA-35 |
| `0b4d88f5` (21/09) | "capacidade própria, inicialmente no gestor, sem inventar o papel diretoria." | Implementada (`visao:consultar` no Gestor), mas a `040` (G-010, §23) e a auditoria de 26/09 ainda a dão como aberta | GO-14, GO-41 |
| `de544cbf` (12/09) | "lembrando que isso só se aplica a editais de alunos.. temos diversos outros editais, como bolsistas" | O enquadramento seleção × matrícula entrou em parte na descoberta da 029 (16/09). O "registro de descoberta" que o usuário assinaria não foi escrito, nem as duas perguntas ao encarregado (Termo revogável × cessão de imagem e voz; Anexo II de todos os inscritos) | CA-07 |
| `3bd46d67` (~19/09) | "Concordo com o diagnóstico e com a ordem geral." | O teto contra spec à frente do código (~100 linhas de código → ~300 de spec, uma passada de analyze) foi aplicado na 038 e na 039 e não foi escrito | não entra: regra de processo, não pendência de produto |
| `7bf91059` (13/10) | "cada componente novo precisa atender uma tarefa existente ou resolver um problema demonstrado" | Critério anti-excesso do piloto; a busca literal em `doc/` e `specs/` não o encontra | não entra: regra de processo |
| `75d0dcc9` (29/08) | "Use Create a merge commit. Não use squash nem rebase." | A política de merge valeu para #3–#7; depois o repositório usou squash (#16, #124) sem decisão nova | não entra: governança do repositório (a proteção de branch está em GO-32) |

**Decisões que constavam só como menção ou tarefa, sem dono.** Três das mais pesadas estão escritas, mas
nunca viraram trabalho:

| Sessão | Citação | Onde está escrita | Onde está agora |
|---|---|---|---|
| `0b03a4b5` (28/08) | (pergunta) "LDAP" | `specs/002-frontend-administrativo/spec.md:18`; T056 aberta desde 29/08 | GO-01 |
| `c7194461` (01/09) | "A área candidata não entra em produção com dados reais enquanto a política… não estiver definida." | `specs/010-area-do-candidato/spec.md:69`; README | GO-19 |
| `8f427c86` (16/09) | "Não nesta feature, e vira spec própria." | `specs/029-requerimento-de-matricula/spec.md:114-120`, como lacuna nomeada | CA-19 |
| `533156c5` (03/09) | "Registrar E2E-004 e E2E-021 como pendências explícitas" | `doc/auditoria-exploratoria-e2e-2026-09-02.md:20`, "implementado na metade" | ED-08 |

### (d) Problemas vistos em teste ou percurso, sem encaminhamento

| Sessão | Citação | O que se perdeu | Onde está agora |
|---|---|---|---|
| `3445162b` (25/09) | "Pode ser um defeito antigo da 030." | Marcar "Admite recurso" recompôs o cartão e apagou o critério de desempate já preenchido; não foi investigado | ED-21 |
| `8f427c86` (16/09) | "Dois achados registrados que não viraram escopo: as duas ordens de travamento incompatíveis" | `comando_de_comissao` e `replace_draft` travam Processo e Edital em ordens opostas (risco de deadlock) | AV-50 (não confirmado) |
| `8f427c86` (16/09) | "a cegueira de test_trilha_legivel a operações passadas por constante" | O guardião da trilha legível não enxerga operação passada por constante | não entra: sem item; ninguém mediu quantas operações escapam |
| `8b6f3ada` (16/09) | "O mesmo pedido é ora saneado, ora recusado." | `atribuicao_id` malformado é descartado num caminho e recusado com 404 noutro; a prévia com `prever_a_definitiva` sem orçamento de consulta | não entra: sem reprodução posterior |
| `8a1c834a` (11/09) | "N+1 em profile.modalidades.order_by(\"code\")" | 16 consultas com um Perfil, 38 com sete, na emissão do quadro | não entra como item próprio; aproxima-se de AV-49 (escala sem teto medido) |
| `b82fa294` (08/10) | "Um Edital criado com “≥” no número não publica e não se corrige pela tela." | Número e título do Processo são recusados por caractere sem grafia, e nenhuma etapa os edita | ED-19 |
| `ffc0d6a5` (12/09) | "A 023 teria copiado os dois" | O 78/2026 abre inscrição antes da publicação e o 59 cita "Nível A2" num Edital A1; o reuso copiaria os dois erros | não entra como item próprio; aproxima-se de ED-14 (validação cruzada) |
| `ea8c1d68` (02/09) | "Não tenho explicação para nenhum dos dois." | Dois testes da 012 falharam uma vez e não se reproduziram | não entra: sem recorrência; as instabilidades conhecidas estão em GO-35 |
| `7bf91059` (13/10) | "um teste de tempo de outra área (`test_ocupacao.py`, que mede milissegundos)" | Falhou uma vez em 11.095 na suíte completa e passou isolado | GO-35 |
| `d2d89b94` (29/09) | "se a hipótese estiver certa, o efeito vale também em produção" | Leitura intermitente da versão vigente (hipótese: relógio recuando); três saídas, nenhuma escolhida | GO-35 |
| `85e2efd5` (28/09) | usuário: "sobe o sistema pra eu ver uma oportunidade de melhoria." | A oportunidade nunca foi descrita, e o servidor foi derrubado | não entra: o conteúdo não existe em fonte nenhuma |

---

## 4. Decisões superadas e substituídas

| Decisão original (data, fonte) | O que a substituiu (data, fonte) | Efeito |
|---|---|---|
| FR-084 da `010` no rascunho: só a mensagem do código (antes de 01/09) | recibo de inscrição e aviso de credencial — duas situações (01/09, `c7194461`) | o candidato recebe o protocolo por e-mail |
| FR-084 com duas situações | a convocação por mensagem individual, quando o Edital a declara (12/09, `019`; `specs/010-area-do-candidato/spec.md:548`) | o Edital que convoca por e-mail passa a ser cumprido |
| FR-084 com três situações | o aviso complementar vinculado a ato (09/10, `066`, `713f5a59`) | avisos manuais de resultado e chamada; a quinta situação (confirmação do Requerimento, e-mail de teste) exige nova revisão (CA-21) |
| Permissões por grupos LDAP mapeados em seis papéis (28/08, escolha do agente a partir de "O que for mais simples inicialmente.") | autenticação inteira adiada, na mesma sessão | a gestão nunca teve desenho de autenticação (GO-01) |
| Design system do SUAP como base visual (28/08, pergunta) | nunca obtido; CSS próprio (T057 aberta) | a identidade visual foi adiada de novo em 12/10 (Q2) |
| Conversão por âncoras e `before=`/`after=` na `004` (29/08, Q3/Q4) | "O sistema não está em produção e não há dados persistidos a preservar." (29/08) | a `004` sem compatibilidade histórica |
| Brasão e justificação fora da V1 (30/08) | aplicados na `008` (30/08) | PDF com brasão do Edital 146 e texto justificado |
| Sem PDF de comprovante (FR-063 da `009`) | "Reabra a decisão." — PDF determinístico no servidor (30/08) | comprovante com HMAC, sem botão "Imprimir" |
| Roadmap 008–014 com a Mesa como `010` (30/08, "Eu adotaria isso.") | "o roadmap mudou" (31/08, `e790da97`): `010` área do candidato, Mesa na `012` | a jornada do candidato veio antes da avaliação |
| Presidente não obrigatório (D-007 da `011`) | alocar exige presidente (01/09, revisão colada) | a comissão sem presidente não aloca |
| Sorteio "implementado posteriormente; vou buscar referência" (03/09) | `021` com fonte pública externa (08–10/09) e D-G3 (19/09) | a semente não é do operador; o piloto é por sorteio |
| Quantidade de vagas na Modalidade (alternativa A, recomendação do agente) | "C revisada" do usuário: quadro como coleção do Perfil (10/09) | `025` e `027` |
| Cascata Grupo 1→2→3 "da 016" (Out of Scope da `014`, 11/09) | "É da 014 (alvo derivado)" (12/09, pergunta) | a cascata ficou sem dono e não foi construída (ED-10) |
| E2E15-003 "aguarda decisão de governança" (03/09) | bloquear salvo reavaliação (RC-62, 28/09, #220) | a Mesa recusa concluir com Resultado vigente |
| "Deferir determinando reavaliação — Não utilize" (manual, 08/09) | a espécie tem caminho (#218, 28/09) | só a orientação nas telas continua aberta (AV-14) |
| Nome social coletado na `029` (resposta "A", 16/09) | "resposta B. Não nesta feature, e vira spec própria." (16/09, mesma sessão) | a spec própria nunca foi aberta (CA-19) |
| FR-470 da `032`: aviso para reserva em marco de ordem única (18/09, pergunta) | aposentada pela `034`, que emite ordem por lista | — |
| FR-461 como aviso → D-G1 impeditiva (19/09) | invariante do Perfil da `046` (26/09, pergunta "Invariante do Perfil") | Perfil sem nenhum marco com corte é impedido |
| D-G5 como spec própria (19/09) → absorvida pela `039` (20/09) | `048`: a Retificação acrescenta qualquer Modalidade, inclusive cota (26/09) | a `039` perdeu o motivo de existir |
| `039` com rótulo de família → "modelo honesto" (20/09) | recusada por `doc/decisao-recorte-documental.md` (25/09) e pela Constituição; "Mesclar com nota" (26/09) | a `039` está na `main` como `Draft`, nunca encerrada (ED-46) |
| DP-06 "só aviso" para a dupla leitura | "Impede só se exigido" na `046` (26/09, pergunta) | a regra de combinação segue sem decisão (AV-34) |
| UX-034: "Tirar o link da ocupação" (27/09, pergunta) | RC-137 emenda a UX-034 e repõe o link (28/09) | a convocação ganhou porta pela ocupação |
| Teste com o setor como porta das specs 049–051 (ordem de 27/09) | "Queria começar o piloto já com todas otimizações possíveis no operacional." (28/09) | as três foram feitas; o teste ficou sem data (GO-31) |
| RC-121: "Versão citada, sem exceção" (28/09, `06266eb6`) | "Manter a do #220" — citada, salvo se concede (28/09, `628c5ea1`) | o prazo retificado que concede alcança o resultado já divulgado |
| Retificação aceita teto 0: "Só registrar" (28/09) | corrigida no #227 (28/09) | — |
| Proposta de "zerar a auditoria" antes do piloto (27/09) | admitida como over-engineering (27/09) | ficaram só os itens que o piloto encontraria |
| Adiar a multiunidade até haver segundo campus (recomendação do agente, 06/10) | "TENHO RECEIO DE DEIXAR ISSO PARA DEPOIS" (06/10) | a `060` foi feita antes de haver dado |
| Normalizar `◦` em `•` (proposta do agente) | recusado: "O marcador vazado deve ser recusado para revisão" (08/10, pergunta) | — |
| Visualizador próprio de PDF, com zoom e rotação (07/10) | "Abrir em aba própria" na Mesa e no recurso (#258) | — |
| "Você perderá esta convocação" | "a comissão poderá registrar o não atendimento" (07/10, colado) | nenhuma frase promete perda automática |
| Página própria do assistente, "nenhum balão flutuante" (auditoria de 12/10) | painel lateral no desktop e tela cheia no celular, aberto por botão (14/10) | protótipo da Fase C (#280) |
| FR-1507 com orçamentos da aplicação; FR-1521 bloqueando qualquer divergência | só o limite de gasto da chave; DP-7 (b) — só o modelo bloqueia (13/10) | — |
| "Nenhuma interface" para configurações (auditoria de 14/10, do agente) | CLI agora; página "Configuração e diagnóstico" depois da autenticação (14/10) | `073` (#282; #283 aberto) |
| Premissa de operação pública: a `071` escreveu os portões da rota pública (FR-1462), a `073` desenhou a verificação de implantação, e a DP-20 pensou o piloto com candidatos (12–14/10) | "Ajuste a premissa: o sistema existe apenas no meu computador." (14/10, `e76c2efd`) | a `074` abre o assistente só no local; as prioridades passam a "P0 para a implantação"; a exceção ao FR-1462 está sem commit |

---

## 5. Ideias exploratórias (não são requisito)

Maturidade: **exploratória** (ideia sem discussão com o usuário) · **discutida** (o usuário falou dela sem
decidir) · **decidida** (há decisão, inclusive a de não fazer agora) · **especificada** (há spec ou FR).

| Ideia | Origem | Maturidade | Decisão necessária |
|---|---|---|---|
| Ifes Ads — campanhas geradas por programa | `34ab2a4e` (12/10); `doc/auditoria-ux-conversao-2026-10-12/jornada-publica.md:78-83` | exploratória (texto do agente); excluída do escopo do assistente pelo usuário (`84c96e5f`, 12/10) | nenhuma agora; não fechar a porta ao mudar endereço ou cabeçalho |
| Cadastro de interessados e captação (leads) | `84c96e5f` (12/10): "Não inclua essas funcionalidades no escopo." | decidida (fora do assistente) | se e quando, fora do assistente |
| Biblioteca audiovisual de Libras integrada | `9526cf31` (11/10); `docs/libras/viabilidade.md` | discutida; o próprio estudo diz que não há base para desenvolvê-la | Fase 1 do protocolo com profissionais e participantes surdos; enquadramento jurídico (ED-44) |
| Assistente de acompanhamento da candidatura (área autenticada) | `84c96e5f` (12/10): "Registre no roadmap, como evolução posterior" | decidida (evolução posterior) | se e quando (AS-22) |
| Modelo Oferta / eixos da oferta declarados pelo operador | `ae3ad7c8` (16/09); `3bd46d67` (~19/09) | discutida (posições do usuário, sem registro) | E2 — registrar ou descartar as posições de 16/09 (ED-31) |
| "Natureza do Edital" como facetas da autoria | `ae3ad7c8` (16/09) | exploratória | estudo Q4 da `072` (ED-28) |
| Reaproveitar documentos entre inscrições | `59745df3` (07/10) | decidida (não agora) | retomar se o piloto mostrar inscrições em vários Perfis (CA-35) |
| Gerador HTML → PDF, ato integral em HTML | `46626552` (12/10) | discutida (aprovada como alternativa futura) | quando tratar a acessibilidade do ato (ED-11) |
| LLM na elaboração do Edital | análise de linguagem simples, §7.5 (12/10) | exploratória ("depois") | nenhuma agora |
| Banco vetorial (pgvector) | `84c96e5f` (12/10) | exploratória | só se, depois de medir a L4, faltar recuperação |
| Classificador que manda a pergunta digitada à `070` | `7bf91059` (14/10) | decidida (rejeitada agora) | — |
| Página "Configuração e diagnóstico" | `f55c52a5` (14/10); `073` D-001 | decidida (depois da autenticação) | depende de GO-01 |
| Central "Ajuda" e ajuda contextual por tela | `6ef6d5ee` (06/10) | exploratória | depende do manual (GO-43) |
| Recuperação de acesso por gov.br ou suporte institucional | `29bde0c2` (30/08) | exploratória | se o portal troca o código por e-mail (CA-18) |
| Importar Edital externo em PDF; seleção parcial no reuso | `211d74e8` (09/09) | exploratória ("outra feature") | — |
| Catálogo do IFRN como tipo editorial fora do snapshot | `eeca206a` (03/09) | exploratória ("não agora") | — |
| SMS, WhatsApp e push | `713f5a59` (09/10) | decidida (fora do MVP da `066`) | — |
| Paralelizar a suíte (xdist) | `3bd46d67` (~20/09) | exploratória | isolar os papéis do cluster antes |

---

## 6. Lacunas desta reconstrução

- **Decisões por formulário que não se recuperaram.** As 111 respostas cobrem a maior parte, mas não todas.
  Onde só existe o relato do agente ("suas três respostas no clarify"), a decisão é do usuário pelo relato e
  não pela fala: clarify da `006` e da `007` em parte, PERGUNTAs do polish da `020`, a T055 da `022`, o
  recorte da `024`, o clarify da `049`, da `050` e da `068`.
- **Respostas perdidas.** Na `3bd46d67`, a resposta ao pedido "investigue os pontos identificados" (AX-14 e
  a correlação entre conceitos genéricos e particulares) se perdeu num replay; não se sabe se foi entregue.
  A `713f5a59` perdeu a resposta da implementação da `066` (erro de API), e a `9b1a378e` tem seis respostas
  com erro 529.
- **Autoria dos pareceres colados.** Não é possível separar, em todos os casos, o que o usuário pensou do
  que ele adotou de outro assistente. A própria `2bc3c441` chama de "decisões que as sessões tomaram
  sozinhas" escolhas da DP-14 que a `05b71845` tinha perguntado ao usuário, e as respostas recuperadas
  confirmam que ele as escolheu.
- **Outra pessoa no projeto.** O repositório é `vitofranzosi/processo_seletivo`, e a sessão `0b03a4b5`
  (28/08) deixou duas decisões "do Vito" sem resposta: `kind`/`provenance` no `openapi.yaml` (ED-45) e a
  regra do ADD (depois resolvida pela `004`). Conversas e decisões fora destas sessões — reuniões no Cefor,
  conversas com o Vito, mensagens — não estão em fonte nenhuma, e esta reconstrução não as vê.
- **Relatórios em Artifacts.** Os relatórios com capturas das jornadas de 01–02/09 (candidato, presidente,
  escala da 011, Mesa com 600 inscritos, "O caminho até a nota") e o de 07/09 existem só como artefatos do
  claude.ai. O que eles registram além do que as sessões resumem não foi conferido.
- **Microcópia da reauditoria.** Os ACH da varredura única proposta em ~19/09 não foram reconferidos um a
  um contra a `main`; parte foi corrigida pelas 030–038 e pela série de polish, e o resto não tem item.
- **Datas intermediárias.** Nas sessões que duram dias, a data de cada decisão é inferida de âncoras no
  texto ("18/09", "ontem"); o erro possível é de um ou dois dias.
- **Estado conferido por leitura.** O estado de cada linha vem da matriz, que conferiu código, specs e
  histórico da `main`. Esta seção não rodou nada; a suíte da `main` (11.297 passando, 11 pulados) foi rodada
  pela orquestração da auditoria em 15/10.
- **O que o usuário disse e as sessões não guardaram.** Uma oportunidade de melhoria anunciada em 28/09
  (`85e2efd5`) nunca foi descrita; o conteúdo dela não existe em fonte nenhuma.
