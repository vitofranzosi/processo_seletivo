/* O visualizador do documento — a Mesa (012, FR-112) e a conferência da convocação (157).

   O que se afirma aqui é a **regra** do script: o que abre no painel e o que abre fora da página, o
   que se guarda na aba e o que se restaura, onde o foco vai, e que nada carrega sem clique. O
   visualizador de PDF em si é do navegador, e o que ele desenha é verificação no navegador
   (quickstart da 157).

   **Um DOM próprio, e não o `dom.js`.** O shim comum responde a poucos seletores e não tem árvore:
   o visualizador sobe e desce a árvore (`closest`, `contains`, `replaceWith`), e um shim que
   fingisse responder deixaria o teste passar sem exercer nada. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/interface/static/interface/visualizador.js");

// --- Um DOM pequeno, com árvore ----------------------------------------------------------------

class No {
  constructor(tag, atributos = {}) {
    this.tagName = tag.toUpperCase();
    this.atributos = {};
    this.filhos = [];
    this.parentNode = null;
    this.ouvintes = {};
    this.textContent = "";
    this.hidden = false;
    this.value = "";
    this.checked = false;
    this.open = false;
    this.classes = [];
    this.classList = {
      add: (c) => this.classes.includes(c) || this.classes.push(c),
      remove: (c) => (this.classes = this.classes.filter((x) => x !== c)),
      contains: (c) => this.classes.includes(c),
    };
    Object.entries(atributos).forEach(([k, v]) => this.setAttribute(k, v));
  }
  get id() {
    return this.atributos.id || "";
  }
  get name() {
    return this.atributos.name || "";
  }
  get type() {
    return this.atributos.type || (this.tagName === "INPUT" ? "text" : "");
  }
  set type(v) {
    this.atributos.type = v;
  }
  set className(v) {
    this.classes = String(v).split(/\s+/).filter(Boolean);
  }
  setAttribute(k, v) {
    this.atributos[k] = String(v);
    if (k === "class") this.className = v;
    if (k === "value") this.value = String(v);
  }
  getAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.atributos, k) ? this.atributos[k] : null;
  }
  hasAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.atributos, k);
  }
  removeAttribute(k) {
    delete this.atributos[k];
  }
  appendChild(no) {
    if (no.parentNode) no.remove();
    no.parentNode = this;
    this.filhos.push(no);
    return no;
  }
  append(...nos) {
    nos.forEach((no) => this.appendChild(no));
  }
  insertBefore(no, referencia) {
    if (no.parentNode) no.remove();
    no.parentNode = this;
    const i = this.filhos.indexOf(referencia);
    this.filhos.splice(i < 0 ? this.filhos.length : i, 0, no);
    return no;
  }
  remove() {
    if (!this.parentNode) return;
    const irmaos = this.parentNode.filhos;
    irmaos.splice(irmaos.indexOf(this), 1);
    this.parentNode = null;
  }
  replaceWith(novo) {
    const pai = this.parentNode;
    const i = pai.filhos.indexOf(this);
    pai.filhos.splice(i, 1, novo);
    novo.parentNode = pai;
    this.parentNode = null;
  }
  replaceChildren(...nos) {
    this.filhos.forEach((f) => (f.parentNode = null));
    this.filhos = [];
    this.append(...nos);
  }
  contains(no) {
    for (let n = no; n; n = n.parentNode) if (n === this) return true;
    return false;
  }
  descendentes() {
    return this.filhos.flatMap((f) => [f, ...f.descendentes()]);
  }
  closest(seletor) {
    for (let n = this; n && n.tagName; n = n.parentNode) if (casa(n, seletor)) return n;
    return null;
  }
  querySelectorAll(seletor) {
    return this.descendentes().filter((n) => casa(n, seletor));
  }
  querySelector(seletor) {
    return this.querySelectorAll(seletor)[0] || null;
  }
  addEventListener(tipo, f) {
    (this.ouvintes[tipo] = this.ouvintes[tipo] || []).push(f);
  }
  removeEventListener(tipo, f) {
    this.ouvintes[tipo] = (this.ouvintes[tipo] || []).filter((x) => x !== f);
  }
  focus() {
    globalThis.document.activeElement = this;
  }
  scrollIntoView() {
    this.rolado = true;
  }
}

/** Seletores simples — tag, `.classe`, `[attr]`, `[attr=v]`, `:not([type=hidden])` —, vírgula e
 *  um nível de descendência ("form input"). É o que o script usa. */
