# Contrato: a validação do conflito, as mudanças de agenda e os testes

## 1. Onde o conflito é conferido, e o que acontece

O conflito é sempre o mesmo cálculo (FR-8202): duas Atribuições ativas do mesmo avaliador, no mesmo
Edital, cujos horários se sobrepõem — `início_a < fim_b` e `início_b < fim_a`. O que muda de um gesto
para outro é a consequência.

| Gesto | Quem | Horário usado | Consequência do conflito | Requisito |
|---|---|---|---|---|
| Distribuir em lote | comissão | publicado, ou da montagem | **recusa a linha**, distribui o resto | FR-8205 |
| Duas linhas do mesmo lote em conflito entre si | comissão | idem | recusa a segunda, na ordem da agenda | FR-8205 |
| Propor e confirmar o rodízio | presidência | idem | **par inelegível**; a inscrição sai como "fora da proposta" com o motivo | FR-8207 |
| Distribuir inscrição sem horário | comissão | nenhum | **nada**: aceita | FR-8206 |
| Montar, preencher, agendar à mão (antes da publicação) | comissão | da montagem | **aceita**; aparece na Distribuição e como aviso na conferência | FR-8208, `D-003` |
| Publicar a agenda | comissão | — | **não impede**; a conferência mostra como aviso | FR-8208 |
| Remarcar, incluir (depois da publicação) | comissão | publicado | **aceita, dito antes da confirmação**; aparece depois | FR-8209, `D-003` |
| Cancelar o agendamento | comissão | — | o horário sai, e com ele o conflito | FR-8210 |
| Remover atribuição | comissão | — | o conflito some; a remoção continua sujeita à FR-092 da `012` | — |
| Avisar os avaliadores (Inc. 2) | comissão | publicado | **o avaliador em conflito futuro fica fora**, nomeado | FR-8221 |

**Por que a recusa só está na Distribuição.** É o único gesto cujo objeto é o avaliador. Os gestos da
agenda são sobre o candidato, e recusá-los por causa de quem avalia inverteria a dependência: a
agenda vem antes ou depois da distribuição, e nenhuma das duas ordens pode travar a outra. O que
impede o conflito de passar despercebido é ele aparecer em três lugares — a confirmação do gesto que
o cria, a agenda publicada e a Distribuição — e impedir o aviso de quem está nele.

## 2. Concorrência

- **Distribuir × distribuir.** O lote e o rodízio já travam o Edital (`_edital_do_processo(...,
  travar=True)`). A conferência do conflito acontece **depois** da trava, sobre o estado relido: duas
  sessões que atribuem horários simultâneos à mesma pessoa são serializadas, e a segunda vê a
  primeira (SC-2840).
- **Distribuir × remarcar, incluir, cancelar.** Os dois lados passam por `comando_de_comissao`, que
  trava o Processo antes de tudo (research T-006): são serializados, e cada um lê o estado depois do
  outro. A remarcação ainda confere, sob essa trava, que os conflitos que a tela anunciou são os de
  agora (`conflitos_mudaram`, 409).
- **Distribuir × montagem.** A montagem (configurar, preencher, agendar à mão, liberar) trava só a
  agenda, e por isso pode correr junto de uma distribuição e criar um conflito que nenhuma das duas
  viu. É aceitável **por construção**: a montagem já pode criar conflito (`D-003`), e ele aparece na
  leitura seguinte, na Distribuição e na conferência da agenda. Pôr a montagem sob a trava do Processo
  serializaria a comissão inteira durante o ajuste da grade.
- **Avisar × mudar.** O aviso grava o estado da programação que avisou. Uma remarcação depois da
  leitura e antes do envio deixa o avaliador como "mudou depois do aviso", que é a verdade: o aviso
  saiu dizendo "veja no GPS", e o GPS já mostra o horário novo. Nenhuma mensagem fica errada, porque
  nenhuma leva horário.

## 3. As mudanças de agenda, caso a caso

