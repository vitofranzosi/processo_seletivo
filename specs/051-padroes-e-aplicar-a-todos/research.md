# Research — 051 · Padrões do Edital e "aplicar a todos"

Conferido contra a `main` em `44165855` (28/09/2026). Cada decisão diz o que foi escolhido, por quê, e o
que foi descartado.

## R-001 — O gesto é um envio da etapa, e a materialização acontece sobre o digitado

**Decision**: o botão do gesto é um `submit` do formulário da etapa (`name="aplicar"`, valor
identificando a origem). O servidor lê a etapa inteira pelo leitor de sempre (`ler_classificacao`,
`ler_perfis`), calcula os efeitos e devolve a **mesma tela**, com o digitado reexibido — o caminho da
recusa — e a prévia no alto. Nada é gravado. A confirmação é outro `submit` (`name="confirmar_aplicacao"`),
que relê a etapa, recalcula, confere a impressão e grava.

**Rationale**: é o que a `D-001` da spec pede e o que a `FR-638` da `043` já justificou: um só caminho de
gravação, porque `replace_draft` apaga o que o formulário não reenviar. A etapa Classificação grava os
marcos de todos os Perfis num formulário só, e o gesto precisa ver o que está na tela, inclusive o marco
ainda não gravado da origem. Sem JavaScript novo: a CSP não admite `hx-vals` com `js:`.

**Alternatives considered**: *materializar no servidor, por comando próprio* — segundo caminho para o
rascunho, e a gravação seguinte da etapa apagaria o que o formulário não trouxesse; *materializar no
navegador* — exigiria reescrever o formulário por script, e a prévia não seria calculada pela regra do
domínio (Princípio IV: a regra mora no backend).

## R-002 — A regra única numa função pura, por unidade

**Decision**: `editais/domain/aplicacao.py` expõe, para cada unidade, uma função
`efeitos_do_<unidade>(perfis, origem…) -> list[Efeito]` e uma `aplicar(perfis, efeitos, incluidos)`
que devolve os Perfis com os valores materializados. `Efeito` carrega o Perfil, o efeito
(`NASCE`, `SUBSTITUI`, `SEM_MUDANCA`, `FORA`), o motivo, o valor que será gravado e a lista de
mudanças. A comparação de *sem mudança* é pela **unidade normalizada**: a leitura do marco sem
identidade, com os critérios reescritos em termos de código de fato, e não de identidade.

**Rationale**: a `043` pôs o duplicar numa função pura porque é ali que a feature erra em silêncio; o
mesmo vale aqui, com uma diferença: o destino já existe, e a referência a fato precisa ser achada pelo
**código** (`DP-13`, fato 3), com o tipo conferido (edge case da spec). Etapa é do Edital e passa como
está.

**Alternatives considered**: *reusar `remapear`* — ele mapeia identidades para identidades novas, e aqui
o mapa vai para identidades **existentes** do destino, achadas por código; a travessia é a mesma lista
curta (critérios), e escrevê-la aqui é mais claro que torcer o mapa.

## R-003 — A impressão da prévia

**Decision**: a prévia leva, num campo oculto, um resumo (SHA-256) da lista `(Perfil, efeito, valor
normalizado)` de todos os destinos. A confirmação recalcula; se o resumo diverge, a confirmação é
recusada e a tela mostra a prévia de agora (`FR-919`).

**Rationale**: é o padrão da `050` (`FR-863`, `alcance.assinatura`). Cobre as duas divergências: a
pessoa editou a origem ou um destino depois de ver a prévia, e o gravado mudou por outra sessão (esta
última também cai na revisão esperada do `replace_draft`).

## R-004 — O registro do gesto mora na trilha, com uma coluna nova

