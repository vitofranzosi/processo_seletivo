/* O preenchimento assistido por CEP, executado de verdade (029, T030).

   O que se prende aqui é **o efeito**, e não a presença da mensagem no fonte: qual campo fecha,
   qual abre, o que é sugerido sem sobrescrever, e o que acontece quando a base não responde.

   **O caso que mais importa é a falha.** A `FR-390` diz que indisponibilidade, ausência do CEP na
   base ou resposta incompleta não impedem preenchimento, envio, inscrição nem matrícula. Um
   script que travasse o formulário numa dessas transformaria serviço auxiliar em porta de
   entrada — e o teste da falha é o único que prova que ele não faz isso. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/portal/static/portal/cep.js");

const CAMPOS = ["cep", "logradouro", "bairro", "municipio", "uf", "aviso-do-cep"];

/* **A UF é um `<select>`, e modelá-la como `<input>` escondeu um defeito.** `readonly` não existe
   para lista: o atributo era escrito, o navegador o ignorava, e a UF seguia editável enquanto o
   município travava. Um shim que não reproduz o tipo do controle aprova o que o navegador recusa. */
function tagDe(nome) {
  if (nome === "aviso-do-cep") return "span";
  return nome === "uf" ? "select" : "input";
}

function tela({ valores = {}, resposta = null, falha = false } = {}) {
  const porId = {};
  CAMPOS.forEach(function (nome) {
    const elemento = new Elemento(tagDe(nome));
    elemento.value = valores[nome] || "";
    porId[nome] = elemento;
  });
  porId.cep.setAttribute("data-rota-do-cep", "/selecoes/requerimento/cep");
  porId.cep.setAttribute("data-csrf", "token-de-teste");
  globalThis.FormData = class {
    constructor() {
      this.itens = {};
    }
    append(chave, valor) {
      this.itens[chave] = valor;
    }
  };
  globalThis.__enviados = [];
  globalThis.fetch = function (rota, opcoes) {
    globalThis.__enviados.push({ rota, corpo: opcoes.body.itens });
    if (falha) {
      return Promise.reject(new Error("rede fora"));
    }
    return Promise.resolve({ json: () => Promise.resolve(resposta) });
  };
  montar({ formulario: new Elemento("form"), porId });
  carregar(SCRIPT);
  return porId;
}

async function digitar(porId, valor) {
  porId.cep.value = valor;
  porId.cep.disparar("blur");
  // Duas voltas de microtarefa: a promessa do `fetch` e a do `json()`.
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
}

test("CEP reconhecido preenche município e UF e os fecha", async () => {
  const porId = tela({
    resposta: { conferido: true, municipio: "Vitória", uf: "ES", logradouro: "Rua X", bairro: "B" },
  });

  await digitar(porId, "29040-860");

  assert.equal(porId.municipio.value, "Vitória");
  assert.equal(porId.uf.value, "ES");
  assert.equal(porId.municipio.getAttribute("readonly"), "readonly");
  assert.equal(porId.uf.disabled, true, "`readonly` não fecha um `<select>`: o que fecha é `disabled`");
  assert.match(porId["aviso-do-cep"].textContent, /vieram do CEP/);
});

test("o CEP vai no corpo, e nunca no endereço", async () => {
  const porId = tela({ resposta: { conferido: true, municipio: "Vitória", uf: "ES" } });

  await digitar(porId, "29040-860");

  const envio = globalThis.__enviados[0];
  assert.equal(envio.rota, "/selecoes/requerimento/cep");
  assert.ok(!envio.rota.includes("29040860"), "endereço em URL viaja para log e histórico");
  assert.equal(envio.corpo.cep, "29040860");
});

test("logradouro e bairro são sugeridos, e não sobrescrevem o que a pessoa digitou", async () => {
  const porId = tela({
    valores: { logradouro: "Rua que eu escrevi melhor" },
    resposta: { conferido: true, municipio: "Vitória", uf: "ES", logradouro: "Rua X", bairro: "B" },
  });

  await digitar(porId, "29040860");

  assert.equal(porId.logradouro.value, "Rua que eu escrevi melhor");
  assert.equal(porId.bairro.value, "B", "o que estava vazio recebe a sugestão");
});

test("CEP desconhecido abre os campos e não culpa quem digitou", async () => {
  const porId = tela({ valores: { municipio: "Serra" }, resposta: { conferido: false } });
  porId.municipio.setAttribute("readonly", "readonly");
  porId.uf.disabled = true;

  await digitar(porId, "29040860");

  assert.equal(porId.municipio.getAttribute("readonly"), null);
  assert.equal(porId.uf.disabled, false, "a lista volta a abrir quando a referência não responde");
  assert.equal(porId.municipio.value, "Serra", "o que a pessoa digitou fica");
  assert.match(porId["aviso-do-cep"].textContent, /não impede o envio/);
  assert.ok(
    !/inválido|incorreto|errado/i.test(porId["aviso-do-cep"].textContent),
    "o CEP pode estar certo e a base é que não o conhece"
  );
});

test("serviço fora abre os campos e o formulário continua utilizável", async () => {
  const porId = tela({ falha: true });
  porId.municipio.setAttribute("readonly", "readonly");

  await digitar(porId, "29040860");

  assert.equal(porId.municipio.getAttribute("readonly"), null);
  assert.match(porId["aviso-do-cep"].textContent, /à mão/);
});

test("CEP incompleto não consulta nada", async () => {
  const porId = tela({ resposta: { conferido: true } });

  await digitar(porId, "2904");

  assert.deepEqual(globalThis.__enviados, []);
});

test("o mesmo CEP não é consultado duas vezes", async () => {
  const porId = tela({ resposta: { conferido: true, municipio: "Vitória", uf: "ES" } });

  await digitar(porId, "29040860");
  await digitar(porId, "29040-860");

  assert.equal(globalThis.__enviados.length, 1);
});
