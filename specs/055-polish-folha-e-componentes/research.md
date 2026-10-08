# Research — 055 · Polish da folha e dos componentes

Medições em 30/09/2026, na worktree `polish-folha-componentes-82ee7f` sobre `c0f5ad3d`, no banco
`ps_055_polish` (cópia de `ps_polish_audit`, o banco da auditoria), a 1280 × 900.

---

## As decisões recebidas

O prompt de sessão trouxe dez decisões fechadas. Elas entram como recebidas, e **não** se
reaproveitam como números desta spec — por isso vão aqui nomeadas por ordem, e não por
identificador:

| Recebida | Assunto | Critério que ela fixou |
|---|---|---|
| 1ª | Escopo: G1 a G8, D1 e F7. Nada dos lotes 2 e 3 | O item está na lista? Entra. Não está? É registro |
| 2ª | G1: o padrão dos blocos da Convocação, reaproveitando `ul.resumo` | Número preso ao seu rótulo; a `section` da Ocupação deixa de ser flex |
| 3ª | G2: `.5rem .75rem` | Linha das Inscrições do 51/2026 de 70 para ≤ 45 px |
| 4ª | G3: uma classe para coluna numérica | A pontuação da ordem do marco fica à direita |
| 5ª | G4/G5: mesma altura externa para principal e secundário; borda da cor do fundo no principal | Na barra do assistente, 0 px de diferença |
| 6ª | G5: a ação principal nunca é `.acao`, só nas ações medidas | Nenhum botão de envio sem classe no portal |
| 7ª | G6: h3 global; escala 1,6 / 1,15 / 1 rem, peso 600 | Nenhum h3 maior que o h2 da mesma página |
| 8ª | G7: uma altura por folha para `input` e `select` | 0 px de diferença na mesma linha |
| 9ª | G8: o desenho da Vitrine; a ajuda não sai da tela | Desnível de 22 px para 0 na Distribuição |
| 10ª | D1 e F7 | Cronograma sem o vão de 335 px; campos curtos ≤ ~20 rem, nomes ≤ ~40 rem |

---

## D-001 — A margem sob o teto é de 47 caracteres

**Medida.** O teste `test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`, rodado isolado
contra o PostgreSQL, com a asserção trocada por um `print`: **119.953 caracteres** (121.708 bytes em
UTF-8). A margem é de 47.

**Consequência.** Nenhum item desta feature cabe "por cima". Cada regra nova sai de uma regra velha,
e a folha é editada **no lugar** — nunca por uma regra de sobreposição mais abaixo. Isso é o que a
seção *Restrições* do prompt pedia, e o número mostra que não é recomendação de estilo.

**Descartado.** Remover comentários da folha para abrir espaço. São ~36,8 mil caracteres de prosa
que viajam em toda página, e a decisão sobre eles é do usuário. Se o lote não coubesse, o caminho
era entregar o que coubesse e registrar o que faltou.

## D-002 — Uma altura só, de 40 px, para botão e controle

**Decisão.** `2.5rem` (40 px) para `input` e `select` na gestão, e a mesma altura externa para
`.botao`: `line-height:1.375rem` (22 px) + `padding:.5rem` (2 × 8 px) + borda de 1 px (2 × 1 px).

**Por quê.** Prototipado na página viva: com essas regras injetadas, a barra da Revisão (quatro
**links**) e a do Cronograma (três **botões**) mediram 40 px em todos os itens, e todo controle do
Cronograma também. A folha antiga tinha uma segunda causa de desalinhamento que a auditoria não
nomeou: **link e botão com a mesma classe tinham alturas diferentes** — `a.botao` 44 px contra
`button.botao` 42 px, `a.acao` 30 px contra `button.acao` 26 px —, porque o link herda o
`line-height:1.5` do corpo e o botão usa a métrica `normal` do navegador. Declarar o `line-height`
resolve as duas causas de uma vez.

**Descartado.**
- `min-height` no botão: iguala a caixa, mas o texto do link fica colado no topo, e não centrado.
- `2.625rem`, a altura da Vitrine: 42 px deixaria o botão com 11 px de preenchimento vertical para
  um texto de 15 px — mais pesado que o que existe hoje.

## D-003 — A borda do principal é transparente

**Decisão.** `.botao{border:1px solid transparent}`, e não `border:1px solid var(--verde)`.

**Por quê.** O fundo pinta por baixo da borda (`background-clip:border-box` é o padrão), então a borda
transparente **é** a borda da cor do fundo que a 5ª decisão recebida pede — e continua sendo quando o
fundo muda: no `:hover`, no `.perigoso` e no `.desabilitado`. Com a cor declarada, cada variante
precisaria repetir a sua borda, e isso custa caracteres que não há.

## D-004 — A ação de linha cresce só dentro das três barras

