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

**A decisão que mais economiza** é o cumprimento derivado. A quarta espécie de decisão — deferimento
cuja providência é ato de outra autoridade — se fecha quando a publicação vigente divulga ato
diferente do reconhecido viciado. Sem entidade de cumprimento, sem espécie estruturada, sem ato de
impossibilidade: três vocabulários que verificariam o que uma comparação responde, e um passo humano
que, esquecido, travaria o marco por omissão.

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

**Storage**: PostgreSQL. **Duas migrations.** `recursos/0001` cria três tabelas — a peça, o juízo de
admissibilidade e a decisão —, com o `CHECK` de exatamente um objeto atacado, a unicidade por
titular × objeto, a unicidade de um juízo e de uma decisão por recurso, três triggers de
imutabilidade e uma de coerência. `resultados/0005` é **inteiramente de esquema**: três colunas
anuláveis, o terceiro valor de `origem`, quatro constraints novas, duas recriadas e a trigger
`resultado_etapa_coerente` recriada por inteiro — **sem backfill e sem desligar
`resultado_etapa_append_only`** (T-002). Uma terceira migration existe apenas se `appealWindow`
exigir declaração em `colecoes.py`; a elevação em si não é migration. `divulgacao` ganha **uma
coluna anulável** para a declaração expressa de encerramento do prazo (T-010).

**Testing**: pytest com pytest-django, marcadores `acceptance`, `contract`, `integration`,
`authorization` e `performance` já declarados. Quatro exigências específicas, e a primeira é a que
mais engana: as duas constraints de cadeia sob concorrência, a trigger de coerência e a recusa de
`UPDATE` pelo papel de runtime **só são exercidas com `TEST_DB_ENGINE=postgresql` e `DB_USER`** —
sem o primeiro a suíte cai para SQLite e pula tudo isso em silêncio, e um PR verde não prova nada
(T-014). As três tabelas novas entram em `TABELAS_APPEND_ONLY`; `recursos` entra em `APPS` e em
`TRIGGERS_POR_APP`; e o teste estrutural de vigência (T-004) é artefato desta feature, não herdado.

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

**Scale/Scope**: um Edital com mil inscritos e até três marcos por Perfil. **Um app novo, três
tabelas, duas migrations, quatro triggers, um papel e uma capacidade novos, uma elevação de versão
canônica, quatro rotas administrativas, duas rotas do candidato e dois acréscimos ao
acompanhamento.** O item que domina o cronograma não é nenhum desses: é o inventário de vigência
(T-004), que atravessa quatro apps e não entrega comportamento visível nenhum.

## Constitution Check

*GATE: aprovado antes da Fase 0 e reavaliado após a Fase 1.*

