# Contrato das telas: Andamento da seleção

Nenhuma rota nova. Nenhuma rota de API nova. Muda o detalhe do Edital e, por último, as mensagens de
sucesso de seis telas de ato.

## `GET /gestao/editais/<id>/` — Edital publicado ou encerrado

### Topo

Título, selo da situação, mensagem do ato (quando houver). **Sem a trilha de situação** (`ol.etapas`)
depois da publicação (D-002). Em elaboração, em revisão, homologado e cancelado: como hoje.

### "O que fazer agora" (nível 1, B1)

`section.cartao` com `aria-labelledby="acoes-titulo"`, título "O que fazer agora", e:

1. **A contagem**: `p.contagem-de-providencias` — "N providências em aberto · M são suas" (ou
   "· nenhuma é sua"); sem providência: `p.nada-em-aberto` "Nada em aberto: <porquê>."
2. **As suas**: `ul.providencias.suas`, cada `li` com `span.marca-sua` "Sua", o link (`a`) com o verbo
   do ato e o lugar ("Emitir a comunicação — Cefor · Ampla concorrência"), e `span.quando` com o
   prazo ou a espera, quando houver.
3. **As de outros papéis**: `ul.providencias.de-outros`, cada `li` começa pelo papel em `strong`
   ("Quem publica resultado:") e diz o ato e o lugar, **sem link**.
4. **As que aguardam ou estão impedidas**: `ul.providencias.em-espera`, cada `li` com o sinal e a
   palavra da situação, o ato, o lugar e a razão (`span.razao`); no impedimento, quem resolve.
5. Até cinco itens no total, na ordem 2 → 3 → 4; as demais em `details.mais-providencias` com
   `summary` "Mais N".
6. **Atenção** (D-010): `div.atencao-do-andamento` com um `p` por Etapa sem efeito: "<Etapa> está
   declarada no Edital, e nenhum ato do GPS depende do resultado dela."
7. **As ações de hoje**, `ul.lista-acoes` como hoje; com providência da pessoa, nenhuma é cheia.
8. **Conteúdo imutável**: `p.imutavel` numa linha no pé do cartão.
9. A Retificação que aguarda a pessoa e as frases da FR-2820 da `104` continuam (são providências de
   Retificação: aparecem no item 2 ou 3, e não duas vezes).

"Nenhum ato disponível para seus papéis nesta situação" **não** aparece quando há providência da
pessoa (FR-4086).

### "Andamento da seleção" (nível 2, B2) — no lugar de "Classificação"

Só para quem hoje via o cartão "Classificação" (D-004). `section.cartao.andamento` com
`aria-labelledby="andamento-titulo"`:

- `p.linha-das-inscricoes`: "Inscrições encerradas em dd/mm/aaaa · N enviadas" ou "Inscrições
  abertas até dd/mm/aaaa hh:mm · N enviadas até agora".
- Um `details.perfil-do-andamento` por Perfil com marco, **fechado**; `summary` com o nome do Perfil,
  a forma e o resumo em palavras. O Perfil sem inscrição: um `p` só, "Não se aplica: nenhuma
  inscrição enviada".
- Aberto: `div.rolavel.moldura-do-andamento` com `table` (`caption` = "Andamento de <Perfil>, por
  lista"), uma linha de grupos (`th colspan scope="colgroup"`), uma de pontos (`th scope="col"`), e
  uma linha por lista (`th scope="row"`). Cada `td` tem `data-situacao`, o sinal (`aria-hidden`), a
  palavra, a nota; é link (`a`) só para quem abre a tela.
- `p.destinos-do-perfil`: os destinos do antigo cartão para aquele Perfil (por marco).
- Nota da matrícula (D-003), quando cabe.

## As telas de ato (por último, D-015)

`corte`, `ordenacao`, `ocupacao`, `sorteio`, `convocacao` e a página dos documentos da convocação:
logo abaixo da mensagem de sucesso (`p.sucesso`), o parcial `_proximo_nesta_lista.html`:

- `p.proximo-nesta-lista`: "Próximo nesta lista: <ato>" (link, se é da pessoa; "<papel>:
  <ato>", se não; "Nada mais em aberto nesta lista.", se não há);
- `p.ainda-neste-marco` (opcional): "Ainda neste marco: <lista> — <ato ou situação>; …".

Só aparece no GET que mostra a mensagem de sucesso de um ato; abrir a tela não o mostra.
