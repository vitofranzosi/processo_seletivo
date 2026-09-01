/* O nome do arquivo escolhido, ao lado do botão.

   O `input[type=file]` do navegador é o elemento mais feio de qualquer formulário, e por isso ele
   sai de vista e o `label` assume a aparência de botão. Só que o navegador escrevia ali o nome do
   arquivo escolhido, e escondê-lo tirava a única confirmação de que a escolha aconteceu — a pessoa
   escolheria o arquivo e não veria nada mudar.

   Este script devolve essa confirmação. Sem ele, o texto padrão diz o que fazer em vez de
   descrever um estado que ninguém conseguiria ver: o envio continua funcionando, e o pior que
   acontece é a pessoa não ler o nome do que escolheu antes de enviar. */
(function () {
  var padrao = "Nenhum arquivo escolhido";

  function ligar(campo) {
    var alvo = campo.closest(".escolher").querySelector("[data-nome-do-arquivo]");
    if (!alvo) {
      return;
    }
    var enviar = campo.form ? campo.form.querySelector("button[type=submit]") : null;
    campo.addEventListener("change", function () {
      var escolhido = campo.files && campo.files.length ? campo.files[0].name : "";
      alvo.textContent = escolhido || padrao;
      alvo.classList.toggle("escolhido", Boolean(escolhido));
      /* O botão só ganha peso quando há o que enviar: antes disso a ação principal da tela é
         `Revisar inscrição`, e dois botões sólidos disputariam a mesma decisão (SC-UX-008). */
      if (enviar) {
        enviar.classList.toggle("pronta", Boolean(escolhido));
      }
    });
  }

  function ligarTodos(raiz) {
    var campos = (raiz || document).querySelectorAll("[data-arquivo]");
    for (var i = 0; i < campos.length; i++) {
      ligar(campos[i]);
    }
  }

  ligarTodos(document);
  /* O bloco de documentos volta inteiro do servidor a cada envio, e o que voltou nunca passou por
     `ligarTodos`. Sem isto, escolher um arquivo funcionaria uma vez por carregamento de página. */
  document.body.addEventListener("htmx:afterSwap", function (evento) {
    ligarTodos(evento.target);
  });
})();
