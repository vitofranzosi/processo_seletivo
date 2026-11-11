/* A ficha do barema na Mesa (146, UX-422): a parcela, o limite e o total ao vivo.

   O que se afirma são as **regras** — as mesmas de `avaliacoes.domain.barema.calcular`, que é quem
   vale ao gravar. A montagem na página (a célula reescrita, a lista de pendentes) foi verificada no
   navegador pelo roteiro do quickstart §2, em desktop e a 375 px. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/mesa_barema.js")
);

const docencia = { maxima: 40, pontosPorUnidade: 1 };
const especializacao = { maxima: 10, pontosPorUnidade: 5 };
const entrevista = { maxima: 15, pontosPorUnidade: null };

test("52 meses de docência a 1 por mês, até 40: parcela 40, limitada ao máximo", () => {
  assert.deepEqual(regras.parcela(docencia, "52"), { parcela: 40, limitada: true });
});

test("3 certificados a 5, até 10: parcela 10, limitada", () => {
  assert.deepEqual(regras.parcela(especializacao, "3"), { parcela: 10, limitada: true });
  assert.deepEqual(regras.parcela(especializacao, "2"), { parcela: 10, limitada: false });
});

test("zero é resposta, e não pendente", () => {
  assert.deepEqual(regras.parcela(especializacao, "0"), { parcela: 0, limitada: false });
});

test("em branco é pendente", () => {
  assert.deepEqual(regras.parcela(especializacao, ""), { pendente: true });
  assert.deepEqual(regras.parcela(entrevista, "  "), { pendente: true });
});

test("quantidade fracionária é erro dito na linha", () => {
  assert.ok(regras.parcela(especializacao, "1,5").erro);
});

test("pontos diretos acima da máxima são erro, com a máxima na frase", () => {
  assert.equal(regras.parcela(entrevista, "16").erro, "acima da máxima, 15");
});

test("pontos diretos com vírgula e quatro casas", () => {
  assert.deepEqual(regras.parcela(entrevista, "12,3456"), { parcela: 12.3456, limitada: false });
  assert.ok(regras.parcela(entrevista, "1,23456").erro);
});

test("o total do quickstart §2 é 70, e soma sem erro de ponto flutuante", () => {
  // 1 doutorado (20), 0 mestrado, 3 especializações (10), 0 curso, 52 meses (40).
  assert.equal(regras.formatar(regras.somar([20, 0, 10, 0, 40])), "70");
  assert.equal(regras.formatar(regras.somar([0.1, 0.2])), "0,3");
});

test("sem nada respondido não há total", () => {
  assert.equal(regras.somar([null, null]), null);
  assert.equal(regras.formatar(regras.somar([])), "—");
});
