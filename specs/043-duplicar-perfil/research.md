# Research: Duplicar Perfil

**Feature**: [spec.md](./spec.md) · **Plano**: [plan.md](./plan.md) · **Data**: 2026-09-25

Toda decisão aqui foi tomada **depois** de ler o código que ela toca — os caminhos estão citados. A
Fase 0 não tinha `NEEDS CLARIFICATION` técnico em aberto; o que ela resolveu foram quatro premissas
da spec que a leitura desmentiu ou precisou (`R-002`, `R-003`, `R-007`, `R-008`).

---

## R-001 — O remapeamento reusa o da `023`, com mapa estendido

**Decision**: a cópia é produzida por uma função pura nova, `duplicar_perfil`, em
`editais/domain/duplicacao.py`, que **reusa** `reaproveitamento.mapa_de_identidades` e
`reaproveitamento.remapear` sobre `{"profiles": [origem]}`. O mapa é o de `mapa_de_identidades` —
identidade nova para tudo o que é do Perfil — **mais** a identidade em si mesma para cada Etapa do
Edital (`{etapa: etapa}`).

**Rationale**: `remapear` já percorre exatamente as referências que importam — ampla concorrência
declarada, `modalityId` das linhas, `factId` e `stageId` dos critérios, `stages` do marco,
`drawMethod.qualifyingStageId` — e **falha alto** diante de referência que o mapa não conhece. No
reuso de Edital inteiro, as Etapas também são copiadas e por isso também ganham identidade nova;
aqui elas são do mesmo Edital e **ficam** (`FR-642`). Estender o mapa com a identidade das Etapas
**do Edital** — e não de qualquer Etapa que o marco cite — mantém o dente: uma referência a Etapa de
outro Edital continua sem mapa, e continua estourando.

E o ganho que justifica o reuso: a lista de referências é **fechada e cobrada por teste** na `023`.
Um campo de referência acrescentado ao Perfil amanhã entra em `remapear` uma vez, e passa a valer
para as duas operações. Duas travessias do mesmo conteúdo divergiriam no primeiro campo novo — é o
argumento que o repositório já escreve em `forms.marco_do_formulario`.

**Alternatives considered**:
- *Função de travessia própria.* Descartada pelo argumento acima: o achado da `027` sobre
  `generalCompetitionModalityId` — campo que nasceu na `014` e nunca entrou no remapeamento — é
  exatamente o defeito que uma segunda travessia reproduziria.
- *Chamar `remapear` com o mapa só do Perfil.* Não funciona: `stages` do marco estouraria
  `ReferenciaNaoMapeada`, corretamente, porque a Etapa não é do Perfil.

**O que `remapear` não faz e a duplicação acrescenta**, em ordem:
1. **A linha geral do quadro** recebe `identidade_da_linha_geral(novo_id)` por cima do que o mapa
   lhe deu (`FR-640`). O `uuid5` sobre o Perfil é o que torna a gravação idempotente (027).
2. **Código e Localidade** informados (`FR-635`).
3. **Identidade do marco derivada** — `R-005`.
4. **Campos sem tela** — `CAMPOS_SEM_TELA` — removidos (`FR-643`), pela mesma razão da `023`.

---

## R-002 — Identidade vazia vinda do formulário não pode ser mapeada

**Decision**: antes de montar o mapa, a duplicação **atribui identidade nova e distinta** a todo
item cuja identidade venha vazia (`""`), em vez de deixá-la entrar no mapa.

**Rationale**: `forms._texto` devolve `""` para campo ausente. `mapa_de_identidades` registra por
valor — `mapa[str(valor)]` —, de modo que **duas** regras normativas com `ruleId` vazio seriam
mapeadas para **a mesma** identidade nova, e a cópia nasceria com duas Modalidades partilhando uma
Regra. No reuso isso não acontece, porque o conteúdo publicado tem sempre identidade; o formulário
não tem essa garantia. `_modalidade.html` hoje sempre emite `ruleId`, mas a guarda não pode depender
do template.

**Alternatives considered**: normalizar `""` para `None` — descartada: `remapear` deixa `None`
atravessar, e o item da cópia ficaria **sem** identidade, que a gravação preservaria como ausência.

---

## R-003 — Os marcos não estão na etapa Perfis; viajam como marcos em trânsito

