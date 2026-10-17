# Pesquisa — 077

## R-001 — A trilha vai ao cabeçalho por um bloco

**Decisão**: o `base.html` passa a ter, dentro do `header.cabecalho-de-contexto`, o bloco
`caminho_do_contexto`, cujo conteúdo padrão é o caminho da `076` — *GPS › seção*, em texto. As
quatro telas de uso diário sobrescrevem o bloco com a própria trilha, a mesma
`nav aria-label="Trilha de navegação"` que traziam no conteúdo, e a tiram do `main`. O produto
abre a trilha em texto, como na `076`; cada nível acima da tela é link; a tela é a página atual.

**Por quê**: a trilha é conhecimento da tela — só ela sabe o nome da Etapa, o protocolo da
inscrição, e se chegou pela Alocação ou por Minhas Etapas. Pelo bloco, ela continua escrita no
template da tela, com os mesmos dados que ele já recebe, e só muda de lugar na página. O
cabeçalho das outras 55 telas não muda, porque o bloco delas é o padrão. Não há duplicação: a
`nav` que sobe é a mesma que sai.

**Alternativas**:
- *A trilha sobe para o cabeçalho como dado* — cada view entregaria uma lista de níveis, e o
  `base.html` a desenharia. Exige mexer em quatro views e criar uma estrutura que o template já
  resolve, e põe na view o rótulo de um link, que é apresentação.
- *O cabeçalho repete o bloco `titulo`*, que a `076` também descartou (R-004 da `076`): mostra o
  título três vezes seguidas.
- *Manter a trilha no conteúdo e completar o cabeçalho* — é a duplicação que o pedido proíbe.

**A classe.** A `nav` do cabeçalho leva `class="caminho-da-secao"`, a classe do caminho da `076`,
que já tem regra (margem zero, texto fraco). A folha ganha só `.caminho-da-secao a`, para a cor dos
links, a mesma da `.trilha`. Não leva `trilha`: a regra dela dá margem inferior de 1rem, que no
cabeçalho desalinharia a linha com "Trocar identidade".

**Lista e Minhas Etapas.** São a raiz da seção, e a trilha delas tem um nível: *GPS ›* e a tela,
como página atual. É o mesmo texto que o cabeçalho já mostrava, agora como navegação, para que as
quatro telas de uso diário tenham a trilha do mesmo jeito.

## R-002 — Os cinco estouros, medidos

Medidos a 375 px no `ps_inventario_telas`, com a sonda do inventário, antes da mudança, e de novo
com cada regra injetada na página. Com as cinco, as cinco telas ficam com `scrollWidth` de 375.

| Tela | Causa medida | Correção |
|---|---|---|
| `conclusoes-preservadas` (835) | cada linha tem um `label.oculto` com `position:absolute`; a `.tabela-rolavel` que rola não é posicionada, e o rótulo, sem ancestral posicionado dentro dela, toma a página como referência e a alarga — nenhum elemento visível passa da borda | `.tabela-rolavel{position:relative}` na folha da tela: o rótulo passa a ter a moldura como referência, e rola com ela |
| `reaproveitar` (994) | o `fieldset` cresce até a largura mínima da tabela das origens (`min-width:min-content`, padrão do navegador), e a `.tabela-rolavel` dentro dele nunca chega a rolar | `fieldset{min-width:0}` na folha da tela — há um `fieldset` só nela |
| `sorteio` (643) | os dois resumos SHA-256 do parágrafo `.imutavel` (manifesto) não têm onde quebrar; os de `.metodo dd` já quebram por regra própria | `.imutavel code{overflow-wrap:anywhere}` na folha da tela |
| `compor-anexos` (432) | o campo de arquivo tem largura intrínseca de ~366 px, e o `fieldset.linha.anexo-novo` cresce até ela | `fieldset.linha.anexo-novo{min-width:0}` no bloco de estilo que a tela já tem |
| `retificacao-detalhe` (388) | a tabela das alterações, de quatro colunas, não está em moldura que rola, e a largura mínima dela passa 13 px da borda | a tabela dentro de `div.tabela-rolavel`, a moldura que as outras tabelas largas já usam |

