# Avaliação de capacidade — seis Editais novos, e a amostra inteira contra a `main` pós-014

Leitura de uma **amostra nova** de Editais reais do Ifes/Cefor, e remedição da amostra inteira
contra `daded41` — `main` com a `014` (Corte e progressão entre Etapas) integrada pelo PR #105. A
medição anterior é a de [`2026-09-11`](avaliacao-de-capacidade-editais-2026-09-11.md), em `d16459f`,
antes da `014`.

**Este documento relê Editais**, e é o primeiro desde 07/09 que faz isso. Os de 08, 09 e 11 de
setembro remediam o repositório contra a leitura de 07/09; aqui a leitura é nova, e por isso volta a
alimentar [`achados-editais-externos.md`](achados-editais-externos.md), que é onde as perguntas do
domínio moram.

## A amostra nova

| Edital | Natureza | Quadro de vagas | O que ele traz |
|---|---|---|---|
| **58/2026** unificado, 3 cursos FIC | discente, sorteio | 3 códigos — 010 (200), 011 (200), 012 (120) | turmas com início próprio **dentro** de um código; regularização de indeferimento |
| **59/2026** Libras A1, presencial | discente, sorteio | 2 códigos — Turma 1 (40), Turma 2 (40) | **o código de vaga é a turma**, distinguida só por dia e horário |
| **69/2026** Multimeios Didáticos, chamada pública | discente, sorteio, CR | 6 vagas remanescentes | entrega presencial de documentos; **reclassificação**; impugnação sem recurso; procuração |
| **77/2026** FIC Acessibilização, remanescentes | discente, sorteio | 1 perfil (39) | **já estava na amostra** — é a versão retificada em 26/08, a mesma que a `014` citou |
| **78/2026** Libras A1, remanescentes | discente, sorteio | 2 códigos — Turma 1 (21), Turma 2 (40) | clone textual do 59; cronograma com inscrição **antes** da publicação |
| **158/2024** FIC Educação Especial, remanescentes | discente, sorteio, parceria SECADI | **2719 vagas, sem código nenhum** | a escala; alvo derivado **sem excedente**; elegibilidade alternativa; retificação que deixa buraco na numeração |

O 77 repete; os outros cinco são novos. A amostra acumulada passa de **sete para doze Editais**, dos
quais **onze estão no alvo do produto** — o 46/2026 continua fora por decisão.

O 158/2024 chegou depois dos outros cinco e é o mais antigo da amostra. Ele é da mesma família
textual do 58, do 59, do 77 e do 78 — dois anos antes —, e traz a única coisa que a amostra ainda
não tinha: **ordem de grandeza**.

**Cinco dos seis são o mesmo Edital com números trocados.** O 58, o 59, o 77, o 78 e o 158 compartilham
seções inteiras, palavra por palavra — o 158 é de dezembro de 2024, e a cláusula 6.3 dele é idêntica
à do 78, de agosto de 2026: a inscrição, o processo seletivo, o recurso, a matrícula, as
disposições finais. O 78 é o 59 com quatro alterações — título, uma frase de abertura, as
quantidades (80 → 61, sendo 40 → 21 numa linha) e o cronograma inteiro. **É exatamente o caso de uso
que a `023` entregou**, e a amostra nova é a evidência mais forte que ele já teve.

**E nenhum dos seis tem cota.** Todos são ampla concorrência pura: um único recorte, sem Modalidade
declarada, sem heteroidentificação, sem reversão. Isso confirma pela negativa o achado que organizou
o documento de 07/09 — *cota é escolha do Edital, e não propriedade da família* — e tem consequência
de medição: a amostra nova **não exercita** o quadro de vagas por modalidade que a `025` entregou,
nem a `R-006` que ela deixou aberta. O 158 vai além e **não tem quadro nenhum**: declara 2719 vagas
num parágrafo e não abre tabela de código de vaga.

---

## Veredito

**A `014` fechou o degrau que quatro Editais da amostra anterior esperavam — e os Editais novos
pedem literalmente a mesma operação.** A cláusula que a `014` generalizou aparece em cinco dos seis
lidos agora, com a mesma redação:

