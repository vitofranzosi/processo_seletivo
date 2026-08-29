/* O contador é renderizado pelo servidor, mas o HTMX troca apenas a lista.
   Sem isto, acrescentar um Perfil mantém "0 Perfis" na tela até recarregar.

   Observa o contêiner em vez de escutar htmx:afterSwap: na remoção o evento
   dispara no fieldset já desconectado do documento e nunca chega ao body. */
(function () {
  document.querySelectorAll("[data-contador]").forEach(function (alvo) {
    var lista = document.querySelector(alvo.dataset.contador);
    if (!lista) return;

    function atualizar() {
      var total = lista.querySelectorAll(alvo.dataset.item).length;
      var forte = document.createElement("strong");
      forte.textContent = total;
      var palavra = total === 1 ? alvo.dataset.singular : alvo.dataset.plural;
      alvo.querySelector("span").replaceChildren(forte, " " + palavra);
    }

    new MutationObserver(atualizar).observe(lista, { childList: true });
    atualizar();
  });
})();
