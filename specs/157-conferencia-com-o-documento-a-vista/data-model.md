# Data Model: Conferência com o documento à vista

**Nenhuma entidade, coluna, tabela ou migration nova.** O que muda é quando um evento é gravado e
quantas pessoas um gesto alcança.

## As entidades de hoje, como esta feature as lê

| Entidade | Onde | O que esta feature faz com ela |
|---|---|---|
| `ApresentacaoDeDocumento` | `convocacao` | entrega o arquivo dela; lê o tamanho do arquivo para o link (R-011) |
| `ConferenciaDeDocumento` | `convocacao` | grava pelo comando de hoje (`documentos.conferir`), sem mudança |
| `RegistroAuditoria` — `CONSULTAR_DOCUMENTO_DA_CONVOCACAO` | `auditoria` | **o mesmo evento, gravado ao fim da entrega** (R-001) |
| `RegistroAuditoria` — `INTEGRIDADE`, `ARQUIVO_INDISPONIVEL` | `auditoria` | como hoje, também quando o painel pede (R-002) |
| `Aviso` e `DestinatarioDoAviso`, origem `PENDENCIA` | `avisos` | o pedido de uma pessoa grava um `Aviso` com um destinatário, igual ao do lote (R-008) |
| `RegistroAuditoria` — `OPERACAO_AVISAR_PENDENCIAS` | `auditoria` | o `detalhe` ganha `"recorte": "pessoa"` e `"convocacao"` no gesto individual (FR-4620 da `134`) |
| `Avaliacao`, Atribuição | `avaliacoes` | nada: a Mesa não ganha regra (FR-6548) |

## O evento da abertura (R-001)

```text
pedido → autorização → cópia verificada (resumo) ─┬─ diverge → INTEGRIDADE, recusa (409)
                                                   ├─ ilegível → ARQUIVO_INDISPONIVEL, recusa (409)
                                                   └─ confere → entrega em blocos
                                                                 ├─ último bloco entregue → CONSULTAR_DOCUMENTO_DA_CONVOCACAO
                                                                 └─ entrega interrompida → nada
```

- **Agregado**: a apresentação, como hoje. **Motivo**: o requisito, e *"baixado"* no download.
- **Quem lê**: `documentos._aberta_por` (FR-3611 da `115`, FR-4460 da `131`), sem mudança; a página,
  para *"aberto por você"*.
- Na Mesa, o evento da `012` continua gravado antes da entrega (FR-6548).

## O gesto do aviso, no recorte de uma pessoa (R-008)

Entrada: `edital`, `perfil`, `marco`, `lista` e, novo, `convocacao_id`.

| Situação da pessoa | Resultado |
|---|---|
| alcançada (FR-4606 da `134`) | um `Aviso` com um destinatário, texto com todas as pendências dela |
| `já avisada hoje` | recusa `aviso_sem_pendencia_a_avisar`, com o motivo e a data do dia seguinte |
| `desfecho registrado`, `vencimento decorrido`, `convocação ainda não comunicada`, `documento reenviado…`, `sem endereço` | recusa, com o motivo, sem data |
| `AVISOS_AOS_CANDIDATOS` desligada | recusa `aviso_envio_desabilitado`, como no lote |
| Processo em estado final | recusa `aviso_processo_em_estado_final`, como no lote |

A idempotência leva a convocação no `payload`: a mesma chave para outra pessoa é outro pedido.

## A situação do aviso (R-009)

| Estado do destinatário (`066`) | Grupo |
|---|---|
| `PENDENTE`, `EM_ENVIO`, falha temporária | solicitado, aguardando envio |
| `ACEITA` | enviado (aceito pelo servidor de correio) |
| falha definitiva, indeterminada, expirada sem envio, interrompido, sem endereço, não elegível | não enviado |

## O que fica só no navegador (R-010)

`sessionStorage` da aba, chave por página e item (ou documento, na Mesa): `{ item, campos }` de quem
abriu fora da página. Apagado no registro aceito e no fechamento da aba. Nunca enviado sem o gesto de
registrar.
