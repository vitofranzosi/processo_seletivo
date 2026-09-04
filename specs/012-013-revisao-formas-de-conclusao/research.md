# Research: revisão de compatibilidade 012–013

**Revisão**: `012-013-revisao-formas-de-conclusao` | **Data**: 2026-09-03 | **Escopo**: [spec.md](./spec.md)

As decisões abaixo são **técnicas**, e levam o prefixo `TR-` para não colidir com os `T-` da 012 e
da 013, que continuam valendo para a construção original. As decisões de produto estão fechadas na
D-008 de cada spec; este documento responde *como*, e confronta os dois pontos que as specs mandaram
confrontar antes de qualquer migration: a elevação de esquema (012, D-002/FR-098) e a conferência de
coerência do Resultado com a sua fonte (013, D-008.2).

Verificado contra `fb3860f`, com 012 e 013 já implementadas em `main`.

---

## TR-001 — O segundo incremento eleva em cadeia, e não por uma segunda origem solta

`publicacoes/domain/elevacao.py` foi escrito para **um** incremento e diz isso em voz alta:
`VERSAO_DE_ORIGEM = 4`, com o comentário de que *"elevar não é um mecanismo genérico de
compatibilidade: é este incremento, e só ele"*. A guarda existe para que um snapshot v3 não saia
carimbado como 5 — sem ela, a verificação de versão deixaria de verificar coisa alguma.

Duas saídas foram consideradas.

**Origem como conjunto** — `declarada in (4, 5, SCHEMA_VERSION)`, com uma função de elevação que
aplica todos os campos ausentes de uma vez. É a menor mudança de linhas e a pior de significado:
elevar um v4 direto para v6 salta uma forma intermediária que existiu de verdade, e a próxima
revisão herdaria uma função que decide o que fazer por ausência de chave, e não por versão. O modo
de falha é o que `colecoes.py` já recusa em outro lugar — acertar hoje e falhar em silêncio no dia
em que nascer coleção nova.

**A decisão: cadeia explícita.** Um degrau por incremento, cada um sabendo só a sua origem e o seu
destino, aplicados em sequência enquanto houver degrau:

```text
4 → 5   evaluationsPerRegistration, maximumScore     (012, D-001)
5 → 6   forma, rotuloFavoravel, rotuloDesfavoravel   (012, D-008)
```

O que se preserva: idempotência (conteúdo já na versão vigente atravessa sem cópia de dicionário),
a restrição de alcance (só o fluxo de Retificação, nunca a leitura pública, senão a tela mostraria
uma coisa e o `content_hash` provaria outra — 012, T-002), e o alcance ao `newValue` de cada ato
publicado, path-aware, que a 012 descobriu ser obrigatório (T-001). Nada disso muda; o que muda é
que a função passa a ser uma lista de degraus em vez de um degrau.

O comentário de `VERSAO_DE_ORIGEM` é reescrito, e não apagado: ele registrava uma decisão verdadeira
sobre o primeiro incremento, e continua verdadeiro sobre ele.

## TR-002 — O que a elevação escreve, e a equivalência de grafias

`AUSENCIA` hoje é `{"evaluationsPerRegistration": 1, "maximumScore": None}` — a mesma leitura que
`avaliacoes/domain/previsao.py` aplica no consumo, virada grafia. O degrau novo acrescenta:

```python
AUSENCIA_V6 = {"forma": "PONTUADA", "rotuloFavoravel": None, "rotuloDesfavoravel": None}
```

`forma` é o único dos três que a elevação **escreve com valor**, e ela pode fazê-lo porque a spec
declara o que a ausência significa (012, FR-120): todo o domínio anterior à v6 só admitia a forma
pontuada, e escrever `PONTUADA` não inventa nada — é a mesma norma na forma nova. Os rótulos
continuam nulos, porque na forma pontuada não há sentido a nomear.

