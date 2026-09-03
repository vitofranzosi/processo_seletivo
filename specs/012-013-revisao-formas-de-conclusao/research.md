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
Campo("forma", str, admite_nulo=True, valores=("PONTUADA", "DECISORIA")),
Campo("rotuloFavoravel", str, admite_nulo=True),
Campo("rotuloDesfavoravel", str, admite_nulo=True),
```

`admite_nulo=True` nos três, porque conteúdo em v5 elevado por leitura passa por aqui e porque a
forma pontuada não tem rótulos. **Mas a regra de verdade é entre campos**, e `Campo` não a expressa —
o próprio arquivo já diz isso ao deixar `content` e `source` de fora da seção publicada.

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

A conferência passa a alternar, e ganha um campo:

```sql
fonte.forma      IS DISTINCT FROM NEW.forma       → erro
fonte.pontuacao  IS DISTINCT FROM NEW.pontuacao   → erro
fonte.sentido    IS DISTINCT FROM NEW.sentido     → erro
```

Comparar os três incondicionalmente é mais forte que alternar por forma **e mais simples**: se as
formas são iguais e os dois campos são iguais, a alternância é redundante; se as formas divergem, o
primeiro teste já reprova. A alternância voltaria a existir só se algum dia uma forma admitisse os
dois campos — e nenhuma admite, por construção.

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

São quatro migrations, em três apps, e a ordem entre elas é imposta por dependência de dado:

```text
1. editais       dois campos na Etapa de elaboração: forma e os dois rótulos
2. avaliacoes    forma + sentido na Avaliacao e na ConclusaoAvaliacao,
                 backfill PONTUADA, constraints que alternam
3. resultados    forma + sentido no ResultadoEtapa, backfill, trigger nova
4. —             nenhuma em publicacoes: a elevação é função pura sobre conteúdo lido
```

A quarta linha é a que mais importa e é a que a 012 já provou: elevar não escreve linha nenhuma, e
`Publicacao` e `VersaoConsolidada` continuam byte a byte o que foi publicado.

`SCHEMA_VERSION` sobe para 6 **junto** da migration de `editais`, e não antes: entre o salto da
constante e a chegada do campo, toda Retificação em curso passaria a comparar contra uma versão que
o conteúdo elaborado ainda não sabe escrever.
