// Tela da convocação (jornadas D e E). M-05: um índice curto das seções, porque a tela tem 3.500 px e
// a providência do Centro mira uma seção do meio dela; M-09: "Ocupadas" diz de onde vem; M-04: o
// gesto dos titulares passa por uma conferência, sempre.

// M-05. Só as seções que a tela real tem, na ordem dela, e cada uma com a contagem que já mostra.
const secoes = [...main.querySelectorAll("h2[id]")];
const indice = el("nav", { class: "indice-da-tela", "aria-label": "Seções desta tela" }, el("strong", {}, "Nesta tela:"));
for (const h2 of secoes) indice.append(el("a", { href: `#${h2.id}` }, h2.textContent.trim()));
exigir(main.querySelector("h1 + p.sub, h1 ~ p.sub"), "subtítulo").after(indice);

// M-09. "3 Ocupadas, 0 A ocupar, 0 Convocadas" lia como "já estão ocupadas" antes de qualquer chamada.
// A contagem é da apuração, e o rótulo passa a dizê-lo; o número não muda.
for (const li of main.querySelectorAll("li, div")) {
  const rotulo = [...li.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim() === "Ocupadas");
  if (rotulo) rotulo.textContent = "Ocupadas na apuração";
  const aOcupar = [...li.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim() === "A ocupar");
  if (aOcupar) aOcupar.textContent = "A ocupar na apuração";
}

// M-02 no destino: o documento da pessoa leva à página de documentos do protótipo.
for (const [trecho, destino] of Object.entries(ctx.documentos || {})) {
  const artigo = porTexto("article.recorte", trecho);
  const link = artigo && porTexto("a", "Documentos da convocação", artigo);
  if (link) link.setAttribute("href", destino);
}

// M-04. O gesto dos titulares pratica e comunica no mesmo clique quando o complemento está vazio — e a
// ajuda prometia "antes de confirmar, você o verá". Aqui o botão leva à conferência, sempre.
const titulares = main.querySelector("section[aria-labelledby=titulares], h2#titulares")?.closest("section") || main;
const botao = porTexto("button", "Convocar as", titulares);
if (botao && ctx.conferencia) {
  const link = el("a", { class: "botao", href: ctx.conferencia }, `${botao.textContent.trim()}…`);
  botao.replaceWith(link);
  const ajuda = porTexto("span.ajuda", "antes de confirmar, você o verá como o candidato", titulares);
  if (ajuda) {
    ajuda.replaceChildren(
      el("strong", {}, "Este texto será mostrado ao candidato. "),
      "Entra depois do fundamento derivado, igual em todas as convocações deste ato. A tela seguinte mostra quem será convocado, o texto que cada pessoa lerá e o prazo, antes de praticar.",
    );
  }
}
