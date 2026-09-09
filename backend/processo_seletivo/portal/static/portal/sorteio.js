/* Implementação de referência do `IFES-SORTEIO-SHA256-v1`, em JavaScript.

   É a **segunda** implementação que a SC-002 exige, e ela existe para provar que o contrato em
   `specs/021-sorteio-publico-auditavel/contracts/algoritmo-sorteio.md` basta: quem escreveu este
   arquivo escreveu a partir do contrato, e não do código Python. Os mesmos vetores normativos
   rodam contra as duas, e um vetor que passe numa e falhe na outra é o defeito que este arranjo
   existe para encontrar.

   Mora em `static/` de propósito: é arquivo **publicado**, que qualquer pessoa baixa junto com o
   manifesto e roda na própria máquina. Não é script de página — nenhum template o carrega —, e é
   por isso que usa `node:crypto` sem se preocupar com o navegador.

   Sem dependência externa: só a biblioteca padrão do Node. Uma dependência de npm aqui
   transformaria "reimplementável por terceiro" em "reimplementável por quem confia no npm". */

const crypto = require("node:crypto");

const DOMINIO = "processo-seletivo/sorteio/v1";
const ALGORITMO = "IFES-SORTEIO-SHA256-v1";

/* Os bytes do § 2 do contrato, e a ordem das operações importa:

   1. objeto com exatamente as cinco chaves, escritas já em ordem alfabética — `JSON.stringify`
      preserva a ordem de inserção, e escrevê-las ordenadas é mais legível que ordená-las depois;
   2. sem espaço: é o que `JSON.stringify` sem terceiro argumento produz;
   3. sem escape de não-ASCII: é o padrão do `JSON.stringify`, e equivale ao `ensure_ascii=false`;
   4. NFC sobre o texto **inteiro**, e não campo a campo — é o que o lado Python faz;
   5. UTF-8. */
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

function chave(entrada) {
  return crypto.createHash("sha256").update(bytesCanonicos(entrada)).digest("hex");
}

/* O § 4, e ele é função à parte pela razão que o contrato declara: o desempate precisa de prova
   executável, e nenhuma entrada válida produz duas chaves iguais. Aqui elas chegam prontas. */
function ordenar(chavesPorNumero) {
  return Object.entries(chavesPorNumero)
    .map(([numero, valor]) => [Number(numero), String(valor)])
    .sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : a[0] - b[0]))
    .map(([numero]) => numero);
}

function chaves({ relationHash, drawScopeId, seed, publicNumbers }) {
  const saida = {};
  for (const numero of publicNumbers) {
    saida[Number(numero)] = chave({ relationHash, drawScopeId, seed, publicNumber: numero });
  }
  return saida;
}

/* Todos os participantes recebem posição. A ordem não é truncada pelo número de vagas. */
function ordem(entrada) {
  return ordenar(chaves(entrada));
}

module.exports = { ALGORITMO, DOMINIO, bytesCanonicos, chave, chaves, ordem, ordenar };
