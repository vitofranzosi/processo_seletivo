/* Protótipo de estudo — rodada 2. Duas vistas sobre o mesmo modelo: o trilho e o texto do edital. */
(function () {
  "use strict";
  const G = window.GPS2;
  const q = new URLSearchParams(location.search);

  const S = {
    m: null,
    cenario: q.get("cenario") || "pronto",
    perfil: q.get("perfil") || "docinfo",
    modo: q.get("modo") === "texto" ? "texto" : "trilho",
    modoMarca: q.get("marca") === "manual" ? "manual" : "derivada",
    sel: null,
    pendente: null,
    anteriores: false,
    foco: null,
    anuncio: "",
  };

  function carregar(cenario) {
    S.m = G.base();
    (G.cenarios[cenario] || G.cenarios.pronto).aplicar(S.m);
    S.cenario = cenario;
    S.pendente = null;
  }
  carregar(S.cenario);
  if (q.get("sel")) {
    const [tipo, id] = q.get("sel").split(":");
    S.sel = { tipo, id };
  }

  // ------------------------------------------------------------------ utilidades

  const esc = function (t) {
    return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };
  const perfilAtivo = function (m) {
    return (m || S.m).perfis.find(function (p) { return p.id === S.perfil; }) || S.m.perfis[0];
  };
  const acharMarco = function (m, perfilId, id) {
    const p = m.perfis.find(function (x) { return x.id === perfilId; });
    return p && p.marcos.find(function (x) { return x.id === id; });
  };
  let seq = 1;
  const novoId = function (prefixo) {
    return prefixo + "-" + Date.now().toString(36) + "-" + seq++;
  };
  const modeloVisivel = function () {
    return S.pendente ? S.pendente.depois : S.m;
  };
  const nivelRotulo = {
    naoRespondida: "sem resposta",
    incompleta: "incompleta",
    invalida: "inválida",
    execucao: "falha na execução",
    leitura: "leitura",
  };

  function ordemDaJornada(m, p) {
    return p.marcos.slice().sort(function (a, b) {
      const pa = G.posicao(m, a);
      const pb = G.posicao(m, b);
      if (pa !== pb) return pa - pb;
      const da = a.corte.destino === "nenhuma" ? 99 : G.indice(m, a.corte.destino);
      const db = b.corte.destino === "nenhuma" ? 99 : G.indice(m, b.corte.destino);
      return da - db;
    });
  }

  function resumoDoCorte(m, p, mc) {
    const c = mc.corte;
    if (c.tipo === "nao") return "não corta — a etapa seguinte recebe todos";
    if (c.destino === "") return "segue para… <em>qual Etapa?</em>";
    if (!c.destino) return "o que acontece depois? <em>sem resposta</em>";
    const quantos = c.tipo === "quadro" ? (p.vagas === 1 ? "a vaga do quadro" : "as " + p.vagas + " vagas do quadro") : c.tipo === "fixo" ? (c.alvo || "?") + (c.suplentes ? " + " + c.suplentes + " suplentes" : "") : "quantos?";
    const emp = c.empate === "todos" ? " + empatados" : "";
    if (c.destino === "nenhuma") return "classificação final · " + quantos + emp;
    return quantos + emp + " seguem para " + esc(G.etapa(m, c.destino).nome);
  }

  function desempateFora(mc) {
    const fora = [];
    mc.criterios.forEach(function (cr) {
      if (cr.tipo === "pontuacao" && cr.alvo && mc.entradas.indexOf(cr.alvo) < 0 && fora.indexOf(cr.alvo) < 0) fora.push(cr.alvo);
    });
    return fora;
  }

  function regraCurta(e) {
    if (e.forma === "decisao") return e.eliminatoria ? esc(e.desfavoravel) + " elimina" : esc(e.desfavoravel) + ": efeito não declarado";
    if (e.eliminatoria) return e.minima != null ? "elimina abaixo de " + G.fmt(e.minima) : "eliminatória sem mínima";
    return "não elimina";
  }

  // ------------------------------------------------------------------ cabeçalho e estado

  function contagem(diag, perfilId) {
    const c = { naoRespondida: 0, incompleta: 0, invalida: 0, execucao: 0, leitura: 0 };
    diag.forEach(function (d) {
      if (perfilId && d.perfil && d.perfil !== perfilId) return;
      c[d.nivel]++;
    });
    return c;
  }

  function cabecalho(diag) {
    const geral = contagem(diag);
    const impede = geral.incompleta + geral.invalida;
    const perfis = S.m.perfis
      .map(function (p) {
        const c = contagem(diag.filter(function (d) { return d.perfil === p.id; }));
        const marca = c.invalida ? "invalida" : c.incompleta ? "incompleta" : c.naoRespondida ? "naoRespondida" : c.execucao ? "execucao" : "ok";
        const semFinal = p.marcos.length && !G.relacoes(S.m, p).temFinal;
        const txt = c.invalida ? c.invalida + " inválida" + (c.invalida > 1 ? "s" : "") : c.incompleta ? c.incompleta + " incompleta" + (c.incompleta > 1 ? "s" : "") : c.naoRespondida ? "perguntas abertas" : semFinal ? "sem pendência · sem ordem final" : c.execucao ? "sem pendência · " + c.execucao + " falha na execução" : "sem pendência";
        return '<button type="button" class="aba-perfil" data-acao="perfil" data-id="' + p.id + '" data-k="perfil:' + p.id + '" aria-pressed="' + (p.id === S.perfil) + '">' +
          '<span class="codigo">' + esc(p.codigo) + "</span><span class=\"estado estado-" + marca + '">' + txt + "</span></button>";
      })
      .join("");
    return (
      '<div class="faixa-estudo" role="note"><strong>Protótipo de estudo · rodada 2.</strong> Dados sintéticos. As regras são simplificações em JavaScript, ' +
      'cada uma citando a fonte no GPS; nada é gravado nem calculado com candidatos.</div>' +
      '<header class="topo"><div><p class="sobre">Edital sintético 90/2027 · em elaboração · 6 Etapas · 3 Perfis</p>' +
      "<h1>" + (S.modo === "trilho" ? "Trilho da classificação" : "Texto do edital que se edita") + "</h1></div>" +
      '<nav class="modos" aria-label="Vista"><button type="button" data-acao="modo" data-id="trilho" data-k="modo:trilho" aria-pressed="' + (S.modo === "trilho") + '">Trilho</button>' +
      '<button type="button" data-acao="modo" data-id="texto" data-k="modo:texto" aria-pressed="' + (S.modo === "texto") + '">Texto do edital</button></nav></header>' +
      '<div class="barra-perfis" role="group" aria-label="Perfil em edição">' + perfis + "</div>" +
      '<div class="eixos"><p><span class="eixo">Configuração</span> ' +
      geral.naoRespondida + " sem resposta · " + geral.incompleta + " incompleta" + (geral.incompleta === 1 ? "" : "s") + " · " + geral.invalida + " inválida" + (geral.invalida === 1 ? "" : "s") + "</p>" +
      '<p><span class="eixo">Publicação</span> ' + (impede ? "impedida por " + impede + " ponto" + (impede > 1 ? "s" : "") : "nada nesta parte a impede") + "</p>" +
      '<p><span class="eixo">Execução</span> depende de resultados e atos — ' + (geral.execucao ? geral.execucao + (geral.execucao > 1 ? " regras não funcionarão" : " regra não funcionará") + " como o texto diz" : "não se verifica aqui") + "</p></div>"
    );
  }

  // ------------------------------------------------------------------ trilho

  function trilho(diag) {
    const m = modeloVisivel();
    const p = perfilAtivo(m);
    const porMarco = {};
    diag.forEach(function (d) {
      if (d.alvo && d.alvo.tipo === "marco" && d.perfil === p.id) (porMarco[d.alvo.id] = porMarco[d.alvo.id] || []).push(d);
    });
    const usadas = new Set();
    p.marcos.forEach(function (mc) {
      mc.entradas.forEach(function (id) { usadas.add(id); });
    });
    const posFinal = Math.max.apply(null, [-1].concat(p.marcos.filter(function (mc) { return mc.corte.destino === "nenhuma"; }).map(function (mc) { return G.posicao(m, mc); })));
    const itens = [];
    m.etapas.forEach(function (e, i) {
      itens.push(
        '<li class="passagem"><span aria-hidden="true">▾</span> ' +
          (i === 0 ? "Entram os inscritos" : "Entram os habilitados em “" + esc(m.etapas[i - 1].nome) + "”" + (m.etapas.slice(0, i - 1).some(function (x) { return x.eliminatoria; }) ? " e não eliminados antes" : "")) +
          (p.marcos.some(function (mc) { return mc.corte.tipo !== "nao" && mc.corte.destino === e.id; }) ? "; entre eles, só os da faixa abaixo" : "") + "</li>"
      );
      p.marcos.forEach(function (mc) {
        if (mc.corte.destino !== e.id || mc.corte.tipo === "nao") return;
        const pos = G.posicao(m, mc);
        const puladas = m.etapas.slice(pos + 1, i).map(function (x) { return x.nome; });
        const quantos = mc.corte.tipo === "quadro" ? "tantos quantas as vagas da lista (" + p.vagas + " na ampla)" : (mc.corte.alvo || "?") + (mc.corte.suplentes ? " + " + mc.corte.suplentes + " suplentes" : "") + " por lista";
        itens.push(
          '<li class="portao' + (puladas.length ? " salta" : "") + '" data-portao="' + mc.id + '"><span class="seta" aria-hidden="true">▼</span> Depois de emitido o corte de <strong>' + esc(mc.codigo) + "</strong>, só entram " + quantos +
            (mc.corte.empate === "todos" ? " + empatados" : "") +
            (puladas.length ? ' <span class="aviso-salto">vem de antes de ' + esc(puladas.join(", ")) + ", que não é cortada</span>" : "") + "</li>"
        );
      });
      const usos = G.usos(m, e.id);
      const usosAqui = usos.filter(function (u) { return u.perfil.id === p.id; }).length;
      const classif = G.classificatoria(m, e, S.modoMarca);
      const depoisDoFinal = posFinal >= 0 && i > posFinal;
      const governa = p.marcos.filter(function (mc) { return mc.corte.tipo !== "nao" && mc.corte.destino === e.id; }).map(function (mc) { return mc.codigo; });
      const sel = S.sel && S.sel.tipo === "etapa" && S.sel.id === e.id;
      itens.push(
        '<li class="etapa' + (sel ? " selecionada" : "") + (depoisDoFinal ? " apos-final" : "") + '" data-etapa="' + e.id + '">' +
          '<button type="button" class="cartao-etapa" data-acao="sel" data-tipo="etapa" data-id="' + e.id + '" data-k="sel:etapa:' + e.id + '">' +
          '<span class="num">' + (i + 1) + "</span>" +
          '<span class="corpo"><span class="nome">' + esc(e.nome) + "</span>" +
          '<span class="meta">' + (e.forma === "nota" ? "nota" + (e.peso != null ? " · peso " + G.fmt(e.peso) : " · <em>sem peso</em>") : "decisão · " + esc(e.favoravel) + "/" + esc(e.desfavoravel)) + "</span>" +
          '<span class="meta">' + regraCurta(e) + "</span></span>" +
          '<span class="lado">' + (usosAqui ? '<span class="uso">usada em ' + usosAqui + (usosAqui > 1 ? " ordens" : " ordem") + "</span>" : depoisDoFinal ? '<span class="uso fraco">depois da final</span>' : governa.length ? "" : '<span class="uso fraco">nenhuma ordem usa a nota</span>') +
          (governa.length ? '<span class="uso">entrada decidida por ' + esc(governa.join(" e ")) + "</span>" : "") +
          (classif ? '<span class="marca">classificatória</span>' : "") + "</span></button>" +
          "</li>"
      );
      const aqui = ordemDaJornada(m, p).filter(function (mc) { return G.posicao(m, mc) === i; });
      aqui.forEach(function (mc) {
        const ds = porMarco[mc.id] || [];
        const pior = ["invalida", "incompleta", "naoRespondida", "leitura"].find(function (n) { return ds.some(function (d) { return d.nivel === n; }); }) || "ok";
        const selM = S.sel && S.sel.tipo === "marco" && S.sel.id === mc.id;
        const entradas = mc.entradas.map(function (id) {
          const x = G.etapa(m, id);
          return x.forma === "decisao" ? esc(x.nome) + " (porta)" : esc(x.nome) + " ×" + (x.peso == null ? "?" : G.fmt(x.peso));
        });
        itens.push(
          '<li class="marco' + (selM ? " selecionado" : "") + '" data-marco="' + mc.id + '">' +
            '<button type="button" class="cartao-marco estado-' + pior + '" data-acao="sel" data-tipo="marco" data-id="' + mc.id + '" data-k="sel:marco:' + mc.id + '">' +
            '<span class="rotulo">Ordem ' + esc(mc.codigo) + " · " + esc(mc.nome) + "</span>" +
            '<span class="usa">usa ' + (entradas.length ? entradas.join(" · ") : "<em>nenhuma etapa</em>") + "</span>" +
            (desempateFora(mc).length ? '<span class="usa">desempata pela nota de ' + desempateFora(mc).map(function (id) { return esc(G.etapa(m, id).nome); }).join(", ") + "</span>" : "") +
            '<span class="sai">' + resumoDoCorte(m, p, mc) + "</span>" +
            (pior !== "ok" ? '<span class="selo selo-' + pior + '">' + nivelRotulo[pior] + "</span>" : "") + "</button></li>"
        );
      });
      if (!S.pendente)
        itens.push(
          '<li class="junta"><button type="button" class="mais" data-acao="novo-marco" data-depois="' + i + '" data-k="novo-marco:' + i + '">+ ordenar ou cortar depois de ' + esc(e.nome) + "</button></li>"
        );
    });
    const prevista = S.pendente
      ? '<div class="previa-mudanca" role="status"><strong>Prévia da nova ordem das Etapas.</strong> Nada mudou ainda — confirme ou cancele no painel ao lado.</div>'
      : "";
    return (
      '<section class="area-trilho" aria-labelledby="t-trilho">' + prevista +
      '<h2 id="t-trilho" class="sr">Trilho do Perfil ' + esc(p.codigo) + "</h2>" +
      '<p class="legenda"><span class="lg lg-etapa"></span> Etapa do edital (vale para todos os Perfis) <span class="lg lg-marco"></span> Ordem deste Perfil, posta depois da última Etapa que usa <span class="lg lg-portao"></span> Corte: decide quem entra, por lista</p>' +
      '<p class="legenda" aria-hidden="true"><svg width="34" height="10"><path class="arco" d="M2 5H26"/><path class="arco ponta" d="M22 1L27 5L22 9"/></svg> nota que entra na conta <svg width="34" height="10"><path class="arco porta" d="M2 5H27"/><path class="arco porta" d="M28 1V9"/></svg> porta: só filtra, não soma <svg width="34" height="10"><path class="arco desempate" d="M2 5H28"/></svg> nota usada só no desempate</p>' +
      '<p class="legenda">Ninguém eliminado numa Etapa chega às seguintes, haja corte ou não; e quem não for habilitado na Etapa anterior também não, depois que ela tiver resultado. As posições das ordens são leitura: o GPS não as grava.</p>' +
      '<div class="trilho-moldura"><svg class="arcos" aria-hidden="true"></svg><ol class="trilho" aria-label="Etapas e ordens de ' + esc(p.codigo) + ', na ordem do certame">' +
      itens.join("") +
      '<li class="fim' + (G.relacoes(m, p).temFinal ? "" : " sem-final") + '"><span>Resultado de ' + esc(p.codigo) + ": " + p.vagas + " vaga" + (p.vagas > 1 ? "s" : "") + ". " +
      (G.relacoes(m, p).temFinal ? "A ocupação é ato próprio." : "<strong>Nenhuma ordem chega aqui:</strong> todas alimentam outra Etapa, e ninguém é classificado para as vagas.") + "</span></li></ol></div></section>"
    );
  }

  function desenharArcos() {
    const svg = document.querySelector(".arcos");
    const moldura = document.querySelector(".trilho-moldura");
    if (!svg || !moldura || window.matchMedia("(max-width: 760px)").matches) return;
    const m = modeloVisivel();
    const p = perfilAtivo(m);
    const r0 = moldura.getBoundingClientRect();
    svg.setAttribute("width", r0.width);
    svg.setAttribute("height", r0.height);
    // Faixas aninhadas como parênteses: a ordem de menor alcance fica mais perto dos cartões, e as
    // de alcance maior passam por fora — assim as verticais não se atravessam. Cada ordem sai do
    // cartão da Etapa numa altura própria, para que duas ordens que usam a mesma Etapa não se
    // fundam numa linha só.
    const marcos = ordemDaJornada(m, p).filter(function (mc) { return mc.entradas.length; });
    const alcance = function (mc) {
      const idx = mc.entradas.concat(desempateFora(mc)).map(function (id) { return G.indice(m, id); });
      return Math.max.apply(null, idx) - Math.min.apply(null, idx);
    };
    const faixas = marcos.slice().sort(function (a, b) { return alcance(a) - alcance(b) || G.posicao(m, a) - G.posicao(m, b); });
    const n = faixas.length;
    const gap = Math.min(14, 54 / Math.max(n, 1));
    const realce = S.realce || (S.sel && S.sel.tipo === "marco" ? S.sel.id : null);
    const etapaSel = S.sel && S.sel.tipo === "etapa" ? S.sel.id : null;
    const ativo = function (mc) {
      return realce ? mc.id === realce : etapaSel ? mc.entradas.indexOf(etapaSel) >= 0 : false;
    };
    const algumAtivo = marcos.some(ativo);
    let fundo = "";
    let frente = "";
    faixas.forEach(function (mc, rank) {
      const el = moldura.querySelector('[data-marco="' + mc.id + '"] .cartao-marco');
      if (!el) return;
      const rm = el.getBoundingClientRect();
      const ym = rm.top - r0.top + Math.min(24, rm.height / 2);
      const xm = rm.left - r0.left;
      const cls = "arco" + (ativo(mc) ? " ativo" : algumAtivo ? " apagado" : "");
      let traco = "";
      let topo = ym;
      let base = ym;
      let xLane = null;
      // Cada ligação tem o seu tipo: nota que entra na conta, porta que só filtra, nota só de
      // desempate. As três descem pela mesma faixa até a ordem.
      const ligacoes = mc.entradas.map(function (id) { return { id: id, tipo: G.ePorta(m, id) ? "porta" : "nota" }; })
        .concat(desempateFora(mc).map(function (id) { return { id: id, tipo: "desempate" }; }));
      ligacoes.forEach(function (lg) {
        const ee = moldura.querySelector('[data-etapa="' + lg.id + '"] .cartao-etapa');
        if (!ee) return;
        const re = ee.getBoundingClientRect();
        const xe = re.left - r0.left;
        if (xLane === null) xLane = xe - 12 - rank * gap;
        const ye = re.top - r0.top + re.height / 2 + (rank - (n - 1) / 2) * 7;
        topo = Math.min(topo, ye);
        base = Math.max(base, ye);
        if (lg.tipo === "porta") {
          traco += '<path class="' + cls + ' porta" d="M' + xe + " " + ye + " H" + xLane + '"/>' +
            '<path class="' + cls + ' porta" d="M' + (xe - 6) + " " + (ye - 5) + " V" + (ye + 5) + '"/>';
        } else if (lg.tipo === "desempate") {
          traco += '<path class="' + cls + ' desempate" d="M' + xe + " " + ye + " H" + xLane + '"/>';
        } else {
          traco += '<path class="' + cls + '" d="M' + xe + " " + ye + " H" + xLane + '"/>' +
            '<circle class="' + cls + ' ponto" cx="' + xe + '" cy="' + ye + '" r="2.6"/>';
        }
      });
      if (xLane === null) return;
      traco += '<path class="' + cls + '" d="M' + xLane + " " + topo + " V" + base + " M" + xLane + " " + ym + " H" + (xm - 1) + '"/>' +
        '<path class="' + cls + ' ponta" d="M' + (xm - 7) + " " + (ym - 4) + " L" + (xm - 1) + " " + ym + " L" + (xm - 7) + " " + (ym + 4) + '"/>';
      const pt = moldura.querySelector('[data-portao="' + mc.id + '"]');
      let corte = "";
      if (pt) {
        const rp = pt.getBoundingClientRect();
        const yp = rp.top - r0.top + rp.height / 2;
        const xd = r0.width - 14 - rank * gap;
        corte = '<path class="' + cls + ' corte" d="M' + (rm.right - r0.left) + " " + ym + " H" + xd + " V" + yp + " H" + (rp.right - r0.left) + '"/>';
      }
      if (ativo(mc)) frente += traco + corte; else fundo += traco + corte;
    });
    svg.innerHTML = fundo + frente;
  }

  // ------------------------------------------------------------------ inspetor

  function campoDiag(ds) {
    if (!ds.length) return "";
    return '<ul class="achados">' + ds.map(function (d) {
      return '<li class="achado achado-' + d.nivel + '"><span class="selo selo-' + d.nivel + '">' + nivelRotulo[d.nivel] + "</span> " + d.texto +
        (d.campo ? ' <button type="button" class="link" data-acao="ir" data-campo="' + esc(d.campo) + '">ir ao campo</button>' : "") + "</li>";
    }).join("") + "</ul>";
  }

  function inspetor(diag) {
    if (S.pendente) return inspetorMudanca();
    if (!S.sel) return inspetorVazio(diag);
    if (S.sel.tipo === "etapa") return inspetorEtapa(diag);
    return inspetorMarco(diag);
  }

  function inspetorVazio(diag) {
    const m = S.m;
    const p = perfilAtivo();
    const blocos = ordemDaJornada(m, p).map(function (mc) {
      const fr = G.frases(m, p, mc);
      return "<h3>" + esc(mc.codigo) + " · " + esc(mc.nome) + "</h3><p>" + [fr.ordem, fr.porta].concat(fr.corte).filter(Boolean).join(" ") +
        (fr.desempate.length ? " Persistindo o empate, terá preferência, sucessivamente: " + fr.desempate.map(function (t, i) { return String.fromCharCode(97 + i) + ") " + t; }).join("; ") + "." : "") + "</p>";
    });
    const leituras = diag.filter(function (d) { return d.perfil === p.id && d.nivel === "leitura"; });
    return (
      '<h2 id="t-insp" tabindex="-1">O que ' + esc(p.codigo) + " vai publicar</h2>" +
      '<p class="nota">Escolha uma Etapa ou uma ordem no trilho para editar. Este é o texto do documento, na ordem do certame.</p>' +
      (blocos.join("") || "<p>Nenhuma ordem ainda. Use <strong>+ ordenar ou cortar</strong> no trilho, depois da Etapa em que o edital decide algo.</p>") +
      (leituras.length ? '<h3>Leituras da estrutura</h3><p class="nota">Não são erros: é o que a ordem das Etapas faz. Confira com o edital.</p>' + campoDiag(leituras) : "")
    );
  }

  function inspetorEtapa(diag) {
    const m = S.m;
    const e = G.etapa(m, S.sel.id);
    if (!e) return "";
    const i = G.indice(m, e.id);
    const t = G.tabelaLocal(e);
    const usos = G.usos(m, e.id);
    const k = "etapa:" + e.id + ":";
    const linhas = t.linhas.map(function (l) {
      return "<tr><th scope=\"row\">" + esc(l[0]) + "</th><td>" + esc(l[1]) + "</td></tr>";
    }).join("");
    const classif = G.classificatoria(m, e, S.modoMarca);
    let marca;
    if (S.modoMarca === "derivada") {
      marca = '<p class="derivada"><strong>' + (classif ? "Classificatória" : "Não classificatória") + "</strong> — " +
        (classif ? "porque " + usos.length + " uso" + (usos.length > 1 ? "s" : "") + " a coloca" + (usos.length > 1 ? "m" : "") + " numa ordem. O edital publica “caráter classificatório”." : "nenhuma ordem a usa.") +
        ' <span class="nota">Opção D-1(c): a marca é deduzida dos usos e continua gravada no campo de sempre.</span></p>';
    } else {
      marca = '<p><label><input type="checkbox" data-b="' + k + 'classificatoriaManual" data-k="' + k + 'marca"' + (e.classificatoriaManual ? " checked" : "") + "> Classificatória</label></p>" +
        (!e.classificatoriaManual && usos.length ? '<p class="achado achado-invalida">Ainda há ' + usos.length + " uso" + (usos.length > 1 ? "s" : "") + " — eles continuam apontando esta Etapa e ficam inválidos. Restaure a marca ou retire a Etapa de cada ordem abaixo.</p>" : "");
    }
    const listaUsos = usos.length
      ? "<ul class=\"usos\">" + usos.map(function (u) {
          return "<li>" + esc(u.perfil.codigo) + " · " + esc(u.marco.codigo) + " — " + (u.como === "entrada" ? (e.forma === "decisao" ? "porta" : "parcela") : "desempate") +
            (S.modoMarca === "manual" && !e.classificatoriaManual && u.como === "entrada" ? ' <button type="button" class="link" data-acao="retirar-uso" data-perfil="' + u.perfil.id + '" data-marco="' + u.marco.id + '" data-etapa="' + e.id + '">retirar desta ordem</button>' : "") + "</li>";
        }).join("") + "</ul>"
      : '<p class="nota">Nenhuma ordem usa esta Etapa. Ela ainda vale para a progressão: ' + (e.eliminatoria ? "quem for eliminado nela não segue." : "não elimina ninguém.") + "</p>";
    return (
      '<h2 id="t-insp" tabindex="-1">Etapa ' + (i + 1) + " · " + esc(e.nome) + "</h2>" +
      '<p class="nota">Vale para todos os Perfis do edital.</p>' +
      campoDiag(diag.filter(function (d) { return d.alvo && d.alvo.tipo === "etapa" && d.alvo.id === e.id; })) +
      '<p><label>Nome<br><input type="text" data-b="' + k + 'nome" data-k="' + k + 'nome" value="' + esc(e.nome) + '"></label></p>' +
      '<fieldset><legend>Como se conclui</legend><label><input type="radio" name="forma-' + e.id + '" value="nota" data-b="' + k + 'forma" data-k="' + k + 'forma-nota"' + (e.forma === "nota" ? " checked" : "") + "> com nota</label> " +
      '<label><input type="radio" name="forma-' + e.id + '" value="decisao" data-b="' + k + 'forma" data-k="' + k + 'forma-decisao"' + (e.forma === "decisao" ? " checked" : "") + "> com decisão, sem nota</label></fieldset>" +
      '<fieldset class="tabela-local"><legend>O que o resultado causa nesta Etapa</legend>' +
      (e.forma === "nota"
        ? '<p class="linha-campos"><label><input type="checkbox" data-b="' + k + 'eliminatoria" data-k="' + k + 'elim" data-campo="eliminatoria"' + (e.eliminatoria ? " checked" : "") + "> Eliminatória</label> " +
          '<label>Nota mínima <input type="number" step="0.5" min="0" data-b="' + k + 'minima" data-k="' + k + 'min" value="' + (e.minima == null ? "" : e.minima) + '" class="curto"></label> ' +
          '<label>Máxima <input type="number" min="0" data-b="' + k + 'maxima" data-k="' + k + 'max" value="' + (e.maxima == null ? "" : e.maxima) + '" class="curto"></label></p>'
        : '<p class="linha-campos"><label>Favorável <input type="text" data-b="' + k + 'favoravel" data-k="' + k + 'fav" value="' + esc(e.favoravel) + '" class="medio"></label> ' +
          '<label>Desfavorável <input type="text" data-b="' + k + 'desfavoravel" data-k="' + k + 'desf" value="' + esc(e.desfavoravel) + '" class="medio"></label> ' +
          '<label><input type="checkbox" data-b="' + k + 'eliminatoria" data-k="' + k + 'elim" data-campo="eliminatoria"' + (e.eliminatoria ? " checked" : "") + "> Eliminatória</label></p>") +
      '<table class="decisao"><caption class="sr">Resultado e consequência</caption><thead><tr><th scope="col">Resultado</th><th scope="col">Consequência</th></tr></thead><tbody>' + linhas + "</tbody></table>" +
      (t.nota ? '<p class="nota">' + esc(t.nota) + "</p>" : "") + "</fieldset>" +
      (e.forma === "nota"
        ? '<p><label>Peso <input type="number" step="0.5" min="0" data-b="' + k + 'peso" data-k="' + k + 'peso" data-campo="peso:' + e.id + '" value="' + (e.peso == null ? "" : e.peso) + '" class="curto"></label> ' +
          '<span class="nota">o mesmo em todos os usos abaixo</span></p>'
        : '<p class="nota">Decisória não tem peso: numa ordem, ela é uma porta.</p>') +
      "<h3>Onde é usada</h3>" + listaUsos +
      '<h3>Caráter classificatório</h3><div data-campo="marca:' + e.id + '">' + marca + "</div>" +
      '<h3>Posição no certame</h3><p class="linha-campos"><button type="button" data-acao="mover" data-id="' + e.id + '" data-dir="-1" data-k="' + k + 'subir"' + (i === 0 ? " disabled" : "") + ">↑ antes</button> " +
      '<button type="button" data-acao="mover" data-id="' + e.id + '" data-dir="1" data-k="' + k + 'descer"' + (i === S.m.etapas.length - 1 ? " disabled" : "") + ">↓ depois</button> " +
      '<span class="nota">Mudar a posição mostra o efeito antes de confirmar.</span></p>' +
      '<p><button type="button" class="link" data-acao="desselecionar">Voltar ao resumo</button></p>'
    );
  }

  function opcaoDestino(m, mc, pos, e, i) {
    const circular = mc.entradas.indexOf(e.id) >= 0;
    const puladas = i > pos + 1 ? m.etapas.slice(pos + 1, i).map(function (x) { return x.nome; }) : [];
    let rot = e.nome + (circular ? " — não: esta ordem usa a nota dela" : puladas.length ? " — antes dela: " + puladas.join(", ") : i === pos + 1 ? " — a seguinte" : "");
    if (i <= pos && !circular) rot = e.nome + " — acontece antes desta ordem";
    return '<option value="' + e.id + '"' + (mc.corte.destino === e.id ? " selected" : "") + (circular ? " disabled" : "") + ">" + esc(rot) + "</option>";
  }

  function inspetorMarco(diag) {
    const m = S.m;
    const p = perfilAtivo();
    const mc = acharMarco(m, p.id, S.sel.id);
    if (!mc) return inspetorVazio(diag);
    const pos = G.posicao(m, mc);
    const fr = G.frases(m, p, mc);
    const k = "marco:" + p.id + ":" + mc.id + ":";
    const c = mc.corte;
    const ds = diag.filter(function (d) { return d.alvo && d.alvo.tipo === "marco" && d.alvo.id === mc.id && d.perfil === p.id; });
    const pontuadas = mc.entradas.filter(function (id) { return !G.ePorta(m, id); });
    const entradas = m.etapas.map(function (e) {
      const marcada = mc.entradas.indexOf(e.id) >= 0;
      const ok = G.classificatoria(m, e, S.modoMarca) || S.modoMarca === "derivada";
      return '<li><label><input type="checkbox" data-acao="entrada" data-perfil="' + p.id + '" data-marco="' + mc.id + '" value="' + e.id + '" data-k="' + k + "ent:" + e.id + '"' + (marcada ? " checked" : "") + (!ok && !marcada ? " disabled" : "") + "> " +
        esc(e.nome) + "</label> <span class=\"nota\">" + (e.forma === "decisao" ? "porta — exige " + esc(e.favoravel) + ", não soma" : e.peso == null ? "<strong>sem peso</strong>" : "peso " + G.fmt(e.peso)) + (!ok ? " · não classificatória" : "") + "</span></li>";
    }).join("");
    const destinoOpts = m.etapas.map(function (e, i) {
      if (i <= pos && !S.anteriores && mc.corte.destino !== e.id) return "";
      return opcaoDestino(m, mc, pos, e, i);
    }).join("");
    const segueQuando = c.tipo !== "nao" && c.destino !== null && c.destino !== "nenhuma";
    const vagas = c.tipo !== "nao" && c.destino === "nenhuma";
    const criterios = mc.criterios.map(function (cr, i) {
      const kc = "crit:" + p.id + ":" + mc.id + ":" + i + ":";
      const temData = p.fatos.some(function (f) { return f.tipo === "data"; });
      const val = cr.tipo === "pontuacao" ? "pont:" + (cr.alvo || "") : cr.tipo === "menor_fato" && p.fatos.find(function (f) { return f.id === cr.alvo && f.tipo === "data"; }) ? "velho" : cr.tipo === "maior_fato" && p.fatos.find(function (f) { return f.id === cr.alvo && f.tipo === "data"; }) ? "novo" : "";
      const opts = ['<option value="">Escolha…</option>']
        .concat(m.etapas.filter(function (e) { return e.forma === "nota"; }).map(function (e) {
          return '<option value="pont:' + e.id + '"' + (val === "pont:" + e.id ? " selected" : "") + ">Maior nota em " + esc(e.nome) + "</option>";
        }))
        .concat(['<option value="velho"' + (val === "velho" ? " selected" : "") + ">Mais velho primeiro" + (temData ? "" : " (declara a data de nascimento)") + "</option>",
          '<option value="novo"' + (val === "novo" ? " selected" : "") + ">Mais novo primeiro" + (temData ? "" : " (declara a data de nascimento)") + "</option>"]);
      return '<li class="criterio" data-campo="criterio:' + i + '"><span class="ordem-crit">' + (i + 1) + "º</span> " +
        '<label class="sr" for="' + kc + 'q">Critério ' + (i + 1) + "</label>" +
        '<select id="' + kc + 'q" data-acao="criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-i="' + i + '" data-k="' + kc + 'q">' + opts.join("") + "</select> " +
        '<label>Sem o valor: <select data-b="' + kc + 'ausente" data-k="' + kc + 'aus"><option value="">escolha…</option><option value="ultimo"' + (cr.ausente === "ultimo" ? " selected" : "") + '>fica por último</option><option value="naoaplica"' + (cr.ausente === "naoaplica" ? " selected" : "") + ">o critério não se aplica</option></select></label> " +
        '<button type="button" class="link" data-acao="rm-criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-i="' + i + '">remover</button>' +
        '<p class="traducao">→ ' + G.fraseDoCriterio(m, p, cr) + "</p></li>";
    }).join("");
    return (
      '<h2 id="t-insp" tabindex="-1">Ordem ' + esc(mc.codigo) + " · " + esc(mc.nome) + "</h2>" +
      '<p class="nota">Do Perfil ' + esc(p.codigo) + ". Fica no trilho depois de " + (pos >= 0 ? "“" + esc(m.etapas[pos].nome) + "”, a última Etapa que usa" : "nenhuma Etapa") + ".</p>" +
      campoDiag(ds) +
      '<div class="documento" aria-live="polite"><p class="sobre">Como o edital vai dizer</p><p>' + [fr.ordem, fr.porta].concat(fr.corte).filter(Boolean).join(" ") +
      (fr.desempate.length ? " Persistindo o empate, terá preferência, sucessivamente: " + fr.desempate.map(function (t, i) { return String.fromCharCode(97 + i) + ") " + t; }).join("; ") + "." : "") + "</p></div>" +
      '<fieldset data-campo="entradas"><legend>1. O que forma esta ordem</legend><ul class="sem-marca">' + entradas + "</ul></fieldset>" +
      (pontuadas.length >= 2 || (mc.entradas.length && !pontuadas.length)
        ? '<fieldset data-campo="divide"><legend>2. As notas são divididas pela soma dos pesos?</legend>' +
          '<label><input type="radio" name="' + k + 'div" value="sim" data-b="' + k + 'divide" data-k="' + k + 'div-sim"' + (mc.divide ? " checked" : "") + "> Sim — média ponderada</label> " +
          '<label><input type="radio" name="' + k + 'div" value="nao" data-b="' + k + 'divide" data-k="' + k + 'div-nao"' + (!mc.divide ? " checked" : "") + "> Não — soma ponderada</label>" +
          '<p class="nota">Uma pergunta só. No GPS são dois campos (combinação e normalização) para este mesmo efeito.</p></fieldset>'
        : "") +
      '<fieldset data-campo="destino"><legend>3. Depois desta ordem</legend>' +
      '<label><input type="radio" name="' + k + 'dep" value="segue" data-acao="depois" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="' + k + 'dep-segue"' + (segueQuando ? " checked" : "") + "> quem passar segue para uma Etapa</label><br>" +
      (segueQuando
        ? '<label class="recuo">Etapa <select data-b="' + k + 'corte.destino" data-k="' + k + 'destino">' + (c.destino ? "" : '<option value="" selected>Escolha a Etapa</option>') + destinoOpts + "</select></label>" +
          '<label class="recuo nota"><input type="checkbox" data-acao="anteriores" data-k="' + k + 'ant"' + (S.anteriores ? " checked" : "") + "> mostrar Etapas que acontecem antes (o GPS permite; é raro)</label><br>"
        : "") +
      '<label><input type="radio" name="' + k + 'dep" value="final" data-acao="depois" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="' + k + 'dep-final"' + (vagas ? " checked" : "") + "> é a classificação final, para as vagas</label><br>" +
      '<label><input type="radio" name="' + k + 'dep" value="nao" data-acao="depois" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="' + k + 'dep-nao"' + (c.tipo === "nao" ? " checked" : "") + "> só ordena; ninguém é cortado</label></fieldset>" +
      (c.destino !== null && c.tipo !== "nao"
        ? '<fieldset data-campo="tipo"><legend>4. Quantos</legend>' +
          '<label><input type="radio" name="' + k + 'tipo" value="fixo" data-b="' + k + 'corte.tipo" data-k="' + k + 'tipo-fixo"' + (c.tipo === "fixo" ? " checked" : "") + "> um número fixo</label> " +
          '<label><input type="radio" name="' + k + 'tipo" value="quadro" data-b="' + k + 'corte.tipo" data-k="' + k + 'tipo-quadro"' + (c.tipo === "quadro" ? " checked" : "") + "> as vagas do quadro (" + p.vagas + ")</label>" +
          (c.tipo === "fixo"
            ? '<p class="linha-campos" data-campo="alvo"><label>Primeiros <input type="number" min="1" class="curto" data-b="' + k + 'corte.alvo" data-k="' + k + 'alvo" value="' + (c.alvo || "") + '"></label> ' +
              '<label>+ suplentes <input type="number" min="0" class="curto" data-b="' + k + 'corte.suplentes" data-k="' + k + 'sup" value="' + (c.suplentes || 0) + '"></label></p>'
            : "") +
          "</fieldset>" +
          '<fieldset data-campo="empate"><legend>5. Empate na última posição</legend>' +
          '<label><input type="radio" name="' + k + 'emp" value="todos" data-b="' + k + 'corte.empate" data-k="' + k + 'emp-todos"' + (c.empate === "todos" ? " checked" : "") + "> todos os empatados passam</label><br>" +
          '<label><input type="radio" name="' + k + 'emp" value="para" data-b="' + k + 'corte.empate" data-k="' + k + 'emp-para"' + (c.empate === "para" ? " checked" : "") + "> o número não é ultrapassado (o corte pode ficar impedido)</label></fieldset>" +
          '<fieldset data-campo="continuacao"><legend>6. Se alguém de dentro não assumir</legend>' +
          '<label><input type="radio" name="' + k + 'cont" value="sim" data-b="' + k + 'corte.continuacao" data-k="' + k + 'cont-sim"' + (c.continuacao === "sim" ? " checked" : "") + "> chamar os próximos da ordem</label><br>" +
          '<label><input type="radio" name="' + k + 'cont" value="nao" data-b="' + k + 'corte.continuacao" data-k="' + k + 'cont-nao"' + (c.continuacao === "nao" ? " checked" : "") + "> não chamar ninguém além</label>" +
          '<p class="nota">No GPS: “Faixa seguinte”.</p></fieldset>'
        : "") +
      '<fieldset><legend>7. Desempate, na ordem</legend><ol class="criterios sem-marca">' + criterios + "</ol>" +
      '<button type="button" data-acao="add-criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="' + k + 'addcrit">+ critério</button></fieldset>' +
      '<details class="nome-codigo"><summary>Nome e código</summary><p><label>Denominação <input type="text" data-b="' + k + 'nome" data-k="' + k + 'nome" value="' + esc(mc.nome) + '"></label></p>' +
      '<p><label>Código <input type="text" class="medio" data-b="' + k + 'codigo" data-k="' + k + 'codigo" value="' + esc(mc.codigo) + '"></label></p></details>' +
      '<p class="linha-campos"><button type="button" class="link" data-acao="desselecionar">Voltar ao resumo</button> <button type="button" class="link perigo" data-acao="rm-marco" data-perfil="' + p.id + '" data-marco="' + mc.id + '">Remover esta ordem</button></p>'
    );
  }

  function inspetorMudanca() {
    const pd = S.pendente;
    const e = G.etapa(S.m, pd.id);
    const im = G.impacto(S.m, pd.depois, S.modoMarca);
    const li = function (arr, cls) {
      return arr.map(function (x) {
        return '<li class="achado achado-' + (cls || x.nivel) + '">' + (typeof x === "string" ? x : '<span class="selo selo-' + x.nivel + '">' + nivelRotulo[x.nivel] + "</span> " + x.texto) + "</li>";
      }).join("");
    };
    return (
      '<h2 id="t-insp" tabindex="-1">Mover “' + esc(e.nome) + "” " + (pd.dir < 0 ? "para antes" : "para depois") + "</h2>" +
      '<p class="nota">Calculado só da estrutura: quais ordens, cortes e Etapas mudam de relação. Quantas pessoas mudam de lugar depende de notas que ainda não existem.</p>' +
      (im.posicoes.length ? "<h3>Ordens que mudam de lugar</h3><ul class=\"achados\">" + li(im.posicoes, "leitura") + "</ul>" : "") +
      (im.novas.length ? "<h3>Passa a valer</h3><ul class=\"achados\">" + li(im.novas) + "</ul>" : "") +
      (im.resolvidas.length ? "<h3>Deixa de valer</h3><ul class=\"achados\">" + li(im.resolvidas) + "</ul>" : "") +
      (!im.posicoes.length && !im.novas.length && !im.resolvidas.length ? "<p>Nenhuma relação entre ordens, cortes e Etapas muda.</p>" : "") +
      '<p class="linha-campos"><button type="button" class="primario" data-acao="confirmar-mover" data-k="confirmar-mover">Confirmar a nova ordem</button> ' +
      '<button type="button" data-acao="cancelar-mover" data-k="cancelar-mover">Cancelar</button></p>'
    );
  }

  // ------------------------------------------------------------------ vista "texto do edital"

  function texto(diag) {
    const m = S.m;
    const etapas = m.etapas.map(function (e, i) {
      const k = "etapa:" + e.id + ":";
      const t = G.tabelaLocal(e);
      const caixa = '<label><input type="checkbox" data-b="' + k + 'eliminatoria" data-k="tx-' + k + 'elim"' + (e.eliminatoria ? " checked" : "") + "> eliminatória</label>";
      const regra = !e.eliminatoria
        ? caixa + ' <span class="nota">ninguém é eliminado nesta Etapa</span>'
        : e.forma === "nota"
          ? caixa + " — elimina quem tiver nota menor que " +
            '<input type="number" step="0.5" class="curto slot' + (e.minima == null ? " vazio" : "") + '" aria-label="Nota mínima de ' + esc(e.nome) + '" data-b="' + k + 'minima" data-k="tx-' + k + 'min" value="' + (e.minima == null ? "" : e.minima) + '">'
          : caixa + " — elimina quem obtiver “" + esc(e.desfavoravel) + "”";
      const vistos = {};
      const usos = [];
      G.usos(m, e.id).forEach(function (u) {
        const chave = u.perfil.codigo + " " + u.marco.codigo;
        if (vistos[chave]) { if (u.como === "desempate") vistos[chave].push("desempate"); return; }
        vistos[chave] = [u.como === "desempate" ? "desempate" : ""];
        usos.push(chave);
      });
      usos.forEach(function (chave, i) {
        const extra = vistos[chave].filter(Boolean);
        if (extra.length) usos[i] = chave + " (" + (vistos[chave][0] ? "" : "nota e ") + "desempate)";
      });
      return "<tr><th scope=\"row\">" + (i + 1) + ". " + esc(e.nome) + "</th><td>" + (e.forma === "nota" ? "nota de 0 a " + (e.maxima || "?") : "“" + esc(e.favoravel) + "” ou “" + esc(e.desfavoravel) + "”") + "</td><td>" + regra +
        (t.impede ? '<span class="nota-margem achado-execucao">' + esc(t.impede) + "</span>" : "") + "</td><td>" +
        (e.forma === "nota" ? '<input type="number" step="0.5" class="curto" aria-label="Peso de ' + esc(e.nome) + '" data-b="' + k + 'peso" data-k="tx-' + k + 'peso" value="' + (e.peso == null ? "" : e.peso) + '">' : "—") +
        "</td><td>" + (usos.length ? esc(usos.join(", ")) : '<span class="nota">não entra em ordem</span>') + "</td></tr>";
    }).join("");

    const perfis = m.perfis.map(function (p, pi) {
      const marcos = ordemDaJornada(m, p);
      const clausulas = marcos.map(function (mc, j) {
        return clausula(m, p, mc, "3." + (pi + 2) + "." + (j + 1), diag);
      }).join("");
      return '<section class="perfil-texto' + (p.id === S.perfil ? " ativo" : "") + '" aria-labelledby="tx-' + p.id + '"><h3 id="tx-' + p.id + '">3.' + (pi + 2) + " Perfil " + esc(p.codigo) + " — " + esc(p.nome) + " (" + p.vagas + " vaga" + (p.vagas > 1 ? "s" : "") + ")</h3>" +
        (clausulas || '<p class="vazio">Este Perfil ainda não classifica ninguém.</p>') +
        '<p class="acrescentar">Acrescentar uma ordem: <button type="button" data-acao="novo-marco-texto" data-perfil="' + p.id + '" data-tipo="corte" data-k="tx-add-corte:' + p.id + '">que seleciona quem segue para uma Etapa</button> ' +
        '<button type="button" data-acao="novo-marco-texto" data-perfil="' + p.id + '" data-tipo="final" data-k="tx-add-final:' + p.id + '">a classificação final</button></p>' +
        campoDiag(diag.filter(function (d) { return d.perfil === p.id && !d.alvo; })) + "</section>";
    }).join("");

    return (
      '<article class="edital" aria-label="Texto do edital, editável">' +
      '<p class="sobre">Cada trecho entre colchetes é um campo. O texto em volta é o que o documento publica.</p>' +
      "<h2>3. Como será a seleção</h2><h3>3.1 Etapas de avaliação</h3>" +
      '<table class="etapas-texto"><thead><tr><th scope="col">Etapa</th><th scope="col">Resultado</th><th scope="col">Quem é eliminado</th><th scope="col">Peso</th><th scope="col">Usada em</th></tr></thead><tbody>' + etapas + "</tbody></table>" +
      perfis + "</article>"
    );
  }

  function sel(nomeB, k, opcoes, atual, rotulo, extra) {
    return '<select class="slot' + (atual == null || atual === "" ? " vazio" : "") + '" aria-label="' + esc(rotulo) + '" data-b="' + nomeB + '" data-k="' + k + '"' + (extra || "") + ">" +
      (atual == null || atual === "" ? '<option value="" selected>[' + esc(rotulo) + "]</option>" : "") +
      opcoes.map(function (o) {
        return '<option value="' + esc(o[0]) + '"' + (String(atual) === String(o[0]) ? " selected" : "") + (o[2] ? " disabled" : "") + ">" + esc(o[1]) + "</option>";
      }).join("") + "</select>";
  }

  function clausula(m, p, mc, numero, diag) {
    const k = "marco:" + p.id + ":" + mc.id + ":";
    const kk = "tx-" + k;
    const c = mc.corte;
    const pos = G.posicao(m, mc);
    const pontuadas = mc.entradas.filter(function (id) { return !G.ePorta(m, id); });
    const chips = mc.entradas.map(function (id) {
      const e = G.etapa(m, id);
      return '<span class="chip">' + esc(e.nome) + (e.forma === "decisao" ? " (exige “" + esc(e.favoravel) + "”)" : " (peso " + (e.peso == null ? "?" : G.fmt(e.peso)) + ")") +
        '<button type="button" class="tira" aria-label="Retirar ' + esc(e.nome) + ' desta ordem" data-acao="retirar-uso" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-etapa="' + id + '">×</button></span>';
    }).join(" ");
    const faltam = m.etapas.filter(function (e) { return mc.entradas.indexOf(e.id) < 0; });
    const add = faltam.length
      ? '<select class="slot mais" aria-label="Acrescentar Etapa a ' + esc(mc.codigo) + '" data-acao="add-entrada" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="' + kk + 'add"><option value="">+ Etapa</option>' +
        faltam.map(function (e) { return '<option value="' + e.id + '">' + esc(e.nome) + "</option>"; }).join("") + "</select>"
      : "";
    const destinos = [["nenhuma", "ficam classificados para as vagas"]].concat(
      m.etapas.map(function (e, i) {
        const circular = mc.entradas.indexOf(e.id) >= 0;
        return [e.id, "seguem para a Etapa “" + e.nome + "”" + (circular ? " (não: esta ordem usa a nota dela)" : i <= pos ? " (que acontece antes)" : ""), circular];
      })
    );
    let frase = "<p><strong>" + numero + "</strong> <span class=\"slot-texto\">" + esc(mc.nome) + "</span> (" + esc(mc.codigo) + "). ";
    if (pontuadas.length >= 2) {
      frase += "A ordem segue a " + sel(k + "divide", kk + "div", [["sim", "média ponderada"], ["nao", "soma ponderada"]], mc.divide ? "sim" : "nao", "média ou soma") + " das notas em ";
    } else {
      frase += "A ordem segue a nota em ";
    }
    frase += chips + " " + add + ". ";
    if (c.tipo === "nao") {
      frase += "Esta ordem não corta ninguém.";
    } else {
      frase += "Os primeiros " + sel(k + "corte.tipo", kk + "tipo", [["fixo", "em número de"], ["quadro", "em número igual ao das vagas (" + p.vagas + ")"]], c.tipo, "quantos") + " " +
        (c.tipo === "fixo" ? '<input type="number" min="1" class="curto slot' + (c.alvo ? "" : " vazio") + '" aria-label="Quantos" data-b="' + k + 'corte.alvo" data-k="' + kk + 'alvo" value="' + (c.alvo || "") + '">' : "") +
        (c.tipo === "fixo" ? ", mais " + '<input type="number" min="0" class="curto slot" aria-label="Suplentes" data-b="' + k + 'corte.suplentes" data-k="' + kk + 'sup" value="' + (c.suplentes || 0) + '"> suplentes,' : "") + " " +
        sel(k + "corte.destino", kk + "dest", destinos, c.destino, "o que acontece com eles") + "; " +
        sel(k + "corte.empate", kk + "emp", [["todos", "havendo empate na última posição, passam todos os empatados"], ["para", "havendo empate na última posição, esse número não é ultrapassado"]], c.empate, "e se houver empate") + ". " +
        sel(k + "corte.continuacao", kk + "cont", [["sim", "Depois, poderão ser chamados outros candidatos, seguindo a mesma ordem"], ["nao", "Não serão chamados candidatos além desses"]], c.continuacao, "e se alguém não assumir") + ".";
    }
    frase += "</p>";
    if (mc.criterios.length || c.destino === "nenhuma") {
      const temData = p.fatos.some(function (f) { return f.tipo === "data"; });
      const itens = mc.criterios.map(function (cr, i) {
        const val = cr.tipo === "pontuacao" ? "pont:" + (cr.alvo || "") : cr.tipo === "menor_fato" ? "velho" : cr.tipo === "maior_fato" ? "novo" : "";
        const opts = m.etapas.filter(function (e) { return e.forma === "nota"; }).map(function (e) { return ["pont:" + e.id, "a maior nota na " + e.nome]; })
          .concat([["velho", "o candidato mais velho" + (temData ? "" : " (declara a data de nascimento)")], ["novo", "o candidato mais novo" + (temData ? "" : " (declara a data de nascimento)")]]);
        return "<li>" + String.fromCharCode(97 + i) + ") " +
          '<select class="slot' + (val ? "" : " vazio") + '" aria-label="Critério ' + (i + 1) + '" data-acao="criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-i="' + i + '" data-k="tx-crit:' + mc.id + ":" + i + '">' +
          (val ? "" : '<option value="" selected>[escolha o critério]</option>') +
          opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === val ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("") + "</select>" +
          "; " + sel("crit:" + p.id + ":" + mc.id + ":" + i + ":ausente", "tx-crit-aus:" + mc.id + ":" + i, [["ultimo", "quem não tiver o valor fica por último"], ["naoaplica", "se faltar a alguém do grupo, o critério não se aplica"]], cr.ausente, "e se faltar o valor") +
          ' <button type="button" class="tira" aria-label="Retirar o critério ' + (i + 1) + '" data-acao="rm-criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-i="' + i + '">×</button></li>';
      }).join("");
      frase += "<p>Persistindo o empate, terá preferência, sucessivamente:</p><ol class=\"criterios-texto sem-marca\">" + itens +
        '<li><button type="button" class="link" data-acao="add-criterio" data-perfil="' + p.id + '" data-marco="' + mc.id + '" data-k="tx-addcrit:' + mc.id + '">+ outro critério</button></li></ol>';
    }
    const ds = diag.filter(function (d) { return d.alvo && d.alvo.tipo === "marco" && d.alvo.id === mc.id && d.perfil === p.id; });
    const grava = {
      code: mc.codigo, orderProduction: "POR_PONTUACAO", stages: mc.entradas,
      operation: mc.divide ? "MEDIA_PONDERADA" : "SOMA_PONDERADA", normalization: "NENHUMA",
      cutRule: c.tipo === "nao" ? null : { targetKind: c.tipo === "fixo" ? "FIXED" : c.tipo === "quadro" ? "FROM_VACANCY_TABLE" : null, targetCount: c.alvo, surplusCount: c.suplentes,
        tieOutcome: c.empate === "todos" ? "ADMITS_SURPLUS" : c.empate === "para" ? "STRICT" : null,
        governedStageId: c.destino === "nenhuma" ? "NONE" : c.destino, continuation: c.continuacao === "sim" ? "ALLOWED" : c.continuacao === "nao" ? "NONE" : null },
      criteria: mc.criterios.map(function (cr, i) {
        return { order: i + 1, type: cr.tipo === "pontuacao" ? "MAIOR_PONTUACAO_NA_ETAPA" : cr.tipo === "menor_fato" ? "MENOR_VALOR_DE_FATO" : cr.tipo === "maior_fato" ? "MAIOR_VALOR_DE_FATO" : null, target: cr.alvo, whenMissing: cr.ausente === "ultimo" ? "ULTIMO_NO_CRITERIO" : cr.ausente === "naoaplica" ? "CRITERIO_NAO_SE_APLICA" : null };
      }),
    };
    return '<div class="clausula" data-campo-marco="' + mc.id + '"><div class="corpo-clausula">' + frase + "</div>" +
      '<aside class="margem" aria-label="Notas sobre ' + esc(mc.codigo) + '">' + campoDiag(ds) +
      '<details><summary>o que esta frase grava</summary><pre>' + esc(JSON.stringify(grava, null, 1)) + "</pre></details>" +
      '<button type="button" class="link perigo" data-acao="rm-marco" data-perfil="' + p.id + '" data-marco="' + mc.id + '">retirar esta ordem</button></aside></div>';
  }

  // ------------------------------------------------------------------ controles do estudo

  function controles() {
    const cen = Object.keys(G.cenarios).map(function (id) {
      return '<button type="button" data-acao="cenario" data-id="' + id + '" data-k="cen:' + id + '" aria-pressed="' + (S.cenario === id) + '">' + esc(G.cenarios[id].rotulo) + "</button>";
    }).join("");
    return '<footer class="controles"><p><strong>Controles do estudo</strong> — não fazem parte da proposta.</p>' +
      '<div role="group" aria-label="Cenário">' + cen + "</div>" +
      '<div role="group" aria-label="Decisão D-1, marca classificatória"><span>Marca classificatória:</span>' +
      '<button type="button" data-acao="marca" data-id="derivada" data-k="marca:derivada" aria-pressed="' + (S.modoMarca === "derivada") + '">deduzida dos usos</button>' +
      '<button type="button" data-acao="marca" data-id="manual" data-k="marca:manual" aria-pressed="' + (S.modoMarca === "manual") + '">manual, como hoje</button></div></footer>';
  }

  // ------------------------------------------------------------------ render

  function render() {
    const diag = G.diagnostico(modeloVisivel(), S.modoMarca);
    const app = document.getElementById("app");
    const rolagem = window.scrollY;
    const corpo = S.modo === "trilho"
      ? '<div class="grade"><div class="col-trilho">' + trilho(diag) + '</div><aside class="inspetor" aria-labelledby="t-insp">' + inspetor(G.diagnostico(S.m, S.modoMarca)) + "</aside></div>"
      : texto(diag);
    app.innerHTML = cabecalho(G.diagnostico(S.m, S.modoMarca)) + '<main id="conteudo">' + corpo + "</main>" + controles();
    document.getElementById("anuncio").textContent = S.anuncio;
    S.anuncio = "";
    if (S.foco) {
      const el = app.querySelector('[data-k="' + S.foco.k + '"]');
      if (el) {
        el.focus({ preventScroll: true });
        if (S.foco.cursor != null && el.setSelectionRange && el.type === "text") el.setSelectionRange(S.foco.cursor, S.foco.cursor);
      } else if (S.foco.titulo) {
        const t = document.getElementById("t-insp");
        if (t) t.focus({ preventScroll: true });
      }
    }
    window.scrollTo(0, rolagem);
    requestAnimationFrame(desenharArcos);
    const u = new URL(location.href);
    u.searchParams.set("cenario", S.cenario);
    u.searchParams.set("modo", S.modo);
    u.searchParams.set("perfil", S.perfil);
    u.searchParams.set("marca", S.modoMarca);
    if (S.sel) u.searchParams.set("sel", S.sel.tipo + ":" + S.sel.id); else u.searchParams.delete("sel");
    history.replaceState(null, "", u);
  }

  // ------------------------------------------------------------------ edição

  /** `data-b`: "etapa:<id>:<campo>" | "marco:<perfil>:<id>:<campo.sub>" | "crit:<perfil>:<marco>:<i>:<campo>" */
  function aplicarBind(b, el) {
    const partes = b.split(":");
    let obj, campo;
    if (partes[0] === "etapa") {
      obj = G.etapa(S.m, partes[1]);
      campo = partes[2];
    } else if (partes[0] === "marco") {
      obj = acharMarco(S.m, partes[1], partes[2]);
      campo = partes[3];
    } else {
      obj = acharMarco(S.m, partes[1], partes[2]).criterios[+partes[3]];
      campo = partes[4];
    }
    let v;
    if (el.type === "checkbox") v = el.checked;
    else if (el.type === "number") v = el.value === "" ? null : Number(el.value);
    else v = el.value === "" ? null : el.value;
    if (campo === "divide") v = el.value === "sim";
    if (campo === "forma" && v === "decisao" && obj.forma !== "decisao") obj.eliminatoria = true; // padrão da 051
    const caminho = campo.split(".");
    let alvo = obj;
    while (caminho.length > 1) alvo = alvo[caminho.shift()];
    alvo[caminho[0]] = v;
    if (campo === "corte.destino" && v === "nenhuma" && !obj.corte.tipo) obj.corte.tipo = "quadro";
    if (campo === "corte.alvo" && v != null && obj.corte.tipo !== "fixo") obj.corte.tipo = "fixo";
  }

  function criarMarco(p, depoisDe, tipo) {
    const e = S.m.etapas[depoisDe];
    const seguinte = S.m.etapas[depoisDe + 1];
    const n = p.marcos.length + 1;
    const ehFinal = tipo === "final" || (!seguinte && tipo !== "corte");
    const mc = {
      id: novoId("m"),
      codigo: ehFinal ? "FINAL" : "SEL-" + n,
      nome: ehFinal ? "Classificação final" : seguinte ? "Seleção para " + seguinte.nome.toLowerCase() : "Seleção " + n,
      entradas: e && e.forma === "nota" ? [e.id] : [],
      divide: true,
      corte: { tipo: null, alvo: null, suplentes: 0, empate: null, destino: ehFinal ? "nenhuma" : null, continuacao: null },
      criterios: [],
    };
    if (ehFinal) mc.corte.tipo = "quadro";
    p.marcos.push(mc);
    return mc;
  }

  document.addEventListener("click", function (ev) {
    const b = ev.target.closest("[data-acao]");
    if (!b || b.tagName === "SELECT" || (b.tagName === "INPUT" && b.type !== "button")) return;
    const a = b.dataset.acao;
    const p = perfilAtivo();
    S.foco = b.dataset.k ? { k: b.dataset.k } : null;
    if (a === "perfil") { S.perfil = b.dataset.id; S.sel = null; }
    else if (a === "modo") S.modo = b.dataset.id;
    else if (a === "cenario") { carregar(b.dataset.id); S.sel = null; }
    else if (a === "marca") S.modoMarca = b.dataset.id;
    else if (a === "sel") { S.sel = { tipo: b.dataset.tipo, id: b.dataset.id }; S.foco = { titulo: true }; }
    else if (a === "desselecionar") { S.sel = null; S.foco = { titulo: true }; }
    else if (a === "novo-marco") {
      const mc = criarMarco(p, +b.dataset.depois, null);
      S.sel = { tipo: "marco", id: mc.id };
      S.foco = { titulo: true };
      S.anuncio = "Nova ordem criada depois de " + S.m.etapas[+b.dataset.depois].nome + ". Responda o que acontece depois dela.";
    } else if (a === "novo-marco-texto") {
      const pp = S.m.perfis.find(function (x) { return x.id === b.dataset.perfil; });
      criarMarco(pp, 0, b.dataset.tipo);
      S.anuncio = "Cláusula acrescentada ao Perfil " + pp.codigo + ".";
    } else if (a === "add-criterio") {
      acharMarco(S.m, b.dataset.perfil, b.dataset.marco).criterios.push({ tipo: null, alvo: null, ausente: null });
    } else if (a === "rm-criterio") {
      acharMarco(S.m, b.dataset.perfil, b.dataset.marco).criterios.splice(+b.dataset.i, 1);
    } else if (a === "rm-marco") {
      const pp = S.m.perfis.find(function (x) { return x.id === b.dataset.perfil; });
      pp.marcos = pp.marcos.filter(function (x) { return x.id !== b.dataset.marco; });
      S.sel = null;
      S.foco = { titulo: true };
    } else if (a === "retirar-uso") {
      const mc = acharMarco(S.m, b.dataset.perfil, b.dataset.marco);
      mc.entradas = mc.entradas.filter(function (x) { return x !== b.dataset.etapa; });
    } else if (a === "mover") {
      const depois = G.clonar(S.m);
      const i = G.indice(depois, b.dataset.id);
      const j = i + +b.dataset.dir;
      const [e] = depois.etapas.splice(i, 1);
      depois.etapas.splice(j, 0, e);
      S.pendente = { id: b.dataset.id, dir: +b.dataset.dir, depois };
      S.foco = { titulo: true };
    } else if (a === "confirmar-mover") {
      S.m = S.pendente.depois;
      S.pendente = null;
      S.anuncio = "Nova ordem das Etapas confirmada.";
      S.foco = { titulo: true };
    } else if (a === "cancelar-mover") {
      S.pendente = null;
      S.foco = { titulo: true };
    } else if (a === "ir") {
      const alvo = document.querySelector('[data-campo="' + b.dataset.campo + '"]');
      if (alvo) {
        const foc = alvo.matches("input,select") ? alvo : alvo.querySelector("input,select,button");
        alvo.scrollIntoView({ block: "center" });
        if (foc) foc.focus();
      }
      return;
    } else return;
    render();
  });

  function aoMudar(ev) {
    const el = ev.target;
    if (!(el instanceof HTMLElement)) return;
    S.foco = el.dataset.k ? { k: el.dataset.k, cursor: el.selectionStart } : null;
    const a = el.dataset.acao;
    if (el.dataset.b) aplicarBind(el.dataset.b, el);
    else if (a === "entrada") {
      const mc = acharMarco(S.m, el.dataset.perfil, el.dataset.marco);
      const antes = G.posicao(S.m, mc);
      if (el.checked) mc.entradas.push(el.value); else mc.entradas = mc.entradas.filter(function (x) { return x !== el.value; });
      mc.entradas.sort(function (x, y) { return G.indice(S.m, x) - G.indice(S.m, y); });
      const depois = G.posicao(S.m, mc);
      if (antes !== depois && depois >= 0) S.anuncio = "A ordem " + mc.codigo + " passou para depois de " + S.m.etapas[depois].nome + ", a última Etapa que ela usa.";
    } else if (a === "add-entrada") {
      if (!el.value) return;
      const mc = acharMarco(S.m, el.dataset.perfil, el.dataset.marco);
      mc.entradas.push(el.value);
      mc.entradas.sort(function (x, y) { return G.indice(S.m, x) - G.indice(S.m, y); });
    } else if (a === "depois") {
      const mc = acharMarco(S.m, el.dataset.perfil, el.dataset.marco);
      const pos = G.posicao(S.m, mc);
      if (el.value === "final") { mc.corte.destino = "nenhuma"; if (!mc.corte.tipo || mc.corte.tipo === "nao") mc.corte.tipo = "quadro"; }
      if (el.value === "nao") { mc.corte.tipo = "nao"; mc.corte.destino = null; }
      if (el.value === "segue") {
        if (mc.corte.tipo === "nao" || mc.corte.tipo === "quadro") mc.corte.tipo = null;
        const prox = S.m.etapas[pos + 1];
        mc.corte.destino = prox && mc.entradas.indexOf(prox.id) < 0 ? prox.id : "";
      }
    } else if (a === "criterio") {
      const p = S.m.perfis.find(function (x) { return x.id === el.dataset.perfil; });
      const cr = acharMarco(S.m, p.id, el.dataset.marco).criterios[+el.dataset.i];
      const v = el.value;
      if (v.indexOf("pont:") === 0) { cr.tipo = "pontuacao"; cr.alvo = v.slice(5); }
      else if (v === "velho" || v === "novo") {
        let f = p.fatos.find(function (x) { return x.tipo === "data"; });
        if (!f) {
          f = { id: novoId("fato"), codigo: "NASC", rotulo: "Data de nascimento", tipo: "data" };
          p.fatos.push(f);
          S.anuncio = "Declarado o fato “Data de nascimento” no Perfil " + p.codigo + ". A inscrição passará a pedi-lo.";
        }
        cr.tipo = v === "velho" ? "menor_fato" : "maior_fato";
        cr.alvo = f.id;
      }
    } else if (a === "anteriores") S.anteriores = el.checked;
    else return;
    render();
  }
  // Texto e número atualizam ao sair do campo: re-desenhar a cada tecla moveria o cursor.
  document.addEventListener("change", aoMudar);
  window.addEventListener("resize", function () { requestAnimationFrame(desenharArcos); });

  // Passar o ponteiro ou o foco por uma ordem acende as linhas dela, sem redesenhar a página.
  function realcar(ev) {
    const c = ev.target.closest && ev.target.closest(".cartao-marco");
    const id = c ? c.dataset.id : null;
    if (id === S.realce) return;
    S.realce = id;
    desenharArcos();
  }
  document.addEventListener("mouseover", realcar);
  document.addEventListener("focusin", realcar);

  if (q.get("mover")) {
    const [id, dir] = q.get("mover").split(":");
    const depois = G.clonar(S.m);
    const i = G.indice(depois, id);
    const [e] = depois.etapas.splice(i, 1);
    depois.etapas.splice(i + (dir === "up" ? -1 : 1), 0, e);
    S.pendente = { id, dir: dir === "up" ? -1 : 1, depois };
  }
  render();
  window.GPS2.estado = S;
})();