| Princípio | Exigência | Como esta feature responde |
|---|---|---|
| I — Linguagem ubíqua e integridade | Conceitos distintos; identificadores estáveis; invariantes em constraint; histórico não excluído | **Recurso** é o conceito que a Constituição já nomeia entre os que exigem autorização própria, e nasce distinto de Avaliação, Resultado e Publicação. O impedimento recursal **é** o `Impedimento` da 012, ampliado do avaliar para o julgar — criar um segundo seria a linguagem se partindo pelo canal da pergunta (D-005). As invariantes centrais vão ao banco: raiz única por par, sucessor único, exatamente um objeto atacado, um juízo e uma decisão por recurso. Nada é excluído: `delete` recusa, a trigger recusa, o papel de runtime não tem privilégio. **Passa** |
| II — Integridade normativa e temporalidade | Fonte única; publicado imutável; estado vigente reproduzível; zona institucional | A janela é lida do conteúdo publicado, e a ausência tem significado declarado no degrau 8 — nunca inferida de `EventoCronograma.type`, que é texto livre (T-007). A vigência do Resultado é **derivada da cadeia**, e não coluna: a segunda fonte que o princípio proíbe é exatamente o que a alternativa 3 da decisão C perdia. A reprodução histórica é imune por construção (T-004). A contagem usa a zona institucional, que sobe de `interface/` para módulo compartilhado antes de ser usada pelo domínio (T-008). **Passa** |
| III — Segurança, dados pessoais e auditoria | Negar por padrão; autorização específica para julgamento de recurso; IDOR; LGPD; auditoria | O Princípio III **nomeia** julgamento de recurso entre as operações que exigem autorização específica, e é o que `recurso:julgar` faz, em papel próprio para não conceder julgamento por carona (T-005). A titularidade do candidato usa o contrato existente, com 404 uniforme. Nenhum dado de terceiro atravessa as superfícies do recurso: o candidato vê o próprio Resultado, e a listagem administrativa não expõe fundamentação a quem não pode lê-la. Interposição, admissibilidade, decisão e superação entram na trilha existente, sem copiar fundamentação nem pontuação para ela. **Passa** |
| IV — Regras explícitas e consistência | Regra no backend; estados explícitos; transação; concorrência | Julgar é comando de domínio com transação, autorização reavaliada **depois** do bloqueio, reserva de idempotência e revalidação do que foi lido. O Recurso **não ganha máquina de estados persistida**: a situação deriva de quais atos existem (D-010), e a spec declara isso em vez de omitir. Concorrência coberta em cinco frentes, cada uma para um caso que as outras não pegam: idempotência, unicidade de sucessor no banco, unicidade de decisão por recurso, assinatura do que foi lido e bloqueio do Processo. **Passa** |
| V — Qualidade, rastreabilidade e simplicidade | Citação resolvível; teste como prova; simplicidade justificada | As onze decisões estão na spec, no formato que `test_citacoes_de_requisito.py` resolve. A simplicidade é **ativa e custou análise**: sem registro de cumprimento, sem espécie estruturada de providência, sem ato de impossibilidade, sem exceção à regra da janela, sem anexos, sem segunda instância, sem comissão recursal. Cada recusa está argumentada por alcançabilidade ou por precedente, e não por gosto. O que se acrescenta — um app, três tabelas, um degrau — é o mínimo que a imutabilidade e a promessa do Edital exigem. **Passa** |
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
├── data-model.md        # Fase 1 — as três tabelas novas e a sucessão do Resultado
├── quickstart.md        # Fase 1 — o roteiro que demonstra o gate da spec
├── contracts/
│   ├── recurso.md       # O candidato: ver o Resultado, interpor, acompanhar, ler a decisão
│   ├── julgamento.md    # A instituição: lista, admissibilidade, decisão e suas recusas
│   └── janela.md        # O degrau 8, a contagem, e a aferição de definitividade
├── checklists/
│   └── requirements.md  # Validação da spec, já aprovada
└── tasks.md             # Fase 2 — $speckit-tasks, não criado aqui
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── recursos/                            # app novo
│   ├── models.py                        # Recurso, JuizoDeAdmissibilidade, DecisaoRecurso
│   ├── migrations/0001_initial.py       # 3 tabelas, 13 constraints, 4 triggers
│   ├── domain/
│   │   ├── janela.py                    # contagem pura: abre, fecha, está aberta (T-008)
│   │   ├── elegibilidade.py             # as cinco perguntas do impedimento (T-006)
│   │   └── pejus.py                     # a comparação de piora, nos dois pontos (T-011)
│   ├── application/
│   │   ├── interpor.py                  # comando do candidato
│   │   ├── admitir.py                   # juízo de admissibilidade
│   │   ├── julgar.py                    # decisão + superação, na mesma transação
│   │   └── selectors.py                 # recursos do marco, do titular, pendências derivadas
│   └── domain/protocolo.py              # REC-AAAA-XXXXXXXX, alfabeto compartilhado (T-012)
├── resultados/
│   ├── models.py                        # + sucessão, origem RECURSO, FK da decisão
│   ├── migrations/0005_superacao.py     # só esquema, sem backfill (T-002)
│   ├── application/selectors.py         # + manager `vigentes` em todas as leituras de efeito
│   ├── application/prontidao.py         # + vigência nos 4 Exists; + pendência de reavaliação
│   └── application/consolidacao.py      # + a exceção única da FR-068
├── classificacao/application/calculo.py # + vigência e order_by determinístico (T-004)
├── divulgacao/
│   ├── models.py                        # + declaração expressa de encerramento do prazo
│   └── domain/publicabilidade.py        # + natureza pretendida e os cinco fatos (T-010)
├── publicacoes/domain/elevacao.py       # + DEGRAUS_DE_MARCO e elevar_marco (T-007)
├── shared/canonical.py                  # SCHEMA_VERSION 7 → 8
├── shared/tempo.py                      # a zona institucional, saindo de interface/ (T-008)
├── interface/                           # canal administrativo (existente)
│   ├── urls.py / views.py               # 4 rotas: lista, recurso, admitir, julgar
│   ├── forms.py                         # + a janela no assistente do marco
│   └── templates/interface/             # lista, tela do recurso, confirmações
├── portal/                              # canal do candidato (existente)
│   ├── urls.py / views.py               # 2 rotas: interpor e consultar o recurso
│   └── templates/portal/                # + Resultado da Etapa e bloco do recurso no acompanhamento
└── seguranca/papeis.py                  # + 3 tabelas em TABELAS_APPEND_ONLY

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

