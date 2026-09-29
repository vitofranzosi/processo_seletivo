/* As regras da linha da etapa Classificação (053).

   O que se afirma aqui é a **regra**, e não o desenho: o texto de cada célula a partir do que o
   cartão do Perfil tem digitado — os marcos, a forma da ordem, o corte, os critérios, o recurso e a
   origem. As frases vêm do template (`data-resumo-*`); aqui elas chegam já lidas.

   O que estes testes NÃO provam: a montagem — a tabela, o `hidden`, o foco, o campo inválido que
   abre o cartão e o bloco, o fragmento do endereço. Nada disso existe no shim, e tudo isso foi
   verificado no navegador, pelo roteiro de quickstart.md. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/classificacao.js")
);

function marco(extra = {}) {
  return {
    codigo: "FINAL",
    ordem: "pela pontuação",
    metodo: "",
    corte: { valor: "FROM_VACANCY_TABLE", resumo: "o que o quadro de vagas publicar", quantidade: "" },
    recurso: { valor: "admite", resumo: "admite", prazo: "2" },
    criterios: [
      { ordem: "1", sentido: "maior nota em", alvo: "Prova objetiva" },
      { ordem: "2", sentido: "maior nota em", alvo: "Análise de títulos" },
    ],
    ...extra,
  };
}

function perfil(extra = {}) {
  return {
    codigo: "DOC-INFO-03",
    denominacao: "Professor de Informática",
    localidade: "Campus Cariacica",
    origem: "",
    marcos: [marco()],
    ...extra,
  };
}

test("a linha de um marco diz o que o operador compara, com as frases do cartão", () => {
  assert.deepEqual(regras.resumo(perfil()), {
    perfil: "Professor de Informática · Campus Cariacica",
    origem: "—",
    marcos: ["FINAL"],
    ordem: ["pela pontuação"],
    corte: ["o que o quadro de vagas publicar"],
    desempate: ["1º maior nota em Prova objetiva; 2º maior nota em Análise de títulos"],
    recurso: ["admite, prazo de 2 dias"],
  });
});

test("dois marcos são dois blocos por coluna, na ordem do cartão", () => {
  const corta = marco({
    codigo: "CORTE",
    corte: { valor: "FIXED", resumo: "quantidade fixa", quantidade: "30" },
    criterios: [],
    recurso: { valor: "nao_declarada", resumo: "nada declarado", prazo: "" },
  });
  const linha = regras.resumo(perfil({ marcos: [corta, marco()] }));

  assert.deepEqual(linha.marcos, ["CORTE", "FINAL"]);
  assert.deepEqual(linha.corte, ["quantidade fixa de 30", "o que o quadro de vagas publicar"]);
  assert.deepEqual(linha.desempate[0], "nenhum critério");
  assert.deepEqual(linha.recurso, ["nada declarado", "admite, prazo de 2 dias"]);
});

test("o Perfil sem marco tem linha, e diz que não tem", () => {
  const linha = regras.resumo(perfil({ marcos: [] }));

  assert.equal(linha.marcos, "sem marco");
  assert.equal(linha.ordem, undefined);
});

test("o marco recém-acrescentado, ainda sem código, aparece", () => {
  assert.deepEqual(regras.resumo(perfil({ marcos: [marco({ codigo: "" })] })).marcos, ["sem código"]);
});

test("a origem é a frase que o servidor mandou", () => {
  const frase = "aplicado a partir do Perfil DOC-INFO, por ana.elaboradora, em 29/09/2026 15:02";

  assert.equal(regras.resumo(perfil({ origem: frase })).origem, frase);
});

test("sob sorteio, a forma diz o método", () => {
  assert.equal(regras.ordem({ ordem: "por sorteio", metodo: "método próprio" }), "por sorteio, método próprio");
  assert.equal(regras.ordem({ ordem: "pela pontuação", metodo: "" }), "pela pontuação");
});

test("o prazo só acompanha quem admite, e no singular quando é um", () => {
  assert.equal(regras.recurso({ valor: "admite", resumo: "admite", prazo: "1" }), "admite, prazo de 1 dia");
  assert.equal(regras.recurso({ valor: "admite", resumo: "admite", prazo: "" }), "admite");
  assert.equal(
    regras.recurso({ valor: "nao_admite", resumo: "não admite por esta via", prazo: "5" }),
    "não admite por esta via"
  );
});

test("a quantidade só acompanha o corte fixo", () => {
  assert.equal(regras.corte({ valor: "FIXED", resumo: "quantidade fixa", quantidade: "" }), "quantidade fixa");
  assert.equal(
    regras.corte({ valor: "FROM_VACANCY_TABLE", resumo: "o que o quadro de vagas publicar", quantidade: "9" }),
    "o que o quadro de vagas publicar"
  );
});

test("os critérios saem pela ordem que declaram, e o sem alvo diz só o sentido", () => {
  const criterios = [
    { ordem: "2", sentido: "menor", alvo: "Idade" },
    { ordem: "1", sentido: "maior nota em", alvo: "" },
  ];

  assert.equal(regras.desempate(criterios), "1º maior nota em; 2º menor Idade");
});
