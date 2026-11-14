/*
Prova de conceito da verificação da autodeclaração por vídeo (estudo de 13/11/2026, entrega 0).

O que ela é: uma página isolada, sem servidor do GPS, que exercita o caminho inteiro do lado do
navegador (permissão, prévia, gravação guiada, revisão, regravação, envio em partes com resumo,
reprodução pela comissão com parecer e deliberação) e mede o que o navegador produz.

O que ela não é: nada sai do aparelho. O "envio" fatia o arquivo e calcula o SHA-256 de cada parte
e do todo, como o servidor faria; a "trilha" vive na memória da aba. Fechar a aba apaga tudo.

As regras citadas (R-n) são as de `../03-especificacao.md`.
*/
"use strict";

// ---------------------------------------------------------------- parâmetros

// O roteiro é dado versionado (R-14). A ordem é a da UFC: documento, perfis, frente com a fala.
const ROTEIRO = {
  versao: "sintetico-1",
  passos: [
    {id: "documento", texto: "Mostre o documento com foto: a frente e depois o verso."},
    {id: "perfil-esquerdo", texto: "Vire o rosto devagar para a sua esquerda e espere um pouco."},
    {id: "perfil-direito", texto: "Agora vire devagar para a sua direita."},
    {id: "frente", texto: "Olhe para a câmera e diga seu nome, a data de hoje e: “Eu me autodeclaro preta, preto ou parda, pardo”."},
  ],
};
// Teto técnico, e não prazo do rito: só para o arquivo não crescer sem fim (R-14).
const TETO_MS = 3 * 60 * 1000;
const AVISO_ANTES_DO_TETO_MS = 30 * 1000;
// Partes de 8 MiB: cabem no nginx (12 MB) e numa requisição síncrona de 120 s mesmo a 1 Mbit/s.
const PARTE_BYTES = 8 * 1024 * 1024;
const LIMITE_BYTES = 60 * 1024 * 1024;
const TENTATIVAS_POR_PARTE = 3;
// A ordem é a de quem toca em mais lugares: MP4/H.264 abre em todo navegador da comissão, Safari
// incluído; WebM fica para quem não grava MP4.
const FORMATOS = [
  "video/mp4;codecs=avc1.42E01E,mp4a.40.2",
  "video/mp4;codecs=avc1,opus",
  "video/mp4",
  "video/webm;codecs=vp9,opus",
  "video/webm;codecs=vp8,opus",
  "video/webm",
];
const VIDEO_BITS = 1000000;
const AUDIO_BITS = 64000;

// ---------------------------------------------------------------- estado

const estado = {
  fonte: "camera",
  stream: null,
  recursosSinteticos: null,
  contextoDeAudio: null,
  quadroDoMedidor: 0,
  gravador: null,
  pedacos: [],
  mime: "",
  inicio: 0,
  relogio: 0,
  temporizadores: [],
  passo: 0,
  marcas: [],
  descartar: false,
  motivoDescarte: "",
  bloqueioDeTela: null,
  tomada: null,
  enviado: null,
  tomadasDescartadas: 0,
  interrupcoes: 0,
  trilha: [],
  violacoesCsp: [],
  aberturaAtual: null,
  medicao: {},
};

// ---------------------------------------------------------------- utilidades

const $ = (id) => document.getElementById(id);
const todas = (seletor) => Array.from(document.querySelectorAll(seletor));

function anunciar(texto) {
  const regiao = $("anuncio");
  regiao.textContent = "";
  // O texto novo numa tarefa seguinte, para o leitor de tela anunciar mesmo quando se repete.
  setTimeout(() => { regiao.textContent = texto; }, 50);
}

function registrar(evento, detalhe) {
  const quando = new Date();
  estado.trilha.push({evento, detalhe: detalhe || "", quando: quando.toISOString()});
  const item = document.createElement("li");
  item.textContent = `${quando.toLocaleTimeString("pt-BR")} ${evento}${detalhe ? " · " + detalhe : ""}`;
  $("trilha").appendChild(item);
}

