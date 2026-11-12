# Research: Conferência com o documento à vista

Plano sobre a `main` em `7441e5c0`, com o #481 (esta spec), o #482 (155), o #483 (150) e o #484
(154, plano) mergeados. Os `R-` dizem onde e como cada requisito se cumpre no código, e o que o plano
escolheu dentro da latitude da spec. As decisões de produto são todas do usuário (D-001 a D-008 da
spec, e a R-001 abaixo) e nenhuma se reabre.

---

## R-001 — O que é acesso bem-sucedido (FR-6544)

**Decisão do usuário (11/11/2026)**: *"defina abertura como acesso ao arquivo vigente, sem afirmar
comprovação de exibição ou leitura."* O plano a lê assim, sem acrescentar:

- **acesso** é o servidor entregar a quem pediu o arquivo de uma apresentação — a vigente, para a
  FR-3611 da `115` —, depois de autorizar o pedido e conferir o resumo (FR-3605 da `115`);
- **bem-sucedido** é a entrega ter terminado: o último bloco do arquivo foi passado ao servidor web.
  Pedido recusado (integridade, arquivo indisponível, autorização) e pedido interrompido antes do fim
  não são acesso;
- nada disso diz que o navegador **mostrou** ou que a pessoa **leu**: os textos dizem *"aberto por
  você"* e explicam que é acesso (FR-6549, UX-652).

**Como.** Hoje `documento_da_convocacao` grava a consulta **antes** de devolver a `FileResponse`: o
registro existe mesmo quando a conexão cai no primeiro byte. Passa a responder com uma
`StreamingHttpResponse` sobre um gerador que lê a cópia verificada em blocos e grava a consulta
**depois** do último bloco, no próprio gerador, em `command_context` próprio. Se o cliente desiste, o
servidor web para de iterar, o gerador é fechado (`GeneratorExit`) e nada é gravado.

- Gerador, e não arquivo: com objeto de arquivo, a `FileResponse` usa o `wsgi.file_wrapper` (o
  `sendfile`), que entrega sem passar pelo Python — e o fim da entrega seria invisível.
- O cabeçalho é o de hoje: `Content-Type: application/pdf`, `Content-Disposition` `inline` ou
  `attachment` com o nome original, `Content-Length`, e a resposta privada e sem cache
  (`marcar_como_privada`). O download (`?baixar=1`) segue o mesmo caminho e conta como abertura, como
  hoje, com *"baixado"* no motivo.
- A trilha não muda de forma: o mesmo `CONSULTAR_DOCUMENTO_DA_CONVOCACAO`, sob a apresentação, com o
  requisito no motivo (FR-3603 da `115`). Muda **quando** ele é gravado.

**A consequência na tela.** O registro fica pronto um instante depois de o último byte sair. A
página relê a marca quando a moldura termina de carregar (R-005); se a releitura chegar antes do
registro, ela tenta de novo uma vez, um segundo depois, e depois desiste em silêncio — o aviso de
abertura fica, e a próxima releitura (ao registrar, ou ao voltar à aba) o corrige. O comando não
depende disso: ele lê a trilha no instante do registro (FR-3611 da `115`).

**Nos testes.** O cliente de teste do Django não consome o corpo de uma resposta em fluxo: quem
afirma o registro passa a ler `b"".join(resposta.streaming_content)` antes. São três arquivos de
`tests/interface/` que pedem a rota da gestão; os testes de domínio usam a fixture `abrir`, que grava
o evento direto e não muda.

**A Mesa** continua gravando como hoje (FR-6548): a abertura dela só informa, a FR-027 da `012` não é
revista, e mexer nela pediria revisão que o usuário não pediu. A diferença fica escrita no módulo.

**Alternativas descartadas**: gravar antes, como hoje (o pedido interrompido viraria abertura,
contra a US3, cenário 7); gravar quando a página avisa que a moldura carregou (autodeclaração do
cliente, falsificável — D-002 da spec); uma pré-verificação sem entrega (dobra o cálculo do resumo e
não diz nada sobre a entrega).