function casa(no, seletor) {
  return seletor.split(",").some((parte) => {
    const passos = parte.trim().split(/\s+/);
    if (!casaComposto(no, passos[passos.length - 1])) return false;
    if (passos.length === 1) return true;
    for (let a = no.parentNode; a && a.tagName; a = a.parentNode) if (casaComposto(a, passos[0])) return true;
    return false;
  });
}

function casaComposto(no, composto) {
  if (!no.tagName) return false;
  let resto = composto;
  const nao = /:not\(\[(\w[\w-]*)=(\w+)\]\)/.exec(resto);
  if (nao) {
    if (no.getAttribute(nao[1]) === nao[2]) return false;
    resto = resto.replace(nao[0], "");
  }
  const tag = /^[a-z]+/i.exec(resto);
  if (tag && no.tagName !== tag[0].toUpperCase()) return false;
  for (const [, c] of resto.matchAll(/\.([\w-]+)/g)) if (!no.classes.includes(c)) return false;
  for (const [, a, v] of resto.matchAll(/\[([\w-]+)(?:=([^\]]+))?\]/g)) {
    if (!no.hasAttribute(a)) return false;
    if (v !== undefined && no.getAttribute(a) !== v) return false;
  }
  return true;
}

function el(tag, atributos = {}, ...filhos) {
  const no = new No(tag, atributos);
  filhos.forEach((f) => no.appendChild(f));
  return no;
}

class Armazem {
  constructor() {
    this.itens = {};
  }
  getItem(k) {
    return k in this.itens ? this.itens[k] : null;
  }
  setItem(k, v) {
    this.itens[k] = String(v);
  }
  removeItem(k) {
    delete this.itens[k];
  }
}

// --- As duas telas ------------------------------------------------------------------------------

/** Um cartão de documento da conferência, como `_documento_da_convocacao.html` o renderiza. */
function cartao(id, { aberto = false, motivo = "" } = {}) {
  const link = el("a", {
    href: `/doc/${id}`,
    target: "_blank",
    "data-abrir-documento": "",
    "data-documento": "Diploma de graduação",
    "data-rotulo": "Diploma de graduação — versão 1, apresentada em 11/11/2026 17:52",
    "data-tamanho": "1,2 MB",
    "data-baixar": `/doc/${id}?baixar=1`,
    "data-cartao": `/cartao/${id}`,
    "data-alvo": `item-${id}`,
    ...(aberto ? { "data-aberto": "" } : {}),
  });
  const radio = el("input", { type: "radio", name: "resultado", value: "CONFORME" });
  const texto = el("textarea", { name: "motivo", id: `motivo-${id}` });
  texto.value = motivo;
  const formulario = el(
    "form",
    {},
    el("input", { type: "hidden", name: "chave", value: "k" }),
    el("p", { class: "erro", "data-mensagem": "" }),
    radio,
    texto
  );
  const artigo = el("article", { id: `item-${id}` }, el("p", { "data-retorno": "" }), link, formulario);
  return { artigo, link, radio, texto, formulario };
}

