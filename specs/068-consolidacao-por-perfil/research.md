# Research: O que se repete por Perfil sai uma vez no Edital em PDF

Decisões técnicas da implementação. As decisões de produto são `D-001` a `D-003`, na spec; aqui elas
aparecem só como premissa.

## R-001 — Um plano de consolidação, calculado antes de compor

**Decision**: uma função pura, `plano_de_consolidacao(snapshot)`, sobre o snapshot já grafado,
devolve tudo o que a composição precisa decidir antes de escrever: os grupos de atribuições (os da
`064`), de requisitos, de marcos e de tabelas de modalidades; o número de cada subseção comum; as
linhas e as colunas da tabela de vagas e a forma dela (matriz ou longa); as frases de reversão e de
convocação, com os códigos que as iniciam; e o item em que as linhas do método comum saem.

**Rationale**: a remissão sai **antes** do item a que remete, e o método comum pode ser impresso num
Perfil e remetido de uma subseção posterior — ou o contrário. O número tem de existir antes de a
primeira linha ser escrita, e tem de vir da mesma lista que numera as subseções: é o que a `064` já
fazia com `item_comum`, generalizado. E `itens_do_documento` e `tabelas_do_documento` (065, D-004)
precisam da mesma resposta sem compor o documento inteiro (R-009).

**Alternatives considered**: decidir durante a composição — a remissão precisaria de um número que
ainda não existe; duas passadas de composição — dobraria o custo e deixaria `itens_do_documento`
sem uma fonte própria.

## R-002 — A identidade é a dos itens que a composição escreveria

**Decision**: para requisitos e marcos, cada bloco é composto numa `Composicao` de rascunho, pela
mesma função que o imprime no Perfil, **sem o título que nomeia o Perfil** (`nomear_perfil=False`),
e a chave é a tupla dos itens produzidos — texto, fonte, corpo, recuo, espaço, alinhamento,
fronteiras de bloco. Para as tabelas de modalidades, a chave é o cabeçalho e as células impressas,
na ordem canônica (R-005). O agrupamento segue a regra da `064`: ordem do primeiro Perfil de cada
grupo, grupo de um só não existe, bloco vazio não agrupa.

**Rationale**: é a definição literal de `D-003` — "o documento os imprimiria com o mesmo texto,
linha a linha, com a mesma hierarquia". Uma chave por campos do snapshot teria de reproduzir cada
regra do compositor (o método que governa, a habilitação, a ordem dos critérios, as omissões da
`067` sob sorteio) e divergiria na primeira mudança dele. Os itens da composição são deterministas:
mesmo bloco, mesmos itens.

**Alternatives considered**: comparar o texto extraído do PDF — depende da paginação, que ainda não
existe; comparar o dicionário do marco sem identificadores — junta marcos que imprimem diferente
(método próprio idêntico ao comum, `_publica_a_mesma_norma`) e separa os que imprimem igual.

## R-003 — Edital de um Perfil não passa pelo plano

**Decision**: com um Perfil, `_perfis` segue o caminho de hoje, sem tocar uma linha; o plano devolve
"sem consolidação".

**Rationale**: FR-1356 (mesmos bytes) e a fixture de contrato `documento_publicado_v1.pdf`, que tem um
Perfil. Também a `064` já excluía esse caso.

## R-004 — A tabela de vagas em matriz, com a forma longa como degrau

**Decision**: legenda "Vagas por lista de concorrência"; cabeçalho "Perfil", "Ampla concorrência" e o
código de cada modalidade reservada (o nome, se não houver código); uma linha por Perfil com quadro
e com vaga imediata, na ordem do documento, com o código do Perfil e os números do quadro; "—" na
lista que o Perfil não declara. Sai logo depois da tabela de Perfis, como `_tabela`, com cabeçalho
repetido. **Forma longa** — "Perfil", "Lista de concorrência", "Vagas imediatas", uma linha por Perfil
e lista — quando a soma das larguras mínimas das colunas (a maior palavra de cada cabeçalho e de cada
célula, mais o padding) não cabe na área útil.

