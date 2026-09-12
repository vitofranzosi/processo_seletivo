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
migrations acabaram de criar. O comando informa quantas protegeu; se disser `0 de 18`, a segunda
passada não rodou.

**Migration desaplicada contamina a sessão inteira.** O sintoma é `relation ... does not exist` num
arquivo sorteado, longe da causa. Antes de investigar qualquer erro estranho, confira
`manage.py migrate --check`.

## As armadilhas caras

**O modo padrão da suíte não é confiável — rode contra PostgreSQL.** Sem variável nenhuma, a
suíte cai para SQLite: **21 falham e 182 são puladas** (medido em 2026-09-09). As falhas são SQL
de PostgreSQL — `ALTER TABLE ... DISABLE TRIGGER` — executando sob SQLite, em testes que deveriam
ter sido pulados e não foram. O CI não vê nada disso, porque só roda contra PostgreSQL. Ver
[doc/achado-suite-em-sqlite.md](doc/achado-suite-em-sqlite.md).

Contra PostgreSQL a suíte fecha em **4862 passando e 2 pulados** (medido em 2026-09-12). Os dois
pulados são deliberados e estão nomeados em
[doc/achado-fonte-real-do-sorteio-sem-gatilho.md](doc/achado-fonte-real-do-sorteio-sem-gatilho.md):
um só roda fora do PostgreSQL, e o outro é o E2E contra o serviço real da Caixa, atrás da chave
`SORTEIO_E2E_FONTE_REAL`. Para chegar lá é preciso o **par**:
`TEST_DB_ENGINE=postgresql` **e** `DB_USER`. Só o primeiro cai para SQLite; só o segundo tenta
conectar como a role de runtime, que não pode criar banco de teste. Nenhum dos dois casos avisa.

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
