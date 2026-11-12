/* O envio dos documentos da convocação: um seletor por documento, um botão de envio só (150).

   Sem o shim de `dom.js`: objetos simples, como `envio.test.js` e `arquivo.test.js`. O que se prova
   é a regra — o que cada cartão e a área do envio dizem a cada escolha, o lote um por vez e na ordem
   da tela, o arquivo grande que não viaja, e o que a tela diz quando o lote para no meio. O foco, o
   anúncio pelo leitor de tela e a volta à âncora são do navegador, e estão na jornada no navegador.

   A D-001 foi revista em 12/11/2026: o botão de cada cartão sai de vista, e o envio é o da área no
   fim da lista. Os casos da primeira versão — "Enviar os N documentos escolhidos" em cada cartão —
   viraram os da área. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const SCRIPT = path.join(__dirname, "../../processo_seletivo/portal/static/portal/varios.js");

const ACESSO_EXPIRADO = "Não foi possível enviar: o seu acesso expirou.";
const CONEXAO = "Não foi possível enviar: a conexão falhou.";
const FALHA = "Não foi possível enviar agora.";

function classes(iniciais = []) {
  const lista = new Set(iniciais);
  return {
    add: (nome) => lista.add(nome),
    remove: (nome) => lista.delete(nome),
    contains: (nome) => lista.has(nome),
    toggle: (nome, sim) => (sim ? lista.add(nome) : lista.delete(nome)),
  };
}

function elemento(extra = {}) {
  return { hidden: true, textContent: "", classList: classes(), ...extra };
}

function botaoQueEscuta(extra = {}) {
  const ouvintes = {};
  return {
    hidden: true,
    disabled: false,
    textContent: "",
    addEventListener: (tipo, ouvinte) => (ouvintes[tipo] = ouvinte),
    clicar() {
      ouvintes.click();
    },
    ...extra,
  };
}

function cartao(nome, { limite = 1000, substituicao = false, tarefa = !substituicao } = {}) {
  const ouvintes = {};
  /* Como no navegador: zerar o `value` de um campo de arquivo esvazia a lista de arquivos. */
  const campo = {
    files: [],
    focado: false,
    get value() {
      return this.files.length ? `C:\\fakepath\\${this.files[0].name}` : "";
    },
    set value(valor) {
      if (valor === "") this.files = [];
    },
    disabled: false,
    focus() {
      this.focado = true;
    },
    addEventListener: (tipo, ouvinte) => {
      ouvintes[tipo] = ouvinte;
    },
  };
  /* O "Enviar" de hoje, no cartão: é o envio sem script, e com script sai de vista. */
  const botao = { hidden: false, innerHTML: `Enviar<span class="oculto">: ${nome}</span>` };
  const nomeDoArquivo = { textContent: "Nenhum arquivo escolhido", classList: classes() };
  const estado = elemento();
  const remover = botaoQueEscuta();
  const escolher = elemento({ hidden: false });
  const trocar = elemento();
  const limiteDoCartao = elemento({ hidden: false });
  const ficha = { value: "ficha-csrf" };
  const filhos = [];
  /* A recusa que a volta anterior pôs no cartão, como o servidor a desenha. */
  const recusaAntiga = {
    removida: false,
    remove() {
      this.removida = true;
    },
  };
  /* O "Falta enviar." do cartão sem arquivo recebido, que sai de vista com a escolha. */
  const situacao = { classList: classes() };
  const li = {
    classList: classes(),
    getAttribute: (chave) => (chave === "data-documento" ? nome : null),
    hasAttribute: (chave) => chave === "data-tarefa" && tarefa,
    querySelector: (s) => {
      if (s === "[data-some-com-a-escolha]") return substituicao ? null : situacao;
      if (s === ".recusa-do-envio") return filhos.find((f) => f.className.includes("recusa-do-envio"));
      if (s === "[data-recusa]") return recusaAntiga.removida ? null : recusaAntiga;
      return null;
    },
    appendChild: (filho) => filhos.push(filho),
  };
  const ouvintesDoForm = {};
  const form = {
    nome,
    action: `/envio/${nome}`,
    getAttribute: (chave) => (chave === "data-limite-em-bytes" ? String(limite) : null),
    querySelector: (s) =>
      ({
        "[data-envio-do-cartao]": botao,
        "[data-arquivo]": campo,
        "[data-nome-do-arquivo]": nomeDoArquivo,
        "[data-estado-da-escolha]": estado,
        "[data-remover-escolha]": remover,
        "[data-rotulo-escolher]": escolher,
        "[data-rotulo-trocar]": trocar,
        "[data-limite-do-cartao]": limiteDoCartao,
        "[name=csrfmiddlewaretoken]": ficha,
      })[s] || null,
    closest: (s) => {
      if (s === ".cartao-do-documento") return li;
      if (s === "details.envio-de-novo") return substituicao ? {} : null;
      return null;
    },
    addEventListener: (tipo, ouvinte) => {
      ouvintesDoForm[tipo] = ouvinte;
    },
  };
  return {
    form,
    campo,
    botao,
    nomeDoArquivo,
    estado,
    remover,
    escolher: escolher,
    trocar,
    limiteDoCartao,
    li,
    situacao,
    recusaAntiga,
    recado: () => filhos.find((f) => f.className.includes("recusa-do-envio")),
    escolherArquivo(arquivo = { name: `${nome}.pdf`, size: 10 }) {
      campo.files = [arquivo];
      ouvintes.change();
    },
    submeter() {
      const evento = {
        prevenido: false,
        parado: false,
        preventDefault() {
          this.prevenido = true;
        },
        stopPropagation() {
          this.parado = true;
        },
      };
      ouvintesDoForm.submit(evento);
      return evento;
    },
  };
}

