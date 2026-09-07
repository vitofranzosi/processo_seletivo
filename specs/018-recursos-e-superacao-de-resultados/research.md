# Fase 0 — Pesquisa e decisões técnicas

**Feature**: 018 — Recursos e Superação de Resultados · **Data**: 2026-09-06 ·
**Spec**: [spec.md](./spec.md)

Cada decisão abaixo foi tomada lendo o repositório, e não por preferência. Onde há alternativa
descartada, ela está escrita: é a fundamentação da escolha, e é por ela que uma revisão futura sabe
o que mudaria a conta.

Nenhum item aqui é requisito. Requisito está na spec; aqui está **como** atendê-lo com o que já
existe.

---

## T-001 — App novo `recursos`, e a dependência que ele cria nos dois sentidos

**Decisão.** App novo `recursos`, no precedente do que a 015 fez com `classificacao` e a 017 com
`divulgacao`. Ele hospeda os três agregados da feature: a peça, o juízo de admissibilidade e a
decisão.

**A parte incômoda, e ela é real.** A dependência não é de mão única, como foi nas duas features
anteriores:

```text
recursos  ──lê──▶  resultados, divulgacao, classificacao, inscricoes, avaliacoes
resultados ──cita──▶  recursos.DecisaoRecurso      (a FK obrigatória em todo sucessor, FR-054)
```

**Por que a FK tem de morar no `ResultadoEtapa`, e não o inverso.** Inverter — a decisão apontando
para o sucessor que criou — quebraria o ciclo de graça, e perderia a invariante que importa: a
FR-054 exige que **todo** sucessor cite a decisão, e isso só é constraint se a coluna estiver do
lado do sucessor. Do outro lado, a constraint possível seria "toda decisão que fixa correção aponta
para um sucessor", que não impede o que se quer impedir — um sucessor nascer sem fundamento.

**Por que isso não é ciclo de verdade.** São dois níveis diferentes:

- **Python**: `recursos/models.py` importa `resultados.models`; `resultados/models.py` declara a FK
  como *string* (`"recursos.DecisaoRecurso"`), que é como o Django resolve referência tardia. Não há
  import circular.
- **Migrations**: `recursos/0001` depende de `resultados/0001`, `divulgacao/0001` e `inscricoes`;
  `resultados/0005` depende de `recursos/0001`. O grafo continua acíclico, porque a granularidade é
  a migration, e não o app.

**Alternativa descartada — não criar app e pendurar tudo em `resultados`.** Deixaria a interposição
do candidato, o juízo de admissibilidade e a autoridade de julgar dentro do app cuja
responsabilidade é a consequência da Etapa. É o mesmo argumento que fez `divulgacao` não nascer
dentro de `publicacoes`: são atos distintos, por autoridades distintas, sobre objetos distintos.

---

## T-002 — A sucessão no `ResultadoEtapa`: só esquema, e nenhuma linha escrita

**Decisão.** `resultados/0005`, inteiramente de esquema. Nenhum backfill, e **a trigger
`resultado_etapa_append_only` não é desligada**.

```text
+ resultado_anterior    FK(self, null, PROTECT, related_name="sucessor")
+ motivo_da_superacao   TextField(blank, default="")
+ decisao               FK("recursos.DecisaoRecurso", null, PROTECT, related_name="resultados")
  origem                ganha o terceiro valor: AVALIACAO | OCORRENCIA | RECURSO

- uq_resultado_inscricao_etapa
+ uq_resultado_raiz_por_par      UNIQUE(inscricao, etapa_id) WHERE resultado_anterior IS NULL
+ uq_resultado_sucessor_unico    UNIQUE(resultado_anterior)  WHERE resultado_anterior IS NOT NULL
+ ck_superacao_com_motivo        resultado_anterior IS NULL OR motivo_da_superacao <> ''
+ ck_sucessor_cita_decisao       (anterior IS NULL AND decisao IS NULL)
                              OR (anterior IS NOT NULL AND decisao IS NOT NULL)
~ ck_resultado_origem            ganha o ramo RECURSO, e NÃO menciona `decisao` em ramo nenhum
~ ck_resultado_completo_por_forma  deixa de ser fechada em três ramos fixos
```

