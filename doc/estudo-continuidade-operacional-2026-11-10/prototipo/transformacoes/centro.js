// Centro de Controle (136). M-02: cada providência leva ao lugar do ato na tela de destino, e não ao
// topo dela; M-11: a concordância das contagens. Nada mais muda no Centro: ele é o ponto de
// orientação, e o estudo não o redesenha.

for (const [trecho, destino] of Object.entries(ctx.ancoras)) {
  for (const a of main.querySelectorAll("a")) {
    if (a.textContent.trim().startsWith(trecho) || (trecho === "Abrir a tela" && a.textContent.trim() === trecho)) {
      a.setAttribute("href", destino);
    }
  }
}

// M-11: "1 aguardam documentos" — a frase concorda com o número.
for (const no of main.querySelectorAll("p, li, span, div")) {
  if (no.children.length === 0 && /\b1 aguardam\b/.test(no.textContent)) {
    no.textContent = no.textContent.replace(/\b1 aguardam\b/, "1 aguarda");
  }
}

// A frase da D-5, no lugar em que o Centro diz que a ordem entre as ações é livre. Ela não é: obter a
// semente antes de fixar a PPP condena o sorteio da PPP. É o achado F-1; aqui, só a variante (c) da
// D-5 ("só alertar"), marcada, para que a decisão se tome olhando a tela.
if (ctx.d5) {
  const livre = porTexto("p", "o GPS não escolhe a ordem entre elas");
  if (livre) {
    livre.after(
      el(
        "p",
        { class: "dependente-da-d5" },
        "Exceto no sorteio: obtida a semente, a PPP ainda não fixada não poderá ser sorteada. Fixe-a antes.",
      ),
    );
  }
}
