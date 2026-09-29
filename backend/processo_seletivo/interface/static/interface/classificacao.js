/* A visão do conjunto da etapa Classificação e um Perfil à vista por vez (053).

   A vista — a tabela, um cartão por vez, o campo inválido escondido, o fragmento do endereço — mora
   no `vista-do-conjunto.js`, a mesma dos Perfis (052). Aqui fica só o que a linha da Classificação lê
   do cartão do Perfil: os marcos dele, e o que o operador compara entre Perfis — a forma da ordem, o
   corte, os critérios de desempate, o recurso e de onde o marco veio.

   **A linha é o Perfil, e não o marco** (D-002 da spec). O cartão que se abre é o do Perfil, e é nele
   que se acrescenta marco; o Perfil sem marco também precisa de linha. Com mais de um marco, cada
   coluna de marco tem um valor por marco, na ordem do cartão — o 1º sobre o 1º, como a Revisão
   compara.

   **A linha lê, e não calcula** (FR-963). As frases vêm do template, em `data-resumo-*`, e são as do
   resumo de cada bloco do cartão; a origem e as pendências vêm do servidor, que é quem as sabe.

   As regras puras vêm primeiro e são exportadas para `node --test`. */
(function () {
  "use strict";

  var vista =
    typeof module === "object" && module.exports
      ? require("./vista-do-conjunto.js")
      : window.VistaDoConjunto;
  // Sem o script comum não há vista, e a etapa é a de sempre, com todos os cartões à vista.
  if (!vista) return;

  /* ── Regras ──────────────────────────────────────────────────────────────────────────────── */

  /** A forma da ordem; sob sorteio, se o marco usa o método comum ou declara o próprio. */
  function ordem(dados) {
    var forma = dados.ordem || "";
    return dados.metodo ? forma + ", " + dados.metodo : forma;
  }

  /** O corte com a frase do resumo do bloco; a quantidade fixa leva a quantidade. */
  function corte(dados) {
    var frase = dados.resumo || "";
    return dados.valor === "FIXED" && dados.quantidade ? frase + " de " + dados.quantidade : frase;
  }

  /** O recurso com a frase do resumo do bloco; *admite* leva o prazo, quando há. */
  function recurso(dados) {
    var frase = dados.resumo || "";
    if (dados.valor !== "admite" || !dados.prazo) return frase;
    return frase + ", prazo de " + dados.prazo + (String(dados.prazo) === "1" ? " dia" : " dias");
  }

  /** Os critérios, na ordem que declaram: o sentido e o que comparam. Sem alvo, só o sentido. */
  function desempate(criterios) {
    var ordenados = (criterios || []).slice().sort(function (a, b) {
      return (parseInt(a.ordem, 10) || 0) - (parseInt(b.ordem, 10) || 0);
    });
    if (!ordenados.length) return "nenhum critério";
    return ordenados
      .map(function (criterio, i) {
        var posicao = (parseInt(criterio.ordem, 10) || i + 1) + "º ";
        return posicao + [criterio.sentido, criterio.alvo].filter(Boolean).join(" ");
      })
      .join("; ");
  }

  /** As células de uma linha, a partir do que o cartão do Perfil tem digitado. */
  function resumo(dados) {
    var marcos = dados.marcos || [];
    var celulas = {
      perfil: [dados.denominacao, dados.localidade].filter(Boolean).join(" · "),
      origem: dados.origem || "—",
    };
    if (!marcos.length) {
      celulas.marcos = "sem marco";
      return celulas;
    }
    celulas.marcos = marcos.map(function (marco) {
      return marco.codigo || "sem código";
    });
    celulas.ordem = marcos.map(ordem);
    celulas.corte = marcos.map(function (marco) {
      return corte(marco.corte || {});
    });
    celulas.desempate = marcos.map(function (marco) {
      return desempate(marco.criterios);
    });
    celulas.recurso = marcos.map(function (marco) {
      return recurso(marco.recurso || {});
    });
    return celulas;
  }

  var regras = {
    ordem: ordem,
    corte: corte,
    recurso: recurso,
    desempate: desempate,
    resumo: resumo,
  };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var formulario = document.getElementById("formulario");
  var lista = document.getElementById("classificacao-perfis");
  var lugar = document.getElementById("visao-da-classificacao");
  if (!formulario || !lista || !lugar) return;

  function frase(controle) {
    if (!controle) return "";
    return controle.getAttribute("data-resumo-" + (controle.value || "nenhuma").toLowerCase()) || "";
  }

  function valor(controle) {
    return controle ? String(controle.value || "").trim() : "";
  }

  /* O método comum é o do alto da etapa, e se lê como o cartão o lê: declarado quando algum campo
     dele tem valor. A resposta do cartão (`resumo-do-bloco`) é a mesma pergunta, feita no servidor. */
  function temMetodoComum() {
    return [].some.call(formulario.querySelectorAll('[name^="edital-draw-"]'), function (c) {
      return valor(c) !== "";
    });
  }

  /* Sob sorteio, o bloco do método existe; o marco diverge do comum quando algum campo dele tem
     valor — a definição que a 030 escreveu (FR-430), e não uma regra desta tela. */
  function metodo(marco) {
    var bloco = marco.querySelector("[data-metodo-do-marco]");
    if (!bloco) return "";
    var proprio = [].some.call(bloco.querySelectorAll("[name]"), function (c) {
      return valor(c) !== "";
    });
    var chave = proprio ? "proprio" : temMetodoComum() ? "comum" : "nenhum";
    return bloco.getAttribute("data-resumo-" + chave) || "";
  }

  function lerMarco(marco) {
    var escolha = marco.querySelector('[name$="-appealDeclaration"]:checked');
    var tipoDoCorte = marco.querySelector('[name$="-cutTargetKind"]');
    return {
      codigo: valor(marco.querySelector('[name^="marco-"][name$="-code"]')),
      ordem: frase(marco.querySelector('[name$="-orderProduction"]')),
      metodo: metodo(marco),
      corte: {
        valor: valor(tipoDoCorte),
        resumo: frase(tipoDoCorte),
        quantidade: valor(marco.querySelector('[name$="-cutTargetCount"]')),
      },
      recurso: {
        valor: escolha ? escolha.value : "",
        resumo: escolha ? escolha.dataset.resumo || "" : "",
        prazo: valor(marco.querySelector('[name$="-appealDurationDays"]')),
      },
      criterios: [].map.call(marco.querySelectorAll("fieldset.criterio"), function (criterio) {
        var alvo = criterio.querySelector('[name$="-target"]');
        var escolhido = alvo && alvo.value ? alvo.options[alvo.selectedIndex] : null;
        return {
          ordem: valor(criterio.querySelector('[name$="-order"]')),
          sentido: frase(criterio.querySelector('[name$="-type"]')),
          alvo: escolhido ? escolhido.textContent.trim() : "",
        };
      }),
    };
  }

  function lerCartao(cartao) {
    return {
      codigo: cartao.dataset.codigo || "",
      denominacao: cartao.dataset.denominacao || "",
      localidade: cartao.dataset.localidade || "",
      origem: cartao.dataset.origem || "",
      marcos: [].map.call(cartao.querySelectorAll("fieldset.marco"), lerMarco),
    };
  }

  vista.montar({
    formulario: formulario,
    lista: lista,
    lugar: lugar,
    item: "fieldset.perfil",
    // A notícia é a prévia ou a recusa. O aviso de "nenhuma Etapa classificatória" é permanente, e
    // não notícia de um envio: não é para ele que a tela rola.
    noticia: "#previa-da-aplicacao, .erro[role=alert]",
    legenda: function (quantos) {
      return "Classificação dos Perfis deste Edital (" + quantos + ")";
    },
    colunas: [
      ["perfil", "Perfil"],
      ["marcos", "Marcos", "sem-quebra"],
      ["ordem", "Ordem"],
      ["corte", "Corte"],
      ["desempate", "Desempate"],
      ["recurso", "Recurso"],
      ["origem", "Origem"],
      ["situacao", "Situação"],
    ],
    ler: function (cartao) {
      var dados = lerCartao(cartao);
      var complemento = dados.localidade || dados.denominacao;
      return {
        codigo: dados.codigo,
        rotulo: dados.codigo,
        titulo: complemento ? dados.codigo + " — " + complemento : dados.codigo,
        celulas: resumo(dados),
      };
    },
  });
})();
