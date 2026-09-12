# Quickstart — validando a Supervisão do Processo

Guia de validação de ponta a ponta, pelo canal do ator: a interface administrativa, com o papel de
quem preside. Sem manipulação de banco e sem shell — é o que o Princípio VI exige.

---

## Preparação

```bash
cd backend && make preparar
```

A preparação é **provisionar, migrar, provisionar de novo** — a segunda passada é a que concede
privilégio sobre as tabelas que as migrations acabaram de criar. Confira `migrate --check` antes de
investigar qualquer erro estranho.

```bash
cd backend && make runserver
```

A interface exige `INTERFACE_SELETOR_IDENTIDADE=true`; sem isso `/gestao/` devolve 503. E lembre que
nada carrega `backend/.env` sozinho: quem o lê é o `make` e o `docker compose`.

Um Processo com **dois Editais** é o mínimo para exercitar `FR-011` e `FR-020` — prazo aberto e
resultado divulgado não cabem no mesmo Edital.

---

## Roteiro 1 — O pulso, e a soma que não existia (`US1`)

1. Identifique-se como a **presidência** do Processo.
2. Abra o Processo e alcance a supervisão.

**Confira:**

- o total de submetidas é a **soma** dos dois Editais — `SC-002`;
- cada Edital aparece **nomeado**, mesmo que um deles tenha zero — `FR-011`;
- rascunhos aparecem separados e **não** entram no total — `FR-012`, `SC-003`;
- o prazo de inscrições nomeia o Edital, e nenhuma data é apresentada como sendo do Processo —
  `FR-020`, `SC-007`;
- há instante de leitura na página — `FR-009`;
- **não há percentual algum sobre inscrição** — `FR-017`, `SC-005`.

**Contraprova.** Abra a tela de inscrições de cada Edital e some os dois totais à mão. Os números
têm de bater. Divergência aqui é defeito de agregação, não de arredondamento.

---

## Roteiro 2 — A curva, e o que ela não conta (`US2`)

1. Submeta inscrições em **três dias distintos** dentro do período.
2. Deixe pelo menos um rascunho aberto e **não** o submeta.
3. Recarregue a supervisão.

**Confira:**

- a série tem um ponto por dia do período, inclusive dias com zero;
- o rascunho **não** aparece na série — `FR-015`;
- o volume das últimas 24 horas confere com o que você acabou de submeter — `FR-013`;
- a série tem equivalente textual com os mesmos valores — `FR-016`, `SC-015`;
- a página não rola na horizontal em 375 px de largura — `FR-016`.

**Contraprova de `FR-015`.** Um rascunho criado há dias e nunca submetido não pode deslocar nenhum
ponto da série. Se deslocar, a agregação está usando o instante errado.

---

## Roteiro 3 — Os cinco sinais, um a um (`US3`)

Monte cada condição, confira o sinal, **desfaça** e confira que ele some sem deixar seção vazia
(`FR-025`, `SC-011`).

### `UX-001` — Etapa sem marco no cronograma

1. No assistente, deixe uma Etapa **sem** Evento vinculado e publique o Edital.
2. Confira: a Etapa aparece como **sem marco no cronograma**, nomeando o Edital.
3. Confira o que **não** aparece: atrasada, aguardando, progresso zero — `SC-008`.
4. Vincule o Evento por Retificação; o sinal some.

### `UX-002` — Declarado × temporal

1. Deixe um Evento como `PLANEJADO` com `end_at` no passado.
2. Confira: o sinal apresenta **as duas** informações — `SC-009`.
3. Confira que a supervisão **não** mudou o `status` do Evento — `FR-023`.
4. Marque o Evento como `CANCELADO`: o sinal some, porque cancelado sai da leitura temporal.

**Contraprova.** Um Evento **sem** `end_at` não produz sinal. Sem término não há posição a comparar,
e tratar a ausência como divergência encheria o painel de ruído sobre a forma normal do dado.

### `UX-003` — Cobertura insuficiente

1. Numa Etapa com avaliações previstas declaradas, distribua **menos** avaliadores do que o previsto
   para pelo menos uma inscrição.