**`diz_o_mesmo_que_a_ausencia` precisa acompanhar, e é aqui que uma leitura desatenta quebraria a
Retificação.** Essa função existe porque `null` e ausência são a mesma coisa, e
`publicacoes/domain/conflicts.py` a usa para não acusar conflito entre duas grafias do mesmo nada.
Com o campo novo, ela passa a aceitar `forma` ausente **ou** `"PONTUADA"` como equivalentes, com os
dois rótulos nulos. Sem isso, uma Retificação elaborada antes do salto entraria em conflito com o
conteúdo elevado por diferença que não é diferença.

`endereca_etapa` e `elevar_valor` não mudam de forma: continuam classificando o caminho e elevando
só o que é entidade Etapa.

## TR-003 — A forma no contrato da Etapa publicada, e a condicionalidade que `Campo` não expressa

`ETAPA_PUBLICADA` em `editais/domain/validation.py` é uma tupla de `Campo`, e `Campo` valida um campo
por vez — tipo, nulidade, formato, mínimo, conjunto de valores. Três campos entram por ali:

```python
Campo("forma", str, valores=("PONTUADA", "DECISORIA")),   # obrigatória e NÃO nula
Campo("rotuloFavoravel", str, admite_nulo=True),
Campo("rotuloDesfavoravel", str, admite_nulo=True),
```

**`forma` não admite nulo, e essa é a correção mais importante desta seção.** A primeira redação a
deixava anulável "porque conteúdo v5 passa por aqui", e isso é falso: `validate_for_publication` é
chamada em três lugares — a projeção de elaboração, a publicação e a consolidação de Retificação —, e
nos três o conteúdo já está na forma vigente, porque a elevação roda antes. Nenhum snapshot v5 cru
chega a este validador.

Admitir nulo criaria **duas grafias canônicas para a mesma versão**: um v6 com `forma: null` e um v6
com `forma: "PONTUADA"` descreveriam a mesma Etapa com bytes diferentes, e a versão canônica existe
justamente para identificar *uma* forma. FR-120 autoriza a ausência em **conteúdo anterior à v6**, e
só ali; quem a interpreta é o leitor legado, não o contrato da versão nova.

Os rótulos continuam anuláveis porque `null` neles tem significado — a forma pontuada não nomeia
sentido nenhum —, exatamente como `minimumScore` é anulável e obrigatório. No conteúdo publicado não
há campo opcional: obrigatório significa **presente**, e não preenchido, e é isso que
`test_todo_campo_do_conteudo_publicado_e_obrigatorio` já cobra de toda coleção.

No modelo de **elaboração**, `forma` nasce com `default="PONTUADA"` e **não** é anulável. A primeira
redação a deixava anulável, "porque quem está compondo ainda não escolheu", e o argumento não vale
para este campo: a ausência de forma já significa pontuada em todo o resto do sistema, de modo que um
`NULL` na elaboração seria uma terceira grafia do mesmo nada. É o padrão que `eliminatory` e
`classificatory` já seguem — campo normativo publicado, com estado inicial visível e editável.

O default resolve, no mesmo `AddField`, as Etapas **já em elaboração**. Sem ele, todo Edital hoje em
rascunho ficaria impublicável no instante em que `forma` passasse a ser exigida no conteúdo
publicado, porque `_stages()` transcreve `etapa.forma` direto para o snapshot e a validação recusaria
`null`.

**A compatibilidade precisa existir também na entrada da API**, e o default do modelo sozinho não a
dá. `StageSerializer` aplica `PONTUADA` quando `forma` vem **omitida** e recusa `forma: null`
explícito — as duas coisas são diferentes, e tratá-las igual devolveria a mensagem errada a quem
chamou. E `draft.py` **não pode** transformar ausência em `forma=None` no caminho de `stage.get(...)`,
como faz hoje com os campos anuláveis: escrever `None` contornaria o default do modelo e reintroduziria
o `NULL` que ele existe para impedir.

Os **rótulos continuam anuláveis**, e a assimetria é deliberada: neles o "não se aplica" é real, e um
default seria exatamente o default institucional que a D-008.2 recusa.

