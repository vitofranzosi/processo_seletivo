# Decisão — Avisos aos candidatos ligados por padrão (15/11/2026)

*Decisão do usuário em 15/11/2026, ao fechar a spec `167` (agendamento da Etapa). Registro, e não
estudo: o que mudou, o que a decisão substitui e o que continua valendo.*

## O que mudou

`AVISOS_AOS_CANDIDATOS`, a chave única dos avisos complementares (`066`), passa a vir **ligada por
padrão em todo ambiente**, produção inclusive (`backend/config/settings/base.py`). Um ambiente que
ainda não tem correio pronto a desliga com `AVISOS_AOS_CANDIDATOS=false`.

## Por quê

Nas palavras do usuário: *não faz sentido ele estar desabilitado*. Com a chave desligada, a agenda da
Etapa era publicada e ninguém era avisado do horário — e o registro de 09/10
(`doc/registro-convocacao-para-etapas-2026-10-09.md`) já anotava que o candidato perde a Etapa por não
ter visto uma publicação. A página pública continua sendo o ato; o e-mail é o caminho até ela.

## O que a decisão substitui

- A condição da `066` (`D-009` daquela spec): avisos desligados em produção **até** a validação
  institucional de LGPD, com o encarregado de dados, e a da infraestrutura de correio.
- A recomendação CA-05 da auditoria de prontidão de 31/10
  (`doc/auditoria-prontidao-arquitetural-e-operacional-2026-10-31.md`), que pedia trava em
  `production.py` enquanto a LGPD não validasse. As auditorias ficam como estão, porque são datadas.

## O que continua valendo

- **A chave é uma só** (`D-011` da `167`): ligá-la libera todas as origens — resultado, chamada,
  pendência documental e agenda —, e não só a agenda.
- **A confirmação não envia.** Quem envia é o despacho (`manage.py despachar_avisos`), a cada minuto em
  produção, com `AVISOS_LIMITE_POR_MINUTO` mensagens por execução.
- **Produção já recusa subir sem correio que entregue** (`config/settings/production.py`, backend de
  e-mail). O que a decisão não dispensa é conferir, antes da implantação, que o limite por minuto cabe
  no limite da conta de correio institucional (guia de implantação, §16.4).
- **A validação de LGPD com o encarregado de dados continua recomendada.** As mensagens levam nome,
  protocolo, horário e, na agenda remota, o endereço da sala da própria pessoa — nunca CPF. Ela deixa
  de ser condição para ligar.
- **Nenhum aviso antigo dispara ao ligar**: aviso mais velho que `AVISOS_JANELA_DE_DESPACHO_HORAS`
  expira sem envio, e o aviso da agenda é efeito do ato, no instante dele.
