# Verificação da 150 — incremento 1 (MVP e US2)

12/11/2026. Escopo: Setup, Foundational, US1 e US2 (T001–T025). US3, US4 e US5 ficam para depois.

## No navegador

Banco `ps_demo_150`, novo (migrate, `semear_unidades`, autoridade da suíte), com o cenário de
treinamento **C11** (`carregar_cenarios_de_treinamento --cenario C11`): Edital `SIM11/2026`,
convocado fictício 01, dois documentos obrigatórios a enviar. Todos os dados são de treinamento
(*"TREINAMENTO — DADO FICTÍCIO, SEM VALOR LEGAL"*). Os arquivos escolhidos foram montados no próprio
navegador (`DataTransfer`), com conteúdo sintético: o painel não preenche `input type=file`.

| # | O que se fez | O que a tela mostrou | Captura |
|---|---|---|---|
| 1 | Escolher os dois arquivos | Os dois botões passam a "Enviar os 2 documentos escolhidos", os dois com o destaque; a região viva diz "2 documentos escolhidos para enviar." | `capturas/01-dois-escolhidos.jpg` |
| 2 | Diploma como imagem JPEG, comprovante em PDF; enviar pelo cartão do comprovante | "Enviando 1 de 2: Diploma de graduação… Não feche esta página."; a volta é `?lote=2#confirmacao`: "Recebemos 1 de 2 documentos.", o comprovante com data e hora, "1 documento não foi recebido:" com link ao diploma; no cartão do diploma, a recusa de hoje sobre foto e PDF | `capturas/02-um-recusado-no-meio.jpg` |
| 3 | Dois PDFs escolhidos; o segundo pedido derrubado como falha de rede (`fetch` substituído no console) | A página fica. No cartão acionado: "Não foi possível enviar: a conexão falhou… Recebemos: Diploma de graduação. Comprovante de residência: não é possível saber se chegou — a conexão caiu durante o envio. Recarregue a página para conferir, ou envie de novo…"; o diploma diz "Recebido agora."; o comprovante continua escolhido | — (texto acima) |
| 4 | A 375 px, dois "Enviar outro arquivo" escolhidos | O rótulo longo cabe no cartão; `scrollWidth` = 375, sem rolagem horizontal | `capturas/03-rotulo-a-375px.jpg` |
| 5 | Enviar os dois "Enviar outro arquivo" | "Recebemos 2 de 2 documentos. Os arquivos aguardam a conferência da comissão.", cada um com data e hora, e a conclusão de hoje; o foco na confirmação | `capturas/04-dois-de-dois.jpg` |

Console sem erro e sem violação da política de conteúdo.

**Dois defeitos achados aqui, e corrigidos antes do commit final:**

- Na primeira tentativa, os dois documentos chegaram ao servidor **sem arquivo** e voltaram com
  "Escolha um arquivo PDF antes de enviar.": o script desabilitava os campos antes de montar o
  `new FormData(formulario)`, e o navegador deixa campo desabilitado fora do `FormData`. O corpo
  passou a ser montado à mão, e o teste em `node` passou a imitar o navegador nisso.
- No cenário 3, a confirmação da volta anterior continuava no topo ("1 documento não foi recebido:
  Diploma") e a recusa antiga continuava no cartão do diploma que acabara de chegar. O lote agora
  esconde a confirmação anterior ao começar, e o cartão recebido perde a recusa antiga.

## Testes

- `node --test tests/javascript/varios.test.js`: 13 casos (contagem, rótulo, lote em ordem e um por
  vez, arquivo acima do limite, recusa no meio, página de acesso, 404, 500, queda de conexão,
  volta pelo cache).
- `tests/interface/test_portal_documentos_da_convocacao.py`: o ramo JSON, a sessão do lote, a
  marcação, a volta com recebidos e recusados; o envio sem cabeçalho continua o de hoje.
- `tests/integration/portal/test_envio_de_varios.py`: quatro no lote são quatro apresentações e
  quatro eventos de trilha, iguais ao envio de um; prazo vencido e resultado registrado no meio.
- `tests/unit/portal/test_obrigacoes_da_convocacao.py`: `confirmacao_do_lote`.
- A contagem de consultas da convocação (`test_portal_jornada_consolidada.py`) não mudou.

## O que não foi verificado

- Leitor de tela real (SC-1804) e a sessão com pessoas (SC-1805).
- A jornada automatizada no navegador (T035), que é do polimento.
