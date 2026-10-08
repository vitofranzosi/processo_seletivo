# Contrato das telas: o que cada estado mostra

**Feature**: [../spec.md](../spec.md) · **Data**: 2026-10-06

Contrato de interface do canal do candidato. As rotas são as que já existem; **nenhuma nasce**
(`FR-1105`). Os textos entre aspas são os que os testes procuram.

## Minhas inscrições — `portal:inscricoes`

| Estado da inscrição | Situação | Linha extra | Ação principal | Ação secundária |
|---|---|---|---|---|
| rascunho | como hoje | — | como hoje | — |
| enviada, sem convocação | "✓ Inscrição enviada" + protocolo | — | "Acompanhar" → `acompanhamento` | — |
| enviada, convocação **aberta** | "✓ Inscrição enviada" + protocolo | "Convocação aberta", com símbolo | "Ver convocação" → `convocacao` | "Acompanhar" → `acompanhamento` |
| enviada, convocação **concluída** | "✓ Inscrição enviada" + protocolo | "Convocação: <espécie do desfecho>", discreta | "Acompanhar" → `acompanhamento` | — |

## Acompanhar — `portal:acompanhamento`

Seção "Convocação", logo abaixo do aviso de Retificação e antes de "Sua participação", **só** com
convocação vigente (`FR-1093`, `FR-1095`):

| Estado | Situação dita |
|---|---|
| comunicação não enviada | "ainda não foi enviada" e "não começou a correr" |
| prazo em curso | o prazo, "contado do envio da comunicação" |
| vencimento decorrido sem desfecho | "já passou" e "não decide nada sozinho" |
| desfecho registrado | "Situação registrada: <espécie>" |

Sempre: "Ver convocação" → `convocacao`. Depois, o chamado ao requerimento (tabela abaixo).

## Convocação — `portal:convocacao`

Conteúdo de hoje, inalterado. Acrescenta o chamado ao requerimento, abaixo da seção da chamada e
acima de "Voltar ao acompanhamento".

## O chamado ao requerimento (`_chamado_do_requerimento.html`)

| Estado de leitura | Mostra | Destino |
|---|---|---|
| disponível, em preenchimento | "Preencher Requerimento de Matrícula" (`a.principal`) | `requerimento` |
| enviado | "Conferir o Requerimento de Matrícula enviado" | `requerimento` |
| ainda indisponível, não aplicável | nada | — |

## Recusas

Inalteradas, e conferidas por teste (`FR-1101`): `acompanhamento`, `convocacao`, `requerimento` e
`requerimento-anterior` de inscrição alheia respondem como inscrição inexistente — mesmo status,
mesmo corpo. A lista de Maria não contém identificador nenhum de inscrição, convocação ou
requerimento de João.

## Proibições de texto (`UX-147`)

Nenhum texto novo diz "recebida em", "lida em", "entregue em", "direito à vaga", "vaga garantida" —
os termos de `PROIBIDOS` em `tests/test_vocabulario_da_convocacao.py`.
