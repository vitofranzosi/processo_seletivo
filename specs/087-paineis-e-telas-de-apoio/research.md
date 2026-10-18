# Pesquisa — 087

As decisões de governança — o que se escolheu e o que não se muda — estão na spec (D-001 a D-005).
Aqui ficam as questões de desenho e de teste, e os achados.

## R-001 — A trilha das oito telas

**Decisão**: os oito templates sobrescrevem o bloco `caminho_do_contexto` que a `077` criou, com a
mesma `nav aria-label="Trilha de navegação" class="caminho-da-secao"` e o produto pelo parcial
`_produto_na_trilha.html` (`078`), e os seis que a tinham a tiram do `main`:

| Tela | Antes | Agora, no cabeçalho |
|---|---|---|
| Visão Geral | cabeçalho: *GPS › Visão Geral*, texto; nenhuma trilha | GPS › **Visão Geral** |
| Autoridades da unidade | cabeçalho: *GPS › Autoridades da unidade*, texto; nenhuma trilha | GPS › **Autoridades da unidade** |
| Supervisão | conteúdo: Processos Seletivos › código › Supervisão | GPS › Processos Seletivos › código › **Supervisão** |
| Conferência do ato do Processo | conteúdo: Processos Seletivos › código › ato | GPS › Processos Seletivos › código › **ato** |
| Respostas do assistente de dúvidas | conteúdo: Processos Seletivos › Edital › tela | GPS › Processos Seletivos › código › Edital › **tela** |
| Assistente do Edital (piloto) | conteúdo: Processos Seletivos › Edital › tela | GPS › Processos Seletivos › código › Edital › **tela** |
| Conferência do ato do Edital | conteúdo: Processos Seletivos › Edital › ato | GPS › Processos Seletivos › código › Edital › **ato** |
| Criar Processo Seletivo | conteúdo: Processos Seletivos › Criar | GPS › Processos Seletivos › **Criar** |

Em negrito, a página atual. **Medido antes**, sobre `cf6d7372`: das três telas do Edital, nenhuma
levava ao Processo (`SC-773`); das oito, seis tinham duas indicações de lugar por página — o texto
do cabeçalho e a trilha do conteúdo —, e duas tinham uma, que não era navegação.

**Por quê**: é o desenho da `077` à `080`. As telas do Edital levam a trilha do Edital, com elas no
fim (D-001); os painéis de seção, a da lista (D-002). As telas moram sob `/gestao/` — a Visão Geral e
as Autoridades sob o endereço da própria seção, as demais sob `/gestao/processos/` e
`/gestao/editais/` —, e a barra já as marca pelo endereço: a trilha e a barra concordam sem
declaração da view.

**Alternativa descartada**: "Novo Processo Seletivo" como rótulo de Criar, que é o do botão da
lista. A tela dizia "Criar" como página atual, e a regra destes incrementos é manter o rótulo que a
tela já usava (D-001 da `080`); o título continua "Criar Processo Seletivo".

## R-002 — "Perguntar"

**Decisão**: `class="botao"`, com um comentário do porquê no template. "Começar outra conversa"
continua `acao`, num formulário próprio, como a `071` o fixou (`contracts/tela.md`, item 7).

**Por quê**: D-003. Nenhuma regra da folha muda: `botao` é a classe da ação principal em toda a
gestão, e o `p.campo.escolha` em volta já o alinha. O teste conta um `botao` só no conteúdo, para
que a hierarquia não se desfaça por um segundo botão principal.

**Alternativa descartada**: "Consultar neste instante" como `botao` nas Respostas do assistente de
dúvidas, por analogia com "Filtrar" (D-004 da `080`). Lá "Filtrar" era a única ação da consulta; aqui
a principal já é "Ver a resposta", e duas na mesma tela desfazem a hierarquia (D-003).

## R-003 — O código do Processo nas telas do Edital

**Decisão**: `edital.processo_id` para o endereço e `edital.processo.institutional_code` para o
rótulo — a forma do detalhe do Edital (`078`).

**Por quê**: `obter_edital` carrega o Edital com `select_related("processo")`, e as duas telas do
assistente passam `edital.processo` como `processo`; nenhuma consulta a mais. O guardião
`test_o_processo_da_trilha_nao_custa_consulta` prova que nenhuma consulta lê o Processo sozinho, nas
três telas; **foi provado por mutação** — sem o `select_related`, os três casos reprovam.

## R-004 — O que muda nos testes

- **`test_shell_da_gestao.py::test_na_propria_secao_o_item_e_a_pagina_atual`** (`076`) lia o texto
  *› Visão Geral* do `p.caminho-da-secao`, que a Visão Geral não tem mais. Passa a ler o fim da trilha
  do cabeçalho — a mesma afirmação, "o caminho acaba nela", na forma nova —, com a docstring dizendo
  por quê.
- Nenhum outro teste fixava a trilha no conteúdo destas oito telas, nem o desenho de "Perguntar".
- **Novos**, em `tests/interface/test_paineis_e_telas_de_apoio.py`: a trilha única no cabeçalho e o
  conteúdo pelo título nas oito; a barra na mesma seção; o Processo e o Edital na trilha das telas do
  Edital; o custo zero de consulta; a hierarquia no Assistente e nas Respostas; "Confirmar" e
  "Encerrar a vigência" com o desenho de antes, e a conferência com recusa certa sem "Confirmar"; os
  quatro indicadores da Visão Geral e o Pulso da Supervisão, na ordem de antes.

## R-005 — A contagem do fechamento

**Decisão**: `doc/inventario-visual-da-gestao-2026-10-16/trilhas_no_cabecalho.py` conta, pelo texto,
os modelos que estendem `interface/base.html` diretamente e não têm o bloco, e lista à parte os que
têm o bloco com `block.super` — uma variante que fica com o cabeçalho da `076`.

**Medido** (D-005, `SC-776`): na `main` em `cf6d7372`, 59 modelos estendem a base; 42 sem o bloco, e a
Auditoria, com a variante do Edital. Nesta branch, antes de trazer a `main` de novo, 34 sem o bloco,
e a mesma Auditoria. A contagem do PR é a da `main` de quando ele for aberto.

**Por quê pelo texto, e não pela tela**: o pedido conta modelos de página, e o inventário abre só as
telas que o roteiro alcança por endereço — as conferências que respondem a um envio ficam fora dele.
Pelo texto, nenhuma escapa.

## Achados registrados, fora do escopo

- **O ajudante `caminho()` de `test_shell_da_gestao.py` lê o `p.caminho-da-secao` da `076`**, e o
  guardião que o usa nas Inscrições do Edital (`test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha`)
  quebra quando as Inscrições ganharem a trilha no cabeçalho — é o que a `085` faz. Quando a última
  tela da gestão sair do cabeçalho da `076`, o ajudante e a regra `p.caminho-da-secao` deixam de ter
  quem os use; se o bloco padrão do `base.html` deve então virar a trilha de um nível, é decisão
  aberta.
- **A conferência dos atos da Retificação** (`retificacao_confirmar.html`) tem a trilha no conteúdo, e
  ela começa pelo Edital — sem Processos Seletivos nem o Processo. Fica com o grupo da Retificação.
- **As duas telas do assistente repetem, cada uma, regras de folha quase iguais** (`.versao`,
  `.natureza`, `.literal`, `.origem`, `.referencia`). Não muda caixa nenhuma, e unificá-las é
  refatoração da folha, fora de um incremento de apresentação.
