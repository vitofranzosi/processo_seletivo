# Pesquisa: O Cronograma — visibilidade no PDF, ordenação e prévia (144)

Medido em 10/11/2026 sobre a `main` em `daba322f`. Tudo o que está aqui foi **lido no código**; nada
foi executado nesta sessão, que é só de especificação. Os caminhos são relativos a
`backend/processo_seletivo/`.

## 1. O pedido, em resumo

Três capacidades na etapa 3 do assistente, numa experiência única: (A) olho por Evento para exibir ou
ocultar no PDF — ocultar não desativa; (B) "Ordenar por data de início ↑", estável, explícito, sem
gravar sozinho; (C) prévia compacta no topo, fiel ao formulário não gravado. Restrições: não criar
estado, não mexer em semântica de Etapa nem de prazo, não remover validação, não alterar documento
publicado fora da Retificação, não perder digitação, não criar infraestrutura de canais, preservar
acessibilidade e o padrão visual. Dez cenários mínimos de aceitação, que são aqui os critérios
SC-1580 a SC-1589.

## 2. O que existe

### 2.1 O dado

- `editais/models/cronograma.py` — `Cronograma` (um por Edital) e `EventoCronograma`: `type`,
  `description`, `start_at`, `end_at` (opcional), `order` (único por Cronograma), `status` (só o
  cancelamento é declarado, `045`), `is_registration_period` (único por Cronograma, `009`) e
  `location` (`021`). **Não é append-only**: o rascunho relacional é apagado e recriado a cada
  gravação.
- `editais/application/draft.py:414` — `replace_draft` apaga os Eventos e os recria com
  `bulk_create`, **lendo cada campo do payload com padrão**; depois recria as Etapas, que referenciam
  Evento pela identidade (`EtapaAvaliacao.evento_id`). A identidade do Evento é o que mantém o
  vínculo: reordenar não o toca.
- `editais/domain/cronograma.py` — `validate_schedule`: identidade e ordem não se repetem, e a ordem
  não é negativa — **`0` e lacunas são aceitos**. A tela renumera 1..n (`forms._renumerar`), mas a API
  grava o `order` como chegou, e `publish_edital` o publica como está; instantes
  com fuso; início não posterior ao término; `status` só `PLANEJADO` ou `CANCELADO`.

### 2.2 A etapa

- `interface/templates/interface/compor_cronograma.html` — o formulário, a contagem
  (`data-contador`, de `assistente.js`), a lista `#eventos[data-ordenavel]` e "Acrescentar Evento"
  (HTMX, `fragmento-evento`). Scripts: `ordenacao.js`, `rascunho.js`, `validacao.js`, `remocao.js`.
- `interface/templates/interface/_evento.html` — o cartão: legenda com a categoria, a posição
  (`[data-ordem]`) e o tipo; `_acoes_da_linha.html` (↑, ↓, lixeira), compartilhado com Perfis, Etapas
  e as demais linhas; campos ocultos `id` e `order`; Tipo, Descrição, Início, Término, Onde.
- `interface/static/interface/ordenacao.js` — **a ordem é dado enviado, não a posição**: `renumerar`
  reescreve o campo `-order` de cada linha conforme a posição, e roda na carga e **a cada mutação de
  filhos da lista** (`MutationObserver`). Mover um cartão no DOM, por qualquer código, já renumera.
- `interface/forms.py:699` — `ler_eventos` lê os campos de cada linha e `_renumerar` faz 1..n na
  sequência enviada. Lê `id`, `type`, `description`, `startAt`, `endAt`, `order`, `location`.
- `interface/views.py:2443` — `PRESERVADO_DA_ETAPA["cronograma"] = ("status", "isRegistrationPeriod")`:
  o que a tela não desenha é **preservado do gravado** por `_preservando`.
- `interface/forms.py:1587` — `eventos_persistidos`: o Cronograma gravado, no formato do comando, que
  as **demais etapas** reenviam. A docstring registra o defeito que a omissão de campo causa
  (E2E17-001): campo que falta aqui volta ao padrão na gravação seguinte, sem aviso.
- `interface/forms.py:1177` — `eventos_do_edital`: os Eventos para desenhar a etapa e para a lista de
  Eventos da etapa Etapas (`_etapa.html`, "Evento do Cronograma").
