# Pesquisa — 085

As decisões de governança — o que se escolheu e o que não se muda — estão na spec (D-001 a D-004).
Aqui ficam as questões de desenho e de teste, e os achados.

## R-001 — A trilha das quatro telas

**Decisão**: `inscricoes.html`, `inscricao_detalhe.html`, `recursos.html` e `recurso.html`
sobrescrevem o bloco `caminho_do_contexto` que a `077` criou, com a mesma `nav aria-label="Trilha de
navegação" class="caminho-da-secao"` e o produto pelo parcial `_produto_na_trilha.html` (`078`), e a
tiram do `main`:

| Tela | Trilha antes, no conteúdo | Trilha agora, no cabeçalho |
|---|---|---|
| Inscrições | Processos Seletivos › Edital › Inscrições | GPS › Processos Seletivos › código › Edital › Inscrições |
| Inscrição recebida | Processos Seletivos › Edital › Inscrições › protocolo | … › Edital › Inscrições › protocolo |
| Recursos | Processos Seletivos › Edital › Recursos | … › Edital › Recursos |
| Recurso | Processos Seletivos › Edital › Recursos › protocolo | … › Edital › Recursos › protocolo |

**Por quê**: é o desenho da `077` à `080`, e os níveis são os do detalhe do Edital (D-001). As telas
moram sob `/gestao/editais/`, `/gestao/inscricoes/` e `/gestao/recursos/`, e a seção delas, pelo
endereço, já é Processos Seletivos: a barra e o começo da trilha concordam sem declaração da view.

**As portas dos níveis**, lidas nas views em 18/10/2026:

| Nível | Porta | Quem abre a tela de origem também abre o nível? |
|---|---|---|
| Processos Seletivos | identidade | sim |
| o Processo (`processo_detalhe`) | escopo da unidade | sim — é a mesma condição de escopo das quatro telas |
| o Edital (`detalhe`, por `obter_edital`) | escopo da unidade | sim — já estava na trilha de antes |
| Inscrições | `inscricao:consultar` (`_edital_no_escopo`) | sim — é a permissão da Inscrição recebida |
| Recursos | `recursos_admitir.PERMISSAO` | sim — é a permissão do Recurso |

O nível novo é o Processo, e a porta dele é a do Edital, que já estava na trilha. O teste abre os
quatro níveis do Recurso como quem só julga, e todos respondem 200.

**Alternativas**:
- *O nome da pessoa na página atual da Inscrição recebida* — o `h1` já é o nome; repeti-lo na trilha
  seria levar dado pessoal ao cabeçalho, que é a região que se lê de longe numa tela compartilhada. O
  protocolo é o que a trilha do conteúdo já usava.
- *"Inscrição recebida" como página atual, sem o protocolo* — perderia o que distingue uma inscrição
  da outra quando há duas abas abertas.

## R-002 — O Processo na mesma leitura

**Decisão**: em `inscricoes/application/consulta.py`, `_edital_no_escopo` ganha
`com_processo=False`, e só `consulta_de_inscricoes` o pede verdadeiro; `inscricao_para_consulta` lê a
inscrição com `edital__processo` em vez de `edital`.

**Medido em 18/10/2026, antes da mudança**, com o cenário da `012` e o recurso de `cenario_julgavel`:
Inscrições 15 consultas, Inscrição recebida 6, Recursos 5, Recurso 8. Os Recursos e o Recurso já liam
o Processo junto do Edital; nas outras duas, o template, sozinho, custaria uma consulta a mais — a
prova é o teste `sem_consulta_ao_processo`, que reprova as duas telas quando a junção é retirada
(conferido ao escrever). Depois da mudança, os quatro números são os mesmos.

**Por quê nesta função e não na view**: é dela que as views recebem o Edital; uma segunda leitura na
view seria a consulta que se quer evitar. `_edital_no_escopo` também é chamada por duas leituras que só
conferem o escopo e descartam o Edital — `inscricao_para_consulta` e `documento_para_consulta` —, e
por isso a junção é pedida, e não posta na função para todas: na primeira versão ela valia para as
três, e cada documento aberto lia as colunas do Processo para nada (achado da revisão de código).

**Alternativa**: *aceitar a consulta a mais* — é constante por página e não cresceria com o certame
(`test_inscricoes_em_escala.py` continua verde de qualquer modo); mas o repositório prende orçamento
de consulta tela a tela, e a trilha da `080` foi feita sem nenhuma.

## R-003 — O estado vazio das Inscrições

**Decisão**: `<p class="aviso">Nenhuma inscrição recebida até agora.</p>` passa a `p.vazio`, com o
mesmo texto. A advertência dos rascunhos continua `p.aviso`.

**Por quê**: o desenho de aviso é o das advertências (`.aviso`, amarelo e borda à esquerda); o estado
vazio comum (`.vazio`, borda tracejada) é o da lista filtrada sem resultado na mesma tela e o da
lista de Recursos. É o passo da `FR-1772` da `078`. O inventário não mostra a mudança: o Edital dele
tem inscrições.

## R-004 — Os rascunhos como região

**Decisão**: o `h2` "Em preenchimento — N", a advertência, a tabela e a paginação dos rascunhos entram
numa `section aria-labelledby="em-preenchimento"`, e o `h2` ganha o `id`.

