# 1. Diagnóstico: o que o GPS tem, e o que falta para agendar

*Estudo de 14/11/2026, sobre a `main` em `37ed0ad0`. Caminhos relativos a
`backend/processo_seletivo/`, salvo indicação. **[F]** é fato conferido no código ou na spec;
**[I]** é inferência; **[P]** é proposta deste estudo.*

## 1.1 A resposta curta

O GPS sabe **quem** faz cada Etapa e já tem as peças de **conferir, publicar e avisar**. Não sabe
**quando** cada pessoa é atendida: não existe horário por pessoa, banca como lugar de atendimento,
nem ato que diga "compareça às 8h15". O agendamento cabe como **uma camada fina sobre a Etapa**, que
lê a participação dela, publica pelo mesmo padrão da convocação e avisa pelo mesmo app de avisos.

## 1.2 A Etapa

- **[F]** `EtapaAvaliacao` (`editais/models/etapas.py:11-93`) tem nome livre, ordem, peso, caráter
  eliminatório e classificatório, nota mínima e máxima, `evaluations_per_registration`, `forma`
  (PONTUADA ou DECISORIA) e rótulos. **Não tem natureza** (entrevista, heteroidentificação), nem
  data, local ou duração próprios.
- **[F]** A Etapa aponta **um** Evento do cronograma (`evento`, `:57-63`; no conteúdo publicado,
  `scheduleEventId`). O Evento (`editais/models/cronograma.py:17-84`) tem `start_at`, `end_at` e
  um `location` de texto. É a única data da Etapa, e é norma: está no Edital publicado.
- **[F]** A Etapa é normativa. Depois da publicação, a fonte é a Versão Consolidada vigente, e não
  a tabela (`comissoes/domain/etapas.py:1-70`); a Retificação pode acrescentar Etapa sem linha em
  `EtapaAvaliacao` (`comissoes/models.py:6-12`). Por isso `AlocacaoEtapa` guarda `etapa_id` como
  UUID, e não FK (`comissoes/models.py:76-107`).
- **[F]** O `scheduleEventId` é **estrutural**: não se retifica (`editais/domain/mutabilidade.py:449-462`).
  As datas do Evento se retificam (`:421-448`).

**Consequência [P].** A agenda não pode ser campo da Etapa — mudá-la exigiria Retificação, e o
horário de cada pessoa não é norma. Ela é **operacional**, referida à Etapa pelo `etapa_id`, como a
alocação da comissão, e fica **dentro** do período que o Evento publica.

## 1.3 Quem participa

- **[F]** A fonte única é `resultados/application/prontidao.py`: `participacao_detalhada`
  (`:98-162`), `restringir_a_participantes` (`:408`), `participa_da_etapa` (`:477`),
  `motivo_de_nao_participar` (`:246`). Três regras: eliminada antes fica fora; habilitação na Etapa
  imediatamente anterior, quando ela já produziu Resultado; dentro da faixa do Corte vigente da `014`.
- **[F]** A lista **é uma projeção recalculada a cada leitura**, e não uma lista congelada. Muda
  com recurso que supera Resultado (`resultados/managers.py:25-35`), reabilitação
  (`classificacao/domain/universo.py:49-55`), Regularização (`resultados/models.py:57-66`), nova
  geração do Corte, e quando a Etapa anterior passa a ter Resultado.
