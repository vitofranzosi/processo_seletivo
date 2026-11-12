/* O visualizador do documento: a Mesa do avaliador (012, FR-112) e a conferência dos documentos da
   convocação (157). Um script para as duas telas (D-001 da 157), lido por atributos `data-`.

   **Em tela larga, o documento ao lado do trabalho.** Abrir um documento substituía a página, e
   depois virou uma aba nova: ler e registrar eram dois lugares que se revezavam. Acima de 64rem o
   documento abre num painel ao lado do formulário, com o nome, a versão e — na conferência — a
   pessoa na barra (UX-640 da 157), para que o arquivo de uma pessoa não seja conferido no formulário
   de outra.

   **Abaixo dela, fora da página** (D-006 da 157). O link faz o que sempre fez; este script guarda o
   que estava sendo feito e, na volta, relê a marca de abertura, restaura o que foi digitado se o
   navegador recarregou a página, e oferece o retorno ao ponto de trabalho (FR-6528, FR-6529).

   **A abertura continua sendo um ato, e é o servidor que a registra.** Nada carrega sozinho: quem
   abre um documento clica nele (FR-6501). E nada aqui decide se houve abertura — a marca "aberto
   por você" é relida do servidor depois da entrega, porque é a trilha que o "conforme" lê (FR-3611
   da 115). A leitura que este script faz do navegador (`pdfViewerEnabled`) decide só o que se
   mostra no painel, nunca o que se registra (FR-6502, D-002 da 157).

   **Sem script, as telas funcionam como antes**: os links abrem em aba própria, e a conferência é
   registrada com a recarga da página. O painel existe no HTML escondido, e só este script o mostra. */
