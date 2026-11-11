/* A ficha do barema na Mesa: parcela, limite, pendentes e total ao vivo (146, UX-422).

   **O script só mostra; quem calcula é o servidor.** O total não viaja no envio — o formulário
   manda o que foi informado em cada critério, e `avaliacoes.domain.barema.calcular` refaz a conta
   ao gravar (FR-5215). Sem o script, a ficha que o servidor desenhou continua certa até a próxima
   gravação, e nada se perde.

   **A conta é em décimos de milésimo inteiros**, como a de `barema.js`: 0,1 + 0,2 em ponto flutuante
   daria um total que a coluna `decimal(7,4)` não grava e que o servidor não mostraria.

   O que a pessoa lê é texto, e não só cor: "pendente", "limitada ao máximo" e a lista dos
   pendentes ao pé — é o que a conclusão vai cobrar, dito antes do clique. */
(function () {
  "use strict";

  var ESCALA = 10000;
  var QUANTIDADE_MAXIMA = 9999;

  /* "12,5", "12.5", " 12 " → 12.5; vazio → null; não-número → NaN. */
  function numero(texto) {
    if (texto === null || texto === undefined) return null;
    var limpo = String(texto).trim().replace(",", ".");
    if (!limpo) return null;
    var valor = Number(limpo);
    return isFinite(valor) ? valor : NaN;
  }

  function emEscala(valor) {
    return Math.round(valor * ESCALA);
  }

  /* 40 → "40"; 12.5 → "12,5" — a grafia do filtro `pontuacao` do servidor. */
  function formatar(valor) {
    if (valor === null || valor === undefined) return "—";
    var texto = (emEscala(valor) / ESCALA).toFixed(4).replace(/\.?0+$/, "");
    return texto.replace(".", ",");
  }

  /* A parcela de um critério: `{pendente}`, `{erro}` ou `{parcela, limitada}`.

     As mesmas regras de `barema.calcular`: por quantidade, inteiro de 0 a 9999 e parcela limitada
     pela máxima; direta, de zero à máxima com no máximo quatro casas. O erro é dito na linha, com a
     frase que a gravação usaria, para que a pessoa o veja antes de enviar. */
  function parcela(criterio, informado) {
    var valor = numero(informado);
    if (valor === null) return { pendente: true };
    if (isNaN(valor)) return { erro: "valor inválido" };
    if (valor < 0) return { erro: "não pode ser negativo" };
    var maxima = emEscala(criterio.maxima);
    if (criterio.pontosPorUnidade !== null) {
      if (Math.floor(valor) !== valor) return { erro: "a quantidade é um número inteiro" };
      if (valor > QUANTIDADE_MAXIMA) return { erro: "no máximo " + QUANTIDADE_MAXIMA };
      var bruta = emEscala(criterio.pontosPorUnidade) * valor;
      return { parcela: Math.min(bruta, maxima) / ESCALA, limitada: bruta > maxima };
    }
    if (Math.abs(valor * ESCALA - Math.round(valor * ESCALA)) > 1e-6) {
      return { erro: "no máximo quatro casas decimais" };
    }
    if (emEscala(valor) > maxima) return { erro: "acima da máxima, " + formatar(criterio.maxima) };
    return { parcela: emEscala(valor) / ESCALA, limitada: false };
  }

  /* A soma das parcelas respondidas; `null` se nenhuma foi. */
  function somar(parcelas) {
    var total = 0;
    var respondidas = 0;
    for (var i = 0; i < parcelas.length; i++) {
      if (parcelas[i] === null || parcelas[i] === undefined) continue;
      total += emEscala(parcelas[i]);
      respondidas += 1;
    }
    return respondidas ? total / ESCALA : null;
  }

  var regras = { numero: numero, formatar: formatar, parcela: parcela, somar: somar };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ------------------------------------------------------------------ a montagem na página */

  if (typeof document === "undefined") return;

  function criterioDa(linha) {
    var pontos = numero(linha.getAttribute("data-pontos-por-unidade"));
    return {
      maxima: numero(linha.getAttribute("data-maxima")) || 0,
      pontosPorUnidade: pontos === null || isNaN(pontos) ? null : pontos,
      nome: (linha.querySelector(".nome-do-criterio") || {}).textContent || "",
    };
  }

  function escrever(saida, resultado) {
    while (saida.firstChild) saida.removeChild(saida.firstChild);
    if (resultado.pendente || resultado.erro) {
      var marca = document.createElement("span");
      marca.className = "pendente";
      marca.textContent = resultado.erro ? "pendente — " + resultado.erro : "pendente";
      saida.appendChild(marca);
      return;
    }
    saida.appendChild(document.createTextNode(formatar(resultado.parcela)));
    if (resultado.limitada) {
      var limite = document.createElement("span");
      limite.className = "limitada";
      limite.textContent = " — limitada ao máximo";
      saida.appendChild(limite);
    }
  }

  function refazer(ficha) {
    var linhas = [].slice.call(ficha.querySelectorAll("[data-criterio-da-ficha]"));
    var parcelas = [];
    var pendentes = [];
    var maxima = 0;
    linhas.forEach(function (linha) {
      var criterio = criterioDa(linha);
      maxima += emEscala(criterio.maxima);
      var campo = linha.querySelector("[data-quantidade], [data-pontos]");
      var resultado = parcela(criterio, campo ? campo.value : null);
      var saida = linha.querySelector("[data-parcela]");
      if (saida) escrever(saida, resultado);
      if (resultado.pendente || resultado.erro) {
        pendentes.push(criterio.nome.trim());
        parcelas.push(null);
      } else {
        parcelas.push(resultado.parcela);
      }
    });
    var total = ficha.querySelector("[data-total-da-ficha]");
    if (total) {
      while (total.firstChild) total.removeChild(total.firstChild);
      var forte = document.createElement("strong");
      forte.textContent = formatar(somar(parcelas));
      total.appendChild(forte);
      total.appendChild(document.createTextNode(" de " + formatar(maxima / ESCALA)));
    }
    var aviso = ficha.querySelector("[data-pendentes-da-ficha]");
    if (aviso) {
      aviso.textContent = pendentes.length ? "Pendentes: " + pendentes.join("; ") + "." : "";
    }
  }

  [].forEach.call(document.querySelectorAll("[data-ficha-do-barema]"), function (ficha) {
    ficha.addEventListener("input", function () {
      refazer(ficha);
    });
    refazer(ficha);
  });
})();
