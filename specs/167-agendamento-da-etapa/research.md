# Research: O agendamento dos participantes da Etapa

Decisões técnicas da `167`. Cada uma diz o que foi escolhido, por quê e o que foi descartado. Os
identificadores `T-` são locais a este documento; as decisões de produto são as `D-001` a `D-010` da
[spec](spec.md), e as regras `R-01` a `R-26` são as da proposta do estudo
(`doc/estudo-agendamento-da-etapa-2026-11-14/02-proposta.md`).

Os fatos de código foram conferidos em 14/11/2026 sobre a `main` em `cf6327c8` (a `163`, a `164` e a
`165` já mergeadas). Onde o diagnóstico do estudo divergia do código, a divergência está anotada na
decisão que ela muda — são cinco, resumidas no fim (*O que o diagnóstico não dizia*).

Caminhos relativos a `backend/processo_seletivo/`, salvo indicação.

## T-001 — Um app novo, `agendamento`, e nunca o nome "agenda" sozinho

**Decisão.** O domínio, a aplicação e as tabelas ficam num app próprio, `processo_seletivo.agendamento`,
com `domain/`, `application/` e `migrations/`, como a `formalizacao` da `117`. Ele **lê** `editais`,
`comissoes`, `resultados`, `inscricoes`, `unidades`, `publicacoes` e `avisos`; nenhum deles passa a
conhecê-lo. As telas da gestão ficam num módulo de interface próprio, `interface/agenda_da_etapa.py`, e
as do portal em `portal/views.py`, como as da `149`.

Os nomes de arquivo, rota, folha e template levam **"agenda da Etapa"** ou **"agendamento"**, nunca
`agenda` sozinho.

**Por quê.** `interface/agenda.py`, a rota `interface:agenda` e a folha `telas/agenda.css` já são da
**Agenda dos Editais** (`101`), uma projeção de leitura do cronograma de todos os Editais, que aparece
como "Agenda" na barra da gestão. Um segundo `agenda.py` ou uma segunda `agenda.css` colidiria na
importação e no guardião das folhas, e confundiria quem lê. A comissão continua lendo "Agenda" na
seção da página da Etapa, onde o contexto desfaz a ambiguidade.

App próprio, e não dentro de `comissoes`, porque as migrations de `comissoes`, `editais` e `resultados`
têm contagem fixada por guardião (`tests/migrations/test_migrations.py`, as da `011`, da `017` e da
`022`), e porque o ato é outro: nem alocar, nem avaliar, nem convocar para vaga (`D-005`).

**Descartado.** Pôr a agenda em `convocacao`: a convocação é de vaga, e a ocupação enxergaria
convocados que ninguém chamou (`D-005`). Pôr em `comissoes`: mexeria na contagem guardada e misturaria
a alocação de pessoas com o horário de candidatos.

## T-002 — A Etapa é lida da Versão Consolidada, pelo `etapa_id`

**Decisão.** `AgendaDaEtapa` guarda `edital` (FK) e `etapa_id` (UUID, sem FK), com
`UNIQUE(edital, etapa_id)`, como `AlocacaoEtapa` (`comissoes/models.py:76`). A Etapa é lida por
`comissoes.domain.etapas.etapa_vigente(edital, etapa_id)` — o dict vigente da Versão Consolidada, com
`name`, `forma`, `scheduleEventId` e `modalityCodes` — e o Evento por
`evento_vigente(edital, etapa["scheduleEventId"])`, com `startAt` e `endAt` em ISO, como faz
`minha_etapa` (`interface/views.py:12373`). A Etapa ausente da versão vigente é 404.

**Por quê.** Depois da publicação a fonte da Etapa é a Versão Consolidada, e a Retificação pode
acrescentar Etapa sem linha em `EtapaAvaliacao` (FR-7201). O Evento é retificável nas datas, e por isso
é relido a cada conferência (FR-7221), nunca copiado para a agenda.

**Descartado.** FK para `EtapaAvaliacao` — não existe linha para a Etapa da Retificação. Copiar o
período do Evento para a agenda — divergiria na primeira Retificação.

## T-003 — Os horários são uma função pura da configuração

**Decisão.** `agendamento/domain/horarios.py` expõe `derivar(configuracao) -> tuple[Horario, ...]`,
em que `Horario` é um valor imutável `(dia, inicio, fim, banca_id)`, e `inicio`/`fim` são instantes
com fuso, construídos pela data local do dia e pela hora local da janela em `America/Sao_Paulo`
(`settings.TIME_ZONE`, a zona institucional). Em cada janela, `t = início`; enquanto
`t + duração ≤ fim`, há um horário em `t` em cada banca, e `t += duração + intervalo` (FR-7203). A
ordem natural é `(inicio, banca.ordem)`. A identidade de um horário é `(banca_id, inicio)`, a mesma do
`UNIQUE` do agendamento.

