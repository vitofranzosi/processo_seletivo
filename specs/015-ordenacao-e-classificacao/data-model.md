# Modelo de dados — 015 Ordenação e Classificação

**Fase 1.** Duas tabelas novas num app novo, duas linhas de elaboração no app `editais`, e o que
deliberadamente **não** é tabela.

## Elaboração — app `editais`

As linhas que produzem o conteúdo publicado, no molde exato de `ModalidadeConcorrencia`
(`editais/models/perfis.py:56-69`), que pende de `PerfilVaga` e viaja aninhada no snapshot.

### `MarcoClassificatorio`

| Campo | Forma | Nota |
|---|---|---|
| `id` | UUID, pk | identidade estável; é ela que a Retificação endereça |
| `perfil` | FK → `PerfilVaga`, CASCADE | remover o Perfil leva os marcos junto, como as modalidades |
| `code` | texto | único por Perfil, como `uq_modalidade_perfil_code` |
| `name` | texto | rótulo publicado |
| `operacao` | texto, escolhas | como as pontuações se combinam (FR-011) |
| `normalizacao` | texto, escolhas | declarada junto com a operação, e não inferida |
| `arredondamento` | JSON | mesma forma que `RegraNormativa.rounding` já usa |
| `etapas` | lista de UUID | as Etapas enumeradas, por identidade publicada (FR-008) |

`etapas` guarda identidade do conteúdo publicado, e **não** FK para a linha de elaboração — pela
mesma razão que `ResultadoEtapa.etapa_id` não é FK: existe Etapa real no Edital vigente sem linha
correspondente, porque a Retificação sabe acrescentar item a coleção e não escreve de volta em
`editais`.

**O peso não está aqui.** Ele é lido de `Etapa.weight`, que continua sendo a fonte autoritativa
(FR-009). Copiá-lo criaria duas respostas para a mesma pergunta.

### `CriterioDesempate`

| Campo | Forma | Nota |
|---|---|---|
| `id` | UUID, pk | endereçado pela Retificação |
| `marco` | FK → `MarcoClassificatorio`, CASCADE | |
| `ordem` | inteiro | **publicada** como campo, única no marco; a ordem é a norma (FR-014, FR-015) |
| `tipo` | texto, escolhas | tipo executável que o motor sabe interpretar (D-004) |
| `parametros` | JSON | Etapa referida, fato referido, sentido da comparação |
| `quando_ausente` | texto, escolhas | obrigatório: o que fazer quando o valor não existe (FR-018) |

`quando_ausente` não é anulável, e essa é a diferença entre a regra estar declarada e o cálculo
inventar semântica. Uma inscrição submetida antes de o Edital declarar um fato não o congelou; uma
Etapa decisória não produz número.

## O ato — app `classificacao`

### `AtoDeOrdenacao`

| Campo | Forma | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `edital` | FK → `Edital`, PROTECT | |
| `perfil_id` | UUID | identidade publicada do Perfil |
| `marco_id` | UUID | identidade publicada do marco |
| `versao` | FK → `VersaoConsolidada`, PROTECT | a norma que governou o cálculo (FR-003) |
| `ato_anterior` | FK → `self`, nulo, PROTECT, **único** | o ato que este sucede; nulo no primeiro |
| `motivo_da_sucessao` | texto | exigido quando `ato_anterior` não é nulo (FR-034) |
| `universo` | JSON | resumo declarado: participantes considerados e Resultados que entraram |
| `emitido_por` | texto | subject do ator |
| `emitido_em` | instante | `ctx.now` da transação |

**Vigente não é campo, e isso não é elegância — é privilégio.** A tabela entra em
`TABELAS_APPEND_ONLY`, e a política de papéis roda `REVOKE UPDATE, DELETE` sobre cada uma delas
(`seguranca/papeis.py:129`): o papel de runtime **não tem `UPDATE`**. Um desenho que virasse um
booleano `vigente` na emissão do sucessor seria impossível em produção, e nenhuma exceção em trigger
resolveria — a falta é de privilégio, não de regra. A sucessão é, portanto, **linha nova apontando a
anterior**, e o vigente é derivado: o ato que ninguém sucedeu (FR-032, FR-033).

