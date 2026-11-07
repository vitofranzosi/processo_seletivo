# Research: A organização da lista de Processos Seletivos

Nenhum ponto da Technical Context ficou em aberto. Cada decisão abaixo responde a uma pergunta que o
código atual levantou.

## R-1 — O grupo do Processo é uma anotação, e não um filtro por aba

**Decision**: `listar_processos` anota cada Processo com `grupo` — `0` em andamento, `1` encerrado, `2`
cancelado —, por `Case`/`When` sobre a situação dele e um `Exists` de Edital fora de Encerrado e
Cancelado. A aba filtra pelo grupo; "Todos" não filtra; a busca não filtra pelo grupo e **ordena** por
ele (FR-4308). A ordem dentro do grupo é `-created_at, -id`.

**Rationale**: uma regra só responde às três perguntas — que aba, que contagem, que ordem da busca —, e
a partição da FR-4302 sai por construção: cada Processo tem um grupo. O `Exists` não multiplica linhas
nem pede `distinct`.

**Alternatives considered**: três filtros independentes por aba (a partição passaria a depender de três
expressões coincidirem); ler os Processos e agrupar em Python (custo linear no acervo).

## R-2 — A busca: texto e "N/AAAA"

**Decision**: o termo é o parâmetro `busca`, sem os espaços das pontas e cortado em 100 caracteres, como
na Visão Geral. Casa o Processo quando:
- o título ou o código do Processo contém o termo (`icontains`);
- algum Edital dele tem o título que contém o termo;
- o termo é só dígitos e algum Edital tem aquele número, em qualquer ano.

O termo `N/AAAA` (dígitos, barra, quatro dígitos, com espaços em volta da barra tolerados) é
**identificador, e só**: casa o Processo que tem um Edital com aquele número **e** aquele ano, e não o
texto. Somado ao texto, "90/2026" traria também o Edital 190/2026, cujo título costuma ser "Edital
190/2026 — …" (achado da revisão independente, `verificacao.md`).

O número se compara **sem os zeros à esquerda** (`LTRIM(number, '0')`): "1/2026" acha "01/2026", e
pelo número "90" não acha "190" — mas "90" sozinho também se busca como texto, e acha o título que o
contém. As condições de Edital são `Exists`, e não junção.

**Rationale**: FR-4306 e D-004. A Visão Geral compara o número como texto (`icontains`), e "90" acharia
"190" e "900"; aqui o número é identificador. "90/" e "/2026" não casam o padrão e se buscam como texto
(Edge Cases).

**Alternatives considered**: `number__icontains` (impreciso); `unaccent` (pede extensão e migration —
Assumptions da spec).

## R-3 — Uma agregação conta as abas e a busca

**Decision**: `contar_por_situacao(consulta, busca)` faz **uma** consulta: `aggregate` com `Count` filtrado
por grupo para as três abas, e os mesmos três com o filtro da busca. Sem busca, o filtro da busca é
vazio e os seis números coincidem dois a dois.

**Rationale**: FR-4327 pede o mesmo número de consultas com e sem busca. Duas agregações distintas, uma
só quando há busca, fariam a busca custar uma consulta a mais.

## R-4 — A página sem `Paginator`

**Decision**: o total vem da agregação (R-3); a página se calcula em Python (`POR_PAGINA = 20`) e a
consulta é um recorte `[início:fim]`.
- Parâmetro ausente, não numérico, zero ou negativo: página 1.
- Além da última: a última.

**Rationale**: `Paginator.count` repetiria o `COUNT` que a agregação já fez. E `Paginator.get_page` leva
zero e negativo à **última** página (trata como `EmptyPage`), quando a FR-4315 manda à primeira.

## R-5 — Os Editais da unidade, lidos uma vez

**Decision**: a view lê `Edital.objects.filter(institution_scope=…).select_related("processo")`, na ordem
do Processo (`-processo__created_at, -processo_id`) e depois `year, number`. A lista inteira vai para
`trabalho.do_ator` (FR-4323), e as Retificações em curso são lidas para os mesmos ids. As linhas da
página recebem os Editais do seu Processo por `processo_id`, sem `prefetch_related`.

**Rationale**:
- A faixa lia os Editais que a página carregava; com a página recortada, ela passaria a esconder
  trabalho (D-006).
- A leitura que a faixa precisa já traz os Editais da página, e um segundo `prefetch` seria uma
  consulta a mais, que some quando a página vem vazia — o número de consultas mudaria com a aba
  (FR-4327).
- A ordem é a de hoje, e a ordenação estável da faixa (`_ordem`) desempata pela posição de entrada.

