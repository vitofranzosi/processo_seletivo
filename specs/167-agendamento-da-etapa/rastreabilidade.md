# Rastreabilidade — 167 · O agendamento dos participantes da Etapa

**Frase que governa**: *a agenda é operacional, lê a participação sem guardar lista, e depois de
publicada só muda por ato individual, que guarda o anterior.*

Uma linha por identificador em negrito da spec: a tarefa, onde entrou no código (relativo a
`backend/processo_seletivo/`) e o teste que o prova. Gerada das citações reais — o identificador, ou
a faixa que o contém, no texto do código e dos testes — e conferida à mão onde a citação faltava.
Abreviações dos testes:

- **U** — `tests/unit/agendamento/`
- **I** — `tests/integration/agendamento/`
- **GI** — `tests/interface/`
- **P** — `tests/portal/`
- **G** — os guardiões na raiz de `tests/` (`test_situacoes_de_mensagem.py`, `test_citacoes_de_requisito.py`)

Tudo roda contra o PostgreSQL (`make test-pg`); os casos de gatilho, privilégio e trava pulam fora
dele.

| Identificador | Tarefas | Código | Teste |
|---|---|---|---|
| FR-7200 | T009, T013 | — | I:leitura |
| FR-7201 | T013 | `agendamento/models.py` (`etapa_id` sem FK), `application/leitura.py` (a Etapa da Versão Consolidada vigente) | **sem teste próprio** — achado abaixo |
| FR-7202 | T009 | `agendamento/application/configurar.py`, `agendamento/domain/nomes.py` | U:conteudo, U:mensagem, I:configuracao |
| FR-7203 | T005, T006 | `agendamento/application/configurar.py`, `agendamento/domain/capacidade.py`, `agendamento/domain/horarios.py` | U:horarios |
| FR-7204 | T007, T008, T015 | `agendamento/application/configurar.py`, `agendamento/domain/configuracao.py` | I:configuracao, U:configuracao |
| FR-7205 | T006, T014, T015 | `agendamento/application/configurar.py`, `agendamento/domain/capacidade.py`, `interface/agenda_da_etapa.py` | I:configuracao, U:capacidade, U:horarios |
| FR-7206 | T005, T006 | `agendamento/application/configurar.py`, `agendamento/domain/horarios.py` | U:horarios |
| FR-7207 | T011, T015 | `agendamento/application/configurar.py` | I:configuracao |
| FR-7208 | T024, T029, T044, T057 | `agendamento/application/configurar.py`, `agendamento/domain/nomes.py`, `agendamento/domain/recusas.py` | I:configuracao, I:montagem, I:publicacao |
| FR-7210 | T010, T013 | — | I:leitura |
| FR-7211 | T009, T025, T028 | `agendamento/application/montar.py`, `agendamento/models.py` | I:concorrencia_da_montagem |
| FR-7212 | T024, T028 | `agendamento/application/montar.py`, `interface/agenda_da_etapa.py` | I:montagem |
| FR-7213 | T023, T028 | `agendamento/domain/horarios.py`, `agendamento/domain/preenchimento.py` | I:montagem, U:conteudo, U:preenchimento |
| FR-7214 | T023, T024, T028 | `agendamento/application/montar.py`, `agendamento/domain/preenchimento.py`, `interface/agenda_da_etapa.py` | I:montagem, U:preenchimento |
| FR-7215 | T024, T028 | `agendamento/application/montar.py`, `interface/agenda_da_etapa.py` | I:montagem (`agenda_mudou_desde_a_previa`) |
| FR-7216 | T009, T024, T028 | `agendamento/domain/nomes.py`, `agendamento/models.py` | I:montagem |
| FR-7217 | T010, T013, T031 | `agendamento/application/leitura.py` | I:leitura, GI:agenda_da_etapa_conferir |
| FR-7220 | T043, T048 | `agendamento/application/conferir.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_conferir.html` | I:conferencia |
| FR-7221 | T043, T048 | `agendamento/application/conferir.py`, `agendamento/domain/configuracao.py`, `agendamento/domain/recusas.py`, `interface/agenda_da_etapa.py` | I:conferencia (os cinco impedimentos) |
| FR-7222 | T043, T047, T048, T088 | `agendamento/application/conferir.py`, `agendamento/domain/conteudo.py`, `agendamento/domain/mensagem.py`, `interface/agenda_da_etapa.py` | I:conferencia, GI:agenda_da_etapa_conferir |
| FR-7223 | T044, T049 | `agendamento/application/conferir.py`, `agendamento/application/publicar.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_conferir.html` | I:publicacao |
| FR-7224 | T037, T040, T044, T049, T086, T087 | `agendamento/application/publicar.py`, `agendamento/infrastructure/documento.py`, `agendamento/models.py`, `interface/agenda_da_etapa.py` | I:atos_imutaveis, I:publicacao, P:documento_da_agenda, U:documento |
| FR-7225 | T041, T042, T045 | `agendamento/domain/conteudo.py`, `agendamento/domain/nomes.py`, `portal/templates/portal/agenda_da_etapa.html`, `portal/views.py` | P:agenda_publica, U:conteudo |
| FR-7226 | T041, T042, T045, T086 | `agendamento/application/leitura.py`, `agendamento/domain/conteudo.py`, `agendamento/domain/nomes.py`, `agendamento/infrastructure/documento.py` | P:agenda_publica, U:conteudo, U:documento |
| FR-7227 | T045, T053 | `agendamento/application/leitura.py`, `portal/static/portal/portal.css`, `portal/templates/portal/_agendas_da_selecao.html`, `portal/templates/portal/agenda_da_etapa.html` | P:agenda_publica |
| FR-7228 | T046, T054 | `portal/static/portal/portal.css`, `portal/templates/portal/_horario_da_inscricao.html`, `portal/views.py` | P:horario_na_area_do_candidato |
| FR-7229 | T046, T054 | `agendamento/application/avisar.py`, `agendamento/application/leitura.py`, `agendamento/domain/mensagem.py`, `portal/templates/portal/_horario_da_inscricao.html` | I:conferencia, P:horario_na_area_do_candidato |
| FR-7230 | T088, T064, T068 | `avisos/application/despacho.py`, `avisos/domain/nomes.py` | I:avisos_da_agenda, GI:agenda_da_etapa_conferir, G:situacoes_de_mensagem |
| FR-7231 | T066, T067 | `agendamento/domain/mensagem.py` | I:avisos_da_agenda, U:mensagem |
| FR-7232 | T068 | — | I:avisos_da_agenda |
| FR-7233 | T068, T069, T072 | `agendamento/application/avisos_da_agenda.py`, `agendamento/application/reenviar.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_publicada.html` | I:avisos_da_agenda, GI:agenda_da_etapa_publicada |
| FR-7240 | T044, T057, T073, T075 | `agendamento/application/atos_individuais.py`, `agendamento/application/montar.py`, `agendamento/domain/recusas.py`, `interface/agenda_da_etapa.py` | I:atos_individuais, I:publicacao, GI:agenda_da_etapa_publicada |
| FR-7241 | T037, T040, T073, T077 | `agendamento/application/atos_individuais.py`, `agendamento/models.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_remarcar.html` | I:atos_imutaveis, I:atos_individuais |
| FR-7242 | T073, T077 | `agendamento/application/atos_individuais.py`, `agendamento/models.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_remarcar.html` | I:atos_individuais |
| FR-7243 | T073, T077 | `agendamento/application/atos_individuais.py`, `agendamento/models.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_cancelar.html` | I:atos_individuais |
| FR-7244 | T066, T073, T077 | `agendamento/application/atos_individuais.py`, `agendamento/domain/mensagem.py` | I:atos_individuais, U:mensagem |
| FR-7245 | T050, T076 | `agendamento/application/leitura.py`, `portal/templates/portal/_horario_da_inscricao.html`, `portal/templates/portal/agenda_da_etapa.html` | I:atos_individuais, P:agenda_publica, P:horario_na_area_do_candidato |
| FR-7246 | T073 | `agendamento/application/atos_individuais.py`, `agendamento/domain/conteudo.py`, `agendamento/infrastructure/documento.py`, `agendamento/models.py` | I:atos_individuais |
| FR-7247 | T074, T077 | `agendamento/application/atos_individuais.py` | I:atos_individuais, I:concorrencia_dos_atos |
| FR-7248 | T091 | `agendamento/application/atos_individuais.py`, `agendamento/application/leitura.py`, `agendamento/domain/conteudo.py` | I:atos_individuais, P:agenda_publica |
| FR-7250 | T059, T081, T084 | `agendamento/application/leitura.py` (`horarios_na_ocorrencia`), `interface/views.py` (`registrar_ocorrencia`) | I:fronteira, GI:vocabulario_da_agenda_da_etapa, GI:horario_na_ocorrencia |
| FR-7251 | T059 | — | I:fronteira, GI:vocabulario_da_agenda_da_etapa |
| FR-7252 | T059 | — | I:fronteira, GI:vocabulario_da_agenda_da_etapa |
| FR-7255 | T012, T016, T047, T089 | `agendamento/application/conferir.py`, `agendamento/application/configurar.py`, `interface/agenda_da_etapa.py` | I:publicacao, GI:agenda_da_etapa_conferir, GI:agenda_da_etapa_configurar |
| FR-7256 | T015, T024, T044, T073 | `agendamento/application/atos_individuais.py`, `agendamento/application/configurar.py`, `agendamento/application/publicar.py`, `agendamento/application/reenviar.py` | I:configuracao, I:publicacao |
| UX-760 | T014, T016, T020 | `agendamento/domain/configuracao.py`, `agendamento/domain/horarios.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/_agenda_capacidade.html` | GI:agenda_da_etapa_configurar, U:capacidade |
| UX-761 | T026, T031 | `interface/agenda_da_etapa.py`, `interface/templates/interface/_agenda_grade.html`, `interface/templates/interface/agenda_montar.html` | GI:agenda_da_etapa_montar, GI:agenda_da_etapa_no_estreito |
| UX-762 | T026, T031 | `interface/agenda_da_etapa.py`, `interface/templates/interface/_agenda_painel.html`, `interface/templates/interface/agenda_montar.html` | GI:agenda_da_etapa_montar |
| UX-763 | T032 | `interface/agenda_da_etapa.py`, `interface/static/interface/telas/agenda-da-etapa.css`, `interface/templates/interface/_agenda_grade.html`, `interface/templates/interface/agenda_montar.html` | GI:agenda_da_etapa_no_estreito |
| UX-764 | T026 | `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_montar.html` | GI:agenda_da_etapa_montar |
| UX-765 | T016, T021 | `interface/agenda_da_etapa.py`, `interface/templates/interface/distribuicao.html`, `interface/views.py` | GI:agenda_da_etapa_configurar |
| UX-766 | T008, T016, T020, T047, T052, T069 | `agendamento/application/conferir.py`, `agendamento/domain/recusas.py`, `interface/agenda_da_etapa.py`, `interface/templates/interface/agenda_configurar.html` | GI:agenda_da_etapa_conferir, GI:agenda_da_etapa_configurar, GI:agenda_da_etapa_publicada, U:configuracao |
| UX-767 | T022, T034 | `interface/agenda_da_etapa.py` | GI:agenda_da_etapa_no_estreito |
| SC-2390 | — | — | *(humano)* pendente de validação |
| SC-2391 | T006, T008 | `agendamento/domain/horarios.py` | U:horarios |
| SC-2392 | T023, T025 | — | I:concorrencia_da_montagem, I:montagem, U:preenchimento |
| SC-2393 | T043 | — | I:conferencia, I:publicacao |
| SC-2394 | T042, T045 | — | P:agenda_publica, U:conteudo |
| SC-2395 | T068, T073 | — | I:atos_individuais, I:avisos_da_agenda |
| SC-2396 | T044, T068 | `agendamento/application/publicar.py`, `agendamento/models.py` | I:avisos_da_agenda, I:publicacao |
| SC-2397 | T034, T035, T058, T061, T079 | — | GI:agenda_da_etapa_no_estreito |
| SC-2399 | T086, T087, T091 | `agendamento/infrastructure/documento.py`, `portal/views.py` | P:documento_da_agenda, U:documento |
| SC-2398 | — | — | *(humano)* pendente de validação |

## Achados (registro, e não escopo)

- **A-1 — A FR-7201 não tem teste próprio.** A Etapa acrescentada por Retificação continua servida
  porque a agenda guarda o `etapa_id`, sem chave estrangeira, e lê a Etapa da Versão Consolidada
  vigente; nenhum caso publica uma Retificação que acrescente Etapa e configura a agenda dela. O
  desenho cobre; o teste falta. Fica para quem tocar a Retificação de Etapas.
- **A-2 — O reenvio do aviso de agenda é da agenda, e não da tela de reenvio da `066`.** O contrato
  dizia que a agenda publicada levaria à tela da `066`; aquela tela recompõe um texto só para o
  universo, e o aviso de agenda tem o texto de uma pessoa. Segue o precedente da pendência da `134`:
  a `066` recusa (`aviso_de_agenda_sem_reenvio`) e a agenda publicada reenvia, pessoa a pessoa,
  num aviso filho com o mesmo texto (research T-024).
- **A-3 — A contagem da FR-084 no código é seis, e a da norma é sete.** A sexta situação, o aviso do
  desfecho da `156`, está escrita e não tem código; o guardião conta as implementadas
  (`test_situacoes_de_mensagem.py`). Quando a `156` for implementada, ela acrescenta o par dela.
