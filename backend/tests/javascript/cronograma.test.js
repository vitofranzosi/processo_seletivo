/* A etapa Cronograma (144): o que o cartão diz em cada estado de visibilidade no PDF.

   O que se afirma aqui é a **regra** — a tabela de estados que a montagem aplica. A montagem em si
   (o `hidden` que o script tira, o `change` despachado no campo, a linha nova revelada pela
   mutação da lista) não existe no shim, e foi verificada no navegador, pelo roteiro de
   quickstart.md; a jornada inteira entra no teste de navegador do incremento C (T026). */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/cronograma.js")
);

test("exibido: campo verdadeiro, botão solto, sem marca", () => {
  assert.deepEqual(regras.estado(true), {
    valor: "true",
    pressionado: "false",
    titulo: "Exibido no PDF — ocultar",
    marcaVisivel: false,
  });
});

test("oculto: campo falso, botão pressionado, marca à vista", () => {
  assert.deepEqual(regras.estado(false), {
    valor: "false",
    pressionado: "true",
    titulo: "Oculto do PDF — exibir",
    marcaVisivel: true,
  });
});

test("o campo e o botão nunca discordam: pressionado é o contrário de exibido", () => {
  for (const exibido of [true, false]) {
    const estado = regras.estado(exibido);
    assert.equal(estado.valor === "true", estado.pressionado === "false");
    assert.equal(estado.marcaVisivel, estado.pressionado === "true");
  }
});
