# Contrato — a Atenção depois da `045`

O que cada superfície **diz**, e o que ela **não afirma**. As redações entre aspas são o alvo; a
implementação pode ajustar a pontuação, e não o conteúdo. Onde a frase é de condução, ela **não** é
redigida aqui: sai do mecanismo único da `037` (`frase_do_aviso`), e o que este contrato fixa são as
bases e a oração do ato.

---

## 1. A frase de ausência (`FR-730`, `FR-731`, `UX-084`)

| O leitor alcança | E não há sinal | A região |
|---|---|---|
| todas as espécies do catálogo | — | *"Nenhuma condição de atenção neste Processo."* (a de hoje) |
| parte delas | — | *"Nenhuma condição de atenção entre as que você acompanha neste Processo."* |
| nenhuma | — | a região não aparece (`038`, sem mudança) |

**Não afirma**: que há algo fora do alcance, quantas coisas, nem de que espécie. A escolha usa só
`alcance(ator, processo)`; nunca `alcance_no_edital` nem os sinais montados.

**As duas páginas** — Processo e Supervisão — usam a mesma escolha. A Supervisão só abre para a
gestão, e a gestão sozinha **não** alcança o catálogo inteiro (não alcança recursos nem divulgação):
na Supervisão, a frase global só aparece para quem acumula papéis.

---

## 2. O catálogo — oito espécies (`FR-744`)

| Espécie | Condição | Mensagem | Medida | Destino | Condução, a quem não pratica |
|---|---|---|---|---|---|
| `UX-003` | participante da Etapa com menos avaliadores que o previsto | *"A Etapa «X», do Edital N/AAAA, tem inscrição sem avaliador suficiente."* (a de hoje) | carentes **de participantes**, em *inscrições* | distribuição da Etapa | só a gestão lê, e a gestão pratica |
| `UX-004` | ato de ordenação vigente obsoleto | a de hoje | — | ordenação, ou sorteio | Auditor: na ordenação **já existe**; no sorteio, **acrescentar** — bases gestão e presidência, *"que o emita"* |
| `UX-005` | peça **aguardando decisão** com toda a comissão impedida | *"Há recurso aguardando {fase} no Edital N/AAAA para o qual todos os membros da comissão estão impedidos de julgar."* | — | recursos do Edital | Julgador impedido: a peça **já** conduz — diz o impedimento e *"Aguardando apreciação por quem não esteja impedido"*; nada a acrescentar |
| `UX-046` | acervo que declara vaga imediata sem linha do quadro | a de hoje, **sem** repetir os números da medida | recortes sem linha, em *recortes* | Retificação | gestão sem retificar: **no sinal**, `CONDUCAO_DA_RETIFICACAO` |
| `UX-063` | participante distribuído e não concluído | a de hoje | paradas de distribuídas, em *inscrições* | distribuição da Etapa | só a gestão lê, e a gestão pratica |
| `UX-064` | peça **aguardando decisão** com membro desimpedido | *"Há recurso aguardando {fase} no Edital N/AAAA com membro da comissão desimpedido para decidi-lo."* | soltas de pendentes, em *recursos* | recursos do Edital | Julgador impedido: a mesma da `UX-005` — a peça já conduz |
| `UX-065` | recorte com ordem vigente e sem apuração vigente | a de hoje | — | ocupação do marco | Auditor: **acrescentar** — bases gestão e presidência, *"que a apure"* |
| `UX-066` | ato vigente sem divulgação vigente | a de hoje | — | prévia da divulgação | Publicador diante de ato obsoleto: **acrescentar** na prévia — bases gestão e presidência, *"que emita o ato sucessor"* |

**`{fase}`** é *"admissibilidade"*, *"julgamento"* ou *"decisão — admissibilidade ou julgamento"*,
conforme as peças que **aquele** sinal conta (`UX-085`). A partição por peça é a da `038`: nenhuma peça
conta nos dois.

**Retirados**: `UX-001` (vai à validação do conteúdo, seção 4) e `UX-002` (a condição deixou de
existir, seção 5).

**Não afirma**: prazo de resposta (não existe no domínio); quem deve decidir (`038`, `FR-564`); que o
leitor impedido está impedido — isso é da peça, que já o diz. **E a peça não recebe "peça a alguém com a permissão de julgar"**: o Julgador impedido **tem** a permissão, e a frase seria falsa para ele (`037`, `FR-544`). O que lhe falta é não estar impedido, e a peça já nomeia isso.

---

## 3. A medida (`FR-743`, `UX-087`)

A forma é `numerador de denominador unidade`, com a unidade no plural quando o denominador pede —
*"1 de 2 recursos"*, *"2 de 4 inscrições"*, *"1 de 3 recortes"*. Par ou nada, como antes. A unidade
é da **espécie**, e não do template: quem monta o sinal a declara.

**A contagem da ação de recursos** (`FR-734`): *"Recursos aguardando decisão (N)"*. O número conta
peças sem juízo, ou com juízo que admitiu e sem decisão. A tela a que leva continua listando todas.

---

## 4. O aviso da Etapa sem Evento (`FR-739`, `UX-086`)

- **Severidade**: aviso. Aparece como *"Aviso"*, nunca *"Impede"*; não bloqueia submissão, publicação
  nem Retificação.
- **Texto**: *"A Etapa «X» não está vinculada a nenhum Evento do Cronograma."* Nomeia a Etapa; nunca
  diz *aguardando*, *atrasada* ou progresso.
- **Código**: `stage_without_schedule_event` — próprio, porque aviso com código de impeditivo é
  descartado pela Retificação e reprova o invariante dos dois conjuntos. Caminho
  `/stages/id=<uuid>/scheduleEventId`.
- **Ato**: só o de **publicação**. Na confirmação de uma Retificação ele não aparece: ali não tem
  remédio (`D-003`).
- **Onde**: onde a validação do conteúdo já aparece — as pendências da etapa do assistente que trata
  Etapas, a Revisão antes de submeter, a confirmação de submeter e de publicar, e *"Validação do
  conteúdo"* na página do Edital, inclusive publicado. Várias Etapas sem Evento viram **uma** linha.
- **Destino no assistente**: a etapa das Etapas, onde o vínculo se escolhe. Num Edital publicado, o
  aviso não leva à Retificação: `scheduleEventId` é estrutural (`026`) e ela não o alcança.

---

## 5. A fase do Evento (`FR-735` a `FR-737`, `UX-088`)

| Evento | Fase exibida |
|---|---|
| declarado `CANCELADO` | *cancelado* — e sai dos próximos marcos, como hoje |
| período de inscrições | a do período: futuro → *planejado*, aberto → *em andamento*, encerrado → *concluído* |
| outro, antes do início | *planejado* |
| outro, vencido pela régua da `037` | *concluído* — e sai dos próximos marcos |
| outro, entre os dois | *em andamento* |

**Os próximos marcos do pulso** mostram só os não concluídos, e marcam *"em andamento"* o que está em
curso. O futuro não precisa de marca: a data diz. Nunca aparece *"declarado"*.

**A API do rascunho** aceita `status` `PLANEJADO` ou `CANCELADO`; recusa `EM_ANDAMENTO` e
`CONCLUIDO` com *"A fase do Evento é derivada das datas; só o cancelamento é declarado."*

**Não afirma**: atraso, nem que um Evento *deveria* ter começado. A fase é o relógio, e não juízo.
