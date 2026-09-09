/* O verificador independente confere um manifesto, e denuncia um adulterado (SC-001, FR-050).

   Ele é o artefato que a `SC-001` promete: a pessoa baixa o manifesto e roda isto na máquina dela.
   O teste exercita a mesma função que o executável usa, com um manifesto montado aqui a partir da
   implementação de referência — de modo que "o CLI concorda com a referência" seja afirmação
   verificada, e não expectativa. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const cli = require("../../processo_seletivo/portal/static/portal/sorteio-cli.js");
const referencia = require("../../processo_seletivo/portal/static/portal/sorteio.js");

const RELACAO = "a".repeat(64);
const ESCOPO = { profileId: "perfil-1", listId: null };
const SEMENTE = "12345 67890 11223 44556 77889";
const NUMEROS = [1, 2, 3, 4, 5];

const manifestoDe = () => {
  const escopo = cli.recorteDe(ESCOPO);
  const chaves = referencia.chaves({
    relationHash: RELACAO,
    drawScopeId: escopo,
    seed: SEMENTE,
    publicNumbers: NUMEROS,
  });
  const ordem = referencia.ordenar(chaves);
  return {
    drawId: "sorteio-1",
    process: { editalNumber: "77/2026" },
    scope: ESCOPO,
    relation: { relationHash: RELACAO, count: NUMEROS.length },
    seed: { normalized: SEMENTE },
    participants: NUMEROS.map((numero) => ({
      publicNumber: numero,
      key: chaves[numero],
      position: ordem.indexOf(numero) + 1,
    })),
  };
};

test("o verificador concorda com a implementação de referência", () => {
  const resultado = cli.verificar(manifestoDe());

  assert.equal(resultado.iguais, true);
  assert.deepEqual(resultado.divergenciasDeChave, []);
});

test("a ordem trocada no manifesto é detectada e localizada", () => {
  const manifesto = manifestoDe();
  const primeiro = manifesto.participants.find((p) => p.position === 1);
  const segundo = manifesto.participants.find((p) => p.position === 2);
  primeiro.position = 2;
  segundo.position = 1;

  const resultado = cli.verificar(manifesto);

  assert.equal(resultado.iguais, false);
});

test("a chave adulterada é denunciada pelo número público", () => {
  const manifesto = manifestoDe();
  manifesto.participants[2].key = "f".repeat(64);

  const resultado = cli.verificar(manifesto);

  assert.deepEqual(resultado.divergenciasDeChave, [manifesto.participants[2].publicNumber]);
});

test("a semente trocada muda a ordem inteira", () => {
  const manifesto = manifestoDe();
  const original = cli.verificar(manifesto).ordem;
  manifesto.seed.normalized = "99999 99999 99999 99999 99999";

  const resultado = cli.verificar(manifesto);

  assert.notDeepEqual(resultado.ordem, original);
  assert.equal(resultado.iguais, false);
});

test("a canonicalização do CLI ordena as chaves em todos os níveis", () => {
  assert.equal(cli.canonical({ b: [2, { d: 1, c: 2 }], a: "x" }), '{"a":"x","b":[2,{"c":2,"d":1}]}');
});

test("o manifesto íntegro tem o seu resumo conferido", () => {
  const manifesto = manifestoDe();
  manifesto.manifestHash = cli.resumoDoManifesto(manifesto);

  const resultado = cli.verificar(manifesto);

  assert.equal(resultado.coerenteConsigo, true);
  assert.equal(resultado.iguais, true);
  assert.equal(cli.verificar(manifesto, manifesto.manifestHash).resumoConfere, true);
});

test("um manifesto autoconsistente porém adulterado é denunciado pelo resumo", () => {
  /* **O defeito que este teste fecha.** O verificador recalculava as chaves e a ordem, e nunca
     tocava no `manifestHash`. Bastava reescrever a semente e recalcular as chaves de forma
     coerente entre si — um pacote internamente consistente, mas que não é o que a instituição
     publicou — e ele dizia que conferia. */
  const manifesto = manifestoDe();
  manifesto.manifestHash = cli.resumoDoManifesto(manifesto);

  manifesto.seed.normalized = "99999 99999 99999 99999 99999";
  const chaves = referencia.chaves({
    relationHash: manifesto.relation.relationHash,
    drawScopeId: cli.recorteDe(manifesto.scope),
    seed: manifesto.seed.normalized,
    publicNumbers: NUMEROS,
  });
  const ordem = referencia.ordenar(chaves);
  manifesto.participants = NUMEROS.map((numero) => ({
    publicNumber: numero,
    key: chaves[numero],
    position: ordem.indexOf(numero) + 1,
  }));

  const resultado = cli.verificar(manifesto);

  assert.equal(resultado.iguais, true, "o pacote é internamente coerente");
  assert.deepEqual(resultado.divergenciasDeChave, [], "e as chaves fecham entre si");
  assert.equal(
    resultado.coerenteConsigo,
    false,
    "e o resumo declarado, não recalculado, o denuncia"
  );
});

