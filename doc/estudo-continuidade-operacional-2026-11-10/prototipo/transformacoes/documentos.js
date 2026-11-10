// Documentos da convocação (jornada E). M-08: o contexto (Edital, Perfil, lista) no alto, e o
// próximo passo **desta pessoa** no bloco que segue a conferência; M-07: o da lista leva ao lugar; M-01:
// o retorno ao Centro.

const sub = exigir(main.querySelector("h1 + p, h1 + p.sub"), "linha da pessoa");
sub.after(
  el(
    "p",
    { class: "objetivo-da-tela" },
    "Edital SIM12/2026 · Professor de Informática · Ampla concorrência · Classificação final",
  ),
);

const proximo = exigir(document.querySelector("p.proximo-nesta-lista"), "bloco do próximo");
const pronta = main.textContent.includes("Pronta para decidir");
const desta = el(
  "p",
  { class: "proximo-nesta-lista" },
  el("strong", {}, "Próximo para esta pessoa: "),
  pronta
    ? el("a", { href: ctx.desfecho }, "registrar o desfecho da Cecília")
    : "aguardar o reenvio do documento pendente",
  pronta ? " — os dois documentos estão conformes." : ".",
);
proximo.before(desta);
proximo.replaceChildren(
  el("strong", {}, "Depois, nesta lista: "),
  el("a", { href: ctx.chamadas }, "conferir os documentos de 1 convocação"),
  " (Alice: 1 documento pendente, aguardando o reenvio).",
);
const ainda = document.querySelector("p.ainda-neste-marco");
retornoAoCentro(ainda || proximo, ctx.centro);

for (const a of main.querySelectorAll("a")) {
  if (a.textContent.trim() === "Voltar à convocação") a.setAttribute("href", ctx.chamadas);
}
