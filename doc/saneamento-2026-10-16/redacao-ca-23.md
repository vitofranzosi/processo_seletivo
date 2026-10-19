# CA-23 — redação final proposta, não implementada

Data: 16/10/2026. Estado: **aguardando aprovação da redação**.
Fonte: [achado de 09/10](../achado-reenvio-da-convocacao-sugere-prazo-novo.md).

## Regra a preservar

O vencimento é absoluto, informado ao convocar. O primeiro envio bem-sucedido põe o prazo em
curso; reenvio não reinicia contagem nem muda vencimento. Não calcular uma data nova a partir
do reenvio e não substituir o instante do primeiro envio pelo mais recente.

## Texto proposto

Para a comunicação com vencimento, na primeira emissão e em reenvios:

> Prazo para atender: até **{vencimento original, DD/MM/AAAA às HH:MM}**.
> O prazo é contado do primeiro envio bem-sucedido, realizado em **{primeiro envio, DD/MM/AAAA às HH:MM}**.

Acrescentar somente em reenvio:

> Esta mensagem é um reenvio. O vencimento original permanece o mesmo.

No portal e na gestão, usar os rótulos:

- **Primeiro envio:** DD/MM/AAAA às HH:MM.
- **Último reenvio:** DD/MM/AAAA às HH:MM, quando houver.
- **Prazo para atender:** até DD/MM/AAAA às HH:MM.
- **O reenvio não altera o vencimento.**, quando houver reenvio.

Datas apresentadas no fuso institucional, de maneira uniforme. Sem vencimento declarado, manter
o texto que remete ao prazo publicado no Edital, sem inventar data ou primeiro envio.

O instante real de sucesso da primeira emissão pode ainda não existir ao montar a mensagem.
A futura especificação deve resolver essa disponibilidade sem registrar sucesso fictício ou
alterar a emissão. Se não puder afirmar o instante com evidência, a mensagem inicial deve dizer
apenas **“Prazo para atender: até {vencimento original}. O reenvio desta comunicação não altera
o vencimento.”** O portal pode mostrar o primeiro sucesso depois de registrado. Esta alternativa
de apresentação também depende do aceite da redação; nenhuma mudança de serviço está autorizada.

## Pontos que devem mudar juntos em execução futura

| Artefato | Texto ou situação atual |
|---|---|
| `backend/processo_seletivo/convocacao/application/comunicar.py`, `COM_PRAZO` | “contado do envio desta mensagem” |
| `backend/processo_seletivo/portal/templates/portal/convocacao.html` | “contado do envio da comunicação” e data do envio selecionado |
| `backend/processo_seletivo/portal/templates/portal/_convocacao_da_inscricao.html` | Mesma ambiguidade no cartão |
| `backend/processo_seletivo/interface/templates/interface/convocacao.html` | “Enviada em” e “contado do envio da comunicação”, incluindo lista/cartão |
| `backend/processo_seletivo/convocacao/application/selectors.py` | Seleção do envio mais recente deve continuar distinguível do primeiro sucesso |
| Spec 019, UX-038; 050/059 quando afetadas | Emenda rastreável de apresentação, preservando regra |
| Guardiões de mensagem/vocabulário/portal | Atualizar expectativas em conjunto com a spec, sem apenas afrouxar asserções |

Guardiões identificados pela auditoria: `tests/unit/convocacao/test_mensagem.py`,
`tests/test_vocabulario_da_convocacao.py` e `tests/interface/test_portal_caminho_da_convocacao.py`
(relativos a `backend/`). Manter o caso de integração
`tests/integration/convocacao/test_reenvio_nao_reinicia_prazo.py`.

## Aceite futuro

Primeiro envio e múltiplos reenvios mantêm a mesma data absoluta; falha inicial não é apresentada
como sucesso; primeiro sucesso e último reenvio não se confundem; e-mail, portal e gestão não
sugerem prazo novo. A informação deve ser demonstrável ao candidato e ao operador.

O eventual encurtamento por primeiro envio tardio é achado separado e não resolvido aqui.
Não mudar vencimentos, regras do Edital, recusas ou estados da convocação para corrigir texto.
