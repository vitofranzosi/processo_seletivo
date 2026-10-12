// Lê o rótulo de seção que os vídeos do Cefor mostram na barra lateral (rodada 4). Roda no console da página do
// vídeo no YouTube, com o vídeo carregado; não baixa, não recorta e não grava o vídeo. Não interpreta a Libras: só
// detecta onde a imagem da barra lateral muda, para que uma pessoa leia o rótulo naquele ponto.
//
// Uso: definir a região da barra (em pixels do quadro 1920x1080), amostrar, achar as mudanças e conferir cada uma
// com `fronteira`, que bissecciona entre dois instantes depois de carregar o trecho. Os intervalos que saem daqui são
// pontos observados, e não limites de corte.
//
// Vídeos do 19/2026 e do 46/2026: região [0, 360, 660, 480]. Vídeo do 28/2026 (barra mais estreita, rótulo com o
// título da seção): região [20, 380, 400, 500]; amostrar por reprodução acelerada (`amostrarTocando`), porque o salto
// devolve quadros desatualizados. Anúncios interrompem a reprodução: descartar as amostras capturadas durante eles.

const REGIAO = [0, 360, 660, 480];

function assinaturaDoQuadro(v, regiao = REGIAO) {
  const c = document.createElement("canvas");
  c.width = 48;
  c.height = 24;
  const g = c.getContext("2d");
  g.drawImage(v, ...regiao, 0, 0, 48, 24);
  const d = g.getImageData(0, 0, 48, 24).data;
  let s = "";
  for (let i = 0; i < d.length; i += 4) s += (d[i] + d[i + 1] + d[i + 2]) / 3 > 170 ? "1" : "0";
  return s;
}

async function saltar(v, t) {
  v.pause();
  v.currentTime = t;
  await new Promise((r) => { v.addEventListener("seeked", r, { once: true }); setTimeout(r, 8000); });
  await new Promise((r) => setTimeout(r, 250));
}

async function carregar(v, t) {
  v.muted = true;
  v.currentTime = t;
  await v.play().catch(() => {});
  await new Promise((r) => setTimeout(r, 3500));
  v.pause();
}

const distancia = (a, b) => [...a].filter((x, i) => x !== b[i]).length;

async function fronteira(v, a, b, tolerancia = 4) {
  await carregar(v, a); await saltar(v, a); const sa = assinaturaDoQuadro(v);
  await carregar(v, b); await saltar(v, b); const sb = assinaturaDoQuadro(v);
  if (distancia(sa, sb) <= tolerancia) return [a, b, "igual"];
  while (b - a > 1) {
    const m = Math.floor((a + b) / 2);
    await saltar(v, m);
    if (distancia(assinaturaDoQuadro(v), sa) <= tolerancia) a = m; else b = m;
  }
  return [a, b];
}

async function amostrarTocando(v, regiao, passoMs = 700, velocidade = 8) {
  const amostras = [];
  v.muted = true; v.playbackRate = velocidade; await v.play().catch(() => {});
  while (v.currentTime < v.duration - 2) {
    await new Promise((r) => setTimeout(r, passoMs));
    if (!document.querySelector(".ad-showing")) amostras.push([v.currentTime, assinaturaDoQuadro(v, regiao)]);
  }
  return amostras;
}