**Por quê**: é o desenho da Comissão na `079` — título por região. `section` e `h2` não precisam de
classe, e nenhuma regra da folha alcança `section` sem classe: nada muda de lugar.

**Alternativa**: *a região também para as recebidas* — elas não têm título próprio (o `h1` é o total),
e dar-lhes um `h2` mudaria o que se vê.

## R-005 — O que muda nos testes

Um guardião muda de amostra; os outros que tocam estas telas continuam verdes sem emenda:

| Guardião | O que muda, ou por que continua |
|---|---|
| `interface/test_shell_da_gestao.py::test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha` | passa das Inscrições aos Avisos do Edital: prova o caminho da `076` numa tela abaixo do Edital, e as Inscrições deixaram de sê-la. Era o detalhe do Edital até a `078`, que o moveu para cá. Os Avisos foram escolhidos por não estarem no escopo da `083` nem da `084`, que correm em paralelo — conferido nas worktrees delas em 18/10 |
| `integration/interface/test_inscricoes_recebidas.py` | as asserções são do conteúdo — total, colunas, CPF mascarado, documentos sob o requisito —, e o conteúdo não muda |
| `integration/interface/test_inscricoes_em_escala.py` | o custo continua constante: a junção não cresce com o certame |
| `interface/test_proveniencia_do_recurso.py` | o orçamento de 8 consultas do Recurso não muda |
| `interface/test_instrucao_na_peca.py` | os orçamentos de 13 consultas e o da instrução com dois atos não mudam |
| `authorization/test_julgamento_de_recurso.py` | o impedimento antes de qualquer botão |
| `interface/test_polish_da_055.py` | "Filtrar" com o desenho de ação principal nas Inscrições |
| `interface/test_telas_de_quem_elabora.py::test_o_produto_da_trilha_tem_uma_fonte_so` | as quatro incluem o parcial |
| `interface/test_telas_de_uso_diario.py::test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076` | prova a Auditoria do Edital, que continua fora |

Testes novos em `tests/interface/test_telas_de_inscricoes_e_recursos.py`; as fixtures de recurso usam
`seed=185` e o código `0885`, que nenhum outro teste usa (fixtures colidem por idempotência).

## Achados registrados, fora do escopo

- **A tela de recusa não sabe de onde a pessoa veio.** Responde por toda a gestão (D-002), e o único
  caminho que oferece é "Voltar aos Processos Seletivos" — ou "Reabrir a tela como está gravada",
  quando a recusa sabe. Uma trilha nela pediria que `interface/erros.py` entregasse o contexto do
  endereço recusado, o que é mudança do shell e não de um grupo de telas.
- **A impressão perde o Edital na Inscrição recebida e nos Recursos** (D-004). Junta-se à pergunta
  sobre impressão que a `081` registrou para o produto.
- **O comentário do Requerimento de Matrícula em `inscricao_detalhe.html` está sem acentos**
  ("permissao", "so", "declaracao"). É comentário, e não texto da tela; não foi mexido.
- **O Recurso tem oito títulos de seção soltos, sem região.** Com a trilha fora do conteúdo, o `h1` é a
  primeira coisa da página; as regiões ficam para um incremento que trate do Recurso por inteiro
  (D-004).
- **Coordenação com a `081`**: o PR 298 traz dois guardiões que alcançam esta feature. O da abertura
  da trilha varre todo template que sobrescreve o bloco, e as quatro telas daqui já abrem com a mesma
  `nav`. O que proíbe importar o `cenario` do módulo da `012` reprovaria este arquivo de testes se ele
  o importasse — e por isso ele declara a fixture dele.

## Achados da revisão de código (18/10), registrados e não corrigidos

A revisão do PR 304 levantou sete achados; quatro foram corrigidos — a junção do Processo pedida só
pela lista (R-002), uma asserção presa à indentação do template, a docstring que prometia provar o
impedimento e a prova das portas da trilha da Inscrição recebida. Ficam três:

- **A impressão perde o Edital na Inscrição recebida e nos Recursos.** É a troca da D-004, e a
  resposta é do produto: a `081`, no PR 298, registra a pergunta sobre impressão (caso-limite da `076` e da
  `077`). Pô-lo de volta na linha abaixo do título mudaria o que se vê na tela, e é por isso que não
  se faz aqui sem a resposta.
- **O guardião da `076` mora numa tela escolhida à mão.**
  `test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha` precisa de uma tela abaixo do Edital
  com o cabeçalho antigo; a `078` o moveu do detalhe do Edital para as Inscrições, e esta feature, das
  Inscrições para os Avisos do Edital. A quebra só aparece na suíte completa, e quando a última tela
  for modernizada o guardião não terá onde morar. A correção de raiz — decidir se o caminho da `076`
  abaixo da seção continua sendo requisito quando nenhuma tela o usar — é de governança (`FR-1716` e
  `FR-1718` da `076`).
- **O prefixo da trilha até o Edital está copiado em seis templates** — estas quatro telas, o detalhe
  do Edital e a base da composição. Um parcial o tornaria uma fonte só, como o do produto na `078`;
  mas tocaria `detalhe.html` e `compor_base.html`, que estão no escopo da `083`, em paralelo, e a
  `081`, no PR 298 ainda aberto, decide manter a abertura da trilha escrita em cada tela (a decisão
003 dela). Fica para
  quando os incrementos paralelos estiverem na `main`.
