# Research — 052 · Perfis de Vaga: a visão do conjunto e um editor por vez

## R-001 — Esconder com `hidden`, nunca mover nem recriar

**Decisão**: o cartão fora de vista recebe `hidden`; o script não move, clona, remove nem cria campo
com nome. A tabela e o cabeçalho do editor são elementos novos **sem controles com nome**, fora de
`#perfis`.

**Por quê**: é o que torna a `SC-350` verdadeira por construção — o formulário enviado é o mesmo — e
é o que mantém intactos os contratos do htmx (`hx-target="closest fieldset"` do duplicar e do remover,
`hx-include="closest fieldset"` da Modalidade e do quadro) e os do rascunho local (`data-lista="#perfis"`,
item `.perfil`). O cabeçalho do editor fica **fora** de `#perfis` porque o `MutationObserver` do
`assistente.js` trata toda inserção ali como linha nova e leva o foco a ela.

**Precedente**: o filtro da Retificação (`retificacao.js`) esconde linhas do mesmo formulário com
`hidden` e continua enviando todas.

**Alternativas descartadas**: servidor renderizar só o Perfil aberto (grava por Perfil, reabre as
decisões da `027`, `043` e `051`); `<details name>` por Perfil (muda três contratos do htmx e não dá
tabela — relatório, §4).

## R-002 — O campo inválido num cartão escondido

**Decisão**: ouvinte de `invalid` **em captura** no formulário. No primeiro evento de cada rodada de
validação, se o controle está num cartão escondido, o script abre aquele cartão antes de o navegador
focar e desenhar a mensagem. A rodada termina numa microtarefa (`queueMicrotask`), para que o segundo
inválido da mesma rodada não troque o cartão aberto.

**Por quê**: `invalid` não borbulha; a validação interativa dispara o evento em cada controle
inválido, em ordem de árvore, e só depois procura o primeiro para focar. A `030` escreveu o princípio
(`test_acessibilidade_da_classificacao.py`): campo obrigatório que não pode ser mostrado é envio
recusado em silêncio.

**A verificar no navegador real** (o shim não tem foco nem `hidden`): que o Chrome foca o campo depois
de o cartão perder `hidden` dentro do próprio evento. Se não focar, o plano B é, no `invalid`, abrir o
cartão, cancelar o evento e chamar `reportValidity()` do formulário na microtarefa seguinte.

**O mesmo vale para o `validacao.js`**: ele marca com `setCustomValidity` e, no `submit`, chama
`reportValidity()` — que também dispara `invalid`. Um ouvinte cobre os dois caminhos.

## R-003 — As pendências de cada Perfil

**Decisão**: a view conta, entre as pendências **da etapa** (`_pendencias_da_etapa`), as que têm o
campo começando por `/profiles/id=<uuid>`, e entrega `{id: quantas}`. O cartão leva
`data-pendencias="N"`. A que não nomeia Perfil fica só no bloco da etapa (`FR-948`).