function montar({ larga = true, mesa = false, pdf = true, armazem = new Armazem(), cartoes = ["a"] } = {}) {
  const titulo = el("h2", { id: "painel-documento-titulo", tabindex: "-1", "data-titulo-do-painel": "" });
  const identificacao = el("p", { "data-identificacao": "" });
  identificacao.textContent = "Alice Treinamento C09-01 · INS-1";
  const barra = el("div", { class: "barra-do-painel" }, titulo, ...(mesa ? [] : [identificacao]));
  const texto = el("p", { "data-texto-do-painel": "" });
  const quadro = el("iframe", { "data-quadro": "" });
  quadro.src = "about:blank";
  const painel = el("aside", { "data-painel": "" }, barra, texto, quadro);
  painel.hidden = true;
  const feitos = cartoes.map((id) => cartao(id));
  const pontuacao = el("input", { id: "pontuacao", name: "pontuacao" });
  const lista = el("div", {}, ...feitos.map((c) => c.artigo));
  const raiz = el(
    "div",
    {
      "data-visualizador": "",
      ...(mesa
        ? {
            "data-foco-ao-fechar": "#pontuacao",
            "data-prefixo-do-retorno": "Voltar ao documento ",
            "data-retorno-ao-documento": "",
          }
        : {}),
    },
    painel,
    lista,
    ...(mesa ? [el("form", { class: "avaliacao" }, pontuacao)] : [])
  );
  const anuncio = el("p", { "data-anuncio": "" });
  const corpo = el("body", {}, raiz, anuncio);
  const ouvintes = {};
  const documento = {
    activeElement: null,
    visibilityState: "visible",
    querySelector: (s) => (s === "#pontuacao" ? pontuacao : corpo.querySelector(s)),
    querySelectorAll: (s) => corpo.querySelectorAll(s),
    getElementById: (id) => corpo.descendentes().find((n) => n.id === id) || null,
    createElement: (tag) => {
      if (tag !== "template") return new No(tag);
      // O HTML que o servidor devolve: o teste registra, por texto, o elemento que ele produz.
      const molde = { content: { firstElementChild: null } };
      Object.defineProperty(molde, "innerHTML", {
        set: (html) => (molde.content.firstElementChild = (globalThis.__htmls || {})[html] || null),
      });
      return molde;
    },
    addEventListener: (t, f) => (ouvintes[t] = ouvintes[t] || []).push(f),
    disparar: (t, ev = {}) => (ouvintes[t] || []).forEach((f) => f(Object.assign(ev, { type: t }))),
  };
  globalThis.document = documento;
  const consulta = { matches: larga, addEventListener: () => {} };
  const pedidos = [];
  const janela = {
    location: { pathname: "/gestao/documentos" },
    navigator: { pdfViewerEnabled: pdf ? true : false },
    sessionStorage: armazem,
    matchMedia: () => consulta,
    setTimeout: (f) => f(),
    addEventListener: (t, f) => (ouvintes["janela:" + t] = ouvintes["janela:" + t] || []).push(f),
    fetch: (url) => {
      pedidos.push(url);
      const html = (globalThis.__respostas || {})[url] || "";
      return Promise.resolve({ ok: true, text: () => Promise.resolve(html) });
    },
  };
  globalThis.window = janela;
  if (globalThis.__antesDeCarregar) globalThis.__antesDeCarregar(feitos);
  delete require.cache[require.resolve(SCRIPT)];
  require(SCRIPT);
  const [, avulso, baixar, fechador] = barra.filhos.filter((f) => f !== identificacao);
  return { documento, painel, quadro, titulo, texto, barra, avulso, baixar, fechador, feitos, anuncio, armazem, pedidos, pontuacao, consulta };
}

function clicar(documento, alvo, extra = {}) {
  const evento = { target: alvo, button: 0, impedido: false, preventDefault() { this.impedido = true; }, ...extra };
  documento.disparar("click", evento);
  return evento;
}

const esperar = () => new Promise((r) => setImmediate(r));

// --- Tela larga: o painel -------------------------------------------------------------------------

test("a barra oferece a aba própria, o download e o fechar — e a pessoa fica na segunda linha", () => {
  const { barra, avulso, baixar, fechador } = montar();
  assert.equal(avulso.textContent, "Abrir em aba própria");
  assert.equal(avulso.getAttribute("target"), "_blank");
  assert.equal(baixar.textContent, "Baixar");
  assert.equal(fechador.textContent, "Fechar");
  // A identificação vem por último: as ações ficam na linha do nome (UX-640).
  assert.equal(barra.filhos[barra.filhos.length - 1].hasAttribute("data-identificacao"), true);
});

test("em tela larga, Abrir põe o documento no painel, com a versão, a pessoa e o tamanho", () => {
  const { documento, painel, quadro, titulo, texto, avulso, baixar, feitos } = montar();
  const evento = clicar(documento, feitos[0].link);

  assert.ok(evento.impedido, "em tela larga o clique abre no painel, e não na aba");
  assert.equal(painel.hidden, false);
  assert.equal(quadro.src, "/doc/a?painel=1");
  assert.equal(titulo.textContent, "Diploma de graduação — versão 1, apresentada em 11/11/2026 17:52");
  assert.equal(quadro.getAttribute("title"), `${titulo.textContent} — Alice Treinamento C09-01 · INS-1`);
  assert.equal(texto.textContent, "Carregando o documento (1,2 MB)…");
  assert.equal(avulso.getAttribute("href"), "/doc/a");
  assert.equal(baixar.getAttribute("href"), "/doc/a?baixar=1");
  assert.equal(feitos[0].link.getAttribute("aria-current"), "true");
  assert.equal(documento.activeElement, titulo, "o foco vai ao título do painel");
  assert.ok(feitos[0].artigo.rolado, "o cartão do item é levado à vista");
});