**Por que não há backfill.** Todo Resultado existente tem `resultado_anterior IS NULL` e, portanto,
já satisfaz `uq_resultado_raiz_por_par`. As três colunas novas nascem nulas e assim ficam. A `0004`
precisou desligar a trigger porque preencheu `versao` linha a linha; aqui não há linha a tocar.

> **Se a implementação se vir precisando desligar `resultado_etapa_append_only`, é sinal de que
> alguém está corrigindo com `UPDATE` o que esta feature manda corrigir com linha nova.** Vale como
> critério de revisão do PR.

**A matriz de origem distingue raiz de sucessor, e é onde uma redação anterior errou.** Aquela
redação punha `decisao IS NULL` no ramo `AVALIACAO` de `ck_resultado_origem`, e isso tornava a
FR-068 **impossível**: `ck_sucessor_cita_decisao` exige decisão em todo sucessor, de modo que o
sucessor por reavaliação — que é `AVALIACAO` **e** sucessor — não podia existir. São quatro linhas
legítimas, e só quatro:

| linha | `origem` | `avaliacao` | `decisao` | `resultado_anterior` |
|---|---|---|---|---|
| raiz por avaliação | `AVALIACAO` | presente | ausente | ausente |
| **sucessor por reavaliação** | `AVALIACAO` | presente | **presente** | presente |
| raiz por ocorrência | `OCORRENCIA` | ausente | ausente | ausente |
| sucessor por recurso | `RECURSO` | ausente | presente | presente |

O ramo do `AVALIACAO` **não menciona `decisao`**: quem amarra a decisão ao sucessor é
`ck_sucessor_cita_decisao`, e repetir a regra no outro `CHECK` foi o que produziu a contradição.
Os ramos de `OCORRENCIA` e `RECURSO` ganham a condição sobre `resultado_anterior`, e é ela que barra
as duas linhas que não existem — raiz por recurso e sucessor por ocorrência.

**A espécie da decisão citada é da trigger, e não do `CHECK`.** Sucessor `AVALIACAO` cita decisão
`REAVALIACAO_DETERMINADA`; sucessor `RECURSO` cita `CORRECAO_FIXADA`. Nenhuma das duas cabe em
`CheckConstraint`, porque `CHECK` não atravessa tabelas em PostgreSQL — é a mesma razão pela qual as
quatro coerências que já existem moram na trigger.

**`ck_resultado_completo_por_forma` também depende da origem.** O terceiro ramo de hoje — as três
ausências — vale para a Ocorrência, e **não** pode valer para o Recurso, porque a decisão pode fixar
pontuação:

| origem | forma | pontuação | sentido |
|---|---|---|---|
| `AVALIACAO` | `PONTUADA` \| `DECISORIA` | conforme a forma | conforme a forma |
| `OCORRENCIA` | vazia | nula | vazio |
| `RECURSO` | a forma que a Etapa publica, **ou** vazia | conforme a forma | conforme a forma |

O ramo vazio do `RECURSO` é o desfecho sem grandeza da FR-059 — o recurso contra Ocorrência que a
decisão acolhe sem que ninguém tenha avaliado nada.

**Reversibilidade.** Limpa enquanto não houver Resultado com origem `RECURSO`; havendo, a mesma
guarda `IrreversibleError` que a `0004` escreveu para a `OCORRENCIA`, e pela mesma razão: desfazê-los
é ato administrativo, e precisa acontecer antes.

---

## T-003 — O objeto atacado: duas chaves anuláveis, e por que não uma abstração

**Decisão.** O `Recurso` guarda duas FKs anuláveis — uma para `PublicacaoResultado`, outra para
`ResultadoEtapa` — e um `CHECK` de que **exatamente uma** está presente.

**Por que FK, e não identidade solta.** O idioma do projeto já separa os dois casos: identidade
publicada (`etapa_id`, `marco_id`, `perfil_id`) para o que vive no conteúdo normativo e pode existir
sem linha correspondente; FK com `PROTECT` para a linha que não pode desaparecer sob quem a cita
(`ResultadoEtapa.avaliacao`, `PublicacaoResultado.ato`). O objeto atacado é linha, e das que não
podem sumir.