function mmss(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

function megabytes(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / 1024 / 1024).toLocaleString("pt-BR", {maximumFractionDigits: 1})} MB`;
}

async function sha256(dados) {
  const buffer = dados instanceof Blob ? await dados.arrayBuffer() : dados;
  const resumo = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(resumo)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function plataforma() {
  const ua = navigator.userAgent;
  if (/iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)) return "ios";
  if (/Android/.test(ua)) return "android";
  return "computador";
}

// ---------------------------------------------------------------- navegação

function mostrarTela(id) {
  todas("[data-tela]").forEach((tela) => { tela.hidden = tela.id !== id; });
  const titulo = $(id).querySelector("h2");
  if (titulo) titulo.focus();
}

function mostrarVisao(nome) {
  todas("[data-visao-corpo]").forEach((corpo) => { corpo.hidden = corpo.dataset.visaoCorpo !== nome; });
  todas("nav.abas button").forEach((botao) => {
    if (botao.dataset.visao === nome) botao.setAttribute("aria-current", "page");
    else botao.removeAttribute("aria-current");
  });
  document.querySelector("main").classList.toggle("larga", nome !== "candidato");
  if (nome === "medicao") desenharMedicao();
  if (nome === "comissao") prepararComissao();
  const titulo = document.querySelector(`[data-visao-corpo="${nome}"] h2`);
  if (titulo) titulo.focus();
}

// ---------------------------------------------------------------- fontes de imagem

// A imagem de teste é sintética de propósito: um vulto cinza, sem cor de pele, para que ninguém
// precise se gravar para testar a página, e para que nenhum teste produza dado de cor ou raça.
function fonteSintetica() {
  const tela = document.createElement("canvas");
  tela.width = 720;
  tela.height = 960;
  const ctx = tela.getContext("2d");
  const inicio = performance.now();
  let ativo = true;
  function desenhar() {
    if (!ativo) return;
    const t = (performance.now() - inicio) / 1000;
    ctx.fillStyle = "#3a4250";
    ctx.fillRect(0, 0, tela.width, tela.height);
    const giro = Math.sin(t * 0.8) * 60;
    ctx.fillStyle = "#9aa3b2";
    ctx.beginPath();
    ctx.ellipse(360 + giro, 400, 150, 200, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(210 + giro / 2, 600, 300, 360);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 34px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("IMAGEM DE TESTE · SINTÉTICA", 360, 70);
    ctx.font = "28px ui-monospace, monospace";
    ctx.fillText(`t = ${t.toFixed(1)} s`, 360, 120);
    requestAnimationFrame(desenhar);
  }
  desenhar();
  const video = tela.captureStream(30);
  const audio = new (window.AudioContext || window.webkitAudioContext)();
  const oscilador = audio.createOscillator();
  oscilador.frequency.value = 330;
  const volume = audio.createGain();
  volume.gain.value = 0.05;
  // Um volume que oscila, para o medidor mostrar que o microfone "ouve".
  const lfo = audio.createOscillator();
  lfo.frequency.value = 0.7;
  const amplitude = audio.createGain();
  amplitude.gain.value = 0.04;
  lfo.connect(amplitude).connect(volume.gain);
  const destino = audio.createMediaStreamDestination();
  oscilador.connect(volume).connect(destino);
  oscilador.start();
  lfo.start();
  estado.recursosSinteticos = {parar() { ativo = false; oscilador.stop(); lfo.stop(); audio.close(); }};
  return new MediaStream([...video.getVideoTracks(), ...destino.stream.getAudioTracks()]);
}

async function abrirFonte() {
  if (estado.fonte === "sintetica") return fonteSintetica();
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    const erro = new Error("sem mediaDevices");
    erro.name = "SemSuporte";
    throw erro;
  }
  return navigator.mediaDevices.getUserMedia({
    video: {facingMode: "user", width: {ideal: 1280}, height: {ideal: 720}, frameRate: {ideal: 30}},
    audio: true,
  });
}

function fecharFonte() {
  if (estado.stream) estado.stream.getTracks().forEach((faixa) => faixa.stop());
  estado.stream = null;
  if (estado.recursosSinteticos) estado.recursosSinteticos.parar();
  estado.recursosSinteticos = null;
  if (estado.quadroDoMedidor) cancelAnimationFrame(estado.quadroDoMedidor);
  if (estado.contextoDeAudio) estado.contextoDeAudio.close();
  estado.contextoDeAudio = null;
  $("previa").srcObject = null;
  $("previa-gravacao").srcObject = null;
}

const EXPLICACOES = {
  NotAllowedError: "O navegador ou você negou a permissão de usar a câmera e o microfone.",
  NotFoundError: "Não encontramos câmera ou microfone neste aparelho.",
  NotReadableError: "A câmera está sendo usada por outro programa. Feche-o e tente de novo.",
  OverconstrainedError: "A câmera não aceitou a configuração pedida.",
  SecurityError: "A página não está num endereço seguro (https ou localhost).",
  SemSuporte: "Este navegador não oferece acesso à câmera.",
};
const COMO_LIBERAR = {
  ios: "No iPhone: Ajustes › Safari › Câmera e Microfone › Permitir. Depois volte e toque em “Tentar de novo”.",
  android: "No Android: toque no cadeado ao lado do endereço › Permissões › Câmera e Microfone › Permitir.",
  computador: "No computador: clique no ícone à esquerda do endereço, permita câmera e microfone e recarregue a página.",
};

async function abrirCamera() {
  estado.fonte = $("usar-sintetica").checked ? "sintetica" : "camera";
  try {
    estado.stream = await abrirFonte();
  } catch (erro) {
    estado.medicao.erroDePermissao = erro.name;
    registrar("CAMERA_RECUSADA", erro.name);
    $("motivo-permissao").textContent = EXPLICACOES[erro.name] || `Erro do navegador: ${erro.name}.`;
    $("como-liberar").textContent = COMO_LIBERAR[plataforma()];
    mostrarTela("tela-permissao");
    return;
  }
  registrar("CAMERA_ABERTA", estado.fonte);
  // A prévia da câmera é espelhada, como todo "selfie": quem se vê espelhado se ajeita sem
  // pensar. A imagem de teste não é rosto, e espelhá-la só inverteria o texto.
  todas(".camera").forEach((c) => c.classList.toggle("sem-espelho", estado.fonte === "sintetica"));
  $("previa").srcObject = estado.stream;
  $("previa-gravacao").srcObject = estado.stream;
  const video = estado.stream.getVideoTracks()[0];
  const ajustes = video ? video.getSettings() : {};
  estado.medicao.fonte = estado.fonte;
  estado.medicao.trilhaDeVideo = {
    largura: ajustes.width, altura: ajustes.height, quadros: ajustes.frameRate,
    facingMode: ajustes.facingMode || "", rotulo: estado.fonte === "camera" ? "(câmera)" : "(sintética)",
  };
  $("checa-camera").textContent = `Câmera funcionando (${ajustes.width || "?"}×${ajustes.height || "?"})`;
  $("checa-camera").className = "checagem ok";
  $("checa-microfone").className = "checagem pendente";
  medirSom();
  mostrarTela("tela-teste");
}

function medirSom() {
  const faixas = estado.stream.getAudioTracks();
  if (!faixas.length) {
    $("checa-microfone").textContent = "Microfone: nenhum encontrado";
    return;
  }
  const contexto = new (window.AudioContext || window.webkitAudioContext)();
  estado.contextoDeAudio = contexto;
  const analisador = contexto.createAnalyser();
  analisador.fftSize = 512;
  contexto.createMediaStreamSource(new MediaStream(faixas)).connect(analisador);
  const amostras = new Uint8Array(analisador.fftSize);
  let ouviu = false;
  const medidor = document.querySelector(".medidor[role=meter]");
  function quadro() {
    analisador.getByteTimeDomainData(amostras);
    let pico = 0;
    for (const v of amostras) pico = Math.max(pico, Math.abs(v - 128));
    const nivel = Math.min(100, Math.round((pico / 128) * 250));
    $("nivel").style.width = `${nivel}%`;
    medidor.setAttribute("aria-valuenow", String(nivel));
    if (!ouviu && nivel > 8) {
      ouviu = true;
      $("checa-microfone").textContent = "Microfone funcionando";
      $("checa-microfone").className = "checagem ok";
    }
    estado.quadroDoMedidor = requestAnimationFrame(quadro);
  }
  quadro();
}

// ---------------------------------------------------------------- gravação

function escolherFormato() {
  const suportados = {};
  for (const tipo of FORMATOS) {
    suportados[tipo] = typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(tipo);
  }
  estado.medicao.isTypeSupported = suportados;
  return FORMATOS.find((tipo) => suportados[tipo]) || "";
}

function desenharPassos() {
  const lista = $("lista-de-passos");
  lista.textContent = "";
  ROTEIRO.passos.forEach((passo, i) => {
    const item = document.createElement("li");
    item.textContent = passo.texto;
    if (i < estado.passo) item.className = "feito";
    if (i === estado.passo) item.className = "atual";
    lista.appendChild(item);
  });
  const atual = ROTEIRO.passos[estado.passo];
  const seguinte = ROTEIRO.passos[estado.passo + 1];
  $("passo-atual").textContent = atual ? atual.texto : "";
  $("passo-proximo").textContent = seguinte ? `Depois: ${seguinte.texto}` : "Depois: revisar o vídeo.";
  $("proximo").textContent = seguinte ? "Próximo passo" : "Terminar a gravação";
}

function prepararGravacao() {
  estado.passo = 0;
  $("tela-gravacao").classList.remove("em-gravacao");
  $("teto").textContent = mmss(TETO_MS);
  $("comecar").hidden = false;
  $("proximo").hidden = true;
  $("recomecar").hidden = true;
  $("selo-gravando").hidden = true;
  $("aviso-teto").hidden = true;
  $("tempo").textContent = "0:00";
  desenharPassos();
  mostrarTela("tela-gravacao");
  anunciar(`Quando estiver pronto, toque em Começar a gravar. Primeiro passo: ${ROTEIRO.passos[0].texto}`);
}

async function comecarGravacao() {
  estado.mime = escolherFormato();
  estado.medicao.formatoEscolhido = estado.mime || "(nenhum declarado; padrão do navegador)";
  const opcoes = {videoBitsPerSecond: VIDEO_BITS, audioBitsPerSecond: AUDIO_BITS};
  if (estado.mime) opcoes.mimeType = estado.mime;
  try {
    estado.gravador = new MediaRecorder(estado.stream, opcoes);
  } catch (erro) {
    estado.medicao.erroDoGravador = `${erro.name}: ${erro.message}`;
    registrar("GRAVADOR_RECUSADO", erro.name);
    mostrarTela("tela-falha");
    return;
  }
  estado.pedacos = [];
  estado.marcas = [{passo: ROTEIRO.passos[0].id, ms: 0}];
  estado.descartar = false;
  estado.gravador.ondataavailable = (e) => { if (e.data && e.data.size) estado.pedacos.push(e.data); };
  estado.gravador.onstop = aoPararGravacao;
  // Pedaços de 1 s: se a aba morrer no meio, o que já foi gravado não está todo num buffer só.
  estado.gravador.start(1000);
  estado.inicio = performance.now();
  estado.relogio = setInterval(() => { $("tempo").textContent = mmss(performance.now() - estado.inicio); }, 250);
  estado.temporizadores = [
    setTimeout(() => {
      $("aviso-teto").textContent = "Faltam 30 segundos para o limite técnico do vídeo.";
      $("aviso-teto").hidden = false;
      anunciar("Faltam 30 segundos para o limite do vídeo.");
    }, TETO_MS - AVISO_ANTES_DO_TETO_MS),
    setTimeout(() => terminarGravacao("teto"), TETO_MS),
  ];
  try {
    if ("wakeLock" in navigator) estado.bloqueioDeTela = await navigator.wakeLock.request("screen");
    estado.medicao.wakeLock = estado.bloqueioDeTela ? "obtido" : "sem suporte";
  } catch (erro) {
    estado.medicao.wakeLock = `recusado: ${erro.name}`;
  }
  $("comecar").hidden = true;
  $("proximo").hidden = false;
  $("recomecar").hidden = false;
  $("selo-gravando").hidden = false;
  $("tela-gravacao").classList.add("em-gravacao");
  registrar("GRAVACAO_INICIADA", estado.mime || "padrão");
  anunciar(`Gravando. ${ROTEIRO.passos[0].texto}`);
  $("proximo").focus();
}

function avancarPasso() {
  if (estado.passo >= ROTEIRO.passos.length - 1) {
    terminarGravacao("concluida");
    return;
  }
  estado.passo += 1;
  estado.marcas.push({passo: ROTEIRO.passos[estado.passo].id, ms: Math.round(performance.now() - estado.inicio)});
  desenharPassos();
  anunciar(ROTEIRO.passos[estado.passo].texto);
}

function limparTemporizadores() {
  clearInterval(estado.relogio);
  estado.temporizadores.forEach(clearTimeout);
  estado.temporizadores = [];
  if (estado.bloqueioDeTela) estado.bloqueioDeTela.release().catch(() => {});
  estado.bloqueioDeTela = null;
}

function terminarGravacao(motivo) {
  if (!estado.gravador || estado.gravador.state === "inactive") return;
  estado.duracaoMs = Math.round(performance.now() - estado.inicio);
  estado.motivoFim = motivo;
  limparTemporizadores();
  estado.gravador.stop();
}

// Recomeçar descarta a tomada inteira: a gravação é contínua e não se emenda (R-13).
function descartarTomada(motivo) {
  if (!estado.gravador || estado.gravador.state === "inactive") return;
  estado.descartar = true;
  estado.motivoDescarte = motivo;
  limparTemporizadores();
  estado.gravador.stop();
}

function aoPararGravacao() {
  if (estado.descartar) {
    estado.pedacos = [];
    estado.tomadasDescartadas += 1;
    registrar("TOMADA_DESCARTADA", estado.motivoDescarte);
    // Quem saiu para a entrevista ao vivo ou para o início não volta à tela da gravação.
    if (estado.motivoDescarte === "saiu") return;
    if (estado.motivoDescarte === "tela-oculta") {
      estado.interrupcoes += 1;
      prepararGravacao();
      $("aviso-teto").textContent = "A gravação parou porque a tela saiu do navegador. Grave de novo, do começo.";
      $("aviso-teto").hidden = false;
    } else {
      prepararGravacao();
    }
    return;
  }
  const tipo = (estado.gravador.mimeType || estado.mime || "video/webm").split(";")[0];
  const blob = new Blob(estado.pedacos, {type: tipo});
  estado.pedacos = [];
  estado.tomada = {
    blob, url: URL.createObjectURL(blob), mime: estado.gravador.mimeType || tipo,
    duracaoMs: estado.duracaoMs, marcas: estado.marcas.slice(), motivoFim: estado.motivoFim,
    versaoDoRoteiro: ROTEIRO.versao,
  };
  registrar("GRAVACAO_CONCLUIDA", `${mmss(estado.duracaoMs)}, ${megabytes(blob.size)}`);
  mostrarRevisao();
}

function mostrarRevisao() {
  const t = estado.tomada;
  const video = $("revisao");
  video.src = t.url;
  video.onloadedmetadata = () => {
    // O WebM do Chrome sai sem duração no cabeçalho (`Infinity`): o servidor não pode confiar nela,
    // e o comprovante usa a duração medida na gravação.
    estado.medicao.duracaoNoArquivo = Number.isFinite(video.duration) ? Math.round(video.duration * 10) / 10 : String(video.duration);
  };
  video.onerror = () => {
    estado.medicao.revisaoTocou = `erro ${video.error ? video.error.code : "?"}`;
  };
  video.onplaying = () => { estado.medicao.revisaoTocou = "sim"; };
  const kbps = Math.round((t.blob.size * 8) / (t.duracaoMs / 1000) / 1000);
  $("dados-da-tomada").textContent = `${mmss(t.duracaoMs)} · ${megabytes(t.blob.size)} · ${t.mime.split(";")[0]} · ~${kbps} kbit/s`;
  if (t.motivoFim === "teto") anunciar("O vídeo chegou ao limite técnico e parou sozinho.");
  Object.assign(estado.medicao, {
    mimeDoArquivo: t.mime, bytes: t.blob.size, duracaoMedidaS: Math.round(t.duracaoMs / 100) / 10,
    kbitPorSegundo: kbps, mbPorMinuto: Math.round((t.blob.size / 1024 / 1024) / (t.duracaoMs / 60000) * 10) / 10,
  });
  mostrarTela("tela-revisao");
}

function regravar() {
  if (estado.tomada) URL.revokeObjectURL(estado.tomada.url);
  estado.tomada = null;
  estado.tomadasDescartadas += 1;
  registrar("TOMADA_DESCARTADA", "regravar");
  $("revisao").removeAttribute("src");
  prepararGravacao();
}

// ---------------------------------------------------------------- validação e envio

// A mesma conferência que o servidor faria: o conteúdo, e não a extensão (shared/arquivos.py).
async function conferirConteudo(blob) {
  const cabeca = new Uint8Array(await blob.slice(0, 12).arrayBuffer());
  const webm = cabeca[0] === 0x1a && cabeca[1] === 0x45 && cabeca[2] === 0xdf && cabeca[3] === 0xa3;
  const ftyp = String.fromCharCode(cabeca[4], cabeca[5], cabeca[6], cabeca[7]) === "ftyp";
  if (webm) return "WebM";
  if (ftyp) return "MP4";
  return "";
}

const espera = (ms) => new Promise((r) => setTimeout(r, ms));

async function enviar() {
  const t = estado.tomada;
  if (!t) return;
  const formato = await conferirConteudo(t.blob);
  estado.medicao.assinatura = formato || "desconhecida";
  let recusa = "";
  if (!formato) recusa = "O arquivo não é um vídeo que o sistema reconhece.";
  else if (t.blob.size > LIMITE_BYTES) recusa = `O vídeo tem ${megabytes(t.blob.size)}, e o limite é ${megabytes(LIMITE_BYTES)}.`;
  else if (t.duracaoMs > TETO_MS + 2000) recusa = "O vídeo passou do limite de duração.";
  if (recusa) {
    registrar("ENVIO_RECUSADO", recusa);
    $("motivo-recusa").textContent = `${recusa} Grave de novo.`;
    mostrarTela("tela-recusa");
    return;
  }

  mostrarTela("tela-envio");
  const total = Math.ceil(t.blob.size / PARTE_BYTES) || 1;
  const lista = $("partes");
  lista.textContent = "";
  const resumosDasPartes = [];
  let quedaSimulada = $("simular-queda").checked;
  registrar("ENVIO_INICIADO", `${total} parte(s)`);
  for (let i = 0; i < total; i += 1) {
    const parte = t.blob.slice(i * PARTE_BYTES, Math.min((i + 1) * PARTE_BYTES, t.blob.size));
    const item = document.createElement("li");
    lista.appendChild(item);
    let enviada = false;
    for (let tentativa = 1; tentativa <= TENTATIVAS_POR_PARTE && !enviada; tentativa += 1) {
      item.textContent = `Parte ${i + 1} de ${total} (${megabytes(parte.size)}): enviando, tentativa ${tentativa}`;
      // A rede simulada: ~4 MB/s, para a barra andar de um jeito visível.
      await espera(Math.max(300, (parte.size / (4 * 1024 * 1024)) * 1000));
      const caiuAgora = quedaSimulada && i === Math.min(1, total - 1);
      if (caiuAgora) {
        quedaSimulada = false;
        $("estado-envio").textContent = `A conexão caiu na parte ${i + 1}. Retomando dela, e não do começo…`;
        anunciar("A conexão caiu. Retomando o envio.");
        registrar("ENVIO_INTERROMPIDO", `parte ${i + 1}`);
        await espera(1200);
        continue;
      }
      resumosDasPartes.push(await sha256(parte));
      enviada = true;
    }
    if (!enviada) {
      $("falha-envio").hidden = false;
      registrar("ENVIO_FALHOU", `parte ${i + 1}`);
      return;
    }
    item.textContent = `Parte ${i + 1} de ${total}: recebida · ${resumosDasPartes[i].slice(0, 12)}…`;
    const pct = Math.round(((i + 1) / total) * 100);
    $("progresso").style.width = `${pct}%`;
    document.querySelector("[role=progressbar]").setAttribute("aria-valuenow", String(pct));
    $("estado-envio").textContent = `${pct}% enviado`;
  }

  // O servidor remonta as partes e calcula o resumo do todo: é este que vai para o comprovante.
  const resumo = await sha256(t.blob);
  const agora = new Date();
  estado.enviado = Object.assign({}, t, {
    formato, resumo, resumosDasPartes, recebidoEm: agora, numero: "SIM-VA-0001", aberto: false,
  });
  estado.medicao.partes = total;
  registrar("VIDEO_RECEBIDO", `${formato}, ${megabytes(t.blob.size)}, sha256 ${resumo.slice(0, 16)}…`);
  // Enviado o vídeo, a câmera se fecha: não há motivo para ela continuar ligada (minimização).
  fecharFonte();
  mostrarComprovante();
}

function mostrarComprovante() {
  const e = estado.enviado;
  $("recebido-em").textContent = `${e.recebidoEm.toLocaleDateString("pt-BR")}, ${e.recebidoEm.toLocaleTimeString("pt-BR", {hour: "2-digit", minute: "2-digit"})} · duração ${mmss(e.duracaoMs)}`;
  const recibo = $("recibo");
  recibo.textContent = "";
  const linhas = [
    ["Comprovante", e.numero],
    ["Inscrição", "SIM-0001 (sintética)"],
    ["Formato", `${e.formato} · ${megabytes(e.blob.size)}`],
    ["Roteiro", e.versaoDoRoteiro],
    ["Resumo SHA-256", e.resumo],
  ];
  for (const [rotulo, valor] of linhas) {
    const dt = document.createElement("dt");
    dt.textContent = rotulo;
    const dd = document.createElement("dd");
    dd.textContent = valor;
    recibo.append(dt, dd);
  }
  // O titular assiste ao próprio vídeo (R-24).
  $("meu-video").src = e.url;
  mostrarTela("tela-comprovante");
  anunciar("Seu vídeo chegou. O comprovante está na tela.");
}

// ---------------------------------------------------------------- comissão

function prepararComissao() {
  const tem = Boolean(estado.enviado);
  $("sem-envio").hidden = tem;
  $("mesa").hidden = !tem;
  if (!tem) return;
  const e = estado.enviado;
  $("dados-do-recebido").textContent = `Enviado ${e.recebidoEm.toLocaleString("pt-BR")} · ${mmss(e.duracaoMs)} · roteiro ${e.versaoDoRoteiro} · resumo conferido · sem botão de baixar`;
  const marcas = $("marcas");
  marcas.textContent = "";
  e.marcas.forEach((marca, i) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.textContent = `${i + 1}. ${marca.passo} (${mmss(marca.ms)})`;
    botao.addEventListener("click", () => {
      const video = $("video-comissao");
      video.currentTime = marca.ms / 1000;
      video.play();
    });
    marcas.appendChild(botao);
  });
}

// Abrir é um ato, como na Mesa de hoje (mesa_inscricao.html): nada carrega sozinho, e a trilha
// registra **uma** abertura por vez que o vídeo é aberto, e não cada pedaço que o player pede.
async function abrirVideo() {
  const e = estado.enviado;
  // A conferência do resumo antes de entregar, como `copia_verificada` faz com o PDF.
  const conferido = (await sha256(e.blob)) === e.resumo;
  if (!conferido) {
    registrar("VIDEO_RECUSADO_POR_RESUMO");
    return;
  }
  estado.aberturaAtual = {inicio: new Date()};
  e.aberto = true;
  registrar("VISUALIZAR_VIDEO_DA_VERIFICACAO", "membro 1 · resumo conferido");
  const video = $("video-comissao");
  video.src = e.url;
  video.controls = true;
  $("abrir-video").hidden = true;
  $("reprodutor").hidden = false;
  video.oncanplay = () => { estado.medicao.comissaoTocou = "sim"; };
  video.onerror = () => { estado.medicao.comissaoTocou = `erro ${video.error ? video.error.code : "?"}`; };
}

function fecharVideo() {
  const video = $("video-comissao");
  video.pause();
  video.removeAttribute("src");
  video.load();
  $("reprodutor").hidden = true;
  $("abrir-video").hidden = false;
  estado.aberturaAtual = null;
}

function saltar(segundos) {
  const video = $("video-comissao");
  video.currentTime = Math.max(0, video.currentTime + segundos);
}

const ROTULOS_DE_PARECER = {confirmo: "Confirmo", nao_da: "Não dá para confirmar pelo vídeo"};

// R-11: pelo vídeo, a deliberação só tem dois desfechos. "Não confirmada" não existe aqui.
function deliberar(pareceres, regra) {
  const confirmam = pareceres.filter((p) => p === "confirmo").length;
  const n = pareceres.length;
  const satisfeita = {
    maioria: confirmam > n / 2,
    unanimidade: confirmam === n,
    recusa_unanime: confirmam >= 1,
  }[regra];
  return {confirmam, n, desfecho: satisfeita ? "confirmada" : "encaminhada"};
}

function registrarParecer(evento) {
  evento.preventDefault();
  const form = $("form-parecer");
  const escolha = form.querySelector("input[name=parecer]:checked");
  const motivos = Array.from(form.querySelectorAll("input[name=motivo]:checked")).map((c) => c.value);
  const erro = $("erro-parecer");
  erro.hidden = true;
  if (!estado.enviado.aberto) {
    erro.textContent = "Abra o vídeo antes de registrar o parecer.";
    erro.hidden = false;
    return;
  }
  if (!escolha) {
    erro.textContent = "Escolha uma das duas opções.";
    erro.hidden = false;
    return;
  }
  if (escolha.value === "nao_da" && !motivos.length) {
    erro.textContent = "Marque ao menos um motivo.";
    erro.hidden = false;
    return;
  }
  estado.meuParecer = escolha.value;
  registrar("PARECER_REGISTRADO", `membro 1 · ${escolha.value}${motivos.length ? " · " + motivos.join(",") : ""}`);
  Array.from(form.elements).forEach((campo) => { campo.disabled = true; });
  // Os pareceres alheios só aparecem depois do próprio (R-4, IN 261 art. 23).
  $("deliberacao").hidden = false;
  desenharDeliberacao();
}

function desenharDeliberacao() {
  const outros = {cc: ["confirmo", "confirmo"], cn: ["confirmo", "nao_da"], nn: ["nao_da", "nao_da"]}[$("cenario").value];
  const pareceres = [estado.meuParecer, ...outros];
  const lista = $("pareceres");
  lista.textContent = "";
  pareceres.forEach((p, i) => {
    const item = document.createElement("li");
    item.textContent = `Membro ${i + 1}${i === 0 ? " (você)" : ""}: ${ROTULOS_DE_PARECER[p]}`;
    lista.appendChild(item);
  });
  const r = deliberar(pareceres, $("regra").value);
  const caixa = $("desfecho");
  caixa.className = r.desfecho === "confirmada" ? "cartao ok" : "cartao espera";
  caixa.textContent = "";
  const titulo = document.createElement("strong");
  titulo.textContent = r.desfecho === "confirmada" ? "Confirmada" : "Encaminhada à entrevista ao vivo";
  const explicacao = document.createElement("p");
  explicacao.className = "fraco";
  explicacao.textContent = r.desfecho === "confirmada"
    ? `${r.confirmam} de ${r.n} confirmam, e a regra está satisfeita. A presidência confirma a deliberação.`
    : `${r.confirmam} de ${r.n} confirmam, e a regra não está satisfeita. Pelo vídeo não se indefere: o caso vai para a agenda da entrevista ao vivo.`;
  caixa.append(titulo, explicacao);
}

// ---------------------------------------------------------------- medição

function capacidades() {
  const video = document.createElement("video");
  return {
    navegador: navigator.userAgent,
    plataforma: plataforma(),
    contextoSeguro: window.isSecureContext,
    mediaDevices: Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    mediaRecorder: typeof MediaRecorder !== "undefined",
    wakeLockApi: "wakeLock" in navigator,
    tocaMp4H264: video.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"') || "não",
    tocaWebmVp8: video.canPlayType('video/webm; codecs="vp8, opus"') || "não",
    tocaWebmVp9: video.canPlayType('video/webm; codecs="vp9, opus"') || "não",
  };
}

function medicaoCompleta() {
  return Object.assign({data: new Date().toISOString(), roteiro: ROTEIRO.versao}, capacidades(), estado.medicao, {
    tomadasDescartadas: estado.tomadasDescartadas,
    interrupcoesPorTelaOculta: estado.interrupcoes,
    violacoesDeCsp: estado.violacoesCsp,
  });
}

function desenharMedicao() {
  const corpo = $("tabela-medicao");
  corpo.textContent = "";
  for (const [chave, valor] of Object.entries(medicaoCompleta())) {
    const linha = document.createElement("tr");
    const th = document.createElement("th");
    th.textContent = chave;
    const td = document.createElement("td");
    td.textContent = typeof valor === "object" ? JSON.stringify(valor) : String(valor);
    linha.append(th, td);
    corpo.appendChild(linha);
  }
}

async function copiarMedicao() {
  const texto = JSON.stringify(medicaoCompleta(), null, 2);
  try {
    await navigator.clipboard.writeText(texto);
    $("copiado").textContent = "Copiado.";
  } catch (erro) {
    $("copiado").textContent = `Não foi possível copiar (${erro.name}). Use “Baixar JSON”.`;
  }
}

function baixarMedicao() {
  const blob = new Blob([JSON.stringify(medicaoCompleta(), null, 2)], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `medicao-${plataforma()}-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ---------------------------------------------------------------- ligações

