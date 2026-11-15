# Research: A detecção do giro do rosto

Decisões técnicas da `176`, de `T-001` a `T-012`. Conferidas no pacote em 15/11/2026.

## T-001 — O motor: `@mediapipe/tasks-vision` 1.2.0, Face Landmarker

- **Decisão**: a versão **1.2.0** (publicada em 27/10/2026), e não a 1.2.3 (11/11): a regra da casa
  para dependência nova é versão com pelo menos duas semanas. Licença Apache 2.0. Do pacote entram
  três arquivos — `vision_bundle.mjs` (o módulo, 156 kB), `wasm/vision_wasm_internal.js` (o carregador,
  334 kB) e `wasm/vision_wasm_internal.wasm` (14,5 MB, cerca de 2,8 MB em brotli e 4,1 MB em gzip) —
  e a licença. O modelo é o `face_landmarker.task`, float16, versão 1 (3,76 MB), Apache 2.0.
- **Por quê**: a Q-4 (D-006). Os pontos do rosto acompanham até perto do perfil, e o giro sai deles
  sem treinar nada.
- **Sem rede**: o módulo e o carregador não têm endereço de outra origem nem `sendBeacon`, e a
  política de conteúdo (`connect-src 'self'`) recusaria de todo modo. Nenhum `eval(` nem `new
  Function` no módulo nem no carregador — o guardião da `092` (`test_nenhum_script_escreve_estilo_que_
  a_politica_recusaria`) passa a lê-los, e passa.
- **Descartado**: a variante sem SIMD (12,9 MB a mais no repositório) — o Safari tem SIMD desde a 16.4
  (2023), e o aparelho sem ele cai no toque (FR-8016); a variante `module` (duplicata); a 1.2.3, nova
  demais; TensorFlow.js (em manutenção, e o mesmo peso de modelo); a API `FaceDetector` do navegador
  (não existe no Safari).

## T-002 — Onde moram os arquivos, e como se conferem

- **Decisão**: `portal/static/portal/deteccao/tasks-vision-1.2.0/` com os três arquivos do pacote,
  **sem nenhuma alteração** (o resumo bate com o do pacote publicado), e o `LICENSE`; o modelo em
  `portal/static/portal/deteccao/face_landmarker-float16-1.task`. O manifesto — versão, caminho e
  SHA-256 de cada arquivo — mora em `processo_seletivo/portal/deteccao.py`, e um teste confere cada
  resumo (FR-8023).
- **Por quê**: servidos pelo `nginx` da implantação como o resto de `/static/portal/`, com o cache
  longo que o `?v=` dá (`doc/implantacao-em-producao-ubuntu.md`, `map $arg_v`). A versão no nome da
  pasta e o `?v=` do conteúdo nos endereços fazem o navegador baixar uma vez por versão (FR-8016).
- **O peso no repositório**: cerca de 18 MB num repositório de 560 MB. Baixar na implantação,
  conferindo o resumo, seria o caminho do tokenizer da `071`; aqui o arquivo é servido ao navegador e
  precisa estar no mesmo lugar em todo ambiente, e um passo a mais na implantação só trocaria o peso
  por uma falha possível.
- **O mapa de fonte**: o módulo termina citando `vision_bundle_mjs.js.map`, que não vem. O navegador só
  o pede com as ferramentas de desenvolvimento abertas; tirar a linha mudaria o resumo do arquivo.

## T-003 — Como o motor é carregado

- **Decisão**: `deteccao.js` (script clássico, do sistema) chama `import()` do módulo pelo endereço
  com `?v=`, e entrega ao `FaceLandmarker.createFromOptions` o conjunto de arquivos **explícito**
  (`wasmLoaderPath`, `wasmBinaryPath`), e não o `FilesetResolver.forVisionTasks`, que escolheria a
  variante sem SIMD por conta própria. Antes, `FilesetResolver.isSimdSupported()`; sem SIMD, nada.
  `runningMode: "VIDEO"`, `numFaces: 1`, delegado `GPU` e, se a criação falhar, `CPU`.