```
58/2026, 6.3   "serão analisadas as documentações dos primeiros candidatos sorteados até o
                número limite de vagas ofertadas por este edital"
158/2024, 6.3  idem, palavra por palavra — dois anos antes
58/2026, 6.10  "Para cada código de vaga, haverá a análise dos documentos de até 30 (trinta)
                suplentes para chamada imediata"
59/2026, 6.10  idem, palavra por palavra
78/2026, 6.10  idem, palavra por palavra
77/2026, 6.10  "Haverá a análise dos documentos de até 30 (trinta) suplentes"  — sem "por código",
                porque este Edital tem um Perfil só
158/2024       não tem cláusula de suplente analisado: alvo derivado, excedente zero
```

Nove Editais da amostra, cinco formas de dizer a mesma coisa, e a `014` executa as duas que
importam: **alvo derivado** do quadro de vagas e **excedente** fixo — e admite o excedente ausente,
porque `normalizar` grafa `surplusCount: 0` (`classificacao/domain/faixa.py:80`), que é o caso do
158. A generalização segurou contra
evidência que ela não viu ao ser escrita — que é o teste que a disciplina de
[`achados-editais-externos.md`](achados-editais-externos.md) impõe.

```
autoria   — documento publicável inteiro          11/09  6 de 6      hoje  11 de 11
condução  — o mecanismo produz a ordem            11/09  5 de 6      hoje  10 de 11
corte     — a ordem vira universo da Etapa        11/09  0 de 6      hoje   8 de 11   (2 n/a, 1 bloqueado)
convocação — a vaga é ocupada e chamada           11/09  0 de 6      hoje   0 de 11
```

A terceira linha é nova, e é o que a `014` acrescentou. A quarta é a que não se moveu e não se move
sozinha: **é a `016`/`019`, e nenhuma das duas tem spec.**

**O que restou é uma coisa só, e agora dá para dizer o nome dela.** Até 11/09 a resposta era "o arco
reservado", com três features dentro. Hoje o arco tem uma entregue e duas pendentes, e as duas
pendentes tratam do mesmo momento do certame: **o que acontece entre a análise documental concluída
e o aluno matriculado**. Todos os onze Editais no alvo param ali.

---

## O que a `014` fechou — estado verificado

Conferido em `daded41`, uma afirmação por linha.

| O que faltava | Onde está hoje |
|---|---|
| a regra de corte como conteúdo publicado | `regra_de_corte` (`editais/models/perfis.py:260`), degrau **13** (`publicacoes/domain/elevacao.py:125`), `SCHEMA_VERSION = 13` (`shared/canonical.py:125`) |
| as duas formas de alvo, sem uma gerar a outra | `FR-179`; alvo fixo é número publicado, alvo derivado lê a linha do quadro da `025` |
| o excedente — os suplentes — como quantidade própria | `FR-180`, normalizado no snapshot (`publish_edital.py`, `cutRule`) |
| o corte como ato imutável, e não como leitura de tela | `Corte` (`classificacao/models.py:217`), `ItemDoCorte` (`:360`), `FR-190` e `FR-192` |
| ficar fora do corte sem ser eliminado | `ItemDoCorte.Consequencia` (`:372`) — não grava Resultado, não elimina (`FR-212`) |
| a faixa seguinte, com causa declarada por quem a emite | `FR-202`, `FR-203`, `D-003` — e `FR-206` proíbe o sistema emiti-la sozinho |
| a Etapa governada participar só de quem progrediu | `FR-208` a `FR-211` |
| o corte ficar obsoleto quando a ordem que ele cita for sucedida | `FR-215` a `FR-218`, com bloqueio de publicação dependente (`FR-219`) |

**E a `014` fechou, de lambuja, a pressão que a `025` tinha deixado.** A `R-006` — o Edital que
declara "Ampla concorrência" como Modalidade, e portanto a deixa sem linha no quadro — tem resposta:
`modalidade_ampla_concorrencia` (`editais/models/perfis.py:54`), publicada como
`generalCompetitionModalityId` e conferida contra quem lhe der linha própria. O Edital **diz** qual
Modalidade corresponde à linha geral, em vez de o sistema adivinhar pelo nome — que é a saída que a
`025` havia recusado por escrito e continua certa em recusar.

