/* O painel do documento na Mesa (012, FR-112) — e a saída dele para a aba própria.

   O visualizador de PDF do navegador encolhe a própria barra para caber na moldura, e no Firefox o
   menu que guarda "Girar" some: a foto tirada de lado só se endireitava pelo atalho R, que ninguém
   adivinha. A aba própria devolve a barra inteira em qualquer navegador.

   O que se afirma aqui é a **regra**: o link aponta sempre para o documento que está no painel,
   abre fora desta aba e diz qual documento abre. O visualizador em si é do navegador, e o que ele
   mostra na aba própria é verificação manual. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/interface/static/interface/mesa.js");

/** `classList` que acrescenta e retira — o do shim só responde `contains`. */
function comClasses(elemento) {
  elemento.classList = {
    add: (nome) => elemento.classes.includes(nome) || elemento.classes.push(nome),
    remove: (nome) => {
      elemento.classes = elemento.classes.filter((classe) => classe !== nome);
    },
    contains: (nome) => elemento.classes.includes(nome),
  };
  return elemento;
}

function linkDeDocumento(nome, href) {
  const link = new Elemento("a", { href, target: "_blank", rel: "noopener", "data-documento": nome });
  link.button = 0;
  return link;
}

/** A Mesa em tela larga, com o painel escondido e dois documentos, como o template a renderiza. */
function mesa({ larga = true } = {}) {
  montar();
  const painel = new Elemento("aside");
  painel.hidden = true;
  const quadro = new Elemento("iframe");
  quadro.src = "about:blank";
  const barra = new Elemento("div");
  barra.appendChild = (no) => {
    no.parentNode = barra;
    barra.filhos.push(no);
    return no;
  };
  const titulo = new Elemento("h2");
  titulo.parentNode = barra;
  barra.filhos.push(titulo);
  const pontuacao = new Elemento("input");
  const identidade = linkDeDocumento("Documento de identificação com foto", "/documentos/d1");
  const diploma = linkDeDocumento("Diploma de graduação", "/documentos/d2");

  const porId = {
    "painel-documento": painel,
    "painel-documento-quadro": quadro,
    "painel-documento-titulo": titulo,
    pontuacao,
  };
  const porClasse = {
    ".mesa-trabalho": comClasses(new Elemento("div")),
    ".pagina-da-inscricao": comClasses(new Elemento("div")),
  };
  const documento = globalThis.__documento;
  documento.getElementById = (id) => porId[id] || null;
  documento.querySelector = (seletor) => porClasse[seletor] || null;
  documento.querySelectorAll = (seletor) => (seletor === "[data-documento]" ? [identidade, diploma] : []);
  const consulta = { matches: larga, addEventListener: () => {} };
  globalThis.window.matchMedia = () => consulta;

  carregar(SCRIPT);
  const [, avulso, fechador] = barra.filhos;
  return { painel, quadro, titulo, barra, avulso, fechador, identidade, diploma };
}

test("a barra do painel oferece a aba própria antes do Fechar", () => {
  const { barra, avulso, fechador } = mesa();

  assert.equal(barra.filhos.length, 3);
  assert.equal(avulso.tagName, "a");
  assert.equal(avulso.textContent, "Abrir em aba própria");
  assert.equal(avulso.getAttribute("target"), "_blank");
  assert.equal(avulso.getAttribute("rel"), "noopener");
  assert.equal(fechador.textContent, "Fechar");
});

test("o link leva ao documento que está no painel, e diz qual é", () => {
  const { quadro, avulso, identidade } = mesa();

  const clique = identidade.disparar("click", { button: 0 });

  assert.ok(clique.impedido, "em tela larga o clique abre no painel, e não na aba");
  assert.equal(quadro.src, "/documentos/d1");
  assert.equal(avulso.getAttribute("href"), "/documentos/d1");
  // O nome acessível começa pelo texto visível (WCAG 2.5.3): quem comanda por voz diz o que lê.
  assert.equal(
    avulso.getAttribute("aria-label"),
    "Abrir em aba própria: Documento de identificação com foto"
  );
});

test("trocar de documento troca o destino — nunca abre o anterior", () => {
  const { avulso, identidade, diploma } = mesa();

  identidade.disparar("click", { button: 0 });
  diploma.disparar("click", { button: 0 });

  assert.equal(avulso.getAttribute("href"), "/documentos/d2");
  assert.equal(avulso.getAttribute("aria-label"), "Abrir em aba própria: Diploma de graduação");
});

test("fechar o painel tira o destino do link", () => {
  const { painel, avulso, fechador, identidade } = mesa();

  identidade.disparar("click", { button: 0 });
  fechador.disparar("click");

  assert.equal(painel.hidden, true);
  assert.equal(avulso.getAttribute("href"), null);
});

test("em tela estreita o link do documento continua sendo o link de sempre", () => {
  const { painel, avulso, identidade } = mesa({ larga: false });

  const clique = identidade.disparar("click", { button: 0 });

  assert.equal(clique.impedido, false);
  assert.equal(painel.hidden, true);
  assert.equal(avulso.getAttribute("href"), null);
});
