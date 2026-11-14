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

  var api = {
    FORMATOS: FORMATOS,
    escolherFormato: escolherFormato,
    formatoBase: formatoBase,
    marcasEmSegundos: marcasEmSegundos,
    mmss: mmss,
    hex: hex,
    Envio: Envio,
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
  var passos = Array.prototype.slice.call(pagina.querySelectorAll("[data-passo]")).map(function (item) {
    return { chave: item.getAttribute("data-passo"), texto: item.getAttribute("data-texto") };
  });
  var estado = {
    stream: null, sintetica: null, gravador: null, pedacos: [], marcas: [], passo: 0,
    inicio: 0, relogio: null, limiteDaTomada: null, descartar: "", tomada: null, envio: null,
    medidor: null, contexto: null, quedaSimulada: 0,
  };

  function q(seletor) {
    return pagina.querySelector(seletor);
  }

  function mostrar(nome) {
    Array.prototype.forEach.call(pagina.querySelectorAll("[data-tela]"), function (tela) {
      tela.hidden = tela.getAttribute("data-tela") !== nome;
    });
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
    q("[data-previa]").srcObject = estado.stream;
    q("[data-previa-gravacao]").srcObject = estado.stream;
    q("[data-checagem-camera]").textContent = "Câmera funcionando.";
    q("[data-ir-gravar]").disabled = false;
    medirSom();
    mostrar("camera");
  }

  function medirSom() {
    var faixas = estado.stream.getAudioTracks();
    var medidor = q("[data-nivel]");
    if (!faixas.length) return;
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
      medidor.value = Math.min(100, Math.round((pico / 128) * 250));
      estado.medidor = requestAnimationFrame(quadro);
    }
    quadro();
  }

  // --- a gravação -------------------------------------------------------------------------

  function desenharPassos() {
    Array.prototype.forEach.call(pagina.querySelectorAll("[data-passo]"), function (item, i) {
      item.classList.toggle("feito", i < estado.passo);
      item.classList.toggle("atual", i === estado.passo);
    });
    var atual = passos[estado.passo];
    var seguinte = passos[estado.passo + 1];
    q("[data-passo-atual]").textContent = atual ? atual.texto : "";
    q("[data-passo-proximo]").textContent = seguinte ? "Depois: " + seguinte.texto : "Depois: assistir ao vídeo.";
    q("[data-proximo]").textContent = seguinte ? "Próximo passo" : "Terminar a gravação";
  }

  function prepararGravacao(aviso) {
    estado.passo = 0;
    q("[data-comecar]").hidden = false;
    q("[data-proximo]").hidden = true;
    q("[data-recomecar]").hidden = true;
    q("[data-selo]").hidden = true;
    q("[data-tempo]").textContent = "0:00";
    var caixa = q("[data-aviso-gravacao]");
    caixa.textContent = aviso || "";
    caixa.hidden = !aviso;
    desenharPassos();
    mostrar("gravacao");
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
      prepararGravacao("Este navegador não conseguiu gravar. A entrevista ao vivo continua disponível.");
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
    estado.relogio = setInterval(function () {
      q("[data-tempo]").textContent = mmss((performance.now() - estado.inicio) / 1000);
    }, 250);
    estado.limiteDaTomada = setTimeout(function () { terminar(); }, teto * 1000);
    q("[data-comecar]").hidden = true;
    q("[data-proximo]").hidden = false;
    q("[data-recomecar]").hidden = false;
    q("[data-selo]").hidden = false;
    q("[data-proximo]").focus();
  }

  function avancar() {
    if (estado.passo >= passos.length - 1) {
      terminar();
      return;
    }
    estado.passo += 1;
    estado.marcas.push({ passo: passos[estado.passo].chave, ms: performance.now() - estado.inicio });
    desenharPassos();
  }

  function pararRelogios() {
    clearInterval(estado.relogio);
    clearTimeout(estado.limiteDaTomada);
  }

  function terminar() {
    if (!estado.gravador || estado.gravador.state === "inactive") return;
    estado.duracao = (performance.now() - estado.inicio) / 1000;
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
      prepararGravacao(
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
      "Duração: " + mmss(estado.tomada.duracao) + ". Tamanho: " + (arquivo.size / 1048576).toFixed(1) + " MB.";
    mostrar("revisao");
  }

  function regravar() {
    if (estado.tomada) URL.revokeObjectURL(estado.tomada.url);
    estado.tomada = null;
    q("[data-revisao]").removeAttribute("src");
    prepararGravacao("");
  }

  // A tomada é contínua: se a página some no meio, ela é descartada (FR-7115; A-3 da prova).
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden" && estado.gravador && estado.gravador.state === "recording") {
      descartar("tela-oculta");
    }
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
        q("[data-progresso]").value = Math.round(fracao * 100);
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
      q("[data-estado-do-envio]").textContent = "Enviando o vídeo.";
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
      var destino = alvo.getAttribute("data-ir");
      if (destino !== "camera") {
        descartar("saiu");
        fecharFonte();
      }
      mostrar(destino);
    } else if (alvo.hasAttribute("data-continuar-acolhimento")) {
      var escolhida = pagina.querySelector("[data-maioridade]:checked");
      q("[data-erro-maioridade]").hidden = Boolean(escolhida);
      if (!escolhida) return;
      mostrar(escolhida.value === "sim" ? "camera" : "menor");
    } else if (alvo.hasAttribute("data-abrir-camera")) {
      abrirCamera();
    } else if (alvo.hasAttribute("data-ir-gravar")) {
      prepararGravacao("");
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