A função recebe um valor de configuração (`Configuracao`, com `forma`, `duracao`, `intervalo`,
`dias`, `bancas`), e não o modelo: a tela de configurar a chama sobre o que está sendo digitado, sem
gravar (T-006), e o comando a chama sobre o que está gravado.

**Por quê.** É a `D-003`: gravar os horários seria a segunda fonte. A aritmética em minutos sobre a
data local evita o erro de somar `timedelta` a um instante perto de transição de horário — que hoje o
Brasil não tem, mas a zona sim, na história.

**Descartado.** Uma tabela de horários. Um gerador em JavaScript espelhando o Python, como o
protótipo, que não tinha servidor: seriam duas fontes da FR-7203, e o SC-2391 precisaria de duas
provas.

## T-004 — A sobra é o que fica depois do último atendimento e do intervalo

**Decisão.** Em cada janela com ao menos um horário, `sobra = fim − (fim do último atendimento) −
intervalo`; é informada quando positiva (FR-7206), e nunca recusa. É `sobras(configuracao)` em
`horarios.py`.

**Por quê.** O intervalo depois do último atendimento é a pausa que a própria configuração pede, e não
tempo perdido: 08:00–12:00 com 10 + 5 termina às 11:55, e os 5 minutos não são sobra. É a regra que o
protótipo já mostrava.

## T-005 — A validação da configuração é uma lista de recusas, toda de uma vez

**Decisão.** `agendamento/domain/configuracao.py::problemas(configuracao, *, periodo)` devolve a
lista de `Recusa(codigo, frase)` dos oito casos da FR-7204 e dos três de forma (`sem_dia`,
`sem_banca`, `dia_repetido`), na ordem de `contracts/recusas.md` §1. `periodo` é `(início, fim)` em
datas locais do Evento vigente, ou `None` para a Etapa sem Evento (Edge Cases), e então não há
`dia_fora_do_periodo`. A mesma função serve à gravação (recusa tudo se a lista não for vazia), ao
painel de capacidade (mostra sem recusar) e à conferência (vira o impedimento
`configuracao_invalida`, relida contra o Evento vigente; FR-7221).

O nome da banca é comparado aparado e sem distinção de caixa; no banco, o
`UniqueConstraint(Lower("nome"), "agenda")` é a última guarda.

**Por quê.** Uma função só para os três lugares é o que garante que a conferência recusa exatamente o
que a configuração recusaria. A lista inteira, e não o primeiro erro, porque a comissão corrige tudo
numa passada (UX-766).

## T-006 — A capacidade se recalcula no servidor, a cada campo, por htmx

**Decisão.** O formulário de configurar tem `hx-post` para o fragmento
`…/agenda/capacidade`, com `hx-trigger="input changed delay:250ms, change"` e `hx-target` no painel
de capacidade. O fragmento lê o formulário **sem gravar**, monta a `Configuracao`, chama `derivar`,
`sobras` e `problemas`, compara com a participação (T-007) e devolve o veredito (UX-760). Os atalhos do
simulador ("Acrescentar Ter., 24/11 +32", "Acrescentar uma banca", "Tirar o intervalo"; `04-redesign`,
decisão 3) são botões `type="submit" name="atalho"` com `hx-post` para a própria configuração, que
devolve o formulário com o acréscimo, ainda sem gravar; o ganho de cada atalho é calculado pela mesma
`derivar`. "+ janela", "+ dia" e "+ banca" seguem o mesmo caminho.

Sem JavaScript, um botão "Calcular" envia o mesmo formulário: a tela continua funcionando.

**Por quê.** O htmx já está na gestão, servido de arquivo, com `includeIndicatorStyles:false` e
`allowEval:false` no `<meta>` (`interface/templates/interface/base.html:10`), o que o faz caber na CSP
da `091`/`092` (UX-767). Uma fonte só da FR-7203 (T-003). 250 ms de espera mantém a resposta "ao
digitar" sem uma requisição por tecla.

**Descartado.** JavaScript próprio que replica a derivação: segunda fonte. `hx-on` para os atalhos:
`allowEval:false` o desliga, e é a CSP que pede isso.

Uma armadilha conhecida: o htmx não troca resposta 4xx. Toda recusa de fragmento volta **200** com
`HX-Retarget` para a área de mensagem, como as telas da composição.

## T-007 — Quem precisa de horário vem de `participacao_detalhada`, a cada abertura

