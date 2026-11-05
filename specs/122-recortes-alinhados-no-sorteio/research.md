# Research: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão

Medido em 05/11/2026 sobre a `main` em `de5df85c`. Cada item diz o que foi lido, a decisão e o que
se descartou. Os caminhos são relativos a `backend/processo_seletivo/`.

## R-1 — Onde o recorte é derivado hoje

Onze lugares respondem "quais recortes este marco tem" ou agem sobre um recorte sem perguntar.

| # | Lugar | O que faz hoje | Derivação |
|---|---|---|---|
| a | `editais/domain/recortes.py`, `recortes_do_perfil` | a derivação canônica: ampla + Modalidades, menos a apontada | **canônica** |
| b | `sorteios/application/previa.py`, `recortes_do_marco` | os recortes da tela do sorteio: ampla + **toda** Modalidade | própria |
| c | `sorteios/application/selectors.py`, `marcos_sorteados_em_todos_os_recortes` (`102`) | lê `b` | herda `b` |
| d | `interface/supervisao.py`, `listas_do_marco` | canônica, **exceto** no marco por sorteio, que lista toda Modalidade | mista |
| e | `interface/views.py`, `_destinos_do_marco` | um destino por ato vigente, rótulo fixo | nenhuma: lê atos |
| f | `interface/relatorio_do_edital.py`, linhas por lista | a união das listas dos atos e das publicações | nenhuma: lê atos |
| g | `sorteios/application/relacao.py`, `publicar_relacao` | congela a relação de qualquer `lista_id` com participante | não confere |
| h | `sorteios/application/sorteio.py`, `constituir_sorteio` | sorteia qualquer relação vigente | não confere |
| i | `divulgacao/application/publicar.py`, `publicar_resultado` | divulga qualquer ato vigente | não confere |
| j | `interface/acoes.py`, ações do ato; `templates/interface/sorteio.html`, link por recorte | oferecem divulgar o ato | herdam `b` e o ato |
| k | `interface/previa_do_sorteio.py`, frase da Modalidade apontada | diz que ela *"ganha uma lista própria no sorteio do certame"* | descreve `b` |

A classificação computada (`classificacao/application/calculo.py`, por `normalizar_recorte`), a
ocupação (`ocupacao/application/selectors.py`), a condução do marco (`interface/conducao_do_marco.py`)
e o resumo da página do Edital (`resumo_dos_marcos`) **já** usam a canônica.

- **Decisão**: `b` passa a separar **recortes operacionais**, lidos de `a`, de **registros
  excedentes**, lidos à parte para a seção de histórico (FR-3903). `c` e a tela herdam a separação.
  `d` perde o ramo do sorteio. `e` e `f` passam a filtrar pelos recortes de `a`. `g`, `h` e `i`
  ganham a recusa de R-4. `j` e `k` seguem a tela.
- **Descartado**: manter `b` e filtrar só na apresentação. A tela deixaria de oferecer, e o comando
  continuaria aceitando; é exatamente o que a 9ª decisão do usuário recusa.

## R-2 — O Publicador puro chega à condução do marco

- **Lido**: `interface/views.py`, `_marco_para_conduzir`. A porta é `pode_classificar or
  ator.can("resultado:publicar")` (FR-830 da `049`). O Publicador puro, com `resultado:publicar` e sem
  vínculo de comissão, **abre** a tela. Os testes de `tests/interface/test_destinos_do_edital.py` já
  identificam esse ator como `paula.publicadora` com o papel `publicador`.
- **Lacuna encontrada**: no quadro de recortes, a célula de divulgação (`_celula_da_publicacao`, em
  `interface/conducao_do_marco.py`) aponta para **"Resultados divulgados"**
  (`publicacoes-do-marco`), e não para a prévia do ato. O caminho até a prévia é o gesto em lote ou,
  hoje, o link por ato da página do Edital, que esta feature retira. Sem mudança, o Publicador puro
  chegaria ao quadro e não teria caminho por recorte até a prévia, e a SC-1167 falharia.
- **Decisão**: a célula aponta para a **prévia do ato vigente** quando o estado é *falta* ou
  *obsoleto* e o ator divulga; *feito* continua apontando para "Resultados divulgados". A rota e a
  autorização da prévia não mudam.
- **Verificação**: um teste com `paula.publicadora` percorre página do Edital → quadro → prévia de
  cada recorte operacional, em dois cliques (SC-1167).

## R-3 — O caminho único da página do Edital

- **Lido**: `_destinos_do_marco` recebe `atos_vigentes` e cria um destino por ato. `_marcos_publicados`
  já lê `resumo_dos_marcos`, com a contagem de recortes operacionais com ordem, sem consulta por marco.
