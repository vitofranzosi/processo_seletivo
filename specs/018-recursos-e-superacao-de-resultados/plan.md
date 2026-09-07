# Implementation Plan: Recursos e Superação de Resultados

**Branch**: `claude/spec-018-recursos-6a3ffe` | **Date**: 2026-09-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-recursos-e-superacao-de-resultados/spec.md`

## Summary

A 017 fechou a borda: a instituição chega a uma decisão classificatória e a torna oficialmente
acessível. A 018 fecha o ciclo — a pessoa contesta essa decisão, uma autoridade imparcial a julga
com motivo, e a correção produz efeito **acrescentando** atos.

**A novidade conceitual é uma só, e ela é pequena: o `ResultadoEtapa` ganha sucessão.** Tudo o mais
já existe em duplicata no repositório. O que torna a feature grande não é o mecanismo novo — é o
inventário de leituras que hoje dizem "existe Resultado" querendo dizer "existe **um**".

Quatro verificações que sustentam esse tamanho, e nenhuma delas é otimismo:

1. **A forma da sucessão já foi escrita duas vezes.** `AtoDeOrdenacao` e `PublicacaoResultado` usam
   o mesmo par — raiz única por chave de negócio, sucessor único — com vigência derivada de
   `sucessor__isnull=True` e nenhuma coluna de estado. O `ResultadoEtapa` é o terceiro uso do mesmo
   padrão, e não um padrão novo (T-002).
2. **A cadeia a jusante já reage sozinha.** O ato de ordenação grava o conjunto de ids dos Resultados
   em `universo.stageResults`; `comparar()` emite `resultados_alterados` quando o conjunto muda;
   `aferir()` recusa a publicação e **nomeia o caminho**. Um Resultado novo já produz, hoje, o
   bloqueio que esta feature precisa. Nada disso é trabalho da 018.
3. **A reprodução histórica é imune por construção.** `reproduzir_ato` lê os Resultados por `pk__in`
   dos ids gravados na proveniência, e o superado permanece na tabela, imutável. A IO-5 da 015
   permanece verdadeira sem uma linha de cuidado — desde que ninguém acrescente filtro de vigência
   ali (T-004).
4. **A autoridade tem precedente exato.** A 017 já resolveu o caso simétrico ao separar constituir de
   divulgar: capacidade no mapa de papéis, `require_permission` fora da transação, bloqueio do
   Processo dentro dela. Julgar segue o mesmo desenho, e não o de `comando_de_comissao` — que
   autoriza por presidência, exatamente a derivação que a D-005 proíbe (T-005).

**A decisão que mais determina o desenho** é o filtro de vigência, e ela é defensiva. Duas leituras
quebram **em silêncio** quando existem dois Resultados do mesmo par: o dicionário de pontuações do
cálculo classificatório colapsa e o último do queryset vence — sem `order_by`, sem exceção, sem log
—, e os quatro `Exists` da progressão continuam excluindo quem teve a eliminação superada, tornando
o deferimento inofensivo exatamente onde ele deveria valer. Por isso o desenho não é "lembrar de
filtrar": é um manager nomeado `vigentes`, um `order_by` determinístico e um **teste estrutural** que
falha em uso não declarado de `ResultadoEtapa.objects` (T-004).

**A decisão que mais economiza** é o cumprimento por citação. A quarta espécie de decisão —
deferimento cuja providência é ato de outra autoridade — se fecha quando o ato de ordenação que se
publica **cita** a decisão que a determinou. A citação é proveniência do próprio ato, gravada por
quem o emite, na mesma transação: não há ato de cumprimento com autoridade própria, não há espécie
estruturada de providência, não há ato de impossibilidade. Uma redação anterior dava a pendência por
cumprida quando a publicação divulgasse "ato diferente", e isso a quitaria **por acidente** — um ato
sucessor emitido por razão alheia encerraria a pendência sem que ninguém tivesse corrigido o vício
(T-015).

**A que mais exigiu cuidado** é a reavaliação determinada. Consolidar recusa o par que já tem
Resultado, e é a consolidação que deve produzir o sucessor: sem exceção declarada, a inscrição
ficaria eliminada **e inconsolidável**, esperando a reavaliação que o próprio deferimento ordenou. A
exceção é única, limitada ao par que tem decisão dessa espécie não cumprida, e cita a decisão
obrigatoriamente (FR-055, FR-068). Uma garantia estrutural ajuda de graça:
`uq_avaliacao_concluida_por_pessoa` já impede que quem concluiu a Avaliação original conclua a
reavaliação.

**O que não aparece no diagrama e custa mais que tudo** é o degrau 8. A janela recursal é conteúdo
normativo novo, e arrasta `SCHEMA_VERSION` 7→8, um nível que a elevação ainda não sabe descer — o
marco é coleção **dentro** do Perfil —, escrita no assistente, presença no documento e entrada no
catálogo de Retificação. É a última fatia de propósito: o produto funciona sem ela pela degradação
que a própria decisão institucional declara (T-007).

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`)

