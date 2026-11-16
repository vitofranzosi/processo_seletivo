# Achado — a foto do documento não é percebida com câmera real (T041 da `176`)

Encontrado em 16/11/2026, pelo usuário, na primeira passada da T041 da `176`: câmera real, documento
de verdade, cenário C19 num banco local (`ps_demo_video`), sobre a `main` em `619a4ae0`, com
`VERIFICACAO_POR_VIDEO` e `VERIFICACAO_DETECCAO_DO_GIRO` ligadas.

> **Não vira escopo por estar escrito aqui.** O que se registra é o resultado da T041, o que ele
> exclui e o que fica por medir. Decidir o que fazer com o passo do documento é do usuário.

## O que se observou

- **Os dois perfis avançaram sozinhos.** O motor carregou, aqueceu e leu o rosto da pessoa: a
  detecção do giro funciona na mesma página, na mesma tomada.
- **O passo do documento nunca avançou, e "Documento visto" nunca apareceu.** A pessoa mostrou o
  documento e o passo só seguiu pelo toque em "Próximo".

Pela sequência da D-009 — o rosto sozinho, dois rostos, o rosto sozinho de novo —, "Documento visto"
é o estado `na-mao`, o do segundo rosto mantido pelo instante (`avaliarDocumento`, em
`portal/static/portal/deteccao.js`). Ele não ter aparecido diz que o motor **nunca contou dois
rostos**. A revisão do #578, que exige a volta de um rosto com 0,6 da altura do da pessoa
(FR-8062), não chegou a entrar em jogo: ela só decide a terceira etapa.

## O que a observação exclui

- **A chave desligada.** Na primeira tentativa do mesmo dia o servidor subiu sem
  `VERIFICACAO_DETECCAO_DO_GIRO`, e nem o giro funcionou. Com ela ligada, a página passou a trazer o
  motor e `'wasm-unsafe-eval'` na política de conteúdo, e o giro passou a avançar. A observação acima
  é a da segunda tentativa.
- **O passo sem marca.** O `<li>` do passo `documento` recebe `data-documento` sempre que a detecção
  está ligada (`portal/templates/portal/verificacao.html`), e a `gravacao.js` pede ao vigia
  `observar("documento")` nesse passo.
- **O motor que não carrega ou que se desliga pelo orçamento.** O mesmo vigia, com o mesmo motor,
  leu os perfis na mesma tomada; o orçamento esgotado desligaria a detecção inteira até o fim da
  página.

## A causa provável — não medida

O motor é o `FaceLandmarker` do MediaPipe (`tasks-vision` 0.10.35, `face_landmarker-float16-1.task`),
com `numFaces: 2` e a confiança mínima de detecção no padrão. O detector que vem nesse pacote é feito
para o rosto perto da câmera, e procura numa imagem reduzida. A foto 3×4 de um RG ou de uma CNH,
segurada ao lado do rosto, ocupa uma fração pequena do quadro de 1280×720 que a `gravacao.js` pede, e
pode sumir na redução. É o caso que a spec já previa como limite ("foto pequena demais para o motor:
nada é percebido; o toque resolve"), e a T041 sugere que ele não é a exceção, e sim o caso comum.

**Isso não foi medido.** Falta saber a que distância e com que tamanho de foto o motor passa a contar
o segundo rosto, se é que passa.

## O que fica por medir

1. **A distância.** Com o documento cada vez mais perto da câmera, ao lado do rosto e sem cobri-lo:
   em algum ponto o motor conta dois rostos? Um contador de rostos visível só no desenvolvimento, atrás
   de `DEBUG`, responderia sem gravar nada.
2. **A confiança mínima.** Baixar `minFaceDetectionConfidence` muda o resultado, e a que custo em
   falsos segundos rostos?
3. **Outro aparelho.** A T041 pede também o Safari e um celular; a câmera frontal do celular, mais
   perto, pode dar outro resultado.

## O que está em aberto para decidir

Se a medição confirmar que o motor atual não percebe a foto na distância de uso, as saídas mudam o
produto, e cada uma é emenda da `176`:

- **Um detector para rostos pequenos**, ao lado do atual ou no lugar dele: aumenta o download da
  página e entra na leitura da P-13 (LGPD).
- **O passo do documento só pelo toque**, como antes da emenda do #578: a D-009 é revista.

**A página promete hoje o que a T041 não confirmou.** Antes de gravar, o candidato lê "A tela percebe
quando você mostra o documento e quando vira o rosto, para passar sozinha aos passos seguintes", e
durante a gravação "No documento e nos dois perfis, a tela passa sozinha"
(`portal/templates/portal/verificacao.html`). O caminho continua inteiro — "Próximo" resolve o passo
do documento, como a spec previu —, mas quem espera a tela passar fica parado diante dela até
perceber que precisa tocar. Qualquer das duas saídas revê essas frases.
