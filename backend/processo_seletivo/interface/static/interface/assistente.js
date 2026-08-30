/* Comportamento das listas dinâmicas do assistente: o contador e o foco.

   O contador é renderizado pelo servidor, mas o HTMX troca apenas a lista — sem isto,
   acrescentar um Perfil mantém "0 Perfis" na tela até recarregar.

   O foco importa tanto quanto: a linha nova entra ANTES do botão que a criou, então quem
   navega por teclado tabularia para frente e pularia o que acabou de acrescentar; e o botão
   "Remover" sai do documento junto com a linha, deixando o foco no BODY — de volta ao topo,
   com todo o formulário para retravessar (WCAG 2.4.3).

   Um MutationObserver responde às três coisas: ele enxerga a mudança independentemente de
   como ela aconteceu, e distingue inserção de remoção. Escutar `htmx:afterSwap` não serviria
   para a remoção, porque o evento dispara no fieldset já desconectado e nunca chega ao body. */
(function () {
  function primeiroCampo(elemento) {
    return elemento && elemento.querySelector("input:not([type=hidden]), select, textarea");
  }

  document.querySelectorAll("[data-contador]").forEach(function (alvo) {
    var lista = document.querySelector(alvo.dataset.contador);
    if (!lista) return;
    var acrescentar = document.querySelector('[hx-target="' + alvo.dataset.contador + '"]');

    function atualizar() {
      var total = lista.querySelectorAll(alvo.dataset.item).length;
      var forte = document.createElement("strong");
      forte.textContent = total;
      var palavra = total === 1 ? alvo.dataset.singular : alvo.dataset.plural;
      alvo.querySelector("span").replaceChildren(forte, " " + palavra);
    }

    function reposicionarFoco(registro) {
      var inserida = [].find.call(registro.addedNodes, function (no) {
        return no.nodeType === Node.ELEMENT_NODE;
      });
      if (inserida) {
        var campo = primeiroCampo(inserida);
        if (campo) campo.focus();
        return;
      }
      // Só assume o foco quando ele se perdeu com a linha removida.
      if (registro.removedNodes.length && document.activeElement === document.body) {
        var restantes = lista.querySelectorAll(alvo.dataset.item);
        var destino = restantes.length
          ? primeiroCampo(restantes[restantes.length - 1])
          : acrescentar;
        if (destino) destino.focus();
      }
    }

    new MutationObserver(function (registros) {
      atualizar();
      registros.forEach(reposicionarFoco);
    }).observe(lista, { childList: true });
    atualizar();
  });
})();
