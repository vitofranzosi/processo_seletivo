/* Navegação, busca local e "voltar ao topo".
   Sem dependência externa: o arquivo abre por file:// sem servidor. */
(function () {
  "use strict";

  var lateral = document.querySelector(".lateral");
  var abre = document.querySelector(".abre-menu");
  var campo = document.getElementById("busca");
  var vazia = document.querySelector(".busca-vazia");
  var links = Array.prototype.slice.call(document.querySelectorAll("nav.sumario a"));
  var topo = document.querySelector(".ao-topo");

  /* ---- menu no celular ---- */
  if (abre) {
    abre.addEventListener("click", function () {
      lateral.classList.toggle("aberta");
    });
  }
  links.forEach(function (a) {
    a.addEventListener("click", function () {
      lateral.classList.remove("aberta");
    });
  });

  /* ---- índice ativo conforme a rolagem ---- */
  var alvos = links
    .map(function (a) {
      var id = a.getAttribute("href");
      return id && id.charAt(0) === "#" ? document.getElementById(id.slice(1)) : null;
    })
    .filter(Boolean);

  if ("IntersectionObserver" in window && alvos.length) {
    var visiveis = new Set();
    var observador = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (e) {
          if (e.isIntersecting) visiveis.add(e.target.id);
          else visiveis.delete(e.target.id);
        });
        var primeiro = alvos.find(function (t) {
          return visiveis.has(t.id);
        });
        if (!primeiro) return;
        links.forEach(function (a) {
          a.classList.toggle("ativo", a.getAttribute("href") === "#" + primeiro.id);
        });
      },
      { rootMargin: "-10% 0px -70% 0px", threshold: 0 }
    );
    alvos.forEach(function (t) {
      observador.observe(t);
    });
  }

  /* ---- busca: filtra o índice pelo texto da seção inteira ---- */
  var dobra = function (s) {
    return s
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  };

  var indice = links.map(function (a) {
    var href = a.getAttribute("href") || "";
    var alvo = href.charAt(0) === "#" ? document.getElementById(href.slice(1)) : null;
    return {
      link: a,
      item: a.closest("li"),
      texto: dobra((a.textContent || "") + " " + (alvo ? alvo.textContent || "" : "")),
    };
  });

  var termos = document.querySelectorAll(".glossario dt");

  if (campo) {
    campo.addEventListener("input", function () {
      var q = dobra(campo.value.trim());
      var achou = 0;
      indice.forEach(function (registro) {
        var bate = !q || registro.texto.indexOf(q) !== -1;
        if (registro.item) registro.item.classList.toggle("oculto", !bate);
        if (bate) achou++;
      });
      document.querySelectorAll("nav.sumario .grupo").forEach(function (g) {
        g.style.display = q ? "none" : "";
      });
      /* o glossário também responde à busca, porque é onde se procura um termo */
      termos.forEach(function (dt) {
        var bloco = [dt];
        var n = dt.nextElementSibling;
        while (n && n.tagName === "DD") {
          bloco.push(n);
          n = n.nextElementSibling;
        }
        var bate =
          !q ||
          bloco.some(function (el) {
            return dobra(el.textContent || "").indexOf(q) !== -1;
          });
        bloco.forEach(function (el) {
          el.classList.toggle("oculto", !bate);
        });
      });
      if (vazia) vazia.style.display = q && !achou ? "block" : "none";
    });

    campo.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        campo.value = "";
        campo.dispatchEvent(new Event("input"));
      }
      if (e.key === "Enter") {
        var primeiro = indice.find(function (r) {
          return r.item && !r.item.classList.contains("oculto");
        });
        if (primeiro) primeiro.link.click();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== campo) {
        e.preventDefault();
        campo.focus();
      }
    });
  }

  /* ---- voltar ao topo ---- */
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

  /* ---- âncora clicável em cada título ---- */
  document.querySelectorAll("section[id] > h2").forEach(function (h) {
    var secao = h.parentElement;
    var a = document.createElement("a");
    a.href = "#" + secao.id;
    a.textContent = "¶";
    a.setAttribute("aria-label", "Link para esta seção");
    a.style.cssText =
      "float:right;font-weight:400;text-decoration:none;color:var(--texto-tenue);opacity:.35;font-size:.8em";
    h.appendChild(a);
  });
})();