A amostra nova não exercita esse campo: nenhum dos seis declara Modalidade nenhuma. A pressão
fechou contra os Editais da amostra **anterior**.

---

## Por Edital — a amostra inteira

| Edital | Autoria | Mecanismo até a ordem | Corte | O que falta depois |
|---|---|---|---|---|
| **58/2026** 3 cursos FIC | publicável | 3 códigos, 3 atos raiz, um marco | **alvo derivado + 30** | convocação, suplência, regularização, desistência por inércia (019) |
| **59/2026** Libras A1 | publicável | 2 códigos (as turmas) | **alvo derivado + 30** | idem |
| **69/2026** Multimeios | publicável | um ato raiz | **n/a** — não há Etapa após a ordem | convocação, entrega presencial (P-12), reclassificação (P-11) |
| **77/2026** FIC remanescentes | publicável | um ato raiz | **alvo derivado + 30** | convocação e suplência (019) |
| **78/2026** Libras A1 remanescentes | publicável | 2 códigos | **alvo derivado + 30** | idem |
| **158/2024** FIC Educação Especial | publicável | um ato raiz, **2719 vagas** | **alvo derivado, excedente 0** | convocação e suplência (019) — e a escala, medida abaixo |
| **57/2026** unificado, 2 cursos | publicável | três listas, três atos raiz | **alvo derivado + 20** | heteroidentificação (L-2 + spec própria), ocupação (016) |
| **28/2026** Informática na Educação | publicável | 7 polos × 3 modalidades | **alvo derivado + 15** | heteroidentificação, ocupação por polo (P-5) |
| **173/2025** Designer Educacional | publicável | computado, até a lista | **n/a** — CR puro, sem Etapa após a ordem | ordem por lista (decisão declarada), heteroidentificação, autopontuação (P-7), P-9 |
| **14/2026** Orientador de TFC | publicável | o mais próximo | **alvo fixo, 10 por código** | cascata Grupo 1→2→3 (016/019), terceiro desempate (L-4), barema (D-4) |
| **76/2026** Secretaria Escolar | publicável | **bloqueado pela P-8** | bloqueado antes | tudo |
| 46/2026 técnicos integrados | fora do alvo por decisão | | | |

**O 14/2026 deixou de ser a medida da distância.** Ele era o único que media, e o que o media eram
quatro pontos; um deles — *"corte de dez por código"* — fechou. Hoje quem mede é o conjunto: **onze
Editais parando no mesmo lugar**, e o lugar tem nome.

**O 69/2026 é a novidade estrutural da amostra.** Ele não tem análise documental entre a ordem e a
convocação: sorteia, publica o resultado, convoca e manda comparecer. É o primeiro Edital lido em
que o corte **não se aplica** por ausência de Etapa governada — e a `014` prevê exatamente isso, com
declaração explícita de que não governa nenhuma (`FR-224`). Também é o primeiro sem seção de
recurso: só impugnação, que é a `P-4`, que continua aberta.

**O 76/2026 continua sendo a única inversão**, e a `P-8` continua sendo o único bloqueio que não é
do arco.

---

## A escala, que a amostra nunca tinha posto

**O 158/2024 oferece 2719 vagas, e são vagas remanescentes.** A matriz curricular diz o tamanho da
oferta de origem sem rodeio: *"1 professor e 96 tutores (1 tutor para cada 50 alunos)"* — algo como
quatro mil e oitocentos alunos. É um FIC nacional, em parceria com a SECADI, num ambiente virtual de
outra instituição.

Até aqui, o maior Edital **no alvo** era o 28/2026, com 280 vagas; o 58 tem 520, mas repartidas em
três códigos de 200, 200 e 120. **O recorte é o que dimensiona o ato**, e o 158 não tem código
nenhum: são 2719 numa lista só.

Isso torna a pergunta de capacidade literal, e ela **foi medida**. A suíte de performance passou a
ler a população de `PERF_ESCALA` (`backend/tests/performance/escala.py`, padrão mil, nada muda sem a
variável), e rodou contra PostgreSQL local em 12/09, três vezes:

