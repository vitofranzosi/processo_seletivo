# Research — Avisos complementares (066)

*Decisões técnicas do plano, de 09/10/2026. Numeradas `R-`, porque `D-001` a `D-008` são da spec. As
afirmações sobre o código foram conferidas na `main` em `4ace3722`. Caminhos relativos a
`backend/processo_seletivo/`.*

---

## R-001 — Um app novo, `avisos`, e nada de "comunicação" genérica

**Decision**: o app `avisos` tem os modelos, o domínio (composição da mensagem, variáveis,
estados), a aplicação (destinatários, confirmação, despacho, interrupção) e um comando
`despachar_avisos`. As telas ficam em `interface/`, como as de todas as features da gestão.

**Rationale**: o aviso cita atos de dois apps, `divulgacao` e `convocacao`, e não pertence a nenhum
deles. Pô-lo em `convocacao` faria a comunicação com efeito e o aviso sem efeito dividirem módulo,
que é a confusão que a `D-001` proíbe. Pô-lo em `divulgacao` daria à publicação um remetente, e a
`017` revisada diz que publicar não envia nada.

**Alternatives considered**: (a) estender `ComunicacaoEmitida` com uma forma "aviso", recusada pela
`FR-1242`, que proíbe tocar nela; (b) um app `comunicacao` genérico, para futuros canais, recusado
pelo Princípio V: não há segundo canal demonstrado.

## R-002 — A concorrência se resolve com trava consultiva, porque `FOR UPDATE` não é possível

**Decision**: há três camadas, cada uma suficiente para o que guarda.

1. **Uma execução do despacho por vez.** `pg_try_advisory_lock` com uma constante. A execução que
   não obtém a trava sai em silêncio. É o padrão de `requerimentos/management/commands/carregar_ceps.py:163`.
2. **Interrupção e início de tentativa serializados por aviso.** `pg_advisory_xact_lock(aviso)` na
   transação curta que confere a interrupção e grava o início da tentativa, e na transação que grava
   a interrupção. É o padrão de `inscricoes/application/submissao.py:59`.
3. **`UNIQUE (destinatario, numero)` em `TentativaDeEnvio`.** É a última porta: duas inserções da
   mesma tentativa colidem no banco, venham de onde vierem.

**Rationale**: as tabelas de tentativa são append-only, e a role de runtime não tem `UPDATE` sobre
elas. **O PostgreSQL exige `UPDATE` para `SELECT … FOR UPDATE`.** Isso foi verificado nesta máquina
em 09/10/2026, com uma role com `SELECT, INSERT`:

- `FOR UPDATE` respondeu `permission denied for table t`;
- `pg_advisory_xact_lock(42)` funcionou.

Nenhum `select_for_update` do código atual cai sobre tabela append-only, e esta feature não pode ser
a primeira.

A camada 1 tem uma consequência que simplifica o resto (R-004): com uma execução só, **tentativa
sem resultado é sempre de uma execução que morreu**.

**Alternatives considered**: (a) uma coluna de estado no destinatário, com `UPDATE`, recusada porque
a tabela seria a única não append-only do envio e reabriria a mutação que o resto do sistema fechou;
(b) `SKIP LOCKED` para paralelizar o despacho, recusado porque exige `FOR UPDATE` e porque o limite de
envio (R-005) torna o paralelismo inútil; (c) confiar só no timer do systemd, que não sobrepõe um
serviço `oneshot` ativo, recusado como camada única porque um `manage.py despachar_avisos` à mão o
contornaria.

## R-003 — A tentativa tem duas gravações: o início antes do servidor, o resultado depois

**Decision**: para cada destinatário, numa transação curta e própria:

1. trava o aviso (R-002, camada 2);
2. confere que o aviso não foi interrompido;
3. insere `TentativaDeEnvio(destinatario, numero, iniciada_em)`;
4. confirma a transação.

