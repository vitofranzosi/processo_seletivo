/* Shim de DOM mínimo para executar os scripts da interface fora do navegador.

   Por que um shim escrito à mão e não jsdom: acrescentar npm, package.json e node_modules a um
   projeto Python é decisão de toolchain, que pertence ao plano e não a um teste. O shim cobre
   exatamente as APIs que `validacao.js` e `rascunho.js` usam, e nada além.

   O que estes testes provam: as **regras** — qual mensagem cada situação produz, quando o envio
   é bloqueado, quando o rascunho é descartado. O que eles NÃO provam: a integração com o
   navegador — movimentação de foco, anúncio pelo leitor de tela, `reportValidity` desenhando o
   balão. Isso continua verificado manualmente e está descrito em quickstart.md. Um shim é uma
   aproximação; tratá-lo como o navegador seria a mesma confusão de um teste que verifica a si
   mesmo. */

const CAMPOS_POR_SUFIXO = /^\[name\$="-(.+)"\]$/;

class Elemento {
  constructor(tag, atributos = {}) {
    this.tagName = tag;
    this.atributos = { ...atributos };
    this.filhos = [];
    this.value = atributos.value !== undefined ? atributos.value : "";
    this.type = atributos.type || "text";
    this.checked = false;
    this.validationMessage = "";
    this.hidden = false;
    this.style = {};
    this.dataset = {};
    this.className = "";
    this.textContent = "";
    this.nodeType = 1;
    this.parentNode = null;
    this.classes = [];
    // `remocao.js` só age sobre o botão destrutivo, distinguido pela classe `perigo`.
    this.classList = {
      contains: (nome) => this.classes.includes(nome),
    };
  }

  /** O ancestral mais próximo — incluindo o próprio — que satisfaz `[atributo]` ou uma tag. */
  closest(seletor) {
    const atributo = /^\[([\w-]+)\]$/.exec(seletor);
    for (let no = this; no; no = no.parentNode) {
      if (atributo && no.getAttribute && no.getAttribute(atributo[1]) !== null) return no;
      if (!atributo && no.tagName === seletor) return no;
    }
    return null;
  }

  get name() {
    return this.atributos.name || "";
  }

  setCustomValidity(mensagem) {
    this.validationMessage = mensagem || "";
  }

  setAttribute(chave, valor) {
    this.atributos[chave] = valor;
  }

  getAttribute(chave) {
    return Object.prototype.hasOwnProperty.call(this.atributos, chave)
      ? this.atributos[chave]
      : null;
  }

  removeAttribute(chave) {
    delete this.atributos[chave];
  }

  append(...nos) {
    this.filhos.push(...nos);
  }

  remove() {}

  focus() {
    documento.activeElement = this;
  }

  addEventListener() {}

  replaceChildren() {}

  querySelector(seletor) {
    /* `:scope > legend` — o rótulo da própria linha. A linha de Etapa tem um segundo `legend`,
       o do grupo "Caráter", e o escopo é o que impede a numeração de ir parar nele. */
    if (seletor === ":scope > legend") {
      return this.filhos.find((filho) => filho.tagName === "legend") || null;
    }
    const mover = /^\[data-mover="(cima|baixo)"\]$/.exec(seletor);
    if (mover) {
      return this.filhos.find((filho) => filho.dataset && filho.dataset.mover === mover[1]) || null;
    }
    const sufixo = CAMPOS_POR_SUFIXO.exec(seletor);
    if (!sufixo) return null;
    return this.filhos.find((filho) => filho.name && filho.name.endsWith("-" + sufixo[1])) || null;
  }

  querySelectorAll(seletor) {
    // `remocao.js` conta campos preenchidos e sub-linhas; o shim responde a esses dois seletores.
    if (seletor === "input, textarea, select") {
      return this.filhos.filter((filho) =>
        ["input", "textarea", "select"].includes(filho.tagName)
      );
    }
    // `fieldset` e `fieldset.classe` — o segundo é o que distingue linha removível de agrupamento
    // estrutural, e era a distinção que faltava.
    const fieldsets = /^fieldset(?:\.([\w-]+))?$/.exec(seletor);
    if (fieldsets) {
      return this.filhos.filter(
        (filho) =>
          filho.tagName === "fieldset" &&
          (!fieldsets[1] || (filho.classes || []).includes(fieldsets[1]))
      );
    }
    return [];
  }
}