| Fase | Entrega | Termina quando |
|---|---|---|
| **F0** | Sucessão do `ResultadoEtapa`, filtro de vigência em toda leitura de efeito, teste estrutural | O teste estrutural falha em uso não declarado de `ResultadoEtapa.objects`, e a suíte inteira continua verde em PostgreSQL |
| **F1** | O candidato vê o próprio Resultado da Etapa | Helena, eliminada na Etapa 1 e fora do universo do ato, lê o próprio Indeferimento com o motivo escrito |
| **F2** | Interposição, protocolo, acompanhamento, recusa por objeto superado | O candidato recorre pelo portal e recebe protocolo; a segunda interposição é recusada nomeando a primeira |
| **F3** | App `recursos`, papel `julgador`, impedimento que bloqueia, admissibilidade motivada | Quem consolidou o Resultado atacado é recusado; quem tem a capacidade admite com motivo |
| **F4** | Decisão nas quatro espécies; deferimento que fixa correção supera na mesma transação | O Resultado sucessor nasce, o anterior permanece, o ato fica obsoleto e a publicação é recusada com caminho |
| **F5** | Reavaliação determinada: pendência nomeada, consolidação que produz o sucessor, *non reformatio* | A Etapa mostra a pendência, a nova Avaliação é consolidada como sucessor, e a pior é recusada |
| **F6** | Progressão retroativa visível e guarda de publicação | A linha reaberta aparece nomeada na Mesa e no painel; a publicação do marco é impedida |
| **F7** | Definitividade: os cinco fatos e a declaração expressa | Publicar como definitivo é recusado em cada um dos cinco casos, e permitido depois de resolvidos |
| **F8** | Janela recursal como conteúdo publicado | O elaborador declara a janela, o candidato vê os dois instantes, e a interposição fora do prazo é recusada citando a norma |

**A F0 é a maior, e não entrega nada visível.** É o preço de dar sucessão ao elo que não a tinha, e
é onde mora o risco silencioso da feature. Ela precisa de duas provas antes de qualquer outra coisa
existir: que o cálculo classificatório não colapsa com dois Resultados do mesmo par, e que a
eliminação superada deixa de excluir da progressão.

**A F8 vem por último de propósito.** É a única com custo de conteúdo publicado, e a única que, se a
feature precisar ser fatiada, tem por onde ser adiada sem desmontar as demais — a tempestividade
continua sendo juízo de admissibilidade motivado, que é a degradação que a decisão institucional
declara.

**A F6 não é polimento.** Sem os avisos nomeados, o efeito da progressão retroativa acontece e é
descoberto por acaso — uma Etapa que todos consideravam encerrada volta a ter linha pendente, e
ninguém sabe por quê.

## Complexity Tracking

> Sem violações a justificar. As quatro escolhas que acrescentam estrutura estão argumentadas, e
> três delas **reduzem** o que precisa ser confiado ao código.

| Escolha | Por que é necessária | Alternativa mais simples, e por que foi recusada |
|---|---|---|
| App novo `recursos`, com dependência de mão dupla (T-001) | A FK da decisão precisa morar no `ResultadoEtapa` para que "todo sucessor cita a decisão" seja constraint | Inverter a FK quebraria o ciclo de graça e perderia a invariante: do outro lado, a constraint possível não impede um sucessor nascer sem fundamento |
| Manager `vigentes` + teste estrutural (T-004) | Duas leituras quebram **em silêncio** com dois Resultados do mesmo par | "Lembrar de filtrar" — recusada porque a próxima feature que escrever `ResultadoEtapa.objects` reintroduz o defeito, e nenhum teste funcional o denuncia sem um recurso deferido em fixture |
| Papel novo `julgador` (T-005) | Cada papel existente concede julgamento a quem tende a estar impedido | Reaproveitar `publicador` ou `gestor` — recusada porque a D-005 proíbe que julgar derive de publicar ou de gerir |
| `DEGRAUS_DE_MARCO` na elevação (T-007) | O marco é coleção dentro do Perfil, e a elevação só desce dois níveis | Pôr a janela no Perfil, evitando o nível novo — recusada porque a decisão institucional é por marco, e um Edital com marco intermediário e final pode querer prazos distintos |