## R-002 — A moldura e a recusa dentro dela (FR-6504, FR-6510, FR-6545)

`documento_da_convocacao` ganha `@xframe_options_sameorigin`, como `documento_da_mesa` (FR-112 da
`012`): só a própria origem emoldura. A CSP já permite `frame-src 'self'`.

**A recusa.** Hoje a recusa sai como exceção, o middleware `RecusaDoDominioMiddleware` monta a página
de recusa da área, e o `XFrameOptionsMiddleware` lhe põe `DENY`: dentro da moldura, o navegador
mostra a página de bloqueio dele (o achado registrado na spec, agora confirmado pela leitura do
código). O painel passa a pedir o arquivo com `?painel=1`. Com esse parâmetro, as duas rotas —
convocação e Mesa — capturam a recusa da entrega (integridade, arquivo indisponível) depois de gravar
o evento de hoje e respondem `interface/_recusa_no_painel.html`: um documento pequeno, sem a barra da
gestão, com a frase da recusa, status 409, emoldurável pela própria origem e com a folha da gestão.
O elemento raiz leva `data-recusa-no-painel`, e o script lê a frase de lá e a leva para o texto do
painel (FR-6510, UX-654); sem script, a frase aparece dentro da moldura, legível do mesmo jeito.

Sem `?painel=1` — a aba própria, o download —, a recusa continua a página da área, como hoje.

**A autorização** não muda e não é capturada: o 404 de quem não alcança continua 404, também no
painel.

## R-003 — Um visualizador, duas telas (D-001, FR-6533)

`mesa.js` vira `visualizador.js`, configurado por atributos no HTML, e as duas telas o carregam:

- `data-visualizador` no contêiner de trabalho; `data-painel`, `data-quadro`, `data-titulo-do-painel`
  e `data-identificacao` no painel; `data-abrir-documento` em cada link, com `data-documento` (o
  nome), `data-versao` e `data-tamanho`;
- o painel vem **antes** no DOM, `hidden`, como hoje na Mesa;
- a barra ganha *"Baixar"* nas duas telas (FR-6507, FR-6546) e a linha de identificação na da
  conferência (FR-6506, UX-640).

O teste de JavaScript `tests/javascript/mesa.test.js` vira `visualizador.test.js` e passa a cobrir
as duas telas. O comportamento da Mesa que ele prende — o link avulso aponta para o documento do
painel, o fechar devolve o foco — continua.

**A largura.** A fronteira é a de hoje, `64rem`, em `matchMedia`. Abaixo dela o script não intercepta
o clique: o link abre fora da página, como sempre (D-006, FR-6527).

## R-004 — O navegador que declara não mostrar PDF (FR-6502, FR-6546)

`navigator.pdfViewerEnabled === false` — a declaração padrão dos navegadores atuais — faz o painel
mostrar a alternativa (UX-643) com *"Abrir em aba própria"* e *"Baixar"*, sem `src` na moldura.
`undefined` (navegador que não declara) é tratado como `true`: a prévia. Nenhum dado disso vai ao
servidor; o registro e o "conforme" não o veem (D-002).

## R-005 — A releitura da marca de abertura (FR-6503, FR-6511, FR-6528)

Uma rota nova, só `GET`, devolve o **cartão** de um item já renderizado — o mesmo parcial que a
página usa:

`editais/<edital>/marcos/<marco>/convocacao/<convocacao>/documentos/itens/<item>/cartao`

com a mesma porta de `documentos_da_convocacao` (`_convocacao_para_conferir`) e sem registro de
consulta (o da página já existe; FR-3604 da `115`). O script a chama: quando a moldura termina de
carregar (com uma tentativa a mais, R-001); quando a pessoa volta à aba depois de abrir fora da
página (`visibilitychange` para `visible`, ou `pageshow`); e depois de um download. O cartão novo
substitui o antigo **preservando o que está digitado** — o script copia os valores do formulário
antigo para o novo antes da troca, e a troca não acontece enquanto o foco está dentro do formulário
(adiada para o `focusout`).

