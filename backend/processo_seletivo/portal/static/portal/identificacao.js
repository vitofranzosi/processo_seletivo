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

  function digitosDe(valor) {
    return (valor || "").replace(/\D/g, "").slice(0, 11);
  }

  function mascarar(numero) {
    if (numero.length <= 3) {
      return numero;
    }
    if (numero.length <= 6) {
      return numero.slice(0, 3) + "." + numero.slice(3);
    }
    if (numero.length <= 9) {
      return numero.slice(0, 3) + "." + numero.slice(3, 6) + "." + numero.slice(6);
    }
    return (
      numero.slice(0, 3) + "." + numero.slice(3, 6) + "." + numero.slice(6, 9) + "-" + numero.slice(9)
    );
  }

  /* Os dígitos verificadores, e não só a contagem — o mesmo cálculo de
     `inscricoes/domain/pessoais.cpf_valido`, e a mesma mensagem. Contar onze dígitos aceitava
     `11111111111`, e um CPF inventado produz uma identidade que a pessoa não reencontra depois. */
  function eCpf(numero) {
    if (numero.length !== 11 || /^(\d)\1{10}$/.test(numero)) {
      return false;
    }
    for (var tamanho = 9; tamanho <= 10; tamanho++) {
      var soma = 0;
      for (var i = 0; i < tamanho; i++) {
        soma += parseInt(numero.charAt(i), 10) * (tamanho + 1 - i);
      }
      var resto = (soma * 10) % 11;
      if ((resto === 10 ? 0 : resto) !== parseInt(numero.charAt(tamanho), 10)) {
        return false;
      }
    }
    return true;
  }

  function conferirCpf() {
    var numero = digitosDe(cpf.value);
    if (!cpf.value.trim()) {
      marcar(cpf, "");
      return;
    }
    if (numero.length !== 11) {
      marcar(cpf, "Informe um CPF com 11 dígitos.");
      return;
    }
    marcar(cpf, eCpf(numero) ? "" : "Este CPF não existe. Confira os números digitados.");
  }

  if (cpf) {
    cpf.addEventListener("input", function () {
      var noFim = cpf.selectionStart === cpf.value.length;
      cpf.value = mascarar(digitosDe(cpf.value));
      if (noFim) {
        cpf.setSelectionRange(cpf.value.length, cpf.value.length);
      }
      conferirCpf();
    });
    cpf.addEventListener("blur", conferirCpf);
  }
  formulario.addEventListener("submit", conferirCpf);
})();