/** Um `fieldset.linha.<classe>` com os campos indexados que o template renderiza. */
function linha(classe, indice, campos, { rotulo = "" } = {}) {
  const elemento = new Elemento("fieldset");
  elemento.classes = ["linha", classe];
  if (rotulo) {
    const legenda = new Elemento("legend");
    legenda.textContent = rotulo;
    legenda.parentNode = elemento;
    elemento.filhos.push(legenda);
  }
  for (const [sufixo, valor] of Object.entries(campos)) {
    const campo = new Elemento("input", {
      name: `${classe}-${indice}-${sufixo}`,
      value: String(valor),
    });
    campo.parentNode = elemento;
    elemento.filhos.push(campo);
  }
  return elemento;
}

/** Um botão de mover, como `_evento.html` o renderiza: atributo e `dataset` com a direção. */
function botaoDeMover(direcao) {
  const botao = new Elemento("button", { "data-mover": direcao });
  botao.dataset = { mover: direcao };
  botao.disabled = false;
  botao.focado = false;
  // Registra que **este** botão recebeu foco, além de atualizar `activeElement`. Os dois são
  // necessários: `activeElement` diz quem tem o foco agora; `focado` diz quem já o recebeu, que é
  // o que distingue "o foco foi para o botão oposto" de "o foco nunca saiu do lugar".
  const focarBase = botao.focus.bind(botao);
  botao.focus = function () {
    this.focado = true;
    focarBase();
  };
  return botao;
}

/** A `<div data-ordenavel>` que contém as linhas: o mínimo de DOM que `ordenacao.js` percorre. */
class Lista extends Elemento {
  constructor(linhas = []) {
    super("div", { "data-ordenavel": "" });
    this.children = [];
    this.ouvintes = {};
    linhas.forEach((umaLinha) => this.append(umaLinha));
  }

  append(no) {
    no.parentNode = this;
    this.children.push(no);
  }

  insertBefore(no, referencia) {
    const atual = this.children.indexOf(no);
    if (atual >= 0) this.children.splice(atual, 1);
    const posicao = this.children.indexOf(referencia);
    this.children.splice(posicao < 0 ? this.children.length : posicao, 0, no);
    no.parentNode = this;
    return no;
  }

  contains(no) {
    for (let atual = no; atual; atual = atual.parentNode) {
      if (atual === this) return true;
    }
    return false;
  }

  addEventListener(tipo, ouvinte) {
    (this.ouvintes[tipo] = this.ouvintes[tipo] || []).push(ouvinte);
  }

  /** Um clique que borbulha até a lista, como o do navegador. */
  clicar(alvo) {
    (this.ouvintes.click || []).forEach((ouvinte) => ouvinte({ type: "click", target: alvo }));
  }

  /** A ordem enviada, linha a linha — é o que o servidor vai ler. */
  ordens() {
    return this.children.map((umaLinha) => {
      const campo = umaLinha.querySelector('[name$="-order"]');
      return campo ? campo.value : null;
    });
  }
}

class Formulario extends Elemento {
  constructor(linhas = [], dataset = {}) {
    super("form", {});
    this.linhas = linhas;
    this.dataset = dataset;
    this.ouvintes = {};
    this.parentNode = { insertBefore: () => {} };
  }

  get elements() {
    return this.linhas.flatMap((umaLinha) => umaLinha.filhos);
  }

  querySelectorAll(seletor) {
    const classe = seletor.split(".").pop();
    return this.linhas.filter((umaLinha) => umaLinha.classes.includes(classe));
  }

  addEventListener(tipo, ouvinte) {
    (this.ouvintes[tipo] = this.ouvintes[tipo] || []).push(ouvinte);
  }

