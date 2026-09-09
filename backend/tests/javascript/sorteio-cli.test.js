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
