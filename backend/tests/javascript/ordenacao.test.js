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

/** Três Eventos, cada um com o campo oculto de ordem e os dois botões que o template renderiza. */
function cronograma(ordens = [1, 2, 3]) {
  const linhas = ordens.map((ordem, indice) => {
    const item = linha("evento", indice, { id: `e${indice}`, type: `T${indice}`, order: ordem });
    item.cima = botaoDeMover("cima");
    item.baixo = botaoDeMover("baixo");
    item.cima.parentNode = item;
    item.baixo.parentNode = item;
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
    lista.children.map((item) => item.filhos[0].value),
    ["e1", "e0", "e2"]
  );
  assert.deepEqual(lista.ordens(), ["1", "2", "3"], "a numeração acompanha a nova sequência");
});

test("subir a última linha a leva ao topo quando repetido", () => {
  const lista = cronograma();
  lista.clicar(lista.children[2].cima);
  lista.clicar(lista.children[1].cima);

  assert.deepEqual(
    lista.children.map((item) => item.filhos[0].value),
    ["e2", "e0", "e1"]
  );
  assert.deepEqual(lista.ordens(), ["1", "2", "3"]);
});

test("subir a primeira e descer a última não fazem nada", () => {
  const lista = cronograma();
  lista.clicar(lista.children[0].cima);
  lista.clicar(lista.children[2].baixo);

  assert.deepEqual(
    lista.children.map((item) => item.filhos[0].value),
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
