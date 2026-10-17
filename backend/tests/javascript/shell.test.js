/* FR-1725 a FR-1729 — a barra retrátil do shell da gestão.

   O que se afirma é a regra: qual estado vale quando nada foi guardado, o que a troca grava, e o
   que o controle diz. A ligação com o documento — `currentScript`, o clique, o primeiro quadro sem
   salto — é do navegador, e está no quickstart da 076. Sem o shim de `dom.js`: as funções recebem
   objetos simples. */

const assert = require("node:assert/strict");
const { test } = require("node:test");

const shell = require("../../processo_seletivo/interface/static/interface/shell.js");

function armazenamento(inicial = {}) {
  const dados = { ...inicial };
  return {
    dados,
    getItem: (chave) => (chave in dados ? dados[chave] : null),
    setItem: (chave, valor) => {
      dados[chave] = valor;
    },
  };
}

test("a escolha guardada vale, qualquer que seja a largura da janela", () => {
  assert.equal(shell.estadoInicial("recolhida", true), "recolhida");
  assert.equal(shell.estadoInicial("expandida", false), "expandida");
});

test("sem escolha, a barra começa expandida na janela larga e recolhida na estreita", () => {
  assert.equal(shell.estadoInicial(null, true), "expandida");
  assert.equal(shell.estadoInicial(null, false), "recolhida");
  // Valor estranho no armazenamento não é escolha.
  assert.equal(shell.estadoInicial("lateral", true), "expandida");
});

test("alternar troca os dois estados, e só eles", () => {
  assert.equal(shell.alternar("expandida"), "recolhida");
  assert.equal(shell.alternar("recolhida"), "expandida");
});

test("a troca fica guardada para a tela seguinte", () => {
  const local = armazenamento();

  shell.gravar(local, "recolhida");

  assert.equal(shell.ler(local), "recolhida");
  assert.deepEqual(local.dados, { [shell.CHAVE]: "recolhida" });
});

test("armazenamento que recusa não impede a troca nem derruba a leitura", () => {
  const recusa = {
    getItem: () => {
      throw new Error("SecurityError");
    },
    setItem: () => {
      throw new Error("QuotaExceededError");
    },
  };

  assert.equal(shell.ler(recusa), null);
  assert.doesNotThrow(() => shell.gravar(recusa, "recolhida"));
  assert.equal(shell.ler(null), null);
});

test("o controle diz o que fará, e o estado em que a barra está", () => {
  const atributos = {};
  const controle = {
    setAttribute: (nome, valor) => {
      atributos[nome] = valor;
    },
    rotulo: { textContent: "" },
  };

  shell.descrever(controle, "expandida");
  assert.equal(atributos["aria-expanded"], "true");
  assert.equal(controle.rotulo.textContent, "Recolher a barra lateral");

  shell.descrever(controle, "recolhida");
  assert.equal(atributos["aria-expanded"], "false");
  assert.equal(controle.rotulo.textContent, "Expandir a barra lateral");
});
