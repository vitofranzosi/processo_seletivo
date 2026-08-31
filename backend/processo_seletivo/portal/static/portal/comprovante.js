/* O botão de imprimir do comprovante (FR-063).

   A página já é imprimível — `@media print` na base tira cabeçalho e ações. O que faltava era o
   caminho: num celular, "imprimir ou salvar em PDF" está escondido atrás do menu do navegador, e
   quem acabou de se inscrever não vai procurá-lo. O protocolo é a única prova que a pessoa leva.

   O botão nasce escondido e só aparece quando este arquivo carrega: sem JavaScript não existe
   botão morto na tela, e a impressão continua possível pelo menu do navegador. */
(function () {
  var botao = document.querySelector("[data-imprimir]");
  if (!botao || typeof window.print !== "function") {
    return;
  }
  botao.hidden = false;
  botao.addEventListener("click", function () {
    window.print();
  });
})();
