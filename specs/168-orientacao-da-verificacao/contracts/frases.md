# Contrato: as frases

Os textos fixos que os testes prendem. `{…}` é dado publicado ou derivado. Nenhum texto fixo do
candidato contém "heteroidentificação", "fenótipo", "fenotípic", "aferição" ou "indeferid"
(FR-7330).

## Candidato: o degrau (FR-7304, FR-7306, FR-7312)

| Estado | Rótulo | Texto |
|---|---|---|
| `FALTA`, antes do período | Falta um passo seu | Porquê: "Você se inscreveu em {modalidade}, e quem se inscreve nela passa também por esta etapa: {etapa}." Ação: "Acontece de {início} a {fim}. A comissão vai informar o dia, a hora e como participar." |
| `FALTA`, no período | Falta um passo seu | Ação: "Está acontecendo até {fim}. A comissão vai informar o dia, a hora e como participar." |
| `FALTA`, sem período | Falta um passo seu | Ação: "A comissão vai informar quando e como participar." |
| `AGUARDA_COMISSAO` | Aguardando a comissão | "O período desta etapa terminou em {fim}. Aguarde a comissão: o resultado aparece neste acompanhamento quando for publicado." |
| `AGUARDA_RESULTADO` | Aguardando o resultado | "O resultado desta etapa aparece neste acompanhamento quando for publicado." |

Em todo `FALTA`:

- **Consequência**, se o efeito for "retira": "Se você não participar, deixa de concorrer pela reserva
  de vagas e continua concorrendo pela ampla concorrência."
- **Consequência**, se o efeito for "elimina": "Se você não participar, é eliminado desta seleção."
- **Secundária**: "No Edital, veja a etapa {etapa}." com o link "Ver o Edital vigente".

Com o vídeo, só com a chave ligada:

- **`PODE_GRAVAR`**: "Você pode gravar um vídeo curto ou fazer a entrevista ao vivo. As duas formas
  valem igual. O vídeo pode ser enviado até {fim}." Link: "Ver como funciona".
- **`RECEBIDO`**: "Seu vídeo chegou em {data}. A comissão ainda não o abriu." Link: "Ver o
  comprovante".
- **`EM_ANALISE`**: "A comissão está analisando o seu vídeo." Link: "Ver o comprovante".
- **`ENCAMINHADA`**: "A comissão quer conversar com você ao vivo. Isso não é reprovação." (a FR-7144
  da `166`)

Na convocação e nos passos seguintes, a linha do porquê é: "Também falta um passo seu: {etapa}, de
{início} a {fim}." Sem período, ela termina em "{etapa}.".

## Candidato: o modelo inicial do aviso do passo (FR-7319, FR-7320)

- **Nome**: "Aviso do passo de uma etapa".
- **Assunto**: o assunto neutro da `066`.
- **Corpo**, com as variáveis `{nome_do_candidato}`, `{etapa}`, `{periodo_da_etapa}`,
  `{processo_seletivo}` e `{area_do_candidato}`: "Olá, {nome_do_candidato}. Há um passo a mais para
  você no {processo_seletivo}: a etapa {etapa}{periodo_da_etapa}. Veja no seu acompanhamento quando e
  como participar: {area_do_candidato}".

O corpo não contém "cota", "reserva", "modalidade", "lista", "ppi" nem "heteroidentifica".

## Gestão: as células (FR-7321 a FR-7327)

| Célula | Natureza | De quem | Ato | Leva a |
|---|---|---|---|---|
| Pareceres que faltam | AVALIAR (dos outros) | avaliadores | "Avaliar N inscrições"; nota à presidência: "faltam: Bruno 2, Carla 2"; até {fim} | Mesa / distribuição |
| Aviso não dado | AVISAR (nova) | quem conduz | "Avisar N inscrições sobre {etapa}" | confirmação do aviso do passo |
| Período vencido | DISTRIBUIR | quem conduz | "Registrar a ausência ou os pareceres de N inscrições"; nota: "o período terminou em {fim}" | distribuição |
| A encaminhar (vídeo) | CONSOLIDAR | quem conduz | "Encaminhar N inscrições à entrevista ao vivo" | conferência da consolidação |
| Linha de avaliar (Minhas atividades) | AVALIAR | o avaliador | "Avaliar N inscrições · até {fim}" | Mesa |

## Gestão: a advertência (FR-7336)

"O nome da etapa «{etapa}» usa o termo «{termo}», e o candidato lê esse nome no acompanhamento. Se o
Edital permitir, prefira um nome sem ele." Severidade: advertência; não impede publicar.
