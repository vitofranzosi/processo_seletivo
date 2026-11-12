# Research: O envio de vários documentos da convocação (150)

## 1. O relato e o diagnóstico

O relato (11/11/2026), de uso da área do candidato: na convocação que pede documentos, a pessoa
escolhe os arquivos e clica depois em enviar, e "não dá certo"; é preciso subir cada arquivo
individualmente.

O diagnóstico veio da leitura do código, na `main` em `1b467b4f`:

- `portal/templates/portal/_cartao_do_documento_da_convocacao.html` põe **um formulário por cartão**,
  com campo de arquivo e botão "Enviar" próprios. Os formulários não se conhecem.
- `portal/views.py`, `apresentar_documento_da_convocacao`, lê **um** `arquivo` e redireciona para
  `#confirmacao` (aceito) ou `#item-‹id›` (recusado). A página inteira recarrega.
- O navegador não preserva a escolha de um campo de arquivo através de uma navegação: as escolhas
  dos outros cartões somem, e nada na tela diz isso.
- `portal/static/portal/arquivo.js` dá a classe `pronta` ao botão de **cada** cartão com arquivo
  escolhido: com quatro escolhas, quatro botões destacados.

Não é defeito do servidor — cada envio funciona como a `115` e a `121` especificaram. É defeito da
tela: ela convida a escolher tudo e enviar no fim, e descarta em silêncio o que a pessoa fez.

**O mesmo na inscrição.** `portal/templates/portal/_documentos.html` envia por htmx e troca o bloco
`#documentos` inteiro pela resposta; as escolhas dos outros cartões também somem. Ver D-004.

## 2. O limite que decide o desenho

O guia de implantação (`doc/implantacao-em-producao-ubuntu.md`, §14) limita o corpo da requisição em
`/selecoes/` — onde mora o portal — a 12 MB, dimensionado para **um** PDF de até 10 MiB
(`ARQUIVOS_CANDIDATOS_LIMITE_BYTES`). Um envio com todos os arquivos numa requisição só passaria do
limite com dois arquivos grandes e voltaria 413 do proxy, sem frase nenhuma do sistema. A gestão tem
limite de 60 MB porque a Retificação envia vários anexos num POST; o portal não tem.

## D-001 — Com dois ou mais escolhidos, todo botão de enviar envia todos, e diz isso

**Decisão.** Enquanto houver dois ou mais cartões com arquivo escolhido, o botão de enviar de cada um
deles diz "Enviar os N documentos escolhidos" e envia todos. Com um só, "Enviar", como hoje. Quem quer
mandar só um desfaz as outras escolhas por "Remover a escolha".

**Razão.** O botão fica onde a pessoa está olhando — no cartão em que ela acabou de escolher — e o
rótulo diz a verdade sobre o que vai acontecer. Não existe, em momento nenhum, um botão que envia um e
descarta os outros.

**Descartadas.**

- *Um botão único no fim da lista, e os dos cartões enviando só o seu.* Mantém o botão do cartão que
  descarta os outros, que é o defeito; e a 375 px o fim da lista fica várias telas abaixo.
- *O botão do cartão envia só o seu, sem recarregar a página, e as outras escolhas ficam.* Resolve a
  perda, mas não a expectativa: quem escolheu quatro continua precisando de quatro cliques, e a tela
  tem de atualizar "Andamento", blocos e confirmação sem navegar, contra a âncora sem script da `121`.
- *Só avisar antes de enviar que as outras escolhas se perderão.* Remove o silêncio, mas mantém o
  trabalho repetido; e um diálogo de confirmação a cada envio é ruído.

## D-002 — Um envio por documento, em sequência, e não uma requisição com todos

**Decisão.** O envio de vários é uma sequência de envios de um documento, na ordem da tela, cada um
pelo mesmo caminho do envio individual.

**Razão.** O limite de corpo do portal (§2) cabe um arquivo por requisição. Cada apresentação já é um
ato próprio na `115`, com validação, prazo e trilha próprios: a sequência preserva isso sem tocar o
domínio, e a falha de um não arrasta os outros. A queda de conexão no meio perde só o que faltava.