**Decisão.** A agenda lê `resultados.application.prontidao.participacao_detalhada(edital=…,
etapa_id=…)`, que hoje devolve **seis** valores — `(participantes, eliminadas, aguardando, fora,
ha_corte, fora_do_alcance)` (`prontidao.py:134`, `:229`); o docstring ainda fala em três. Os
participantes são quem precisa de horário (FR-7210); o motivo de quem tem horário e saiu é
`motivo_de_nao_participar(edital, etapa_id, candidatas)` (`:328`). A agenda não guarda lista
(`D-002`).

A frase de "lista ainda aberta" (US1, cenário 7) aparece quando a Etapa tem Etapa anterior e ela
ainda não produziu Resultado — o mesmo fato que faz `participacao_detalhada` não aplicar a
habilitação. A leitura dele é a que a prontidão já usa; a tarefa T011 a localiza, e não cria outra.

A participação é lida **uma vez por requisição** e passada adiante: a montagem de 3 dias × 2 bancas ×
32 horários lê a agenda em duas consultas (agendamentos com inscrição e banca; participação), e não
por célula.

**Por quê.** É a fonte única que o Princípio II pede. Com a `163` na `main`, o alcance por Modalidade
já está dentro dela (`fora_do_alcance`), e a agenda da heteroidentificação alcança só a reserva sem
nada a mais.

**Descartado.** `restringir_a_participantes` sobre a consulta dos agendamentos: esconderia justamente
os agendados que não participam mais, que a FR-7217 manda mostrar.

## T-008 — As recusas são um módulo de domínio, e o código é o contrato

**Decisão.** `agendamento/domain/recusas.py` define os códigos e compõe as frases de
`contracts/recusas.md`; os comandos levantam `DomainError(codigo, frase, status)` — 422 para entrada
recusada, 409 para concorrência e versão (`horario_ocupado`, `agenda_mudou_desde_a_previa`,
`agenda_mudou_desde_a_conferencia`). A tela inteira mostra a frase; o fragmento a devolve com 200 e
`HX-Retarget` (T-006).

## T-009 — A trava é a da agenda; a do Processo só nos atos

**Decisão.** Toda operação que grava trava a linha de `AgendaDaEtapa` com `select_for_update()` —
tabela operacional, que a role de runtime pode atualizar. As operações da montagem (salvar
configuração, agendar, mudar, liberar, aplicar o preenchimento) usam `exigir_base_de_comissao`
(`comissoes/application/__init__.py:45`), sem a trava do Processo. Os **atos** (publicação,
remarcação, inclusão, cancelamento) correm dentro de `comando_de_comissao(actor=…, processo_id=…,
operation=…, payload=…, idempotency_key=…)` (`:76`), que trava o Processo, confere a base e reserva a
chave de idempotência, e só então travam a agenda. A ordem é sempre **Processo → agenda**.

As duas unicidades do `Agendamento` são a última guarda (FR-7211, FR-7247): o `IntegrityError` de
`uq_agendamento_inscricao` vira `pessoa_ja_agendada`, e o de `uq_agendamento_horario` vira
`horario_ocupado`, ambos 409, dentro de um `atomic()` próprio para a transação externa sobreviver —
como `convocacao/application/publicar.py:529`.

Nenhuma tabela append-only recebe `FOR UPDATE` (a role de runtime não tem `UPDATE`, e o vigia do
`tests/conftest.py` recusa); a serialização dos atos vem da trava da agenda, e a unicidade do ato de
publicação (T-012) é a guarda final.

**Por quê.** Um clique na grade não deve esperar a convocação de outro Edital do mesmo Processo. Os
atos, sim: eles escolhem autoridade, que `autoridade_para_o_ato` trava, e a ordem fixa evita
deadlock com a convocação.

**Descartado.** Advisory lock: não há helper comum (cada uso escreve o SQL), e a linha da agenda é
travável. `compare_and_swap` sobre `revision` (`shared/concurrency.py:23`) sozinho: ele recusa a
segunda escrita, mas não serializa a leitura da participação com a escrita, e a FR-7211 precisa das
duas coisas.

## T-010 — Prévia e conferência se comparam por assinatura, e não só por versão

**Decisão.** `AgendaDaEtapa.revision` sobe a cada escrita da agenda (configuração, agendamento,
preenchimento, ato). A prévia do preenchimento e a conferência calculam uma **assinatura**,
`canonical_sha256` de `{revision, configuração derivada, pares (inscrição, banca, início)}` — e, na
prévia, também dos pares propostos. A aplicação e a confirmação recomputam sob a trava e comparam:
diferente, recusam com `agenda_mudou_desde_a_previa` ou `agenda_mudou_desde_a_conferencia` (409) e a
tela mostra a prévia ou a conferência nova (FR-7215, FR-7223).

