/* O "Copiar" do kit de divulgação (111): o texto do alvo vai para a área de transferência, e a
   região de situação diz o que aconteceu — copiado, com o nome do texto, ou a falha, com o que
   fazer. A ligação com o documento é do navegador. Sem o shim de `dom.js`: objetos simples. */

const assert = require("node:assert/strict");
const { test } = require("node:test");

const kit = require("../../processo_seletivo/interface/static/interface/kit-de-divulgacao.js");

function montar(escrever) {
  const ouvintes = {};
  const botao = { addEventListener: (tipo, ouvinte) => (ouvintes[tipo] = ouvinte) };
  const alvo = { textContent: "Edital nº 91/2026 — Cefor/Ifes" };
  const situacao = { textContent: "" };
  const escritos = [];
  kit.ligar(botao, alvo, situacao, "Legenda para rede social", (texto) => {
    escritos.push(texto);
    return escrever();
  });
  return { clicar: () => ouvintes.click(), situacao, escritos };
}

test("copiar escreve o texto do alvo e anuncia o nome dele", async () => {
  const tela = montar(() => Promise.resolve());
  tela.clicar();
  await new Promise((resolver) => setImmediate(resolver));
  assert.deepEqual(tela.escritos, ["Edital nº 91/2026 — Cefor/Ifes"]);
  assert.equal(tela.situacao.textContent, kit.COPIADO + "Legenda para rede social.");
});

test("a falha diz o que fazer, e não finge que copiou", async () => {
  const tela = montar(() => Promise.reject(new Error("negado")));
  tela.clicar();
  await new Promise((resolver) => setImmediate(resolver));
  assert.equal(tela.situacao.textContent, kit.FALHOU);
});