**Primary Dependencies**: Django 5.2, DRF 3.16. **Nenhuma dependência nova, e nenhuma rota de API
nova.** Os dois canais já existem: `interface` (HTML administrativo) para a lista de recursos, a
admissibilidade e o julgamento; `portal` (HTML do candidato, atrás de titularidade) para ver o
Resultado da Etapa, interpor e ler a decisão. O `openapi.yaml` da 001 não muda: nada aqui é contrato
de API.

**Storage**: PostgreSQL. **Quatro migrations**, e o grafo entre elas importa:

```text
resultados/0004 ──▶ recursos/0001 ──▶ resultados/0005
                          └────────▶ classificacao/0004
divulgacao/0001 ──▶ divulgacao/0002        (independente das demais)
```

`recursos/0001` cria três tabelas — a peça, o juízo de admissibilidade e a decisão —, com **17
constraints** e **5 triggers**: três de imutabilidade e **duas** de coerência, porque uma trigger
instalada no `Recurso` não valida linha da `DecisaoRecurso`. `resultados/0005` é **inteiramente de
esquema** — três colunas anuláveis, o terceiro valor de `origem`, quatro constraints novas, duas
recriadas e a trigger `resultado_etapa_coerente` recriada por inteiro, **sem backfill e sem desligar
`resultado_etapa_append_only`** (T-002) —, e vem **depois** de `recursos/0001`, porque cita
`DecisaoRecurso`. `classificacao/0004` cria a citação que o ato carrega, com **apenas** `UNIQUE(ato, decisao)` — a unicidade global criaria beco e impediria a pertinência a mais de um marco (T-015, FR-112). `divulgacao/0002`
acrescenta os **três** campos da declaração expressa de encerramento do prazo, com o `CHECK` de que
estão os três presentes ou os três ausentes (T-010).

`appealWindow` **não exige migration**: é JSON dentro de `VersaoConsolidada.content`, e o degrau 8 é
código de leitura e elevação.

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. Quatro exigências específicas, e a primeira é a que
mais engana: as duas constraints de cadeia sob concorrência, a trigger de coerência e a recusa de
`UPDATE` pelo papel de runtime **só são exercidas com `TEST_DB_ENGINE=postgresql` e `DB_USER`** —
sem o primeiro a suíte cai para SQLite e pula tudo isso em silêncio, e um PR verde não prova nada
(T-014). As **quatro** tabelas novas entram em `TABELAS_APPEND_ONLY`; `recursos` entra em `APPS` e
em `TRIGGERS_POR_APP`, e `classificacao` ganha ali as duas triggers da citação; e o teste
estrutural de vigência (T-004) é artefato desta feature, não herdado.

**Target Platform**: servidor Linux; navegador institucional e celular. A superfície do candidato
cresce em dois pontos — o Resultado individual da Etapa e a peça recursal —, e os dois vivem dentro
do acompanhamento, que já é responsivo.

**Project Type**: aplicação web com canal HTML servido pelo Django. Sem SPA, sem build de front.

**Performance Goals**: número **constante** de consultas nas três leituras que a feature acrescenta:
o Resultado da Etapa no acompanhamento (3 consultas, entre 1 e N marcos — T-009), a lista de recursos
recebidos e a aferição de definitividade (5 perguntas de existência — T-010). O impedimento custa
cinco perguntas pontuais **por ato de julgamento**, e nenhuma por linha de listagem: é ponto único, e é isso
que o distingue do custo que a 012 recusou (T-006). Os orçamentos de consulta que a 011, a 012 e a
015 escreveram em teste não podem regredir — o filtro de vigência dobra-se nos `Exists` que já
existem, sem round-trip adicional.

**Constraints**: julgar segura a linha do `ProcessoSeletivo` pela duração da transação, como toda a
família de comandos já faz — julgar, consolidar, emitir e publicar passam a esperar um pelo outro. A
aferição de definitividade acrescenta cinco existências ao caminho que já reproduz o estado
classificatório; a reprodução continua sendo o custo dominante, e ela não mudou.

