/* A etapa Cronograma (144): a visibilidade de cada Evento no PDF.

   **O dado é o campo oculto `evento-N-shownInPdf`, e o olho só o alterna** (D-007). A visibilidade
   viaja com o formulário como qualquer campo: é gravada com a etapa, reexibida na recusa e guardada
   pelo rascunho local. Nenhum pedido sai daqui.

   **Alterar `value` por código não emite evento**, e por isso a alternância despacha `change` no
   campo: sem isso, o rascunho local não perceberia a mudança e a pessoa a perderia ao fechar a aba
   — o defeito que o rascunho existe para evitar.

   O botão sai do servidor com `hidden` e é este script que o revela: sem ele, o olho não faria nada,
   e botão inerte é pior do que botão ausente. A linha acrescentada pelo HTMX também nasce com ele
   escondido, e a mutação da lista o revela. */
(function () {
  "use strict";

  /* O que o cartão diz em cada estado. Uma tabela só, lida pela montagem e pelo teste: o nome do
     botão é constante ("Ocultar do PDF") e o estado mora em `aria-pressed`, que é como um botão de
     alternância se anuncia; o `title` o diz em palavras a quem passa o mouse (UX-390). */
  function estado(exibido) {
    return {
      valor: exibido ? "true" : "false",
      pressionado: exibido ? "false" : "true",
      titulo: exibido ? "Exibido no PDF — ocultar" : "Oculto do PDF — exibir",
      marcaVisivel: !exibido,
    };
  }

  var regras = { estado: estado };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var formulario = document.getElementById("formulario");
  var lista = document.getElementById("eventos");
  if (!formulario || !lista) return;

  function revelar(raiz) {
    [].forEach.call(raiz.querySelectorAll("[data-visibilidade-no-pdf]"), function (botao) {
      botao.hidden = false;
    });
  }

  function aplicar(cartao, exibido) {
    var novo = estado(exibido);
    var campo = cartao.querySelector("[data-campo-visibilidade-no-pdf]");
    var botao = cartao.querySelector("[data-visibilidade-no-pdf]");
    var marca = cartao.querySelector("[data-marca-pdf]");
    if (campo) campo.value = novo.valor;
    if (botao) {
      botao.setAttribute("aria-pressed", novo.pressionado);
      botao.title = novo.titulo;
    }
    if (marca) marca.hidden = !novo.marcaVisivel;
    cartao.classList.toggle("oculto-do-pdf", !exibido);
    if (campo) campo.dispatchEvent(new Event("change", { bubbles: true }));
  }

  lista.addEventListener("click", function (evento) {
    var botao = evento.target.closest("[data-visibilidade-no-pdf]");
    if (!botao || !lista.contains(botao)) return;
    var cartao = botao.closest("fieldset");
    var campo = cartao && cartao.querySelector("[data-campo-visibilidade-no-pdf]");
    if (!campo) return;
    aplicar(cartao, campo.value === "false");
  });

  revelar(lista);
  if (typeof MutationObserver === "function") {
    new MutationObserver(function (registros) {
      registros.forEach(function (registro) {
        [].forEach.call(registro.addedNodes, function (no) {
          if (no.nodeType === Node.ELEMENT_NODE) revelar(no);
        });
      });
    }).observe(lista, { childList: true });
  }
})();