| Medição | Padrão (1000) | `PERF_ESCALA=3000` | `PERF_ESCALA=10000` | Teto declarado |
|---|---|---|---|---|
| tela da ordenação | 0,026 s | 0,069 s | **0,155 s** | 2,8 s |
| tela do corte | 0,035 s | 0,107 s | **0,277 s** | 3,0 s |
| consultas do cálculo da ordem | 7 → 7, de 5 a 1000 | 7 → 7, de 5 a 3000 | **7 → 7, de 5 a 10000** | não pode crescer |
| consultas do cálculo do corte | 16 → 16, de 1000 a 2000 | 16 → 16, de 3000 a 6000 | **16 → 16, de 10000 a 20000** | não pode crescer |
| consolidação num envio | 1000 inscrições | 3000 inscrições | **10000 inscrições** | `SC-002` promete mil |

**`tests/performance/` inteiro: 55 passando nas três execuções** — 21 s a 3000, 28 s a 10000. Nenhum
teto foi arranhado: a tela do corte usa **9,2%** do seu orçamento de relógio com dez mil
participantes, e o cálculo do corte chegou a **vinte mil** sem uma consulta a mais.

**O orçamento de consulta é a propriedade que segurou, e a curva é sublinear.** Dez vezes a população
custou **6×** na tela da ordenação e **7,9×** na do corte — e **zero** na contagem de consultas, nos
dois cálculos. É o que `SC-067` promete em palavras: *"o custo de abrir o corte é do conjunto, não uma
consulta por participante"*. O 158 não é problema de desenho, e o ponto em que o desenho dobra não
apareceu nesta faixa.

Três ressalvas, e nenhuma delas desfaz o resultado:

- **2719 é o alvo, não o universo.** O número de inscritos que disputaram essas vagas o Edital não
  diz. A medição de 10000 cobre o alvo com quase quatro vezes de folga, e cobre 20000 no cálculo do
  corte; acima disso é uma variável de ambiente, não um teste novo.
- **A máquina é um laptop, não o servidor do Cefor.** O `T059` da `002` — medir `SC-001`, `SC-002` e
  `SC-008` com servidores do Cefor — continua aberto e continua nunca medido. O que estes números
  provam com solidez é a **forma da curva**; o valor absoluto é desta máquina.
- **A relação de habilitados ao sorteio não entrou nesta medição.** A `021` a produz para todo
  inscrito submetido, e ela é o terceiro lugar onde o número aparece inteiro, ao lado do ato de
  ordenação e do corte.

**Isto deixou de ser achado em aberto.** A amostra passou a conter um Edital fora da faixa em que o
sistema tinha sido medido; a faixa foi estendida em uma ordem de grandeza, e ele cabe com folga.

---

## As quatro perguntas novas

Registradas em [`achados-editais-externos.md`](achados-editais-externos.md), com a evidência. Aqui
está só o que elas custam ao sistema de hoje.

### P-10 · A oferta se reparte em turmas, e a turma nem sempre é o recorte de vaga

Dois Editais do mesmo mês respondem a mesma necessidade em lugares incompatíveis:

```
59/2026   a turma É o código de vaga     Turma 1 (40) e Turma 2 (40), distinguidas por
                                         "Segundas e quintas-feiras, das 09h às 11h"
58/2026   a turma fica ABAIXO do código  código 011 = 200 vagas, repartidas em
                                         1ª Turma (120) e 2ª Turma (80), só no cronograma
```

**O 59 o sistema publica sem esforço**: a turma vira Perfil, com `code` e `name`, e o horário é texto
descritivo — mesma classe de `duties`, `workload` e `compensation`, que são texto por decisão
registrada da `006`.

**O 58 o sistema publica, e publica no lugar que o próprio Edital escolheu**: as duas turmas com suas
quantidades e datas de início são linhas do cronograma, e `EventoCronograma.description` é texto
livre de 500 caracteres. Funciona — e é honesto dizer que funciona porque o Edital **também** não
estruturou a repartição: ele não diz como um aprovado vai parar numa turma ou na outra.

A pergunta que fica para o domínio, e que nenhuma feature precisa responder hoje: **quando a
repartição por turma passar a ter consequência — vaga contada, ocupada ou revertida por turma —, ela
é um Perfil novo ou uma dimensão abaixo do Perfil?** É a `P-5` com o eixo do tempo, e a resposta
errada custa migration no quadro de vagas, que é publicado.

