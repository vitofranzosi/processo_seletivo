# Pesquisa: o piloto do design system em três telas

*Fase 0 do plano. Cada item resolve uma incógnita do contexto técnico e diz o que foi escolhido, por
quê e o que se descartou. Lido sobre a `main` em `c0f715c9`.*

## 1. Onde o contêiner de escopo entra, e o que ele desfaz

**Escolhido.** Um `<div class="piloto-ds">` aberto logo depois de `{% block conteudo %}` e fechado
antes de `{% endblock %}`, em cada um dos cinco templates. A base (`base.html`) não muda: o `main`
dela não tem bloco de classe, e o contêiner fica dentro dele.

**O que ele desfaz.** `grupos/confirmacao-de-ato.css` limita a medida por
`main>:is(.aviso,.erro,.bastao,.consequencias,form.confirmar)` e `main>.avisos-anteriores>.aviso`.
Dentro do contêiner, esses blocos deixam de ser filhos diretos de `main`, e a regra da P0 para de
valer em `confirmar.html`, sem erro nenhum. A folha do piloto redeclara a mesma medida sob o escopo
(`.piloto-ds>:is(…)`), com o mesmo valor, `calc(var(--leitura) + 2.5rem)`, ou o da coluna centrada,
se for menor. As confirmações do Processo e da Retificação não recebem o contêiner, e a regra da P0
continua valendo nelas (D-002).

**Descartado.** Mudar o seletor da P0 para `main :is(…)`: mudaria duas telas de fora do piloto.
E pôr a classe no `main` pela base: exigiria um bloco novo na base, que todas as telas herdam.

## 2. A folha nova e quem a carrega

**Escolhido.** `interface/static/interface/grupos/piloto-ds.css`, carregada pelo bloco
`estilo_da_pagina` dos cinco templates. `confirmar.html` carrega as duas folhas, a da P0 e a do
piloto, nesta ordem. `ocupacao.html`, `ocupacao_acrescimo.html` e `ocupacao_nao_preenchida.html` não
têm o bloco hoje e passam a ter. `lista.html` carrega `telas/lista.css` e a do piloto.

O mapa escrito à mão de `tests/interface/test_folha_estatica.py`, que diz quem carrega cada folha de
`telas/` e de `grupos/`, ganha a linha da folha nova com os cinco templates. É cumprir um guardião
existente, e não criar outro (D-009).

**Toda regra começa por `.piloto-ds`.** A conferência é a de leitura, na revisão, e a do SC-2602, que
acusa vazamento pelo `telas.csv`. Um teste que a recusasse seria um guardião novo, e o aceite não o
pede.

## 3. Os tokens

**Escolhido.** Acrescentar a `shared/static/shared/tokens.css`, com nomes novos, os neutros da
entrada (`--tinta`, `--tinta-2`, `--tinta-3`, `--linha`, `--linha-forte`, `--fundo-p`, `--verde-50`,
`--verde-100`), o `--azul` e o `--azul-fundo`, e as escalas `--e-*`, `--raio-p`, `--raio`,
`--raio-pilula`, `--sombra-1`, `--controle`, `--controle-p`. Os valores são os do
`03-design-system.md` e de `acesso.css`.

**O que conferir antes.** `acesso.css` já declara alguns desses nomes, num escopo próprio. Se a
declaração dele for em `:root`, o nome em `tokens.css` colide, e a ordem de carga decide qual vale.
A tarefa T004 confere os seletores de `acesso.css` antes de escrever; se houver colisão de nome com
valor diferente, o token do piloto ganha prefixo (`--ds-`), e o registro diz por quê. O `--t-*` não
entra (D-010).

**O contraste** dos pares novos entra no `test_contraste_atende_wcag_aa`, se o teste os listar
explicitamente; se ele derivar os pares de `tokens.css`, já os alcança. A T004 confere qual é o caso.
Acrescentar pares a uma lista existente não é guardião novo.

## 4. Como cada estado do catálogo é montado

**Escolhido.** Um módulo de catálogo, `tests/navegador/piloto/estados.py`, com uma função de
montagem por código de estado (C-01 a L-12), que devolve o endereço da tela, a identidade e os papéis
de quem a abre e o trecho literal que prova o estado. As funções reusam o que a suíte já tem:

