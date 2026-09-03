/* Marcar de uma vez as inscrições desta página (FR-049).

   Sem isto, distribuir 600 inscrições à mão custava 25 marcações por página em 24 páginas — cerca
   de 600 cliques só para dizer "estas". O caminho continua sendo o mesmo formulário e as mesmas
   caixas; o que muda é quantas vezes a pessoa precisa apontar para dizer a mesma coisa.

   **Progressivo de propósito.** O controle é criado aqui, e não no template: sem JavaScript não
   aparece caixa nenhuma, e as marcações individuais continuam funcionando exatamente como antes.
   Um controle que existe no HTML e só funciona com script é pior que não existir, porque promete.

   O estado indeterminado é usado quando parte das linhas está marcada, e não uma terceira caixa:
   é o que o leitor de tela anuncia como "parcialmente marcado", que é o que de fato acontece. */
(function () {
  var tabela = document.querySelector("[data-selecionavel]");
  if (!tabela) return;

  var caixas = [].slice.call(tabela.querySelectorAll('tbody input[type="checkbox"]'));
  if (caixas.length < 2) return;

  var cabecalho = tabela.querySelector("thead th");
  if (!cabecalho) return;

  var todas = document.createElement("input");
  todas.type = "checkbox";
  todas.id = "selecionar-todas";
  var rotulo = document.createElement("label");
  rotulo.htmlFor = todas.id;
  rotulo.className = "oculto";
  rotulo.textContent = "Selecionar as " + caixas.length + " inscrições desta página";

  cabecalho.textContent = "";
  cabecalho.appendChild(todas);
  cabecalho.appendChild(rotulo);

  function sincronizar() {
    var marcadas = caixas.filter(function (caixa) {
      return caixa.checked;
    }).length;
    todas.checked = marcadas === caixas.length;
    todas.indeterminate = marcadas > 0 && marcadas < caixas.length;
  }

  todas.addEventListener("change", function () {
    caixas.forEach(function (caixa) {
      caixa.checked = todas.checked;
    });
    todas.indeterminate = false;
  });

  caixas.forEach(function (caixa) {
    caixa.addEventListener("change", sincronizar);
  });

  sincronizar();
})();