| Mudança | Atribuições | Programação | Conflito | Aviso (Inc. 2) |
|---|---|---|---|---|
| Remarcação para outro horário da mesma banca | não mudam | horário novo, "remarcada em" | conferido no horário novo | os avaliadores da pessoa ficam "mudou" |
| Remarcação para outra banca (transferência) | não mudam | banca e sala novas para os mesmos avaliadores | idem | idem |
| Inclusão de quem passou a participar | não existem ainda | não aparece até ser distribuída | conferido na distribuição | quem a receber fica "mudou" |
| Cancelamento | não mudam | sai | sai | os avaliadores ficam "mudou" |
| Troca de avaliador na Distribuição | uma sai, outra entra | sai de um, entra no outro | conferido para quem entra | os dois ficam "mudou" |
| Banca, dia ou janela acrescentados | não mudam | — | — | — |

A agenda nunca mexe em Atribuição (FR-8209). Quem decide se a transferência leva os mesmos
avaliadores à outra sala, ou se a pessoa ganha outros avaliadores, é a comissão, na Distribuição.

## 4. Testes por incremento

### Incremento 1

**Domínio, puros (sem banco):**

- sobreposição: igual, contida, parcial, que só se toca (não é conflito), em dias diferentes;
- a mesma pessoa em duas Etapas do mesmo Edital; em Editais diferentes (não conta);
- o rodízio na ordem da agenda, com o conflito como inelegível: o caso 43 × 6 × 3, com dez ordens de
  protocolo, dá zero conflito (SC-2842); com um impedimento, a inscrição sai com o motivo certo.

**Aplicação (banco):**

- lote com uma linha em conflito: a linha é recusada e nomeada, o resto é criado (SC-2840);
- lote com duas linhas em conflito entre si;
- inscrição sem horário não é recusada; distribuição antes da montagem continua válida;
- montagem depois da distribuição cria conflito, e a leitura o mostra;
- duas distribuições concorrentes (caso transacional): uma vale, a outra é recusada;
- remarcação que cria conflito acontece, e a leitura o mostra; cancelamento o desfaz;
- a programação contém todas e somente as entrevistas das Atribuições da pessoa, em ordem
  (SC-2843); inscrição atribuída sem horário vai ao bloco à parte;
- a próxima entrevista em Minhas atividades ignora as passadas.

**Interface:**

- o filtro de dia e banca e o lote: o caso 43 × 6 × 3 distribuído em seis submissões (SC-2841);
- a remarcação diz quem avalia e marca os horários ocupados;
- a agenda publicada mostra "Avaliam"; a página pública, o PDF do ato e a área do candidato não
  (SC-2846, com a varredura de nomes de avaliador nos três);
- a Mesa de Bruno não mostra entrevista de Ana (autorização); sala só ao avaliador atribuído;
- a Programação a 375 px sem rolagem horizontal e sem violação da política de conteúdo (SC-2850);
- o orçamento de consulta da Mesa: a Programação não cresce com o número de entrevistas.

### Incremento 2

- o destinatário: membro com pessoa institucional e e-mail; sem pessoa; sem e-mail; suspenso;
  identificador de demonstração;
- a confirmação mostra o alcance e a mensagem sem gravar;
- um aviso por avaliador por gesto; repetir sem mudança cria zero (SC-2847);
- remarcação, troca de avaliador e cancelamento marcam "mudou" só os avaliadores afetados; desfazer
  a mudança desfaz a marca;
- o avaliador em conflito futuro fica fora, nomeado;
- a mensagem não contém nome, protocolo, CPF, e-mail ou telefone de candidato, Modalidade nem sala
  (SC-2848), em todas as variantes;
- o despacho envia pela fila da `066`, respeita o limite por minuto, registra falha e oferece reenvio;
- habilitação desligada: nenhum aviso, e a seção o diz;
- a trilha registra o gesto sem e-mail;
- a varredura das situações de envio conta oito, com a revisão datada (SC-2849).

## 5. O tamanho, sem prometer antes do plano

O estudo chamou o primeiro incremento de "baixo" quando ele era só leitura. Com a recusa por
conflito no lote e no rodízio, a revisão da FR-107 e o caso concorrente, ele é **médio**: não tem
migration, mas toca a regra de atribuição em massa, que é das mais testadas do sistema, e o
orçamento de consulta da Mesa. O segundo incremento é **médio** pelo outro lado: pouca tela, mas o
despacho da `066` passa a ter um destinatário que não é inscrição, e isso é o que o plano tem de
desenhar com cuidado (`D-010`). As estimativas firmes saem do `/speckit-plan`.
