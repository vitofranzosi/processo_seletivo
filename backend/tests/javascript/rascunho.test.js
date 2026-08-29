/* FR-022 da 003 — o rascunho guardado tem prazo, verificado executando o script.

   O teste anterior procurava a constante no fonte. Isto aqui carrega o script contra um
   `localStorage` falso e afirma o efeito: o rascunho velho é removido sem ser oferecido, o
   recente é oferecido, e o que não tem carimbo de tempo utilizável é descartado. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Armazem, Formulario, carregar, linha, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/rascunho.js"
);
const CHAVE = "ps:rascunho:edital:perfis:ana";
const UM_DIA = 24 * 60 * 60 * 1000;

function formulario() {
  return new Formulario(
    [linha("perfil", 0, { id: "p1", code: "P1", name: "Renderizado pelo servidor" })],
    { rascunho: "edital:perfis:ana", lista: "#perfis", fragmento: "/fragmentos/perfil" }
  );
}

/** Um rascunho guardado com conteúdo diferente do renderizado, na idade pedida. */
function guardado(idadeMs, opcoes = {}) {
  // `hasOwnProperty` e não `em !== undefined`: o caso "chave ausente no JSON" precisa ser
  // distinguível de "não informei o carimbo neste teste", e é justamente ele que se quer cobrir.
  const carimbo = Object.prototype.hasOwnProperty.call(opcoes, "em")
    ? opcoes.em
    : new Date(Date.now() - idadeMs).toISOString();
  return JSON.stringify({
    em: carimbo,
    dados: {
      simples: {},
      linhas: [{ id: "p1", code: "P1", name: "O que a pessoa digitou e não enviou" }],
    },
  });
}

function carregarCom(bruto) {
  const armazem = new Armazem(bruto === null ? {} : { [CHAVE]: bruto });
  const form = formulario();
  montar({ formulario: form, armazem });
  carregar(SCRIPT);
  // O script sonda o armazenamento gravando e apagando `CHAVE + ":teste"`; só interessa aqui o
  // que aconteceu com a chave do rascunho.
  armazem.removeuORascunho = armazem.removidos.filter((chave) => chave === CHAVE).length > 0;
  return armazem;
}

test("rascunho mais velho que um dia é descartado sem ser oferecido", () => {
  const armazem = carregarCom(guardado(UM_DIA + 60_000));

  assert.equal(armazem.removeuORascunho, true);
  assert.equal(armazem.getItem(CHAVE), null);
});

test("rascunho de meses atrás também é descartado", () => {
  const armazem = carregarCom(guardado(90 * UM_DIA));

  assert.equal(armazem.removeuORascunho, true);
});

test("rascunho recente é preservado para ser oferecido", () => {
  const armazem = carregarCom(guardado(60_000));

  assert.equal(armazem.removeuORascunho, false);
  assert.notEqual(armazem.getItem(CHAVE), null);
});

test("rascunho na fronteira, com um dia menos um minuto, ainda é oferecido", () => {
  const armazem = carregarCom(guardado(UM_DIA - 60_000));

  assert.equal(armazem.removeuORascunho, false);
});

test("rascunho sem carimbo de tempo utilizável é tratado como vencido", () => {
  for (const carimbo of [undefined, "", "não é data"]) {
    const armazem = carregarCom(guardado(0, { em: carimbo }));
    assert.equal(armazem.removeuORascunho, true, `carimbo ${JSON.stringify(carimbo)}`);
  }
});

test("conteúdo corrompido é descartado em vez de derrubar a tela", () => {
  const armazem = carregarCom("{ isto não é JSON");

  assert.equal(armazem.removeuORascunho, true);
});

test("sem nada guardado, nada é removido", () => {
  const armazem = carregarCom(null);

  assert.equal(armazem.removeuORascunho, false);
});
