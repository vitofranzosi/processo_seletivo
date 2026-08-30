/* Confirmar antes de descartar trabalho não enviado (FR-038).

   "Remover este Perfil" eliminava a linha e tudo dentro dela — requisitos, modalidades,
   fundamentos, percentuais — sem confirmação, sem desfazer, e com o botão a poucos pixels de
   "↓ Descer". O produto é cuidadoso com atos irreversíveis de domínio e era descuidado com a perda
   de trabalho não enviado, que é a que acontece todo dia.

   **Linha vazia não confirma.** Perguntar onde não há nada a perder transforma a confirmação em
   ruído, e ruído é o que faz as pessoas clicarem "sim" sem ler. A pergunta só aparece quando há o
   que descartar: algum campo preenchido ou algum item filho.

   Por que interceptar no `htmx:confirm` e não no clique: a remoção é uma requisição HTMX, e
   cancelar o clique deixaria a requisição em andamento. `htmx:confirm` é o ponto em que a
   biblioteca oferece a decisão antes de disparar. */
(function () {
  var IGNORADOS = ["hidden", "submit", "button"];

  /* Campos da linha que representam conteúdo digitado. O `id` oculto e os botões não contam:
     eles existem em toda linha, inclusive na recém-criada que ninguém tocou. */
  function preenchidos(linha) {
    var campos = linha.querySelectorAll("input, textarea, select");
    return [].filter.call(campos, function (campo) {
      if (IGNORADOS.indexOf(campo.type) >= 0) return false;
      if (campo.type === "checkbox" || campo.type === "radio") return campo.checked;
      // `order` é mantido pelo próprio script de ordenação e nunca está vazio.
      if (campo.name && /-order$/.test(campo.name)) return false;
      // Um `select` no primeiro valor é a ausência de escolha, não uma escolha.
      if (campo.tagName === "SELECT") return campo.selectedIndex > 0;
      return String(campo.value || "").trim() !== "";
    }).length;
  }

  /* Itens filhos — uma Modalidade dentro de um Perfil. Remover o Perfil leva a Modalidade junto,
     e é justamente o caso em que a perda é maior e menos visível. */
  function filhos(linha) {
    return linha.querySelectorAll("fieldset").length;
  }

  function descricao(linha) {
    var legenda = linha.querySelector(":scope > legend");
    return legenda ? legenda.dataset.rotulo || legenda.textContent.trim() : "esta linha";
  }

  document.addEventListener("htmx:confirm", function (evento) {
    var botao = evento.detail && evento.detail.elt;
    if (!botao || !botao.classList || !botao.classList.contains("perigo")) return;
    var linha = botao.closest("fieldset");
    if (!linha) return;

    var campos = preenchidos(linha);
    var sublinhas = filhos(linha);
    if (!campos && !sublinhas) return; // Nada a perder: remove direto.

    evento.preventDefault();
    var perdas = [];
    if (campos) perdas.push(campos === 1 ? "1 campo preenchido" : campos + " campos preenchidos");
    if (sublinhas) perdas.push(sublinhas === 1 ? "1 item" : sublinhas + " itens");

    // `confirm` tem o cancelamento como ação padrão, é operável por teclado e é anunciado por
    // leitor de tela sem markup próprio. Um diálogo desenhado à mão teria de reconquistar os três.
    if (window.confirm("Remover " + descricao(linha) + "? Isto descarta " + perdas.join(" e ") +
        ", e não pode ser desfeito.")) {
      evento.detail.issueRequest();
    }
  });
})();
