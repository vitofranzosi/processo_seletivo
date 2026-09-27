# Research — 048 · A Retificação acrescenta o que o contrato já permite

**Spec**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · Conferido contra a `main` em `717eb0c`.

As decisões de domínio estão na spec (`D-001` a `D-004`). Aqui ficam as de desenho, cada uma com a
alternativa descartada.

---

## R-1 — A guarda da janela mora no ato, e não na reprodução

**Decisão**: a guarda de conteúdo desta feature — a janela que nasce sem admitir recurso (`FR-787`) —
fica numa função de domínio nova de `publicacoes/domain/changes.py`, que compara o conteúdo **antes**
e **depois** do ato. Ela é chamada pela aplicação da Retificação em três pontos, e só neles:
- `_apply_declared_changes`, na elaboração e na edição;
- `advertencias_do_ato`, sem recusar: para mostrar o problema cedo;
- `publish_retification`, depois do `apply_changes` da linha 690.

**Por que não dentro de `apply_change`**, que é onde as recusas de hoje moram: `apply_changes` também é
o motor de `consolidation.consolidate`, que **reproduz** atos já publicados para materializar versões
(`retificacoes.py:616-651`). Uma guarda nova ali passaria a julgar atos que foram válidos quando
praticados. Se algum ato de produção já fez nascer, pela API, uma janela que não admite recurso, a
guarda recusaria a própria história, e toda Retificação futura daquele Edital. A Constituição
diz que a publicação anterior não se reescreve, e a leitura dela também não pode passar a falhar.

**Por que comparar antes e depois, e não olhar cada alteração**: a verificação por alteração se
contorna com `REMOVE` seguido de `ADD` no mesmo ato. `REMOVE` apaga a chave, e o `ADD` seguinte parece
nascimento. A comparação do conteúdo resultante com o de partida resolve: para cada `appealWindow`
ausente no início e presente no fim, `admits` tem de ser verdadeiro. A janela que já existia e é
alterada segue a regra de hoje.

**Uma guarda genérica, retirada.** A primeira redação comparava também todo campo não retificável de
toda entidade presente antes e depois, fechando a troca por objeto inteiro pela API. O parecer de 26/09
a tirou do escopo, porque é porta anterior e não nasceu dos achados da auditoria (achado A-6 da spec). O
lugar que este `R-1` decide continua valendo para ela, se um dia for tratada.

**Descartadas**:
- Guarda dentro de `apply_change`: julga a história (acima).
- Guarda só na tela: a tela nem oferece *"não admite"* (`R-2`); a guarda existe para a API.

**A recusa** usa `CampoNaoRetificavel`, que `_recusa_de_caminho` já traduz para `invalid_change`/422,
com a razão da `D-003`. Nenhum mapeamento novo.

---

## R-2 — Os objetos que nascem: uma lista de nascimento por objeto, conferida contra o contrato

**Decisão**: cada objeto que pode nascer ganha, em `interface/retificacao.py`, a lista dos campos que a
tela oferece **quando ele está ausente**. `campos_editaveis` escolhe entre a lista de alteração (objeto
existente) e a de nascimento (objeto ausente), e o mecanismo `nascendo` de `diferencas` já monta o
objeto inteiro num `REPLACE` só.

| Objeto | Existente: oferece | Ausente: oferece | Complemento fixo no nascimento |
|---|---|---|---|
| `drawMethod` | os dez | os dez (inalterado) | — |
| `vacancyReversion` | `kind` | `kind` — a mesma lista | — |
| `appealWindow` | `admits`, `durationDays`, `unit` | só `durationDays` | `admits: true`, `unit: DIAS_CORRIDOS` |
| `cutRule` | `targetCount`, `surplusCount`, `tieOutcome` | os seis | — |