### P-11 · Que desfechos a convocação admite, além de aceitar e desistir?

Três, e nenhum deles é recurso nem eliminação:

| Desfecho | Onde | O que faz |
|---|---|---|
| **reclassificação** | 69/2026, 6.3 | não compareceu → vai para o **fim** da lista, e é convocável de novo depois de esgotados os suplentes |
| **regularização** | 58 e 59/2026, 8.2–8.3 | matrícula indeferida → o Cefor **reconvoca** quem foi indeferido, com 2 dias úteis para corrigir, se sobrarem vagas |
| **desistência por inércia** | 58, 9.2 · 59, 8.4 | não acessou o AVA em 6 dias, ou faltou à primeira semana → matrícula cancelada, próximo suplente convocado |

Os três são material da `019`, e o segundo tem um detalhe que importa: **é a Administração desfazendo
um ato desfavorável sem que ninguém tenha recorrido**. A superação append-only já está decidida para
o caso do recurso deferido ([`descoberta-018-decisao-c`](descoberta-018-decisao-c-superacao-de-resultado.md)),
e a `019` terá de dizer se este caso usa o mesmo mecanismo com outra origem ou se é outra coisa.

### P-12 · O sistema pode registrar o cumprimento de exigência que ele não guarda?

No 69/2026 a inscrição não carrega documento nenhum. Os documentos são entregues **presencialmente**,
em endereço publicado no cronograma, dentro de uma janela de cinco dias, podendo ser por procurador
com procuração simples (Anexo II) — e não voltam ao candidato: compõem o acervo da instituição por
cinco anos (8.8).

É o espelho da `P-8`. Lá a **inscrição** nasce fora do sistema; aqui a **comprovação** acontece fora
dele, e o sistema precisaria registrar que houve, quem atestou e o que concluiu, sem deter o
artefato. O `DocumentoExigido` de hoje (`editais/models/documentos.py:21`) descreve o que se anexa;
não há a forma "exigido, conferido presencialmente, não retido".

**E o 69 traz junto uma pessoa que o modelo de identidade não tem**: o menor de idade, cujo ato é
praticado pelo responsável legal, e o procurador, que age por terceiro. A inscrição é de uma pessoa
só, e é ela que o portal autentica.

### P-13 · Como se declara requisito satisfeito por uma entre várias vias?

O 158/2024 admite duas pessoas diferentes no mesmo Perfil: *"professores da Educação Básica **OU**
Superior … que possuam graduação **OU** aluno de curso de Licenciatura a partir do 6º período"*
(2.1). São dois caminhos de elegibilidade, e cada um se comprova com documento próprio.

**E o Edital não conseguiu dizer isso.** O item 5.4.c exige *"Comprovante de vínculo como professor
da educação básica de escola pública ou privada"*, marcado *"(Para todos os candidatos)"* — que é
exatamente o documento que o aluno de Licenciatura não tem, e para ele não há alternativa listada. O
documento publicado pede de metade do seu público-alvo uma prova impossível.

A evidência é de **um** Edital, e é defeituosa — que é o que a torna interessante: a instituição
precisou expressar *uma de duas vias, cada via com sua comprovação*, e o que saiu foi contradição.
Hoje `PerfilVaga.requirements` é uma lista plana de texto (`editais/models/perfis.py:20`) e
`DocumentoExigido` tem `required` booleano mais as dimensões de Perfil e Modalidade
(`editais/models/documentos.py:30,32,39`) — nenhum dos dois diz "um destes".

**Não confundir com a alternativa dentro de um requisito**, que os seis Editais praticam e que o
sistema já resolve: *"Carteira de Identidade; Carteira de Trabalho; CNH; …"* e *"Diploma ou
Declaração de Conclusão"* são várias formas de provar **o mesmo** fato, e cabem em `instructions`,
que é texto. O que não cabe é a ramificação **antes** do documento: quem é professor prova assim,
quem é licenciando prova assado.

---

## O que a amostra nova confirmou