**Scale/Scope**: um Edital com mil inscritos e até três marcos por Perfil. **Um app novo, quatro
tabelas, quatro migrations, sete triggers novas e uma recriada, um papel e uma capacidade novos, uma
elevação de versão canônica, quatro rotas administrativas, duas rotas do candidato e dois acréscimos
ao acompanhamento.** O item que domina o cronograma não é nenhum desses: é o inventário de vigência
(T-004), que atravessa quatro apps e não entrega comportamento visível nenhum.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; invariantes em constraint; histórico não excluído | **Recurso** é o conceito que a Constituição já nomeia entre os que exigem autorização própria, e nasce distinto de Avaliação, Resultado e Publicação. O impedimento recursal **é** o `Impedimento` da 012, ampliado do avaliar para o julgar — criar um segundo seria a linguagem se partindo pelo canal da pergunta (D-005). As invariantes centrais vão ao banco: raiz única por par, sucessor único, exatamente um objeto atacado, um juízo e uma decisão por recurso. Nada é excluído: `delete` recusa, a trigger recusa, o papel de runtime não tem privilégio. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível; zona institucional | A janela é lida do conteúdo publicado, e **cada um dos três estados** tem significado declarado no degrau 8 — não declarada, negada e declarada (FR-113) —, nunca inferida de `EventoCronograma.type`, que é texto livre (T-007). A vigência do Resultado é **derivada da cadeia**, e não coluna: a segunda fonte que o princípio proíbe é exatamente o que a alternativa 3 da decisão C perdia. A reprodução histórica é imune por construção (T-004). A contagem usa a zona institucional, que sobe de `interface/` para módulo compartilhado antes de ser usada pelo domínio (T-008). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; autorização específica para julgamento de recurso; IDOR; LGPD; auditoria | O Princípio III **nomeia** julgamento de recurso entre as operações que exigem autorização específica, e é o que `recurso:julgar` faz, em papel próprio para não conceder julgamento por carona (T-005). A titularidade do candidato usa o contrato existente, com 404 uniforme. Nenhum dado de terceiro atravessa as superfícies do recurso: o candidato vê o próprio Resultado, e a listagem administrativa não expõe fundamentação a quem não pode lê-la. Interposição, admissibilidade, decisão e superação entram na trilha existente, sem copiar fundamentação nem pontuação para ela. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Julgar é comando de domínio com transação, autorização reavaliada **depois** do bloqueio, reserva de idempotência e revalidação do que foi lido. O Recurso **não ganha máquina de estados persistida**: a situação deriva de quais atos existem (D-010), e a spec declara isso em vez de omitir. Concorrência coberta em cinco frentes, cada uma para um caso que as outras não pegam: idempotência, unicidade de sucessor no banco, unicidade de decisão por recurso, assinatura do que foi lido e bloqueio do Processo. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Citação resolvível; teste como prova; simplicidade justificada | As onze decisões estão na spec, no formato que `test_citacoes_de_requisito.py` resolve. A simplicidade é **ativa e custou análise**: sem **ato autônomo** de cumprimento, sem espécie estruturada de providência, sem ato de impossibilidade, sem exceção à regra da janela, sem anexos, sem segunda instância, sem comissão recursal. Cada recusa está argumentada por alcançabilidade ou por precedente, e não por gosto. O que se acrescenta — **um app novo, quatro tabelas** e um degrau — é o mínimo que a imutabilidade e a promessa do Edital exigem, e a quarta tabela é **proveniência**, não ato: `CitacaoDeDecisao` registra que um ato citou uma decisão, e quem conclui que a providência foi cumprida é a leitura, não uma linha. **Passa** |
| VI — Completude de jornada e valor demonstrável | Capacidade observável pelo canal do ator | A jornada fecha nos canais dos quatro atores: o candidato vê o próprio Resultado e recorre pelo portal; a autoridade admite e julga pela interface administrativa; a presidência vê a reabilitação na Etapa; o publicador é impedido e depois autorizado a publicar como definitivo. O único slice sem comportamento observável é o F0, e a spec declara o que ele desbloqueia. **Passa** |

**Reavaliação após a Fase 1**: os artefatos de contrato e o modelo de dados não introduziram
violação nova. A única tensão que a Fase 1 acrescentou está registrada em T-001 — a dependência de
mão dupla entre `recursos` e `resultados` — e ela é resolvida por referência tardia, sem ciclo no
grafo de migrations e sem import circular em Python.

