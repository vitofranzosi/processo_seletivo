# Avaliação de capacidade — os sete Editais contra a `main` pós-021 e pós-022

Releitura do repositório em `6013929` — `main` com a `021` (Sorteio público auditável) e a `022`
(Supervisão do Processo) integradas — contra a mesma amostra de sete Editais reais do Ifes/Cefor
lida em [`avaliacao-de-capacidade-editais-2026-09-07.md`](avaliacao-de-capacidade-editais-2026-09-07.md).
A medição anterior é a de [`2026-09-08`](avaliacao-de-capacidade-editais-2026-09-08.md), em `2910c06`.

> **Adendo de 10/09/2026 — a `023` entrou na `main` e não move nada aqui.** Enquanto este
> documento era escrito, a `023` (*criar Edital a partir de Edital anterior*) foi integrada por
> outro PR. Conferi a única lacuna que ela poderia tocar — a **P-6** — e ela permanece aberta, por
> recusa explícita da própria `023`. O que mudou está em [§A `023` e a P-6](#a-023-e-a-p-6), no fim.
> Nenhuma contagem deste documento se altera.

**Este documento não relê os Editais**, pela mesma disciplina do anterior: a leitura de 07/09
continua valendo como leitura, e as perguntas P-1 a P-9 continuam sendo as de
[`achados-editais-externos.md`](achados-editais-externos.md). O que mudou foi o repositório, e é o
repositório que se remede aqui — cada lacuna conferida de novo no código, com a linha.

## Veredito

**O bloqueio de maior alcance da amostra deixou de existir.** O sorteio era o que impedia quatro
dos sete Editais de produzir resultado nenhum, e a `021` o trouxe para dentro do certame — do
universo congelado à ordem que qualquer pessoa reproduz. Fechou também a L-6, que era a última
ressalva de autoria do 76.

**Os dois eixos não são o mesmo, e as medições anteriores os misturavam.** Um Edital pode ter o
mecanismo que o conduz e não ter documento publicável — é o caso do 173 desde 07/09, contado como
"vai até a lista publicada" enquanto a L-1 o impedia de existir como documento. Aqui eles vão
separados, e a linha que interessa é a terceira, que é a interseção das duas primeiras.

```
autoria   — documento publicável inteiro          08/09  3 de 6      hoje  3 de 6   (o 76 perde a ressalva)
condução  — o mecanismo produz a ordem            08/09  2 de 7      hoje  5 de 7
certame   — publicável E conduzível até a ordem   08/09  1 de 7      hoje  2 de 7
```

O mecanismo andou três passos: 77, 57 e 28 passaram a ter como produzir a ordem. O certame inteiro
andou um, porque dois desses três não têm documento — e o quarto Edital de sorteio, o 76, não se
moveu por um motivo que não é o sorteio.

**A L-1 sozinha leva a terceira linha de 2 para 5.** Fechada ela, 57, 28 e 173 passam a ser
publicáveis, e os três já têm mecanismo — o dos dois primeiros é o mesmo que o 77 exercita hoje.
Nenhuma outra lacuna aberta tem esse rendimento, e nenhuma delas depende da 014, 016 ou 019.

## O que a 021 fechou — estado verificado

O que faltava era o **fato que alimenta o resultado**: o sistema produzia `ResultadoEtapa` a partir
de Avaliação humana e de Ocorrência, e nada mais. Agora produz ordem a partir de sorteio, e a ordem
é auditável por fora.

| O que faltava | Onde está hoje |
|---|---|
| o universo comprometido antes da semente | `RelacaoDeHabilitados` (`sorteios/models.py:29`), publicada e imutável, sucedida quando corrigida |
| e comprometido sem digitação | projeção das inscrições submetidas do recorte, numeradas por protocolo crescente (`sorteios/domain/projecao.py`), com o critério gravado em `criterio_de_projecao` (`sorteios/models.py:49`) |
| a semente vinda de fonte pública externa | `OcorrenciaDaFonte` (`sorteios/models.py:143`) e a fonte da Loteria Federal (`sorteios/infrastructure/fontes/loteria_federal.py`) |
| a proveniência que amarra relação, ocorrência e ordem | `Sorteio` (`sorteios/models.py:197`), `OneToOne` imutável com o ato |
| a ordem como ato de ordenação, e não como entidade paralela | `OrigemDaOrdem.SORTEIO` em `AtoDeOrdenacao.origem` (`classificacao/models.py:22,40`), com `universo` guardando proveniência e `stageResults` vazio (`:57-80`) |
| a dimensão da lista de concorrência | `AtoDeOrdenacao.lista_id` (`classificacao/models.py:36`) e `PublicacaoResultado.lista_id` (`divulgacao/models.py:56`), cada um com a constraint de raiz partida em duas parciais |
| não recomputar o que não veio de cálculo | `estado_do_marco` despacha pela origem e afere o ato de sorteio contra a relação, não contra as Etapas (`classificacao/application/selectors.py:53,114`) |
| o método como conteúdo versionado, e não escolha do executor | `drawMethod` no marco de classificação (degrau 10, `publicacoes/domain/elevacao.py:102`), lido e nunca escrito pelo sorteio (`sorteios/domain/metodo.py`), com `metodo_hash` gravado na relação antes de existir semente (`sorteios/models.py:48`) |
| qualquer pessoa reproduzir a ordem | manifesto público e verificador que recalcula **das entradas**, nunca das posições gravadas (`sorteios/application/verificacao.py:1-14`), em `portal/urls.py:82,87,92` |
| o resultado publicado dizer que veio de sorteio | `divulgacao/infrastructure/documento.py:181` |
| anular um sorteio sem apagá-lo | sucessão com motivo, pela forma que `AtoDeOrdenacao.ato_anterior` já tinha; anular custa Retificação (D-017) |
| **L-6** — onde o evento acontece | `EventoCronograma.location` (`editais/models/cronograma.py:50`), campo único de texto, sem valor institucional por padrão, no snapshot em `publicacoes/application/publish_edital.py:210` (degrau 11, `elevacao.py:114`) |

`SCHEMA_VERSION` foi de 9 para **11** (`shared/canonical.py:105`): dois degraus, ambos da `021`.

**E o que ela recusou, de propósito.** O *Out of Scope* da `021` é explícito, e um item dele
carrega uma frase que vale repetir aqui porque governa a contagem acima: *"Corte e progressão entre
Etapas — sem elas o 77/2026 não fecha, e a spec diz isso"*. Ficaram igualmente fora a ocupação de
vagas e a concorrência concomitante, a convocação e a suplência, a heteroidentificação, o recurso
contra a relação de habilitados e o **quadro de vagas estruturado por modalidade** — a L-1.

## O que a 022 acrescentou, e por que não move esta contagem

A `022` não é feature de Edital: ela observa a **fronteira** entre as features — o Processo acima
do Edital e o tempo acima de todos — e informa que existe um problema sem se tornar uma segunda
implementação do domínio que o resolve. Não escreve em tabela alguma, e o teste de fronteira
(`backend/tests/integration/supervisao/test_fronteira.py`) é o que mantém esse corte.

Ela **não fecha lacuna nenhuma da amostra**, e não deveria: nenhum dos sete Editais fica mais
publicável ou mais conduzível por causa dela. O que ela muda é quem preside ter onde ver que o
prazo corre e que existe condição impedindo o próximo ato — inclusive, agora, a de marco de
sorteio sem método declarado (`interface/supervisao.py:661`).

Ela também **fixou a numeração do arco**, e isso vale para a leitura de qualquer roadmap daqui em
diante: *012 conclui avaliações; 013 oficializa resultados de Etapa; **014** determina progressão;
015 ordena; **016** ocupa vagas*; e a **019** convoca. Os três números continuam reservados e sem
spec: `specs/` salta de `018` para `020`, e segue em `021`, `022` e `023`.

## Por Edital

| Edital | Autoria | Mecanismo até a ordem | O que falta depois |
|---|---|---|---|
| **77/2026** FIC, vagas remanescentes | publicável inteiro | **passou a produzir**: sorteio, ampla concorrência, `lista_id` nulo | corte dos suplentes analisados (014) e convocação (019) |
| **76/2026** Secretaria Escolar, CR | **publicável inteiro** — L-6 fechada, a coluna LOCAL tem onde ir | **bloqueada, e por outro motivo**: o universo é projeção das inscrições submetidas, e as do 76 acontecem no SIGAA (P-8) | impugnação por quem não é candidato (P-4) |
| **57/2026** unificado, 2 cursos | **não** — resta a L-1 | **passou a ter mecanismo**: três listas, três atos raiz, um marco — esperando o documento existir | heteroidentificação (L-2) e 2ª instância com órgão distinto |
| **28/2026** Informática na Educação | **não** — resta a L-1 | **idem**, 7 polos × 3 modalidades | heteroidentificação (L-2) e ocupação de vagas entre modalidades (016) |
| **173/2025** Designer Educacional | **não** — resta a L-1 | mecanismo computado, até a lista, como em 07/09 | ordem de convocação e heteroidentificação |
| **14/2026** Orientador de TFC | publicável inteiro | o mais próximo, como em 07/09 | os mesmos quatro pontos, nenhum tocado |
| **46/2026** técnicos integrados | fora do alvo do produto por decisão | | |

**O 14/2026 continua sendo a medida da distância**, e para exatamente onde parava: o corte de dez
por código para a entrevista (014), a cascata Grupo 1 → 2 → 3 na convocação (016/019), o terceiro
critério de desempate (L-4) e o barema das duas fichas (D-4 da `015`). Nada disso é de sorteio, e
por isso nada disso se moveu.

**A heteroidentificação alcança quatro, e a tabela de 07/09 dizia dois.** O §L-2 daquele
documento enumera 57, 28, 173 e 46 como os Editais em que a Etapa se aplica a quem declarou a
modalidade; a tabela por Edital da mesma leitura só a nomeava no 57 e no 173, porque listava o
bloqueio principal e não a lista inteira. A coluna acima segue o §L-2, que é o enunciado mais
específico dos dois.

**O 76/2026 trocou de bloqueio, e é a troca que interessa.** Até 08/09 ele parava no sorteio, que
não existia; hoje o sorteio existe e ele para antes — a relação de habilitados **é projeção de
fatos oficiais já existentes** (D-011), e as inscrições dele não estão neste sistema. A P-8, que
era uma observação sobre origem de inscrição, virou o bloqueio operacional de um Edital inteiro.

## As lacunas de autoria que continuam abertas

Conferidas de novo hoje, uma por uma, em `6013929`.

| Lacuna | Estado verificado |
|---|---|
| **L-1** quadro de vagas por modalidade | `ModalidadeConcorrencia` (`editais/models/perfis.py:56`) segue com `code`, `name` e `description`; `RegraNormativa.percentage` (`:224`) segue sendo um decimal só; `PerfilVaga.immediate_vacancies` (`:21`) segue guardando o total do Perfil. **É o único bloqueio de autoria de 57, 28 e 173** |
| **L-2** aplicabilidade da Etapa | `EtapaAvaliacao` (`editais/models/etapas.py:11`) continua sendo do Edital e alcançando todos os Perfis, e a docstring continua adiando a mudança para "quando houver um Edital real que precise disso" |
| **L-3** parcela nomeada de Etapa no desempate | `CriterioDesempate.MAIOR_PONTUACAO_NA_ETAPA` (`editais/models/perfis.py:191`) endereça a Etapa inteira, e `Avaliacao.pontuacao` continua sendo um número só |
| **L-4** fato que não é número nem data | `FatoDeclarado.Tipo` (`editais/models/perfis.py:90`) ainda tem só `DATA` e `INTEIRO` |
| **L-5** anexos | fechada pela `020` |
| **L-6** local do evento | **fechada pela `021`** |

**A L-1 ficou mais estranha do que era, e vale dizer por quê.** Depois da `021`, a modalidade tem
papel operacional: ela é o `lista_id` que reparte o universo, a relação, o ato e a publicação —
`sorteios/application/relacao.py:186` a resolve lendo `competitionModalities` do conteúdo
publicado. O sistema hoje **ordena por lista de concorrência e não sabe dizer quantas vagas cada
lista tem**. As duas metades do mesmo quadro deixaram de estar no mesmo lugar.

## As lacunas com endereço em feature futura

Todas onde estavam, exceto a que a `021` retirou da lista.

| Lacuna | Endereço | Estado verificado |
|---|---|---|
| sorteio como mecanismo | `021` | **entregue** |
| corte por alvo e progressão | `014` | inexistente; sem spec |
| ocupação de vagas, cotas, remanejamento, concorrência concomitante | `016` | `percentage`, `distribution` e `callRules` viajam no snapshot (`publish_edital.py:118-122`) e **ninguém os consome** fora das telas de composição (`interface/forms.py:729`) |
| convocação, chamada, suplência | `019` | inexistente; sem spec |
| ordem computada por lista de concorrência | — | **assimetria nova**: `emitir_ordem` (`classificacao/application/emissao.py:20`) não tem a dimensão `lista_id` que o sorteio tem. Ordem concomitante em AC e em cota existe **se vier de sorteio**, e não existe se vier de cálculo. É o que o 173 precisaria |
| barema estruturado | D-4 da `015` | `Avaliacao.pontuacao` é um decimal só |
| autopontuação vinculante | P-7 | inexistente |
| heteroidentificação | spec própria | inexistente — nenhuma ocorrência no código |
| validade do Edital e prorrogação | P-3 | `Edital` (`processos/models.py:34`) segue sem prazo de validade; 77 publica seis meses, 14 e 173 publicam dois anos, e o que fica publicado é prosa que nada consome |
| impugnação por quem não é candidato | P-4 | `Recurso.inscricao` segue obrigatório (`recursos/models.py:46`) |
| recurso contra a relação de habilitados | P-4 | os dois objetos atacáveis continuam sendo `PublicacaoResultado` e `ResultadoEtapa` (`recursos/models.py:53,60`). **A `021` acrescentou um artefato publicado que não é nenhum dos dois** — e todo Edital de sorteio o publica |
| Edital que deriva de outro | P-6 | inexistente — **e a `023` a recusou por escrito**; ver o adendo no fim |
| inscrição originada fora | P-8 | inexistente — e agora é bloqueio, não observação |
| requisito declarado e não verificado | P-9 | inexistente |
| segunda instância recursal | D-011 da `018` | inexistente |

## As pressões, atualizadas

As três de 07/09 seguem intactas — o limite de arquivo em dois lugares desde a `020`, a terceira
dimensão do `DocumentoExigido` (condição sobre a pessoa) e o custo de autoria da modalidade que é
do Perfil. A `021` acrescentou duas, e nenhuma delas é defeito:

- **A assimetria da lista de concorrência.** Registrada na tabela acima. Quando a `016` ou a
  ordenação computada por lista chegarem, a decisão já tem forma pronta para copiar — o que é raro
  o bastante para valer a nota.
- **A relação de habilitados é artefato publicado sem via de contestação.** A `021` a declarou
  fora de escopo com todas as letras, e a consequência é que o objeto mais atacável de um certame
  por sorteio é justamente o que o `Recurso` não alcança.

## Resíduos das duas features

Três, nenhum deles defeito de produto:

1. **A `022` tem uma tarefa em aberto**: `T055` — executar o `quickstart.md` inteiro, os cinco
   roteiros, com o papel exato de quem preside. As outras 57 estão marcadas, incluindo o
   `make lint check test-pg` da `T056`.
2. **A `021` não entrou na tabela de incrementos do `README.md`** — a `020` e a `022` entraram, e
   a `021`, que ficou entre as duas, não tinha a tarefa equivalente. *Corrigido junto com este
   documento.*
3. **[`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md) continua aberto**, e
   continua não sendo defeito.

## Onde as lacunas incidem, agora

| Lacuna | Linhagem | Estado |
|---|---|---|
| sorteio como mecanismo | spec própria (`021`) | **fechada** — desbloqueia 3 dos 4 Editais de sorteio; o 76 fica pela P-8 |
| L-6 local do evento | Cronograma | **fechada pela `021`** |
| L-5 anexos | autoria do Edital | fechada pela `020` |
| **L-1** quadro de vagas por modalidade | autoria (006/008), **antes** da 016 | aberta — bloqueia 3 dos 6, e é a de maior rendimento |
| L-2 aplicabilidade da Etapa | autoria; precondição da heteroidentificação | aberta |
| L-3 parcela de Etapa no desempate | mesma estrutura do barema (D-4 da `015`) | aberta |
| L-4 fato sem grandeza | `FatoDeclarado` e `CriterioDesempate`, ambos da `015` | aberta |

O achado de 07/09 era que **três das seis lacunas novas eram de autoria, e nenhuma dependia da
014, 016 ou 019 para existir**. Duas já fecharam — a L-5 pela `020`, a L-6 pela `021` —, e nenhuma
das duas exigiu um passo da fila de execução. Resta uma, a L-1, e ela é hoje a única coisa entre
três Editais e um sistema que já sabe conduzi-los.

---

## A `023` e a P-6

*Adendo de 10/09/2026, sobre a `main` em `f80e6e5`.*

A `023` — *criar Edital a partir de Edital anterior* — foi integrada enquanto este documento era
escrito. Ela é de autoria, e portanto a única lacuna da amostra que poderia tocar é a **P-6**:
*"um processo pode derivar de outro, e o que herda dele?"* — o 76/2026 declara preencher as vagas
não preenchidas pelo 52/2026, e o 77/2026 diz "vagas remanescentes" sem citar a origem.

**Não toca, e diz que não toca.** O *Out of Scope* da `023` traz o item com o nome da pergunta:

> *"**Derivação normativa entre Editais** — este Edital preenche as vagas que aquele não preencheu.
> É P-6 de `doc/achados-editais-externos.md`, e esta feature deliberadamente não lhe toca."*

A frase que governa a feature já separava as duas coisas: *"um Edital anterior pode ser o **ponto de
partida** de um novo Edital; nunca sua **continuação**"*. Reaproveitar configuração é composição;
herdar vaga não preenchida é norma.

**Mas uma coisa adjacente mudou, e vale registrar antes que confunda quem escrever a P-6.** Pela
primeira vez existe um vínculo legível por máquina entre dois Editais. Ele vive na **trilha de
auditoria**, não no domínio: a operação `REAPROVEITAR_EDITAL` grava como motivo a identidade da
`VersaoConsolidada` da origem (`editais/application/reaproveitamento.py:233-246`), e o comentário
explica a escolha — a versão, e não o Edital, porque um identificador só responde as duas perguntas.
Nenhuma migration acompanha a feature: **não há coluna nova em `Edital` apontando para outro
Edital.**

São, portanto, duas relações diferentes com a mesma aparência:

```
composição   "este Edital PARTIU daquele"        existe hoje, na trilha, para auditar quem copiou o quê
norma        "este Edital HERDA vagas daquele"   é a P-6, e continua sem existir em lugar nenhum
```

A P-6 dizia que *"a relação existe no texto publicado e não no domínio, o que significa que ninguém
consegue perguntar quantas vagas sobraram de onde"*. As duas metades da frase continuam verdadeiras.

**E a pressão de autoria que a `023` não alivia.** O custo registrado em 07/09 é o do Edital
**grande** — no 46, nove modalidades repetidas em cerca de setenta ofertas, seiscentas e trinta
linhas para dizer nove coisas. A `023` reduz o custo do Edital **recorrente**, que é outro eixo:
ela copia de um Edital para o seguinte, e não de um Perfil para os outros sessenta e nove do mesmo
Edital. As duas economias são legítimas e nenhuma substitui a outra.
