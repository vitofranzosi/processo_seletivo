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
      // A própria marcação de remoção não é conteúdo a perder. Na tela de Retificação o evento
      // chega **depois** de a caixa ficar marcada, então contá-la inflava o número anunciado:
      // "descarta 3 campos preenchidos" quando dois eram do usuário e o terceiro era o pedido.
      if (/^remover:/.test(campo.name || "")) return false;
      if (campo.type === "checkbox" || campo.type === "radio") return campo.checked;
      // `order` é mantido pelo próprio script de ordenação e nunca está vazio.
      if (campo.name && /-order$/.test(campo.name)) return false;
      // Um `select` no primeiro valor é a ausência de escolha, não uma escolha.
      if (campo.tagName === "SELECT") return campo.selectedIndex > 0;
      return String(campo.value || "").trim() !== "";
    }).length;
  }

  /* Itens filhos — uma Modalidade dentro de um Perfil. Remover o Perfil leva a Modalidade junto,
     e é justamente o caso em que a perda é maior e menos visível.

     `fieldset.linha`, e não qualquer `fieldset`: a linha de Etapa tem um `fieldset` **estrutural**,
     o do grupo "Caráter", e contá-lo fazia toda Etapa — inclusive a recém-criada e vazia — pedir
     confirmação. A regra é que linha vazia não pergunta, e um agrupamento de rótulo não é item. */
  function filhos(linha) {
    return linha.querySelectorAll("fieldset.linha").length;
  }

  function descricao(linha) {
    var legenda = linha.querySelector(":scope > legend");
    return legenda ? legenda.dataset.rotulo || legenda.textContent.trim() : "esta linha";
  }

  /* O que se perde ao descartar a linha, em palavras — ou vazio quando não há nada a perder. */
  function perda(linha) {
    var campos = preenchidos(linha);
    var sublinhas = filhos(linha);
    var partes = [];
    if (campos) partes.push(campos === 1 ? "1 campo preenchido" : campos + " campos preenchidos");
    if (sublinhas) partes.push(sublinhas === 1 ? "1 item" : sublinhas + " itens");
    return partes.join(" e ");
  }

  /* `confirm` tem o cancelamento como ação padrão, é operável por teclado e é anunciado por leitor
     de tela sem markup próprio. Um diálogo desenhado à mão teria de reconquistar os três. */
  function confirmar(linha, perdas) {
    return window.confirm(
      "Remover " + descricao(linha) + "? Isto descarta " + perdas + ", e não pode ser desfeito."
    );
  }

  /* Qualquer botão que remova a própria linha — e não só os marcados com `perigo`.

     Os fragmentos da Retificação usam "Não acrescentar este Perfil" e "Não acrescentar este
     Evento" **sem** a classe, e descartavam a linha inteira em silêncio. O que identifica a
     remoção não é a cor do botão: é o `hx-target` apontar para a própria linha e o `hx-swap`
     trocá-la por outra coisa. */
  function removeAPropriaLinha(botao) {
    if (botao.classList && botao.classList.contains("perigo")) return true;
    var alvo = botao.getAttribute && botao.getAttribute("hx-target");
    var troca = botao.getAttribute && botao.getAttribute("hx-swap");
    return alvo === "closest fieldset" && troca === "outerHTML";
  }

  document.addEventListener("htmx:confirm", function (evento) {
    var botao = evento.detail && evento.detail.elt;
    if (!botao || !removeAPropriaLinha(botao)) return;
    var linha = botao.closest("fieldset");
    if (!linha) return;

    var perdas = perda(linha);
    if (!perdas) return; // Nada a perder: remove direto.

    evento.preventDefault();
    if (confirmar(linha, perdas)) evento.detail.issueRequest();
  });

  /* A remoção na tela de Retificação não é requisição: é uma marcação que só tem efeito no envio.
     `htmx:confirm` nunca dispara ali, e "Remover do Edital" desmarcava o conteúdo de um Perfil
     publicado sem perguntar nada. Confirmar ao **marcar**; desmarcar não pergunta, porque desfazer
     não perde nada. */
  document.addEventListener("change", function (evento) {
    var caixa = evento.target;
    if (!caixa || caixa.type !== "checkbox" || !/^remover:/.test(caixa.name || "")) return;
    if (!caixa.checked) return;
    var linha = caixa.closest("fieldset");
    if (!linha) return;

    var perdas = perda(linha);
    if (!perdas) return;
    if (!confirmar(linha, perdas)) caixa.checked = false;
  });
})();
