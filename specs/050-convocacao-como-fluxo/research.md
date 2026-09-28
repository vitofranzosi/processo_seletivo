# Research: A convocação como fluxo

Decisões técnicas da `050`, conferidas contra a `main` em `28b3815b`. As `D-001` a `D-004` estão na
[spec](spec.md); estas continuam a numeração.

---

### D-005 — A apuração seguinte é emitida junto com o desfecho, e nunca quando moveria vaga

**A pergunta do usuário:** *"a apuração seguinte emitida junto com o desfecho que a torna obsoleta, ou
derivada. Decida no plano, com o custo de cada caminho."*

**O que existe.** Todo desfecho escreve um efeito na porta da `016`
(`convocacao/application/desfechar.py`, `porta_de_efeitos.registrar_efeito`). A apuração vigente passa
a ter a causa `efeito_posterior` (`ocupacao/application/selectors.py`, `causas_de_obsolescencia`), e
`convocar` recusa com `apuracao_obsoleta` (`FR-266`) até alguém emitir a seguinte na tela da ocupação.
A emissão não pede decisão nenhuma: o único campo é o motivo da sucessão
(`ocupacao/application/emissao.py`). Mas ela pode **mover vaga**: quando a cota não tem mais quem
ocupar, a emissão grava a reversão que o Edital declarou (`movimento_de_vaga.gravar_reversao`).

**Três caminhos, com o custo de cada um.**

| | A. Emitida com o desfecho | B. Derivada, sem ato | C. Emitida com a convocação seguinte |
|---|---|---|---|
| **O que é** | O ato do desfecho, individual ou em lote, emite a apuração sucessora na mesma transação, com o mesmo autor, quando a única causa de obsolescência é `efeito_posterior` | A convocação lê o número ao vivo — apuração vigente mais os efeitos posteriores — e a recusa por `efeito_posterior` deixa de existir | A convocação, ao encontrar a apuração obsoleta só por efeito, emite a sucessora antes de convocar |
| **`FR-266` e `FR-294`** | intactas: convoca-se sobre ato vigente, que cita os efeitos que leu | **quebradas**: a convocação cita uma apuração cujo número não é o que a motivou; reconstruir exige congelar os efeitos lidos numa coluna nova da `Convocacao`, append-only | intactas |
| **Reversão** | tratável: ver abaixo | **errada**: a reversão só acontece na emissão, e o número derivado ignora a vaga que a cota cederia | tratável, mas a chamada individual passaria a esconder um segundo ato |
| **Custo em linhas** | uma apuração por desfecho individual, uma por gesto de não atendimento. No 28/2026, ~100–300 linhas a mais, com `efeitosLidos` crescendo por recorte (dezenas de ids) | nenhuma linha; uma coluna nova e uma migration em tabela append-only | uma por rodada de convocação |
| **Tela da ocupação** | fica em dia a cada desfecho | continua mostrando a apuração obsoleta, com números que já não são os da convocação | fica obsoleta entre o desfecho e a chamada seguinte |
| **Código** | uma função na `016` que emite **dentro** da transação de quem chama, sem movimento; um passo no fim de `desfechar` | recusa relaxada, leitura nova, migration | a chamada individual ganharia prévia de números, que hoje ela não tem |

**Decisão: A**, com duas condições que a tornam segura:

1. **Só quando a única causa é o efeito.** Depois de registrar o efeito, o ato relê as causas; se
   houver qualquer outra — ordem sucedida, corte obsoleto, quadro retificado, movimento posterior —, não
   emite nada, e a tela continua dizendo o que diz hoje (`FR-884`). Uma apuração obsoleta por outra
   razão é um fato que alguém precisa ver, e não algo que o desfecho deva varrer para baixo do tapete.
2. **Nunca quando a conta moveria vaga.** A função nova calcula a apuração e, se ela cederia vaga da cota
   pela reversão, **não grava nada** e devolve o motivo. A tela diz que a apuração seguinte, com o
   movimento, é emitida na ocupação (`FR-885`). Mover quantidade entre recortes continua sendo ato que
   alguém pratica na tela da `016`, e a varredura de `test_dependencia_da_convocacao.py` continua
   verdadeira na letra e no espírito: nenhum módulo da convocação grava movimento (`FR-270`).

**A recusa da emissão não desfaz o desfecho.** A emissão roda num *savepoint*; uma recusa dela
(`empate_na_fronteira_do_alvo`, `sem_quadro_publicado`) deixa o desfecho gravado e a apuração
obsoleta, com a causa — que é exatamente o comportamento de hoje. O desfecho é decisão sobre uma
pessoa, e uma conta que não fecha não pode impedi-lo.

**O que a `019` dizia, e continua dizendo.** A `FR-276` manda a liberação tornar obsoleta a apuração
vigente; a `FR-278`, excluir *"na emissão seguinte"* sem alterar a apuração emitida. As duas continuam
verdadeiras: a apuração anterior não é tocada, deixa de ser a vigente e fica legível no histórico; a
emissão seguinte só acontece mais cedo, pelo mesmo código, com o mesmo autor e com o motivo derivado
(*"efeito de N desfecho(s) de convocação registrado(s) neste ato"*).