  disparar(tipo) {
    const evento = { type: tipo, impedido: false, preventDefault() { this.impedido = true; } };
    (this.ouvintes[tipo] || []).forEach((ouvinte) => ouvinte(evento));
    return evento;
  }

  checkValidity() {
    return this.elements.every((campo) => campo.validationMessage === "");
  }

  reportValidity() {
    return this.checkValidity();
  }

  /** Mensagem de validade do campo cujo nome termina no sufixo — o que o navegador exibiria. */
  mensagemDe(sufixo) {
    const campo = this.elements.find((item) => item.name.endsWith("-" + sufixo));
    return campo ? campo.validationMessage : null;
  }

  invalidoEmAria(sufixo) {
    const campo = this.elements.find((item) => item.name.endsWith("-" + sufixo));
    return campo ? campo.getAttribute("aria-invalid") : null;
  }
}

class Armazem {
  constructor(inicial = {}) {
    this.itens = { ...inicial };
    this.removidos = [];
  }
  getItem(chave) {
    return Object.prototype.hasOwnProperty.call(this.itens, chave) ? this.itens[chave] : null;
  }
  setItem(chave, valor) {
    this.itens[chave] = String(valor);
  }
  removeItem(chave) {
    this.removidos.push(chave);
    delete this.itens[chave];
  }
}

let documento;

/** Monta o ambiente global e devolve o que o teste precisa inspecionar. */
function montar({
  formulario,
  armazem = new Armazem(),
  avisos = [],
  ordenaveis = [],
  // O recibo do servidor: a chave do rascunho que ele acabou de receber. `null` é a tela que
  // não vem de um salvamento, que é o caso comum.
  rascunhoSalvo = null,
} = {}) {
  const ouvintes = {};
  documento = {
    activeElement: null,
    // `remocao.js` escuta `htmx:confirm` no documento — é o ponto em que a biblioteca oferece a
    // decisão antes de disparar a requisição.
    addEventListener: (tipo, ouvinte) => {
      (ouvintes[tipo] = ouvintes[tipo] || []).push(ouvinte);
    },
    disparar: (tipo, detalhe) => {
      const evento = {
        type: tipo,
        detail: detalhe,
        // `change` lê `target`; `htmx:confirm` lê `detail`. O mesmo disparador serve aos dois.
        target: detalhe,
        impedido: false,
        preventDefault() {
          this.impedido = true;
        },
      };
      (ouvintes[tipo] || []).forEach((ouvinte) => ouvinte(evento));
      return evento;
    },
    getElementById: (id) => (id === "formulario" ? formulario : null),
    querySelector: (seletor) => {
      if (seletor === "[data-nao-enviado]") return null;
      if (seletor === "[data-rascunho-salvo]") {
        if (rascunhoSalvo === null) return null;
        const recibo = new Elemento("p");
        recibo.dataset.rascunhoSalvo = rascunhoSalvo;
        return recibo;
      }
      return seletor.startsWith("#") ? new Elemento("div") : null;
    },
    querySelectorAll: (seletor) => (seletor === "[data-ordenavel]" ? ordenaveis : []),
    createElement: (tag) => new Elemento(tag),
  };
  globalThis.document = documento;
  globalThis.window = { localStorage: armazem };
  globalThis.__documento = documento;
  globalThis.Node = { ELEMENT_NODE: 1 };
  globalThis.MutationObserver = class {
    observe() {}
  };
  globalThis.setTimeout = globalThis.setTimeout || ((fn) => fn());
  // `window.confirm` decidido pelo teste, e o registro do que foi perguntado.
  globalThis.__perguntas = [];
  globalThis.window.confirm = (texto) => {
    globalThis.__perguntas.push(texto);
    return globalThis.__resposta !== false;
  };
  globalThis.__avisos = avisos;
  return { formulario, armazem, avisos };
}

function carregar(caminho) {
  // Reexecuta o IIFE contra o ambiente recém-montado.
  delete require.cache[require.resolve(caminho)];
  require(caminho);
}

module.exports = { Armazem, Elemento, Formulario, Lista, botaoDeMover, carregar, linha, montar };
