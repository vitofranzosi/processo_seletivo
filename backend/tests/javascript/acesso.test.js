/* FR-1695 — a busca da escolha de identidades filtra pelo texto declarado em cada linha.

   O que se afirma é a regra: qual linha fica, qual grupo some, e que acento e caixa não separam
   "Avaliação" de "avaliacao". A ligação com o campo de verdade é do navegador, e está no
   quickstart da 075. Sem o shim de `dom.js`: a função recebe objetos simples, que é tudo o que ela
   lê de um elemento. */

const assert = require("node:assert/strict");
const { test } = require("node:test");

const { filtrar, normalizar } = require("../../processo_seletivo/interface/static/interface/acesso.js");

function grupo(...buscas) {
  return {
    elemento: { hidden: false },
    linhas: buscas.map((busca) => ({ dataset: { busca }, hidden: false })),
  };
}

test("acento e caixa não separam o que a pessoa digitou do que a linha diz", () => {
  assert.equal(normalizar("  Avaliação "), "avaliacao");
});

test("só as linhas com o termo ficam à vista, e a contagem diz quantas", () => {
  const comissoes = grupo("paulo.presidente Presidência", "joana.avaliadora Avaliação");
  const papeis = grupo("Gestor gustavo.gestor", "Auditor demo.auditor");

  const total = filtrar("avaliacao", [comissoes, papeis]);

  assert.equal(total, 1);
  assert.deepEqual(
    comissoes.linhas.map((l) => l.hidden),
    [true, false]
  );
});

test("o grupo sem nenhuma linha à vista some junto", () => {
  const comissoes = grupo("paulo.presidente Presidência");
  const papeis = grupo("Gestor gustavo.gestor");

  filtrar("gestor", [comissoes, papeis]);

  assert.equal(comissoes.elemento.hidden, true);
  assert.equal(papeis.elemento.hidden, false);
});

test("termo vazio devolve a lista inteira", () => {
  const comissoes = grupo("paulo.presidente");
  filtrar("ninguém", [comissoes]);

  const total = filtrar("", [comissoes]);

  assert.equal(total, 1);
  assert.equal(comissoes.linhas[0].hidden, false);
  assert.equal(comissoes.elemento.hidden, false);
});
