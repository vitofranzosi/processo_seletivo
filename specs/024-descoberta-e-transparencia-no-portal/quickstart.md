# Quickstart — validando Descoberta e Transparência no Portal Público

Guia de validação de ponta a ponta, pelo canal do ator: **o portal público, sem sessão**. É o que o
Princípio VI exige — e aqui a exigência é literal, porque `FR-150` diz que nenhuma tela desta
feature pode pedir identificação. Se em algum passo você precisou entrar, a feature falhou.

---

## Preparação

**Um banco por sessão.** Suítes e demonstrações paralelas disputam o mesmo banco e se derrubam;
passe um `DB_NAME` próprio. O que a implementação usou:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 createdb ps_demo_024
```

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_024 POSTGRES_USER=$USER \
  DB_MIGRATION_USER=ps_migracao_024 DB_MIGRATION_PASSWORD=migra \
  DB_RUNTIME_USER=ps_runtime_024 DB_RUNTIME_PASSWORD=runtime make preparar
```

Provisionar, migrar, provisionar de novo — a segunda passada concede privilégio sobre as tabelas que
as migrations acabaram de criar. Antes de investigar qualquer erro estranho, confira
`manage.py migrate --check`: migration desaplicada aparece como `relation ... does not exist` num
arquivo sorteado, longe da causa.

### O catálogo que este roteiro exige

Quatro situações e um Edital retificado. Três vêm de comando; a quarta é montada pela interface.

```bash
cd backend && make seed
```

O `seed_demo` cria um Processo **publicado e retificado** — e são **duas** Retificações, que é
exatamente o que a `US2` precisa:

| Retificação | O que altera | Vigência |
|---|---|---|
| a | vagas imediatas do primeiro Perfil | imediata |
| b | término do primeiro Evento do cronograma | daqui a 15 dias |

As duas cobrem os dois tradutores que a `T-002` exige — Perfil e Evento — e a segunda produz, de
graça, o caso de borda de **Retificação publicada com vigência futura**.

```bash
cd backend && uv run python manage.py seed_demo --codigo PS-ENCERRADO --numero 02 --dias-atras 60
```

Uma seleção com o prazo já vencido, para a situação `encerrada`.

**A seleção `futura` é montada à mão**, pela gestão: elabore um Edital com o Evento de inscrições
começando daqui a alguns dias, homologue e publique. Não há opção de comando para ela, e montar pela
interface é o caminho do ator de qualquer forma.

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_024 DB_USER=$USER DB_RUNTIME_USER=$USER \
  INTERFACE_SELETOR_IDENTIDADE=true PORTAL_IDENTIDADE_DEMO=true \
  uv run python manage.py runserver 8024
