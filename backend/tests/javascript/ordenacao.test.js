/* FR-003 — mover a linha só vale se o campo `order` for junto.

   É o teste que a versão anterior do plano teria deixado passar. Ela supunha que a gravação
   derivaria a ordem da posição das linhas; não deriva — `interface/forms.py` recolhe os índices em
   um conjunto e os devolve ordenados numericamente, descartando a posição visual antes da leitura.
   Um teste que afirmasse apenas "a linha mudou de lugar" aprovaria o defeito, com a tela mostrando
   a ordem nova e o banco guardando a antiga.

   Por isso o que se afirma aqui é o valor do campo enviado, e não a posição no documento. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Lista, botaoDeMover, carregar, linha, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/ordenacao.js"
);

/** O valor de um campo da linha, pelo sufixo do nome — e não pela posição entre os filhos.
    A linha ganhou um `legend` na `007`, e índices posicionais quebrariam a cada mudança de
    marcação sem que o defeito estivesse no script. */
const campo = (item, sufixo) =>
  item.filhos.find((filho) => filho.name && filho.name.endsWith("-" + sufixo)).value;

/** O texto do `legend` da linha — a posição que ela anuncia. */
const legendaDe = (item) => item.filhos.find((filho) => filho.tagName === "legend").textContent;

/** Três Eventos, cada um com o campo oculto de ordem e os dois botões que o template renderiza. */
function cronograma(ordens = [1, 2, 3]) {
  const linhas = ordens.map((ordem, indice) => {
    const item = linha(
      "evento",
      indice,
      { id: `e${indice}`, type: `T${indice}`, order: ordem },
      { rotulo: "Evento do Cronograma" }
    );
    item.cima = botaoDeMover("cima");
    item.baixo = botaoDeMover("baixo");
    item.cima.parentNode = item;
    item.baixo.parentNode = item;
    // Também como filhos: é assim que `ordenacao.js` os encontra para desabilitar nas pontas.
    item.filhos.push(item.cima, item.baixo);
    return item;
  });
  const lista = new Lista(linhas);
  montar({ ordenaveis: [lista] });
  carregar(SCRIPT);
  return lista;
}

test("descer a primeira linha troca a ordem enviada, e não só a posição", () => {
  const lista = cronograma();
  lista.clicar(lista.children[0].baixo);

  assert.deepEqual(
    lista.children.map((item) => campo(item, "id")),
    ["e1", "e0", "e2"]
  );
  assert.deepEqual(lista.ordens(), ["1", "2", "3"], "a numeração acompanha a nova sequência");
});

test("subir a última linha a leva ao topo quando repetido", () => {
  const lista = cronograma();
  lista.clicar(lista.children[2].cima);
  lista.clicar(lista.children[1].cima);

  assert.deepEqual(
    lista.children.map((item) => campo(item, "id")),
    ["e2", "e0", "e1"]
  );
  assert.deepEqual(lista.ordens(), ["1", "2", "3"]);
});

test("subir a primeira e descer a última não fazem nada", () => {
  const lista = cronograma();
  lista.clicar(lista.children[0].cima);
  lista.clicar(lista.children[2].baixo);

  assert.deepEqual(
    lista.children.map((item) => campo(item, "id")),
    ["e0", "e1", "e2"]
  );
  assert.deepEqual(lista.ordens(), ["1", "2", "3"]);
});

test("a numeração é refeita quando o formulário chega com buracos", () => {
  // Uma remoção anterior deixou ordens 1, 4 e 9: renumerar na carga é o que impede que a
  // gravação seguinte tente gravar uma sequência que a unicidade por Edital não aceitaria.
  const lista = cronograma([1, 4, 9]);
  assert.deepEqual(lista.ordens(), ["1", "2", "3"]);
});

test("o foco fica no botão acionado", () => {
  const lista = cronograma();
  const botao = lista.children[0].baixo;
  lista.clicar(botao);

  assert.equal(document.activeElement, botao, "sem isto, reordenar por teclado perde o foco");
});


/* T074 — a posição da linha e o estado dos botões nas pontas (FR-035). */

test("cada linha diz sua posição na legenda", () => {
  const lista = cronograma();

  assert.deepEqual(
    lista.children.map(legendaDe),
    ["Evento do Cronograma 1 de 3", "Evento do Cronograma 2 de 3", "Evento do Cronograma 3 de 3"]
  );
});

test("a numeração acompanha o movimento em vez de congelar no rótulo inicial", () => {
  const lista = cronograma();
  lista.clicar(lista.children[0].baixo);

  const legendas = lista.children.map(legendaDe);
  assert.deepEqual(legendas, [
    "Evento do Cronograma 1 de 3",
    "Evento do Cronograma 2 de 3",
    "Evento do Cronograma 3 de 3",
  ]);
  // E o rótulo base não acumula: numerar duas vezes não produz "Evento 1 de 3 1 de 3".
  assert.ok(!legendas.some((texto) => /de 3.*de 3/.test(texto)));
});

test("subir na primeira e descer na última ficam desabilitados", () => {
  const lista = cronograma();

  assert.equal(lista.children[0].cima.disabled, true, "primeira linha não sobe");
  assert.equal(lista.children[0].baixo.disabled, false);
  assert.equal(lista.children[2].cima.disabled, false);
  assert.equal(lista.children[2].baixo.disabled, true, "última linha não desce");
  assert.equal(lista.children[1].cima.disabled, false, "a do meio move nos dois sentidos");
  assert.equal(lista.children[1].baixo.disabled, false);
});

test("o estado dos botões acompanha o movimento", () => {
  const lista = cronograma();
  lista.clicar(lista.children[0].baixo);

  // A que era primeira agora é a segunda: passa a poder subir.
  const segunda = lista.children[1];
  assert.equal(legendaDe(segunda), "Evento do Cronograma 2 de 3");
  assert.equal(segunda.cima.disabled, false);
  assert.equal(lista.children[0].cima.disabled, true, "a nova primeira não sobe");
});

test("o foco não se perde quando o botão acionado chega à ponta", () => {
  const lista = cronograma();
  // A segunda linha sobe: o botão "cima" acionado fica desabilitado ao chegar ao topo.
  const acionado = lista.children[1].cima;
  lista.clicar(acionado);

  assert.equal(acionado.disabled, true);
  assert.equal(acionado.focado, false, "focar um botão desabilitado devolveria o foco ao body");
  assert.equal(lista.children[0].baixo.focado, true, "o foco vai para o botão que ainda opera");
});

test("uma lista de uma linha só não oferece movimento", () => {
  const lista = cronograma([1]);

  assert.equal(lista.children[0].cima.disabled, true);
  assert.equal(lista.children[0].baixo.disabled, true);
  assert.equal(legendaDe(lista.children[0]), "Evento do Cronograma 1 de 1");
});
