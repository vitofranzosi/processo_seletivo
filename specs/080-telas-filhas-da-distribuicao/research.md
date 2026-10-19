# Pesquisa — 080

As decisões de governança — o que se escolheu e o que não se muda — estão na spec (D-001 a D-005).
Aqui ficam as questões de desenho e de teste, e os achados.

## R-001 — A trilha das filhas e da auditoria da comissão

**Decisão**: `impedimentos.html`, `ocorrencia.html`, `resultados.html`, `conclusoes.html`,
`distribuicao_remover_confirmar.html` e `auditoria.html` sobrescrevem o bloco `caminho_do_contexto`
que a `077` criou, com a mesma `nav aria-label="Trilha de navegação" class="caminho-da-secao"` e o
produto pelo parcial `_produto_na_trilha.html` (`078`), e a tiram do `main`:

| Tela | Trilha antes, no conteúdo | Trilha agora, no cabeçalho |
|---|---|---|
| Impedimentos | Alocação por Etapa › Etapa › Impedimentos | GPS › Processos Seletivos › código › Alocação por Etapa › Etapa › Impedimentos |
| Registrar ocorrência | Processos Seletivos › Etapa › Ocorrência | … › Alocação por Etapa › Etapa › Ocorrência |
| Resultados | Processos Seletivos › Etapa › Resultados | … › Alocação por Etapa › Etapa › Resultados |
| Trilha da avaliação | Processos Seletivos › Etapa › Trilha da avaliação | … › Alocação por Etapa › Etapa › Trilha da avaliação |
| Conclusões preservadas | Processos Seletivos › Etapa › Conclusões preservadas | … › Alocação por Etapa › Etapa › Conclusões preservadas |
| Conferir retirada | Processos Seletivos › Etapa › Conferir | … › Alocação por Etapa › Etapa › Conferir |
| Auditoria da comissão | Processos Seletivos › código › Auditoria da comissão | GPS › Processos Seletivos › código › Auditoria da comissão |

**Por quê**: é o desenho da `077` à `079`. Os níveis das filhas são os da Distribuição, e não os que
cada uma tinha, porque elas os tinham diferentes (D-001). As telas moram sob `/gestao/editais/` e
`/gestao/processos/`, e a seção delas, pelo endereço, já é Processos Seletivos: a barra e o começo da
trilha concordam sem declaração nenhuma da view.

**Nenhuma consulta a mais.** As seis views já entregam `processo` (de `edital.processo`, com
`select_related` na porta da auditoria) — os mesmos objetos que a trilha do conteúdo lia ou podia ler.

**Alternativas**:
- *O Edital na trilha* (Processo › Edital › Etapa) — seria um nível que a Distribuição não mostra; o
  Edital continua na linha abaixo do título.
- *Manter os níveis de cada tela* — levaria ao cabeçalho a diferença que existia (D-001).

## R-002 — Um modelo de página, três trilhas

**Decisão**: em `auditoria.html`, o bloco `caminho_do_contexto` escolhe pela variável que a view já
entrega — `da_avaliacao` ou `da_comissao` — e, sem nenhuma delas, devolve o `block.super`, o
cabeçalho da `076`. A trilha do Edital continua no conteúdo, sob a mesma condição negada.

**Por quê**: a Auditoria do Edital fica fora do escopo (D-002), e o modelo é um só. Separar o
template em três seria mudança de view, e o pedido proíbe; um `include` por ramo não tiraria a
condição, só a mudaria de lugar.

**Alternativa**: *levar a Auditoria do Edital junto* — é um template só, e custaria uma linha; mas a
tela é de quem audita o Edital, e o incremento muda só o que o pedido nomeia e o inventário prova.

## R-003 — As mensagens do último envio

**Decisão**: em `ocorrencia.html`, o erro, o resultado e os grupos de recusa do resultado sobem para
logo depois do `p.sub`, antes do parágrafo que explica o ato. Em `conclusoes.html`, o erro e o
resultado da reabertura sobem para o mesmo lugar, antes da explicação e do filtro. O erro do filtro
(`filtro_invalido`) fica dentro do `form`. Os elementos são os mesmos — `p.erro` com `role="alert"`,
`tabindex="-1"` e `autofocus`, `p.sucesso` com `role="status"` —, com o mesmo texto.

**Por quê**: é a ordem da Distribuição (`079`) e de Impedimentos: título, Etapa, o que acabou de
acontecer. O foco já ia ao erro pelo `autofocus`; a mudança é de onde ele está quando se olha.