- **Decisão**: um destino *"divulgar o resultado"* por marco, para o quadro de recortes com a âncora
  da divulgação, quando o ator divulga e `resumo["ordem"] > 0`. Isso dispensa `atos_vigentes_por_marco`
  na página, que **perde** uma consulta. "Conduzir o marco" continua; os dois levam à mesma tela, um
  ao topo e o outro à parte da divulgação (D-001).
- **Descartado**: rotular os links por recorte. Manteria N destinos na página, contra a 1ª decisão.

## R-4 — A recusa: uma função, três comandos

- **Lido**: os códigos de recusa do sorteio são em inglês e em `snake_case` (`relation_superseded`,
  `occurrence_not_declared`, `relation_would_be_empty`, este com 422). A normalização da `034`
  (`normalizar_recorte`) é da classificação, e transforma o apelido em ampla.
- **Decisão**: uma função em `editais/domain/recortes.py`, `exigir_recorte_operacional(conteudo, *,
  perfil_id, lista_id)`, que levanta `DomainError("list_is_general_competition_alias", <frase>, 422)`.
  Ela é chamada por `publicar_relacao` (sobre a versão relida dentro da trava), por `constituir_sorteio`
  (sobre a relação, na versão vigente) e por `publicar_resultado` (sobre o ato). A frase é uma só
  (D-003) e está em [contracts/recorte-excedente.md](contracts/recorte-excedente.md).
- **A emissão computada não muda.** Ela já normaliza; recusar ali quebraria a gramática que a `034`
  fixou (FR-3900).
- **Idempotência**: o pedido repetido devolve o desfecho anterior **antes** da recusa, porque
  `comando_de_comissao` responde `ctx.repetido` no início. Nenhuma mudança.
- **Descartado**: recusar na view. A porta do comando também é alcançada por formulário antigo.

## R-5 — O papel do recorte, e a origem do registro

- **Lido**: `AtoDeOrdenacao.versao` e `RelacaoDeHabilitados.versao` apontam para a `VersaoConsolidada`
  que citaram. `Sorteio` chega à versão pela relação, e `PublicacaoResultado` pelo ato.
  `VersaoConsolidada.source_publication` dá o número da Retificação que a produziu.
- **Decisão**: `papel_do_recorte(conteudo, *, perfil_id, lista_id)` em `editais/domain/recortes.py`,
  com três respostas: `OPERACIONAL`, `EXCEDENTE` e `AUSENTE` (Modalidade que não existe na versão).
  Um registro é excedente quando o papel **na vigente** é `EXCEDENTE` (FR-3911). A origem é
  - **nascido excedente**, quando o papel na versão do registro também é `EXCEDENTE`;
  - **tornado excedente**, quando era `OPERACIONAL`. A Retificação que o tornou é a primeira versão
    posterior à do registro em que o papel passou a `EXCEDENTE`, e o número vem dela.
- **Custo**: a origem só é composta na seção de histórico (FR-3903) e nas telas de um registro
  (FR-3904). São poucas linhas, e as versões do Edital se leem numa consulta só. Nenhuma superfície de
  listagem, nem a Supervisão, nem a página do Edital, paga por ela.
- **Descartado**: gravar o papel no registro (D-002).

## R-6 — A mudança de papel como causa de obsolescência

- **Lido**: `classificacao/application/selectors.py`, `estado_do_marco`, devolve `divergencias`
  nomeadas, com `tipo` e `descricao`. No ato de sorteio, `_estado_do_marco_sorteado` as compõe de
  `_divergencias_do_sorteio(vigente)`. O filtro barato `candidato_a_obsoleto` (Supervisão e condução)
  já admite todo ato cuja versão citada difere da vigente, e é o que acontece depois de uma
  Retificação.
- **Decisão**: uma divergência nova, `tipo="papel_do_recorte"`, com a frase *"o papel do recorte mudou
  na Retificação nº N"*. Ela entra quando o papel na versão do ato difere do papel na vigente **e** o
  papel na vigente é `OPERACIONAL` (FR-3912). Isso vale nos dois ramos, computado e sorteado. A
  publicabilidade (`divulgacao/domain/publicabilidade.aferir`) já recusa ato obsoleto, e a recusa
  passa a vir com essa causa. O caminho seguinte é a sucessão que já existe: relação nova, com motivo,
  sorteio novo e ato novo (D-004).
- **Cabe sem tabela** (FR-3914, Assumptions da spec): `divergencias` é composta, não gravada.

## R-7 — O relatório do Edital é a sexta superfície

- **Lido**: `interface/relatorio_do_edital.py` monta `listas_por_marco` e `atos_por_marco` a partir de
  `PublicacaoResultado` e `AtoDeOrdenacao`, e itera `sorted(listas | emitidas)`. O nome da linha vem de
  `_nome_da_lista(perfil, lista)`, que, para a lista da Modalidade apontada, devolve o nome dela, em
  geral *"Ampla Concorrência"*, ao lado da linha nula *"Ampla concorrência"*. `definitivo_em_todas`
  considera toda lista: um ato excedente não divulgado como definitivo impede o marco de aparecer como
  definitivo.
