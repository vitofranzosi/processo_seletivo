# Research: 143

## R-1 — Onde está o "candidato avisado"

- **Decisão**: ler `DestinatarioDoAviso` (origem `PENDENCIA`) da chamada, com o estado derivado pela
  `066` (`estado_do_destinatario`), e comparar o instante do aviso com o da pendência mais recente.
- **Por quê**: é o único registro de que um aviso foi pedido e do que o servidor de correio
  respondeu. A conferência pendente não gera aviso (a `134` é por gesto, nunca por evento).
- **Alternativas**: contar "avisada hoje" pela exclusão da prévia — diz só do dia, e não do envio.

## R-2 — Quem o gesto alcançaria, por pessoa

- **Decisão**: a prévia da `134` já seleciona pessoa a pessoa (`Selecao.pessoas`, com `exclusao`);
  ela passa a devolver o motivo por chamada.
- **Alternativas**: uma segunda seleção na interface — divergiria da regra.

## R-3 — Âncora da chamada

- **Decisão**: `id="convocacao-<vigente>"` no cartão, além do `chamada-N`.
- **Alternativas**: parâmetro de consulta que a tela leia (vetado pela primeira decisão da `139`);
  calcular a posição na página dos documentos (exigiria a ordem da tela).

## R-4 — O formulário do desfecho aberto

- **Decisão**: `open` no `<details>` do desfecho quando o passo é desfecho (pronta ou vencida). Sem
  script: o navegador não abre um `<details>` por fragmento de forma confiável.

## R-5 — Ocupada na apuração

- **Achado**: `ocupacao.domain.apuracao.ocupantes` — ocupante é o titular **habilitado**, mais e
  menos os efeitos dos desfechos; a suplente só entra depois de aceitar. A explicação da tela diz
  isso, e só isso.
