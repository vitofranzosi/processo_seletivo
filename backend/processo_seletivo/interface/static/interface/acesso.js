/* A busca da escolha de identidades na página de acesso (075, FR-1695).

   Atalho, e não porta: sem este script o campo fica escondido e a lista inteira continua na tela,
   cada linha um botão de envio. Com ele, o campo aparece e filtra as linhas pelo texto que cada uma
   declara em `data-busca` — nome, responsabilidade e Processo —, sem diferença de acento nem de
   caixa. O grupo que fica sem linha some junto, para que o título de um grupo vazio não sugira que
   há o que escolher nele. */
(function () {
  function normalizar(texto) {
    return String(texto || "")
      .normalize("NFD")
      .replace(/\p{Diacritic}/gu, "")
      .toLowerCase()
      .trim();
  }

  /** Mostra as linhas que contêm o termo e devolve quantas ficaram à vista. */
  function filtrar(termo, grupos) {
    var alvo = normalizar(termo);
    var total = 0;
    grupos.forEach(function (grupo) {
      var visiveis = 0;
      grupo.linhas.forEach(function (linha) {
        var mostra = alvo === "" || normalizar(linha.dataset.busca).indexOf(alvo) !== -1;
        linha.hidden = !mostra;
        if (mostra) visiveis += 1;
      });
      grupo.elemento.hidden = visiveis === 0;
      total += visiveis;
    });
    return total;
  }

  function ligar(documento) {
    var caixa = documento.getElementById("busca-de-identidade");
    if (!caixa) return;
    var campo = caixa.querySelector("input");
    var vazio = documento.getElementById("busca-sem-resultado");
    var grupos = Array.prototype.map.call(
      documento.querySelectorAll("[data-grupo-de-identidades]"),
      function (elemento) {
        return {
          elemento: elemento,
          linhas: Array.prototype.slice.call(elemento.querySelectorAll("[data-busca]")),
        };
      }
    );
    caixa.hidden = false;
    campo.addEventListener("input", function () {
      vazio.hidden = filtrar(campo.value, grupos) > 0;
    });
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { filtrar: filtrar, normalizar: normalizar };
  } else {
    ligar(document);
  }
})();
