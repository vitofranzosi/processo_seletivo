/* A correção da convocação (120): o vencimento informado estende, antecipa ou mantém o prazo.

   Sem o shim de `dom.js`: objetos simples, como o teste da emissão do relatório. A ligação com a
   página é do navegador, verificada no painel e na jornada do `navegador/`. */

const assert = require("node:assert/strict");
const { test } = require("node:test");

const correcao = require("../../processo_seletivo/interface/static/interface/correcao-da-convocacao.js");

const ATUAL = "2026-11-10T18:00";
const REGRAS = "Um vencimento posterior ao atual estende o prazo; anterior o antecipa; igual o mantém.";

function montar({ eventos = [] } = {}) {
  const ouvintes = {};
  const ouvir = (nome) => (tipo, funcao) => {
    ouvintes[nome + ":" + tipo] = funcao;
  };
  const formulario = { getAttribute: (chave) => (chave === "data-vencimento-atual" ? ATUAL : null) };
  const campo = { value: "", addEventListener: ouvir("campo") };
  const opcoes = [{ getAttribute: () => null }, ...eventos.map((fim) => ({ getAttribute: () => fim }))];
  const evento = eventos.length
    ? { value: "", options: opcoes, selectedIndex: 0, addEventListener: ouvir("evento") }
    : null;
  const regiao = { textContent: REGRAS };
  correcao.ligar(formulario, campo, evento, regiao);
  return {
    regiao,
    digitar(valor) {
      campo.value = valor;
      ouvintes["campo:input"]();
    },
    escolher(indice) {
      evento.value = indice ? "evento-" + indice : "";
      evento.selectedIndex = indice;
      ouvintes["evento:change"]();
    },
  };
}

test("sem valor, a região diz as três regras", () => {
  assert.equal(montar().regiao.textContent, REGRAS);
});

test("posterior ao atual estende, e diz até quando", () => {
  const tela = montar();
  tela.digitar("2026-11-20T18:00");
  assert.equal(tela.regiao.textContent, correcao.ESTENDE + "20/11/2026 às 18h00.");
});

test("anterior ao atual antecipa, e avisa que encurta um prazo já comunicado", () => {
  const tela = montar();
  tela.digitar("2026-11-08T09:30");
  assert.match(tela.regiao.textContent, /^O prazo é antecipado para 08\/11\/2026 às 09h30/);
  assert.match(tela.regiao.textContent, /encurta um prazo já comunicado/);
});

test("igual ao atual mantém", () => {
  const tela = montar();
  tela.digitar(ATUAL);
  assert.equal(tela.regiao.textContent, correcao.MANTEM);
});

test("o fim do Evento escolhido vale no lugar do campo", () => {
  const tela = montar({ eventos: ["2026-12-01T23:59"] });
  tela.digitar("2026-11-08T09:30");
  tela.escolher(1);
  assert.equal(tela.regiao.textContent, correcao.ESTENDE + "01/12/2026 às 23h59.");
});

test("apagado o valor, a região volta às três regras", () => {
  const tela = montar();
  tela.digitar("2026-11-20T18:00");
  tela.digitar("");
  assert.equal(tela.regiao.textContent, REGRAS);
});

test("os segundos que o navegador acrescente não mudam a comparação", () => {
  assert.equal(correcao.efeito(ATUAL, ATUAL + ":00").chave, "mantido");
});