function json(dados) {
  return { ok: true, status: 200, headers: { get: () => "application/json" }, json: async () => dados };
}

function html(status) {
  return { ok: status < 400, status, headers: { get: () => "text/html; charset=utf-8" } };
}

/* A área do envio, como o servidor a desenha: escondida, com o botão indisponível. */
function areaDoEnvio() {
  const barra = { atributos: { value: "0" }, removeAttribute(chave) { delete this.atributos[chave]; } };
  const ajuda = { textContent: "Enviando… não feche esta página." };
  const progresso = { hidden: true, querySelector: (s) => ({ progress: barra, ".ajuda": ajuda })[s] || null };
  const botao = botaoQueEscuta({ hidden: false, disabled: true, textContent: "Enviar documentos" });
  const contagem = { textContent: "Nenhum arquivo selecionado" };
  const orientacao = { textContent: "Escolha o arquivo PDF de cada documento acima." };
  const recado = { hidden: true, textContent: "" };
  return {
    hidden: true,
    classList: classes(),
    botao,
    contagem,
    orientacao,
    progresso,
    ajuda,
    recado,
    querySelector(s) {
      return (
        {
          "[data-enviar-os-escolhidos]": botao,
          "[data-contagem-da-escolha]": contagem,
          "[data-orientacao-da-escolha]": orientacao,
          "[data-progresso-do-lote]": progresso,
          "[data-recado-do-lote]": recado,
        }[s] || null
      );
    },
  };
}

/* Cada chamada do `fetch` fica pendente até o teste respondê-la: assim se vê que o lote espera a
   resposta de um documento antes de mandar o seguinte. */
function carregar(cartoes, { comArea = true } = {}) {
  const chamadas = [];
  const janela = {};
  const anuncio = { textContent: "" };
  const area = areaDoEnvio();
  const instrucao = { hidden: true };
  global.window = {
    location: { assign: (destino) => (janela.destino = destino) },
    addEventListener: (tipo, ouvinte) => (janela[tipo] = ouvinte),
  };
  const confirmacaoAnterior = { hidden: false };
  global.document = {
    querySelectorAll: (s) =>
      ({
        "form[data-envio]": cartoes.map((c) => c.form),
        "[data-instrucao-com-script]": [instrucao],
      })[s] || [],
    querySelector: (s) =>
      ({
        "[data-anuncio-de-varios]": anuncio,
        "#confirmacao": confirmacaoAnterior,
        "[data-envio-dos-documentos]": comArea ? area : null,
      })[s] || null,
    createElement: () => ({
      className: "",
      textContent: "",
      atributos: {},
      setAttribute(chave, valor) {
        this.atributos[chave] = valor;
      },
    }),
  };
  /* Como no navegador: o campo desabilitado fica fora do `FormData` do formulário. O lote desabilita
     os campos antes de enviar, e por isso o corpo precisa ser montado à mão. */
  global.FormData = class {
    constructor(form) {
      const campo = form && form.querySelector("[data-arquivo]");
      this.campos = campo && !campo.disabled ? [["arquivo", campo.files[0]]] : [];
    }
    append(chave, valor) {
      this.campos.push([chave, valor]);
    }
  };
  global.fetch = (url, opcoes) =>
    new Promise((resolver, rejeitar) => chamadas.push({ url, opcoes, resolver, rejeitar }));
  delete require.cache[require.resolve(SCRIPT)];
  require(SCRIPT);
  return { chamadas, janela, anuncio, confirmacaoAnterior, area, instrucao };
}