(function () {
  "use strict";

  var LARGA = "(min-width: 64rem)";
  var NAO_MOSTRA_PDF =
    "Este navegador não mostra o documento dentro da página. Abra em aba própria ou baixe o " +
    "arquivo; a abertura fica registrada do mesmo jeito.";
  var FALHA_DE_REDE =
    "A conferência não foi registrada. Não foi possível falar com o servidor; tente de novo. " +
    "O que você marcou continua aqui.";
  var RESTAURADO =
    "Restauramos o que você tinha marcado e digitado neste navegador. Nada foi registrado ainda.";
  // Campos que são do servidor, e não de quem preenche: copiá-los de volta reenviaria uma chave já
  // usada, ou uma versão que deixou de ser a vigente.
  var DO_SERVIDOR = ["csrfmiddlewaretoken", "chave", "apresentacao", "lista"];

  var raiz = document.querySelector("[data-visualizador]");
  if (!raiz) return;
  var painel = raiz.querySelector("[data-painel]");
  var quadro = raiz.querySelector("[data-quadro]");
  var titulo = raiz.querySelector("[data-titulo-do-painel]");
  if (!painel || !quadro || !titulo) return;
  var identificacao = raiz.querySelector("[data-identificacao]");
  var texto = raiz.querySelector("[data-texto-do-painel]");
  var pagina = document.querySelector("[data-pagina-do-visualizador]");
  var anuncio = document.querySelector("[data-anuncio]");
  var larga = window.matchMedia ? window.matchMedia(LARGA) : { matches: false };
  var guarda = "ps:visualizador:" + (window.location ? window.location.pathname : "");

  var atual = null; // o link cujo documento está no painel
  var aReler = null; // o link aberto fora da página, a reler na volta

  /* --- O armazenamento da aba (R-010 da 157) -----------------------------------------------------

     `sessionStorage`, e não `localStorage`: o que se guarda é o motivo digitado — texto que a pessoa
     convocada vai ler — ou a nota e o parecer de uma avaliação, e a máquina de um órgão público é
     compartilhada. A aba fechada leva tudo junto; o registro aceito também apaga. Janela anônima ou
     armazenamento bloqueado: a tela funciona igual, só não restaura. */
  function armazem() {
    try {
      return window.sessionStorage || null;
    } catch (erro) {
      return null;
    }
  }

  function lerGuardado() {
    var a = armazem();
    if (!a) return null;
    try {
      return JSON.parse(a.getItem(guarda) || "null");
    } catch (erro) {
      return null;
    }
  }

  function gravarGuardado(valor) {
    var a = armazem();
    if (!a) return;
    try {
      if (valor) a.setItem(guarda, JSON.stringify(valor));
      else a.removeItem(guarda);
    } catch (erro) {
      /* cota estourada: segue sem guardar */
    }
  }

  /* --- Pequenos auxiliares ----------------------------------------------------------------------- */
  function rotuloDe(link) {
    return link.getAttribute("data-rotulo") || link.getAttribute("data-documento") || "Documento";
  }

  function noPainel(url) {
    return url + (url.indexOf("?") >= 0 ? "&" : "?") + "painel=1";
  }

  function mostraPdf() {
    return !(window.navigator && window.navigator.pdfViewerEnabled === false);
  }

  function escrever(frase) {
    if (texto) texto.textContent = frase || "";
  }

  function anunciar(frase) {
    if (!anuncio || !frase) return;
    // Esvaziar antes é o que faz o leitor de tela anunciar a mesma frase duas vezes seguidas.
    anuncio.textContent = "";
    window.setTimeout(function () {
      anuncio.textContent = frase;
    }, 50);
  }

  function links() {
    return [].slice.call(document.querySelectorAll("[data-abrir-documento]"));
  }

  function formulariosGuardados(alvoId) {
    var seletor = raiz.getAttribute("data-guardar");
    if (seletor) return [].slice.call(document.querySelectorAll(seletor));
    var alvo = alvoId ? document.getElementById(alvoId) : null;
    return alvo ? [].slice.call(alvo.querySelectorAll("form")) : [];
  }

  function camposDe(formularios) {
    var campos = [];
    formularios.forEach(function (formulario) {
      [].slice.call(formulario.querySelectorAll("input, textarea, select")).forEach(function (c) {
        if (!c.name || DO_SERVIDOR.indexOf(c.name) >= 0 || c.type === "hidden") return;
        if (c.type === "radio" || c.type === "checkbox") {
          if (c.checked) campos.push({ nome: c.name, valor: c.value, marcado: true });
        } else if (c.value) {
          campos.push({ nome: c.name, valor: c.value });
        }
      });
    });
    return campos;
  }

  function preencher(formularios, campos) {
    campos.forEach(function (campo) {
      formularios.forEach(function (formulario) {
        [].slice.call(formulario.querySelectorAll("input, textarea, select")).forEach(function (c) {
          if (c.name !== campo.nome) return;
          if (c.type === "radio" || c.type === "checkbox") {
            if (c.value === campo.valor) c.checked = true;
          } else {
            c.value = campo.valor;
          }
        });
      });
    });
  }

  function primeiroCampo(alvoId) {
    var seletor = raiz.getAttribute("data-foco-ao-fechar");
    if (seletor) {
      var achado = document.querySelector(seletor);
      if (achado) return achado;
    }
    var alvo = alvoId ? document.getElementById(alvoId) : null;
    return alvo
      ? alvo.querySelector("form input:not([type=hidden]), form textarea, form select")
      : null;
  }

  /* --- A barra: aba própria, baixar e fechar ----------------------------------------------------- */
  var barra = titulo.parentNode;

  function acrescentar(no) {
    if (identificacao && identificacao.parentNode === barra) barra.insertBefore(no, identificacao);
    else barra.appendChild(no);
    return no;
  }

  // **A barra inteira do visualizador, a um clique** (FR-112 da 012): o visualizador de PDF do
  // navegador encolhe a própria barra dentro da moldura, e girar ou ampliar se faz melhor em aba
  // própria. É o mesmo endereço: uma abertura a mais na trilha, que é o que ela é.
  var avulso = acrescentar(document.createElement("a"));
  avulso.className = "acao";
  avulso.textContent = "Abrir em aba própria";
  avulso.setAttribute("target", "_blank");
  avulso.setAttribute("rel", "noopener");

  // O download, ação secundária e individual (FR-3606 da 115; FR-6507 e FR-6546 da 157).
  var baixar = acrescentar(document.createElement("a"));
  baixar.className = "acao secundaria";
  baixar.textContent = "Baixar";

  var fechador = acrescentar(document.createElement("button"));
  fechador.type = "button";
  fechador.className = "acao";
  fechador.textContent = "Fechar";
  fechador.setAttribute("aria-label", "Fechar o documento e voltar ao formulário");

  /* --- Abrir e fechar no painel ------------------------------------------------------------------ */
  function abrir(link) {
    var rotulo = rotuloDe(link);
    var url = link.getAttribute("href");
    atual = link;
    painel.hidden = false;
    raiz.classList.add("com-documento");
    if (pagina) pagina.classList.add("com-documento");
    titulo.textContent = rotulo;
    avulso.hidden = false;
    avulso.setAttribute("href", url);
    // O nome acessível começa pelo texto visível: quem comanda por voz diz o que lê.
    avulso.setAttribute("aria-label", "Abrir em aba própria: " + rotulo);
    var paraBaixar = link.getAttribute("data-baixar");
    baixar.hidden = !paraBaixar;
    if (paraBaixar) {
      baixar.setAttribute("href", paraBaixar);
      baixar.setAttribute("aria-label", "Baixar: " + rotulo);
    }
    links().forEach(function (outro) {
      if (outro === link) outro.setAttribute("aria-current", "true");
      else outro.removeAttribute("aria-current");
    });
    var pessoa = identificacao ? identificacao.textContent.trim() : "";
    quadro.setAttribute("title", rotulo + (pessoa ? " — " + pessoa : ""));
    if (mostraPdf()) {
      var tamanho = link.getAttribute("data-tamanho");
      var carregando = "Carregando o documento" + (tamanho ? " (" + tamanho + ")" : "") + "…";
      quadro.hidden = false;
      escrever(carregando);
      anunciar(carregando);
      quadro.src = noPainel(url);
    } else {
      // A alternativa sem prévia (FR-6502, UX-643): sem moldura, sem pedido ao servidor. A aba
      // própria e o download, na barra, são o caminho — e a volta relê a marca (FR-6511).
      quadro.hidden = true;
      quadro.src = "about:blank";
      escrever(NAO_MOSTRA_PDF);
      anunciar(NAO_MOSTRA_PDF);
    }
    // O foco vai ao título do painel, e não para dentro da moldura: de lá a pessoa tabula para o
    // documento ou volta ao formulário — e quem usa leitor de tela ouve qual documento abriu.
    titulo.focus();
    var alvo = document.getElementById(link.getAttribute("data-alvo") || "");
    if (alvo && alvo.scrollIntoView) alvo.scrollIntoView({ block: "nearest" });
  }

  function fechar(comFoco) {
    var alvoId = atual ? atual.getAttribute("data-alvo") : "";
    painel.hidden = true;
    raiz.classList.remove("com-documento");
    if (pagina) pagina.classList.remove("com-documento");
    quadro.src = "about:blank";
    escrever("");
    avulso.removeAttribute("href");
    baixar.removeAttribute("href");
    links().forEach(function (link) {
      link.removeAttribute("aria-current");
    });
    atual = null;
    if (comFoco) {
      var campo = primeiroCampo(alvoId);
      if (campo) campo.focus();
    }
  }

  fechador.addEventListener("click", function () {
    fechar(true);
  });

  // A recusa da entrega volta como um documento pequeno, legível dentro da moldura (FR-6510,
  // FR-6545). A raiz dele se declara; a frase sobe para o texto do painel, e a aba própria e o
  // download somem — para arquivo recusado não há outro caminho.
  function fraseDaRecusa() {
    try {
      var doc = quadro.contentDocument;
      if (doc && doc.documentElement && doc.documentElement.hasAttribute("data-recusa-no-painel")) {
        var frase = doc.querySelector("[data-frase-da-recusa]");
        return frase ? frase.textContent.trim() : "O documento não pôde ser entregue.";
      }
    } catch (erro) {
      /* documento de outra origem: não é a nossa recusa */
    }
    return "";
  }

  quadro.addEventListener("load", function () {
    if (!atual || !quadro.src || quadro.src.indexOf("about:blank") === 0) return;
    var recusa = fraseDaRecusa();
    if (recusa) {
      quadro.hidden = true;
      escrever(recusa);
      avulso.hidden = true;
      baixar.hidden = true;
      anunciar(recusa);
      return;
    }
    escrever("");
    reler(atual, 0);
  });

  /* --- A releitura da marca (FR-6503, R-005) -----------------------------------------------------

     A abertura é registrada pelo servidor ao fim da entrega (FR-6544). O cartão relido traz a marca
     da trilha; se ele chega antes do registro, uma segunda tentativa, um segundo depois, e depois
     nada — a próxima releitura corrige. */
  function aberto(container, href) {
    return [].slice
      .call(container.querySelectorAll("[data-abrir-documento]"))
      .some(function (link) {
        return link.getAttribute("href") === href && link.hasAttribute("data-aberto");
      });
  }

  function reler(link, tentativa, aoTerminar) {
    var url = link.getAttribute("data-cartao");
    var alvoId = link.getAttribute("data-alvo");
    var href = link.getAttribute("href");
    var rotulo = rotuloDe(link);
    if (!url || !alvoId || !window.fetch) {
      if (aoTerminar) aoTerminar();
      return;
    }
    window
      .fetch(url, { credentials: "same-origin" })
      .then(function (resposta) {
        return resposta.ok ? resposta.text() : "";
      })
      .then(function (html) {
        trocar(alvoId, html, function (novo) {
          if (novo && aberto(novo, href)) anunciar("Aberto por você: " + rotulo + ".");
          else if (tentativa < 1) {
            window.setTimeout(function () {
              reler(link, tentativa + 1);
            }, 1000);
          }
          if (aoTerminar) aoTerminar();
        });
      })
      .catch(function () {
        if (aoTerminar) aoTerminar();
      });
  }

  // A troca preserva o que está digitado, e espera o foco sair do formulário: trocar o cartão
  // debaixo do cursor apagaria a palavra que a pessoa está escrevendo.
  function trocar(alvoId, html, depois) {
    var antigo = document.getElementById(alvoId);
    if (!antigo || !html) {
      if (depois) depois(null);
      return;
    }
    var ativo = document.activeElement;
    if (ativo && antigo.contains(ativo) && /^(INPUT|TEXTAREA|SELECT)$/i.test(ativo.tagName || "")) {
      var esperar = function () {
        window.setTimeout(function () {
          if (antigo.contains(document.activeElement)) return;
          antigo.removeEventListener("focusout", esperar);
          trocar(alvoId, html, depois);
        }, 0);
      };
      antigo.addEventListener("focusout", esperar);
      return;
    }
    var molde = document.createElement("template");
    molde.innerHTML = html.trim();
    var novo = molde.content ? molde.content.firstElementChild : null;
    if (!novo || novo.id !== alvoId) {
      if (depois) depois(null);
      return;
    }
    preencher(formulariosNo(novo), camposDe(formulariosNo(antigo)));
    var abertos = [].slice.call(antigo.querySelectorAll("details")).map(function (d) {
      return d.open;
    });
    [].slice.call(novo.querySelectorAll("details")).forEach(function (d, i) {
      if (abertos[i]) d.open = true;
    });
    antigo.replaceWith(novo);
    if (window.htmx && window.htmx.process) window.htmx.process(novo);
    if (atual && atual.getAttribute("data-alvo") === alvoId) {
      // O link do painel foi substituído: o novo, do mesmo endereço, passa a ser o atual.
      var mesmo = [].slice.call(novo.querySelectorAll("[data-abrir-documento]")).filter(function (l) {
        return l.getAttribute("href") === atual.getAttribute("href");
      })[0];
      if (mesmo) {
        atual = mesmo;
        mesmo.setAttribute("aria-current", "true");
      }
    }
    if (depois) depois(novo);
  }

  function formulariosNo(elemento) {
    return elemento.tagName === "FORM" ? [elemento] : [].slice.call(elemento.querySelectorAll("form"));
  }

  /* --- Fora da página, e a volta (FR-6527 a FR-6530, FR-6547) ------------------------------------ */
  function saiuPara(link) {
    aReler = link;
    var alvoId = link.getAttribute("data-alvo") || "";
    gravarGuardado({
      alvo: alvoId,
      href: link.getAttribute("href"),
      rotulo: rotuloDe(link),
      campos: camposDe(formulariosGuardados(alvoId)),
    });
  }

  function mostrarRetorno(alvoId, rotulo, restaurado, href) {
    var alvo = document.getElementById(alvoId);
    var lugar = (alvo && alvo.querySelector("[data-retorno]")) || document.querySelector("[data-retorno]");
    if (!lugar) return;
    var prefixo = raiz.getAttribute("data-prefixo-do-retorno") || "Voltar à conferência do ";
    var retorno = document.createElement("a");
    retorno.className = "acao";
    retorno.setAttribute("href", "#" + alvoId);
    retorno.textContent = prefixo + rotulo.split(" — ")[0];
    retorno.addEventListener("click", function (evento) {
      evento.preventDefault();
      // Na Mesa, o retorno é à linha do documento (FR-6547); na conferência, ao formulário dele.
      var destino = null;
      if (raiz.hasAttribute("data-retorno-ao-documento") && href) {
        destino = [].slice.call(document.querySelectorAll("[data-abrir-documento]")).filter(
          function (l) {
            return l.getAttribute("href") === href;
          }
        )[0];
      }
      destino = destino || primeiroCampo(alvoId);
      if (destino) destino.focus();
    });
    var partes = [retorno];
    if (restaurado) {
      var frase = document.createElement("span");
      frase.className = "preenchimento-restaurado";
      frase.textContent = " " + RESTAURADO;
      partes.push(frase);
    }
    lugar.replaceChildren.apply(lugar, partes);
    retorno.focus();
  }

  function voltou() {
    var link = aReler;
    if (!link) return;
    aReler = null;
    var alvoId = link.getAttribute("data-alvo") || "";
    var rotulo = rotuloDe(link);
    reler(link, 0, function () {
      // Sem painel aberto, o retorno: a pessoa estava fora da página (FR-6528).
      if (!atual) mostrarRetorno(alvoId, rotulo, false, link.getAttribute("href"));
    });
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") voltou();
  });
  window.addEventListener("pageshow", function (evento) {
    if (evento.persisted) voltou();
  });

  // O que se digita depois de sair continua guardado, enquanto houver o que guardar.
  document.addEventListener("input", function () {
    var guardado = lerGuardado();
    if (!guardado) return;
    guardado.campos = camposDe(formulariosGuardados(guardado.alvo));
    gravarGuardado(guardado);
  });

  // A página recarregada pelo navegador na volta: o formulário vazio recebe o que estava guardado,
  // com a frase que diz que nada foi registrado (FR-6529, UX-653). Nada é enviado.
  (function restaurar() {
    var guardado = lerGuardado();
    if (!guardado || !guardado.campos || !guardado.campos.length) return;
    var formularios = formulariosGuardados(guardado.alvo);
    if (!formularios.length || camposDe(formularios).length) return;
    preencher(formularios, guardado.campos);
    mostrarRetorno(guardado.alvo, guardado.rotulo || "", true, guardado.href);
  })();

  /* --- Os cliques ------------------------------------------------------------------------------ */
  document.addEventListener("click", function (evento) {
    var alvo = evento.target;
    if (alvo === avulso || alvo === baixar) {
      // A aba própria e o download também são abertura: a volta relê a marca (FR-6511).
      if (atual) aReler = atual;
      return;
    }
    var link = alvo && alvo.closest ? alvo.closest("[data-abrir-documento]") : null;
    if (!link) return;
    var comum = !(evento.metaKey || evento.ctrlKey || evento.shiftKey || evento.button);
    if (comum && larga.matches) {
      evento.preventDefault();
      abrir(link);
      return;
    }
    saiuPara(link);
  });

  // A janela que encolhe abaixo da tela larga fecha o painel; o formulário fica como está, e o
  // arquivo não é pedido de novo (FR-6530).
  var aoMudar = function (evento) {
    if (!evento.matches && !painel.hidden) fechar(false);
  };
  if (larga.addEventListener) larga.addEventListener("change", aoMudar);
  else if (larga.addListener) larga.addListener(aoMudar);

  /* --- O registro sem recarga (FR-6514 a FR-6518) ------------------------------------------------ */
  document.addEventListener("htmx:afterSwap", function (evento) {
    var id = evento.detail && evento.detail.target ? evento.detail.target.id : "";
    var novo = id ? document.getElementById(id) : null;
    // Só o cartão interessa aqui; a situação e as pessoas do recorte chegam pela mesma resposta.
    if (!novo || !novo.querySelector("form, [data-confirmacao]")) return;
    // Uma confirmação por vez: a do cartão anterior fica velha quando outro é registrado.
    if (novo.querySelector("[data-confirmacao]")) {
      [].slice.call(document.querySelectorAll("[data-confirmacao]")).forEach(function (c) {
        if (!novo.contains(c)) c.remove();
      });
    }
    var recusa = novo.querySelector(".erro[tabindex]");
    if (recusa) {
      recusa.focus();
      return;
    }
    var confirmacao = novo.querySelector("[data-confirmacao]");
    if (confirmacao) {
      var guardado = lerGuardado();
      if (guardado && guardado.alvo === id) gravarGuardado(null);
      if (atual && atual.getAttribute("data-alvo") === id) {
        var mesmo = [].slice.call(novo.querySelectorAll("[data-abrir-documento]")).filter(
          function (l) {
            return l.getAttribute("href") === atual.getAttribute("href");
          }
        )[0];
        if (mesmo) {
          atual = mesmo;
          mesmo.setAttribute("aria-current", "true");
        }
      }
    }
  });

  function falhou(evento) {
    var formulario = evento.detail && evento.detail.elt;
    var mensagem = formulario && formulario.querySelector ? formulario.querySelector("[data-mensagem]") : null;
    if (mensagem) mensagem.textContent = FALHA_DE_REDE;
  }
  document.addEventListener("htmx:sendError", falhou);
  document.addEventListener("htmx:responseError", falhou);
})();