| Tela | De onde vem a montagem |
|---|---|
| Confirmação | `tests/fixtures/publicacao.py` (`publish_original`), os cenários de `tests/interface/test_confirmacao_do_encerramento.py` e os de segregação e de homologação da `001`; a recusa do envio por POST com motivo em branco depois de aparar, ou pelo `DomainError` que o teste da `113` já provoca |
| Ocupação | `tests/fixtures/ocupacao.py` (`rascunho_com_quadro`, `montar_cenario_da_ocupacao`), `tests/fixtures/ocupacao_sorteada.py`, e as fixtures locais de `test_ocupacao.py` (`com_continuacao`, `sem_regra_de_corte`), `test_acrescimo.py` (`reserva`) e `test_destinacao_na_ocupacao.py` (`silente`, `reversao_que_nao_sai`, `prazo_encerrado`) |
| Conferências | os mesmos cenários, com o primeiro POST (sem `confirmar`) da rota de acréscimo, de desfazimento, de declaração e de desfazimento da declaração |
| Lista | `tests/interface/test_lista.py` e `tests/interface/test_organizacao_da_lista.py` (`129`), com a paginação de `POR_PAGINA = 20` |

As fixtures locais de um arquivo de teste (as de `test_ocupacao.py`, por exemplo) não se importam de
outro módulo sem arrastar o arquivo inteiro. **Onde for preciso, o corpo delas sobe para
`tests/fixtures/`**, sem mudar o que montam, e o arquivo de origem passa a importá-lo. É mudança de
teste, e não de produto, e os 54 testes que desenham a Ocupação continuam passando.

Os papéis seguem o padrão das jornadas de navegador: `identificar(cliente, nome, papeis)` de
`tests/interface/conftest.py` num `Client`, e o `sessionid` passado ao contexto do Chromium, como em
`test_jornada_da_pagina_do_processo.py`. O vínculo de comissão (quem preside, quem integra) é o das
fixtures de comissão da `011`.

**Um estado por caso.** Dois cenários de ocupação no mesmo banco colidem pelos identificadores fixos
de linha (`LINHA_GERAL`, `LINHA_PPI`) e pela identidade que não repete Perfil. A jornada é
parametrizada pelo código, e cada caso monta um estado só e fotografa as cinco larguras.

## 5. A jornada de fotografia

**Escolhido.** `tests/navegador/test_fotografia_do_piloto.py`, parametrizado pelos 63 códigos. Pula o
módulo inteiro sem `PILOTO_DS_FOTOGRAFIA=<pasta>`: um pulado a mais na suíte com o grupo `navegador`,
e nenhum caso no CI. Por estado:

1. monta pelo catálogo;
2. abre a tela com o papel, a cada largura (375, 768, 1280, 1440, 1920 px, altura 900; e 1280 × 800
   para a dobra);
3. confere o trecho que prova o estado e falha se não o achar (FR-7718);
4. grava `<pasta>/<código>/<largura>.png`, página inteira, e `<pasta>/<código>/<largura>.json`, o
   inventário (seção 6);
5. vigia a política de conteúdo pelo `securitypolicyviolation`, como as outras jornadas, e grava as
   violações no inventário.

Os retornos (R-01 a R-12) e as recusas das conferências (K-05, K-09) praticam o gesto pelo navegador:
o retorno só existe depois do POST. A jornada clica no botão do estado anterior, e não navega para o
endereço, para que a sessão e a chave de idempotência sejam as da tela.

**A pasta "antes"** é tirada com a jornada já escrita e os templates ainda iguais aos da `main`. As
PNG ficam fora do repositório, na pasta de trabalho; os inventários (texto, poucos kB cada) e uma
captura reduzida por estado, a 1440 px, vão para `doc/auditoria-design-system-2026-11-14/piloto/`,
como a `referencia-p0/` fez.

**Descartado.** Fotografar no `ps_p0_referencia`: ele tem a Ocupação num estado só. E pelo cliente de
teste, sem navegador: não daria a ordem visual, a dobra nem a captura.

## 6. O inventário de conteúdo

