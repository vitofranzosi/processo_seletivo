/* A Classificação em somente leitura ainda simula (132, FR-4507, D-004).

   Em somente leitura, cada campo da etapa sai desabilitado. Os botões que só leem — "Simular
   classificação", "Simular sorteio", "Conferir na Caixa" e os da prévia aberta — continuam ativos,
   e pedem os valores do cartão pelo `hx-include`. Mas o htmx não leva campo desabilitado no pedido:
   sem este script, quem homologa simularia um marco vazio e leria "sem marco".

   O script devolve ao pedido, e só a ele, o valor de cada campo desabilitado que o `hx-include` do
   botão alcança. Não habilita campo nenhum: o que a tela mostra continua sem aceitar digitação. É
   carregado só quando a etapa é somente leitura, e só a Classificação o carrega — nas outras etapas
   não há botão que leia campo.

   A regra que escolhe os valores é pura e exportada para `node --test`; a ligação com o htmx se
   verifica no navegador. */
(function () {
  "use strict";

  /** O que um campo desabilitado mandaria se não estivesse desabilitado: `[nome, valor]` por valor. */
  function valoresDesabilitados(controles) {
    var pares = [];
    controles.forEach(function (controle) {
      if (!controle.disabled || !controle.name) return;
      var tipo = controle.type;
      if (tipo === "button" || tipo === "submit" || tipo === "reset" || tipo === "file") return;
      if ((tipo === "checkbox" || tipo === "radio") && !controle.checked) return;
      if (controle.options && controle.multiple) {
        [].forEach.call(controle.options, function (opcao) {
          if (opcao.selected) pares.push([controle.name, opcao.value]);
        });
        return;
      }
      pares.push([controle.name, controle.value]);
    });
    return pares;
  }

  /** O `hx-include` em partes: `{modo, css}`, com os modos estendidos do htmx (revisão do #429).

      `this`, `closest X`, `find X`, `next X` e `previous X` são relativos ao elemento que declara o
      atributo; o resto é seletor CSS do documento. Lido só como CSS, `find .marco` ia ao
      `querySelectorAll` e quebrava o pedido em silêncio. */
  function interpretar(seletor) {
    var partes = [];
    (seletor || "").split(",").forEach(function (parte) {
      parte = parte.trim();
      if (!parte) return;
      if (parte === "this") {
        partes.push({ modo: "this", css: "" });
        return;
      }
      var modo = /^(closest|find|next|previous)\s+(.+)$/.exec(parte);
      if (modo) partes.push({ modo: modo[1], css: modo[2].trim() });
      else partes.push({ modo: "documento", css: parte });
    });
    return partes;
  }

  var regras = { valoresDesabilitados: valoresDesabilitados, interpretar: interpretar };
  if (typeof module === "object" && module.exports) module.exports = regras;
  if (typeof document === "undefined") return;

  /** Os elementos que o `hx-include` nomeia, a partir de quem o declara. */
  function alcancados(portador, seletor) {
    var elementos = [];
    interpretar(seletor).forEach(function (parte) {
      try {
        if (parte.modo === "this") elementos.push(portador);
        else if (parte.modo === "closest") {
          var perto = portador.closest(parte.css);
          if (perto) elementos.push(perto);
        } else if (parte.modo === "find") {
          var dentro = portador.querySelector(parte.css);
          if (dentro) elementos.push(dentro);
        } else if (parte.modo === "next" || parte.modo === "previous") {
          var todos = [].slice.call(document.querySelectorAll(parte.css));
          var depois = parte.modo === "next";
          var achado = (depois ? todos : todos.reverse()).find(function (candidato) {
            var posicao = portador.compareDocumentPosition(candidato);
            return depois
              ? posicao & Node.DOCUMENT_POSITION_FOLLOWING
              : posicao & Node.DOCUMENT_POSITION_PRECEDING;
          });
          if (achado) elementos.push(achado);
        } else {
          [].push.apply(elementos, document.querySelectorAll(parte.css));
        }
      } catch (erro) {
        // Seletor que o navegador não entende: o htmx também o recusa, e o pedido segue sem ele.
      }
    });
    return elementos;
  }

  function controlesDe(elementos) {
    var controles = [];
    elementos.forEach(function (elemento) {
      if (elemento.matches("input, select, textarea")) controles.push(elemento);
      [].push.apply(controles, elemento.querySelectorAll("input, select, textarea"));
    });
    return controles;
  }

  document.addEventListener("htmx:configRequest", function (evento) {
    if (!document.querySelector("form[data-somente-leitura]")) return;
    var origem = evento.target;
    var portador = origem.closest && origem.closest("[hx-include]");
    if (!portador) return;
    var dados = evento.detail.formData;
    valoresDesabilitados(controlesDe(alcancados(portador, portador.getAttribute("hx-include"))))
      .forEach(function (par) {
        dados.append(par[0], par[1]);
      });
  });
})();
