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

function carregarCom(bruto, opcoes = {}) {
  const armazem = new Armazem(bruto === null ? {} : { [CHAVE]: bruto });
  const form = opcoes.semFormulario ? null : formulario();
  montar({ formulario: form, armazem, rascunhoSalvo: opcoes.rascunhoSalvo ?? null });
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

/* O recibo do servidor — a metade que faltava.

   Sem ela, salvar o rascunho recarregava a tela dizendo "Rascunho salvo" e, logo abaixo, "há
   preenchimento não enviado neste navegador": duas frases contraditórias sobre o mesmo ato, na
   mesma tela, no mesmo segundo. A comparação por conteúdo não desfazia o engano porque o
   servidor normaliza o que recebe, e o digitado nunca volta textualmente igual. */

test("o que o servidor confirma ter recebido é apagado do navegador", () => {
  const armazem = carregarCom(guardado(60_000), { rascunhoSalvo: "edital:perfis:ana" });

  assert.equal(armazem.removeuORascunho, true);
  assert.equal(armazem.getItem(CHAVE), null);
});

test("o recibo apaga a etapa que foi gravada, e não a que está na tela", () => {
  // "Avançar" grava uma etapa e abre a seguinte: o recibo fala da anterior.
  const outra = "ps:rascunho:edital:cronograma:ana";
  const armazem = new Armazem({ [CHAVE]: guardado(60_000), [outra]: guardado(60_000) });
  montar({ formulario: formulario(), armazem, rascunhoSalvo: "edital:cronograma:ana" });
  carregar(SCRIPT);

  assert.equal(armazem.getItem(outra), null, "a etapa gravada foi apagada");
  assert.notEqual(armazem.getItem(CHAVE), null, "a etapa em edição continua guardada");
});

test("o recibo é honrado mesmo numa etapa que não guarda rascunho", () => {
  // Conteúdo e Revisão não têm formulário com rascunho local, e "Avançar" pode parar numa delas.
  const armazem = carregarCom(guardado(60_000), {
    rascunhoSalvo: "edital:perfis:ana",
    semFormulario: true,
  });

  assert.equal(armazem.removeuORascunho, true);
});

test("sem recibo, o rascunho recente continua sendo oferecido", () => {
  const armazem = carregarCom(guardado(60_000), { rascunhoSalvo: null });

  assert.equal(armazem.removeuORascunho, false);
});
