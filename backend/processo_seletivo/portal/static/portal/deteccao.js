/* A detecção do giro do rosto na gravação do vídeo da verificação (176).

   O que ela faz: no palco da página de gravação, estima no aparelho para onde o rosto aponta — se
   está dentro do oval, antes de começar; se virou para o lado pedido, nos dois perfis — e avisa a
   `gravacao.js`, que confirma na tela e passa ao passo seguinte pelo mesmo caminho do toque.

   O que ela nunca faz (FR-8000 a FR-8003): mandar ao servidor, guardar ou mostrar a alguém qualquer
   quadro, ponto, ângulo ou resultado; ler cor, luz, expressão, idade ou identidade; decidir nada. As
   leituras vivem na memória desta página, no máximo as últimas `LEITURAS_GUARDADAS`, e somem ao sair
   do palco. O motor só lê no preparo, no documento e nos dois perfis: no passo de frente ele não olha
   nada, porque não há o que guiar ali (minimização, research T-008). No documento ele só **conta**
   os rostos (emenda, FR-8060): a foto do documento é um rosto a mais, e nada além disso é lido — nem
   o documento, nem se ele é um, nem se a foto é da pessoa.

   Quando ela não está — sem a chave, sem WebAssembly, com economia de dados, motor que não carrega,
   aparelho lento, ou a pessoa que prefere tocar —, a página é a da 174, sem frase de falha (FR-8016).

   As funções puras ficam em `DeteccaoDoGiro`, para o teste de `tests/javascript/deteccao.test.js`; o
   `Vigia`, que fala com o motor, só roda no navegador. */

