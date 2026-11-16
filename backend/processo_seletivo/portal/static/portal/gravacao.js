/* A gravação guiada do vídeo da verificação da autodeclaração (166, US2; prova de conceito de 13/11).

   O que a página faz no aparelho: abre a câmera (ou a imagem de teste, no desenvolvimento), grava
   numa tomada contínua seguindo o roteiro, mostra a tomada para revisão e a envia em partes de até
   8 MiB, retomando de onde parou, com o resumo SHA-256 do arquivo inteiro.

   O que ela nunca faz: enviar uma tomada que a pessoa não escolheu enviar (R-15), emendar tomadas
   (R-13) ou analisar a imagem (R-19). O servidor confere tudo de novo; o que se confere aqui é para
   a pessoa não esperar à toa (Constituição, IV).

   As funções puras ficam em `GravacaoDoVideo`, para o teste de `tests/javascript/gravacao.test.js`;
   a ligação com a página só roda quando a página existe. */

(function (raiz) {
  "use strict";

  // MP4 primeiro: o Chromium e o Safari gravam o mesmo contêiner, que toca em qualquer navegador da
  // comissão; o WebM fica para quem não grava MP4 (A-2 da prova de conceito).
  var FORMATOS = [
    "video/mp4;codecs=avc1.42E01E,mp4a.40.2",
    "video/mp4;codecs=avc1,opus",
    "video/mp4",
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
  ];
  var TENTATIVAS_POR_PARTE = 3;

  function escolherFormato(suporta) {
    for (var i = 0; i < FORMATOS.length; i += 1) {
      if (suporta(FORMATOS[i])) return FORMATOS[i];
    }
    return "";
  }

  function formatoBase(tipo) {
    return String(tipo || "").split(";")[0].trim().toLowerCase();
  }

  // As marcas em segundos, com três casas: é a forma que o servidor confere (FR-7113).
  function marcasEmSegundos(marcas) {
    return marcas.map(function (marca) {
      return { passo: marca.passo, instante: Math.round(marca.ms) / 1000 };
    });
  }

  function mmss(segundos) {
    var s = Math.max(0, Math.floor(segundos));
    return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
  }

  function hex(buffer) {
    return Array.prototype.map
      .call(new Uint8Array(buffer), function (byte) {
        return byte.toString(16).padStart(2, "0");
      })
      .join("");
  }

  /* O envio em partes, retomável. `pedir(metodo, url, corpo, cabecalhos)` devolve
     `{status, dados}`, e é injetado para o teste. A retomada pergunta ao servidor o deslocamento
     recebido, em vez de confiar no que o aparelho acha que mandou (FR-7119). */
  function Envio(opcoes) {
    this.arquivo = opcoes.arquivo;
    this.tamanho = opcoes.tamanho;
    this.parte = opcoes.parte;
    this.pedir = opcoes.pedir;
    this.rotas = opcoes.rotas;
    this.progresso = opcoes.progresso || function () {};
    this.deslocamento = 0;
    this.quedaSimulada = opcoes.quedaSimulada || 0;
  }

  Envio.prototype.retomar = async function () {
    var resposta = await this.pedir("GET", this.rotas.estado);
    if (resposta.status === 200) this.deslocamento = resposta.dados.deslocamento;
    return this.deslocamento;
  };

  Envio.prototype.enviarPartes = async function () {
    var numero = 0;
    while (this.deslocamento < this.tamanho) {
      numero += 1;
      var fim = Math.min(this.deslocamento + this.parte, this.tamanho);
      var corpo = this.arquivo.slice(this.deslocamento, fim);
      var falhas = 0;
      for (;;) {
        if (this.quedaSimulada && numero === this.quedaSimulada) {
          this.quedaSimulada = 0;
          throw new Error("queda simulada");
        }
        var resposta;
        try {
          resposta = await this.pedir(
            "PUT",
            this.rotas.partes + "?deslocamento=" + this.deslocamento,
            corpo,
            { "Content-Type": "application/octet-stream" }
          );
        } catch (erro) {
          falhas += 1;
          if (falhas >= TENTATIVAS_POR_PARTE) throw erro;
          continue;
        }
        if (resposta.status === 409 && resposta.dados.codigo === "deslocamento") {
          this.deslocamento = resposta.dados.deslocamento;
          break;
        }
        if (resposta.status !== 200) {
          var recusa = new Error(resposta.dados.mensagem || "O envio foi recusado.");
          recusa.recusa = resposta.dados;
          throw recusa;
        }
        this.deslocamento = resposta.dados.deslocamento;
        break;
      }
      this.progresso(this.deslocamento / this.tamanho);
    }
    return this.deslocamento;
  };

  // --- as funções do palco (174) -----------------------------------------------------------

  // "Passo 2 de 4": a posição no roteiro, sobre o vídeo e no anúncio ao leitor de tela (FR-7868).
  function rotuloDoPasso(indice, total) {
    return "Passo " + (indice + 1) + " de " + total;
  }

  // Dois toques a menos de meio segundo contam como um (FR-7870). É proteção contra o toque duplo
  // de um gesto só, e não tempo mínimo de passo: ninguém mostra um documento em meio segundo.
  var INTERVALO_DO_TOQUE_DUPLO = 500;

  function aceitaAvanco(agora, ultimo) {
    return ultimo === null || ultimo === undefined || agora - ultimo >= INTERVALO_DO_TOQUE_DUPLO;
  }

  // Megabytes com vírgula e uma casa: "o envio vai usar cerca de 9,4 MB da sua internet" (FR-7880).
  function megabytes(bytes) {
    return (Math.max(0, Number(bytes) || 0) / 1048576).toFixed(1).replace(".", ",");
  }

  // "1 min 12 s", e não "72.3 segundos" (FR-7883). O filtro do servidor tem os mesmos casos.
  function duracaoPorExtenso(segundos) {
    var total = Math.max(0, Math.round(Number(segundos) || 0));
    var minutos = Math.floor(total / 60);
    var resto = total % 60;
    if (!minutos) return resto + " s";
    return resto ? minutos + " min " + resto + " s" : minutos + " min";
  }

  /* Houve fala? Nível de pelo menos `limiar` por `minimo` ms seguidos (FR-7873, research T-006). É
     nível de sinal, calculado no aparelho, e não entra no que se envia (FR-7890). `amostras` são
     `{nivel, ms}` em ordem de tempo. */
  function ouviuFala(amostras, limiar, minimo) {
    limiar = limiar === undefined ? LIMIAR_DA_FALA : limiar;
    minimo = minimo === undefined ? 300 : minimo;
    var inicio = null;
    for (var i = 0; i < amostras.length; i += 1) {
      if (amostras[i].nivel >= limiar) {
        if (inicio === null) inicio = amostras[i].ms;
        if (amostras[i].ms - inicio >= minimo) return true;
      } else {
        inicio = null;
      }
    }
    return false;
  }

  /* O medidor do microfone (176, emenda; FR-8080 a FR-8082, D-011). A régua da fala continua a da
     174 — `nivelDoPico`, de 0 a 100, que `ouviuFala` lê —; o que muda é o que se desenha. A barra é
     o pico em decibéis entre `DB_MINIMO` e `DB_MAXIMO`: na escala linear de antes, a fala comum
     ficava no primeiro quinto da barra e parecia parada. Sobe em dezenas de milissegundos e desce em
     quase meio segundo, para seguir a voz sem piscar a cada quadro. */
  var DB_MINIMO = -48;
  var DB_MAXIMO = -6;
  var SUBIDA_DO_MEDIDOR = 40;
  var DESCIDA_DO_MEDIDOR = 450;
  var LIMIAR_DA_FALA = 20;

  // O pico, de 0 a 1, das amostras do analisador: em ponto flutuante (-1 a 1) ou em bytes (128 é
  // o silêncio), conforme o navegador oferecer.
  function picoDasAmostras(amostras, emBytes) {
    var pico = 0;
    for (var i = 0; i < amostras.length; i += 1) {
      var valor = emBytes ? (amostras[i] - 128) / 128 : amostras[i];
      if (Math.abs(valor) > pico) pico = Math.abs(valor);
    }
    return Math.min(1, pico);
  }

  // A régua da 174 (`pico/128*250` sobre bytes), que decide "Estamos ouvindo você" (FR-7873).
  function nivelDoPico(pico) {
    return Math.min(100, Math.round((Number(pico) || 0) * 250));
  }

  // Quanto da barra o pico preenche, de 0 a 1, em decibéis.
  function fracaoDoMedidor(pico) {
    if (!(pico > 0)) return 0;
    var db = 20 * Math.log10(pico);
    return Math.max(0, Math.min(1, (db - DB_MINIMO) / (DB_MAXIMO - DB_MINIMO)));
  }

  // A marca de "volume bom" é o limiar da fala na régua da barra (FR-8082): onde a barra passa da
  // marca, a página passa a dizer que ouve.
  var MARCA_DO_VOLUME_BOM = fracaoDoMedidor(LIMIAR_DA_FALA / 250);

  // Um passo de `ms` em direção ao `alvo`: rápido para cima, devagar para baixo.
  function suavizarMedidor(anterior, alvo, ms) {
    var constante = alvo > anterior ? SUBIDA_DO_MEDIDOR : DESCIDA_DO_MEDIDOR;
    var passo = 1 - Math.exp(-Math.max(0, Number(ms) || 0) / constante);
    return anterior + (alvo - anterior) * passo;
  }

  /* A frase do passo de frente, em partes, para o destaque do que se diz (176, emenda; FR-8072,
     D-010): o que está entre «aspas» no roteiro vem em destaque, com as aspas, e nada é
     acrescentado — juntas, as partes são o texto do roteiro, letra por letra. */
  function partesDaFrase(texto) {
    var partes = [];
    var resto = String(texto || "");
    while (resto) {
      var abre = resto.indexOf("«");
      var fecha = abre < 0 ? -1 : resto.indexOf("»", abre);
      if (abre < 0 || fecha < 0) {
        partes.push({ texto: resto, destaque: false });
        break;
      }
      if (abre > 0) partes.push({ texto: resto.slice(0, abre), destaque: false });
      partes.push({ texto: resto.slice(abre, fecha + 1), destaque: true });
      resto = resto.slice(fecha + 1);
    }
    return partes;
  }

  /* O giro da imagem de teste no instante `t`, em segundos (176, FR-8040, research T-010): um ciclo
     previsível de dez segundos — de frente, esquerda, de frente, direita —, de -1 a 1, positivo à
     esquerda da pessoa, como o giro dos pontos. A detecção simulada lê este número, e não a imagem. */
  var CICLO_DA_IMAGEM_DE_TESTE = [
    [0, 0], [2.5, 0], [3, 1], [5, 1], [5.5, 0], [7, 0], [7.5, -1], [9.5, -1], [10, 0],
  ];

  function giroDaImagemDeTeste(t) {
    var x = ((Number(t) || 0) % 10 + 10) % 10;
    for (var i = 1; i < CICLO_DA_IMAGEM_DE_TESTE.length; i += 1) {
      var a = CICLO_DA_IMAGEM_DE_TESTE[i - 1];
      var b = CICLO_DA_IMAGEM_DE_TESTE[i];
      if (x <= b[0]) return a[1] + ((b[1] - a[1]) * (x - a[0])) / (b[0] - a[0] || 1);
    }
    return 0;
  }

  /* Quantos rostos a imagem de teste mostra no instante `t` (176, emenda; FR-8065): entre 0,6 e 2,2
     segundos do ciclo, de frente, um segundo vulto pequeno — o "documento" — aparece ao lado do
     primeiro, e depois sai. A detecção simulada lê este número, e não a imagem. */
  var DOCUMENTO_DA_IMAGEM_DE_TESTE = [0.6, 2.2];

  function rostosDaImagemDeTeste(t) {
    var x = ((Number(t) || 0) % 10 + 10) % 10;
    return x >= DOCUMENTO_DA_IMAGEM_DE_TESTE[0] && x < DOCUMENTO_DA_IMAGEM_DE_TESTE[1] ? 2 : 1;
  }

  var api = {
    FORMATOS: FORMATOS,
    escolherFormato: escolherFormato,
    formatoBase: formatoBase,
    marcasEmSegundos: marcasEmSegundos,
    mmss: mmss,
    hex: hex,
    Envio: Envio,
    rotuloDoPasso: rotuloDoPasso,
    aceitaAvanco: aceitaAvanco,
    megabytes: megabytes,
    duracaoPorExtenso: duracaoPorExtenso,
    ouviuFala: ouviuFala,
    giroDaImagemDeTeste: giroDaImagemDeTeste,
    rostosDaImagemDeTeste: rostosDaImagemDeTeste,
    picoDasAmostras: picoDasAmostras,
    nivelDoPico: nivelDoPico,
    fracaoDoMedidor: fracaoDoMedidor,
    suavizarMedidor: suavizarMedidor,
    MARCA_DO_VOLUME_BOM: MARCA_DO_VOLUME_BOM,
    LIMIAR_DA_FALA: LIMIAR_DA_FALA,
    partesDaFrase: partesDaFrase,
  };
  raiz.GravacaoDoVideo = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;

  if (typeof document === "undefined") return;
  var pagina = document.querySelector("[data-verificacao]");
  if (!pagina) return;

  // ------------------------------------------------------------------- a página

  var teto = Number(pagina.getAttribute("data-teto"));
  var limite = Number(pagina.getAttribute("data-limite"));
  var tamanhoDaParte = Number(pagina.getAttribute("data-parte"));
  var ficha = pagina.querySelector("[name=csrfmiddlewaretoken]");
  var palco = pagina.querySelector('[data-tela="palco"]');
  var momentos = document.querySelector("[data-momentos]");
  var passos = Array.prototype.slice.call(pagina.querySelectorAll("[data-passo]")).map(function (item) {
    return {
      chave: item.getAttribute("data-passo"),
      texto: item.getAttribute("data-texto"),
      titulo: item.getAttribute("data-titulo"),
      // "esquerda" ou "direita" nos dois perfis, com a detecção (176); ausente no resto.
      giro: item.getAttribute("data-giro"),
      // O passo do documento, com a detecção (176, emenda, FR-8060).
      documento: item.hasAttribute("data-documento"),
      // O sinal sobre a prévia: "esquerda", "direita", "documento", ou nenhum (176, FR-8050).
      gesto: item.getAttribute("data-gesto") || "",
    };
  });
  var estado = {
    stream: null, sintetica: null, gravador: null, pedacos: [], marcas: [], passo: 0,
    inicio: 0, relogio: null, limiteDaTomada: null, descartar: "", tomada: null, envio: null,
    medidor: null, contexto: null, quedaSimulada: 0, ultimoAvanco: null, telaAcesa: null,
    amostras: [], ouviu: false, tela: "escolha", volume: 0, volumeDesenhado: -1,
    // A detecção do giro (176): o vigia do palco, a escolha de tocar, a confirmação em curso e a fala
    // do passo de frente.
    vigia: null, soTocando: false, deteccaoAtiva: false, confirmando: null, prefixo: "",
    amostrasDaFrente: [], ouviuNaFrente: false,
  };

  // Em que momento da jornada cada tela fica (FR-7852): o cabeçalho diz onde a pessoa está.
  var MOMENTO_DA_TELA = { palco: "gravar", permissao: "gravar", revisao: "enviar", envio: "enviar" };

  function q(seletor) {
    return pagina.querySelector(seletor);
  }

  function mostrar(nome) {
    estado.tela = nome;
    Array.prototype.forEach.call(pagina.querySelectorAll("[data-tela]"), function (tela) {
      tela.hidden = tela.getAttribute("data-tela") !== nome;
    });
    if (momentos) {
      var atual = MOMENTO_DA_TELA[nome] || "preparar";
      Array.prototype.forEach.call(momentos.querySelectorAll("[data-momento]"), function (item) {
        if (item.getAttribute("data-momento") === atual) item.setAttribute("aria-current", "step");
        else item.removeAttribute("aria-current");
      });
    }
    // A tela acesa só enquanto o palco está aberto (FR-7877, research T-004), e a detecção também:
    // fora do palco o rosto não é lido (176, FR-8003).
    if (nome === "palco") {
      pedirTelaAcesa();
      ligarDeteccao();
    } else {
      soltarTelaAcesa();
      pausarDeteccao();
    }
    var titulo = pagina.querySelector('[data-tela="' + nome + '"] h2');
    if (titulo) {
      titulo.setAttribute("tabindex", "-1");
      titulo.focus();
    }
  }

  async function pedir(metodo, url, corpo, cabecalhos) {
    var opcoes = { method: metodo, credentials: "same-origin", headers: cabecalhos || {} };
    opcoes.headers["X-CSRFToken"] = ficha ? ficha.value : "";
    if (corpo !== undefined) opcoes.body = corpo;
    var resposta = await fetch(url, opcoes);
    var dados = {};
    try {
      dados = await resposta.json();
    } catch (erro) {
      dados = {};
    }
    return { status: resposta.status, dados: dados };
  }

  // --- a tela acesa -----------------------------------------------------------------------

  /* O pedido do próprio navegador para a tela não apagar (FR-7877, research T-004). A tela que
     apaga esconde a página, e a página escondida descarta a tomada (FR-7115 da 166): sem este
     pedido, o celular parado no tripé perdia a gravação. Onde não há suporte, o aviso explica. */
  async function pedirTelaAcesa() {
    var aviso = q("[data-aviso-tela-acesa]");
    if (estado.telaAcesa) return;
    if (!navigator.wakeLock || !navigator.wakeLock.request) {
      aviso.hidden = false;
      return;
    }
    try {
      var pedido = await navigator.wakeLock.request("screen");
      if (estado.tela !== "palco") {
        pedido.release();
        return;
      }
      estado.telaAcesa = pedido;
      pedido.addEventListener("release", function () {
        if (estado.telaAcesa === pedido) estado.telaAcesa = null;
      });
      aviso.hidden = true;
    } catch (erro) {
      aviso.hidden = false;
    }
  }

  function soltarTelaAcesa() {
    if (!estado.telaAcesa) return;
    var pedido = estado.telaAcesa;
    estado.telaAcesa = null;
    pedido.release().catch(function () {});
  }

  // --- a fonte ----------------------------------------------------------------------------

  /* A imagem de teste: um vulto cinza, sem cor de pele, e um tom sintético — para verificar a
     página sem câmera e sem gravar ninguém (research T-007). Só aparece no desenvolvimento. */
  function fonteSintetica() {
    var tela = document.createElement("canvas");
    tela.width = 480;
    tela.height = 640;
    var ctx = tela.getContext("2d");
    var comeco = performance.now();
    var ativo = true;
    // O vulto gira de um lado para o outro num ciclo previsível, e o nariz mostra o lado (176,
    // FR-8040). A prévia da imagem de teste não é espelhada: o giro à esquerda da pessoa põe o nariz
    // à direita do quadro, como na câmera frontal de verdade.
    function giroAgora() {
      return giroDaImagemDeTeste((performance.now() - comeco) / 1000);
    }
    function desenhar() {
      if (!ativo) return;
      var t = (performance.now() - comeco) / 1000;
      ctx.fillStyle = "#3a4250";
      ctx.fillRect(0, 0, tela.width, tela.height);
      var giro = giroAgora() * 40;
      ctx.fillStyle = "#9aa3b2";
      ctx.beginPath();
      ctx.ellipse(240 + giro, 260, 100, 135, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillRect(140 + giro / 2, 400, 200, 240);
      ctx.fillStyle = "#6b7484";
      ctx.beginPath();
      ctx.moveTo(240 + giro * 2.2, 270);
      ctx.lineTo(240 + giro * 1.4 - 12, 300);
      ctx.lineTo(240 + giro * 1.4 + 12, 300);
      ctx.fill();
      // O "documento" (176, emenda, FR-8065): um cartão com um vulto pequeno, ao lado do rosto, que
      // aparece e sai no começo do ciclo.
      if (rostosDaImagemDeTeste(t) > 1) {
        ctx.fillStyle = "#d8dce3";
        ctx.fillRect(330, 300, 120, 80);
        ctx.fillStyle = "#6b7484";
        ctx.beginPath();
        ctx.ellipse(362, 335, 16, 21, 0, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 24px system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("IMAGEM DE TESTE", 240, 50);
      ctx.fillText("t = " + t.toFixed(1) + " s", 240, 85);
      requestAnimationFrame(desenhar);
    }
    desenhar();
    var video = tela.captureStream(30);
    var Contexto = window.AudioContext || window.webkitAudioContext;
    var audio = new Contexto();
    var oscilador = audio.createOscillator();
    oscilador.frequency.value = 330;
    var volume = audio.createGain();
    volume.gain.value = 0.05;
    var destino = audio.createMediaStreamDestination();
    oscilador.connect(volume).connect(destino);
    oscilador.start();
    estado.sintetica = {
      // A leitura da detecção simulada (176, FR-8040): a caixa e o giro do vulto desenhado, na
      // mesma forma que os pontos do rosto dão. O giro do desenho vai de -1 a 1; o da leitura passa
      // do limiar só perto do extremo, como um giro de verdade.
      ler: function () {
        var g = giroAgora();
        var centro = 240 + g * 40;
        return {
          caixa: { x: (centro - 100) / 480, y: 125 / 640, largura: 200 / 480, altura: 270 / 640 },
          giro: g * 0.6,
          rostos: rostosDaImagemDeTeste((performance.now() - comeco) / 1000),
        };
      },
      parar: function () {
        ativo = false;
        oscilador.stop();
        audio.close();
      },
    };
    return new MediaStream(video.getVideoTracks().concat(destino.stream.getAudioTracks()));
  }

  var EXPLICACOES = {
    NotAllowedError: "A permissão de usar a câmera e o microfone foi negada.",
    NotFoundError: "Não encontramos câmera ou microfone neste aparelho.",
    NotReadableError: "A câmera está sendo usada por outro programa. Feche-o e tente de novo.",
    SecurityError: "A página precisa estar num endereço seguro.",
    SemSuporte: "Este navegador não oferece acesso à câmera.",
  };

  function comoLiberar() {
    var agente = navigator.userAgent || "";
    if (/iPhone|iPad|iPod/.test(agente)) {
      return "No iPhone: Ajustes › Safari › Câmera e Microfone › Permitir. Depois volte e toque em «Tentar de novo».";
    }
    if (/Android/.test(agente)) {
      return "No Android: toque no cadeado ao lado do endereço › Permissões › Câmera e Microfone › Permitir.";
    }
    return "No computador: clique no ícone à esquerda do endereço, permita a câmera e o microfone e recarregue a página.";
  }

  function fecharFonte() {
    if (estado.stream) estado.stream.getTracks().forEach(function (faixa) { faixa.stop(); });
    estado.stream = null;
    if (estado.sintetica) estado.sintetica.parar();
    estado.sintetica = null;
    if (estado.medidor) cancelAnimationFrame(estado.medidor);
    if (estado.contexto) estado.contexto.close();
    estado.medidor = null;
    estado.contexto = null;
  }

  /* A câmera abre no "Continuar" do "Antes de gravar" (FR-7866, D-004): o toque é o gesto que o
     navegador exige, e o palco aparece sem o "Abrir a câmera" e o "Ir para a gravação" de antes. */
  async function abrirCamera() {
    fecharFonte();
    var sintetica = q("[data-sintetica]");
    try {
      if (sintetica && sintetica.checked) {
        estado.stream = fonteSintetica();
      } else {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          var semSuporte = new Error("sem câmera");
          semSuporte.name = "SemSuporte";
          throw semSuporte;
        }
        estado.stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: true,
        });
      }
    } catch (erro) {
      q("[data-motivo-permissao]").textContent = EXPLICACOES[erro.name] || "A câmera não abriu.";
      q("[data-como-liberar]").textContent = comoLiberar();
      mostrar("permissao");
      return;
    }
    // A câmera aparece espelhada, como toda "selfie"; a imagem de teste não é rosto, e espelhá-la só
    // inverteria o texto. O arquivo gravado nunca é espelhado: é o `MediaStream`, e não a prévia.
    var previa = q("[data-previa]");
    previa.classList.toggle("sem-espelho", Boolean(sintetica && sintetica.checked));
    previa.srcObject = estado.stream;
    medirSom();
    entrarNoPalco("");
  }

  /* As barras do microfone (FR-8080, FR-8083): a do preparo e a pequena do selo. A largura muda por
     `transform`, escrito pelo CSSOM — a política de conteúdo recusa o atributo `style`, e não a
     propriedade —, e só quando muda de verdade, para não redesenhar a cada quadro. */
  var barrasDoSom = Array.prototype.slice.call(pagina.querySelectorAll("[data-volume]"));
  Array.prototype.forEach.call(pagina.querySelectorAll("[data-marca-do-volume]"), function (marca) {
    marca.style.left = (MARCA_DO_VOLUME_BOM * 100).toFixed(1) + "%";
  });

  function desenharVolume(fracao) {
    if (Math.abs(fracao - estado.volumeDesenhado) < 0.005) return;
    estado.volumeDesenhado = fracao;
    var transformacao = "scaleX(" + fracao.toFixed(3) + ")";
    barrasDoSom.forEach(function (barra) {
      barra.style.transform = transformacao;
    });
  }

  // O Safari pode criar a leitura do som suspensa; pedir de novo não custa (FR-8084).
  function retomarSom() {
    var contexto = estado.contexto;
    if (contexto && contexto.state === "suspended" && contexto.resume) {
      contexto.resume().catch(function () {});
    }
  }

  function medirSom() {
    var faixas = estado.stream.getAudioTracks();
    var frase = q("[data-estado-do-som]");
    estado.amostras = [];
    estado.ouviu = false;
    estado.volume = 0;
    estado.volumeDesenhado = -1;
    desenharVolume(0);
    if (!faixas.length) {
      frase.textContent = "Não encontramos o microfone. Você pode mostrar a frase escrita num papel.";
      return;
    }
    frase.textContent = "Fale alguma coisa para testar o microfone.";
    var Contexto = window.AudioContext || window.webkitAudioContext;
    estado.contexto = new Contexto();
    retomarSom();
    var analisador = estado.contexto.createAnalyser();
    analisador.fftSize = 512;
    estado.contexto.createMediaStreamSource(new MediaStream(faixas)).connect(analisador);
    // Em ponto flutuante onde houver: os bytes param em 1/128, e o silêncio da sala some neles.
    var emBytes = !analisador.getFloatTimeDomainData;
    var amostras = emBytes ? new Uint8Array(analisador.fftSize) : new Float32Array(analisador.fftSize);
    var anterior = performance.now();
    function quadro() {
      if (emBytes) analisador.getByteTimeDomainData(amostras);
      else analisador.getFloatTimeDomainData(amostras);
      var pico = picoDasAmostras(amostras, emBytes);
      var nivel = nivelDoPico(pico);
      var agora = performance.now();
      estado.volume = suavizarMedidor(estado.volume, fracaoDoMedidor(pico), agora - anterior);
      anterior = agora;
      desenharVolume(estado.volume);
      if (!estado.ouviu) {
        estado.amostras.push({ nivel: nivel, ms: performance.now() });
        if (estado.amostras.length > 120) estado.amostras.shift();
        if (ouviuFala(estado.amostras)) {
          estado.ouviu = true;
          frase.textContent = "Estamos ouvindo você.";
        }
      }
      // No passo de frente, com a detecção, a mesma leitura de nível diz que a fala chegou — sem
      // reconhecer palavra e sem terminar a gravação (176, FR-8013).
      if (
        estado.deteccaoAtiva && !estado.ouviuNaFrente && estado.passo === passos.length - 1 &&
        palco.getAttribute("data-estado") === "gravando"
      ) {
        estado.amostrasDaFrente.push({ nivel: nivel, ms: performance.now() });
        if (estado.amostrasDaFrente.length > 120) estado.amostrasDaFrente.shift();
        if (ouviuFala(estado.amostrasDaFrente)) {
          estado.ouviuNaFrente = true;
          var ouvindo = q("[data-ouvindo]");
          if (ouvindo) ouvindo.hidden = false;
        }
      }
      estado.medidor = requestAnimationFrame(quadro);
    }
    quadro();
  }

  // --- a gravação -------------------------------------------------------------------------

  // O passo atual sobre a prévia, com a posição e o título (FR-7868); o texto é o do roteiro,
  // inteiro (D-003). O anúncio diz os três, e o foco não sai de "Próximo" (UX-875).
  function desenharPassos() {
    var atual = passos[estado.passo];
    if (!atual) return;
    var rotulo = rotuloDoPasso(estado.passo, passos.length);
    q("[data-passo-rotulo]").textContent = rotulo;
    q("[data-passo-titulo]").textContent = atual.titulo;
    q("[data-passo-atual]").textContent = atual.texto;
    // O sinal do gesto e o tamanho da frase saem da folha, por estes dois atributos (FR-8050,
    // FR-8051); a confirmação do perfil anterior não vale para o novo.
    palco.setAttribute("data-gesto", atual.gesto);
    palco.removeAttribute("data-confirmado");
    // O passo da fala, o último: a frase desce para junto do botão, fora do rosto, com o que se diz
    // em destaque (176, emenda; FR-8070 a FR-8072, D-010). No alto fica só o "Passo 4 de 4".
    var daFala = estado.passo === passos.length - 1;
    palco.toggleAttribute("data-passo-da-fala", daFala);
    var fala = q("[data-fala-do-passo]");
    fala.textContent = "";
    if (daFala) {
      partesDaFrase(atual.texto).forEach(function (parte) {
        var trecho = parte.destaque ? document.createElement("strong") : document.createTextNode("");
        trecho.textContent = parte.texto;
        fala.appendChild(trecho);
      });
    }
    q("[data-proximo]").textContent = estado.passo < passos.length - 1 ? "Próximo" : "Terminar a gravação";
    // Quem avançou pelo giro ouve a confirmação antes do passo novo (176, FR-8012).
    q("[data-anuncio]").textContent = estado.prefixo + rotulo + ": " + atual.titulo + ". " + atual.texto;
    estado.prefixo = "";
    var confirmacao = q("[data-confirmacao]");
    if (confirmacao) confirmacao.hidden = true;
    var ouvindo = q("[data-ouvindo]");
    if (ouvindo) ouvindo.hidden = true;
    estado.amostrasDaFrente = [];
    estado.ouviuNaFrente = false;
    observarPasso();
  }

  // --- a detecção do giro (176) --------------------------------------------------------------

  /* A página só conversa com a detecção se o script dela veio e a página traz os endereços do motor:
     sem a chave, nenhum dos dois, e tudo abaixo é inerte (SC-2751). A detecção avisa; quem confirma
     e avança é esta página, pelo mesmo `avancar()` do toque (FR-8012, FR-8014). */
  var Deteccao = raiz.DeteccaoDoGiro;
  var detectar = Boolean(Deteccao && pagina.hasAttribute("data-deteccao-motor"));
  var GUIA_FORA = "Encaixe o rosto no oval. Ele não aparece no vídeo.";
  var GUIA_DENTRO = "Rosto no oval. Ele não aparece no vídeo.";

  function ligarDeteccao() {
    if (!detectar || estado.soTocando) return;
    var previa = q("[data-previa]");
    var simulada = estado.sintetica ? estado.sintetica.ler : null;
    if (estado.vigia) {
      // O vigia é um por página, e o motor fica entre as tomadas (achado da revisão do #573). Só a
      // troca entre a câmera e a imagem de teste pede outro: um tem motor, o outro não.
      if (Boolean(estado.vigia.opcoes.simulada) === Boolean(simulada)) {
        estado.vigia.opcoes.simulada = simulada;
        estado.vigia.opcoes.espelhada = !previa.classList.contains("sem-espelho");
        observarPasso();
        return;
      }
      estado.vigia.parar();
      estado.vigia = null;
    }
    estado.vigia = new Deteccao.Vigia({
      enderecos: {
        motor: pagina.getAttribute("data-deteccao-motor"),
        carregador: pagina.getAttribute("data-deteccao-carregador"),
        binario: pagina.getAttribute("data-deteccao-binario"),
        modelo: pagina.getAttribute("data-deteccao-modelo"),
      },
      video: previa,
      oval: q("[data-oval]"),
      espelhada: !previa.classList.contains("sem-espelho"),
      simulada: simulada,
      // Com a tomada em curso o motor não aquece: o aquecimento congela a página por segundos.
      emGravacao: function () {
        return palco.getAttribute("data-estado") === "gravando";
      },
      aoEstado: aoEstadoDaDeteccao,
      aoRosto: aoRosto,
      aoGiro: aoGiro,
    });
    // Depois do primeiro quadro do palco: o motor não está no caminho da câmera (FR-8016).
    var vigia = estado.vigia;
    setTimeout(function () {
      if (estado.vigia === vigia) vigia.carregar();
    }, 0);
    observarPasso();
  }

  // Fora do palco: o vigia para de ler e esquece as leituras (FR-8003), e o motor fica.
  function pausarDeteccao() {
    if (estado.confirmando) clearTimeout(estado.confirmando);
    estado.confirmando = null;
    if (estado.vigia) estado.vigia.pausar();
  }

  function desligarDeteccao() {
    pausarDeteccao();
    if (!estado.vigia) return;
    estado.vigia.parar();
    estado.vigia = null;
  }

  // Ao sair da página, o motor é solto.
  window.addEventListener("pagehide", function () {
    desligarDeteccao();
  });

  // O que o vigia olha agora: o oval antes de começar, o lado nos perfis, o documento no primeiro
  // passo (emenda, FR-8060), nada no de frente.
  function observarPasso() {
    if (!estado.vigia) return;
    if (palco.getAttribute("data-estado") !== "gravando") {
      estado.vigia.observar("oval");
      return;
    }
    // Gravando, o oval não é mais pedido: volta ao traço da 174.
    aoRosto(false);
    var atual = passos[estado.passo];
    var alvo = null;
    if (atual && atual.giro) alvo = atual.giro;
    else if (atual && atual.documento) alvo = "documento";
    estado.vigia.observar(alvo);
  }

  function aoEstadoDaDeteccao(situacao) {
    pagina.setAttribute("data-deteccao", situacao);
    estado.deteccaoAtiva = situacao === "pronta" || situacao === "simulada";
    var aviso = q("[data-aviso-deteccao]");
    var ajuda = q("[data-ajuda-deteccao]");
    var ajudaDoToque = q("[data-ajuda-toque]");
    if (aviso) aviso.hidden = !(estado.deteccaoAtiva || situacao === "recusada");
    // Uma frase de ajuda por vez: a do toque (a da 174) ou a da detecção, que diz o mesmo e mais.
    if (ajuda) ajuda.hidden = !estado.deteccaoAtiva;
    if (ajudaDoToque) ajudaDoToque.hidden = estado.deteccaoAtiva;
    if (situacao === "recusada") {
      q("[data-frase-deteccao]").textContent = "Combinado: você avança tocando em «Próximo».";
      q("[data-so-tocando]").hidden = true;
    }
    // Sem a detecção, a página é a da 174, sem frase de falha (FR-8016, UX-923).
    if (!estado.deteccaoAtiva) {
      aoRosto(false);
      var confirmacao = q("[data-confirmacao]");
      if (confirmacao) confirmacao.hidden = true;
      // A confirmação some, e o sinal do passo volta: sem isto, a detecção desligada logo depois de
      // "Documento visto" deixava o passo sem sinal e sem confirmação (revisão da emenda).
      palco.removeAttribute("data-confirmado");
      var ouvindo = q("[data-ouvindo]");
      if (ouvindo) ouvindo.hidden = true;
    }
  }

  // O oval muda de traço e a frase muda: nenhum estado só pela cor (FR-8010, UX-922).
  function aoRosto(dentro) {
    var oval = q("[data-oval]");
    if (oval) oval.setAttribute("data-rosto", dentro ? "dentro" : "fora");
    var guia = q("[data-guia-do-oval]");
    if (guia) guia.textContent = dentro ? GUIA_DENTRO : GUIA_FORA;
  }

  function aoGiro(situacao) {
    if (palco.getAttribute("data-estado") !== "gravando") return;
    var caixa = q("[data-confirmacao]");
    if (!caixa) return;
    if (situacao === "na-mao") {
      // O documento apareceu (emenda, FR-8061): "Documento visto", no tom do perfil (UX-925), no lugar
      // do sinal; a passagem espera o rosto voltar sozinho (FR-8062). O leitor de tela ouve agora, e
      // não de novo ao mudar de passo.
      caixa.textContent = passos[estado.passo].titulo + " visto";
      caixa.setAttribute("data-tipo", "visto");
      caixa.hidden = false;
      palco.setAttribute("data-confirmado", "");
      q("[data-anuncio]").textContent = caixa.textContent + ".";
    } else if (situacao === "visto") {
      // "Perfil esquerdo visto": o gesto bem feito, e não uma aprovação (UX-920).
      var frase = passos[estado.passo].titulo + " visto";
      var jaAnunciado = !caixa.hidden && caixa.textContent === frase;
      caixa.textContent = frase;
      caixa.setAttribute("data-tipo", "visto");
      caixa.hidden = false;
      // A confirmação toma o lugar da seta (FR-8053).
      palco.setAttribute("data-confirmado", "");
      if (estado.confirmando) clearTimeout(estado.confirmando);
      estado.confirmando = setTimeout(function () {
        estado.confirmando = null;
        estado.prefixo = jaAnunciado ? "" : frase + ". ";
        avancar();
      }, Deteccao.CONFIRMACAO);
    } else if (situacao === "outro-lado") {
      caixa.textContent = "Para o outro lado";
      caixa.setAttribute("data-tipo", "outro-lado");
      caixa.hidden = false;
      // Também para quem usa leitor de tela: a confirmação só seria lida ao mudar de passo, e esta
      // não muda passo nenhum (R-21 do estudo; achado da revisão do #573).
      q("[data-anuncio]").textContent = "Para o outro lado.";
    } else {
      caixa.hidden = true;
    }
  }

  // "Prefiro avançar só tocando" (FR-8005, D-003): o vigia para, e nada é guardado — vale até a
  // página ser recarregada.
  function soTocando() {
    estado.soTocando = true;
    desligarDeteccao();
    aoEstadoDaDeteccao("recusada");
  }

  function entrarNoPalco(aviso) {
    estado.passo = 0;
    estado.ultimoAvanco = null;
    palco.setAttribute("data-estado", "preparo");
    q("[data-tempo]").textContent = "0:00";
    var caixa = q("[data-aviso-gravacao]");
    caixa.textContent = aviso || "";
    caixa.hidden = !aviso;
    desenharPassos();
    mostrar("palco");
    // No computador o palco fica na coluna, abaixo do título: rolar até ele põe a prévia e "Começar
    // a gravar" na mesma tela. No celular ele já ocupa a tela inteira.
    if (window.matchMedia && window.matchMedia("(min-width: 40rem)").matches) {
      palco.scrollIntoView({ block: "start" });
    }
  }

  function comecar() {
    var formato = escolherFormato(function (tipo) {
      return typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(tipo);
    });
    var opcoes = { videoBitsPerSecond: 1000000, audioBitsPerSecond: 64000 };
    if (formato) opcoes.mimeType = formato;
    try {
      estado.gravador = new MediaRecorder(estado.stream, opcoes);
    } catch (erro) {
      entrarNoPalco("Este navegador não conseguiu gravar. A entrevista ao vivo continua disponível.");
      return;
    }
    estado.pedacos = [];
    estado.marcas = [{ passo: passos[0].chave, ms: 0 }];
    estado.descartar = "";
    estado.gravador.ondataavailable = function (evento) {
      if (evento.data && evento.data.size) estado.pedacos.push(evento.data);
    };
    estado.gravador.onstop = aoParar;
    retomarSom();
    estado.gravador.start(1000);
    estado.inicio = performance.now();
    estado.ultimoAvanco = estado.inicio;
    estado.relogio = setInterval(function () {
      q("[data-tempo]").textContent = mmss((performance.now() - estado.inicio) / 1000);
    }, 250);
    estado.limiteDaTomada = setTimeout(function () { terminar(); }, teto * 1000);
    palco.setAttribute("data-estado", "gravando");
    desenharPassos();
    q("[data-proximo]").focus();
  }

  // Só pelo gesto, sem relógio (FR-7869, D-001); o toque duplo conta uma vez (FR-7870).
  function avancar() {
    // O toque durante a confirmação do giro avança na hora, e uma vez só (176, FR-8014).
    if (estado.confirmando) {
      clearTimeout(estado.confirmando);
      estado.confirmando = null;
    }
    var agora = performance.now();
    if (!aceitaAvanco(agora, estado.ultimoAvanco)) return;
    estado.ultimoAvanco = agora;
    if (estado.passo >= passos.length - 1) {
      terminar();
      return;
    }
    estado.passo += 1;
    estado.marcas.push({ passo: passos[estado.passo].chave, ms: agora - estado.inicio });
    desenharPassos();
    q("[data-proximo]").focus();
  }

  function pararRelogios() {
    clearInterval(estado.relogio);
    clearTimeout(estado.limiteDaTomada);
    if (estado.confirmando) clearTimeout(estado.confirmando);
    estado.confirmando = null;
  }

  function terminar() {
    if (!estado.gravador || estado.gravador.state === "inactive") return;
    // Nunca acima do teto: o temporizador dispara depois dele por milissegundos (achado 3 do review).
    estado.duracao = Math.min((performance.now() - estado.inicio) / 1000, teto);
    pararRelogios();
    estado.gravador.stop();
  }

  // Recomeçar descarta a tomada inteira: a gravação é contínua e não se emenda (R-13).
  function descartar(motivo) {
    if (!estado.gravador || estado.gravador.state === "inactive") return;
    estado.descartar = motivo;
    pararRelogios();
    estado.gravador.stop();
  }

  function aoParar() {
    if (estado.descartar) {
      var motivo = estado.descartar;
      estado.pedacos = [];
      estado.descartar = "";
      // Quem saiu do palco ("Voltar", "Não consigo") não volta a ele: só o recomeço e a tela que
      // sumiu reabrem o preparo.
      if (motivo === "saiu") return;
      entrarNoPalco(
        motivo === "tela-oculta"
          ? "A gravação parou porque a tela saiu do navegador. Grave de novo, do começo."
          : ""
      );
      return;
    }
    var tipo = formatoBase(estado.gravador.mimeType) || "video/webm";
    var arquivo = new Blob(estado.pedacos, { type: tipo });
    estado.pedacos = [];
    if (estado.tomada) URL.revokeObjectURL(estado.tomada.url);
    estado.tomada = {
      arquivo: arquivo,
      url: URL.createObjectURL(arquivo),
      formato: tipo,
      duracao: Math.round(estado.duracao * 1000) / 1000,
      marcas: marcasEmSegundos(estado.marcas),
    };
    while (estado.tomada.marcas.length < passos.length) {
      estado.tomada.marcas.push({ passo: passos[estado.tomada.marcas.length].chave, instante: estado.tomada.duracao });
    }
    q("[data-revisao]").src = estado.tomada.url;
    q("[data-dados-da-tomada]").textContent =
      "Duração: " + duracaoPorExtenso(estado.tomada.duracao) +
      ". O envio vai usar cerca de " + megabytes(arquivo.size) + " MB da sua internet.";
    mostrar("revisao");
  }

  function regravar() {
    if (estado.tomada) URL.revokeObjectURL(estado.tomada.url);
    estado.tomada = null;
    q("[data-revisao]").removeAttribute("src");
    if (estado.stream) entrarNoPalco("");
    else abrirCamera();
  }

  // A tomada é contínua: se a página some no meio, ela é descartada (FR-7115; A-3 da prova). Ao
  // voltar com o palco aberto, a tela acesa é pedida de novo: o navegador a solta ao esconder.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden" && estado.gravador && estado.gravador.state === "recording") {
      descartar("tela-oculta");
    }
    if (document.visibilityState === "visible" && estado.tela === "palco") pedirTelaAcesa();
  });

  // --- o envio ----------------------------------------------------------------------------

  function mostrarErro(texto) {
    var caixa = q("[data-erro-do-envio]");
    caixa.textContent = texto;
    caixa.hidden = !texto;
  }

  async function enviar() {
    var tomada = estado.tomada;
    if (!tomada) return;
    mostrar("envio");
    mostrarErro("");
    q("[data-tentar-de-novo]").hidden = true;
    if (tomada.arquivo.size > limite) {
      mostrarErro("O vídeo ficou maior que o permitido. Grave de novo, um pouco mais curto.");
      return;
    }
    q("[data-estado-do-envio]").textContent = "Calculando o resumo do vídeo.";
    tomada.sha256 = tomada.sha256 || hex(await crypto.subtle.digest("SHA-256", await tomada.arquivo.arrayBuffer()));
    var inicio = await pedir(
      "POST",
      pagina.getAttribute("data-envios"),
      JSON.stringify({
        tamanho: tomada.arquivo.size,
        formato: tomada.formato,
        duracao: tomada.duracao,
        marcas: tomada.marcas,
        roteiro: pagina.getAttribute("data-roteiro"),
        maioridade: true,
      }),
      { "Content-Type": "application/json" }
    );
    if (inicio.status !== 201) {
      mostrarErro(inicio.dados.mensagem || "O envio não pôde começar.");
      return;
    }
    estado.envio = new Envio({
      arquivo: tomada.arquivo,
      tamanho: tomada.arquivo.size,
      parte: tamanhoDaParte,
      pedir: pedir,
      rotas: { estado: inicio.dados.estado, partes: inicio.dados.partes },
      quedaSimulada: estado.quedaSimulada,
      progresso: function (fracao) {
        var porcento = Math.round(fracao * 100);
        q("[data-progresso]").value = porcento;
        q("[data-estado-do-envio]").textContent = "Enviando… " + porcento + "%";
      },
    });
    estado.envio.concluir = inicio.dados.concluir;
    estado.quedaSimulada = 0;
    await continuarEnvio();
  }

  async function continuarEnvio() {
    var envio = estado.envio;
    q("[data-tentar-de-novo]").hidden = true;
    mostrarErro("");
    try {
      await envio.retomar();
      q("[data-estado-do-envio]").textContent = "Enviando… " + q("[data-progresso]").value + "%";
      await envio.enviarPartes();
    } catch (erro) {
      if (erro.recusa) {
        mostrarErro(erro.message);
        return;
      }
      mostrarErro("A conexão caiu. O que já chegou está guardado: toque em «Tentar de novo» para continuar de onde parou.");
      q("[data-tentar-de-novo]").hidden = false;
      q("[data-sugestao-ao-vivo]").hidden = false;
      return;
    }
    q("[data-estado-do-envio]").textContent = "Conferindo o vídeo recebido.";
    var fim = await pedir(
      "POST",
      envio.concluir,
      JSON.stringify({ sha256: estado.tomada.sha256 }),
      { "Content-Type": "application/json" }
    );
    if (fim.status !== 201) {
      mostrarErro(fim.dados.mensagem || "O vídeo não pôde ser conferido.");
      return;
    }
    fecharFonte();
    URL.revokeObjectURL(estado.tomada.url);
    window.location.assign(fim.dados.comprovante);
  }

  // --- os botões --------------------------------------------------------------------------

  pagina.addEventListener("click", function (evento) {
    var alvo = evento.target.closest("button");
    if (!alvo) return;
    if (alvo.hasAttribute("data-ir")) {
      descartar("saiu");
      fecharFonte();
      mostrar(alvo.getAttribute("data-ir"));
    } else if (alvo.hasAttribute("data-continuar-acolhimento")) {
      var escolhida = pagina.querySelector("[data-maioridade]:checked");
      q("[data-erro-maioridade]").hidden = Boolean(escolhida);
      if (!escolhida) {
        // A recusa só depois do gesto, junto da pergunta, com o foco nela (FR-7865).
        q("[data-pergunta-maioridade]").focus();
        return;
      }
      if (escolhida.value === "sim") abrirCamera();
      else mostrar("menor");
    } else if (alvo.hasAttribute("data-abrir-camera")) {
      abrirCamera();
    } else if (alvo.hasAttribute("data-comecar")) {
      comecar();
    } else if (alvo.hasAttribute("data-proximo")) {
      avancar();
    } else if (alvo.hasAttribute("data-recomecar")) {
      descartar("recomecar");
    } else if (alvo.hasAttribute("data-regravar")) {
      regravar();
    } else if (alvo.hasAttribute("data-enviar")) {
      enviar();
    } else if (alvo.hasAttribute("data-tentar-de-novo")) {
      continuarEnvio();
    } else if (alvo.hasAttribute("data-so-tocando")) {
      soTocando();
    }
  });

  // A queda simulada da verificação no navegador (quickstart, passo 3): a parte N falha uma vez.
  raiz.__verificacao = {
    simularQueda: function (parte) {
      estado.quedaSimulada = Number(parte) || 0;
      if (estado.envio) estado.envio.quedaSimulada = estado.quedaSimulada;
    },
  };
})(typeof window !== "undefined" ? window : globalThis);
