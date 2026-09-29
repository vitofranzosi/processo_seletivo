/* A visão do conjunto dos Perfis e um cartão à vista por vez (052).

   A vista — a tabela, um cartão por vez, o campo inválido escondido, o fragmento do endereço — mora
   no `vista-do-conjunto.js`, que a Classificação (053) também usa. Aqui fica só o que a linha dos
   Perfis lê do cartão, e as frases dela.

   **A linha é leitura do cartão.** Um desenho da linha no servidor e outro aqui envelheceriam
   separados; por isso a tabela só existe onde este script existe, como o filtro da Retificação. O
   servidor entrega o que a tela não sabe: `data-pendencias` e `data-nao-salvo` no cartão, e as frases
   curtas em `data-resumo`, que mantêm o vocabulário no template.

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

  /** O texto das células de uma linha, a partir do que o cartão tem digitado. */
  function resumo(dados) {
    var reserva = dados.reserva || {};
    var modalidades = (dados.modalidades || []).filter(function (m) {
      return m.codigo;
    });
    return {
      codigo: dados.codigo || "sem código",
      perfil: [dados.denominacao, dados.localidade].filter(Boolean).join(" · "),
      vagas: dados.vagas === "" || dados.vagas == null ? "0" : String(dados.vagas),
      reserva:
        reserva.valor === "LIMITED" && reserva.limite
          ? reserva.resumo + " a " + reserva.limite
          : reserva.resumo || "",
      modalidades: modalidades.length
        ? modalidades
            .map(function (m) {
              return m.percentual ? m.codigo + " " + percentual(m.percentual) + "%" : m.codigo;
            })
            .join(" · ")
        : "nenhuma",
      convocacao: dados.convocacao || "",
      situacao: vista.situacao(dados.pendencias, dados.alterado),
    };
  }

  /** `20.0000` → `20`, `12.5` → `12,5`: a gravação devolve o percentual com quatro casas. */
  function percentual(texto) {
    var numero = Number(String(texto).replace(",", "."));
    return isFinite(numero) ? String(numero).replace(".", ",") : texto;
  }

  var regras = {
    percentual: percentual,
    resumo: resumo,
    situacao: vista.situacao,
    cartaoAAbrir: vista.cartaoAAbrir,
    controleAlterado: vista.controleAlterado,
  };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var formulario = document.getElementById("formulario");
  var lista = document.getElementById("perfis");
  var lugar = document.getElementById("visao-dos-perfis");
  if (!formulario || !lista || !lugar) return;

  function campo(cartao, sufixo) {
    return cartao.querySelector('[name^="perfil-"][name$="-' + sufixo + '"]');
  }

  function valor(cartao, sufixo) {
    var controle = campo(cartao, sufixo);
    return controle ? String(controle.value || "").trim() : "";
  }

  function lerCartao(cartao) {
    var marcada = cartao.querySelector('[name^="perfil-"][name$="-reserveType"]:checked');
    var forma = campo(cartao, "callForm");
    return {
      codigo: valor(cartao, "code"),
      denominacao: valor(cartao, "name"),
      localidade: valor(cartao, "locality"),
      vagas: valor(cartao, "immediateVacancies"),
      reserva: {
        valor: marcada ? marcada.value : "",
        resumo: marcada ? marcada.dataset.resumo || "" : "",
        limite: valor(cartao, "reserveLimit"),
      },
      convocacao: forma
        ? forma.getAttribute("data-resumo-" + (forma.value || "nenhuma").toLowerCase()) || ""
        : "",
      modalidades: [].map.call(cartao.querySelectorAll("fieldset.modalidade"), function (m) {
        var codigo = m.querySelector('[name$="-code"]');
        var percentual = m.querySelector('[name$="-percentage"]');
        return {
          codigo: codigo ? codigo.value.trim() : "",
          percentual: percentual ? percentual.value.trim() : "",
        };
      }),
    };
  }

  function identificacao(dados) {
    var complemento = dados.localidade || dados.denominacao;
    if (!dados.codigo) return "Perfil novo";
    return complemento ? dados.codigo + " — " + complemento : dados.codigo;
  }

  vista.montar({
    formulario: formulario,
    lista: lista,
    lugar: lugar,
    item: "fieldset.perfil",
    contador: document.querySelector('[data-contador="#perfis"]'),
    noticia: "#previa-da-aplicacao, .erro[role=alert], #formulario .aviso[role=status]",
    legenda: function (quantos) {
      return "Perfis deste Edital (" + quantos + ")";
    },
    colunas: [
      ["perfil", "Perfil"],
      ["vagas", "Vagas imediatas", "numero"],
      ["reserva", "Cadastro reserva"],
      ["modalidades", "Modalidades"],
      ["convocacao", "Convocação"],
      ["situacao", "Situação"],
    ],
    ler: function (cartao) {
      var dados = lerCartao(cartao);
      return {
        codigo: dados.codigo || "sem código",
        rotulo: dados.codigo || "Perfil novo",
        titulo: identificacao(dados),
        celulas: resumo(dados),
      };
    },
  });
})();
