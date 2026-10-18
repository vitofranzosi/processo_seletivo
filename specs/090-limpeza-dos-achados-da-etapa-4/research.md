# Research — 090

Medido sobre a `main` em `46c374cc` (com a `088`), em 18/10/2026. A implementação parte da `main` com
a `089`, que move a folha comum de `interface/templates/interface/base.html` para
`interface/static/interface/gestao.css`; os caminhos de folha abaixo são os de depois da `089`.

## R-001 — A marca descreve o ato pelo `id`

**Decisão**: em `processo_detalhe.html`, `_acao_do_edital.html` e `retificacao_detalhe.html`, a marca
`<span class="marca-irreversivel">` ganha `id="irreversivel-<chave do ato>"`, e o link do ato,
`aria-describedby` com esse `id` — o desenho que a `081` deu às consolidações da Distribuição
(`FR-1827` da `081`). Só quando o ato é irreversível: os outros não ganham atributo nenhum.

**Por quê**: a marca é texto visível depois do link, e o leitor de tela só a lê ao percorrer a página
linha a linha; no foco, anuncia o nome acessível do link — o rótulo — e a descrição, se houver. A chave
do ato é única na página: nos três detalhes, ela já é o identificador da rota do ato, e no do Edital o
mesmo `acao.chave` já forma o `id` do motivo da ação indisponível (`motivo-<chave>`), sem colisão. O
prefixo `irreversivel-` não aparece em nenhum outro `id` da gestão (medido por `grep`).

**Os atos alcançados** (medido nas listas de atos, 18/10): no Processo, "Encerrar Processo" e
"Cancelar Processo" (`atos_processo.py`); no Edital, "Publicar", "Encerrar" e "Cancelar" (`atos.py`);
na Retificação, "Publicar Retificação" e "Cancelar Retificação" (`atos_retificacao.py`). O ato
indisponível do Edital é um `span` desabilitado descrito pelo motivo e não tem marca, como antes.

**Alternativas descartadas**:
- *A marca dentro do link* — mudaria o nome acessível ("Encerrar Processo irreversível") e o desenho:
  a marca tem fundo e borda próprios, e o link a envolveria.
- *`aria-label` com o sufixo* — duplicaria o rótulo num atributo e o desligaria do texto visível; a
  `081` já escolheu a descrição.

## R-002 — A trilha das consultas da Etapa pergunta à porta

**Decisão**: `_etapa_para_auditar` passa a devolver, além de ator, Edital e Etapa, se quem lê **gere a
comissão** do Processo — o `pode_gerir_comissao` que ela já calcula para decidir a porta. As três
views (`resultados_da_etapa`, `trilha_da_avaliacao`, `conclusoes_preservadas`) o entregam ao template
como `pode_gerir_a_comissao`; em `resultados.html`, `conclusoes.html` e no ramo `da_avaliacao` de
`auditoria.html`, a Alocação por Etapa e a Etapa são link com ele, e texto sem ele. O Processo e
Processos Seletivos continuam link para todos: abrem para quem audita (medido pela `080`).

**Por quê não custa consulta**: a porta das três telas é `_pode_auditar_a_etapa`, que é
`pode_gerir_comissao(...) is not None or ator.can("auditoria:consultar")`. O primeiro termo é avaliado
sempre — é ele que consulta a presidência — e o segundo é leitura da identidade em memória. Guardar o
primeiro termo, em vez de recalculá-lo na view, deixa a contagem igual; medir antes e depois, nas três
telas e para quem preside e quem audita, é o teste (`FR-2064`).

**Por quê é a mesma regra das portas de destino**: a Alocação abre por `_processo_para_gerir` e a
Distribuição por `_etapa_para_distribuir`; as duas recusam com `pode_gerir_comissao(...) is None`. A
Distribuição pede ainda a Etapa vigente — a mesma que `_etapa_para_auditar` já exigiu para abrir a tela
de origem. Não há caso em que a tela de origem abra, o termo diga sim e a de destino recuse.

**Alternativas descartadas**:
- *Uma consulta nova na view* (`pode_gerir_comissao` de novo) — é o que a decisão 003 da `080` evitou, e
  o pedido proíbe consulta a mais.
- *Esconder os dois níveis para quem audita* — a trilha mudaria de forma por papel; a `083` já decidiu
  que o nível fica, como texto.
- *Pendurar o resultado na `request` ou na Etapa* — esconderia de quem lê a view de onde vem a
  informação; a tupla da porta é o caminho explícito, e só três views a usam.

## R-003 — `flex-wrap` na regra comum `.salvar`

**Decisão**: `flex-wrap:wrap` na regra `.salvar` de `gestao.css`. Nada mais muda nela: o `gap` de 1rem
passa a valer também entre as linhas.