- **Quando**: depois que a câmera abriu e o palco apareceu (FR-8016), num `setTimeout(0)`, para não
  disputar o primeiro quadro; nunca com `navigator.connection.saveData` (FR-8018), sem `WebAssembly`
  ou com a escolha "Prefiro avançar só tocando".
- **O carregador**: o módulo injeta um `<script src>` da própria origem com o carregador — permitido por
  `script-src 'self'` — e o carregador compila o WebAssembly, que pede `'wasm-unsafe-eval'` (T-004).
  O tipo `application/wasm` já sai do `mimetypes` do Python 3.13 no `runserver` e do `mime.types` do
  `nginx`.

## T-004 — A política de conteúdo: `'wasm-unsafe-eval'`, só na gravação e só com a chave

- **Decisão**: `com_midia_local(resposta, compilar_wasm=False)`; com `True`, `script-src 'self'
  'wasm-unsafe-eval'`. A view da gravação passa `True` só com a chave da detecção ligada (FR-8022).
- **Por quê**: `'wasm-unsafe-eval'` libera a compilação de WebAssembly e nada mais — `eval` e `new
  Function` continuam recusados. Chrome 97, Firefox 102 e Safari 16 a aceitam. Navegador que não a
  conhece recusa a compilação, e cai no toque (FR-8016).
- **Descartado**: `'unsafe-eval'` (abriria `eval`); a diretiva na política comum (abriria a compilação
  em todas as páginas, sem motivo).

## T-005 — O giro, a partir dos pontos

- **Decisão**: `giroDosPontos(pontos)` = (x do nariz − meio do rosto) ÷ largura do rosto, com o nariz no
  ponto 1 e as bordas do rosto nos pontos 234 e 454 da malha, em coordenadas do quadro **não
  espelhado** (é o que o motor lê do `<video>`; o espelho é só CSS). Positivo = o rosto virou para a
  **esquerda da pessoa**: na câmera frontal, a esquerda de quem está diante dela fica à direita do
  quadro (D-005 da spec). Frente dá perto de zero; pela geometria, o valor cresce com a tangente do
  ângulo (cerca de 0,25 a 20°, 0,37 a 30°, 0,64 a 45°).
- **Limiar**: `0,3` (cerca de 25°), mantido por **400 ms** (FR-8011), em `LIMIAR_DO_GIRO` e
  `INSTANTE_MANTIDO`, juntos, no topo de `deteccao.js`. Ajustáveis na verificação com câmera real, e
  registrados no `doc/` (FR-8041).
- **Descartado**: a matriz de transformação facial (`outputFacialTransformationMatrixes`) — dá o ângulo
  em graus, mas o sinal depende da convenção da matriz, e a razão dos pontos é verificável à mão e no
  teste; e o detector leve (D-006).

## T-006 — O rosto no oval

- **Decisão**: `rostoNoOval(caixa, quadro, palco, oval)`: a caixa do rosto (mínimo e máximo dos pontos),
  levada do quadro ao palco pela regra do `object-fit: cover` da prévia, espelhada como a prévia, tem
  o centro dentro da elipse do oval (medida pelo `getBoundingClientRect` do `.oval`) e altura de pelo
  menos 35% da do oval. Só antes de começar (FR-8010).

## T-007 — A decisão, como função pura

- **Decisão**: `avaliarGiro(leituras, lado, opcoes)` → `"esperando" | "outro-lado" | "visto"`, sobre as
  leituras `{ms, giro}` em ordem de tempo, no mesmo desenho de `ouviuFala` da `174`: a corrida mais
  recente no lado pedido além do limiar, se durar o instante, é `visto`; no lado oposto, `outro-lado`;
  leitura sem rosto (`giro: null`) interrompe a corrida. Testada em `tests/javascript/deteccao.test.js`.