**O que fica**: em Registrar ocorrência, a conferência — o aviso que lista quem será eliminado e
"Registrar mesmo assim" — continua depois da explicação: é a pergunta antes do ato, e não a resposta
a ele (D-005).

**Alternativa**: *a explicação antes de tudo* — é o estado de hoje; a frase que a pessoa procura ao
voltar do envio é a do resultado, e a explicação continua antes do formulário, onde ela decide.

## R-004 — Impedimentos com título para o registro

**Decisão**: o formulário de registro entra numa `section aria-labelledby="registrar-titulo"` com
`h2` "Registrar um impedimento", antes da seção "Avaliações fora do conjunto elegível". Os campos, o
botão e a conferência não mudam, e a conferência continua antes da seção, logo abaixo das mensagens.

**Por quê**: a Comissão ganhou título para cada região na `079`; aqui a região sem título era a do
ato. "Registrar um impedimento" e não "Registrar impedimento": o título nomeia a seção, e o botão,
o ato — os dois iguais seriam lidos como repetição.

**Classes.** Nenhuma: `section` e `h2` não precisam de classe.

## R-005 — "Filtrar" nas consultas

**Decisão**: na Trilha da avaliação, na Auditoria da comissão e nas Conclusões preservadas,
`<button type="submit" class="acao">Filtrar</button>` passa a `class="botao"`. "Limpar", no mesmo
`p.salvar`, continua `a.acao`; "Reabrir", em cada linha, continua `button.acao`.

**Por quê**: D-004. No `p.salvar`, `.acao` já tinha a altura do botão (`055`, `FR-1006`) e o desenho
contornado do secundário: o que muda é só o preenchimento, o mesmo passo que a `055` deu nas
Inscrições, na Distribuição e na Comissão.

## R-006 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_telas_da_presidencia.py::test_as_filhas_da_distribuicao_continuam_com_o_cabecalho_da_076` | sai: provava a `FR-1782` da `079` em quatro filhas, e as quatro estão agora na `080`; o comentário no lugar dele aponta para o arquivo novo |
| `test_telas_de_uso_diario.py::test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076` | passa da Trilha da avaliação à Auditoria do Edital, que continua fora (`FR-1748` da `077`) |
| `test_telas_de_uso_diario.py::trilha_unica_no_cabecalho` e os auxiliares da `079` | reusados, sem mudança |
| `test_telas_de_quem_elabora.py::test_o_produto_da_trilha_tem_uma_fonte_so` | continua igual — as seis telas incluem o parcial |
| `test_polish_da_055.py::test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha` | continua igual — as três telas dele não mudam |
| `test_distribuicao.py::test_a_remocao_tem_rota_e_formulario_proprios` | continua igual — "Confira antes de retirar" |
| `test_acessibilidade_da_012.py` | continua igual — a trilha está na página, no cabeçalho |

Testes novos em `tests/interface/test_telas_filhas_da_distribuicao.py`.

## Achados registrados, fora do escopo

- **Quem audita lê na trilha dois níveis que não abre.** Resultados, Trilha da avaliação e Conclusões
  preservadas abrem para a auditoria; a trilha leva à Alocação por Etapa e à Etapa, que respondem
  **403** a quem audita sem presidir (medido em 17/10 com `inventario.auditora`: Processos Seletivos
  200, Processo 200, Alocação 403, Distribuição 403). A Distribuição já estava na trilha de antes; a
  Alocação é nível novo. Oferecer os níveis por capacidade pediria à view uma informação que ela não
  entrega (D-003). O comentário de `_pode_auditar_a_etapa` já registra a
  mesma preocupação para a tela do recurso ("link para porta fechada responde 404, e 404 não explica
  nada"), e a resposta sairia dali.
- **A Auditoria do Edital é a última do modelo com a trilha no conteúdo.** Ela e as outras telas do
  Edital fora da `078` são o próximo grupo natural (D-002).
- **A frase da trilha da avaliação diz "Trilha de auditoria".** O `h1` das três auditorias é o mesmo,
  e a página atual da trilha diz "Trilha da avaliação" ou "Auditoria da comissão". Não mudou aqui: o
  `h1` é medido pelo inventário, e mudá-lo não é o que o pedido nomeia.
- **O inventário de antes não reproduz `depois-da-079/` em duas telas**, por dado: as duas alocações
  que o percurso da `079` gravou depois da captura dela (auditoria da comissão) e a hora da leitura
  (aviso). O código de `backend/processo_seletivo/` é o mesmo desde o merge da `079`.
