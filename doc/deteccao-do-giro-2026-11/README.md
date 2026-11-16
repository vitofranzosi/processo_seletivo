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

## O sinal do gesto (emenda de 15/11)

Capturas da jornada no navegador (câmera simulada do Chromium e imagem de teste), em `capturas/`: o
documento e o perfil esquerdo a 375 px, o perfil esquerdo a 1280 px e o perfil visto a 375 px. O oval
sai durante a gravação; a frase do roteiro fica inteira, em tamanho de leitura, nos passos de gesto.

## O documento, a frase de frente e o microfone (emenda de 15/11, à noite)

Depois do teste do usuário com câmera real no Safari do macOS, no C19 (FR-8060 a FR-8085, D-009 a
D-011). Capturas em `capturas/`:

- `375-documento-visto.png` — a imagem de teste mostra o "documento" (o cartão com um vulto pequeno)
  ao lado do rosto; a tela diz "Documento visto" no lugar do sinal, e passa ao perfil esquerdo quando
  o cartão sai. Sem modelo novo: o motor já procurava dois rostos.
- `375-de-frente.png` e `1280-de-frente.png` — no passo de frente, o alto tem só "Passo 4 de 4 · De
  frente"; a frase do roteiro, inteira, fica embaixo, com as frases entre aspas em destaque. No palco
  deitado ela fica ao lado do botão. Medido no navegador: a 375 × 667 a faixa de cima ocupa 134 px
  (20%; antes, a frase de 250 caracteres ocupava cerca de metade e a faixa cortava o fim), a frase
  ocupa 162 px a partir de 59% da altura, sem rolagem; a 1280 × 800 ela começa a 70% da altura do
  palco.
- `375-preparo-microfone.png` — a barra do microfone, em decibéis, com a marca de "volume bom".

**O medidor.** O tom da imagem de teste (ganho 0,05, pico de −26 dB) enchia 12% do `<meter>` de
antes; na barra nova ele enche 52%, abaixo da marca (62%), e a frase continua pedindo "Fale alguma
coisa" — a régua de "Estamos ouvindo você" é a mesma da `174`, e a marca é ela desenhada. A fala em voz
normal, com pico entre −20 e −10 dB, enche de 67% a 90%. O pico em bytes da escala de antes parava em
1/128 (−42 dB); a leitura passou a ponto flutuante onde o navegador oferece.

**A medir com câmera real** (SC-2757, SC-2764, humano): o documento de verdade perto da câmera — o
motor encontra a foto como segundo rosto? a que distância? — e a barra no Safari, com a voz.