**Decisão.** A geometria do botão é partilhada com `:is(.navegacao-etapa,.salvar,.filtros) .acao`.

**Por quê.** Levantamento de todos os `p.salvar` e `p.navegacao-etapa` dos templates: é ali que
`.acao` aparece ao lado de `.botao` — "‹ Voltar" no assistente, "Cancelar" em nove rodapés de
confirmação, "Limpar" nos filtros. As barras de filtro escritas no singular (`.filtro`) põem os
botões num `p.salvar`, e por isso `.filtro` não precisa entrar na lista. Fora dessas barras, a ação de
linha continua com 25 px, como a 5ª decisão recebida exige.

## D-005 — As ações reclassificadas viram `.botao`, e não secundário

**Decisão.** "Filtrar" (Inscrições, Distribuição, Comissão) e "Ver o que sairá vazio" (Matrículas)
passam de `acao` a `botao`.

**Por quê.** São a ação **única** do formulário em que estão. Secundário pressupõe um principal ao
lado, e aqui não há. "Limpar", que aparece junto do "Filtrar" quando há filtro ativo, continua `acao`
— e ganha a altura do "Filtrar" pela D-004.

## D-006 — A barra de filtro alinha pelo topo, e o botão desce a altura do rótulo

**Decisão.** `.filtro,.filtros{align-items:flex-start}`; os contêineres do botão (`.filtro .salvar`,
`.filtros .acoes`) e a marca de escolha (`.filtro .escolha`) ganham `margin-top:1.46875rem` — a altura
exata do rótulo: 13 px de fonte × 1,5 de entrelinha + 4 px de margem = 23,5 px. A marca ganha também
a altura do controle (`2.5rem`), e o `align-items:center` que ela já tinha a centra.

**Medido no protótipo.** Distribuição: os dois controles e o "Filtrar" em y = 1200,03, com 40 px
cada; a ajuda logo abaixo do campo, em y = 1244. Comissão: o centro do campo, da marca e do botão em
y = 318,09.

**Descartado.** Tirar a ajuda do fluxo (`position:absolute`): ela passaria a sobrepor o que vem
abaixo da barra sempre que tivesse mais de uma linha. E reduzi-la a `placeholder`, que a auditoria
sugeria como alternativa: é texto de interface mudando de lugar, e o placeholder some quando se
digita — exatamente quando a ajuda é lida (**UX-136**).

**Custo aceito.** O valor `1.46875rem` depende do tamanho e da entrelinha do rótulo. Se alguém mudar
`.campo label`, o botão desalinha — e é por isso que o teste desta feature prende os três números
juntos.

## D-007 — O G1 troca `dl` por `ul.resumo`

**Decisão.** No Corte, no histórico do Corte, na Ocupação e no histórico da Ocupação, os números
passam a `<ul class="resumo">` com `<li><strong>valor</strong>rótulo</li>` — a marcação exata da
Convocação —, e a `section` do recorte perde a classe `.resumo`.

**Por quê.** A 2ª decisão recebida manda reaproveitar a regra que existe se ela servir, e ela serve
sem uma linha de CSS. O `ul` já leva `aria-label` na Convocação, e o mesmo nome acompanha aqui.

**Descartado.** Manter o `dl` com cada par num `div`, e ensinar `.resumo` a desenhar `div` e `dd`: é
a semântica de lista de definição preservada, ao custo de uma regra nova na folha que vai para toda
página — e para a de distribuição, que não tem margem.

**Custo aceito.** O leitor de tela deixa de anunciar "termo, definição" e passa a anunciar "lista,
seis itens". A Convocação já é assim, e é a mesma informação.

## D-008 — Quais sobreposições de título saem

**Critério.** Sai a declaração `font-size` que põe um h2 no tamanho de h3 (1 rem) ou um h3 no
tamanho que ele passa a ter pela regra global. Fica a que desenha **outra coisa** além de um título
de seção.

| Regra | Decisão | Por quê |
|---|---|---|
| `.cartao h2{font-size:1rem}` | sai o tamanho | É ela que deixa o h2 do Processo com 16 px, abaixo do h3 "Atenção" |
| `.pendencias h2`, `.consequencias h2` | sai o tamanho | São os dois h2 da Revisão com 16 px, irmãos de um de 18,4 px |
| `.conferencia h3{font-size:1rem}` | sai o tamanho | Fica igual à regra global |
| `.secao-da-retificacao>h2` | sai o tamanho, a caixa-alta e o espaçamento de letra | O comentário acima dela explica o `scroll-margin-top`, e não a caixa-alta |
| `.barra-do-painel h2` | fica | É rótulo de barra de ferramentas ao lado de um botão, no painel da Mesa: crescê-lo mudaria a altura da barra, numa tela do lote 3 |
| `.modalidades h3`, `.quadro h3`, `.marcos h3`, `.exclusoes h3` | ficam | São **menores** que a regra global, e nenhuma gera h3 maior que h2 |

