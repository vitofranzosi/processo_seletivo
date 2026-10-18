# Research — 081

## R-001 — "Consolidar as selecionadas" com o desenho dos atos do Processo

**Decisão**: o botão passa de `botao` a `botao secundario`, e ganha logo depois a marca
`<span class="marca-irreversivel">irreversível</span>`. Rótulo, `formaction`, `name`, `value` e lugar
não mudam. "Distribuir as selecionadas" continua `botao`.

**Por quê**: no detalhe do Processo, os atos que não se desfazem são `botao secundario` (ou
`botao perigoso`, quando interrompem) com a mesma marca ao lado (`processo_detalhe.html`), e levam a
uma conferência antes do ato — como os dois "Consolidar" da Distribuição, que sem `confirmar=1` só
mostram a conferência de dois passos. É o mesmo caso, e o desenho já existe. O secundário tem a
altura do principal (`.botao`), e a linha continua de uma família só (`UX-135` da `055`).

**Alternativas descartadas**:
- *`acao perigoso`, como "Retirar as selecionadas"* — o vermelho da casa é de retirar e de
  interromper; consolidar não apaga nada, produz um ato. E `.acao` fora das três barras da `055` é
  menor que `.botao`, o que punha na mesma linha dois botões de alturas diferentes.
- *`botao perigoso`* — continuaria cheio, e a pesquisa da `079` apontou justamente os dois cheios lado
  a lado.
- *Separar os dois botões em formulários* — a seleção é a mesma, e o comentário do template registra
  por que o `formaction` existe: duplicar as caixas obrigaria a marcar duas vezes.
- *Deixar "Consolidar as N prontas" cheio* — foi a primeira versão, por estar sozinho no formulário
  dele; a revisão do PR mostrou o mesmo ato com dois desenhos na mesma página, e ele passou ao mesmo
  desenho (R-007; D-006 da spec, emendada).

## R-002 — A marca não estica em linha flexível

**Decisão**: `align-self:center` na própria regra de `.marca-irreversivel`, na folha comum.

**Por quê**: `.acoes` é flexível, e um item flexível estica até a altura da linha por padrão — a
marca, que tem fundo, viraria uma faixa da altura do botão. A primeira versão escreveu
`.acoes .marca-irreversivel{align-self:center}`; a revisão do PR apontou que a causa é a marca ser
item de **qualquer** linha flexível (`.acoes-do-painel`, `.salvar`, `.linha-de-acoes` também são), e
a próxima tela pediria outro seletor. Fora de flex e de grid, `align-self` não faz nada; na
`.lista-acoes` do detalhe do Processo, cujo `li` já centraliza, também não muda nada (o inventário
confere).

## R-003 — "antes de alocar"

**Decisão**: o aviso da Alocação sem presidência passa a dizer "Designe a presidência antes de
alocar.". O `role="status"`, o `strong`, o link para a Comissão e a condição não mudam.

**Por quê**: é a divergência que o R-004 da `079` corrigiu no botão ("Salvar alocação") e deixou no
aviso porque um teste o guardava como frase. O teste muda junto (R-006). A recusa do domínio, que diz
"distribuir trabalho", fica (D-007 da spec).

## R-004 — A montagem do `cenario` vai para o apoio comum, e a fixture fica em cada módulo

**Decisão**: o corpo da fixture `cenario` de `test_acessibilidade_da_012.py` passa a ser a função
`montar_cenario_da_presidencia`, em `tests/fixtures/mesa.py`, composta sobre `montar_banca`, que já
publicava, constituía com presidência e alocava — ganhou só `com_documentos`. O código do Processo e
as chaves de idempotência vêm do `seed`, como na banca (revisão do PR: com eles fixos, dois cenários
no mesmo teste reproduziam um ao outro). O módulo da `012` e os três que importavam a fixture — os da `077`, da `079` e da `080` —
declaram cada um a sua `cenario`, de duas linhas, que chama a função; saem o import, o `noqa: F401` e
os `noqa: F811`. Um guardião lê, pela árvore sintática, todo módulo de teste da interface e falha se
algum voltar a importar o `cenario` do módulo da `012`.

**Por quê**: é a regra que a suíte já escreveu em `tests/fixtures/corte.py` — "funções ficam aqui, e
a fixture fica no `conftest.py`" —, e que o conftest da interface repete: importar fixture de um
módulo de teste a redefine no importador, e o mesmo estado ganha dois donos.

**Alternativas descartadas**:
- *A fixture no conftest da interface* — o nome está tomado: o conftest já declara um `cenario`, o da
  ocupação (`016`), e 26 módulos da interface declaram o seu próprio, contando os cinco que usam o
  da presidência. Um segundo `cenario` no conftest seria impossível; um nome novo pediria editar o
  corpo de cada teste que o usa.
- *Um nome novo para a fixture, num conftest* — idem: dezenas de linhas de teste mudariam só de nome.

