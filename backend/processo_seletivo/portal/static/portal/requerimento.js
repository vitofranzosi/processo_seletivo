/* ENTER avança para o campo seguinte, e não envia o formulário (029).

   **O que acontecia sem este arquivo.** Num formulário com dois botões de envio, o navegador trata
   ENTER como clique no **primeiro** deles — que aqui é `Guardar e continuar depois`. Quem apertasse
   ENTER no quinto campo, por reflexo de quem preenche formulário, era levado embora da tela no meio
   do preenchimento. Não perdia o que digitou, porque guardar grava; perdia o lugar, a rolagem e a
   linha de raciocínio, e voltava sem saber por quê.

   **Por que avançar, e não apenas impedir.** Impedir seria corrigir o defeito e deixar a tecla
   morta — e num formulário de vinte campos ENTER é o que a mão faz. Avançar é o que quem preenche
   espera, e é o comportamento que planilha, caixa eletrônico e formulário de balcão ensinaram.

   **O que NÃO é tocado.** A área de texto, onde ENTER é quebra de linha e não navegação. A caixa
   de aceite, onde ENTER é o gesto de marcar. E os botões, onde ENTER é o clique — quem chega ao
   `Enviar requerimento` pelo teclado precisa poder acioná-lo assim.

   **O TAB continua sendo o TAB.** Este arquivo não reordena nada e não escreve `tabindex`: a ordem
   de foco é a ordem do documento, que é a ordem visual. Quem navega por leitor de tela encontra
   exatamente o que encontraria sem o script — e é por isso que a página funciona com ele bloqueado.
*/
(function () {
  var formulario = document.getElementById("formulario-do-requerimento");
  if (!formulario) {
    return;
  }

  /* O que ENTER faz, por tipo de controle. Três respostas, e nenhuma delas é "enviar".

     `passa`   — a tecla é do navegador: quebra linha na área de texto, aciona o botão.
     `avanca`  — vai para o campo seguinte, que é o caso dos vinte campos.
     `segura`  — não faz nada, e principalmente **não envia**.

     `segura` existe para a caixa de aceite. Ela é o último controle antes dos botões, e é onde a
     cadeia de ENTER termina: deixar a tecla passar ali faria o navegador acionar o primeiro botão
     de envio — que é `Guardar e continuar depois` — e a pessoa seria levada embora no gesto
     seguinte ao de ler a declaração. Aceitar é ato deliberado (`UX-056`): quem chegou aqui lê,
     marca com a barra de espaço, e vai ao botão pelo TAB. */
  function oQueEnterFaz(elemento) {
    if (!elemento || elemento.disabled || elemento.readOnly) {
      return "passa";
    }
    var etiqueta = nomeDe(elemento);
    if (etiqueta === "TEXTAREA" || etiqueta === "BUTTON") {
      return "passa";
    }
    if (etiqueta === "INPUT" && elemento.type === "submit") {
      return "passa";
    }
    if (etiqueta === "INPUT" && elemento.type === "checkbox") {
      return "segura";
    }
    return etiqueta === "INPUT" || etiqueta === "SELECT" ? "avanca" : "passa";
  }

  /* **`form.elements` traz o `<fieldset>` junto dos controles**, e é a armadilha deste arquivo: a
     primeira redação passava o foco para a caixa do grupo, que não o aceita, e a cadeia parava no
     último campo de cada seção — ENTER funcionava dentro de *Sobre você* e morria ao chegar em
     *Filiação*. A lista abaixo é de controles, e não de "o que a coleção do formulário devolve". */
  var CONTROLES = ["INPUT", "SELECT", "TEXTAREA", "BUTTON"];

  /* **`tagName` normalizado, e a razão não é preciosismo.** O DOM devolve o nome em maiúsculas para
     elemento HTML; o shim que executa estes scripts fora do navegador devolve em minúsculas. Um
     script que compara com literal maiúsculo funciona no navegador e **passa reto** no teste — que
     é a pior das duas falhas, porque ela aprova calada. */
  function nomeDe(elemento) {
    return String(elemento.tagName || "").toUpperCase();
  }

  function focaveis() {
    return Array.prototype.filter.call(formulario.elements, function (elemento) {
      if (CONTROLES.indexOf(nomeDe(elemento)) === -1) {
        return false;
      }
      if (elemento.type === "hidden" || elemento.disabled) {
        return false;
      }
      /* Campo escondido por qualquer razão não recebe foco: mandar o foco para o que não se vê é
         pior do que não mover — a pessoa digita e não vê onde. */
      return elemento.offsetParent !== null || nomeDe(elemento) === "SELECT";
    });
  }

  formulario.addEventListener("keydown", function (evento) {
    if (evento.key !== "Enter" || evento.shiftKey || evento.ctrlKey || evento.metaKey) {
      return;
    }
    var acao = oQueEnterFaz(evento.target);
    if (acao === "passa") {
      return;
    }
    /* Prevenido nos dois casos restantes: é isto que impede o envio acidental, e é a metade da
       correção que importa mais do que o avanço. */
    evento.preventDefault();
    if (acao === "segura") {
      return;
    }
    var lista = focaveis();
    var posicao = lista.indexOf(evento.target);
    var seguinte = lista[posicao + 1];
    if (!seguinte) {
      return;
    }
    seguinte.focus();
    /* O cursor no fim do que já estava escrito, e não selecionando tudo: quem avança para um campo
       pré-preenchido quer **conferir** e corrigir a ponta, não apagar com a primeira tecla. */
    if (typeof seguinte.setSelectionRange === "function" && seguinte.type === "text") {
      var fim = seguinte.value.length;
      try {
        seguinte.setSelectionRange(fim, fim);
      } catch (erro) {
        /* Alguns tipos de campo recusam seleção; mover o foco já é o essencial. */
      }
    }
  });
})();