**Descartada.** *Um POST com todos os arquivos.* Pediria aumentar o limite do proxy só para o portal,
exposto à internet, e transformaria uma recusa parcial em resposta única a desmontar; a falha de
rede no meio perderia tudo.

## D-003 — Nada se envia ao escolher o arquivo

**Decisão.** Escolher o arquivo não o envia; o envio continua sendo um ato da pessoa.

**Razão.** Nada é excluído nesta base: o arquivo errado, uma vez enviado, vira apresentação
registrada, que a comissão vê e que só se substitui por outro envio. A pessoa precisa de um instante
para conferir o nome do que escolheu.

**Descartada.** *Envio automático ao escolher* — menos cliques, e um registro permanente por engano.

## D-004 — A inscrição fica fora, registrada como achado

**Decisão.** Esta spec cobre só a convocação. O mesmo defeito na lista exigida da inscrição fica
registrado aqui (§1) para decisão do usuário.

**Razão.** O relato foi da convocação, e governança é do usuário: achado encontrado no caminho vira
registro, não escopo. A inscrição envia por htmx e troca o bloco inteiro; o conserto lá é parecido,
mas não idêntico, e merece a própria decisão.

## D-005 — Sem script, uma frase, e não um formulário único

**Decisão.** Sem script, cada cartão envia o seu, como hoje, e a tela diz antes do primeiro cartão
que os documentos se enviam um de cada vez e que as outras escolhas não são guardadas.

**Razão.** Um formulário único sem script mandaria todos os arquivos numa requisição só, e esbarraria
no limite do §2. A frase remove o silêncio, que é o defeito, no caminho em que não há como enviar em
sequência.

## D-006 — O arquivo repetido entre documentos é avisado no cartão, e não bloqueado

*(Acrescentada em 2026-11-11, pelo achado 11 do estudo da jornada final,
`doc/estudo-jornada-final-2026-11-11/`, telas `B13-bernardo-enviou` e `C08-diploma-pendente`.)*

**Decisão.** Ao escolher um arquivo, o cartão compara o conteúdo com o escolhido nos outros cartões e
com o vigente dos outros documentos da convocação; sendo idêntico, diz com qual, antes do envio. O
envio continua possível, sem confirmação a mais. A regra de não bloquear é do usuário, na aprovação da
revisão (11/11/2026).

**Razão.** No estudo, o mesmo PDF foi aceito como diploma e como comprovante de residência; o servidor
conhecia o resumo SHA-256 dos dois e não disse nada, e o engano só apareceu na conferência, ao custo
de uma pendência, um aviso e um reenvio. O servidor já compara o resumo dentro do mesmo item — é a
frase *"Este arquivo já tinha sido recebido."* (`FR-3581` da `115`) —, e o que faltava era olhar para
os outros itens. O envio de vários torna o engano mais provável: quatro escolhas em sequência, na
mesma tela.

**Descartadas.**

- *Recusar o arquivo idêntico ao de outro documento.* Há documento legítimo que serve a dois itens — o
  mesmo PDF com diploma e histórico, pedidos em itens separados; a recusa empurraria a pessoa para
  dividir ou alterar o arquivo só para passar.
- *Pedir confirmação ("Enviar assim mesmo?").* Um diálogo a mais no caminho de quem enviou certo; o
  texto no cartão já está onde a pessoa olha, e o botão continua dizendo a verdade.
- *Avisar só depois do recebimento.* O arquivo já estaria registrado, e nada se exclui nesta base; o
  aviso antes do envio é o que poupa a rodada. O aviso depois, para o caminho sem script, ficou como
  pergunta ao usuário na spec.

## Fase 0 do plano

As decisões técnicas do plano, de 11/11/2026, sobre a `main` em `ef568113`. São do plano, e não da
spec: nenhuma muda requisito; mudam o como. Por isso se numeram `R-`, e não `D-`.

