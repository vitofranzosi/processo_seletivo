/* Guardar a escolha de modalidade na hora.
 *
 * A escolha decide quais documentos são pedidos, e antes ela só era gravada ao avançar: quem
 * escolhia a modalidade reservada continuava vendo a lista antiga e o aviso de "todos enviados",
 * e descobria o terceiro documento na revisão — quando já se considerava pronto. Quem saía e
 * voltava reencontrava o campo em branco.
 *
 * Submete o formulário que já existe, com `acao=guardar`; o servidor grava e devolve a página
 * recarregada. Sem JavaScript, nada disso acontece e nada quebra: a escolha é gravada ao clicar
 * em "Revisar inscrição", como sempre foi.
 */
(function () {
  "use strict";
  var campo = document.querySelector("select[data-guardar]");
  if (!campo || !campo.form) return;

  campo.addEventListener("change", function () {
    if (!campo.value) return;
    var acao = document.createElement("input");
    acao.type = "hidden";
    acao.name = "acao";
    acao.value = "guardar";
    campo.form.appendChild(acao);
    campo.form.submit();
  });
})();
