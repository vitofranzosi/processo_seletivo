# A detecção do giro do rosto — o que foi medido (176)

Registro da FR-8041 da `176`. Medido em 15/11/2026, na branch `claude/176-deteccao-do-giro-do-rosto`.

## O motor

| | |
|---|---|
| Pacote | `@mediapipe/tasks-vision` **0.10.35** (27/04/2026), Apache 2.0, sem alteração |
| Modelo | `face_landmarker.task`, float16, versão 1 (Apache 2.0); as expressões não são ligadas |
| Módulo + carregador + binário | 137 kB + 322 kB + 11,15 MB |
| Modelo | 3,76 MB |
| **Baixado, sem compressão** | **15,4 MB** (o `runserver` e o `nginx` do guia de hoje) — medido: 14,7 MiB de corpo |
| **Baixado, com gzip** | **cerca de 6,7 MB** (binário 3,27 MB; modelo 3,33 MB; scripts ~0,1 MB) |
| Com brotli, o binário | 2,27 MB |

O teto da SC-2755 é 7 MB com compressão e 19 MB sem ela. A compressão depende do `nginx` declarar
`gzip_types application/wasm application/octet-stream` — o guia de implantação não declara (A-2 da spec).

**Por que não a 1.x** (D-007, research T-013): a partir da 1.0.0 o módulo manda medidas de uso a
`odml.pa.googleapis.com`. A jornada no navegador o pegou pela violação da política de conteúdo. O
guardião `test_o_motor_nao_traz_registrador_de_uso` lê os bytes dos arquivos copiados.

## Tempo, no Chromium do computador

Chromium da suíte (Playwright), câmera simulada, Mac com Apple Silicon, servidor local; três rodadas
da bancada (`bancada/`), cada uma num navegador novo:

| Medida | Rodadas |
|---|---|
| Da câmera aberta ao motor pronto, **com o aquecimento** | 2 832, 2 799 e 2 816 ms |
| Leitura de um quadro, média | 19,8, 21,6 e 18,8 ms |
| Leitura de um quadro, pior | 71,1, 71,7 e 68,6 ms |

**O aquecimento.** Sem ele, a primeira leitura levava ~2,7 s (2 733, 2 673 e 2 690 ms) e as seguintes
~20 ms. O `Vigia` faz essa primeira leitura dentro do carregamento, para que ela não caia no meio de um
perfil nem conte no orçamento (teto de 120 ms, cinco vezes seguidas). As leituras de depois ficam a um
sexto do teto.

**O que ainda não foi medido** — e depende de aparelho e de pessoa:

- o celular de entrada (a SC-2753 pede a gravação sem perda de quadros perceptível, num celular
  de entrada, com e sem a detecção);
- o sinal do giro e o limiar com um rosto de verdade (SC-2757): a câmera do painel do app é bloqueada,
  e o Claude in Chrome não estava conectado em 15/11. O sinal está provado só pela geometria dos pontos
  (research T-005) e pela imagem de teste.

## Como conferir com câmera real

Na raiz do repositório:

```bash
python3 -m http.server 8178 --bind 127.0.0.1
```

Abra `http://localhost:8178/doc/deteccao-do-giro-2026-11/bancada/` no navegador (o `localhost` é contexto
seguro, e nada sai da máquina), toque em "Abrir a câmera e carregar o motor" e permita a câmera.

| Gesto | Esperado |
|---|---|
| de frente | giro perto de 0; lado "de frente" |
| virar para a **sua** esquerda | giro positivo, passando de 0,30; lado "esquerda" |
| virar para a **sua** direita | giro negativo, abaixo de −0,30; lado "direita" |

Se o sinal sair trocado, o defeito é da D-005 (o referencial do quadro), e não do limiar. Se o perfil
pedido pelo roteiro passar muito de 0,30, ou não chegar a ele, o limiar se ajusta em `deteccao.js`
(`LIMIAR_DO_GIRO`), e este registro ganha a medida.
