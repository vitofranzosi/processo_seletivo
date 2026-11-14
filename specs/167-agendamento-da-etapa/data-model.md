# Data Model: O agendamento dos participantes da Etapa

Seis tabelas novas no app `agendamento` — quatro operacionais na entrega A, duas append-only na B — e
uma origem nova, com uma coluna anulável, no `Aviso` da `066`, na C. Nada muda em `EtapaAvaliacao`,
`EventoCronograma`, `Inscricao`, `ResultadoEtapa` ou `Ocorrencia` (T-001, T-022).

O §2.5 do estudo diz "cinco tabelas — três operacionais e duas append-only", mas a figura e a tabela
dele listam quatro operacionais: a agenda, a janela, a banca e o agendamento. São as mesmas do estudo,
contadas de novo; nenhuma foi acrescentada.

```text
AgendaDaEtapa ─────────┬── JanelaDaAgenda (n)
 (operacional)         ├── BancaDaAgenda (n)
                       └── Agendamento (n) ──── Inscricao
                                    │
AtoDaAgenda (append-only) ── HorarioPublicado (n, append-only) ── Inscricao, BancaDaAgenda
 PUBLICACAO | REMARCACAO |     substitui → HorarioPublicado
 INCLUSAO | CANCELAMENTO       aviso → avisos.Aviso (origem AGENDA)
```

## `AgendaDaEtapa` — a configuração (A)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | identidade da agenda, e do endereço público (T-016) |
| `edital` | FK `processos.Edital`, `PROTECT` | |
| `etapa_id` | UUID | a Etapa na Versão Consolidada, sem FK (T-002, FR-7201) |
| `forma` | `REMOTA` \| `PRESENCIAL` | FR-7202 |
| `duracao_minutos` | inteiro positivo | `ck_agenda_duracao_positiva` |
| `intervalo_minutos` | inteiro ≥ 0 | `ck_agenda_intervalo_nao_negativo` |
| `orientacoes` | texto | livre (FR-7252); pode ser vazio na montagem |
| `revision` | inteiro, começa em 1 | sobe a cada escrita da agenda (T-010) |
| `criada_por`, `criada_em`, `atualizada_por`, `atualizada_em` | | o sujeito do ator e o instante |

Constraints: `uq_agenda_por_etapa` (`edital`, `etapa_id`) — FR-7200.

**Publicada** não é coluna: é existir um `AtoDaAgenda` de espécie `PUBLICACAO` para a agenda. A
leitura é uma consulta por índice, e não há dois fatos para divergir.

## `JanelaDaAgenda` — um dia e um intervalo de horas (A)

| Campo | Tipo | Regra |
|---|---|---|
| `agenda` | FK `AgendaDaEtapa`, `CASCADE` | |
| `dia` | data local | dentro do período do Evento vigente (domínio, T-005) |
| `inicio`, `fim` | hora local | `ck_janela_inicio_antes_do_fim` |

Constraints: `uq_janela_inicio` (`agenda`, `dia`, `inicio`). A sobreposição e o "menor que a duração"
são do domínio (`configuracao.problemas`), porque dependem de outras linhas e da duração da agenda.

## `BancaDaAgenda` — o ponto de atendimento (A)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | estável entre edições da configuração: o formulário o carrega |
| `agenda` | FK `AgendaDaEtapa`, `CASCADE` | |
| `nome` | 80 | não vazio (`ck_banca_com_nome`) |
| `acesso` | texto | o local (presencial) ou o endereço da sala (remota); vazio impede publicar (FR-7221) |
| `ordem` | inteiro | a posição na grade e no preenchimento (T-011) |

Constraints: `uq_banca_nome` (`Lower("nome")`, `agenda`) — FR-7204.

`acesso` nunca entra no conteúdo público na forma remota (FR-7226), nem na trilha (FR-7256).