- `interface/static/interface/assistente.js:32` — `reposicionarFoco`: a cada mutação de filhos da
  lista, o **primeiro nó acrescentado** recebe o foco no primeiro campo. Mover um cartão existente com
  `appendChild` ou `insertBefore` produz um registro com esse nó em `addedNodes` (e outro com ele em
  `removedNodes`), e o observador roda **depois** do tratador de clique, numa microtarefa: o foco que o
  script de ordenação devolvesse ao botão seria tomado em seguida. As setas de `ordenacao.js` movem
  pelo mesmo caminho; se elas já perdem o foco hoje, só o navegador dirá — o `dom.js` dos testes de
  `node` não executa `MutationObserver` como o navegador.
- `interface/static/interface/rascunho.js` — guarda **todos** os campos do formulário, inclusive os
  ocultos, e compara por conteúdo; a restauração é feita pelo servidor, que reexibe o enviado.
- `interface/views.py:1768` — `_vencidos_entre`: Evento vencido deixa a etapa pendente. Lê todos.

### 2.3 O conteúdo publicado e o PDF

- `publicacoes/application/publish_edital.py:284` — o `schedule` do conteúdo: cada Evento com
  `id`, `type`, `description`, `startAt`, `endAt`, `order`, `status`, `location`,
  `isRegistrationPeriod`, **sempre presentes**. A prévia do PDF compõe do mesmo conteúdo.
- `shared/canonical.py:161` — `SCHEMA_VERSION = 19`. Cada campo novo do conteúdo é um **degrau**, com
  a razão escrita no bloco de comentário; `publicacoes/domain/elevacao.py` tem `DEGRAUS_DE_EVENTO =
  {11: {"location": ""}}` — o molde exato do que esta feature precisa.
- `editais/domain/validation.py:175` — `EVENTO_PUBLICADO`, a forma conferida de cada Evento publicado.
- `editais/domain/mutabilidade.py:421` — a classificação de cada campo do Evento na Retificação;
  `order` e `id` são estruturais, `isRegistrationPeriod` e `location` retificáveis.
- `interface/revisao.py:322` — `_evento`, o bloco do Evento na Revisão; `_LIDOS_POR_COLECAO`
  (`revisao.py:958`) é uma **partição** do contrato: campo novo que a Revisão não lê nem explica
  reprova no dia em que nasce.
- `duvidas/domain/cobertura.py` — `VERSAO_DO_ESQUEMA` e a cobertura de cada caminho do conteúdo pelo
  assistente; acompanha cada degrau.
- `publicacoes/infrastructure/pdf.py:3976` — `_cronograma`, a tabela: "Nº" é `evento["order"]`;
  "Onde" só quando algum Evento declara local.
- `publicacoes/infrastructure/pdf.py:2163` — `frase_do_periodo_de_inscricoes`: "Período de
  inscrições: … (Cronograma, nº {order})". **É a única remissão a Evento por número** no documento
  (conferido por busca em `pdf.py`, `apresentacao.py` e `humano.py`).
- `publicacoes/infrastructure/pdf.py:2200` e `:4096` — a frase e os pares da Etapa leem o Evento
  vinculado e imprimem as datas dele ("Será feita de … a …").
- `publicacoes/infrastructure/pdf.py:4376` — `_materializaveis`: **seção gerada de fonte vazia não é
  composta**. Testa `snapshot.get(source)`.
- `publicacoes/infrastructure/apresentacao.py:188` — `_principal_presente`, a mesma pergunta na
  apresentação por perguntas, **por outro caminho**: `bool(snapshot.get(catalogada.source))`.
- `publicacoes/infrastructure/pdf.py:4525` — `tabelas_do_documento`: na plana, conta 1 tabela por
  seção Cronograma materializável; na por perguntas, conta o que a composição escreveu.
- `publicacoes/infrastructure/apresentacao.py:433` — o resumo do início: "Datas: no Cronograma
  (item N)", só quando o plano tem a seção.

### 2.4 Reaproveitamento e Retificação

- `editais/domain/reaproveitamento.py:205, 276, 342` — copia o `schedule` do conteúdo publicado com
  `{**evento, …}`: troca identidades, converte instantes, zera o `status`. **Toda chave do Evento
  viaja**; o que falta na origem fica ausente e cai no padrão de `replace_draft`.
