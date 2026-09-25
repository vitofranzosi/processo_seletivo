# Rastreabilidade — a hierarquia do detalhe do Perfil

**Feature**: `042-hierarquia-do-detalhe-do-perfil` · **Data**: 2026-09-21

Cada `FR-` e cada `SC-` desta spec, com onde a garantia mora. Onde a coluna diz **navegador**, a
propriedade é perceptiva e foi medida no percurso de [quickstart.md](./quickstart.md) — nenhum
teste a substitui, e é isso que a `SC-222` reconhece.

---

## Requisitos funcionais

| Requisito | Onde vive | Onde é cobrado |
|---|---|---|
| **FR-622** — `<details>` nativo, **zero** JavaScript | `_perfis_do_edital.html` | `test_visao_geral.py::test_t011_o_controle_tem_dois_rotulos_e_a_legenda_e_invisivel` (`"<script" not in corpo`) |
| **FR-623** — região filha recuada e **mais estreita**; parentesco preservado em viewport estreito | bloco `estilo_da_pagina` de `visao_geral.html` (régua, `padding-left`, consulta estreita) | `test_larguras.py::test_a_consulta_estreita_vence_a_regra_de_mesa_do_recuo`; medida no **navegador** — `747,7 px` contra `798,7 px` (**93,6 %**), e em 375 px recuo `9,6 px` com `scrollWidth == clientWidth` |
| **FR-624** — cabeçalho filho menos dominante | `.tabela-de-perfis thead th` (`.7rem`/`500`) | **navegador** — `11,2 px`/`500` contra `13,12 px`/`600` |
| **FR-625** — nome acessível presente e não desenhado | `<caption class="oculto">` em `_perfis_do_edital.html` | `test_t011…` (`'<caption class="oculto">' in corpo`); **navegador** — `position:absolute`, `clip-path:inset(50%)` |
| **FR-626** — código, localidade e reserva na **identidade**; ausência **é** a representação | `PerfilDaLinha.identidade_secundaria` em `visao_geral.py` | `test_visao_institucional.py::test_a_identidade_secundaria_junta_os_tres_por_ponto_medio`, `…_omite_o_que_nao_existe`, `test_a_ausencia_de_reserva_nao_produz_texto`, `test_sem_nenhum_dos_tres_a_identidade_secundaria_e_vazia`; `test_visao_geral.py::test_t009b_as_tres_especies_de_reserva_se_distinguem_na_identidade` |
| **FR-627** — uma coluna de identidade e **cinco** de dado | `_perfis_do_edital.html` | `test_visao_geral.py::test_t009_a_tabela_filha_tem_uma_coluna_de_identidade_e_cinco_de_dado`; `test_larguras.py::test_a_consulta_estreita_nao_alcanca_a_tabela_aninhada` — **em telefone a filha perdia duas colunas**, porque o seletor da consulta estreita era descendente e atravessava `<table>` dentro de `<table>`; `test_cabecalho_e_numero_dividem_a_borda_nas_duas_tabelas` — rótulo e número **na mesma borda**, nas duas tabelas |
| **FR-628** — atenção **uma vez por granularidade** | `Marca.rotulo` em `visao_geral.py`; `_perfis_do_edital.html` usa o rótulo, `_linha_do_edital.html` a mensagem | `test_visao_institucional.py::test_cada_especie_tem_rotulo_curto_distinto_da_mensagem`; `test_visao_geral.py::test_t010_a_mesma_frase_nao_aparece_nas_duas_granularidades` |
| **FR-629** — o controle nomeia **ação** e **quantidade**, e não é caixa solta | `<summary>` com `.ao-abrir`/`.ao-fechar` e marcador `::before` | `test_t011…` (os dois rótulos no documento); **navegador** — marcador `▸` fechado, girado 90° aberto |
| **FR-630** — critério separado de direção | `ORDENS` e `SENTIDOS_LEGIVEIS` em `visao_geral.py`; os dois `<select>` em `visao_geral.html` | `test_visao_geral.py::test_t012_os_rotulos_de_ordenacao_nao_embutem_direcao` |
| **FR-631** — a `SC-217` da `041` substituída **por escrito** | anotação em `specs/041-perfil-na-visao-institucional/spec.md` | leitura: a `SC-217` está riscada, cita o próprio texto e aponta para a `SC-224` |
| **FR-632** — grade **estável entre Editais**; texto secundário não dita largura | `<colgroup>` em `_perfis_do_edital.html`; `table-layout:fixed` e as seis proporções na folha | `test_larguras.py::test_a_grade_da_tabela_filha_e_declarada_e_fecha_em_cem`; `test_visao_geral.py::test_fr632_a_tabela_filha_declara_a_grade_e_nao_a_negocia`; **navegador** — as duas expansões em `[194, 90, 90, 112, 105, 157]` |
| **FR-633** — marca do Perfil **menos dominante** que a do Edital | `.tabela-de-perfis .marca` na folha | `test_larguras.py::test_a_marca_do_perfil_e_menor_que_a_do_edital` (comparação **numérica**); `test_visao_geral.py::test_fr633_a_marca_do_perfil_continua_sendo_texto` |

