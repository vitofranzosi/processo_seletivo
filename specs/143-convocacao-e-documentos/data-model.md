# Data Model: 143

Nenhum modelo, tabela ou coluna. Duas leituras, nunca gravadas:

## Passo da chamada

| Campo | O que é |
|---|---|
| `codigo` | `DESFECHADA`, `SEM_COMUNICACAO`, `VENCIDA`, `REENVIADO`, `A_CONFERIR`, `PENDENCIA`, `AGUARDANDO_DOCUMENTOS`, `PRONTA`, `AGUARDANDO_RESPOSTA` |
| `frase` | o que falta, para quem conduz |
| `tom` | a classe visual (`passo-acao`, `passo-espera`, `passo-feito`, `passo-alerta`) |
| `acao` | `conferir`, `desfecho`, `emitir` ou vazio — a ação rotineira, oferecida só a quem pode |

Precedência: desfecho → sem comunicação → vencimento decorrido → reenviado → a conferir → pendência
→ aguardando documentos → pronta → aguardando a resposta.

## Situação do aviso de pendência

| Campo | O que é |
|---|---|
| `pendencia_em` | `conferido_em` mais recente das conferências vigentes pendentes |
| `reenviado_em` | `apresentado_em` mais recente das versões vigentes complementadas |
| `aviso_em`, `estado`, `rotulo` | o destinatário de aviso mais recente da chamada **depois** da pendência, e o estado derivado (`066`) |
| `alcancavel` | se o gesto do aviso a alcançaria agora (prévia da `134`) |
| `motivo` | por que não alcançaria, com as palavras da `134` |
