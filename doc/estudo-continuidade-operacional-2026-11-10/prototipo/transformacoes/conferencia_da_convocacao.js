// A conferência antes de convocar os titulares (M-04), montada sobre a moldura real da tela da
// convocação do C15 e com as classes das conferências que a gestão já tem (`marco_conferir.html`:
// `consequencias irreversivel`, `ajuda`, `confirmar`). Os dados são os da tela real: as pessoas, o
// fundamento derivado e o prazo vêm do HTML salvo, e não de texto escrito à mão.

// A lista é a da própria tela: o gesto dos titulares já a mostra como `ol.consequencias`.
const titulares = exigir(document.querySelector("section[aria-labelledby=titulares]"), "seção dos titulares");
const pessoas = [...titulares.querySelectorAll("ol.consequencias li")].map((li) => li.textContent.trim());
// Sem a nota "(derivado do Edital…)", que é ajuda da tela, e não parte do texto que a pessoa lê.
const dd = exigir(porTexto("dd", "Convocação para vaga inicial no Edital", titulares), "fundamento").cloneNode(true);
dd.querySelectorAll(".ajuda").forEach((n) => n.remove());
const fundamento = dd.textContent.trim();
const regularizar = porTexto("li", "próxima na ordem", porTexto("section", "regularizar") || main);
const faixa = main.querySelector(".prototipo-faixa");

main.replaceChildren(
  faixa,
  el("h1", {}, "Confira antes de convocar"),
  el("p", { class: "sub" }, "Convocar os titulares — Classificação final, Professor de Informática, Edital SIM15/2026 · Ampla concorrência"),
  el(
    "p",
    { class: "ajuda" },
    "Nasce ",
    el("strong", {}, "uma convocação imutável por pessoa"),
    ", com você como autor, e a comunicação sai no mesmo ato para cada uma. Corrigir uma convocação é sucedê-la com motivo, uma a uma.",
  ),
  el(
    "section",
    { class: "consequencias irreversivel", "aria-labelledby": "convocadas-titulo" },
    el("h2", { id: "convocadas-titulo" }, `Serão convocadas (${pessoas.length}), para vaga inicial`),
    el("ul", {}, ...pessoas.map((p) => el("li", {}, p))),
  ),
  el(
    "section",
    { class: "consequencias", "aria-labelledby": "texto-titulo" },
    el("h2", { id: "texto-titulo" }, "O que cada pessoa lerá"),
    el("p", { class: "texto-do-candidato" }, fundamento),
    el("p", { class: "ajuda" }, "Sem complemento. A mensagem diz que a convocação pede documentos e leva à área do candidato."),
  ),
  el(
    "section",
    { class: "consequencias", "aria-labelledby": "prazo-titulo" },
    el("h2", { id: "prazo-titulo" }, "Prazo"),
    el("p", {}, "Nenhum vencimento informado. Se o Edital publica prazo para atender, volte e informe-o: ele corre do envio desta comunicação."),
  ),
  ...(regularizar
    ? [
        el(
          "section",
          { class: "consequencias", "aria-labelledby": "fora-titulo" },
          el("h2", { id: "fora-titulo" }, "Fica de fora (1)"),
          el("ul", {}, el("li", {}, `${regularizar.textContent.split("·")[0].trim()} — Resultado indeferido: chamar para regularizar é outro gesto, na tela da convocação.`)),
        ),
      ]
    : []),
  el(
    "p",
    { class: "acoes" },
    el("a", { class: "botao", href: "#", "aria-disabled": "true" }, `Convocar ${pessoas.length} e enviar ${pessoas.length} comunicações`),
    " ",
    el("a", { class: "botao secundario", href: ctx.voltar }, "Cancelar e voltar"),
  ),
);
document.title = "Conferir — Convocar os titulares — Cefor/Ifes";
