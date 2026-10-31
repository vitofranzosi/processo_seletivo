# Auditoria independente de prontidão arquitetural e operacional do GPS — 31/10/2026

*Auditoria técnica, arquitetural e operacional do GPS — Sistema de Gestão de Processos Seletivos
do Cefor/Ifes —, feita em 31/10/2026 sobre a `main` em `4ca16b1d` (depois do #352, que fechou a
spec `110`), com as specs `106` a `110` integradas. Nada do código de produção, das specs ou da
documentação anterior foi alterado; nenhuma spec foi criada; nenhum commit de implementação foi
feito. Caminhos relativos a `backend/processo_seletivo/`, salvo quando começam por `backend/`,
`doc/`, `specs/` ou `config/`.*

Marcas, em todo o documento: **[F]** fato lido no código, com `arquivo:linha` · **[E]** fato
demonstrado em execução, com o comando ou o teste · **[I]** inferência fundamentada · **[H]**
hipótese não verificada. Conclusão de leitura e conclusão de execução ficam separadas.

**Como foi feito.** Sete frentes de investigação, em paralelo, sobre a mesma árvore e o mesmo
ambiente: um banco de auditoria (`processo_seletivo_audit`) preparado pelo caminho canônico
(`make preparar`: provisionar, migrar, provisionar — `46 de 46` tabelas append-only protegidas —
e a semente das Unidades) e semeado com `seed_demo`; inspeção como a role de **produção**
(`processo_seletivo_runtime`) e como a de migração; testes direcionados e descartáveis contra
PostgreSQL, um banco por frente; um boot da configuração de **produção** sob gunicorn com
variáveis fictícias; e um ensaio local de restauração. A suíte inteira não foi executada (ela é
conhecida: 12.775 passando em 21/10). O achado P0 foi reproduzido por três frentes distintas e
pela coordenação, por quatro caminhos; os P1, por duas frentes cada. O método e os limites
estão no Anexo III.

---

## Resumo executivo (para a coordenação)

**O GPS está arquiteturalmente sólido no que importa para um ato administrativo: o que é
publicado é imutável em duas camadas independentes, o isolamento entre unidades funciona em
execução, a autorização nega por padrão e os fluxos críticos são serializados e idempotentes.**
Isso foi verificado, e não presumido: 75 acessos de uma unidade a objetos de outra devolveram 404
sem gravar nada; a role de produção não consegue alterar nem apagar nenhuma das 46 tabelas de ato;
dois julgamentos, duas interposições e dois Editais com o mesmo número, lançados ao mesmo tempo,
terminam em um ato e uma recusa legível; o código de acesso do candidato é gerado, guardado e
conferido como manda a prática.

**Há um defeito comprovado que bloqueia o rito recursal em produção, invisível para a suíte.** O
julgamento de recurso *com efeito* (correção fixada ou reavaliação determinada) tranca a linha do
Resultado com `SELECT … FOR UPDATE`; o PostgreSQL exige privilégio de `UPDATE` para isso, e a
role de produção não o tem sobre a tabela, que é append-only. Em produção, o primeiro deferimento
com efeito termina em erro do servidor; os indeferimentos funcionam, e por isso o módulo parece
são até o dia em que não é. A suíte roda como superusuário e não vê. O mesmo defeito já ocorreu na
`106`, foi corrigido ali e recebeu um guardião que só varre `seguranca/`. A correção é de poucas
linhas (a trava é redundante: o comando já tranca o Processo e a unicidade do sucessor responde
no banco), mas o que ela revela é sistêmico: **nenhum fluxo de aplicação é exercitado com os
privilégios reais da role de produção.**

**O segundo ponto é de garantia, não de fluxo.** A inscrição enviada, o documento submetido, a
avaliação concluída e a homologação do Edital são protegidos **só pela aplicação**: a role de
produção altera nome, CPF e e-mail de inscrições enviadas, devolve-as a rascunho e apaga as
credenciais de acesso dos candidatos sem que gatilho algum recuse — ao contrário das 46 tabelas de
ato e do Requerimento de Matrícula, que têm gatilho condicional exatamente para isso. O projeto
tem o padrão pronto e o próprio comentário da migration do Requerimento cita a Inscrição como
motivo; nunca foi aplicado a ela.

**O terceiro é operacional e depende de medição.** O e-mail do código de acesso, do comprovante e
da convocação sai dentro da requisição, com workers síncronos e sem limite de taxa no proxy
proposto. Um servidor de correio degradado no último dia de inscrição prende cada worker por até
20 segundos por pedido; com cinco workers, o portal inteiro — e não só o envio — para de responder a
partir de 15 pedidos de código por minuto. O mecanismo foi demonstrado; a carga, não foi medida.

**A jornada inteira foi refeita pela interface, como a role de produção, e fecha — com quatro
avisos.** Criar, partir de um Edital anterior, submeter, homologar, publicar, retificar, inscrever
três candidatos, constituir comissão, distribuir, avaliar na Mesa, consolidar, emitir ordem,
divulgar, avisar (com o timer), recorrer, admitir, indeferir, cortar, apurar, convocar, comunicar e
encerrar Edital e Processo: tudo pelo canal do ator, com segregação e trilha, cada passo em menos de
0,2 s. Os avisos: o deferimento com efeito é o P0 acima; uma Retificação homologada **é publicada
depois de o Edital ser encerrado**, contra o que a tela e a spec `103` afirmam; "partir de um
Edital anterior" **não copia a declaração do Requerimento de Matrícula** e nada avisa — a convocada
recebe 404 na matrícula; e o encerramento do Edital não confere pendências (recurso admitido sem
decisão, convocação sem desfecho).

