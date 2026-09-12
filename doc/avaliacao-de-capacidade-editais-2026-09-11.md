# Avaliação de capacidade — os sete Editais contra a `main` pós-024 e pós-025

Releitura do repositório em `d16459f` — `main` com a `024` (Descoberta e transparência no portal) e
a `025` (Quadro de vagas por modalidade) integradas — contra a mesma amostra de sete Editais reais
do Ifes/Cefor lida em
[`avaliacao-de-capacidade-editais-2026-09-07.md`](avaliacao-de-capacidade-editais-2026-09-07.md).
A medição anterior é a de [`2026-09-09`](avaliacao-de-capacidade-editais-2026-09-09.md), em
`6013929`.

**Este documento não relê os Editais**, pela mesma disciplina dos anteriores: a leitura de 07/09
continua valendo como leitura, e as perguntas P-1 a P-9 continuam sendo as de
[`achados-editais-externos.md`](achados-editais-externos.md). O que mudou foi o repositório, e é o
repositório que se remede aqui — cada lacuna conferida de novo no código, com a linha.

> **A `025` foi mesclada às 11h27 de hoje** (PR #102, merge `d16459f`). Esta avaliação é a primeira
> escrita depois disso, e a contagem que ela move é a que o documento de 09/09 já previa.

---

## Veredito

**A última lacuna de autoria da amostra fechou.** Desde 07/09 o achado que organizava estas
avaliações era que *três das seis lacunas novas eram de autoria, e nenhuma dependia da 014, 016 ou
019 para existir*. A `020` fechou a L-5, a `021` fechou a L-6, e a `025` fecha a L-1. **Não resta
lacuna de autoria aberta na amostra.**

```
autoria   — documento publicável inteiro          09/09  3 de 6      hoje  6 de 6
condução  — o mecanismo produz a ordem            09/09  5 de 7      hoje  5 de 7
certame   — publicável E conduzível até a ordem   09/09  2 de 7      hoje  5 de 7
```

A previsão de 09/09 era literal — *"a L-1 sozinha leva a terceira linha de 2 para 5"* — e é o que
aconteceu: 57, 28 e 173 já tinham mecanismo e passaram a ter documento.

**O único Edital do alvo que não é publicável e conduzível é o 76/2026**, e o que o segura não é
lacuna de autoria nem feature do arco reservado: é a **P-8**, inscrição originada fora. Isso muda a
natureza da pergunta de priorização — até hoje havia sempre uma lacuna de autoria disputando com o
arco; a partir de agora não há.

**E a segunda linha é a que não se move sozinha.** Condução parou em 5 de 7 e continuará parada:
os dois que faltam são o 76 (P-8) e o 46 (fora do alvo por decisão). Quem anda daqui para frente
não é mais *autoria* — é o arco `014`/`016`/`019`, que leva o certame **além** da ordem, e nenhuma
das três tem spec.

---

## O que a 025 fechou — estado verificado

O que faltava era a **quantidade**: o sistema sabia dizer que um Perfil tem modalidades e não sabia
dizer quantas vagas cada uma tem.

| O que faltava | Onde está hoje |
|---|---|
| a linha do quadro como entidade com identidade própria | `LinhaDoQuadroDeVagas` (`editais/models/perfis.py:72`), `perfil` em `CASCADE` e `modalidade` em `PROTECT` |
| a ampla concorrência ser uma linha, e não uma ausência | `modalidade` anulável, com **duas** constraints parciais — `NULL` não colide com `NULL` no PostgreSQL, e uma constraint só deixaria passar duas linhas gerais |
| o quadro ser conteúdo do Edital, e não configuração | `vacancyTable` no Perfil do snapshot (`publicacoes/application/publish_edital.py:212`), degrau **12** (`publicacoes/domain/elevacao.py:65`), `SCHEMA_VERSION = 12` (`shared/canonical.py:116`) |
| a soma conferida contra o total declarado | `vacancy_sum_mismatch` em duas metades — igualdade quando o quadro é completo, limite superior quando é parcial (`editais/domain/validation.py`) |
| retificar uma linha sem reescrever o quadro | `"/profiles/*/vacancyTable"` em `COLECOES_COM_CHAVE` (`publicacoes/domain/colecoes.py:41`), declarada **antes** da primeira emissão |
| o acervo anterior continuar legível | degrau 12 eleva com `vacancyTable: []`, e nenhuma tela passou a afirmar zero vaga |

**A declaração da coleção antes da emissão é o detalhe que não teria conserto.** Sem ela, o
endereçamento por identidade seria recusado, sobraria o endereçamento por posição — que o sistema
proíbe — e o primeiro Edital publicado com quadro nasceria **irretificável**. Endereço de
retificação não se conserta depois: a publicação é ato imutável.

**As duas metades do quadro voltaram para o mesmo lugar.** O documento de 09/09 registrou a
estranheza que a `021` havia criado: *"o sistema hoje ordena por lista de concorrência e não sabe
dizer quantas vagas cada lista tem"*. A modalidade era o `lista_id` que reparte universo, relação,
ato e publicação, e a quantidade não existia em lugar nenhum. Agora existe, no mesmo conteúdo
publicado de onde o `lista_id` já era lido.

**O percurso conduzido achou seis defeitos que teste de domínio nenhum pegaria** — quatro na
composição, um no documento publicado (duas tabelas com o mesmo nome dizendo coisas diferentes) e
um na lista de concorrência —, e os seis foram corrigidos com teste que os prende
([relatório](e2e/025-quadro-de-vagas/relatorio.md)). A suíte foi de **4358 para 4681 passando**, com
os mesmos 2 pulados deliberados.

---

## O que a 024 acrescentou, e por que não move esta contagem

A `024` é a primeira feature da amostra que **não publica nada** — e a spec diz isso com todas as
letras: *"cada informação que ela acrescenta à tela já é conteúdo normativo vigente; o que muda é
que passa a ser legível por quem ainda está decidindo"*.

Por isso ela **não fecha lacuna nenhuma** e não deveria: nenhum dos sete Editais fica mais
publicável ou mais conduzível porque o portal passou a mostrar cronograma, atribuições, carga
horária, remuneração e histórico de retificações antes da identificação.

**Mas ela criou o lugar onde uma pergunta da `025` vai bater.** O relatório E2E da `025` registrou
que *"a página pública da seleção não exibe o quadro"* — nenhum requisito o pedia, porque a `FR-169`
fala do **documento publicado**. Agora que existe uma feature cujo objeto é exatamente *tornar
legível na tela o que o ato já diz*, o quadro de vagas é a informação publicada mais óbvia que a
vitrine ainda não mostra. **Não é defeito de nenhuma das duas**, e é pergunta para quem decidir a
próxima feature de transparência.

---

## Por Edital

| Edital | Autoria | Mecanismo até a ordem | O que falta depois |
|---|---|---|---|
| **77/2026** FIC, vagas remanescentes | publicável inteiro | sorteio, ampla concorrência, `lista_id` nulo | corte dos suplentes analisados (014) e convocação (019) |
| **76/2026** Secretaria Escolar, CR | publicável inteiro | **bloqueada pela P-8** — as inscrições estão no SIGAA, e a relação de habilitados é projeção das inscrições deste sistema | tudo, e o bloqueio é anterior ao arco |
| **57/2026** unificado, 2 cursos | **publicável** — a L-1 fechou | três listas, três atos raiz, um marco | heteroidentificação (L-2 + spec própria) e ocupação entre modalidades (016) |
| **28/2026** Informática na Educação | **publicável** — a L-1 fechou | idem, 7 polos × 3 modalidades | heteroidentificação e ocupação (016), com reversão **por polo** (P-5) |
| **173/2025** Designer Educacional | **publicável** — a L-1 fechou | computado, até a lista | ordem por lista vinda de cálculo (decisão declarada, ver adendo de 10/09), heteroidentificação, autopontuação (P-7), requisitos não verificáveis (P-9) |
| **14/2026** Orientador de TFC | publicável inteiro | o mais próximo | corte de dez por código (014), cascata Grupo 1→2→3 (016/019), terceiro desempate (L-4), barema (D-4) |
| **46/2026** técnicos integrados | fora do alvo do produto por decisão | | |

**O 14/2026 continua sendo a medida da distância, e agora é o único que a mede.** Ele para
exatamente onde parava, e os quatro pontos são os mesmos de 07/09 — nenhum foi tocado, porque
nenhum é de autoria e nenhum é de sorteio. Com a autoria fechada, ele é o Edital que diz quanto
falta do arco.

**O 76/2026 é a única inversão da amostra**: publicável inteiro desde a `021`, e o mais distante de
ser conduzido. A P-8 deixou de ser observação sobre origem de inscrição e é o bloqueio operacional
de um Edital inteiro.

---

## As lacunas de autoria — a lista fechou

Conferidas de novo hoje, uma por uma, em `d16459f`.

| Lacuna | Estado verificado |
|---|---|
| **L-1** quadro de vagas por modalidade | **fechada pela `025`** — `LinhaDoQuadroDeVagas` (`editais/models/perfis.py:72`); `PerfilVaga.immediate_vacancies` (`:21`) segue guardando o total, e é **conferido contra a soma**, nunca sobrescrito por ela |
| **L-2** aplicabilidade da Etapa | **aberta** — `EtapaAvaliacao` (`editais/models/etapas.py:11`) continua sendo do Edital e alcançando todos os Perfis, e a docstring continua adiando a mudança para *"quando houver um Edital real que precise disso"* |
| **L-3** parcela nomeada de Etapa no desempate | **aberta** — `CriterioDesempate.MAIOR_PONTUACAO_NA_ETAPA` (`editais/models/perfis.py:257`) endereça a Etapa inteira, e `Avaliacao.pontuacao` continua sendo um número só |
| **L-4** fato que não é número nem data | **aberta** — `FatoDeclarado.Tipo` (`editais/models/perfis.py:156`) ainda tem só `DATA` e `INTEIRO` |
| **L-5** anexos | fechada pela `020` |
| **L-6** local do evento | fechada pela `021` |

**As três que restam não bloqueiam publicação de Edital nenhum da amostra.** É a diferença que este
documento registra: L-2, L-3 e L-4 impedem o Edital de ser escrito **com fidelidade**, não de ser
escrito. A L-1 impedia o documento de existir; estas impedem que ele diga a coisa certa.

- **L-2** é **precondição da heteroidentificação**, que alcança quatro Editais. Sem ela, uma Etapa
  de heteroidentificação criaria Atribuição para todo inscrito e a prontidão da `013` esperaria
  avaliação de quem nunca foi convocado. Metade da lacuna é dela — *aplicar-se a quem declarou a
  modalidade*, que é a dimensão que o `DocumentoExigido` já tem — e **a outra metade é da `014`**:
  aplicar-se aos dez primeiros de cada código depende de uma ordem que ainda não existe.
- **L-3 e D-4 são a mesma estrutura vista de dois lados**, e fazê-las separadas paga a mesma
  migration duas vezes: a Etapa precisa de **parcelas nomeadas**, o barema precisa produzi-las e o
  desempate precisa endereçá-las.
- **L-4** são **duas** mudanças, não uma: o tipo novo no `FatoDeclarado` e o tipo de critério que
  sabe consumi-lo — `CriterioDesempate.Tipo` só tem maior e menor valor, e um fato booleano
  comprovado por documento não tem grandeza a comparar.

---

## As lacunas com endereço em feature futura

| Lacuna | Endereço | Estado verificado |
|---|---|---|
| sorteio como mecanismo | `021` | entregue |
| quadro de vagas por modalidade | `025` | **entregue** |
| corte por alvo e progressão | `014` | inexistente; sem spec |
| ocupação de vagas, cotas, remanejamento, concorrência concomitante | `016` | inexistente; sem spec. `percentage`, `distribution` e `callRules` viajam no snapshot (`publish_edital.py:118-122`) e **ninguém os consome** — e agora `vacancyTable` (`:212`) viaja ao lado deles, lido pela conferência da soma e pelo documento, e por mais ninguém |
| convocação, chamada, suplência | `019` | inexistente; sem spec |
| ordem computada por lista de concorrência | — | decisão declarada (PR #85): `emitir_ordem` fixa `lista_id=None` (`classificacao/application/emissao.py:63`). A necessidade do 173 continua descoberta, contra decisão e não contra descuido |
| barema estruturado | D-4 da `015` | `Avaliacao.pontuacao` é um decimal só |
| autopontuação vinculante | P-7 | inexistente |
| heteroidentificação | spec própria | inexistente — nenhuma ocorrência no código; **depende da L-2** |
| validade do Edital e prorrogação | P-3 | `Edital` (`processos/models.py:35`) segue sem prazo de validade |
| impugnação por quem não é candidato | P-4 | `Recurso.inscricao` segue obrigatório (`recursos/models.py:46`) |
| recurso contra a relação de habilitados | P-4 | os dois objetos atacáveis continuam sendo `PublicacaoResultado` e `ResultadoEtapa`; a `RelacaoDeHabilitados` da `021` não é nenhum dos dois, e **todo Edital de sorteio a publica** |
| Edital que deriva de outro | P-6 | inexistente — recusado por escrito pela `023` |
| inscrição originada fora | P-8 | inexistente — **bloqueia o 76/2026 inteiro** |
| requisito declarado e não verificado | P-9 | inexistente |
| segunda instância recursal | D-011 da `018` | inexistente — **escopo recusado por decisão vigente**, e não lacuna descoberta |

---

## O arco reservado, e o que a L-1 fechada muda nele

O encadeamento aprovado em 10/09
([documento](decisao-encadeamento-l1-e-o-arco-operacional.md)) era:

```
L-1 ───────────────┐
                   ├── 016 ── 019
015 ── 014 ────────┘
```

Com a `025` na `main`, **a aresta `L-1 → 016` deixou de existir**: a `016` tem de onde ler quantas
vagas cada lista tem. Sobra

```
015 ✔ ── 014 ─ ─ ─ ─ 016 ── 019
```

- **`016 → 019` continua firme**: não se convoca sem saber quantos cabem.
- **`014 → 016` continua frouxa**, e é a nuance que evita erro de sequenciamento. O 28 sorteia,
  publica e ocupa, sem Etapa intermediária nenhuma. A aresta **enrijece só onde a regra de parada é
  a própria ocupação**, que é o caso do 77/2026.

**A `Q-1` continua aberta, e agora é o único bloqueio declarado do arco.** O repositório tem duas
frases incompatíveis sobre a fronteira `016`/`019` — o arco da `013` diz *"016 ocupa vagas"*, e
`specs/018-…/spec.md:1260` diz que *ocupação de vagas é da 019* — e nenhuma feature existe para
forçar a escolha. Decidir antes de especificar qualquer uma das duas: com a fronteira ambígua, saem
duas features que se sobrepõem ou uma lacuna entre elas.

**A `Q-2` foi respondida pela construção.** Ela perguntava se a L-1 seria entregue estruturada ou
adiada em favor de anexo binário, e o documento de 10/09 recomendava a forma estruturada porque
*"se a L-1 é entrada da `016`, entregá-la como binário é não entregá-la"*. A `025` a entregou
estruturada. **O acervo não bifurcou**, que era o custo irreversível registrado ali.

**A restrição que a `019` herda continua de pé**: a `D-007` da `018` definiu progressão retroativa
de efeito pleno quando nenhuma vaga estava ocupada, e a `019` terá de especificar seus efeitos
depois de convocação, aceite ou matrícula — **preservando a decisão vigente ou propondo formalmente
sua revisão**.

**E a `014` não está livre de decisões.** Ela não tem dependência estrutural previamente
identificada, o que é diferente de não pedir decisão: empate atravessando o corte, alvo fixo contra
alvo derivado de vagas, e progressão dependente da ocupação são dela.

---

## As pressões, atualizadas

As três de 07/09 seguem intactas — o limite de arquivo em dois lugares desde a `020`, a terceira
dimensão do `DocumentoExigido` e o custo de autoria da modalidade que é do Perfil. As duas da `021`
seguem: a assimetria da lista (hoje decisão declarada) e a relação de habilitados como artefato
publicado sem via de contestação.

**A `025` acrescenta uma, e é de norma, não de código.**

**A lacuna da `R-006` — o Edital que declara "Ampla concorrência" como Modalidade.** A `FR-176`
manda derivar as linhas das Modalidades declaradas, e a linha geral é a de `modalidade` nula. Num
Edital que declara uma Modalidade *chamada* "Ampla concorrência" — que a própria spec diz ser o
formato normal —, essa Modalidade fica sem linha, o quadro nunca fica completo, e a **igualdade** da
`FR-161` não roda ali. O limite superior da `FR-177` roda e pega a direção perigosa; o que sobra é o
quadro que soma **menos** que o total nesse formato. As duas saídas estão nomeadas na `research.md`
da `025`, com o custo de cada uma, e a escolha é do usuário. Verificado por
`tests/interface/test_compor_quadro.py::test_a_igualdade_nao_roda_onde_uma_modalidade_fica_sem_linha`.

**E duas observações que a `025` registrou e que não são pressão**: a recusa da referência cruzada
não ancora no controle (inferir a linha seria adivinhar), e a emissão do snapshot cresce com o
número de Perfis por causa de `profile.modalidades.order_by("code")`, que é **anterior** a esta
feature — o quadro entra no `prefetch_related` e custa uma consulta em qualquer caso.

---

## Resíduos

1. **A tabela de incrementos do `README.md` para na `022`.** Faltam a `023`, a `024` e a `025`. É a
   terceira vez que o resíduo aparece: a `021` já havia ficado de fora e foi corrigida junto com a
   avaliação de 09/09.
2. **[`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md) continua aberto**, e
   continua não sendo defeito.
3. **A `002` tem sete tarefas em aberto, e uma delas é bloqueio de implantação.** A `T056` —
   integração da autenticação institucional (LDAP) — diz, na própria tarefa, que *enquanto não for
   feito, esta feature não é implantável em produção*. Conferido hoje: **nenhuma ocorrência de LDAP
   no repositório**, e `ator_da_sessao` (`interface/identidade.py:78`) continua sendo o adaptador do
   seletor de demonstração. Com ela ficam a verificação com leitor de tela (`T053`), o ASES
   (`T054`), o design system do SUAP (`T055`/`T057`), a política de CSP (`T058`) e a medição de
   `SC-001`, `SC-002` e `SC-008` com servidores do Cefor (`T059`) — **nunca medidos**.
4. **A `013` tem a `T063` em aberto** — conferir `distribuicao.html` e `resultados.html` em 375 px.
5. **A `025` deixou um achado novo**:
   [`achado-teste-com-data-em-utc.md`](achado-teste-com-data-em-utc.md).

---

## Onde as lacunas incidem, agora

| Lacuna | Linhagem | Estado |
|---|---|---|
| sorteio como mecanismo | spec própria (`021`) | fechada |
| L-6 local do evento | Cronograma | fechada pela `021` |
| L-5 anexos | autoria do Edital | fechada pela `020` |
| **L-1** quadro de vagas por modalidade | autoria (006/008), antes da `016` | **fechada pela `025`** |
| L-2 aplicabilidade da Etapa | autoria; precondição da heteroidentificação | aberta |
| L-3 parcela de Etapa no desempate | mesma estrutura do barema (D-4 da `015`) | aberta |
| L-4 fato sem grandeza | `FatoDeclarado` e `CriterioDesempate`, ambos da `015` | aberta |

**O achado que organizou quatro avaliações seguidas encerrou-se.** Ele dizia que três das seis
lacunas novas eram de autoria e nenhuma dependia da `014`, `016` ou `019` para existir — e que,
portanto, havia sempre algo de alto rendimento a fazer **fora** da fila do arco. As três fecharam:
L-5 pela `020`, L-6 pela `021`, L-1 pela `025`, e nenhuma delas exigiu um passo daquela fila.

**A consequência para a próxima priorização, e é só isto que este documento conclui:** pela
primeira vez, o que separa a amostra de um certame completo está inteiro no arco reservado e na
P-8. Não há mais uma lacuna de autoria de maior rendimento competindo com ele.

> **Isto ordena; não prioriza.** *"Limites registrados são insumo de priorização, nunca a
> priorização em si"* (Constituição). Nenhuma linha daqui vira requisito, tarefa ou migration antes
> de a spec correspondente ser aberta pelo fluxo — e a `Q-1` precede a `016` e a `019`.
