# Contrato — o canal da instituição

**Feature**: 018 · **Canal**: `interface/`, HTML administrativo · **Spec**: [spec.md](../spec.md)

Quatro rotas novas. Nenhuma rota de API, nenhum contrato público: julgar é ato interno, e o que dele
chega ao candidato está em [recurso.md](./recurso.md).

---

## 1. Autorização, e o que ela não é

```text
capacidade   recurso:julgar        no mapa de papéis, em papel próprio (`julgador`)
NÃO deriva   de presidir a comissão, de integrá-la, de avaliar, de consolidar,
             de constatar ocorrência, de emitir o ato, de publicar
```

`require_permission(ator, "recurso:julgar")` **fora** da transação, no molde de
`publicar_resultado` — e não `comando_de_comissao`, que autoriza por presidência e é exatamente a
derivação que a D-005 proíbe (T-005).

**O impedimento é verificado dentro da transação, depois do bloqueio do Processo** (FR-043), e são
cinco perguntas pontuais:

```text
avaliacao.concluida_por    == ator?   →  concluiu a Avaliação fonte
resultado.consolidado_por  == ator?   →  consolidou o Resultado, ou constatou a Ocorrência
ato.emitido_por            == ator?   →  emitiu o ato de ordenação atacado
publicacao.publicado_por   == ator?   →  praticou a publicação atacada
Impedimento(ator, inscricao) existe?  →  o mesmo Impedimento da 012
```

Cinco perguntas **por ato de julgamento**, e nenhuma por linha de listagem. A listagem mostra
recursos que o ator pode não poder julgar; é a tela do recurso que diz o impedimento. Verificar na
listagem custaria a consulta por linha que a 012 recusou (T-006).

---

## 2. `GET interface:recursos` — os recursos recebidos

Lista por Edital, com filtro por situação derivada (D-010).

| coluna | origem |
|---|---|
| protocolo, instante | `Recurso` |
| candidato | nome e protocolo da Inscrição |
| objeto atacado | marco e natureza da publicação, **ou** Etapa e consequência do Resultado |
| situação | derivada: aguardando admissibilidade · aguardando julgamento · inadmitido · decidido · reavaliação pendente · providência pendente |
| tempestividade | dentro da janela · fora · sem janela computável |

**Sem consulta de impedimento**, e sem fundamentação na lista: ela é conteúdo do juízo, e a lista é
para escolher o que abrir.

---

## 3. `GET interface:recurso` — a peça

Objeto atacado com o caminho para ele, a fundamentação como escrita, a proveniência que a FR-092
exige, e o impedimento do ator quando houver — nomeado, e antes de qualquer botão.

**O que a proveniência responde aqui** (FR-092): quem interpôs, qual Inscrição, qual objeto, qual era
o ato vigente naquele instante, sob qual versão, quando, se dentro da janela computável, quem
admitiu e por quê, quem decidiu e por quê, qual efeito, qual ato superado, qual sucessor nasceu.

---

## 4. `POST interface:recurso-admitir` — o juízo de admissibilidade

**Entrada**: `admitido` (sim/não), `motivo` (obrigatório nas duas direções), assinatura do estado
lido, chave de idempotência.

**Recusas**

| código | HTTP | quando |
|---|---|---|
| `forbidden` | 403 | sem `recurso:julgar` |
| `appeal_judge_barred` | 403 | impedido — a mensagem nomeia qual das cinco razões |
| `appeal_reason_required` | 422 | motivo vazio |
| `appeal_already_reviewed` | 409 | já existe juízo para este recurso |
| `stale_appeal_state` | 409 | o estado mudou entre a leitura e a confirmação |

**Admitir também é ato motivado.** A assimetria de exigir motivo só na inadmissão faria a admissão
parecer automática, e ela não é.

**Tempestividade**: com janela estruturada, ela **não** é matéria daqui — a interposição já foi
recusada (FR-033). Sem janela, é o juízo humano que decide, e o motivo é onde ele o diz (FR-034).

---

## 5. `POST interface:recurso-julgar` — a decisão

**Entrada**

| campo | quando | observação |
|---|---|---|
| `especie` | sempre | uma das quatro |
| `motivacao` | sempre | obrigatória em todas, inclusive no indeferimento |
| `etapa_id` | correção fixada, reavaliação | o par que a decisão alcança |
| `consequencia` | correção fixada | derivada, e não digitada: ver abaixo |
| `pontuacao` ou `sentido` | correção fixada com grandeza | conforme a forma que a Etapa publica |
| assinatura do Resultado vigente lido | correção fixada | é o que recusa decidir sobre o que já mudou |
| chave de idempotência | sempre | |

