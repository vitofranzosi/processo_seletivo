/* T079 — confirmar antes de descartar trabalho não enviado (FR-038).

   O produto é cuidadoso com atos irreversíveis de domínio e era descuidado com a perda que
   acontece todo dia: "Remover este Perfil" apagava requisitos, modalidades e fundamentos sem
   perguntar, com o botão a poucos pixels de "↓ Descer".

   O que se afirma aqui é a **regra**: quando perguntar, quando não perguntar, e o que a pergunta
   diz. O diálogo em si é do navegador — `confirm` já tem cancelamento como padrão, teclado e
   anúncio por leitor de tela, e reimplementá-lo seria reconquistar os três. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/remocao.js"
);

/** Uma linha com legenda, campos e o botão destrutivo, como os fragmentos a renderizam. */
function linhaRemovivel({ valores = {}, filhas = 0, rotulo = "Perfil de Vaga" } = {}) {
  const linha = new Elemento("fieldset");
  const legenda = new Elemento("legend");
  legenda.textContent = rotulo;
  legenda.parentNode = linha;
  linha.filhos.push(legenda);

  for (const [nome, valor] of Object.entries(valores)) {
    // O `id` é `hidden` no template real: existe em toda linha, inclusive na recém-criada, e por
    // isso não pode contar como conteúdo digitado.
    const tipo = /-id$/.test(nome) ? "hidden" : "text";
    const campo = new Elemento("input", { name: nome, value: String(valor), type: tipo });
    campo.parentNode = linha;
    linha.filhos.push(campo);
  }
  for (let i = 0; i < filhas; i += 1) {
    const filha = new Elemento("fieldset");
    filha.parentNode = linha;
    linha.filhos.push(filha);
  }

  const botao = new Elemento("button");
  botao.classes = ["acao", "perigo"];
  botao.parentNode = linha;
  linha.filhos.push(botao);
  return { linha, botao };
}

function remover(alvo, { responder = true } = {}) {
  montar({});
  carregar(SCRIPT);
  globalThis.__resposta = responder;
  let disparou = false;
  const evento = globalThis.__documento.disparar("htmx:confirm", {
    elt: alvo.botao,
    issueRequest: () => {
      disparou = true;
    },
  });
  return { evento, disparou, perguntas: globalThis.__perguntas };
}

test("linha vazia é removida sem perguntar", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-id": "abc", "perfil-0-code": "" } });
  const { evento, perguntas } = remover(alvo);

  assert.equal(evento.impedido, false, "sem nada a perder, perguntar é ruído");
  assert.deepEqual(perguntas, []);
});

test("o campo de ordem não conta como conteúdo", () => {
  // `ordenacao.js` mantém `order` preenchido em toda linha, inclusive na recém-criada.
  const alvo = linhaRemovivel({ valores: { "evento-0-order": "1", "evento-0-type": "" } });
  const { perguntas } = remover(alvo);

  assert.deepEqual(perguntas, []);
});

test("linha com campo preenchido pergunta antes de remover", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-code": "PROF", "perfil-0-name": "" } });
  const { evento, disparou, perguntas } = remover(alvo);

  assert.equal(evento.impedido, true, "a requisição precisa esperar a decisão");
  assert.equal(disparou, true, "confirmado, a remoção acontece");
  assert.match(perguntas[0], /Perfil de Vaga/);
  assert.match(perguntas[0], /1 campo preenchido/);
  assert.match(perguntas[0], /não pode ser desfeito/);
});

test("cancelar impede a remoção", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-code": "PROF" } });
  const { disparou } = remover(alvo, { responder: false });

  assert.equal(disparou, false, "cancelar não pode remover");
});

test("itens filhos entram na conta, que é o caso de maior perda", () => {
  // Um Perfil com duas Modalidades: remover leva as duas junto, e é o que menos se vê.
  const alvo = linhaRemovivel({ valores: { "perfil-0-code": "PROF" }, filhas: 2 });
  const { perguntas } = remover(alvo);

  assert.match(perguntas[0], /1 campo preenchido e 2 itens/);
});

test("linha só com filhos também pergunta", () => {
  const alvo = linhaRemovivel({ valores: {}, filhas: 1 });
  const { evento, perguntas } = remover(alvo);

  assert.equal(evento.impedido, true);
  assert.match(perguntas[0], /1 item/);
});

test("botão que não é o destrutivo não dispara confirmação", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-code": "PROF" } });
  alvo.botao.classes = ["acao"];
  const { evento, perguntas } = remover(alvo);

  assert.equal(evento.impedido, false, "só o botão destrutivo confirma");
  assert.deepEqual(perguntas, []);
});
