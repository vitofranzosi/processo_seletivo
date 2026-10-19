# Pesquisa — 083

As decisões de governança — o que se escolheu e o que não se muda — estão na spec (D-001 a D-007).
Aqui ficam as questões de desenho e de teste, e os achados.

## R-001 — A trilha das doze telas

**Decisão**: os doze templates sobrescrevem o bloco `caminho_do_contexto` que a `077` criou, com a
mesma `nav aria-label="Trilha de navegação" class="caminho-da-secao"` e o produto pelo parcial
`_produto_na_trilha.html` (`078`), e a tiram do `main`. Em `auditoria.html`, o ramo do Edital, que
devolvia o `block.super`, passa a ter a trilha, e a trilha condicional do conteúdo sai.

| Tela | Trilha antes, no conteúdo | Trilha agora, no cabeçalho (depois de *GPS › Processos Seletivos › código*) |
|---|---|---|
| Novo Edital | Processos Seletivos › código › Novo Edital | › Novo Edital |
| Retificar | Processos Seletivos › Edital › Retificar | › Edital › Retificar |
| Retificação | Processos Seletivos › Edital › Retificação | › Edital › Retificação |
| Conferência do ato | Edital › Retificação › ato | › Edital › Retificação › ato |
| Prévia | Processos Seletivos › Edital › Prévia | › Edital › Prévia |
| Partir de um Edital anterior | Processos Seletivos › Edital › Compor › Partir de um Edital anterior | › Edital › Compor › Partir de um Edital anterior |
| Conferência da troca | Processos Seletivos › Edital › Partir de um Edital anterior › Confirmar | › Edital › Compor › Partir de um Edital anterior › Confirmar |
| Condução do marco | Processos Seletivos › Edital › marco | › Edital › marco |
| Conferência do gesto | Processos Seletivos › Edital › marco › Conferir | › Edital › marco › Conferir |
| Prévia de publicação | Processos Seletivos › Edital › Ato de classificação¹ › Publicar resultado | › Edital › Ato de classificação¹ › Publicar resultado |
| Resultados divulgados | Processos Seletivos › Edital › Classificação¹ › Resultados divulgados | › Edital › Classificação¹ › Resultados divulgados |
| Auditoria do Edital | Processos Seletivos › Edital › Auditoria | › Edital › Auditoria |

¹ Link só para quem alcança a tela da classificação; texto para os demais (D-003).

**Os níveis de cima num parcial** (revisão do PR): Processos Seletivos, o Processo e o Edital vêm de
`_ate_o_edital_na_trilha.html`, incluído nas onze telas que passam pelo Edital — o mesmo motivo do
parcial do produto da `078`: renomear um nível não pode esquecer uma tela. A abertura da `nav` continua
escrita em cada tela, que é o que a `081` decidiu e o guardião dela confere; o parcial vem depois do
produto, e não muda a abertura. Novo Edital não o usa: lá ainda não há Edital.

**Antes, medido nos templates de `cf6d7372`**: das doze, só Novo Edital passava pelo Processo, e a
conferência do ato começava pelo Edital, sem Processos Seletivos (SC-733).

**Por quê**: é o desenho da `077` à `080`, e o nível que se acrescenta é o que o detalhe do Edital já
tem no cabeçalho desde a `078` (D-001). As telas moram sob `/gestao/processos/`, `/gestao/editais/` e
`/gestao/retificacoes/`, e a barra marca Processos Seletivos em todas: a barra e o começo da trilha
concordam sem declaração nenhuma da view.

**O Compor da conferência da troca.** A conferência é a resposta ao envio de Partir de um Edital
anterior, e a view entrega como `voltar` o endereço dessa tela, e não o da composição. O nível
Compor leva a `interface:compor`, que abre a primeira etapa — o mesmo destino que o `voltar` de
Partir de um Edital anterior tem. Nenhuma variável nova da view.

**Alternativas**:
- *Acrescentar a classificação à trilha da Prévia de publicação* (Edital › Classificação › Ato) —
  seria um nível que a tela não mostrava, e ele também teria de ser condicional; os níveis ficam os
  de cada tela.
- *O Perfil no nível do marco* — o `h1` da Condução já diz o Perfil, e a trilha diz o que a tela
  dizia; acrescentá-lo é decisão de rótulo, e não deste incremento.

## R-002 — Nenhuma consulta a mais

**Decisão**: a trilha lê o código pelo Edital (`edital.processo.institutional_code`) e o endereço
por `edital.processo_id`, como o detalhe do Edital e a composição.

**Medido em 18/10/2026**, com um teste descartável que renderiza cada tela pelo cliente de teste, com
os templates de antes e de depois, e conta as consultas: o total é **idêntico** nas doze telas, e
nenhuma consulta nova lê `processos_processo`. As views que leem o Edital por `obter_edital`, por
`_edital_para_publicar` ou pela porta da auditoria já trazem o Processo junto (`select_related`); a
Retificação o traz pelo Edital dela. Novo Edital lê o Processo, que a view já entrega.

## R-003 — A resposta ao envio

**Decisão**: em `retificar.html`, o resumo de recusas (`_erros.html`) sobe para logo depois do
`p.sub`, antes do aviso "Como funciona" ou "Somente leitura". Em `previa_de_publicacao.html`, o
`p.erro` sobe para logo depois do `p.sub`, antes do `p.imutavel` ("Esta é uma prévia"). Os elementos
são os mesmos — `role="alert"`, `tabindex="-1"` e `autofocus` —, com o mesmo texto.

**Por quê**: é a ordem da Distribuição (`079`) e das telas da `080`: título, linha de baixo, o que
acabou de acontecer.

