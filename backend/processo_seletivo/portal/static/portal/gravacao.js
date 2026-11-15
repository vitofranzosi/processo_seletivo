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
    limiar = limiar === undefined ? 20 : limiar;
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
    };
  });
  var estado = {
    stream: null, sintetica: null, gravador: null, pedacos: [], marcas: [], passo: 0,
    inicio: 0, relogio: null, limiteDaTomada: null, descartar: "", tomada: null, envio: null,
    medidor: null, contexto: null, quedaSimulada: 0, ultimoAvanco: null, telaAcesa: null,
    amostras: [], ouviu: false, tela: "escolha",
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
    // A tela acesa só enquanto o palco está aberto (FR-7877, research T-004).
    if (nome === "palco") pedirTelaAcesa();
    else soltarTelaAcesa();
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
    function desenhar() {
      if (!ativo) return;
      var t = (performance.now() - comeco) / 1000;
      ctx.fillStyle = "#3a4250";
      ctx.fillRect(0, 0, tela.width, tela.height);
      var giro = Math.sin(t * 0.8) * 40;
      ctx.fillStyle = "#9aa3b2";
      ctx.beginPath();
      ctx.ellipse(240 + giro, 260, 100, 135, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillRect(140 + giro / 2, 400, 200, 240);
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

  function medirSom() {
    var faixas = estado.stream.getAudioTracks();
    var medidor = q("[data-nivel]");
    var frase = q("[data-estado-do-som]");
    estado.amostras = [];
    estado.ouviu = false;
    if (!faixas.length) {
      frase.textContent = "Não encontramos o microfone. Você pode mostrar a frase escrita num papel.";
      return;
    }
    frase.textContent = "Fale alguma coisa para testar o microfone.";
    var Contexto = window.AudioContext || window.webkitAudioContext;
    estado.contexto = new Contexto();
    var analisador = estado.contexto.createAnalyser();
    analisador.fftSize = 512;
    estado.contexto.createMediaStreamSource(new MediaStream(faixas)).connect(analisador);
    var amostras = new Uint8Array(analisador.fftSize);
    function quadro() {
      analisador.getByteTimeDomainData(amostras);
      var pico = 0;
      for (var i = 0; i < amostras.length; i += 1) pico = Math.max(pico, Math.abs(amostras[i] - 128));
      var nivel = Math.min(100, Math.round((pico / 128) * 250));
      medidor.value = nivel;
      if (!estado.ouviu) {
        estado.amostras.push({ nivel: nivel, ms: performance.now() });
        if (estado.amostras.length > 120) estado.amostras.shift();
        if (ouviuFala(estado.amostras)) {
          estado.ouviu = true;
          frase.textContent = "Estamos ouvindo você.";
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
    q("[data-proximo]").textContent = estado.passo < passos.length - 1 ? "Próximo" : "Terminar a gravação";
    q("[data-anuncio]").textContent = rotulo + ": " + atual.titulo + ". " + atual.texto;
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
