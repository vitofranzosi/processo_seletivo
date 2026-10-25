/* A emissão do relatório do Edital (099): um clique, uma emissão.

   Cada envio do formulário é uma emissão numerada e registrada na trilha do Edital — e a resposta
   é um download, que não troca a página. Sem este script, o segundo clique de quem achou que o
   primeiro não pegou virava uma segunda emissão na trilha, e nada na tela dizia que a primeira
   estava a caminho.

   **Por que um prazo, e não o fim do download.** O navegador não avisa a página quando um anexo
   termina de baixar. O botão volta depois de `ESPERA` milissegundos, com a frase que diz o que
   fazer se o arquivo não veio; a recusa do servidor (concorrência, caractere sem grafia) troca a
   página, e a mensagem dela é a que vale. */
(function () {
  var ESPERA = 6000;
  var EMITINDO = "Emitindo…";
  var A_CAMINHO = "Emitindo o relatório com os dados atuais. O download começa em seguida.";
  var DEPOIS =
    "Se o download não começou, emita de novo — cada emissão recebe um número próprio.";

  /* Liga o formulário. `agendar` é o `setTimeout` do navegador, e é parâmetro para o teste. */
  function ligar(formulario, botao, situacao, agendar) {
    var rotulo = botao.textContent;
    var emitindo = false;
    formulario.addEventListener("submit", function (evento) {
      if (emitindo) {
        evento.preventDefault();
        return;
      }
      emitindo = true;
      botao.setAttribute("aria-disabled", "true");
      botao.textContent = EMITINDO;
      situacao.textContent = A_CAMINHO;
      agendar(function () {
        emitindo = false;
        botao.removeAttribute("aria-disabled");
        botao.textContent = rotulo;
        situacao.textContent = DEPOIS;
      }, ESPERA);
    });
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { ESPERA: ESPERA, EMITINDO: EMITINDO, A_CAMINHO: A_CAMINHO, DEPOIS: DEPOIS, ligar: ligar };
    return;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var formulario = document.querySelector("[data-emissao]");
    if (!formulario) return;
    ligar(
      formulario,
      formulario.querySelector("button[type=submit]"),
      formulario.querySelector("[data-situacao-da-emissao]"),
      window.setTimeout.bind(window)
    );
  });
})();
