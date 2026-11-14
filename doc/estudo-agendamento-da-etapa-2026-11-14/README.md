# Estudo: agendamento de participantes nas Etapas (2026-11-14)

**Pergunta.** Como uma comissão sai de uma lista de participantes de uma Etapa — entrevista,
verificação da autodeclaração, arguição — para uma agenda conferida, publicada e avisada, sem
planilha, aproveitando o que o GPS já tem?

**Resposta curta.** Com **uma agenda por Etapa**, operacional, que lê quem participa e não guarda
lista própria; publicada pelo mesmo gesto da convocação (`140`, `149`, `159`); avisada pelo mesmo
app de avisos (`066`); e mudada depois só por ato individual. São cinco tabelas novas e uma origem de
aviso. Nada muda na Etapa, no Edital, na avaliação ou no resultado.

1. **O GPS sabe quem e não sabe quando.** A participação da Etapa é uma projeção única
   (`resultados/application/prontidao.py`). Não existe horário por pessoa, nem banca como lugar, nem
   ato de comparecimento (`doc/registro-convocacao-para-etapas-2026-10-09.md`).
2. **O horário tem efeito, e é publicado.** Nos Editais 28/2026, 140/2025, 90/2026 e 146/2025, a
   agenda sai em listagem, a sala vem "no ato da convocação", a justificativa conta do horário e a
   ausência elimina. Publicar a agenda é ato, e não só informação.
3. **A heteroidentificação não precisa de nada a mais.** Com a `163` (alcance por Modalidade), ela
   usa a mesma agenda; a única diferença é a página pública mostrar só o protocolo.

**O que o estudo não fez.** Não implementou nada no sistema nem tocou Edital publicado. O protótipo
é estático e não fala com o GPS.

## Entregas

1. [Diagnóstico](01-diagnostico.md): Etapa, participação, comissão, conferência, publicação,
   avisos, portal; os Editais reais; as lacunas.
2. [Proposta](02-proposta.md): as jornadas da comissão e do candidato; as regras R-01 a R-26; o
   modelo mínimo; concorrência; os cenários A e B; as decisões de interface; as cinco perguntas de
   09/10 respondidas.
3. [Protótipo navegável](prototipo/README.md), com as folhas reais e a CSP de produção:
   configurar, montar (automático e à mão), conferir, publicar, remarcar, página pública, área do
   candidato e e-mail. Catorze verificações no Chromium do painel.
4. [Redesign da experiência](04-redesign.md), segunda rodada do mesmo dia: diagnóstico crítico do
   protótipo, nove decisões (veredito antes do detalhe, a falta resolvida no simulador, a montagem
   como workspace com painel de ação, o seletor de horário único), antes e depois por tarefa, e as
   quatro limitações do design system registradas fora do escopo. Capturas em
   [prototipo/capturas/](prototipo/capturas/).
5. [Plano de entregas](03-plano-de-entregas.md): o marco de aprovação visual, as entregas A a D, os
   riscos e os testes.
6. [Especificação](../../specs/166-agendamento-da-etapa/spec.md), pelo Spec Kit.

## Pontos de integração

| Peça do GPS | Papel na agenda |
|---|---|
| `participacao_detalhada` (`prontidao.py`) | quem precisa de horário; nada de lista própria |
| `EventoCronograma` da Etapa | o período dentro do qual os dias da agenda cabem |
| `AlocacaoEtapa` | o padrão de referência por `etapa_id`; a comissão continua como está |
| Conferência da `140` | a moldura e as regras da tela "Confira antes de publicar a agenda" |
| Publicação da `149` / `159` | ato append-only, bytes canônicos, autoridade, veículo |
| Avisos da `066` | origem nova AGENDA; despacho, falha e reenvio como hoje |
| `situacao_da_inscricao` (`063`) | o horário na área do candidato |
| Ocorrência | a ausência, como hoje |
| Centro (`136`), Minhas atividades (`160`) | a pendência "montar e publicar a agenda" (entrega D) |

## Decisões

Tomadas pelo usuário em 14/11/2026, todas pela recomendação, e registradas na spec `166`
(*Clarifications*, `D-008` a `D-010`):

- **Q-2: só o protocolo** na página pública da agenda de Etapa restrita por Modalidade; nome e
  protocolo nas demais. A consulta ao encarregado de dados continua recomendada antes da implantação.
- **Q-3: publicação formal**, com a natureza da relação de convocados da `149` e o veículo escolhido
  como na `159`.
- **Q-5: revisar a FR-084** para o aviso de agenda, como origem do aviso complementar, sem envio novo.

## Decisões pendentes

Só o que depende de validação humana ou de regra institucional. Cada uma traz a recomendação, que a
spec adota como premissa.

- **Q-1 — O Cefor opera bancas simultâneas?** Muda a capacidade desde o primeiro dia. *Recomendação:*
  incluir no MVP mesmo assim. Custa uma tabela e uma coluna na grade, e o cenário B já tem duas salas
  da RNP.
- **Q-4 — Publicar em partes?** Uma agenda por dia, à medida que a lista fecha. *Recomendação:* não
  no MVP: todo participante com horário antes de publicar (R-13).
- **Q-6 — A ordem do preenchimento automático.** Nome, classificação ou inscrição? *Recomendação:*
  nome, com o protocolo no empate: explicável e sem expor a posição na classificação.
- **Q-7 — A sala virtual é por banca ou por pessoa?** *Recomendação:* por banca, que é o que os
  Editais descrevem (uma sala da RNP por comissão).

**Que podem esperar a implementação:** o aviso de cancelamento (R-22) e lembrete na véspera, que
seria uma oitava situação de mensagem.

## Fora, de propósito

Autosserviço de escolha de horário pelo candidato; disponibilidade de cada avaliador; calendário
institucional; integração com Google ou Outlook; videoconferência embutida; gravação; presença
registrada na agenda. O vídeo assíncrono do estudo de 13/11 é outra solução para outra parte do
problema: **a agenda reduz o trabalho de montar a escala, avisar e remarcar, e não o tempo que a banca
passa entrevistando.**

## Próximo passo proposto

1. **Marco 0:** percorrer o protótipo com a comissão, num caso real de entrevista ou de
   heteroidentificação, e confirmar a Q-1.
2. Com a experiência aprovada, plan, tasks e a entrega A da spec `166`, uma sessão por entrega.
