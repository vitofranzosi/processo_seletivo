# Research — Ocupação de Vagas entre Listas de Concorrência

**Feature:** `016` · **Base medida:** `daded41` · **Data:** 2026-09-12

Sete questões. A que mais importa é a `R-001`, porque ela define **o que o número central da
feature significa** — e a resposta não era óbvia, já que o fato que ocupa vaga pertence a uma
feature que não existe. Duas foram medidas contra o banco e contra o código, não deduzidas.

---

## R-001 · O que faz uma vaga estar "ocupada", se a `019` não existe

**Problema.** A feature inteira apura "quantas estão ocupadas". Mas aceite, matrícula e desistência
são fatos da `019`, que **não existe** — e a decisão de fronteira da `014` proíbe, com estas
palavras, usar *"quantidade de habilitados"* como sinônimo incorreto de *"vagas ocupadas"*. Sem
resolver isto, a feature apura um número que ninguém sabe interpretar.

**Decisão.** Vaga ocupada é **posição dentro da faixa do corte vigente cujo Resultado da Etapa
governada é `HABILITADA`**. São as duas condições juntas, e nenhuma sozinha.

**Rationale — é o que o próprio Edital chama de preenchimento.** O 77/2026, item 6.3, escreve o
mecanismo inteiro em uma frase:

> serão analisadas as documentações dos primeiros candidatos sorteados **até o número limite de
> vagas**; […] o **deferimento** da inscrição de cada candidato sorteado se dará após a análise da
> documentação; […] caso indeferida, haverá a análise do próximo candidato classificado,
> respeitando-se a ordem do sorteio, **até que se preencha o número total de vagas**.

O deferimento da análise **é** o preenchimento, nas palavras do Edital, e não a matrícula. O sistema
já tem esse fato: `ResultadoEtapa.consequencia` é `HABILITADA` ou `ELIMINADA`
(`resultados/models.py:42`), e a `013` o consolida.

**E a decisão não viola a advertência da fronteira**, porque a advertência é sobre *habilitados* —
todos eles. Aqui a conta exige **também** estar dentro da faixa: quem é habilitado fora do alvo não
ocupa nada. É a diferença entre "quantos passaram" e "quantos couberam", e é exatamente a que aquela
decisão mandou preservar.

**O limite, dito agora para não ser descoberto depois.** Quando a `019` existir, ocupação ganha
eventos posteriores — aceite, desistência, matrícula — e **esta decisão terá de ser revisitada**: o
mesmo recorte passará a ter um fato mais tardio que desfaz a ocupação. A `016` não deve gravar a
ocupação como verdade final, e é uma razão adicional para a apuração ser **ato sucedido** (`D-008`)
em vez de estado.

**Uma consequência imediata: metade do item 8.8 do 28/2026 é inalcançável hoje.** A cláusula tem
duas metades — sorteado nas duas listas é classificado na ampla (alcançável, e é a História 4) e
*"caso um candidato sorteado em vaga reservada desista, a vaga será preenchida pelo autodeclarado
imediatamente após"* (**inalcançável**: desistência não existe como fato). A segunda metade cai no
*Out of Scope* que a spec já declara — "aceite, suplência, posse e matrícula é a `019`" —, e fica
aqui nomeada para que ninguém a procure nos requisitos.

## R-002 · Onde a apuração mora, e em que sentido a dependência corre

**Problema.** `Corte` mora em `classificacao`. Pôr a apuração lá seria o caminho de menor atrito.

**Decisão.** Módulo novo, `ocupacao`, com a dependência em **um** sentido: `ocupacao` lê
`classificacao` e `publicacoes`, e **`classificacao` nunca importa `ocupacao`**. Quem chama a
emissão da faixa seguinte é `ocupacao.application.causar_faixa`.

**Rationale.** A `FR-255` manda o déficit ser entregue à `014` como causa. Se `classificacao`
lesse a apuração para descobrir a causa, o import circular seria o menor dos problemas — o grave
é que a `014` deixaria de ser compreensível sozinha, contra a fronteira de 11/09, que diz
literalmente que *"a `016` calcula o déficit e **causa** uma nova progressão pela `014`"*. A
seta é dela para a `014`.

**Alternativa descartada:** tudo em `classificacao`. Além do acoplamento, tornaria o nome do módulo
falso — ele ordena, combina, desempata e corta; ocupação de vaga é consequência disso sobre o
quadro, e não classificação.

## R-003 · Vigência e obsolescência não podem ser coluna

**Problema.** A leitura precisa saber qual apuração vale, e a tabela é append-only.

**Decisão.** Vigência é **derivada** (a apuração que ninguém sucedeu no recorte) e obsolescência é
**calculada**, devolvida com as causas nomeadas — nunca gravada.

**Rationale, verificado no código.** É o desenho do `Corte`, e a docstring dele diz por quê:
*"vigência não é coluna […] mantê-la exigiria `UPDATE` numa tabela em que o papel de runtime não o
tem"* (`classificacao/models.py:221`). E a obsolescência da `014` já devolve
`{"obsoleto": bool(causas), "causas": causas}` (`classificacao/application/corte.py:292`), com a
razão registrada: *"nunca 'divergências' — a `018` já pagou esse preço"*.

**Não é o provisionamento que recusaria a coluna** — ele apenas revoga `UPDATE` e `DELETE`, e
verifica a revogação. O que falharia é a tentativa posterior de atualizar a flag, barrada pelo
privilégio ausente e pelo gatilho. Ou seja: a coluna seria aceita e **nunca poderia ser mantida**,
que é o pior dos dois mundos.