**A janela nasce sem booleano, e isso resolve duas coisas.** O controle booleano da tela é um `select`
com *"Não"* pré-selecionado (`_retificacao_linha.html:50-53`). Oferecido para objeto ausente, ele seria
enviado sempre, `_declarou_algo` contaria `False` como declaração (`retificacao.py:523-527`), e **toda**
Retificação de Edital com marco sem janela faria nascer uma janela *"não admite"* sem ninguém pedir. É o
defeito que a `FR-785` e a `SC-294` proíbem. Como a `D-003` só deixa nascer a janela que concede, a
pergunta *"admite?"* não tem outra resposta, e a tela não a faz: pede o prazo e completa o resto.

**A regra de corte nasce com os seis campos**, e três deles são não retificáveis. A guarda de carga
(`_conferir_que_nada_se_oferece_sem_decisao`) recusa, com razão, campo não retificável nas listas de
alteração. As listas de nascimento ficam num registro próprio, e a guarda ganha uma segunda
conferência (`FR-803`): toda lista de nascimento aponta objeto que `PODE_PASSAR_A_EXISTIR` declara
`True`, e todo campo dela está no contrato. É a decisão declarada que a `FR-803` pede, e não uma
exceção silenciosa.

**Vocabulários do corte**: `faixa.ESPECIES_DE_ALVO`, `DESFECHOS_DE_EMPATE`, `POLITICAS_DE_CONTINUACAO` e
`SEM_ETAPA_GOVERNADA` (`classificacao/domain/faixa.py:21-41`), com os rótulos que a composição já usa
no cartão do marco. A Etapa governada é escolha entre as Etapas do Edital e *"não governa Etapa"*,
conferida no servidor contra o conteúdo vigente, como já se faz com as referências.

**Descartadas**:
- Oferecer as listas de alteração sempre, como o método: o corte nasceria sem espécie de alvo, sem Etapa
  e sem continuação, e seria recusado sempre; a janela cairia no defeito do booleano.
- Booleano de três estados para `admits`: resolve o defeito e pergunta algo cuja única resposta aceita
  é *"sim"*.
- Um fragmento *"acrescentar regra de corte"* como os de coleção: o corte não é item de coleção, é
  objeto do marco, e o mecanismo de nascimento já existe para isso.

---

## R-3 — A guarda do corte é da aplicação, e consulta o seletor que já existe

**Decisão**: uma função em `publicacoes/application/retificacoes.py` que, para cada marco com
`cutRule` ausente na base e presente no conteúdo resultante, lê `faixa.etapa_governada(regra)`. Se ela
aponta uma Etapa e `resultados.application.selectors.ha_resultado_em(edital=, etapa_id=)` responde
`True`, a função recusa com `DomainError`, e a recusa nomeia o marco e a Etapa. Ela é chamada em
`_apply_declared_changes`, que passa a receber o `edital`, e em `publish_retification`, sob o
`select_for_update` que já tranca o Edital (Edge Case *Resultado registrado entre a conferência e a
publicação*).

**Importação local**, dentro da função: `resultados/models.py:37` importa
`publicacoes.models_retificacao`, e a importação no topo faria ciclo. `publish_edital.py:5` já importa de
`classificacao.domain.faixa`, e nenhum teste estrutural proíbe `publicacoes` → `resultados`.

**`ha_resultado_em` e não uma consulta nova**: ele lê `ResultadoEtapa.vigentes`, e uma leitura nova por
`objects` reprovaria `tests/test_vigencia_do_resultado.py`, que é a lista fechada de quem lê fora da
vigência. Toda cadeia de Resultado tem raiz, então *"há Resultado vigente"* equivale a *"há Resultado
registrado"*.

**Descartadas**:
- Na validação de publicação (`validation.py`): ela é função do conteúdo, e não conhece o Edital nem a
  base. A `046` aceitou uma dependência de `editais` para `resultados`, mas era de função pura, e esta
  é consulta ao banco.
- Só em `advertencias_do_ato`: avisa e não recusa, e a `D-002` pede recusa.

---

## R-4 — A Modalidade e o critério acrescentados usam a validação da composição, extraída e não copiada

