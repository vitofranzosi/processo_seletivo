/* A emissão do relatório do Edital (099): um clique, uma emissão.

   O que se afirma é a regra: o segundo envio, enquanto o primeiro está a caminho, é cancelado; o
   botão diz que está emitindo e volta depois do prazo, com a frase do que fazer. A ligação com o
   documento é do navegador, verificada no painel. Sem o shim de `dom.js`: objetos simples. */

const assert = require("node:assert/strict");
const { test } = require("node:test");

const emissao = require("../../processo_seletivo/interface/static/interface/relatorio-do-edital.js");

function montar() {
  const ouvintes = {};
  const formulario = {
    addEventListener: (tipo, ouvinte) => {
      ouvintes[tipo] = ouvinte;
    },
  };
  const atributos = {};
  const botao = {
    textContent: "Emitir e baixar PDF",
    setAttribute: (chave, valor) => {
      atributos[chave] = valor;
    },
    removeAttribute: (chave) => {
      delete atributos[chave];
    },
  };
  const situacao = { textContent: "" };
  const agendados = [];
  emissao.ligar(formulario, botao, situacao, (funcao, espera) => agendados.push([funcao, espera]));
  function enviar() {
    const evento = { cancelado: false, preventDefault: () => (evento.cancelado = true) };
    ouvintes.submit(evento);
    return evento;
  }
  return { botao, atributos, situacao, agendados, enviar };
}

test("o primeiro envio segue, e o botão diz que está emitindo", () => {
  const tela = montar();
  const evento = tela.enviar();
  assert.equal(evento.cancelado, false);
  assert.equal(tela.botao.textContent, emissao.EMITINDO);
  assert.equal(tela.atributos["aria-disabled"], "true");
  assert.equal(tela.situacao.textContent, emissao.A_CAMINHO);
});

test("o segundo envio, com o primeiro a caminho, não vira outra emissão", () => {
  const tela = montar();
  tela.enviar();
  assert.equal(tela.enviar().cancelado, true);
  assert.equal(tela.agendados.length, 1);
});

test("passado o prazo, o botão volta e a frase diz o que fazer", () => {
  const tela = montar();
  tela.enviar();
  const [voltar, espera] = tela.agendados[0];
  assert.equal(espera, emissao.ESPERA);
  voltar();
  assert.equal(tela.botao.textContent, "Emitir e baixar PDF");
  assert.equal("aria-disabled" in tela.atributos, false);
  assert.equal(tela.situacao.textContent, emissao.DEPOIS);
  assert.equal(tela.enviar().cancelado, false, "depois do prazo, emitir de novo é possível");
});