**Achado.** A spec supunha que tudo o que a cópia contém estava na tela da etapa Perfis. **Não
está**: os marcos são desenhados pela etapa **Classificação**, e a gravação da etapa Perfis os
**preserva** do que está gravado (`views.PRESERVADO_DA_ETAPA["perfis"]` inclui
`classificationMilestones`; E2E14-001). O cartão do Perfil não tem campo de marco.

**Decision**: a cópia leva os marcos **remapeados** num campo oculto único do cartão,
`perfil-<i>-marcosEmTransito`, com o JSON da coleção `classificationMilestones` no formato do
contrato do rascunho. `forms.ler_perfis` o lê quando presente; `_reexibir_perfis` o devolve na
recusa; o cartão o emite **só** para Perfil que ainda não foi gravado.

**Por que funciona sem tocar na gravação**: `views._preservando` só sobrescreve os campos
preservados de item **que tem par gravado**. A cópia não tem — é linha nova —, então os marcos que
`ler_perfis` leu dela atravessam intactos até o `replace_draft` (`_preservando`, docstring: *"Linha
nova — sem par no que estava gravado — fica com o padrão do contrato"*). Depois da primeira gravação
a cópia **tem** par, o cartão deixa de emitir o campo, e a preservação normal assume.

**De onde vêm os marcos da origem** (`FR-636`):
- origem **gravada**: `forms._marco_persistido` sobre `edital.perfis.get(pk=origem)` — o mesmo
  serializador que a gravação usa;
- origem que é **cópia ainda não gravada**: o campo em trânsito dela, já lido por `ler_perfis`.

Os dois caminhos entregam o mesmo formato, e a cadeia LP01 → LP02 → LP03 funciona sem gravar no meio
(cenário 7).

**Rationale**: é o menor desvio que cumpre `FR-636`/`FR-638` — duplicar não grava — sem abrir um
segundo caminho de gravação.

**Alternatives considered**:
- *Emitir os marcos como os campos do cartão da Classificação, ocultos.* Reusaria o leitor
  `_marcos` sem ramo novo, mas exigiria espelhar ~40 nomes de campo (método de sorteio, corte,
  janela recursal, critérios) num template oculto; e campo oculto com `required` bloqueia a
  submissão sem mostrar o que falta. O JSON viaja no formato do contrato, e não no da tela: o
  round-trip é exato por construção.
- *Gravar no ato de duplicar.* Contraria `FR-638`/`D-001` e perderia as edições não gravadas dos
  outros cartões ao reexibir.
- *Levar só a referência à origem e copiar os marcos na gravação.* A gravação precisaria refazer o
  mapa de fatos da cópia, que só existe no momento de duplicar; e origem não gravada não teria de
  onde copiar.

**Custo que fica registrado**: é o **quinto** lugar por onde a coleção de marcos atravessa a etapa
(os quatro da `025`, R-009, mais este). O teste de `R-009` — travessia inteira — é o guardião.

---

## R-004 — O fragmento é GET, como todos os da composição

**Decision**: `GET fragmentos/perfil/<indice>/duplicar?edital=<id>`, com `hx-include` trazendo o
`fieldset` do Perfil de origem, os Códigos de todos os Perfis da tela e os dois campos do diálogo.
Resposta: o cartão novo, inserido com `hx-swap="afterend"` no cartão de origem.

**Rationale**: nenhum fragmento da composição usa POST (varrido: zero `hx-post` em
`interface/templates`); todos leem o formulário por `hx-include="closest fieldset"` sobre GET, e o
de quadro (`fragmento_quadro`) já manda o Perfil inteiro assim. Duplicar não grava nada, e por isso
GET é semanticamente correto. A CSP proíbe `hx-vals='js:…'` — `hx-include` por seletor é o que o
repositório já usa.

**A recusa volta com `200` e `HX-Retarget`**, e não com `422`: o htmx 2.0.4 do repositório, na
configuração padrão, não troca resposta 4xx, e nenhum script da interface muda isso (varrido:
nenhum `responseHandling` nem `htmx:beforeSwap`). Com `422`, o Código repetido produziria um botão
que não faz nada, sem mensagem.

**Risco registrado, não resolvido aqui**: o tamanho da URL. Um Perfil com requisitos e atribuições
longos, mais os marcos em trânsito, pode passar de 8 KB. Nenhum servidor de aplicação com limite de
linha está configurado no repositório (o contêiner roda `runserver`), e o fragmento de quadro tem o
mesmo perfil de risco hoje. Se a implantação trouxer um limite, a troca é para POST com o token
CSRF no `hx-include` — sem mudar o contrato de resposta.

---

## R-005 — Identidade do marco: derivada é derivada de novo

**Decision**: para cada marco da origem, código e denominação são avaliados **separadamente**:

- o **código** é considerado derivado se for igual ao código da origem, ou ao código da origem
  seguido de `-<n>` com `n` entre 2 e o número de marcos mais um — exatamente o que
  `marcos.identidade_derivada` pode produzir no desempate. *A primeira versão aceitava qualquer
  número, e tomaria o `LP01-2025` escrito à mão por derivado; corrigido na revisão de código.* A comparação é
  contra o código **digitado** da origem **e** contra o **gravado**: quem muda o Código do LP01 na
  tela sem gravar não pode fazer o marco `LP01` parecer escrito à mão;
- a **denominação** é considerada derivada se for igual a `"Classificação final — <denominação da
  origem>"`, pela mesma dupla comparação.

Derivado, recebe `marcos.identidade_derivada(codigo_do_perfil=<Código novo>,
nome_do_perfil=<denominação da cópia>, codigos_em_uso=<códigos já atribuídos na cópia>)`, na ordem
dos marcos da origem — o que reproduz o desempate `-2`, `-3`. Não derivado, é copiado como está.

**Rationale**: é a `FR-420` da `030` aplicada a conteúdo **novo**; a `FR-421` protege conteúdo já
declarado, e o marco escrito à mão continua protegido (`D-004`).

**Alternatives considered**: guardar no marco uma marca de "derivado". Descartada: seria campo novo
no contrato, com migration, para responder uma pergunta que a comparação responde sem estado.

---

## R-006 — Autorização: a guarda do fragmento, mais a de compor

**Decision**: o fragmento exige o parâmetro `edital` (sem ele, 404); resolve o Edital por
`_edital_do_fragmento` — fora do escopo do ator é 404 —; e exige `pode_compor(edital, ator)` —
permissão `edital:elaborar` **e** Edital em elaboração —, recusando com 403 quem alcança o Edital e
não pode compô-lo. A origem gravada é buscada **dentro** do Edital (`edital.perfis.filter(pk=…)`);
identidade de origem que não seja do Edital é tratada como origem não gravada — sem leitura de banco.

**Rationale**: os outros fragmentos devolvem linhas vazias ou leem só Etapas e fatos; este lê
**marcos e Documentos gravados**, e por isso a guarda de escopo sozinha não basta (`FR-648`). 403 e
não 404 no segundo caso porque quem chega lá já lê o Edital: a existência dele não é segredo, e a
tela de composição já mostra a esse ator o modo de leitura.

---

## R-007 — Os campos do diálogo ficam fora do formulário da etapa

**Achado.** `static/interface/rascunho.js` agrupa campos pelo padrão `^([a-z]+)-(\d+)-(\w+)$`, e o
índice do meio é a chave da linha. Um campo `duplicar-3-code` cairia na mesma linha de
`perfil-3-code`, com a mesma chave `code`: o rascunho local gravaria o Código do diálogo — vazio —
por cima do Código do Perfil, e a restauração o apagaria.

**Decision**: os dois campos do diálogo levam o atributo `form` apontando para um identificador que
não é o do formulário da etapa. Assim eles **não** pertencem a `form.elements`: não viajam na
gravação da etapa, não entram no rascunho local e nenhum `required` deles pode bloquear a submissão.
O `hx-include` do botão os nomeia por seletor.

**Alternatives considered**: nomes fora do padrão (`duplicar-codigo-3`). Resolveria o rascunho
local, mas os campos continuariam viajando na gravação da etapa — lixo no POST, e um `required`
esquecido travaria a gravação inteira.

---

## R-008 — O rascunho local não restaura aninhados, de Perfil nenhum

**Achado**, lido no código e **não** reproduzido no navegador: a restauração de
`rascunho.js` pede um fragmento **vazio** por linha e preenche só os campos que casam o padrão de
`R-007`. Modalidades (`modalidade-3-0-code`), linhas do quadro e fatos não casam — o `\w+` final não
atravessa o segundo hífen —, caem em `simples`, e são escritos em `form.elements[nome]`, que no
fragmento vazio recém-pedido não existe. Resultado: um Perfil acrescentado volta sem Modalidades,
quadro e fatos.

**Decision**: registrar (`G-006` da spec) e **não** corrigir aqui. A primeira redação da spec
afirmava o contrário e foi corrigida. O campo em trânsito (`R-003`) casa o padrão e seria restaurado
para a linha certa, mas o fragmento vazio não tem o campo — ele também se perde.

**Rationale**: é limitação anterior, de toda a etapa; corrigi-la é escopo de outra feature
(governança: achado vira registro).

---

## R-009 — Posição, foco e anúncio

**Decision**: o cartão novo entra **logo após** o de origem (`hx-swap="afterend"`). O primeiro campo
editável do cartão novo leva `autofocus`, que o htmx honra na inserção; o cartão carrega uma região
`role="status"` com o anúncio — *"Perfil LP02 criado a partir de LP01"* —, e é nela que vão os
avisos de `FR-645` (documentos não replicados) e `FR-650` (marcos levados).

**Registrado**: depois de gravar, a tela reordena os Perfis por **Código** (`perfis_do_edital`
ordena por `code`). A posição "logo após a origem" vale até a gravação; com Códigos sequenciais, que
é o caso da amostra, a ordem coincide.

---

## R-010 — A contagem de documentos não replicados

**Decision**: conta os Documentos Exigidos **gravados** do Edital cujo `profileId` é a origem, **ou**
cujo `modalityId` é uma Modalidade gravada da origem. Origem não gravada conta zero, e o aviso não
aparece.

**Rationale**: documentos são da etapa de Documentos e referenciam Perfis gravados; é o único lugar
de onde a contagem pode sair sem inventar. Uma consulta a mais no fragmento, sobre um Edital já
resolvido.

---

## R-011 — A medição de SC-230/SC-231

**Decision**: a mesma unidade do estudo — clique, campo preenchido, escolha de *radio* ou lista —,
contada no percurso pela interface, sobre o conteúdo do 140/2025 composto com datas futuras
(sem cadastro retroativo, decisão de 25/09). O roteiro está em [quickstart.md](./quickstart.md).
`SC-230` e `SC-231` contam **só a etapa Perfis**, como o baseline de ~530. A economia na etapa
Classificação — as cópias herdam os marcos sem interação, onde o 140/2025 pedia 16 marcos × 3
critérios — é real, mas fica **fora** do critério: o estudo não a separou da mesma forma, e
somá-la inflaria a comparação. Ela é contada e relatada à parte, na demonstração.

---

## R-012 — A reexibição após recusa perdia fatos e reversão *(achado na implementação)*

**Achado**, anterior a esta feature e revelado por ela: `views._reexibir_perfis` — a função que
devolve o digitado quando a gravação da etapa Perfis é recusada — passava ao cartão `declaredFacts`
e `vacancyReversion` na forma da **leitura** (`[...]` e `{"kind": …}`), mas o cartão desenha
`perfil.fatos` e compara a reversão com o **texto** da espécie. Resultado, em qualquer recusa: o
cartão voltava **sem os fatos** e com a reversão desmarcada — e no ramo oculto, com a representação
do dicionário no valor. A gravação seguinte apagava os dois, sem aviso.

**Decision**: corrigido aqui, e não só registrado. A duplicação desenha a cópia **por esse mesmo
caminho**, e sem a correção toda cópia nascia sem fatos — o que viola `FR-639` desta feature, e não
só um requisito alheio. A correção é a tradução das duas chaves, e o teste
`test_a_recusa_devolve_os_fatos_e_a_reversao_digitados` prende o caminho da recusa, independente da
duplicação. Foi a comparação das três cópias gravadas contra a origem (`SC-233`) que o revelou.

**Registrado também**: o reuso de Edital inteiro (`023`) não remapeava `cutRule.governedStage`.
**Não** foi corrigido aqui — ficou como tarefa separada — e foi corrigido à parte, no #169, antes do
merge desta feature: `remapear` passou a trocar a Etapa governada, e a duplicação herda a troca
pelo mesmo mapa estendido (a Etapa do Edital mapeia para si mesma).
