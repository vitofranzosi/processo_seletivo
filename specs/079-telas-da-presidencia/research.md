# Pesquisa — 079

## R-001 — A trilha das telas da presidência

**Decisão**: `comissao.html`, `comissao_confirmar.html`, `alocacoes.html` e `distribuicao.html`
sobrescrevem o bloco `caminho_do_contexto` que a `077` criou, com a mesma `nav aria-label="Trilha de
navegação" class="caminho-da-secao"`, o produto pelo parcial `_produto_na_trilha.html` (`078`), e a
tiram do `main`. Os níveis são os que cada tela já mostrava:

| Tela | Trilha |
|---|---|
| Comissão | GPS › [Processos Seletivos] › [código] › Comissão |
| Conferência da inclusão | GPS › [Processos Seletivos] › [código] › [Comissão] › Conferir |
| Alocação por Etapa | GPS › [Processos Seletivos] › [código] › Alocação por Etapa |
| Distribuição | GPS › [Processos Seletivos] › [código] › [Alocação por Etapa] › nome da Etapa |

**Por quê**: é o desenho da `077` e da `078`, e a Distribuição fica igual à Etapa aberta pela gestão,
que tem essa mesma trilha no cabeçalho desde a `077` (`FR-1752`). As quatro telas moram sob
`/gestao/processos/` e `/gestao/editais/`, e a seção delas, pelo endereço, já é Processos Seletivos:
a barra e o começo da trilha concordam sem declaração nenhuma da view.

**A Alocação.** A barra dela fica no topo em qualquer largura pela rota (`TELAS_LARGAS`, DP-4 da
`076`), e o cabeçalho de contexto já estava acima da matriz, fora da moldura: a trilha troca o texto
dele e não lhe dá largura nem a tira da matriz. O guardião da `076`
(`test_na_alocacao_a_barra_fica_no_topo`) continua dizendo o que diz.

**Nenhuma consulta a mais.** As quatro views já entregam o Processo e, na Distribuição, a Etapa —
são os mesmos objetos que a trilha do conteúdo lia.

**Alternativas**:
- *O Edital na trilha da Distribuição* (Processo › Edital › Etapa) — seria um nível que a tela não
  mostrava e que divergiria da Etapa aberta pela gestão; o Edital continua na linha abaixo do título.
- *Levar as filhas da Distribuição junto* (Impedimentos, ocorrência, Resultados, Trilha, conclusões,
  retirada) — o pedido nomeia quatro telas, e cada incremento muda só o que o inventário refeito
  pode provar; ficam para outro.

## R-002 — A faixa dos lugares da Etapa, na Distribuição

**Decisão**: o `p.acoes-do-painel` com Impedimentos, Registrar ocorrência, Resultados e Trilha sai do
meio da página — depois de "Quem está alocado" — e vai para logo depois do título, do erro e do
resultado do último envio, antes da ficha. Os quatro links, o desenho `a.acao`, a ordem e o
comentário que explica o "Registrar ocorrência" vão juntos.

**Por quê**: nas três outras telas da presidência e no Processo, os lugares de onde se sai ficam
logo abaixo do título: a Comissão leva à Alocação, a Alocação à Comissão, o Processo à Supervisão,
Comissão e Alocação. Na Distribuição a faixa estava depois da tabela de carga, que tem uma linha por
pessoa alocada. Medido antes, no inventário, com duas pessoas: y ≈ 644 a 1280 px, y ≈ 998 a 375 px.

**As mensagens do último envio antes dela.** É a ordem da Comissão e da Alocação, as telas vizinhas:
título, linha do Edital, o que acabou de acontecer, e então a faixa. O resultado do lote é a resposta
ao clique que trouxe a pessoa de volta; separá-lo do título pela faixa seria pô-lo onde ela não olha
primeiro.

**O que não sai do lugar.** Os avisos de bloqueio e de inscrições em curso, o desfecho da
consolidação, "Consolidar as prontas" com a frase que o precede, o rodízio, os botões da tabela e
"Retirar as selecionadas" ficam onde estão (`FR-1786`). Cada um está ao lado do número ou da frase a
que se refere — o que a `030` decidiu para a consolidação (`FR-422`) e a `013` para o alcance das
prontas —, e mover qualquer um deles mudaria a leitura de um ato que não se desfaz. A orientação de
reabrir pelas conclusões preservadas também fica, logo depois de "Quem está alocado": é prosa sobre
as avaliações concluídas, e não lugar.

**O link "Registrar ocorrência" não é o ato.** Ele leva à tela do registro, que tem conteúdo e
confirmação próprios (a decisão 1 da `012`). O peso dele continua o de `a.acao`, igual aos outros três.

**Bytes.** A faixa só muda de lugar; a trilha sai do `main` e entra no cabeçalho, com o produto no
lugar de "Processos Seletivos" sozinho. O teto é medido antes e depois no cenário de escala.

**Alternativas**:
- *A faixa entre a ficha e os números* — ainda abaixo de dois blocos que crescem com a Etapa.
- *Os lugares como abas da Etapa* — seria componente novo, e "Trilha" e "Resultados" não são vistas
  da mesma tabela, são telas.

## R-003 — A Comissão: título para os membros e estado vazio

