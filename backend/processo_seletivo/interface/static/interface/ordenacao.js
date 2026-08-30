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

  /* A ordem é o dado que se está editando, e era o único que não aparecia: vivia num campo
     oculto, e toda linha se anunciava igual à anterior — "EVENTO DO CRONOGRAMA", "EVENTO DO
     CRONOGRAMA". O documento imprime "1. Inscrições"; o editor, não (FR-035). */
  function rotular(lista, linha, indice, total) {
    /* `:scope >`: a linha de Etapa tem um segundo `legend`, o do grupo "Caráter". Sem o escopo,
       a numeração iria parar no rótulo errado se a ordem dos blocos mudasse. */
    var legenda = linha.querySelector(":scope > legend");
    if (!legenda) return;
    var base = legenda.dataset.rotulo || legenda.textContent.trim();
    legenda.dataset.rotulo = base;
    legenda.textContent = base + " " + (indice + 1) + " de " + total;
  }

  /* Botão inerte é pior do que botão ausente: clicar em "Subir" na primeira linha não mudava
     nada, não dizia nada, e o controle continuava com aparência de disponível (FR-035). */
  function extremidades(linha, indice, total) {
    var cima = linha.querySelector('[data-mover="cima"]');
    var baixo = linha.querySelector('[data-mover="baixo"]');
    if (cima) cima.disabled = indice === 0;
    if (baixo) baixo.disabled = indice === total - 1;
  }

  function renumerar(lista) {
    var atuais = linhas(lista);
    atuais.forEach(function (linha, indice) {
      var campo = linha.querySelector('[name$="-order"]');
      if (campo) campo.value = String(indice + 1);
      rotular(lista, linha, indice, atuais.length);
      extremidades(linha, indice, atuais.length);
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
        //
        // Quando a linha chega à ponta, o próprio botão acionado fica desabilitado — e focar um
        // controle desabilitado devolve o foco ao body, que é o defeito que esta linha evita.
        // Nesse caso o foco vai para o botão oposto, que continua operável.
        if (botao.disabled) {
          var oposto = linha.querySelector(
            botao.dataset.mover === "cima" ? '[data-mover="baixo"]' : '[data-mover="cima"]'
          );
          if (oposto && !oposto.disabled) oposto.focus();
        } else {
          botao.focus();
        }
      }
    });
  });
})();
