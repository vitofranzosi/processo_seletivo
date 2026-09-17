/* O preenchimento assistido por CEP (029, T030).

   **Isto é melhoria, e não regra.** Com o script bloqueado, a pessoa digita município e UF à mão e
   o envio conclui igual: quem decide o código IBGE é o servidor, que o deriva da referência e
   ignora o que o formulário mandar (FR-388). Este arquivo existe para poupar digitação, nunca para
   validar endereço.

   **Nada do candidato é guardado no navegador.** Guardar os CEPs já consultados seria a otimização
   óbvia — e é exatamente o que a varredura do canal do candidato existe para impedir. Ela percorre
   todo `.js` e `.html` do portal atrás das quatro formas de armazenamento local e alcança este
   arquivo automaticamente.

   Os nomes daquelas quatro APIs não são escritos aqui de propósito: **a varredura lê o comentário**.
   A primeira redação deste bloco as citava para explicar a proibição, e foi reprovada por prometer
   em prosa o que não fazia em código — uma armadilha que este repositório já pagou antes.

   **CEP não reconhecido abre os campos e não culpa quem digitou** (UX-055, FR-390). Base ausente,
   desatualizada ou sem aquele CEP são o mesmo caso para quem preenche, e nenhum deles impede o
   envio. A mensagem diz o que fazer — preencher à mão —, e não que o CEP está errado: ele pode
   estar certo e a base é que não o conhece. */
(function () {
  var cep = document.getElementById("cep");
  if (!cep) {
    return;
  }

  var rota = cep.getAttribute("data-rota-do-cep");
  var token = cep.getAttribute("data-csrf");
  /* Município e UF são somente leitura **enquanto** a referência responde, e voltam a abrir quando
     ela não responde. Não é o mesmo que derivado: o código IBGE nunca é editável, em nenhum dos
     dois casos, e por isso não aparece nesta lista nem em campo nenhum. */
  var FECHAM = ["municipio", "uf"];
  var SUGERIDOS = ["logradouro", "bairro"];
  var ultimo = "";

  function campo(nome) {
    return document.getElementById(nome);
  }

  function aviso() {
    return document.getElementById("aviso-do-cep");
  }

  function digitos(valor) {
    return (valor || "").replace(/\D/g, "").slice(0, 8);
  }

  function abrir() {
    FECHAM.forEach(function (nome) {
      var alvo = campo(nome);
      if (alvo) {
        alvo.removeAttribute("readonly");
        alvo.disabled = false;
      }
    });
  }

  /* **`readonly` não existe para `<select>`**, e foi assim que a UF continuou editável enquanto o
     município travava: o atributo era escrito, o navegador o ignorava, e o teste — que modelava a
     UF como `<input>` — nunca viu. Para a lista, o que fecha é `disabled`.

     Fechar a UF com `disabled` faz o campo **não** viajar no `POST`, e isso é inofensivo aqui: com
     o CEP reconhecido, quem decide município e UF é a referência, e o servidor os deriva dela
     ignorando o que o formulário mandar. É a mesma regra que já vale para o código IBGE. */
  function fechar() {
    FECHAM.forEach(function (nome) {
      var alvo = campo(nome);
      if (!alvo) {
        return;
      }
      if (String(alvo.tagName || "").toUpperCase() === "SELECT") {
        alvo.disabled = true;
      } else {
        alvo.setAttribute("readonly", "readonly");
      }
    });
  }

  function dizer(texto) {
    var caixa = aviso();
    if (caixa) {
      caixa.textContent = texto;
    }
  }

  function aplicar(resposta) {
    if (!resposta.conferido) {
      abrir();
      dizer("CEP não encontrado. Preencha o endereço à mão — isso não impede o envio.");
      return;
    }
    FECHAM.forEach(function (nome) {
      var alvo = campo(nome);
      if (alvo && resposta[nome]) {
        alvo.value = resposta[nome];
      }
    });
    /* Sugeridos, e não impostos: um CEP de logradouro traz o nome genérico da via, e quem mora lá
       às vezes o escreve melhor. Sobrescrever o que a pessoa digitou apagaria a correção dela uma
       tecla depois. */
    SUGERIDOS.forEach(function (nome) {
      var alvo = campo(nome);
      if (alvo && !alvo.value && resposta[nome]) {
        alvo.value = resposta[nome];
      }
    });
    fechar();
    dizer("Município e UF vieram do CEP.");
  }

  function consultar() {
    var numero = digitos(cep.value);
    if (numero.length !== 8 || numero === ultimo) {
      return;
    }
    ultimo = numero;
    var corpo = new FormData();
    corpo.append("cep", numero);
    corpo.append("csrfmiddlewaretoken", token);
    fetch(rota, { method: "POST", body: corpo, credentials: "same-origin" })
      .then(function (resposta) {
        return resposta.json();
      })
      .then(aplicar)
      .catch(function () {
        /* **A falha do serviço não pode travar ninguém** (FR-390). Rede fora, servidor fora,
           resposta ilegível — os três são o mesmo caso para quem preenche: os campos abrem e o
           envio segue. Um `catch` que exibisse erro técnico faria a pessoa achar que perdeu o
           formulário. */
        abrir();
        dizer("Não conseguimos consultar o CEP agora. Preencha à mão — isso não impede o envio.");
      });
  }

  cep.addEventListener("blur", consultar);
  cep.addEventListener("change", consultar);
})();
