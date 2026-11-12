# Contrato das telas e rotas: Conferência com o documento à vista

As rotas são da gestão (`/gestao/`); a porta de cada uma é a de hoje para o mesmo objeto. Toda
resposta HTML segue sob a CSP da `091`.

## Rotas

| Método e caminho (sob `editais/<edital>/marcos/<marco>/convocacao/<convocacao>/`) | Novo? | Resposta |
|---|---|---|
| `GET documentos` | não | a página, com o painel e o formulário por htmx |
| `GET documentos/<apresentacao>` | revista | o arquivo, `inline`; `?baixar=1` como anexo; `?painel=1` muda só a forma da recusa; `X-Frame-Options: SAMEORIGIN`; consulta gravada ao fim da entrega |
| `GET documentos/itens/<item>/cartao` | **sim** | o cartão do item (parcial), 200; sem registro |
| `POST documentos/itens/<item>/conferencia` | revista | sem `HX-Request`: 302, como hoje. Com `HX-Request`: 200 com o cartão e os `hx-swap-oob` |
| `POST aviso-de-pendencia` | **sim** | sem `HX-Request`: 302 à página com a frase na sessão. Com `HX-Request`: 200 com a confirmação e a situação |

| Método e caminho (sob `minhas-etapas/<edital>/<etapa>/inscricoes/<inscricao>/`) | Novo? | Resposta |
|---|---|---|
| `GET documentos/<requisito>` | revista | o arquivo, como hoje; `?painel=1` muda só a forma da recusa |
| `GET documentos` | **sim** | a lista de documentos da inscrição (parcial), 200 |

## O registro com `HX-Request` (R-006)

| Caso | Status | Corpo | Cabeçalhos |
|---|---|---|---|
| aceito | 200 | cartão + `#situacao-da-convocacao` + `#pessoas-do-recorte` + `#confirmacao-da-conferencia` (oob) | — |
| recusado com cartão (sem abertura, motivo, versão superada) | 200 | cartão com a recusa e o preenchimento | — |
| recusado sem cartão (desfecho, Processo encerrado) | 200 | vazio | `HX-Refresh: true` |
| sem identidade | 200 | a frase da UX-646 | `HX-Retarget: #mensagem-<item>`, `HX-Reswap: innerHTML` |
| item inexistente ou fora do alcance | 404 | — | — |

## Os textos

| Onde | Texto |
|---|---|
| barra, linha 1 (UX-640) | *"‹documento› — versão N, apresentada em DD/MM/AAAA HH:MM"*; substituída: *"versão N, substituída pela versão M"* |
| barra, linha 2 (UX-640) | *"‹nome› · ‹inscrição›"* |
| link (UX-641) | *"Abrir"* + tamanho; nome acessível *"Abrir ‹documento›, versão N"* |
| alternativa (UX-643) | *"Este navegador não mostra o documento dentro da página. Abra em aba própria ou baixe o arquivo; a abertura fica registrada do mesmo jeito."* |
| carregamento (UX-644) | *"Carregando o documento (‹tamanho›)…"* |
| ajuda — arquivo que não abre (UX-645) | *"O arquivo não abre, ou abre em branco? Registre como pendente e diga no motivo que o arquivo não pôde ser lido."* |
| ajuda — a marca (UX-652) | *"«Aberto por você» quer dizer que o arquivo desta versão foi acessado por você nesta chamada. Não comprova que ele foi exibido nem lido."* |
| recusa sem abertura (UX-651) | *"A conferência não foi registrada: você ainda não abriu a versão N. Abra a versão N e registre de novo; o que você marcou continua aqui."* + *"Abrir a versão N"* |
| falha sem identidade (UX-646) | *"A conferência não foi registrada. Sua sessão terminou; entre de novo. O que você marcou continua aqui."* |
| falha de rede (UX-646) | *"A conferência não foi registrada. Não foi possível falar com o servidor; tente de novo. O que você marcou continua aqui."* |
| confirmação (UX-642, UX-647) | ver a UX-642 e a UX-647 da spec |
| pedido de aviso (UX-648) | *"Pedir aviso para ‹nome›"*; resposta *"Aviso solicitado; aguardando envio. A mensagem sai pelo despacho dos avisos, e não neste clique."* |
| recusa do pedido (UX-650) | *"‹nome› já foi avisado hoje nesta chamada. Um novo pedido poderá ser feito a partir de DD/MM/AAAA."*; nos demais motivos, *"O aviso não alcança ‹nome› agora: ‹motivo›."* |
| situação do aviso (UX-649) | *"Aviso solicitado em ‹data›; aguardando envio."* · *"Aviso enviado em ‹data›: aceito pelo servidor de correio."* · *"Aviso não enviado: ‹estado›."* |
| volta (UX-653) | *"Voltar à conferência do ‹documento›"*; Mesa: *"Voltar ao documento ‹nome›"*; restaurado: *"Restauramos o que você tinha marcado e digitado neste navegador. Nada foi registrado ainda."* |
| recusa no painel (UX-654) | a frase da recusa de hoje (FR-3605 da `115`, FR-3695 da `117`) |
