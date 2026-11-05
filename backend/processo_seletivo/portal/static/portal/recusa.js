/* O foco na recusa (L2 da auditoria de percurso, SC-UX-005).

   A recusa aparece no topo, mas quem acionou o botão estava no fim da página. Depois de um POST o
   navegador volta ao topo e quem enxerga vê a mensagem; quem usa leitor de tela não vê nada — o
   envio simplesmente não acontece, e nada é dito. `role=alert` anuncia o que **muda** numa página
   já carregada, e não o que já veio no HTML.

   Mover o foco resolve os dois casos: o leitor de tela lê a mensagem, e o teclado continua a
   navegação de onde o erro está, não do começo da página.

   Sem JavaScript nada se perde: a mensagem continua no topo, visível e legível. */
(function () {
  var recusa = document.querySelector("[data-recusa]");
  if (!recusa) {
    return;
  }
  recusa.focus();
  /* A recusa no cartão da convocação (121, FR-3871): a volta é a âncora do item, e o navegador
     trata a âncora **depois** deste script, focando o cartão — que é focável, para a âncora da 118.
     O foco volta à recusa no `load`, quando a âncora já foi tratada; antes dele, nada a fazer. */
  window.addEventListener("load", function () {
    if (document.activeElement !== recusa) {
      recusa.focus();
    }
  });
})();