**O que fica**: na Prévia de publicação, as consequências ("O que acontece ao confirmar") continuam
antes do formulário — são a pergunta antes do ato (D-006). Na Condução do marco, o erro e o desfecho
continuam depois de "Termos desta tela" (D-007): o desfecho usa *recorte*, que o bloco define, e a
`FR-424` da `030` pede a definição no primeiro uso. Medido: o texto do desfecho contém "Abrir este
recorte", e subir o bloco poria esse uso antes do `dfn`. O guardião da `030`
(`test_vocabulario_da_composicao.py`) não varre `marco.html` — a lista dele é literal —, e por isso
não teria acusado.

## R-004 — O que fazer, no detalhe da Retificação

**Decisão**: em `retificacao_detalhe.html`, a `section` "O que fazer agora" passa a ser o primeiro
cartão de `.colunas`, antes de "Vigência". Os atos, o desenho de cada um (`botao`, `secundario`,
`perigoso`) e a marca "irreversível" não mudam.

**Por quê**: é a ordem que a `078` deu ao detalhe do Processo e ao do Edital (`FR-1765` da `078`). Em
`.colunas`, a ordem do código é a da leitura a 1280 px (da esquerda para a direita) e a do
empilhamento a 375 px.

**Pelo topo** (revisão do PR): `.colunas` passa a `.colunas ao-topo`, a regra da `057` (`FR-1047`) que o
detalhe do Edital e o do Processo já usam, e a tela inclui o parcial `_estilo_das_terminais.html`, onde
ela mora. Sem isso, a 1280 px, o cartão de "O que fazer agora" sem ato tinha uma linha e se esticava à
altura da Vigência, vazio — o defeito que a `057` corrigiu no detalhe do Edital. As outras regras do
parcial não casam aqui: a tela não tem `em-linha` nem `terminais`.

## R-005 — "Filtrar" e "Limpar" em Partir de um Edital anterior

**Decisão**: `<button type="submit" class="acao">Filtrar</button>` passa a `class="botao"`, e o
"Limpar" sem classe passa a `a.acao` — a marcação de `inscricoes.html`, que o comentário do filtro
já citava.

**Por quê**: D-005. As duas classes têm regra na folha comum; nenhuma classe nova.

## R-006 — O que muda nos testes

| Guardião | O que muda |
|---|---|
| `test_telas_de_uso_diario.py::test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076` | passa da Auditoria do Edital à Supervisão do Processo, que nenhum incremento nomeou (`FR-1748` da `077`, `FR-1853`) |
| `test_telas_filhas_da_distribuicao.py::test_a_auditoria_do_edital_continua_com_o_cabecalho_da_076` | sai: provava a `FR-1803` da `080` na Auditoria do Edital, que está agora na `083`; o comentário no lugar dele aponta para o arquivo novo |
| `test_telas_de_uso_diario.py::trilha_unica_no_cabecalho` e os auxiliares da `079` | reusados, sem mudança |
| `test_telas_de_quem_elabora.py::test_o_produto_da_trilha_tem_uma_fonte_so` | continua igual — os doze templates incluem o parcial |
| `test_retificar.py`, `test_reaproveitar.py`, `test_conducao_do_marco.py`, `test_acessibilidade_publicacao.py`, `test_destinos_do_edital.py` | continuam iguais; os auxiliares e as fixtures deles são reusados no arquivo novo |

Testes novos em `tests/interface/test_telas_do_edital.py`. **Provado que reprovam sem a mudança**: com
os templates de `cf6d7372`, os onze casos do arquivo novo falham, e com os de agora passam.

## Achados registrados, fora do escopo

- **"Termos desta tela" na Condução do marco vem antes da resposta ao gesto** (D-007). Para a resposta
  subir sem contrariar a `FR-424`, o desfecho teria de dizer o que faz sem a palavra *recorte*, ou o
  bloco de termos teria de vir junto dele — decisão de texto, e não de apresentação.
- **A lista do guardião de vocabulário não tem `marco.html`.** A tela usa *recorte* em texto visível e
  o define num `dfn`, mas nenhum teste cobra que a definição continue no primeiro uso. É a armadilha
  que a memória do projeto chama de "lista literal".
- **A Prévia volta com o desenho de ação principal** (D-006). É a única ação da tela além de abrir o
  arquivo, e por isso não foi tocada; se a equipe achar que "Voltar" não é a ação principal de uma
  prévia, a mudança é de uma classe.
- **O nível do marco não diz o Perfil.** Dois marcos de Perfis diferentes costumam ter o mesmo nome
  (comentário de `marco.html`); a trilha diz só o nome, como dizia, e o `h1` desfaz a ambiguidade.

## Revisão do PR (18/10/2026)

`/code-review` no PR 303, sete achados, todos corrigidos neste PR:

| Achado | Correção |
|---|---|
| Comentário em `test_telas_da_presidencia.py` dizia que o arquivo da `080` ainda provava a Auditoria do Edital de fora | reescrito: ela está no cabeçalho desde a `083` |
| A linha da `FR-1748` na rastreabilidade da `077` dava o guardião na Auditoria do Edital | acrescentado o passo da `083`, à Supervisão |
| O teste da conferência do ato dependia do espaço que o `{% if %}` vazio deixa na classe | a expressão aceita a classe com ou sem espaço |
| `origem` e `destino` importadas de `test_reaproveitar.py`, com `noqa` em cada caso | declaradas no próprio módulo, sobre `publish_original` |
| `next()` sem padrão sobre os gestos do marco | lista e asserção com mensagem |
| O prefixo da trilha copiado em onze telas | o parcial `_ate_o_edital_na_trilha.html` (R-001) |
| O detalhe da Retificação sem `ao-topo` | `ao-topo` e o parcial de estilo (R-004) |