**Por quê.** A `revision` sozinha não vê a participação que mudou sem tocar a agenda — um recurso
deferido entre a prévia e a aplicação mudaria os pares propostos sem subir versão nenhuma. É o mesmo
desenho da assinatura do alcance na convocação (`convocacao/domain/alcance.py:100`, `ALCANCE_MUDOU`).

## T-011 — A ordem do preenchimento é escrita uma vez, no domínio

**Decisão.** `agendamento/domain/preenchimento.py::propor(sem_horario, livres) -> Proposta` ordena as
pessoas por `(nome normalizado, protocolo)` — nome sem acento e em caixa dobrada, para que "Álvaro"
não vá para o fim — e os horários livres por `(inicio, banca.ordem)`, e emparelha até acabar um dos
dois (FR-7213). A `Proposta` traz os pares, os que continuam sem horário, os horários que sobram, a
distribuição por dia × banca e a frase da ordem (FR-7214). É pura: a prévia e a aplicação chamam a
mesma função sobre a mesma leitura.

**Por quê.** A ordem é explicável e não expõe posição na classificação (Assumptions, Q-6). Função pura
porque o SC-2392 e a tabela do empate são testes de unidade.

## T-012 — A publicação é o molde da `149`, com o veículo da `159`

**Decisão.** A confirmação, em `agendamento/application/publicar.py`, dentro de `comando_de_comissao`
(T-009):

1. recompõe a conferência e confere a assinatura (T-010) e os impedimentos (FR-7221);
2. confere a autoridade por `publicacoes.application.contexto_do_ato.contexto_do_ato(edital,
   autoridade_id, now)`, que chama `autoridade_para_o_ato` e congela o signatário — o mesmo caminho da
   convocação (`fluxo._conferir_autoridade`); a tela oferece as vigentes por `_escolha_da_autoridade`
   (`interface/views.py:4639`), extraída para um lugar comum se a importação cruzada pedir;
3. lê o **veículo**, como a `159`: `GPS` exige a declaração do item do Edital que admite a página
   pública como veículo; `EXTERNO` exige onde e quando a agenda foi publicada fora. Na `convocacao`
   o veículo não é campo (são as constantes `VEICULO_GPS`/`VEICULO_EXTERNO` de
   `convocacao/application/fluxo.py:92`); aqui ele **é** campo do ato, porque a agenda não tem outra
   linha onde guardá-lo (`D-008`);
4. compõe o conteúdo público (T-014), grava `AtoDaAgenda` (espécie `PUBLICACAO`) com
   `canonical_bytes` e `canonical_sha256`, os `HorarioPublicado` em `bulk_create`, e os avisos (T-018);
5. registra a trilha (T-019).

A confirmação repetida (FR-7223, SC-2396) devolve o ato já criado por dois caminhos: a mesma chave de
idempotência cai em `Contexto.repetido`; outra chave, depois da primeira, encontra o
`uq_ato_da_agenda_uma_publicacao` e devolve o ato existente, sem segundo aviso.

**Por quê.** `D-008`: a mesma natureza da relação de convocados, com autoridade e veículo. Publicar de
novo não existe — a agenda publica inteira uma vez (Assumptions, Q-4), e o que muda depois é ato
individual (`D-006`).

**Descartado.** Reusar `PublicacaoDeConvocados`: ela tem número por Edital, vínculo com convocação e
comunicação, e efeitos que a agenda não tem (`D-005`).

## T-013 — Um documento PDF por ato, gravado no ato, no molde da `149` (`D-012`)

**Decisão.** Cada `AtoDaAgenda` — publicação, remarcação, inclusão, cancelamento — tem um documento
PDF, gerado **uma vez**, na mesma transação do ato, e gravado em `DocumentoDoAtoDaAgenda`
(append-only, `OneToOne` com o ato, `bytes`, `content_type`, `documento_hash`). É o molde de
`DocumentoDaPublicacaoDeConvocados` (`convocacao/models.py:756`), que é o de `DocumentoDoResultado`:

- `agendamento/infrastructure/documento.py::render_agenda_pdf(conteudo)` recebe o conteúdo já
  composto — o mesmo objeto que virou `conteudo_publico` (T-014) — e devolve bytes, **sem consultar
  o banco**, pela `Composicao` e por `render_documento` de `publicacoes/infrastructure/pdf.py`, com
  `_tabela` por dia, como `convocacao/infrastructure/documento.py`. Timbre da unidade congelada,
  identificação, a agenda por dia (horário, banca quando há mais de uma, identificação da FR-7225),
  orientações, autoridade e veículo, e o resumo de integridade. O instante impresso é o do ato, e não
  o da geração.
- O documento do ato individual tem só a linha da pessoa afetada: na remarcação, o horário novo e a
  frase de que substitui o publicado antes; na inclusão, o horário; no cancelamento, a frase de que o
  horário deixa de valer. Nunca o motivo (FR-7246), e nunca o endereço da sala (FR-7226).