**Decisão**: o filtro, a linha do recorte e a lista de membros entram numa
`section aria-labelledby="membros-titulo"` com `h2` "Membros (N)", em que N é `total_de_membros` — a
comissão inteira. A `ul` mantém o `aria-label` "Membros da comissão". Com `total_de_membros` zero, o
filtro não vem, e o `p.vazio` diz "Esta comissão ainda não tem membros." com o link "Adicionar membro"
para `#adicionar-titulo`, o título da seção de inclusão, na mesma página. Com membros e um recorte
vazio, o filtro continua e o estado vazio é o de hoje.

**Por quê**: a página tinha título para as duas seções de inclusão e nenhum para o conteúdo
principal; quem navega por títulos pulava dos membros. "Membros (N)" segue os "Editais (3)" do
Processo (`078`). O total, e não o recorte, porque o recorte tem a linha própria ("1 de 3
membros."): um título que muda com o filtro diria duas coisas com o mesmo rótulo. Sem membro, o filtro
procura em nada e anuncia "(0 de 0)" antes de dizer que não há ninguém — a mesma razão da faixa vazia
que a `078` tirou do Processo (`FR-1776`).

**O aviso da presidência.** Continua antes da seção: é a situação da comissão, e não um membro.

**Classes.** Nenhuma nova: `vazio` tem regra na folha comum, e `section` e `h2` não precisam de
classe.

**Alternativas**:
- *As seções de inclusão antes da lista* — a leitura corrente é "quem está aqui e onde atua"; numa
  comissão constituída, incluir é exceção.
- *"Filtrar" com o desenho secundário, para deixar "Continuar" como a única ação cheia* — a `055`
  decidiu o contrário, por medição de auditoria, e um teste o guarda (`FR-1008` da `055`,
  `test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha`). Reabrir é governança, e não escopo.

## R-004 — "Salvar alocação"

**Decisão**: o botão depois da matriz passa de "Salvar distribuição" a "Salvar alocação". Nada mais
muda nele: lugar, classe, condição (`matriz.linhas and tem_presidente`).

**Por quê**: o template da Alocação registra a decisão de chamar a tela de Alocação, e não de
Distribuição, porque a Distribuição é a tela vizinha e as duas se confundiam ("uma palavra por
conceito"). A mensagem que o botão produz já diz "Alocação salva.". A arquitetura do manual registrou
a divergência como rótulo atual (C-13, "embora o ato seja alocar"), e é atualizada.

**O que fica, e por quê.** O aviso "Designe a presidência antes de distribuir." tem a mesma
divergência, mas é guardado por teste como frase (`test_alocacoes.py`) e não é a ação principal:
fica registrado como achado. O link "Distribuir" de cada coluna está certo — leva à Distribuição.

## R-005 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_telas_de_uso_diario.py::trilha_unica_no_cabecalho` | reusado, sem mudança |
| `test_telas_de_quem_elabora.py::test_o_produto_da_trilha_tem_uma_fonte_so` | continua igual — as quatro telas incluem o parcial |
| `test_shell_da_gestao.py::test_na_alocacao_a_barra_fica_no_topo` | continua igual |
| `test_jornada_da_presidente.py` (filtros da comissão) | continua igual — corta a página em "Membros da comissão" e "Adicionar membro", que continuam, nessa ordem, com a lista entre eles |
| `test_alocacoes.py` | continua igual — sem presidência, nenhum "Salvar distribuição" |
| `test_polish_da_055.py::test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha` | continua igual — "Filtrar" não muda |
| `test_distribuicao.py` (a frase antes de "Consolidar as selecionadas") | continua igual |
| `performance/test_escala_da_mesa.py` (120 000 caracteres, no máximo seis formulários) | medido antes e depois; a faixa não tem formulário |
| `test_acessibilidade_da_012.py::test_as_telas_tem_titulo_e_trilha_de_navegacao` | continua igual — a trilha está na página, no cabeçalho |

Testes novos em `tests/interface/test_telas_da_presidencia.py`.

## Achados registrados, fora do escopo

- **Na Distribuição, as duas ações sobre a seleção têm o mesmo peso, e uma não se desfaz.**
  "Distribuir as selecionadas" e "Consolidar as selecionadas" são dois botões cheios lado a lado,
  sobre a mesma seleção; o segundo transforma avaliações em Resultado da Etapa, que é imutável. A
  frase antes deles diz isso (`FR-422` da `030`), e o pedido proibiu mudar peso de ação irreversível
  sem a spec dizer por quê: esta não muda. Fica para quem decide o desenho das ações irreversíveis.
- **O aviso da Alocação ainda diz "distribuir".** "Designe a presidência antes de distribuir." tem a
  mesma divergência que o botão tinha (R-004), mas é guardado como frase por
  `test_alocacoes.py::test_comissao_sem_presidente_nao_deixa_distribuir`, e não é a ação principal.
- **As filhas da Distribuição continuam com a trilha no conteúdo.** Impedimentos, Registrar
  ocorrência, Resultados, Trilha, as conclusões preservadas e a retirada de atribuições
  (`distribuicao_remover_confirmar.html`) são o próximo grupo natural; a auditoria da comissão
  também.
- **O `comparar.py` do inventário não compara altura.** Ele acusa `status` e estouro, e a `078`
  conferiu largura e altura à mão. Esta feature escreveu a conta (`medidas.py`, na pasta do
  inventário), e não mudou o `comparar.py`, que outras features citam com a saída de hoje.