async function esperar() {
  for (let i = 0; i < 10; i++) await new Promise((r) => setImmediate(r));
}

function tres() {
  return [cartao("Certidão"), cartao("Histórico"), cartao("Residência")];
}

// --- Com script, um envio só (D-001 revista, FR-5612) -------------------------------------------

test("com script, a área e a frase aparecem, e o botão de cada cartão sai de vista", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);

  assert.equal(tela.area.hidden, false);
  assert.equal(tela.instrucao.hidden, false);
  for (const c of [a, b]) {
    assert.equal(c.botao.hidden, true, "nenhum botão de envio dentro do cartão");
    assert.ok(c.limiteDoCartao.classList.contains("oculto"), "o limite é dito uma vez, na frase");
  }
  assert.equal(tela.area.botao.disabled, true, "nada escolhido, nada a enviar");
  assert.equal(tela.area.botao.textContent, "Enviar documentos");
  assert.ok(tela.area.classList.contains("vazia"), "sem escolha, a área é leve");
  assert.equal(tela.area.contagem.hidden, true, "e não conta zero");
});

test("sem a área — nenhum cartão com envio —, o script não mexe em nada", () => {
  const [a] = tres();
  const tela = carregar([a], { comArea: false });

  assert.equal(a.botao.hidden, false);
  assert.equal(tela.instrucao.hidden, true);
});

// --- A escolha (FR-5601, FR-5602, FR-5603, UX-501, UX-503) --------------------------------------

test("escolher um arquivo: o cartão diz que foi escolhido e não enviado, e a área conta", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);

  a.escolherArquivo();

  assert.equal(a.estado.hidden, false, "Selecionado — ainda não enviado.");
  assert.equal(a.remover.hidden, false);
  assert.equal(a.escolher.hidden, true);
  assert.equal(a.trocar.hidden, false, "o seletor vira Trocar arquivo");
  assert.ok(a.li.classList.contains("com-escolha"));
  assert.ok(a.situacao.classList.contains("oculto"), "\"Falta enviar.\" sai de vista");
  assert.ok(!b.situacao.classList.contains("oculto"));
  assert.ok(!tela.area.classList.contains("vazia"));
  assert.equal(tela.area.contagem.hidden, false);
  assert.equal(b.estado.hidden, true, "o outro cartão não muda");
  assert.equal(b.remover.hidden, true);
  assert.equal(tela.area.contagem.textContent, "1 de 2 arquivos selecionados");
  assert.equal(tela.area.orientacao.textContent, "O arquivo ainda não foi enviado à comissão.");
  assert.equal(tela.area.botao.textContent, "Enviar 1 documento");
  assert.equal(tela.area.botao.disabled, false);
  assert.equal(tela.anuncio.textContent, "1 documento escolhido para enviar.");
});

test("dois escolhidos: o botão diz os dois, e a área diz que ainda não foram enviados", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);

  a.escolherArquivo();
  b.escolherArquivo();

  assert.equal(tela.area.contagem.textContent, "2 de 2 arquivos selecionados");
  assert.equal(tela.area.orientacao.textContent, "Os arquivos ainda não foram enviados à comissão.");
  assert.equal(tela.area.botao.textContent, "Enviar 2 documentos");
  assert.equal(tela.anuncio.textContent, "2 documentos escolhidos para enviar.");
});

test("escolher de novo no mesmo cartão troca a escolha e não muda a contagem", () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);

  a.escolherArquivo();
  b.escolherArquivo();
  b.escolherArquivo({ name: "outro.pdf", size: 20 });

  assert.equal(tela.area.botao.textContent, "Enviar 2 documentos");
  assert.equal(tela.area.contagem.textContent, "2 de 3 arquivos selecionados");
});

test("a pendência de correção conta no \"de M\", mesmo sendo substituição", () => {
  const a = cartao("Histórico", { substituicao: true, tarefa: true });
  const b = cartao("Residência");
  const tela = carregar([a, b]);

  a.escolherArquivo();
  b.escolherArquivo();

  assert.equal(tela.area.contagem.textContent, "2 de 2 arquivos selecionados");
});

