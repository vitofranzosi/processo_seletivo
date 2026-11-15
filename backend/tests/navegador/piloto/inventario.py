# ruff: noqa: E501 — o JavaScript das constantes é avaliado no navegador, e quebrá-lo em
# concatenações de 100 colunas o deixaria ilegível sem ganho nenhum.
"""O inventário de conteúdo de uma tela, lido no navegador (172, FR-7721, FR-7722).

É o que o aceite do piloto compara antes e depois: os blocos de texto, as quantidades com rótulo,
as associações, as ações e as duas ordens. O formato está em
`specs/172-piloto-do-design-system/contracts/inventario.md`.

**O bloco sai da estrutura, e não do CSS.** O primeiro desenho tomava o ancestral cujo `display` não
fosse `inline`, e o piloto muda `display` de propósito (o `.acao` vira `inline-flex`): o mesmo texto
viraria outro bloco, e a comparação acusaria diferença onde só há composição. Por isso o bloco é o
ancestral mais próximo com uma das etiquetas de `BLOCOS`, e o texto dele é só o que não pertence a um
bloco de dentro.

**O item da estrutura sai do que ele diz, e não da posição**: a seção pelo título que a rotula, o
Processo pelo título, o campo pelo rótulo, o formulário pelo botão. É o que deixa a comparação dizer
"o aviso continua no recorte dele" sem se importar com onde o recorte foi desenhado.

**A normalização é feita aqui**, antes de calcular o identificador do bloco: UUID, data e hora mudam
entre duas montagens do mesmo estado, e um identificador que os contivesse mudaria junto.
"""