- `interface/retificacao.py:103` — `CAMPOS_EVENTO`, os campos do Evento que a Retificação altera,
  com o tipo (`BOOLEANO` já existe, para `isRegistrationPeriod`); `:620` os campos do Evento
  acrescentado; `:2046` o Evento novo nasce com `isRegistrationPeriod: False`.
- `publicacoes/domain/alteracoes.py:103` — os rótulos dos campos na página pública da Retificação.

### 2.5 Os outros canais (FR-5112)

Leem o mesmo `schedule` e **não** mudam: `portal/leitura.py` e `portal/templates/portal/_cronograma.html`
(página pública da seleção), `duvidas/domain/` (assistente), `interface/agenda.py` (Agenda dos
Editais), `interface/kit_textos.py` e `kit_familias/` (Kit de Divulgação),
`interface/relatorio_do_edital.py` (relatório), `editais/api/` (leitura).

### 2.6 Os testes que já existem e que esta feature toca

- `tests/javascript/` — `node --test` contra o DOM mínimo de `dom.js`; já há `ordenacao.test.js` e
  `rascunho.test.js`. Rodado por `tests/test_javascript.py`, pulado sem `node`.
- `tests/interface/test_fluxo.py:40` — `texto_de_pdf_bytes`: o texto **realmente desenhado** no PDF.
- `tests/navegador/` — jornadas no Chromium (grupo `navegador`).
- `tests/contract/test_elevacao_degrau_11.py` — o molde do teste do degrau.
- `tests/migrations/test_migrations.py:716, 928` — a contagem de migrations por app (`editais: 25`).
- `tests/interface/test_campos_vem_do_contrato.py` — "85 retificáveis, e 85 com tela".
- Guardiões: `test_citacoes_de_requisito`, `test_vocabulario_da_composicao`, `test_acessibilidade`
  (classe citada exige regra na folha), CSP sem `unsafe-inline`, `test_estaticos`.

O commit `a7d9480a` (degrau 19, `131`) é o gabarito do que um campo novo no conteúdo publicado
atravessa: 25 arquivos, de `canonical.py` a `openapi.yaml` da `001` e à matriz da `026`.

## 3. Decisões

## D-001 — Booleano do Evento, sempre presente no conteúdo publicado, com degrau de elevação

O atributo é uma coluna `shown_in_pdf` do `EventoCronograma`, padrão verdadeiro, e a chave
`shownInPdf` em cada item de `schedule`, sempre presente. O degrau 20 diz que a ausência é `true`.

**Por que no conteúdo publicado.** O PDF se compõe do conteúdo do ato, sem consultar o banco — é o
que faz a Retificação e o consolidado reproduzirem o documento. Guardar a visibilidade só no
relacional faria o documento depender de dado que o ato não contém.

**Por que a conversão não inventa.** Todo Edital publicado antes do degrau imprimiu todos os Eventos:
a capacidade não existia. `true` é a verdade sobre o acervo, como `""` foi para o local no degrau 11.

**Descartadas.** (a) Um `status` novo "OCULTO": seria estado, que o pedido proíbe, e o `status` é a
única declaração que a `045` admite. (b) Uma lista de ocultos no Cronograma: segunda fonte da
identidade do Evento, que o reaproveitamento teria de traduzir à parte. (c) O negativo
(`hiddenFromPdf`): a pergunta da tela e do documento é "sai no PDF?", e o nome positivo lê como o
rótulo.

## D-002 — Uma função só decide o que sai; os vínculos continuam lendo todos

`eventos_no_documento(snapshot)` devolve os Eventos exibidos, na sequência do Cronograma, com o
número que terão na tabela. Leem dela: a tabela (`_cronograma`), a presença da seção nas duas
apresentações (`_materializaveis` e `_principal_presente`) e, por consequência, a contagem de tabelas
e a numeração. **Não** leem dela a frase da Etapa nem a do período, que citam o Evento pelo vínculo e
continuam imprimindo as datas dele.

**Por que não filtrar o `schedule` antes de compor.** Seria uma linha só, e quebraria a Etapa
vinculada ao Evento oculto: o documento deixaria de dizer quando ela é feita — o oposto do que
"ocultar não é desativar" pede.

**O risco que esta decisão fecha.** Hoje há duas perguntas "a seção Cronograma sai?" escritas por
caminhos diferentes. Sem a função única, uma delas responderia "sim" com todos ocultos, e a "Tabela
N" e o número das seções se desalinhariam do que foi impresso.