## Critérios de sucesso

| Critério | Como foi verificado |
|---|---|
| **SC-222** — continua-se percebendo a **mesma linha, aprofundada** | **Juízo humano**, passo 16 do quickstart. Nenhum teste a substitui; as três medidas abaixo são as consequências que a sustentam |
| **SC-223** — filha mais estreita, cabeçalho menor, e telefone sem rolagem lateral | **navegador**: `93,6 %` (era `98,0 %`), `11,2 px` contra `13,12 px` (era `12,16` contra `13,12`), e em 375 px `scrollWidth == clientWidth` com a filha rolando **dentro** da moldura |
| **SC-224** — seis colunas, nenhuma de reserva; espécie na identidade; sem reserva, nada escrito | `test_t009…` e `test_t009b…`; **navegador** — `DOC-INFO · Campus Serra · CR limitado a 6`, `TEC-LAB · Campus Vitória · CR ilimitado`, `TEC-EAD · Polo Serra` |
| **SC-225** — **zero** repetições da frase de atenção | `test_t010…`; **navegador** — Edital *"1 de 2 Perfis sem nenhuma inscrição."*, Perfil *"Sem procura"* |
| **SC-226** — **zero** JavaScript novo, e abre por teclado | `test_t011…` para o zero. O teclado é **nativo do `<details>`** e não foi exercitado por tecla injetada: o harness não dispara a ação padrão de `<summary>` nem no `<details>` da `040`, que esta feature não tocou. O que se conferiu é a estrutura que o produz — `tabIndex 0`, foco no `<summary>`, e nenhum JavaScript na página |
| **SC-227** — **zero** critérios que embutam direção | `test_t012…`; **navegador** — *Data do Edital · Vagas · Inscrições submetidas · Inscr./vaga*, com `ordem=`/`sentido=` intactos |
| **SC-228** — as larguras da tabela filha são **iguais** entre expansões | **navegador**: `[194, 90, 90, 112, 105, 157]` nas duas, contra `[179, 89, 83, 111, 192, 93]` e `[193, 102, 83, 118, 78, 173]` antes — nenhuma coluna coincidia |
| **SC-229** — a marca do Perfil é **menor** que a do Edital | `test_a_marca_do_perfil_e_menor_que_a_do_edital`; **navegador** — `11,52 px`/borda `2 px` contra `12,8 px`/borda `3 px` |

## Agrupamento e estrutura

| Decisão | Onde | Onde é cobrada |
|---|---|---|
| **`R-002`** — um `<tbody>` por Edital, e o caso vazio no seu grupo | `_linha_do_edital.html`, `visao_geral.html` | `test_visao_geral.py::test_t008_um_tbody_por_edital_e_o_caso_vazio_no_seu_grupo` |
| Orçamento de consulta **inalterado** | — | `tests/performance/test_visao_institucional.py`, sem mudança de número |
| Nenhum dado pessoal na expansão | — | `test_visao_geral.py::test_t16_nenhum_dado_pessoal_de_candidato_no_html` |

