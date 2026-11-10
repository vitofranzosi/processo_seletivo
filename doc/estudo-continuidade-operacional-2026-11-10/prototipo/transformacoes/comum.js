// Núcleo comum das transformações. Roda no navegador, sobre o HTML real salvo, em tempo de
// montagem: nada disto vai para o "depois" como script. O que sai é HTML estático, sem estilo nem
// script inline, porque a CSP da gestão os recusaria.
//
// `ctx` chega de montar_depois.py: { antes, paginas, centro }, com os nomes de arquivo do protótipo.

const main = document.querySelector("main");

function el(tag, atributos = {}, ...filhos) {
  const no = document.createElement(tag);
  for (const [nome, valor] of Object.entries(atributos)) no.setAttribute(nome, valor);
  for (const filho of filhos) no.append(typeof filho === "string" ? document.createTextNode(filho) : filho);
  return no;
}

function porTexto(seletor, trecho, raiz = document) {
  return [...raiz.querySelectorAll(seletor)].find((no) => no.textContent.includes(trecho)) || null;
}

function exigir(no, descricao) {
  // A montagem falha alto quando a tela real mudou: um "depois" que não encontrou o que transformar
  // mostraria o "antes" com outro nome, e a comparação mentiria.
  if (!no) throw new Error(`não encontrado no HTML real: ${descricao}`);
  return no;
}

// A faixa do protótipo, as folhas e o caminho de volta ao "antes".
document.head.append(el("link", { rel: "stylesheet", href: "/static/prototipo/continuidade.css" }));
main.prepend(
  el(
    "p",
    { class: "prototipo-faixa" },
    "Protótipo · depois · ",
    el("a", { href: `../antes/${ctx.antes}` }, "ver a tela real (antes)"),
    " · ",
    el("a", { href: "../index.html" }, "índice do protótipo"),
  ),
);

// Os formulários não gravam no protótipo: o que leva adiante vira link, um a um, nas transformações.
for (const form of document.querySelectorAll("main form")) form.setAttribute("action", "#");

// M-01: o retorno ao Centro, no bloco que a tela já mostra depois de um ato (127, FR-4090).
function retornoAoCentro(depoisDe, destino, rotulo = "Voltar ao Centro de Controle do Edital") {
  const p = el("p", { class: "retorno-ao-centro" }, el("a", { href: destino }, rotulo));
  depoisDe.after(p);
  return p;
}