## D-003 — Sem oculto, "Nº" é o `order`; com algum, a posição entre os exibidos

Sem nenhum Evento oculto, a tabela imprime o `order`, como hoje — inclusive o `0` e as lacunas que a
API admite. Com algum oculto, numera os exibidos de 1 a k. A remissão do período de inscrições usa o
número que a tabela imprimir; com o Evento oculto, a frase sai sem a remissão: "Período de
inscrições: de …, a …."

**Por que duas regras, e não uma.** *Sempre 1..k* mudaria o texto de conteúdo antigo que publicou
"0, 1, 2" ou "1, 3, 4" — a primeira versão desta decisão fazia isso, e contradizia a compatibilidade
(SC-1580); a revisão do usuário de 10/11 a apontou. *Sempre o `order`* faria a tabela com oculto sair
"1, 3, 4" — num ato normativo, lacuna de numeração lê como item suprimido por engano, e aqui seria a
própria feature produzindo a lacuna. A condição que separa as duas é a única situação nova: haver
oculto. Todo conteúdo anterior ao degrau 20 é elevado com todos exibidos, e cai sempre na primeira.

**Descartada: proibir ocultar o período de inscrições.** Exigiria regra cruzada entre duas etapas (a
designação é feita em "Inscrição", depois do Cronograma) e um impeditivo novo, para um caso em que o
documento continua dizendo o período no resumo e em "Como se inscrever?".

## D-004 — Todos ocultos não impede publicar

A seção não é composta, pela regra que já omite seção gerada de fonte vazia (`_materializaveis`). A
prévia e a Revisão dizem que ela não será impressa. Um impeditivo novo seria regra de publicação, e o
pedido manda não mexer nelas; o Edital sem tabela de Cronograma já é publicável hoje no caminho
inverso — basta não ter Evento, e a pendência da etapa é que o acusa.

## D-005 — Ordenar é do cliente, estável, sem gravar

Um script move os cartões no DOM, em ordem crescente pelo valor do campo Início. A renumeração do
campo `-order` é a que `ordenacao.js` já faz a cada mutação da lista; o script novo não a duplica.

- **Comparação.** O valor de `datetime-local` é `AAAA-MM-DDTHH:MM`, de largura fixa: a comparação de
  texto é a cronológica. Vazio — incompleto ou não preenchido — vai ao fim.
- **Estabilidade.** A chave de desempate é a posição anterior; não se confia na estabilidade do
  `Array.prototype.sort` do motor.
- **Sem gravar.** Como as setas: a ordem viaja no formulário e é gravada com a etapa. O rascunho local
  a registra.
- **Descartadas.** Ordenar no servidor (um pedido para o que o formulário já sabe, e perderia o não
  gravado); ordenar ao gravar (seria ordenação automática, que o pedido recusa).

## D-006 — A prévia é do cliente, lida do formulário; sem filtro

Um script lê os cartões — Descrição (ou Tipo), Início, Término e o campo de visibilidade, nessa
ordem, que é a das colunas — e desenha a tabela compacta; escuta `input` e `change` no formulário e a mutação da lista. Nenhum pedido ao
servidor, nenhuma formatação de norma: as datas saem em `dd/mm/aaaa hh:mm`, que é apresentação.

**Por que não renderizar no servidor.** Teria de ser refeita a cada digitação (pedido por tecla) ou
ficaria desatualizada até gravar — o pedido exige o não gravado.

**Por que sem "Todos / Somente no PDF".** Com a marca "Oculto" em cada linha e a contagem no
cabeçalho, o filtro não acrescenta informação, e acrescenta um estado de tela que precisa sobreviver
à recarga e à restauração do rascunho. Reavaliar se uma lista real passar de uma tela.

## D-007 — Botão de alternância sobre um campo oculto do formulário

O cartão leva `<input type="hidden" name="evento-N-shownInPdf" value="true|false">`. O botão alterna
o valor, `aria-pressed`, o glifo, o `title` e a marca da legenda, e **dispara `change` no campo** —
sem isso, nem o rascunho local nem a prévia percebem a mudança, porque alterar `value` por código não
emite evento.

**Por que não uma caixa de marcar.** Seria um campo a mais na faixa de campos de um cartão que já
quebra a 1280 px, e o pedido pede o olho nas ações da linha.