**Quem usa** (medido por `grep` nos templates, 18/10): dezoito templates, 27 rodapés — `alocacoes`,
`auditoria` (dois: a Trilha da avaliação e a Auditoria da comissão), `autoridades`, `aviso_interromper`,
`comissao` (três), `comissao_confirmar` (dois), `conclusoes`, `confirmar`, `consolidacao_confirmar`,
`distribuicao_remover_confirmar`, `marco_conferir`, `matriculas` (dois), `modelo_de_aviso`,
`ordenacao_confirmar`, `processo_confirmar`, `recurso` (três), `recursos` e `retificacao_confirmar`.
Dezesseis deles têm mais de um elemento no rodapé; só nesses a regra pode mudar alguma coisa, e só
quando não cabem lado a lado. No inventário, as variantes que os abrem são: `alocacoes`,
`auditoria-comissao`, `trilha-da-avaliacao`, `conclusoes-preservadas`, `autoridades`, `comissao`,
`aviso-interromper`, `ato-*` (cinco do Edital), `processo-ato-*` (três), `retificacao-ato-*` (cinco),
`exportar-matriculas`, `modelo-de-aviso`, `modelo-de-aviso-novo`, `recursos`, `recurso-pendente` e
`recurso-admitido`. As conferências que só se abrem por envio (`comissao_confirmar`,
`consolidacao_confirmar`, `distribuicao_remover_confirmar`, `marco_conferir`, `ordenacao_confirmar`)
ficam fora do inventário, e são vistas no navegador.

**Por quê não muda nada a 1280 px**: com `flex-wrap`, cada item parte da largura do próprio conteúdo
e só desce de linha quando a soma não cabe; a 1280 px, a soma cabe em todos os rodapés medidos — o
inventário é a prova, variante a variante, nos dois estados da barra (`FR-2066`).

**Por quê a quebra é entre os botões a 375 px**: sem `flex-wrap`, a linha não pode crescer para baixo,
e o único jeito de caber é encolher os itens — o rótulo quebra dentro do botão. Com ele, o item desce
inteiro. Um rótulo maior que a largura inteira ainda quebraria dentro do botão, e é o que deve
acontecer; nenhum dos rótulos medidos chega perto disso.

**Alternativas descartadas**:
- *Corrigir só a interrupção do aviso* — é uma de dezesseis telas com o mesmo rodapé (D-003 da spec).
- *`white-space:nowrap` nos botões* — faria o rodapé estourar a 375 px em vez de quebrar; é o defeito
  que a gestão já teve num `fieldset` com botões `nowrap` em linha flexível.

## R-004 — A quarta porta da prévia, dita pelo endereço

**Decisão**: o link "Avisar candidatos" dos Resultados divulgados (`publicacoes_do_marco.html`) ganha
`de=marco` no endereço. Em `aviso_do_resultado`, com `de=marco` e se quem lê abre os Resultados
divulgados — `resultado:publicar` ou `auditoria:consultar`, as capacidades da porta de consulta de
`_edital_para_publicar` —, o `voltar` passa a ser os Resultados divulgados do marco, e a view entrega
`de` e se quem lê abre a Classificação (`pode_ver_a_classificacao`, a mesma pergunta que os
Resultados divulgados fazem para o mesmo nível). `aviso_previa.html` repete `de` nos dois formulários
— o de "Usar este modelo" (GET) e o do envio (POST) —, como já repete `natureza`, `lista` e
`comunicacao`; e a trilha ganha o ramo dos Resultados divulgados, depois do reenvio e da chamada e
antes do de sempre.

**Por quê pelo endereço**: o `Referer` nem sempre vem, e daria duas trilhas ao mesmo endereço (D-004
da spec). A chamada já diz a lista pelo endereço, e o reenvio é rota própria; a quarta porta segue a
primeira.

**O custo**: as capacidades de `_edital_para_publicar` são leitura da identidade, em memória. A da
Classificação pergunta, como nos Resultados divulgados, se quem lê gere a comissão — uma consulta à
presidência quando não há permissão sistêmica —, e só nesta porta. A prévia aberta pelos Avisos aos
candidatos não faz consulta a mais; a aberta pelos Resultados divulgados faz no máximo uma, medida no
teste.

**Por quê "porta que quem lê não abre" cai nos Avisos**: quem abre a prévia do aviso de resultado
tem base para avisar (`base_do_aviso`), e quem tem base abre os Avisos aos candidatos
(`pode_consultar`). Um presidente sem `resultado:publicar` alcança a prévia, mas não os Resultados
divulgados; com `de=marco` escrito à mão, a trilha não lhe ofereceria uma porta fechada.

**Alternativas descartadas**:
- *Rota própria para a prévia pelo marco* — duplicaria a view, e a porta de autorização, por uma
  diferença só de navegação.
- *Omitir a Classificação da trilha* — dispensaria a consulta, mas a trilha da prévia deixaria de ser
  a trilha da tela de onde se abre mais a própria tela, que é a regra da `086` (o reenvio carrega os
  Avisos e o aviso anterior).

## R-005 — Testes que mudam

Nenhum teste existente muda de asserção, salvo se a varredura do implement mostrar o contrário. Os
que prendem a trilha das três consultas (`test_telas_filhas_da_distribuicao.py`) abrem como
presidência, e a trilha da presidência não muda. Os da prévia (`test_telas_dos_avisos.py`) abrem pelo
endereço sem `de`, que continua dando a trilha dos Avisos. As anotações de emenda na `080` e na `086`
não mudam identificador nenhum.

Os testes novos ficam em `tests/interface/test_limpeza_dos_achados_da_etapa_4.py`.

## Achados (registrados, não corrigidos)

- **"Publicar resultado", no Ato de classificação, declara-se irreversível e não tem marca.** A ação
  vem de `acoes.py` com `irreversivel=True`, mas `ato_ordenacao.html` a desenha sem a marca — o
  defeito não é a marca não ser anunciada, é não existir. Acrescentá-la é mudar o desenho de outra
  tela, que nenhum dos quatro achados nomeia. Visto em 18/10/2026.