**Por que não uma abstração de "recorrível".** É a mesma recusa que a 017 fez com `Publicavel`
(D-002 dela): generalizar sobre dois casos concretos, quando os dois são conhecidos e finitos,
produz indireção sem consumidor. Duas colunas e um `CHECK` dizem a mesma coisa no banco, e o banco
as verifica.

**Alternativa descartada — chave genérica com discriminador de tipo.** Perde `PROTECT`, perde
integridade referencial, e transfere para o código a garantia de que o identificador aponta para a
tabela que o discriminador diz. É trocar constraint por promessa.

---

## T-004 — O filtro de vigência: o inventário, e o que quebra em silêncio

Este é **o trabalho real da feature**, e é o que a decisão C já enumerou. A lista é fechada, e está
separada pelo que a torna perigosa.

**Quebram em silêncio — produzem resultado errado sem erro:**

| onde | o que assume | o que aconteceria |
|---|---|---|
| `classificacao/application/calculo.py:97` | `pontuacoes = {etapa_id: pontuacao}` | Dois Resultados da mesma Etapa **colapsam**, e o último do queryset vence. O queryset não tem `order_by`. Ordem classificatória errada, sem exceção e sem log. **É a assunção mais perigosa do sistema.** |
| `resultados/application/prontidao.py:143,154,174,183` | os quatro `Exists` da progressão | Uma eliminação **superada** continuaria excluindo a pessoa de toda Etapa seguinte. O deferimento não teria efeito onde mais importa. |
| `resultados/application/selectors.py:35` | `eliminadas_ate` | Idem, na forma em conjunto. |
| `resultados/application/selectors.py:24` | `habilitadas_em` | Pertinência satisfeita por qualquer `HABILITADA`, superada inclusive. |
| `resultados/application/selectors.py:122` | `contestacoes_supervenientes` indexa por `(subject, inscricao_id)` | Dois Resultados da mesma inscrição por avaliadores distintos colidem na chave, e um perde a marcação. |

**Mudam de significado** — passam a responder "existe algum" onde queriam "existe o vigente":
`ha_resultado_em`, `inscricoes_com_resultado`, `_estado_do_participante`, `contagens`,
`resultados_da_etapa`, `avaliacoes/application/impedimento.py:148`.

**Imune, e não deve ser tocado:** `classificacao/application/reproducao.py:34` lê os Resultados por
`pk__in` dos ids gravados em `ato.universo.stageResults`. É essa leitura que torna a IO-5 da 015
verdadeira; acrescentar filtro de vigência ali quebraria a reprodução histórica.

**Decisão — um caminho canônico, e um teste estrutural que o obriga.**

1. `ResultadoEtapa.vigentes` — manager nomeado que filtra `sucessor__isnull=True`. Nomeado, e não
   `objects` redefinido: a reprodução histórica **precisa** ver os superados, e um default que os
   esconde faria o caminho correto ser o exótico. **Ele mora em `resultados/models.py`** — ou em
   `resultados/managers.py`, importado pelo modelo —, e não em `application/selectors.py`: manager é
   do modelo, e os selectors o **consomem**.
2. `calculo.py` recebe, além do filtro, um `order_by` determinístico. **Sem ele, a ausência futura
   do filtro volta a produzir ordem arbitrária sem erro** — e é o teste de regressão mais importante
   da 018.
3. Um teste estrutural varre `ResultadoEtapa.objects` no código de aplicação e falha em uso não
   declarado, no molde de `tests/migrations/test_migrations.py` e da varredura de vocabulário da
   013. A lista de exceções é curta e explícita: a reprodução e a consulta histórica.

**Por que o teste estrutural, e não revisão.** Sem ele, a próxima feature que escrever
`ResultadoEtapa.objects.filter(...)` para responder "existe resultado?" reintroduz o defeito, e
nenhum teste funcional o denuncia enquanto não houver um recurso deferido em fixture.

---

## T-005 — Onde vive a autoridade de julgar, e por que um papel novo

**Decisão.** Capacidade `recurso:julgar` no mapa de papéis, num papel **novo** — `julgador`.

**Por que não em papel existente.** Cada opção existente concede o julgamento a quem tende a estar
impedido:

- `publicador` já tem `resultado:publicar`, e quem publicou o ato atacado é impedido (FR-039);
- `gestor` tem `comissao:gerir`, e é por ela que a presidência gere — a D-005 proíbe exatamente que
  julgar derive de gerir;
- `auditor` consulta e não decide, por desenho.

Um papel próprio custa uma entrada em `PAPEIS` e é o que permite à instituição concedê-lo a quem
está fora da comissão — que é a saída que o documento institucional nomeia para o caso em que o
impedimento não deixa ninguém elegível.

**O invólucro é o da 017, e não o da 011.** `comando_de_comissao` autoriza por `pode_gerir_comissao`,
que é presidência — exatamente a derivação que a D-005 proíbe. O precedente certo é o de
`publicar_resultado`: `require_permission` **fora** da transação, `select_for_update` no
`ProcessoSeletivo` dentro dela, autorização e impedimento **reavaliados depois do bloqueio**
(FR-043), `reserve` em seguida.

**Por que travar o Processo.** É a mesma linha que `comando_de_comissao` e `publicar_resultado` já
tomam. Sem ela, julgar, consolidar, emitir e publicar não se serializam, e a 017 já pagou esse
aprendizado (T-005 dela): revalidar dentro da transação não impede a outra transação de existir.

---

## T-006 — O impedimento: cinco perguntas pontuais, e nenhuma na listagem

**Decisão.** O impedimento é verificado **no ponto**, dentro do comando, depois do bloqueio.

As cinco perguntas são diretas porque o autor de cada ato está gravado:

```text
avaliacao.concluida_por        == ator?     (concluiu a Avaliação fonte)
resultado.consolidado_por      == ator?     (consolidou o Resultado atacado, ou constatou a Ocorrência)
ato.emitido_por                == ator?     (emitiu o ato de ordenação atacado)
publicacao.publicado_por       == ator?     (praticou a publicação atacada)
Impedimento.objects.filter(identity_subject=ator, inscricao=...)
```

**Por que isso não reabre o que a 012 fechou.** A 012 manteve o `Impedimento` fora da cadeia de
autorização por custo de escala: consultá-lo custaria uma verificação por linha em toda listagem.
Julgamento é **ponto único**. A listagem de recursos recebidos não consulta impedimento nenhum — ela
lista; a recusa acontece quando alguém tenta decidir.

**Consequência de interface a registrar:** a lista mostra recursos que o ator pode não poder julgar,
e a tela do recurso é que diz o impedimento. Mostrar "você está impedido" na listagem custaria a
verificação por linha que a 012 recusou.

---

## T-007 — A janela recursal: degrau 8, e o nível que a elevação ainda não desce

**Decisão.** `appealWindow` é objeto dentro de cada marco, no conteúdo publicado:

```json
"appealWindow": {"admits": true, "durationDays": 5, "unit": "DIAS_CORRIDOS"}
```

Ausente ou `null` significa **janela não declarada** (FR-029). `admits: false` é o **terceiro**
estado, e não sinônimo do segundo: é norma publicada dizendo que aquele marco não admite recurso, e
a interposição por esta via é recusada com código próprio (FR-113).

A distinção só apareceu na revisão da implementação, e vale registrar por quê: `computavel()`
devolvia `None` para os três casos, porque a pergunta que ela responde é *"há prazo a contar?"* — e
para essa pergunta os três são iguais. A pergunta que faltava era outra, *"cabe recurso?"*, e ela
tem três respostas. Uma função respondendo duas perguntas com um valor só é o modo de falha que
apaga a diferença sem produzir erro nenhum.

**O custo escondido, e ele é o maior da feature.** `publicacoes/domain/elevacao.py` sabe descer dois
níveis: `elevar_etapa` reescreve `/stages`, e `elevar_perfil` reescreve chaves do Perfil — este
último acrescentado pela 015, que foi a primeira a precisar dele. O marco é uma coleção **dentro** do
Perfil, e a elevação não sabe descer o terceiro nível. Entra `DEGRAUS_DE_MARCO` e `elevar_marco`,
simétricos aos dois existentes:

```python
DEGRAUS_DE_MARCO = {8: {"appealWindow": None}}
```