**Por que campo oculto e não `PRESERVADO_DA_ETAPA`.** A etapa Cronograma **desenha** a visibilidade;
preservar do gravado faria a alternância nunca chegar ao servidor.

## D-008 — Reaproveitar preserva a visibilidade

Copiar o Edital copia o que ele decidiu publicar. O `{**evento}` do reaproveitamento já leva a chave;
`replace_draft` lê com padrão verdadeiro, de modo que a origem anterior ao degrau chega toda exibida.

## D-009 — A Revisão mostra a visibilidade

Quem homologa confere o documento. O Evento oculto ganha a linha "Não sai no PDF"; com todos
ocultos, o bloco diz que a seção não será impressa. O campo entra em `_LIDOS_POR_COLECAO["schedule"]`.

## D-010 — Mover não é acrescentar

O foco das listas (`assistente.js`) passa a considerar linha nova só o nó que entrou na lista **sem
ter saído dela na mesma entrega de registros** do observador. A ordenação reanexa todos os cartões
num laço síncrono, e o navegador entrega a mutação inteira num lote só; a seta move um cartão, também
num lote. Nos dois casos cada nó acrescentado está também entre os removidos, e o foco não é tocado.

**Por que no observador, e não uma marca posta pela ordenação.** Uma marca (`data-reordenando`) teria
de sobreviver até a microtarefa do observador e ser limpa depois — uma corrida entre dois scripts
para resolver um fato que o próprio registro de mutação já diz. E a regra corrige as setas de todas
as listas pelo mesmo motivo, sem que cada uma precise saber da outra.

**O que a prova exige.** O teste roda no navegador (T026 e T029), e lê `document.activeElement`
**depois** de o observador ter respondido — esperando a microtarefa, e não logo após o clique.

## 4. Riscos concretos

| Risco | Onde | O que o fecha |
|---|---|---|
| Campo omitido numa travessia volta a exibido sem aviso (o defeito da E2E17-001) | `ler_eventos`, `eventos_do_edital`, `eventos_persistidos`, `replace_draft`, `EventSerializer`, a reexibição da recusa | um teste por caminho: gravar outra etapa, recusar, API, restaurar (T008, T009) |
| A seção "sai" por um caminho e "não sai" por outro, com todos ocultos | `_materializaveis` × `_principal_presente` × `tabelas_do_documento` | função única (D-002); teste com todos ocultos nas duas apresentações (T013) |
| Remissão "(Cronograma, nº N)" para linha inexistente ou com número errado | `frase_do_periodo_de_inscricoes` | D-003; teste com o período oculto e com Evento oculto antes dele (T012), e no texto extraído do PDF (T014) |
| A numeração de conteúdo antigo mudar | `order` `0` ou com lacunas, aceitos pela API | D-003: sem oculto, o `order` como hoje; casos com `0` e lacunas (T012, T014) |
| O foco ir para o primeiro campo do cartão movido | `assistente.js:32` trata mover como acrescentar | D-010; teste no navegador depois do observador (T029, T026) |
| A alternância não chega ao rascunho local nem à prévia | `value` alterado por script não emite evento | `change` despachado (D-007); teste `node` (T016) |
| Guardiões que reprovam no dia do degrau | `cobertura.py`, `_LIDOS_POR_COLECAO`, `EVENTO_PUBLICADO`, matriz da `026`, `openapi.yaml` da `001`, contagem de migrations, "85 retificáveis" | lista fechada pelo commit do degrau 19; tarefas T002–T007 |
| Outra feature em curso sobe o degrau 20 antes | `shared/canonical.py` | as branches abertas (138, 142, 143) estão em 19 em 10/11; quem mergear depois renumera o degrau e roda a suíte |
| A ordenação textual erra se o valor não for `AAAA-MM-DDTHH:MM` | navegador que entregue segundos | o navegador normaliza o `datetime-local`; o teste cobre `:SS` e vazio (T020) |
| Documento publicado mudar | PDFs guardados | não se regeneram (FR-5114); a feature não toca artefato publicado |

## 5. Conferências que esta sessão não fez

Nada foi executado: nem a suíte, nem o preview do GPS (só a maquete, no navegador do painel). A
afirmação "a remissão do período é a única por número" é de busca textual em três arquivos; a
implementação a reconfere com o texto extraído do PDF (SC-1588). Se as setas já perdem o foco hoje
(ver §2.2) não foi medido.
