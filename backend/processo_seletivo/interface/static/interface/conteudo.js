/* O número que cada seção terá no documento, acompanhando o que se digita (054, UX-130).

   O servidor desenha a etapa com o número do conteúdo gravado, pela mesma regra do compositor
   (`pdf.numeracao`). Digitar numa seção vazia faz ela — e todas as seguintes — mudarem de número,
   e a tela que dissesse o número gravado estaria errada até o próximo salvamento. Aqui só se refaz
   essa conta; nada é gravado, e nenhum campo é criado ou alterado.

   **A regra é a do compositor, e não uma segunda** (FR-985): cada seção declara, em `data-estado`,
   de que depende sair no documento — `sai` e `nao-sai` são decisões do servidor (a gerada pela
   coleção de origem, a textual pela norma que o sistema lhe acrescenta), e `texto` depende do
   campo. O preâmbulo sai sem número. Sem script, a tela fica com o número do conteúdo gravado.

   As regras puras vêm primeiro e são exportadas para `node --test`. */
(function () {
  "use strict";

  /* ── Regras ──────────────────────────────────────────────────────────────────────────────── */

  /** Se a seção sai no documento. */
  function sai(secao) {
    if (secao.estado === "sai") return true;
    if (secao.estado === "nao-sai") return false;
    return Boolean(String(secao.texto || "").trim());
  }

  /** O número de cada seção, na ordem: `null` quando não sai, `0` para o preâmbulo. */
  function numerar(secoes) {
    var proximo = 1;
    return secoes.map(function (secao) {
      if (!sai(secao)) return null;
      if (secao.preambulo) return 0;
      return proximo++;
    });
  }

  /** O que a legenda diz ao lado do título, para o número calculado. */
  function rotulos(numero) {
    if (numero === null) return { numero: "", estado: " (vazia — não sai no documento)" };
    if (numero === 0) return { numero: "", estado: " (preâmbulo, sem número)" };
    return { numero: numero + ". ", estado: "" };
  }

  var regras = { sai: sai, numerar: numerar, rotulos: rotulos };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var formulario = document.getElementById("formulario");
  if (!formulario) return;
  var conjuntos = Array.prototype.slice.call(formulario.querySelectorAll("fieldset[data-secao]"));
  if (!conjuntos.length) return;

  function ler(conjunto) {
    var campo = conjunto.querySelector("textarea");
    return {
      estado: conjunto.getAttribute("data-estado"),
      preambulo: conjunto.hasAttribute("data-preambulo"),
      texto: campo ? campo.value : "",
    };
  }

  function atualizar() {
    var numeros = numerar(conjuntos.map(ler));
    conjuntos.forEach(function (conjunto, indice) {
      var texto = rotulos(numeros[indice]);
      var numero = conjunto.querySelector("[data-numero]");
      var estado = conjunto.querySelector("[data-estado-texto]");
      if (numero && numero.textContent !== texto.numero) numero.textContent = texto.numero;
      if (estado && estado.textContent !== texto.estado) estado.textContent = texto.estado;
    });
  }

  formulario.addEventListener("input", function (evento) {
    if (evento.target && evento.target.tagName === "TEXTAREA") atualizar();
  });
  // Uma vez ao carregar: depois de um envio recusado, os campos trazem o que foi digitado, e o
  // número desenhado pelo servidor é o do conteúdo gravado.
  atualizar();
})();
