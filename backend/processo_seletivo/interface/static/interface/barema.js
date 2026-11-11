/* A seção Barema do cartão da Etapa (146, FR-5203, FR-5207, UX-421).

   **O script só mostra; quem decide é o servidor.** A prévia, a soma e a máxima da Etapa são
   refeitas a cada tecla para que a pessoa veja a ficha como o Edital a imprimirá antes de gravar —
   mas a máxima gravada é a que `ler_etapas` calcula, e a frase de cada linha é a mesma que
   `pdf.pontuacao_do_criterio` escreve no documento. Sem o script, a prévia que o servidor desenhou
   continua certa até a próxima gravação, e nada se perde.

   **Nada do que a pessoa digita vira marcação.** As células são escritas por `textContent`: um
   critério chamado "<b>Doutorado</b>" aparece com os sinais, como foi digitado.

   **A soma é em décimos de milésimo inteiros**, e não em ponto flutuante: 0,1 + 0,2 daria
   0,30000000000000004, e a máxima da Etapa sairia com um resto que nenhum Edital escreveu. As
   quatro casas são as da coluna `decimal(7,4)`.

   Acrescentar, remover e mover critérios são do `ordenacao.js` e do HTMX, como em toda lista do
   assistente; este script só observa a lista e refaz a prévia quando ela muda. */