Só então chama o servidor de correio, **fora de transação**. A resposta vira
`ResultadoDaTentativa(tentativa, resultado, detalhe_tecnico)`, numa segunda transação curta.

**Rationale**: é a ordem que `convocacao/application/comunicar.py` escreve — reservar, conferir,
enviar, gravar —, aplicada por destinatário. O início confirmado antes da rede é o que torna a
queda observável (`FR-1266`). Tentativa sem resultado é indeterminada, e o despacho nunca a repete
(`FR-1267`).

**Alternatives considered**: gravar só o resultado, depois do envio, recusado porque a queda entre o
aceite e a gravação reenviaria a mensagem na execução seguinte. É o caso que o usuário nomeou.

## R-004 — Classificar pela fase da conversa SMTP, e só por código quando ele é resposta

*Revisto na aprovação do plano, de 09/10/2026: "nem todo erro 4xx ou 5xx significa que o sistema
conhece com segurança o estado final da mensagem".*

**Decision**: o despacho abre **uma** conexão por execução, por `django.core.mail.get_connection()`,
e a abre **antes** de qualquer tentativa. Cada mensagem é preparada e validada **antes** de ir à
rede. A classificação segue a fase em que a resposta veio:

| Fase | O que acontece | Resultado |
|---|---|---|
| **0. Abertura** (conexão, `EHLO`, `STARTTLS`, `AUTH`) | qualquer falha | **nenhuma tentativa registrada**. A execução termina com saída diferente de 0, e a seguinte tenta de novo. Nenhum byte de mensagem saiu |
| **1. Preparação** (endereço, cabeçalhos, codificação), antes da rede | `ValueError` ou `UnicodeError` ao sanear o endereço ou montar a mensagem | **FALHA_DEFINITIVA**, "endereço ou conteúdo inválido". A tentativa existe, mas nada foi ao servidor |
| **2. `MAIL FROM`** | resposta com código de três dígitos 4xx ou 5xx (`SMTPSenderRefused`) | 4xx → **FALHA_TEMPORARIA**; 5xx → **FALHA_DEFINITIVA**. O servidor recusou antes do conteúdo |
| **3. `RCPT TO`** | idem (`SMTPRecipientsRefused`, um destinatário só) | idem |
| **4. `DATA`** | resposta diferente de 354, com código 4xx ou 5xx (`SMTPDataError`) | idem: o conteúdo nem começou |
| **5. Conteúdo e `.` final** | resposta **250** à confirmação final | **ACEITA** |
| | resposta 4xx ou 5xx **lida** à confirmação final (`SMTPDataError`) | 4xx → **FALHA_TEMPORARIA**; 5xx → **FALHA_DEFINITIVA**. O servidor disse, por resposta, que não aceitou |
| **Qualquer fase de 2 a 5** | conexão fechada (`SMTPServerDisconnected`), timeout (`socket.timeout`, `OSError`), resposta ilegível (o `smtplib` devolve código `-1`) ou qualquer código fora de 400–599 | **INDETERMINADA**, e a execução **para** |
| — | `send_messages` devolve 0 sem exceção | **FALHA_TEMPORARIA**, pelo critério de `comunicar.py:359-378` (zero não é sucesso). O limite de tentativas a torna definitiva |
| — | tentativa sem resultado, encontrada por uma execução que tem a trava global | **INDETERMINADA**, gravada pela execução que a encontrou |

**O código só classifica quando é resposta a um comando, e foi lido inteiro.** Por isso o código
`-1`, que o `smtplib` usa para resposta que não conseguiu interpretar, vai para indeterminada, e não
para falha: ele parece código e não é resposta.

**A fase 1 antes da rede** é o que separa endereço inválido de falha de transporte. Sanear o endereço
e montar a mensagem (`message.message()`) antes de chamar o servidor faz o `ValueError` acontecer
onde se sabe que nada saiu.

