# Research: Cadastro de reserva sem vaga imediata impresso como CR

**Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Date**: 2026-10-21

As decisões de produto (D-001 a D-004) estão na spec. Aqui ficam as técnicas, D-005 a D-011, e o
mapa do código que a pesquisa levantou. Nenhuma questão ficou aberta.

## Onde o `0` sai hoje

O documento tem dois eixos independentes desde a `069`: a **redação** (`redacao_do_documento`, 1 ou 2,
o vocabulário) e a **apresentação** (`catalogo.apresentacao_de`, plana ou por perguntas, a
organização). O `0` depende da apresentação, e não da redação.

| Apresentação | Onde | Função | O que imprime hoje |
|---|---|---|---|
| plana, 2 ou mais Perfis | tabela "Perfis de vaga", coluna "Vagas" | `pdf._quadro_de_perfis` | `str(immediateVacancies)` |
| plana, 1 Perfil | par "Vagas imediatas" da ficha | `pdf._perfil_unico` | `str(immediateVacancies)` |
| plana | tabela de vagas por lista (forma longa) | `pdf._tabela_de_vagas` | só os Perfis com vaga desde a `067` (`_com_vaga_no_quadro`): **não muda** |
| por perguntas, todos com vaga | matriz Perfil × lista | `apresentacao._matriz_de_vagas` | só entra quando todos têm vaga: **não muda** |
| por perguntas, algum sem vaga | tabela "Perfis" dos avulsos | `apresentacao._vagas_em_partes` | `str(_total(perfil))` |
| por perguntas, algum sem vaga | uma tabela por grupo de mesmo nome | `apresentacao._vagas_em_partes` | `str(_total(perfil))` |
| por perguntas | tabela por lista, só dos com vaga | `apresentacao._vagas_em_partes` | **não muda** |
| por perguntas | resumo do começo | `apresentacao` (linha "Vagas") | já diz "não há vaga imediata; há cadastro de reserva": **não muda** |

São **quatro** pontos de escrita: dois em `pdf.py` e dois em `apresentacao.py`. O portal tem **um**:
o `<span class="reserva">` de `portal/selecao.html` que diz "N vagas imediatas agora" quando há
`perfil.oferta`. Os cartões (`leitura.quantidade_da_oferta`) já dizem "cadastro reserva" sem número e
não mudam.

## D-005 — Um predicado de domínio, ao lado do da `067`

`cadastro_sem_vaga_imediata(perfil)` vai para `editais/domain/quadro.py`, junto de
`sem_vaga_imediata`. É verdadeiro quando o total é o inteiro `0` (e não `bool`), nenhuma linha do
quadro declarado tem quantidade positiva e o `reserveType` é `LIMITED` ou `UNLIMITED`.

**Por que não reusar `sem_vaga_imediata`:** ele responde outra pergunta, se o quadro e a reversão
saem, e por isso responde **não** quando não há quadro declarado. O acervo anterior à `025` não tem
quadro, e o consolidado de uma Retificação dele, composto depois desta feature, imprimiria `0` num
Perfil de cadastro. Os dois predicados concordam sobre o Perfil incoerente: total `0` com linha
positiva não é "sem vaga" em nenhum dos dois (o caso-limite da spec).

**Descartada:** decidir no compositor, com `immediateVacancies == 0 and reserveType != "NONE"`.
Seriam quatro cópias da mesma regra, que é o que a `FR-2402` proíbe.

## D-006 — Uma função de célula, que as quatro composições chamam

`vagas_impressas(perfil) -> str`, em `pdf.py`, devolve `SIGLA_DO_CADASTRO` (`"CR"`) quando o predicado
é verdadeiro, e o número como texto nos outros casos. `pdf._quadro_de_perfis`, `pdf._perfil_unico` e
os dois pontos de `apresentacao._vagas_em_partes` passam a chamá-la. `apresentacao` já importa
`pdf` como `composicao_pdf` e usa dele `_reserva` e `frase_do_cadastro`, que são do mesmo assunto.

`_total_de_vagas` (a linha de total) e `apresentacao._total` não mudam: somam o número guardado, e o
`CR` vale `0` (`FR-2407`). A decisão de qual tabela sai (`com_vaga`, `_matriz_de_vagas` contra
`_vagas_em_partes`) também não muda: ela é pelo número.

