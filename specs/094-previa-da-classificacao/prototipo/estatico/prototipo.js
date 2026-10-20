// O foco do painel da prévia (FR-2203). Nenhuma regra de classificação mora aqui: o cálculo é do
// servidor, e este arquivo só leva o foco ao título quando o painel abre ou troca de vista, e de volta
// ao botão do cartão que o abriu quando ele fecha.
(function () {
  "use strict";
  var abriu = null;
  document.addEventListener("htmx:afterSwap", function (evento) {
    var alvo = evento.detail && evento.detail.target;
    if (!alvo || alvo.id !== "painel-da-previa") {
      return;
    }
    var gatilho = evento.detail.requestConfig && evento.detail.requestConfig.elt;
    if (!alvo.firstElementChild) {
      var botao = abriu && document.body.contains(abriu)
        ? abriu
        : document.querySelector("[data-abre-previa]");
      if (botao) {
        botao.focus();
      }
      return;
    }
    if (gatilho && gatilho.hasAttribute("data-abre-previa")) {
      abriu = gatilho;
    }
    // Abrir, trocar de vista ou de marco leva o foco ao título; no recálculo, quem digita continua
    // no campo.
    if (
      gatilho &&
      (gatilho.hasAttribute("data-abre-previa") || gatilho.hasAttribute("data-foco-no-titulo"))
    ) {
      var titulo = document.getElementById("titulo-da-previa");
      if (titulo) {
        titulo.focus();
      }
    }
  });
})();
