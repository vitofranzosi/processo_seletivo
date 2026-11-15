/* A bancada da detecção do giro (176, FR-8041): mede o tempo até o motor ficar pronto e o tempo de
   cada leitura, e mostra o giro ao vivo, para conferir o sinal (D-005) e o limiar com uma pessoa de
   verdade. Usa o `Vigia` de `deteccao.js`, com os mesmos arquivos da página da gravação. */

(function () {
  "use strict";
  var D = window.DeteccaoDoGiro;
  // Endereços absolutos: o `import()` de um script clássico resolve o caminho a partir do próprio
  // script, e não da página — na gravação eles já vêm absolutos do servidor.
  var BASE = new URL("../../../backend/processo_seletivo/portal/static/portal/deteccao/", location.href).href;
  var enderecos = {
    motor: BASE + "tasks-vision-0.10.35/vision_bundle.mjs",
    carregador: BASE + "tasks-vision-0.10.35/vision_wasm_internal.js",
    binario: BASE + "tasks-vision-0.10.35/vision_wasm_internal.wasm",
    modelo: BASE + "face_landmarker-float16-1.task",
  };
  var $ = function (id) { return document.getElementById(id); };
  var tempos = [];
  window.__bancada = { tempos: tempos, carga: null, giros: [] };

  async function abrir() {
    var video = $("previa");
    video.srcObject = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    var inicio = performance.now();
    var vigia = new D.Vigia({
      enderecos: enderecos,
      video: video,
      aoEstado: function (estado) { $("estado").textContent = estado; },
    });
    await vigia.carregar();
    var carga = Math.round(performance.now() - inicio);
    window.__bancada.carga = carga;
    $("carga").textContent = carga + " ms";
    if (!vigia.motor) return;
    // A orçamento da página não vale aqui: a bancada quer medir, e não desligar.
    vigia.orcamento = { registrar: function () { return true; } };
    setInterval(function () {
      var antes = performance.now();
      var leitura = vigia.lerQuadro();
      var ms = performance.now() - antes;
      tempos.push(ms);
      if (tempos.length > 200) tempos.shift();
      var media = tempos.reduce(function (a, b) { return a + b; }, 0) / tempos.length;
      $("leitura").textContent = media.toFixed(1) + " / " + Math.max.apply(null, tempos).toFixed(1);
      var giro = leitura ? leitura.giro : null;
      window.__bancada.giros.push(giro);
      $("giro").textContent = giro === null ? "sem rosto" : giro.toFixed(2);
      $("lado").textContent =
        giro === null ? "—" : giro >= D.LIMIAR_DO_GIRO ? "esquerda" : giro <= -D.LIMIAR_DO_GIRO ? "direita" : "de frente";
    }, D.INTERVALO);
  }

  $("abrir").addEventListener("click", function () {
    abrir().catch(function (erro) { $("estado").textContent = "falhou: " + erro.message; });
  });
})();