**O que bloqueia o primeiro edital real não é só código.** A entrada institucional da gestão
continua sem provedor real (a gestão responde 503 em produção, como já se sabia); o caminho de
produção — gunicorn, nginx, systemd, backup, restauração — vive inteiro num guia de 3.162 linhas
e nada dele está versionado ou ensaiado além do que esta auditoria ensaiou localmente; a política
de retenção não existe; e três decisões institucionais pendentes mudam o que o código deve fazer
(o que "elaborou" quer dizer na segregação de funções; como o candidato distingue dois "Edital
01/2026" de unidades diferentes; se os avisos aos candidatos saem).

**Recomendação.** Corrigir os dois defeitos de banco e fechar a causa raiz com um guardião geral e
fluxos de fumaça sob a role de produção (dias, não semanas); medir o portal sob correio lento
antes de abrir inscrições; versionar o ensaio de restauração; e levar à coordenação as três
decisões acima. O plano mínimo está na seção F; os critérios objetivos de liberação, na G.

| Severidade | Novos | Dos quais em execução | Conhecidos confirmados |
|---|---|---|---|
| P0 | 1 | 1 (quatro reproduções independentes) | — |
| P1 | 2 | 2 | B-1, B-2 (institucionais) |
| P2 | 8 | 7 | CA-05, AUD-RET-05, AS-24, ED-06, AV-04 |
| P3 | 29 (alguns agrupam vários) | maioria | I-2…I-10, M-2…M-10 e outros (Anexo I) |

---

## A. Diagnóstico geral

**Riscos arquiteturais.** O GPS fez uma escolha correta e cara: as garantias moram no banco
(gatilho append-only, privilégio ausente, trava de linha, unicidade), e a aplicação é cliente
delas. O risco que essa escolha cria é o de **a suíte não exercitar o banco como produção o vê**:
o banco de teste é criado pelo superusuário, de modo que privilégio ausente e trava de linha nunca
falham em teste. Foi assim que a `106` encontrou um defeito na revogação, e é assim que o
julgamento de recurso carrega outro desde 07/09 (A-01). Toda garantia que depende de privilégio e
não de gatilho está, hoje, sem rede.

A segunda escolha correta foi congelar nas publicações tudo o que o documento oficial cita —
unidade, autoridade, conteúdo, renderizador — e derivar os atos posteriores da versão publicada.
Verificou-se que 35 módulos leem `effective_version` ou a `versao_aceita`, e nenhum ato posterior
lê o relacional atual (Anexo II). O risco que sobrou está **antes** da publicação: a Inscrição
enviada e a Avaliação concluída alimentam o resultado, o sorteio, a matrícula e os avisos, e só a
aplicação as protege (A-03).

A terceira é a identidade: a pessoa é o `auth_user` com identificador opaco, os papéis são
vínculos e a segregação compara identificadores estáveis. Isso resolve o que a demonstração não
resolvia. O que ficou são **três leituras divergentes do que a segregação impede** (código,
auditoria de 30/10 e spec), um catálogo de papéis que mora na interface e é lido pelo domínio, e a
comissão apontando para texto livre — nenhuma delas é defeito, todas pedem decisão ou pequeno
ajuste (A-17, A-18, A-24).

**Riscos operacionais.** Tudo o que é produção — servidor WSGI, estáticos, timers, backup,
restauração, página de manutenção, correlação pelo proxy — é prosa no guia e não está no
repositório nem em teste; o boot de produção nunca sobe contra banco de forma automatizada
(A-22, A-23). O envio de e-mail e a geração de PDF são síncronos, sem fila (A-04). A sessão
institucional de 30 minutos derruba um POST longo e perde o texto (A-05). E a documentação
envelhece mais depressa que o código: 109 commits na última semana; totais, comandos e direções
de dependência estão desatualizados em pontos que o operador lê como fato (A-27, A-28).

**O que está controlado.** A lista do Anexo II é longa e foi obtida por execução, não por leitura:
isolamento por escopo, append-only em duas camadas, concorrência dos fluxos críticos, rotação de
sessão, código de acesso, documentos oficiais servidos dos bytes gravados, barreiras de produção,
ausência de dado pessoal em logs (com uma exceção), ordem de provisionamento e restauração.

---

## B. Achados novos

Os achados estão numerados `A-NN` nesta seção e na matriz; o identificador da frente que os
encontrou (`INT-`, `SEG-`, `MU-`, `INF-`, `DAD-`, `ARQ-`, `OPE-`) aparece entre parênteses, e o
relatório de cada frente — com a evidência completa — fica no scratchpad desta sessão, não no
repositório. Aqui estão os P0, P1 e P2; os P3 estão no Anexo I.

### A-01 (P0) — O julgamento de recurso com efeito é recusado pela role de produção

- **Componente.** `recursos/application/julgar.py`, função `_protegido`; tabela
  `resultados_resultadoetapa`.
- **Evidência.** [F] `julgar.py:221` faz `ResultadoEtapa.vigentes.select_for_update(of=("self",))`
  para toda espécie em `COM_EFEITO` (`CORRECAO_FIXADA`, `REAVALIACAO_DETERMINADA`,
  `julgar.py:72-75`). [F] A tabela está em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`), e a
  política revoga `UPDATE, DELETE` dela para a runtime. [F] O PostgreSQL exige `UPDATE` para
  `FOR UPDATE`/`FOR SHARE`; o repositório conhece a regra (`avisos/application/despacho.py`, R-002
  da `066`; docstring de `tests/seguranca/test_privilegios.py`). [E] Como
  `processo_seletivo_runtime`, no banco de auditoria: `SELECT id FROM resultados_resultadoetapa
  LIMIT 1 FOR UPDATE` → `permission denied for table resultados_resultadoetapa`; o mesmo com `FOR
  SHARE` e `FOR KEY SHARE`. [E] Pelo ORM, em `manage.py shell` com `DB_ROLE=runtime`, a expressão
  exata de `_protegido` → `ProgrammingError`. [E] Teste descartável com o SQL gerado pelo ORM
  executado pela role de conformidade criada **pela política real** → `InsufficientPrivilege`.
  [E] Pela interface, com `django.test.Client` conectado como a role de runtime: `POST
  /gestao/recursos/<id>/julgar` com `CORRECAO_FIXADA` → **500**, `ProgrammingError: permission
  denied for table resultados_resultadoetapa`; `REAVALIACAO_DETERMINADA` → 500 idêntico;
  `INDEFERIDO` → 302. Reproduzido por três frentes e pela coordenação, por quatro caminhos.
- **Cenário de falha.** A julgadora defere um recurso com correção fixada ou reavaliação
  determinada na tela (`interface/views.py:10208` → `julgar`). Em produção a transação aborta;
  nenhuma camada trata `ProgrammingError` → erro genérico do servidor. Indeferimento e providência
  a jusante não passam por `_protegido` e funcionam.
- **Consequência.** Nenhum deferimento com efeito se consuma; o Resultado sucessor nunca nasce; a
  divulgação definitiva fica travada pelo recurso pendente. Acontece no meio do prazo recursal.
- **Probabilidade.** Certa, na primeira decisão com efeito, em qualquer implantação que siga o
  guia ou o compose. Não ocorre em desenvolvimento nativo se `DB_RUNTIME_USER` for o superusuário.
- **Cobertura existente.** 19 a 22 arquivos de teste chamam `julgar`, todos como superusuário. O
  ensaio operacional com a role de runtime deixou "recurso" de fora
  (`doc/roteiro-teste-operacional-assistido-28-2026.md:354-356`). O guardião AST da `106` varre só
  `processo_seletivo/seguranca`.
- **Correção mínima.** Remover a trava de linha de `_protegido`. O próprio docstring diz que "a
  unicidade ainda responde no banco, e é ela a garantia" (`uq_resultado_sucessor_unico`), e
  `julgar` já tranca o `ProcessoSeletivo` antes (`porta.py`). [E] Teste descartável com dois
  julgadores concorrentes: sob a trava do Processo, o resultado já é uma decisão e um `409
  stale_stage_result`. Zero migration, zero mudança de privilégio.
- **Alternativa.** Nenhuma segura: conceder `UPDATE` na tabela desfaz a segunda camada.
- **Dependências.** Nenhuma. **Spec própria?** Não; correção de defeito da `018`.
- **Critério de resolução.** (1) `julgar` com `CORRECAO_FIXADA` executado por conexão com a role
  de runtime grava decisão e sucessor; (2) guardião AST **geral**: todo `select_for_update`/`FOR
  UPDATE`/`FOR SHARE` cujo alvo esteja em `TABELAS_APPEND_ONLY` reprova, e o guardião tem teste
  que o vê reprovar quando a trava é reintroduzida.

### A-02 (P1) — Nenhum fluxo de aplicação é exercitado com os privilégios da role de produção

- **Componente.** Desenho da suíte (`backend/Makefile`, `tests/conftest.py`,
  `tests/integration/test_database_permissions.py`).
- **Evidência.** [F] O banco de teste é criado pelo superusuário; a única fixture que conecta como
  runtime (`runtime_connection`) é uma conexão `psycopg` à parte, usada em 7 arquivos para SQL
  direto — nunca para um comando ou view. [F] O que o gatilho não cobre e só o privilégio recusa:
  `FOR UPDATE`/`FOR SHARE` em append-only, `TRUNCATE`, `setval`, `DISABLE TRIGGER`, e qualquer
  tabela criada depois da segunda passada do provisionamento. [E] `has_table_privilege(…,
  'TRUNCATE')` falso nas 95 tabelas; `has_sequence_privilege(…, 'UPDATE')` falso nas 15 sequências.
  [F] O job `compose` do CI sobe com a role de runtime, mas só faz quatro `GET`s.
- **Cenário.** Qualquer comando novo que trave uma linha append-only ou escreva em tabela nova
  passa na suíte e falha em produção. Já produziu dois defeitos reais (a revogação da `106`, A-01).
- **Correção mínima.** Uma fixture que execute `SET ROLE <papel de conformidade>` na conexão de
  teste (o papel já é criado pela fixture existente com a política real; `SET ROLE` não exige nova
  conexão) e um conjunto pequeno de fluxos de fumaça por app sob ela: publicar Edital, consolidar,
  emitir ordem, julgar com efeito, convocar e registrar desfecho, conceder e revogar acesso,
  registrar unidade. Mais o guardião geral de A-01.
- **Dependências.** A-01 corrigido antes. **Spec própria?** Não.
- **Critério.** Fluxos de fumaça verdes sob `SET ROLE`; `test_database_permissions` continua verde.

### A-03 (P1) — Inscrição enviada, documento submetido, avaliação concluída e homologação só têm imutabilidade de aplicação

- **Componente.** `inscricoes/models.py` (`Inscricao.save`), `inscricoes_documentosubmetido`,
  `avaliacoes_avaliacao`, `publicacoes_homologacao`, `identidade_candidateemail`.
- **Evidência.** [F] `inscricoes/models.py:118-134`: `save()` recusa alterar `SUBMETIDA`, e a
  docstring diz que "não é garantia de banco". [F] O projeto já tem o padrão de gatilho
  condicional para a mesma família: `requerimentos/migrations/0002` (`WHEN (OLD.status =
  'ENVIADO')`) e `publicacoes/migrations/0007` (Retificação em estado final); a docstring da
  `0002` cita a Inscrição como o achado que a motivou. [E] Gatilhos existentes nas tabelas de dado
  pessoal: nenhum em `inscricoes_inscricao`, `inscricoes_documentosubmetido`,
  `identidade_candidateidentity`, `identidade_candidateemail`. [E] Como a role de produção, em
  transação desfeita, no banco semeado: `UPDATE inscricoes_inscricao SET nome=…, cpf='000…' WHERE
  status='SUBMETIDA'` → 12 linhas; devolver as 12 enviadas a `RASCUNHO` sem nome, CPF e e-mail →
  aceito; `DELETE FROM identidade_candidateemail` → 12; `UPDATE avaliacoes_avaliacao SET
  pontuacao = pontuacao + 10 WHERE estado='CONCLUIDA'` → 11; `UPDATE publicacoes_homologacao SET
  homologated_by='alguem'` → 4. Pelo ORM, `Inscricao.objects.filter(status="SUBMETIDA").update(…)`
  → 12; só `save()` recusa. Para contraste, `UPDATE auditoria_registroauditoria` → `permission
  denied`. [F] O gatilho de coerência do Resultado confere a Avaliação **só no INSERT**.
- **Cenário.** Um `QuerySet.update()` num comando de manutenção ou numa migration de dados
  futura (a `identidade/0002` já atuou sobre inscrições), um `psql` de operador, uma restauração
  parcial ou uma "correção rápida" altera nome, CPF, e-mail, Perfil, Modalidade ou status de
  inscrição enviada, ou a nota de avaliação concluída, sem trilha. Nome e CPF relacionais
  alimentam o resultado ao publicar (`divulgacao/domain/conteudo.py:87`), a relação do sorteio, o
  arquivo de matrícula, o aviso da `066` e o comprovante regenerado.
- **Consequência.** Para estas entidades, a reprodução histórica que a Constituição exige depende
  de uma camada só, enquanto para as 46 tabelas de ato depende de duas. A diferença não está
  registrada como decisão em lugar nenhum.
- **Probabilidade.** Baixa como ataque; real como erro operacional ou de migration.
- **Cobertura existente.** Nenhuma de banco: `test_database_permissions` e
  `test_imutabilidade_*` são parametrizados por listas que excluem estas tabelas.
- **Correção mínima.** Migration só de gatilhos, no molde exato da `requerimentos/0002`:
  `inscricoes_inscricao` com `WHEN (OLD.status = 'SUBMETIDA')` (a transição RASCUNHO→SUBMETIDA e
  o `reconhecer_versao` do rascunho travado passam); `inscricoes_documentosubmetido` consultando o
  status da inscrição; `avaliacoes_avaliacao` com `WHEN (OLD.estado = 'CONCLUIDA')` exceto a
  reabertura prevista pela `012`; `publicacoes_homologacao` append-only exceto as colunas de
  revogação. Para `identidade_*`, revogar `DELETE` da runtime em `candidateidentity` (não há caminho
  legítimo de exclusão) e registrar o resto como decisão. Os testes de imutabilidade existentes
  ganham as novas tabelas.
- **Alternativa.** Registrar em `papeis.py` a exclusão como decisão deliberada, com a razão.
- **Dependências.** Nenhuma. **Spec própria?** Pequena, sim: é o incremento que a `029` fez para o
  Requerimento, agora para a `009`/`012`/`003`.
- **Critério.** `UPDATE`/`DELETE` nas condições acima, como a role de runtime, recusados pelo
  gatilho; teste em PostgreSQL cobre cada tabela; o `M` do provisionamento não muda.

### A-04 (P2) — E-mail síncrono na requisição com workers síncronos: correio degradado no pico derruba o portal inteiro

- **Evidência.** [F] `portal/views.py:838` chama `enviar_codigo` dentro da view de acesso, sem
  fila; idem para o comprovante e a convocação. [F] `EMAIL_TIMEOUT = 20` é o único limite; o guia
  fixa gunicorn `sync`, 5 workers, `timeout 120`, nginx `proxy_read_timeout 130s`, e **não tem**
  `limit_req`. [E] Conexão SMTP a endereço que não responde, `timeout=20`: `TimeoutError` após
  20,0 s. [F] `scripts/carga_publica.py` mede só a API pública (I-8).
- **Cenário.** Último dia de inscrições, SMTP institucional lento ou fora. Cada POST em
  `/selecoes/acesso` ocupa um worker por até 20 s; com 5 workers o teto é 15 pedidos de código por
  minuto, e enquanto os 5 estão presos **nenhuma rota responde** — vitrine, inscrição em
  andamento, upload. O nginx devolve 504 após 130 s.
- **Consequência.** Indisponibilidade total do portal no período mais crítico, causada por serviço
  externo. Nenhum dado se perde. Já se sabia que o e-mail é o único fator do candidato (I-10); o
  novo é que a falha dele derruba o resto.
- **Probabilidade.** Depende de o SMTP degradar no pico; o pico é certo.
- **Cobertura.** Nenhuma de carga. **[I]** Os tetos são aritmética sobre o timeout medido e a
  configuração do guia; a carga real não foi medida.
- **Correção mínima.** (a) `limit_req` em `/selecoes/acesso` no nginx, abaixo da capacidade dos
  workers; (b) `EMAIL_TIMEOUT` menor só para o código de acesso (`get_connection(timeout=5)`);
  (c) estender `carga_publica.py` ao POST de acesso e medir contra homologação com um SMTP de
  teste lento, **antes** do primeiro edital.
- **Alternativa.** Uma fila mínima no banco, no molde de `avisos/application/despacho.py` — a
  correção estrutural, e spec própria.
- **Dependências.** Decisão sobre o SMTP institucional (I-10) e sobre `limit_req` atrás de NAT.
- **Critério.** Medição registrada: com SMTP respondendo em 20 s a 100% dos envios, `/selecoes/`
  continua respondendo em < 2 s (p95) sob N pedidos de código por minuto, N definido pela
  instituição.

### A-05 (P2) — POST na gestão com a sessão institucional vencida é redirecionado e o ato se perde

- **Evidência.** [F] `interface/identidade.py:323-333`: a sessão vence em 30 min de inatividade
  ou 8 h. [F] `pedir_identificacao` (`:610-626`) leva `proximo` **só em GET**; um POST volta a
  `identificar` sem destino e sem corpo. [F] O cabeçalho `Requisicao-Automatica` existe "para a
  primeira sondagem que vier" — não há sondagem nem aviso no cliente. [E] Teste descartável:
  POST com sessão válida → 422 (formulário conferido); relógio avançado 31 min; o mesmo POST →
  302 para `/gestao/identificar`, sem `proximo`; trilha grava `SAIDA` com motivo `inatividade`.
- **Cenário.** Parecer da Mesa, motivação de julgamento ou etapa Perfis (centenas de campos)
  redigidos por mais de 30 min sem outra requisição à gestão: digitar não conta como atividade. A
  pessoa envia e perde o texto; a página de acesso diz "sessão encerrada por inatividade".
- **Consequência.** Retrabalho; na Mesa e no julgamento, decisão redigida duas vezes. Nenhuma
  exposição.
- **Probabilidade.** Alta no primeiro edital real; só no modo institucional.
- **Cobertura.** `tests/seguranca/test_sessao_com_prazo.py` cobre GET; nenhum caso cobre POST.
- **Correção mínima.** (a) Aviso no cliente ~2 min antes do vencimento, com sondagem que não
  renova (o cabeçalho já existe); (b) na recusa de POST por prazo, guardar o corpo em chave
  efêmera e reapresentar o formulário preenchido após a nova entrada — nunca reexecutar o ato.
- **Alternativa provisória.** Elevar `GESTAO_SESSAO_INATIVIDADE_MINUTOS` em produção, o que é a
  decisão P4 da `107`, a registrar e não a tomar aqui.
- **Spec própria?** Sim, pequena (ajuste de UX da `107`).
- **Critério.** Teste em que o POST após o prazo devolve a pessoa ao mesmo formulário com o
  conteúdo preservado, ou aviso antes do vencimento verificado em navegador.

### A-06 (P2) — O candidato com inscrições em duas unidades não distingue dois "Edital 01/2026"

- **Evidência.** [E] Dois Editais publicados com o mesmo número, ano e `institutionalCode` em
  `cefor` e `campus-a` — o banco aceita, porque as unicidades são por escopo
  (`processos/models.py:25-27,119-121`). A candidata se inscreve nos dois. `GET
  /selecoes/inscricoes/` lista duas entradas idênticas ("Processo Seletivo 2026 · Edital 01/2026"),
  sem sigla; a página de cada inscrição tem título "Sua inscrição — Ifes" e nenhuma unidade. [F]
  `portal/views.py:1277-1300` e `portal/inscricoes.html:25`; a moldura com duas ativas é "Ifes"
  (`unidades/application/identificacao.py:93-104`). O resultado público e a relação do sorteio têm
  o mesmo problema. [F] A `versao-vigente` pública também não traz a unidade (só
  `publicacoes/<id>`).
- **Cenário.** Campi numeram Editais de forma independente, por desenho. A candidata abre a
  inscrição errada, recorre do resultado errado ou lê a convocação errada.
- **Probabilidade.** Nula com só o Cefor ativo; alta com dois campi.
- **Cobertura.** Nenhuma com dois escopos na área do candidato.
- **Correção mínima.** A sigla da unidade do ato (`versao_aceita.source_publication.unidade_sigla`,
  como a página da seleção já faz) na lista e nos cabeçalhos de inscrição, acompanhamento,
  convocação e recurso; `unit` na `VersaoConsolidadaSerializer`. Uma consulta a mais, no máximo.
- **Dependências.** É a resposta que a **P-7** da `109` adiou ("o conteúdo já diz o Edital"); a
  execução mostra que não diz o suficiente. **Spec própria?** Não; emenda da `109`/`072`.
- **Critério.** Teste com dois Editais de mesmo número em unidades distintas em que a lista e a
  página da inscrição contêm a sigla de cada um.

### A-07 (P2) — Abrir o dossiê do candidato com o Requerimento de Matrícula integral não gera evento na trilha

- **Evidência.** [F] `interface/views.py:5729-5734`: `inscricao_recebida` chama
  `inscricao_para_consulta` e renderiza; nenhum `record_event`; `inscricoes/application/consulta.py`
  não grava evento. [F] O dossiê carrega o Requerimento inteiro sob a mesma permissão
  (`consulta.py:470-480` → `requerimentos/application/selectors.py:91-131`): data de nascimento,
  filiação, RG, **cor/raça**, **necessidade específica**, renda, endereço. [F] O download do
  documento **é** registrado (`views.py:5767-5788`), com a justificativa "acesso a dado sensível
  deixa rastro"; a prévia da exportação também é. [E] Trilha com 106 eventos antes e depois de
  `inscricao_para_consulta` como gestor.
- **Cenário.** Pedido do titular ou do encarregado — "quem leu meus dados de matrícula?" — sem
  resposta; acesso indevido por alguém com o papel Gestor indetectável.
- **Consequência.** Lacuna de rastreabilidade sobre o conjunto mais sensível lido tela a tela.
  Não está entre as quatro lacunas de I-7.
- **Correção mínima.** `record_event CONSULTAR_DOSSIE` em `inscricao_recebida` (e na Mesa, se
  exibir o Requerimento), no molde de `_registrar_consulta`; rotular em `OPERACOES` e em
  `relatorio_trilha.py`. Alternativa: registrar só quando há bloco do Requerimento.
- **Spec própria?** Não; cabe como emenda da `029` ou junto do fechamento de I-7.
- **Critério.** Abrir o dossiê de uma inscrição com Requerimento enviado produz exatamente um
  `RegistroAuditoria`; teste de integração o exige.

### A-08 (P2) — Pendências conhecidas que esta auditoria reavalia para cima ou precisa pôr em evidência

Não são achados novos; estão aqui porque o relatório de prontidão não pode tratá-los como
rodapé.

- **CA-05 — `AVISOS_AOS_CANDIDATOS` sem trava em produção.** [F] `config/settings/production.py`
  não a menciona; uma variável liga os avisos sem a validação de LGPD que a `D-009` da `066` exige.
  Confirmada aberta pela coordenação. É de uma linha e deveria entrar com as correções da seção F.
- **AUD-RET-05 — "elaborou" é quem submete.** [F] `publish_edital.py:508` grava `prepared_by` na
  submissão; a recusa (`:705`) só bloqueia `prepared_by == homologated_by == publicador`; homologar
  a própria revisão é permitido; A redige, B submete, A homologa e A publica passa. [F] A
  auditoria de 30/10 afirma que "a regra impede que a mesma pessoa elabore e homologue o próprio
  ato" — não é o que o código faz. [F] A emenda à FR-021 está reservada e sem decisão. Com uma
  equipe de duas ou três pessoas acumulando papéis, o caso "submete e homologa, outra publica" será
  a rotina. **Decisão institucional**, e a frase do doc de 30/10 precisa de correção.
- **AS-24 — Fonte da Caixa sem contrato e sem E2E periódico.** [F] O parser é testado só com JSON
  escrito à mão; o E2E real está atrás de `SORTEIO_E2E_FONTE_REAL` e ninguém o agenda. Confirmado
  aberto; a correção mínima sem rede é gravar uma resposta real como fixture.
- **ED-06 e AV-04 (P1 na matriz de 15/10)** — "Edital completo" que pode não conter Retificação
  vigente; reabilitação antes do marco não alcança o corte. Confirmados abertos sem decisão.

### A-09 (P2) — Retificação homologada é publicada depois de o Edital ser encerrado

- **Componente.** `publicacoes/application/retificacoes.py` (`publish_retification`,
  `transition_retification`); `processos/domain/finalizacao.py`.
- **Evidência.** [F] `retificacoes.py:74` e `:398` conferem só `ensure_processo_accepts_changes`;
  `ensure_edital_accepts_changes` (`finalizacao.py:98-100`) existe e **não é chamado** em nenhum
  ato da Retificação — só `create_retification` exige Edital `PUBLICADO`. [F] A tela de encerrar
  promete o contrário (`interface/atos.py:129`: "Nenhuma Retificação poderá ser publicada depois
  disso"), e a spec `103` (linhas 250-251) afirma que os atos são recusados pelo servidor. [E] Na
  jornada: Edital 80/2026 encerrado às 17:43 → `POST /retificacoes/<r3>/atos/publicar` → **302**;
  detalhe: "Retificação nº 3 publicado em 31/10/2026 17:43"; o portal mostra "Edital encerrado"
  com versão vigente nova. Confirmado por leitura pela coordenação.
- **Cenário.** Retificação em curso quando o gestor encerra o Edital: quem publica ainda pode
  publicá-la; o Edital em estado final ganha versão normativa nova.
- **Consequência.** Estado final que não é final; a trilha diz o contrário do que a tela prometeu.
- **Cobertura.** `tests/interface/test_jornada_da_retificacao.py` cobre Retificação encerrada,
  não Edital encerrado.
- **Correção mínima.** `publish_retification` e `transition_retification` chamarem
  `ensure_edital_accepts_changes(item.edital)`; teste de integração. **Spec própria?** Não — é a
  FR já escrita na `103`.
- **Critério.** Publicar ou transitar Retificação de Edital `ENCERRADO`/`CANCELADO` responde 409.

### A-10 (P2) — "Partir de um Edital anterior" não traz a Identificação, e nada avisa

- **Componente.** `editais/application/reaproveitamento.py`; tela `reaproveitar.html`.
- **Evidência.** [F] `reaproveitamento.py:334-347`: o comando chama `replace_draft` com perfis,
  cronograma, etapas, seções, documentos exigidos e método de sorteio; descrição, teto e
  `matriculationRequest` têm comandos próprios e **não viajam**. Confirmado por leitura pela
  coordenação. [E] O 51/2026 declara `matriculationRequest = {moment: AT_CALL, …}`; o 80/2026,
  criado a partir dele, publicou `matriculationRequest = None` e descrição vazia. [E] A tela "O
  que não vem" não menciona a Identificação; a validação avisou só "O Edital não possui descrição"
  e o Edital foi publicável. [E] Consequências: a convocada abre `/requerimento` → **404**
  (`exigido=False`); a exportadora vê "Nenhum ato disponível" e, por URL, "Ver o que sairá vazio".
  [F] O `moment` do Requerimento não é retificável ("não se corrige por Retificação").
- **Cenário.** O caso de uso central da `023`: partir do Edital do ano anterior, publicar,
  convocar — e descobrir na matrícula que ninguém pode preencher o Requerimento, sem caminho de
  correção além de um Edital novo.
- **Probabilidade.** Alta: é o fluxo recomendado pelo roteiro de teste.
- **Cobertura.** `tests/acceptance/test_quickstart.py` (`023`) cobre coleções; nenhum teste afirma
  que `matriculationRequest` viaja ou que a tela avisa.
- **Correção mínima.** (a) copiar também descrição, teto e `matriculationRequest` (os comandos
  existem), ou (b) a tela listar "não vem: descrição, teto, Requerimento de Matrícula" e a
  validação advertir quando algum Perfil convoca e o Edital não declara Requerimento enquanto a
  origem o declarava. **Spec própria?** Não (emenda à `023`/`029`).
- **Critério.** Teste de reaproveitamento comparando `matriculationRequest`, descrição e teto da
  origem e do destino, ou o aviso na tela e na validação.

### A-11 (P2) — Encerrar o Edital não confere nem lista pendências operacionais

- **Evidência.** [F] `processos/domain/finalizacao.py:75-80` (`ensure_edital_can_be_closed`): só
  estado. [E] Edital 80/2026 encerrado com um recurso **admitido e sem decisão**, uma convocação
  comunicada **sem desfecho** e uma Retificação **homologada** aguardando publicação; a tela só
  mostrou as três consequências fixas e pediu o motivo. [E] Depois de encerrado, julgar continua
  aceito e a Retificação foi publicada (A-09). Contraste [E]: o Processo lista "Estes Editais
  precisam ser encerrados ou cancelados antes".
- **Consequência.** Encerramento precoce deixa recurso e convocação em curso num Edital que a
  interface considera concluído; `pode_retificar` recusa Retificação nova, mas as pendências
  continuam operáveis.
- **Cobertura.** `tests/acceptance/test_us7_finalizacao.py` cobre estado; nada sobre pendências.
- **Correção mínima.** A tela de confirmação listar recursos aguardando decisão
  (`acoes.recursos_aguardando_decisao` já existe), convocações sem desfecho, Retificações em curso
  e inscrições em preenchimento; decidir com o usuário quais viram recusa do domínio.
  **Spec própria?** Sim, curta.
- **Critério.** A confirmação de encerramento lista as pendências; as que a decisão tornar
  impeditivas respondem 409.

### A-12 (P2) — O teto de 30 códigos por hora por origem bloqueia um laboratório inteiro em silêncio

- **Evidência.** [F] `identidade/application/desafio.py:36-42` (`LIMITE_POR_ORIGEM = 30`/h; o
  comentário reconhece que laboratório e telecentro compartilham origem); `:127-130` no teto, "o
  recibo continua o mesmo" e nenhum código é gerado. [F] `portal/views.py:845-866`: a frase é a
  mesma da espera por endereço ("peça de novo em 60 s"). [E] Reproduzido o caso irmão (segundo
  pedido para o mesmo e-mail → 302, zero e-mails, "daqui a 15 segundos"); para o teto por origem a
  mensagem é a mesma [F] e o bloqueio dura até esvaziar a janela de uma hora. Sem evento, métrica
  ou tela para "origem no teto".
- **Cenário.** Polo EaD ou laboratório com 40 candidatos atrás de um NAT no último dia (o 26/2026
  da demonstração tem 40 vagas num polo). Do 31º pedido em diante ninguém daquele IP recebe
  código; cada um lê "espere 60 s", repete e conclui que o e-mail não chega.
- **Consequência.** Inscrições perdidas no prazo, sem rastro; indistinguível de SMTP caído (I-10).
- **Cobertura.** `tests/integration/identidade/test_limites.py` cobre que o teto para de gerar
  código; nada sobre a mensagem nem a observabilidade.
- **Correção mínima.** Distinguir no recibo "espera do endereço" de "origem no teto" e, neste,
  dizer que a rede atingiu o limite por uma hora (outra rede ou o atendimento); log estruturado
  quando uma origem bate o teto. **Alternativa provisória.** Teto configurável por variável para o
  dia de pico; orientar os polos. **Spec própria?** Não (emenda à `010`).
- **Critério.** Teste que leva uma origem ao teto e afirma a frase correta; evento no log.

---

## C. Pendências conhecidas — abertas, resolvidas, a reavaliar

Conferidas uma a uma contra a `main` em `4ca16b1d`. As fontes são o §26 do guia de implantação,
a auditoria institucional de 30/10 e suas pendências de 31/10, a revisão multiunidade de 30/10, a
matriz de 15/10 e os `doc/achado-*.md`.

| Pendência | Situação em 31/10 | Observação desta auditoria |
|---|---|---|
| B-1 gestão sem autenticação de produção | **aberta em parte** | arquitetura da `106`/`107` pronta; provedor real não existe; `/gestao/identificar` responde 503 sob produção [E]; o seletor de demonstração continua sem `cycle_key` (só fora de produção) [E] |
| B-2 política de retenção | **aberta** | esta auditoria acrescenta o inventário técnico que a política precisa cobrir (Anexo I, A-31 e A-32): tabelas irremovíveis por construção, identidades sem inscrição, rascunhos de Requerimento, `IdempotencyRecord` |
| I-1 API admin sem classe institucional | **aberta**; paliativo seguro | `RemoteUserAuthentication` nega tudo [E]; a API admin não tem consumidor real fora da suíte e do `seed_demo` [F] |
| I-2 gunicorn fora do lock | **aberta** | `gunicorn==26.2.0` existe e é a última; instalado sem hash [E] |
| I-3 sem `STATIC_ROOT` | **aberta** | `/static/*` → 404 sob produção sem nginx [E] |
| I-4 `EMAIL_TIMEOUT`/`EMAIL_USE_SSL` | **meio resolvida** | timeout presente; `EMAIL_USE_SSL` ausente |
| I-5 sessões sem limpeza; `Sair` do portal sem `flush` | **aberta** | `SESSION_COOKIE_AGE=1209600` [E]; ver A-14 |
| I-6 HSTS com subdomínios e preload | **aberta** | padrão `true`; o guia manda `false` |
| I-7 lacunas da trilha (quatro) | **aberta** nas quatro | A-07 e A-34 são lacunas **além** delas |
| I-8 SLO de carga não medido | **aberta** | A-04 quantifica o efeito colateral |
| I-9 `SECRET_KEY` como segredo dos comprovantes | **aberta** | só `inscricoes/domain/autenticidade.py:61`; códigos de acesso não dependem dela |
| I-10 e-mail único fator | **aberta** | inclui reciclagem de endereço (credencial verificada entra sem CPF, deliberado) |
| M-1 CSP | **resolvida** (`091`/`092`) | em recusa em todo HTML [E] |
| M-2 sem `500.html` | **aberta** | o 400 também é a página inglesa do Django [E] (A-25) |
| M-3, M-4, M-5, M-6, M-7, M-9, M-10 | **abertas** | leitura |
| M-8 `DJANGO_DEBUG` | **resolvida** no `.env.example` | |
| M-06 (30/10) identificador da comissão é texto livre | **aberta** | consequência medida em A-24 |
| M-07 segregação por pessoa | **resolvida em parte**; **reavaliar** | o doc de 30/10 descreve a regra mais estrita do que ela é (A-08) |
| M-09 / J-1 registrar unidade | **resolvida** (`110`) | a tabela de 31/10 ainda a dá como aberta |
| M-10 renomear unidade sem afetar o publicado | **resolvida em parte**; **reavaliar** | o sub da página da seleção lê o código, não a sigla (A-19) |
| M-11 / P-1 marca com duas ativas = "Ifes" | **aberta**, provisória | [E] vitrine e portal dizem "Ifes" com duas ativas |
| M-17 identidade institucional no código | **resolvida em parte** | sigla da unidade do registro; "Ifes" em constante por decisão |
| M-18 / M-19 diagnóstico de correio | **abertas** | o journal tem a falha com traceback; sem alerta nem tela |
| M-25 / Q-7 retenção; `auth_user` com nome e e-mail | **aberta** | consequência nova: descartar essas linhas devolve `pessoa-<uuid>` nas telas de trilha; o PDF não é afetado |
| M-26 `seed_demo` em produção | **resolvida** (#343) | recusa por marca, não por banco (limite conhecido) |
| P-7 da `109` (moldura da implantação na área do candidato) | **reavaliar** | insuficiente com numeração coincidente (A-06) |
| P1 da `108` (quem audita o institucional) | **aberta** | |
| §5.1 da revisão multiunidade (escopo mutável por `update()`) | **resolvida** (`110`) | gatilhos `processo_escopo_imutavel` e `edital_escopo_imutavel` [F] |
| CA-05 `AVISOS_AOS_CANDIDATOS` sem trava | **aberta** | A-08 |
| AS-24 fonte da Caixa | **aberta** | A-08 |
| ED-06, AV-04, CA-23 (P1 em 15/10) | **abertas**, sem decisão | texto do reenvio da convocação inalterado |
| AUD-RET-05 "elaborou" = submeteu | **aberta** | A-08 |
| DP-07 (três recusas em 403) | **decidida (28/09) e não implementada** | merece linha na próxima consolidação |
| `decisao-sc273-estreitada` | **decidida e não executada** | a spec `045` mantém a SC-273 original |
| `achado-valor-de-fato-sem-gatilho` | **resolvido** | gatilho presente [E] |
| `achado-release-sem-o-grupo-do-assistente` | **aberto** | `ps-construir` sem `--extra assistente` |
| `achado-reservada-vazia-nao-reverte` | **aberto, sem decisão** | |
| Passo 0 da `110` na VM; T051 humano | **abertos** | a tela da `110` depende do provedor real fora da suíte [E] |

Dos 47 `doc/achado-*.md`: 27 resolvidos ou superados, 5 abertos com decisão registrada, cerca de
18 abertos sem decisão — os quatro de maior peso são ED-06, AV-04, CA-23 e AS-24. Das DP-01 a
DP-21: 12 decididas e implementadas; DP-07 decidida e não implementada; DP-08 (itens 1 e 3), 09,
10, 11, 12, 15, 18 e 20 (itens 4 e 5) pendentes.

---

## D. Riscos sistêmicos — o que compartilha causa raiz

1. **A suíte não vê o que só o privilégio recusa.** Superusuário no banco de teste → A-01, A-02,
   o defeito da `106` e a janela de A-20. Uma causa, dois defeitos reais, um guardião local.
2. **Imutabilidade em uma camada só para o que o candidato declara.** O padrão de duas camadas
   vale para os atos e para o Requerimento; não para a Inscrição, o documento, a Avaliação e a
   Homologação → A-03; e o inventário do que é irremovível (A-31) mostra o outro lado da mesma
   escolha, onde a eliminação é impossível por construção.
3. **A produção vive num guia, não no repositório.** Servidor WSGI, estáticos, units, timers,
   backup, restauração, página de manutenção e correlação pelo proxy são prosa → I-2, I-3, A-22,
   A-23, A-26, A-27, A-28, A-30. O boot de produção nunca sobe contra banco de forma
   automatizada; o ensaio de restauração não tem registro.
4. **Síncrono na requisição, sem fila.** E-mail e PDF dentro do worker → A-04, I-10, e os atos
   pesados sob os 120 s do gunicorn.
5. **A identidade do operador é texto nos atos e o catálogo de papéis mora na interface.**
   Segregação por submissor, comissão por texto livre, três catálogos reconciliados em tempo de
   execução → A-08 (AUD-RET-05), A-17, A-18, A-24.
6. **As superfícies públicas assumem uma unidade.** A resposta provisória da `109` (P-7) fica
   insuficiente assim que dois campi numeram Editais → A-06, A-19, A-21.
7. **A trilha registra o ato e não a leitura.** Dossiê e arquivo de exportação sem evento, ao
   lado de download e prévia com evento → A-07, A-34, I-7.
8. **O estado final do Edital só é conferido no Processo.** Encerrar não lista pendências e a
   Retificação não confere o Edital → A-09, A-11; e o reaproveitamento copia coleções sem a
   Identificação → A-10. Três lacunas na mesma costura entre `processos`, `publicacoes` e `editais`.
9. **A documentação envelhece mais depressa que o código.** 109 commits em sete dias; totais,
   comandos e direções de dependência desatualizados em pontos que o operador lê como fato →
   A-27, A-28, M-09 ainda "aberta" na tabela de 31/10, a frase da segregação no doc de 30/10.

---

## E. Prontidão para o primeiro edital real

**Bloqueadores técnicos** (código; impedem ou comprometem a operação; correção pequena):

- A-01 — remover a trava de linha em `julgar` e instalar o guardião geral de travas.
- A-03 — gatilhos condicionais na Inscrição enviada, no documento submetido, na Avaliação
  concluída e na Homologação (ou decisão escrita de não os ter).
- A-02 — fluxos de fumaça sob `SET ROLE` da role de produção, para que a classe de A-01 não volte.
- CA-05 — trava de `AVISOS_AOS_CANDIDATOS` em `production.py` enquanto a LGPD não validar.
- A-09 — a Retificação conferir o estado do Edital (uma chamada que já existe).
- A-10 — o reaproveitamento copiar a Identificação, ou a tela e a validação avisarem.
- A-12 — a mensagem e o registro do teto por origem, antes de abrir inscrições com polos.

**Bloqueadores de configuração e infraestrutura** (não são código, mas sem eles não há produção):

- Provedor institucional real (B-1): adaptador OIDC ou SAML, decisão 1 do roteiro de ativação; até
  lá a gestão responde 503.
- Correio institucional com redundância e monitorado (I-10) **e** medição de A-04 com `limit_req`
  no proxy antes de abrir inscrições.
- Versionar o que hoje é prosa: gunicorn no lock (I-2), `STATIC_ROOT`/`collectstatic` (I-3) ou o
  `alias` do nginx como arquivo, units e timers (`despachar_avisos`, `clearsessions`,
  `limpar_terminais`, CEP), script de backup e **ensaio de restauração com registro datado** (A-26).
- Passo 0 da `110` (ampliação do papel institucional) e a concessão dos dois administradores
  institucionais designados por ato formal.
- Correção do guia (A-27): totais, comandos da `106`/`107`, `ASSISTENTE_NA_PAGINA_DO_EDITAL` na
  lista de proibidas, `proxy_hide_header Server`, control socket do gunicorn.

**Decisões institucionais pendentes** (mudam o que o código deve fazer; registrar, não tomar):

1. O que "elaborou" significa na FR-021 — submeteu ou compôs (AUD-RET-05 / emenda D-8). Com duas
   ou três pessoas acumulando papéis, define se a segregação existe na prática.
2. Provedor e protocolo do SSO (Q-2), e o portão do diretório (decisão 6 do roteiro).
3. Política de retenção e descarte (B-2), agora com o inventário do que é irremovível (A-31) e
   aviso de privacidade no portal (A-33).
4. Identificação da unidade nas superfícies do candidato quando houver mais de uma ativa (P-1,
   P-7; A-06) — e se o segundo campus entra antes ou depois do primeiro edital real (Q-9).
5. Se os avisos complementares aos candidatos saem no primeiro edital (`D-009` da `066`), e com
   que validação.
6. Prazo de inatividade da sessão (P4 da `107`) diante de atos longos (A-05), ou aviso prévio.
7. ED-06, AV-04 e CA-23, P1 desde 15/10 e ainda sem decisão.
8. O que o encerramento do Edital deve impedir (A-11), e se existe recebimento individual fora
   do prazo — inscrição ou recurso por falha alegada do sistema — e correção de CPF congelado
   (A-40): hoje só há o caminho coletivo, a Retificação do prazo, que funciona [E].

**Pendências que podem continuar no backlog** sem comprometer o primeiro edital: os P3 do Anexo I
(logs de segurança, `connect_timeout`, `400.html`, `CHECK` de status, catálogo de papéis,
comentários de `INSTALLED_APPS`, `origem_hash` com sal, `X-Correlation-ID`, tamanho de
`views.py`), M-3 a M-10, e as questões multiunidade que só se materializam com o segundo campus.

### A jornada do edital, etapa a etapa

Refeita pela interface (gestão e portal) com `django.test.Client` sobre as views reais, conectado
como a role de runtime, alternando identidades pelo seletor de demonstração; nenhum shell, nenhum
command. Processo `PS-AUD-D-2026`, Edital 80/2026 criado a partir do 51/2026, publicado às 11:28,
retificado duas vezes, três inscrições, comissão de três, Mesa, consolidação, ordem, resultado
preliminar, aviso despachado (dois e-mails), dois recursos, corte, apuração, convocação
comunicada, Edital e Processo encerrados.

| # | Etapa | Ator | Canal | Pré-condição escondida ou risco |
|---|---|---|---|---|
| 0 | Registrar unidade; primeira administração institucional | TI | shell, uma vez por instalação | conhecidos (J-1, J-7); depois tudo é interface |
| 1 | Cadastrar autoridades com nome e portaria | Gestor | interface | **nada avisa antes da tela de publicar**; sem nome, o PDF sai só com o cargo [E] |
| 2 | Criar Processo e primeiro Edital | Gestor | interface | nenhuma |
| 3 | Compor ou partir de Edital anterior | Elaborador | interface | Gestor não compõe (acúmulo de papéis); **a Identificação não vem** (A-10) |
| 4 | Submeter → homologar → publicar | três papéis | interface | três pessoas ou três sessões; publicação síncrona em 0,10 s, PDF de 80 KB |
| 5 | Inscrição | Candidato | portal | segundo clique em "Inscrever-se" depois de "Seus dados" (conhecido); teto por IP (A-12) |
| 6 | Comissão e alocação | Gestor | interface do Processo | o Edital publicado não aponta para elas (A-39); identificador é o `subject` exato do provedor, texto da tela desatualizado |
| 7 | Distribuir | Gestor ou presidência | Supervisão → distribuição | recusa com orientação enquanto as inscrições correm; a Supervisão alerta cedo demais |
| 8 | Avaliar | Membro | Mesa | — |
| 9 | Consolidar | Presidência | distribuição | eliminado na Etapa anterior "não participa" (correto) |
| 10 | Emitir ordem | Presidência | marco | **emite ato vazio** se uma Etapa enumerada não está consolidada (A-38) |
| 11 | Divulgar resultado | Publicador | detalhe → prévia | 403 na página do ato, 200 na prévia (incoerente, funciona) |
| 12 | Avisar candidatos | Publicador ou Gestor | tela + timer | zero e-mails no clique; produção com a chave desligada |
| 13 | Recurso → admitir → julgar | Candidato → Julgador | portal → interface | **julgar com efeito → 500** (A-01); indeferir funciona; fora do prazo, sem caminho |
| 14 | Corte → apuração → convocar → comunicar | Presidência | condução | ordem rígida avisada ("Feito/Falta"); e-mail síncrono no clique |
| 15 | Requerimento de Matrícula | Candidato | portal | **404** quando o Edital não declarou o Requerimento (A-10); CEP ausente não bloqueia |
| 16 | Exportar matrículas | Exportador | interface | ação só aparece com Requerimento declarado |
| 17 | Encerrar Edital e Processo | Gestor | interface | **sem conferência de pendências** no Edital (A-11); Retificação publicável depois (A-09); o Processo confere os Editais |

**Doze transições difíceis, e o caminho de cada uma** [E]/[F]: (a) cronograma publicado com erro —
Retificação em três atos, reproduzida em ~1 min; (b) inscrição encerrada e candidato alega falha —
só o caminho coletivo; (c) homologadora de férias — qualquer pessoa com o papel homologa ou
devolve; unidade com uma só é beco até o administrador de acessos conceder o papel; (d)
autoridade mudou — cadastro e a tela de publicar listam as vigentes; (e) Caixa sem extração —
regra de substituição declarada, senão Retificação e relação nova (A-41); (f) convocação ao e-mail
errado — destino é o principal verificado, o candidato troca no portal, a gestão não; (g)
resultado com erro — reabrir, consolidar, suceder e publicar, sem reabrir prazo; se a correção
vier por recurso com efeito, cai em A-01; (h) recurso fora do prazo — sem caminho; (i) CPF
congelado errado — sem caminho, nem por shell; (j) código não chega — reenvio após 60 s e tetos
(A-12); (k) cancelar após inscrições — existe, sem aviso automático aos inscritos; (l) encerrar
Processo com pendências — guarda só dos Editais.

**Tempos medidos na escala da demonstração** (dois Perfis por Edital): publicação com PDF 0,10 s
(80 KB); relatório do Edital em PDF 0,06 s (148 KB); relatório consolidado 0,03 s; documento do
resultado e comprovante abaixo de 0,03 s. Nada se aproxima dos 120 s do servidor de aplicação
nessa escala; o Edital multicampi da `051` (66 Perfis) não foi medido em tempo — só em número de
campos (13.000).

**Pré-condições que a interface não avisa antes da hora:** autoridade com nome e portaria;
Gestor e Elaborador na mesma pessoa para criar e compor; a Identificação não vem do Edital
anterior; comissão com presidência antes de alocar; identificador do membro igual ao do provedor;
todas as Etapas enumeradas consolidadas antes de emitir; `AVISOS_AOS_CANDIDATOS` ligado e o timer
ativo; o teto de códigos por rede.

---

## F. Plano mínimo de saneamento

Agrupado por causa raiz e dependência. Não é uma spec: a maioria dos itens cabe em PRs de
correção com teste; os que pedem spec estão marcados.

**Grupo 1 — Privilégio da role de produção (dias).** Ordem obrigatória.

1. A-01: remover `select_for_update` de `_protegido`; traduzir `IntegrityError` da unicidade em
   `stale_stage_result`; teste de corrida já existe (B1 descartável serve de modelo).
2. Guardião geral de travas × `TABELAS_APPEND_ONLY` (generalizar
   `tests/seguranca/test_privilegios.py` para `processo_seletivo/**`), com teste do guardião.
3. A-02: fixture `SET ROLE` e sete fluxos de fumaça (publicar, consolidar, emitir ordem, julgar
   com efeito, convocar e registrar desfecho, conceder e revogar, registrar unidade).
4. A-20 (opcional, mesmo PR): `ALTER DEFAULT PRIVILEGES` sem `UPDATE, DELETE` e concessão
   explícita às mutáveis; conferência de `tgenabled` na `CONSULTA_DE_CONFERENCIA` (A-29).

**Grupo 2 — Duas camadas para o que o candidato declara (spec pequena).**

5. A-03: migration só de gatilhos (Inscrição, documento, Avaliação, Homologação) + revogar
   `DELETE` em `identidade_candidateidentity`; testes de imutabilidade ganham as tabelas. Se a
   decisão for não fazer, registrar em `papeis.py`.

**Grupo 3 — Portal sob correio degradado (medição + procedimento; fila é spec).**

6. A-04: `limit_req` no nginx do guia; `EMAIL_TIMEOUT` curto para o código; `carga_publica.py`
   estendido ao POST de acesso; medir em homologação com SMTP lento e registrar.
7. A-14: `flush()` no `Sair` do portal; `SESSION_COOKIE_AGE` explícito (I-5).
8. A-15: `logger.error` sem traceback nos três pontos de falha de envio.

**Grupo 4 — Sessão institucional e atos longos (spec pequena de UX da 107).**

9. A-05: sondagem com `Requisicao-Automatica` e aviso antes do vencimento; preservação do corpo.

**Grupo 5 — Trilha de leitura e exportação (emenda da 029 / fechamento de I-7).**

10. A-07: `CONSULTAR_DOSSIE`; A-34: `GeracaoDeArquivo` na trilha da condução.

**Grupo 6 — Produção versionada (procedimento, sem spec).**

11. I-2 (extra `prod` no `pyproject.toml`), I-3, `400.html` e `500.html` (A-25, M-2), `connect_timeout`
    (A-23), `django.security` no `LOGGING` (A-22), `proxy_hide_header Server`, control socket do
    gunicorn (A-30).
12. A-26: `scripts/ensaio_de_restauracao.sh` (dump → createdb → provisionar → restore →
    provisionar → `migrate --check` → conferências) e registro datado em homologação.
13. A-27: atualizar o guia (totais, §11.4, comandos da `106`/`107`, lista de proibidas) e um
    guardião que compare o `M` do guia com `len(TABELAS_APPEND_ONLY)`.
14. CA-05: trava de `AVISOS_AOS_CANDIDATOS` em `production.py`.

**Grupo 7 — Multiunidade no portal (emenda da 109/072; só se o segundo campus entrar).**

15. A-06, A-19, A-21: sigla do ato na lista e nas páginas do candidato, no sub da seleção e na
    `versao-vigente`; o índice da API sem cancelados (A-16).

**Grupo 8 — Costura do estado final e do reaproveitamento (correções com teste; A-11 é spec curta).**

16. A-09: `ensure_edital_accepts_changes` em `publish_retification` e `transition_retification`.
17. A-10: o reaproveitamento copiar descrição, teto e `matriculationRequest`, ou a tela e a
    validação avisarem.
18. A-12: recibo distinto para "origem no teto" e log estruturado; teto configurável para o pico.
19. A-11: tela de encerrar com as pendências listadas; recusas por decisão do usuário.
20. A-38: "Emitir ordem" desabilitado com motivo quando a ordem não posiciona ninguém e há Etapa
    sem consolidação.

**Grupo 9 — Decisões (coordenação).** Os oito itens da seção E, cada um com registro em
`doc/decisoes-pendentes-da-consolidacao.md` ou na spec que o recebe. Corrigir a frase da
segregação no doc de 30/10 e a linha M-09 na tabela de 31/10.

---

## G. Critérios de liberação

Evidências objetivas que precisam existir para considerar o GPS apto a iniciar o primeiro edital
real. Cada uma é verificável por quem não participou da correção.

1. **Fluxo recursal sob a role de produção.** Um teste da suíte executa `julgar` com
   `CORRECAO_FIXADA` e com `REAVALIACAO_DETERMINADA` por conexão `SET ROLE` da role de conformidade
   e grava decisão e sucessor; o guardião geral de travas está verde e tem teste que o vê
   reprovar.
2. **Sete fluxos de fumaça sob `SET ROLE`** (publicar, consolidar, emitir ordem, julgar, convocar,
   conceder/revogar, registrar unidade) verdes no CI.
3. **Imutabilidade da Inscrição enviada no banco.** `UPDATE`/`DELETE` em `inscricoes_inscricao`
   com `status='SUBMETIDA'`, como a role de runtime, recusados pelo gatilho; idem documento
   submetido, Avaliação concluída e Homologação — ou decisão escrita e assinada de não os ter.
4. **Boot de produção automatizado.** Um passo do CI sobe `config.settings.production` contra
   banco real com variáveis mínimas e confirma `/health`, `/readiness`, `/gestao/` 503 (ou 200 com
   provedor de homologação), `/selecoes/` 200 e os cabeçalhos de segurança.
5. **Provedor institucional real** configurado em homologação, com entrada, troca de unidade,
   revogação e suspensão demonstradas por pessoas (T051 da `110` e critério humano da `107`).
6. **Medição do portal sob correio degradado**, registrada: `/selecoes/` em < 2 s (p95) com SMTP
   a 20 s por envio sob N pedidos de código por minuto, N fixado pela instituição; `limit_req`
   ativo no proxy.
7. **Restauração ensaiada e registrada** em VM descartável, com volume representativo, RTO
   medido, `46 de 46`, 68 gatilhos, `migrate --check` 0 e documentos conferidos (`ps-conferir-documentos`).
8. **Produção versionada**: gunicorn no `uv.lock`; `STATIC_ROOT` ou o `alias` como arquivo
   versionado; units e timers versionados; `AVISOS_AOS_CANDIDATOS` com trava; `.env` de produção
   validado por `check --deploy` sem W005/W021 inesperados.
9. **Decisões registradas**: FR-021 ("elaborou"), retenção (B-2) com o inventário do irremovível,
   avisos aos candidatos, identificação multiunidade (ou declaração de que o primeiro edital é de
   uma unidade só), prazo de inatividade.
10. **Trilha de leitura**: abrir dossiê com Requerimento gera evento; a exportação aparece na
    trilha da condução.
11. **Documentação coerente com o código**: guia com totais e comandos atuais; doc de 30/10 com a
    frase da segregação corrigida; comentários de `INSTALLED_APPS` verdadeiros ou substituídos por
    guardião.
12. **Estado final respeitado**: publicar ou transitar Retificação de Edital encerrado responde
    409 (teste); a confirmação de encerramento lista recursos sem decisão, convocações sem desfecho
    e Retificações em curso.
13. **Reaproveitamento íntegro**: teste em que o Edital criado a partir de outro leva descrição,
    teto e `matriculationRequest` — ou a validação adverte a ausência quando a origem os tinha.
14. **Jornada completa sob a role de produção**, repetida depois das correções, inclusive o
    deferimento com efeito, o Requerimento de Matrícula e a exportação até o arquivo.

---

## Pergunta final

*Se o GPS precisasse conduzir seu primeiro edital real após concluir a homologação funcional,
quais falhas arquiteturais, de segurança, integridade, implantação ou recuperação ainda poderiam
comprometer essa operação — e quais evidências demonstram que estão ou não controladas?*

**Comprometeriam a operação, e não estão controladas:**

- **O julgamento de recurso com efeito falha em produção** (A-01). Evidência de que **não** está
  controlado: `permission denied` reproduzido quatro vezes como a role de produção — por SQL,
  pelo ORM e pelo POST da própria tela, que respondeu 500; 19 a 22 testes que o exercitam passam porque rodam como superusuário; o ensaio operacional
  excluiu "recurso". Evidência de que a correção é segura: sob a trava do Processo que já existe,
  dois julgamentos concorrentes terminam em um ato e um 409.
- **A ausência de rede para essa classe de defeito** (A-02): nenhum teste executa fluxo como a
  role de produção; o guardião existente varre um app só.
- **A inscrição enviada protegida por uma camada só** (A-03): 12 inscrições enviadas alteradas e
  devolvidas a rascunho, 12 credenciais apagadas, como a role de produção, sem recusa — ao lado de
  `permission denied` nas tabelas de ato.
- **O portal sob correio degradado** (A-04): mecanismo demonstrado (20 s por pedido, e-mail dentro
  da requisição, sem `limit_req`); carga não medida. Enquanto não houver medição, é risco
  fundamentado e não controlado.
- **A entrada institucional** (B-1): sem provedor real a gestão responde 503; nenhuma jornada da
  gestão acontece em produção. Controlado no sentido de que nada cai para a demonstração [E]; não
  controlado no sentido de que não há como operar.
- **A recuperação** (A-26): a sequência de restauração do guia está correta e **passou** no ensaio
  local (46/46, 68 gatilhos, donos corretos, runtime sem `UPDATE`, `migrate --check` 0), mas não
  há registro, script versionado nem ensaio em volume real. Está controlada por procedimento, e
  não por evidência.
- **Dois defeitos de regra na jornada** (A-09, A-10): a Retificação publicada em Edital
  encerrado e o Requerimento de Matrícula que não viaja no reaproveitamento — reproduzidos pela
  interface como a role de produção, confirmados por leitura, e sem teste que os cubra.
- **Três decisões institucionais** (segregação, retenção, avisos) que, não tomadas, deixam o
  código fazendo o que ninguém decidiu.

**Estão controladas, com evidência de execução** (Anexo II): isolamento entre unidades (75 de 75
acessos alheios em 404, nada gravado); append-only em duas camadas nas 46 tabelas de ato (recusa
por privilégio e por gatilho, inclusive para o dono); concorrência dos fluxos críticos (padrão
uniforme de `atomic` → trava no Processo → idempotência → unicidade, com três corridas novas
terminando em um ato e um 409); autenticação do candidato (código por `secrets`, hash salgado,
cinco tentativas atômicas, resposta neutra, rotação de sessão); autorização por escopo (varredura
por `pk` sem vazamento); documentos oficiais servidos dos bytes gravados com hash, e atos
posteriores lendo só a versão publicada; barreiras de produção funcionando no boot e em execução,
sob gunicorn; logs sem dado pessoal, exceto o traceback da falha de correio (A-15); ordem de
provisionamento e restauração reproduzindo privilégios e gatilhos.

**Estão controlados, com evidência de execução, também:** a jornada normativa completa pela
interface, como a role de produção, com segregação e trilha e cada passo abaixo de 0,2 s (A-01 é a
única etapa que não fecha); as recusas de domínio percorridas dizem o que fazer; as transições
(a), (c), (d), (g), (k) e (l) têm caminho na interface.

**Não foi possível verificar** (Anexo III): comportamento sob nginx, systemd e certbot reais;
carga; provedor institucional real; volume de dados de um certame; o Requerimento e a exportação
até o arquivo (A-10 impediu); desfecho e atestado da convocação, reabertura de avaliação, sorteio e
anulação (só lidos).

---

## Matriz de rastreabilidade

| ID | Frente | Sev. | Componente | Evidência | Teste existente | Ação (seção F) | Critério (seção G) |
|---|---|---|---|---|---|---|---|
| A-01 | INT-1 / ARQ-01 / OPE-02 | P0 | `recursos/application/julgar.py:221` | [E] `permission denied` como runtime (SQL, ORM e POST da tela → 500); [F] `papeis.py` | 19–22 arquivos como superusuário | F-1, F-2 | G-1 |
| A-02 | INT-2 / ARQ-02 | P1 | desenho da suíte; `test_database_permissions.py` | [F] única fixture runtime é SQL direto; [E] `TRUNCATE`/`setval` negados | `test_privilegios.py` (só `seguranca`) | F-3 | G-2 |
| A-03 | DAD-01 / INT-3 | P1 | `inscricoes/models.py:118-134`; `avaliacoes`; `publicacoes_homologacao` | [E] UPDATE/DELETE aceitos como runtime (12/12/11/4 linhas) | nenhum de banco | F-5 | G-3 |
| A-04 | INF-01 | P2 | `portal/views.py:838`; `identidade/application/mensagem.py` | [E] 20,0 s por envio; [F] sem `limit_req`; [I] tetos | `test_configuracao_de_correio.py` | F-6 | G-6 |
| A-05 | SEG-01 | P2 | `interface/identidade.py:610-626` | [E] POST após 31 min → 302 sem corpo | `test_sessao_com_prazo.py` (GET) | F-9 | — |
| A-06 | MU-1 / MU-7 | P2 | `portal/views.py:1277-1300`; `public_serializers.py` | [E] duas entradas idênticas; sem `unit` na versão vigente | nenhum com dois escopos | F-15 | G-9 |
| A-07 | DAD-02 | P2 | `interface/views.py:5729-5734`; `consulta.py` | [E] 106→106 eventos ao abrir dossiê | `test_inscricoes_recebidas.py` (só documento) | F-10 | G-10 |
| A-08 | coord. | P2 | `production.py`; `publish_edital.py:508,705`; fonte da Caixa | [F] confirmações | — | F-14, Grupo 9 | G-8, G-9 |
| A-09 | OPE-06 | P2 | `publicacoes/application/retificacoes.py:74,398`; `interface/atos.py:129` | [E] publicar Retificação após encerrar → 302; [F] guarda existe e não é chamada | `test_jornada_da_retificacao.py` (só Retificação encerrada) | F-16 | G-12 |
| A-10 | OPE-04 | P2 | `editais/application/reaproveitamento.py:334-347` | [E] `matriculationRequest=None` no destino; 404 no Requerimento | `test_quickstart.py` (023, só coleções) | F-17 | G-13 |
| A-11 | OPE-03 | P2 | `processos/domain/finalizacao.py:75-80`; tela `atos/encerrar` | [E] encerrado com recurso admitido, convocação sem desfecho, Retificação homologada | `test_us7_finalizacao.py` (estado) | F-19 | G-12 |
| A-12 | OPE-01 | P2 | `identidade/application/desafio.py:36-42,127-130`; `portal/views.py:845-866` | [F] mesma frase para teto e espera; [E] caso irmão reproduzido | `test_limites.py` (teto, não a mensagem) | F-18 | — |
| A-13…A-41 | ver Anexo I | P3 | — | — | — | F-7, F-8, F-11…F-13, F-15, F-20 | G-4, G-7, G-8, G-11 |

---

## Anexo I — Achados P3

Cada um com evidência resumida; o detalhe está no relatório da frente.

- **A-13 (SEG-02)** Os dois canais compartilham a sessão e se afetam de forma assimétrica: `Sair`
  do portal só faz `pop` e a gestão continua aberta na mesma `session_key` [E]; `Sair`
  institucional faz `flush` e derruba o candidato [E]; `contexto_identidade` resolve o ator
  institucional em toda página pública e, vencido o prazo, grava `SAIDA` a partir de um GET do
  portal [E]. Sem vazamento de contexto nos templates [F]. Correção: `flush()` no portal (I-5).
- **A-14 (I-5 ampliada)** `SESSION_COOKIE_AGE` padrão de duas semanas; `clearsessions` e
  `limpar_terminais` só por timer do guia.
- **A-15 (SEG-03)** `logger.exception` na falha de correio leva o e-mail do candidato ao log pelo
  traceback de `SMTPRecipientsRefused` [E], contra o comentário "sem o endereço"
  (`identidade/application/mensagem.py:107-109`, `convocacao/application/comunicar.py:373`).
- **A-16 (MU-3)** `GET /` lista Edital cancelado em `editaisPublicados` [E]; a vitrine não
  (`shared/api/operacional.py:72-82` sem o `exclude` de `selecoes_publicas`).
- **A-17 (ARQ-05)** `PAPEIS` mora em `interface/identidade.py` e é importado por
  `seguranca/application/acessos.py:76` (domínio → canal); três catálogos e dois mapas de descrição
  reconciliados em tempo de execução; o guardião de `FR-1701` cobre só `PAPEIS × DESCRICOES`.
  Preferência arquitetural com um benefício concreto: o guardião que falta.
- **A-18 (SEG-05)** `conceder_administracao_institucional` aceita qualquer `--provedor` e
  `--identificador` sem conferir com o adaptador configurado; grafia divergente cria uma
  administração que ninguém alcança, corrigível só por comando.
- **A-19 (MU-2)** A página pública da seleção imprime "Unidade: CEFOR" (código interno em caixa
  alta, `portal/views.py:148`) em vez da sigla do ato; a `072` corrigiu só o cartão.
- **A-20 (INT-4)** Entre `migrate` e a segunda passada de `provisionar_papeis`, tabela append-only
  nova nasce com `UPDATE, DELETE` para a runtime (`pg_default_acl` = `arwd` [E]); o gatilho segura.
  Inverter para "negar por padrão" nos privilégios default.
- **A-21 (MU-7)** `versao-vigente` pública não identifica a unidade; só `publicacoes/<id>` traz
  `unit` [E].
- **A-22 (INF-02)** `django.security.*` (DisallowedHost, CSRF) não é logado em produção [E]: 400 e
  403 sem linha no errorlog. Uma linha em `LOGGING`.
- **A-23 (INF-03)** Sem `connect_timeout` em `DATABASES`: banco inalcançável → `/readiness` 503
  só após ~90 s e toda requisição espera o TCP [E]; porta recusada → 0,44 s. `OPTIONS
  connect_timeout=3`.
- **A-24 (MU-5)** A comissão aceita presidente sem vínculo na unidade (201) e o mantém depois da
  revogação do último vínculo; dois presidentes simultâneos permitidos; a substituição exige
  promover antes de remover, sem orientação na tela [E]. É a M-06 com a consequência medida.
- **A-25 (INF-08)** `400` em inglês (sem `400.html`) enquanto 403 e 404 são institucionais [E];
  `Server: gunicorn` exposto e o nginx do guia sem `proxy_hide_header` [E].
- **A-26 (INF-06)** Nenhuma evidência versionada de restauração testada. O ensaio local passou
  [E]: dump 0,17 s / 1,2 MB, restore 0,26 s, 46/46, 68 gatilhos, 51 funções, donos corretos, runtime
  sem `UPDATE`/`DELETE`, gatilho recusa até o dono, `migrate --check` 0. Observações: o dump carrega
  ACLs; a primeira passada do provisionamento é obrigatória antes do restore.
- **A-27 (INF-05)** Guia desatualizado: `40 de 40` em seis lugares (hoje 46), "46 gatilhos" (68),
  "33 RunPython" (39), §11.4 "não há como criar administrador" (os comandos da `106`/`107` existem
  e não estão no guia), `ASSISTENTE_NA_PAGINA_DO_EDITAL` fora da lista de proibidas, 15
  `ASSISTENTE_*` ausentes do §10.1.
- **A-28 (ARQ-04)** Quatro comentários de `INSTALLED_APPS` falsos (`sorteios` é importado por
  quatro apps; "única de mão dupla" é falso para seis pares; `inscricoes → requerimentos` importa
  mais que o predicado; `duvidas` tem models) [F, grafo por AST]; só quatro fronteiras têm
  guardião.
- **A-29 (INT-5)** A role de migração pode `DISABLE TRIGGER` e reescrever o histórico [E, em
  `ROLLBACK`]; nada confere `tgenabled`. Dívida aceita pelo guia; acrescentar a conferência.
- **A-30 (INF-04)** gunicorn 26.2.0 cria *control socket* em `$HOME/.gunicorn`; sob a unit
  endurecida do guia vira `ERROR` em todo start [E com `HOME` sem escrita]. Desligar no
  `gunicorn.conf.py`.
- **A-31 (DAD-05)** Inventário do dado pessoal **irremovível** por construção: e-mail em
  `avisos_destinatariodoaviso` e `convocacao_comunicacaoemitida`, data de nascimento em
  `valordefato`, texto livre em `recursos_*` e nos `motivo` sobre servidores, nome e protocolo nos
  PDFs e no sorteio, `signatory_name`, `auth_user`. A política B-2 precisa tratar eliminação como
  inaplicável a esse conjunto e orientar os campos `motivo`.
- **A-32 (DAD-06)** Retenção prática sem mecanismo: rascunhos de inscrição e de Requerimento (com
  arquivos), identidades sem inscrição, `IdempotencyRecord` (uma linha por comando, nunca limpo).
- **A-33 (DAD-07)** Portal sem aviso de privacidade, finalidade ou base legal; o envio pede só
  `veracidade` e `ciencia`; o Requerimento coleta cor/raça e necessidade específica sem texto
  informativo. Decisão institucional.
- **A-34 (DAD-08)** A prévia da exportação é auditada em `RegistroAuditoria`; o arquivo (CPF, RG,
  filiação) só em `GeracaoDeArquivo`, que a trilha da condução não lista; sem limite nem marca.
- **A-35 (DAD-04)** `origem_hash` do desafio é SHA-256 do IP sem sal (`desafio.py:64`),
  reversível por enumeração; transitório.
- **A-36 (INT-6)** Status de Processo, Edital, Inscrição, Retificação, Evento e Avaliação sem
  `CHECK`; transições inválidas recusadas no comando com 409 [F].
- **A-37 (ARQ-06/07/08/09/10, MU-4, MU-6, SEG-06/07/08, INF-07/09, DAD-03)** Observações de
  menor peso, registradas nos relatórios das frentes: `views.py` com 10.624 linhas e acoplamento
  baixo (custo de merge, não defeito); tempo medido em cinco constantes e nenhum teste de tempo do
  PDF; `check --deploy` só via teste em subprocesso; fixture `autouse` do Cefor torna a unidade
  implícita; parser da Caixa testado só com JSON à mão; fragmento `perfil/<indice>/marco` com
  índice não-UUID → 500 [E]; unidade desativada não recebe substituto de quem saiu (dívida aceita
  pela `110`); tetos de código de acesso contam sem trava; `X-Forwarded-For[0]` só seguro com um
  proxy; retorno do SSO só GET e `form-action 'self'` inviabilizam SAML POST; `unidades/0003`
  quebra código anterior só ao inserir Unidade; `X-Correlation-ID` aceito do cliente; a trilha não
  guarda antes/depois fora das tabelas administrativas.

- **A-38 (OPE-05)** A ordem classificatória pode ser emitida **vazia** quando uma Etapa enumerada
  não está consolidada: a tela avisa "Nenhum participante recebeu posição" e oferece "Emitir
  ordem"; o ato nasce sem posições e exige sucessor com motivo [E].
- **A-39 (OPE-07, OPE-08)** O detalhe do Edital publicado não aponta para comissão, alocação nem
  distribuição (estão no Processo e na Supervisão); a Supervisão alerta "sem avaliador suficiente"
  enquanto as inscrições correm e a distribuição recusa [E]; o texto da tela da comissão diz "Não
  existe diretório institucional integrado", desatualizado desde a `106`, e o identificador precisa
  ser o `subject` exato do provedor, sem autocompletar.
- **A-40 (OPE-09)** Nem correção de CPF congelado (nem por shell) nem recebimento individual fora
  do prazo (inscrição ou recurso): só o caminho coletivo, a Retificação do prazo, que funciona [E].
  Limitação funcional que pede decisão institucional.
- **A-41 (OPE-10, OPE-11)** O sorteio lê o método **da relação congelada**: método retificado exige
  suceder a relação, e a recusa não o diz (complementa o achado de 29/10). Miúdos: atos de submeter
  e homologar aceitos sem chave de idempotência (só envios montados à mão); `acao` desconhecida na
  comissão responde como sucesso; o publicador recebe 403 na página do ato e 200 na prévia que o
  detalhe linka.

---

## Anexo II — O que foi verificado e está controlado

Por execução, salvo marca contrária.

- **Isolamento entre unidades.** 46 GETs e 29 POSTs da gestão com o ator de outra unidade →
  75 de 75 em 404; contadores de auditoria, apuração, corte e ato inalterados; agenda, trilha da
  unidade, relatório consolidado, lista e visão geral não misturam; revogar vínculo alheio → 404;
  autoridades de outra unidade, fora de vigência e encerradas em corrida → recusadas (10 testes);
  modelos iniciais de aviso nascem na criação de unidade pela aplicação; trilha filtra por escopo
  em todas as consultas, inclusive por `aggregate_id`; gatilhos de escopo imutável existem
  (`processos/0005`) [F].
- **Append-only em duas camadas.** 46 de 46 no provisionamento; `UPDATE`/`DELETE` como runtime →
  `permission denied`; como dono → o gatilho recusa; as 46 têm gatilho incondicional, sem
  divergência "coluna permitida × privilégio negado" [F]; funções de gatilho do dono sem
  `SECURITY DEFINER`; todos os `.delete()`/`.update()` do app recaem em tabelas mutáveis [F].
- **Concorrência.** Padrão uniforme `atomic` → trava no Processo → idempotência → CAS ou
  unicidade, em publicação, Retificação, submissão, divulgação, recursos, sorteio, convocação,
  avisos e numeração [F]; três corridas novas (julgamento duplo, interposição dupla, Edital
  duplicado) → um ato e um 409 legível; 30 arquivos de teste com threads já existem [F].
- **Transações e efeitos externos.** Os quatro envios de e-mail ficam fora da transação; a
  convocação reserva em transação curta e não reenvia reserva pendente; os avisos marcam órfãs;
  `despachar_avisos` idempotente com trava global [F].
- **Fuso e tempo.** `USE_TZ`, zona institucional, sem offset fixo; período de inscrição e prazo
  recursal cientes de fuso; vigência de Retificação no passado recusada [F].
- **Migrations.** `makemigrations --check` e `migrate --check` limpos; 39 `RunPython` reversíveis;
  nenhuma lê arquivo ou settings; só `plpgsql` como extensão.
- **Sessões e autenticação.** `login()` rotaciona na entrada institucional; `cycle_key()` no
  portal; estado anti-CSRF de login com `token_urlsafe(32)` e `compare_digest`; revogação vale na
  requisição seguinte; suspensão troca o hash e derruba a sessão parada; código de acesso por
  `secrets`, `make_password` salgado, 5 tentativas atômicas, consumo atômico, 5/h por endereço e
  30/h por origem, resposta neutra; CPF fora da decisão de identidade e congelado após a primeira
  inscrição enviada; 93 casos existentes de autorização e identidade rodados, 93 passaram.
- **Autorização.** Varredura por `pk` em `interface/`, `*/application/`, `*/api/`: todo acesso
  direto seguido de filtro de escopo ou objeto-pai filtrado [F]; IDOR de inscrição, documento e
  comprovante → 404 indistinguível; nenhum `csrf_exempt`; ações de estado por POST; fragmentos
  htmx só leem; `AllowAny` só em índice, health, readiness, documento publicado, artefato
  congelado e públicos do sorteio; `IndexView` só lista o que tem `VersaoConsolidada`, criada na
  publicação; `/metrics` e API admin → 403 com o paliativo [E].
- **Documentos e arquivos.** Nome físico UUID, sem URL, `%PDF-` por assinatura, cópia verificada
  contra `content_hash` e 409 na divergência, `no-store`; anexos do Edital em coluna binária com
  limite; PDF publicado e documento do resultado servidos dos bytes gravados com hash e ETag;
  comprovante regenerado da `versao_aceita` e da identificação do ato; CPF ausente de todo
  documento público e mascarado na gestão; `effective_version` lê só `VersaoConsolidada` e 35
  módulos de atos posteriores o usam — nenhuma leitura retroativa do relacional encontrada.
- **Produção.** `production.py` recusa cada substituto de demonstração no boot **e** em execução;
  `check --deploy` só com W005/W021 esperados; gunicorn 26.2.0 sobe com `--preload` e responde
  302/503/200/403/404/301 como o guia descreve; HSTS, CSP, XFO, nosniff, Referrer-Policy e COOP
  presentes; `/health` não toca o banco; `/readiness` custa ~4 ms e dá 503 em 0,44 s com porta
  recusada; `EMAIL_TIMEOUT` respeitado (20,0 s); nenhuma dependência de versão do PostgreSQL entre
  16 e 18 no SQL; `/gestao/identificar/demonstracao` → 503 em produção.
- **Logs e trilha.** `JsonFormatter` só com correlação, código, status, operação e ator; nenhum
  `logger.*` com CPF, e-mail, código ou nome (exceto A-15); `reason`/`detalhe` dos 94 eventos do
  seed sem CPF, e-mail ou nome; `detalhe_tecnico` dos avisos só com o tipo da exceção; perguntas do
  piloto mascaradas antes de gravar; idempotência só com UUIDs.
- **Jornada.** A sequência normativa completa — criar → partir de anterior → corrigir →
  submeter → homologar → publicar → retificar → inscrever → comissão → alocar → distribuir →
  avaliar → consolidar → emitir → publicar resultado → avisar → recorrer → admitir → indeferir →
  corte → apurar → convocar → comunicar → encerrar — executável só pela interface, como a role de
  runtime, com segregação e trilha preenchidas, cada passo abaixo de 0,2 s; as recusas certas onde
  deviam (inscrições abertas, dois avaliadores para exigência de um, eliminado fora da consolidação
  seguinte, prazo recursal computado); inscrição pelo portal de ponta a ponta com três documentos,
  comprovante e e-mail; `seed_demo` usa os commands da aplicação e nenhum atalho dele é capacidade
  só de shell.
- **Código.** Zero `TODO`/`FIXME`; "provisório" só o adaptador de API, recusado em produção.

---

## Anexo III — Método, ambiente e limitações da verificação

**Ambiente.** Worktree da `main` em `4ca16b1d`; PostgreSQL 16.14 local (o guia e o CI usam 18 —
nenhuma dependência de versão encontrada no SQL); Django 5.2.17, DRF 3.16.1, psycopg 3.3.4;
banco `processo_seletivo_audit` por `make preparar` (`46 de 46`, `Unidades: 1 semeadas`, `Modelos
de aviso: 3 criados`) e `seed_demo`; roles `processo_seletivo_runtime` e `processo_seletivo_owner`
da política real; um banco de teste por frente (`ps_aud_a`…`ps_aud_g`), sem xdist; testes
descartáveis em `backend/tests/_auditoria_<letra>/`, apagados ao final; `git status` limpo no fim de
cada frente; boot de produção sob gunicorn 26.2.0 na porta 8105 com variáveis fictícias; ensaio de
restauração em `ps_aud_e_restore`, apagado.

**O que não foi feito, e por quê.** A suíte inteira não foi executada (conhecida; o custo não se
justificava). Nenhum provedor institucional real: a entrada foi exercitada com o simulado da suíte.
Nenhum servidor nginx, systemd, certbot ou ufw: o guia foi lido, não executado; A-30 simulou o
`HOME` sem escrita, não a unit. Nenhum teste de carga: os tetos de A-04 são aritmética sobre o
timeout medido e a configuração do guia. O volume de dados é o do `seed_demo` (1,2 MB): tempos de
dump e restore não extrapolam. CVEs conferidas só para o Django por busca pública; DRF, psycopg e
gunicorn não [H]. O inventário de `select_for_update` e a varredura por `pk` foram por grep e
leitura de contexto, não por análise estática automática. A tabela dos `doc/achado-*.md` foi
produzida a partir de cabeçalhos e greps, com conferência por amostragem das linhas usadas em
achados. A presença de dado pessoal na trilha foi conferida sobre os 94 eventos do seed e os
construtores de `reason`/`detalhe`, não sobre um certame completo (o seed não tem Requerimento,
documentos em disco, avisos despachados, recursos nem exportação).

**Limites da jornada refeita.** Tudo por `django.test.Client` no mesmo processo: sem gunicorn,
nginx, CSRF real ou navegador (htmx não executado); o seletor de demonstração no lugar do
provedor, de modo que os vínculos da `107` não foram exercitados e a comissão foi montada com
identificadores livres; não medida em escala (60 Perfis × 4 modalidades); Caixa real não testada;
Requerimento e exportação não percorridos até o arquivo (A-10 impediu); desfecho e atestado da
convocação, reabertura de avaliação, sorteio e anulação só lidos; o primeiro recurso da jornada
saiu "não admitido" por erro de operação da própria frente (valor do botão), e o julgamento com
efeito foi testado no segundo.

**Independência das reproduções.** O achado P0 foi reproduzido pela frente de integridade, pela
de arquitetura, pela de jornada e pela coordenação, por caminhos distintos (SQL direto como a
role, ORM em `manage.py shell`, SQL gerado pelo ORM pela role de conformidade da suíte, e o POST da
tela pelo `Client` como a role de runtime, que respondeu 500). Os dois defeitos de regra da jornada
(A-09, A-10) foram reproduzidos pela frente de jornada e confirmados por leitura pela coordenação. O P1 de imutabilidade
foi reproduzido pela frente de integridade e pela de dados, com consultas distintas.