## D-007 — A nota como parâmetro da tabela, colada à última linha

`_tabela` ganha `nota=None`, que escreve a linha **depois** da grade, em `CORPO_TABELA`, alinhada ao
recuo da tabela, com `antes=ANTES_DE_LINHA` e `junto=True`. O `junto` é o que a paginação já usa para
a legenda, e impede a nota de começar a página seguinte sozinha, longe da tabela que explica. Cada
ponto de escrita passa `nota=nota_da_sigla(perfis)`, que devolve `NOTA_DO_CADASTRO`
(`"CR: cadastro de reserva."`) quando algum dos Perfis da tabela é `CR`, e `None` nos outros casos.
Na ficha do Perfil único, a mesma linha sai depois de `_pares`, dentro do mesmo bloco.

**Descartadas:** `CORPO_NOTA` (7,5 pt), que é o corpo do rodapé técnico e do resumo criptográfico e
ficaria ilegível como nota do ato; a nota na legenda, que fica acima da tabela, antes de o leitor
ver a sigla; e a nota como mais uma linha da grade, que entraria na medida das colunas e alargaria a
de vagas.

## D-008 — A nota não é item do documento

A conferência de remissões da `065` (`tabelas_do_documento`) e os itens da `054` contam o que tem
número ou endereço. A nota não tem nenhum dos dois: é escrita por `composicao.escrever`, como a
legenda, e não abre tabela. Não há nada a mudar ali, e o guardião existente
(`test_os_itens_sao_os_que_a_composicao_escreve`) confirma isso compondo o documento de verdade.

## D-009 — Os bytes esperados passam a ser os da `096`

Os três PDFs do cenário B gravados pela `069` (`B-plana-069.pdf`, `B-publicado-069.pdf`,
`B-variante-069.pdf`) mudam de propósito. Seguindo o que a `068` e a `069` fizeram:

- os bytes esperados de `test_itens_do_documento.py` e de `test_documento_da_auditoria_depois_da_069.py`
  passam a ser os de `specs/096-…/demonstracao/`;
- os da `069` ficam onde estão, como evidência dela;
- um guardião novo, `test_documento_da_auditoria_depois_da_096.py`, compara o texto corrido dos PDFs
  da `069` com o dos da `096` e exige que a **única** diferença seja: cada `0` dos dezesseis Perfis de
  tutor presencial virou `CR`, e saiu uma nota por tabela com `CR`. É o `SC-900` provado, e a
  garantia de que nada mais mudou.

O cenário A e a fixture de contrato (`documento_publicado_v1.pdf`, um Perfil com 3 vagas e cadastro
limitado) **não** podem mudar de byte nenhum. É o `SC-901`, e a fixture continua intocada. Se o A
mudar, a implementação está errada.

## D-010 — No portal, tirar a linha, e não a oferta

Sai só o `<span class="reserva">…vagas imediatas agora</span>` do ramo `perfil.oferta` de
`portal/selecao.html`, com o comentário do bloco atualizado. `_oferta` e `perfil.vagas` ficam: o ramo
com vaga continua a usar o número. O teste de `FR-136` em
`tests/integration/portal/test_detalhe_selecao.py` prende hoje *"0 vagas imediatas agora"*. Ele muda
no mesmo commit para prender a ausência de "0 vaga" e de `CR`, citando a `FR-2414`. O teste deixa de
afirmar a parte da `FR-136` que esta feature revisa, e continua afirmando o resto dela.

## D-011 — O que fica igual, de propósito

- **A gestão.** `_perfil.html`, a Revisão (`interface/revisao.py`) e a visão institucional continuam
  lendo o número. A prévia do documento passa pelo mesmo compositor, e diz `CR` sem mudança própria.
- **O quadro de alterações** (`publicacoes/domain/alteracoes.py`) registra o valor do campo (D-003).
- **O conteúdo canônico e o assistente.** O snapshot continua com `immediateVacancies: 0`. O corpus da
  `070` (`tests/fixtures/corpus_070/`) é conteúdo canônico, e não documento composto, e não muda.
- **As células de lista do quadro** de um Perfil com vaga. Uma lista declarada em `0` num Perfil com
  6 vagas continua `0` (o cenário 2 da história 4 da `067`). A regra é sobre o Perfil, e não sobre a
  linha.
