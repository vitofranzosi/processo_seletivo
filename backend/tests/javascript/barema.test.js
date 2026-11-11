/* A seção Barema (146): a prévia, a soma e a frase de cada critério ao vivo.

   O que se afirma aqui são as **regras** — as mesmas frases que `pdf.pontuacao_do_criterio` escreve
   no documento, e a soma em décimos de milésimo. A montagem (a tabela refeita, a máxima da Etapa
   em leitura, a linha nova observada) não existe no shim, e foi verificada no navegador, pelo
   roteiro do quickstart §1, em desktop e a 375 px. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/barema.js")
);

const porUnidade = (pontos, maxima, unidade) => ({
  porUnidade: true,
  pontos,
  maxima,
  unidade,
});

test("por unidade com teto que limita: '5 pontos por certificado, até 10' (US1, cenário 2)", () => {
  assert.equal(regras.pontuacao(porUnidade(5, 10, "certificado")), "5 pontos por certificado, até 10");
});

test("valor fixo não repete o teto: '20 pontos por diploma'", () => {
  assert.equal(regras.pontuacao(porUnidade(20, 20, "diploma")), "20 pontos por diploma");
});

test("abaixo de dois, ponto no singular, como no PDF", () => {
  assert.equal(regras.pontuacao(porUnidade(1, 40, "mês")), "1 ponto por mês, até 40");
  assert.equal(regras.pontuacao(porUnidade(0.5, 10, "mês")), "0,5 ponto por mês, até 10");
});

test("pontuação atribuída pela comissão: 'de 0 a 15'", () => {
  assert.equal(regras.pontuacao({ porUnidade: false, pontos: null, maxima: 15 }), "de 0 a 15");
});

test("por unidade sem os pontos avisa antes de gravar", () => {
  assert.equal(
    regras.pontuacao(porUnidade(null, 10, "certificado")),
    "Falta informar os pontos por unidade"
  );
});

test("a soma do 14/2026 é 100, e é a máxima da Etapa (FR-5203)", () => {
  assert.equal(regras.somar([20, 15, 10, 15, 40]), 100);
});

test("a soma não erra o ponto flutuante: 0,1 + 0,2 é 0,3", () => {
  assert.equal(regras.formatar(regras.somar([0.1, 0.2])), "0,3");
  assert.equal(regras.noCampo(regras.somar([0.1, 0.2])), "0.3");
});

test("com uma máxima em branco não há soma", () => {
  assert.equal(regras.somar([20, null]), null);
  assert.equal(regras.somar([]), null);
});

test("o número aceita vírgula e recusa o que não é número", () => {
  assert.equal(regras.numero("12,5"), 12.5);
  assert.equal(regras.numero(" 7 "), 7);
  assert.equal(regras.numero(""), null);
  assert.equal(regras.numero("abc"), null);
});

test("a linha da prévia tem as quatro colunas da ficha, com a descrição junto do título", () => {
  assert.deepEqual(
    regras.linha({
      nome: "Especialização",
      descricao: "na área da Educação",
      maxima: 10,
      porUnidade: true,
      pontos: 5,
      unidade: "certificado",
      documento: "Títulos acadêmicos",
    }),
    ["Especialização — na área da Educação", "5 pontos por certificado, até 10", "10", "Títulos acadêmicos"]
  );
});

test("sem documento ligado, a comprovação é um travessão", () => {
  const linha = regras.linha({ nome: "Entrevista", maxima: 15, porUnidade: false, pontos: null });
  assert.equal(linha[3], "—");
});

test("a prévia inteira: linhas na ordem da ficha e o total", () => {
  const previa = regras.previa([
    { nome: "Doutorado", maxima: 20, porUnidade: true, pontos: 20, unidade: "diploma" },
    { nome: "Docência", maxima: 40, porUnidade: true, pontos: 1, unidade: "mês" },
  ]);
  assert.deepEqual(
    previa.linhas.map((linha) => linha[0]),
    ["Doutorado", "Docência"]
  );
  assert.equal(previa.total, 60);
});

test("pontos acima da máxima avisam na prévia, como a gravação recusaria", () => {
  assert.equal(
    regras.pontuacao(porUnidade(25, 10, "certificado")),
    "Pontos por unidade acima da máxima: uma unidade já passaria do teto"
  );
  assert.equal(regras.pontuacao(porUnidade(10, 10, "certificado")), "10 pontos por certificado");
});