**Alternativas recusadas:** B, porque quebra a proveniência e erra na reversão; C, porque mistura dois
atos na chamada individual e deixa a tela da ocupação envelhecida entre um e outro.

---

### D-006 — O gesto é um comando só; a comunicação vem depois dele, por pessoa

O ato em lote roda num único `comando_de_comissao`, com uma chave de idempotência, e grava N
`Convocacao` e N linhas de trilha. A transação trava o Processo, como toda convocação.

**A comunicação não pode estar dentro dela**, pela razão que `comunicar.py` já escreve: o envio
acontece fora da transação, com a chave reservada antes, e o SMTP lento não pode travar o certame.
Por isso, depois do `commit`, o fluxo chama o `comunicar` existente para cada convocação, com uma chave
**derivada** — a do gesto mais a identidade da convocação. As garantias são as de hoje, pessoa a
pessoa, e ainda ganham uma: repetir a confirmação devolve o ato gravado e **completa** os envios que
não começaram, sem reenviar os concluídos (a chave derivada é a mesma), e sem reenviar os pendentes
(estado indeterminado).

**Alternativa recusada:** enviar dentro da transação, que desfaria o registro sem desfazer a
mensagem num `rollback`.

---

### D-007 — A confirmação carrega a assinatura do alcance

É o padrão do corte (`assinatura_da_proposta`) e do impedimento: a prévia calcula um `sha256`
canônico do que declarou — a apuração vigente, a versão do Edital, a forma, e as identidades das
pessoas ou convocações alcançadas, em ordem —, e a confirmação o envia. O comando recalcula **sob a
trava** e recusa com `alcance_mudou` quando diverge, sem gravar nada. A view devolve a prévia nova.

O vencimento e o complemento não entram na assinatura: são o que a pessoa digitou no mesmo
formulário, e não o que o sistema calculou.

---

### D-008 — A espécie é derivada no comando

`convocar` passa a derivar a espécie: `PARA_REGULARIZAR` para quem está entre os regularizáveis e não
na faixa habilitada; `VAGA_INICIAL` para quem está no conjunto de ocupantes; `SUPLENCIA` para os
demais. A espécie informada que diverge da derivada é recusada com `especie_divergente_da_posicao`
(`FR-868`). A fixture de teste deixa de fixar `VAGA_INICIAL` por padrão.

A sucessão (correção com motivo) deriva do mesmo jeito: corrigir não muda a posição da pessoa.

---

### D-009 — O fundamento é texto derivado no domínio

Uma função pura em `convocacao/domain/fundamento.py` recebe o Edital, o recorte por extenso, a espécie
e a data da apuração, e devolve a frase. A aplicação a monta com os nomes do conteúdo vigente e a
entrega pronta à prévia e ao comando. O complemento entra depois, separado por *"Complemento:"*. O
texto não usa as palavras que a varredura da `019` proíbe (`UX-035`, `UX-039`, `FR-292c`).

---

### D-010 — O vencimento: uma vez por ato, digitado ou do Cronograma

A prévia oferece os Eventos do Cronograma **vigente** que têm data de fim futura, e um campo de data e
hora. O vencimento escolhido é o mesmo para as N convocações. A origem — *"informado neste ato"* ou
*"fim do Evento «Matrícula»"* — entra na razão da trilha de cada convocação (`FR-866`), e não em
coluna nova: a trilha é append-only e já é onde a proveniência de cada ato é lida.

**Vencimento passado recusa o gesto antes de gravar** (`FR-269b`), com o código que a emissão já usa
(`vencimento_anterior_ao_envio`). Na chamada individual pela tela, o fluxo novo a antecipa antes de
convocar, qualquer que seja a forma; a `convocar` da API continua recusando no envio, como na `019`.

---

### D-011 — O gesto não é entidade

Não há tabela de lote. O que nasceu junto é reconstruído pela **correlação** da trilha: todas as linhas
de um gesto carregam `correlation_id = convocacao-lote-<chave>`. Uma tabela de lote seria a segunda
fonte do mesmo fato, e a Constituição (Princípio II) pede uma só. **Nenhuma migration.**

---

### D-012 — As comunicações pendentes, num gesto

Um gesto só cobre os dois casos: na mensagem individual ele emite as comunicações das convocações
vigentes sem desfecho e sem envio com sucesso; na publicação, ele pede **uma** referência e grava uma
`ComunicacaoEmitida` por convocação com ela. Cada emissão passa pelo `comunicar` existente, com chave
derivada e as recusas de hoje, e o resultado conta enviadas e falhas. A prévia lista quem será
comunicado, com a mesma assinatura da `D-007`.

---

### D-013 — O desfecho em lote reusa o registro do desfecho individual

O registro de um desfecho — as recusas, o efeito, a linha, a trilha — sai de `desfechar` para uma
função interna que os dois caminhos chamam, dentro da mesma transação. O gesto de não atendimento
chama-a N vezes e, no fim, faz **uma** tentativa de apuração seguinte (`D-005`). É assim que a
`FR-880` fica verdadeira por construção: não há segundo caminho que possa divergir.
