/* As regras da vista do conjunto dos Perfis (052).

   O que se afirma aqui é a **regra**, e não o desenho: o texto de cada célula a partir do que o
   cartão tem digitado, qual cartão abre quando a etapa carrega, e quando um controle difere do que
   a página trouxe.

   O que estes testes NÃO provam: a montagem — a tabela, o `hidden`, o foco, o campo inválido que
   abre o cartão escondido, o fragmento do endereço que sobrevive ao envio. Nada disso existe no
   shim, e tudo isso foi verificado no navegador, pelo roteiro de quickstart.md. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/perfis.js")
);

function cartao(extra = {}) {
  return {
    codigo: "P03",
    denominacao: "Professor de Informática",
    localidade: "Vitória",
    vagas: "40",
    reserva: { valor: "LIMITED", resumo: "limitado", limite: "6" },
    convocacao: "por publicação",
    modalidades: [
      { codigo: "AC", percentual: "" },
      { codigo: "PPI", percentual: "25.0000" },
    ],
    pendencias: "0",
    alterado: false,
    ...extra,
  };
}

test("a linha diz o Perfil com as frases da tela", () => {
  assert.deepEqual(regras.resumo(cartao()), {
    codigo: "P03",
    perfil: "Professor de Informática · Vitória",
    vagas: "40",
    reserva: "limitado a 6",
    modalidades: "AC · PPI 25%",
    convocacao: "por publicação",
    situacao: "sem pendência",
  });
});

test("o Perfil sem código ainda aparece, e se edita", () => {
  const linha = regras.resumo(cartao({ codigo: "", localidade: "", vagas: "" }));

  assert.equal(linha.codigo, "sem código");
  assert.equal(linha.perfil, "Professor de Informática");
  assert.equal(linha.vagas, "0");
});

test("o limite só acompanha a reserva limitada", () => {
  const ilimitada = { valor: "UNLIMITED", resumo: "ilimitado", limite: "6" };

  assert.equal(regras.resumo(cartao({ reserva: ilimitada })).reserva, "ilimitado");
});

test("Modalidade sem código não entra, e Perfil sem Modalidade diz nenhuma", () => {
  assert.equal(regras.resumo(cartao({ modalidades: [{ codigo: "", percentual: "5" }] })).modalidades, "nenhuma");
});

test("o percentual volta sem as casas da gravação, e com vírgula", () => {
  assert.equal(regras.percentual("20.0000"), "20");
  assert.equal(regras.percentual("12.5"), "12,5");
  assert.equal(regras.percentual("12,5"), "12,5");
});

test("a situação são dois fatos, em texto", () => {
  assert.equal(regras.situacao("0", false), "sem pendência");
  assert.equal(regras.situacao("1", false), "1 pendência");
  assert.equal(regras.situacao("3", true), "3 pendências · alterado — não salvo");
  assert.equal(regras.situacao(undefined, true), "sem pendência · alterado — não salvo");
});

test("com um Perfil só, ele é sempre o aberto", () => {
  assert.equal(regras.cartaoAAbrir({ quantos: 1, recusado: null, apontado: null, gravou: true }), 0);
});

test("a recusa vence o endereço, e o endereço vence o nada", () => {
  assert.equal(regras.cartaoAAbrir({ quantos: 7, recusado: 4, apontado: 2, gravou: false }), 4);
  assert.equal(regras.cartaoAAbrir({ quantos: 7, recusado: null, apontado: 2, gravou: false }), 2);
  assert.equal(regras.cartaoAAbrir({ quantos: 7, recusado: null, apontado: null, gravou: false }), null);
});

test("depois de gravar, o endereço não reabre cartão nenhum", () => {
  assert.equal(regras.cartaoAAbrir({ quantos: 7, recusado: null, apontado: 2, gravou: true }), null);
});

test("o controle difere do que a página trouxe", () => {
  assert.equal(regras.controleAlterado({ type: "text", value: "9", defaultValue: "2" }), true);
  assert.equal(regras.controleAlterado({ type: "text", value: "2", defaultValue: "2" }), false);
  assert.equal(regras.controleAlterado({ type: "radio", checked: true, defaultChecked: false }), true);
  assert.equal(regras.controleAlterado({ type: "hidden", value: "x", defaultValue: "y" }), false);
});

test("o select que nasce sem opção marcada não está alterado", () => {
  const opcoes = [{ defaultSelected: false }, { defaultSelected: false }];

  assert.equal(regras.controleAlterado({ type: "select-one", options: opcoes, selectedIndex: 0 }), false);
  assert.equal(regras.controleAlterado({ type: "select-one", options: opcoes, selectedIndex: 1 }), true);
  const marcada = [{ defaultSelected: false }, { defaultSelected: true }];
  assert.equal(regras.controleAlterado({ type: "select-one", options: marcada, selectedIndex: 1 }), false);
});
