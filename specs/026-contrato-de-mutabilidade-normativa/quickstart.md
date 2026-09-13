# Quickstart — como se verifica que o contrato existe e funciona

Guia de validação, não de implementação. Cada seção prova um pedaço do que a spec promete, e as
quatro últimas são as jornadas do gate de conclusão (D-009): pelo canal do ator, sem API e sem
banco.

A forma do contrato está em [contracts/mutabilidade.md](contracts/mutabilidade.md); as entidades,
em [data-model.md](data-model.md).

## Pré-requisitos

```bash
cd backend && uv sync --extra dev
```

Banco preparado nos três passos — provisionar, migrar, provisionar de novo. A segunda passada é a
que concede privilégio sobre as tabelas que as migrations acabaram de criar:

```bash
cd backend && make preparar
```

**Um banco de teste por worktree.** Se houver outra sessão rodando a suíte, passe um `DB_NAME`
próprio; do contrário as duas disputam `test_processo_seletivo` e se derrubam com erros que não
têm nada a ver com a feature.

---

## 1. O guardião existe e falha por omissão — SC-095, SC-096

```bash
cd backend && make test-pg
```

Verde é a condição de partida: **zero campos da forma publicada sem natureza declarada**.

Para provar que ele falha quando deve — que é o que importa num guardião —, acrescente um campo ao
conteúdo publicado sem tocar em `mutabilidade.py` e rode de novo. A suíte precisa falhar **nomeando
o campo e o caminho onde ele apareceu**. Uma falha que diga apenas "contagem divergente" não
atende: quem quebrou a suíte precisa saber qual decisão faltou.

Depois desfaça o campo experimental. A recíproca vale igual: declarar natureza para um campo que o
conteúdo não carrega também derruba a suíte (FR-302).

## 2. Toda exclusão tem razão, e nenhuma é técnica — SC-101

```bash
cd backend && uv run pytest tests/contract/test_mutabilidade.py -k razao -v
```

O teste confere que toda `NAO_RETIFICAVEL` carrega razão não vazia. O que ele **não** consegue
conferir é se a razão é normativa ou técnica — isso é leitura humana, e é o trabalho da fase D do
plano. A verificação de SC-101 termina lendo as razões:

```bash
cd backend && grep -n 'NAO_RETIFICAVEL' -A 2 processo_seletivo/editais/domain/mutabilidade.py
```

Uma razão que descreva limitação de implementação — "a tela publicaria valor que o cálculo não
interpreta" — reprova. Ela deixa de valer quando a limitação some, e ninguém percebe.

---

## As quatro jornadas

Todas pela interface administrativa, com um Edital **publicado**. Subir o ambiente exige o seletor
de identidade; sem ele `/gestao/` devolve 503:

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_NAME=ps_demo_026 DB_USER="$(whoami)" DB_RUNTIME_USER="$(whoami)" \
  INTERFACE_SELETOR_IDENTIDADE=true PORTAL_IDENTIDADE_DEMO=true \
  uv run python manage.py runserver 8026
```

Direto pelo `manage.py`, e não por `make runserver`: o Makefile faz `include`/`export` do `.env`, e
variável passada na linha de comando de um alvo não sobrevive a isso. `PORTAL_IDENTIDADE_DEMO` é o
que a jornada 3 precisa, porque o passo 4 é lido pelo portal do candidato.

Um Edital publicado com marco, sorteio declarado e prazo recursal não sai do `seed_demo` pronto —
monte o certame pela interface. Ponto de partida: **Gestão → Processos → o Edital publicado →
Retificar**.

### Jornada 1 — corrigir o local de uma prova — SC-097

1. Abrir a Retificação do Edital publicado.
2. No bloco do Cronograma, localizar o Evento da prova e **o campo de local**.
3. Alterar o local, justificar, homologar e publicar a Retificação.
4. Abrir a página pública do Edital: o local novo aparece; o anterior continua legível na versão
   consolidada anterior.

**Falha hoje no passo 2**: o campo não existe na tela. E o achado é mais fundo — `location` é
emitido no conteúdo publicado por `publicacoes/application/publish_edital.py:261` e **não está
declarado** em `EVENTO_PUBLICADO` (`editais/domain/validation.py`). Nenhum teste acusa, porque o
guardião de hoje confere coleções e não campos.

### Jornada 2 — corrigir um requisito de participação — SC-098

1. Retificação → bloco do Perfil → **requisitos de participação**.
2. Corrigir o texto do requisito, justificar, homologar, publicar.
3. A página pública do Perfil mostra o requisito corrigido.

O que esta jornada prova além do campo: item de lista não tem identidade estável, e o ato precisa
registrar **o que** mudou de forma que a versão consolidada anterior continue legível.

### Jornada 3 — corrigir o prazo recursal — SC-099

1. Retificação → bloco do marco classificatório → **janela recursal**.
2. Alterar a duração em dias. A unidade é **lista fechada** e precisa aparecer como escolha, nunca
   como caixa de texto (FR-311).
3. Publicar a Retificação.
4. No portal, o candidato lê a **data-limite** recalculada a partir da divulgação do resultado.

Contradição que a tela precisa recusar pelo mesmo critério da elaboração: marco que declara não
admitir recurso não tem duração a declarar.

### Jornada 4 — corrigir o método do sorteio — SC-100

1. Retificação → bloco do marco → **método do sorteio**, campo a campo: `algorithm`, `source`,
   `occurrence`, `occurrenceAt`, `derivation`, `qualifyingStageId`, e o par `rule`/`text` de
   `normalization` e de `substitutionRule`.
2. Publicar a Retificação.
3. Abrir um sorteio **já realizado** sob o método anterior: a verificação continua conferindo.

O passo 3 já está estruturalmente garantido e o que falta é o teste de fronteira que o declare:
`sorteios/models.py:48` grava `metodo_hash` em `RelacaoDeHabilitados` no congelamento, e
`models.py:213` o copia e confere no `Sorteio`. A relação congelada **não relê** o método vigente.

---

## 3. A tela diz o que não alcança — SC-102

Com a Retificação aberta num Edital com marco declarado, o bloco do marco precisa dizer quais
campos daquela entidade a Retificação não alcança, **e por quê**.

Uma vez por bloco de coleção, e não por campo: explicação que não muda de um cartão para o outro
não se imprime uma vez por cartão — é a decisão que `tests/interface/test_medida_dos_campos.py` já
guarda no assistente.

---

## Verificação final

```bash
cd backend && make lint check test-pg
```

`lint` são dois passos (`ruff check` **e** `ruff format --check`), e `test-pg` e não `test` — no
modo padrão a suíte cai para SQLite e falha em casos que nada têm a ver com a feature.

Esta spec escreve `specs/`, então a varredura de citações também precisa passar: todo `FR-`, `SC-`
e `D-` citado em código ou teste tem de apontar para identificador que alguma spec define.