**A regra de verdade, porém, é entre campos**, e `Campo` não a expressa — o próprio arquivo já diz
isso ao deixar `content` e `source` de fora da seção publicada.

A condicionalidade vai para `validate_stages`, onde já vive a única coerência entre campos que o
contrato escreve para a Etapa — hoje "nota mínima não supera a máxima". Ela ganha companhia:

| forma | exigido | proibido |
|---|---|---|
| `PONTUADA` (ou ausente) | — | `rotuloFavoravel`, `rotuloDesfavoravel` |
| `DECISORIA` | `rotuloFavoravel`, `rotuloDesfavoravel` | `minimumScore`, `maximumScore` |

`weight`, `eliminatory`, `classificatory`, `order` e `scheduleEventId` ficam fora da tabela nas duas
formas: descrevem a Etapa, e não a conclusão (012, D-008.9). A recusa usa `RESTRICAO_VIOLADA` e
aponta o caminho do campo, como as demais, para que a tela de elaboração a mostre no lugar certo.

## TR-004 — `Avaliacao`: o `sentido`, a constraint que alterna, e a única cópia

O modelo ganha dois campos, e a assimetria entre eles é a decisão:

```python
forma    = CharField(choices=Forma.choices, null=True)   # gravada na conclusão
sentido  = CharField(choices=Sentido.choices, null=True) # FAVORAVEL | DESFAVORAVEL
```

Os dois são anuláveis **porque o rascunho é anulável**: a Avaliação nasce vazia e vai sendo
preenchida, e é a conclusão que exige completude — exatamente como `pontuacao`, `versao`,
`concluida_em` e `concluida_por` já são hoje.

`ck_avaliacao_concluida_completa` deixa de ser uma conjunção e passa a alternar:

```text
estado = RASCUNHO   → nada é exigido
estado = CONCLUIDA  → versao, concluida_em, concluida_por, forma
                      ∧ (forma = PONTUADA  ∧ pontuacao ≠ NULL ∧ sentido = NULL)
                      ∨ (forma = DECISORIA ∧ sentido  ≠ NULL ∧ pontuacao = NULL)
```

O comentário acima dela — *"o que 'concluída' significa, dito no banco"* — continua exato, e é por
isso que a mudança é ali e não num validador. O que a constraint afirma mudou; o nível em que ela
afirma, não.

**Por que `forma` é copiada e a nota mínima não.** FR-072 proíbe a Avaliação de copiar máxima,
mínima e caráter da Etapa, e a proibição continua valendo para os três. A forma é exceção por um
motivo que nenhum dos outros tem: uma `CheckConstraint` do PostgreSQL não referencia outra tabela, e
sem a forma na linha a regra sairia do banco e voltaria para a aplicação — a camada de que a 012
desconfiou quando escreveu a constraint. Copiar a nota mínima não compraria invariante nenhum;
copiar a forma compra este. Onde a cópia não compra invariante, ela segue proibida (012, FR-072).

A leitura da forma acontece **na transação que conclui**, do conteúdo da versão já lida por FR-096 —
não numa segunda consulta, e não da tela. Retificação consolidada no intervalo é recusada por
FR-073/FR-088, com a frase que já existe.

> **Revisto na implementação.** Dois pontos desta seção e da seguinte não sobreviveram ao código, e
> ambos para melhor: o projeto proíbe `NULL` em campo de texto, então a ausência de forma e de
> sentido é **vazio**; e o `DROP TRIGGER` em torno do backfill é desnecessário, porque o
> preenchimento da conclusão preservada vem do `DEFAULT` do `ADD COLUMN` — DDL, que não dispara
> trigger de linha — com `preserve_default=False` removendo o default logo depois. O que ficou está
> em [`traceability.md`](./traceability.md) §3.

## TR-004a — `Avaliacao`: o backfill que a constraint nova exige

