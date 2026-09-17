/* ENTER avança, e nunca envia (029).

   **O defeito que este arquivo prende é de uma tecla.** Num formulário com dois botões de envio, o
   navegador trata ENTER como clique no primeiro — `Guardar e continuar depois`. Quem apertasse
   ENTER no quinto dos vinte campos, por reflexo, era levado embora da tela no meio do
   preenchimento.

   **E prende também a armadilha de `form.elements`**: a coleção traz os `<fieldset>` junto dos
   controles. A primeira redação passava o foco para a caixa do grupo, que não o aceita, e a cadeia
   morria no último campo de cada seção — funcionava dentro do primeiro grupo e parava no segundo,
   que é o tipo de defeito que uma conferência rápida não encontra. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/portal/static/portal/requerimento.js"
);

/** Um formulário com dois grupos, uma área de texto, um aceite e dois botões — como a tela real. */
function formulario() {
  const form = new Elemento("form");
  const controles = [];
  function acrescentar(tag, atributos) {
    const elemento = new Elemento(tag, atributos);
    elemento.id = atributos.id || "";
    elemento.parentNode = form;
    form.filhos.push(elemento);
    controles.push(elemento);
    return elemento;
  }
  acrescentar("input", { id: "nome", type: "text" });
  acrescentar("select", { id: "uf" });
  /* O `<fieldset>` **entre** os controles: é ele que a coleção do formulário devolve junto, e é
     onde a primeira redação deixava o foco cair. */
  const grupo = new Elemento("fieldset");
  grupo.parentNode = form;
  form.filhos.push(grupo);
  controles.push(grupo);
  acrescentar("input", { id: "rg", type: "text" });
  acrescentar("textarea", { id: "observacao" });
  acrescentar("input", { id: "aceite", type: "checkbox" });
  acrescentar("button", { id: "guardar", type: "submit" });
  form.elements = controles;
  return form;
}

function montarTela() {
  const form = formulario();
  const porId = {};
  form.elements.forEach((e) => {
    if (e.id) porId[e.id] = e;
  });
  porId["formulario-do-requerimento"] = form;
  montar({ formulario: form, porId });
  carregar(SCRIPT);
  return { form, porId };
}

/** Dispara ENTER no controle e devolve se foi impedido e onde o foco parou.

    O evento é disparado **no formulário com `target` no campo**, que é como o borbulhamento o
    entrega ao ouvinte no navegador. */
function enter(form, alvo, extra = {}) {
  alvo.focus();
  const evento = form.disparar("keydown", { key: "Enter", target: alvo, ...extra });
  return {
    impedido: evento.impedido,
    foco: globalThis.__documento.activeElement && globalThis.__documento.activeElement.id,
  };
}

test("ENTER num campo avança para o seguinte, e não envia", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.nome);

  assert.equal(desfecho.foco, "uf");
  assert.equal(desfecho.impedido, true, "impedir é o que evita o envio acidental");
});

test("a cadeia atravessa o fieldset em vez de parar nele", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.uf);

  assert.equal(desfecho.foco, "rg", "o `<fieldset>` da coleção não recebe foco");
});

test("ENTER na área de texto é quebra de linha, e o script não interfere", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.observacao);

  assert.equal(desfecho.impedido, false);
  assert.equal(desfecho.foco, "observacao", "o foco não sai de onde se está escrevendo");
});

test("ENTER no aceite não envia, não marca e não avança", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.aceite);

  assert.equal(desfecho.impedido, true, "sem isto o navegador aciona o primeiro botão de envio");
  assert.equal(desfecho.foco, "aceite");
  assert.equal(porId.aceite.checked, false, "aceitar é ato deliberado — a tecla não aceita por ela");
});

test("ENTER no botão continua acionando o botão", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.guardar);

  assert.equal(desfecho.impedido, false, "quem chegou ao botão pelo teclado precisa acioná-lo");
});

test("ENTER com modificador é do navegador", () => {
  const { form, porId } = montarTela();

  const desfecho = enter(form, porId.nome, { ctrlKey: true });

  assert.equal(desfecho.impedido, false);
});

test("campo desabilitado fica fora da cadeia", () => {
  const { form, porId } = montarTela();
  porId.uf.disabled = true;

  const desfecho = enter(form, porId.nome);

  assert.equal(desfecho.foco, "rg", "mandar foco para o que não se pode editar trava quem preenche");
});
