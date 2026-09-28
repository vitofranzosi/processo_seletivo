# Research — 049 · Operar o resultado por marco

*Medido contra `28b3815b`. Cada decisão tem a alternativa descartada. As decisões de domínio `D-001` a
`D-005` estão na [spec](spec.md); as de desenho são `R-n`.*

## R-1 — O gesto chama os comandos de hoje, um por recorte, cada um na sua transação

**Decisão.** O gesto é um laço sobre os recortes do alcance. Para cada um, chama o comando de domínio
que a tela do recorte chama: `emitir_ordem`, `emitir_corte`, `emitir_apuracao` e
`publicar_resultado`. Cada chamada abre a própria transação (`command_context`), toma a trava do
Processo, reautoriza e grava. O projeto não usa `ATOMIC_REQUESTS`, e por isso o que um recorte grava
já está confirmado quando o seguinte começa.

**Por quê.** A `FR-820` pede o mesmo ato, e o jeito de garantir isso é não escrever outro caminho de
gravação. A `FR-823` pede que a recusa de um recorte não desfaça os outros, e transação por recorte é
exatamente isso: uma recusa desfaz só a transação dela.

**Descartado.** *Uma transação para o gesto inteiro*: a primeira recusa desfaria tudo, que é o que a
`FR-823` proíbe. *Um comando de domínio novo "emitir o marco"*: duplicaria as validações de quatro
comandos, e a primeira que mudasse num deles deixaria o outro para trás.

## R-2 — O coordenador mora em `interface/`, como a Supervisão

**Decisão.** A derivação do indicador e o laço do gesto moram em `interface/conducao_do_marco.py`.

**Por quê.** O gesto atravessa três apps: `classificacao` (ordem e corte), `ocupacao` (apuração) e
`divulgacao` (publicação). A dependência entre eles tem sentido único, e ela é verificada por teste:
`tests/test_dependencia_da_ocupacao.py` proíbe a ocupação de importar a emissão da ordem, e a
classificação não lê a apuração. Pôr o laço em qualquer um dos três obrigaria a importar o que a
fronteira proíbe. A camada que já lê os três é a da interface: é onde vivem a Supervisão
(`interface/supervisao.py`) e o conjunto de ações (`interface/acoes.py`). O coordenador **não
decide** nada de domínio: ele pergunta ao domínio, mostra, e chama o comando.

**Descartado.** *Um app novo*: seria um app sem modelo, só para abrigar um laço.

## R-3 — A conferência de cada recorte viaja com o gesto, e é conferida pelo comando

**Decisão.** A conferência compõe, para cada recorte do alcance, a mesma assinatura que a tela do
recorte compõe hoje:

| Operação | Assinatura | Quem confere na gravação |
|---|---|---|
| Ordem | `assinatura_da_proposta` (`classificacao/application/emissao.py`) | `emitir_ordem` |
| Corte | `assinatura_da_proposta` (`classificacao/application/emissao_do_corte.py`) | `emitir_corte` |
| Publicação | `assinatura_da_previa` (`divulgacao/application/publicar.py`) | `publicar_resultado` |
| Apuração | **nova**, no coordenador — ver `R-4` | o coordenador, sob a trava |

O formulário da confirmação carrega um par *(recorte, assinatura)* por recorte do alcance, e só esses
recortes são praticados (`SC-303`). Um recorte que o formulário traga e que não seja recorte do marco
pela derivação única é recusado com 404, como na tela de hoje (`normalizar_recorte`).

**Por quê.** As três assinaturas já existem e já cobrem o mundo que muda entre ler e confirmar (a
ordem, o ato vigente, a geração, a cadeia de publicações). Recompô-las no coordenador seria uma
segunda definição de "o que foi conferido".

**Consequência.** O gesto nunca sucede nada: a assinatura da ordem e a do corte incluem o vigente
lido, que no alcance é sempre nenhum (`FR-816`), e o gesto passa motivo vazio, que os três comandos
recusam na sucessão. Um recorte que ganhou ato entre a conferência e a confirmação é recusado com a
razão que o comando dá (`FR-821`).

## R-4 — A apuração não tem assinatura hoje; o gesto confere o que ela lê, sob a mesma trava

**Decisão.** `emitir_apuracao` não recebe confirmação: ela apura o que houver. Para a `FR-821`, o
coordenador compõe uma assinatura do que a apuração vai ler — o ato de ordenação vigente, as faixas
da geração vigente, a apuração vigente (nenhuma, no alcance) e a versão normativa vigente — e, na
confirmação, abre uma transação, toma a trava do Processo, recompõe a assinatura e só então chama
`emitir_apuracao`, que roda aninhada (ponto de salvamento) e toma a mesma trava sem esperar.

**Por quê.** Sem isso a apuração seria o único ato do gesto sem conferência, e ela é o que a
convocação consome. Mudar a assinatura do comando `emitir_apuracao` mexeria numa porta da `016` que
a tela de hoje usa sem conferência, e que esta feature não pediu para mudar.

**Descartado.** *Conferir fora da trava*: entre a conferência e a gravação, outra emissão poderia
suceder a ordem. *Acrescentar `confirmacao` a `emitir_apuracao`*: mudaria o contrato do comando para
todos os chamadores.

## R-5 — Chave por recorte, derivada da chave do gesto