**Decisão**: o código inline de `editais/domain/perfis.py` que confere Modalidade e critério na
composição vira duas funções:
- `validar_modalidade`: código único no Perfil, denominação, e a regra por `validate_normative_rule`;
- `validar_criterio`: tipo e comportamento na ausência no vocabulário, parâmetro presente, ordem única
  no marco.

`validate_profile` e `validate_classification_milestones` passam a chamá-las, e o comportamento deles
não muda. A aplicação da Retificação chama as mesmas funções **só para as entidades que o ato
acrescenta**, identificadas por identidade presente no fim e ausente no início. A pertinência do
parâmetro — Etapa do Edital, fato do Perfil — já é conferida pela publicação sobre o conteúdo resultante
(`validation.py:749-793`).

**Chamadas em dois lugares, pela mesma função.** Na tela, `diferencas` as chama **ao conferir**: é a
fase em que a spec promete a recusa (`FR-778`, `FR-793`), e nela nenhuma chamada de domínio acontece
(`views.py:3240`: conferir só calcula as diferenças). Na aplicação, elas correm de novo na
confirmação e na publicação, que é o que alcança a API. A ordem única do critério conta os critérios
que **continuam** depois do ato: remover um e acrescentar outro com a mesma ordem é a troca que a US4
existe para permitir. *Corrigido depois do `/speckit-analyze` de 26/09 (I1), que achou a spec
prometendo recusa na conferência e as tarefas só a fazendo na confirmação.*

**Só as acrescentadas, e não todo o conteúdo**: a publicação não confere unicidade de código nem de
ordem (`validation.py:893-898`: *"a Retificação não passa por `validate_profiles`"*). Um impeditivo
novo sobre o conteúdo inteiro julgaria o acervo pela regra de hoje, e um Edital com dado antigo
imperfeito deixaria de ser retificável em qualquer campo. O alcance da `FR-778` e da `FR-793` é o que o
ato acrescenta, e é ele que a `SC-292` mede.

**O vocabulário do critério já tem fonte no domínio**: `classificacao/domain/desempate.py:25-32`, que é
quem o executa. `validar_criterio` lê de lá, por importação local, como `perfis.py` já faz com
`faixa`. As outras duas cópias — o serializer da API (`editais/api/serializers.py:71-74`) e as `choices`
do modelo (`editais/models/perfis.py:350-355`) — continuam onde estão. Unificá-las é higiene, e fica
fora.

**Descartadas**:
- Impeditivos novos em `validation.py`: julgam o acervo (acima).
- Validar só na tela: a API continuaria publicando Modalidade só com `id` e `code`
  (`test_enderecamento.py:610-633`).

---

## R-5 — A Modalidade entra por fragmento próprio, com identidade estável e as duas consequências embutidas

**Decisão**: um fragmento `fragmento-retificacao-modalidade`, com escopo de Edital como o da linha do
quadro, na seção *Perfis de Vaga*. Os campos são:
- `profileId`: referência aos Perfis vigentes;
- `id`: oculto, nascido no fragmento, como o do Anexo;
- código, denominação e descrição;
- fundamento, versão e percentual;
- *"É a ampla concorrência deste Perfil"*: caixa de marcação;
- vagas imediatas: inteiro, opcional.

`diferencas` emite, por Modalidade:
- sempre, `ADD /profiles/id=P/competitionModalities/-`, com a forma do snapshot. A regra só existe se
  houver fundamento, versão ou percentual, como em `interface/forms._modalidades`; os quatro parâmetros
  opacos vão vazios, como o modelo cria na composição, e `effectiveFrom` vai nulo;
- se ampla, `REPLACE /profiles/id=P/generalCompetitionModalityId` com a identidade dela;
- se houver vagas, `ADD /profiles/id=P/vacancyTable/-` com `modalityId` igual à identidade dela.

Ampla **com** vagas é recusada na conferência (cenário 7 da US1), com a razão que
`general_competition_modality_with_row` já dá.