Confirmação é sinal de que a generalização anterior estava certa, e cinco delas são fortes:

- **P-2 · oferta sem quantidade conhecida.** O 69 é cadastro de reserva sobre 6 vagas remanescentes
  — quantidade conhecida **e** lista sem fim, no mesmo Edital. `reserve_type` (`perfis.py:22`)
  admite os dois desde sempre, e o portal os **exibe** (`portal/views.py:160,171`).
  Continua sem nada que os **execute**: ocupar é da `016`.
- **P-3 · validade e suplente para turma futura.** Cinco Editais repetem a cláusula palavra por
  palavra — 6 meses, prorrogável por igual período, suplentes convocáveis para a nova turma —, e o
  mais antigo deles é de 2024. `Edital` (`processos/models.py:35`) segue sem prazo de validade.
- **P-4 · impugnação por qualquer cidadão.** O 69, 8.2, é a **terceira** evidência independente:
  cinco dias úteis, protocolo no campus, movida por quem não é candidato. `Recurso.inscricao`
  (`recursos/models.py:46`) continua obrigatório, e os dois objetos atacáveis continuam sendo
  `PublicacaoResultado` e `ResultadoEtapa` — nenhum deles é o Edital.
- **P-6 · um processo deriva de outro.** A amostra nova traz as **duas formas ao mesmo tempo**: o 69
  cita a origem pelo número (*"vagas não preenchidas pelo Edital Multicampi Nº 20/2026"*), e o 77 e
  o 78 são remanescentes que **não citam** a origem. Que o 78 é o resto do 59 o texto prova sozinho
  — é o mesmo Edital com 61 vagas no lugar de 80 —, e que o 77 é o resto do código 012 do 58 sai da
  data de início idêntica (06/10/2026) e do curso, não de citação nenhuma. A `023` deliberadamente não tocou nessa aresta, e continua certa: sem ela,
  ninguém consegue perguntar quantas vagas sobraram de onde.
- **P-9 · requisito declarado e não verificado.** Nos seis: *"ter acesso a computador com
  internet"*, *"ter habilidade no uso do computador"*, *"ter disponibilidade para frequentar as
  aulas presenciais"*. Não é peculiaridade de Edital de bolsa.

E duas confirmações de pressão já registrada:

- **A terceira dimensão do `DocumentoExigido` aparece nos seis.** *"Certificado de Alistamento
  Militar, no caso de candidatos do sexo masculino, maiores de 17 anos"* é condição **sobre a
  pessoa** — não é Perfil e não é Modalidade, que são as duas dimensões que o modelo tem
  (`documentos.py:32,39`). O 58 exige o certificado de pós-graduação só de quem se inscreveu num dos
  três cursos, e **essa** o modelo resolve: é a dimensão de Perfil.
- **Retificação é rotina.** Quatro dos seis são versões retificadas, e no 59 a retificação alcançou
  o cronograma inteiro.

---

## As pressões, atualizadas

As de 07/09 e da `021` seguem. A da `025` — a `R-006` — **fechou**, pela `014`. A amostra nova
acrescenta duas, e as duas são de fidelidade do documento, não de mecanismo.

**O texto repete dado estruturado, e nada os amarra.** O 59/2026 tem, na cláusula 10.8, uma citação
ao *"Edital Nº 59/2026 – … Língua Brasileira de Sinais (Libras **Básico - Nível A2**)"* — num Edital
que é **Iniciante - Nível A1** —, e o Requerimento de Matrícula do Anexo II repete o erro. O 78/2026,
que é o clone, **carrega os dois**, e ainda cita o número do 59 em vez do seu. É defeito de
reaproveitamento manual, e é honesto registrar o limite: **a `023` teria copiado o erro junto**. Ela
elimina a redigitação, não a prosa que repete o que já é campo. Se a instituição quiser que o número
e o título do Edital saiam da identidade dele em vez de serem redigitados no texto, isso é feature, e
não existe.