Para o parcial existir, o `<article>` de cada item sai de `convocacao_documentos.html` para
`interface/_documento_da_convocacao.html`. Os `id` deixam de usar `forloop.counter` e passam a usar
o `id` do item: um cartão relido sozinho não sabe a posição dele na página. Nenhum teste lê os `id`
antigos.

Na Mesa, a mesma ideia com a lista de documentos: `GET
minhas-etapas/<edital>/<etapa>/inscricoes/<inscricao>/documentos` devolve a `<ul class="documentos">`
(a marca *"aberto"* é dela), pela porta da Mesa (`_mesa_do_avaliador` e a Atribuição).

## R-006 — Registrar sem recarregar (FR-6514 a FR-6518, D-004)

**htmx**, que a gestão já serve (`htmx.min.js`, com `includeIndicatorStyles` e `allowEval` desligados
em `base.html`, por causa da CSP). O formulário de cada item ganha `hx-post` para a mesma rota de
hoje, `hx-target` no próprio `<article>` e `hx-swap="outerHTML"`. Sem script, `method="post"` e o
redirecionamento de hoje continuam (FR-6517).

`conferir_documento_view`, com o cabeçalho `HX-Request`, responde **200** — o htmx não troca 4xx — com:

- o cartão do item (parcial da R-005), com a recusa dentro, quando houver, e o que foi marcado e
  digitado — exceto o resultado na versão superada, como hoje (`_recusa_da_conferencia`);
- `hx-swap-oob` para a seção *"Situação desta convocação"*, para a navegação das pessoas do recorte e
  para a região de confirmação (`#confirmacao-da-conferencia`, `role="status"`).

A recusa sem cartão onde morar (desfecho, Processo encerrado) responde a página inteira com
`HX-Refresh: true`: os formulários que deixaram de valer somem, e a recusa vai ao alto, como hoje
(FR-6516). Sem identidade, a resposta é 200 com `HX-Retarget` para a mensagem do formulário e
`HX-Reswap: innerHTML`, e o texto da UX-646: o formulário fica, com o que foi digitado. Falha de
rede: o evento `htmx:sendError` escreve a mesma frase, pelo `visualizador.js`.

A chave de idempotência continua uma por formulário. Depois de um registro aceito, o cartão relido
traz chave nova (FR-6515). O duplo clique: o htmx já descarta o segundo pedido enquanto o primeiro
corre, e a chave cobre o resto.

## R-007 — A confirmação e o próximo (FR-6519 a FR-6522, UX-642)

A região de confirmação recebe, depois de um registro aceito:

- a frase do que foi registrado (UX-642, UX-647);
- o próximo documento desta pessoa com versão a conferir, na ordem da página (o primeiro `RECEBIDO`
  ou `COMPLEMENTADO` da leitura relida), com o mesmo link *"Abrir"* dos cartões — e portanto aberto
  no painel em tela larga, fora da página em tela estreita, sempre por gesto (D-003);
- sem documento a conferir nesta pessoa: a próxima pessoa com documento a conferir, pela
  `pessoas_do_recorte` de hoje (FR-5024 da `143`), como link para a página dela;
- sem nenhuma: *"Não há outro documento a conferir neste recorte."* e o caminho à convocação.

A confirmação não abre nada e não registra nada.

## R-008 — O pedido de aviso de uma pessoa (D-008, FR-6537 a FR-6542; FR-4603, FR-4605, FR-4620 da `134`)

`avisos/application/pendencias.py`:

- `selecionar(...)` ganha `convocacao_id=None`. Com ele, a seleção é a do recorte filtrada à
  convocação vigente daquela pessoa — a mesma regra, as mesmas exclusões, o mesmo dia local
  (`inicio_do_dia`). Nenhum caminho de regra novo;
