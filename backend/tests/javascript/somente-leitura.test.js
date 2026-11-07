/* A simulação em somente leitura recebe o que o cartão mostra (132, FR-4507, D-004).

   O que se afirma aqui é a **regra**: de uma lista de campos, o que cada desabilitado mandaria.
   O que estes testes NÃO provam: a ligação com o `htmx:configRequest` no navegador — verificada
   pela tela, na verificação da spec. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/somente-leitura.js")
);

test("só o desabilitado entra: o habilitado o htmx já leva", () => {
  const pares = regras.valoresDesabilitados([
    { name: "marco-a-0-code", type: "text", value: "SORT", disabled: true },
    { name: "marco-a-0-name", type: "text", value: "Sorteio", disabled: false },
  ]);
  assert.deepEqual(pares, [["marco-a-0-code", "SORT"]]);
});

test("caixa desmarcada não manda nada, como no envio do formulário", () => {
  const pares = regras.valoresDesabilitados([
    { name: "marcado", type: "checkbox", value: "on", checked: true, disabled: true },
    { name: "desmarcado", type: "checkbox", value: "on", checked: false, disabled: true },
    { name: "opcao", type: "radio", value: "B", checked: true, disabled: true },
  ]);
  assert.deepEqual(pares, [
    ["marcado", "on"],
    ["opcao", "B"],
  ]);
});

test("botão e campo sem nome ficam de fora", () => {
  const pares = regras.valoresDesabilitados([
    { name: "aplicar", type: "submit", value: "marco:0:0", disabled: true },
    { name: "", type: "text", value: "x", disabled: true },
  ]);
  assert.deepEqual(pares, []);
});

test("seleção múltipla manda cada opção marcada", () => {
  const pares = regras.valoresDesabilitados([
    {
      name: "etapas",
      type: "select-multiple",
      multiple: true,
      disabled: true,
      options: [
        { value: "e1", selected: true },
        { value: "e2", selected: false },
        { value: "e3", selected: true },
      ],
    },
  ]);
  assert.deepEqual(pares, [
    ["etapas", "e1"],
    ["etapas", "e3"],
  ]);
});

test("seleção simples manda o valor escolhido", () => {
  const pares = regras.valoresDesabilitados([
    {
      name: "producao",
      type: "select-one",
      value: "POR_SORTEIO",
      disabled: true,
      options: [{ value: "POR_PONTUACAO" }, { value: "POR_SORTEIO", selected: true }],
    },
  ]);
  assert.deepEqual(pares, [["producao", "POR_SORTEIO"]]);
});