**O catálogo de seções é fixo, e os Editais reais não têm todos a mesma estrutura.** As doze seções
do documento publicado são declaração em código (`editais/domain/secoes.py`), e a validação exige
que **todas estejam presentes e que nenhuma textual esteja vazia**
(`_topologia_das_secoes`, `editais/domain/validation.py:403`). Foi decisão da `006`, e a razão está
escrita: *"É o que separa um documento institucional estruturado de um construtor de documentos"*.
O que a amostra mostra é o preço. Três Editais têm seção de **Matrícula**, três têm **Certificado**,
dois têm **Acesso ao ambiente virtual**, e o catálogo não tem nenhuma das três — esse texto vai para
Disposições Finais ou para Critérios de Classificação, e o documento publicado deixa de ter a forma
que a instituição publica. E o 69/2026, que **não tem recurso**, não pode simplesmente não ter a
seção: alguém terá de escrever ali que não cabe recurso. Isso é fidelidade de forma, não de norma, e
não impede Edital nenhum de ser publicado — mas é a primeira vez que a amostra o expõe em três
Editais de uma vez.

**A retificação real deixa buraco na numeração, e a do sistema não deixaria.** O 158/2024, retificado
em 31/01/2025, vai de `5.4` direto a `5.7`: as cláusulas removidas levaram os números embora e o que
ficou não foi renumerado. É a convenção jurídica — renumerar mudaria o endereço de tudo o que veio
depois, e é precisamente por isso que a `004` endereça por identidade estável e não por posição. Vale
registrar porque a consequência é visível: **um Edital retificado neste sistema não se parece com um
Edital retificado pela instituição**, e quem conferir um contra o outro vai notar.

**O cronograma não é conferido contra a data de publicação.** O 78/2026 publica em 05/08/2026 e abre
inscrições em **04/08/2026** — um dia antes. O sistema publica esse Edital como está: a única
conferência de ordem no cronograma é `end_at >= start_at`
(`ck_evento_end_not_before_start`, `editais/models/cronograma.py`), e `_periodo_de_inscricoes`
(`editais/domain/validation.py:1202`) só verifica quantos Eventos estão marcados como período de
inscrição. **Isto não é defeito**, e a `023` já registrou por escrito a razão: recusar Edital com
período vencido *"é regra de todo Edital, e não remendo desta cópia"*. Fica como observação de que a
instituição publica cronograma incoerente, e de que o sistema hoje não a impede nem a avisa.

---

## O arco, depois da `014`

```
015 ✔ ── 014 ✔ ─── 016 ── 019
```

**A aresta `014 → 016` endureceu.** O documento de 11/09 a chamava de frouxa e nomeava a exceção:
*"enrijece só onde a regra de parada é a própria ocupação, que é o caso do 77/2026"*. A amostra nova
transforma a exceção em maioria — a cláusula *"até que se preencha o número total de vagas
ofertadas"* está no 58, no 59, no 77, no 78 e no 158, e já estava no 57 e no 28. **Em sete dos onze
Editais no alvo, a causa da faixa seguinte é a ocupação**, e a ocupação é da `016`.

A `014` não ficou bloqueada por isso — a `D-003` resolveu declarando a causa por quem emite, o que é
a ponte provisória certa. Mas o custo operacional agora é mensurável: **em sete Editais, alguém terá
de digitar à mão, a cada rodada, quantas vagas ainda faltam.**

**A `Q-1` continua aberta, e continua sendo o único bloqueio declarado do arco.** O repositório tem
duas frases incompatíveis sobre a fronteira `016`/`019` — o arco da `013` diz *"016 ocupa vagas"*, e
`specs/018-…/spec.md:1260` diz que ocupação é da `019`. A amostra nova **acrescenta matéria dos dois
lados**: a reclassificação e a regularização da `P-11` são inequivocamente de convocação, e a causa
da faixa seguinte é inequivocamente de ocupação. Decidir antes de especificar qualquer uma das duas.

**A restrição que a `019` herda continua de pé** — a `D-007` da `018` definiu progressão retroativa
de efeito pleno quando nenhuma vaga estava ocupada, e a `019` terá de especificar seus efeitos
depois de convocação, aceite ou matrícula.

---

## As lacunas de autoria

Conferidas de novo hoje em `daded41`.