test("a substituição conta no envio, mas não no \"de M\" dos pendentes", () => {
  const a = cartao("Certidão");
  const b = cartao("Histórico", { substituicao: true });
  const tela = carregar([a, b]);

  b.escolherArquivo();
  assert.equal(tela.area.contagem.textContent, "1 arquivo selecionado", "não \"1 de 1\"");

  a.escolherArquivo();
  assert.equal(tela.area.contagem.textContent, "2 arquivos selecionados");
  assert.equal(tela.area.botao.textContent, "Enviar 2 documentos");
});

test("remover a escolha volta o cartão ao começo, refaz a contagem e devolve o foco ao campo", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);
  a.escolherArquivo();
  b.escolherArquivo();
  a.nomeDoArquivo.textContent = "Certidão.pdf";
  a.nomeDoArquivo.classList.add("escolhido");

  a.remover.clicar();

  assert.equal(a.campo.files.length, 0);
  assert.equal(a.nomeDoArquivo.textContent, "Nenhum arquivo escolhido");
  assert.ok(!a.nomeDoArquivo.classList.contains("escolhido"));
  assert.equal(a.estado.hidden, true);
  assert.equal(a.remover.hidden, true);
  assert.equal(a.escolher.hidden, false);
  assert.ok(!a.li.classList.contains("com-escolha"));
  assert.ok(!a.situacao.classList.contains("oculto"), "\"Falta enviar.\" volta");
  assert.equal(a.campo.focado, true);
  assert.equal(b.campo.files.length, 1, "a outra escolha fica");
  assert.equal(tela.area.botao.textContent, "Enviar 1 documento");

  b.remover.clicar();
  assert.ok(tela.area.classList.contains("vazia"));
  assert.equal(tela.area.botao.disabled, true);
  assert.equal(tela.area.botao.textContent, "Enviar documentos");
  assert.equal(tela.area.orientacao.textContent, "Escolha o arquivo PDF de cada documento acima.");
});

test("um envio que escape pelo formulário vai pelo lote; sem nada escolhido, a frase no cartão", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);

  const vazio = a.submeter();
  assert.equal(vazio.prevenido, true, "não sai da página (FR-5604)");
  assert.equal(a.recado().textContent, "Escolha um arquivo PDF antes de enviar.");
  assert.equal(tela.chamadas.length, 0);

  b.escolherArquivo();
  const evento = a.submeter();
  assert.equal(evento.prevenido, true, "o envio nativo levaria um só");
  assert.equal(evento.parado, true, "o ouvinte de `envio.js` não age sobre o lote");
  assert.equal(tela.chamadas.length, 1);
  assert.equal(tela.chamadas[0].url, "/envio/Histórico");
});

// --- O lote (FR-5605 a FR-5607, R-002, R-004, R-009) --------------------------------------------

test("o lote envia um por vez, na ordem da tela, e volta à âncora do servidor", async () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);
  a.escolherArquivo();
  b.escolherArquivo();
  c.escolherArquivo();

  tela.area.botao.clicar();

  assert.equal(tela.chamadas.length, 1, "o segundo só sai depois da resposta do primeiro");
  assert.equal(tela.chamadas[0].url, "/envio/Certidão");
  assert.equal(tela.chamadas[0].opcoes.headers["X-Envio-De-Varios"], "1/3");
  assert.equal(tela.area.progresso.hidden, false);
  assert.equal(tela.area.ajuda.textContent, "Enviando 1 de 3: Certidão… Não feche esta página.");
  assert.equal(tela.anuncio.textContent, "Enviando 1 de 3: Certidão… Não feche esta página.");
  assert.equal(tela.area.botao.disabled, true);
  for (const cartao of [a, b, c]) {
    assert.equal(cartao.campo.disabled, true);
    assert.equal(cartao.remover.disabled, true);
  }

  tela.chamadas[0].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();
  assert.equal(tela.chamadas.length, 2);
  assert.equal(tela.chamadas[1].opcoes.headers["X-Envio-De-Varios"], "2/3");
  assert.equal(tela.area.ajuda.textContent, "Enviando 2 de 3: Histórico… Não feche esta página.");

  tela.chamadas[1].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();
  tela.chamadas[2].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();

  assert.deepEqual(
    tela.chamadas.map((c) => c.url),
    ["/envio/Certidão", "/envio/Histórico", "/envio/Residência"]
  );
  assert.equal(tela.janela.destino, "/c?lote=3#confirmacao");
});

