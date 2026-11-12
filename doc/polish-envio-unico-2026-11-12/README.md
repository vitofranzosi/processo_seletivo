# Envio dos documentos da convocação: um botão só — 12/11/2026

Revisão da D-001 da `150`, por decisão do usuário, depois da implementação (#496). As mudanças de
requisito estão na spec (FR-5601, FR-5613, UX-500 revistas; FR-5620 a FR-5622, UX-505 e SC-1808
novos) e a razão em `research.md`, D-001.

## O problema

Com dois arquivos escolhidos, cada cartão mostrava o mesmo botão verde, *"Enviar os 2 documentos
escolhidos"*: duas entradas para uma operação só, lidas como o envio de cada cartão. E escolher um
arquivo não se distinguia de enviá-lo — o cartão continuava "Falta enviar." com um nome em negrito ao
lado do botão de escolher.

## O que mudou

- **Um seletor por documento, um botão de envio só**, numa área cinza no fim do bloco *O que falta*
  (ou de *O que você já apresentou*, quando só há substituição): *"2 de 4 arquivos selecionados"*,
  *"Os arquivos ainda não foram enviados à comissão."* e *"Enviar 2 documentos"*. Sem escolha, o botão
  fica indisponível e a área diz o que fazer.
- **O cartão diz o que foi escolhido, e que ainda não foi enviado**: o nome do arquivo e
  *"Selecionado — ainda não enviado."* numa caixa cinza, sem verde nem marca de concluído; o seletor
  vira *"Trocar arquivo"*, e *"Remover a escolha"* aparece ao lado (FR-5603, que estava pendente).
- **O limite do arquivo é dito uma vez**, na frase antes dos cartões; em cada cartão ele continua na
  descrição acessível do campo.
- **Envio parcial continua**: um documento só também se envia, pelo mesmo caminho.
- **Sem script, nada muda**: cada cartão envia o seu, e uma frase em `<noscript>` diz que o envio é um
  de cada vez (FR-5612, que estava pendente).
- **Defeito corrigido no caminho** (FR-5622): a volta do lote é `?lote=N#…`, e dois envios seguidos do
  mesmo tamanho voltavam ao endereço em que a página já estava — o navegador só rolava a tela, com o
  progresso à mostra. Com o botão único, enviar um documento e depois outro era o caso comum.

Nenhuma regra, view, modelo ou migration mudou. A projeção ganhou três propriedades de leitura
(`envio_no_que_falta` e `envio_no_que_ja_apresentou`, que dizem onde a área mora, e
`um_so_com_envio`, que põe a frase no singular).

## Rodada de polish (mesmo dia, depois da implementação)

Revisadas as capturas em todas as larguras e em mais quatro cenários da jornada do convocado
(`tests/fixtures/jornada_do_convocado.py`): F (uma pendência de correção e um a enviar), J (pendência
sem arquivo, e substituição abaixo do botão), E (tudo enviado: a área em *O que você já apresentou*)
e L (só um opcional). O que mudou:

- **"2 de 2" conta a pendência.** O "de M" contava só os cartões sem arquivo recebido, e a pendência
  de correção — que é uma tarefa, mas tem arquivo — ficava de fora: no F, dois escolhidos davam
  "2 arquivos selecionados". Agora o servidor marca a tarefa no cartão (`data-tarefa`).
- **"Falta enviar." sai de vista com a escolha**, e continua na descrição acessível do campo — era o
  ponto que a primeira rodada tinha deixado. Só no cartão sem arquivo e sem pendência: a frase da
  pendência traz o motivo da comissão, e fica.
- **"Ir ao botão de envio" numa linha própria.** Colado à frase, o link quebrava no meio ("Ir para
  o / envio") a 1280 px.
- **A área sem escolha ficou leve**: contorno tracejado, sem fundo e sem "Nenhum arquivo
  selecionado" — a caixa cinza pesava como aviso antes de a pessoa fazer qualquer coisa.
- **A frase no singular** quando só um cartão tem envio.
- **Foco pelo teclado** conferido nos controles novos ("Remover a escolha", o botão de envio, o link):
  o contorno verde da folha comum (`*:focus-visible`) vale para todos.

Ficou como estava: a altura igual dos cartões na mesma linha (do polish #505) deixa um cartão vazio
alto ao lado de uma pendência aberta, no F e no J a 1280 px. Mexer nisso é decisão sobre a grade da
tela inteira, e não do envio.

## Capturas

Convocação com quatro documentos, `documentos_do_aluno` da `115`. Em cada largura: nada escolhido;
dois escolhidos; e, a 390 e 1280 px, o envio de três com uma imagem no lugar do PDF — *"Recebemos 2
de 3 documentos"*, o link ao cartão do que não chegou e a recusa nele.

| Cena | 390 | 768 | 1280 | 1440 |
|---|---|---|---|---|
| Nada escolhido | antes / depois | antes / depois | antes / depois | antes / depois |
| Dois escolhidos | antes / depois | antes / depois | antes / depois | antes / depois |
| Depois do envio | antes / depois | — | antes / depois | — |
| F: pendência, nada escolhido (`4-…`) | antes / depois | antes / depois | antes / depois | antes / depois |
| F: pendência e a enviar escolhidos (`5-…`) | antes / depois | antes / depois | antes / depois | antes / depois |
| E: tudo enviado, uma substituição (`8-…`) | antes / depois | — | antes / depois | — |
| L: só um opcional (`9-…`) | antes / depois | — | antes / depois | — |
| J: substituição abaixo do botão (`10-…`) | antes / depois | — | antes / depois | — |

Os arquivos são `‹cena›-‹largura›-‹antes|depois›.jpg`. No "antes" da terceira cena, o envio foi
pelo botão de um cartão, que levava os três pelo lote.

## O que fica para o usuário

- **A compactação dos cartões** foi só a da caixa da escolha, do limite e da frase de estado; o
  polish de 12/11 (#505) já tinha reorganizado o resto da tela, e a grade de altura igual é dele.
- **SC-1805**, a validação com pessoas, continua aberta.