## R-004 · A constraint parcial vem em par, e o `NULL` é a razão

**Problema.** `lista_id` nulo é a ampla concorrência. Uma `UniqueConstraint` sobre
`(edital, perfil_id, marco_id, lista_id)` parece bastar para "uma raiz por recorte".

**Decisão.** **Duas** constraints parciais: uma com `lista_id__isnull=True` sobre
`(edital, perfil_id, marco_id)`, e outra sobre os quatro campos.

**Rationale — medido, não suposto.** No PostgreSQL, dois `NULL` não colidem em índice único:

```sql
create temp table t (a int, b int);
create unique index on t (a, b);
insert into t values (1, null), (1, null);   -- INSERT 0 2
select count(*) from t;                      -- 2
```

Duas raízes de ampla concorrência no mesmo marco passariam com uma constraint só. É a cirurgia
que `uq_corte_raiz_por_marco` e a irmã dela já fazem (`classificacao/models.py:283`), e o mesmo
preço que a `025` pagou nas duas constraints da linha geral do quadro.

## R-005 · O nome e a forma da declaração da reversão

**Problema.** A `D-007` decidiu duas espécies de gatilho declaradas pelo Edital. Falta fixar nome,
forma e nível.

**Decisão.**

| Onde | Nome |
|---|---|
| conteúdo publicado | `vacancyReversion`, objeto no Perfil, irmão de `vacancyTable` |
| campos | `kind`: `ON_EXHAUSTION` \| `ON_BALANCE` |
| ausência | objeto `null` = **este Edital não declara reversão** |
| modelo | `PerfilVaga.especie_de_reversao` — **uma** coluna anulável |
| degrau canônico | **14** |
| Retificação | entrada em `CAMPOS_PERFIL` (`interface/retificacao.py:51`) |

**Rationale.** É objeto e não campo solto pela mesma razão que a `014` juntou os quatro campos da
regra de corte num degrau só: são uma decisão, e separá-los seriam duas elevações e dois caminhos de
leitura. É do **Perfil** porque é onde os Editais a escrevem e porque a Constituição manda cota ser
definida por Perfil. E é objeto nulo — nunca meio objeto —, como a regra de corte do degrau 13, para
que "não declarou" e "declarou incompleto" não se confundam.

**Por que objeto no publicado e uma coluna no relacional.** O objeto tem hoje **um** campo, e duas
colunas para ele seriam invenção — `especie_de_reversao` anulável diz tudo: nula é "não declara".
No conteúdo publicado, porém, a forma é objeto pela mesma razão do `cutRule`: é onde um campo novo
da mesma decisão entra sem inventar um segundo degrau. As duas formas não divergem porque a
conversão é explícita, e é o que o contrato fixa.

**Alternativa descartada:** campo por linha do quadro. Resolveria Editais heterogêneos que ninguém
leu, ao custo de catálogo de Retificação e tela por linha.

## R-006 · De onde sai o número sem estourar o orçamento de consulta

**Problema.** A tela lista recortes, e cada linha precisa de quatro números. Calcular cada um
abrindo o conteúdo publicado seria uma consulta por linha.

**Decisão.** `publicadas`, `ocupadas` e `efetivas` são **colunas do ato**, gravadas na emissão; a
tela lê colunas e SQL, nunca o snapshot por linha. `faltando` **não** é coluna: é
`efetivas − ocupadas`, aritmética da mesma linha. A distinção não é estética — `efetivas` depende de
**somar movimentos**, e `CHECK` não agrega, de modo que sem ela o limite `ocupadas ≤ efetivas` não
seria expressável no banco.

**Rationale.** É a lição que o `Corte` já registra no próprio modelo, com a medição escrita:
`etapa_governada_id` existe como coluna porque *"sem ela, a prontidão teria de abrir o conteúdo
publicado a cada listagem […] uma consulta por listagem que os orçamentos da 011, da 012 e da 015
não têm folga para pagar"* (`classificacao/models.py:265`). A apuração cai no mesmo padrão, e a
`D-008` — que já a fez ato — torna isso natural em vez de otimização.

**O que isso não autoriza:** a coluna é **cópia do que o ato leu no instante em que nasceu**, e não
segunda fonte de verdade. As duas nunca divergem porque a linha é append-only — o mesmo argumento
que o `Corte` usa para `universo.cutRule.governedStage` ao lado da coluna.

## R-007 · O invariante da soma constante, e o que ele não cobre

**Problema.** A `FR-247` exige que a soma por recorte depois da reversão seja igual à de antes.
Convém saber onde ele pode ser violado sem que ninguém perceba.

**Decisão.** O invariante é verificado sobre a **sequência de movimentos**, e não sobre o quadro
publicado: soma das quantidades do quadro + soma algébrica dos movimentos = soma das quantidades
efetivas. Teste de propriedade sobre sequências aleatórias de reversão e liberação.

**Rationale.** Reversão e liberação andam em sentidos opostos (§1.2 da spec), e é a
composição delas que erra — não cada uma. Um caso concreto: reverter 3 de PPI para a ampla e depois
liberar 1 vaga reservada de PPI por concorrência concomitante. Se a liberação voltar para a ampla, a
soma continua certa e **o recorte está errado** — exatamente o que a `FR-253` proíbe. Invariante de
soma sozinho não pega isso; por isso o teste é de soma **e** de recorte.

**O que ele não cobre, e fica declarado:** retificação do quadro entre dois movimentos. Ali a
soma de referência muda por ato normativo, e é a obsolescência (`FR-263`) que responde, não o
invariante.