- **[F]** Hoje toda Etapa vale para toda inscrição enviada. O **alcance por Modalidade**, que a
  heteroidentificação pede, é a `163` (#542, mergeada em 14/11, depois deste diagnóstico).

**Consequência [P].** A agenda **não tem lista própria**: lê a projeção, e mostra a diferença entre
o que está agendado e quem participa — "sem horário" e "agendada que não participa mais". A
publicação congela o que foi publicado, e não a participação.

## 1.4 Avaliação e comissão

- **[F]** A comissão é do Processo (`MembroComissao`, `comissoes/models.py:31`, PRESIDENTE ou
  MEMBRO); `AlocacaoEtapa` liga membro e Etapa. A distribuição cria `Atribuicao`
  (`avaliacoes/application/distribuicao.py:270`), a Mesa registra `Avaliacao`, e a consolidação
  produz `ResultadoEtapa` (`resultados/application/consolidacao.py:315`).
- **[F]** **Não existe banca como entidade.** "Banca" é texto de tela
  (`interface/templates/interface/distribuicao.html:34`).
- **[F]** A ausência é **Ocorrência** na Etapa, que vira `ResultadoEtapa` ELIMINADA
  (`resultados/application/ocorrencia.py:1-35`), sem ligação com convocação nem horário.

**Consequência [P].** Banca, na agenda, é **ponto de atendimento** (nome e local ou sala), e não
grupo de avaliadores. A avaliação continua onde está. Nada no agendamento produz Resultado.

## 1.5 Conferir, publicar, avisar

- **[F] Conferência sem efeito.** `convocacao/application/fluxo.py:405`
  (`conferencia_dos_titulares`, `140`) não abre comando nem reserva chave, e usa as mesmas recusas
  do comando. A tela é `interface/templates/interface/convocacao_conferir.html`: o ato irreversível
  em destaque, quem fica de fora, o que cada pessoa lê, o que será público, a autoridade.
- **[F] Assinatura e idempotência.** A prévia gera uma assinatura (`convocacao/domain/alcance.py:100`)
  que a confirmação confere (`ALCANCE_MUDOU`, 409). A chave de idempotência
  (`shared/idempotency.py`, `IdempotencyRecord` com `UNIQUE(scope, actor, operation, key)`) faz a
  repetição devolver o mesmo desfecho.
- **[F] Trava.** O comando trava o Processo (`select_for_update`, `comissoes/application/__init__.py:76-91`).
  Em tabela append-only, a role de runtime não tem `UPDATE`, e por isso não pode `FOR UPDATE`; usa
  advisory lock, e a última guarda é UNIQUE com tradução do `IntegrityError` (`avisos/application/despacho.py:21-22`;
  `convocacao/application/publicar.py:529-531`).
- **[F] Publicação.** `PublicacaoDeConvocados` (`convocacao/models.py:660-770`, `149`) guarda o
  conteúdo público em bytes canônicos e SHA-256, com autoridade signatária; não tem sucessão: a
  correção sai na seguinte, marcada. A página pública lê os bytes gravados
  (`portal/views.py:3773`).
- **[F] Identificação pública.** Nome e protocolo; proibidos CPF inteiro ou parcial, e-mail,
  telefone, desfecho e espécie (`specs/149-publicacao-das-convocacoes/spec.md:327`).
- **[F] Veículo e prazo.** Na `159`, o operador escolhe publicar no GPS (e declara onde o Edital
  admite a página como veículo) ou registrar a publicação feita fora; o prazo corre da publicação
  ou do envio (`convocacao/domain/prazo.py:1-18`).
- **[F] Avisos (`066`).** `Aviso`, `DestinatarioDoAviso` (`UNIQUE(aviso, inscricao)`),
  `TentativaDeEnvio` e `ResultadoDaTentativa` são append-only (`avisos/models.py`). A confirmação
  **não envia**; o despacho roda a cada minuto (`avisos/application/despacho.py:388`). Cada origem
  cita o seu ato (`avisos/models.py:132-146`). As origens hoje são RESULTADO, CHAMADA e PENDENCIA
  (`avisos/domain/nomes.py:15`). Falha temporária é retentada; indeterminada só sai por reenvio
  confirmado por pessoa (`avisos/application/confirmar.py:366`).
- **[F] FR-084.** A lista de situações em que o sistema manda mensagem é **fechada**
  (`specs/010-area-do-candidato/spec.md:572`), e o guardião
  `tests/test_situacoes_de_mensagem.py:42-91` falha se um módulo novo enviar. Uma situação nova
  pede revisar a FR-084 — já revista três vezes (`010`, `019`, `066`).

**Consequência [P].** Publicar a agenda é o mesmo gesto da `149`/`159`, com outro conteúdo; avisar é
**uma origem nova do app de avisos**, e não um envio novo.

## 1.6 A área do candidato e a página pública

- **[F]** A situação da inscrição é `portal/situacao.py:213` (`situacao_da_inscricao`, `063`), com
  estados em `:42-56`. **Nenhum diz "convocado para comparecer"**.
- **[F]** A página pública da seleção é `portal/templates/portal/selecao.html`, que já inclui as
  convocações publicadas; a relação pública de convocados é `portal/templates/portal/convocados.html`.

## 1.7 O que os Editais reais pedem

Amostra em `~/Downloads`, lida em 14/11.

| Edital | O que diz sobre o horário |
|---|---|
| **28/2026** (Pós em Informática na Educação), 6.9 | Pretos e pardos convocados "por meio de listagem divulgada"; o link da sala vem "no ato da convocação"; entrar até 5 min antes; no nome, o **número do documento**; menor com responsável; 3 tentativas de conexão; queda > 10 min cancela e **reagenda por e-mail**; justificativa em **24 h a partir do horário marcado**; ausência indefere |
| **140/2025** (Tutor UAB), 8 | Mesmas regras; até 3 candidatos por código convocados; "só terá direito a nova convocação se justificar"; gravada |
| **90/2026** (Tutor TADS), 4 | Mesmas regras; **um só reagendamento** a pedido, justificado no mesmo dia |
| **146/2025** (Assistente pedagógico), 15 | Entrevista com 3 classificados; "datas, horários e o endereço da sala virtual serão divulgados conforme o cronograma"; "cabe ao candidato acompanhar as publicações"; quem falta é desclassificado |

Três conclusões:

1. **[F]** O horário é **publicado**, e a publicação é o que vale; o e-mail aparece como canal de
   reagendamento, e não de convocação.
2. **[F]** O horário **tem efeito**: a justificativa da ausência conta dele, e a ausência elimina.
   Publicar a agenda não é só informar.
3. **[F]** O endereço da sala vai **a cada pessoa**, e o candidato entra na sala com o número do
   documento, e não com o nome — o próprio Edital evita expor quem é quem.

## 1.8 O que já foi dito sobre isto

- **[F]** `doc/registro-convocacao-para-etapas-2026-10-09.md` registra a lacuna: "Não há horário
  por pessoa", e lista cinco perguntas — ato próprio com lista congelada; quem é alcançado na
  heteroidentificação; horário individual; exposição da Modalidade; relação com o aviso. Este estudo
  responde às cinco (`02-proposta.md` §2.9).
- **[F]** A `066` registrou "agendamento fica fora" do MVP de avisos (`specs/066-avisos-complementares/spec.md:101`).
- **[F]** O estudo da verificação da autodeclaração (PR #541) deixou de fora a "agenda individual
  da entrevista ao vivo", "porque serve a qualquer entrevista, e não só a esta". As specs `163`
  (alcance), `164` (efeito por lista) e `165` (deliberação) — as três mergeadas em 14/11, depois deste
  diagnóstico — fazem da
  heteroidentificação uma Etapa. **O agendamento é a peça que faltava a elas**, e não concorre com
  nenhuma.

## 1.9 Lacunas

| Lacuna | Onde aparece | Quem resolve |
|---|---|---|
| Horário por pessoa | não existe | **este estudo** |
| Banca como ponto de atendimento | só texto de tela | **este estudo**, sem avaliadores |
| Ato de comparecimento à Etapa | `registro-convocacao-para-etapas` | **este estudo**, como publicação da agenda |
| Aviso de horário | FR-084 fechada; origens da `066` | **este estudo**, origem nova, com revisão da FR-084 |
| Degrau "seu horário" no acompanhamento | `portal/situacao.py` | **este estudo** |
| Etapa só para quem declarou a Modalidade | `prontidao.py` sem filtro | `163` (#542, mergeada) |
| Natureza da Etapa (entrevista × análise) | `EtapaAvaliacao` sem campo | **não é preciso**: a agenda existe ou não; ver `02-proposta.md` §2.1 |
| Presença registrada | Ocorrência existe | **não é preciso** |
