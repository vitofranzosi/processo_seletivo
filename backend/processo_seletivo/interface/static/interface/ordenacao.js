/* Mover uma linha para cima ou para baixo, e manter o campo `order` de acordo (FR-003).

   O campo é a parte que importa. `interface/forms.py` recolhe os índices do formulário em um
   conjunto e os devolve ordenados numericamente: a posição da linha no documento é descartada
   antes da leitura. Mover a linha só na tela produziria o pior defeito possível — a tela mostrando
   a ordem nova e o banco guardando a antiga, sem nada acusando.

   Por isso não há renumeração dos nomes dos campos. Renumerar `evento-0-…`, `evento-1-…` ao mover
   faria a correção do formulário depender de o cliente e o parser concordarem sobre uma convenção
   implícita, e quebraria em silêncio quando uma remoção deixasse buraco entre os índices. A ordem
   viaja como dado, e o índice continua sendo apenas o agrupador de campos daquela linha.

   Botões, e não arrastar: arrastar depende de biblioteca ou de muito código próprio, e degrada em
   teclado e em leitor de tela. */
(function () {
  function linhas(lista) {
    return [].filter.call(lista.children, function (no) {
      return no.nodeType === Node.ELEMENT_NODE;
    });
  }

  function renumerar(lista) {
    linhas(lista).forEach(function (linha, indice) {
      var campo = linha.querySelector('[name$="-order"]');
      if (campo) campo.value = String(indice + 1);
    });
  }

  function mover(lista, linha, direcao) {
    var atuais = linhas(lista);
    var posicao = atuais.indexOf(linha);
    var destino = posicao + direcao;
    if (posicao < 0 || destino < 0 || destino >= atuais.length) return false;
    if (direcao < 0) lista.insertBefore(linha, atuais[destino]);
    else lista.insertBefore(atuais[destino], linha);
    renumerar(lista);
    return true;
  }

  document.querySelectorAll("[data-ordenavel]").forEach(function (lista) {
    // Também na carga e a cada mutação: a linha acrescentada pelo HTMX nasce sem ordem, e a
    // removida deixaria buraco na numeração.
    renumerar(lista);
    if (typeof MutationObserver === "function") {
      new MutationObserver(function () {
        renumerar(lista);
      }).observe(lista, { childList: true });
    }

    lista.addEventListener("click", function (evento) {
      var botao = evento.target.closest("[data-mover]");
      if (!botao || !lista.contains(botao)) return;
      var linha = botao.closest("fieldset");
      if (!linha) return;
      if (mover(lista, linha, botao.dataset.mover === "cima" ? -1 : 1)) {
        // O foco acompanha o botão acionado: sem isto ele volta ao body a cada movimento, e
        // reordenar por teclado exigiria retravessar o formulário inteiro entre dois cliques.
        botao.focus();
      }
    });
  });
})();
