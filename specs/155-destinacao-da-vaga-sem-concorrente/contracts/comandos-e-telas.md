# Contrato: comandos e telas da 155

Todos os comandos passam por `comando_de_comissao` (permissão `pode_gerir_comissao`, trava do
Processo, idempotência por chave) e gravam evento de trilha com correlação (FR-6341). Toda escrita
vem de dois passos — prévia com assinatura e confirmação —, e a confirmação com leitura divergente é
recusada com `leitura_do_recorte_mudou`, como no acréscimo.

## Comandos

### `ocupacao.application.destinacao.destinar_vaga`

```text
destinar_vaga(*, actor, processo_id, edital_id, perfil_id, marco_id, lista_id, assinatura,
              fatos_externos, idempotency_key, correlation_id) -> declarado
```

- **Aceita**:
  - reversão declarada por esgotamento, com a condição da FR-6304 cumprida e nenhum impedimento;
  - no incremento F, também por saldo.
- **Grava**: o movimento (R-001); a sucessora da apuração da origem, num *savepoint*; o evento
  `OCUPACAO_DESTINAR_VAGA`.
- **Recusa** (código, 409 salvo dito):

| Código | Quando |
|---|---|
| `sem_reversao_declarada` | o Perfil não declara reversão |
| `passagem_entre_cotas` | o Perfil declara a terceira resposta |
| `reversao_por_saldo_aguarda_decisao` | por saldo, até o incremento F |
| `ainda_ha_quem_ocupar` | a condição da FR-6304 não está cumprida; diz quantos |
| `destinacao_impedida` | algum impedimento da FR-6306; diz qual e até quando |
| `sem_saldo_a_destinar` | não há saldo, inclusive porque um movimento antigo já cedeu |
| `leitura_do_recorte_mudou` | a assinatura da prévia não confere |

### `desfazer_destinacao`

- **Aceita**: um movimento de reversão sem desfazimento.
- **Grava**: o movimento contrário, com motivo, e o evento.
- **Com chamada dependente**: grava `OCUPACAO_DESFAZIMENTO_IMPEDIDO`, com as chamadas, e devolve 409
  `destinacao_com_chamada_dependente` (R-005).

### `declarar_nao_preenchida` / `desfazer_nao_preenchida`

- **Aceita**:
  - reserva sem reversão declarada, ou linha geral, com ninguém que ainda possa ocupar e nenhum
    impedimento;
  - fundamento não vazio.
- **Recusa**:

| Código | Quando |
|---|---|
| `fundamento_obrigatorio` (422) | o fundamento está vazio |
| `o_edital_manda_destinar` | a reversão declarada é aplicável |
| `passagem_entre_cotas` | o Perfil declara a terceira resposta |
| `ainda_ha_quem_ocupar` | há quem ainda possa ocupar |
| `destinacao_impedida` | algum impedimento da FR-6306 |
| `sem_saldo_a_destinar` | não há vaga a ocupar |

### Lista sem concorrente (classificação)

`registrar_lista_sem_concorrente`, na interface, compõe `emitir_ordem` e `emitir_corte` numa
transação. Recusa o que eles recusam, e mais `lista_com_concorrente`.

### `divulgacao.application.publicar.publicar_resultado` (existente)

Inclui, na mesma transação, as ordens vigentes das listas sem concorrente do marco, da mesma
natureza e ainda não publicadas. A prévia as lista, e a assinatura as cobre.

## Telas

| Tela | Rota | Muda |
|---|---|---|
| Ocupação | `interface:ocupacao` | a situação de cada recorte (R-008); os botões "Destinar à ampla concorrência", "Declarar vaga não preenchida" e os desfazimentos, cada um com "Confira antes" |
| Confira antes | `interface:destinar-vaga`, `interface:declarar-nao-preenchida`, `interface:desfazer-destinacao`, `interface:desfazer-nao-preenchida` | página de conferência no molde de `ocupacao_acrescimo.html` |
| Ordenação | `interface:registrar-lista-sem-concorrente` | o gesto da lista vazia, com a conferência que diz o que se registra |
| Publicação do resultado | `interface:publicar-resultado` | a prévia lista as listas sem concorrente que entram junto |
| Centro do Edital | detalhe do Edital | o ramo "Ocupar a vaga — impedida" passa à situação de R-008 |
| Convocação | `interface:convocacao` | com a fila vazia, o índice cita a situação da vaga |
| Passo Perfis | composição e Retificação | a terceira resposta |
| Página pública da seleção | `portal:selecao` | a seção "Destinação das vagas" (`portal/_destinacao_das_vagas.html`) |
| Relatório do Edital | `interface:relatorio-do-edital` | a seção "Destinação das vagas" |

Vocabulário: nada de "convoca*", "aceite", "matrícul*", "desistênci*" nem "chamada de suplente" nos
arquivos da ocupação (`tests/test_vocabulario_da_ocupacao.py`). A chamada dependente é dita como
"pessoa chamada para esta vaga".
