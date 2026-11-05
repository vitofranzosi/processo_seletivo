/* O progresso do envio, com e sem htmx (121, FR-3872, R-007).

   Sem o shim de `dom.js`: objetos simples, como o teste da correção da convocação. O que se prova é
   a regra — no formulário do htmx, o percentual; no da convocação, sem `hx-post`, o aviso aparece no
   `submit` e o botão desabilita. O foco e o retorno à âncora são do navegador, e estão na jornada do
   `navegador/`. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/portal/static/portal/envio.js");

function elemento(atributos = {}) {
  const attrs = { ...atributos };
  return {
    hidden: true,
    disabled: false,
    value: 0,
    hasAttribute: (nome) => Object.prototype.hasOwnProperty.call(attrs, nome),
    removeAttribute: (nome) => {
      delete attrs[nome];
    },
    attrs,
  };
}

function formulario(atributos) {
  const barra = elemento({ value: "0" });
  const bloco = elemento();
  bloco.querySelector = (seletor) => (seletor === "progress" ? barra : null);
  const botao = elemento();
  const form = elemento(atributos);
  form.querySelector = (seletor) => (seletor === ".progresso" ? bloco : null);
  form.querySelectorAll = (seletor) => (seletor === "button" ? [botao] : []);
  return { form, bloco, barra, botao };
}

function carregar(formularios) {
  const ouvintes = {};
  const janela = {};
  global.window = {
    addEventListener: (tipo, ouvinte) => {
      janela[tipo] = ouvinte;
    },
  };
  global.document = {
    body: {
      addEventListener: (tipo, ouvinte) => {
        ouvintes[tipo] = ouvinte;
      },
    },
    querySelectorAll: (seletor) => (seletor === "form[data-envio]" ? formularios : []),
  };
  delete require.cache[require.resolve(SCRIPT)];
  require(SCRIPT);
  return {
    disparar: (tipo, evento) => ouvintes[tipo](evento),
    voltar: () => janela.pageshow(),
  };
}

test("com htmx, o percentual do envio, como antes", () => {
  const { form, bloco, barra } = formulario({ "data-envio": "", "hx-post": "/x" });
  const tela = carregar([form]);

  tela.disparar("htmx:xhr:progress", {
    target: form,
    detail: { lengthComputable: true, loaded: 25, total: 100 },
  });

  assert.equal(bloco.hidden, false);
  assert.equal(barra.value, 25);
});

test("com htmx, o submit nativo não mexe no formulário", () => {
  const { form, bloco, botao } = formulario({ "data-envio": "", "hx-post": "/x" });
  const tela = carregar([form]);

  tela.disparar("submit", { target: form });

  assert.equal(bloco.hidden, true);
  assert.equal(botao.disabled, false);
});

test("sem hx-post, o submit mostra o aviso e desabilita o botão", () => {
  const { form, bloco, barra, botao } = formulario({ "data-envio": "" });
  const tela = carregar([form]);

  tela.disparar("submit", { target: form });

  assert.equal(bloco.hidden, false, "o aviso de não fechar a página aparece");
  assert.equal(botao.disabled, true, "o segundo clique não envia de novo");
  assert.equal(barra.hasAttribute("value"), false, "sem medida, a barra fica indeterminada");
});

test("formulário sem data-envio fica de fora", () => {
  const { form, bloco, botao } = formulario({});
  const tela = carregar([form]);

  tela.disparar("submit", { target: form });

  assert.equal(bloco.hidden, true);
  assert.equal(botao.disabled, false);
});

test("a volta pelo cache do navegador devolve o botão", () => {
  const { form, bloco, botao } = formulario({ "data-envio": "" });
  const tela = carregar([form]);
  tela.disparar("submit", { target: form });

  tela.voltar();

  assert.equal(bloco.hidden, true);
  assert.equal(botao.disabled, false);
});
