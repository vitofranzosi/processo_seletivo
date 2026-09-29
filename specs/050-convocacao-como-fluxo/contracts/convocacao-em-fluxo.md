# Contrato: a convocação como fluxo

Contrato da aplicação e da tela. A API REST da `019` não ganha rota: os gestos são da gestão, e a
`convocar` da API passa a derivar a espécie como a tela.

## Funções de aplicação (`convocacao/application/fluxo.py`)

| Função | Entrada | Saída | Recusas |
|---|---|---|---|
| `previa_dos_titulares(edital, perfil_id, marco_id, lista_id)` | recorte | `{pessoas: [{id, protocolo, nome, posicao, especie}], parada: {pessoa, motivo} \| None, fundamento, forma, eventos, assinatura, impedimento}` | — (o impedimento vem como dado) |
| `convocar_titulares(actor, processo_id, …, vencimento, origem_do_vencimento, complemento, alcance, idempotency_key, endereco_do_portal)` | a prévia confirmada | `{convocadas: [...], enviadas, falhas, pendentes_por_publicacao}` | `alcance_mudou`, `forma_de_comunicacao_nao_declarada`, `vencimento_anterior_ao_envio`, as de `convocar` |
| `convocar_e_comunicar(…, inscricao_id, vencimento, origem_do_vencimento, complemento, …)` | a chamada individual | `{convocacao, comunicacao \| None, motivo_sem_comunicacao}` | as de `convocar` |
| `previa_dos_vencidos(…)` | recorte | `{convocacoes: [...], fora: {em_curso, nao_iniciado, sem_vencimento}, fundamento, assinatura}` | — |
| `registrar_nao_atendimento_dos_vencidos(…, complemento, alcance, idempotency_key)` | a prévia confirmada | `{desfechos: [...], apuracao: {...} \| None, apuracao_pendente: str \| None}` | `alcance_mudou`, as de `desfechar` |
| `previa_das_pendentes(…)` | recorte | `{convocacoes: [...], forma, assinatura}` | — |
| `emitir_pendentes(…, referencia_da_publicacao, alcance, idempotency_key, endereco_do_portal)` | a prévia confirmada | `{enviadas, falhas}` | `alcance_mudou`, `referencia_da_publicacao_obrigatoria` |

`desfechar` passa a devolver também `apuracao` ou `apuracaoPendente` (`D-005`).

## Códigos de recusa novos (`convocacao/domain/nomes.py`)

| Código | Status | Quando |
|---|---|---|
| `alcance_mudou` | 409 | a assinatura da confirmação diverge do alcance recalculado sob a trava |
| `especie_divergente_da_posicao` | 422 | a espécie informada não é a que a posição determina |
| `nenhum_titular_a_convocar` | 409 | o gesto é confirmado sem ninguém no alcance |
| `nenhuma_convocacao_vencida` | 409 | idem, no não atendimento |
| `nenhuma_comunicacao_pendente` | 409 | idem, nas pendentes |

## Motivos de a apuração seguinte não sair (dado, não recusa)

`outra_causa_de_obsolescencia` · `moveria_vaga` · o código da recusa da emissão.

## Rotas da gestão (`interface/urls.py`)

| Método | Caminho | View |
|---|---|---|
| POST | `editais/<id>/marcos/<id>/convocacao/titulares` | `convocar_titulares_view` |
| POST | `editais/<id>/marcos/<id>/convocacao/vencidos` | `nao_atendimento_dos_vencidos_view` |
| POST | `editais/<id>/marcos/<id>/convocacao/pendentes` | `emitir_pendentes_view` |
| POST | `editais/<id>/marcos/<id>/convocacao/convocar` (existente) | passa por `convocar_e_comunicar` |

Todas pelo POST-redirect-GET, preservando `?lista=`. `alcance_mudou` volta à tela com a prévia nova e
a recusa em destaque (`UX-104`).
