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
function linhaRemovivel({
  valores = {},
  filhas = 0,
  rotulo = "Perfil de Vaga",
  agrupamento = false,
  atributos = {},
} = {}) {
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
    filha.classes = ["linha", "modalidade"];
    filha.parentNode = linha;
    linha.filhos.push(filha);
  }
  // Agrupamento **estrutural**, como o `fieldset.campo.caracter` da linha de Etapa. Não é item:
  // toda Etapa tem um, inclusive a vazia. Foi contá-lo que fez a Etapa vazia pedir confirmação.
  if (agrupamento) {
    const grupo = new Elemento("fieldset");
    grupo.classes = ["campo", "caracter"];
    grupo.parentNode = linha;
    linha.filhos.push(grupo);
  }

  const botao = new Elemento("button", atributos);
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


/* Os dois defeitos que a revisão encontrou, e que o DOM simplificado não representava. */

test("uma Etapa vazia não pergunta, apesar do agrupamento estrutural do Caráter", () => {
  // `_etapa.html` tem um `fieldset.campo.caracter` dentro da linha. Contá-lo como item fazia
  // **toda** Etapa — inclusive a recém-criada — pedir confirmação, contra a própria regra.
  const alvo = linhaRemovivel({
    valores: { "etapa-0-id": "abc", "etapa-0-name": "" },
    rotulo: "Etapa de Avaliação",
    agrupamento: true,
  });
  const { evento, perguntas } = remover(alvo);

  assert.equal(evento.impedido, false, "agrupamento de rótulo não é item a perder");
  assert.deepEqual(perguntas, []);
});

test("uma Etapa preenchida continua perguntando, e não conta o Caráter como item", () => {
  const alvo = linhaRemovivel({
    valores: { "etapa-0-name": "Prova didática" },
    rotulo: "Etapa de Avaliação",
    agrupamento: true,
  });
  const { perguntas } = remover(alvo);

  assert.match(perguntas[0], /1 campo preenchido/);
  assert.ok(!/item/.test(perguntas[0]), "o Caráter não pode aparecer como item descartado");
});

test("botão sem a classe perigo, mas que remove a própria linha, também confirma", () => {
  // "Não acrescentar este Perfil" na tela de Retificação: descartava tudo em silêncio.
  const alvo = linhaRemovivel({
    valores: { "novo-perfil-0-code": "PROF" },
    atributos: { "hx-target": "closest fieldset", "hx-swap": "outerHTML" },
  });
  alvo.botao.classes = ["acao"];
  const { evento, disparou, perguntas } = remover(alvo);

  assert.equal(evento.impedido, true);
  assert.equal(disparou, true);
  assert.match(perguntas[0], /1 campo preenchido/);
});

test("botão que não remove a própria linha continua fora", () => {
  const alvo = linhaRemovivel({
    valores: { "perfil-0-code": "PROF" },
    atributos: { "hx-target": "#modalidades-0", "hx-swap": "beforeend" },
  });
  alvo.botao.classes = ["acao"];
  const { evento, perguntas } = remover(alvo);

  assert.equal(evento.impedido, false, "acrescentar não é remover");
  assert.deepEqual(perguntas, []);
});

/* A marcação de remoção da tela de Retificação: `htmx:confirm` nunca dispara ali. */

function marcarRemocao(alvo, { responder = true } = {}) {
  montar({});
  carregar(SCRIPT);
  globalThis.__resposta = responder;
  const caixa = new Elemento("input", { name: "remover:r7", type: "checkbox" });
  caixa.type = "checkbox";
  caixa.parentNode = alvo.linha;
  alvo.linha.filhos.push(caixa);
  caixa.checked = true;
  globalThis.__documento.disparar("change", caixa);
  return { caixa, perguntas: globalThis.__perguntas };
}

test("marcar Remover do Edital confirma antes de descartar", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-name": "Professor" } });
  const { caixa, perguntas } = marcarRemocao(alvo);

  assert.equal(caixa.checked, true, "confirmado, a marcação permanece");
  assert.match(perguntas[0], /1 campo preenchido/);
});

test("cancelar desmarca a caixa em vez de deixar a remoção pedida", () => {
  const alvo = linhaRemovivel({ valores: { "perfil-0-name": "Professor" } });
  const { caixa } = marcarRemocao(alvo, { responder: false });

  assert.equal(caixa.checked, false, "cancelar não pode deixar a linha marcada para remoção");
});

test("a própria caixa de remoção não conta como campo descartado", () => {
  // O evento chega **depois** de a caixa ficar marcada: contá-la inflava o número anunciado.
  const alvo = linhaRemovivel({ valores: { "perfil-0-name": "Professor" } });
  const { perguntas } = marcarRemocao(alvo);

  assert.match(perguntas[0], /1 campo preenchido/);
  assert.ok(!/2 campos/.test(perguntas[0]), "a marcação de remoção não é conteúdo a perder");
});

test("desmarcar não pergunta, porque desfazer não perde nada", () => {
  montar({});
  carregar(SCRIPT);
  const alvo = linhaRemovivel({ valores: { "perfil-0-name": "Professor" } });
  const caixa = new Elemento("input", { name: "remover:r7", type: "checkbox" });
  caixa.type = "checkbox";
  caixa.parentNode = alvo.linha;
  caixa.checked = false;

  globalThis.__documento.disparar("change", caixa);

  assert.deepEqual(globalThis.__perguntas, []);
});
