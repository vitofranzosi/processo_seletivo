# Contrato: a recusa do marco intermediário

## Código e resposta

| Item | Valor |
|---|---|
| Código | `apuracao_em_marco_intermediario` |
| Status HTTP (API) | 409 |
| Campo | `marco` |
| Frase | "A {marco} decide quem participa da Etapa {Etapa governada}: ela não apura vagas nem convoca. As vagas são apuradas e convocadas na {marco que lê}." |

A frase não leva identificador interno, UUID nem código de enum (FR-4537).

## Onde acontece

A recusa acontece sempre sob a trava do Processo e antes de qualquer gravação (FR-4536).

| Comando | Caminhos que passam por ele |
|---|---|
| `emitir_apuracao` → `_apurar` | tela da ocupação (inicial e sucessora), gesto "Apurar" da condução, API |
| `emitir_sucessora_por_efeito` → `_apurar` | desfecho de convocação e acréscimo de vaga. **No desfecho, a recusa vira `apuracaoPendente`, e o desfecho é gravado** (D-002) |
| `acrescentar_vagas` | tela da ocupação |
| `causar_faixa_seguinte` | tela da ocupação |
| `convocar` | chamada individual, "Convocar titulares" em lote, correção da `120`, API |

## Garantias

- **Nada é gravado:** ato, apuração, movimento, acréscimo, faixa, convocação, comunicação, evento de
  trilha de emissão e reserva de idempotência (SC-1420).
- **Repetir** o pedido recusado continua recusando: a chave não ficou reservada.
- **Atos existentes** no marco intermediário continuam vigentes e legíveis (FR-4540).

## O que não muda

- Recusas existentes, como `ordem_nao_vigente`, `sem_quadro_publicado` e `motivo_da_sucessao_obrigatorio`:
  continuam com o código e a frase de hoje.
- `emitir_corte`, `continuar_corte`, `emitir_ordem`, `publicar_resultado`, `desfechar`, `comunicar` e
  `atestar`.