`Avaliacao` **não** é append-only e não tem trigger; o backfill dela é um `UPDATE` comum. Mas ele é
obrigatório, e esquecê-lo derruba a migration: `ck_avaliacao_concluida_completa` passa a exigir
`forma` para o estado `CONCLUIDA`, e o PostgreSQL **valida a tabela inteira** ao criar a constraint.
Toda avaliação já concluída nasceria com `forma = NULL` e reprovaria.

```text
estado = CONCLUIDA  → forma := 'PONTUADA'
estado = RASCUNHO   → forma permanece NULL
```

Os rascunhos ficam sem forma de propósito: a forma é lida e gravada **no ato de concluir**, do
conteúdo da versão validada (FR-117), e escrevê-la num rascunho afirmaria antecipadamente uma regra
que a conclusão ainda vai ler. Um rascunho aberto hoje e concluído depois de uma Retificação que
mudou a forma da Etapa deve concluir na forma nova — ou ser recusado por FR-073 —, e nunca numa forma
carimbada quando ele nasceu.

A ordem dentro da migration é a mesma das outras duas: acrescentar anulável, preencher, só então
trocar a constraint.

## TR-005 — `ConclusaoAvaliacao`: coluna não-nulável em tabela append-only

`ConclusaoAvaliacao.pontuacao` é `NOT NULL`, a tabela está em `TABELAS_APPEND_ONLY` e tem trigger
`conclusao_avaliacao_append_only` que recusa `UPDATE` e `DELETE`. A migração precisa de três coisas,
nesta ordem, e o motivo da ordem é a trigger:

1. **acrescentar** `forma` e `sentido`, anuláveis;
2. **preencher** `forma = 'PONTUADA'` nas linhas existentes — todas são pontuadas, e a decisão de
   domínio já registra isso;
3. **relaxar** `pontuacao` para anulável e criar a `CheckConstraint` que alterna por forma, agora que
   toda linha tem forma.

O passo 2 é `UPDATE`, e a trigger recusa `UPDATE`. Ela é `BEFORE UPDATE OR DELETE ... FOR EACH ROW`
e **dispara para qualquer papel**, dono incluído: não há privilégio que a contorne. A saída é a que o
próprio mecanismo já prevê — as migrations de `avaliacoes` e de `resultados` já carregam o par
`PROTEGER` / `DESPROTEGER`, e aqui ele é usado na ordem inversa: derruba, faz o backfill, recria,
tudo na mesma migration e na mesma transação.

Como a trigger é condicional ao vendor — em SQLite ela não existe —, o `DROP`/`CREATE` também é, e a
demonstração de que o invariante continua no banco é `postgresql_only`, como as demais garantias de
banco da 012.

Alternativa considerada e recusada: nascer `forma` com `DEFAULT 'PONTUADA'` no `ADD COLUMN`,
evitando o `UPDATE`. Evita o backfill e deixa um default no esquema que afirma, para sempre, que
conclusão sem forma é pontuada — que é verdade sobre o passado e falsa sobre o futuro. O default é
removido depois, e remover default também é `ALTER TABLE`; não se economiza nada e se ganha uma
janela em que uma inserção decisória sem forma vira pontuada em silêncio.

A restrição de implantação é a mesma que a 012 já nomeou para esta tabela: quem migra altera
esquema, quem roda em produção só faz `SELECT` e `INSERT`.

## TR-006 — `ResultadoEtapa` e a trigger que confere a fonte

Mesma forma, um nível acima, e com um agravante: além da `CheckConstraint`, existe
`check_stage_result_source()`, que compara o Resultado com a Avaliação fonte no `INSERT` e hoje
inclui `fonte.pontuacao IS DISTINCT FROM NEW.pontuacao`. Comparar pontuação com uma conclusão que
não tem pontuação não é conferência nenhuma — é uma comparação de `NULL` com `NULL`, que em SQL
`IS DISTINCT FROM` resolve como *iguais*, e a trigger passaria a aprovar qualquer coisa na forma
decisória.

