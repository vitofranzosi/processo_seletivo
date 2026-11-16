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

/* As funções do palco (174, contracts/telas.md). */

test("o passo diz a posição no roteiro, contando de um", () => {
  assert.equal(g.rotuloDoPasso(0, 4), "Passo 1 de 4");
  assert.equal(g.rotuloDoPasso(3, 4), "Passo 4 de 4");
});

test("dois toques a menos de meio segundo contam como um, e não há tempo mínimo além disso", () => {
  assert.equal(g.aceitaAvanco(1000, null), true);
  assert.equal(g.aceitaAvanco(1499, 1000), false);
  assert.equal(g.aceitaAvanco(1500, 1000), true);
});

test("os megabytes saem com vírgula e uma casa", () => {
  assert.equal(g.megabytes(9856000), "9,4");
  assert.equal(g.megabytes(0), "0,0");
});

test("a duração sai em minutos e segundos, como o filtro do comprovante", () => {
  assert.equal(g.duracaoPorExtenso(72.3), "1 min 12 s");
  assert.equal(g.duracaoPorExtenso(45), "45 s");
  assert.equal(g.duracaoPorExtenso(180), "3 min");
  assert.equal(g.duracaoPorExtenso(4.5), "5 s");
});

test("a fala só conta com nível alto por 300 ms seguidos", () => {
  const amostras = (niveis, passo = 100) => niveis.map((nivel, i) => ({ nivel, ms: i * passo }));
  assert.equal(g.ouviuFala(amostras([30, 30, 30, 30])), true);
  assert.equal(g.ouviuFala(amostras([30, 30, 5, 30, 30])), false);
  assert.equal(g.ouviuFala(amostras([10, 10, 10, 10, 10])), false);
  assert.equal(g.ouviuFala([]), false);
});

test("a imagem de teste gira de frente, à esquerda, de frente e à direita, a cada dez segundos (176)", () => {
  assert.equal(g.giroDaImagemDeTeste(1), 0);
  assert.equal(g.giroDaImagemDeTeste(4), 1);
  assert.equal(g.giroDaImagemDeTeste(6), 0);
  assert.equal(g.giroDaImagemDeTeste(8), -1);
  assert.equal(g.giroDaImagemDeTeste(14), 1);
  assert.ok(g.giroDaImagemDeTeste(2.75) > 0 && g.giroDaImagemDeTeste(2.75) < 1);
});

/* A emenda da 176: o documento na imagem de teste, a frase da fala e o medidor do microfone. */

test("a imagem de teste mostra o documento ao lado do rosto no começo do ciclo, e depois o tira (FR-8065)", () => {
  assert.equal(g.rostosDaImagemDeTeste(0.2), 1);
  assert.equal(g.rostosDaImagemDeTeste(1), 2);
  assert.equal(g.rostosDaImagemDeTeste(2.5), 1);
  assert.equal(g.rostosDaImagemDeTeste(11), 2);
  // O documento aparece com o vulto de frente, e não durante um giro.
  for (const t of [0.6, 1, 1.5, 2.1]) assert.equal(g.giroDaImagemDeTeste(t), 0, t);
});

test("a frase da fala põe em destaque só o que está entre aspas, sem acrescentar nada (FR-8072)", () => {
  const texto =
    "Olhe para a câmera e diga a frase «Eu me autodeclaro pessoa preta» ou «pessoa parda», como declarou.";
  const partes = g.partesDaFrase(texto);
  assert.equal(partes.map((p) => p.texto).join(""), texto);
  assert.deepEqual(
    partes.filter((p) => p.destaque).map((p) => p.texto),
    ["«Eu me autodeclaro pessoa preta»", "«pessoa parda»"]
  );
  assert.deepEqual(g.partesDaFrase("Sem aspas."), [{ texto: "Sem aspas.", destaque: false }]);
  assert.deepEqual(g.partesDaFrase("Aspa «sem fim"), [{ texto: "Aspa «sem fim", destaque: false }]);
  assert.deepEqual(g.partesDaFrase(""), []);
});

test("a frase do roteiro de frente sai inteira das partes", () => {
  // A do roteiro de verdade, como o template a entrega no `data-texto`.
  const frente =
    "Olhe para a câmera e diga o seu nome e a frase «Eu me autodeclaro pessoa preta» ou " +
    "«pessoa parda», como declarou na inscrição. Não diga o seu CPF. Se preferir, mostre a " +
    "frase escrita num papel, ou diga em Libras.";
  assert.equal(g.partesDaFrase(frente).map((p) => p.texto).join(""), frente);
});

test("o pico sai das amostras em ponto flutuante ou em bytes, na mesma escala", () => {
  assert.equal(g.picoDasAmostras(new Float32Array([0, 0.1, -0.25, 0.2]), false), 0.25);
  assert.equal(g.picoDasAmostras(new Uint8Array([128, 128, 160, 96]), true), 0.25);
  assert.equal(g.picoDasAmostras(new Uint8Array([128, 128]), true), 0);
});

test("a régua da fala continua a da 174: nível 20 a partir de 8% do fundo de escala (FR-8082)", () => {
  assert.equal(g.LIMIAR_DA_FALA, 20);
  assert.equal(g.nivelDoPico(0.08), 20);
  assert.equal(g.nivelDoPico(1), 100);
  assert.equal(g.nivelDoPico(0), 0);
});

test("a barra é em decibéis: a fala comum fica no meio, e a marca no limiar da fala (FR-8081)", () => {
  assert.equal(g.fracaoDoMedidor(0), 0);
  assert.equal(g.fracaoDoMedidor(1), 1);
  // Um pico de -30 dB (fala baixa, longe do microfone) já sai do começo da barra.
  assert.ok(g.fracaoDoMedidor(10 ** (-30 / 20)) > 0.4);
  // Na escala linear de antes, o mesmo pico dava 8% da barra.
  assert.ok(g.nivelDoPico(10 ** (-30 / 20)) < 10);
  // A marca de "volume bom" é exatamente onde a régua da fala passa a ouvir.
  assert.equal(g.MARCA_DO_VOLUME_BOM, g.fracaoDoMedidor(g.LIMIAR_DA_FALA / 250));
  assert.ok(g.MARCA_DO_VOLUME_BOM > 0.55 && g.MARCA_DO_VOLUME_BOM < 0.7);
  // O silêncio da sala (-60 dB) não mexe a barra.
  assert.equal(g.fracaoDoMedidor(10 ** (-60 / 20)), 0);
});

test("a barra sobe rápido e desce devagar, para não piscar", () => {
  // Em 50 ms a barra já subiu quase toda, e ainda não desceu quase nada; em um segundo, desceu.
  const subida = g.suavizarMedidor(0, 1, 50);
  const descida = g.suavizarMedidor(1, 0, 50);
  assert.ok(subida > 0.6, String(subida));
  assert.ok(descida > 0.85, String(descida));
  assert.ok(g.suavizarMedidor(1, 0, 1000) < 0.15);
  assert.equal(g.suavizarMedidor(0.5, 0.5, 16), 0.5);
  assert.equal(g.suavizarMedidor(0.2, 1, 0), 0.2);
});