## D-009 — A regra de altura alcança todo `input` de uma linha

**Decisão.** `select,input:not([type$=box],[type=radio],[type=file]){height:2.5rem}`.

**Por que `$=box`.** A primeira versão escrevia o tipo da caixa de marcar por extenso, e a suíte
recusou: `test_seletor_de_identidade_nao_existe_com_a_configuracao_desligada` confere que essa palavra
não aparece em lugar nenhum da tela de identificação indisponível — e a folha vai no corpo. A folha
já contornava o mesmo guardião em `.escolha input`. O sufixo alcança só esse tipo entre os que os
templates usam.

**Por quê.** Enumerar os sete tipos da 8ª decisão recebida custaria o dobro de caracteres, e a lista
repetiria o defeito que a própria folha registra: "uma lista que enumera tipos esquece o tipo
seguinte". Os tipos que a negação alcança além dos sete — `password` e `url` — são campos de uma linha
e pedem a mesma altura. Não há `input` de envio, de cor ou de intervalo nos templates (levantado).

**Consequência aceita.** Os controles compactos — `.gerir-membro select` (36 px), o motivo da
reabertura e a busca da Retificação — passam a 40 px. A 8ª decisão recebida é "uma altura por folha",
e esses eram justamente as alturas que faziam a Comissão ter 35, 36 e 38 px na mesma tela.

## D-010 — O preenchimento de célula que ficou redundante sai

**Decisão.** Com o padrão em `.5rem .75rem`, as declarações idênticas de `.conferencia-lote th,td` e
`.distribuicao th,td` saem. Nenhuma das duas muda de desenho, e as duas juntas pagam quase metade do
lote.

Nenhuma tabela declarava preenchimento **menor** que o novo padrão: a regra "tabela com preenchimento
próprio menor fica como está" não tem, hoje, a quem se aplicar.

## D-011 — A coluna numérica é `td.numero`, dentro de `table.tabela`

**Decisão.** A classe de coluna numérica é a que já existia, `.tabela td.numero`. A tabela da ordem
calculada (`ordenacao.html`) passa a declarar `class="tabela"`, e a coluna "Pontuação combinada"
recebe `numero` no `th` e no `td`.

**Descartado — e medido.** Soltar o prefixo (`td.numero,th.numero`) era mais curto e alcançaria
`resultados.html`, que escreve `td.numero` fora de `.tabela` e hoje fica à esquerda. Mas `.tabela`
não tem outra regra na folha, e a guarda de classe órfã reprovou sete templates que a citam. Manter a
classe viva com uma regra de enfeite seria enganar a guarda. A `resultados.html` é tela de operação,
fora da lista desta feature, e fica registrada em `doc/achado-coluna-numerica-dos-resultados.md`.

**Fica como está.** `.distribuicao td.num`: renomear custaria caracteres no próprio HTML da página
sem margem. É a mesma regra com outro nome, e a unificação é registro.

## D-012 — O vão da seleção se resolve por `:has()`, sem tocar no template

**Decisão.** Na folha do portal, a grade larga de `.corpo-da-selecao` passa a ter duas versões: sem
sorteio, `"vagas cronograma" "documentos cronograma"`; com sorteio
(`:has(>.sorteio-da-selecao)`), a de antes.

**Por quê.** A seção do sorteio só é renderizada quando há sorteio, e o vão vinha de a área `sorteio`
continuar declarada: as Vagas ocupam duas linhas, e a altura delas se reparte entre a linha vazia do
sorteio e a do Cronograma — daí os 315 px antes do Cronograma.

**Degradação.** Navegador sem `:has()` fica com a disposição de antes, que é a de hoje.

## D-013 — As larguras do Requerimento vêm de `auto-fill`

**Decisão.** `.grade-de-campos` passa de `auto-fit` a `auto-fill`, e o campo `.largo` limita o
controle a `40rem`.

**Por quê.** `auto-fit` recolhe as colunas vazias, e um grupo de um campo só — o Telefone celular é o
único de "Contato" — esticava esse campo à linha inteira: 1.232 px. Com `auto-fill` as colunas vazias
continuam reservadas, e o campo fica com uma coluna (296 px, ~18,5 rem). O mesmo vale para a UF, que
fica sozinha na última linha do endereço — agora com a largura de uma coluna. Juntá-la à linha de
cima seria reorganizar a grade, e isso é o `achado-grade-dos-cartoes`.

## D-014 — Os campos da Comissão ganham tipo, e o identificador ganha teto próprio

**Decisão.** Os dois `input` do formulário de inclusão recebem `type="text"`; o Identificador
institucional recebe `max-width:20rem` num `{% block estilo_da_pagina %}` da `comissao.html`.