## `Agendamento` — quem está em que horário agora (A)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `agenda` | FK `AgendaDaEtapa`, `CASCADE` | |
| `inscricao` | FK `inscricoes.Inscricao`, `PROTECT` | |
| `banca` | FK `BancaDaAgenda`, `PROTECT` | da mesma agenda (domínio) |
| `inicio`, `fim` | instante com fuso | um horário derivado (T-003) |
| `origem` | `MANUAL` \| `AUTOMATICA` | FR-7216 |
| `feito_por`, `feito_em` | | FR-7216 |

Constraints (FR-7211, FR-7247; as últimas guardas de T-009):

- `uq_agendamento_inscricao` (`agenda`, `inscricao`) — uma inscrição, um horário;
- `uq_agendamento_horario` (`agenda`, `banca`, `inicio`) — um horário, uma inscrição.

**É o estado corrente, antes e depois da publicação.** Antes, a montagem o cria, o muda e o apaga
(liberar, configuração que remove o horário). Depois, cada ato individual o atualiza na mesma transação
em que grava o `HorarioPublicado`: é ele que barra duas remarcações para o mesmo horário. Apagar a
linha não perde história: antes da publicação, a trilha guarda estado anterior e posterior
(FR-7256); depois, o append-only guarda tudo o que foi publicado. É a leitura que a Constituição faz
da exclusão física — proibida quando compromete a rastreabilidade.

## `AtoDaAgenda` — publicação, remarcação, inclusão, cancelamento (B, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `agenda` | FK `AgendaDaEtapa`, `PROTECT` | |
| `edital` | FK `processos.Edital`, `PROTECT` | denormalizado para a página pública e o índice |
| `especie` | `PUBLICACAO` \| `REMARCACAO` \| `INCLUSAO` \| `CANCELAMENTO` | |
| `praticado_por`, `praticado_em` | | o autor e o instante |
| `motivo` | texto | obrigatório nas três individuais, vazio na publicação (`ck_ato_da_agenda_motivo`) |
| `veiculo` | `GPS` \| `EXTERNO` \| vazio | só na publicação (`ck_ato_da_agenda_veiculo`) |
| `declaracao_do_veiculo` | texto | obrigatória com `GPS` (`D-008`, a FR-5703 da `149`) |
| `publicado_fora_onde`, `publicado_fora_em` | texto, data | obrigatórios com `EXTERNO` |
| `signatario_id`, `signatario_nome`, `signatario_cargo`, `signatario_ato_de_nomeacao` | | congelados; só na publicação (`ck_ato_da_agenda_signatario`) |
| `unidade_codigo`, `unidade_sigla`, `unidade_nome`, `unidade_cabecalho`, `unidade_local` | | `colunas_da_unidade`, como a `149` |
| `conteudo_publico` | bytes | `canonical_bytes` (T-014); na individual, só a linha da pessoa |
| `conteudo_publico_hash` | 64 | `canonical_sha256` do mesmo conteúdo |
| `assinatura_conferida` | 64 | a assinatura da conferência que a confirmação conferiu (T-010) |
| `idempotency_key` | 128 | |

Constraints:

- `uq_ato_da_agenda_uma_publicacao` — `UNIQUE(agenda)` com `condition=Q(especie="PUBLICACAO")`: a
  agenda publica uma vez, e a confirmação repetida encontra o ato existente (FR-7223, SC-2396);
- `ck_ato_da_agenda_motivo`, `ck_ato_da_agenda_veiculo`, `ck_ato_da_agenda_signatario`, acima.

## `HorarioPublicado` — o que cada ato publicou, por pessoa (B, append-only)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | |
| `ato` | FK `AtoDaAgenda`, `PROTECT` | |
| `inscricao` | FK `inscricoes.Inscricao`, `PROTECT` | |
| `situacao` | `AGENDADO` \| `CANCELADO` | |
| `banca` | FK `BancaDaAgenda`, `PROTECT`, anulável | obrigatória em `AGENDADO`, nula em `CANCELADO` |
| `banca_nome` | 80 | congelado, como foi publicado |
| `inicio`, `fim` | instante, anuláveis | obrigatórios em `AGENDADO`, nulos em `CANCELADO` (`ck_horario_publicado_forma`) |
| `substitui` | FK `self`, `PROTECT`, anulável | o item que este troca; nulo na publicação e na inclusão |
| `aviso` | FK `avisos.Aviso`, `PROTECT`, anulável | o aviso desta pessoa neste ato (T-018); nulo no cancelamento e com os avisos desligados |

