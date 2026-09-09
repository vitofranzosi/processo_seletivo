#!/usr/bin/env node
/* O verificador independente: lê um manifesto e imprime a ordem (021, SC-001).

   É o que uma pessoa fora da instituição roda na máquina dela, com Node e nada mais:

       node sorteio-cli.js < manifesto.json

   Ele **não** confere as posições publicadas contra si mesmas. Recalcula a chave de cada
   participante a partir das entradas que o manifesto traz — resumo da relação, identidade do
   recorte, semente e número público —, ordena, e compara com as posições que o manifesto afirma.
   Se divergirem, ele diz onde.

   O resumo da relação ele **não** recalcula, porque o manifesto não traz os nomes: para isso a
   pessoa abre a relação publicada no portal, que traz número, nome e protocolo, e é exatamente o
   que o resumo cobre. As duas conferências juntas fecham o círculo sem pedir confiança a ninguém.

   Sem dependência de npm: só `node:crypto`, pela mesma razão que a implementação de referência —
   "reimplementável por terceiro" não pode significar "por quem confia no npm". */

const crypto = require("node:crypto");

const DOMINIO = "processo-seletivo/sorteio/v1";

function bytesCanonicos({ relationHash, drawScopeId, seed, publicNumber }) {
  const texto = JSON.stringify({
    domain: DOMINIO,
    drawScopeId: String(drawScopeId),
    publicNumber: Number(publicNumber),
    relationHash: String(relationHash),
    seed: String(seed),
  });
  return Buffer.from(texto.normalize("NFC"), "utf8");
}

const chave = (entrada) =>
  crypto.createHash("sha256").update(bytesCanonicos(entrada)).digest("hex");

const ordenar = (chavesPorNumero) =>
  Object.entries(chavesPorNumero)
    .map(([numero, valor]) => [Number(numero), String(valor)])
    .sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : a[0] - b[0]))
    .map(([numero]) => numero);

/* `drawScopeId` é derivado do recorte como o contrato manda: o perfil sozinho quando não há lista,
   e `perfil:lista` quando há. É a única coisa que o verificador precisa montar. */
const recorteDe = (escopo) =>
  escopo.listId ? `${escopo.profileId}:${escopo.listId}` : String(escopo.profileId);

function verificar(manifesto) {
  const escopo = recorteDe(manifesto.scope);
  const chaves = {};
  const divergenciasDeChave = [];
  for (const participante of manifesto.participants) {
    const recalculada = chave({
      relationHash: manifesto.relation.relationHash,
      drawScopeId: escopo,
      seed: manifesto.seed.normalized,
      publicNumber: participante.publicNumber,
    });
    chaves[participante.publicNumber] = recalculada;
    if (participante.key && participante.key !== recalculada) {
      divergenciasDeChave.push(participante.publicNumber);
    }
  }
  const ordem = ordenar(chaves);
  const publicada = manifesto.participants
    .slice()
    .sort((a, b) => a.position - b.position)
    .map((p) => p.publicNumber);
  const iguais =
    ordem.length === publicada.length && ordem.every((n, i) => n === publicada[i]);
  return { ordem, publicada, iguais, divergenciasDeChave };
}

function principal(bruto) {
  const manifesto = JSON.parse(bruto);
  const { ordem, publicada, iguais, divergenciasDeChave } = verificar(manifesto);

  console.log(`Sorteio ${manifesto.drawId}`);
  console.log(`Edital ${manifesto.process.editalNumber}, ${manifesto.relation.count} participantes`);
  console.log(`Semente: ${manifesto.seed.normalized}`);
  console.log(`Resumo da relação: ${manifesto.relation.relationHash}`);
  console.log("");
  console.log("Ordem recalculada a partir das entradas:");
  ordem.forEach((numero, indice) => console.log(`  ${indice + 1}. número público ${numero}`));
  console.log("");

  if (divergenciasDeChave.length) {
    console.error(
      `DIVERGÊNCIA: a chave publicada não confere para os números ${divergenciasDeChave.join(", ")}.`
    );
  }
  if (!iguais) {
    const primeira = ordem.findIndex((n, i) => n !== publicada[i]);
    console.error(
      `DIVERGÊNCIA: a ordem publicada difere da recalculada na posição ${primeira + 1}.`
    );
    process.exitCode = 1;
    return;
  }
  if (divergenciasDeChave.length) {
    process.exitCode = 1;
    return;
  }
  console.log("Confere: a ordem publicada é a que estas entradas produzem.");
  console.log(
    "Para fechar o círculo, abra a relação publicada no portal e recalcule o resumo dela a " +
      "partir do número, do nome e do protocolo de cada participante."
  );
}

if (require.main === module) {
  const pedacos = [];
  process.stdin.on("data", (pedaco) => pedacos.push(pedaco));
  process.stdin.on("end", () => principal(Buffer.concat(pedacos).toString("utf8")));
}

module.exports = { bytesCanonicos, chave, ordenar, recorteDe, verificar };