A conferência **não** alterna por forma: ela ganha `forma` e `sentido` e compara os três
incondicionalmente.

```sql
fonte.forma      IS DISTINCT FROM NEW.forma       → erro
fonte.pontuacao  IS DISTINCT FROM NEW.pontuacao   → erro
fonte.sentido    IS DISTINCT FROM NEW.sentido     → erro
```

Comparar os três incondicionalmente é mais forte que alternar por forma **e mais simples**: se as
formas são iguais e os dois campos são iguais, a alternância é redundante; se as formas divergem, o
primeiro teste já reprova. A alternância voltaria a existir só se algum dia uma forma admitisse os
dois campos — e nenhuma admite, por construção.

A D-008.2 e a FR-049 da `specs/013` diziam "alterna por forma" na primeira redação, e **foram
emendadas** para descrever a comparação incondicional. Implementar diferente do que a spec diz seria
divergência deliberada, e a Constituição não a admite: quando o desenho corrige a spec, quem muda é
a spec.

`ResultadoEtapa.pontuacao` relaxa para anulável e `sentido` nasce anulável, pelo mesmo caminho de
TR-005, com o mesmo `DROP TRIGGER` / backfill / `CREATE TRIGGER` — a tabela também é append-only por
privilégio e por trigger.

O `docstring` do modelo diz hoje que *"`pontuacao` descreve o Resultado, e não a fonte: a V1 a copia
porque consolida leitura única"*. Continua verdadeiro, e passa a valer para os dois campos.

## TR-007 — A consequência, e os dois impedimentos simétricos

`resultados/domain/regra.py` é função pura sobre o dicionário da Etapa publicada, e é onde a decisão
de produto aterrissa quase sem mecanismo novo.

`impedimento_da_regra` ganha o caso simétrico e condiciona o que já tinha:

```text
previstas > 1                          → regra de combinação ausente        (inalterado)
PONTUADA  ∧ eliminatória ∧ sem mínima  → regra insuficiente                 (era incondicional)
DECISORIA ∧ não eliminatória           → regra insuficiente                 (novo)
```

O segundo passa a ser condicionado à forma porque análise documental eliminatória sem nota mínima é
**normal** nos Editais 35 e 57; recusá-la seria o sistema procurando um número que a norma nunca
teve (013, FR-048). O terceiro é a decisão de 03/09: o Edital não publicou o que o sentido
desfavorável produz, e inferir o efeito — pelo sentido ou por definição da forma — afirmaria norma
que ninguém escreveu (013, FR-047).

`consequencia` ganha o ramo decisório, e a frase do motivo usa o rótulo publicado:

```text
DESFAVORAVEL → ELIMINADA,  "análise documental: Indeferido"
FAVORAVEL    → HABILITADA, "análise documental: Deferido"
```

O rótulo entra na frase porque `motivo` é texto exibível e o modelo já exige que consequência tenha
causa legível — *"quem consulta precisa ler a razão, e não apenas 'eliminada'"*. Ler `DESFAVORAVEL`
numa tela institucional seria mostrar o enum interno a quem tem direito ao vocabulário do Edital.

A assinatura passa a receber a conclusão, e não um decimal solto: `consequencia(etapa, conclusao)`.
É a mudança que mantém a função pura sem que ela precise adivinhar qual dos dois campos veio.

`progressao.py` **não muda**. Consome `HABILITADA` e `ELIMINADA`, nunca pontuação — e é a evidência
concreta de que generalizar a 013 não a infla.

## TR-008 — Compatibilidade normativa: a forma entra, os rótulos não

`resultados/domain/compatibilidade.py` compara quatro campos entre a Etapa histórica e a vigente.
`forma` vira o quinto, com um leitor que trata ausência como `PONTUADA` — o mesmo leitor do consumo,
importado, e não uma segunda interpretação escrita ali.

