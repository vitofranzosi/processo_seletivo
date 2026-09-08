/* A contagem do que já foi alterado, na tela de Retificação.

   Um Edital publicado rende dezenas de linhas editáveis e vários metros de rolagem, e nada na
   tela distinguia o campo que alguém acabou de mudar dos outros noventa: o resumo "antes e
   depois" só existe depois de um envio. Quem alterava uma data no primeiro cartão e seguia
   rolando não tinha como reencontrá-la, nem como responder "quantas coisas eu mexi?" antes de
   enviar.

   O que se afirma aqui é a **regra**, e não o desenho:

   - o ponto de comparação é o valor que o servidor entregou, e não o que estava no campo há um
     segundo — desfazer a edição desmarca;
   - a justificativa e a vigência descrevem o **ato**, e não o conteúdo do Edital, e não entram
     na conta: contá-las faria a tela anunciar "1 campo alterado" no exato caso que o servidor
     recusa com "nenhum campo foi alterado".

   O que estes testes NÃO provam: o filtro. Ele só é montado a partir de uma dúzia de linhas, e
   exercitá-lo pediria um DOM de verdade — `hidden`, seletores compostos, o recorte de seções.
   Ele esconde e nunca remove, então o formulário enviado é o mesmo com ou sem filtro; é
   verificado à mão, e está descrito em quickstart.md. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/retificacao.js"
);

/** Um campo como o template o renderiza: dentro de um `p.campo`, dentro de um `fieldset.linha`. */
function campo(nome, valor, { tipo = "text" } = {}) {
  const celula = new Elemento("p");
  celula.classes = ["campo"];
  const controle = new Elemento("input", { name: nome, value: valor, type: tipo });
  controle.defaultValue = valor;
  controle.parentNode = celula;
  celula.filhos.push(controle);
  return { celula, controle };
}

/** Uma linha do conteúdo vigente, com legenda e campos. */
function linhaEditavel(rotulo, campos) {
  const linha = new Elemento("fieldset");
  linha.classes = ["linha"];
  linha.atributos["data-linha"] = "";
  linha.atributos["data-nome"] = rotulo;
  const legenda = new Elemento("legend");
  legenda.textContent = rotulo;
  legenda.parentNode = linha;
  linha.filhos.push(legenda);
  campos.forEach(({ celula, controle }) => {
    celula.parentNode = linha;
    controle.parentNode = celula;
    linha.filhos.push(celula);
  });
  return linha;
}

/** O formulário da tela: as linhas e a barra de ações que recebe a contagem. */
function formularioDaRetificacao(linhas) {
  const form = new Elemento("form");
  const barra = new Elemento("p");
  barra.classes = ["navegacao-etapa", "barra-de-acoes"];
  barra.parentNode = form;

  form.ouvintes = {};
  form.filhos = linhas.concat([barra]);
  form.filhos.forEach((filho) => {
    filho.parentNode = form;
  });

  /* Busca em profundidade, que é o que o script faz sobre o documento real. O shim comum é raso
     de propósito — os outros scripts só olham a própria linha —, e aqui a mesma consulta precisa
     descer do formulário até o `input` dentro do `p.campo` dentro do `fieldset`. */
  const descendentes = (no) =>
    (no.filhos || []).flatMap((filho) => [filho].concat(descendentes(filho)));

  const casa = (no, seletor) => {
    if (seletor === "input, select, textarea") {
      return ["input", "select", "textarea"].includes(no.tagName);
    }
    if (seletor === ".campo") return (no.classes || []).includes("campo");
    if (seletor === ".remover-linha") return (no.classes || []).includes("remover-linha");
    if (seletor === ".barra-de-acoes") return (no.classes || []).includes("barra-de-acoes");
    if (seletor === ".alterada") return (no.classes || []).includes("alterada");
    if (seletor === "fieldset.linha") {
      return no.tagName === "fieldset" && (no.classes || []).includes("linha");
    }
    // Nem seção nem linha acrescentada existem neste formulário mínimo.
    return false;
  };

  form.querySelectorAll = (seletor) => descendentes(form).filter((no) => casa(no, seletor));
  form.querySelector = (seletor) => form.querySelectorAll(seletor)[0] || null;
  form.addEventListener = (tipo, ouvinte) => {
    (form.ouvintes[tipo] = form.ouvintes[tipo] || []).push(ouvinte);
  };
  form.digitar = () => (form.ouvintes.input || []).forEach((ouvinte) => ouvinte({ type: "input" }));

  linhas.forEach((linha) => {
    linha.querySelectorAll = (seletor) => descendentes(linha).filter((no) => casa(no, seletor));
    const legenda = linha.filhos.find((filho) => filho.tagName === "legend");
    legenda.querySelector = (seletor) =>
      (legenda.filhos || []).find((filho) => casa(filho, seletor)) || null;
    legenda.appendChild = (no) => {
      no.parentNode = legenda;
      legenda.filhos.push(no);
      return no;
    };
  });

  return form;
}