2. Confira: o sinal nomeia Etapa e Edital, com numerador e denominador — `FR-032`, `SC-004`.
3. Confira que a supervisão **não** lista as inscrições carentes — `FR-037`.
4. Siga o encaminhamento: chega à distribuição da Etapa, onde o recorte já existe — `FR-035`.

**Contraprova de `FR-033`.** Uma inscrição sem nenhum avaliador tem de contar como carente e
permanecer no denominador. Se o denominador encolher junto, o número mente para melhor.

### `UX-004` — Ato vigente obsoleto

1. Emita o ato de ordenação de um marco.
2. Produza entrada nova que altere o universo — um Resultado consolidado depois da emissão.
3. Confira: o sinal aparece na supervisão **sem** abrir o marco.
4. Siga o encaminhamento: chega à ordenação, onde a divergência já é diagnosticada.

**Contraprova de `T-003`.** Um fato posterior que **não** altere o universo do marco **não** pode
produzir sinal. Se produzir, a confirmação exata não está sendo feita e o painel dá alarme falso.

### `UX-005` — Comissão inteira impedida

1. Com uma comissão pequena, faça com que **todos** os membros ativos tenham autoria de ato sobre o
   objeto atacado — avaliar, consolidar, emitir ou publicar.
2. Interponha recurso e deixe-o pendente.
3. Confira: o sinal nomeia a condição — `SC-010`.
4. Confira a redação: ela **não** afirma que o julgamento é impossível — `FR-030a`.
5. Acrescente à comissão um membro sem autoria: o sinal some.

**Contraprova de `FR-031`.** Com dezenas de recursos pendentes, a página não pode ficar
perceptivelmente mais lenta. O impedimento é calculado por conjuntos, e não por par.

### Ausência

Desfeitas as cinco condições, a região de atenção ocupa **uma linha** e não apresenta seção por
sinal — `FR-025`, `SC-011`.

---

## Roteiro 4 — Alcance e supressão (`US4`)

1. Identifique-se com um papel que preside o Processo mas **não** alcança a tela de recursos.
2. Monte a condição de `UX-005`.

**Confira:**

- o sinal **não** aparece — `FR-004`;
- **nada** indica que ele foi suprimido — `SC-013`;
- os demais sinais, cujos destinos você alcança, continuam aparecendo.

3. Identifique-se com alguém **sem** vínculo com o Processo e tente a mesma URL.

**Confira:** a resposta é a mesma de um Processo inexistente — `SC-012`. Compare as duas
literalmente: se diferirem em qualquer detalhe, a distinção vaza.

---

## Roteiro 5 — A fronteira (`D-007`)

Não é roteiro de tela; é a conferência que fecha a feature.

```bash
cd backend && uv run python manage.py makemigrations --check --dry-run
```

**Nenhuma migration pendente.** A supervisão não acrescenta estrutura persistente — `SC-014`. Se
este comando pedir migration, a fronteira foi atravessada e a spec precisa ser revista antes do
código.

Confira também, por leitura do diff, que a feature não contém `save`, `create`, `update` ou `delete`
— `FR-006`.

---

## Verificação final

```bash
cd backend && make lint check test-pg
```

`test-pg`, e não `test`: sem `TEST_DB_ENGINE=postgresql` **e** `DB_USER`, a suíte cai para SQLite e
mente. Num ambiente com mais de uma worktree, passe um `DB_NAME` próprio — suítes paralelas disputam
o mesmo banco de teste e se derrubam.

`lint` são **dois** passos: `ruff check` e `ruff format --check`.

E, tendo esta feature tocado `specs/`, a varredura de citações precisa passar — ela lê
`specs/**/*.md` e falha se algum `FR-`, `SC-`, `UX-` ou `D-` apontar para identificador que nenhuma
spec define.

---

## Gate de conclusão

A feature está pronta quando os cinco roteiros passam, `SC-001` é observável numa única tela, e
nenhuma migration foi criada. A demonstração ocorre pela interface administrativa, com o papel exato
de quem preside — demonstrar por chamada manual o que o canal do ator não oferece não satisfaz o
Princípio VI.
