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
