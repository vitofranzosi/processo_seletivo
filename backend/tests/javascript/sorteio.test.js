/* Os vetores normativos, pela implementação de referência em JavaScript (SC-002).

   Este arquivo lê **os mesmos** arquivos JSON que `tests/contract/test_vetores_de_sorteio.py`.
   Duplicar os vetores aqui destruiria o valor do arranjo: as duas implementações concordariam com
   dados diferentes, que é precisamente o que ninguém quer saber.

   As asserções são sobre o **resultado**, e nunca sobre o texto do relatório do runner: `node
   --test` escolhe o relator pelo destino da saída, e uma afirmação sobre o resumo passa no
   terminal e reprova no pipe da CI. */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");

const sorteio = require("../../processo_seletivo/portal/static/portal/sorteio.js");

const FIXTURES = path.join(__dirname, "../contract/fixtures/sorteio");

const vetores = fs
  .readdirSync(FIXTURES)
  .filter((nome) => nome.endsWith(".json"))
  .map((nome) => JSON.parse(fs.readFileSync(path.join(FIXTURES, nome), "utf8")));

const conferirBlocoDeChave = (bloco) => {
  const entrada = bloco.input;
  for (const numero of entrada.participants) {
    const produzidos = sorteio.bytesCanonicos({
      relationHash: entrada.relationHash,
      drawScopeId: entrada.drawScopeId,
      seed: entrada.seed,
      publicNumber: numero,
    });
    assert.equal(produzidos.toString("utf8"), bloco.canonicalBytes[String(numero)]);
    assert.equal(
      sorteio.chave({
        relationHash: entrada.relationHash,
        drawScopeId: entrada.drawScopeId,
        seed: entrada.seed,
        publicNumber: numero,
      }),
      bloco.keys[String(numero)]
    );
  }
  assert.deepEqual(
    sorteio.ordem({
      relationHash: entrada.relationHash,
      drawScopeId: entrada.drawScopeId,
      seed: entrada.seed,
      publicNumbers: entrada.participants,
    }),
    bloco.expectedOrder
  );
};

test("os cinco vetores obrigatórios estão presentes", () => {
  const nomes = new Set(vetores.map((v) => v.name));
  for (const obrigatorio of [
    "tres-participantes",
    "acentos-e-nfc",
    "um-participante",
    "mesma-semente-recortes-distintos",
    "desempate-por-numero-publico",
  ]) {
    assert.ok(nomes.has(obrigatorio), `vetor ausente: ${obrigatorio}`);
  }
});

for (const vetor of vetores) {
  test(`vetor ${vetor.name}`, () => {
    if (vetor.ordering) {
      assert.deepEqual(sorteio.ordenar(vetor.ordering.keys), vetor.expectedOrder);
      return;
    }
    conferirBlocoDeChave(vetor);
    if (vetor.contrast) {
      conferirBlocoDeChave(vetor.contrast);
      assert.notDeepEqual(vetor.expectedOrder, vetor.contrast.expectedOrder);
    }
  });
}

test("a normalização NFC é aplicada: NFD e NFC produzem a mesma chave", () => {
  const vetor = vetores.find((v) => v.name === "acentos-e-nfc");
  for (const numero of vetor.input.participants) {
    assert.equal(
      sorteio.chave({
        relationHash: vetor.input.relationHash,
        drawScopeId: vetor.input.drawScopeId,
        seed: vetor.seedNFC,
        publicNumber: numero,
      }),
      vetor.keys[String(numero)]
    );
  }
});
