# Contrato: o cadastro de reserva nas telas e nas recusas

**Feature**: [../spec.md](../spec.md) · **Decisões técnicas**: [../research.md](../research.md) (T-003, T-004, T-008 a T-011)

`{rotulo}` é o código do Perfil, ou o nome quando não há código, como nas advertências da `097`.
`{marco}` é o nome do marco que convoca ("Classificação final"); sem nome, "classificação deste
Perfil". Os números seguem a forma do [documento](documento.md).

---

## R — As recusas e a advertência da Revisão (FR-6933 a FR-6940, UX-726)

| Código | Severidade | Frase |
|---|---|---|
| `reserve_limited_with_continuation` | impeditiva | `O Perfil '{rotulo}' declara cadastro de reserva limitado, e a {marco} admite chamar candidatos além da faixa: o cadastro não teria limite. Retire a continuação do corte da {marco}, ou declare o cadastro de reserva sem limite.` |
| `reserve_unlimited_without_continuation` | impeditiva | `O Perfil '{rotulo}' declara cadastro de reserva sem limite, e o corte da {marco} não admite chamar além da faixa: o cadastro pararia nos primeiros que ela alcança. Admita a continuação no corte da {marco}, ou declare o cadastro de reserva limitado.` |
| `reserve_limited_without_cut` | impeditiva | `O Perfil '{rotulo}' declara cadastro de reserva limitado, e a {marco} não tem regra de corte: o número do cadastro vem do corte. Declare o corte da {marco}, ou declare o cadastro de reserva sem limite.` — sem marco que convoca: `… e nenhum marco de classificação deste Perfil convoca: …` |
| `reserve_limited_to_nobody` | impeditiva | `O Perfil '{rotulo}' declara cadastro de reserva limitado, e o corte da {marco} não alcança ninguém além das vagas{ na lista X}: o cadastro seria de zero classificados. Aumente o alvo ou o excedente do corte, ou declare que não há cadastro de reserva.` |
| `reserve_limited_divergent_milestones` | impeditiva | `O Perfil '{rotulo}' declara cadastro de reserva limitado, e os cortes da {marco 1} e da {marco 2} dão números diferentes{ na lista X} ({N1} e {N2}): o documento não teria um número para dizer. Iguale o alvo e o excedente dos dois cortes.` |
| `reserve_limit_typed_in_draft` | advertência | `O Perfil '{rotulo}' guardava o cadastro de reserva limitado em {digitado}, digitado antes de o número passar a vir do corte. O Edital vai publicar {derivado}, que é o que o corte da {marco} alcança além das vagas.` |

O caminho de cada achado é o do Perfil (`/profiles/id={id}/reserveType`, a gramática da `004`), para que a Revisão o leve à
Etapa Perfis, onde a espécie se troca; o da advertência também. As recusas da Retificação (FR-6951)
usam o mesmo código e a mesma frase.

## G — A gravação de rascunho (FR-6931)

`validate_profile`, para `LIMITED` com número: `O número do cadastro de reserva limitado não se digita: ele vem do corte do marco que convoca deste Perfil.` Campo `reserveLimit`.

## P — A Etapa Perfis (FR-6932, UX-725)

O fieldset "Cadastro Reserva" mantém as três opções. Debaixo de "Cadastro reserva limitado", um único
elemento de ajuda, sem link:

- sem corte no marco que convoca: `O número vem do corte do marco que convoca deste Perfil, na etapa Classificação.`
- com corte, número único: `O número vem do corte da {marco}: até {N} classificados.`
- com corte, números por lista: `O número vem do corte da {marco}:` seguida de lista curta `Ampla concorrência: até {N1}` · `{Modalidade}: até {N2}`.

O resumo do cartão (`perfis.js`, a tabela da etapa) usa o `data-resumo` da opção "limitado", escrito
pelo servidor com `Cadastro.resumo_limitado()`: `limitado` sem corte; `limitado: até {N}` com número
único; `limitado: até {N1} AC, {N2} {código 2}` por lista.

## D — O texto curto da gestão (`Cadastro.descricao_curta`)

Usado pela Revisão (linha "Cadastro Reserva"), pelo relatório do Edital, pela visão institucional e
pela tabela da etapa.

| Caso | Texto |
|---|---|
| não há | `Não há` |
| ilimitado | `Sem limite` |
| limitado legado | `Limitado em {N}` |
| limitado, número único | `Limitado: até {N}` (com `por lista` quando há Modalidade) |
| limitado, números diferentes | `Limitado: até {N1} AC, {N2} {código 2}, …` |
| limitado sem corte (só no rascunho) | `Limitado, sem corte no marco que convoca` |

Os números aqui são algarismos, sem o extenso do documento.

## O — O portal (FR-6945)

| Lugar | Caso | Texto |
|---|---|---|
| oferta (`_oferta`) | número único | `até {N} classificado(s), para convocação futura` *(a forma de hoje)* |
| | com Modalidade, mesmo número | `até {N} classificados em cada lista de concorrência, para convocação futura` |
| | números diferentes | `até {N1} na ampla concorrência, {N2} na lista {Modalidade 2} e {N3} na lista {Modalidade 3}, para convocação futura` |
| acompanhamento (`frase_da_reserva`) | número único | `O Edital prevê cadastro reserva de até {N} pessoa(s) para este Perfil.` *(a de hoje)* |
| | com Modalidade, mesmo número | `O Edital prevê cadastro reserva de até {N} pessoas em cada lista de concorrência deste Perfil.` |
| | números diferentes | `O Edital prevê cadastro reserva de até {N1} pessoas na ampla concorrência, {N2} na lista {Modalidade 2} e {N3} na lista {Modalidade 3} deste Perfil.` |

No legado, o número publicado, na forma de hoje.

## A — O assistente de dúvidas (FR-6946)

O cartão "Limite do cadastro de reserva" diz o texto de D sem a palavra "Limitado". No legado, cita
`/profiles/…/reserveLimit`, como hoje. No derivado, cita o `cutRule` do marco que convoca, com o rótulo
`Cadastro de reserva (pelo corte)`.

## N — A nota da ocupação e da convocação (FR-6947, FR-6949, UX-727)

Só no Perfil legado, como `<p class="nota">`, no topo do recorte da ocupação e no da convocação:

- sem continuação: `O Edital publicou cadastro de reserva limitado em {publicado}. O sistema não aplica esse número: a convocação alcança quem o corte alcança — até {M} classificados além das vagas{ em cada lista de concorrência}.`
- com continuação: `O Edital publicou cadastro de reserva limitado em {publicado}. O sistema não aplica esse número: a convocação alcança quem o corte alcança, e a faixa cresce pela faixa seguinte do corte, na ordem.`
- sem corte no marco que convoca: `O Edital publicou cadastro de reserva limitado em {publicado}. O sistema não aplica esse número, e nenhum marco que convoca deste Perfil declara corte.`

`{M}` é o número derivado; com números diferentes por lista, a forma de C1 do documento sem "cadastro de
reserva de".

## T — A Retificação (FR-6948, FR-6950)

- O campo `Limite do Cadastro Reserva` só é desenhado no Perfil legado.
- O formulário de Perfil acrescentado por Retificação não o tem.
- Na conferência, quando a Retificação muda `cutRule/targetCount` ou `cutRule/surplusCount` do marco
  que convoca de um Perfil limitado não legado, a lista de antes e depois ganha a linha
  `Cadastro de reserva`, com D do conteúdo-base e D do conteúdo retificado.
