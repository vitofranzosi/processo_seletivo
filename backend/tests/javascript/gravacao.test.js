/* A gravação do vídeo da verificação (166, FR-7111, FR-7113, FR-7119).

   As funções puras de `portal/static/portal/gravacao.js`: o formato escolhido (MP4 primeiro), as
   marcas em segundos e o envio em partes que retoma do deslocamento que o servidor devolve. Sem
   navegador: a câmera e o `MediaRecorder` são da jornada no painel, com a imagem de teste. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const g = require(path.join(__dirname, "../../processo_seletivo/portal/static/portal/gravacao.js"));

test("o MP4 vem antes do WebM, e o WebM só para quem não grava MP4", () => {
  assert.equal(g.escolherFormato(() => true), "video/mp4;codecs=avc1.42E01E,mp4a.40.2");
  assert.equal(g.escolherFormato((tipo) => tipo.startsWith("video/webm")), "video/webm;codecs=vp9,opus");
  assert.equal(g.escolherFormato(() => false), "");
  assert.equal(g.formatoBase("video/mp4;codecs=avc1"), "video/mp4");
});

test("as marcas saem em segundos, na ordem em que o candidato tocou", () => {
  assert.deepEqual(
    g.marcasEmSegundos([
      { passo: "documento", ms: 0 },
      { passo: "frente", ms: 2345.6 },
    ]),
    [
      { passo: "documento", instante: 0 },
      { passo: "frente", instante: 2.346 },
    ]
  );
});

function servidor(tamanho, { cairNa } = {}) {
  const recebidas = [];
  let recebido = 0;
  let pedidos = 0;
  async function pedir(metodo, url, corpo) {
    pedidos += 1;
    if (metodo === "GET") return { status: 200, dados: { deslocamento: recebido, tamanho } };
    const deslocamento = Number(new URL("http://x" + url).searchParams.get("deslocamento"));
    if (cairNa !== undefined && recebidas.length === cairNa) {
      cairNa = undefined;
      throw new Error("rede caiu");
    }
    if (deslocamento !== recebido) {
      return { status: 409, dados: { codigo: "deslocamento", deslocamento: recebido } };
    }
    recebidas.push([deslocamento, corpo.length]);
    recebido += corpo.length;
    return { status: 200, dados: { deslocamento: recebido } };
  }
  return { pedir, recebidas, total: () => recebido, pedidos: () => pedidos };
}

function arquivo(tamanho) {
  return { slice: (a, b) => ({ length: Math.min(b, tamanho) - a }) };
}

test("o envio vai em partes do tamanho combinado", async () => {
  const s = servidor(25);
  const envio = new g.Envio({ arquivo: arquivo(25), tamanho: 25, parte: 10, pedir: s.pedir, rotas: { estado: "/e", partes: "/p" } });
  await envio.enviarPartes();
  assert.deepEqual(s.recebidas, [[0, 10], [10, 10], [20, 5]]);
});

test("a falha de rede é tentada de novo, e a retomada continua do recebido", async () => {
  const s = servidor(30, { cairNa: 1 });
  const envio = new g.Envio({ arquivo: arquivo(30), tamanho: 30, parte: 10, pedir: s.pedir, rotas: { estado: "/e", partes: "/p" } });
  await envio.enviarPartes();
  assert.equal(s.total(), 30);
  assert.deepEqual(s.recebidas.map((r) => r[0]), [0, 10, 20]);
});

test("a queda simulada interrompe, e o envio retoma da parte em que caiu", async () => {
  const s = servidor(30);
  const envio = new g.Envio({
    arquivo: arquivo(30), tamanho: 30, parte: 10, pedir: s.pedir,
    rotas: { estado: "/e", partes: "/p" }, quedaSimulada: 2,
  });
  await assert.rejects(envio.enviarPartes(), /queda simulada/);
  assert.equal(s.total(), 10);
  // Outra aba, ou a página recarregada, não sabe onde parou: pergunta ao servidor.
  envio.deslocamento = 0;
  assert.equal(await envio.retomar(), 10);
  await envio.enviarPartes();
  assert.deepEqual(s.recebidas.map((r) => r[0]), [0, 10, 20]);
});

test("a parte recusada pelo servidor não é repetida em silêncio", async () => {
  const envio = new g.Envio({
    arquivo: arquivo(10), tamanho: 10, parte: 10,
    pedir: async () => ({ status: 422, dados: { codigo: "tamanho", mensagem: "O envio passou do tamanho declarado." } }),
    rotas: { estado: "/e", partes: "/p" },
  });
  await assert.rejects(envio.enviarPartes(), /passou do tamanho/);
});

test("o resumo sai em hexadecimal, e o tempo em minutos e segundos", () => {
  assert.equal(g.hex(new Uint8Array([0, 15, 255]).buffer), "000fff");
  assert.equal(g.mmss(65.4), "1:05");
});