test("nada é pedido ao servidor sem clique (FR-6501)", () => {
  const { quadro, pedidos } = montar();
  assert.equal(quadro.src, "about:blank");
  assert.deepEqual(pedidos, []);
});

test("o navegador que declara não mostrar PDF recebe a alternativa, sem moldura", () => {
  const { documento, quadro, texto, avulso, feitos } = montar({ pdf: false });
  clicar(documento, feitos[0].link);

  assert.equal(quadro.hidden, true);
  assert.equal(quadro.src, "about:blank", "nenhum pedido pela moldura");
  assert.match(texto.textContent, /não mostra o documento dentro da página/);
  assert.equal(avulso.getAttribute("href"), "/doc/a");
});

test("Fechar esconde o painel e devolve o foco ao formulário do item", () => {
  const { documento, painel, quadro, fechador, feitos } = montar();
  clicar(documento, feitos[0].link);
  fechador.ouvintes.click[0]();

  assert.equal(painel.hidden, true);
  assert.equal(quadro.src, "about:blank");
  assert.equal(feitos[0].link.getAttribute("aria-current"), null);
  assert.equal(documento.activeElement, feitos[0].radio);
});

test("a recusa da entrega sobe para o painel, e a aba própria some", () => {
  const { documento, quadro, texto, avulso, baixar, feitos, pedidos } = montar();
  clicar(documento, feitos[0].link);
  const frase = el("p", { "data-frase-da-recusa": "" });
  frase.textContent = "O arquivo guardado não confere com o que foi recebido.";
  quadro.contentDocument = { documentElement: el("html", { "data-recusa-no-painel": "" }), querySelector: () => frase };
  quadro.ouvintes.load[0]();

  assert.equal(quadro.hidden, true);
  assert.equal(texto.textContent, "O arquivo guardado não confere com o que foi recebido.");
  assert.equal(avulso.hidden, true);
  assert.equal(baixar.hidden, true);
  assert.deepEqual(pedidos, [], "recusa não é abertura: nada a reler");
});

test("depois da entrega, o cartão é relido e a marca vem do servidor", async () => {
  const { documento, quadro, feitos, pedidos, anuncio } = montar();
  feitos[0].texto.value = "rascunho do motivo";
  clicar(documento, feitos[0].link);
  const novo = cartao("a", { aberto: true });
  globalThis.__respostas = { "/cartao/a": "<article id=item-a>" };
  globalThis.__htmls = { "<article id=item-a>": novo.artigo };
  quadro.contentDocument = { documentElement: el("html") };
  quadro.ouvintes.load[0]();
  await esperar();
  await esperar();

  assert.deepEqual(pedidos, ["/cartao/a"]);
  assert.equal(documento.getElementById("item-a"), novo.artigo);
  assert.equal(novo.texto.value, "rascunho do motivo", "o digitado sobrevive à troca");
  assert.match(anuncio.textContent, /^Aberto por você: Diploma de graduação/);
});

// --- Tela estreita: fora da página, e a volta ----------------------------------------------------

test("abaixo da tela larga o link é o de sempre, e o trabalho fica guardado na aba", () => {
  const { documento, painel, feitos, armazem } = montar({ larga: false });
  feitos[0].texto.value = "falta o verso";
  const evento = clicar(documento, feitos[0].link);

  assert.equal(evento.impedido, false);
  assert.equal(painel.hidden, true, "nenhum painel abaixo da tela larga");
  const guardado = JSON.parse(armazem.getItem("ps:visualizador:/gestao/documentos"));
  assert.equal(guardado.alvo, "item-a");
  assert.deepEqual(guardado.campos, [{ nome: "motivo", valor: "falta o verso" }]);
});

test("na volta, o cartão é relido e o retorno ao ponto recebe o foco", async () => {
  const { documento, feitos } = montar({ larga: false });
  feitos[0].texto.value = "falta o verso";
  clicar(documento, feitos[0].link);
  const novo = cartao("a", { aberto: true });
  globalThis.__respostas = { "/cartao/a": "<article id=item-a>" };
  globalThis.__htmls = { "<article id=item-a>": novo.artigo };
  documento.disparar("visibilitychange");
  await esperar();
  await esperar();

  const retorno = novo.artigo.querySelector("[data-retorno]").filhos[0];
  assert.equal(retorno.textContent, "Voltar à conferência do Diploma de graduação");
  assert.equal(documento.activeElement, retorno);
  assert.equal(novo.texto.value, "falta o verso");
  retorno.ouvintes.click[0]({ preventDefault() {} });
  assert.equal(documento.activeElement, novo.radio, "o retorno leva ao formulário do item");
});