**Rationale**: o código no cabeçalho é o que permite dez listas na largura de uma página; o nome
está na tabela de modalidades, na mesma ordem. O critério da forma longa é o único que garante "nunca
coluna cortada": `_larguras_das_colunas` reparte o espaço entre colunas longas, e uma palavra maior
que a coluna seria partida ao meio por `_quebrar`.

**Alternatives considered**: coluna de total por Perfil — é o número de vagas da tabela de Perfis,
logo acima; repeti-lo seria informação em dobro. Nome da lista no cabeçalho — não cabe com mais de
quatro listas.

## R-005 — Uma ordem de listas para o documento inteiro (ED-11)

**Decision**: a linha geral primeiro; depois as modalidades reservadas na ordem em que aparecem nos
quadros, percorridos na ordem dos Perfis (a primeira ocorrência decide); depois as modalidades que
nenhum quadro declara, na ordem do snapshot. A modalidade de ampla concorrência declarada (a "grafia
armadilha", `generalCompetitionModalityId`) vai à frente das reservadas na tabela de modalidades,
onde ela aparece hoje. As tabelas de modalidades seguem essa ordem; a matriz também.

**Rationale**: é a ordem que o gestor declarou no quadro — a única ordem que alguém escolheu. A ordem
por código é da collation do banco (auditoria §8 C6).

## R-006 — Tabelas de modalidades agrupadas

**Decision**: uma tabela por grupo de Perfis de tabela idêntica (R-002), na ordem do primeiro Perfil
de cada grupo, logo depois da tabela de vagas e da frase de reversão. Legenda "Modalidades de
concorrência" quando o grupo é o Edital inteiro; senão "Modalidades de concorrência — Perfis A e B"
(ou "— Perfil A"), com a regra de enumeração da `064`. A colunas sem valor continuam omitidas.

**Rationale**: `D-002`. Perfis com modalidades diferentes continuam com a sua tabela, nomeada; o
grupo de um Perfil é uma tabela como as de hoje.

## R-007 — As frases, depois das tabelas e com os códigos quando não valem para todos

**Decision**: a reversão sai logo abaixo da tabela de vagas; uma frase por espécie, na ordem do
primeiro Perfil de cada uma. Sem prefixo quando todos os Perfis da tabela de vagas declaram a mesma
espécie; senão, "No Perfil A, " ou "Nos Perfis A e B, " antes da frase, com a primeira letra dela em
minúscula. A convocação sai depois das tabelas de modalidades, pela mesma regra, sobre todos os
Perfis do Edital. As frases são parágrafos da seção, com o espaço de bloco acima, justificadas.

**Rationale**: FR-1350 e FR-1351. A reversão é regra sobre as quantidades, e as quantidades saíram
do Perfil; a convocação é regra do Perfil inteiro, inclusive do que não tem quadro.

**O texto das frases não muda** — só o prefixo, quando o alcance não é o Edital inteiro.

## R-008 — Códigos inseparáveis em frase e em legenda

**Decision**: as frases com prefixo e as legendas que enumeram códigos são quebradas por pedaços
(como `_linhas_sem_partir` da `064`), e não por palavra: cada código é um pedaço. A frase escreve
cada linha já pronta, justificando todas menos a última. `_tabela` aceita a legenda como lista de
linhas.

**Rationale**: o caso que a `064` corrigiu — "ADS" no fim de uma linha e "- P06" na seguinte — aparece
em todo lugar que enumera códigos. O espaço inseparável não serve: a `grafia` o preserva no texto do
gestor, e `_quebrar` divide nele; mudar `_quebrar` mudaria a quebra de textos já compostos.

## R-009 — `itens_do_documento` e `tabelas_do_documento` leem o plano

**Decision**: as duas funções da `065` passam a ler o plano: subseções comuns de atribuições, de
requisitos e de marcos, com as naturezas `atribuicoes_comuns`, `requisitos_comuns` e
`marcos_comuns`; tabelas — a de Perfis, a de vagas (se houver linha), uma por grupo de modalidades, e
o Cronograma; com um Perfil, a contagem de hoje. `validation._DESCRICAO_DO_ITEM` ganha as duas
naturezas novas. O guardião `test_itens_do_documento.py` ganha casos com grupos de cada matéria.

**Rationale**: a `065` (D-004 dela) exige uma regra só para o que o documento numera, presa por um
guardião que compõe o documento de verdade. Sem a natureza nova em `_DESCRICAO_DO_ITEM`, a
conferência de remissões cai com `KeyError` no primeiro Edital consolidado — é o erro que o pedido
desta feature avisou.

## R-010 — Os marcos na subseção comum

**Decision**: título "N.k Marcos classificatórios comuns aos Perfis …" (`_linhas_sem_partir`); logo
abaixo, a frase do FR-1347; depois os marcos, compostos pela mesma `_marcos`, sem o rótulo "Marcos
classificatórios" (o título da subseção o substitui) e com o recuo deslocado um degrau para a
esquerda (marco a 18, pares a 18, método a 32), como a `064` fez com as atribuições. Um bloco coeso
por marco, como no Perfil. No Perfil agrupado, `_pares` com "Marcos classificatórios" e "os
descritos no item N.k.", com o espaço de sub-bloco. Requisitos: o mesmo molde — "N.k Requisitos
comuns aos Perfis …", os itens com o marcador, e "Requisitos: os descritos no item N.k." no Perfil.

**Frase do FR-1347**: *"Os marcos abaixo se aplicam a cada um desses Perfis separadamente, sobre as
inscrições do próprio Perfil: cada Perfil tem a sua própria classificação e o seu próprio
resultado."* Não fala em corte, porque nem todo marco tem corte, nem em recurso, que a frase do marco
já liga ao resultado.

**Rationale**: o recuo é hierarquia, e não regra; o texto é o mesmo, linha a linha (FR-1348), e o
teste de equivalência compara texto, não recuo.

## R-011 — O método comum, uma vez, no primeiro lugar em que sairia

**Decision**: o plano percorre os lugares em que marcos são impressos, na ordem do documento — os
Perfis não agrupados, depois as subseções comuns —, e o primeiro marco por sorteio governado pelo
método comum (`_origem_do_metodo` = "comum a este Edital") é o que imprime as sete linhas. Todo outro
imprime, sob "Sorteio", só "Método: o comum a este Edital, descrito no item N.k." e a "Habilitação",
que é dele. O método próprio continua no marco. A identidade dos marcos (R-002) é calculada sobre a
forma completa, antes dessa troca.

**Rationale**: FR-1349. No caso comum — todos os marcos iguais — o método já sai uma vez por estar
na subseção comum, e a remissão não aparece; ela existe para os marcos diferentes que seguem o mesmo
método.

## R-012 — A prova da equivalência

**Decision**: um teste reconstrói, para cada Perfil, as frases normativas que o documento de depois
lhe aplica — o bloco dele, a subseção a que ele remete (sem o título e sem a frase do FR-1347), a
linha dele na tabela de vagas (cada célula como "nome da lista (código): número"), a tabela de
modalidades do grupo dele, as frases que o nomeiam ou valem para todos — e compara com as do bloco do
Perfil no documento de antes, como multiconjunto de linhas normalizadas. Sobre a composição
(`Composicao.itens`) nos casos sintéticos; sobre o texto do PDF nos cenários A e B, cujo "antes" são
os bytes de `specs/067-…/demonstracao/` — a `main` de hoje. Um segundo teste, no molde do da `067`,
prende a diferença de texto do documento inteiro.

**Rationale**: SC-513 e o pedido — "prove a equivalência". O multiconjunto pega a frase perdida, a
duplicada e a de outro Perfil; a comparação por linha normalizada ignora só o que a feature muda de
propósito (recuo, posição, número da tabela).