**Escolhido.** Uma função JavaScript, numa constante de texto do módulo da jornada (como o
`OUVIR_A_CSP` das outras jornadas), avaliada no `main` da página:

- **blocos**: para cada nó de texto não vazio, o ancestral de bloco mais próximo (o primeiro cujo
  `display` não é `inline`), registrado uma vez, com o `innerText` normalizado (espaços colapsados),
  a visibilidade (visível, recolhido num `details` fechado, escondido por CSS) e o retângulo;
- **quantidades**: em cada bloco, os números e o texto do bloco sem eles, que é o rótulo; e os pares
  de `ul.resumo>li` (o `strong` e o rótulo);
- **associações**: para cada bloco, o item da estrutura que o contém, o mais próximo entre `section`
  com `aria-labelledby`, `article`, `li`, `fieldset`, `p.campo`, `form` e `details`, identificado pelo
  texto do título, da legenda ou do rótulo dele, e não pela posição;
- **ações**: cada `a[href]` (rótulo e caminho), cada `form` (rótulo do botão, método, `action` e os
  nomes de campo, ordenados) e cada `button`;
- **ordens**: a lista dos blocos na ordem do documento e na ordem visual, esta pela posição do topo e,
  na mesma linha (tolerância de meia linha), pela esquerda;
- **linhas**: para cada bloco de prosa visível, os caracteres da linha mais longa, medidos pelos
  retângulos de `Range.getClientRects()` agrupados por linha (FR-7730);
- **dobra**: a 1280 × 800, se a ação principal do estado está acima da dobra.

**Normalização** (FR-7722), na comparação: UUID vira `‹id›`; data e hora de registro (`dd/mm/aaaa`,
`dd/mm/aaaa hh:mm`) viram `‹data›`; o valor de `chave`, `chave_idempotencia`, `leitura` e
`csrfmiddlewaretoken` vira `‹chave›`.

**A linha de 80 caracteres é nova medida, e não a do estudo.** `medicoes/largura.js` estima a média
de caracteres por linha só nos blocos acima de 160 caracteres, e diz "sem prosa longa" abaixo disso.
O piloto mede a linha real de todo bloco de prosa. O `largura.js` continua sendo o do SC-2602, que
precisa ser comparável com a referência.

## 7. A comparação

**Escolhido.** `doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py`, fora da suíte,
que lê duas pastas de inventários e grava, por estado e largura, o relatório da comparação: o que
faltou, o que sobrou, o que mudou de associação, as quantidades e as ações diferentes, cada sequência
declarada (aprovada ou invertida, nas duas ordens) e o que mudou de ordem fora delas. As sequências
estão num arquivo de dados ao lado (`sequencias.toml`), escrito da tabela da spec, com cada uma
identificada por trechos literais dos blocos (o primeiro e o segundo termo).

**Por que fora da suíte.** Um teste que comparasse com uma pasta "antes" gravada seria um guardião
novo e, pior, preso a fixtures que mudam com a próxima feature. A comparação é do piloto, e o
resultado entra no relatório.

## 8. O banco da validação

**Escolhido.** `doc/auditoria-design-system-2026-11-14/piloto/scripts/montar_banco_da_validacao.sh`:

1. cria dois bancos novos, `ps_piloto_antiga` e `ps_piloto_nova`, por `pg_restore --no-owner` da cópia
   `ps_p0_referencia.dump` da pasta de notas;
2. acrescenta aos dois, com o `manage.py shell` sobre o código da `main`, os Editais nos estados que as
   tarefas pedem (seis, no máximo: os da tabela de tarefas da `validacao.md`), em duplicata, para que
   cada versão use registros diferentes no mesmo estado (FR-7737). O roteiro reusa as funções de
   montagem do catálogo, com um `APIClient` do DRF e o host `testserver` admitido no ambiente do
   comando;
3. confere, por consulta, que cada Edital chegou ao estado.

Dois servidores na `.claude/launch.json`, `piloto-antiga` (a `main`) e `piloto-nova` (a branch), em
portas próprias (8167 e 8168), cada um sobre o seu banco. **As entradas são acrescentadas, e não
sobrescritas**: o arquivo é versionado e tem entradas do usuário. A antiga roda de uma worktree na
`main`, porque o servidor serve o código da worktree.

