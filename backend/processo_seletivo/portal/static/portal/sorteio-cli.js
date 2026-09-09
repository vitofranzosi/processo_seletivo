#!/usr/bin/env node
/* O verificador independente: lê um manifesto e imprime a ordem (021, SC-001).

   É o que uma pessoa fora da instituição roda na máquina dela, com Node e nada mais:

       node sorteio-cli.js < manifesto.json

       node sorteio-cli.js --resumo <64 hex do portal> < manifesto.json

   Ele **não** confere as posições publicadas contra si mesmas. Recalcula a chave de cada
   participante a partir das entradas que o manifesto traz — resumo da relação, identidade do
   recorte, semente e número público —, ordena, e compara com as posições que o manifesto afirma.
   Se divergirem, ele diz onde.

   **E o resumo tem de vir de fora.** Recalcular o `manifestHash` e compará-lo com o campo que o
   próprio arquivo carrega não prova coisa alguma: quem adultera o manifesto recalcula o campo
   junto, e o pacote fecha consigo mesmo. O `--resumo` recebe o valor copiado da página pública do
   sorteio, que é a única âncora que não veio no arquivo. Sem ele, o programa confere apenas a
   **coerência interna** — e diz isso, em vez de dizer que confere.

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

/* A serialização canônica do sistema, reimplementada aqui: chaves ordenadas **em todos os níveis**,
   sem espaços, sem escape de não-ASCII, NFC sobre o texto inteiro, UTF-8.

   `JSON.stringify` ordena nada — ele preserva a ordem de inserção —, e por isso a ordenação é
   explícita e recursiva. É a diferença entre conferir o manifesto e confiar nele. */
function canonical(valor) {
  if (Array.isArray(valor)) {
    return `[${valor.map(canonical).join(",")}]`;
  }
  if (valor !== null && typeof valor === "object") {
    const chaves = Object.keys(valor).sort();
    return `{${chaves.map((k) => `${JSON.stringify(k)}:${canonical(valor[k])}`).join(",")}}`;
  }
  return JSON.stringify(valor);
}

const canonicalSha256 = (valor) =>
  crypto
    .createHash("sha256")
    .update(Buffer.from(canonical(valor).normalize("NFC"), "utf8"))
    .digest("hex");

/* O resumo do manifesto cobre o objeto **sem o próprio campo**, como o contrato declara. */
function resumoDoManifesto(manifesto) {
  const semOProprioCampo = { ...manifesto };
  delete semOProprioCampo.manifestHash;
  return canonicalSha256(semOProprioCampo);
}

function verificar(manifesto, resumoEsperado = null) {
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

  /* **O resumo do manifesto, conferido — e não ignorado.** Sem esta linha, um manifesto
     autoconsistente porém adulterado passava: bastava reescrever a semente e as chaves de forma
     coerente entre si, e o verificador dizia que conferia. O `manifestHash` é o que amarra o pacote
     ao que o sistema publicou, e conferi-lo é metade do que este programa existe para fazer. */
  const resumoRecalculado = resumoDoManifesto(manifesto);
  const coerenteConsigo = Boolean(
    manifesto.manifestHash && manifesto.manifestHash === resumoRecalculado
  );
  /* **A âncora externa, e a diferença entre conferir e acreditar.** `coerenteConsigo` diz que o
     arquivo fecha com o próprio campo — o que um adulterador consegue de graça, recalculando o
     campo junto. `resumoConfere` só é verdadeiro quando o resumo recalculado bate com um valor que
     **não veio no arquivo**: o que a pessoa copiou da página pública. Sem esse valor, a resposta é
     `null` — nem confere, nem deixa de conferir; simplesmente não foi verificado. */
  const resumoConfere =
    resumoEsperado === null ? null : resumoRecalculado === String(resumoEsperado).toLowerCase();

  return {
    ordem,
    publicada,
    iguais,
    divergenciasDeChave,
    resumoRecalculado,
    coerenteConsigo,
    resumoConfere,
  };
}

/* `--resumo <hex>`, e nada mais: o programa não tem opção que mude o que ele calcula. */
function resumoEsperadoDosArgumentos(argumentos) {
  const posicao = argumentos.indexOf("--resumo");
  return posicao >= 0 && argumentos[posicao + 1] ? argumentos[posicao + 1] : null;
}

function principal(bruto, resumoEsperado = null) {
  const manifesto = JSON.parse(bruto);
  const {
    ordem,
    publicada,
    iguais,
    divergenciasDeChave,
    resumoRecalculado,
    coerenteConsigo,
    resumoConfere,
  } = verificar(manifesto, resumoEsperado);

  console.log(`Sorteio ${manifesto.drawId}`);
  console.log(`Edital ${manifesto.process.editalNumber}, ${manifesto.relation.count} participantes`);
  console.log(`Semente: ${manifesto.seed.normalized}`);
  console.log(`Resumo da relação: ${manifesto.relation.relationHash}`);
  console.log("");
  console.log("Ordem recalculada a partir das entradas:");
  ordem.forEach((numero, indice) => console.log(`  ${indice + 1}. número público ${numero}`));
  console.log("");

  if (!coerenteConsigo) {
    console.error(
      "DIVERGÊNCIA: o manifesto não fecha consigo mesmo. " +
        `Declarado: ${manifesto.manifestHash || "(ausente)"}. Recalculado: ${resumoRecalculado}.`
    );
  }
  if (resumoConfere === false) {
    console.error(
      `DIVERGÊNCIA: o resumo recalculado (${resumoRecalculado}) não é o que você copiou do ` +
        `portal (${String(resumoEsperado).toLowerCase()}). Este pacote não é o que a instituição ` +
        "publicou."
    );
  }
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
  if (divergenciasDeChave.length || !coerenteConsigo || resumoConfere === false) {
    process.exitCode = 1;
    return;
  }
  if (resumoConfere === null) {
    /* **Dizer o que foi conferido, e o que não foi.** Sem a âncora externa este programa provou
       que o arquivo é internamente coerente — e nada sobre ele ser o que a instituição publicou.
       Anunciar "confere" aqui seria a mentira que ele existe para não contar. */
    console.log(
      "Coerência interna confere: a ordem é a que estas entradas produzem, e o manifesto fecha " +
        "com o próprio resumo."
    );
    console.log(
      "ATENÇÃO: sem `--resumo`, isto **não** prova que este arquivo é o que a instituição " +
        "publicou — quem adultera o manifesto recalcula o resumo junto. Copie o resumo do " +
        "manifesto da página do sorteio e rode de novo com `--resumo <valor>`."
    );
    return;
  }
  console.log("Confere: este é o manifesto publicado, e a ordem é a que estas entradas produzem.");
  console.log(
    "Para fechar o círculo, abra a relação publicada no portal e recalcule o resumo dela a " +
      "partir do número, do nome e do protocolo de cada participante."
  );
}

if (require.main === module) {
  const pedacos = [];
  process.stdin.on("data", (pedaco) => pedacos.push(pedaco));
  const esperado = resumoEsperadoDosArgumentos(process.argv.slice(2));
  process.stdin.on("end", () =>
    principal(Buffer.concat(pedacos).toString("utf8"), esperado)
  );
}

module.exports = {
  bytesCanonicos,
  canonical,
  canonicalSha256,
  chave,
  ordenar,
  recorteDe,
  resumoDoManifesto,
  resumoEsperadoDosArgumentos,
  verificar,
};
