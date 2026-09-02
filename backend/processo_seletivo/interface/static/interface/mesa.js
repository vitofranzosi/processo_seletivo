/* Ler o documento e registrar a avaliação na mesma tela (FR-112).

   Antes, abrir um documento substituía a página: ler e avaliar eram duas telas que se revezavam, e
   quem já tinha digitado a nota corria o risco de perder o formulário no caminho. Depois passaram a
   ser duas abas, o que resolve a perda e mantém a troca de contexto — uma vez por documento, em
   toda inscrição de uma Mesa que tem centenas.

   **Só em tela larga.** Abaixo de 64rem não há onde pôr duas colunas, e o link continua abrindo em
   aba própria. Sem JavaScript, idem: o painel é montado aqui, e não no HTML, porque um painel que
   existisse na página e só funcionasse com script prometeria o que não cumpre.

   **A abertura continua sendo um ato.** Nada carrega sozinho ao entrar na inscrição: quem abre um
   documento clica nele, e é esse clique que a trilha registra — com o mesmo significado de antes
   (FR-027, FR-053). Embutir o arquivo automaticamente faria "abriu o documento" virar "abriu a
   inscrição", que é o mesmo evento dizendo outra coisa.

   O documento vai para a esquerda porque é a superfície maior e é o que se lê primeiro; o painel
   vem antes no DOM justamente para que a tabulação siga a mesma ordem. */
(function () {
  var LARGA = "(min-width: 64rem)";

  var painel = document.getElementById("painel-documento");
  var quadro = document.getElementById("painel-documento-quadro");
  var titulo = document.getElementById("painel-documento-titulo");
  var trabalho = document.querySelector(".mesa-trabalho");
  // O limite de largura é da página, e sai junto quando o documento entra.
  var pagina = document.querySelector(".pagina-da-inscricao");
  var links = [].slice.call(document.querySelectorAll("[data-documento]"));
  if (!painel || !quadro || !titulo || !trabalho || !links.length) return;

  var larga = window.matchMedia(LARGA);

  function fechar() {
    painel.hidden = true;
    trabalho.classList.remove("com-documento");
    if (pagina) pagina.classList.remove("com-documento");
    quadro.src = "about:blank";
    links.forEach(function (link) {
      link.removeAttribute("aria-current");
    });
  }

  function abrir(link) {
    quadro.src = link.getAttribute("href");
    titulo.textContent = link.getAttribute("data-documento");
    painel.hidden = false;
    trabalho.classList.add("com-documento");
    if (pagina) pagina.classList.add("com-documento");
    links.forEach(function (outro) {
      if (outro === link) {
        outro.setAttribute("aria-current", "true");
      } else {
        outro.removeAttribute("aria-current");
      }
    });
    // O foco vai para o título do painel, e não para dentro da moldura: de lá a pessoa tabula para
    // o documento se quiser rolá-lo, ou volta ao formulário — e quem usa leitor de tela ouve qual
    // documento abriu.
    titulo.focus();
  }

  links.forEach(function (link) {
    link.addEventListener("click", function (evento) {
      if (!larga.matches) return; // em tela estreita, o link faz o que sempre fez
      if (evento.metaKey || evento.ctrlKey || evento.shiftKey || evento.button !== 0) return;
      evento.preventDefault();
      abrir(link);
    });
  });

  // Quando a janela encolhe abaixo do limite, o painel não cabe mais: some, e os links voltam a
  // abrir em aba própria sem que nada precise ser recarregado.
  var aoMudar = function (evento) {
    if (!evento.matches && !painel.hidden) fechar();
  };
  if (larga.addEventListener) {
    larga.addEventListener("change", aoMudar);
  } else if (larga.addListener) {
    larga.addListener(aoMudar);
  }

  // O fechar mora na barra, ao lado do nome do documento — e não no fim do painel, a uma tela de
  // distância do que ele fecha.
  var fechador = document.createElement("button");
  fechador.type = "button";
  fechador.className = "acao";
  fechador.textContent = "Fechar";
  fechador.setAttribute("aria-label", "Fechar o documento e voltar ao formulário");
  fechador.addEventListener("click", function () {
    fechar();
    var primeiro = document.getElementById("pontuacao");
    if (primeiro) primeiro.focus();
  });
  titulo.parentNode.appendChild(fechador);
})();
