# Research: Convocar e publicar num gesto só (159)

## D-001 — O que esta spec substitui

Evolução deliberada pedida pelo usuário em 12/11/2026. Ficam substituídos:

| De onde | O que dizia | O que passa a valer |
|---|---|---|
| `149`, a decisão da declaração do veículo no ato de publicar, e a FR-5703 | a declaração é campo da página de publicação | ela também está na conferência de convocar, quando o veículo escolhido é o GPS (FR-6809) |
| `149`, a FR-5727 e a FR-5731 | publicar é percurso próprio: a página do Edital, e o "Publicar no GPS" das pendentes | publicar é consequência da confirmação de convocar (FR-6801); a página continua para o pendente (FR-6814) |
| `149`, o achado 3 do roteiro de 12/11 | "publicar não é automático, e isso é de propósito" | revisto pelo usuário: o ato aconteceu, e a relação é consequência dele |
| `140`, o botão da conferência dos titulares | *"Convocar as N e enviar N mensagens"* | o botão diz as três consequências (FR-6803) |
| `125`, a convocação por publicação como "aguardando a publicação" em todo caso | o sistema não publica; a comissão registra | com o GPS como veículo, a publicação é a própria confirmação; fora dele, como antes (FR-6810) |

Nada da semântica de prazo muda: o prazo continua correndo da comunicação bem-sucedida, nas duas
formas (a decisão de prazo por canal da `149`).

## D-002 — A conferência dos titulares é a conferência única

A `140` já tem a conferência antes de convocar, no mesmo endereço do gesto, sem gravar nada, com a
confirmação que leva a assinatura do alcance e o resumo do texto conferido. Esta feature acrescenta a
ela o que será público, o veículo, a declaração, a autoridade e o botão que diz as consequências — e
não cria tela nova. O veículo, a autoridade e a declaração são escolhidos **na própria conferência**, no
formulário que confirma — não há o que mudar entre vê-los e confirmá-los —, e por isso não entram no
resumo do texto conferido, que continua cobrindo o fundamento, o prazo e as mensagens.

## D-003 — O núcleo da publicação, extraído e reutilizado

`publicar_convocados` (149) faz duas coisas: confere a prévia do Edital e grava o ato. A gravação —
o ato, a comunicação de cada *convoca*, os vínculos, o documento e a trilha — passa a uma função que
recebe a prévia já calculada e roda dentro de um `comando_de_comissao` aberto por quem chama. A prévia
ganha um filtro por convocações: a publicação de um gesto considera **só** as convocações daquele
gesto (FR-6815), com a mesma avaliação de efeito da `149`.

## D-004 — No GPS, convocar e publicar são uma transação

Na forma por publicação com o GPS como veículo, a publicação nasce dentro do mesmo `comando_de_comissao`
que cria as convocações, no mesmo `now`. Não há efeito externo a proteger de `rollback`, e a
atomicidade é o que garante a FR-6809: nenhuma convocação "aguardando publicação" sobra de uma
confirmação que publicaria. As validações que poderiam recusar a publicação — declaração, autoridade
— são feitas antes de gravar a primeira convocação.

## D-005 — Na mensagem, a publicação vem depois dos envios, em transação própria

A decisão de envio depois do `commit` da `050` continua: o SMTP não roda dentro da trava. A
publicação informativa vem depois, num `comando_de_comissao` próprio com a chave derivada
`‹chave do gesto›:publicar`, e só com as comunicadas com sucesso. Falhou a publicação, as convocações
e as mensagens ficam (FR-6812); repetir a confirmação com a mesma chave reaproveita o que já
aconteceu e completa a publicação (FR-6813).

## D-006 — O veículo é escolhido, nunca presumido

Na forma por publicação, a conferência oferece *"Na página pública do GPS"* e *"Fora do GPS"*, sem
nenhum marcado. O comando, sem veículo informado, mantém o comportamento de hoje (fora do GPS): é o
que preserva as chamadas feitas por outros caminhos e não presume o GPS.

## D-007 — A publicação externa registrada também divulga

O gesto das pendentes por publicação já registra, pessoa a pessoa, a referência externa. Ele ganha a
autoridade e, depois dos registros, publica a relação informativa das registradas (o efeito *divulga*
da `149`), que cita a referência. O mesmo gesto, na mensagem, reenvia as que falharam e publica as
que saírem (FR-6807).

## D-008 — Uma publicação por gesto

Cada confirmação que publica gera uma publicação numerada. Agrupar por dia exigiria rotina agendada e
deixaria a relação fora do ar até ela rodar; o pedido é a relação publicada ao confirmar.

## D-009 — A chamada individual e a correção, pelo mesmo formulário de hoje

`convocar_view` atende a chamada da fila, a regularização e a correção. Os três ganham, por um
parcial comum, a autoridade, o veículo (na forma por publicação), a declaração e a frase do que será
público, e o botão que diz as consequências. A conferência antes de chamar uma pessoa da `152` (PR
#502) é tela própria; quando ela entrar, estes campos vão para ela — o comando já os recebe.

**Cumprido no merge com a `main`, em 12/11** (#502 mergeado antes do #504): a chamada da fila e a
regularização passam pela conferência compartilhada (`convocacao_conferir.html`), que ganhou a seção
«Na página pública da seleção» para os dois casos, e os botões por veículo nomeiam a pessoa. O
formulário da tela da convocação voltou a ser só "Conferir antes de convocar"; a correção, que não
tem a conferência da `152`, continua com o parcial no próprio cartão.

## D-010 — Sem autoridade informada, o comando não publica

O comando de convocar continua aceitando a chamada sem autoridade — é o que mantém os demais caminhos
e a suíte —, e então não publica. A interface sempre a pede: é ela que garante a FR-6801 a quem
confirma pela conferência.

Sem autoridade vigente na unidade, porém, a tela não tem o que pedir, e o botão que prometia publicar
terminaria em silêncio. Por isso o resultado diz que a relação não foi publicada e por quê — "nenhuma
autoridade signatária foi escolhida" —, e aponta a seção «Na página pública da seleção» (revisão do
PR #504).