test("um manifestHash arbitrário é denunciado", () => {
  const manifesto = manifestoDe();
  manifesto.manifestHash = "f".repeat(64);

  assert.equal(cli.verificar(manifesto).coerenteConsigo, false);
});

test("um manifesto sem manifestHash não é dado como válido", () => {
  const manifesto = manifestoDe();

  assert.equal(cli.verificar(manifesto).coerenteConsigo, false);
  assert.equal(cli.verificar(manifesto, "a".repeat(64)).resumoConfere, false);
});

test("sem âncora externa o CLI não afirma que confere", () => {
  /* **A circularidade que a revisão encontrou.** Comparar o hash recalculado com o campo que o
     próprio arquivo carrega não prova nada: quem adultera recalcula o campo junto. Sem um resumo
     vindo de fora, a resposta correta é "não verificado" — e não "confere". */
  const manifesto = manifestoDe();
  manifesto.manifestHash = cli.resumoDoManifesto(manifesto);

  const resultado = cli.verificar(manifesto);

  assert.equal(resultado.coerenteConsigo, true, "o arquivo fecha consigo mesmo");
  assert.equal(resultado.resumoConfere, null, "e isso não é o mesmo que conferir");
});

test("um manifesto forjado com o resumo recalculado é denunciado pela âncora externa", () => {
  const publicado = manifestoDe();
  publicado.manifestHash = cli.resumoDoManifesto(publicado);
  const resumoDoPortal = publicado.manifestHash;

  /* O forjado: outra semente, chaves e posições coerentes entre si, e `manifestHash` recalculado —
     um pacote impecável por dentro, e que não é o que a instituição publicou. */
  const forjado = manifestoDe();
  forjado.seed.normalized = "99999 99999 99999 99999 99999";
  const chaves = referencia.chaves({
    relationHash: forjado.relation.relationHash,
    drawScopeId: cli.recorteDe(forjado.scope),
    seed: forjado.seed.normalized,
    publicNumbers: NUMEROS,
  });
  const ordem = referencia.ordenar(chaves);
  forjado.participants = NUMEROS.map((numero) => ({
    publicNumber: numero,
    key: chaves[numero],
    position: ordem.indexOf(numero) + 1,
  }));
  forjado.manifestHash = cli.resumoDoManifesto(forjado);

  const semAncora = cli.verificar(forjado);
  const comAncora = cli.verificar(forjado, resumoDoPortal);

  assert.equal(semAncora.coerenteConsigo, true, "o forjado fecha consigo mesmo");
  assert.equal(comAncora.resumoConfere, false, "e a âncora do portal o denuncia");
});

test("o manifesto publicado confere contra o resumo copiado do portal", () => {
  const manifesto = manifestoDe();
  manifesto.manifestHash = cli.resumoDoManifesto(manifesto);

  assert.equal(cli.verificar(manifesto, manifesto.manifestHash).resumoConfere, true);
  assert.equal(cli.verificar(manifesto, manifesto.manifestHash.toUpperCase()).resumoConfere, true);
});

test("o argumento --resumo é lido da linha de comando", () => {
  assert.equal(cli.resumoEsperadoDosArgumentos(["--resumo", "abc"]), "abc");
  assert.equal(cli.resumoEsperadoDosArgumentos([]), null);
  assert.equal(cli.resumoEsperadoDosArgumentos(["--resumo"]), null);
});
