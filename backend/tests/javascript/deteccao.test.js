/* A detecção do giro do rosto (176, FR-8010 a FR-8018; research T-005 a T-008).

   As funções puras de `portal/static/portal/deteccao.js`: o giro a partir dos pontos, o rosto no
   oval, a decisão do giro mantido, o orçamento e quando o motor pode ser baixado. Sem navegador e
   sem motor: os pontos são de um rosto desenhado à mão, e o motor de verdade é da jornada no
   navegador. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const d = require(path.join(__dirname, "../../processo_seletivo/portal/static/portal/deteccao.js"));

// Um rosto de 478 pontos no meio do quadro, com o nariz e as duas bordas onde o teste mandar. Em
// coordenadas do quadro **não espelhado**: a esquerda da pessoa fica à direita do quadro.
function rosto({ nariz, direitaDaPessoa, esquerdaDaPessoa }) {
  const pontos = Array.from({ length: 478 }, () => ({ x: 0.5, y: 0.45 }));
  pontos[1] = { x: nariz, y: 0.5 };
  pontos[234] = { x: direitaDaPessoa, y: 0.45 };
  pontos[454] = { x: esquerdaDaPessoa, y: 0.45 };
  pontos[10] = { x: 0.5, y: 0.25 };
  pontos[152] = { x: 0.5, y: 0.7 };
  return pontos;
}

const DE_FRENTE = rosto({ nariz: 0.5, direitaDaPessoa: 0.38, esquerdaDaPessoa: 0.62 });
// Virada para a esquerda dela: o nariz vai para a direita do quadro, e o rosto estreita.
const PARA_A_ESQUERDA = rosto({ nariz: 0.6, direitaDaPessoa: 0.42, esquerdaDaPessoa: 0.6 });
const PARA_A_DIREITA = rosto({ nariz: 0.4, direitaDaPessoa: 0.4, esquerdaDaPessoa: 0.58 });

test("o giro é positivo à esquerda da pessoa, negativo à direita, e perto de zero de frente", () => {
  assert.ok(Math.abs(d.giroDosPontos(DE_FRENTE)) < 0.05);
  assert.ok(d.giroDosPontos(PARA_A_ESQUERDA) > d.LIMIAR_DO_GIRO);
  assert.ok(d.giroDosPontos(PARA_A_DIREITA) < -d.LIMIAR_DO_GIRO);
});

test("sem pontos, ou com o rosto sem largura, não há giro", () => {
  assert.equal(d.giroDosPontos(null), null);
  assert.equal(d.giroDosPontos([]), null);
  assert.equal(d.giroDosPontos(rosto({ nariz: 0.5, direitaDaPessoa: 0.5, esquerdaDaPessoa: 0.5 })), null);
});

test("a caixa vai do menor ao maior ponto", () => {
  const caixa = d.caixaDosPontos(DE_FRENTE);
  assert.ok(Math.abs(caixa.x - 0.38) < 1e-9);
  assert.ok(Math.abs(caixa.largura - 0.24) < 1e-9);
  assert.ok(Math.abs(caixa.y - 0.25) < 1e-9);
  assert.ok(Math.abs(caixa.altura - 0.45) < 1e-9);
});

// Um palco de 400×300 na tela, com um quadro de 1280×720 (cobre pela altura e sobra dos lados) e o
// oval no meio, de 150×200.
const QUADRO = { largura: 1280, altura: 720 };
const PALCO = { x: 0, y: 0, largura: 400, altura: 300 };
const OVAL = { x: 125, y: 50, largura: 150, altura: 200 };

test("o rosto no meio do quadro está no oval, espelhado ou não", () => {
  const caixa = { x: 0.42, y: 0.25, largura: 0.16, altura: 0.5 };
  assert.equal(d.rostoNoOval(caixa, QUADRO, PALCO, OVAL, true), true);
  assert.equal(d.rostoNoOval(caixa, QUADRO, PALCO, OVAL, false), true);
});

test("o rosto encostado num lado do quadro não está no oval, e o espelho decide de que lado", () => {
  const aEsquerdaDoQuadro = { x: 0.3, y: 0.25, largura: 0.1, altura: 0.5 };
  // Sem espelho, ele aparece à esquerda da tela, fora do oval; com espelho, à direita, também fora.
  assert.equal(d.rostoNoOval(aEsquerdaDoQuadro, QUADRO, PALCO, OVAL, false), false);
  assert.equal(d.rostoNoOval(aEsquerdaDoQuadro, QUADRO, PALCO, OVAL, true), false);
});

test("o rosto pequeno demais, longe da câmera, não conta como no oval", () => {
  const longe = { x: 0.47, y: 0.42, largura: 0.06, altura: 0.12 };
  assert.equal(d.rostoNoOval(longe, QUADRO, PALCO, OVAL, true), false);
});

test("sem caixa, sem quadro ou sem oval, o rosto não está no oval", () => {
  assert.equal(d.rostoNoOval(null, QUADRO, PALCO, OVAL, true), false);
  assert.equal(d.rostoNoOval({ x: 0.4, y: 0.2, largura: 0.2, altura: 0.5 }, { largura: 0, altura: 0 }, PALCO, OVAL, true), false);
});

function leituras(giros, passo = 150) {
  return giros.map((giro, i) => ({ ms: i * passo, giro }));
}

test("o giro mantido pelo instante é visto", () => {
  assert.equal(d.avaliarGiro(leituras([0, 0.4, 0.4, 0.4, 0.4]), "esquerda"), "visto");
  assert.equal(d.avaliarGiro(leituras([0, -0.4, -0.4, -0.4, -0.4]), "direita"), "visto");
});

test("um relance não conta", () => {
  assert.equal(d.avaliarGiro(leituras([0, 0.5, 0.5, 0]), "esquerda"), "esperando");
  assert.equal(d.avaliarGiro(leituras([0, 0.5, 0.5]), "esquerda"), "esperando");
});

test("o giro que não chega ao limiar não conta, por mais tempo que dure", () => {
  assert.equal(d.avaliarGiro(leituras([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]), "esquerda"), "esperando");
});

test("o lado oposto mantido dá outro-lado, e não visto", () => {
  assert.equal(d.avaliarGiro(leituras([0, 0.4, 0.4, 0.4, 0.4]), "direita"), "outro-lado");
  assert.equal(d.avaliarGiro(leituras([0, -0.4, -0.4, -0.4, -0.4]), "esquerda"), "outro-lado");
});

test("a leitura sem rosto interrompe a corrida", () => {
  assert.equal(d.avaliarGiro(leituras([0.4, 0.4, null, 0.4, 0.4]), "esquerda"), "esperando");
  assert.equal(d.avaliarGiro(leituras([]), "esquerda"), "esperando");
});

test("o orçamento desliga na quinta leitura lenta seguida, e não volta", () => {
  const orcamento = new d.Orcamento();
  for (let i = 0; i < d.LEITURAS_LENTAS - 1; i += 1) assert.equal(orcamento.registrar(200), true);
  assert.equal(orcamento.registrar(200), false);
  assert.equal(orcamento.registrar(10), false);
});

test("uma leitura rápida no meio zera a conta das lentas", () => {
  const orcamento = new d.Orcamento();
  for (let i = 0; i < 4; i += 1) orcamento.registrar(200);
  assert.equal(orcamento.registrar(20), true);
  for (let i = 0; i < 4; i += 1) assert.equal(orcamento.registrar(200), true);
});

test("o motor não é baixado com economia de dados, sem WebAssembly ou com a escolha de tocar", () => {
  const wasm = {};
  assert.equal(d.podeCarregar({ WebAssembly: wasm, conexao: null }), true);
  assert.equal(d.podeCarregar({ WebAssembly: wasm, conexao: { saveData: false } }), true);
  assert.equal(d.podeCarregar({ WebAssembly: wasm, conexao: { saveData: true } }), false);
  assert.equal(d.podeCarregar({ WebAssembly: null }), false);
  assert.equal(d.podeCarregar({ WebAssembly: wasm, recusada: true }), false);
  assert.equal(d.podeCarregar(null), false);
});

test("os parâmetros da decisão são os da research T-005 a T-008", () => {
  assert.equal(d.LIMIAR_DO_GIRO, 0.3);
  assert.equal(d.INSTANTE_MANTIDO, 400);
  assert.equal(d.CONFIRMACAO, 900);
  assert.equal(d.INTERVALO, 150);
  assert.equal(d.TETO_DA_LEITURA, 120);
});

test("o vigia simulado conta o giro visto e para de olhar até o pedido seguinte", async () => {
  let giro = 0;
  const vistos = [];
  const estados = [];
  const vigia = new d.Vigia({
    simulada: () => ({ caixa: null, giro }),
    aoEstado: (e) => estados.push(e),
    aoGiro: (e) => vistos.push(e),
  });
  await vigia.carregar();
  assert.deepEqual(estados, ["simulada"]);
  vigia.observar("esquerda");
  giro = 0.5;
  await new Promise((pronto) => setTimeout(pronto, d.INTERVALO * 6));
  assert.deepEqual(vistos, ["visto"]);
  assert.equal(vigia.alvo, null);
  vigia.parar();
  assert.equal(vigia.relogio, null);
});
