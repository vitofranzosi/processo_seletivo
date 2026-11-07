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

  var regras = { valoresDesabilitados: valoresDesabilitados };
  if (typeof module === "object" && module.exports) module.exports = regras;
  if (typeof document === "undefined") return;

  /** Os elementos que o `hx-include` nomeia: seletor CSS, ou `closest X` a partir do botão. */
  function alcancados(origem, seletor) {
    var elementos = [];
    seletor.split(",").forEach(function (parte) {
      parte = parte.trim();
      if (!parte) return;
      if (parte.indexOf("closest ") === 0) {
        var perto = origem.closest(parte.slice("closest ".length));
        if (perto) elementos.push(perto);
        return;
      }
      [].push.apply(elementos, document.querySelectorAll(parte));
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
    valoresDesabilitados(controlesDe(alcancados(origem, portador.getAttribute("hx-include"))))
      .forEach(function (par) {
        dados.append(par[0], par[1]);
      });
  });
})();