- O portal serve os bytes gravados, e nada recomposto, como `portal/views.py:3800`: `ETag` com o
  `documento_hash` e `attachment`. Endereço público, como o da 149, porque o conteúdo é o público.

**Por quê a tabela.** O dado a preservar são **os bytes do documento tal como foi publicado**. O
`conteudo_publico` do ato já é imutável, mas o compositor não é: fonte, margem e cabeçalho mudam
entre versões, e recompor daria, para o mesmo ato, um arquivo diferente do que circulou — o mesmo
motivo pelo qual a `149` e a `017` guardam os delas. Uma tabela do próprio app, e não coluna no ato,
porque a ausência de documento fica sendo a ausência de linha, e porque o ato é gravado antes do
documento que cita o resumo dele. O `M` vai a **68** (três append-only na B).

**Descartado.** Gerar sob demanda do `conteudo_publico` (o arquivo mudaria com o compositor);
reusar `DocumentoPublicado` de `publicacoes` (é o documento do Edital, com versão e Retificação); um
documento "consolidado do vigente", regenerado a cada ato (não seria ato de ninguém; a página pública
já mostra o vigente, FR-7248).

## T-014 — O conteúdo público: por dia, por horário, só o que a FR-7225 permite

**Decisão.** `agendamento/domain/conteudo.py::compor(...)` devolve:

```json
{
  "versao": 1,
  "cabecalho": {
    "unidade": {"cabecalho": ["…"], "local": "…", "sigla": "…", "nome": "…"},
    "edital": "Edital 146/2025",
    "etapa": "Entrevista",
    "publicadoEm": "2026-11-20T13:00:00+00:00",
    "signatario": {"nome": "…", "cargo": "…", "atoDeNomeacao": "…"},
    "veiculo": "GPS",
    "forma": "REMOTA",
    "duracao": 10,
    "identificacao": "NOME_E_PROTOCOLO"
  },
  "bancas": [{"nome": "Banca 1", "local": ""}],
  "dias": [
    {"dia": "2026-11-23", "horarios": [
      {"inicio": "2026-11-23T11:00:00+00:00", "fim": "…", "banca": "Banca 1",
       "pessoa": {"nome": "…", "protocolo": "INS-2026-0001"}}
    ]}
  ]
}
```

- `identificacao` é `PROTOCOLO` quando `editais.domain.alcance.restrita(etapa)` — a Etapa restrita por
  Modalidade —, e então `pessoa` não tem `nome` (FR-7225, `D-009`). Nas demais, nome e protocolo, como
  a FR-5712 da `149`.
- `banca` só aparece em cada horário quando há mais de uma.
- `local` da banca só na forma `PRESENCIAL`, porque o local de atendimento presencial é público como
  o `location` do Evento; na `REMOTA` é sempre vazio. O endereço da sala **nunca** entra (FR-7226).
- Nada de CPF, e-mail, telefone, Modalidade, desfecho (FR-7226). Um teste compõe o conteúdo das
  fixtures e procura cada um desses valores nos bytes (SC-2394).

**Por quê.** Só o que a FR-7225 lista, mais o local presencial, que é o que a pessoa precisa para
chegar e já é público no cronograma.

## T-015 — Publicada a agenda, a configuração só cresce

**Decisão.** Depois do ato de publicação, salvar a configuração recusa (`horario_publicado_removido`,
`parametro_publicado_alterado`) toda mudança que não seja acrescentar dia, janela a um dia, ou banca
(FR-7208). Isso inclui o local, o endereço da sala e as orientações: o aviso já os levou à pessoa, e
nenhuma situação de mensagem desta spec os corrigiria. Quem precisa de outra sala acrescenta uma banca
e remarca.

**Por quê.** A FR-7208 diz "só aceitar acrescentar". Uma correção silenciosa do endereço mudaria o que
a pessoa leu no aviso sem avisá-la — e o aviso de correção seria uma situação nova da FR-084.

**Descartado.** Permitir corrigir o endereço da sala com motivo: seria o requisito novo que o parágrafo
acima recusa, e fica como registro para o usuário se aparecer no uso.

## T-016 — A página pública lê o append-only, nunca o operacional

**Decisão.** A rota pública é `portal:agenda-da-etapa`, em `agendas/<uuid:agenda_id>/`, e a seleção
ganha a seção "Agendas" por `portal/_agendas_da_selecao.html`, incluída em `selecao.html` como as
convocações (`selecao.html:210`). A página mostra a agenda **vigente**: os `HorarioPublicado` não
substituídos e não cancelados ([data-model.md](data-model.md), *Vigente*), com o cabeçalho do conteúdo da publicação e a marca
"remarcado em" quando o vigente veio de remarcação (FR-7245). Lê só tabelas append-only — nunca o
`Agendamento`, que é rascunho operacional.