### R-001 — Um script novo, `varios.js`, e os de hoje sem mudança de comportamento

**Decisão.** Contagem, rótulo, "Remover a escolha", o envio em sequência e o aviso do arquivo repetido
moram num script novo, `portal/static/portal/varios.js`, carregado só pela convocação, **antes** de
`envio.js`. Ele escuta o `submit` **no próprio formulário** (que dispara antes do ouvinte de
`document.body` de `envio.js`) e:

- com N ≥ 2, cancela o envio nativo (`preventDefault` e `stopPropagation`) e conduz o lote;
- num cartão sem arquivo, cancela e escreve a frase de hoje no cartão (FR-5604);
- com N = 1, no cartão escolhido, não faz nada: o envio de hoje segue, com o progresso de `envio.js`.

`arquivo.js` continua o mesmo: já dá a classe `pronta` a cada botão com arquivo escolhido, que é o
destaque que a UX-500 pede para o "Enviar os N documentos escolhidos". `envio.js` continua o mesmo:
o `pageshow` dele já reabilita botões restaurados pelo "voltar", e o `varios.js` repete o cuidado
para o que ele mesmo mudou (rótulos, progresso).

**Razão.** `arquivo.js` e `envio.js` servem também à inscrição, que fica fora (D-004); mexer neles
arrastaria a inscrição para o escopo. A FR-5614 admite script novo.

**Descartadas.** *Estender `envio.js`*: misturaria o ramo do htmx da inscrição com o lote, e os
testes da inscrição passariam a depender dele. *Um formulário único na página*: esbarra no limite do
proxy (D-002, D-005).

### R-002 — O lote fala com a rota de hoje, por um cabeçalho, e recebe JSON

**Decisão.** Cada documento do lote é um `fetch` `POST` ao `action` do próprio formulário, com o
`FormData` dele (o `csrfmiddlewaretoken` incluso) e o cabeçalho `X-Envio-De-Varios: k/n` (posição e
total). Com o cabeçalho, `apresentar_documento_da_convocacao` responde **200 com JSON** — recebido,
já recebido ou recusado — em vez do redirecionamento; sem ele, responde como hoje. O 404 do comando
continua 404. O contrato está em [contracts/envio-de-varios.md](contracts/envio-de-varios.md).

**Razão.** O `fetch` segue o redirecionamento sozinho e entrega a URL **sem a âncora**: não haveria
como saber se a volta era `#confirmacao` ou `#item-…`. `redirect: "manual"` devolve resposta opaca,
sem `Location`. O JSON é o mesmo resultado que a sessão já guarda, dito ao script. Uma rota nova
duplicaria titularidade, CSRF e recusas.

**O acesso expirado.** Sem identidade na sessão, a rota redireciona ao acesso, e o `fetch` recebe a
página de acesso com 200 e `text/html`. O script trata **toda resposta que não seja JSON** como
falha do lote: a 404, o acesso expirado; as demais, a frase genérica de hoje (FR-5610). O 413 do
proxy cai aqui também — o lote para, e a frase diz o que chegou e o que não.

### R-003 — A sessão acumula o lote, e a volta o lê de uma vez

**Decisão.** As duas chaves de hoje (`confirmacao_da_convocacao` e `recusa_da_convocacao`) passam a
guardar **listas**: os envios recebidos (`item_id`, `apresentacao_id`, `ja_recebido`) com o total
tentado, e as recusas (`ancora`, `frase`). A posição `1/n` zera as duas; cada resposta acrescenta a
sua. O envio individual grava a mesma forma, com um elemento e total 1. A leitura aceita também a
forma antiga, de um elemento só, para a sessão aberta durante a implantação.

**Razão.** A confirmação depende da projeção **depois** do último envio — a próxima tarefa, a
conclusão —, e a projeção é do servidor. Montar a confirmação no navegador repetiria regra da `121`
em JavaScript. A sessão já é o canal da volta (`_da_inscricao`), com a guarda de inscrição.