- `avisar_pendencias(...)` ganha `convocacao_id=None`. Com ele, a reserva de idempotência leva a
  convocação no `payload`, a recusa sem alcançado diz o motivo **daquela pessoa** e, no *"já avisada
  hoje"*, a data do dia seguinte (FR-6541, UX-650), e a trilha leva `"recorte": "pessoa"` e a
  convocação no `detalhe`, e *"de uma pessoa"* no motivo (FR-4620 da `134`). O resto — a trava do
  Processo, a autorização de quem confere, a chave `AVISOS_AOS_CANDIDATOS`, o estado final, o texto
  com todas as pendências da pessoa, o despacho — é o mesmo código.
- `proximo_dia_do_pedido(agora)` devolve a data local do dia seguinte, para o texto.

**A rota**: `POST editais/<edital>/marcos/<marco>/convocacao/<convocacao>/aviso-de-pendencia`, em
`views.py`, `pedir_aviso_de_pendencia_view`. Com `HX-Request`, responde 200 com a confirmação e a
situação (`hx-swap-oob`); sem, redireciona à página dos documentos com a frase na sessão.

**Quando o gesto aparece**: a confirmação de um registro aceito, quando a leitura relida não tem
documento desta pessoa com versão a conferir e a prévia (`avisos_pendencias.previa`, já lida pela
página) diz que a pessoa tem pendência. Alcançável: o botão. Não alcançável: o motivo, e a data no
*"já avisada hoje"*. Envio desabilitado: a frase da UX-313 da `134`, sem botão.

**O gesto em lote** não muda (FR-6542). O limite é um só, porque os dois gravam o mesmo `Aviso` de
origem `PENDENCIA` e o `_raizes_avisadas_hoje` conta os dois.

## R-009 — A situação do aviso em três grupos (FR-6543, UX-649)

`interface/conducao_da_convocacao.py`, `frase_do_aviso`, passa a três começos de frase:

| Estado da `066` | Frase |
|---|---|
| pendente, em envio, falha temporária | *"Aviso solicitado em ‹data›; aguardando envio."* |
| aceita pelo servidor | *"Aviso enviado em ‹aceito_em›: aceito pelo servidor de correio."* |
| falha definitiva, indeterminada, expirada sem envio, interrompido, sem endereço, não elegível | *"Aviso não enviado: ‹rótulo da `066`›."* (com o motivo da interrupção, quando há) |

A frase é a mesma no cartão da convocação e na página dos documentos (FR-6536, SC-2153), porque as
duas leem `frase_do_aviso`. Nenhum texto diz *entregue*, *recebido* ou *lido* (FR-5016 da `143`).
Os testes da `143` e da `134` que prendem as frases antigas mudam junto, citando a FR-6543.

## R-010 — A volta de um arquivo aberto fora da página (FR-6528, FR-6529, FR-6547)

O script guarda, ao abrir fora da página, qual item (ou documento, na Mesa) foi aberto, e o
preenchimento do formulário daquele cartão, em `sessionStorage` — da aba, apagado quando ela fecha.
Na volta:

- **sem recarga** (o caso comum: a aba própria abriu outra aba): no `visibilitychange`, relê o cartão
  (R-005), mostra no cartão o link *"Voltar à conferência do ‹documento›"* (UX-653) e leva o foco a
  ele; o link leva ao primeiro campo do formulário;
- **com recarga** (navegador que abriu na mesma aba, ou descartou a página): no carregamento, se há
  item guardado e o formulário dele está vazio, preenche-o com o que foi guardado, mostra a frase da
  restauração (UX-653) e o link de retorno, e leva o foco a ele. Nada é enviado.