Constraints:

- `uq_horario_publicado_por_ato` (`ato`, `inscricao`) — uma pessoa por ato, e por isso um aviso por
  pessoa por ato (FR-7232, SC-2395);
- `uq_horario_publicado_substituido_uma_vez` (`substitui`) — um item é trocado no máximo uma vez, e
  a cadeia é uma lista, não uma árvore;
- `uq_horario_publicado_aviso` (`aviso`);
- `ck_horario_publicado_forma`, acima.

Gatilho de coerência `horario_publicado_coerente`, porque atravessa tabelas: o `substitui` é da mesma
inscrição e de um ato da mesma agenda; a `banca` é da agenda do ato; na `REMARCACAO` e no
`CANCELAMENTO` há `substitui`, na `PUBLICACAO` e na `INCLUSAO` não há; o `CANCELADO` só nasce de ato
`CANCELAMENTO`.

### Vigente

O horário vigente de uma inscrição numa agenda é o `HorarioPublicado` dela **não substituído**
(nenhuma linha o aponta em `substitui`) e de situação `AGENDADO`. A página pública e a área do
candidato leem só isso (T-016, T-017). "Remarcado em" é o `praticado_em` do ato do vigente quando ele
é `REMARCACAO`.

## As três camadas append-only (B)

1. `save` só de linha nova e `delete` recusado, pela classe `_AppendOnly` do app.
2. Gatilhos `ato_da_agenda_append_only` e `horario_publicado_append_only` em `UPDATE` e `DELETE`, na
   migration `agendamento/0002_atos_da_agenda`.
3. As duas em `TABELAS_APPEND_ONLY` (`seguranca/papeis.py`): o papel de runtime não recebe `UPDATE`
   nem `DELETE`. O `M` do provisionamento passa de **65** a **67**.

## `Aviso` da `066` (C)

| Mudança | Regra |
|---|---|
| `origem` ganha `AGENDA` | `ck_aviso_origem_conhecida` refeito |
| `ck_aviso_ato_da_origem` | ramo novo: `origem=AGENDA`, `natureza=""`, `referencia_da_publicacao≠""` |
| `marco_id` anulável | `ck_aviso_marco_da_origem`: `marco_id IS NOT NULL OR origem='AGENDA'` |

Um `Aviso` e um `DestinatarioDoAviso` por pessoa e por ato, com o corpo final daquela pessoa (T-018).

## Valores de domínio (sem tabela)

| Valor | Onde | Campos |
|---|---|---|
| `Configuracao` | `domain/horarios.py` | `forma`, `duracao`, `intervalo`, `dias: ((dia, ((inicio, fim), …)), …)`, `bancas: ((id, nome, acesso, ordem), …)` |
| `Horario` | `domain/horarios.py` | `dia`, `inicio`, `fim`, `banca_id` |
| `Capacidade` | `domain/capacidade.py` | `horarios`, `por_janela`, `participantes`, `falta`, `sobra`, `sobras`, `lista_aberta` |
| `Recusa` | `domain/recusas.py` | `codigo`, `frase` |
| `Proposta` | `domain/preenchimento.py` | `pares`, `sem_horario`, `livres`, `por_dia_e_banca`, `ordem` |
| `Conferencia` | `application/conferir.py` | `impedimentos`, `avisos`, `fatos`, `conteudo`, `mensagem_de_exemplo`, `autoridades`, `assinatura` |

## Transições

```text
(sem agenda) ── configurar ──▶ EM MONTAGEM ── publicar ──▶ PUBLICADA
                                   ▲  │                        │
         salvar configuração,      └──┘     remarcar, incluir, cancelar (um ato por pessoa)
         agendar, mudar, liberar,                              │
         preencher                                             ▼
                                                          PUBLICADA (vigente muda; nada se apaga)
```

Em montagem tudo é operacional e reversível. Publicada, a configuração só cresce (T-015) e o
`Agendamento` só muda por ato.