**A consequência é derivada, e não digitada** (FR-059). O julgador fixa a **conclusão** — a pontuação
na forma pontuada, o sentido na decisória —, e a consequência sai da regra publicada vigente para a
Etapa, sob a versão que a decisão cita: nota mínima e caráter eliminatório na forma pontuada, o
sentido na decisória. Deixá-la livre permitiria uma decisão declarar `HABILITADA` com nota abaixo da
mínima, o que contradiria a norma que a própria decisão cita.

**O desfecho sem grandeza** é o ramo do recurso contra Ocorrência: a decisão declara a consequência
diretamente, sem forma, sem pontuação e sem sentido, e o motivo é onde ela se explica.

**O que acontece dentro da transação**

```text
require_permission(recurso:julgar)                          ← fora da transação
────────────────────────────────────────────────────────────
abre transação
  select_for_update no ProcessoSeletivo                     ← serializa com emitir, publicar, consolidar
  reavalia autorização e as cinco perguntas do impedimento  ← FR-043
  revalida a assinatura do que foi lido                     ← FR-100
  reserve(chave)
  grava a DecisaoRecurso, imutável
  se CORRECAO_FIXADA:
      lê e trava o Resultado vigente do par
      verifica non reformatio contra ele                    ← FR-070; pior ⇒ indeferimento
      cria EXATAMENTE UM sucessor, citando-o e citando a decisão
  se REAVALIACAO_DETERMINADA:
      nenhum sucessor; a decisão declara o efeito e cita o Resultado protegido
  se PROVIDENCIA_A_JUSANTE ou INDEFERIDO:
      nenhum efeito sobre Resultado
  audita — um evento por agregado
  finish(chave) com o desfecho serializado
────────────────────────────────────────────────────────────
qualquer invariante que falhe derruba a transação inteira:
não fica decisão sem efeito, nem efeito sem decisão.
```

**Recusas**

| código | HTTP | quando |
|---|---|---|
| `forbidden` | 403 | sem a capacidade |
| `appeal_judge_barred` | 403 | impedido |
| `appeal_not_admitted` | 409 | ainda não há juízo de admissibilidade, ou ele foi negativo |
| `appeal_already_judged` | 409 | já há decisão |
| `stale_stage_result` | 409 | o Resultado vigente do par mudou entre a leitura e a confirmação |
| `appeal_reason_required` | 422 | motivação vazia |
| `appeal_correction_incomplete` | 422 | correção fixada sem Etapa, sem conclusão exigida pela forma |
| `appeal_worsens_situation` | 422 | a correção proposta pioraria — nenhum sucessor nasce |

**Concorrência**: a corrida entre dois deferimentos sobre o mesmo Resultado é resolvida por
`uq_resultado_sucessor_unico`, **no banco**, e não por leitura prévia — como
`uq_ato_sucessor_unico` já resolve a emissão simultânea de dois sucessores do mesmo ato. Ler o
vigente antes de gravar é conforto de mensagem de erro, e não garantia.

---

## 6. A reavaliação, e a exceção única da consolidação

**Na organização da Etapa**, a inscrição com reavaliação determinada e não cumprida aparece como
pendência nomeada — e não como já consolidada, que é o que a prontidão diz hoje para quem tem
Resultado (FR-067).

**A consolidação em cumprimento da decisão** é a única que cria sucessor com origem em avaliação
(FR-068). Ela existe **somente** onde há, para aquele par, decisão dessa espécie não cumprida; fora
dela, consolidar continua recusando o par que já possui Resultado vigente (FR-055).

Duas coisas que se ganham de graça, e vale registrá-las:

- **quem concluiu a Avaliação original não conclui a reavaliação.** `uq_avaliacao_concluida_por_pessoa`
  já impede a segunda conclusão da mesma pessoa sobre o mesmo par. É garantia estrutural, e não
  regra nova;
- **outro avaliador pode receber Atribuição ativa para o mesmo par**, porque `uq_atribuicao_ativa` é
  por membro. A reavaliação é distribuível sem operação nova.

**A vedação de piora alcança este caminho** (FR-073): a nova Avaliação é registrada — ela é o juízo
do avaliador, e apagá-la seria mentir sobre o que ele concluiu —, mas o seu Resultado não é
consolidado como sucessor quando for pior que o `resultado_protegido` citado pela decisão. A recusa
nomeia a vedação.

---

## 7. A providência a jusante, e quem a cumpre

A decisão da quarta espécie **nomeia** a providência na motivação e não a executa. Quem a executa é
quem tem a autoridade da 015 ou da 017 — e, ao emitir o ato sucessor, **cita a decisão que está
cumprindo**, entre as pendentes daquele marco.

A citação vive em `classificacao.CumprimentoDeProvidencia`, gravada por `emitir_ordem` na mesma
transação do ato. Não é ato administrativo: é proveniência do ato, como `motivo_da_sucessao`.
Nenhuma autoridade nova, nenhum passo humano separado. Ver [janela.md](./janela.md), §3.1, e T-015.
