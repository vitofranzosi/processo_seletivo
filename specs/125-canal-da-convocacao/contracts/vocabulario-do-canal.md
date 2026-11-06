# Contrato: o vocabulário da comunicação, por canal

Incremento C (FR-3998 a FR-4004). Inventário de 06/11/2026 sobre a `main` em `250efe97`, relativo a
`backend/processo_seletivo/`. As linhas são as daquele commit. **Mensagem** é a coluna de hoje, salvo
onde marcado.

## Portal

| Onde | Hoje (as duas formas) | Publicação | Mensagem |
|---|---|---|---|
| `portal/obrigacoes.py` `PRAZO_NAO_INICIADO` (cartão do prazo, chamada aberta, acompanhamento) | *"O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."* | *"... ele conta a partir da publicação da convocação."* (D-006) | igual |
| `portal/convocacao.html:61-62`, `_obrigacoes_da_convocacao.html:91`, `_convocacao_da_inscricao.html:22` | *"Comunicação enviada em ‹data›"* | *"Publicada em ‹referência›"* (D-005) | igual |
| `portal/convocacao.html:64-65`, `_obrigacoes_da_convocacao.html:93`, `_convocacao_da_inscricao.html:28` | *"‹vencimento›, contado do envio da comunicação"* | *"‹vencimento›, contado da publicação"* | igual |
| `portal/obrigacoes.py` `linha_da_substituida` | *"Publicada em ‹ref›"* / *"Comunicada em ‹data›"* | igual | *"Enviada em ‹data›"* (D-008) |

A referência da convocação **vigente** passa a aparecer no portal. Hoje só aparece a da substituída.

## Gestão — `interface/templates/interface/convocacao.html`

| Linha | Hoje | Publicação |
|---|---|---|
| 55 | *"Comunicação enviada. O prazo desta convocação corre a partir do envio."* | *"Publicação registrada: ‹referência›. O prazo desta convocação corre a partir deste registro, e o candidato já vê a convocação no portal."* (D-007) |
| 166 | *"· enviada em ‹data›, vencimento…"* | *"· publicada em ‹referência›, vencimento…"* |
| 170 | *"…porque a comunicação não foi enviada com sucesso"* | *"…porque a publicação ainda não foi registrada"* |
| 191 | *"Comunicações que ainda não saíram"* | *"Publicações a registrar"* |
| 192 | *"…sem comunicação enviada, e o prazo delas não começou"* | *"…sem publicação registrada: o prazo delas não começou, e o candidato ainda não as vê"* |
| 221 | *"…a mensagem pode ter saído sem registro. Confira o histórico antes de emitir de novo"* | *"…o registro da publicação pode ter sido gravado. Confira o histórico antes de registrar de novo"* |
| 270 | *"A comunicação sai no mesmo ato."* (**falsa** na publicação) | *"A publicação, você registra depois; o candidato só vê a convocação a partir dela."* |
| 404, 410 | *"Sem comunicação enviada"* | *"Publicação não registrada"* |
| 417 | *"Enviada em ‹data›"* | *"Publicação registrada em ‹instante› — ‹referência›"* (D-005) |
| 418 | *"— contado do envio da comunicação"* | *"— contado do registro da publicação"* |
| 424 | *"Convocado, prazo não iniciado — a comunicação ainda não foi enviada com sucesso"* | *"Convocado, prazo não iniciado — a publicação ainda não foi registrada, e o candidato ainda não vê esta convocação"* (D-007) |
| 582 | *"Emitir a comunicação"* / *"… de novo"* | *"Registrar a publicação"* / *"Registrar outra publicação"* |

Já decidem pela forma, e não mudam: 135, 209/211, o campo da referência (575-580).

## Gestão — outros arquivos

| Onde | Hoje | Publicação |
|---|---|---|
| `_resultado_da_comunicacao.html:5` | *"N comunicação enviada / comunicações enviadas"*, inclusive na publicação com referência | *"Publicação registrada para N convocações; o prazo corre a partir dela, e os candidatos já as veem."* O resultado do fluxo passa a trazer a forma e a referência |
| `_vencimento_da_convocacao.html:31, :38` | *"O prazo corre a partir do envio da comunicação, e não desta tela."* | *"... a partir do registro da publicação ..."* (a forma passa a entrar no `include`) |
| `_correcao_da_convocacao.html:56` | *"prazo ainda não iniciado: a comunicação não foi enviada com sucesso"* | *"... a publicação ainda não foi registrada"* |
| `convocacao_historico.html:29` | coluna *"Enviada em"* | cabeçalho *"Comunicação"*; por linha, *"publicada em ‹ref›"* / *"enviada em ‹data›"* |
| `convocacao_historico.html:43` | *"não enviada"* | *"publicação não registrada"* |
| trilha, `comunicar.py:533-537` | *"Comunicação ENVIADA da convocação ‹uuid›… na forma PUBLICATION. Enviada em ‹ISO›."* | registros novos: *"Publicação da convocação registrada: ‹referência›…"*; antigos intocados |

## Recusas (`DomainError`, mostradas na gestão)

| Onde | Hoje | Publicação |
|---|---|---|
| `comunicar.py:327-331` `vencimento_anterior_ao_envio` | *"…é anterior ao envio…"* | *"…é anterior ao registro da publicação…"* |
| `comunicar.py:213-217` `emissao_em_estado_indeterminado` | *"A mensagem pode ter saído…"* | *"O registro da publicação pode ter sido gravado…"* |
| `desfechar.py:410-414` não atendimento | *"A comunicação desta convocação não foi enviada com sucesso…"* | *"A publicação desta convocação ainda não foi registrada…"* |
| `fluxo.py:809-813` `nenhuma_comunicacao_pendente` | *"Não há convocação sem comunicação enviada neste recorte."* | *"Não há convocação com publicação a registrar neste recorte."* |

Os códigos das recusas não mudam: muda só o texto.

## A varredura

O teste renderiza cada tela acima numa convocação de cada forma. Na publicação, ele reprova *"envio da
comunicação"*, *"comunicação enviada"*, *"Enviada em"* e *"Emitir a comunicação"*. Na mensagem, reprova
*"publicada"* e *"publicação"*, salvo no campo de forma do recorte (linha 135), que nomeia as duas.
