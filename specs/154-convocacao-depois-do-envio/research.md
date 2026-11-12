# Research: 154 — a convocação depois do envio, e um nome só para o reenviado

Medido na `main` em `d1ec1e0a` (11/11/2026, com a spec do PR #479), **depois** do PR #477, que já mexeu em
`interface/conducao_da_convocacao.py`, `interface/andamento.py`, `interface/views.py` e
`interface/templates/interface/convocacao.html`. Nenhum item abaixo reabre decisão da spec: as D-001
a D-006 e as oito decisões dos achados são do usuário. Os `R-` registram **onde** e **como** cada
requisito se cumpre no código de hoje, e o que o plano escolheu dentro da latitude que a spec deu.

## R-001 — A providência pendente mora na projeção da `118`

**Decisão.** `Obrigacoes` (em `portal/obrigacoes.py`) ganha a propriedade `providencia_pendente`:
`self.aberta and bool(self.tarefas)`. As `tarefas` já são exatamente as da FR-3726 da `118` —
documento obrigatório *a corrigir*, *a enviar* e o Requerimento *a preencher*, nessa ordem —, e já
deixam de fora opcional, facultativo pendente, item com a comissão e conferido (FR-6200, D-001).

**Por quê.** A spec pede que a página nunca diga *"Acompanhe sua convocação"* e, logo abaixo, uma
tarefa (D-001). Ler da mesma tupla que monta o resumo *"Você ainda precisa…"* e a ação *"Ver o que
preciso fazer"* torna isso verdade por construção.

**Descartado:** derivar no template (`{% if o.tarefas %}` em três lugares) ou na view. A regra
apareceria três vezes, e a `118` já paga o preço de ter a projeção como fonte única (FR-3751).

## R-002 — A frase da conferência terminada, e uma conclusão só para três lugares

**Decisão.** `Obrigacoes` ganha `conferencia_terminada`: chamada aberta, sem tarefa, com **ao menos
um** obrigatório, e **todo** obrigatório na categoria `CONFERIDO` (*conforme* ou *não se aplica*). Os
opcionais não entram na conta (D-002). `_aberta` passa a gravar em `frase_de_conclusao` a
`FRASE_DA_CONFERENCIA_TERMINADA` quando ela vale, e a `FRASE_DE_CONCLUSAO` nos outros casos sem
tarefa. Os três consumidores passam a ler esse campo, e não a constante:

| Consumidor | Hoje | Depois |
|---|---|---|
| `Obrigacoes.resumo_do_que_falta` (convocação, FR-3862 da `121`) | `frase_das_tarefas(...) or FRASE_DE_CONCLUSAO` | `... or self.frase_de_conclusao` |
| `_acao_das_obrigacoes` (acompanhamento, linha 5 da FR-3730 da `118`) | `conclusao=obrigacoes.frase_de_conclusao` | igual — já lê o campo |
| `confirmacao_do_envio` (volta do envio, FR-3870 da `121`) | `conclusao=FRASE_DE_CONCLUSAO` | `conclusao=projecao.frase_de_conclusao` |

**Por quê a confirmação entra.** Em Tc a pessoa ainda pode enviar um opcional (o caso-limite *Tc com
um opcional enviado*). A volta desse envio diria hoje *"A comissão ainda vai concluir a análise."*, e
a SC-2003 exige que essa frase não apareça em **nenhum** cenário Tc.

**Os casos em que ela não vale**, cada um com teste: obrigatório com a comissão (recebido,
aproveitado sem conferência, reenviado); chamada só com facultativo (não há obrigatório); chamada
que pede só o Requerimento (não há projeção — R-005).

## R-003 — O título

**Decisão.** Constante nova `TITULO_SEM_PROVIDENCIA = "Acompanhe sua convocação"`. `Obrigacoes.titulo`
devolve ela quando `self.aberta and not self.providencia_pendente`, e `TITULOS[self.momento]` nos
demais. O dicionário `TITULOS` continua com as quatro chaves de momento: o título novo não é momento
novo — é a linha da FR-3858 da `121` dividida (FR-6202), e o momento continua `ABERTA` para tudo o
que dele depende (etapa, cartão do prazo, ressalva, andamento).

**A ida e a volta** (FR-6203) não pedem código próprio: a confirmação do envio é renderizada sobre a
projeção **depois** do envio (R-006 da `121`), e a pendência nova recalcula as tarefas na leitura
seguinte.

## R-004 — A advertência, separada do prazo

Hoje a advertência sai em três lugares, e a condição é a do prazo:

| Onde | Condição hoje | Condição depois (FR-6209) |
|---|---|---|
| `portal/templates/portal/_chamada_da_convocacao.html`, `{% if o.prazo %}` | prazo correndo | `{% if o.cabe_a_consequencia %}` |
| `portal/situacao.py`, `_acao_das_obrigacoes` | vencimento registrado e prazo iniciado | o mesmo **e** `obrigacoes.providencia_pendente` |
| `portal/situacao.py`, `_acao_da_convocacao` (sem documento) | vencimento, prazo correndo, Processo não encerrado | o mesmo **e** `providencia_pendente_sem_documento(politica)` (R-005) |

**Decisão.** `Obrigacoes.cabe_a_consequencia = self.aberta and bool(self.prazo) and
self.providencia_pendente`. `self.prazo` já é vazio com o prazo não iniciado (comunicação não
enviada) e sem vencimento (FR-3749 da `118`), que são as outras três condições da FR-1177 da `063`.

**O prazo não muda de condição** (FR-6208): o cartão do prazo continua `Obrigacoes.cartao`, e o
prazo do acompanhamento continua o `prazo=` de `_acao_das_obrigacoes`. Os dois testes da SC-2002
prendem justamente que eles aparecem **sem** a advertência.

**A ressalva fica onde está** (FR-6210): `<p class="ressalva">` não tem condição nova.

**A constante continua em `portal/situacao.py`.** A FR-1177 da `063` lista as frases de consequência
"estas duas, e nenhuma outra" num lugar só (`CONSEQUENCIAS`); a projeção só diz se cabe.

## R-005 — A chamada que não pede documento (D-006)

**Achado do plano.** O chamado `"conferir"` do Requerimento não quer dizer "pedido nesta chamada":
`_politica_do_requerimento` (`portal/views.py`) devolve `"conferir"` para todo Requerimento enviado,
inclusive o do Edital que o pede **na inscrição**. Nesse caso a chamada não pede nada pelo portal, e
a D-006 manda manter o comportamento de hoje.

**Decisão.** Função pura nova em `portal/obrigacoes.py`:

```python
def providencia_pendente_sem_documento(disponibilidade):
    """FR-6201 (D-006): só o Requerimento pedido nesta chamada, e já enviado, a desfaz."""
    return not (requerimento_na_chamada(disponibilidade) and disponibilidade.enviado)
```

`requerimento_na_chamada` já existe (exigido e momento *na convocação*), e `Disponibilidade.enviado`
é o mesmo campo que `estado_do_requerimento` lê. Ela é chamada em dois pontos, sobre a política que a
tela já leu, sem consulta nova:

- `portal/views.py`, `_chamada_da_tela`, ramo sem projeção: com `momento == ABERTA` e sem
  providência, o título é `TITULO_SEM_PROVIDENCIA`;
- `portal/situacao.py`, `_acao_da_convocacao`: a `consequencia` só com providência.

**A página da convocação sem documento não ganha a advertência** (D-007, decisão do usuário depois
da análise): ela nunca a mostrou, porque o parcial da chamada só a põe com a projeção. A condição
nova da advertência, nesse ramo, vale só para o acompanhamento (`_acao_da_convocacao`).

O bloco *"O que fazer — Siga as instruções do Edital…"* da tela sem documento e o link *"Conferir o
Requerimento de Matrícula enviado"* não mudam (FR-6201: "a ação e o link de hoje… não mudam"). A
frase da conferência terminada não existe nesse ramo, porque ele não tem projeção (FR-6205).

## R-006 — Um nome, uma fonte

**Decisão.** Módulo novo `convocacao/domain/vocabulario_dos_documentos.py`, ao lado de
`vocabulario_do_canal.py`, com:

- `REENVIADO = "Reenviado — aguardando nova conferência"` — o rótulo (FR-6211);
- `reenviado_em_frase()` → `"reenviado — aguardando nova conferência"` — dentro de frase, minúscula;
- `reenviados(n)` → `"1 reenviado — aguardando nova conferência"`, `"2 reenviados — aguardando nova
  conferência"` — a contagem, sem "(s)" (D-004).

O portal (`obrigacoes.py`), a gestão (`views.py`, `conducao_da_convocacao.py`, os dois templates por
contexto) e os avisos (`pendencias.py`) leem dali. A SC-2004 ("idêntico letra a letra") vira um
teste de identidade sobre uma constante, e não seis comparações de texto.

**O travessão é U+2014** (—), com espaço dos dois lados, como na spec. O teste prende o caractere,
porque um hífen ou um meia-risca passariam no olho.

**Descartado:** `convocacao/domain/nomes.py`. Ele guarda identificadores, e nenhum texto de tela; o
precedente para texto do domínio é `vocabulario_do_canal.py`.

## R-007 — O identificador `ITEM_COMPLEMENTADO` fica

A FR-6211 deixa a escolha à implementação. **Fica**, e a chave `"complementados"` das contagens da
`115` também. O estado é derivado e não está gravado, de modo que renomear não pediria migration;
mas tocaria `convocacao/domain/documentos.py`, `convocacao/application/documentos.py`, as
comparações `lido.estado == "COMPLEMENTADO"` dos templates e a `134` — e
`convocacao/application/documentos.py` é arquivo que o plano da `152` (PR #480) altera. A spec
muda texto; o identificador não é texto de tela.

## R-008 — As contagens da gestão (D-004)

| Onde | Hoje | Depois |
|---|---|---|
| `interface/templates/interface/convocacao_documentos.html`, resumo *Documentos pedidos nesta convocação* | `<strong>N</strong>Reenviado{{ pluralize }}, a conferir de novo` | a contagem pelo filtro novo `reenviados` (plano, §4), que lê `vocabulario_dos_documentos.reenviados(n)` |
| `interface/templates/interface/convocacao.html`, linha documental do cartão (FR-3607 da `115`) | `· N complementado{{ pluralize }}` | `· 1 reenviado — aguardando nova conferência` / `· N reenviados — …` |

**A segunda linha não estava na tabela de impacto da spec**, e é a "contagem da condução" que a
FR-6212 e a revisão da FR-3607 nomeiam. Sem ela o achado 23 voltaria com um quarto nome
(*"complementado"*), que nem está na lista da FR-6214 — por isso o teste de vocabulário prende também
a palavra *complementad* no texto visível dessas duas telas.

**A "ordem da condução" não tem texto.** `ORDEM_DOCUMENTAL` (`interface/views.py`) ordena pelos
estados da FR-3591 da `115`, em que o reenviado já é *para conferir*; nenhum rótulo diz
*complementado* ali. A FR-6212 se cumpre sem mudança nesse ponto, e o plano registra isso para que a
implementação não o procure.

## R-009 — O passo da chamada e a explicação do reenvio

**O passo** (`conducao_da_convocacao.py`, código `REENVIADO`, FR-5011 da `143` revista):

- hoje: *"Conferir de novo: o candidato reenviou 1 documento que estava pendente."*
- depois: *"Conferir de novo: 1 documento reenviado — aguardando nova conferência."* e, com dois,
  *"Conferir de novo: 2 documentos reenviados — aguardando nova conferência."*

O código do passo, o tom e a ação (`CONFERIR`) não mudam. A forma *"documento reenviado — aguardando
nova conferência"* é a da FR-5011 revista pela spec; o "1"/"2" à frente é o que o passo já dizia.

**A explicação** (`SituacaoDoAviso.frase_da_pendencia`), que aparece na linha do aviso do cartão e da
página de documentos:

- hoje: *"O candidato reenviou o documento pendente em ‹data›; a nova conferência está por fazer."*
- depois: *"O candidato reenviou o documento pendente em ‹data›."*

A FR-6212 permite ao passo seguir com "a explicação de quem reenviou e quando, desde que nenhuma
delas dê outro nome ao estado". *"A nova conferência está por fazer"* é uma paráfrase do estado, e
fica logo abaixo do passo que já o nomeia. Sai a paráfrase, ficam quem e quando. **É escolha do
plano dentro da latitude da FR-6212**, e não decisão nova; se o usuário preferir manter a frase
inteira, a mudança é de uma linha e não toca teste de outro requisito.

## R-010 — O rótulo do item na página de documentos

`ROTULO_DO_ITEM["COMPLEMENTADO"]` (`interface/views.py`) passa a `vocabulario_dos_documentos.REENVIADO`.
O "*Conferir a versão N*" do `<summary>` e a abertura automática do bloco de conferência para o
reenviado continuam (`convocacao_documentos.html`, as comparações com `"COMPLEMENTADO"` ficam por
R-007).

## R-011 — A exclusão do aviso de pendência e o que já foi gravado

`avisos/application/pendencias.py`, `COMPLEMENTADA` passa a `"documento " +
vocabulario_dos_documentos.reenviado_em_frase()`, isto é, *"documento reenviado — aguardando nova
conferência"* (FR-4607 da `134`, revista).

**Onde esse texto é gravado.** No gesto do aviso, `auditar(...)` grava o motivo **em texto** duas
vezes: no `reason` (*"fora: documento reenviado, aguardando conferência: 1"*) e no `detalhe`
(`exclusoes: [{"motivo": …, "quantas": …}]`). Os registros já feitos ficam com o texto do dia
(FR-6215, SC-2005), como manda a Constituição.

**Nada lê esse texto de volta.** `COMPLEMENTADA` só é comparada em memória
(`motivo_para_nao_enviar`, que a traduz para `SEM_PENDENCIA`) e na prévia por chamada, recalculada a
cada leitura. A implementação confere isso por busca no código antes de mudar a constante — se algum
leitor da trilha comparasse o motivo gravado com a constante, um aviso antigo deixaria de ser
reconhecido, e a mudança precisaria de um alias, e não de troca.

## R-012 — O cartão do portal (D-003, D-005) e o selo

`texto_do_item`, ramo `ITEM_COMPLEMENTADO`:

| Momento | Hoje | Depois |
|---|---|---|
| `ABERTA` e `ENCERRADA_PELO_PRAZO` | *"Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida. A comissão vai conferir."* | *"Reenviado — aguardando nova conferência. Novo arquivo recebido em ‹data›, às ‹hora›, depois da correção pedida."* |
| `ENCERRADA_PELO_PROCESSO` | *"Novo arquivo recebido em ‹data›; não foi conferido antes do encerramento do Processo."* | *"Reenviado em ‹data›; não foi conferido antes do encerramento do Processo."* |
| `DECIDIDA` | *"Novo arquivo enviado em ‹data›; não foi conferido antes do resultado."* | *"Reenviado em ‹data›; não foi conferido antes do resultado."* |

O ramo de hoje já cai no texto da coluna *aberta* com o prazo vencido, que é o que a D-005 manda
manter (*"o vencimento do prazo, sozinho, mantém 'aguardando'"*): o teste prende isso, e não o
código.

**O selo fica.** O cartão do reenviado mostra hoje o selo *"Aguardando conferência"* (aberta e
encerrada pelo prazo) ou *"Não conferido"* (Processo encerrado e decidida), o mesmo do recebido. O
selo é a **categoria** *com a comissão* da FR-3744 da `118`, e não o nome do estado: a spec não o
revê, e a lista da FR-6214 não o inclui. Registrado aqui porque, lido ao lado do texto novo, o cartão
diz *"Aguardando conferência"* e *"Reenviado — aguardando nova conferência"*; se o usuário achar
redundante, é pergunta para outra revisão, e não escopo desta.

## R-013 — As varreduras

- **FR-6214** (nomes antigos), em duas camadas:
  - **estática**: um segundo dicionário em `tests/test_vocabulario_dos_documentos_da_convocacao.py`,
    `NOMES_ANTIGOS_DO_REENVIADO`, com os cinco nomes literais da FR-6214, aplicado à lista `DA_115`
    **mais** `interface/conducao_da_convocacao.py`, `interface/views.py` e
    `avisos/application/pendencias.py`. `visivel()` já tira comentário e docstring (FR-6214:
    "comentário e identificador interno não contam"), e nenhum dos cinco casa com identificador;
  - **renderizada**: *complementad* (o quarto nome da R-008) não entra na varredura estática,
    porque o identificador `"COMPLEMENTADO"` aparece nas condições dos templates da gestão e
    reprovaria o que a FR-6214 permite. Ele é conferido no HTML **renderizado** da página de
    documentos, da condução e do cartão do portal, com um item reenviado.
- **FR-6207** (falsas conclusões): **não** é varredura estática. `situacao.py` diz *"Vaga aceita"* e
  a frase do aceite, legítimas com desfecho; uma busca no arquivo inteiro reprovaria o que a spec
  permite. A regra vira teste sobre a página renderizada, cenário a cenário, só sem desfecho
  (SC-2003): `aprovad`, `aceit`, `deferid`, `concluíd`, `tudo certo`, `pronto`/`pronta`, `enviou
  tudo`, com fronteira de palavra — *"concluir a análise"* da frase de conclusão é verbo, e não
  *concluído*.
- **A marca visual do conferido** (FR-6207, segunda frase): o selo `conferido` só sai da categoria
  `CONFERIDO` (`_selos`); o teste prende que nenhum cartão recebido, aproveitado ou reenviado tem
  a classe `selo-conferido` (ou a que a folha usar), e que o `<h1>` não ganha classe nova.

## R-014 — Os testes que afirmam o texto de hoje

Busca por *"Você foi convocado!"*, *"Complementado, aguardando"*, *"a conferir de novo"*,
*"reenviado, aguardando conferência"*, *"depois da correção pedida"*, a advertência e a frase de
conclusão, em `backend/tests/`, na `main` em `ef568113`:

| Arquivo | O que conferir |
|---|---|
| `tests/unit/portal/test_obrigacoes_da_convocacao.py` | título, conclusão, texto do complementado; os cenários com tarefa ficam |
| `tests/unit/portal/test_situacao_da_inscricao.py` | `consequencia` nas duas montagens |
| `tests/portal/test_acompanhamento_pela_situacao.py` | a advertência no acompanhamento (FR-1177 da `063`) |
| `tests/interface/test_portal_convocacao.py` | título e advertência na página |
| `tests/interface/test_portal_documentos_da_convocacao.py` | texto do cartão do reenviado |
| `tests/interface/test_portal_jornada_consolidada.py` | conclusão e advertência por cenário da `118` |
| `tests/integration/portal/test_destino_da_convocacao.py` | título na chegada |
| `tests/integration/convocacao/test_visibilidade_ao_candidato.py` | texto do reenviado no portal |
| `tests/integration/avisos/test_aviso_de_pendencia.py` | a exclusão `COMPLEMENTADA` |
| `tests/unit/interface/test_conducao_da_convocacao.py` | frase do passo `REENVIADO` e `frase_da_pendencia` |
| `tests/integration/treinamento/test_convocacao_pelas_perguntas.py` | a frase do passo `REENVIADO` no cartão, e *"reenviou o documento pendente em"* — esta continua |
| `tests/navegador/test_jornada_da_convocacao_121.py`, `tests/navegador/test_jornada_dos_documentos_da_convocacao.py` | os textos nos passeios |
| `tests/unit/convocacao/test_escolha_da_mensagem.py` | **só conferir**: a mensagem não muda (fora do escopo), e o achado da busca deve ser o título da mensagem, e não o da tela |

Regra para cada um: o caso que monta cenário **com** tarefa continua afirmando *"Você foi
convocado!"* e a advertência; o que monta cenário sem tarefa passa a afirmar o novo. Nenhum teste
é apagado: o que muda de expectativa ganha o requisito da `154` no nome ou no docstring.

## R-015 — Onde esta spec cruza com as que planejam em paralelo

| Arquivo | `154` (este plano) | `152` (PR #480, plano) | `153` (spec, #476) | `150` (spec) |
|---|---|---|---|---|
| `interface/conducao_da_convocacao.py` | ramo `REENVIADO` de `passo_da_chamada`; `frase_da_pendencia` | frase do passo vencido sem apresentação | — | — |
| `interface/views.py` | só `ROTULO_DO_ITEM` | `convocar_view`, `emitir`/`continuar_corte_view`, `desfechar_view` | condução da formalização (a confirmar no plano dela) | — |
| `interface/templates/interface/convocacao.html` | só a contagem da linha documental | cartão, desfecho, conferência antes de convocar | — | — |
| `convocacao/application/documentos.py` | **nada** (R-007) | motivos do atalho, apresentação nesta chamada | — | — |
| `portal/obrigacoes.py`, `confirmacao_do_envio` | a conclusão lida da projeção (R-002) | — | — | a confirmação de vários envios (FR-3870 da `121`, revista) |

As regiões não se sobrepõem, e o conflito esperado é textual e pequeno: quem entrar depois refaz o
merge. **O ponto que pede atenção é a `150`**: quando ela for implementada, a confirmação de N
envios precisa usar a mesma `projecao.frase_de_conclusao` deste plano, ou Tc volta a dizer *"ainda
vai concluir a análise"* depois de um envio múltiplo de opcionais. Isso vai para o plano dela como
nota, e não para o escopo desta.

## R-016 — Sem consulta nova

Tudo sai do que as telas já leem: a projeção (`tarefas`, `itens`, `totais`) e a `Disponibilidade` do
Requerimento, que viaja com ela (FR-3725 da `118`). Os guardiões de orçamento de consulta das telas
do portal e da condução (`tests/performance/`) não devem mudar de número; se mudarem, é defeito do
desenho, e não do teto.
