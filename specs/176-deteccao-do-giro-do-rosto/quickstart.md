# Quickstart: validar a detecção do giro do rosto

Roteiro de verificação da `176`. A forma da página está em [contracts/pagina.md](contracts/pagina.md);
as decisões técnicas, em [research.md](research.md).

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado e um `DB_NAME` próprio (*As armadilhas caras*, no `CLAUDE.md`).
  Nenhuma migration nova.
- `uv sync --extra dev --extra navegador` e `uv run playwright install chromium`, para a jornada.

## 1. As funções puras

```bash
cd backend && node --test tests/javascript/deteccao.test.js tests/javascript/gravacao.test.js
```

Esperado: o giro sai positivo à esquerda da pessoa e negativo à direita; um relance não conta; o lado
oposto dá "outro-lado"; o orçamento desliga depois de cinco leituras lentas; e os testes da `174`
passam sem mudança.

## 2. O manifesto, a chave, a política e o guardião

```bash
cd backend && DB_NAME=ps_176 make test-pg PYTEST_ADDOPTS="tests/portal tests/test_sem_inferencia_sobre_o_video.py tests/interface/test_politica_de_conteudo.py tests/test_armazenamento_no_navegador.py tests/integration/verificacao tests/contract"
```

Esperado: cada arquivo do motor tem o resumo do manifesto; com a chave desligada, a página e a política
são as da `174`, diretiva a diretiva; com ela ligada, só `'wasm-unsafe-eval'` a mais; nenhum outro
template ou estático cita o motor; a produção recusa a chave; os testes de envio da `166` passam sem
mudança.

## 3. A jornada no navegador

```bash
cd backend && DB_NAME=ps_176 make test-pg PYTEST_ADDOPTS="tests/navegador/test_jornada_do_video.py"
```

| Caso | Critério |
|---|---|
| motor de verdade, câmera simulada do Chromium | `data-deteccao="pronta"`, nenhuma violação da política, nenhum pedido a outra origem; sem rosto, os perfis avançam pelo toque (SC-2751, SC-2754, SC-2756) |
| imagem de teste, detecção simulada | os dois perfis avançam sem toque: "Próximo" no documento e "Terminar a gravação" são os únicos toques (SC-2750); o corpo do envio tem as mesmas chaves que o gravado pelo toque (SC-2752) |
| "Prefiro avançar só tocando" | o aviso some, `data-deteccao="recusada"`, nenhum avanço sozinho |

## 4. À mão, no navegador do desenvolvimento

1. Suba a entrada `verificacao-176` da `.claude/launch.json` (porta 8177, com `VERIFICACAO_POR_VIDEO` e
   `VERIFICACAO_DETECCAO_DO_GIRO` ligadas) e entre como a candidata do C18.
2. A 375 e a 1280 px, com a imagem de teste: o aviso no topo do preparo, sem rolar; o vulto gira; os
   perfis avançam sozinhos com "Perfil esquerdo visto" e "Perfil direito visto".
3. Com câmera real, no computador: o oval muda para "Rosto no oval"; virar para a **sua** esquerda no
   passo 2 avança; virar para a direita no passo 2 diz "Para o outro lado". Anote no `doc/` o tempo até
   `pronta`, o tempo médio por leitura e o peso baixado (painel de rede).
4. Num celular real (contexto seguro: `adb reverse` no Android; mkcert e um proxy TLS no iPhone, como
   na T-016 da `174`): os dois perfis sem toque (SC-2757), e a gravação inteira pelo toque, sem virar
   o rosto, sem nenhuma frase de erro (SC-2758).