**Por que as consequências vêm embutidas**, e não pelos seletores que já existem: as opções de
`modalityId` da linha nova e as de `generalCompetitionModalityId` vêm do conteúdo **vigente**
(`opcoes_da_linha_nova`, `retificacao.py:716-728`). A Modalidade do mesmo ato não está lá, e a linha
dela ficaria para outra Retificação. É a limitação que o `NOVO_EVENTO` já registra (*"o ato não alcança
o que ele mesmo acrescenta"*). Embutir as duas decisões no fragmento a contorna sem mexer na regra das
referências.

**Identidade no fragmento, e não em `diferencas`**: o Perfil e a linha do quadro geram a identidade em
`diferencas`, e ela muda entre conferir e confirmar. Aqui ela é citada por duas outras alterações do
mesmo ato e precisa ser a mesma nas duas fases. É a razão que já decidiu o Anexo (`retificacao.py:1519-1522`).

**Descartadas**:
- Botão *"Acrescentar Modalidade"* dentro de cada Perfil: exigiria um fragmento por Perfil, e o seletor
  de Perfil já resolve com a mesma segurança (a escolha é conferida contra o vigente).
- Oferecer a Modalidade nova nas opções da linha do quadro do mesmo ato: mudaria `opcoes_da_linha_nova`
  para ler o formulário, e a referência deixaria de ser conferida só contra o vigente.

---

## R-6 — O critério entra por fragmento próprio, na seção dos Perfis

**Decisão**: um fragmento `fragmento-retificacao-criterio`, com escopo de Edital. Os campos são:
- o marco: referência a `perfil · marco`, que carrega os dois ids;
- o tipo: os três do vocabulário;
- a Etapa ou o fato comparado: referência às Etapas enumeradas **pelo marco escolhido** e aos fatos do
  Perfil dele, conferida no servidor;
- o comportamento na ausência;
- a ordem;
- `id`: oculto.

O fragmento emite `ADD /profiles/id=P/classificationMilestones/id=M/tiebreakers/-` com
`{id, order, type, parameters: {stageId} | {factId}, whenMissing}`. O resto não é da tela: a
obsolescência da ordem já vem de `recorte_da_regra`, que compara o marco inteiro exceto o corte
(`classificacao/domain/universo.py:28-33, 83-84`), e é a mesma que a remoção de hoje produz.

**`test_derivacao_nao_alcanca_o_declarado.py:78-99` fixa o conjunto exato de fragmentos** e ganha os
dois novos. A asserção que ele guarda — *não há fragmento que acrescente marco* — continua verdadeira.

---

## R-7 — O caminho da tela do corte não muda de endereço

**Decisão**: `_caminho_da_recusa_do_corte` continua apontando para `interface:retificar` sem âncora. A
`FR-790` pede que o destino ofereça a regra, e é o destino que muda (`R-2`). O teste que fixa o
endereço exato (`test_corte.py:373-386`) continua válido, e um teste novo segue o link e encontra a
regra do marco.

**Descartada**: âncora por marco. Ela exigiria expor identidade de entidade no HTML dos grupos, que hoje
não têm `id`. A FR-019 da tela proíbe caminho normativo no HTML, e o ganho é só de rolagem.

---

## R-8 — O que já vale e só precisa de prova

Nada disto ganha código de produção. Ganha teste, e é a lacuna que a auditoria apontou.

| Garantia | Por que já vale | O teste que prova |
|---|---|---|
| inscrição enviada não muda (`FR-781`) | `Inscricao.modality_id` e `ItemDaListaExigida` congelados no envio, com gatilho append-only | Retificação real sobre Edital com inscrições; comparar antes e depois |
| ordem de outro recorte não fica obsoleta (`FR-781`) | `recorte_da_regra` não compara o conjunto de Modalidades; o recorte reservado filtra pela `modality_id` congelada | reescrever `test_ordem_por_recorte.py:356` para **retificar de fato** (`SC-289`) |
| o recorte novo nasce sem ordem (`FR-781`) | a emissão é manual (`test_ordem_por_recorte.py:334`) | o mesmo teste: `ato_vigente(lista_id=nova)` é `None` |
| critério acrescentado torna a ordem obsoleta (`FR-794`) | `regra_alterada` compara o marco inteiro | teste de integração na classificação |
| documento da Retificação mostra o que nasceu (`FR-798`) | `render_edital_pdf(content)` lê janela, corte, critérios, reversão e Modalidades do conteúdo retificado (`pdf.py:1176, 1210, 1438, 1562, 1616`) | teste do PDF da Retificação |
| leituras vigentes refletem (`FR-797`) | inscrição, seleção pública, recortes, corte e recurso leem `effective_version` | os percursos do [quickstart](quickstart.md) |

---

## R-9 — O que a suíte cerca hoje, e muda

| Teste | Hoje | Depois |
|---|---|---|
| `tests/interface/test_retificar_reversao.py:84-94` | prende a **ausência** do campo com reversão nula | prende a **presença** com o rótulo do vazio, e que nada nasce se ele fica em *"Nenhum"* |
| `tests/integration/classificacao/test_ordem_por_recorte.py:356` | emite outro recorte à mão e remete ao quickstart 5.2 da `034` | retifica pela aplicação e prova as três garantias do `R-8` |
| `tests/integration/editais/test_derivacao_nao_alcanca_o_declarado.py:78-99` | conjunto exato de quatro fragmentos | seis, e a asserção sobre o marco continua |
| `tests/integration/publicacoes/test_enderecamento.py:610-633` | publica Modalidade com só `id` e `code` pela API | continua na gramática, mas a Modalidade ganha denominação: sem ela, o `R-4` recusa. A asserção de endereçamento não muda |
| `tests/integration/publicacoes/test_quadro_na_retificacao.py:119-152` | acrescenta Modalidade com `normativeRule: None` | inalterado: sem regra é válido |

**Os dois fragmentos novos devolvem 404** a quem não alcança o Edital, como o da linha do quadro. Todo
`raise Http404` de view nova precisa de linha em
`specs/033-navegacao-por-capacidade/inventario-das-negativas.md`, ou
`tests/test_gramatica_das_portas.py` reprova no `test-pg` completo — e só nele. As duas linhas entram com os fragmentos.

**Nenhum teste fixa a frase** *"Modalidades de Concorrência ainda não são definidas por aqui"*. Ela
aparece só no template e em documentos, e os documentos de `doc/` são registro histórico, que não se
reescreve.

**Sem protótipo de medição.** A `046` precisou de um porque o impeditivo novo dela julgava todo
Edital publicado pela suíte. As guardas desta feature só alcançam o que o ato **faz nascer ou
acrescenta**. A janela, o corte, a Modalidade e o critério acrescentados não existem na suíte de hoje
fora dos quatro testes da tabela acima. O parecer de 26/09 tirou a medição: testes focados em cada
tarefa, suíte completa no fecho.

---

## R-10 — O rótulo do vazio de cada nascimento

`FR-799`. Cada campo oferecido para nascer diz o que o vazio significa, na gramática dos rótulos que já
existem:

| Campo | Rótulo do vazio |
|---|---|
| `appealWindow/durationDays` | *"Em branco — este marco continua sem prever recurso"* |
| `cutRule/targetKind` | *"Não declarada — este marco continua sem cortar"* |
| `cutRule/governedStage` | a opção *"Não governa Etapa"* é valor, e não vazio; o vazio é *"Não declarada — a publicação será impedida"* |
| `cutRule/tieOutcome`, `cutRule/continuation` | *"Não declarado(a) — a publicação será impedida"* |
| `vacancyReversion/kind` | o que já existe: *"Nenhum — este Edital não reverte vaga reservada"* |

O texto final é da implementação, e passa pela varredura de vocabulário da gestão.
