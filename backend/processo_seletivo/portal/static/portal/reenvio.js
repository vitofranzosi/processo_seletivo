/* A contagem regressiva do reenvio.
 *
 * O servidor já responde por escrito a quem clica cedo — isto existe para que a pessoa não
 * precise clicar para descobrir. O botão fica desabilitado só enquanto este script está no ar:
 * sem JavaScript ele continua clicável, e a resposta escrita cobre o caso (UX-006).
 */
(function () {
  "use strict";
  var forma = document.getElementById("reenvio");
  if (!forma) return;
  var restante = parseInt(forma.dataset.espera || "0", 10);
  if (!(restante > 0)) return;

  var botao = forma.querySelector("button");
  var texto = document.getElementById("espera-do-reenvio");
  var modelo = texto.dataset.modelo || "Você poderá pedir outro código daqui a {n} segundos.";

  botao.disabled = true;
  var passo = window.setInterval(function () {
    restante -= 1;
    if (restante > 0) {
      texto.textContent = modelo.replace("{n}", restante);
      return;
    }
    window.clearInterval(passo);
    botao.disabled = false;
    texto.textContent = "Não recebeu? Pode pedir outro código agora.";
  }, 1000);
})();
