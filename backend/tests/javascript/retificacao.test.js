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

   Desde a `123` as **regras** da busca e das frases da barra são funções exportadas pelo próprio
   script, e se afirmam aqui sem DOM: o que a busca acha, o que ela não lê, quando ela começa, o
   teto, e as duas frases da barra em cada estado.

   O que estes testes NÃO provam: a montagem do filtro — `hidden`, seletores compostos, o recorte
   de seções, o foco. Ela pede um DOM de verdade, e é provada no navegador, pela jornada do grupo
   `navegador` (`tests/navegador/test_jornada_da_retificacao_123.py`). */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Elemento, carregar, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/retificacao.js"
);

// As regras, carregadas antes de qualquer `montar`: sem documento, o script só as exporta.
const regras = require(SCRIPT);

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

test("depois da conferência, a contagem diz que zerou desde ela, e não que nada mudou", () => {
  const titulo = campo("campo:g1c1", "Edital 51/2026");
  const form = formularioDaRetificacao([linhaEditavel("Evento 1 — Inscrições", [titulo])]);
  form.setAttribute("data-conferido", "");
  const barra = form.querySelector(".barra-de-acoes");
  barra.filhos = [];
  barra.appendChild = (no) => {
    no.parentNode = barra;
    barra.filhos.push(no);
    return no;
  };

  montar({ formulario: form });
  carregar(SCRIPT);

  assert.equal(barra.filhos[0].textContent, "Nenhuma alteração nova desde a última conferência");
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

/* ── As regras da busca (123, M1) ───────────────────────────────────────────────────────────── */

function cartao(ref, contexto, campos) {
  return { ref, onde: contexto, contexto, campos };
}

/** Um recorte do Edital da auditoria: um Perfil, uma linha do quadro, um marco e uma Seção. */
const TELA = [
  cartao("cartao-g2", "Perfis de Vaga Perfil P1 — Perfil A", [
    { ref: "c-g2c1", rotulo: "Requisitos de participação", valor: "" },
    { ref: "c-g2c9", rotulo: "Remuneração", valor: "R$ 4.200,00 mensais" },
    { ref: "c-g2c10", rotulo: "Vagas imediatas", valor: "" },
    { ref: "c-g2c5", rotulo: "Localidade", valor: "Vitória" },
  ]),
  cartao("cartao-g5", "Perfis de Vaga Linha do quadro Ampla concorrência — P1", [
    { ref: "c-g5c1", rotulo: "Vagas imediatas", valor: "" },
    { ref: "c-g5c2", rotulo: "Lista de concorrência", valor: "Ampla concorrência" },
  ]),
  cartao("cartao-g9", "Perfis de Vaga Marco FINAL — P1", [
    { ref: "c-g9c1", rotulo: "Denominação do marco", valor: "Classificação final" },
    { ref: "c-g9c8", rotulo: "Prazo em dias", valor: "" },
    { ref: "c-g9c9", rotulo: "Admite recurso", valor: "" },
  ]),
  cartao("cartao-g18", "Cronograma Evento 1 — INSCRICAO", [
    { ref: "c-g18c1", rotulo: "Descrição", valor: "Inscrições pelo sistema" },
    { ref: "c-g18c3", rotulo: "Término", valor: "" },
  ]),
  cartao("cartao-g31", "Seções do texto Seção Requisitos gerais", [
    { ref: "c-g31c1", rotulo: "Texto da seção", valor: "" },
  ]),
];

function refs(achado) {
  return achado.resultados.map((r) => `${r.tipo}:${r.ref}`);
}

test("a busca acha o campo pelo rótulo, e não só o cartão", () => {
  const achado = regras.buscar("vagas", TELA);
  // A «Lista de concorrência» não entra: o cartão se chama "…quadro de vagas", mas o campo não.
  assert.deepEqual(refs(regras.buscar("vagas", TELA)), ["campo:c-g2c10", "campo:c-g5c1"]);
  assert.equal(achado.total, 2);
});

test("caixa e acento não distinguem", () => {
  assert.deepEqual(refs(regras.buscar("REMUNERACAO", TELA)), ["campo:c-g2c9"]);
  assert.deepEqual(refs(regras.buscar("remuneração", TELA)), ["campo:c-g2c9"]);
});

test("o valor curto é lido, e o resultado traz o valor atual", () => {
  const achado = regras.buscar("4.200", TELA);
  assert.deepEqual(refs(achado), ["campo:c-g2c9"]);
  assert.equal(achado.resultados[0].valor, "R$ 4.200,00 mensais");
});

test("várias palavras no mesmo campo, com ao menos uma nele próprio", () => {
  assert.deepEqual(refs(regras.buscar("término inscricao", TELA)), ["campo:c-g18c3"]);
  assert.deepEqual(refs(regras.buscar("prazo P1", TELA)), ["campo:c-g9c8"]);
});

test("o termo que só casa com o cartão dá um resultado de cartão, e não um por campo", () => {
  const achado = regras.buscar("requisitos gerais", TELA);
  assert.deepEqual(refs(achado), ["cartao:cartao-g31"]);
  assert.deepEqual(refs(regras.buscar("requisito", TELA)), [
    "campo:c-g2c1",
    "cartao:cartao-g31",
  ]);
});

test("sem termos equivalentes: «prazo recursal» não leva ao prazo do marco (D-003)", () => {
  assert.deepEqual(refs(regras.buscar("prazo recursal", TELA)), []);
  assert.equal(regras.fraseDosAchados(regras.buscar("prazo recursal", TELA)), "Nenhum campo corresponde");
});

test("abaixo de dois caracteres não há busca", () => {
  assert.equal(regras.buscar("v", TELA), null);
  assert.equal(regras.buscar("  v  ", TELA), null);
  assert.equal(regras.fraseDosAchados(null), "");
});

test("o teto de 25, com o total dito", () => {
  const muitos = Array.from({ length: 30 }, (_, i) =>
    cartao(`cartao-g${i}`, `Perfil ${i}`, [{ ref: `c-g${i}c1`, rotulo: "Vagas imediatas", valor: "" }])
  );
  const achado = regras.buscar("vagas", muitos);
  assert.equal(achado.resultados.length, 25);
  assert.equal(achado.total, 30);
  assert.equal(Object.keys(achado.visiveis).length, 30);
  assert.equal(regras.fraseDosAchados(achado), "Mostrando 25 de 30 resultados — refine a busca");
  assert.equal(regras.fraseDosAchados(regras.buscar("vagas", TELA)), "2 resultados em 2 cartões");
});

test("o valor longo, o número, a data, o Sim/Não e o arquivo não se buscam pelo valor", () => {
  const opcao = (texto, selected = false) => ({ textContent: texto, selected });
  assert.equal(regras.valorElegivel({ tagName: "INPUT", type: "text", value: "Serra" }), "Serra");
  assert.equal(regras.valorElegivel({ tagName: "TEXTAREA", value: "texto longo" }), "");
  assert.equal(regras.valorElegivel({ tagName: "INPUT", type: "number", value: "3" }), "");
  assert.equal(regras.valorElegivel({ tagName: "INPUT", type: "datetime-local", value: "2026" }), "");
  assert.equal(regras.valorElegivel({ tagName: "INPUT", type: "file", value: "" }), "");
  assert.equal(
    regras.valorElegivel({ tagName: "SELECT", options: [opcao("Sim", true), opcao("Não")] }),
    ""
  );
  assert.equal(
    regras.valorElegivel({
      tagName: "SELECT",
      options: [opcao("Ampla concorrência"), opcao("PPI — Modalidade PPI", true)],
    }),
    "PPI — Modalidade PPI"
  );
});

/* ── As duas frases da barra (123, M2, contracts §1.5) ──────────────────────────────────────── */

function frases(estado) {
  return regras.frasesDaBarra({
    proposta: null,
    cartoes: 0,
    remocoes: 0,
    edicao: false,
    enviado: false,
    alterados: 0,
    ...estado,
  });
}

test("antes de conferir, a proposta ainda não foi conferida", () => {
  assert.deepEqual(frases({ proposta: "nao-conferida" }), {
    contagem: "Nenhum campo alterado ainda",
    proposta: "Proposta ainda não conferida",
  });
  assert.equal(frases({ proposta: "nao-conferida", alterados: 2 }).contagem, "<strong>2</strong> campos alterados");
});

test("depois de conferir, as duas frases são separadas", () => {
  assert.deepEqual(frases({ proposta: "conferida", cartoes: 3, enviado: true }), {
    contagem: "Nenhuma alteração nova desde a última conferência",
    proposta: "3 cartões com alteração na proposta",
  });
  assert.deepEqual(frases({ proposta: "conferida", cartoes: 1, enviado: true, alterados: 1 }), {
    contagem: "<strong>1</strong> campo alterado desde a última conferência",
    proposta: "1 cartão com alteração na proposta",
  });
  assert.equal(
    frases({ proposta: "conferida", cartoes: 0, enviado: true }).proposta,
    "Nenhuma alteração na proposta"
  );
});

test("a conferência recusada não diz que a proposta está vazia (D-008)", () => {
  assert.equal(
    frases({ proposta: "recusada", enviado: true }).proposta,
    "Proposta não conferida — veja a recusa acima"
  );
});

test("a edição abre com o que o ato já contém, e as remoções à parte", () => {
  assert.deepEqual(frases({ proposta: "conferida", cartoes: 2, remocoes: 1, edicao: true }), {
    contagem: "Nenhuma alteração nova nesta edição",
    proposta: "2 cartões com alteração na proposta e 1 remoção já declarada",
  });
  assert.equal(
    frases({ proposta: "conferida", cartoes: 0, remocoes: 2, edicao: true }).proposta,
    "2 remoções já declaradas na proposta"
  );
  assert.equal(
    frases({ proposta: "conferida", edicao: true, alterados: 1 }).contagem,
    "<strong>1</strong> campo alterado nesta edição"
  );
});

test("a tela que não declara a proposta não ganha a segunda frase", () => {
  assert.equal(frases({}).proposta, null);
});

test("a contagem continua o primeiro filho da barra, e a proposta vem depois dela", () => {
  const titulo = campo("campo:g1c1", "Edital 51/2026");
  const form = formularioDaRetificacao([linhaEditavel("Evento 1 — Inscrições", [titulo])]);
  form.setAttribute("data-enviado", "");
  form.setAttribute("data-proposta", "conferida");
  form.setAttribute("data-proposta-cartoes", "3");
  const barra = form.querySelector(".barra-de-acoes");
  barra.filhos = [];
  barra.appendChild = (no) => {
    no.parentNode = barra;
    barra.filhos.push(no);
    return no;
  };

  montar({ formulario: form });
  carregar(SCRIPT);

  assert.equal(barra.filhos[0].textContent, "Nenhuma alteração nova desde a última conferência");
  assert.equal(barra.filhos[1].textContent, "3 cartões com alteração na proposta");
});
