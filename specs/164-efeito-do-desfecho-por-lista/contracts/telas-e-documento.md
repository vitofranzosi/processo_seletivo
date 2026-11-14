# Contrato: telas e documento

## Composição das Etapas (UX-740, UX-741)

No cartão da Etapa, abaixo de *"A quem a Etapa se aplica"* (da `163`), aparece um grupo **só quando a
Etapa é restrita e eliminatória**:

*"O que acontece com quem tem desfecho desfavorável nesta Etapa?"*

- (•) **Deixa de concorrer pela reserva e continua na ampla concorrência**: marcada quando o rascunho
  não declara.
- ( ) **É eliminado do processo seletivo**

*"E com quem não comparecer?"*

- (•) **O mesmo efeito**
- ( ) **Deixa de concorrer pela reserva e continua na ampla concorrência**
- ( ) **É eliminado do processo seletivo**

Com JavaScript, o grupo aparece e some com o alcance e com o eliminatório. Sem JavaScript, aparece
sempre, e a publicação recusa a declaração incoerente (`efeito_sem_reserva`).

## Revisão, página pública e tela de Retificação (FR-7023)

Uma linha na Etapa que declara: **Efeito**, com a mesma frase do documento. Nada nas demais Etapas.

## Documento (FR-7023, T-014)

Na redação 1, o par `["Efeito", «frase»]`. Nas redações 2 e 3, a frase depois da frase do alcance.

| Desfavorável | Ausência | Frase |
|---|---|---|
| retira | o mesmo | O candidato com resultado desfavorável ou que não comparecer deixa de concorrer pela reserva de vagas e continua concorrendo pela ampla concorrência. |
| elimina | o mesmo | O candidato com resultado desfavorável ou que não comparecer é eliminado do processo seletivo. |
| retira | elimina | O candidato com resultado desfavorável deixa de concorrer pela reserva de vagas e continua concorrendo pela ampla concorrência. O candidato que não comparecer é eliminado do processo seletivo. |
| elimina | retira | O candidato com resultado desfavorável é eliminado do processo seletivo. O candidato que não comparecer deixa de concorrer pela reserva de vagas e continua concorrendo pela ampla concorrência. |

A Etapa sem declaração não ganha texto (SC-2330).

## Motivo do Resultado (FR-7008, FR-7009)

- Por avaliação: *"a avaliação concluiu «rótulo»; deixa de concorrer pela reserva «Modalidade» e
  continua na ampla concorrência"*.
- Por ausência: *"não compareceu: «motivo da presidência»; deixa de concorrer pela reserva
  «Modalidade» e continua na ampla concorrência"*.

## Acompanhamento do candidato (FR-7024, UX-742)

- A retirada não entra nas *eliminações*. O degrau segue a classificação.
- Linha no *porquê*: *"Na etapa «Etapa», o resultado foi «rótulo». Você deixou de concorrer pela
  reserva «Modalidade» e continua concorrendo pela ampla concorrência."*
- Cartão da lista reservada sem posição por retirada: *"Você deixou de concorrer por esta lista."*,
  seguido do motivo.

## Gestão (FR-7025, UX-743)

- **Lista de Resultados da Etapa**: rótulo *"Retirada da reserva"* e filtro próprio.
- **Confirmação da consolidação**: *"«h» habilitadas, «r» retiradas da reserva, «e» eliminadas"*.
- **Relatório do Edital**: linha *"Retiradas da reserva"* à parte das eliminadas, por avaliação e por
  ausência.