**Risco.** As fixtures foram escritas para um banco que some no fim do caso. Os identificadores
fixos de linha podem colidir no segundo Edital do mesmo banco. Se colidirem, cada Edital ganha a sua
linha por cópia do rascunho com os identificadores trocados, e se isso não bastar, o estado vai para
um banco próprio por tarefa. A T010 mede antes de a validação depender disso.

**Os prazos.** O banco da referência data prazos a partir de 14/11. Os Editais acrescentados datam
a partir do dia em que o roteiro roda, e as tarefas não dependem de prazo do banco original.

**Descartado.** Um cenário de treinamento novo (escopo da `134`) e montar à mão pela interface.

## 9. A composição de cada tela

Escolhas de partida, conferidas pelo aceite e não pela preferência:

| Tela | Composição | O que vai onde |
|---|---|---|
| Confirmação | centrada, 44rem | cabeçalho de página com o nome do ato e o Edital; avisos como componente, com a marca de espécie da P0; consequências em cartão de destaque; formulário; barra de ações ao pé, com confirmar e "Cancelar e voltar" |
| Ocupação | principal e trilho a partir de 80rem | no principal, a ordem atual dos blocos; no trilho, só "Abrir esta tela não apura nada" se a O-S3 continuar valendo nas duas ordens, e nada mais. "Termos desta tela" fica no principal, antes dos recortes (O-S1). Os números de cada recorte viram indicadores; cada gesto fica no recorte, num bloco de gesto com a condição antes do botão |
| Conferências | centrada, como a confirmação | os números em indicadores; "Quem a ordem alcança" em lista; a apuração seguinte e o "não se apaga" num bloco de consequência; a barra de ações ao pé |
| Lista | cheia | cabeçalho de página com o título, a unidade e "Novo Processo Seletivo"; os avisos; a faixa; abas em segmentos; a busca em barra de filtros; os Processos em itens de lista dentro de um cartão (D-011) |

**O trilho da Ocupação pode ficar vazio.** Se nada passar pelas sequências, o piloto usa a
composição cheia na Ocupação e registra que o trilho não coube nela, que é resposta à hipótese do
trilho no celular e à do arquétipo "operação com etapas".

**A barra de ações fixa.** Fixa ao pé só a 64rem ou mais, e nunca cobrindo o foco (a 2.4.11): a
folha reserva no fim do contêiner a altura da barra, para que o último controle e a recusa não
fiquem embaixo dela. No estreito, ela não fixa.

## 10. O levantamento dos guardiões candidatos

**Escolhido.** Para cada um dos cinco candidatos do `03-design-system.md` (cor só por token, escala
de fonte, escala de raio, pontos de quebra, caixa nova), rodar a regra como leitura, sem teste,
sobre a folha do piloto e as cinco telas: o que ela acusaria hoje e o que acusaria depois.
O resultado vai para `levantamento-dos-guardioes.md`, nesta pasta.

## 11. A validação com a equipe

**Escolhido.** O roteiro, o gabarito e o registro em `validacao.md`, nesta pasta, com seis tarefas:

| Tarefa | Tela | Pergunta | Tipo |
|---|---|---|---|
| V1 | Lista | ache o Processo X pela busca e diga em que situação estão os Editais dele | localizar |
| V2 | Lista | ache a ação que é sua hoje | localizar |
| V3 | Confirmação, Encerrar com impedimento | o que acontece se confirmar? alguma coisa impede? dá para desfazer? | entender; prevenção (o ato está impedido) |
| V4 | Confirmação, Homologar por quem elaborou | o que muda na publicação depois de homologar? | entender |
| V5 | Ocupação, marco com três recortes | quantas vagas faltam na lista reservada? o que você faria para preenchê-las? | localizar; entender |
| V6 | Conferência do acréscimo | quem a ordem alcança? o que este ato emite? se errar, como desfaz? | entender; prevenção (dois Editais, só um é o certo) |

O gabarito de cada pergunta é a frase da própria tela, copiada antes da sessão. Quem conduz lê a
tarefa e anota. Metade das pessoas começa pela versão antiga. Na versão que vem depois, a tarefa usa
o Edital-duplicata.
