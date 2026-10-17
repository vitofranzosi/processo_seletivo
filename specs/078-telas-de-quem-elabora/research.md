# Pesquisa — 078

## R-001 — As causas latentes, medidas antes de corrigir

**Como se mediu.** Uma sonda derivada do `capturar.py` do inventário abriu as 84 variantes que
carregam, no `ps_inventario_telas`, com a `main` em `a41b67c0` (a `077` já aplicada), a 1280 e a
375 px. Em cada página ela anotou a caixa de todo elemento, injetou uma regra, anotou de novo e
comparou; e listou as molduras que rolam na horizontal (`overflow-x` `auto` ou `scroll`) sem posição
e com algum elemento `position:absolute` dentro. As duas regras medidas:

- *molduras*: `.tabela-rolavel,.rolagem,.distribuicao-moldura,.rolavel-no-estreito,.rolagem-da-tabela,.serie .barras{position:relative}`
- *grupos de campos*: `fieldset{min-width:0}`

**Resultado.**

| | Variantes com a estrutura | Caixas que a regra move | Largura ou altura que muda |
|---|---|---|---|
| Moldura sem posição com absoluto dentro | 19 (18 a 1280; a Visão Geral só a 375, onde a moldura dela rola) | 0 | 0 |
| `fieldset` | 14 | 0 | 0 |

As 19: `visao-geral` (375), `reaproveitar`, `distribuicao`, `resultados-da-etapa`, `ordenacao`,
`corte-historico`, `ato-de-ordenacao`, `corte`, `sorteio`, `previa-de-publicacao`,
`publicacoes-do-marco`, `recursos`, `minha-etapa`, `modelos-de-aviso`, `avisos-do-edital-antes`,
`aviso-do-resultado`, `aviso`, `aviso-reenviar` e `avisos-do-edital`. Os 14 com `fieldset`: as sete
etapas da composição que têm grupo de campos (`perfis`, `cronograma`, `etapas`, `classificacao`,
`inscricao`, `anexos`, `conteudo`), `reaproveitar`, `retificar`, `distribuicao`, `duvidas`,
`ato-publicar`, `retificacao-ato-publicar` e `identificar-demonstracao`.

**Por que a regra das molduras não move caixa nenhuma.** O rótulo oculto é absoluto sem `top` nem
`left`: fica na posição estática, dentro da célula, com moldura posicionada ou não. O que muda é a
quem ele conta como transbordo — sem posição na moldura, à página; com posição, à moldura. Por isso
nenhuma caixa se move e nenhuma largura muda enquanto nenhum rótulo cair além da borda — e por isso a
causa é latente: com a moldura sem posição, o estouro aparece no dia em que uma tabela ganhar uma
coluna ou um nome mais longo, numa tela que nenhum inventário mediu com aqueles dados.

**Por que a de `fieldset` não move.** Nos 14, o conteúdo de cada grupo já cabe na largura
disponível; as duas telas em que não cabia (`reaproveitar` e `compor-anexos`) tinham a regra pontual
da `077`. Sem ela, o inventário refeito é o que prova que a regra geral as cobre (`FR-1762`).

## R-002 — A regra geral, e onde ela mora

**Decisão**: na folha do `base.html`, ao lado de `.tabela-rolavel{overflow-x:auto}`, uma regra
`position:relative` para as molduras que rolam; e `min-width:0` na regra de `fieldset` que já
existe. As regras pontuais da `077` em `conclusoes.html`, `reaproveitar.html` e `compor_anexos.html`
saem — e com elas o bloco de estilo de `reaproveitar.html`, que só tinha a regra.

**Por quê**: é a causa, e a causa é da folha. A `077` não pôs a regra geral porque ela mudaria telas
que não tocava, contra a `FR-1745` dela; a medição do R-001 mostra que não muda — nenhuma caixa em
nenhuma variante —, e é isso que permite subir a regra agora. As molduras são listadas pelo nome,
porque o CSS não seleciona por estilo computado; a lista é a de todo `overflow-x:auto` da gestão
(`grep` na pasta de templates): as cinco classes da folha comum e a `.rolagem-da-tabela`, que a Visão
Geral declara na folha dela.

**A ordem do seletor importa.** `test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem`
procura a primeira regra `.distribuicao-moldura{` fora de `@media` e exige `overflow-x:visible`
nela. Com `.distribuicao-moldura` logo antes da chave, a regra nova seria a encontrada, e o guardião
reprovaria por um motivo que não é o dele. Ela vem no meio do seletor.

**O cabeçalho fixo da distribuição.** `position:sticky` se prende ao ancestral que rola, e
`position:relative` não faz a moldura rolar. A moldura continua `overflow-x:visible` na tela larga.

**Bytes.** A folha comum vai em toda página, inclusive na distribuição, que tem teto de 120 000
bytes. As duas mudanças somam pouco mais de cem bytes renderizados; o comentário vai em
`{% comment %}`, que não sai na página.

**Alternativas**:
- *Manter as regras pontuais e acrescentar a geral* — duas fontes para a mesma decisão, e a pontual
  não diria mais nada.
- *`contain:paint` ou `overflow:clip` na moldura* — mudariam a rolagem ou recortariam o foco de quem
  navega pelo teclado; `position:relative` não tem efeito visível.