test("com a página recarregada, o preenchimento volta, dito, e nada é enviado", () => {
  const armazem = new Armazem();
  armazem.setItem(
    "ps:visualizador:/gestao/documentos",
    JSON.stringify({ alvo: "item-a", rotulo: "Diploma de graduação — versão 1", campos: [{ nome: "motivo", valor: "falta o verso" }, { nome: "resultado", valor: "CONFORME", marcado: true }] })
  );
  const { documento, feitos, pedidos } = montar({ larga: false, armazem });

  assert.equal(feitos[0].texto.value, "falta o verso");
  assert.equal(feitos[0].radio.checked, true);
  const lugar = feitos[0].artigo.querySelector("[data-retorno]");
  assert.match(lugar.filhos[1].textContent, /Nada foi registrado ainda/);
  assert.equal(documento.activeElement, lugar.filhos[0]);
  assert.deepEqual(pedidos, []);
});

test("o preenchimento guardado não sobrescreve o que já está no formulário", () => {
  const armazem = new Armazem();
  armazem.setItem("ps:visualizador:/gestao/documentos", JSON.stringify({ alvo: "item-a", campos: [{ nome: "motivo", valor: "antigo" }] }));
  // O servidor reexibiu o formulário com o que acabou de ser digitado: ele vence o guardado.
  globalThis.__antesDeCarregar = (feitos) => (feitos[0].texto.value = "novo");
  const { feitos } = montar({ larga: false, armazem });
  delete globalThis.__antesDeCarregar;
  assert.equal(feitos[0].texto.value, "novo");
  assert.equal(feitos[0].artigo.querySelector("[data-retorno]").filhos.length, 0);
});

// --- O registro sem recarga --------------------------------------------------------------------

test("a recusa trocada no cartão recebe o foco", () => {
  const { documento, feitos } = montar();
  const recusa = el("p", { class: "erro", tabindex: "-1" });
  feitos[0].formulario.appendChild(recusa);
  documento.disparar("htmx:afterSwap", { detail: { target: feitos[0].artigo } });
  assert.equal(documento.activeElement, recusa);
});

test("a confirmação nova apaga a anterior e o guardado do item", () => {
  const armazem = new Armazem();
  const { documento, feitos } = montar({ cartoes: ["a", "b"], armazem });
  const velha = el("div", { "data-confirmacao": "" });
  feitos[1].artigo.appendChild(velha);
  armazem.setItem("ps:visualizador:/gestao/documentos", JSON.stringify({ alvo: "item-a", campos: [] }));
  feitos[0].artigo.appendChild(el("div", { "data-confirmacao": "" }));
  documento.disparar("htmx:afterSwap", { detail: { target: feitos[0].artigo } });

  assert.equal(velha.parentNode, null);
  assert.equal(armazem.getItem("ps:visualizador:/gestao/documentos"), null);
});

test("a falha de rede diz que nada foi registrado, no formulário", () => {
  const { documento, feitos } = montar();
  documento.disparar("htmx:sendError", { detail: { elt: feitos[0].formulario } });
  assert.match(feitos[0].formulario.querySelector("[data-mensagem]").textContent, /não foi registrada/);
});

// --- A Mesa ----------------------------------------------------------------------------------------

test("na Mesa, Fechar leva o foco à nota, e o retorno é ao documento", async () => {
  const { documento, fechador, feitos, pontuacao } = montar({ mesa: true });
  clicar(documento, feitos[0].link);
  fechador.ouvintes.click[0]();
  assert.equal(documento.activeElement, pontuacao);
});

test("na Mesa, a volta oferece o documento, e não o formulário", async () => {
  const { documento, feitos } = montar({ mesa: true, larga: false });
  clicar(documento, feitos[0].link);
  globalThis.__respostas = {};
  documento.disparar("visibilitychange");
  await esperar();
  await esperar();
  const retorno = feitos[0].artigo.querySelector("[data-retorno]").filhos[0];
  assert.match(retorno.textContent, /^Voltar ao documento Diploma de graduação/);
  retorno.ouvintes.click[0]({ preventDefault() {} });
  assert.equal(documento.activeElement, feitos[0].link);
});
