/* Navegação por páginas, busca global, abas, filtros e tema.
   Sem dependência externa e sem servidor: o arquivo abre por file://. Por isso a documentação
   é um arquivo só — buscar em várias páginas exigiria fetch, que o file:// recusa —, e cada
   "página" é um <article class="pagina"> que o roteador mostra sozinho. Sem JavaScript, tudo
   aparece em sequência e o índice continua funcionando como âncoras: nada se perde. */
(function () {
  "use strict";

  var raiz = document.documentElement;
  var paginas = Array.prototype.slice.call(document.querySelectorAll("article.pagina"));
  var lateral = document.querySelector(".lateral");
  var abre = document.querySelector(".abre-menu");
  var campo = document.getElementById("busca");
  var caixa = document.querySelector(".busca-resultados");
  var linksPagina = Array.prototype.slice.call(document.querySelectorAll("nav.sumario a[href^='#pg-']"));
  var trilha = document.querySelector(".trilha-nav");
  var topo = document.querySelector(".ao-topo");

  var dobra = function (s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  };

  var guardar = function (chave, valor) {
    try {
      if (valor === null) localStorage.removeItem(chave);
      else localStorage.setItem(chave, valor);
    } catch (e) {
      /* navegação privada ou armazenamento bloqueado: o tema só não persiste */
    }
  };
  var ler = function (chave) {
    try {
      return localStorage.getItem(chave);
    } catch (e) {
      return null;
    }
  };

  /* ---------- tema ---------- */
  var botaoTema = document.querySelector(".tema");
  var rotulos = { auto: "Tema: automático", claro: "Tema: claro", escuro: "Tema: escuro" };
  var aplicarTema = function (t) {
    if (t === "claro" || t === "escuro") raiz.setAttribute("data-tema", t);
    else raiz.removeAttribute("data-tema");
    if (botaoTema) botaoTema.textContent = rotulos[t] || rotulos.auto;
  };
  var temaAtual = ler("visao-tema") || "auto";
  aplicarTema(temaAtual);
  if (botaoTema) {
    botaoTema.addEventListener("click", function () {
      temaAtual = temaAtual === "auto" ? "claro" : temaAtual === "claro" ? "escuro" : "auto";
      aplicarTema(temaAtual);
      guardar("visao-tema", temaAtual === "auto" ? null : temaAtual);
    });
  }

  /* ---------- menu no celular ---------- */
  if (abre) {
    abre.addEventListener("click", function () {
      lateral.classList.toggle("aberta");
    });
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("nav.sumario a");
    if (a) lateral.classList.remove("aberta");
  });

  if (!paginas.length) return;

  /* ---------- roteador ---------- */
  var ordem = linksPagina
    .map(function (a) {
      return document.getElementById(a.getAttribute("href").slice(1));
    })
    .filter(Boolean);

  var camadaDe = { entender: "Entender", operar: "Aprender a operar", consultar: "Consultar", produto: "Estado do produto" };

  var tituloDe = function (pg) {
    return pg.getAttribute("data-titulo") || (pg.querySelector("h1") || {}).textContent || "";
  };

  var montarNestaPagina = function (pg) {
    var alvo = pg.querySelector(".nesta-pagina");
    var secoes = Array.prototype.slice.call(pg.querySelectorAll("section[id] > h2"));
    if (alvo && !alvo.childElementCount && secoes.length > 1) {
      var rotulo = document.createElement("span");
      rotulo.textContent = "Nesta página";
      alvo.appendChild(rotulo);
      secoes.forEach(function (h) {
        var a = document.createElement("a");
        a.href = "#" + h.parentElement.id;
        a.textContent = h.firstChild ? h.firstChild.textContent.trim() : h.textContent;
        alvo.appendChild(a);
      });
    }
    /* o mesmo índice, na lateral, debaixo da página ativa */
    document.querySelectorAll("nav.sumario ol.sub").forEach(function (o) {
      o.remove();
    });
    var link = linksPagina.find(function (a) {
      return a.getAttribute("href") === "#" + pg.id;
    });
    if (link && secoes.length > 1) {
      var ol = document.createElement("ol");
      ol.className = "sub";
      secoes.forEach(function (h) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#" + h.parentElement.id;
        a.textContent = h.firstChild ? h.firstChild.textContent.trim() : h.textContent;
        li.appendChild(a);
        ol.appendChild(li);
      });
      link.parentElement.appendChild(ol);
    }
  };

  var montarRodape = function (pg) {
    var nav = pg.querySelector(".pag-nav");
    if (!nav || nav.childElementCount) return;
    var i = ordem.indexOf(pg);
    var ant = ordem[i - 1];
    var prox = ordem[i + 1];
    if (ant) {
      var a = document.createElement("a");
      a.href = "#" + ant.id;
      a.className = "anterior";
      a.innerHTML = "<span>← Anterior</span>" + tituloDe(ant);
      nav.appendChild(a);
    } else nav.appendChild(document.createElement("span"));
    if (prox) {
      var b = document.createElement("a");
      b.href = "#" + prox.id;
      b.className = "proxima";
      b.innerHTML = "<span>Próxima →</span>" + tituloDe(prox);
      nav.appendChild(b);
    }
  };

  var mostrar = function (rolar) {
    var id = decodeURIComponent((location.hash || "").slice(1)) || ordem[0].id;
    var alvo = document.getElementById(id) || ordem[0];
    var pg = alvo.closest("article.pagina") || ordem[0];
    /* trocar de página salta; rolar dentro da mesma página pode ser suave. Animar a troca
       percorreria milhares de pixels de uma página que acabou de aparecer */
    var trocou = !pg.classList.contains("ativa");
    var modo = trocou ? "instant" : "smooth";
    paginas.forEach(function (p) {
      p.classList.toggle("ativa", p === pg);
    });
    linksPagina.forEach(function (a) {
      a.classList.toggle("ativo", a.getAttribute("href") === "#" + pg.id);
    });
    montarNestaPagina(pg);
    montarRodape(pg);
    if (trilha) {
      var camada = camadaDe[pg.getAttribute("data-camada")] || "";
      trilha.innerHTML =
        '<a href="#' + ordem[0].id + '">Início</a>' +
        (camada && pg !== ordem[0] ? "<span>›</span>" + camada : "") +
        (pg !== ordem[0] ? "<span>›</span><strong>" + tituloDe(pg) + "</strong>" : "");
    }
    document.title = (pg === ordem[0] ? "" : tituloDe(pg) + " · ") + "Visão do Sistema — Processos Seletivos e Editais";
    /* âncora dentro de <details> fechado: abre, senão a rolagem cai em lugar nenhum */
    var d = alvo.closest("details");
    while (d) {
      d.open = true;
      d = d.parentElement && d.parentElement.closest("details");
    }
    if (rolar !== false) {
      if (alvo === pg) window.scrollTo({ top: 0, behavior: modo });
      else
        requestAnimationFrame(function () {
          alvo.scrollIntoView({ behavior: modo });
        });
    }
  };
  window.addEventListener("hashchange", function () {
    mostrar(true);
  });
  mostrar(true);

  /* ---------- busca global ---------- */
  /* textContent cola o fim de uma célula no começo da seguinte ("reservaQuadro"): junta os nós
     de texto com espaço, e o trecho mostrado na busca continua legível */
  var textoDe = function (el) {
    var partes = [];
    var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) partes.push(w.currentNode.nodeValue);
    return partes.join(" ").replace(/\s+/g, " ");
  };
  var indice = [];
  paginas.forEach(function (pg) {
    var nomePg = tituloDe(pg);
    var secoes = pg.querySelectorAll("section[id]");
    if (!secoes.length) {
      indice.push({ id: pg.id, titulo: nomePg, pagina: "", texto: dobra(textoDe(pg)), cru: textoDe(pg) });
    }
    secoes.forEach(function (s) {
      var h = s.querySelector("h2") || s.querySelector("h1") || s.querySelector("h3");
      indice.push({
        id: s.id,
        titulo: h ? h.firstChild.textContent.trim() : s.id,
        pagina: nomePg,
        texto: dobra(textoDe(s)),
        cru: textoDe(s),
      });
    });
    /* cada termo do glossário também é um destino */
    pg.querySelectorAll("dl.glossario > dt[id]").forEach(function (dt) {
      var dd = dt.nextElementSibling;
      indice.push({
        id: dt.id,
        titulo: dt.textContent.trim(),
        pagina: "Glossário",
        texto: dobra(dt.textContent + " " + (dd ? textoDe(dd) : "")),
        cru: dd ? textoDe(dd) : "",
        termo: true,
      });
    });
  });

  var trecho = function (cru, q) {
    var limpo = cru.replace(/\s+/g, " ").trim();
    var i = dobra(limpo).indexOf(q);
    if (i < 0) return limpo.slice(0, 110) + "…";
    var ini = Math.max(0, i - 45);
    return (ini ? "…" : "") + limpo.slice(ini, i + q.length + 70) + "…";
  };

  var escapa = function (s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };

  var buscar = function () {
    var q = dobra(campo.value.trim());
    if (!q || q.length < 2) {
      caixa.hidden = true;
      caixa.innerHTML = "";
      return;
    }
    var termos = q.split(/\s+/);
    var achados = indice
      .map(function (r) {
        if (!termos.every(function (t) { return r.texto.indexOf(t) !== -1; })) return null;
        var t = dobra(r.titulo);
        var peso = (t.indexOf(q) !== -1 ? 10 : 0) + (r.termo && t.indexOf(q) === 0 ? 8 : 0);
        return { r: r, peso: peso };
      })
      .filter(Boolean)
      .sort(function (a, b) {
        return b.peso - a.peso;
      })
      .slice(0, 14);
    if (!achados.length) {
      caixa.innerHTML = '<p class="busca-vazia">Nada encontrado. Tente um termo do domínio: “marco”, “reserva”, “sorteio”.</p>';
    } else {
      caixa.innerHTML = achados
        .map(function (x) {
          return (
            '<a href="#' + x.r.id + '"><strong>' + escapa(x.r.titulo) + "</strong>" +
            (x.r.pagina ? "<em>" + escapa(x.r.pagina) + "</em>" : "") +
            "<span>" + escapa(trecho(x.r.cru, termos[0])) + "</span></a>"
          );
        })
        .join("");
    }
    caixa.hidden = false;
  };

  if (campo && caixa) {
    campo.addEventListener("input", buscar);
    campo.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        campo.value = "";
        buscar();
      }
      if (e.key === "Enter") {
        var primeiro = caixa.querySelector("a");
        if (primeiro) primeiro.click();
      }
    });
    caixa.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        caixa.hidden = true;
        campo.value = "";
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== campo && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
        e.preventDefault();
        campo.focus();
      }
    });
  }

  /* ---------- abas ---------- */
  document.querySelectorAll(".abas").forEach(function (grupo, n) {
    var paineis = Array.prototype.slice.call(grupo.querySelectorAll(":scope > .aba"));
    if (!paineis.length) return;
    var lista = document.createElement("div");
    lista.className = "abas-lista";
    lista.setAttribute("role", "tablist");
    var ativar = function (i) {
      paineis.forEach(function (p, j) {
        p.hidden = i !== j;
        lista.children[j].setAttribute("aria-selected", i === j ? "true" : "false");
        lista.children[j].tabIndex = i === j ? 0 : -1;
      });
    };
    paineis.forEach(function (p, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("role", "tab");
      p.setAttribute("role", "tabpanel");
      p.id = p.id || "aba-" + n + "-" + i;
      b.setAttribute("aria-controls", p.id);
      b.innerHTML = p.getAttribute("data-rotulo") || "Aba " + (i + 1);
      b.addEventListener("click", function () {
        ativar(i);
      });
      b.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
          var k = (i + (e.key === "ArrowRight" ? 1 : paineis.length - 1)) % paineis.length;
          ativar(k);
          lista.children[k].focus();
        }
      });
      lista.appendChild(b);
    });
    grupo.insertBefore(lista, grupo.firstChild);
    ativar(0);
  });

  /* ---------- filtros de tabela e de glossário ---------- */
  document.querySelectorAll("input[data-filtra]").forEach(function (entrada) {
    var alvo = document.querySelector(entrada.getAttribute("data-filtra"));
    if (!alvo) return;
    var botoes = Array.prototype.slice.call(
      document.querySelectorAll("[data-filtro-de='" + entrada.getAttribute("data-filtra") + "'] button")
    );
    var marca = "";
    var aplicar = function () {
      var q = dobra(entrada.value.trim());
      var linhas = alvo.matches("dl") ? alvo.querySelectorAll(":scope > dt") : alvo.querySelectorAll("tbody tr:not(.grupo-linha)");
      var visiveis = 0;
      linhas.forEach(function (l) {
        var bloco = [l];
        if (l.tagName === "DT") {
          var n = l.nextElementSibling;
          while (n && n.tagName === "DD") {
            bloco.push(n);
            n = n.nextElementSibling;
          }
        }
        var texto = dobra(bloco.map(function (b) { return b.textContent; }).join(" "));
        var ok = (!q || texto.indexOf(q) !== -1) && (!marca || (l.getAttribute("data-marca") || "").indexOf(marca) !== -1);
        bloco.forEach(function (b) {
          b.classList.toggle("oculto", !ok);
        });
        if (ok) visiveis++;
      });
      /* os títulos de grupo do catálogo somem quando o grupo inteiro some */
      alvo.querySelectorAll("tbody tr.grupo-linha").forEach(function (g) {
        var n = g.nextElementSibling;
        var algum = false;
        while (n && !n.classList.contains("grupo-linha")) {
          if (!n.classList.contains("oculto")) algum = true;
          n = n.nextElementSibling;
        }
        g.classList.toggle("oculto", !algum);
      });
      var contador = document.querySelector("[data-contador='" + entrada.getAttribute("data-filtra") + "']");
      if (contador) contador.textContent = visiveis + (visiveis === 1 ? " item" : " itens");
    };
    entrada.addEventListener("input", aplicar);
    botoes.forEach(function (b) {
      b.addEventListener("click", function () {
        marca = b.getAttribute("data-marca") || "";
        botoes.forEach(function (x) {
          x.setAttribute("aria-pressed", x === b ? "true" : "false");
        });
        aplicar();
      });
    });
    aplicar();
  });

  /* ---------- voltar ao topo ---------- */
  if (topo) {
    topo.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    window.addEventListener(
      "scroll",
      function () {
        topo.classList.toggle("visivel", window.scrollY > 700);
      },
      { passive: true }
    );
  }

  /* ---------- âncora clicável em cada título ---------- */
  document.querySelectorAll("section[id] > h2").forEach(function (h) {
    var a = document.createElement("a");
    a.href = "#" + h.parentElement.id;
    a.textContent = "¶";
    a.className = "ancora";
    a.setAttribute("aria-label", "Link para esta seção");
    h.appendChild(a);
  });
})();
