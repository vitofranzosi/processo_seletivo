() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const px = v => Math.round(parseFloat(v) * 100) / 100;
  const main = document.querySelector('main');
  const doc = document.documentElement;
  const out = { url: location.pathname + location.search, title: document.title, vw: innerWidth, vh: innerHeight,
    scrollW: doc.scrollWidth, scrollH: doc.scrollHeight, overflowX: doc.scrollWidth > doc.clientWidth + 1 };
  out.shell = document.querySelector('.shell') ? (document.querySelector('.shell-barra-no-topo') ? 'barra-no-topo' : 'lateral') : (document.querySelector('header.topo') ? 'topo' : 'nenhum');
  out.bodyClass = document.body.className; out.mainClass = main ? main.className : null;
  out.folhas = [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.getAttribute('href').replace(/\?.*/, '').replace(/^\/static\//, ''));
  if (main) { const r = main.getBoundingClientRect(); const s = getComputedStyle(main);
    out.main = { x: Math.round(r.x), w: Math.round(r.width), maxW: s.maxWidth, pad: s.paddingLeft + '/' + s.paddingTop };
    // extensão real do conteúdo: maior borda direita entre os descendentes visíveis com texto ou controle
    let maxRight = 0, minLeft = 1e9; const filhos = [];
    for (const c of main.children) { if (!vis(c)) continue; const cr = c.getBoundingClientRect(); filhos.push({ tag: c.tagName.toLowerCase() + (c.className ? '.' + String(c.className).trim().split(/\s+/).join('.') : ''), w: Math.round(cr.width), h: Math.round(cr.height), mw: getComputedStyle(c).maxWidth }); maxRight = Math.max(maxRight, cr.right); minLeft = Math.min(minLeft, cr.left); }
    out.filhosDoMain = filhos.slice(0, 40);
    const innerW = r.width - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
    out.usoHorizontal = innerW > 0 ? Math.round(100 * (maxRight - minLeft) / innerW) : null;
    // área pintada: fração da largura interna coberta, ponderada pela altura dos filhos
    let area = 0, total = 0; for (const c of main.children) { if (!vis(c)) continue; const cr = c.getBoundingClientRect(); area += cr.width * cr.height; total += innerW * cr.height; }
    out.preenchimento = total ? Math.round(100 * area / total) : null;
  }
  const h1s = [...document.querySelectorAll('h1')].filter(vis);
  out.h1 = h1s.map(h => ({ t: h.innerText.trim().slice(0, 90), fs: px(getComputedStyle(h).fontSize), fw: getComputedStyle(h).fontWeight, top: Math.round(h.getBoundingClientRect().top + scrollY), dentroDoMain: !!h.closest('main') }));
  out.h2 = [...new Set([...document.querySelectorAll('main h2')].filter(vis).map(h => px(getComputedStyle(h).fontSize)))];
  out.h3 = [...new Set([...document.querySelectorAll('main h3')].filter(vis).map(h => px(getComputedStyle(h).fontSize)))];
  out.nH2 = document.querySelectorAll('main h2').length;
  out.caminho = !!document.querySelector('.caminho-da-secao, nav[aria-label*="aminho"], .migalhas, .trilha-de-navegacao');
  out.sub = !!document.querySelector('main .sub');
  const assin = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return { cls: (e.tagName.toLowerCase() + '.' + String(e.className || '').trim().split(/\s+/).filter(Boolean).sort().join('.')).replace(/\.$/, ''), h: Math.round(r.height), fs: px(s.fontSize), pad: s.paddingTop + ' ' + s.paddingRight, raio: s.borderTopLeftRadius, bg: s.backgroundColor, cor: s.color, borda: s.borderTopWidth + ' ' + s.borderTopColor, fw: s.fontWeight }; };
  const agrupa = (els) => { const m = {}; for (const e of els) { if (!vis(e)) continue; const a = assin(e); const k = JSON.stringify(a); m[k] = (m[k] || 0) + 1; } return Object.entries(m).map(([k, n]) => ({ ...JSON.parse(k), n })).sort((a, b) => b.n - a.n).slice(0, 25); };
  const escopo = main || document.body;
  out.botoes = agrupa(escopo.querySelectorAll('button, input[type=submit], a.botao, a.acao, .botao, .acao'));
  out.campos = agrupa(escopo.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=file]), select, textarea'));
  out.nCampos = escopo.querySelectorAll('input:not([type=hidden]), select, textarea').length;
  out.camposLarg = [...escopo.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=file]), select, textarea')].filter(vis).map(e => Math.round(e.getBoundingClientRect().width)).sort((a, b) => a - b);
  out.selos = agrupa(escopo.querySelectorAll('.situacao, [class*="selo"], [class*="etiqueta"], [class*="marca-"], .codigo, [class*="chip"], [class*="badge"]'));
  out.avisos = agrupa(escopo.querySelectorAll('.aviso, .imutavel, .sucesso, .erro, .bastao, [role=alert], [role=status], [class*="alerta"], [class*="aviso"]'));
  // caixas: elementos com borda e fundo próprios (cartões, painéis)
  const caixas = {}; let nCaixas = 0;
  for (const e of escopo.querySelectorAll('section, article, div, li, fieldset, details, aside, form, ul, ol, dl')) { if (!vis(e)) continue; const s = getComputedStyle(e); const r = e.getBoundingClientRect(); if (r.width < 120 || r.height < 40) continue; const temBorda = parseFloat(s.borderTopWidth) > 0 && parseFloat(s.borderLeftWidth) > 0 && s.borderTopStyle !== 'none'; if (!temBorda) continue; nCaixas++; const k = [s.borderTopLeftRadius, s.paddingTop + ' ' + s.paddingLeft, s.backgroundColor, s.borderTopColor, s.borderTopStyle, s.boxShadow === 'none' ? '' : 'sombra'].join(' | '); (caixas[k] = caixas[k] || { n: 0, ex: [] }).n++; if (caixas[k].ex.length < 3) caixas[k].ex.push(e.tagName.toLowerCase() + '.' + String(e.className).trim().split(/\s+/).join('.')); }
  out.caixas = Object.entries(caixas).map(([k, v]) => ({ k, ...v })).sort((a, b) => b.n - a.n).slice(0, 20); out.nCaixas = nCaixas;
  // caixa dentro de caixa (profundidade)
  let prof = 0; for (const e of escopo.querySelectorAll('*')) { if (!vis(e)) continue; let d = 0, p = e; while (p && p !== escopo) { const s = getComputedStyle(p); if (parseFloat(s.borderTopWidth) > 0 && parseFloat(s.borderLeftWidth) > 0 && p.getBoundingClientRect().width > 120 && !['INPUT','SELECT','TEXTAREA','BUTTON','A','TD','TH','TABLE'].includes(p.tagName)) d++; p = p.parentElement; } if (d > prof) prof = d; }
  out.profundidadeDeCaixa = prof;
  // tabelas
  out.tabelas = [...escopo.querySelectorAll('table')].filter(vis).map(t => { const r = t.getBoundingClientRect(); const td = t.querySelector('tbody td, tbody th'); const th = t.querySelector('thead th'); const s = td ? getComputedStyle(td) : null; const tr = t.querySelector('tbody tr'); const rol = t.closest('.tabela-rolavel, .rolagem, [class*="rolav"], [class*="moldura"]'); return { cls: t.className, w: Math.round(r.width), cols: th ? th.parentElement.children.length : (tr ? tr.children.length : 0), linhas: t.querySelectorAll('tbody tr').length, tdPad: s ? s.paddingTop + ' ' + s.paddingLeft : null, tdFs: s ? px(s.fontSize) : null, thFs: th ? px(getComputedStyle(th).fontSize) : null, thTT: th ? getComputedStyle(th).textTransform : null, linhaH: tr ? Math.round(tr.getBoundingClientRect().height) : null, moldura: rol ? String(rol.className) : null, pai: t.parentElement.tagName.toLowerCase() + '.' + String(t.parentElement.className), transborda: rol ? rol.scrollWidth > rol.clientWidth + 1 : r.right > innerWidth + 1 }; });
  // tipografia: tamanhos por volume de texto; cores de texto
  const fs = {}, cores = {}, familias = {}; const w = document.createTreeWalker(escopo, NodeFilter.SHOW_TEXT); let n; let chars = 0;
  const lum = c => { const m = c.match(/[\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return { l: .2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]), a: m.length > 3 ? m[3] : 1 }; };
  const fundoDe = e => { let p = e; while (p) { const b = getComputedStyle(p).backgroundColor; const L = lum(b); if (L.a > .95) return b; p = p.parentElement; } return 'rgb(255, 255, 255)'; };
  const baixo = {}; let nBaixo = 0;
  while ((n = w.nextNode())) { const t = n.nodeValue.trim(); if (!t) continue; const e = n.parentElement; if (!e || !vis(e)) continue; const s = getComputedStyle(e); if (s.clipPath !== 'none' && e.getBoundingClientRect().width <= 2) continue; const k = px(s.fontSize); fs[k] = (fs[k] || 0) + t.length; cores[s.color] = (cores[s.color] || 0) + t.length; chars += t.length; const fam = s.fontFamily.split(',')[0].replace(/"/g, ''); familias[fam] = (familias[fam] || 0) + t.length;
    const a = lum(s.color), b = lum(fundoDe(e)); if (a.a > .95) { const c = (Math.max(a.l, b.l) + .05) / (Math.min(a.l, b.l) + .05); const grande = k >= 24 || (k >= 18.66 && parseInt(s.fontWeight) >= 700); if (c < (grande ? 3 : 4.5)) { nBaixo++; const kk = s.color + ' sobre ' + fundoDe(e) + ' = ' + c.toFixed(2); (baixo[kk] = baixo[kk] || []).length < 2 && baixo[kk].push(t.slice(0, 40)); } } }
  out.tamanhosDeFonte = Object.entries(fs).map(([k, v]) => [parseFloat(k), v]).sort((a, b) => b[1] - a[1]); out.chars = chars;
  out.coresDeTexto = Object.entries(cores).sort((a, b) => b[1] - a[1]).slice(0, 12); out.familias = familias;
  out.contrasteBaixo = { n: nBaixo, ex: Object.entries(baixo).slice(0, 8) };
  // medida de linha: parágrafos longos demais
  out.linhasLongas = [...escopo.querySelectorAll('p, li, dd, .sub, .ajuda, .nota')].filter(vis).filter(e => e.children.length < 3 && e.innerText.length > 140).map(e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return Math.round(r.width / (parseFloat(s.fontSize) * 0.5)); }).filter(c => c > 95).length;
  // alvos interativos pequenos (WCAG 2.2 2.5.8: 24x24)
  const alvos = [...document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button]')].filter(vis);
  const peq = alvos.filter(e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); if (e.tagName === 'A' && s.display === 'inline' ) return false; return r.width < 24 || r.height < 24; });
  out.alvos = { total: alvos.length, pequenos: peq.length, ex: peq.slice(0, 6).map(e => e.tagName.toLowerCase() + '.' + String(e.className) + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)) };
  out.semRotulo = [...escopo.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]), select, textarea')].filter(vis).filter(e => !(e.labels && e.labels.length) && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby') && !e.getAttribute('title')).length;
  out.dialogos = document.querySelectorAll('dialog, [role=dialog]').length; out.details = escopo.querySelectorAll('details').length;
  out.acoesNoTopo = main ? [...main.querySelectorAll('a.botao, button.botao, .botao')].filter(vis).filter(e => e.getBoundingClientRect().top + scrollY < 400).length : 0;
  out.nBotoesCheios = [...escopo.querySelectorAll('.botao:not(.secundario):not(.desabilitado)')].filter(vis).length;
  out.links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => h && !h.startsWith('#') && !h.startsWith('mailto:') && !h.startsWith('http'));
  out.linksAbs = [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin)).map(h => h.slice(location.origin.length));
  out.formsGet = [...document.querySelectorAll('form')].filter(f => (f.method || 'get').toLowerCase() === 'get').map(f => f.getAttribute('action') || '');
  out.textoDoMain = main ? main.innerText.slice(0, 600) : '';
  return out;
}