**A distinção de fase não vem do texto da exceção.** Vem do tipo e da presença de código válido. O
`smtplib` levanta `SMTPSenderRefused`, `SMTPRecipientsRefused` e `SMTPDataError` só quando leu uma
resposta. Desconexão e timeout têm tipos próprios. A classificação é função pura de
`avisos/domain/resposta.py`, testada com cada caso da tabela.

**Rationale**: é a única distinção que o protocolo permite fazer sem adivinhar. A resposta lida diz
que o servidor **recusou**. Silêncio, desconexão ou resposta ilegível não dizem nada, e ficam
indeterminados mesmo quando vêm acompanhados de algo que parece código.

**Alternatives considered**: (a) tratar toda exceção como falha temporária, recusado porque
reenviaria mensagens que podem ter saído; (b) tratar toda exceção como indeterminada, recusado
porque uma recusa explícita de servidor ocupado (4xx) pararia o aviso inteiro à espera de uma
pessoa; (c) classificar só pelo código numérico, recusado na revisão: `-1` e um código lido depois
de uma queda não são resposta do servidor.

## R-005 — O ritmo é o do timer: N mensagens por execução, uma execução por minuto

**Decision**: o despacho tenta no máximo `AVISOS_LIMITE_POR_MINUTO` destinatários por execução
(padrão 60), e o timer roda a cada minuto.

- **Retentativa de falha temporária**: a 2ª tentativa depois de 5 min, a 3ª depois de 15. Esgotadas
  `AVISOS_MAX_TENTATIVAS` (padrão 3), a falha é definitiva.
- **A ordem é a da confirmação dos avisos**, e dentro de cada aviso a do protocolo, para que um aviso
  grande não passe à frente de um pequeno confirmado antes.

**Rationale**: sem fila e sem worker, o limite por minuto sai de graça do próprio relógio. Uma
execução lenta não se sobrepõe à seguinte (R-002, camada 1).

**Alternatives considered**: `sleep` entre mensagens dentro de uma execução longa, recusado porque
seria um worker disfarçado de comando, com vida longa e sem supervisão.

## R-006 — `EMAIL_TIMEOUT` em `base.py`, valendo para os quatro envios

**Decision**: `EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))` em `config/settings/base.py`.
O backend SMTP do Django o aplica à conexão, e com isso o código de acesso, o comprovante, a
convocação e o aviso passam a ter limite. O runbook registra o gap I-4 como resolvido.

**Rationale**: é a `FR-1270`, e corrige um defeito que já afeta o único fator de autenticação do
candidato (`doc/implantacao-em-producao-ubuntu.md`, §16.2).

**Alternatives considered**: um timeout só no despacho, recusado porque deixaria o código de acesso
prendendo o worker até os 120 s do gunicorn.

## R-007 — O texto é congelado na confirmação; só o nome se resolve no envio

**Decision**: na confirmação, uma requisição HTTP, o sistema:

- resolve todas as variáveis, menos `{nome_do_candidato}`;
- monta os links com `request.build_absolute_uri`, como as views da convocação já fazem
  (`interface/views.py:7491`);
- acrescenta a linha de retificação, quando houver, e o rodapé;
- grava em `Aviso.assunto` e `Aviso.corpo` o texto exato que sairá.

No envio, `{nome_do_candidato}` vem de `Inscricao.nome`, que não muda depois da submissão
(`inscricoes/models.py:113-134`).

**Rationale**: o registro diz exatamente o que saiu, menos o nome, que é dado da inscrição citada.
O despacho não precisa conhecer o endereço público do sistema, e por isso **não nasce configuração
nova de URL-base**. Mudar o rodapé num deploy futuro não reescreve o que avisos antigos dizem ter
enviado.

**Alternatives considered**: renderizar no envio a partir do modelo, recusado pela `FR-1261`.
Guardar o corpo por destinatário, recusado porque guardaria 500 cópias de um texto em que só o nome
muda.