- *`display:block` nas tabelas* — alguns leitores de tela deixam de anunciá-las como tabela (R-002 da
  `077`).

## R-003 — A ação que o fluxo pede: posição, e não segundo botão

**Decisão**: no detalhe do Processo, a `div.colunas` com "O que fazer agora" e os Editais sobe para
antes de "Onde cada Edital está", com "O que fazer agora" em primeiro. No detalhe do Edital, as duas
`section` da `div.colunas.ao-topo` trocam de lugar. Nada muda dentro de nenhuma região.

**Por quê**: o cartão já é o lugar da ação que o fluxo pede, desenhado pela `057` e pela `058` — a
principal cheia, as terminais por último, a passagem de bastão e o motivo da indisponibilidade ao
lado. Subir o cartão inteiro leva tudo isso junto. No Processo do inventário, a ação estava em
y ≈ 1700 a 1280 px; com a mudança, logo abaixo da situação.

**"Onde cada Edital está" depois dos Editais.** A região resume a Supervisão e leva a ela; a lista
dos Editais é o conteúdo próprio do Processo. Nenhum requisito fixa a ordem: a `FR-556` da `038`
pede que a página apresente o pulso e a Atenção, e continua apresentando.

**Alternativas**:
- *A ação principal ao lado do título, num cabeçalho de página* — separaria a ação do motivo de ela
  estar indisponível (`FR-1045` da `057`) e da passagem de bastão, e a repetiria fora do cartão,
  que é a duplicação que a `077` acabou de tirar da lista.
- *Recolher "Onde cada Edital está" num `details`* — esconde o que a `038` quis à vista.
- *Só no celular, por `order`* — a ordem visual divergiria da ordem de leitura e de tabulação.

## R-004 — A trilha das telas de quem elabora

**Decisão**: `processo_detalhe.html`, `detalhe.html` e `compor_base.html` sobrescrevem o bloco
`caminho_do_contexto` que a `077` criou (R-001 da `077`), com a mesma `nav aria-label="Trilha de
navegação" class="caminho-da-secao"`, e a tiram do `main`. As nove etapas da composição herdam a de
`compor_base.html`.

| Tela | Trilha |
|---|---|
| Processo | GPS › [Processos Seletivos] › código |
| Edital | GPS › [Processos Seletivos] › [código] › Edital n/a |
| Composição | GPS › [Processos Seletivos] › [código] › [Edital n/a] › Compor |

**O Processo entra na trilha da composição.** Ela pulava do Processos Seletivos para o Edital,
enquanto a do detalhe do Edital passa pelo Processo; a pessoa que sobe da composição para o
Processo precisava de dois cliques. O `obter_edital` já traz o Processo junto (`select_related`):
nenhuma consulta a mais.

**"Compor" continua sendo a página atual.** O passo é dito pela navegação das etapas, com
`aria-current="step"`; repeti-lo na trilha seria dizer duas vezes onde se está — o que esta
sequência de features vem tirando.

## R-005 — Os Editais do Processo em tabela

**Decisão**: a `ul.resumo-lista` vira a tabela da lista de Processos — `Edital`, `Título`,
`Situação` —, com o número em `th scope="row"` e `a.codigo`, o título como link, a pastilha na
terceira coluna, dentro de `div.tabela-rolavel`. Sem Edital, `p.vazio` com a frase da lista:
"Nenhum Edital neste Processo.". A tabela leva `aria-labelledby` para o título do cartão, que já diz
quantos são.

**Por quê**: é a mesma informação que a lista mostra, e a lista a mostra em colunas desde a `058`.
A quarta coluna da lista, "O que posso fazer", não entra: as ações do Edital estão no Edital, um
clique adiante, e no cartão ao lado; trazê-las seria escopo novo.

**Classes.** Nenhuma classe nova: `tabela-rolavel`, `codigo`, `situacao`, `vazio` têm regra na
folha comum (memória "classe no template exige regra na folha").

## R-006 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_shell_da_gestao.py::test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha` | usava o detalhe do Edital, que agora tem a trilha no cabeçalho; passa a usar as inscrições recebidas do mesmo Edital, que continua com o caminho da `076` |
| `test_telas_de_uso_diario.py::test_cada_correcao_vale_so_na_sua_tela` | perde as três regras que subiram; as duas que ficam (sorteio, Retificação) continuam provadas; um teste novo prova que as três saíram e que a folha comum tem as duas regras |
| `test_compor.py::test_estrutura_acessivel_da_composicao` | continua igual — a trilha está na página, no cabeçalho |
| `test_acessibilidade_da_012.py::test_as_telas_tem_titulo_e_trilha_de_navegacao` | continua igual |
| `test_polish_da_058.py`, `test_conducao_dos_bloqueios.py` | continuam iguais — leem o cartão pelo `id`, onde quer que ele esteja |
| `performance/test_escala_da_mesa.py` (120 000 bytes) | medido antes e depois |

Testes novos em `tests/interface/test_telas_de_quem_elabora.py`.

## Achados registrados, fora do escopo

Nenhum novo até aqui; os que a implementação encontrar entram nesta seção.