| Lacuna | Estado verificado |
|---|---|
| **L-1** quadro de vagas por modalidade | fechada pela `025` |
| **L-2** aplicabilidade da Etapa | **aberta** — `EtapaAvaliacao` (`editais/models/etapas.py:11`) continua sendo do Edital e alcançando todos os Perfis; a docstring continua adiando. **a metade que era da `014` fechou**: aplicar-se aos primeiros de cada código já não depende de uma ordem inexistente, porque é o que a `FR-208` faz. O que resta é a metade de autoria — a Etapa aplicar-se a quem declarou a modalidade |
| **L-3** parcela nomeada de Etapa no desempate | **aberta** — `MAIOR_PONTUACAO_NA_ETAPA` (`editais/models/perfis.py:290`) endereça a Etapa inteira |
| **L-4** fato que não é número nem data | **aberta** — `FatoDeclarado.Tipo` (`:173`) ainda tem só `DATA` e `INTEIRO` |
| **L-5** anexos | fechada pela `020` |
| **L-6** local do evento | fechada pela `021` |

**A amostra nova não abre lacuna de autoria nenhuma.** Os seis Editais são publicáveis inteiros com
o que existe hoje — o que era esperado, já que cinco deles são variações do mesmo texto e nenhum tem
cota. É a segunda avaliação seguida em que a autoria não se move, e é sinal de que ela chegou onde
precisava chegar para esta classe de Edital.

---

## Resíduos

1. **A tabela de incrementos do `README.md` não tem a `014`, e o número da suíte está uma feature
   atrás.** O README diz *"4681 passando e 2 pulados"* (`README.md:212`); a `014` fechou em
   **4862 passando e 2 pulados** (commit `9d1c4f4`). **É a quarta vez que este resíduo aparece** — a
   `021` ficou de fora e foi corrigida junto com a avaliação de 09/09; a `023`, a `024` e a `025`
   ficaram de fora e foram corrigidas depois da de 11/09.
2. **[`achado-anexo-sem-destinatario.md`](achado-anexo-sem-destinatario.md)** continua aberto, e
   continua não sendo defeito.
3. **A `002` tem sete tarefas em aberto, e a `T056` é bloqueio de implantação** — a autenticação
   institucional (LDAP) não existe no repositório, e `ator_da_sessao` continua sendo o adaptador do
   seletor de demonstração. Com ela ficam a verificação com leitor de tela, o ASES, o design system
   do SUAP, a política de CSP e a medição de `SC-001`, `SC-002` e `SC-008` com servidores do Cefor —
   **nunca medidos**.
4. **A `013` tem a `T063` em aberto** — conferir `distribuicao.html` e `resultados.html` em 375 px.
5. **[`achado-teste-com-data-em-utc.md`](achado-teste-com-data-em-utc.md)** segue aberto, da `025`.
6. **`PERF_ESCALA` mede a máquina de quem roda.** Os números desta avaliação saíram de um laptop
   contra PostgreSQL local; o CI roda a suíte de performance no tamanho padrão, e nada mede o
   servidor do Cefor. A variável torna a medição repetível, não portátil.

---

## O que este documento conclui

**Uma frase:** a amostra nova não pede nada que o sistema não saiba fazer **até o corte**, e pede
quatro coisas que ele não sabe fazer **depois dele** — convocar, ocupar, reclassificar e regularizar.

Três delas são da `019`. A quarta é da `016`. E entre elas está a `Q-1`, que ninguém decidiu.

**E o 158/2024 acrescentou uma pergunta de outra natureza, que não é de domínio — e ela já foi
respondida.** Ele cabe inteiro no modelo, e o que ele punha era **2719 vagas numa lista só**, acima do
maior recorte já medido. A suíte de performance passou a ler `PERF_ESCALA` e rodou até dez mil: **55
testes passando, contagem de consultas intacta de 5 a 20000, e a tela do corte em 0,277 s contra um
teto de 3 s**. O que continua nunca medido não é o tamanho — é a máquina: o `T059` da `002`, com
servidores do Cefor.

> **Isto ordena; não prioriza.** *"Limites registrados são insumo de priorização, nunca a
> priorização em si"* (Constituição). Nenhuma linha daqui vira requisito, tarefa ou migration antes
> de a spec correspondente ser aberta pelo fluxo — e a `Q-1` precede a `016` e a `019`.