O que se guarda é o que a pessoa digitou na gestão, e só na aba: `sessionStorage`, e não
`localStorage`, para não sobreviver ao fechamento numa máquina compartilhada. É apagado no registro
aceito e no fechamento da aba. O guardião `tests/test_armazenamento_no_navegador.py` é do portal e
não alcança a gestão; o motivo da escolha fica no comentário do script.

Na Mesa: a nota, o parecer e os campos da ficha do barema, pela mesma regra; o retorno é *"Voltar ao
documento ‹nome›"* e leva o foco à linha dele (FR-6547).

## R-011 — O carregamento e o tamanho (FR-6512, UX-644)

O link de abrir já traz o tamanho na Mesa (`documento.tamanho`); na conferência passa a trazer,
pela `tamanho_legivel` de `shared/arquivos.py`, lido do arquivo guardado no momento da leitura (o
mesmo `size` que o envio conferiu). O painel mostra *"Carregando o documento (‹tamanho›)…"* até o
evento `load` da moldura.

## R-012 — Teclado, foco e anúncios (FR-6523 a FR-6526)

- Abrir: foco no título do painel (`tabindex="-1"`), como hoje na Mesa.
- Fechar: foco no primeiro campo do formulário do item aberto — na Mesa, como hoje.
- Painel: `<aside>` com `aria-labelledby` no título; a moldura com `title` *"‹documento›, versão N —
  ‹pessoa›"*. Nada prende o foco.
- Uma região viva (`role="status"`, `aria-live="polite"`) por página, onde o script escreve
  *"Carregando…"*, *"Aberto por você: ‹documento›, versão N."* e a confirmação. A recusa recebe o
  foco, como hoje (`role="alert"`, `tabindex="-1"`).
- 320 px e 200 %: a página dos documentos já não rola na horizontal; o que muda é a folha nova do
  painel, que só vale acima de `64rem`.

## R-013 — CSP e folhas (FR-6531)

Nenhum estilo nem script no template. As regras do painel saem de `gestao/telas.css` (onde estão as
da Mesa) para `interface/grupos/visualizador.css`, carregada pelas duas telas pelo bloco
`estilo_da_pagina`; as classes novas da conferência entram em `telas/convocacao-documentos.css`. Os
guardiões que exigem regra para toda classe citada (`test_acessibilidade`, `test_estaticos`) leem
essas folhas; o comentário das folhas não escreve `}}`, `%}`, `<a>` nem *checkbox*.

## R-014 — Consultas e orçamento

A página dos documentos não ganha consulta por item: o tamanho dos arquivos vem com as apresentações
(`select_related` do documento da inscrição; o `size` do arquivo é lido do armazenamento local, sem
banco). As rotas novas (cartão, lista da Mesa, pedido de aviso) leem uma convocação ou uma inscrição.
Os guardiões de `tests/performance/` não mudam de número; o da página dos documentos é conferido.

## R-015 — Onde os arquivos se cruzam com as specs em paralelo

- **`154`** (plano mergeado no #484; implementação em sessão própria): toca `interface/views.py`
  (`ROTULO_DO_ITEM`), `conducao_da_convocacao.py` (o passo `REENVIADO` e `frase_da_pendencia`),
  `convocacao_documentos.html` (a contagem do resumo) e `avisos/application/pendencias.py`
  (`COMPLEMENTADA`). Esta toca `frase_do_aviso` (outra função), move o `<article>` para um parcial
  (onde está o rótulo do item) e acrescenta parâmetros a `selecionar` e `avisar_pendencias`. Quem
  entrar depois refaz o merge: o rótulo do item passa a viver no parcial, e a contagem fica na
  página.
- **`152`** (implementação em curso, sem branch no remoto em 11/11): toca as views de convocar, corte
  e desfecho e o cartão da convocação. Sem região em comum com esta, salvo o arquivo `views.py`.
- **`150`** (plano no #483): o portal. Sem arquivo em comum.
- Antes da validação final, a `main` atualizada entra nesta branch e os conflitos se resolvem
  preservando os requisitos de cada incremento (orientação do usuário de 11/11).