## Project Structure

### Documentation (this feature)

```text
specs/018-recursos-e-superacao-de-resultados/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — as decisões técnicas T-001 a T-014
├── data-model.md        # Fase 1 — as quatro tabelas novas e a sucessão do Resultado
├── quickstart.md        # Fase 1 — o roteiro que demonstra o gate da spec
├── contracts/
│   ├── recurso.md       # O candidato: ver o Resultado, interpor, acompanhar, ler a decisão
│   ├── julgamento.md    # A instituição: lista, admissibilidade, decisão e suas recusas
│   └── janela.md        # O degrau 8, a contagem, e a aferição de definitividade
├── checklists/
│   └── requirements.md  # Validação da spec, já aprovada
└── tasks.md             # Fase 2 — 121 tarefas em 11 fases
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── recursos/                            # app novo
│   ├── models.py                        # Recurso, JuizoDeAdmissibilidade, DecisaoRecurso
│   ├── migrations/0001_initial.py       # 3 tabelas, 17 constraints, 5 triggers
│   ├── domain/
│   │   ├── janela.py                    # contagem pura: abre, fecha, está aberta (T-008)
│   │   ├── elegibilidade.py             # as cinco perguntas do impedimento (T-006)
│   │   ├── consequencia.py              # deriva a consequência da conclusão fixada (FR-059)
│   │   ├── pejus.py                     # a comparação de piora, nos dois pontos (T-011)
│   │   └── protocolo.py                 # REC-AAAA-XXXXXXXX, alfabeto compartilhado (T-012)
│   └── application/
│       ├── interpor.py                  # comando do candidato
│       ├── admitir.py                   # juízo de admissibilidade
│       ├── julgar.py                    # decisão + superação, na mesma transação
│       └── selectors.py                 # recursos do marco, do titular, pendências derivadas
├── resultados/
│   ├── models.py                        # + sucessão, origem RECURSO, FK da decisão
│   ├── managers.py                      # o manager `vigentes` — do modelo, não do selector (T-004)
│   ├── migrations/0005_superacao.py     # só esquema, sem backfill (T-002)
│   ├── application/selectors.py         # CONSOME o manager em toda leitura de efeito
│   ├── application/prontidao.py         # + vigência nos 4 Exists; + pendência de reavaliação
│   └── application/consolidacao.py      # + a exceção única da FR-068
├── classificacao/
│   ├── models.py                        # + CitacaoDeDecisao — proveniência, não ato (T-015)
│   ├── migrations/0004_citacao.py       # 1 tabela, 1 constraint, 2 triggers (FR-112)
│   ├── domain/universo.py               # + a causa `participante reingressou` (FR-078)
│   ├── application/calculo.py           # + vigência e order_by determinístico (T-004)
│   └── application/emissao.py           # + a citação das decisões cumpridas, na mesma transação
├── divulgacao/
│   ├── models.py                        # + os 3 campos da declaração de encerramento
│   ├── migrations/0002_declaracao.py    # 3 colunas, 1 constraint
│   ├── domain/publicabilidade.py        # + natureza pretendida e os seis fatos (T-010)
│   └── application/publicar.py          # + a natureza a aferir e a declaração expressa (FR-085)
├── avaliacoes/
│   ├── application/impedimento.py       # + vigência na leitura de Resultado (T-004)
│   └── application/avaliacao.py         # a recusa deixa de prometer "anulação" (FR-111)
├── editais/domain/perfis.py             # + validação de `appealWindow` na publicação (FR-021)
├── publicacoes/
│   ├── domain/elevacao.py               # + DEGRAUS_DE_MARCO e elevar_marco (T-007)
│   ├── domain/colecoes.py               # endereçamento de `appealWindow` por Retificação (T-007)
│   └── infrastructure/pdf.py            # + a frase normativa da janela no documento (FR-030)
├── shared/canonical.py                  # SCHEMA_VERSION 7 → 8
├── shared/tempo.py                      # a zona institucional, saindo de interface/ (T-008)
├── interface/                           # canal administrativo (existente)
│   ├── identidade.py                    # + o papel `julgador` com `recurso:julgar` (T-005)
│   ├── urls.py / views.py               # 4 rotas: lista, recurso, admitir, julgar
│   ├── forms.py                         # + a janela no assistente do marco
│   └── templates/interface/             # lista, tela do recurso, confirmações, Mesa e painel
├── portal/                              # canal do candidato (existente)
│   ├── urls.py / views.py               # 2 rotas: interpor e consultar o recurso
│   └── templates/portal/                # + Resultado da Etapa e bloco do recurso no acompanhamento
└── seguranca/papeis.py                  # + 4 tabelas em TABELAS_APPEND_ONLY

backend/tests/
├── acceptance/                          # o gate da spec, ponta a ponta
├── authorization/                       # os negativos de FR-038 a FR-043
├── contract/                            # a canonização do degrau 8 e a contagem da janela
├── integration/recursos/                # comandos, recusas, concorrência, non reformatio
├── integration/resultados/              # a superação e o que ela obsoleta a jusante
├── interface/ e portal/                 # as telas dos quatro atores
├── performance/                         # derivada zero nas três leituras novas
├── unit/recursos/                       # janela, elegibilidade, pejus
├── migrations/test_migrations.py        # + "recursos" em APPS e TRIGGERS_POR_APP
└── test_vigencia_do_resultado.py        # o teste estrutural de T-004
```