/** Prepara o script contra um formulário com um campo de conteúdo e a justificativa do ato. */
function montarTela() {
  const titulo = campo("campo:g1c1", "Edital 51/2026");
  const justificativa = campo("justificativa", "");
  const linha = linhaEditavel("Evento 1 — Inscrições", [titulo]);
  const ato = linhaEditavel("O ato", [justificativa]);
  delete ato.atributos["data-linha"];

  const form = formularioDaRetificacao([linha, ato]);
  const barra = form.querySelector(".barra-de-acoes");
  barra.appendChild = (no) => {
    no.parentNode = barra;
    barra.filhos.push(no);
    return no;
  };
  barra.filhos = [];

  montar({ formulario: form });
  carregar(SCRIPT);
  return { form, linha, titulo, justificativa, contagem: barra.filhos[0] };
}

test("sem tocar em nada, a tela não anuncia alteração nenhuma", () => {
  const { contagem, linha } = montarTela();

  assert.equal(contagem.textContent, "Nenhum campo alterado ainda");
  assert.equal(linha.getAttribute("data-alterado"), null);
});

test("o campo alterado marca a si e à linha em que ele está", () => {
  const { form, linha, titulo, contagem } = montarTela();

  titulo.controle.value = "Edital 51/2026 — retificado";
  form.digitar();

  assert.match(contagem.innerHTML, /1<\/strong> campo alterado/);
  assert.equal(linha.getAttribute("data-alterado"), "");
  assert.equal(titulo.celula.getAttribute("data-alterado"), "");
  // Cor não informa sozinha: a legenda diz em palavras o que a borda diz em verde (WCAG 1.4.1).
  assert.ok(linha.filhos[0].querySelector(".alterada"), "a legenda precisa dizer que mudou");
});

test("desfazer a edição desmarca — a comparação é com o que o servidor entregou", () => {
  const { form, linha, titulo, contagem } = montarTela();

  titulo.controle.value = "outra coisa";
  form.digitar();
  titulo.controle.value = titulo.controle.defaultValue;
  form.digitar();

  assert.equal(contagem.textContent, "Nenhum campo alterado ainda");
  assert.equal(linha.getAttribute("data-alterado"), null);
  assert.equal(linha.filhos[0].querySelector(".alterada"), null);
});

test("a justificativa do ato não conta como conteúdo alterado do Edital", () => {
  const { form, justificativa, contagem } = montarTela();

  justificativa.controle.value = "Correção da data de inscrição";
  form.digitar();

  /* O servidor recusa o envio que só traz justificativa com "nenhum campo foi alterado". Contar
     a justificativa faria a tela anunciar "1 campo alterado" e prometer o que a recusa desmente. */
  assert.equal(contagem.textContent, "Nenhum campo alterado ainda");
});
