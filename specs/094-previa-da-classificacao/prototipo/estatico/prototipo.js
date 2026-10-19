// O foco do painel da prévia (FR-2203). Nenhuma regra de classificação mora aqui: o cálculo é do
// servidor, e este arquivo só leva o foco ao painel quando ele abre e de volta ao botão quando fecha.
(function () {
  "use strict";
  document.addEventListener("htmx:afterSwap", function (evento) {
    var alvo = evento.detail && evento.detail.target;
    if (!alvo || alvo.id !== "painel-da-previa") {
      return;
    }
    var gatilho = evento.detail.requestConfig && evento.detail.requestConfig.elt;
    if (!alvo.firstElementChild) {
      var botao = document.querySelector("[data-abre-previa]");
      if (botao) {
        botao.focus();
      }
      return;
    }
    // Só a abertura leva o foco ao título: no recálculo, quem digita continua no campo.
    if (gatilho && gatilho.hasAttribute("data-abre-previa")) {
      var titulo = document.getElementById("titulo-da-previa");
      if (titulo) {
        titulo.focus();
      }
    }
  });
})();
