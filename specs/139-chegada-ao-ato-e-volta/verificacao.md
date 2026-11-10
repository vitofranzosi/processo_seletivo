# Verificação: A providência chega ao ato, e o ato volta ao Centro (139)

**Data**: 2026-11-10 · **Base**: `main` em `4ae78556`

## No navegador

Banco descartável `ps139_dev` (migrado, Unidade semeada, autoridade da suíte), com o C06 e o C12
carregados pelo comando da `134`; servidor pela entrada `chegada-139` do `.claude/launch.json`
(porta 8139). Identidade `treino.presidencia`, janela de 1440 × 900. As distâncias são do topo da
janela, depois da rolagem que o fragmento provoca.

| Passo | Antes (estudo) | Depois | Critério |
|---|---|---|---|
| C06 · Centro → "Abrir a tela" (Fixar os participantes, Ampla e PPP juntadas) | topo da tela; congelar a 1.681 px | `#titulo-recortes` a 0 px; o botão de congelar da Ampla a 721 px | SC-1490, UX-319 |
| C06 · congelar a Ampla → bloco | "Ainda neste marco" em texto; sem volta | PPP é link para `#recorte-<PPP>`; "Voltar ao Centro de Controle do Edital" a 399 px | FR-4768, FR-4769 |
| C06 · seguir a PPP no bloco | — | o recorte da PPP na tela, o botão de congelar a 787 px (o fim da página limita a rolagem) | FR-4760 |
| C06 · congelar a PPP → "Voltar ao Centro" | dois cliques (migalha → detalhe → link) | um clique; o Centro no estado novo, o destaque "Obter a semente pública" levando a `#titulo-ocorrencia` | SC-1492, FR-4761 |
| C12 · Centro → "Conferir os documentos de 3 convocações" | topo da tela; chamadas a 2.151 px | `#chamadas` a 0 px | SC-1491, UX-319 |
| C12 · conferir os dois documentos da Cecília → bloco | "Próximo" levava ao topo da convocação | "Registrar o desfecho de 1 convocação pronta" leva a `#chamada-3`, que é a Cecília; o "Ainda neste marco" (a ordem da PPP) é link; volta ao Centro | FR-4764, FR-4768, FR-4769 |
| C12 · seguir o desfecho | desfecho a 3.020 px | a chamada da Cecília a 435 px, com "Registrar desfecho" na dobra (o fim da página limita a rolagem) | FR-4764 |

Console sem erro nem violação de CSP em todas as telas percorridas (FR-4771).

## Automatizada

- `tests/unit/interface/test_chegada_ao_ato.py`: as âncoras, o caminho comum de duas e de três
  listas, cada providência da convocação, a ausência de endereço, e a igualdade das providências sem
  o fragmento (FR-4760 a FR-4767, SC-1493).
- `tests/interface/test_andamento_transicoes.py`: o retorno só depois do ato, depois do próximo, e o
  Centro respondendo; a providência que nasce de convocar leva a `#pendentes`, que a tela tem.
- `tests/integration/treinamento/test_chegada_e_volta_nos_cenarios.py`: no C06, a juntada leva a
  `#titulo-recortes`, cada célula ao seu recorte, e a tela tem os dois ids; depois de congelar a
  Ampla, a PPP é link e o bloco volta ao Centro. No C12, conferir leva a `#chamadas`.

## O que não se verificou

- **Com pessoas.** Nenhum operador percorreu o caminho.
- **A 375 px.** A rolagem por fragmento não depende da largura, e nenhuma regra nova de layout
  entrou; não foi medida.
- **O desfecho num cenário automatizado.** A posição da chamada pronta é provada sem banco e, com
  banco, só no navegador acima: nenhum cenário da `134` nasce com uma chamada pronta.
