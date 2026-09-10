# Avaliação de capacidade — sete Editais anexos contra o repositório

> **Estado do repositório atualizado em 09/09/2026.** A leitura dos sete Editais que este
> documento faz continua valendo; o estado do código que ele mede é o de `368d9cd`. A `020` fechou
> a L-5 e a `021` fechou o sorteio e a L-6 desde então; a medição vigente está em
> [`avaliacao-de-capacidade-editais-2026-09-09.md`](avaliacao-de-capacidade-editais-2026-09-09.md),
> e a intermediária em
> [`avaliacao-de-capacidade-editais-2026-09-08.md`](avaliacao-de-capacidade-editais-2026-09-08.md).

Leitura integral de sete Editais reais do Ifes/Cefor contra o estado do repositório em `368d9cd`
(merge do PR #50, `018` integrada). A pergunta é uma só: **quanto da estrutura destes Editais o
sistema sustenta hoje, e o que falta que ainda não existe em lugar nenhum.**

Os Editais foram escolhidos sem critério e servem como amostra, não como especificação. Vale aqui a
disciplina de [`achados-editais-externos.md`](achados-editais-externos.md): Edital é evidência.

## O que este documento acrescenta

Seis dos sete já haviam sido lidos naquele documento, que registrou as perguntas P-1 a P-9. Este
aqui não as repete: ele **verifica no código** o que mudou desde então, e separa o que já tem
endereço do que não tem. Onde a lacuna já está registrada, o que se acrescenta é o estado
verificado — não "falta", e sim "declarável, nada consome, aqui está a linha".

## Veredito

O sistema é forte onde amadureceu: **autoria, publicação imutável, retificação com vigência,
inscrição com documentos, mesa de avaliação, consolidação, ordenação, divulgação e recurso**. Essa
espinha executa de ponta a ponta e não é pouco — é o arco 001→018 inteiro.

O corte que a amostra revela é anterior a tudo isso:

```
mecanismo de seleção        sorteio      4 de 7   (77, 76, 57, 28)
                            prova objetiva  1 de 7   (46)
                            títulos/entrevista  2 de 7   (14, 173)
```

O sistema produz `ResultadoEtapa` a partir de **Avaliação humana** e de **Ocorrência**, e nada
mais. Logo **cinco dos sete Editais não têm como produzir resultado nenhum** — não por falta de
regra classificatória, mas por falta do fato que a alimenta. A `015` já escreveu essa consequência
para o 57/2026; a amostra mostra que ela alcança a maioria do acervo, e não um caso.

Dos dois que restam, o **14/2026 é o que chega mais longe** e ainda assim para em quatro pontos; o
**173/2025** vai até a lista ordenada publicada e para ali, porque tudo o que ele faz depois é
convocar por uma tabela de ordem que o modelo guarda e ninguém lê.

### Por Edital

| Edital | Autoria do documento | Inscrição | Condução até o resultado |
|---|---|---|---|
| **77/2026** FIC, vagas remanescentes | perfil único, 39 vagas, sem modalidade — cabe; faltam os 3 anexos | integral | **bloqueada**: sorteio |
| **76/2026** Secretaria Escolar, CR | 5 polos com `UNLIMITED` — declarável; faltam anexos | inscrição é no SIGAA (P-8) | **bloqueada**: sorteio; sem recurso, com impugnação (P-4) |
| **57/2026** unificado, 2 cursos | **quadro de vagas não publicável** (L-1); faltam 6 anexos | integral | **bloqueada**: sorteio + heteroidentificação (L-2) + 2ª instância |
| **28/2026** Informática na Educação | idem, 7 polos × 3 modalidades | integral | **bloqueada**: sorteio |
| **173/2025** Designer Educacional | **quadro não publicável**; faltam 9 anexos, incluindo a ficha | integral | vai **até a lista publicada**; para na ordem de convocação e na heteroidentificação |
| **14/2026** Orientador de TFC | 7 códigos × 3 grupos — cabe; faltam 6 anexos, incluindo as duas fichas | integral | **o mais próximo**; para em 4 pontos (abaixo) |
| **46/2026** técnicos integrados | fora do alvo do produto por decisão; entra como evidência de forma completa |  |  |

**O 14/2026, em detalhe** — porque é o caso que mede a distância real. Executam: os sete códigos
como Perfis; os três grupos como Modalidades; uma inscrição por candidato (`Edital.
max_inscricoes_por_candidato`, que a `015` entregou justamente por causa dele); as duas Etapas
pontuadas; a média aritmética como `MEDIA_PONDERADA` normalizada com pesos iguais; o desempate por
idade e o por meses de docência, via `FatoDeclarado`. Não executam: o corte de dez por código para
a entrevista (014); a cascata Grupo 1 → 2 → 3 na convocação (016/019); o terceiro critério de
desempate (L-4); e o barema das duas fichas (D-4 da `015`).

## Lacunas com endereço — estado verificado

Todas já registradas em `achados-editais-externos.md` ou nos *Out of Scope* das specs. O que segue
é o **estado no código**, que em vários casos é "o campo existe e ninguém o lê".

| Lacuna | Endereço | Estado verificado |
|---|---|---|
| ocupação de vagas, cotas, remanejamento, concorrência entre modalidades | 016 | `RegraNormativa.percentage/distribution/call_rules` viajam no snapshot (`publicacoes/application/publish_edital.py:112-122`) e **nenhum código os consome**. A modalidade é uma **coluna** da posição (`classificacao/application/calculo.py:122`), não uma lista própria: não há como haver classificação concomitante em AC e em cota |
| corte por alvo e progressão | 014 | inexistente; é o que o 14 (10 por código) e o 57/28/77 (20/30 suplentes analisados) exigem |
| convocação, chamada, suplência | 019 | inexistente. `PerfilVaga.reserve_type` admite `UNLIMITED` desde a `001` e nada o executa (P-2) |
| sorteio como mecanismo | spec própria | inexistente. É o bloqueio de maior alcance da amostra |
| barema estruturado | D-4 da `015` | `Avaliacao.pontuacao` é um decimal só. As fichas do 14 e do 173 têm item, pontuação unitária, teto por item e teto global |
| autopontuação vinculante | P-7 | inexistente |
| heteroidentificação | spec própria | inexistente — e ver L-2, que é a forma estrutural do problema |
| validade do Edital e prorrogação | P-3 | `Edital` não tem prazo de validade. O 77 (6 meses) e o 14/173 (2 anos) o publicam |
| impugnação por qualquer pessoa | P-4, excluída na `018` | `Recurso` exige `inscricao` (`recursos/models.py:46`); o impugnante não é candidato |
| recurso contra listagem de inscritos | P-4 | `Recurso` ataca `PublicacaoResultado` ou `ResultadoEtapa`; a relação de inscritos/habilitados — publicada em **todo** Edital de sorteio — não é nenhum dos dois |
| Edital que deriva de outro | P-6 | inexistente. O 76 declara preencher o que o 52/2026 não preencheu; o 77 é "vagas remanescentes" sem citar origem |
| inscrição originada fora | P-8 | inexistente (76, via SIGAA) |
| requisito declarado e não verificado | P-9 | inexistente (173: Fapes, Lattes, adimplência, residência; 14: anuência da chefia) |
| segunda instância recursal | D-011 da `018` | inexistente. 57 e 46 a têm com **órgão distinto**: CLVA decide, CPVA julga o recurso |

## Lacunas sem endereço

Nenhuma das seis abaixo aparece em `achados-editais-externos.md` nem nos *Out of Scope*. Três delas
não são de execução, e sim de **autoria**: impedem o sistema de publicar o documento que os Editais
lidos publicam — antes, portanto, de qualquer discussão sobre ocupar vaga.

### L-1 · A Modalidade não tem quantidade de vagas

`ModalidadeConcorrencia` (`editais/models/perfis.py:56-69`) tem `code`, `name` e `description`.
Quantidade não existe nela, e `RegraNormativa.percentage` é **um decimal só**.

Os quadros reais são absolutos e irregulares:

```
57/2026, por curso     AC 56 · PcD 4 · PPI 20                        (total 80)
28/2026, por polo      AC 28 · PcD 2 · PPI 10                        (total 40)
46/2026, um curso      AC 18 · PPI 6 · Q 1 · PCD 1 · EP 1 · …        (total 36)
```

O de 46 nem sequer é gerável por percentual — `Q 1` e `PCD 1` saem de arredondamento sobre censo,
e o quadro publicado é o que vale. `PerfilVaga.immediate_vacancies` guarda o total do Perfil e não
a repartição.

**A consequência é de autoria, não de ocupação.** O quadro de vagas é seção obrigatória de todo
Edital com cota, e o snapshot não tem onde escrevê-lo. Isso é da linhagem 006/008, e é anterior à
016: mesmo que ninguém nunca ocupe vaga pelo sistema, o documento precisa dizer quantas são.

### L-2 · A Etapa não tem aplicabilidade

`DocumentoExigido` restringe por Perfil e por Modalidade, e a ausência dos dois significa "vale
para todos" (`editais/models/documentos.py:1-14`). `EtapaAvaliacao` **não restringe por nada**: ela
é do Edital e alcança todo mundo (`editais/models/etapas.py:12-22`).

Os Editais exigem as duas restrições, e elas são de naturezas diferentes:

```
por modalidade declarada   heteroidentificação alcança quem se declarou PPI/PcD   (57, 28, 173, 46)
por corte derivado         a entrevista alcança os 10 primeiros de cada código    (14)
```

A primeira é **exatamente a dimensão que o Documento Exigido já tem**, e cabe no mesmo lugar: uma
Etapa que declara a quem se aplica. A segunda é outra coisa — depende de uma ordem que só existe
depois de uma Etapa anterior — e é da 014.

Sem a primeira, uma Etapa de heteroidentificação criaria Atribuição para todo inscrito, e a
prontidão da 013 esperaria avaliação de quem nunca foi convocado.

### L-3 · O desempate não alcança parcela de uma mesma Etapa

`CriterioDesempate.MAIOR_PONTUACAO_NA_ETAPA` endereça a Etapa inteira, e `Avaliacao.pontuacao` é um
número só. O 46/2026 tem seis critérios e **cinco deles são subnotas de uma prova única**:

```
1º LP · 2º Matemática · 3º Ciências · 4º História · 5º Geografia · 6º maior idade
```

Modelar cada disciplina como Etapa própria resolveria o desempate e estragaria o resto: peso, nota
mínima e eliminação passariam a existir por disciplina, quando a prova é uma e a nota mínima é
dela. É a mesma estrutura que o barema pede (D-4), vista pelo desempate — a Etapa precisa de
**parcelas nomeadas**, e o desempate precisa saber endereçá-las.

Isso não é do 46 sozinho: qualquer ficha de títulos com desempate por item cai no mesmo ponto.

### L-4 · Não há fato que não seja número nem data

`FatoDeclarado.Tipo` tem `DATA` e `INTEIRO`, e o próprio modelo diz que "o terceiro entra quando
aparecer o Edital que o exija" (`editais/models/perfis.py:72-105`). **Ele apareceu.** O 14/2026,
item 9.2(c), desempata por:

> candidato que tenha realizado o curso "Moodle 3.9 para Educadores" OU "Moodle 4 para Educadores"

É um fato **comprovado por documento**, verdadeiro ou falso, sem grandeza a comparar. Nem
`FatoDeclarado` sabe grafá-lo, nem `CriterioDesempate.Tipo` — que só tem maior/menor valor —
sabe consumi-lo. O 173/2025 tem um irmão dele nos requisitos ("curso de Moodle de no mínimo 60
horas").

### L-5 · O Edital não tem anexos

O catálogo de Seções é declarado, fixo, com onze entradas e nenhuma delas anexo
(`editais/domain/secoes.py:50-160`). Os Editais lidos têm **de dois a onze anexos**, e eles não são
ornamento:

```
formulários que o candidato devolve preenchidos   requerimento de inscrição · requerimento de
                                                  matrícula · autodeclaração étnico-racial ·
                                                  declaração de pertencimento · procuração ·
                                                  declaração da chefia imediata · termo LGPD
conteúdo normativo tabular                        quadro de perfil · ficha de avaliação ·
                                                  ficha da entrevista · conteúdo programático
```

Os do primeiro grupo são o caso mais agudo: são **Documentos Exigidos cujo modelo o próprio Edital
fornece**. Hoje o sistema sabe exigir o documento e não sabe publicar o formulário que o candidato
precisa preencher para produzi-lo — o candidato é mandado a um anexo que o documento publicado não
contém. O Cronograma é a exceção que confirma: ele é anexo em cinco dos sete e o sistema já o
gera, só não o nomeia como tal.

### L-6 · O Cronograma não publica onde o evento acontece

`EventoCronograma` tem tipo, descrição, datas e ordem. O 76/2026 publica uma coluna **LOCAL** por
evento; os demais dizem em prosa "nos sítios do Ifes e do Cefor", e quatro marcam evento com hora e
canal ("Sorteio às 10h, canal do Cefor no YouTube"). A hora cabe em `start_at`; o local, não.
Menor que as outras cinco, e ainda assim conteúdo publicado que o snapshot perde.

## Pressões sobre decisões já tomadas

Não são lacunas: são decisões declaradas no código que a amostra contradiz. Registrar, não decidir.

**O limite de arquivo é da aplicação, não do Edital.** `config/settings/base.py:137-138` afirma que
"um Edital não negocia tamanho de arquivo" (FR-046). Os sete Editais negociam: 7 MB em três deles
(77, 76, 57), 10 MB em dois (14, 173) — e dois publicam ainda um **limite de 50 páginas** que não
tem grafia nenhuma no sistema. Um limite publicado que o sistema não honra é norma que o próprio
sistema contradiz na tela do candidato.

**O Documento Exigido tem duas dimensões e nenhuma quinta forma** (`editais/models/documentos.py`).
A amostra traz uma terceira dimensão em todos os sete: condição sobre a pessoa — "certificado de
reservista, no caso de candidatos do sexo masculino maiores de 18 anos". Hoje isso vira documento
obrigatório para todos, ou opcional para todos. Note que a dimensão que falta é a mesma que a `015`
já criou para outra finalidade: `FatoDeclarado`.

**A modalidade é do Perfil** (`uq_modalidade_perfil_code`). Correto para os seis Editais pequenos.
No 46 as mesmas nove modalidades se repetiriam em cerca de setenta ofertas, cada uma com sua
`RegraNormativa` — seiscentas e trinta linhas para dizer nove coisas. Não é defeito de modelo; é
custo de autoria que nenhuma tela endereça, e é evidência de que a matriz `campus × curso × turno`
(P-5) cobra também na composição, não só na ocupação.

## O que a amostra confirmou

- **Retificação é rotina.** Seis dos sete arquivos são versões retificadas. O sistema faz isso, com
  vigência temporal e consulta histórica — é a capacidade mais madura do repositório e a que a
  amostra mais exercita.
- **A janela recursal é do marco, e não do Edital.** O 77 admite recurso só contra o resultado
  preliminar; o 57, só contra a heteroidentificação e a análise documental; o 76, contra nada. A
  `018` acertou ao pôr `janela_recursal` em `MarcoClassificatorio` e ao fazer a seção "Dos Recursos"
  **remeter** em vez de afirmar.
- **Modalidade como dado publicado, não enumeração.** Nove valores no 46, quatro no 173, três no
  57/28, nenhum no 77. Um enum teria migrado três vezes nesta amostra.
- **`max_inscricoes_por_candidato` é do Edital.** O 14 (7.8) e o 57 confirmam a leitura da `015`:
  o teto é sobre o total no certame, não sobre o Perfil.

## Onde as lacunas novas incidem

| Lacuna | Linhagem |
|---|---|
| L-1 quadro de vagas por modalidade | autoria do Edital (006/008), **antes** da 016 |
| L-2 aplicabilidade da Etapa | autoria do Edital; precondição da heteroidentificação |
| L-3 parcela de Etapa no desempate | mesma estrutura do barema (D-4 da `015`) |
| L-4 fato sem grandeza | `FatoDeclarado` e `CriterioDesempate`, ambos da `015` |
| L-5 anexos | autoria do Edital; toca `DocumentoExigido` |
| L-6 local do evento | Cronograma |

Três das seis são de **autoria** e nenhuma depende da 014, 016 ou 019 para existir. É o achado
principal deste documento: a fila registrada trata do que acontece **depois** do Edital publicado,
e a amostra mostra que o documento publicado ainda não é o documento que estes Editais são.
