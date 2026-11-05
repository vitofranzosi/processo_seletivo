/* A correção da convocação (120): o que o vencimento informado faz com o prazo.

   A prévia da correção é do próprio formulário (D-008), e a única parte dela que depende do que se
   digita é esta: o vencimento novo estende, antecipa ou mantém o atual (FR-3844). Sem este script,
   a região diz as três regras, e o resultado do ato, calculado no servidor, diz qual se aplicou.

   **A comparação é de texto**, e vale porque os dois lados estão no formato do `datetime-local`
   (`AAAA-MM-DDTHH:MM`) e no fuso da instituição: o vencimento atual vem em `data-vencimento-atual`,
   e o fim de cada Evento do Cronograma em `data-fim`, os dois escritos pelo servidor nesse formato.
   Um `Date` aqui leria o fuso do navegador, que não é o do Edital. */
(function () {
  var ESTENDE = "O prazo é estendido até ";
  var ANTECIPA = "O prazo é antecipado para ";
  var ENCURTA = ": um vencimento anterior ao atual encurta um prazo já comunicado.";
  var MANTEM = "O vencimento é mantido: a correção muda só o fundamento, o complemento e a comunicação.";

  /* `AAAA-MM-DDTHH:MM` por extenso, como a tela escreve os instantes. */
  function porExtenso(valor) {
    var partes = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(valor || "");
    if (!partes) return valor;
    return partes[3] + "/" + partes[2] + "/" + partes[1] + " às " + partes[4] + "h" + partes[5];
  }

  /* O efeito do vencimento informado sobre o atual, ou `null` quando nada foi informado. */
  function efeito(atual, informado) {
    var novo = (informado || "").slice(0, 16);
    if (!novo || !atual) return null;
    if (novo > atual) return { chave: "estendido", frase: ESTENDE + porExtenso(novo) + "." };
    if (novo < atual) return { chave: "antecipado", frase: ANTECIPA + porExtenso(novo) + ENCURTA };
    return { chave: "mantido", frase: MANTEM };
  }

  /* O valor informado: o fim do Evento escolhido, ou o campo digitado. O Evento tem precedência,
     como no servidor (`resolver_vencimento`). */
  function informado(campo, evento) {
    if (evento && evento.value) {
      var opcao = evento.options[evento.selectedIndex];
      return (opcao && opcao.getAttribute("data-fim")) || "";
    }
    return campo ? campo.value : "";
  }

  /* Liga um formulário. Os elementos são parâmetros, para o teste. */
  function ligar(formulario, campo, evento, regiao) {
    var atual = formulario.getAttribute("data-vencimento-atual");
    var regras = regiao.textContent;
    function atualizar() {
      var resultado = efeito(atual, informado(campo, evento));
      regiao.textContent = resultado ? resultado.frase : regras;
    }
    if (campo) campo.addEventListener("input", atualizar);
    if (evento) evento.addEventListener("change", atualizar);
    atualizar();
    return atualizar;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { efeito: efeito, porExtenso: porExtenso, ligar: ligar, ESTENDE: ESTENDE, ANTECIPA: ANTECIPA, MANTEM: MANTEM };
    return;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var formularios = document.querySelectorAll("form[data-correcao]");
    for (var i = 0; i < formularios.length; i++) {
      var formulario = formularios[i];
      var regiao = formulario.querySelector("[data-efeito-do-vencimento]");
      if (!regiao) continue;
      ligar(
        formulario,
        formulario.querySelector("input[name=vencimento]"),
        formulario.querySelector("select[name=evento]"),
        regiao
      );
    }
  });
})();