test("com um só escolhido, o envio é o mesmo caminho, de um, e a frase não conta", async () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);
  b.escolherArquivo();

  tela.area.botao.clicar();

  assert.equal(tela.chamadas.length, 1);
  assert.equal(tela.chamadas[0].opcoes.headers["X-Envio-De-Varios"], "1/1");
  assert.equal(tela.area.ajuda.textContent, "Enviando Histórico… Não feche esta página.");
  tela.chamadas[0].resolver(json({ resultado: "recebido", volta: "/c?lote=1#confirmacao" }));
  await esperar();
  assert.equal(tela.janela.destino, "/c?lote=1#confirmacao");
});

test("o arquivo acima do limite não viaja: vai o tamanho, e o lote segue", async () => {
  const a = cartao("Certidão", { limite: 100 });
  const b = cartao("Histórico", { limite: 100 });
  const tela = carregar([a, b]);
  a.escolherArquivo({ name: "grande.pdf", size: 5000 });
  b.escolherArquivo();

  tela.area.botao.clicar();
  const corpo = tela.chamadas[0].opcoes.body.campos;

  assert.deepEqual(corpo, [
    ["csrfmiddlewaretoken", "ficha-csrf"],
    ["tamanho_declarado", "5000"],
  ]);
  tela.chamadas[0].resolver(
    json({ resultado: "recusado", frase: "O arquivo tem…", volta: "/c?lote=2#item-a" })
  );
  await esperar();
  assert.equal(tela.chamadas.length, 2, "a recusa de um não para os seguintes");
  assert.deepEqual(
    tela.chamadas[1].opcoes.body.campos.map(([chave]) => chave),
    ["csrfmiddlewaretoken", "arquivo"]
  );
});

test("o arquivo vai no corpo mesmo com o campo desabilitado pelo lote", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);
  a.escolherArquivo({ name: "certidao.pdf", size: 10 });
  b.escolherArquivo();

  tela.area.botao.clicar();

  assert.equal(a.campo.disabled, true, "durante o lote, ninguém troca o arquivo");
  assert.deepEqual(tela.chamadas[0].opcoes.body.campos, [
    ["csrfmiddlewaretoken", "ficha-csrf"],
    ["arquivo", { name: "certidao.pdf", size: 10 }],
  ]);
});

test("um segundo clique durante o lote não começa outro", () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);
  a.escolherArquivo();
  b.escolherArquivo();

  tela.area.botao.clicar();
  tela.area.botao.clicar();
  a.submeter();

  assert.equal(tela.chamadas.length, 1);
});

// --- O que não chegou (FR-5606, FR-5609, FR-5610, R-010) ----------------------------------------

test("a recusa de um não interrompe os seguintes, e a volta é a do servidor", async () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);
  a.escolherArquivo();
  b.escolherArquivo();
  c.escolherArquivo();

  tela.area.botao.clicar();
  tela.chamadas[0].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();
  tela.chamadas[1].resolver(
    json({ resultado: "recusado", frase: "É uma imagem.", volta: "/c?lote=3#confirmacao" })
  );
  await esperar();
  tela.chamadas[2].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();

  assert.equal(tela.chamadas.length, 3);
  assert.equal(tela.janela.destino, "/c?lote=3#confirmacao");
});

test("a página de acesso no meio: a página fica, a área diz o que chegou, e o resto continua escolhido", async () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);
  a.escolherArquivo();
  b.escolherArquivo();
  c.escolherArquivo();

  tela.area.botao.clicar();
  tela.chamadas[0].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();
  tela.chamadas[1].resolver(html(200));
  await esperar();

  assert.equal(tela.janela.destino, undefined, "não sai da página");
  assert.equal(tela.chamadas.length, 2, "não tenta os seguintes");
  const recado = tela.area.recado.textContent;
  assert.equal(tela.area.recado.hidden, false, "o recado fica junto do botão");
  assert.ok(recado.startsWith(ACESSO_EXPIRADO));
  assert.ok(recado.includes("Recebemos: Certidão."));
  assert.ok(recado.includes("Não foram enviados: Histórico, Residência."));
  assert.equal(a.campo.value, "", "o que chegou perde a escolha");
  assert.equal(a.nomeDoArquivo.textContent, "Recebido agora.");
  assert.equal(a.estado.hidden, true, "não diz mais \"ainda não enviado\"");
  assert.equal(a.recusaAntiga.removida, true, "a recusa da volta anterior sai do que chegou");
  assert.equal(b.recusaAntiga.removida, false, "e fica no que não foi enviado");
  assert.equal(tela.confirmacaoAnterior.hidden, true, "a confirmação anterior não contradiz a nova");
  assert.equal(b.campo.files.length, 1, "o que não foi enviado continua escolhido");
  assert.equal(tela.area.botao.textContent, "Enviar 2 documentos", "o botão volta, com o N novo");
  assert.equal(tela.area.botao.disabled, false);
  assert.equal(tela.area.progresso.hidden, true);
});