**Structure Decision**: app novo `recursos`, no precedente do que a 015 fez com `classificacao` e a
017 com `divulgacao`. A justificativa está em T-001, e o que a torna menos trivial que as anteriores
é a direção da dependência: aqui ela é de mão dupla, porque a FK da decisão precisa morar no
`ResultadoEtapa` para que "todo sucessor cita a decisão" seja constraint, e não promessa.

## Fases de implementação sugeridas

As fases seguem os slices da spec, e cada uma termina em comportamento observável pelo navegador —
exceto a primeira, que a spec declara como desbloqueio.

**A ordem é ditada pelo grafo de migrations, e não por preferência.** `resultados/0005` cita
`recursos.DecisaoRecurso`, de modo que **os modelos de `recursos` precisam existir antes da sucessão
do Resultado**. Uma versão anterior deste plano punha o app na F3 e a sucessão na F0, e era
inexequível: a F0 não teria para onde apontar a chave, e a F2 tentaria interpor recurso num app que
ainda não existia.

| Fase | Entrega | Termina quando |
|---|---|---|
| **F0** | **Fundação persistente, e só o que é indivisível**: app `recursos` com as três tabelas, constraints e triggers; sucessão do `ResultadoEtapa`; manager `vigentes` consumido em toda leitura de efeito; teste estrutural | `recursos/0001` e `resultados/0005` aplicam do zero e a partir da anterior; o teste estrutural falha em uso não declarado de `ResultadoEtapa.objects`; a suíte inteira continua verde em PostgreSQL |
| **F1** | O candidato vê o próprio Resultado da Etapa | Helena, eliminada na Etapa 1 e fora do universo do ato, lê o próprio Indeferimento com o motivo escrito |
| **F2** | Interposição, protocolo, acompanhamento, recusa por objeto superado — **sobre a fundação da F0** | O candidato recorre pelo portal e recebe protocolo; a segunda interposição é recusada nomeando a primeira |
| **F3** | Papel `julgador`, impedimento que bloqueia, admissibilidade motivada, decisão nas quatro espécies, e o deferimento que fixa correção superando na mesma transação | Quem consolidou o Resultado atacado é recusado; o Resultado sucessor nasce, o anterior permanece, o ato fica obsoleto e a publicação é recusada com caminho |
| **F4** | Reavaliação determinada: pendência nomeada, consolidação que produz o sucessor, *non reformatio* nos dois pontos | A Etapa mostra a pendência, a nova Avaliação é consolidada como sucessor, e a pior é recusada |
| **F5** | Progressão retroativa visível e guarda de publicação | A linha reaberta aparece nomeada na Mesa e no painel; a publicação do marco é impedida |
| **F6** | Definitividade: `classificacao/0004` e `divulgacao/0002`, os seis fatos, a declaração expressa, e a citação na emissão | Publicar como definitivo é recusado em cada caso, e permitido depois de resolvidos; ato citante **publicado** cumpre a providência, e a citação impertinente é recusada no banco |
| **F7** | Janela recursal como conteúdo publicado | O elaborador declara a janela, o candidato vê os dois instantes, e a interposição fora do prazo é recusada citando a norma |

**Correspondência com as fases de [tasks.md](./tasks.md)**, que agrupa por história de usuário:

| fase deste plano | fases das tarefas |
|---|---|
| F0 | Phase 1 (Setup) + Phase 2 (Foundational) |
| F1 | Phase 3 — US1 |
| F2 | Phase 4 — US2 |
| F3 | Phase 5 (US3) **e** Phase 6 (US4) — a autoridade e o julgamento são duas histórias |
| F4 | Phase 7 — US5 |
| F5 | Phase 8 — US8 |
| F6 | Phase 9 — US7 |
| F7 | Phase 10 — US6 |
| — | Phase 11 (Polish), que o plano não fatia — e que depende da **conclusão das histórias**, não da fundação |

**A F0 é a maior, e não entrega nada visível.** Ela hospeda as duas coisas que precisam nascer
juntas — a fundação de `recursos` e a sucessão do Resultado —, porque `resultados/0005` cita
`DecisaoRecurso` e a chave estrangeira as amarra. É também onde mora o risco silencioso da feature, e
precisa de duas provas antes de qualquer outra coisa existir: que o cálculo classificatório não
colapsa com dois Resultados do mesmo par, e que a eliminação superada deixa de excluir da progressão.

**E ela é só isso.** `classificacao/0004` e `divulgacao/0002` são independentes da fundação — nada as
amarra a `recursos/0001` além da ordem do grafo — e só entregam a F6. Uma redação anterior as punha
aqui e chamava a F0 de indivisível; a indivisibilidade verdadeira é `recursos/0001 → resultados/0005`,
e inchar a fundação com o que pode esperar é o oposto de fatiar.

**O que a F0 deliberadamente não entrega**: telas, comandos, autorização e o papel `julgador`. Ela
cria a fundação persistente, e nada mais — é trabalho técnico que a spec declara como desbloqueio,
com a capacidade que ele destrava nomeada nas fases seguintes.

**A F7 vem por último de propósito.** É a única com custo de conteúdo publicado, e a única que, se a
feature precisar ser fatiada, tem por onde ser adiada sem desmontar as demais — a tempestividade
continua sendo juízo de admissibilidade motivado, que é a degradação que a decisão institucional
declara.

**A F5 não é polimento.** Sem os avisos nomeados, o efeito da progressão retroativa acontece e é
descoberto por acaso — uma Etapa que todos consideravam encerrada volta a ter linha pendente, e
ninguém sabe por quê.

## Complexity Tracking

> Sem violações a justificar. As quatro escolhas que acrescentam estrutura estão argumentadas, e
> três delas **reduzem** o que precisa ser confiado ao código.

| Escolha | Por que é necessária | Alternativa mais simples, e por que foi recusada |
|---|---|---|
| App novo `recursos`, com dependência de mão dupla (T-001) | A FK da decisão precisa morar no `ResultadoEtapa` para que "todo sucessor cita a decisão" seja constraint | Inverter a FK quebraria o ciclo de graça e perderia a invariante: do outro lado, a constraint possível não impede um sucessor nascer sem fundamento |
| `CitacaoDeDecisao` como tabela de proveniência (T-015) | Sem vínculo causal, um ato sucessor emitido por razão alheia quitaria a providência por acidente | Uma FK única no `AtoDeOrdenacao` — recusada porque dois deferimentos sobre o mesmo marco obrigariam a emitir um ato por decisão, a "sucessão que não sucedeu nada" que a D-007 da 017 critica. `UNIQUE(decisao)` — recusada porque criava beco quando o ato citante ficava obsoleto antes de publicar, e impedia a pertinência a mais de um marco. E "qualquer sucessor cumpre" — recusada por ser o problema de origem |
| Manager `vigentes` + teste estrutural (T-004) | Duas leituras quebram **em silêncio** com dois Resultados do mesmo par | "Lembrar de filtrar" — recusada porque a próxima feature que escrever `ResultadoEtapa.objects` reintroduz o defeito, e nenhum teste funcional o denuncia sem um recurso deferido em fixture |
| Papel novo `julgador` (T-005) | Cada papel existente concede julgamento a quem tende a estar impedido | Reaproveitar `publicador` ou `gestor` — recusada porque a D-005 proíbe que julgar derive de publicar ou de gerir |
| `DEGRAUS_DE_MARCO` na elevação (T-007) | O marco é coleção dentro do Perfil, e a elevação só desce dois níveis | Pôr a janela no Perfil, evitando o nível novo — recusada porque a decisão institucional é por marco, e um Edital com marco intermediário e final pode querer prazos distintos |
