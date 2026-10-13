// Medição da primeira tela da vitrine e da página da seleção (auditoria de 12/10/2026).
//
// Como usar: abra qualquer página do portal servido localmente (mesma origem), cole este arquivo no
// console e chame `await medirTudo("<edital_id>")`. A página é buscada SEM a sessão do navegador
// (`credentials: "omit"`), renderizada num iframe `srcdoc` com a largura e a altura pedidas — a folha
// é inline no `base.html`, então as media queries valem para a largura do iframe — e medida por
// `getBoundingClientRect`. Nada é clicado nem gravado.
//
// "Primeira tela" é sempre o par largura × altura. Uma posição em px só diz alguma coisa junto da
// altura do viewport em que foi medida.

const TELAS = [
  [320, 568], [360, 800], [375, 667], [375, 812], [390, 844], [768, 1024], [1280, 800], [1440, 900],
];

async function renderizar(url, largura, altura, medir) {
  const html = await (await fetch(url, { cache: "reload", credentials: "omit" })).text();
  const quadro = document.createElement("iframe");
  quadro.style.cssText =
    `position:absolute;left:0;top:0;width:${largura}px;height:${altura}px;border:0;visibility:hidden`;
  document.body.appendChild(quadro);
  await new Promise((pronto) => {
    quadro.onload = pronto;
    quadro.srcdoc = html.replace("<head>", `<head><base href="${location.origin}">`);
  });
  await new Promise((pronto) => setTimeout(pronto, 150));
  const resultado = medir(quadro.contentDocument, altura);
  quadro.remove();
  return resultado;
}

const topo = (d, el) => (el ? Math.round(el.getBoundingClientRect().top + d.defaultView.scrollY) : null);
const fundo = (d, el) => (el ? topo(d, el) + Math.round(el.getBoundingClientRect().height) : null);

function vitrine(d, altura) {
  const cartao = d.querySelector(".selecao");
  // `.chamada` é o título do Edital; sem ele, o do Processo. Lista de seletores num `querySelector`
  // só devolveria o primeiro na ordem do documento — que é o do Processo.
  const titulo = cartao && (cartao.querySelector(".chamada") || cartao.querySelector("a.titulo"));
  const convite = cartao && cartao.querySelector(".acao-aparente");
  return {
    rolagemLateral: d.documentElement.scrollWidth - d.documentElement.clientWidth,
    formulario: [topo(d, d.querySelector(".consulta")), fundo(d, d.querySelector(".consulta"))],
    primeiroCartao: topo(d, cartao),
    fundoDoTituloDoEdital: fundo(d, titulo),
    tituloDoEditalVisivel: titulo ? fundo(d, titulo) <= altura : false,
    conviteVisivel: convite ? fundo(d, convite) <= altura : false,
    fundoDoConvite: fundo(d, convite),
  };
}

function selecao(d, altura) {
  const botao = d.querySelector("form.convite button.principal");
  return {
    rolagemLateral: d.documentElement.scrollWidth - d.documentElement.clientWidth,
    fimDoCabecalho: fundo(d, d.querySelector(".cabecalho-da-selecao")),
    tituloVagas: topo(d, d.querySelector("#vagas-titulo")),
    primeiroInscreverSe: topo(d, botao),
    inscreverSeVisivel: botao ? fundo(d, botao) <= altura : false,
  };
}

async function medirTudo(editalAberto) {
  const saida = { navegador: navigator.userAgent, vitrine: {}, selecao: {} };
  for (const [largura, altura] of TELAS) {
    const chave = `${largura}x${altura}`;
    saida.vitrine[chave] = await renderizar("/selecoes/", largura, altura, vitrine);
    saida.selecao[chave] = await renderizar(`/selecoes/${editalAberto}/`, largura, altura, selecao);
  }
  return saida;
}
