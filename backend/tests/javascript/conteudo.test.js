/* A numeração da etapa Conteúdo (054, UX-130).

   O que se afirma aqui é a **regra**: dado de que depende cada seção sair, o número que ela terá.
   É a mesma regra de `pdf.numeracao`, e `test_conteudo_da_054.py` confere, do lado do servidor, que
   os dois dão o mesmo número ao conteúdo gravado.

   O que estes testes NÃO provam: a legenda atualizada ao digitar, no navegador — verificada pelo
   roteiro de quickstart.md, §4. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const regras = require(
  path.join(__dirname, "../../processo_seletivo/interface/static/interface/conteudo.js")
);

test("a textual vazia não sai, e as seguintes são numeradas sem salto", () => {
  const numeros = regras.numerar([
    { estado: "texto", preambulo: true, texto: "A Diretora faz saber" },
    { estado: "texto", texto: "" },
    { estado: "texto", texto: "Informações" },
    { estado: "sai" },
    { estado: "nao-sai" },
    { estado: "texto", texto: "   " },
    { estado: "texto", texto: "Finais" },
  ]);
  assert.deepEqual(numeros, [0, null, 1, 2, null, null, 3]);
});

test("o preâmbulo vazio não sai, e a numeração começa em 1 do mesmo jeito", () => {
  assert.deepEqual(
    regras.numerar([
      { estado: "texto", preambulo: true, texto: "" },
      { estado: "texto", texto: "Disposições" },
    ]),
    [null, 1]
  );
});

test("a textual com norma acrescentada sai mesmo vazia — o servidor a declara 'sai'", () => {
  assert.deepEqual(regras.numerar([{ estado: "sai", texto: "" }]), [1]);
});

test("a legenda diz o número, ou por que não há número", () => {
  assert.deepEqual(regras.rotulos(4), { numero: "4. ", estado: "" });
  assert.deepEqual(regras.rotulos(null), {
    numero: "",
    estado: " (vazia — não sai no documento)",
  });
  assert.deepEqual(regras.rotulos(0), { numero: "", estado: " (preâmbulo, sem número)" });
});

/* Na apresentação por perguntas (069, R-003), o número é o do servidor: "3.1 Público-alvo" não é a
   contagem das seções que saem, e recontá-lo aqui daria "4." onde o documento imprime "3.1". */

test("na apresentação por perguntas, o número é o que o servidor mandou", () => {
  assert.deepEqual(
    regras.rotulosApresentados({ estado: "texto", texto: "Graduados", rotuloDoServidor: "3.1 " }),
    { numero: "3.1 ", estado: "" }
  );
});

test("a seção esvaziada perde o número, e a preenchida espera o servidor", () => {
  assert.deepEqual(
    regras.rotulosApresentados({ estado: "texto", texto: "  ", rotuloDoServidor: "3.1 " }),
    { numero: "", estado: " (vazia — não sai no documento)" }
  );
  assert.deepEqual(
    regras.rotulosApresentados({ estado: "texto", texto: "Novo", rotuloDoServidor: "" }),
    { numero: "", estado: " (sai no documento; o número aparece ao salvar)" }
  );
});

test("o preâmbulo continua sem número na apresentação por perguntas", () => {
  assert.deepEqual(
    regras.rotulosApresentados({ estado: "texto", preambulo: true, texto: "A Diretora" }),
    { numero: "", estado: " (preâmbulo, sem número)" }
  );
});

test("o membro que sai como corpo da seção diz isso, sem número", () => {
  assert.deepEqual(
    regras.rotulosApresentados({
      estado: "texto",
      texto: "Graduados",
      rotuloDoServidor: "",
      estadoDoServidor: " (sai como o texto de 3. Quem pode se inscrever?)",
    }),
    { numero: "", estado: " (sai como o texto de 3. Quem pode se inscrever?)" }
  );
});

test("esvaziar ou preencher uma seção torna provisórios os números das outras", () => {
  const salvas = [
    { apresentada: true, estado: "texto", texto: "Graduados", rotuloDoServidor: "3.1 " },
    { apresentada: true, estado: "texto", texto: "Ser brasileiro", rotuloDoServidor: "3.2 " },
  ];
  assert.equal(regras.numeracaoDefasada(salvas), false);
  const esvaziada = [{ ...salvas[0], texto: "" }, salvas[1]];
  assert.equal(regras.numeracaoDefasada(esvaziada), true);
  assert.deepEqual(regras.rotulosApresentados(esvaziada[1], true), {
    numero: "",
    estado: " (sai no documento; o número aparece ao salvar)",
  });
});