document.addEventListener("securitypolicyviolation", (e) => {
  estado.violacoesCsp.push(`${e.violatedDirective} ${e.blockedURI}`);
});

// Sair do navegador no meio da gravação a interrompe: a tela apagada, a ligação recebida e o
// aplicativo trocado produzem um vídeo com buraco, e o rito pede tomada contínua (R-13).
document.addEventListener("visibilitychange", () => {
  if (document.hidden && estado.gravador && estado.gravador.state === "recording") descartarTomada("tela-oculta");
});

window.addEventListener("pagehide", fecharFonte);

document.addEventListener("DOMContentLoaded", () => {
  todas("nav.abas button").forEach((botao) => botao.addEventListener("click", () => mostrarVisao(botao.dataset.visao)));
  todas("[data-ir]").forEach((botao) => botao.addEventListener("click", () => {
    if (botao.dataset.trilha) registrar(botao.dataset.trilha);
    if (botao.dataset.ir === "tela-falha" || botao.dataset.ir === "tela-inicio") {
      descartarTomada("saiu");
      fecharFonte();
    }
    mostrarTela(botao.dataset.ir);
  }));
  $("perfil").addEventListener("change", (e) => {
    // R-22: menor de idade não vê a opção do vídeo.
    const menor = e.target.value === "menor";
    $("opcao-video").hidden = menor;
    $("aviso-menor").hidden = !menor;
  });
  $("abrir-camera").addEventListener("click", abrirCamera);
  $("tentar-de-novo").addEventListener("click", abrirCamera);
  $("ir-gravar").addEventListener("click", prepararGravacao);
  $("comecar").addEventListener("click", comecarGravacao);
  $("proximo").addEventListener("click", avancarPasso);
  $("recomecar").addEventListener("click", () => descartarTomada("recomecar"));
  $("regravar").addEventListener("click", regravar);
  $("voltar-gravar").addEventListener("click", regravar);
  $("enviar").addEventListener("click", enviar);
  $("registrar-falha").addEventListener("click", () => {
    registrar("FALHA_TECNICA_RELATADA", $("relato").value.trim().slice(0, 200));
    mostrarTela("tela-ao-vivo");
  });
  $("abrir-video").addEventListener("click", abrirVideo);
  $("fechar-video").addEventListener("click", fecharVideo);
  $("voltar-10").addEventListener("click", () => saltar(-10));
  $("avancar-10").addEventListener("click", () => saltar(10));
  $("tocar").addEventListener("click", () => {
    const video = $("video-comissao");
    if (video.paused) video.play(); else video.pause();
  });
  $("velocidade").addEventListener("click", (e) => {
    const video = $("video-comissao");
    const lento = video.playbackRate === 1;
    video.playbackRate = lento ? 0.5 : 1;
    e.target.setAttribute("aria-pressed", String(lento));
  });
  $("form-parecer").addEventListener("submit", registrarParecer);
  $("cenario").addEventListener("change", desenharDeliberacao);
  $("regra").addEventListener("change", desenharDeliberacao);
  $("copiar-medicao").addEventListener("click", copiarMedicao);
  $("baixar-medicao").addEventListener("click", baixarMedicao);
});