`SCHEMA_VERSION` sobe de 7 para 8. `elevar_alteracoes` precisa alcançar o endereço do marco pela
mesma razão que já alcança o da Etapa: um ato v7 que acrescentou marco reintroduziria o marco fora
de forma, e a publicação inteira falharia na materialização — foi o modo de falha que a 012
descobriu (T-001 dela).

**Endereçamento por Retificação.** `/profiles/*/classificationMilestones` já é coleção com
identidade em `publicacoes/domain/colecoes.py`. `appealWindow` é campo de um item já endereçável, e
o caminho `/profiles/{id}/classificationMilestones/{id}/appealWindow` deve resolver sem declaração
nova. **Ponto a verificar na implementação, não a assumir**: se `changes.py` recusar objeto aninhado
como alvo atômico, ele entra em `COLECOES_ATOMICAS` pelo mesmo argumento que a enumeração de Etapas
do marco já entrou — valor normativo substituído inteiro.

**Alternativa descartada — marca booleana no `EventoCronograma`.** Espelharia
`is_registration_period`, e herdaria o modo de falha que a E2E-017 demonstrou neste produto: no
E2E17-001, a marca do período de inscrições era apagada em silêncio por gravação posterior do
assistente. Além disso, datas absolutas descolam-se do ato: publicado o resultado depois da data
marcada, a janela nasce vencida.

---

## T-008 — A contagem, a zona institucional, e um pequeno débito a pagar antes

**Decisão.** A janela é função pura de dois valores — o instante da publicação âncora e a duração
declarada:

```text
abre    = publicacao.publicado_em
fecha   = fim do N-ésimo dia, contado do dia seguinte ao da publicação, na zona institucional
```

Exclui-se o dia do começo e inclui-se o do vencimento, que é a regra geral do processo
administrativo. Sem prorrogação: prorrogar o vencimento que cai em dia sem expediente exige
calendário que o domínio não publica, e é por isso que a unidade da V1 é `DIAS_CORRIDOS` (D-004).

**O débito.** `ZONA = ZoneInfo("America/Sao_Paulo")` está declarada **duas vezes**, e as duas em
`interface/` — `forms.py:16` e `retificacao.py:28`. A contagem da janela é domínio, e domínio não
importa de `interface`. Antes de F5, a zona sobe para um módulo compartilhado e os dois pontos
passam a importá-la. É refatoração pequena e obrigatória: sem ela, ou o domínio inverte a dependência
ou a zona aparece uma terceira vez, e o Princípio II proíbe a segunda fonte.

**Reabertura por conteúdo novo.** A janela é ancorada na publicação vigente do marco que divulgou
**pela primeira vez** o ato que ela publica. Publicação que só muda a natureza do mesmo ato não abre
janela nova (FR-025), e a comparação é de identidade do ato — não de hash de conteúdo, que mudaria
por causa do rótulo da natureza no cabeçalho.

---

## T-009 — A visibilidade do Resultado da Etapa: duas consultas, e a norma histórica

**Decisão.** O acompanhamento ganha um seletor que responde, para uma Inscrição:

```text
1. publicações vigentes de marcos do Perfil da Inscrição      (1 consulta)
2. de cada uma, a versão que o ato cita → marco["stages"]     (1 consulta, por versão distinta)
3. Resultados vigentes da Inscrição naquelas Etapas           (1 consulta)
```

**A enumeração vem da versão que o ato cita, e não da vigente.** É a norma que governou a publicação
que autoriza mostrar; ler a vigente faria uma Retificação posterior alargar ou estreitar, em
silêncio, o que já foi autorizado.

**`conteudos_das_versoes` é o caminho, e não `select_related("versao")`.** O seletor já existe em
`resultados/application/selectors.py:66` e existe exatamente por isto: trazer a versão junto de cada
linha carregaria uma cópia do Edital inteiro em JSON por linha, e nenhum teste de contagem de
consultas denunciaria, porque o número de consultas continuaria o mesmo.

**Número constante de consultas** entre 1 e N marcos, no molde de
`tests/performance/test_public_queries.py`.

---

## T-010 — A definitividade: o que `aferir()` passa a receber, e os seis fatos que apura

