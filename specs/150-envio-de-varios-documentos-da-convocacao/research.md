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