**A queda no meio.** O que chegou fica na sessão, e a próxima abertura da convocação mostra a
confirmação parcial — verdadeira: aqueles documentos foram recebidos. O script, enquanto isso, não
sai da página (FR-5610).

### R-004 — A volta do lote é uma navegação, com as listas

**Decisão.** Terminado o lote, o script navega para a URL `volta` que a última resposta JSON trouxe:
`…/convocacao/?lote=n#confirmacao` com algum recebido, ou `…?lote=n#item-‹primeiro recusado›` sem
nenhum (FR-5608, FR-5609). O parâmetro só força a navegação — sem ele, ir da página para a mesma
página com outra âncora só rolaria a tela, sem recarregar — e a view o ignora. A confirmação lista os
recebidos e conta os recusados, com link para o cartão de cada um; cada cartão recusado traz a sua
recusa; `recusa.js` foca a primeira da página, que é a do primeiro recusado.

**Razão.** Recarregar é o que atualiza "Andamento", blocos e cartões sem reescrever a tela no
navegador, e mantém a âncora e o foco que a `121` já resolveu para o envio de um.

**Descartadas.** *`location.reload()` com a âncora trocada*: o navegador restaura a rolagem anterior
em vez de ir à âncora. *Atualizar a tela no lugar*: a D-001 já a descartou.

### R-005 — O resumo vigente vem do *prefetch* de hoje

**Decisão.** O cartão de todo item com apresentação vigente — com ou sem envio possível — ganha
`data-resumo-recebido="‹content_hash da vigente›"` e `data-documento="‹nome›"`. O valor vem de
`item.lido.vigente.content_hash`, que a projeção já carrega. A apresentação aproveitada da inscrição
tem o mesmo resumo da origem — o gatilho da `0005` da convocação o exige —, e entra sem caso próprio.

**Razão.** Nenhuma consulta nova; o teste de contagem de consultas da convocação prova.

### R-006 — O resumo no HTML não é dado novo

**Decisão.** Expor o resumo SHA-256 do arquivo vigente na página do próprio titular.

**Razão.** A página já oferece o próprio arquivo ("Ver o arquivo recebido"); o resumo não revela o
conteúdo e só confirma a coincidência a quem já tem o mesmo arquivo. A página é da sessão do titular;
a tarefa de implementação confere o `Cache-Control` dela e registra o que encontrar. Nada é gravado
no navegador pelo script (FR-5611).

**Descartada.** *Perguntar ao servidor a cada escolha* — enviaria o resumo ao escolher, contra a
D-003 e a FR-5618, e custaria uma requisição por escolha.

### R-007 — Sem script, `<noscript>`; o que só funciona com script nasce oculto

**Decisão.** A frase da FR-5612 fica num `<noscript>` antes do primeiro cartão com envio. O botão
"Remover a escolha" e a região do aviso do arquivo repetido vêm no HTML com `hidden`, e o script os
revela. O rótulo "Enviar os N documentos escolhidos" é escrito pelo script; o HTML continua com
"Enviar".

**Razão.** `<noscript>` não é script e passa pela CSP; a frase não pisca nem depende de script para
sumir. Um botão que sem script não faz nada não pode estar à vista.

### R-008 — O resumo no navegador, por `crypto.subtle`

**Decisão.** Ao escolher, o script lê o arquivo (`file.arrayBuffer()`) e calcula
`crypto.subtle.digest("SHA-256", …)`, em hexadecimal minúsculo, como `shared.arquivos.resumo`. O
resultado fica em memória, preso ao campo, e é descartado se a escolha mudou enquanto o cálculo
corria. Sem `crypto.subtle` — contexto não seguro, navegador antigo — ou com erro de leitura, não há
aviso (FR-5619). O envio nunca espera o cálculo.

**Razão.** Sem biblioteca nova (FR-5614); disponível em todo navegador atual sob HTTPS e em
`localhost`. Dez megabytes cabem na memória de um celular, e o cálculo é da ordem de dezenas de
milissegundos.
