/* A máscara do telefone, e a recusa antes do envio.

   O campo aceitava qualquer coisa: `28934` era gravado como telefone. Um número errado custa a
   vaga — a comissão liga, não encontra ninguém e conclui que a pessoa desistiu.

   A máscara é escrita enquanto a pessoa digita, e não depois: ver `(27) 99999-` aparecendo diz o
   formato esperado sem nenhuma instrução escrita. O servidor continua decidindo — `telefone_valido`
   recusa o que não tiver dez ou onze dígitos, com ou sem este arquivo — e a mensagem aqui é a
   mesma que ele devolveria.

   Apagar continua funcionando: a máscara é recalculada a partir dos dígitos, então o cursor nunca
   fica preso atrás de um parêntese que a pessoa não consegue remover. */
(function () {
  var campo = document.getElementById("telefone");
  if (!campo) {
    return;
  }

  function digitos(valor) {
    return (valor || "").replace(/\D/g, "").slice(0, 11);
  }

  function mascarar(numero) {
    if (numero.length <= 2) {
      return numero.length ? "(" + numero : "";
    }
    if (numero.length <= 6) {
      return "(" + numero.slice(0, 2) + ") " + numero.slice(2);
    }
    if (numero.length <= 10) {
      return "(" + numero.slice(0, 2) + ") " + numero.slice(2, 6) + "-" + numero.slice(6);
    }
    return "(" + numero.slice(0, 2) + ") " + numero.slice(2, 7) + "-" + numero.slice(7);
  }

  function conferir() {
    var numero = digitos(campo.value);
    var vazio = numero.length === 0;
    var completo = numero.length === 10 || numero.length === 11;
    campo.setCustomValidity(
      vazio || completo ? "" : "Informe o telefone com DDD, como (27) 99999-0000 — ou deixe em branco."
    );
    if (!vazio && !completo) {
      campo.setAttribute("aria-invalid", "true");
    } else {
      campo.removeAttribute("aria-invalid");
    }
  }

  campo.addEventListener("input", function () {
    var noFim = campo.selectionStart === campo.value.length;
    campo.value = mascarar(digitos(campo.value));
    if (noFim) {
      campo.setSelectionRange(campo.value.length, campo.value.length);
    }
    conferir();
  });
  campo.addEventListener("blur", conferir);
  conferir();
})();