**Decisão.** `aferir()` passa a receber a **natureza pretendida**. Hoje ela não a conhece — o comando
decide a natureza depois —, e sem ela a verificação não tem como distinguir o que impede a definitiva
do que não impede nada.

As perguntas novas são todas de existência, e todas de custo constante:

| fato | como se pergunta |
|---|---|
| recurso pendente pertinente | `Exists` sobre recursos do marco e das Etapas que ele enumera, sem decisão |
| reavaliação determinada não cumprida | `Exists` sobre decisões da terceira espécie sem sucessor posterior do par |
| providência a jusante não cumprida | o ato que se publica **não cita** a decisão que a determinou (FR-089, T-015) |
| janela estruturada aberta | função pura sobre a publicação vigente e a norma (T-008) |
| pendência reaberta | `Exists` de inscrição com Resultado sucessor habilitante e sem Resultado numa Etapa do marco |

**Pertinência ao marco custa uma leitura a mais**, e é a que fecha o buraco: alcança o recurso contra
a publicação **e** o recurso contra `ResultadoEtapa` de Etapa que o marco enumera. Sem ela, o recurso
individual seria a porta por onde uma definitiva nasceria com um Resultado em disputa dentro dela.

**A declaração expressa** (FR-085) são **três** campos anuláveis na `PublicacaoResultado` — instante,
autor e fundamento —, com um `CHECK` de que estão os três presentes ou os três ausentes. Preenchidos
no nascimento: a tabela é append-only e nasce completa, então acrescentar colunas anuláveis não fere
nada. São `divulgacao/0002`. Ela é exigida **somente** quando não há janela computável, e recusada quando há: declarar o que
o sistema pode verificar seria pedir à pessoa que respondesse pelo que a máquina sabe.

---

## T-011 — *Non reformatio in pejus*: onde a comparação mora, e contra o quê

**Decisão.** No comando, e no teste. **Não** em constraint — o esquema precisa continuar admitindo o
sucessor pior, porque a instituição pode adotar o agravamento com contraditório depois, e porque a
revisão de ofício produzirá exatamente esse sucessor (D-006).

São dois pontos de verificação, e o segundo é o que fecha a porta de trás:

1. **no julgamento que fixa correção** — compara a consequência e a pontuação propostas com as do
   Resultado vigente do par;
2. **na consolidação em cumprimento de decisão de reavaliação** — compara com o **Resultado
   protegido**, que é o que estava vigente quando a decisão foi tomada.

**O Resultado protegido é citado pela decisão, e não derivado.** Derivá-lo exigiria perguntar "qual
era o vigente naquele instante", que é consulta temporal sobre uma cadeia — cara e frágil. Uma FK na
decisão responde em uma junção, e é honesta: a decisão de fato se referiu àquele Resultado.

---

## T-012 — O protocolo do recurso

**Decisão.** Mesmo alfabeto e mesmo comprimento do protocolo da Inscrição
(`inscricoes/domain/protocolo.py`), com prefixo próprio — `REC-2026-…`. O alfabeto existe por uma
razão que vale igual aqui: ele é ditado ao telefone, e por isso não tem `0`/`O` nem `1`/`I`/`L`.

O gerador sobe para um módulo compartilhado, ou o de `recursos` importa o alfabeto do de
`inscricoes`. **Não** se duplica a constante: seriam dois alfabetos que podem divergir, e o segundo
divergiria em silêncio.

---

## T-013 — Os registros fora do app, e o teste que não enxerga o que não foi registrado

**Decisão.** Como a 017 aprendeu (T-011 dela), tabela append-only nova significa anotações fora do
app — e aqui são **quatro** tabelas, porque a citação de cumprimento também é histórica:

```text
seguranca/papeis.py   → TABELAS_APPEND_ONLY += recursos_recurso,
                                               recursos_juizodeadmissibilidade,
                                               recursos_decisaorecurso,
                                               classificacao_citacaodedecisao
tests/migrations/…    → APPS += "recursos"          ("classificacao" já está lá)
                      → TRIGGERS_POR_APP["recursos"]      = 3 de imutabilidade + 2 de coerência
                      → TRIGGERS_POR_APP["classificacao"] += cumprimento_de_providencia_append_only,
                                                             cumprimento_coerente
                      → TRIGGERS_POR_APP["resultados"]     inalterado: a trigger de coerência é
                                                           recriada, e o nome não muda
```

