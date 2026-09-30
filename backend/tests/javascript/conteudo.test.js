/* A numeração da etapa Conteúdo (054, UX-130).

   O que se afirma aqui é a **regra**: dado de que depende cada seção sair, o número que ela terá.
   É a mesma regra de `pdf.numeracao`, e `test_conteudo_da_054.py` confere, do lado do servidor, que
   os dois dão o mesmo número ao conteúdo gravado.

   O que estes testes NÃO provam: a legenda atualizada ao digitar, no navegador — verificada pelo
   roteiro de quickstart.md, §4. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/conteudo.js")
);

test("a textual vazia não sai, e as seguintes são numeradas sem salto", () => {
  const numeros = regras.numerar([
    { estado: "texto", preambulo: true, texto: "A Diretora faz saber" },
    { estado: "texto", texto: "" },
    { estado: "texto", texto: "Informações" },
    { estado: "sai" },
    { estado: "nao-sai" },
    { estado: "texto", texto: "   " },
    { estado: "texto", texto: "Finais" },
  ]);
  assert.deepEqual(numeros, [0, null, 1, 2, null, null, 3]);
});

test("o preâmbulo vazio não sai, e a numeração começa em 1 do mesmo jeito", () => {
  assert.deepEqual(
    regras.numerar([
      { estado: "texto", preambulo: true, texto: "" },
      { estado: "texto", texto: "Disposições" },
    ]),
    [null, 1]
  );
});

test("a textual com norma acrescentada sai mesmo vazia — o servidor a declara 'sai'", () => {
  assert.deepEqual(regras.numerar([{ estado: "sai", texto: "" }]), [1]);
});

test("a legenda diz o número, ou por que não há número", () => {
  assert.deepEqual(regras.rotulos(4), { numero: "4. ", estado: "" });
  assert.deepEqual(regras.rotulos(null), {
    numero: "",
    estado: " (vazia — não sai no documento)",
  });
  assert.deepEqual(regras.rotulos(0), { numero: "", estado: " (preâmbulo, sem número)" });
});