**Fora do escopo, registrado**: o mesmo padrão existe em outros módulos — `test_polish_da_058.py`
importa um `cenario` diferente, o de `test_exportacao_de_matriculas.py`, e há mais nove importações de
fixture de módulo de teste marcadas com `noqa: F401` na suíte (o `sorteado` de `test_manifesto.py` em
quatro módulos, `composto`, `cliente_no_corte`, `ato` e `sem_publicacao`, `pronto` e a fixture de
`test_suplencia.py`), contadas em 17/10/2026. O guardião desta feature só
olha o `cenario` da `012`; o de `test_exportacao_de_matriculas.py` fica como está. Os auxiliares que
não são fixture — `barra`, `itens_da_barra`, `trilha_unica_no_cabecalho` — continuam importados de
módulo de teste, que é o padrão da casa (165 importações assim em `tests/`) e não sombreia nada.

## R-005 — O guardião da abertura da trilha

**Decisão**: um teste lê todo template que sobrescreve `caminho_do_contexto` e exige que o bloco
abra com `<nav aria-label="Trilha de navegação" class="caminho-da-secao">` seguido do parcial do
produto.

**Por quê**: `trilha_unica_no_cabecalho` confere essa abertura, mas só nas telas que os testes de tela
abrem; o guardião da `078` confere o parcial em todos os templates, mas não a `nav` em volta. O
achado da revisão da `077` era esquecer uma tela ao trocar o rótulo ou a classe — com o guardião, o
esquecimento reprova a suíte. Extrair a abertura foi descartado (D-003 da spec). Depois da revisão,
um bloco sem `nav` — o cabeçalho da `076` refeito, ou só o `block.super` — não reprova: não é trilha;
e a leitura se confere pela presença da lista da `077`, e não por um total que muda.

## R-006 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_telas_da_presidencia.py::test_nenhuma_acao_da_distribuicao_sai_do_lugar` (a contagem de `class="botao"` no template) | a contagem de `class="botao"` passa de 6 para 4, porque as duas consolidações deixaram de ser `botao` puro — é o achado; o comentário, que dizia "as cheias continuam cheias", passa a dizer o que mudou |
| `test_alocacoes.py::test_comissao_sem_presidente_nao_deixa_distribuir` | a frase passa a "antes de alocar" — é o achado |
| `test_telas_da_presidencia.py::test_sem_presidencia_a_alocacao_continua_sem_botao` | idem |
| `test_distribuicao.py` (a frase antes de "Consolidar as selecionadas") | continua igual |
| `test_prontidao_na_tela.py` | continua igual — procura o rótulo, que não muda |
| `test_telas_de_uso_diario.py`, `test_telas_da_presidencia.py`, `test_telas_filhas_da_distribuicao.py`, `test_acessibilidade_da_012.py` | sem o import e sem os `noqa` do `cenario`; corpos iguais |
| `performance/test_escala_da_mesa.py` (120 000 caracteres) | medido antes e depois |

Testes novos em `tests/interface/test_achados_das_revisoes.py`.

## R-007 — A revisão do PR (18/10)

A revisão do PR 298 apontou nove achados, e o usuário pediu a correção de todos:

| Achado | Correção |
|---|---|
| A marca não chega ao leitor de tela | `aria-describedby` do botão para a marca, com `id` (`FR-1827`) |
| "Consolidar as N prontas" cheio e sem marca, na mesma página | o mesmo desenho e a mesma marca (`FR-1828`; D-006, emendada) |
| `seed` não isolava o cenário | código e chaves derivados do `seed` (R-004) |
| O guardião da fixture só olhava o módulo da `012` | lê todos os módulos que declaram o `cenario` da presidência, pela árvore sintática |
| A montagem repetia `montar_banca` | composta sobre ela (R-004) |
| A regra da marca presa a `.acoes` | na própria marca (R-002) |
| Comentário do teste da `079` contradito pela linha seguinte | reescrito (R-006) |
| Testes casando indentação e CSS literal | o aviso por partes; a regra da marca por expressão, tolerante a espaço |
| Guardião da trilha rígido demais | bloco sem `nav` não reprova; sem número mágico (R-005) |

Os dois guardiões novos foram provados por mutação: com a classe da trilha trocada na lista, e com o
`cenario` importado de `test_telas_da_presidencia.py`, cada um reprova.

## Achados registrados, fora do escopo

- **A conferência da consolidação ainda tem a trilha no conteúdo.** "Processos Seletivos › Prova
  objetiva › Conferir", sem o Processo nem a Alocação, e o cabeçalho com o da `076` — como as filhas da
  Distribuição antes da `080`. É a resposta a um envio, e por isso não está no inventário; a `080` não
  a listou entre as filhas. Visto no percurso desta feature, em 17/10/2026.
- **Outras fixtures importadas de módulo de teste.** Ver o R-004: o mesmo padrão, com `noqa`, em dez
  importações da suíte; o guardião desta feature só cobre o `cenario` da presidência.