- **Decisão**: a FR-3916 foi acrescentada à spec. As linhas e o estado vêm dos recortes de `a`; a
  publicação excedente já feita aparece numa linha marcada como fora da operação atual e não entra em
  `definitivo_em_todas`.

## R-8 — A Supervisão

- **Lido**: `listas_do_marco` (`interface/supervisao.py`) tem o ramo do sorteio, e a docstring cita a
  decisão de escopo do sorteio da `034` como razão.
- **Decisão**: o ramo sai, e a função passa a devolver `recortes_do_perfil` para todo marco (D-007).
  Os três sinais (`UX-004`, `UX-065`, `UX-066`) deixam de ver o registro excedente sem mudança em cada
  um. A docstring passa a citar esta feature.

## R-9 — O que a mudança toca na suíte

- **Testes que mudam de expectativa**: `tests/interface/test_destinos_do_edital.py` espera a URL da
  prévia **na página do Edital**, e passa a esperar a do quadro, e a prévia a partir do quadro. Os
  testes do sorteio e da prévia do sorteio com a Modalidade apontada mudam, porque o bloco dela deixa de
  existir. O plano os localiza por `grep -rn "generalCompetitionModalityId" tests/` antes de mexer.
- **Orçamentos de consulta** com teste próprio: `test_conducao_do_marco.py`, `test_previa_do_sorteio.py`,
  os da Supervisão (`integration/supervisao/test_sinais.py`, `test_fronteira.py`) e o da página pública
  do sorteio (`portal/test_sorteio_na_pagina_do_edital.py`). A página do Edital **perde** uma consulta
  (R-3). A tela do sorteio ganha a leitura do histórico excedente, uma consulta por espécie, e o
  orçamento dela é refeito com a medição.
- **Vocabulário**: as frases novas da tela do sorteio e da prévia entram na lista literal de
  `test_vocabulario_da_composicao.py`, que não alcança tela nova sozinha (memória do projeto).
- **Inventário de negativas** (`033`): nenhuma view nova levanta `Http404`; a recusa é `DomainError`
  422, que não entra no inventário.

## R-10 — O levantamento do acervo na instalação do Cefor

- **Exigência**: a 13ª decisão do usuário e as Assumptions da spec. Ele é **só de leitura** e precede
  a implementação.
- **Situação em 05/11/2026**: **não feito.** Esta sessão não tem acesso ao banco da instalação
  (`gps.cefor.cefetes.br`). O único dado é o que as capturas de tela do usuário mostram no Edital
  35/2026: ao menos um ato excedente, e um resumo com uma publicação **em recorte operacional**
  (o resumo não conta o excedente). Se o ato excedente foi divulgado, não se sabe.
- **Decisão**: o roteiro está em [quickstart.md](quickstart.md), passo 0. Ele roda no `manage.py
  shell` da instalação, numa transação marcada como só de leitura, e imprime, por Edital e marco,
  quantas relações, sorteios, atos e publicações excedentes existem, separando os nascidos dos
  tornados. **Se houver publicação excedente, os números vão ao usuário**, que decide sobre a
  explicação no portal. O escopo não muda por si (FR-3915).

## R-11 — A matriz dos casos temporais

Cada linha é um teste de integração contra PostgreSQL. "AC" é a Modalidade que o Edital chama de
ampla; "X" é outra Modalidade de reserva.

| Caso | Antes | Retificação | O que se verifica |
|---|---|---|---|
| T1 | sem apontamento; AC operacional, com relação, sorteio, ato e publicação | passa a apontar AC | AC sai do quadro e da Supervisão; registros na seção de histórico, com a frase de **tornado**, nomeando a Retificação; divulgar de novo é recusado; publicação e verificador intactos; o relatório marca a publicação |
| T2 | aponta AC; registros de AC **nascidos** excedentes | retira o apontamento | AC volta ao quadro; o ato antigo aparece **obsoleto**, com a causa `papel_do_recorte`; a prévia recusa divulgá-lo; congelar relação nova de AC é aceito, com motivo |
| T3 | aponta AC; registros nascidos em AC; X operacional, com ato | passa a apontar X | AC como em T2; X como em T1 |
| T4 | aponta AC; registros nascidos em AC | Retificação que não toca o apontamento | nada muda nos registros; a frase continua a de **nascido** |
| T5 | sem apontamento; ato de AC operacional | aponta AC, depois retira, depois aponta de novo | o ato de AC continua com a frase de **tornado**, e a Retificação nomeada é a primeira que o tornou excedente |
| T6 | aponta AC; relação de AC congelada, **sem sorteio** | nenhuma | constituir o sorteio é recusado; a relação está no histórico com o impedimento |
| T7 | qualquer | qualquer | a frase de origem é composta da versão do registro: trocar a vigente não muda a frase de um registro nascido |
