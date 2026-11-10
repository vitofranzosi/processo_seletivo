// Tela do sorteio (jornada A). Melhorias M-03, M-06 e M-07, e uma frase que depende da D-5.
//
// O que NÃO muda: nenhuma regra, nenhum botão a mais ou a menos, nenhum texto do método publicado. O
// método só é recolhido, e continua a um clique; a observação só desce para depois dos recortes.

const metodo = exigir(document.querySelector("section[aria-labelledby=titulo-metodo]"), "seção do método");
const ocorrencia = exigir(document.querySelector("section[aria-labelledby=titulo-ocorrencia]"), "seção da ocorrência");
const recortes = exigir(document.querySelector("section[aria-labelledby=titulo-recortes]"), "seção dos recortes");
const artigos = [...recortes.querySelectorAll("article.recorte")];
const [ampla, ppp] = artigos;
ampla.id = "recorte-ampla";
ppp.id = "recorte-ppp";
const congeladas = artigos.filter((a) => a.textContent.includes("Relação congelada em")).length;

// M-03: o objetivo na voz do Centro, com a ponte para os nomes do GPS — o Centro diz "Fixar os
// participantes · no GPS: congelar a relação"; a tela dizia "o universo é comprometido".
const sub = exigir(main.querySelector("h1 + p.sub"), "subtítulo");
sub.textContent = "Técnico em Informática (EaD) · Edital SIM06R3/2026 · 2 listas: Ampla concorrência e PPP";
sub.after(
  el(
    "p",
    { class: "objetivo-da-tela" },
    el("strong", {}, "O que se faz aqui: "),
    "fixar os participantes de cada lista, obter a semente pública e realizar o sorteio, nesta ordem.",
  ),
  el(
    "ol",
    { class: "passos-da-tela" },
    el("li", {}, el("strong", {}, "Fixar os participantes"), ` (no GPS: publicar e congelar a relação) — ${congeladas} de 2 listas.`),
    el("li", {}, el("strong", {}, "Obter a semente pública"), " (no GPS: observar a extração) — uma só, vale para todas as listas."),
    el("li", {}, el("strong", {}, "Realizar o sorteio"), " — em cada lista fixada."),
  ),
);

// M-06: o ato antes do método. O método publicado é conteúdo do Edital, consultado; o ato é o que a
// pessoa veio fazer, e ficava a 1.500 px. Recolhido, não some: `details` com o mesmo conteúdo.
const recolhido = el("details", { class: "metodo-recolhido" });
const tituloDoMetodo = metodo.querySelector("h2");
recolhido.append(el("summary", {}, "Método declarado no Edital — algoritmo, fonte, ocorrência e resumo"));
for (const filho of [...metodo.childNodes]) if (filho !== tituloDoMetodo) recolhido.append(filho);
tituloDoMetodo.remove();
metodo.append(recolhido);
recortes.after(ocorrencia);
ocorrencia.after(metodo);

// M-03, na ponte de vocabulário: o nome da lista é o do Centro, e o do GPS fica entre parênteses.
const h3Ampla = ampla.querySelector("h3");
h3Ampla.textContent = "Ampla concorrência (todos os inscritos do recorte, sem lista de concorrência)";

for (const artigo of artigos) {
  // M-06: "Nenhum corte emitido" antes do sorteio é verdade, mas não é passo desta tela — o corte lê a
  // ordem que o sorteio ainda vai produzir. Era um aviso amarelo antes do ato, com link para fora.
  if (!artigo.textContent.includes("Sorteio realizado")) {
    porTexto("p.aviso", "Nenhum corte emitido", artigo)?.remove();
  }
  const naoComprometido = porTexto("p.aviso", "Universo ainda não comprometido", artigo);
  if (naoComprometido) {
    const n = naoComprometido.textContent.match(/Seriam (\d+)/)[1];
    naoComprometido.textContent = `Ainda não fixada. Se fixar agora, participam ${n} pessoas, com os números abaixo — e isso não muda mais.`;
    const botao = porTexto("button", "Publicar e congelar", artigo);
    // O primeiro leva ao estado seguinte do protótipo; o segundo fica, sem destino, como na tela.
    const link = el("a", { class: "botao", href: artigo === ampla ? ctx.paginas.sorteioApos : "#recorte-ppp" }, "Fixar os participantes desta lista (publicar e congelar)");
    botao.replaceWith(link);
  }
}

// A observação desce para depois dos recortes, como passo 2, e deixa de ser o botão de maior peso
// enquanto há lista por fixar. Não some e não se desabilita: isso seria decidir a D-5.
const observar = porTexto("button", "Observar a ocorrência", ocorrencia);
if (observar && congeladas < 2) {
  observar.classList.add("secundario");
  const faltam = artigos.filter((a) => !a.textContent.includes("Relação congelada em")).map((a) => a.querySelector("h3").textContent.split(" (")[0]);
  ocorrencia.querySelector("form").before(
    el(
      "p",
      { class: "dependente-da-d5" },
      `Ainda não fixada: ${faltam.join(" e ")}. Uma lista fixada depois de conhecida a semente não sorteia — o sorteio dela é recusado, e a saída é uma Retificação.`,
    ),
  );
}

// M-07 e M-01: o bloco que segue o ato. O "Ainda neste marco" vira link para a lista que falta; a
// frase da D-5 diz a consequência no lugar; e o caminho de volta ao Centro fecha o bloco.
const proximo = document.querySelector("p.proximo-nesta-lista");
if (proximo) {
  // O "Observar a extração" leva à seção da ocorrência desta mesma tela, e não ao topo dela.
  proximo.querySelector("a")?.setAttribute("href", "#titulo-ocorrencia");
  const ainda = document.querySelector("p.ainda-neste-marco");
  let ultimo = ainda || proximo;
  if (ainda && ainda.textContent.includes("congelar a relação")) {
    ainda.replaceChildren(
      el("strong", {}, "Ainda neste marco: "),
      el("a", { href: "#recorte-ppp" }, "PPP — fixar os participantes (congelar a relação)"),
      ".",
    );
    ultimo = el(
      "p",
      { class: "dependente-da-d5" },
      "Fixe a PPP antes de obter a semente: uma lista fixada depois de conhecida a semente não pode ser sorteada.",
    );
    ainda.after(ultimo);
  }
  retornoAoCentro(ultimo, ctx.centro);
}