**Duas triggers de coerência em `recursos`, e não uma.** Uma trigger instalada no `Recurso` não
valida linha nenhuma da `DecisaoRecurso` — o gatilho é por tabela. A coerência da decisão vive na
`DecisaoRecurso`. O inventário completo, com o que cada uma confere, está na §10 do
[data-model.md](./data-model.md).

**Uma função SQL por trigger**, com mensagem própria: é o padrão de `divulgacao/0001` e de
`resultados/0004`, e não há função compartilhada a reaproveitar.

A trigger `resultado_etapa_coerente` é **recriada por inteiro** no molde da `0004`, com dois ramos
novos — a coerência do Resultado por recurso com a decisão que o fundamenta, e a coerência de par,
ordem e cronologia de todo sucessor. O nome permanece, porque a trigger é a mesma: foi assim que a
`0004` acrescentou o ramo da Ocorrência.

---

## T-014 — Teste: o que só existe em PostgreSQL, e o que a suíte precisa saber

As garantias centrais desta feature vivem no banco, e três delas **não são exercidas em SQLite**:

- `uq_resultado_raiz_por_par` e `uq_resultado_sucessor_unico` sob concorrência;
- a trigger de coerência do Resultado por recurso;
- a recusa de `UPDATE` pelo papel de runtime.

A suíte só as alcança com `TEST_DB_ENGINE=postgresql` **e** `DB_USER`; sem o primeiro ela cai para
SQLite e pula os testes **em silêncio**. Vale registrar na entrega, porque um PR verde em SQLite não
prova nada do que esta feature promete.

---

## T-015 — O cumprimento da providência: vínculo causal, sem ato autônomo

**O problema original.** Uma redação anterior dava a providência por cumprida quando a publicação
vigente divulgasse **ato diferente** do reconhecido viciado. Isso a quitaria **por acidente**: um ato
sucessor emitido por razão alheia — uma Retificação que mudou um peso, um Resultado consolidado
tarde — encerraria a pendência sem que ninguém tivesse corrigido o vício. O vínculo precisa ser
causal, e "diferente" não é vínculo.

**Decisão.** O ato de ordenação emitido em cumprimento **cita** a decisão, e a citação é uma linha de
`classificacao.CitacaoDeDecisao(ato, decisao)`, com `UNIQUE(ato, decisao)` e **nada além disso**.

```text
cumprida_para(decisao, ato_candidato) =
      existe CitacaoDeDecisao(ato_candidato, decisao)
   OU existe CitacaoDeDecisao(A, decisao), com A do MESMO marco e A já publicado
```

**Citar não é cumprir, e a primeira redação confundia os dois.** Ela tinha `UNIQUE(decisao)`,
justificada como "a decisão é cumprida uma vez", e a análise cruzada mostrou que aquela unicidade
errava em três frentes:

1. **contradizia a FR-089**, que exige ato **publicado**: a citação sozinha encerraria a pendência;
2. **criava beco**: emitido `C2` citando a decisão e ficando obsoleto antes de publicar, `C3` não
   poderia recitá-la, e a definitiva do marco ficaria impedida para sempre — o beco que o desenho
   existia para evitar;
3. **impedia a pertinência múltipla**: providência normativa alcança todos os marcos que a regra
   retificada governa, e cada um precisa citar a mesma decisão no seu ato.

Por isso `UNIQUE(decisao)` **não existe**, a recitação é legítima enquanto nenhum ato citante for
publicado, e a apuração é **por marco** — o trabalho feito num marco não libera a definitiva de
outro.

**Por que isto não é a "entidade de cumprimento" recusada na clarificação.** O que se recusou foi um
**ato administrativo próprio** — alguém declarando, depois e em tela separada, que a providência foi
cumprida, com autoridade e instante seus. A citação não é ato: é **proveniência do
`AtoDeOrdenacao`**, do mesmo tipo de `motivo_da_sucessao`, gravada por `emitir_ordem` na mesma
transação em que o ato nasce, por quem já tem autoridade para emitir. O nome acompanhou a correção:
`CumprimentoDeProvidencia` afirmava o que a linha não afirma, e virou `CitacaoDeDecisao`.

