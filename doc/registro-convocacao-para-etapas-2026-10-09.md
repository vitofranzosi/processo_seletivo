# Registro — Convocação para participar de etapas

*Registro de 09/10/2026, pedido pelo usuário ao aprovar o MVP dos avisos complementares. É
capacidade futura, identificada e priorizável. **Não é escopo** da feature de avisos, e nenhuma
decisão de produto foi tomada sobre ela além de registrá-la.*

## O que falta

O setor pediu aviso para "convocação de PPI, para entrevista de títulos, chamada de suplentes".
Dos três exemplos, só a chamada de suplentes tem ato no sistema
([auditoria de 09/10](auditoria-notificacoes-aos-candidatos-2026-10-09.md), matriz B).

O que não existe é **o ato de convocar alguém para comparecer a uma etapa ou procedimento**, com
data, horário, local ou sala, orientações e consequência da ausência:

- **Heteroidentificação e verificação da autodeclaração.** Ficaram para "spec própria"
  (`specs/019-convocacao-chamada-suplencia/spec.md:792`, `specs/014-corte-e-progressao-entre-etapas/spec.md:882`).
  No Edital ela é só seção textual (`backend/processo_seletivo/editais/domain/secoes.py:94-97`). O
  Edital 90/2026 (4.1) convoca os *deferidos* para as vagas de ação afirmativa "por meio de listagem
  divulgada" no site, e quem decide a listagem é a comissão.
- **Entrevista e avaliação de títulos.** São Etapas. Quem avança para elas sai do corte vigente
  (`ItemDoCorte.PROGREDIU`) ou do panorama de participantes, mas convocar para a Etapa não é ato.
  A Etapa pode apontar **um** Evento do Cronograma (`scheduleEventId`), com **uma** data e **um**
  local (`backend/processo_seletivo/editais/api/serializers.py:205, 215-240`). Não há horário por
  pessoa.
- **A ausência** se registra hoje como ocorrência na Etapa
  (`backend/processo_seletivo/resultados/application/ocorrencia.py:1-5`). Ela não se liga a convocação
  nenhuma.

## Por que pode valer mais que o aviso de resultado

Segundo o usuário, o candidato pode perder uma entrevista ou um procedimento obrigatório só por não
ter visto uma publicação. O resultado ele ainda consulta no portal, que a `063` passou a abrir pela
situação. A convocação para comparecer não aparece em lugar nenhum do sistema: não há ato, não há
situação no acompanhamento e não há aviso possível.

## O que o incremento precisaria decidir

Perguntas a responder, e não respostas:

1. **Convocar para etapa é ato próprio, com lista congelada**, como a `Convocacao` da `019`? Ou
   basta citar o corte vigente e uma referência externa?
2. **Quem é alcançado na heteroidentificação?** A lista de uma modalidade, os classificados dela ou
   os deferidos por decisão da comissão? E por qual ato, se nenhum Edital da amostra a deriva de
   regra?
3. **Horário individual** (agenda de entrevista) entra, ou fica uma data e um local por etapa?
4. **Exposição da modalidade.** Uma convocação de heteroidentificação revela autodeclaração racial.
   É a mesma governança que a `063` deixou em aberto.
5. **Relação com o aviso complementar.** Existindo o ato, ele vira uma origem nova do aviso, sem
   modelo novo de envio.

## Dependências

- A spec de heteroidentificação que a `019` e a `014` registraram.
- A feature de avisos complementares, se o incremento quiser avisar por e-mail. Sem ela, o ato
  continua útil pelo portal.
