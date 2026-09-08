// Driver CDP mínimo para capturar as telas do piloto. Sem dependências.
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
const PROFILE = '/tmp/ps-manual-s00-chrome';

export async function abrir({ limpar = false, perfil = PROFILE } = {}) {
  if (limpar) rmSync(perfil, { recursive: true, force: true });
  mkdirSync(perfil, { recursive: true });
  const proc = spawn(CHROME, [
    '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2',
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${perfil}`,
    '--no-first-run', '--no-default-browser-check', 'about:blank',
  ], { stdio: 'ignore' });

  let alvo = null;
  for (let i = 0; i < 60 && !alvo; i++) {
    await new Promise(r => setTimeout(r, 300));
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      alvo = (await r.json()).find(t => t.type === 'page');
    } catch {}
  }
  if (!alvo) throw new Error('Chrome não subiu');

  const ws = new WebSocket(alvo.webSocketDebuggerUrl);
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = no; });
  let id = 0;
  const pendentes = new Map();
  const eventos = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pendentes.has(m.id)) {
      const { ok, no } = pendentes.get(m.id); pendentes.delete(m.id);
      m.error ? no(new Error(m.error.message)) : ok(m.result);
    } else if (m.method) eventos.push(m);
  };
  const send = (method, params = {}) => new Promise((ok, no) => {
    const meu = ++id; pendentes.set(meu, { ok, no });
    ws.send(JSON.stringify({ id: meu, method, params }));
  });

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');

  const api = {
    send,
    async viewport(width, height, mobile = false) {
      await send('Emulation.setDeviceMetricsOverride', {
        width, height, deviceScaleFactor: 2, mobile,
        screenWidth: width, screenHeight: height,
      });
      if (mobile) await send('Emulation.setUserAgentOverride', {
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
      });
    },
    async ir(url) {
      await send('Page.navigate', { url });
      await api.espera();
    },
    async espera(ms = 700) { await new Promise(r => setTimeout(r, ms)); },
    async js(expr) {
      const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails.text));
      return r.result.value;
    },
    async clicar(seletor) {
      const achou = await api.js(`(() => { const e = document.querySelector(${JSON.stringify(seletor)}); if(!e) return false; e.click(); return true; })()`);
      if (!achou) throw new Error(`não achei ${seletor}`);
      await api.espera(900);
    },
    async clicarTexto(texto, tag = '*') {
      const achou = await api.js(`(() => {
        const alvos = [...document.querySelectorAll('a, button, input[type=submit], summary')];
        const e = alvos.find(x => (x.innerText || x.value || '').trim().includes(${JSON.stringify(texto)}));
        if (!e) return false; e.click(); return true; })()`);
      if (!achou) throw new Error(`não achei texto "${texto}"`);
      await api.espera(900);
    },
    async preencher(seletor, valor) {
      await api.js(`(() => { const e = document.querySelector(${JSON.stringify(seletor)}); e.value = ${JSON.stringify(valor)}; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); })()`);
    },
    async foto(caminho, { clip = null, inteira = false } = {}) {
      const params = { format: 'png', captureBeyondViewport: inteira };
      if (clip) params.clip = { ...clip, scale: 2 };
      else if (inteira) {
        const m = await send('Page.getLayoutMetrics');
        params.clip = { x: 0, y: 0, width: m.cssContentSize.width, height: m.cssContentSize.height, scale: 2 };
      }
      const { data } = await send('Page.captureScreenshot', params);
      mkdirSync(caminho.replace(/\/[^/]+$/, ''), { recursive: true });
      writeFileSync(caminho, Buffer.from(data, 'base64'));
      console.log('  →', caminho.split('/').pop());
    },
    async anexar(seletorForm, caminhoArquivo) {
      const doc = await send('DOM.getDocument');
      const { nodeId } = await send('DOM.querySelector', { nodeId: doc.root.nodeId, selector: seletorForm });
      if (!nodeId) throw new Error('não achei input de arquivo ' + seletorForm);
      await send('DOM.setFileInputFiles', { nodeId, files: [caminhoArquivo] });
      await api.espera(200);
    },
    // Recorte com faixa de contexto acima, conforme §G.6 do documento de arquitetura.
    async recorte(caminho, { de, ate = null, contexto = 56, margem = 16, larguraMax = null, margemBaixo = null, alvos = [] } = {}) {
      const r = await api.js(
        "(() => { const a = document.querySelector(" + JSON.stringify(de) + ");" +
        " const b = " + (ate ? "document.querySelector(" + JSON.stringify(ate) + ")" : "a") + ";" +
        " if (!a || !b) return null;" +
        " const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();" +
        " return { top: ra.top + scrollY, bottom: rb.bottom + scrollY," +
        " left: Math.min(ra.left, rb.left) + scrollX, right: Math.max(ra.right, rb.right) + scrollX }; })()"
      );
      if (!r) throw new Error('recorte: seletor nao encontrado ' + de);
      const m = await send('Page.getLayoutMetrics');
      const x = Math.max(0, r.left - margem);
      const y = Math.max(0, r.top - contexto);
      let width = (r.right - r.left) + margem * 2;
      width = Math.min(width, m.cssContentSize.width - x);
      if (larguraMax) width = Math.min(width, larguraMax);
      const clip = { x, y, width, height: (r.bottom + (margemBaixo ?? margem)) - y };
      await api.foto(caminho, { clip, inteira: true });
      if (alvos.length) {
        const caixas = await api.js(
          "(" + JSON.stringify(alvos.map(a => a.sel)) + ").map(function(s){" +
          " var e = document.querySelector(s); if (!e) return null;" +
          " var r = e.getBoundingClientRect();" +
          " return [r.left + scrollX, r.top + scrollY, r.width, r.height]; })"
        );
        const pct = caixas.map((c, i) => c === null ? null : [
          +(((c[0] - clip.x - 4) / clip.width) * 100).toFixed(1),
          +(((c[1] - clip.y - 4) / clip.height) * 100).toFixed(1),
          +(((c[2] + 8) / clip.width) * 100).toFixed(1),
          +(((c[3] + 8) / clip.height) * 100).toFixed(1),
          alvos[i].n ?? null,
        ]);
        console.log("     alvos:", JSON.stringify(pct));
      }
    },
    async caixa(seletor) {
      return api.js(`(() => { const e = document.querySelector(${JSON.stringify(seletor)}); if(!e) return null; const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()`);
    },
    async texto() { return api.js('document.body.innerText'); },
    fechar() { ws.close(); proc.kill(); },
  };
  return api;
}