**Por quê**: é o caminho que o achado já traz (`_destino` o documenta: *"achado de forma vem com o
caminho da entidade (`/profiles/id=…/name`)"*), e é contado sobre a lista que a etapa já mostra — a
tabela não pode dizer uma pendência que o bloco não diz.

## R-004 — "Difere do gravado"

**Decisão**: duas fontes, e a linha diz *"alterado — não salvo"* se qualquer uma disser.

1. **No servidor**, quando a tela é montada a partir do digitado (`digitados is not None`: recusa,
   prévia, cancelamento, preenchimento, restauração), `forms.perfis_alterados(digitados, gravados)`
   compara cada Perfil com o gravado de mesma identidade, **só no que o cartão mostra** — os campos do
   Perfil, as Modalidades (código, nome, percentual, fundamento, versão, arredondamento), a ampla, a
   reversão, a forma de convocação, as linhas do quadro e os fatos —, normalizando o que a leitura e a
   gravação escrevem diferente (percentual `25` × `25.0000`, vazio × `None`, ordem). Perfil sem par
   gravado é alterado. O cartão leva `data-alterado`.
2. **Na tela**, o controle cujo valor difere do `defaultValue` (`defaultChecked`, `defaultSelected`), o
   cartão inserido depois do carregamento, e a subcoleção que ganhou ou perdeu item.

**Por quê**: sem a primeira, a tela que volta de uma recusa diria *"sem alteração"* sobre o que
nunca foi gravado — o `defaultValue` ali é o digitado. Comparar só o que o cartão mostra evita o falso
positivo do que a tela não desenha (os marcos, `classificationInformation`, a descrição da Modalidade),
que o cartão não tem como mudar.

**O guardião**: devolver o formulário sem mudança (um *Preencher pelo percentual* sem linha vazia)
MUST produzir zero Perfis alterados — é o teste que prende a normalização.

## R-005 — As frases curtas moram no template

**Decisão**: cada opção de reserva e de forma de convocação leva `data-resumo` com a frase curta da
linha (*"limitado"*, *"por publicação"*); o script lê o `data-resumo` do escolhido e, na falta, o
rótulo. Vagas, localidade e código são o valor do campo.

**Por quê**: o vocabulário continua num lugar só, no template, onde a varredura de vocabulário o lê.

## R-006 — A legenda

**Decisão**: `Perfil <código> — <localidade>`; sem localidade, `— <denominação>`; sem código,
`Perfil novo`. Um filtro de template, para o cartão de agora e o fragmento que o htmx insere.

**Por quê**: a Classificação já usa `{{ code }} — {{ name }}` na legenda; aqui a localidade vem antes
porque é ela que distingue os polos, e a denominação é o recurso quando não há polo.

## R-007 — Qual cartão abre, e o endereço

**Decisão**: *Editar*, *Anterior* e *Próximo* gravam o cartão aberto no fragmento do endereço
(`history.replaceState`, `#cartao-<id do Perfil>`); *Voltar à lista* o limpa. Ao carregar, a
precedência da `FR-953` é: Perfil único → primeiro campo recusado (`[aria-invalid="true"]` ou
`.recusa` dentro de um cartão) → elemento que o fragmento aponta, dentro de um cartão → nenhum. Com
`salvo` ou `aplicado` na consulta, o fragmento é ignorado e limpo.

**Por quê**: o formulário não tem `action`, e o envio vai ao endereço do documento, fragmento incluso;
a tela que volta sem gravar volta com o fragmento, e o mesmo mecanismo reabre o Perfil que estava
aberto — sem campo novo no formulário. O campo novo contaminaria o rascunho local, que compara o
conteúdo do formulário e acusaria *"preenchimento não enviado"* a cada troca de cartão. O
redirecionamento da gravação herda o fragmento (o `Location` não traz um), e por isso `salvo` e
`aplicado` o descartam: depois de gravar, nenhum aberto (`FR-953`).

**A verificar no navegador real**: que o POST sem `action` preserva o fragmento.

## R-008 — Onde a vista se monta

**Decisão**: o template reserva um contêiner vazio para a tabela, logo depois das ajudas; move
*Acrescentar Perfil* para depois dele; e põe o controle do Edital e *Preencher pelo percentual* entre a
tabela e `#perfis` (`UX-120`). O script preenche o contêiner e insere o cabeçalho do editor antes de
`#perfis`. Sem script, o contêiner fica vazio e oculto, e a etapa é a de hoje.

**A tabela** fica numa `div.tabela-rolavel` (o guardião da `030` exige contêiner de rolagem para
tabela), o que também atende a `UX-121`. O contador `p.contadores` continua, porque o `assistente.js` e
o teste de estáticos o prendem; com a tabela presente ele se oculta, e o número vai à legenda da
tabela (`UX-116`).