INVENTARIO_JS = r"""
() => {
  const main = document.querySelector('main');
  if (!main) return null;
  const BLOCOS = new Set(['P','LI','DT','DD','H1','H2','H3','H4','H5','H6','TD','TH','LABEL','LEGEND',
    'SUMMARY','BUTTON','CAPTION','FIGCAPTION','DIV','SECTION','ARTICLE','HEADER','FOOTER','NAV',
    'ASIDE','FORM','FIELDSET','UL','OL','DL','TABLE','TR','BLOCKQUOTE','PRE','OPTION','MAIN']);
  const UUID = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi;
  const DATA_HORA = /\b\d{2}\/\d{2}\/\d{4}(?:,? (?:às )?\d{2}[:h]\d{2})?\b/g;
  const HORA = /\b\d{2}:\d{2}\b/g;
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim()
    .replace(UUID, '‹id›').replace(DATA_HORA, '‹data›').replace(HORA, '‹hora›');
  const CHAVES = new Set(['chave', 'chave_idempotencia', 'leitura', 'csrfmiddlewaretoken']);
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return (h >>> 0).toString(16); };

  const blocoDe = (no) => { let e = no.parentElement; while (e && e !== main && !BLOCOS.has(e.tagName)) e = e.parentElement; return e || main; };
  const visibilidade = (e) => {
    const fechado = e.closest('details:not([open])');
    if (fechado && !e.closest('summary')) return 'recolhido';
    return e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }) ? 'visivel' : 'escondido';
  };

  // O item da estrutura: o mais próximo de cada espécie, do bloco para fora, como caminho.
  const textoDoRotulo = (id) => { const r = id && document.getElementById(id); return r ? norm(r.innerText) : ''; };
  const itemDe = (e) => {
    const partes = [];
    for (let a = e.parentElement; a && a !== main; a = a.parentElement) {
      if (a.tagName === 'SECTION' && a.getAttribute('aria-labelledby')) partes.push('recorte:' + textoDoRotulo(a.getAttribute('aria-labelledby')));
      else if (a.tagName === 'ARTICLE') { const t = a.querySelector('h2, h3'); partes.push('processo:' + (t ? norm(t.innerText) : '')); }
      else if (a.tagName === 'FIELDSET') { const l = a.querySelector('legend'); partes.push('grupo:' + (l ? norm(l.innerText) : '')); }
      else if (a.tagName === 'DETAILS') { const s = a.querySelector('summary'); partes.push('recolhido:' + (s ? norm(s.innerText) : '')); }
      else if (a.tagName === 'FORM') { const b = a.querySelector('button[type=submit], button:not([type])'); partes.push('form:' + (b ? norm(b.innerText) : norm(a.getAttribute('action') || ''))); }
      else if (a.tagName === 'P' && a.classList.contains('campo')) { const l = a.querySelector('label'); partes.push('campo:' + (l ? norm(l.innerText) : '')); }
      else if (a.tagName === 'LI' && a.querySelector(':scope > form, :scope > a, :scope > strong')) { partes.push('item:' + hash(norm(a.innerText).slice(0, 80))); }
    }
    return partes.reverse().join(' > ') || 'pagina';
  };

  // Os blocos, na ordem do documento: o primeiro nó de texto de cada um decide a posição.
  const porElemento = new Map();
  const ordem = [];
  const andador = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
  for (let no = andador.nextNode(); no; no = andador.nextNode()) {
    if (!no.nodeValue.trim()) continue;
    if (no.parentElement.closest('script, style, template, noscript')) continue;
    const b = blocoDe(no);
    if (!porElemento.has(b)) { porElemento.set(b, []); ordem.push(b); }
    porElemento.get(b).push(no);
  }
  const ocorrencias = new Map();
  const blocos = ordem.map((e) => {
    const texto = norm(porElemento.get(e).map((n) => n.nodeValue).join(' '));
    const item = itemDe(e);
    const base = 'b:' + hash(texto + '|' + item);
    const n = (ocorrencias.get(base) || 0) + 1; ocorrencias.set(base, n);
    const r = e.getBoundingClientRect();
    return { id: base + ':' + n, texto, tag: e.tagName.toLowerCase(), classes: [...e.classList].sort(),
      visibilidade: visibilidade(e), item,
      caixa: [Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)],
      _el: e };
  }).filter((b) => b.texto);

  // As quantidades: cada número do bloco, com o texto do bloco sem os números como rótulo.
  const NUMERO = /\d+(?:[.,]\d+)*/g;
  const quantidades = [];
  for (const b of blocos) {
    const numeros = b.texto.match(NUMERO);
    if (!numeros) continue;
    const rotulo = norm(b.texto.replace(NUMERO, '#'));
    for (const numero of numeros) quantidades.push({ numero, rotulo, item: b.item });
  }
  // E os pares de indicador, em que o número e o rótulo são blocos irmãos.
  for (const li of main.querySelectorAll('ul.resumo > li')) {
    const forte = li.querySelector('strong');
    if (!forte) continue;
    quantidades.push({ numero: norm(forte.innerText), rotulo: norm(li.innerText.replace(forte.innerText, '')), item: itemDe(li), par: true });
  }

  // As ações: link, formulário e botão, com destino, método e campos.
  const caminho = (url) => { try { const u = new URL(url, location.href); return norm(decodeURIComponent(u.pathname + u.search)); } catch (_) { return norm(url); } };
  const acoes = [];
  for (const a of main.querySelectorAll('a[href]')) acoes.push({ tipo: 'link', rotulo: norm(a.innerText), destino: caminho(a.getAttribute('href')), item: itemDe(a) });
  for (const f of main.querySelectorAll('form')) {
    const campos = [...f.elements].filter((c) => c.name).map((c) => {
      const valor = (c.type === 'hidden' && !CHAVES.has(c.name)) ? '=' + norm(c.value) : '';
      return c.name + valor;
    }).sort();
    const botoes = [...f.querySelectorAll('button')].map((b) => norm(b.innerText));
    acoes.push({ tipo: 'form', rotulo: botoes.join(' | '), metodo: (f.getAttribute('method') || 'get').toLowerCase(),
      destino: caminho(f.getAttribute('action') || location.href), campos, item: itemDe(f) });
  }

  // A ordem visual: pelo topo, e na mesma linha (meia linha de tolerância) pela esquerda.
  const visiveis = blocos.filter((b) => b.visibilidade === 'visivel' && b.caixa[2] > 0 && b.caixa[3] > 0);
  const ordemVisual = [...visiveis].sort((x, y) => (Math.abs(x.caixa[1] - y.caixa[1]) <= 8 ? x.caixa[0] - y.caixa[0] : x.caixa[1] - y.caixa[1])).map((b) => b.id);

  // A linha mais longa de cada bloco de prosa, palavra a palavra pelos retângulos de cada uma.
  const NAO_PROSA = new Set(['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'BUTTON', 'TH', 'LABEL', 'OPTION', 'LEGEND', 'SUMMARY']);
  const linhas = [];
  const faixa = document.createRange();
  for (const b of visiveis) {
    if (NAO_PROSA.has(b._el.tagName) || b.texto.length < 40) continue;
    const porLinha = new Map();
    for (const no of porElemento.get(b._el)) {
      const texto = no.nodeValue;
      const re = /\S+/g; let m;
      while ((m = re.exec(texto))) {
        faixa.setStart(no, m.index); faixa.setEnd(no, m.index + m[0].length);
        const r = faixa.getClientRects()[0];
        if (!r || r.width === 0) continue;
        const chave = Math.round((r.top + scrollY) / 4);
        porLinha.set(chave, (porLinha.get(chave) || 0) + m[0].length + 1);
      }
    }
    // Duas linhas de topos vizinhos (dentro de 4 px) são a mesma linha com fontes diferentes.
    const chaves = [...porLinha.keys()].sort((x, y) => x - y);
    let maior = 0, atual = 0, anterior = null;
    for (const k of chaves) { if (anterior !== null && k - anterior <= 1) atual += porLinha.get(k); else atual = porLinha.get(k); maior = Math.max(maior, atual); anterior = k; }
    linhas.push({ bloco: b.id, maior_linha: Math.max(0, maior - 1) });
  }

  return {
    blocos: blocos.map(({ _el, ...resto }) => resto),
    quantidades,
    acoes,
    ordem_documento: blocos.map((b) => b.id),
    ordem_visual: ordemVisual,
    linhas,
    rolagem_horizontal: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  };
}
"""

# A dobra: a ação principal está acima dela, ou a tela diz que ela existe (FR-7731).
DOBRA_JS = r"""
(rotulo) => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const alvo = [...document.querySelectorAll('main button, main a')].find((e) => norm(e.innerText) === rotulo);
  if (!alvo) return { acao_principal: rotulo, achada: false };
  const r = alvo.getBoundingClientRect();
  return { acao_principal: rotulo, achada: true, acima: r.bottom <= innerHeight && r.top >= 0, topo: Math.round(r.top) };
}
"""

OUVIR_A_CSP = """
window.__violacoes = [];
document.addEventListener('securitypolicyviolation', (e) => {
  window.__violacoes.push(e.violatedDirective + ' ' + (e.blockedURI || 'inline'));
});
"""