## R-008 — Três variáveis de destino, cada uma com um significado

*Revisto na aprovação do plano, de 09/10/2026: "não utilize uma variável com nome de publicação
específica para representar indistintamente a página geral do Edital".*

**Decision**:

| Variável | Valor | Quando existe |
|---|---|---|
| `{link_da_publicacao}` | endereço permanente da publicação no portal, `selecoes/resultados/<id>/` (`portal/urls.py:92`) | só quando o aviso de resultado cita **uma** publicação |
| `{pagina_do_processo_seletivo}` | `selecoes/<edital_id>/`, que lista as publicações vigentes por Perfil, marco e lista (`062`) | sempre |
| `{referencia_da_publicacao}` | a referência que a comunicação da chamada declarou, como foi escrita | só na chamada |
| `{area_do_candidato}` | `portal:inscricoes`, sem token | sempre |

O rodapé escolhe por si, nessa ordem: o link da publicação quando ele existe; a referência
declarada na chamada; a página do processo seletivo.

**A URL histórica continua válida.** A publicação sucedida continua respondendo no mesmo endereço e
aponta a vigente (`portal/views.py:2526-2545`). Por isso o link congelado num aviso antigo leva à
retificadora sem que o aviso precise mudar (`FR-1255a`). Um teste prende isso: avisar sobre uma
publicação, retificá-la e seguir o link do aviso.

**Rationale**: o aviso que cobre várias listas manda o mesmo texto a todos. Um link de publicação
nele teria de variar por pessoa, e levaria cada uma à página da lista dela. Melhor não haver link de
publicação ali, e haver a página do processo.

## R-009 — Um contexto de comando próprio, montado com as peças que já existem

**Decision**: `avisos/application/comando.py` define `comando_de_aviso`, irmão de
`comando_de_comissao` (`comissoes/application/__init__.py:76`), com a mesma ordem:

1. `command_context` (transação e instante);
2. `ProcessoSeletivo` com `select_for_update`, filtrado pelo escopo. O Processo é mutável, e o lock
   é permitido;
3. autorização pela origem (`D-004`);
4. `ensure_processo_accepts_changes`;
5. `reservar` da idempotência (`shared/idempotency.py:6`).

A autorização, pela origem:

| Origem | Quem pode |
|---|---|
| resultado | `actor.can("aviso:enviar")` **ou** `pode_gerir_comissao`. O gestor já passa pela primeira; a segunda é a que admite a presidência ativa |
| chamada | `pode_gerir_comissao` (`comissoes/domain/autorizacao.py:65`), a porta de `comunicar` |
| modelos | `aviso:enviar` |

`aviso:enviar` entra em `PAPEIS` (`interface/identidade.py:20`), nos papéis publicador e gestor.

**Rationale**: reaproveitar `comando_de_comissao` direto barraria o publicador, que não tem base de
comissão. O lock do Processo dentro da transação é o que impede duas confirmações simultâneas de
criarem dois avisos sobre as mesmas publicações, porque a conferência de "já avisada" corre sob ele.

**Alternatives considered**: uma trava consultiva por marco, recusada porque o lock do Processo já
existe, é o que os demais comandos tomam, e o aviso não é frequente a ponto de disputá-lo.

## R-010 — A prévia é assinada pelo conjunto, como a publicação

**Decision**: a assinatura é `canonical_sha256` de origem, publicações citadas (ou recorte e
referência), destinatários do universo com elegibilidade e endereço resolvido, e se é reenvio. Ela
segue o desenho de `assinatura_da_previa` (`divulgacao/application/publicar.py:68`). O texto,
o modelo e a justificativa **não** entram: são entrada do operador, validados e não assinados, pelo
mesmo argumento escrito ali.

**Rationale**: é a `FR-1259`. Uma retificação publicada, um desfecho registrado ou uma credencial
trocada entre a prévia e a confirmação mudam a assinatura, e a confirmação é recusada.