- **A confirmação**: percebido o giro, a instrução mostra "Perfil esquerdo visto" por **900 ms**
  (`CONFIRMACAO`) e então chama o mesmo `avancar()` do toque, que já ignora o segundo avanço a menos de
  500 ms (FR-8014). O toque durante a confirmação avança na hora e cancela a espera.

## T-008 — O orçamento

- **Decisão**: uma leitura a cada **150 ms** (cerca de 6,7 por segundo), por `setTimeout` encadeado, só
  enquanto o palco está aberto, a página está visível e o passo é o preparo ou um perfil — no documento
  e no passo de frente o motor não lê nada (minimização, FR-8001). Se a leitura passar de **120 ms**
  cinco vezes seguidas, a detecção desliga até o fim da tomada (FR-8017), por `Orcamento`, função pura
  testada.
- **Por quê a gravação não sofre**: o `MediaRecorder` codifica fora da linha principal; a leitura roda
  na linha principal, e o teto de 120 ms a cada 150 ms deixa folga para os relógios da página. A
  imagem de teste, que é desenhada na linha principal, não usa o motor (T-010).

## T-009 — A chave: `VERIFICACAO_DETECCAO_DO_GIRO`

- **Decisão**: em `base.py`, do ambiente, desligada por padrão; vale só com `VERIFICACAO_POR_VIDEO`
  (FR-8020); `production.py` recusa subir com ela (FR-8021), com a mensagem que nomeia a P-0 e a
  P-13; `test.py` a deixa **desligada**, para que os testes da `166` e da `174` continuem a medir a
  página de hoje, e os da `176` a ligam por `settings`. A entrada da `.claude/launch.json` do vídeo
  ganha a variável.

## T-010 — A imagem de teste gira, e a detecção simulada lê o giro desenhado

- **Decisão**: a imagem de teste (`fonteSintetica`) passa a seguir um ciclo previsível — de frente,
  esquerda, de frente, direita —, desenha um nariz no vulto para mostrar o lado, e expõe o giro
  desenhado. Com ela, `deteccao.js` usa a **detecção simulada**, que devolve esse giro como se fosse
  o dos pontos, e não baixa o motor (FR-8040). Só no desenvolvimento, como a imagem de teste.
- **A jornada no navegador**: o Chromium da suíte com a câmera simulada (`test_jornada_do_video.py`) não
  mostra rosto; ele prova o carregamento do motor de verdade (sem violação da política, sem pedido a
  outra origem, `data-deteccao="pronta"`) e o caminho do toque quando não há rosto. O avanço sozinho
  se prova com a imagem de teste e `DEBUG` ligado na sessão.

## T-011 — O guardião

- **Decisão**: `test_sem_inferencia_sobre_o_video.py` continua recusando visão computacional no
  servidor e ganha três casos: (a) os arquivos do motor são só os do manifesto, com os resumos dele;
  (b) nenhum outro arquivo estático cita o motor (`tasks-vision`, `FaceLandmarker`, `mediapipe`);
  (c) nenhum template além de `portal/verificacao.html` carrega `deteccao.js` ou o motor (FR-8024).

## T-012 — O que não sai do aparelho, provado

- **Decisão**: (a) o corpo do `POST` de início do envio, gravado com e sem a detecção, tem as mesmas
  chaves e marcas (SC-2752), na jornada no navegador; (b) nenhuma rota recebe campo de detecção — o
  `iniciar` ignora o que não conhece, e um teste garante que a página não manda nada além do contrato
  da `166`; (c) a jornada conta os pedidos de rede e só admite os do motor, uma vez (SC-2754).
- **A compressão em produção**: o `nginx` do guia de implantação não declara `gzip_types`, e o padrão
  dele comprime só HTML; o navegador baixaria 14,5 MB em vez de 4,1. O `runserver` também não comprime:
  no desenvolvimento, o peso medido é o sem compressão. Fica como registro para a porta do
  piloto (FR-8042), porque a implantação não liga a chave.