**Os rótulos ficam de fora**, pelo critério que a própria função já aplica a nome e cronograma:
trocar "Deferido" por "Deferido(a)" não altera consequência alguma, e compará-los faria uma correção
de redação bloquear toda consolidação pendente e mandar avaliações corretas de volta à reabertura.

A forma, ao contrário, é o campo mais grave da lista: sem ela, uma Retificação que trocasse
`PONTUADA` por `DECISORIA` não seria detectada, e a 013 fundamentaria Resultado numa conclusão cuja
espécie a norma vigente já não admite — não uma nota fora do limite novo, mas uma nota onde a norma
não prevê nota nenhuma.

## TR-009 — A Mesa apresenta um instrumento, e a recusa é do domínio

A forma vem da versão vigente da Etapa, e a tela escolhe o formulário por ela. Esconder o campo da
outra forma é apresentação; **recusá-lo é regra**, e por isso o comando de gravar e o de concluir
recusam no domínio o envio que traz o campo da forma errada, com mensagem, e não o ignoram em
silêncio (012, FR-122).

`pontuacao.normalizar()` deixa de ser o único caminho de conclusão: a recusa *"Informe a pontuação."*
passa a valer só na forma pontuada, e ganha a irmã *"Informe o sentido da decisão."* — que, na tela,
aparece com os rótulos publicados, e não com o enum.

`exige_parecer(valor, etapa)` já recebe a Etapa, e por isso a extensão é natural: na forma decisória
a obrigatoriedade do parecer vem do sentido desfavorável e **não** depende do caráter eliminatório
(012, FR-123).

## TR-010 — Retificação: a lista literal, e o que a tela não pode oferecer

`interface/retificacao.py` declara `CAMPOS_ETAPA` com cinco entradas e deixa `maximumScore` e
`evaluationsPerRegistration` de fora — a metade barata da lacuna E2E-004. O domínio alcança:
`publicacoes/domain/colecoes.py` já lista `/stages`.

A lista passa a cobrir **todos** os campos normativos da Etapa introduzidos pela 012, os dois
atrasados e os três novos. O requisito é de capacidade e não de contagem (012, D-008.10), e a
verificação correspondente é um teste que compara a lista da tela com o contrato da Etapa publicada,
para que o próximo campo normativo não caia no mesmo buraco em silêncio.

Uma consequência que a tela precisa tratar: retificar `forma` de `PONTUADA` para `DECISORIA` torna
`minimumScore` e `maximumScore` inaplicáveis e os rótulos obrigatórios. A recusa vem de
`validate_stages` (TR-003) e é mostrada como as demais; a tela **não** decide sozinha o que apagar,
porque apagar campo normativo por inferência de formulário seria retificação sem autor.

## TR-011 — O documento materializado

`publicacoes/infrastructure/pdf.py` monta os pares da Etapa condicionalmente — hoje inclui
"Pontuação máxima" quando ela não é nula. A forma entra pela mesma mecânica, com a apresentação
seguindo a aplicabilidade:

```text
PONTUADA    Peso · Nota mínima · Pontuação máxima · Avaliações por inscrição
DECISORIA   Peso · Avaliações por inscrição · Resultado: Deferido / Indeferido
```

Sem isso, a fonte estruturada e o documento divergem, e o candidato lê um Edital que não diz como sua
Etapa é concluída — que é P-007 valendo só na metade que ninguém vê.

`interface/revisao.py`, que resume a Etapa para quem compõe a Retificação, acompanha pela mesma
razão e com a mesma condicionalidade.

## TR-012 — A ordem das migrations, e o que não cabe na mesma

São **três** migrations, em três apps, e a ordem entre elas é imposta por dependência de dado:

```text
1. editais       três campos na Etapa de elaboração: forma e os dois rótulos
2. avaliacoes    forma + sentido na Avaliacao e na ConclusaoAvaliacao,
                 backfill PONTUADA nas duas, constraints que alternam
3. resultados    forma + sentido no ResultadoEtapa, backfill, trigger nova
```