**Por quê.** Os dois campos **não declaravam tipo**, e por isso escapavam do teto
`.campo>input[type=text]{max-width:var(--leitura)}`: é daí que vinham os 1.190 px. Com o tipo, o Nome
fica com `--leitura` (68ch, ~42,8 rem — o "~40 rem" dos nomes). O identificador pede menos que isso,
e a regra dele vai para o estilo da página, que não viaja para a distribuição.

**Descartado.** `.campo.curto` no identificador: o teto dele é 10 rem, e um identificador de vinte
caracteres não caberia.

## D-015 — O Rótulo do Anexo fica como está; o Arquivo deixa de esticar

**Decisão.** `input[type="file"].arquivo` ganha `width:auto`, contra o `width:100%` que herdava de
`.campo input`. O Rótulo já tinha o teto de leitura (685 px, ~42,8 rem), dentro do "~40 rem" dos
nomes, e não muda.

## D-016 — O portal ganha a altura da Vitrine

**Decisão.** Os controles de `.campo` no portal recebem `height:2.625rem`, a mesma que a consulta da
Vitrine já declara, e pela mesma razão que o comentário dela registra.

## D-017 — "Guardar e continuar depois" é `.secundario`, e a guarda passa a varrer o portal

**Decisão.** A classe `secundario` no botão, e a guarda
`test_todo_botao_de_envio_declara_o_seu_peso` estendida aos templates do portal.

**Por quê.** Era o único botão de envio sem classe no portal (levantado), e a guarda que teria pego
só olhava a gestão.

## D-018 — As capturas saem do cliente de teste e do Chrome sem janela

**Decisão.** O HTML de cada tela é salvo pelo `django.test.Client`, identificado como `ana.gestora`,
e fotografado pelo Chrome em modo sem janela a 1280 px.

**Por quê.** A folha é inline, então o HTML salvo renderiza igual à página servida. E o painel do
navegador do aplicativo não salva arquivo.

## D-019 — A Matrículas tem o mesmo defeito do G1, e fica registrado

**Achado.** `matriculas.html` também põe `.resumo` numa `<section>`. É a mesma causa do G1, mas a
tela não está na lista da auditoria para este item, e a 1ª decisão recebida é explícita: o que não
está na lista é registro. Vai para `doc/achado-resumo-na-secao-das-matriculas.md`.

## D-020 — No histórico do Corte, a Proveniência vai para a grade de rótulo e valor

**Decisão.** Dos dois `dl.resumo` do histórico do Corte, "A regra que o governou" vira `ul.resumo`,
como a faixa do Corte — são os mesmos números. A "Proveniência" vai para `dl.participantes`, a grade
de rótulo e valor em duas colunas que a folha já tem.

**Por quê.** Os valores da Proveniência são nomes, datas, identificadores de 36 caracteres e um link —
nenhum número. No bloco da Convocação, cada um sairia em corpo de 1,25 rem, e um UUID nesse tamanho
atravessa a tela. O critério da 2ª decisão recebida — nenhum valor entre dois rótulos — vale do mesmo
jeito na grade: rótulo numa coluna, valor na outra, na mesma linha.

**O mesmo no histórico da Ocupação.** "Emitida em" e "Por" continuam no `dl.meta`; os quatro números
saem dele e vão para o `ul.resumo`.

## D-021 — A linha das Inscrições cai para uma linha só, salvo onde há a marca de CPF repetido

**Medida.** Depois do novo preenchimento, a linha das Inscrições do Edital 51/2026 tem 62,8 px — e
não os ≤ 45 que a 3ª decisão recebida fixou. Escondendo só a marca "⚠ CPF repetido neste Perfil",
ela tem **39,5 px**; com o preenchimento antigo e sem a marca, 68,4. O preenchimento é o que põe a
linha numa linha só, como a auditoria previu; o que ela não previu é que as cinco inscrições do
51/2026 no seed carregam a marca — as candidatas de demonstração compartilham o CPF —, e com ela as
sete colunas pedem 1.316 px numa tabela de 1.232.

**Decisão.** O item fica: ele entrega o que promete em toda linha sem a marca, e melhora a com a
marca. O critério é declarado **parcialmente atendido**, com as duas medidas, na verificação e no PR.
Atendê-lo por inteiro pede mexer na marca — texto ou posição —, e isso é mudar texto ou reorganizar a
tela, que esta feature não faz. Vai para `doc/achado-marca-de-cpf-repetido-alarga-a-lista.md`.

**Descartado.** Reduzir o preenchimento horizontal abaixo de `.75rem`: sete colunas vezes 8 px
somam 56, e faltam 84 — nem assim a linha com a marca cabe, e a 3ª decisão recebida fixou o valor.