## R-011 — Reenvio é um aviso novo, filho do anterior

**Decision**: o reenvio cria um `Aviso` com `aviso_anterior` e motivo `REENVIO_DE_FALHAS` ou
`REENVIO_JUSTIFICADO`.

- Os destinatários são os do anterior no estado escolhido: falha definitiva, ou indeterminada.
- O texto é **o mesmo**, copiado do anterior.
- A justificativa é obrigatória quando entram indeterminadas (`FR-1264`).

O reenvio intencional de uma publicação inteira (`FR-1262`) é a mesma coisa, com universo completo e
justificativa obrigatória.

**Rationale**: o reenvio passa pelo mesmo caminho — prévia, confirmação, despacho, histórico — sem
tabela nem estado novos. "Pendente outra vez" não precisa existir: o destinatário do aviso filho
nasce pendente.

**Alternatives considered**: uma tabela de pedidos de reenvio que reabre o destinatário, recusada
porque obrigaria toda leitura de estado a considerar reaberturas.

## R-012 — Os modelos iniciais nascem em `sincronizar_unidades`, uma vez

**Decision**: `sincronizar_unidades` (`unidades/application/sincronizacao.py`), que o
`make preparar` já roda, chama `garantir_modelos_iniciais(unidade)` para cada unidade. A função
cria os três modelos (`modelo_inicial=True`) **só se a unidade não tiver nenhum modelo inicial**, e
registra o evento na trilha.

- Modelos nunca são excluídos, e por isso a conferência é estável: a unidade que inativou os três
  continua tendo-os, e nada se recria.
- Os textos são constantes em `avisos/domain/modelos_iniciais.py`.
- Na suíte, a mesma função entra na fixture que já registra o Cefor (`AGENTS.md`, *Subir o
  ambiente*).

**Idempotência e não sobrescrita.** A função só **insere**, e nunca atualiza nem relê texto. Duas
sincronizações simultâneas não duplicam, por dois motivos:

- `sincronizar_unidades` já trava as unidades com `select_for_update` (`sincronizacao.py:99`), e a
  segunda espera a primeira;
- o índice único de nome por escopo (data-model §1.1) recusa a cópia, se algum dia a trava não
  estiver lá.

**Rationale**: é o único ponto que já percorre todas as unidades com autor e trilha. Ele não pode ser
data migration (`test_migrations_do_not_import_domain_or_application_code`, citado em
`sincronizacao.py`) e não deve ser escrita em GET.

**Alternatives considered**: (a) criar ao abrir a tela de modelos pela primeira vez, recusado porque
seria escrita num GET; (b) data migration, recusada pelo teste citado e porque ficaria sem evento
na trilha.

## R-013 — A chave de habilitação bloqueia a confirmação e o despacho (**aprovada**)

*Aprovada na revisão do plano, de 09/10/2026, com dois acréscimos: bloquear também a confirmação, e
não deixar a reativação disparar mensagem antiga.*

**Decision**: `AVISOS_AOS_CANDIDATOS = os.getenv("AVISOS_AOS_CANDIDATOS", "false") == "true"`.
Ligada no `development` e no `test`, e desligada por padrão em produção.

- **Desligada**:
  - a prévia de aviso e de reenvio abre só com a explicação, sem formulário de confirmação;
  - o POST de confirmação recusa com `aviso_envio_desabilitado`;
  - o despacho sai com 0 sem iniciar tentativa;
  - o histórico, a interrupção e os modelos continuam disponíveis.
- **Religada**: só sai o que ainda estiver dentro da janela de despacho (`R-016`). O que ficou fora
  dela expira sem envio, e só um aviso filho o reenvia.

**Rationale**: a decisão 10 da spec exige a validação institucional antes de produção. A chave
deixa o código entrar sem que o envio exista.