**A pertinência ao Marco é invariante persistente, e não promessa de comando.** A primeira redação
da trigger conferia apenas o Edital, e deixava aberta a porta que a citação existe para fechar: uma
gravação direta ligaria uma decisão pertinente a `M1` a um ato de `M2`, liberando indevidamente a
definitiva de `M2`. `citacao_coerente` passa a conferir Perfil e Marco — e o ramo que precisa ler a
enumeração de Etapas do JSON normativo **não é inédito**: é o caminho que
`check_ordering_act_provenance` já percorre em `classificacao/0003`. O detalhe está em
[data-model.md](./data-model.md) §10.1.

**O custo, registrado por inteiro**, como a orientação exigiu:

| dimensão | o que muda |
|---|---|
| estrutura | `classificacao.CitacaoDeDecisao`: `ato` FK PROTECT, `decisao` FK PROTECT, `UNIQUE(ato, decisao)`, append-only |
| dependência entre apps | `classificacao → recursos`, por referência tardia (`"recursos.DecisaoRecurso"`). É a segunda aresta desse tipo, ao lado da de `resultados` |
| migration | `classificacao/0004`, dependente de `recursos/0001`. O grafo continua acíclico |
| coerência | trigger `citacao_coerente`: espécie, Edital, **Perfil e Marco**, nos dois ramos de objeto atacado (§10.1) |
| autorização | nenhuma nova: quem cita é quem emite o ato, pela autoridade que a 015 já exige. A tela de emissão passa a oferecer as decisões pendentes daquele marco |
| privilégios | a tabela entra em `TABELAS_APPEND_ONLY`, e as suas duas triggers em `TRIGGERS_POR_APP["classificacao"]` |
| fatiamento | a tabela e a sua migration só entregam a US7, e por isso vivem **na F6**, e não na fundação |

**Alternativa descartada — relaxar para "qualquer sucessor cumpre".** É a redação original, e ela
devolve o problema: a pendência some sem que ninguém tenha corrigido nada. Não foi adotada, e não
deve ser adotada em silêncio: se a instituição a preferir, é escolha dela, e volta à mesa.

---

## Resumo das decisões

| # | Decisão | Custo |
|---|---|---|
| T-001 | App novo `recursos`; FK da decisão mora no `ResultadoEtapa` | referência tardia, grafo de migrations acíclico |
| T-002 | `resultados/0005`, só esquema, sem backfill, sem desligar trigger | 4 constraints novas, 2 recriadas, 1 trigger recriada |
| T-003 | Duas FKs anuláveis + `CHECK` de exatamente uma | duas colunas |
| T-004 | Manager `vigentes` + `order_by` determinístico + teste estrutural | o inventário inteiro da §2.5 |
| T-005 | Papel novo `julgador`; invólucro da 017, não o da 011 | uma entrada em `PAPEIS` |
| T-006 | Impedimento no ponto, nunca na listagem | 5 perguntas por ato de julgamento |
| T-007 | `appealWindow` no marco; `DEGRAUS_DE_MARCO`; `SCHEMA_VERSION` 8 | **o maior item da feature** |
| T-008 | Contagem pura; zona institucional sobe para módulo compartilhado | refatoração pequena e obrigatória |
| T-009 | Visibilidade em 3 consultas, norma histórica pela versão do ato | seletor novo |
| T-010 | `aferir()` recebe a natureza; 5 fatos, todos de existência | assinatura muda; 1 coluna na publicação |
| T-011 | *Non reformatio* em dois pontos; Resultado protegido citado | 1 FK na decisão |
| T-012 | Protocolo com alfabeto compartilhado, prefixo próprio | nenhum |
| T-013 | Três registros fora do app | fáceis de esquecer, e o teste não os inventa |
| T-014 | As garantias centrais exigem PostgreSQL na suíte | disciplina de entrega |
| T-015 | Cumprimento por citação **publicada**, apurado por marco; sem ato autônomo | 1 tabela, 1 migration, 1 aresta entre apps |