**Por que regra da tela, e não da folha comum.** Três das cinco causas são gerais — `fieldset`
que cresce, rótulo oculto sem referência dentro da moldura que rola —, e a regra geral as
resolveria em toda tela. Mas ela mudaria o desenho de telas que este incremento não toca (há 19
templates com `.tabela-rolavel` e algum elemento `.oculto`, e `fieldset` em quase toda a
composição), contra a
`FR-1745`; e a folha comum é servida em toda página, inclusive na distribuição, que tem teto de
bytes. A regra geral fica registrada abaixo, como achado.

**A tabela da Retificação ganha marcação.** É a única correção que toca o HTML. `display:block`
na própria tabela faria a página caber sem `div`, mas alguns leitores de tela deixam de anunciar
como tabela uma `table` com `display` trocado; a moldura é a que a folha já tem.

## R-003 — O que não se mexe na lista

A faixa sai inteira quando não há "Novo Processo Seletivo": o `p.acoes-do-painel` só existe se
houver ação nele. A orientação de quem integra comissão ("Ver minhas atribuições") e o aviso de
quem não tem papel ficam onde estão: são frases, e não as seções duplicadas. Os predicados de
`navegacao.py` continuam sendo o único lugar da regra; a view deixa de pedi-los porque a tela
deixou de usá-los.

## R-004 — O inventário refeito

O roteiro e o banco são os da `076`: `capturar.py`, `ps_inventario_telas`, com o mesmo `AVISO`, uma
vez com `BARRA=expandida` e outra com `BARRA=recolhida`. Cada uma se compara com a linha de base do
shell no mesmo estado, por `comparar.py`. Entram no repositório os dois `resultados.json` e as
capturas das nove telas tocadas, a 1280 e a 375 px, com a barra expandida — as outras capturas
seriam iguais às de `com-o-shell/`, e o `resultados.json` é o que prova isso.

## R-005 — A seção da Etapa aberta pela gestão (emenda de 17/10)

**Achado na revisão do PR.** A Etapa responde em `minhas-etapas/…` pelas duas portas, e a barra
decide a seção pelo endereço (R-003 da `076`): marcava Minhas Etapas também para quem chegou pela
Alocação. Com a trilha no conteúdo, a contradição ficava entre o topo e o corpo; no cabeçalho, ela
ficou lado a lado com a barra — e o cabeçalho deixou de nomear a seção, contra a `FR-1718` da `076`.

**Decisão**: a view declara a seção quando o endereço não basta (`navegacao.declarar_secao`), e a
barra a usa no lugar da do endereço. Pela gestão, a seção é Processos Seletivos, e a trilha é a da
própria Alocação — *Processos Seletivos › código do Processo › Alocação por Etapa* — seguida da
Etapa. Por quem está alocado, nada muda.

**Por quê**: só a view sabe por qual porta a pessoa chegou; o endereço é o mesmo. A barra se monta
preguiçosa, na leitura do `base.html` (R-008 da `076`), depois de a view declarar — não custa
consulta, e nenhuma outra tela muda, porque nenhuma outra declara.

**Alternativas**:
- *Trocar o endereço da Etapa pela gestão* — muda URL, contra a spec.
- *Pôr "Minhas Etapas" antes de "Alocação por Etapa" na trilha* — diria que o gestor veio de onde
  não veio.
- *Só acrescentar "Processos Seletivos" à trilha, sem o Processo* — a Alocação é de um Processo, e
  a trilha pularia um nível que a tela da Alocação mostra.

## Achados registrados, fora do escopo

- **A causa das conclusões preservadas é latente em outras telas.** Toda `.tabela-rolavel` com um
  elemento `position:absolute` dentro pode alargar a página quando o elemento cai além da borda —
  e 19 templates têm `.tabela-rolavel` e algum elemento `.oculto`. Hoje o inventário não acusa
  nenhuma outra. A correção geral, `.tabela-rolavel{position:relative}` na folha comum, é decisão
  de outro incremento.
- **`fieldset` cresce até o conteúdo mínimo em toda a gestão.** É o padrão do navegador, e foi a
  causa de dois dos cinco estouros. Uma regra geral `fieldset{min-width:0}` mudaria a composição
  inteira; fica para o incremento que a modernizar.
