/* O painel do assistente do edital, no protótipo da Fase C: abrir, fechar, o foco, o envio e a
   espera.

   **Um elemento, dois comportamentos** (avaliação de 14/10). No desktop o painel é lateral e não
   modal — `show()` —, para que a pessoa consulte a página enquanto conversa, alternando pelo
   teclado entre as duas. No celular ele cobre a tela e é modal — `showModal()` —: o resto da página
   fica inerte, Esc fecha, e o foco volta ao botão que o abriu.

   **O envio troca só a conversa.** A pergunta vai por `fetch`, e a resposta do servidor — a mesma
   página que o formulário sem script receberia — fornece a conversa nova. A página não recarrega:
   a rolagem dela fica onde estava, e o que a pessoa começou a digitar durante a espera não se perde.
   Sem script, os formulários enviam como sempre.

   **Um envio por vez.** Durante a espera o campo continua aberto para a próxima pergunta, mas
   enviar fica indisponível e diz que aguarda — e não só parece ativo.

   **A espera diz o que está acontecendo, e nada além.** "Consultando…" e, se demorar, "levando um
   pouco mais de tempo". Não há "conferindo": a conferência leva milissegundos, e o navegador não
   teria como saber quando ela começa. */
(function () {
  var painel = document.getElementById("pd-painel");
  var abrir = document.getElementById("pd-abrir");
  var fechar = document.getElementById("pd-fechar");
  if (!painel || !abrir || typeof painel.showModal !== "function") return;
  var celular = window.matchMedia("(max-width: 47.99rem)");
  var reabrindo = false;
  var enviando = false;

  function conversa() {
    return document.getElementById("pd-conversa");
  }

  function focar(alvo) {
    alvo = alvo || document.getElementById("pd-titulo");
    alvo.focus({ preventScroll: true });
    if (alvo.scrollIntoView) alvo.scrollIntoView({ block: "nearest" });
  }

  // O teclado virtual encolhe a área visível sem mudar a altura da janela em todo navegador: o
  // painel modal acompanha a área visível, para o campo de pergunta não ficar atrás do teclado.
  function ajustarAoTeclado() {
    var visivel = window.visualViewport;
    if (!visivel || !painel.matches(":modal")) {
      painel.style.height = "";
      painel.style.top = "";
      return;
    }
    painel.style.height = visivel.height + "px";
    painel.style.top = visivel.offsetTop + "px";
  }
  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", ajustarAoTeclado);
    window.visualViewport.addEventListener("scroll", ajustarAoTeclado);
  }

  function mostrar() {
    if (painel.open) {
      reabrindo = true;
      painel.close();
    }
    if (celular.matches) painel.showModal();
    else painel.show();
    abrir.setAttribute("aria-expanded", "true");
    ajustarAoTeclado();
  }

  painel.addEventListener("close", function () {
    if (reabrindo) {
      reabrindo = false;
      return;
    }
    abrir.setAttribute("aria-expanded", "false");
    abrir.focus();
  });

  abrir.addEventListener("click", function (evento) {
    evento.preventDefault();
    mostrar();
    focar();
  });

  fechar.addEventListener("click", function (evento) {
    evento.preventDefault();
    painel.close();
  });

  // O modal fecha com Esc por conta do navegador; o lateral, não.
  painel.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape" && !celular.matches) {
      evento.preventDefault();
      painel.close();
    }
  });

  // Aberto pelo servidor — pelo link sem script, ou depois de um envio sem script —, ele nasce não
  // modal; no celular, reabre como modal.
  if (painel.open) {
    if (celular.matches) mostrar();
    conversa().scrollTop = conversa().scrollHeight;
    var marcada = location.hash && painel.querySelector(location.hash);
    if (marcada) focar(marcada);
  }

  var botao = document.getElementById("pd-botao-enviar");

  function aguardar(sim) {
    enviando = sim;
    botao.setAttribute("aria-disabled", sim ? "true" : "false");
    botao.textContent = sim ? "Aguardando…" : "Enviar";
  }

  function mostrarEspera(texto) {
    var pendente = document.getElementById("pd-pendente");
    var espera = document.getElementById("pd-espera");
    document.getElementById("pd-pendente-pergunta").textContent = texto || "";
    espera.textContent = painel.dataset.espera;
    pendente.hidden = false;
    conversa()
      .querySelectorAll(".pd-sugestoes, .pd-opcoes")
      .forEach(function (bloco) {
        bloco.hidden = true;
      });
    pendente.scrollIntoView({ block: "end" });
    return window.setTimeout(function () {
      espera.textContent = painel.dataset.esperaLonga;
    }, Number(painel.dataset.segundos) * 1000);
  }

  // A conversa e a linha da versão vêm da página que o servidor devolveu: se o Edital mudou no meio
  // da conversa, as duas mudam juntas.
  function trocarConversa(html) {
    var nova = new DOMParser().parseFromString(html, "text/html");
    ["pd-conversa", "pd-versao"].forEach(function (id) {
      var veio = nova.getElementById(id);
      if (veio) document.getElementById(id).replaceWith(veio);
    });
    var titulos = conversa().querySelectorAll(".pd-troca .pd-pergunta");
    conversa().scrollTop = conversa().scrollHeight;
    if (titulos.length) focar(titulos[titulos.length - 1]);
  }

  // Delegado no painel: a conversa é trocada a cada resposta, e os formulários dela com ela.
  painel.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!formulario.hasAttribute("data-espera")) return;
    if (enviando) {
      evento.preventDefault();
      return;
    }
    var campo = formulario.querySelector("textarea");
    var texto = campo ? campo.value : evento.submitter && evento.submitter.textContent;
    if (formulario.method.toLowerCase() !== "post") {
      // A simulação navega: só mostra a espera até a página seguinte chegar.
      aguardar(true);
      mostrarEspera(texto);
      return;
    }
    evento.preventDefault();
    var dados = new FormData(formulario, evento.submitter);
    if (campo) campo.value = "";
    aguardar(true);
    var relogio = mostrarEspera(texto);
    fetch(formulario.action, { method: "POST", body: dados, credentials: "same-origin" })
      .then(function (resposta) {
        if (!resposta.ok) throw new Error(String(resposta.status));
        return resposta.text().then(function (html) {
          trocarConversa(html);
          history.replaceState(null, "", resposta.url);
        });
      })
      .catch(function () {
        document.getElementById("pd-espera").textContent =
          "Não foi possível enviar agora. Tente de novo.";
        if (campo && !campo.value) campo.value = texto;
      })
      .finally(function () {
        window.clearTimeout(relogio);
        aguardar(false);
      });
  });

  // No celular, o campo focado sobe acima do teclado.
  painel.addEventListener("focusin", function (evento) {
    if (evento.target.id === "pd-campo-pergunta" && celular.matches) {
      window.setTimeout(function () {
        evento.target.scrollIntoView({ block: "nearest" });
      }, 300);
    }
  });
})();
