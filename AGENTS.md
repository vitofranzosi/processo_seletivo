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
- **Nada é excluído.** Não escreva migration que apague dado normativo, nem comando que o faça.
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
— eram 18, são **33** — e é por isso que a armadilha é o zero, e não o total.

**Migration desaplicada contamina a sessão inteira.** O sintoma é `relation ... does not exist` num
arquivo sorteado, longe da causa. Antes de investigar qualquer erro estranho, confira
`manage.py migrate --check`.

## As armadilhas caras

**O modo padrão da suíte não é confiável — rode contra PostgreSQL.** Sem variável nenhuma, a
suíte cai para SQLite: **35 falham, ~7326 passam e 243 são puladas** (medido em 2026-09-21).
Todas deveriam ter sido puladas e não foram, e a causa se reparte em três — o achado original
([doc/achado-suite-em-sqlite.md](doc/achado-suite-em-sqlite.md), de 09/09) nomeava só a primeira,
quando eram 21:

| Quantas | Por que |
|---|---|
| 14 | SQL que só o PostgreSQL entende — `near "DISABLE": syntax error`, de `ALTER TABLE ... DISABLE TRIGGER` |
| 9 | a mensagem do SQLite não nomeia a constraint, e o `pytest.raises(match=...)` não casa |
| 11 | garantia que o SQLite não tem — gatilho ausente (`DID NOT RAISE`, 5), transação que não tranca (3) e erro de constraint que escapa cru (3) |

**O total neste modo não é reprodutível, e o `~` acima é literal**: duas execuções seguidas de um
mesmo commit, em 09/20, deram 7211 e 7212 passando, com 1 e 2 erros. Cinco falhas do `portal` não
se repetiram ao rodar os mesmos arquivos isolados, e não há plugin de ordem aleatória instalado —
de modo que há acoplamento entre casos que só aparece aqui. Não investigue por este caminho: a
repartição acima é o que importa, e nenhuma das três colunas é defeito de produto.

**Ao atualizar estes números, atualize as falhas e os pulados junto — e desconfie se mudarem.**
Entre 09/20 e 09/21 o total subiu **115** casos, e as duas outras contagens ficaram onde estavam:
35 e 243. É o que se espera, porque as três causas são do vendor e não do produto, e teste novo
não entra nelas. Uma delas mexendo é sinal de que alguém escreveu SQL de PostgreSQL num caminho
que antes não tinha — e aí vale investigar, ao contrário do total.

O CI não vê nada disso, porque só roda contra PostgreSQL.

Contra PostgreSQL a suíte fecha em **7594 passando e 11 pulados** (medido em 2026-09-21). Os onze
são deliberados, e se repartem em três: **9** são pares *termo × template* que
`test_vocabulario_da_composicao.py` pula quando a tela não usa aquele termo em texto visível; **1**
é a recusa por vendor, que só aparece fora do PostgreSQL; e **1** é o E2E contra o serviço real da
Caixa, atrás da chave `SORTEIO_E2E_FONTE_REAL`. Os dois últimos estão nomeados em
[doc/achado-fonte-real-do-sorteio-sem-gatilho.md](doc/achado-fonte-real-do-sorteio-sem-gatilho.md).

Para chegar lá é preciso o **par**:
`TEST_DB_ENGINE=postgresql` **e** `DB_USER`. Só o primeiro cai para SQLite; só o segundo tenta
conectar como a role de runtime, que não pode criar banco de teste. Nenhum dos dois casos avisa.

**A suíte leva ~12 minutos, e a preparação do banco não tem nada com isso.** Criar o banco de teste
e aplicar as 80 migrations custa **~2 segundos** — medido em 2026-09-20, isolando a preparação com
`--reuse-db` sobre um caso só. O custo está nos **791 casos que declaram `transaction=True`**, em 292
dos 609 arquivos de teste: eles não podem terminar em `ROLLBACK`, e o Django limpa truncando as
tabelas depois de cada um. São ~10% dos casos, e é o décimo caro. Não é desleixo de quem os
escreveu: é consequência de as garantias deste sistema morarem no banco — gatilho append-only,
privilégio ausente e `select_for_update` que realmente tranca não são observáveis dentro de uma
transação que vai ser desfeita.

**`--reuse-db` não economiza nada, e já foi medido — não repita o experimento.** Duas rodadas com a
bandeira ligada deram 670s e 686s, contra 733s sem ela; e a segunda, que **reusava** o banco, saiu
mais lenta que a primeira, que o **criou**. A variação entre rodadas idênticas é de ~60s, uma ordem
de grandeza acima do que a bandeira poupa. Ela trocaria 2 segundos por um banco que envelhece em
silêncio quando uma migration muda.

**Um banco de teste por worktree.** Suítes paralelas disputam `test_processo_seletivo` e se
derrubam. Passe um `DB_NAME` próprio quando houver mais de uma sessão.

**`/gestao/` não abre sem o seletor de identidade.** Sem `INTERFACE_SELETOR_IDENTIDADE=true` o
runserver local devolve 503. O portal do candidato precisa de `PORTAL_IDENTIDADE_DEMO=true` pelo
mesmo motivo. Os dois deixam qualquer pessoa declarar quem é, e produção recusa subir com eles.

**404 na gestão costuma ser autorização, não rota quebrada.** Reproduza com o papel exato do ator
antes de sair caçando URL.

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
