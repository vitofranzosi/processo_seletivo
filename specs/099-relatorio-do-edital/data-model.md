# Data Model: Relatório do Edital

**Nenhuma entidade persistida nova.** O relatório é uma leitura derivada; a emissão é um evento na
trilha de auditoria que já existe.

## Relatório (derivado, em memória)

| Campo | Conteúdo | Fonte |
|---|---|---|
| `referencia` | instante da leitura | relógio, no início da transação (R-002) |
| `edital`, `processo`, `unidade` | identificação | `Edital`, `ProcessoSeletivo`, 1ª `Publicacao` (unidade congelada) |
| `especie` | `ACOMPANHAMENTO` · `ENCERRAMENTO` · `INTERRUPCAO` | regra da FR-2523 |
| `situacao_no_gps` | estado do Edital e data do ato de desfecho | `desfechos()` |
| `pendencias` | lista de `Pendencia(tipo, perfil, texto)` | R-006 |
| `posteriores` | lista de `(rotulo, quantidade)` | R-008 |
| `frases` | parágrafo da visão geral | regras da FR-2527 |
| `indicadores` | seis `Indicador(valor, rotulo, base)` | FR-2528 |
| `perfis` | uma `LinhaDoPerfil` por Perfil publicado | FR-2535 |
| `serie` | `(dia, quantidade)` e o término original quando houve prorrogação | `serie_do_edital` |
| `retificacoes` | data, justificativa, alterações legíveis com antes e depois | `publicacoes` |
| `recursos` | totais por Perfil e situação | R-007 |
| `datas` | `Data(dia, texto, natureza)` com natureza publicação · registrado · previsto · prazo | atos e snapshot |
| `documentos` | título, data, endereço público, SHA-256 | `DocumentoPublicado`, `DocumentoDoResultado` |
| `anexo` | etapas por Perfil, listas, cronograma, definições, não registrados, emissão | FR-2540 a FR-2544 |
| `cadastros_distintos` | contagem distinta de `identity_subject` das enviadas | FR-2530 |

### Valor ou ausência

Todo número é um `Numero` (valor) ou uma `Ausencia(tipo, motivo)` — nunca os dois, nunca nenhum —,
com os tipos da `040` (não se aplica, ainda não disponível, não publicado, parcial) mais "não
registrado pelo GPS" e "omitido por privacidade" (D-006). A página e o PDF escrevem a ausência pelo
motivo, e nunca 0.

### LinhaDoPerfil

| Campo | Regra |
|---|---|
| `nome`, `local` | publicados |
| `vagas` | imediatas, com o desdobramento por lista (fato público) |
| `inscricoes` | enviadas |
| `por_vaga` | razão da FR-2529, ou "não se aplica" |
| `classificadas` | inscrições distintas com `CLASSIFICADA` nas publicações vigentes do Perfil, e a natureza |
| `habilitadas_nas_vagas` | soma de `ocupadas` das apurações vigentes e atualizadas (fato não público) |
| `convocacoes` | realizadas, aceitas, aguardando, prazo encerrado sem registro, outros desfechos (fato não público) |
| `privado` | `True` se o Perfil tem menos de cinco enviadas: os fatos não públicos viram ausência |

## Emissão (evento de auditoria existente)

`RegistroAuditoria` com:

| Campo | Valor |
|---|---|
| `operation` | `EMITIR_RELATORIO` |
| `aggregate_type`, `aggregate_id` | `Edital`, id |
| `permission` | a base que autorizou (`comissao:gerir` ou `comissao:presidir`) |
| `detalhe` | `{"referencia": ISO, "numero": N, "sha256": hex, "especie": ...}` |

O número da emissão é `count(eventos EMITIR_RELATORIO do Edital) + 1`, lido sob a trava do Edital
(R-003).
