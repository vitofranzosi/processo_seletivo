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
})();
