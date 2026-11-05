/* O nome do arquivo escolhido no cartão (121, FR-3872, SC-1163).

   Sem o shim de `dom.js`: objetos simples. O cartão da convocação usa o mesmo `arquivo.js` da
   inscrição, e o que se prova é que, escolhido o arquivo, `[data-nome-do-arquivo]` diz o nome dele,
   e não "Nenhum arquivo escolhido". */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/portal/static/portal/arquivo.js");

function classes() {
  const lista = new Set();
  return {
    toggle: (nome, ligar) => (ligar ? lista.add(nome) : lista.delete(nome)),
    contains: (nome) => lista.has(nome),
  };
}

function cartao() {
  const nome = { textContent: "Nenhum arquivo escolhido", classList: classes() };
  const enviar = { classList: classes() };
  const ouvintes = {};
  const campo = {
    files: [],
    closest: (seletor) =>
      seletor === ".escolher"
        ? { querySelector: (s) => (s === "[data-nome-do-arquivo]" ? nome : null) }
        : null,
    form: { querySelector: (s) => (s === "button[type=submit]" ? enviar : null) },
    addEventListener: (tipo, ouvinte) => {
      ouvintes[tipo] = ouvinte;
    },
  };
  return { campo, nome, enviar, escolher: (arquivos) => {
    campo.files = arquivos;
    ouvintes.change();
  } };
}

function carregar(campos) {
  global.document = {
    querySelectorAll: (seletor) => (seletor === "[data-arquivo]" ? campos : []),
    body: { addEventListener: () => {} },
  };
  delete require.cache[require.resolve(SCRIPT)];
  require(SCRIPT);
}

test("escolhido o arquivo, o cartão diz o nome dele", () => {
  const um = cartao();
  carregar([um.campo]);

  um.escolher([{ name: "certidao-de-nascimento.pdf" }]);

  assert.equal(um.nome.textContent, "certidao-de-nascimento.pdf");
  assert.notEqual(um.nome.textContent, "Nenhum arquivo escolhido");
  assert.equal(um.nome.classList.contains("escolhido"), true);
});

test("desfeita a escolha, volta o texto que diz o que fazer", () => {
  const um = cartao();
  carregar([um.campo]);

  um.escolher([{ name: "historico.pdf" }]);
  um.escolher([]);

  assert.equal(um.nome.textContent, "Nenhum arquivo escolhido");
});

test("cada cartão diz o seu arquivo", () => {
  const primeiro = cartao();
  const segundo = cartao();
  carregar([primeiro.campo, segundo.campo]);

  segundo.escolher([{ name: "comprovante.pdf" }]);

  assert.equal(primeiro.nome.textContent, "Nenhum arquivo escolhido");
  assert.equal(segundo.nome.textContent, "comprovante.pdf");
});