**Alternatives considered**: deixar a faixa ler por conta própria uma segunda vez (duas leituras dos
mesmos Editais).

## R-6 — Sai o que só a coluna usava

**Decision**: saem `acoes.contagens_da_lista`, `acoes.para_a_lista`, `acoes.CONFERIDOS_NO_DETALHE`,
`acoes.da_linha`, `acoes.FREQUENTES`, o parâmetro `contagens` de `acoes.do_edital`, `acoes._navegacao`
e `trabalho.do_ator`, o `com_relatorio` (só a lista o desligava), `_acao_de_linha.html`, e as regras
`.acoes>*+.terminais`, `.acao.zerada` e `.acao.principal-da-linha` de `telas/lista.css`.

**Rationale**: Princípio V. Código sem chamador é um caminho que ninguém testa pela tela, e a próxima
pessoa o reataria à lista sem saber que a variante V1 o tirou. `acoes.hierarquia`, que o detalhe usa,
fica.

## R-7 — A nota de cobertura: uma fonte, duas frases

**Decision**: `trabalho.FORA_DA_FAIXA` passa a ser só a frase das famílias de fora, e `trabalho.COBERTURA`
é "o que cobre" + `FORA_DA_FAIXA`. A faixa com itens mostra `COBERTURA` logo depois do título (FR-4324);
a frase vazia continua "Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você
agora." e acrescenta `FORA_DA_FAIXA` (FR-4325). `Faixa.cobertura` continua o atributo que o template lê.

**Rationale**: as duas frases nomeiam as mesmas famílias por construção. A primeira frase da vazia já
diz o que a faixa cobre, e repeti-la seria ruído.

## R-8 — O subtítulo pela Unidade

**Decision**: `unidades_selectors.unidade(ator.institution_scope)` dá o nome; sem registro, o código
continua, como hoje. Uma consulta, constante.

## R-9 — A marca da Retificação diz sempre quem ela aguarda

**Decision**: a marca passa a dizer "· aguarda {papel}" também quando o ato é da pessoa. Até a `104`, o
ato da pessoa ia para a coluna, e a marca omitia o "aguarda" para não repetir. Sem coluna, a marca sem
o "aguarda" deixaria de dizer o que a FR-4318 pede, e o ato continua na faixa.

## R-10 — O endereço

**Decision**: `?situacao=andamento|encerrados|cancelados|todos`, `?busca=`, `?pagina=`. O link da aba "Em
andamento" é o endereço sem parâmetro (FR-4316): é o mesmo da barra e da trilha. A busca descarta a aba;
os links de página levam a aba ou a busca, codificadas por `urlencode`. O formulário da busca é GET e
não leva a aba: uma nova busca volta à página 1 (FR-4314).

## R-11 — A paridade lista × detalhe, na forma nova (FR-4329)

**Decision**: `test_listagem_e_detalhe_nao_divergem` e `test_cancelar_aparece_na_listagem_para_quem_pode`
dão lugar a dois casos:
- a lista não apresenta ação de Edital para papel nenhum (nenhum `class="acao` em linha de Edital,
  nenhuma das frases da coluna);
- todo item da faixa de natureza `edital` tem o ato correspondente no detalhe do mesmo Edital, para a
  mesma pessoa (elaborar, homologar, publicar).

## R-12 — Os testes que mudam

| Teste | O que muda |
|---|---|
| `test_acoes.py::test_listagem_e_detalhe_nao_divergem`, `::test_cancelar_aparece_na_listagem_para_quem_pode` | substituídos (R-11) |
| `test_polish_da_057.py::test_a_lista_poe_as_frequentes_primeiro…`, `::test_o_contador_zero_esmaece…` | removidos (FR-1049 e FR-1050 substituídos) |
| `test_polish_da_055.py` (o que lê `_acao_de_linha.html`) | segue o partial removido |
| `test_lista.py::test_a_contagem_diz_o_que_ela_conta` | passa a afirmar que as abas contam Processos e que "Editais no total" sumiu |
| `test_lista.py::test_acoes_seguem_a_permissao…`, `::test_estrutura_acessivel_da_lista`, `::test_plural_de_edital…`, `::test_a_acao_indisponivel…` | reescritos sem tabela nem coluna |
| `test_acoes_disponiveis.py` casos D (`submeter`, `publicar` na linha) e `test_a_coluna_tem_o_ato…` | passam a afirmar a faixa e a ausência na linha |

A lista completa, com o que a suíte revelar, fica em `verificacao.md`.