(function () {
  "use strict";

  var ESCALA = 10000;

  /* "12,5", "12.5", " 12 " → 12.5; vazio ou não-número → null. */
  function numero(texto) {
    if (texto === null || texto === undefined) return null;
    var limpo = String(texto).trim().replace(",", ".");
    if (!limpo) return null;
    var valor = Number(limpo);
    return isFinite(valor) ? valor : null;
  }

  function emEscala(valor) {
    return Math.round(valor * ESCALA);
  }

  /* 20 → "20"; 12.5 → "12,5"; 0.25 → "0,25" — a grafia de `humano.decimal`. */
  function formatar(valor) {
    if (valor === null || valor === undefined) return "";
    var texto = (emEscala(valor) / ESCALA).toFixed(4).replace(/\.?0+$/, "");
    return texto.replace(".", ",");
  }

  /* O valor do campo numérico, que só aceita ponto. */
  function noCampo(valor) {
    return (emEscala(valor) / ESCALA).toFixed(4).replace(/\.?0+$/, "");
  }

  /* `null` se alguma máxima falta: a soma de um barema incompleto não é a máxima de nada. */
  function somar(maximas) {
    if (!maximas.length) return null;
    var total = 0;
    for (var i = 0; i < maximas.length; i++) {
      if (maximas[i] === null || maximas[i] <= 0) return null;
      total += emEscala(maximas[i]);
    }
    return total / ESCALA;
  }

  function pontos(valor) {
    return formatar(valor) + (valor < 2 ? " ponto" : " pontos");
  }

  /* A coluna "Pontuação", na frase de `pdf.pontuacao_do_criterio`. As duas que só a prévia diz são
     as das recusas da gravação — o critério por unidade sem os pontos e os pontos acima da máxima
     —, para a pessoa as ver antes de gravar, e não depois. */
  function pontuacao(criterio) {
    var maxima = criterio.maxima;
    if (criterio.porUnidade && criterio.pontos === null) {
      return "Falta informar os pontos por unidade";
    }
    if (!criterio.porUnidade || criterio.pontos === null) {
      return maxima === null ? "" : "de 0 a " + formatar(maxima);
    }
    /* A mesma recusa do domínio (`etapas.problemas_do_barema`), dita antes de gravar: uma frase de
       aparência normal com o total intacto escondia o erro até o "Salvar". */
    if (maxima !== null && emEscala(criterio.pontos) > emEscala(maxima)) {
      return "Pontos por unidade acima da máxima: uma unidade já passaria do teto";
    }
    var unidade = (criterio.unidade || "").trim();
    var frase = unidade ? pontos(criterio.pontos) + " por " + unidade : pontos(criterio.pontos);
    if (maxima !== null && emEscala(criterio.pontos) < emEscala(maxima)) {
      frase += ", até " + formatar(maxima);
    }
    return frase;
  }

  /* As quatro colunas da ficha dos Editais, como `pdf.linhas_do_barema` as compõe. */
  function linha(criterio) {
    var nome = (criterio.nome || "").trim();
    var descricao = (criterio.descricao || "").trim();
    return [
      descricao ? nome + " — " + descricao : nome,
      pontuacao(criterio),
      formatar(criterio.maxima),
      criterio.documento || "—",
    ];
  }

  function previa(criterios) {
    return {
      linhas: criterios.map(linha),
      total: somar(
        criterios.map(function (criterio) {
          return criterio.maxima;
        })
      ),
    };
  }

  var regras = {
    numero: numero,
    formatar: formatar,
    noCampo: noCampo,
    somar: somar,
    pontuacao: pontuacao,
    linha: linha,
    previa: previa,
  };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;

  function valor(raiz, seletor) {
    var campo = raiz.querySelector(seletor);
    return campo ? campo.value : "";
  }

  function lerCriterio(cartao) {
    var modo = cartao.querySelector("[data-barema-modo]:checked");
    var documento = cartao.querySelector("[data-barema-documento]");
    var escolhido = documento && documento.value ? documento.options[documento.selectedIndex] : null;
    return {
      nome: valor(cartao, "[data-barema-nome]"),
      descricao: valor(cartao, "[data-barema-descricao]"),
      maxima: numero(valor(cartao, "[data-barema-maxima]")),
      porUnidade: !modo || modo.value !== "DIRETA",
      pontos: numero(valor(cartao, "[data-barema-pontos]")),
      unidade: valor(cartao, "[data-barema-unidade]"),
      documento: escolhido ? escolhido.textContent.replace(/\s+/g, " ").trim() : "",
    };
  }

  function cartoes(secao) {
    var lista = secao.querySelector("[data-criterios-do-barema]");
    if (!lista) return [];
    return [].filter.call(lista.children, function (no) {
      return no.matches && no.matches("[data-criterio-de-avaliacao]");
    });
  }

  function celula(tag, texto, rotulo, classe) {
    var elemento = document.createElement(tag);
    elemento.textContent = texto;
    if (rotulo) elemento.setAttribute("data-rotulo", rotulo);
    if (classe) elemento.className = classe;
    return elemento;
  }

  var ROTULOS = ["Critério", "Pontuação", "Máxima", "Comprovação"];

  function refazer(secao) {
    var lidos = cartoes(secao).map(lerCriterio);
    var resultado = previa(lidos);

    var corpo = secao.querySelector("[data-linhas-da-previa]");
    if (corpo) {
      while (corpo.firstChild) corpo.removeChild(corpo.firstChild);
      resultado.linhas.forEach(function (colunas) {
        var tr = document.createElement("tr");
        colunas.forEach(function (texto, indice) {
          tr.appendChild(celula("td", texto, ROTULOS[indice], indice === 2 ? "numero" : ""));
        });
        corpo.appendChild(tr);
      });
    }
    var total = secao.querySelector("[data-total-do-barema]");
    var texto = resultado.total === null ? "—" : formatar(resultado.total);
    if (total && total.textContent !== texto) {
      total.textContent = texto;
      var anuncio = secao.querySelector("[data-anuncio-do-barema]");
      if (anuncio) anuncio.textContent = "Total do barema: " + texto + " pontos.";
    }
    var bloco = secao.querySelector("[data-previa-do-barema]");
    if (bloco) bloco.hidden = lidos.length === 0;

    // A máxima da Etapa vira leitura com critérios, e volta a ser digitável sem eles (UX-420).
    var etapa = secao.closest("fieldset.etapa");
    if (!etapa) return;
    var maxima = etapa.querySelector("[data-maxima-da-etapa]");
    var soma = etapa.querySelector("[data-soma-do-barema]");
    var opcional = etapa.querySelector("[data-maxima-opcional]");
    var comCriterios = lidos.length > 0;
    if (maxima) {
      maxima.readOnly = comCriterios;
      if (comCriterios && resultado.total !== null) maxima.value = noCampo(resultado.total);
    }
    if (soma) soma.hidden = !comCriterios;
    if (opcional) opcional.hidden = comCriterios;
    // O título que a pessoa digita aparece na legenda do cartão, que é o que se acha rolando.
    cartoes(secao).forEach(function (cartao) {
      var nome = cartao.querySelector(":scope > legend .nome");
      var digitado = valor(cartao, "[data-barema-nome]").trim();
      if (!nome && digitado) {
        nome = document.createElement("span");
        nome.className = "nome";
        cartao.querySelector(":scope > legend").appendChild(nome);
      }
      if (nome) nome.textContent = digitado;
    });
  }

  function observar(secao) {
    if (secao.dataset.baremaLigado) return;
    secao.dataset.baremaLigado = "1";
    var lista = secao.querySelector("[data-criterios-do-barema]");
    if (lista && typeof MutationObserver === "function") {
      new MutationObserver(function () {
        refazer(secao);
      }).observe(lista, { childList: true });
    }
    refazer(secao);
  }

  function ligarDentro(raiz) {
    if (!raiz || typeof raiz.querySelectorAll !== "function") return;
    if (raiz.matches && raiz.matches("[data-barema]")) observar(raiz);
    [].forEach.call(raiz.querySelectorAll("[data-barema]"), observar);
  }

  function aoDigitar(evento) {
    var secao = evento.target && evento.target.closest && evento.target.closest("[data-barema]");
    if (secao) refazer(secao);
  }

  document.addEventListener("input", aoDigitar);
  document.addEventListener("change", aoDigitar);
  document.addEventListener("htmx:load", function (evento) {
    ligarDentro(evento.target);
  });
  ligarDentro(document);
})();