---

## Um defeito que esta feature encontrou e fechou

A sobrescrita de recuo para viewport estreito — `.expansao-do-edital>td{padding-left:.6rem}` —
nasceu **acima** da regra de mesa, no bloco das outras consultas da folha. Mesmo seletor, mesma
especificidade, e `@media` não acrescenta nenhuma: a regra de mesa, por vir depois, vencia em toda
largura. O recuo ficava em **40 px** no telefone. Não havia erro de sintaxe, aviso, nem teste
falhando — só apareceu na medição do passo 17. A regra mudou de lugar, e a **ordem** virou
guardião em `test_larguras.py::test_a_consulta_estreita_vence_a_regra_de_mesa_do_recuo`.

## E um segundo, achado ao medir o telefone com a grade já corrigida

A consulta estreita da `040` esconde a terceira, a sexta e a sétima coluna da tabela principal, e
estava escrita com **combinador descendente**. A tabela da expansão vive dentro de um `<td>` da
principal, de modo que o seletor a alcançava — e lá o terceiro e o sexto não são *Período* e *Em
preenchimento*, e sim **Submetidas** e **Atenção**. No telefone a região filha ficava com **três**
colunas onde a `FR-627` exige cinco, e perdia justamente a de atenção.

Nenhum teste via, e nenhum poderia: `display:none` não altera o HTML, de modo que toda asserção
sobre a marcação continuava verde. O seletor passou a `>`, e o guardião é sobre a **forma** dele.

## E um terceiro, apontado por quem usa a tela

Todo cabeçalho de coluna numérica estava alinhado à **esquerda** e todo número à **direita**, nas
duas tabelas. Como o cabeçalho seguinte começa logo depois, o número acabava mais perto do rótulo
da coluna vizinha do que do seu: medido, `Em preenchimento` punha `137 px` entre o começo de um e o
fim do outro.

A correção foi mover o **cabeçalho**, e não o número. Centralizar — a saída que primeiro ocorre —
teria custado o empilhamento dos dígitos pela casa das unidades, que é o que permite comparar
grandeza de relance e o que justifica a coluna ser uma coluna.

Não virou requisito novo, e a razão importa: **a convenção já era da casa**. `base.html` alinha à
direita `td.numero` *e* `th.numero`; a folha desta tela é que cobria só o `td`. O que faltava era
seguir o que o repositório já decidiu, e é isso que o guardião prende.

## E um quarto, que começou como pergunta sobre onde pôr um comentário

A marca de parcialidade era escrita por extenso ao lado do número — *"parcial — as inscrições ainda
estão abertas"* —, em prosa alinhada à direita ocupando **73 px** numa célula de 108. A pergunta
era se ela não pertencia à coluna *Atenção*. Não pertence: *Atenção* carrega **marcas**, que são
sinais de que algo pede ação, e parcialidade é ressalva sobre a **completude de uma medida**. Além
disso a ressalva precisa ficar colada ao número que qualifica, e há **dois** parciais na mesma
linha — em *Atenção* não daria para saber de qual se fala.

O que a pergunta descobriu foi melhor:

1. **O motivo era redundante por construção.** Existe **um** motivo de parcialidade nesta tela, e
   ele é atribuído exatamente quando o período está aberto — que é exatamente quando a coluna
   *Período de inscrições*, na mesma linha, escreve *"Inscrições abertas até DD/MM/AAAA"*.
2. **Pai e filha divergiam.** A tabela dos Perfis já imprimia só `parcial`, sem motivo, e ninguém
   havia decidido qual das duas estava certa.
3. **A razão nunca declarou a própria parcialidade** (`FR-595`). A derivação a marcava —
   `Numero.de(..., parcial=aberto)` — e **os dois templates descartavam a marca**. Um Edital com
   inscrições abertas mostrava a razão como número fechado.

