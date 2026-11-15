() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' && !(s.clipPath !== 'none' && r.width <= 2); };
  const main = document.querySelector('main'); const doc = document.documentElement; if (!main) return null;
  const mr = main.getBoundingClientRect(); const ms = getComputedStyle(main);
  const L = mr.left + parseFloat(ms.paddingLeft), R = mr.right - parseFloat(ms.paddingRight), W = R - L;
  const folhas = [];
  const w = document.createTreeWalker(main, NodeFilter.SHOW_TEXT); let n; const rg = document.createRange();
  while ((n = w.nextNode())) { if (!n.nodeValue.trim()) continue; const e = n.parentElement; if (!e || !vis(e)) continue; rg.selectNodeContents(n); for (const r of rg.getClientRects()) if (r.width > 1) folhas.push([r.left, r.right, r.top + scrollY, r.bottom + scrollY]); }
  for (const e of main.querySelectorAll('input:not([type=hidden]), select, textarea, button, img, svg, canvas, iframe, object, embed')) { if (!vis(e)) continue; const r = e.getBoundingClientRect(); folhas.push([r.left, r.right, r.top + scrollY, r.bottom + scrollY]); }
  if (!folhas.length) return { vazio: true };
  const minL = Math.min(...folhas.map(f => f[0])), maxR = Math.max(...folhas.map(f => f[1]));
  const top = Math.min(...folhas.map(f => f[2])), bot = Math.max(...folhas.map(f => f[3])); const H = Math.max(bot - top, 1);
  const cobertura = (x0) => { const iv = folhas.filter(f => f[1] > x0).map(f => [f[2], f[3]]).sort((a, b) => a[0] - b[0]); let tot = 0, cur = null; for (const [a, b] of iv) { if (!cur) cur = [a, b]; else if (a <= cur[1] + 8) cur[1] = Math.max(cur[1], b); else { tot += cur[1] - cur[0]; cur = [a, b]; } } if (cur) tot += cur[1] - cur[0]; return Math.round(100 * tot / H); };
  // medida de linha: caracteres por linha dos blocos de prosa
  const medidas = [...main.querySelectorAll('p, li, dd, td, .sub, .ajuda, .nota, .explicacao')].filter(vis).filter(e => e.innerText && e.innerText.length > 160 && !e.querySelector('p, ul, table, input, select')).map(e => { const s = getComputedStyle(e); const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.5; const linhas = Math.max(1, Math.round(e.getBoundingClientRect().height / lh)); return Math.round(e.innerText.length / linhas); });
  const lateral = document.querySelector('.barra-lateral'); const lr = lateral ? lateral.getBoundingClientRect() : null;
  return { vw: innerWidth, scrollW: doc.scrollWidth, overflowX: doc.scrollWidth > doc.clientWidth + 1, mainX: Math.round(mr.left), mainW: Math.round(mr.width), margemEsq: Math.round(minL), margemDir: Math.round(innerWidth - maxR), tintaPct: Math.round(100 * (maxR - minL) / W), metadeDireita: cobertura(L + W / 2), tercoDireito: cobertura(L + 2 * W / 3), alturaConteudo: Math.round(H), scrollH: doc.scrollHeight,
    cplMax: medidas.length ? Math.max(...medidas) : null, cplMed: medidas.length ? Math.round(medidas.reduce((a, b) => a + b, 0) / medidas.length) : null, nProsa: medidas.length,
    lateral: lr ? Math.round(lr.width) + 'x' + Math.round(lr.height) : null,
    transbordam: [...main.querySelectorAll('*')].filter(vis).filter(e => e.getBoundingClientRect().right > innerWidth + 2 && !e.closest('.tabela-rolavel, .rolagem, [class*=rolav], [class*=moldura]')).slice(0, 5).map(e => e.tagName.toLowerCase() + '.' + String(e.className).slice(0, 40)),
    moldurasRolando: [...main.querySelectorAll('.tabela-rolavel, .rolagem, [class*=rolav], [class*=moldura]')].filter(vis).filter(e => e.scrollWidth > e.clientWidth + 2).length };
}