**Nenhuma em `publicacoes`**, e essa ausência é a que mais importa: a elevação é função pura sobre
conteúdo lido, não escreve linha nenhuma, e `Publicacao` e `VersaoConsolidada` continuam byte a byte
o que foi publicado. A 012 já provou isso, e a prova não é refeita.

`SCHEMA_VERSION` sobe para 6 **junto** da migration de `editais`, e não antes: entre o salto da
constante e a chegada do campo, toda Retificação em curso passaria a comparar contra uma versão que
o conteúdo elaborado ainda não sabe escrever.

## TR-013 — O `openapi.yaml` é parte da entrega, e não documentação de acompanhamento

`specs/001-processo-seletivo-editais/contracts/openapi.yaml` é a fonte única da forma publicada, e
`tests/contract/test_forma_publicada.py` a confere contra o domínio campo a campo. Três testes de lá
falham no instante em que `ETAPA_PUBLICADA` ganha campos sem a alteração correspondente no contrato:
a transcrição que cobre todos os campos, a que confere dimensão por dimensão, e a que exige que
**todo campo do conteúdo publicado seja obrigatório** — onde obrigatório significa presente, e não
preenchido.

O que muda no arquivo:

| esquema | mudança |
|---|---|
| `EtapaPublicada` | `forma` em `required`, `type: string`, `enum: [PONTUADA, DECISORIA]`, **sem `'null'`** |
| `EtapaPublicada` | `rotuloFavoravel` e `rotuloDesfavoravel` em `required`, `type: [string, 'null']` |
| `EtapaPublicada` | a `description` passa a falar da versão canônica **6**, e registra o segundo incremento como o texto atual registra o primeiro |
| `EtapaInput` | os três campos aceitos na elaboração, com a nulabilidade do rascunho |

A assimetria entre `forma` e os rótulos no contrato é a mesma de TR-003, e é visível na diferença
entre `eliminatory: { type: boolean }` — obrigatório e não nulo — e `minimumScore: { type: [string,
'null'] }`, obrigatório e nulo admitido. `forma` é do primeiro tipo.

Editar o `openapi.yaml` **antes** do domínio inverteria a ordem que o teste protege, mas nada impede
que as duas coisas entrem na mesma tarefa; o que não pode acontecer é a alteração do domínio ser
declarada pronta com o contrato em vermelho.

## TR-014 — O salto de versão precisa ser exercido, e não só o estado final

A suíte roda contra um banco já migrado, e por isso ela demonstra que o **esquema novo** funciona —
não que o **salto** funciona. Os três backfills, o `DROP`/`CREATE` das duas triggers append-only e a
substituição da trigger de coerência são precisamente o tipo de coisa que passa em banco limpo e
falha em produção, onde existem linhas.

`tests/migrations/test_migrations.py` já tem a forma certa — `MigrationExecutor`, upgrade
incremental, conferência de que as triggers sobreviveram — e tem um limite que esta revisão obriga a
remover: `APPS = ("processos", "editais", "publicacoes", "auditoria")`, sem `avaliacoes` e sem
`resultados`, e `TRIGGERS` sem as três daquelas duas. Enquanto for assim, nenhuma migration dos dois
apps que esta revisão mais mexe é exercida por teste de upgrade.

O teste que a revisão acrescenta:

1. aplica as migrations **até o estado anterior** a esta revisão;
2. cria dados históricos — Avaliação concluída, conclusão preservada e Resultado, todos pontuados;
3. aplica as três migrations novas;
4. confere os três backfills: `forma = 'PONTUADA'` em toda linha concluída, e `NULL` nos rascunhos;
5. confere que `conclusao_avaliacao_append_only`, `resultado_etapa_append_only` e
   `resultado_etapa_coerente` existem de novo, e que a última recusa uma fonte divergente.

`postgresql_only`, como os demais — em SQLite não há trigger a recriar, e o teste passaria sem
exercitar o que ele existe para exercitar.
