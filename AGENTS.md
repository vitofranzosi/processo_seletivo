# Instruções para agentes

Este arquivo é para quem chega sem contexto — humano ou agente. Ele registra o que **não se
descobre lendo o código**: as armadilhas que já custaram sessões inteiras. O resto está no
[README](README.md).

`CLAUDE.md` é um symlink para cá. Uma fonte só.

## O que este projeto é

Sistema de Processos Seletivos e Editais do Cefor/Ifes. Monólito Django sobre PostgreSQL,
conduzido por especificação com [GitHub Spec Kit](https://github.com/github/spec-kit).

A [Constituição](.specify/memory/constitution.md) é a autoridade de engenharia e domínio. Em
conflito com qualquer coisa escrita aqui, **ela prevalece**. Três consequências que aparecem no
dia a dia:

- **Publicação é ato imutável.** Não existe corrigir um Edital publicado; existe Retificar. As
  tabelas append-only são protegidas por trigger *e* por privilégio ausente — duas camadas
  independentes, e nenhuma delas é contornável em desenvolvimento.
- **Nada é excluído.** Não escreva migration que apague dado normativo, nem comando que o faça. O
  "nada" é sobre dado normativo: os registros do piloto do assistente (`071`) não são ato do
  certame, e se excluem 90 dias depois do relatório final, por `excluir_registros_do_piloto`.
- **Negar por padrão.** Toda operação exige permissão explícita e verificação de escopo.

## Subir o ambiente

O caminho canônico é `docker compose up --build`, e o README tem os dois — containerizado e
nativo. O que importa saber antes de tentar:

**Nada carrega `backend/.env` sozinho.** O projeto não usa `python-dotenv`. Quem lê o arquivo é o
`docker compose` e são os alvos do `backend/Makefile`. Um `manage.py` chamado à mão fora do `make`
enxerga só o que estiver exportado no ambiente — foi assim que a instrução "copie o `.env.example`"
ficou anos sem efeito nenhum.

**A preparação do banco tem três passos, nesta ordem:** provisionar papéis, migrar, provisionar de
novo. Não é redundância — a segunda passada é a que concede privilégio sobre as tabelas que as
migrations acabaram de criar. O comando informa quantas protegeu, no formato `N de M`; se o
primeiro número vier `0`, a segunda passada não rodou. O `M` cresce a cada tabela append-only nova
— eram 18, depois 34, depois 40 com os avisos da `066`, eram **41** com as vagas acrescidas da `097`, eram **44** com a identidade institucional da `106`, são **46** desde a suspensão de pessoa da `107` — e é por isso que a armadilha é o zero,
e não o total.

**Depois dos três, o `make preparar` semeia as Unidades** de
`backend/processo_seletivo/unidades/unidades.json` — **só num banco vazio** (110). Sem isso, a criação
de Processo recusa com `unidade_nao_registrada` e a publicação não tem cabeçalho. A linha que ele
imprime diz o que aconteceu: `Unidades: N semeadas.` num banco novo, e
`Unidades: registro com N unidades; a semente não se aplica.` em todos os outros. **Editar o arquivo
depois não tem efeito**: o registro é da aplicação, pela tela "Unidades" do Administrador
institucional, com motivo e trilha. O comando é `semear_unidades`; `sincronizar_unidades` continua
como apelido, com um aviso no *stderr*. As tabelas da `060`
**não** são append-only — nada se exclui nelas por gatilho, mas elas mudam —, e não contam no `M`.
A suíte não depende do comando: uma fixture `autouse` registra o Cefor em todo caso que toca o banco,
porque os casos transacionais truncam as tabelas e a linha que uma migration criasse sumiria. O caso
que precisa do registro vazio — os da semente — leva o marcador `sem_unidade_da_suite`.

**O mesmo comando cria os três modelos iniciais de aviso** de cada unidade (066), e imprime
`Modelos de aviso: C criados` — três na primeira vez, **zero** daí em diante, para sempre: a unidade
que editou ou inativou os modelos continua com os dela. A fixture `autouse` **não** os cria, de
propósito: gravaria três modelos e três eventos de trilha em todo caso, e os testes que contam a
trilha quebrariam em bloco. Quem precisa deles chama `garantir_modelos_iniciais()`.

**Migration desaplicada contamina a sessão inteira.** O sintoma é `relation ... does not exist` num
arquivo sorteado, longe da causa. Antes de investigar qualquer erro estranho, confira
`manage.py migrate --check`.

## As armadilhas caras

**O modo padrão da suíte não é confiável — rode contra PostgreSQL.** Sem variável nenhuma, a
suíte cai para SQLite: **35 falham, ~8087 passam, 253 são puladas e 1 erro** (medido em
2026-09-28). Todas deveriam ter sido puladas e não foram, e a causa se reparte em três — o achado
original ([doc/achado-suite-em-sqlite.md](doc/achado-suite-em-sqlite.md), de 09/09) nomeava só a
primeira, quando eram 21:

| Quantas | Por que |
|---|---|
| 14 | SQL que só o PostgreSQL entende — `near "DISABLE": syntax error`, de `ALTER TABLE ... DISABLE TRIGGER` |
| 9 | a mensagem do SQLite não nomeia a constraint, e o `pytest.raises(match=...)` não casa |
| 11 | garantia que o SQLite não tem — gatilho ausente (`DID NOT RAISE`, 6), transação que não tranca (3) e erro de constraint que escapa cru (2) |

A 35ª falha e o erro são de outra natureza: conexão do SQLite que ninguém fechou, acusada pelo
`ResourceWarning` — que o `pyproject.toml` promove a erro — no caso que por acaso estiver rodando
quando o coletor de lixo passa. É o acoplamento do parágrafo seguinte.

**O total neste modo não é reprodutível, e o `~` acima é literal**: duas execuções seguidas de um
mesmo commit, em 09/20, deram 7211 e 7212 passando, com 1 e 2 erros. Cinco falhas do `portal` não
se repetiram ao rodar os mesmos arquivos isolados, e não há plugin de ordem aleatória instalado —
de modo que há acoplamento entre casos que só aparece aqui. Não investigue por este caminho: a
repartição acima é o que importa, e nenhuma das três colunas é defeito de produto.

**Ao atualizar estes números, atualize as falhas e os pulados junto — e desconfie se as falhas
mudarem.** As três causas são do vendor e não do produto, e teste novo bem escrito não entra
nelas: falha mexendo é sinal de que alguém escreveu SQL de PostgreSQL num caminho que antes não
tinha. Os pulados são outra coisa: **sobem sempre que entra teste que só o PostgreSQL verifica**, e
é o esperado. Entre 09/21 e 09/28 foram de 243 a 253, e os dez foram conferidos um a um — cinco da
lista exigida da `044` (`test_lista_exigida_imutavel.py` e `test_lista_exigida_concorrencia.py`),
dois em `test_database_permissions.py`, parametrizado por `TABELAS_APPEND_ONLY`, que ganhou uma
tabela, e três em `test_imutabilidade_do_historico.py`, do gatilho que o `ValorDeFato` recebeu.

**Para saber de onde veio uma diferença, compare listas, não totais.** Rode `pytest -q -rs` nos dois
commits e agrupe os `SKIPPED` por arquivo e motivo, sem o número da linha, que muda entre eles. As
falhas se comparam classificando cada uma pela mensagem. Foi assim que se viu que a repartição
anterior desta tabela, de 09/21, dizia 5 e 3 onde o mesmo commit tinha 6 e 2 — erro de
classificação daquela medição, e não mudança de código.

O CI não vê nada disso, porque só roda contra PostgreSQL.

Contra PostgreSQL a suíte fecha em **12775 passando e 12 pulados** (medido em 2026-10-21, sobre a árvore da `main` em `e869d7a2`, com o grupo `assistente` instalado e 4 workers, em 498s; a medição anterior, de 18/10 em `2abd18db`, dava 12268 e 11 — a diferença é a dos testes da `093` à `097`, e o pulado a mais é o da `097`, descrito abaixo). Aquela rodada teve ainda **uma falha, que não é defeito**: o teste de tempo da ocupação, que oscila com 4 workers e passa isolado — ver *Um teste de tempo oscila sob carga*, adiante. Sem o grupo há um pulado a mais, o da `071`: a contagem real de tokens, que pula sem a biblioteca `tokenizers` — ela é do grupo opcional `assistente`, e não de desenvolvimento; com o grupo instalado, ela roda, e o CI o instala desde 14/10 (`uv sync --extra dev --extra assistente`), de modo que lá são doze pulados. **A `097` acrescentou um** — a conferência da vaga acrescida entrou na varredura de vocabulário e não usa «geração» —, e na worktree dela, sem o grupo, a suíte fechou em 12677 passando e 13 pulados (21/10, 4 workers, 437s). Os
treze — doze com o grupo — são deliberados, e se repartem em quatro: **10** são pares *termo × template* que
`test_vocabulario_da_composicao.py` pula quando a tela não usa aquele termo em texto visível; **1**
é a recusa por vendor, que só aparece fora do PostgreSQL; **1** é o E2E contra o serviço real da
Caixa, atrás da chave `SORTEIO_E2E_FONTE_REAL`; e **1** é a contagem real do tokenizer. A recusa por
vendor e o E2E estão nomeados em
[doc/achado-fonte-real-do-sorteio-sem-gatilho.md](doc/achado-fonte-real-do-sorteio-sem-gatilho.md).

Para chegar lá é preciso o **par**:
`TEST_DB_ENGINE=postgresql` **e** `DB_USER`. Só o primeiro cai para SQLite; só o segundo tenta
conectar como a role de runtime, que não pode criar banco de teste. Nenhum dos dois casos avisa. Com
`DB_RUNTIME_USER` no ambiente, as settings o preferem a `DB_USER`, e então é ele que precisa ser o
superusuário — é o que o `make test-pg` faz, a partir do `POSTGRES_USER`.

**A suíte roda em paralelo, e leva ~10 minutos com 4 workers — 600s, contra 1441s em série** (medido
em 2026-10-17, em `a41b67c0`). O `make test-pg` e o CI passam `-n 4 --dist worksteal`; cada worker
cria o seu banco, `test_<DB_NAME>_gwN`, com os seus gatilhos e privilégios. **O `worksteal` é o que
rende**: com a distribuição padrão os mesmos 4 workers deram 1057s, porque três ficavam ~6 minutos
ociosos esperando o quarto. E 8 workers deram 549s — quase nada a mais, porque o WAL e o disco do
cluster são um só, e cada caso transacional fica ~1,8× mais caro em companhia. Para o caso que só
falha junto de outros, `make test-pg PYTEST_WORKERS=0` volta ao serial. As medições estão em
[doc/estudo-paralelizacao-da-suite.md](doc/estudo-paralelizacao-da-suite.md). No CI, o primeiro run
paralelo levou 836s de pytest e 14m35s de job, contra 1729s a 2856s em série — o runner varia muito.

**Um teste de tempo oscila sob carga.**
`tests/performance/test_ocupacao.py::test_a_apuracao_cabe_no_dobro_do_tempo_da_emissao_da_ordem`
exige que a apuração de um recorte custe no máximo o dobro da emissão da ordem, e os dois tempos são
de poucos milissegundos: com 4 workers dividindo o cluster, um pico qualquer passa do teto. Em 21/10
ele falhou uma vez na suíte paralela (0,0115s contra 0,0038s) e passou seis de seis isolado, com e
sem a `097`. A falha cai justamente quando um PR mexe na ocupação, e parece regressão. Antes de
recusá-lo, meça a razão isolada nos dois commits, várias vezes —
`PYTEST_ADDOPTS="tests/performance/test_ocupacao.py -k dobro" make test-pg PYTEST_WORKERS=0`, e com
`RAZAO_MAXIMA` zerada numa cópia descartável o teste imprime os dois tempos. Ali, oito rodadas deram
razão de 0,88 a 1,49 com a `097` e de 0,64 a 1,06 sem ela, longe do 2,0. Uma rodada sob carga não é
sinal; uma distribuição que se desloca é.

**A preparação do banco não tem nada com o tempo.** Criar o banco de teste e aplicar as 80
migrations — hoje são 95 — custa **~2 segundos**, medido em 2026-09-20, isolando a preparação com
`--reuse-db` sobre um caso só. O custo está nos casos transacionais: **3108 dos 11 468 coletados,
27%, e 79% do tempo em série** (medido em 2026-10-17). Eles não podem terminar em `ROLLBACK`, e o
Django limpa depois de cada um truncando as tabelas e refazendo o `post_migrate` — só essa limpeza
é 44% da suíte serial. A versão de 09/28 deste parágrafo contava 2599 de 8375; a de 09/20 contava as
declarações de `transaction=True` como se fossem casos e concluía "~10%" — uma marca de classe ou de
módulo alcança todos os casos abaixo dela. Não é desleixo de quem os escreveu: é consequência de as
garantias deste sistema morarem no banco — gatilho append-only, privilégio ausente e
`select_for_update` que realmente tranca não são observáveis dentro de uma transação que vai ser
desfeita.

**A limpeza depois de cada caso transacional não é a do Django** desde 10/17. O `tests/conftest.py`
trunca só as tabelas com linha, mais as que têm chave estrangeira para elas, que o PostgreSQL exige
no mesmo `TRUNCATE`. E só emite o `post_migrate` quando `django_content_type` ou `auth_permission`
mudaram. O banco que o caso seguinte recebe é o mesmo, e a suíte cai ~20% (576s → 451s, em rodadas
seguidas). Desconfiou dela? `LIMPEZA_INTEGRAL=1` devolve a do Django. As medições, e a variante com
`DELETE` que tiraria 60% mas expõe um teste dependente da ordem física das linhas, estão em
[doc/estudo-limpeza-dos-casos-transacionais.md](doc/estudo-limpeza-dos-casos-transacionais.md).

**`--reuse-db` não economiza nada, e já foi medido — não repita o experimento.** Duas rodadas com a
bandeira ligada deram 670s e 686s, contra 733s sem ela; e a segunda, que **reusava** o banco, saiu
mais lenta que a primeira, que o **criou**. A variação entre rodadas idênticas é de ~60s, uma ordem
de grandeza acima do que a bandeira poupa. Ela trocaria 2 segundos por um banco que envelhece em
silêncio quando uma migration muda.

**Um banco de teste por worktree.** Suítes paralelas disputam `test_processo_seletivo` e se
derrubam. Passe um `DB_NAME` próprio quando houver mais de uma sessão. Os workers de uma mesma suíte
não precisam disso — o sufixo `_gwN` já os separa —, mas duas suítes com o mesmo `DB_NAME` geram os
mesmos `_gwN` e voltam a se derrubar. Os papéis de conformidade de `test_database_permissions.py`,
que são do cluster e não do banco, levam o worker e o `DB_NAME` no nome desde 10/17: com o nome
fixo, os workers se derrubavam ali — 51 erros em 92 casos com `-n 4`.

**`/gestao/` não abre sem o seletor de identidade.** Sem `INTERFACE_SELETOR_IDENTIDADE=true` o
runserver local devolve 503. Ele deixa qualquer pessoa declarar quem é, e produção recusa subir com
ele. Desde a `075`, desligá-lo também **derruba a sessão de demonstração já aberta** — ligar de novo
não a traz de volta —, e a vitrine deixa de oferecer "Área de gestão". O portal do candidato **não** precisa de `PORTAL_IDENTIDADE_DEMO`: a tela que a chave
habilitava saiu na `010`, e o candidato entra por código enviado ao e-mail. A chave sobrevive só
como armadilha — `production.py` recusa subir com ela ligada (`portal/identidade.py`,
`provedor_de_demonstracao`, que ninguém chama).

**Os avisos aos candidatos (066) não saem no clique.** A confirmação grava o aviso e responde; quem
envia é `manage.py despachar_avisos`, que em produção roda num timer a cada minuto e, em
desenvolvimento, **ninguém roda por você**: rode-o à mão depois de confirmar, e a mensagem sai no
terminal **do comando**, e não no do `runserver`. A chave `AVISOS_AOS_CANDIDATOS` vem ligada no
`development` e no `test`, e desligada em produção até a validação de LGPD.

**As jornadas da gestão de acessos (107) rodam num navegador de verdade, e pedem o grupo
`navegador`.** `uv sync --extra dev --extra navegador` traz o Playwright, e `uv run playwright install
chromium` o navegador. Sem a biblioteca, `tests/navegador/test_jornadas_de_acesso.py` pula inteiro —
**um pulado a mais**, como o tokenizer sem o `assistente` —; o CI instala os dois desde a `107`. Os
casos sobem o `live_server` e uma página de provedor servida pelo próprio teste
(`tests/navegador/provedor.py`): o adaptador continua o provedor simulado da `106`, e nada disso
existe fora da suíte. `make test-navegador` os roda com a janela aberta, para assistir. Duas
armadilhas já pagas: a interceptação do Playwright **não** alcança o destino de um redirecionamento —
por isso a página é um servidor, e não um `page.route` —; e o ORM chamado com o Playwright ativo
deixava uma sessão aberta no banco de teste, que travava o `DROP DATABASE` do fim — a fixture do
navegador fecha as conexões ao sair.

**O piloto do assistente (071) pede três coisas de fora do repositório, e sem elas não chama o
modelo.** O grupo opcional de dependências (`uv sync --extra dev --extra assistente`), que traz a
`tokenizers`; o `tokenizer.json` do modelo, baixado para fora do repositório e apontado em
`ASSISTENTE_TOKENIZER`; e, no OpenRouter, a credencial em `ASSISTENTE_CREDENCIAL`, lida de um arquivo
fora do repositório — **nunca** do `.env`, que um `manage.py` à mão nem lê. Faltando a biblioteca ou
o arquivo, toda pergunta termina em `SEM_TOKENIZER` ("falta o tokenizer do modelo"), sem chamada:
não é o serviço que caiu. O OpenRouter é só do desenvolvimento, e a única barreira de gasto é o
limite da própria chave, no painel dele: sem limite, a verificação de conexão acusa divergência e
não manda a conversa sintética. O corpus da avaliação se publica por
`scripts/publicar_corpus_do_piloto.py`, num banco **sem** `seed_demo`, cujo 01/2026 toma o número do
01/2026 do corpus. O roteiro inteiro está no quickstart da `071`.

**O assistente na página pública da seleção (074) é só local**, pela chave
`ASSISTENTE_NA_PAGINA_DO_EDITAL` — a entrada `assistente-074` do `.claude/launch.json` a liga. É a
visão do candidato sem a gestão; produção recusa subir com ela. As sugestões não chamam o modelo; a
pergunta livre chama, e custa.

**404 na gestão costuma ser autorização, não rota quebrada.** Reproduza com o papel exato do ator
antes de sair caçando URL.

**Estilo e script escritos no template não funcionam: a CSP os recusa.** Desde a `091` e a `092`,
`processo_seletivo/shared/politica_de_conteudo.py` responde todo HTML com `style-src 'self'` e
`script-src 'self'`, sem `unsafe-inline`. Um `style="..."`, um `<style>`, um `<script>` ou um `onclick=` no
template renderiza sem efeito e sem erro no servidor — a única pista é a violação no console do
navegador. Estilo vai para arquivo: a folha comum da gestão em `interface/static/interface/gestao/`
(sete arquivos, na ordem de `FOLHAS_DA_GESTAO`, em `shared/estaticos.py`), o de uma tela só em
`interface/grupos/` ou `interface/telas/`, pelo bloco `estilo_da_pagina`, e a do portal em
`portal/static/portal/portal.css`. Os guardiões que exigem regra para toda classe citada leem esses
arquivos. A página de falha de CSRF do próprio Django, que tem `<style>` embutido, foi a última
exceção: desde a `093` quem responde é `erros.falha_de_csrf`, na recusa da área.

**O código de acesso do portal sai no terminal do servidor.** Na execução nativa o backend de
e-mail é o de console: a mensagem é impressa onde o `runserver` está rodando, e não há outro lugar
de onde lê-la. No compose há um coletor de SMTP, e ela chega em <http://localhost:8025>.

**`lint` são dois passos.** `ruff check` **e** `ruff format --check`. Rodar só o primeiro declara
verde local e quebra no CI — já aconteceu com quatro checkpoints seguidos.

**PR de documentação também quebra o CI.** `tests/test_citacoes_de_requisito.py` varre
`backend/**/*.{py,html,js}` e `specs/**/*.md` e falha se alguma citação `FR-`, `SC-`, `UX-` ou
`D-` apontar para identificador que nenhuma spec define. Escreveu spec? Rode a suíte.

**No macOS com PostgreSQL do Homebrew, exporte `LC_ALL`.** `createdb` e `pg_ctl` falham sem ele.

## Convenções

- **Tudo em português**, inclusive nomes de módulo, modelo e teste. O domínio é normativo
  brasileiro e o vocabulário do código é o do domínio.
- **Comentário explica por quê, não o quê.** Os comentários deste repositório registram a decisão e
  o custo dela — o defeito que motivou a linha, a alternativa descartada. Siga o tom.
- **Cada incremento é uma pasta em `specs/`**, com spec, plan, tasks e os demais artefatos. Não
  invente requisito fora dela: a rastreabilidade é verificada por teste.
- **Governança é do usuário.** Achado encontrado no meio de uma feature vira registro, não escopo
  da seguinte.

## Verificação

```bash
cd backend && make lint check test-pg
```

`test-pg` e não `test` — ver *As armadilhas caras* acima. No ambiente containerizado, o mesmo
comando por `docker compose exec app`.