## R-014 — Telas: as que já existem ganham um botão; as novas copiam padrões existentes

**Decision**:

| Superfície | Mudança | Padrão de origem |
|---|---|---|
| `publicacoes_do_marco.html` | botão e linha de estado do aviso por natureza | o link "Página pública" da mesma tabela |
| `convocacao.html` | no cartão da chamada por publicação, "Avisar os convocados desta publicação" | a seção "Comunicações que ainda não saíram" |
| nova `aviso_previa.html` | prévia e confirmação | `previa_de_publicacao.html` (não grava; assinatura em campo oculto) e o `<ol class="consequencias">` de `convocacao.html` |
| nova `aviso.html` | histórico do aviso, com interromper e reenviar | `_resultado_da_comunicacao.html` |
| nova `avisos_do_edital.html` | lista de avisos do Edital | `convocacao_historico.html` |
| novas `modelos_de_aviso.html` e `modelo_de_aviso.html` | gestão de modelos | os formulários de `interface/forms.py` |

Tudo é POST-redirect-GET e não usa htmx. O htmx não troca 4xx (`AGENTS.md`), e nada aqui precisa
de fragmento.

## R-015 — Os guardiões que esta feature vai acionar, listados antes

| Guardião | O que muda |
|---|---|
| `tests/test_situacoes_de_mensagem.py` | `SITUACOES` ganha `avisos/application/despacho.py`; `test_sao_tres_situacoes…` vira quatro; a conferência da spec lê "revisada pela `066`" e a data |
| `seguranca/papeis.py` (`TABELAS_APPEND_ONLY`) | +6 tabelas. O `M` do `provisionar_papeis` vai de 34 para **40**, e o `AGENTS.md` acompanha |
| `tests/migrations/test_migrations.py` | contagem do app novo, com justificativa, e os gatilhos em `TRIGGERS_POR_APP` |
| inventário de negativas da `033` | cada `Http404` novo precisa de linha |
| varreduras de vocabulário com lista literal | as telas novas entram na lista. Uma tela nova escapa calada |
| `test_acessibilidade*` e `test_estaticos` | toda classe nova precisa de regra na folha. CSS com `}}` numa linha reprova |
| `test_orcamento_de_consulta` | o histórico do aviso é medido com 500 destinatários: consultas constantes |
| `tests/test_citacoes_de_requisito.py` | toda citação de requisito desta feature no código precisa existir na spec |

**Rationale**: cada um já custou sessões quando descoberto no fim da suíte de 15 minutos. Listá-los
no plano faz as tarefas os incluírem.

## R-016 — Janela de despacho, para que nada antigo saia de repente

**Decision**: todo destinatário só é alcançado pelo despacho dentro de
`AVISOS_JANELA_DE_DESPACHO_HORAS` (padrão 24) contadas de `Aviso.solicitado_em`. Fora dela, o estado
derivado é **Expirada sem envio** (data-model §2), e nada é gravado: o estado se deriva do instante,
como o vencimento da convocação.

**Rationale**: é o que satisfaz "a simples reativação não produz disparo de mensagem antiga" sem
saber quando a chave mudou. A chave é variável de ambiente, e o banco não a vê mudar. A mesma regra
cobre o timer parado por dias, e a chamada cujo prazo passou enquanto o aviso esperava. As
retentativas de 5 e 15 minutos cabem na janela com folga.

**Alternatives considered**: (a) uma tabela de ativações gravada no deploy, recusada porque o
esquecimento dela produziria o disparo que ela existe para impedir; (b) o despacho registrar
interrupção de sistema sempre que encontrasse a chave desligada, recusado porque não cobre o caso
de chave desligada **e** timer parado, que é justamente o de produção antes da ativação; (c)
reconferir a elegibilidade da chamada no envio, recusado porque mudaria o universo congelado na
confirmação (`FR-1253`) e não resolveria o aviso de resultado antigo.