A busca é por `GET ?busca=`, no servidor: casa o protocolo inteiro ou o fim dele, e o nome
normalizado (T-011) só quando a identificação é `NOME_E_PROTOCOLO` (FR-7227). Sem JavaScript, sem
`<table>` (o portal as recusa), listas por dia.

**Por quê.** A página pública só pode mostrar o que foi publicado; ler do `HorarioPublicado`, cujas
linhas não mudam, é ler o publicado. A busca no servidor funciona no celular sem script e cabe na CSP.

**Descartado.** Ler os bytes da publicação e "aplicar" as remarcações por cima: duas leituras do mesmo
fato. Busca em JavaScript sobre a página inteira, como o protótipo: obrigaria o portal a ter script
próprio e a forçar `hidden` contra o `display` das listas (o achado do protótipo).

## T-017 — A área do candidato mostra o horário na página da inscrição

**Decisão.** `portal/views.inscricao` ganha o bloco "Seu horário" por Etapa com agenda, lido por
`agendamento/application/leitura.py::horarios_da_inscricao(inscricao)`, em número fixo de consultas
(o orçamento do portal da `118`). Publicado: dia e hora em destaque, duração, banca, local ou o botão
"Entrar na sala virtual", orientações, e "Seu horário mudou em «data». O horário anterior não vale
mais" quando o vigente é remarcação (FR-7228, FR-7245). Antes da publicação, para quem participa da
Etapa: "Seu horário ainda não foi publicado", com o período do Evento.

A situação da inscrição (`portal/situacao.py`) **não** ganha código novo: o horário não é desfecho
nem etapa do processo, e cada código novo ali mexe na trilha de leitura da `063`.

O endereço da sala vem da `BancaDaAgenda`, que depois da publicação não muda (T-015), e só nesta
página, depois da identificação (FR-7229).

## T-018 — O aviso é um por pessoa e por ato, pela origem `AGENDA`

**Decisão.**

- `avisos/domain/nomes.py` ganha `AGENDA`; `avisos/migrations/0003_origem_agenda.py` muda as
  escolhas, refaz `ck_aviso_origem_conhecida` e `ck_aviso_ato_da_origem` com o ramo
  `origem=AGENDA, natureza="", referencia_da_publicacao≠""`, e torna `marco_id` anulável com
  `ck_aviso_marco_da_origem` (`marco_id IS NOT NULL OR origem = 'AGENDA'`): a agenda é da Etapa e
  não tem marco. É DDL da role de migração; a tabela continua append-only.
- **Um `Aviso` por pessoa**, com o `assunto` e o `corpo` finais daquela pessoa — dia, hora, duração,
  banca, local ou endereço da sala, orientações, protocolo e a frase de que vale a agenda publicada
  (FR-7231) —, e um `DestinatarioDoAviso`. É o precedente do aviso de pendência da `134`
  (`avisos/application/pendencias.py:436`), o único que já compõe por pessoa. O texto é de
  `agendamento/domain/mensagem.py`, não de `ModeloDeAviso`: o corpo tem dado por pessoa, e o modelo
  da `066` resolve só `{nome_do_candidato}`.