```

A gestão exige `INTERFACE_SELETOR_IDENTIDADE=true`; sem isso `/gestao/` devolve 503. E nada carrega
`backend/.env` sozinho — quem o lê é o `make`, e por isso as variáveis vão na própria linha.

Há também a entrada `portal-024` em `.claude/launch.json`, que sobe exatamente esse comando.

> **Abra o portal numa janela anônima.** É a única forma de garantir que nenhum passo abaixo está
> passando por causa de uma sessão que ficou aberta.

---

## Roteiro 1 — O cronograma, antes de decidir (`US1`)

1. Abra a vitrine, **sem sessão**.
2. Abra a seleção do `seed_demo`.

**Confira:**

- os Eventos aparecem na ordem publicada, cada um com o período declarado — `FR-125`;
- cada Evento traz situação própria: concluído, em curso ou por vir — `FR-126`;
- a situação fala **do Evento**. Nenhuma frase desta seção diz o que *você* deve fazer — `FR-126`;
- onde o Edital declarou local, ele aparece; onde não declarou, não há linha — `FR-127`;
- em nenhum momento a página pediu identificação — `FR-150`.

**A contraprova da `FR-128` não é percorrível, e isso é achado.** Não dá para publicar um Edital sem
Evento: `schedule_required` é impeditivo, e a submissão é recusada antes da homologação. O guarda
continua valendo para conteúdo publicado antes de a regra existir, e quem o verifica é
`tests/integration/portal/test_cronograma_publico.py`, renderizando o template com a lista vazia.
Está registrado na §7 da [spec](spec.md).

---

## Roteiro 2 — Saber que o Edital mudou (`US2`)

1. Na mesma seleção do `seed_demo`, vá a **Edital e documentos**, no fim da página.

**Confira:**

- há **três** linhas de ato: a abertura e as duas Retificações, do mais recente para o mais
  antigo, cada uma com a data de publicação — `FR-129`;
- abrindo **O que mudou** de uma Retificação, aparecem a justificativa publicada e o que foi
  alterado — `FR-130`;
- o que mudou está dito em português: `Perfil "…" — vagas imediatas` e
  `Cronograma — Evento "…" — término`. **Nenhum `/profiles/id=…` na tela** — `FR-130`, `D-005`;
- o conteúdo exibido está identificado como o vigente — `FR-131`;
- o documento de cada ato é alcançável a partir da própria linha — `FR-132`.

**O caso de borda que o seed dá de graça.** A Retificação `b` foi publicada agora e só vale daqui a
15 dias. Confira que:

- ela aparece no histórico como **publicada**, com a data em que passa a valer;
- e o cronograma da página **ainda mostra o término antigo** — porque é o que vale hoje.

Publicar e entrar em vigor são instantes distintos. Se a página já mostrar o término novo, ela está
exibindo conteúdo que ainda não vigora — defeito de `FR-131`.

**Contraprova.** Abra uma seleção nunca retificada. Não deve haver seção de histórico nem frase
dizendo que não houve retificação — `FR-133`.

---

## Roteiro 3 — Entender a vaga sem abrir o PDF (`US3`)

1. Na página da seleção, percorra os Perfis.

**Confira:**

- atribuições, carga horária e remuneração aparecem quando o Edital as declarou — `FR-134`;
- Perfil que não declarou algum dos três **não** ganha rótulo vazio nem "não informado" — `FR-135`;
- o convite de inscrição continua sendo o de sempre, com os três estados — inalterado;
- antes de acionar o convite, a página já disse que inscrever-se exige identificação — `FR-137`.

**O caso que motivou a `D-007`.** Publique um Perfil com **zero** vagas imediatas e cadastro reserva
ilimitado. Confira que:

- a leitura principal é a **oferta** — cadastro reserva —, e não o número zero;
- o número de vagas imediatas continua dito, em posição secundária;
- o convite continua disponível — `FR-136`.

**Contraprova.** Gere o documento publicado do mesmo Edital. O texto do PDF sobre o cadastro reserva
**não** mudou: documento publicado não se reescreve, e a divergência de redação entre o ato e a
página é declarada na `T-010`.

---

## Roteiro 4 — Encontrar sem ler tudo (`US4`)

1. Volte à vitrine.
2. Busque por um termo que apareça na denominação de um Perfil.

**Confira:**

- só as seleções cujo texto público contém o termo permanecem, e a tela diz **quantas** — um número
  só, do total encontrado, e não um por grupo — `FR-141`;
- os cabeçalhos de grupo **somem**: com consulta ativa a lista é única e ordenada, e cada cartão
  continua trazendo a marca da própria situação — `FR-146a`, `FR-145`. *Quatro cabeçalhos sobre um
  cartão cada seria ruído; sem consulta, os grupos voltam*
- o termo procurado aparece em cada cartão devolvido. Resultado em que ele não aparece em lugar
  nenhum é a falha que a `T-011` existe para evitar;
- busca com acento e sem acento devolvem o mesmo — `T-005`;
- aplique um filtro por cima: os dois se somam, e a contagem cai — `FR-139`;
- há caminho visível para limpar — `FR-141`.

**Confira o endereço:**

- a consulta inteira está nele — `FR-143`;
- copie o endereço para outra janela anônima: a mesma lista aparece — `SC-045`;
- abra uma seleção e volte: a consulta continua aplicada — `FR-144`.

**Contraprova 1.** Busque por algo que não existe. A tela diz o que foi procurado e oferece a volta
ao catálogo — e **não** trata isso como erro — `FR-142`.

**Contraprova 2.** Edite o endereço à mão pondo `situacao=banana` e `ordem=xyz`. A página devolve o
catálogo sem aqueles filtros, sem mensagem de erro e sem 4xx — `T-004`.

---

## Roteiro 5 — As quatro situações (`US5`)

1. Com as quatro seleções publicadas, abra a vitrine sem consulta.

**Confira:**

- cada seleção traz a situação como marca explícita — `FR-145`;
- futuras e encerradas **não** estão no mesmo grupo — `FR-146`;
- a aberta traz data-limite exata **e** prazo restante — `FR-147`;
- a encerrada tem caminho visível para ser consultada — `FR-148`;
- a que não recebe inscrição por este sistema **não** é chamada de encerrada, e não tem frase de
  prazo alguma — `FR-149`.

**Contraprova.** Cancele um Edital pela gestão. Ele some da vitrine e de qualquer resultado de
consulta, e continua alcançável pelo endereço direto — `FR-152`.

---

## Verificação final

```bash
cd backend && make lint check test-pg
```

`test-pg`, e não `test`: sem `TEST_DB_ENGINE=postgresql` **e** a role certa, a suíte cai para SQLite
e 21 casos falham por SQL de PostgreSQL rodando onde não deveria. E `lint` são dois passos —
`ruff check` **e** `ruff format --check`; rodar só o primeiro declara verde local e quebra no CI.

Havendo mais de uma sessão trabalhando ao mesmo tempo, passe um `DB_NAME` próprio: suítes paralelas
disputam `test_processo_seletivo` e se derrubam.

**A spec toca `specs/`, então a suíte de citações precisa rodar:**
`tests/test_citacoes_de_requisito.py` varre `specs/**/*.md` e falha se alguma citação `FR-`, `SC-`,
`UX-` ou `D-` apontar para identificador que nenhuma spec define.

---

## Os sete invariantes, conferidos de uma vez

Ao fim do percurso, nenhum destes pode ter sido violado (§5 da spec):

1. nenhuma tela pediu identificação;
2. nada exibido foi produzido pela feature — tudo tem origem num ato publicado;
3. o conteúdo exibido é o vigente, e não houve duas leituras concorrentes do que vale;
4. nenhuma ausência de dado virou afirmação sobre o Edital;
5. toda situação exibida descreveu a seleção ou o Evento, nunca você;
6. toda consulta foi reproduzível pelo endereço;
7. nenhuma seleção cancelada apareceu em lista ou resultado.