**Decisão.** A chave do gesto nasce na conferência (GET-like: o POST sem `confirmar`), vai em campo
oculto, e a chave de cada recorte é `marco:<chave>:<operação>:<recorte ou "ampla">` (≤ 128
caracteres, o limite de `IdempotencyRecord.key`). A identificação comum da `FR-825` é o
`correlation_id` `gesto-<chave>`, que cada comando já grava na trilha (`RegistroAuditoria`, 100
caracteres).

**Por quê.** Repetir o envio repete cada chave, e cada comando devolve o desfecho da primeira vez
(`FR-822`). O recorte recusado não reservou nada — a reserva morreu com a transação —, e a repetição
o tenta de novo, com a mesma assinatura, e ele é recusado de novo pelo mesmo motivo.

**Descartado.** *Uma chave só para o gesto*: todos os recortes da ordem usam a mesma operação
(`classificacao:emitir`) e payloads diferentes, e uma chave comum daria `idempotency_conflict` no
segundo recorte.

## R-6 — O indicador tem duas profundidades

**Decisão.**
- **Na página do Edital** (`UX-090`), o resumo é de **presença**: um recorte está *feito* numa
  operação quando tem ato vigente nela; na publicação, quando a publicação vigente é do ato vigente.
  São quatro consultas para o Edital inteiro, qualquer que seja o número de marcos (`SC-305`), mais a
  que a página já fazia para os atos vigentes.
- **Na tela do marco** (`UX-091`), o estado é **completo**, com *obsoleto*: pergunta-se, por recorte,
  o que as telas de recorte perguntam — `estado_do_marco`, `estado_do_corte`,
  `causas_de_obsolescencia` e `divulgacao_do_ato`. São até ~5 recortes por marco.

**Por quê.** A obsolescência da ordem é um recálculo, e a Supervisão já registrou o custo de
chamá-la em varredura (`interface/supervisao.py`, `atos_obsoletos`). A página do Edital lista todos
os marcos; a tela do marco lista um. O que envelhece continua sinalizado na Supervisão (`UX-004`,
`UX-065`, `UX-066`), e o resumo diz *"com ato vigente"*, não *"completo"*.

**Descartado.** *Estado completo na página do Edital*: 64 recálculos a cada abertura.

## R-7 — O gesto de publicar usa a porta de publicar; os outros três, a da gestão

**Decisão.** As rotas dos quatro gestos são separadas: ordenar, cortar e apurar passam por
`_edital_para_classificar(somente_gestao=True)`; publicar passa por `_edital_para_publicar`. A tela
do marco abre para quem abre qualquer das duas famílias (`FR-830`) e oferece a cada pessoa só os
gestos da porta dela, com a frase de a quem pedir montada pelo mecanismo único (`frase_do_aviso`).

**Por quê.** É a segregação que a `017` fixou: quem emite o ato não ganha, por tê-lo emitido, o poder
de divulgá-lo. A tela do marco não pode ser o lugar onde as duas autoridades se fundem.

## R-8 — Marco de sorteio

**Decisão.** O indicador lê os atos vigentes do marco de sorteio pelos recortes da derivação única, e
a célula da ordem leva à tela do sorteio. O gesto de ordenar não é oferecido (`FR-817`). Corte,
apuração e publicação funcionam como nos marcos computados.

**O recorte excedente do sorteio** — a Modalidade declarada como ampla, que o sorteio trata como
lista própria (`FR-491a`) — não entra no indicador nem no alcance. A divergência está registrada na
`034`, e esta feature não a reabre.

## R-9 — A publicação em lote aplica a natureza, a autoridade e a declaração a cada recorte

**Decisão.** A conferência da publicação recebe a natureza e a autoridade, e afere cada recorte com
`aferir_publicabilidade(..., natureza=...)`, como a prévia. Entra no alcance o recorte cujo ato
vigente não está divulgado **naquela natureza** e cuja aferição não impede. Na definitiva, a
declaração é pedida uma vez, e vai só às publicações cujo ato não tem janela computável.

*Revisto em 28/09, depois do merge da `main` com a RC-121:* a janela deixou de ser do marco
(`janela_declarada`, removida) e passou a ser do ato (`janela_do_ato`), porque o ato divulgado segue
a versão que cita. Num mesmo marco, um ato pode ter janela e outro não, e a declaração enviada ao
primeiro seria recusada pelo comando. A pergunta é feita por recorte, na conferência e de novo na
gravação. O
preliminar pedido sobre recorte com definitiva fica fora, com a razão da ordem das naturezas.

**Ato de recorte vazio** (`D-003`): a projeção de um ato sem posições é uma lista vazia, e o
documento diz que ninguém concorreu. A conferência mostra *"ninguém concorreu"*.

## R-10 — O desfecho sobrevive ao redirecionamento; o indicador é a verdade

**Decisão.** O desfecho do gesto vai para a sessão e é mostrado uma vez na tela do marco, pelo
padrão POST-redirect-GET das telas de hoje. Perdida a sessão, o indicador diz o que foi feito,
porque ele lê os atos gravados (`FR-824`, `SC-302`).

## R-11 — A porta da tela do marco e o inventário das negativas

**Decisão.** A tela do marco resolve a porta pela mesma gramática das portas que existem
(`require_authorization_base` com as bases das duas famílias), e toda recusa `404` nova ganha linha
no inventário das negativas da `033` (`tests/test_gramatica_das_portas.py`).