**Decision**: `RegistroAuditoria` ganha `detalhe` (JSON, nulo). O gesto grava uma linha
`APLICAR_A_TODOS`, com `reason` legível (*"Classificação — marco do LP01 aplicado a 6 Perfis"*) e
`detalhe` = `{etapa, unidade, origem: {perfil, codigo}, destinos: [{perfil, codigo, efeito, impressao}]}`.
A linha é gravada na mesma transação do `replace_draft`. A Revisão lê as linhas do Edital e atribui um
valor ao gesto **mais recente** que alcançou aquele destino naquela unidade, se a impressão atual for a
gravada (`FR-935`).

**Rationale**: decisão do usuário na clarificação (registro do gesto). A trilha já é append-only nas
duas camadas, já tem autor e instante, e já é o lugar da autoria (Princípio IV: *"a automação NÃO DEVE
eliminar a autoria"*). Uma coluna nula não muda nenhuma linha existente.

**Alternatives considered**: *tabela própria em `editais`* — gatilho e privilégio novos para guardar o
que a trilha guarda; *registro dentro do rascunho* — viraria conteúdo, e a `043` recusou por escrito
proveniência no conteúdo; *texto em `reason`* — é o que a trilha exibe, e JSON ali seria ruído na tela.

## R-005 — Padrões: onde cada um nasce

| Padrão | Onde | Por que ali |
|---|---|---|
| Corte do marco único (`FR-927`) | `_marco_novo`, no fragmento que cria o cartão, quando o Perfil não tem marco **na tela** (o fragmento inclui os cartões do Perfil) | É o cartão novo: `FR-421` protege o resto. Contar os cartões da tela, e não os gravados, evita dar corte padrão ao segundo marco ainda não gravado |
| Empate no sorteio (`FR-928`) | o cartão não desenha o campo quando o marco sorteia; `_regra_de_corte_do_marco` deixa de exigi-lo quando o marco ordena por sorteio | A ordem por sorteio é total: não há empate na última posição. O valor já declarado continua lido e impresso |
| Instante do Evento (`FR-929`) | uma lista de Eventos ao lado do campo, cujo valor é o próprio instante em RFC 3339; o leitor usa o digitado se houver, senão o escolhido | Sem consulta no leitor, e o valor forjado passa pela validação de formato de sempre |
| Prosa gerada (`FR-930`) | `sorteios/domain/prosa.py`; o leitor preenche o texto vazio com a frase da regra | O documento imprime `text`; a frase gerada é a que ele imprimirá |
| Etapa decisória eliminatória (`FR-931`) | um segundo controle *"Eliminatória"* dentro do bloco da decisória, marcado na Etapa nova; `ler_etapas` lê o do bloco da forma escolhida | O caráter é comum às duas formas, e o padrão certo depende da forma, que se escolhe no navegador sem ida ao servidor |
| Quadro sugerido (`FR-932`) | `editais/domain/quadro.py::sugestao`; o `placeholder` da linha e um gesto *"Preencher pelo percentual"* | A validação já calcula piso e teto; o arredondamento declarado escolhe entre eles |

## R-006 — O `rounding` da regra normativa ganha forma lida, e continua opaco

**Decision**: `{"mode": "PARA_CIMA" | "MEIO_PARA_CIMA" | "PARA_BAIXO"}`, pedido na Modalidade como lista
fechada opcional. Valor fora da lista (gravado pela API) é preservado e lido como *"declarado fora da
lista"*. O objeto continua em `OPACOS`, com o comentário atualizado: o leitor novo é a **sugestão** da
tela, que não executa norma — o quadro continua declarado pelo operador e conferido pela faixa de
sempre —, e o conteúdo publicado pode trazer forma arbitrária da API.

**Rationale**: decisão do usuário na clarificação (*"pede o rounding da regra"*). Tirar de `OPACOS`
obrigaria o contrato a classificar folhas de uma forma que a API não garante.

## R-007 — A preservação dos opacos da regra normativa na etapa Perfis

**Decision**: `_gravar_etapa("perfis")` funde, por identidade da Modalidade, os campos `calculation`,
`distribution` e `callRules` gravados sobre a regra digitada, e o `rounding` quando a tela devolveu o
marcador de *"fora da lista"*.

**Rationale**: o mapeamento de 28/09 achou que gravar a etapa Perfis zera os quatro, porque a tela não
os desenha e `PRESERVADO_DA_ETAPA` não desce na Modalidade. A `FR-933` diz *"inclusive quando a etapa
Perfis é gravada"*.

## R-008 — `FR-943`: o Perfil que corta sem forma de convocação

**Decision**: achado impeditivo `profile_cuts_without_call_form` em `validate_for_publication`, só na
publicação (o mesmo lugar do `profile_without_cut_rule` da `046`). Edital publicado não é revalidado.

**Rationale**: decisão do usuário. A tarefa T004 mede, antes de escrever, quantos testes publicam Perfil
com corte e sem forma; a correção é nas fixtures, e não na regra (memória *"regra impeditiva quebra a
suíte em bloco"*).

## R-009 — A Retificação fica para o PR seguinte

**Decision**: a US5 (P2) não entra neste PR. A função pura e a prévia desta entrega são o que ela reusa;
o que falta é traduzir cada efeito em Alterações da `048` (substituir = `REPLACE` campo a campo; lista de
critérios = `REMOVE` + `ADD`; nascimento = o `NASCIMENTOS` que existe), a guarda de destino inteiro
fora quando uma diferença alcança campo não retificável (`FR-939`), e a conferência agrupada (`FR-941`).

**Rationale**: o usuário pediu P1 e P2 separadas *"para poder entregar a composição sem esperar a parte
difícil"*, e autorizou entregar a P1 num PR se o escopo não coubesse num só.

## R-010 — O que a Revisão diz, e de onde

**Decision**: `revisao.blocos(snapshot, contexto=None)`, com `contexto` trazendo os Eventos do
Cronograma e as linhas `APLICAR_A_TODOS` do Edital. As origens por comparação: corte igual ao padrão,
arredondamento do marco igual ao padrão, instante igual ao início de um Evento, prosa igual à frase da
regra, linha do quadro igual à sugestão, Etapa decisória eliminatória. A origem do gesto: uma linha
*"Origem"* no grupo de marcos (e na Modalidade, na forma de convocação e na reversão do Perfil) quando
todos os membros foram alcançados pelo mesmo gesto e continuam com o valor gravado.

**O bloco dos campos definitivos** é derivado do `CONTRATO`: as entradas `NAO_RETIFICAVEL` e
`ESTRUTURAL` que não são identidade (`…/id`) nem opacas, com o valor lido do snapshot pela mesma
travessia `(coleção, caminho)` que o guardião do contrato usa, agrupado por campo e por valor igual.
A razão é a do contrato; o estrutural, que não carrega razão (`Mutabilidade` a proíbe), diz *"é a
identidade que outras declarações citam"* — que é a definição da própria natureza.

---

## A P2 — o gesto na Retificação (US5)

Conferido contra a `main` em `0598a9f3` (29/09/2026), depois da P1 (#226) e do `RC-130` (#217).

## R-011 — Na Retificação, a prévia é a conferência, e o gesto é uma declaração da tela

**Decision**: o botão do cartão de origem é um `submit` do formulário da Retificação
(`aplicar=<unidade>:<referência do cartão>`), como na composição (R-001). Ele **declara** o gesto, e a
tela volta com a conferência — *"O que vai mudar"* — em que as Alterações do gesto aparecem agrupadas,
destino a destino, com os quatro efeitos, o motivo de quem fica fora e a caixa de inclusão. A
declaração atravessa as idas e voltas em campos ocultos (`gesto`, `gesto_mostrado:<gesto>`,
`gesto_impressao:<gesto>`, `gesto_destino:<gesto>`). **A confirmação é o *Criar Retificação* de
sempre**: ele recalcula, confere a impressão do que foi mostrado (FR-919) e cria **um** ato com as
Alterações digitadas e as de cada gesto. *Desfazer* retira o gesto da tela.

As Alterações do gesto são calculadas sobre o conteúdo **proposto** — o vigente com as Alterações
digitadas —, e é dele que sai o valor da origem: quem retifica corrige o prazo no primeiro marco e
pede para aplicar aquele prazo aos demais.

As identidades que o gesto cria — o critério e a Modalidade que nascem no destino — são **derivadas**
(`uuid5` da origem e do destino), e não sorteadas: a conferência e a confirmação calculam duas vezes, e
uma identidade nova a cada chamada mudaria o ato sob a mesma chave de idempotência — a razão que a
`020` já deu para o Anexo e a `048` para a Modalidade acrescentada.

**Rationale**: é o que a `DP-13` escreveu para a Retificação — *"ela é a conferência que já existe
(FR-800), agrupada, e não uma prévia em PDF"* — e é o que torna a `SC-347` literal: um gesto
(*Aplicar*) e uma confirmação (*Criar Retificação*). O caminho de criação continua um só
(`create_retification`), com as guardas do ato de sempre: o `RC-130`, a janela que nasce concedendo, o
corte sobre Etapa com Resultado, a Modalidade e o critério que a composição recusaria.

**Alternatives considered**: *reescrever os campos dos destinos no formulário* — a conferência perderia
o agrupamento e a identidade do que foi mostrado, e o critério trocado não tem campo no destino para
ser reescrito (é remoção e acréscimo); *um ato por gesto* — N atos, N versões e N documentos, o
contrário da `FR-941`.

## R-012 — As unidades são os blocos da `FR-938`, e cada uma produz Alterações campo a campo

**Decision**: um botão por unidade, no cartão da origem. **A natureza de cada campo é lida do contrato
de mutabilidade** (`FR-942`, `FR-803` da `048`): a unidade só enumera os campos, e a pergunta *"este
campo se retifica?"* é respondida por `mutabilidade.CONTRATO`.

| Unidade | Cartão | Campos | Alterações | Fora do alcance quando |
|---|---|---|---|---|
| Janela recursal | Marco | `appealWindow/admits`, `durationDays`, `unit` | `REPLACE` por campo; ausente, nasce inteira (`REPLACE` do objeto) | nasceria sem admitir recurso (`FR-787`) |
| Regra de corte | Marco | os seis de `cutRule` | `REPLACE` de alvo, suplentes e empate; ausente, nasce inteira | espécie do alvo, Etapa governada ou continuação diferem (não retificáveis); nasceria governando Etapa com Resultado (`FR-789`) |
| Critérios de desempate | Marco | a lista | `REMOVE` + `ADD` (`FR-792`); `REPLACE` da ordem quando só ela difere | fato sem correspondente de mesmo código e tipo (`FR-914`) |
| Campos do marco | Marco | forma da ordem, Etapas, combinação, normalização, arredondamento | `REPLACE` por campo | as Etapas diferem (não retificável); o campo falta de um lado; método próprio de sorteio (`FR-922`) |
| Forma de convocação | Perfil | `callForm` | `REPLACE` | — |
| Reversão | Perfil | `vacancyReversion/kind` | `REPLACE`; ausente, nasce (`FR-791`) | sem lista reservada |
| Modalidade | Modalidade | denominação, descrição, fundamento, versão, percentual, arredondamento; a declaração da ampla | `REPLACE` por campo; código ausente, `ADD` da Modalidade (`FR-777`), sem linha do quadro (`FR-924`); ampla, `REPLACE` no Perfil (`FR-925`) | arredondamento diferente (não retificável); regra de um lado só (`FR-940`: não nasce em Modalidade publicada) |

Em todas: o destino com dois ou mais marcos, ou sem marco, fica fora pela regra da composição
(`FR-912`); e **nenhuma aplicação é parcial** (`FR-939`) — basta um campo não retificável diferente
para o destino inteiro sair, com o campo nomeado e a razão escrita no contrato.

**Rationale**: a `FR-938` enumera as unidades. Aplicar o marco inteiro, como na composição, levaria
junto o que ninguém pediu para corrigir — o prazo corrigido nos 16 Perfis carregaria os critérios da
origem — e poria as Etapas, que não se retificam, em todo gesto. É também o que o *Independent Test*
mede: 7 Perfis, 7 Alterações, uma por destino e campo.

**Alternatives considered**: *um botão por marco que aplica "o que foi alterado nele"* — casaria com
*"a mesma alteração"* da US5, mas não aplicaria o valor já publicado na origem aos destinos que
divergem, que é metade da correção (a `G-001` da `043` depois de publicado).

## R-013 — A ausência na origem não se aplica na Retificação

**Decision**: se a origem não declara a unidade — sem janela, sem corte, sem critério, sem forma de
convocação, sem reversão —, o gesto é recusado com *"não há o que aplicar"*. E o destino em que aplicar
**retiraria** uma declaração publicada (o arredondamento que a origem não tem, a regra normativa que
ela não declara) fica fora do alcance.

**Rationale**: na composição a ausência é aplicada como ausência (`FR-922`), porque o rascunho ainda
não é norma. Na Retificação, retirar de N Perfis o prazo de recurso ou a forma de convocação
publicados não é a correção que o gesto existe para fazer, a tela não oferece retirar janela nem corte,
e nada deve sumir em lote sem que alguém o peça campo a campo.

## R-014 — O destino já alterado no mesmo ato fica fora

**Decision**: o destino em que a unidade já recebeu Alteração neste ato — digitada, ou de um gesto
anterior — fica fora do alcance, com *"já tem alteração nesta Retificação"* e o campo.

**Rationale**: o ato teria duas Alterações no mesmo caminho, e a última venceria em silêncio. Quem quer
a edição à mão desmarca o destino; quem quer o gesto desfaz a edição.

## R-015 — As consequências são do ato inteiro, lidas de onde as telas de condução as leem

**Decision**: a conferência declara, sobre o conteúdo que o ato produz (`FR-941`):

- **a ordem que fica obsoleta** — o marco cujo recorte da regra (`classificacao.domain.universo.recorte_da_regra`)
  muda e que tem ato de ordenação vigente em algum recorte (`ato_vigente`);
- **o recorte que nasce sem ordem** — a Modalidade reservada que nasce num Perfil cujo marco já tem
  ato de ordenação vigente (`FR-781` da `048`);
- **o marco com resultado divulgado cuja janela muda** — `appealWindow` diferente, e publicação vigente
  no histórico do marco (`divulgacao.application.selectors.historico_do_marco`).

**Do ato inteiro, e não só do gesto**: a correção da origem é a mesma alteração que o gesto leva, e
contar só os destinos esconderia a consequência no primeiro Perfil. As leituras são as das telas de
condução, e não uma terceira grafia da mesma pergunta; uma por marco alcançado, e nenhuma por
participante.

## R-016 — O registro do gesto na Retificação

**Decision**: uma linha `APLICAR_A_TODOS` por gesto confirmado, com o agregado **Retificação** e a
permissão `retificacao:elaborar`, na mesma transação de `create_retification`; `detalhe` segue o
contrato do registro, com `etapa = "retificacao"` e a identidade da Retificação. A repetição com a
mesma chave de idempotência devolve o ato já criado e não registra de novo.

**Rationale**: `FR-921` vale para o gesto, em qualquer tela. O agregado é a Retificação porque é ela o
ato que o gesto produz; a Revisão da composição lê só as linhas do Edital, e não passa a atribuir a um
rascunho o que uma Retificação fez.

## R-017 — A leitura da `FR-802` da `048` (`FR-942`)

**Decision**: escrita no docstring de `publicacoes/domain/aplicacao.py`, além da spec. A `FR-802`
impede espécie nova e genérica de Alteração, e o gesto não cria nenhuma: cada destino recebe
`REPLACE` de campo retificável, o nascimento de objeto que o contrato deixa nascer, ou a remoção e o
acréscimo de item às duas coleções que a `048` nomeou (critério e Modalidade). Cada uma passa pelas
guardas do ato, e todas saem no mesmo ato, com a mesma versão, o mesmo documento e o mesmo histórico
(`FR-795`).