(function (raiz) {
  "use strict";

  // Os parâmetros da decisão, num lugar só (FR-8011, D-005). O giro é uma razão sem unidade (T-005):
  // perto de zero de frente, cerca de 0,25 a 20°, 0,37 a 30°, 0,64 a 45°. O limiar fica perto de 25°
  // — quem não alcança o perfil inteiro, que o roteiro pede, ainda avança —, e o instante impede que
  // um relance avance. Não são exigência de amplitude: quem não vira toca em "Próximo".
  var LIMIAR_DO_GIRO = 0.3;
  var INSTANTE_MANTIDO = 400;
  // Quanto "Perfil esquerdo visto" fica na tela antes de passar (UX-921).
  var CONFIRMACAO = 900;
  // O orçamento (FR-8017, T-008): uma leitura a cada 150 ms; se cinco seguidas passarem de 120 ms, a
  // detecção desliga até o fim da tomada.
  var INTERVALO = 150;
  var TETO_DA_LEITURA = 120;
  var LEITURAS_LENTAS = 5;
  var LEITURAS_GUARDADAS = 20;
  // O rosto que volta no documento precisa ter pelo menos esta fração da altura do rosto da pessoa
  // medido antes (revisão do #578): a foto do documento tapando o rosto também é "um rosto só".
  var PROPORCAO_DO_ROSTO_DE_VOLTA = 0.6;

  // Os pontos da malha do rosto que bastam para o giro: a ponta do nariz e as duas bordas do rosto,
  // na altura das maçãs (T-005).
  var NARIZ = 1;
  var BORDA_DIREITA_DA_PESSOA = 234;
  var BORDA_ESQUERDA_DA_PESSOA = 454;

  /* Para onde o rosto aponta: o afastamento do nariz do meio do rosto, dividido pela largura do
     rosto, em coordenadas do quadro **não espelhado** — o que o motor lê do `<video>`; o espelho da
     prévia é só CSS. Na câmera frontal, a esquerda de quem está diante dela fica à direita do quadro:
     **positivo é o rosto virado para a esquerda da pessoa** (D-005). `null` sem pontos. */
  function giroDosPontos(pontos) {
    if (!pontos || pontos.length <= BORDA_ESQUERDA_DA_PESSOA) return null;
    var nariz = pontos[NARIZ];
    var a = pontos[BORDA_DIREITA_DA_PESSOA];
    var b = pontos[BORDA_ESQUERDA_DA_PESSOA];
    var largura = Math.abs(b.x - a.x);
    if (!(largura > 0.01)) return null;
    return (nariz.x - (a.x + b.x) / 2) / largura;
  }

  // A caixa do rosto, normalizada ao quadro: do menor ao maior x e y dos pontos.
  function caixaDosPontos(pontos) {
    if (!pontos || !pontos.length) return null;
    var minX = 1, minY = 1, maxX = 0, maxY = 0;
    for (var i = 0; i < pontos.length; i += 1) {
      minX = Math.min(minX, pontos[i].x);
      maxX = Math.max(maxX, pontos[i].x);
      minY = Math.min(minY, pontos[i].y);
      maxY = Math.max(maxY, pontos[i].y);
    }
    return { x: minX, y: minY, largura: maxX - minX, altura: maxY - minY };
  }

  /* O rosto está no oval (FR-8010, T-006)? A caixa vai do quadro à tela pela regra do
     `object-fit: cover` da prévia (o quadro cresce até cobrir o palco, e o excesso sai pelos lados),
     espelhada como a prévia; o centro tem de cair dentro da elipse do oval, e a altura passar de
     35% da dele. `quadro` é `{largura, altura}` em pixels do vídeo; `palco` e `oval`, retângulos da
     tela (`{x, y, largura, altura}`). */
  function rostoNoOval(caixa, quadro, palco, oval, espelhada) {
    if (!caixa || !quadro || !quadro.largura || !quadro.altura || !palco || !oval) return false;
    var escala = Math.max(palco.largura / quadro.largura, palco.altura / quadro.altura);
    var largura = quadro.largura * escala;
    var altura = quadro.altura * escala;
    var origemX = palco.x + (palco.largura - largura) / 2;
    var origemY = palco.y + (palco.altura - altura) / 2;
    var cx = caixa.x + caixa.largura / 2;
    if (espelhada) cx = 1 - cx;
    var cy = caixa.y + caixa.altura / 2;
    var px = origemX + cx * largura;
    var py = origemY + cy * altura;
    var rx = oval.largura / 2;
    var ry = oval.altura / 2;
    if (!rx || !ry) return false;
    var dx = (px - (oval.x + rx)) / rx;
    var dy = (py - (oval.y + ry)) / ry;
    return dx * dx + dy * dy <= 1 && caixa.altura * altura >= 0.35 * oval.altura;
  }

  /* O giro pedido foi mantido? Sobre as leituras `{ms, giro}` em ordem de tempo, no desenho de
     `ouviuFala` da 174: a corrida mais recente além do limiar no lado pedido, se durar o instante, é
     "visto"; no lado oposto, "outro-lado" (FR-8015); leitura sem rosto (`giro: null`) interrompe a
     corrida. `lado` é "esquerda" ou "direita", da pessoa. Com `permitirOposto: false`, o lado oposto
     não é notícia: quem acabou de ter o perfil esquerdo visto ainda está virado para a esquerda
     quando o passo do direito começa, e "Para o outro lado" ali soaria como correção do que deu
     certo (achado da revisão do #573). O vigia só o permite depois de o rosto passar pela frente. */
  function avaliarGiro(leituras, lado, opcoes) {
    opcoes = opcoes || {};
    var permitirOposto = opcoes.permitirOposto !== false;
    var limiar = opcoes.limiar === undefined ? LIMIAR_DO_GIRO : opcoes.limiar;
    var mantido = opcoes.mantido === undefined ? INSTANTE_MANTIDO : opcoes.mantido;
    var sentido = lado === "esquerda" ? 1 : -1;
    function corrida(cabe) {
      return corridaMantida(leituras, cabe, mantido);
    }
    function noLado(leitura) {
      return leitura.giro !== null && leitura.giro !== undefined && leitura.giro * sentido >= limiar;
    }
    function noOposto(leitura) {
      return leitura.giro !== null && leitura.giro !== undefined && leitura.giro * sentido <= -limiar;
    }
    if (corrida(noLado)) return "visto";
    if (permitirOposto && corrida(noOposto)) return "outro-lado";
    return "esperando";
  }

  /* O passo do documento (emenda, FR-8061 a FR-8064, D-009). Uma sequência, e não uma contagem: o
     rosto da pessoa sozinho ("sozinha"), um segundo rosto mantido pelo instante ("na-mao" — a tela diz
     "Documento visto") e o rosto sozinho de novo, mantido ("visto" — o passo pode passar). Cada
     estado só anda para o seguinte, a partir de `anterior`, e as leituras são `{ms, rostos}`. Dois
     rostos desde o começo nunca chegam a "sozinha": quem está ao fundo desde o início não conta, e
     quem fica no quadro não deixa o passo terminar. */
  function avaliarDocumento(leituras, anterior, opcoes) {
    opcoes = opcoes || {};
    var mantido = opcoes.mantido === undefined ? INSTANTE_MANTIDO : opcoes.mantido;
    // A altura do rosto da pessoa, medida quando ela estava sozinha (`referencia`, de 0 a 1). Sem
    // ela, qualquer rosto sozinho vale, como antes.
    var referencia = Number(opcoes.referencia) || 0;
    function sozinho(leitura) {
      return leitura.rostos === 1;
    }
    function comDocumento(leitura) {
      return leitura.rostos >= 2;
    }
    // A volta é a do rosto da pessoa, e não a da foto do documento diante dele (revisão do #578):
    // a foto, mesmo perto da câmera, é menor que o rosto que o oval enquadrou.
    function rostoDeVolta(leitura) {
      if (!sozinho(leitura)) return false;
      return !referencia || (leitura.altura || 0) >= referencia * PROPORCAO_DO_ROSTO_DE_VOLTA;
    }
    var estado = anterior || "esperando";
    if (estado === "esperando") return corridaMantida(leituras, sozinho, mantido) ? "sozinha" : estado;
    if (estado === "sozinha") return corridaMantida(leituras, comDocumento, mantido) ? "na-mao" : estado;
    if (estado === "na-mao") return corridaMantida(leituras, rostoDeVolta, mantido) ? "visto" : estado;
    return estado;
  }

  // A corrida mais recente de leituras que `cabe` aceita dura pelo menos `mantido` ms?
  function corridaMantida(leituras, cabe, mantido) {
    var fim = leituras.length - 1;
    if (fim < 0 || !cabe(leituras[fim])) return false;
    var inicio = fim;
    while (inicio > 0 && cabe(leituras[inicio - 1])) inicio -= 1;
    return leituras[fim].ms - leituras[inicio].ms >= mantido;
  }

  // O orçamento da leitura (FR-8017): `registrar` devolve `false` a partir da quinta leitura lenta
  // seguida, e daí em diante, sempre — a detecção desligada não volta enquanto a página estiver aberta:
  // o vigia é um por página, e o aparelho lento numa tomada é lento na seguinte.
  function Orcamento(teto, limite) {
    this.teto = teto === undefined ? TETO_DA_LEITURA : teto;
    this.limite = limite === undefined ? LEITURAS_LENTAS : limite;
    this.lentas = 0;
    this.esgotado = false;
  }

  Orcamento.prototype.registrar = function (ms) {
    if (this.esgotado) return false;
    this.lentas = ms > this.teto ? this.lentas + 1 : 0;
    if (this.lentas >= this.limite) this.esgotado = true;
    return !this.esgotado;
  };

  // O motor pode ser baixado (FR-8016, FR-8018)? Não com a escolha de tocar, sem WebAssembly, ou com
  // o aparelho pedindo economia de dados.
  function podeCarregar(ambiente) {
    if (!ambiente || ambiente.recusada) return false;
    if (typeof ambiente.WebAssembly !== "object" || !ambiente.WebAssembly) return false;
    if (ambiente.conexao && ambiente.conexao.saveData) return false;
    return true;
  }

  /* O vigia: carrega o motor, lê a prévia quando lhe pedem, e conta o que viu.

     `opcoes`: `enderecos` ({motor, carregador, binario, modelo}), `video`, `oval` (o elemento),
     `espelhada`, `emGravacao` (uma função: a tomada está em curso?) e os retornos `aoEstado(estado)`,
     `aoRosto(dentro)` e `aoGiro(estado)`. Com `simulada` (uma função que devolve `{caixa, giro}`),
     não baixa motor nenhum: é a imagem de teste do desenvolvimento (FR-8040).

     **Uma instância por página.** Sair do palco pausa — o laço para e as leituras somem (FR-8003) —,
     mas o motor fica: recriá-lo a cada "Gravar de novo" recompilava 11 MB e repetia o aquecimento de
     segundos (achado da revisão do #573). `parar()` solta tudo, e é o que a escolha de tocar, o
     orçamento esgotado e a saída da página chamam. */
  function Vigia(opcoes) {
    this.opcoes = opcoes;
    this.motor = null;
    this.alvo = null;
    this.leituras = [];
    this.orcamento = new Orcamento();
    this.relogio = null;
    this.ultimoInstante = 0;
    this.parado = false;
    this.pronto = false;
    this.rosto = null;
    this.giro = null;
    this.passouPelaFrente = false;
    this.documento = null;
    this.alturaDoRosto = 0;
  }

  Vigia.prototype.estado = function (nome) {
    if (this.opcoes.aoEstado) this.opcoes.aoEstado(nome);
  };

  Vigia.prototype.gravando = function () {
    return Boolean(this.opcoes.emGravacao && this.opcoes.emGravacao());
  };

  /* O aquecimento: a primeira leitura custa segundos (a bancada mediu ~2,7 s no computador, contra
     ~20 ms das seguintes), na linha principal. Ele acontece antes de a detecção se dizer pronta, e
     nunca com a tomada em curso: ali ele congelaria o relógio e o toque em "Próximo" (achado da
     revisão do #573). Devolve "feito", "sem-quadro" (a primeira leitura de verdade o paga) ou
     "falhou" — e a falha aqui é a do delegado, que dá lugar ao seguinte. */
  Vigia.prototype.aquecer = function (motor) {
    var video = this.opcoes.video;
    if (!video || video.readyState < 2) return "sem-quadro";
    try {
      this.ultimoInstante = Math.max(performance.now(), this.ultimoInstante + 1);
      motor.detectForVideo(video, this.ultimoInstante);
      return "feito";
    } catch (erro) {
      return "falhou";
    }
  };

  Vigia.prototype.carregar = async function () {
    if (this.opcoes.simulada) {
      this.pronto = true;
      this.estado("simulada");
      this.agendar();
      return;
    }
    var ambiente = {
      WebAssembly: typeof WebAssembly === "undefined" ? null : WebAssembly,
      conexao: typeof navigator !== "undefined" ? navigator.connection : null,
    };
    if (!podeCarregar(ambiente)) {
      this.estado("indisponivel");
      return;
    }
    this.estado("carregando");
    var enderecos = this.opcoes.enderecos;
    var motor = null;
    var aquecido = false;
    try {
      var modulo = await import(enderecos.motor);
      // Sem SIMD, nada: a variante sem ele custaria 12,9 MB a mais, para aparelhos anteriores a 2023
      // (research T-001). O conjunto de arquivos é explícito, para o motor não escolher sozinho.
      if (!(await modulo.FilesetResolver.isSimdSupported())) throw new Error("sem SIMD");
      var arquivos = { wasmLoaderPath: enderecos.carregador, wasmBinaryPath: enderecos.binario };
      var delegados = ["GPU", "CPU"];
      for (var i = 0; i < delegados.length && !motor; i += 1) {
        try {
          motor = await modulo.FaceLandmarker.createFromOptions(arquivos, {
            baseOptions: { modelAssetPath: enderecos.modelo, delegate: delegados[i] },
            runningMode: "VIDEO",
            // Dois: para ficar com o maior nos perfis (o rosto de quem grava) e para contar a foto
            // do documento no primeiro passo (emenda, FR-8060). Nem expressões nem matriz: a
            // detecção lê só a direção do rosto e quantos há (FR-8001).
            numFaces: 2,
            outputFaceBlendshapes: false,
            outputFacialTransformationMatrixes: false,
          });
        } catch (erro) {
          motor = null;
          continue;
        }
        // O delegado que abre mas não lê (o GPU com WebGL que falha na inferência) dá lugar ao
        // seguinte, em vez de a página se dizer pronta com um motor que nunca vai funcionar.
        if (this.gravando()) break;
        var aquecimento = this.aquecer(motor);
        if (aquecimento === "falhou") {
          motor.close();
          motor = null;
        } else {
          aquecido = true;
        }
      }
    } catch (erro) {
      motor = null;
    }
    if (this.parado) {
      if (motor) motor.close();
      return;
    }
    if (!motor) {
      this.estado("indisponivel");
      return;
    }
    this.motor = motor;
    // Pronto com a tomada em curso: espera o próximo preparo para aquecer e começar a ler.
    if (aquecido) this.ficarPronto();
  };

  Vigia.prototype.ficarPronto = function () {
    this.pronto = true;
    this.estado("pronta");
    this.agendar();
  };

  // O que observar agora: "oval" no preparo, "esquerda" ou "direita" num perfil, "documento" no
  // primeiro passo, ou `null` (nada).
  // Cada pedido começa do zero: as leituras do passo anterior não contam para o seguinte.
  Vigia.prototype.observar = function (alvo) {
    this.alvo = alvo || null;
    this.leituras = [];
    // Começa esperando, sem avisar: só a mudança é notícia.
    this.giro = "esperando";
    this.rosto = null;
    this.passouPelaFrente = false;
    this.documento = "esperando";
    this.alturaDoRosto = 0;
    // O motor que chegou com a tomada em curso aquece no primeiro pedido fora dela.
    if (this.motor && !this.pronto && !this.parado && !this.gravando()) {
      if (this.aquecer(this.motor) === "falhou") {
        this.desligar("indisponivel");
        return;
      }
      this.ficarPronto();
      return;
    }
    this.agendar();
  };

  Vigia.prototype.agendar = function () {
    var vigia = this;
    if (this.relogio || this.parado || !this.pronto || !this.alvo) return;
    this.relogio = setTimeout(function () {
      vigia.relogio = null;
      vigia.ler();
      vigia.agendar();
    }, INTERVALO);
  };

  Vigia.prototype.lerQuadro = function () {
    if (this.opcoes.simulada) return this.opcoes.simulada();
    var video = this.opcoes.video;
    if (!this.motor || !video || video.readyState < 2) return null;
    var agora = performance.now();
    // O motor exige instantes crescentes.
    var instante = Math.max(agora, this.ultimoInstante + 1);
    this.ultimoInstante = instante;
    var resultado;
    try {
      resultado = this.motor.detectForVideo(video, instante);
    } catch (erro) {
      // Sem isto a exceção subia do temporizador, o laço morria e a página continuava dizendo que
      // a tela avança sozinha (achado da revisão do #573). Desligada, ela volta a ser a da 174.
      this.desligar("desligada");
      return null;
    }
    if (!this.orcamento.registrar(performance.now() - agora)) {
      this.desligar("desligada");
      return null;
    }
    var rostos = (resultado && resultado.faceLandmarks) || [];
    var maior = null;
    var area = 0;
    for (var i = 0; i < rostos.length; i += 1) {
      var caixa = caixaDosPontos(rostos[i]);
      if (caixa && caixa.largura * caixa.altura > area) {
        area = caixa.largura * caixa.altura;
        maior = { caixa: caixa, giro: giroDosPontos(rostos[i]) };
      }
    }
    // Quantos rostos, até os dois que o motor procura: o documento é contado, e não lido (FR-8060).
    if (!maior) return { caixa: null, giro: null, rostos: 0 };
    maior.rostos = rostos.length;
    return maior;
  };

  Vigia.prototype.ler = function () {
    if (this.parado || !this.alvo) return;
    if (typeof document !== "undefined" && document.hidden) return;
    var leitura = this.lerQuadro();
    if (!leitura || this.parado || !this.alvo) return;
    if (this.alvo === "oval") {
      var video = this.opcoes.video;
      var oval = this.opcoes.oval;
      var dentro = rostoNoOval(
        leitura.caixa,
        { largura: video.videoWidth, altura: video.videoHeight },
        retangulo(video),
        retangulo(oval),
        this.opcoes.espelhada
      );
      if (dentro !== this.rosto) {
        this.rosto = dentro;
        if (this.opcoes.aoRosto) this.opcoes.aoRosto(dentro);
      }
      return;
    }
    if (this.alvo === "documento") {
      var altura = leitura.caixa ? leitura.caixa.altura : 0;
      this.leituras.push({ ms: performance.now(), rostos: leitura.rostos || 0, altura: altura });
      if (this.leituras.length > LEITURAS_GUARDADAS) this.leituras.shift();
      var documento = avaliarDocumento(this.leituras, this.documento, {
        referencia: this.alturaDoRosto,
      });
      if (documento !== this.documento) {
        this.documento = documento;
        // Sozinha, a altura do rosto da pessoa é a referência da volta (revisão do #578).
        if (documento === "sozinha") this.alturaDoRosto = altura;
        // Visto, o vigia para de olhar: o passo vai mudar. Só "na-mao" e "visto" são notícia.
        if (documento === "visto") this.alvo = null;
        if ((documento === "na-mao" || documento === "visto") && this.opcoes.aoGiro) {
          this.opcoes.aoGiro(documento);
        }
      }
      return;
    }
    if (leitura.giro !== null && Math.abs(leitura.giro) < LIMIAR_DO_GIRO) this.passouPelaFrente = true;
    this.leituras.push({ ms: performance.now(), giro: leitura.giro });
    if (this.leituras.length > LEITURAS_GUARDADAS) this.leituras.shift();
    var giro = avaliarGiro(this.leituras, this.alvo, { permitirOposto: this.passouPelaFrente });
    if (giro !== this.giro) {
      this.giro = giro;
      // Visto, o vigia para de olhar até o próximo pedido: o passo vai mudar.
      if (giro === "visto") this.alvo = null;
      if (this.opcoes.aoGiro) this.opcoes.aoGiro(giro);
    }
  };

  function retangulo(elemento) {
    var r = elemento.getBoundingClientRect();
    return { x: r.left, y: r.top, largura: r.width, altura: r.height };
  }

  // Fora do palco: o laço para e as leituras somem (FR-8003); o motor fica para a próxima tomada.
  Vigia.prototype.pausar = function () {
    this.alvo = null;
    this.leituras = [];
    this.rosto = null;
    this.giro = null;
    this.documento = null;
    clearTimeout(this.relogio);
    this.relogio = null;
  };

  // Para e solta tudo: o laço, as leituras e o motor.
  Vigia.prototype.parar = function () {
    this.parado = true;
    this.pausar();
    if (this.motor) this.motor.close();
    this.motor = null;
  };

  Vigia.prototype.desligar = function (motivo) {
    this.parar();
    this.estado(motivo);
  };

  var api = {
    LIMIAR_DO_GIRO: LIMIAR_DO_GIRO,
    INSTANTE_MANTIDO: INSTANTE_MANTIDO,
    CONFIRMACAO: CONFIRMACAO,
    INTERVALO: INTERVALO,
    TETO_DA_LEITURA: TETO_DA_LEITURA,
    LEITURAS_LENTAS: LEITURAS_LENTAS,
    giroDosPontos: giroDosPontos,
    caixaDosPontos: caixaDosPontos,
    rostoNoOval: rostoNoOval,
    avaliarGiro: avaliarGiro,
    avaliarDocumento: avaliarDocumento,
    Orcamento: Orcamento,
    podeCarregar: podeCarregar,
    Vigia: Vigia,
  };
  raiz.DeteccaoDoGiro = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
