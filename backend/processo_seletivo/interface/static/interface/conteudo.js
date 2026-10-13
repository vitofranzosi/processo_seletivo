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

  /** Na apresentação por perguntas (069, R-003), o número é o que o servidor calculou.

     As seções se reúnem sob a pergunta — "3.1 Público-alvo" —, e o número deixa de ser a contagem
     das que saem: recontá-lo aqui seria a segunda regra que a `054` existe para não ter. O script
     só diz se a seção sai com o que está no campo; o número novo aparece ao salvar.

     `provisorio`: alguma seção mudou de "sai" para "não sai", ou o contrário, desde o que o
     servidor numerou — digitando, ou depois de um envio recusado. Os números seguintes se
     deslocam, e o do servidor deixaria de ser o do documento: nenhuma seção mostra número até
     salvar. */
  function rotulosApresentados(secao, provisorio) {
    if (!sai(secao)) return { numero: "", estado: " (vazia — não sai no documento)" };
    if (secao.preambulo) return { numero: "", estado: " (preâmbulo, sem número)" };
    if (provisorio || !(secao.rotuloDoServidor || secao.estadoDoServidor)) {
      return { numero: "", estado: " (sai no documento; o número aparece ao salvar)" };
    }
    return { numero: secao.rotuloDoServidor, estado: secao.estadoDoServidor || "" };
  }

  /** O servidor numerou outro conjunto de seções que o que os campos dizem agora? */
  function numeracaoDefasada(secoes) {
    return secoes.some(function (secao) {
      if (!secao.apresentada || secao.preambulo) return false;
      return sai(secao) !== Boolean(secao.rotuloDoServidor || secao.estadoDoServidor);
    });
  }

  var regras = {
    sai: sai,
    numerar: numerar,
    rotulos: rotulos,
    rotulosApresentados: rotulosApresentados,
    numeracaoDefasada: numeracaoDefasada,
  };
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
      apresentada: conjunto.hasAttribute("data-numeracao-apresentada"),
      rotuloDoServidor: conjunto.getAttribute("data-rotulo-do-numero") || "",
      estadoDoServidor: conjunto.getAttribute("data-estado-do-servidor") || "",
    };
  }

  function atualizar() {
    var lidas = conjuntos.map(ler);
    var numeros = numerar(lidas);
    var provisorio = numeracaoDefasada(lidas);
    conjuntos.forEach(function (conjunto, indice) {
      var texto = lidas[indice].apresentada
        ? rotulosApresentados(lidas[indice], provisorio)
        : rotulos(numeros[indice]);
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