`universo` é resumo, e não cópia: identifica os Resultados que entraram e a versão que governou, de
modo que a comparação de obsolescência (T-011) seja consulta de custo constante e que a reprodução
(FR-046) não precise do estado vigente.

### `PosicaoNaOrdem`

| Campo | Forma | Nota |
|---|---|---|
| `id` | UUID, pk | |
| `ato` | FK → `AtoDeOrdenacao`, CASCADE | |
| `inscricao` | FK → `Inscricao`, PROTECT | |
| `posicao` | inteiro, nulo | **nulo** para participante considerado sem posição (FR-007) |
| `pontuacao_combinada` | decimal, nulo | o valor que colocou ali |
| `modalidade_id` | UUID, nulo | declarada na inscrição, não verificada (FR-005) |
| `consequencia` | texto | copiada do Resultado, para o considerado sem posição |
| `motivo` | texto | por que não tem posição, quando não tem |
| `empate_residual` | booleano | compartilha posição, e não há ordem normativa no grupo |
| `desempate` | JSON | critério a critério: qual foi aplicado e com que valores (FR-050) |

`posicao` anulável é o que faz FR-007 e SC-017 fecharem: o universo inteiro está na tabela, a ordem
contém só os classificáveis, e a soma das duas partes é o total.

## Constraints

| Nome | O que impede |
|---|---|
| `uq_ato_raiz_por_marco` | unicidade **parcial** (`WHERE ato_anterior IS NULL`) — dois primeiros atos no mesmo marco (FR-031) |
| `uq_ato_sucessor_unico` | unicidade sobre `ato_anterior` — dois sucessores do mesmo ato, que bifurcariam a cadeia |
| `uq_posicao_por_ato_inscricao` | a mesma inscrição duas vezes no mesmo ato |
| `ck_posicao_ou_motivo` | posição nula sem motivo, ou posição atribuída com motivo de exclusão |
| `ck_sucessao_com_motivo` | sucessão sem motivo declarado |
| `uq_marco_perfil_code` | código de marco repetido no mesmo Perfil |
| `uq_criterio_marco_ordem` | dois critérios com a mesma ordem — a ordem é a norma |

## Triggers

Duas, no molde de `resultados/migrations/0001_initial.py:23-63`, ambas guardadas por
`vendor == "postgresql"` e reversíveis por `DROP … IF EXISTS`:

- **`ato_de_ordenacao_append_only`** — `BEFORE UPDATE OR DELETE`, **sem exceção alguma**. A primeira
  redação abria uma exceção para a transição de vigente para sucedido; ela era impossível de exercer
  (o runtime não tem `UPDATE`) e desnecessária depois que a sucessão passou a ser linha nova;
- **`posicao_coerente`** — `BEFORE INSERT`. Confere que a inscrição pertence ao mesmo Edital e Perfil
  do ato. Sem ela, a append-only apenas congelaria o erro — é o argumento textual da 013, e vale
  igual porque a posição afirma coisas sobre linhas de outra tabela.

Os dois nomes entram em `TRIGGERS_POR_APP` (`tests/migrations/test_migrations.py:21-38`); as duas
tabelas entram em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py:26-41`).

## O que **não** é persistido

- **vigente** — é o ato que ninguém sucedeu, derivado de `ato_anterior`. Ver acima: gravá-lo exigiria
  um `UPDATE` que o papel de runtime não tem;
- **obsoleto** e **não recomputável** — são fatos sobre o mundo de agora, derivados na leitura
  comparando o `universo` gravado com o vigente. Persistir criaria estado a manter e um segundo lugar
  onde a verdade pode divergir;
- **a ordem calculada e não emitida** — FR-022 proíbe que o cálculo grave;
- **o peso da Etapa** — lido de `Etapa.weight` (FR-009);
- **a norma do marco** — o ato aponta a `VersaoConsolidada`; copiar a regra abriria uma segunda forma
  de o ato se contradizer. É essa âncora que mantém o ato **reproduzível mesmo quando o marco não
  existe mais no conteúdo vigente** (FR-042).

## Relação com o que já existe

`ResultadoEtapa` é lido e nunca escrito (FR-054). `Inscricao` é referenciada por FK com `PROTECT`.
`VersaoConsolidada` ancora a norma. Nenhuma migration nos apps `resultados`, `avaliacoes`,
`inscricoes` ou `auditoria`.