- `perfil_id` é o `profile_id` da inscrição; `referencia_da_publicacao` é a frase do ato ("Agenda da
  «Etapa», publicada em «data»").
- **O vínculo fica do lado da agenda**: `HorarioPublicado.aviso` (FK anulável e única). A `avisos`
  não passa a conhecer a `agendamento`.
- A publicação cria um aviso por `HorarioPublicado`; a remarcação e a inclusão, um (FR-7244); o
  cancelamento, nenhum (Out of Scope: aviso de cancelamento). `UNIQUE(ato, inscricao)` no
  `HorarioPublicado` é o que garante a FR-7232; o `uq_destinatario_do_aviso` da `066` continua valendo.
- O envio é o `despachar` da `066`; o reenvio, `confirmar_reenvio` (`avisos/application/confirmar.py:366`),
  que precisa aceitar a origem nova — `recusar_reenvio_da_pendencia` só barra a `PENDENCIA`. No
  correio, `_html` dá o estado visual "informacao".
- **Com `AVISOS_AOS_CANDIDATOS` desligada** (o padrão de produção até a validação de LGPD da `066`),
  a publicação acontece e **nenhum aviso é criado**; a conferência, a confirmação e a tela da agenda
  publicada dizem que os avisos por e-mail estão desligados nesta instalação e que a agenda vale pela
  publicação. É o FR-1282 da `066` (`avisos/application/comando.py:33`), que vale para toda origem
  dela, e é a decisão `D-011`: nenhuma chave própria da agenda. Ligar a chave depois não cria aviso
  de ato anterior, porque o aviso nasce no ato, e não de uma varredura.
- **Com a chave ligada**, a conferência mostra quantos avisos a publicação criará, a lista de
  destinatários (pessoa e protocolo, sem e-mail) e a prévia de um aviso composto (FR-7222).

**FR-084.** O texto da `010` (`specs/010-area-do-candidato/spec.md:572`) já foi revisto pela `156`
(11/11) para **seis** situações, com vigência na implementação dela — e a `156` ainda não tem código.
A entrega C revê para **sete**, com o aviso de agenda como origem do aviso complementar, preservando
a redação anterior como as revisões anteriores fizeram, e com a frase explícita de que a decisão
humana é a confirmação da publicação, da remarcação ou da inclusão — porque a redação atual mantém
fora o "aviso disparado pela publicação sem decisão humana". O guardião
`tests/test_situacoes_de_mensagem.py` conta pares `(módulo, situação)` do que **está implementado**
(hoje cinco, com o despacho duas vezes) e confere as redações anteriores; a tarefa da C acrescenta o
par do despacho para a agenda e a constante `REVISAO_DA_FR_084_PELA_167` em `despacho.py`, e relê o
guardião no dia, porque a ordem com a `156` depende de qual for implementada primeiro.

**Por quê.** `D-007` e `D-010`: o app de avisos já tem envio fora da confirmação, retentativa,
reenvio e moldura. Um aviso por pessoa é o que a FR-7231 exige: o corpo é diferente para cada uma.

**Descartado.** Um aviso por ato com variáveis resolvidas no despacho: o despacho só conhece
`{nome_do_candidato}`, e ensinar-lhe a agenda faria a `avisos` depender da `agendamento`. FK do aviso
para o ato da agenda: o mesmo acoplamento ao contrário.

## T-019 — A trilha registra a operação, sem e-mail nem sala

**Decisão.** `auditoria.application.record_event` com `operation` em `agenda.configuracao_salva`,
`agenda.preenchimento_aplicado`, `agenda.agendamento` (com `detalhe.gesto` em
`agendar`/`mudar`/`liberar`), `agenda.publicacao`, `agenda.remarcacao`, `agenda.inclusao`,
`agenda.cancelamento`; o reenvio já é registrado pela `066`. Estado anterior e posterior são pares
`(protocolo, banca, início)` e, na configuração, a configuração derivada sem `local` nem endereço; o
motivo vai em `reason` (FR-7256). Um teste procura o endereço da sala e o e-mail das fixtures em
todo `RegistroAuditoria` gravado pela feature.

## T-020 — As telas: servidor e htmx, peças novas na folha comum

**Decisão.**

- Rotas da gestão sob `editais/<uuid:edital_id>/agenda-da-etapa/<uuid:etapa_id>/`: `configurar`,
  `capacidade` (fragmento), `montar`, `painel` (fragmento), `preencher` (prévia e aplicação),
  `agendar`, `liberar`, `conferir`, `publicar`, `publicada`, `remarcar/<uuid:inscricao_id>`,
  `cancelar/<uuid:inscricao_id>`. Sem segmento `etapas/`, como manda a decisão de rotas da `011`.
- A seção "Agenda" entra na página da Etapa, que é a da Distribuição
  (`interface/templates/interface/distribuicao.html`, `interface:distribuicao`), com o estado vazio da
  UX-765 e o caminho para configurar, montar ou a agenda publicada.
- A grade é `<table>` de horário × banca; cada célula é um `<button>` com `hx-get` para o painel. A
  aba do dia é link com `?dia=`. No estreito (< 64rem), a mesma marcação vira lista por CSS (UX-763).
  O painel é `aria-live`. Nenhum JavaScript novo.
- As peças que o redesign criou e que valem para outras telas — controle segmentado, seletor de
  horário, painel de ação, veredito — vão para `interface/static/interface/gestao/componentes.css`
  (`04-redesign` §4.5.2); o resto, para `telas/agenda-da-etapa.css`; o portal, para
  `portal/static/portal/portal.css`. O medidor é o `.medidor` de `gestao/telas.css:264`.
- Os templates novos entram numa varredura de vocabulário própria,
  `tests/interface/test_vocabulario_da_agenda_da_etapa.py`, porque cada varredura tem a sua lista
  literal e tela nova escapa em silêncio.
- Cada `raise Http404` novo ganha linha em `specs/033-navegacao-por-capacidade/inventario-das-negativas.md`,
  que `tests/test_gramatica_das_portas.py` cobra.

**Por quê.** É o padrão das telas de composição e da Distribuição; o redesign aprovado já desenhou a
grade como marcação que o CSS reorganiza. O painel "onde se age" é server-side: o htmx troca o
conteúdo, e o teclado e o leitor de tela recebem botões reais (UX-762).

## T-021 — A autorização é a da gestão da comissão, com o escopo do Edital

**Decisão.** Toda view começa pela guarda de `_etapa_para_distribuir` (`interface/views.py:6676`): o
Edital no `institution_scope` do ator, senão 404; `pode_gerir_comissao(ator, edital.processo)` com
`BASES_DA_GESTAO_DA_COMISSAO`, senão a recusa da gramática das portas; a Etapa vigente, senão 404. A
guarda é extraída para uso comum, e não copiada. Os comandos repetem a conferência da base no
domínio (`exigir_base_de_comissao` ou `comando_de_comissao`), porque a view não é a única porta
(FR-7255).

**Por quê.** "Quem pode gerir a Etapa" é, no código, quem pode gerir a comissão do Processo — a
permissão `comissao:gerir` ou a presidência. A presidência publica porque tem a base; a spec não pede
porta mais estreita para a publicação, e o usuário confirmou isso em 14/11 (`D-013`): nenhum papel
novo. A autoridade signatária é outra responsabilidade: quem publica a escolhe entre as vigentes
(`contexto_do_ato`), e o ato registra o autor e a autoridade separadamente.

## T-022 — Migrations e guardiões, por entrega

**Decisão.**

| Entrega | Migration | Guardiões que mudam |
|---|---|---|
| A | `agendamento/0001_agenda_da_etapa` (quatro tabelas operacionais) | `APPS` de `tests/migrations/test_migrations.py` ganha `agendamento`; `INSTALLED_APPS` com o comentário de fronteira |
| B | `agendamento/0002_atos_da_agenda` (três append-only, gatilhos `ato_da_agenda_append_only`, `horario_publicado_append_only`, `documento_do_ato_da_agenda_append_only` e `horario_publicado_coerente`) | `TABELAS_APPEND_ONLY` em `seguranca/papeis.py` (65 → **68**); `TRIGGERS_POR_APP["agendamento"]`; `CLAUDE.md` e README com o `M` novo |
| C | `avisos/0003_origem_agenda` | `TRIGGERS_POR_APP["avisos"]` se o gatilho mudar; `test_situacoes_de_mensagem.py` |

O gatilho append-only é SQL na própria migration, com `RunPython` só em PostgreSQL, como a
`convocacao/0007`: não há helper comum.

## T-023 — A entrega D é orientação, e é opcional

**Decisão.** "Montar a agenda" e "Publicar a agenda" como pendência no Centro (`interface/centro.py`,
`136`) e em Minhas atividades (`interface/atividades.py`, `160`); e o horário publicado, como
informação, na tela da Ocorrência (`interface/templates/interface/ocorrencia.html`; R-23). Nenhum
requisito da spec depende dela: a D fecha quando a comissão de uso a pedir.

## T-024 — O reenvio do aviso de agenda é da agenda publicada (entrega C)

**Decisão.** "Reenviar o aviso", na agenda publicada, cria um `Aviso` filho
(`motivo=REENVIO_DE_FALHAS`, `aviso_anterior` apontando o que falhou) com o **mesmo** assunto e o
mesmo corpo, e um `DestinatarioDoAviso` com o endereço relido
(`agendamento/application/reenviar.py`). Só o que não saiu — falha definitiva ou expirado sem envio —,
e só a partir do último da cadeia. A tela de reenvio da `066` recusa a origem nova
(`aviso_de_agenda_sem_reenvio`), como recusa a pendência da `134`.

**Por quê.** O reenvio da `066` recompõe um texto só para o universo do ato e o grava num aviso com
muitos destinatários; o aviso de agenda tem o texto de uma pessoa — o horário dela e, na forma
remota, a sala dela (FR-7229). Passar por lá exigiria um texto por destinatário, que a `066` não tem.

**Descartado.** Levar a agenda publicada à tela da `066`, como o contrato dizia antes da
implementação: ela mandaria a todos o texto de um só.

## O que o diagnóstico não dizia

1. **"Agenda" já é nome**: a Agenda dos Editais da `101` (T-001).
2. **`participacao_detalhada` devolve seis valores**, e não três (T-007).
3. **O veículo da `159` não é campo do modelo**, são constantes do fluxo (T-012); e **não há advisory
   lock em `publicar.py`**: a serialização vem da trava do Processo (T-009).
4. **A FR-084 já está em seis situações**, pela `156`, ainda sem código; o `Aviso` exige `marco_id`,
   e só a pendência da `134` compõe por pessoa (T-018).
5. **O modelo do §2.5 tem seis tabelas**, e não cinco: a frase conta três operacionais, e a figura
   lista quatro (data-model).
