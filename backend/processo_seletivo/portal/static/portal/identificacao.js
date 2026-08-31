/* Validação antes do envio, na identificação (L9 da auditoria de percurso).

   Isto NÃO é fronteira de segurança: `_recusas_da_identificacao` continua decidindo, e recusa
   exatamente as mesmas coisas. O que existe aqui é poupar uma ida ao servidor para descobrir o
   que já dava para saber na tela — e dizer **onde** está o problema, e não só que ele existe.

   Segue o padrão que a interface administrativa já usa: `setCustomValidity` faz o próprio
   navegador bloquear o envio, mover o foco para o campo e anunciar a mensagem pelo leitor de
   tela. Nada disso precisa ser reimplementado, e a mensagem é a mesma que o servidor devolveria —
   é o que impede a tela de ensinar uma gramática de erro e o servidor, outra.

   O `novalidate` do formulário sai daqui, e não do HTML: sem JavaScript o navegador volta a
   validar `required` e `type=email` sozinho, que é mais do que havia antes. */
(function () {
  var formulario = document.querySelector("[data-identificacao]");
  if (!formulario) {
    return;
  }
  var cpf = formulario.querySelector("#cpf");

  function marcar(elemento, mensagem) {
    if (!elemento) {
      return;
    }
    elemento.setCustomValidity(mensagem || "");
    if (mensagem) {
      elemento.setAttribute("aria-invalid", "true");
    } else {
      elemento.removeAttribute("aria-invalid");
    }
  }

  function conferirCpf() {
    var digitos = (cpf.value || "").replace(/\D/g, "");
    if (!cpf.value.trim()) {
      marcar(cpf, "");
      return;
    }
    marcar(cpf, digitos.length === 11 ? "" : "Informe um CPF com 11 dígitos.");
  }

  if (cpf) {
    cpf.addEventListener("input", conferirCpf);
    cpf.addEventListener("blur", conferirCpf);
  }
  formulario.addEventListener("submit", conferirCpf);
})();