test("a 404 no meio é o acesso expirado; a 500, a falha genérica", async () => {
  for (const [resposta, frase] of [
    [html(404), ACESSO_EXPIRADO],
    [{ ok: false, status: 500, headers: { get: () => "text/html" } }, FALHA],
  ]) {
    const [a, b] = tres();
    const tela = carregar([a, b]);
    a.escolherArquivo();
    b.escolherArquivo();

    tela.area.botao.clicar();
    tela.chamadas[0].resolver(resposta);
    await esperar();

    assert.ok(tela.area.recado.textContent.startsWith(frase), frase);
    assert.ok(tela.area.recado.textContent.includes("Não foram enviados: Certidão, Histórico."));
  }
});

test("na queda de conexão, do documento em voo não se afirma nada", async () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);
  a.escolherArquivo();
  b.escolherArquivo();
  c.escolherArquivo();

  tela.area.botao.clicar();
  tela.chamadas[0].resolver(json({ resultado: "recebido", volta: "/c?lote=3#confirmacao" }));
  await esperar();
  tela.chamadas[1].rejeitar(new TypeError("Failed to fetch"));
  await esperar();

  const recado = tela.area.recado.textContent;
  assert.ok(recado.startsWith(CONEXAO));
  assert.ok(recado.includes("Recebemos: Certidão."));
  assert.ok(recado.includes("Não foram enviados: Residência."));
  assert.ok(recado.includes("Histórico: não é possível saber se chegou"));
  assert.ok(!/não (foi )?recebid/i.test(recado), "nunca \"não recebido\"");
  assert.equal(b.campo.files.length, 1, "o documento em voo continua escolhido");
  assert.equal(c.campo.files.length, 1);
  assert.equal(tela.janela.destino, undefined);
});

test("um recusado antes da queda traz a recusa no cartão dele", async () => {
  const [a, b, c] = tres();
  const tela = carregar([a, b, c]);
  a.escolherArquivo();
  b.escolherArquivo();
  c.escolherArquivo();

  tela.area.botao.clicar();
  tela.chamadas[0].resolver(
    json({ resultado: "recusado", frase: "É uma imagem.", volta: "/c?lote=3#item-a" })
  );
  await esperar();
  tela.chamadas[1].rejeitar(new TypeError("Failed to fetch"));
  await esperar();

  assert.equal(a.recado().textContent, "É uma imagem.", "a recusa no cartão do recusado");
  assert.ok(tela.area.recado.textContent.startsWith(CONEXAO), "a queda junto do botão");
  assert.equal(a.campo.value, "");
  assert.ok(!tela.area.recado.textContent.includes("Recebemos"), "nada chegou");
});

test("a volta pelo cache do navegador devolve botão, rótulo e progresso", async () => {
  const [a, b] = tres();
  const tela = carregar([a, b]);
  a.escolherArquivo();
  b.escolherArquivo();
  tela.area.botao.clicar();

  tela.janela.pageshow();

  assert.equal(tela.area.botao.disabled, false);
  assert.equal(tela.area.progresso.hidden, true);
  assert.equal(tela.area.ajuda.textContent, "Enviando… não feche esta página.");
  assert.equal(tela.area.botao.textContent, "Enviar 2 documentos");
  assert.equal(a.campo.disabled, false);
});

test("a volta que coincide com o endereço atual ganha `de-novo`, e a seguinte não", async () => {
  for (const [atual, volta, esperado] of [
    ["?lote=1", "/c?lote=1#confirmacao", "/c?de-novo=1&lote=1#confirmacao"],
    ["?de-novo=1&lote=1", "/c?lote=1#confirmacao", "/c?lote=1#confirmacao"],
    ["", "/c?lote=1#confirmacao", "/c?lote=1#confirmacao"],
  ]) {
    const [a] = tres();
    const tela = carregar([a]);
    global.window.location.pathname = "/c";
    global.window.location.search = atual;
    a.escolherArquivo();

    tela.area.botao.clicar();
    tela.chamadas[0].resolver(json({ resultado: "recebido", volta }));
    await esperar();

    assert.equal(tela.janela.destino, esperado, atual);
  }
});
