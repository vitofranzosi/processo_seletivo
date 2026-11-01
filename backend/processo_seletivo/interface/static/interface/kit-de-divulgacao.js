/* O "Copiar" do kit de divulgação (111, FR-3420, D-015).

   Cada botão nomeia, em `data-copiar`, o `id` do texto que copia. O resultado vai para uma região
   `aria-live`, porque a área de transferência não se vê: sem a frase, quem usa leitor de tela não
   sabe se copiou. Sem script, o botão não faz nada e o texto continua selecionável no `<pre>`; as
   exportações são formulários, e não dependem disto (EC-22). Copiar não registra (P-5). */
(function () {
  var COPIADO = "Texto copiado: ";
  var FALHOU = "Não foi possível copiar. Selecione o texto e copie pelo teclado.";

  /* `escrever` é a escrita na área de transferência, e é parâmetro para o teste. */
  function ligar(botao, alvo, situacao, nome, escrever) {
    botao.addEventListener("click", function () {
      escrever(alvo.textContent).then(
        function () {
          situacao.textContent = COPIADO + nome + ".";
        },
        function () {
          situacao.textContent = FALHOU;
        }
      );
    });
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { COPIADO: COPIADO, FALHOU: FALHOU, ligar: ligar };
    return;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var situacao = document.querySelector("[data-situacao-da-copia]");
    if (!situacao || !navigator.clipboard) return;
    var escrever = navigator.clipboard.writeText.bind(navigator.clipboard);
    document.querySelectorAll("[data-copiar]").forEach(function (botao) {
      var alvo = document.getElementById(botao.getAttribute("data-copiar"));
      var nome = document.getElementById(botao.getAttribute("aria-describedby"));
      if (alvo) ligar(botao, alvo, situacao, nome ? nome.textContent : "texto", escrever);
    });
  });
})();