O item 3 é o mais instrutivo: `tests/unit` afirmava `linha.submetidas.parcial` e passava, enquanto
a tela descartava a marca da razão. **Teste de modelo não vê template.** Por isso cada um dos dois
guardiões novos tem par — um em `tests/unit`, um em `tests/interface`.

A gramática da `040` foi emendada por escrito para admitir o motivo **na linha** em vez de colado
ao número; a emenda está na própria `040`, junto da tabela que ela altera.

**Uma medida que não se confirmou:** a linha **não** ficou mais baixa. Antes e depois, as três
linhas medem `140`, `149` e `140` px — quem as dimensiona é a primeira coluna, com o nome do
Processo quebrando em três linhas, e não a nota. O ganho é a redundância que saiu, a prosa
irregular que deixou de existir na célula numérica, e a razão que passou a dizer o que é.

## E um quinto, na barra de filtros — dois defeitos, uma pergunta

**O campo *Buscar* não estava menor: estava sem regra nenhuma.** `22 px` de altura, fonte de
`13,33 px` e borda `2px inset` — a folha do navegador — ao lado de selects de `41 px` e `16 px`. A
regra de campo da `base.html` enumera tipos, e `input[type=search]` não estava na lista. A `040`
trouxe o primeiro `type="search"` daquela folha.

O comentário imediatamente acima da regra já descrevia **o mesmo defeito, de outra vez**: *"a regra
cobria só `input[type=text]`, e `Ano` — que é `number` — ficava com a aparência padrão do
navegador: 22px de altura e fonte de 13px"*. A lista foi estendida para `number`, `date` e outros, e
`search` nunca entrou. `tel`, usado uma vez, estava na mesma situação e ninguém havia notado.

Por isso o guardião **varre os templates** em vez de conferir a lista contra si mesma: o tipo que
ninguém lembrou é exatamente o que uma lista escrita à mão não acusa. Verificado que ele morde —
retirando `search` ou `tel` da regra, ele nomeia o que falta.

Isto também explicava o rótulo *Buscar* parecer torto: a barra alinha por `flex-end`, de modo que
um controle `19 px` mais curto empurra o rótulo os mesmos `19 px` para baixo. Um sintoma, uma causa.

**E o checkbox estava desalinhado por regra própria.** `.filtro-de-atencao{align-self:center}`,
escrita na `040`, anulava o `align-items:flex-end` do formulário só para aquele item: todos os
demais terminavam em `87 px` e ele em `66`. Passou a `flex-end`, com `margin-bottom:0` e
`min-height` igual à do botão *Aplicar* — hoje os dois têm caixa idêntica, `51..87`, centro `69`.

**O que ficou, e por quê:** o campo de busca mede `39 px` contra os `41 px` dos selects. A diferença
é intrínseca — um `<select>` é mais alto que um `<input>` com o mesmo padding e a mesma fonte —, e
igualá-la exigiria cravar altura, que é a mesma espécie de decisão que este repositório já proíbe
para largura. Dois pixels, com as bases alinhadas em `87`: fica registrado, não corrigido.

### E o teto de 120.000 bytes mordeu pela terceira vez

A correção acima foi escrita com um comentário de CSS explicando por que a lista de tipos falha. A
suíte completa reprovou: a tela de distribuição fechou em **120.040 bytes** contra o teto de
**120.000** — quarenta bytes.

**Comentário de CSS viaja em toda página**, e esta folha é a base de toda a gestão. É a terceira vez
nesta linha de trabalho: a `040` estourou o mesmo teto em 3.533 bytes ao pôr a folha da Visão Geral
na base, e depois em 71 bytes com o comentário que explicava o `{% block %}` novo.

A saída é a mesma das duas primeiras: `{% comment %}` do Django, que o motor remove antes de
responder. A prosa continua no arquivo para quem lê o código, e custa zero na rede. Convertido o
bloco inteiro — inclusive a parte que já vinha da `FR-034` e que vinha viajando desde sempre —, a
tela voltou a caber.
