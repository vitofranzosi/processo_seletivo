/* FR-022 da 003 — o rascunho guardado tem prazo, verificado executando o script.

   O teste anterior procurava a constante no fonte. Isto aqui carrega o script contra um
   `localStorage` falso e afirma o efeito: o rascunho velho é removido sem ser oferecido, o
   recente é oferecido, e o que não tem carimbo de tempo utilizável é descartado. */

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const { Armazem, Elemento, Formulario, carregar, linha, montar } = require("./dom.js");

const SCRIPT = path.join(
  __dirname,
  "../../processo_seletivo/interface/static/interface/rascunho.js"
);
const CHAVE = "ps:rascunho:edital:perfis:ana";
const UM_DIA = 24 * 60 * 60 * 1000;

function formulario() {
  return new Formulario(
    [linha("perfil", 0, { id: "p1", code: "P1", name: "Renderizado pelo servidor" })],
    { rascunho: "edital:perfis:ana", lista: "#perfis" }
  );
}

/** Um rascunho guardado com conteúdo diferente do renderizado, na idade pedida. */
function guardado(idadeMs, opcoes = {}) {
  // `hasOwnProperty` e não `em !== undefined`: o caso "chave ausente no JSON" precisa ser
  // distinguível de "não informei o carimbo neste teste", e é justamente ele que se quer cobrir.
  const carimbo = Object.prototype.hasOwnProperty.call(opcoes, "em")
    ? opcoes.em
    : new Date(Date.now() - idadeMs).toISOString();
  return JSON.stringify({
    em: carimbo,
    dados: {
      simples: {},
      linhas: [{ id: "p1", code: "P1", name: "O que a pessoa digitou e não enviou" }],
    },
    copia: { html: "", valores: {} },
  });
}

function carregarCom(bruto, opcoes = {}) {
  const armazem = new Armazem(bruto === null ? {} : { [CHAVE]: bruto });
  const form = opcoes.semFormulario ? null : formulario();
  montar({ formulario: form, armazem, rascunhoSalvo: opcoes.rascunhoSalvo ?? null });
  carregar(SCRIPT);
  // O script sonda o armazenamento gravando e apagando `CHAVE + ":teste"`; só interessa aqui o
  // que aconteceu com a chave do rascunho.
  armazem.removeuORascunho = armazem.removidos.filter((chave) => chave === CHAVE).length > 0;
  return armazem;
}

test("rascunho mais velho que um dia é descartado sem ser oferecido", () => {
  const armazem = carregarCom(guardado(UM_DIA + 60_000));

  assert.equal(armazem.removeuORascunho, true);
  assert.equal(armazem.getItem(CHAVE), null);
});

test("rascunho de meses atrás também é descartado", () => {
  const armazem = carregarCom(guardado(90 * UM_DIA));

  assert.equal(armazem.removeuORascunho, true);
});

test("rascunho recente é preservado para ser oferecido", () => {
  const armazem = carregarCom(guardado(60_000));

  assert.equal(armazem.removeuORascunho, false);
  assert.notEqual(armazem.getItem(CHAVE), null);
});

test("rascunho na fronteira, com um dia menos um minuto, ainda é oferecido", () => {
  const armazem = carregarCom(guardado(UM_DIA - 60_000));

  assert.equal(armazem.removeuORascunho, false);
});

test("rascunho sem carimbo de tempo utilizável é tratado como vencido", () => {
  for (const carimbo of [undefined, "", "não é data"]) {
    const armazem = carregarCom(guardado(0, { em: carimbo }));
    assert.equal(armazem.removeuORascunho, true, `carimbo ${JSON.stringify(carimbo)}`);
  }
});

test("conteúdo corrompido é descartado em vez de derrubar a tela", () => {
  const armazem = carregarCom("{ isto não é JSON");

  assert.equal(armazem.removeuORascunho, true);
});

test("sem nada guardado, nada é removido", () => {
  const armazem = carregarCom(null);

  assert.equal(armazem.removeuORascunho, false);
});

/* O recibo do servidor — a metade que faltava.

   Sem ela, salvar o rascunho recarregava a tela dizendo "Rascunho salvo" e, logo abaixo, "há
   preenchimento não enviado neste navegador": duas frases contraditórias sobre o mesmo ato, na
   mesma tela, no mesmo segundo. A comparação por conteúdo não desfazia o engano porque o
   servidor normaliza o que recebe, e o digitado nunca volta textualmente igual. */

test("o que o servidor confirma ter recebido é apagado do navegador", () => {
  const armazem = carregarCom(guardado(60_000), { rascunhoSalvo: "edital:perfis:ana" });

  assert.equal(armazem.removeuORascunho, true);
  assert.equal(armazem.getItem(CHAVE), null);
});

test("o recibo apaga a etapa que foi gravada, e não a que está na tela", () => {
  // "Avançar" grava uma etapa e abre a seguinte: o recibo fala da anterior.
  const outra = "ps:rascunho:edital:cronograma:ana";
  const armazem = new Armazem({ [CHAVE]: guardado(60_000), [outra]: guardado(60_000) });
  montar({ formulario: formulario(), armazem, rascunhoSalvo: "edital:cronograma:ana" });
  carregar(SCRIPT);

  assert.equal(armazem.getItem(outra), null, "a etapa gravada foi apagada");
  assert.notEqual(armazem.getItem(CHAVE), null, "a etapa em edição continua guardada");
});

test("o recibo é honrado mesmo numa etapa que não guarda rascunho", () => {
  // Conteúdo e Revisão não têm formulário com rascunho local, e "Avançar" pode parar numa delas.
  const armazem = carregarCom(guardado(60_000), {
    rascunhoSalvo: "edital:perfis:ana",
    semFormulario: true,
  });

  assert.equal(armazem.removeuORascunho, true);
});

test("sem recibo, o rascunho recente continua sendo oferecido", () => {
  const armazem = carregarCom(guardado(60_000), { rascunhoSalvo: null });

  assert.equal(armazem.removeuORascunho, false);
});

/* O grupo de rádio — a forma de conclusão da Etapa (012, D-008). Os dois controles dividem o
   `name`, e era essa divisão que o rascunho não sabia tratar: `ler` percorria os dois e o último
   sobrescrevia o escolhido, de modo que o guardado era sempre a última opção da lista. Mudar de
   opção nem marcava o formulário como não enviado, porque o lido não mudava.

   A outra metade — restaurar escrevendo no `value` do rádio, que é a opção que ele
   **representa** e não a escolhida — está coberta mais abaixo, junto da restauração da lista. */

const ETAPAS = "ps:rascunho:edital:etapas:ana";

function comGrupo(marcada) {
  return new Formulario(
    [
      linha("etapa", 0, {
        id: "e1",
        name: "Prova",
        forma: [
          { type: "radio", value: "PONTUADA", checked: marcada === "PONTUADA" },
          { type: "radio", value: "DECISORIA", checked: marcada === "DECISORIA" },
        ],
      }),
    ],
    { rascunho: "edital:etapas:ana", lista: "#etapas" }
  );
}

/** A linha que o script grava depois de o preenchimento divergir do renderizado.
 *
 * O `await`: a gravação é adiada em 400 ms para não escrever a cada tecla, e o shim só substitui
 * `setTimeout` quando ele não existe — sob Node, o adiamento é real. Ler antes dele devolveria
 * `null` e o teste passaria a afirmar nada.
 */
async function gravado(formulario) {
  const armazem = new Armazem();
  montar({ formulario, armazem });
  carregar(SCRIPT);
  formulario.elements.find((campo) => campo.name.endsWith("-name")).value = "Outra coisa";
  formulario.disparar("input");
  await new Promise((pronto) => setTimeout(pronto, 450));
  const guardado = armazem.getItem(ETAPAS);
  return guardado === null ? null : JSON.parse(guardado).dados.linhas[0];
}

test("o rascunho guarda a opção marcada, e não a última do grupo", async () => {
  assert.equal((await gravado(comGrupo("PONTUADA"))).forma, "PONTUADA");
});

test("marcar a segunda opção é o que faz o rascunho registrar a segunda", async () => {
  assert.equal((await gravado(comGrupo("DECISORIA"))).forma, "DECISORIA");
});

test("grupo sem opção marcada não inventa escolha nenhuma", async () => {
  assert.equal("forma" in (await gravado(comGrupo(null))), false);
});

test("registro da forma anterior, sem a cópia da lista, é descartado e não oferecido", () => {
  const anterior = JSON.parse(guardado(60_000));
  delete anterior.copia;

  assert.equal(carregarCom(JSON.stringify(anterior)).removeuORascunho, true);
});

/* A restauração das coleções aninhadas — RC-08 da auditoria de consolidação, FR-020 da 002.

   A restauração recriava cada Perfil pedindo o fragmento vazio ao servidor e preenchia só os
   campos de três segmentos. `modalidade-0-7-code` tem quatro: caía no balaio dos simples, era
   procurado pelo nome antigo numa linha que já tinha outro índice, e sumia. Percorrido na tela em
   28/09: três Modalidades antes de "Restaurar", nenhuma depois, e o autosave regravando a perda.

   O shim não tem HTML. `ListaDoFormulario` faz o papel de `innerHTML` com a mesma assimetria do
   navegador — serializa os **atributos** e não o que foi digitado, que é propriedade do controle —,
   e é essa assimetria que obriga o script a guardar os valores ao lado da estrutura. */

/** A lista `#perfis`: o `innerHTML` dela é a estrutura das linhas do formulário. */
class ListaDoFormulario extends Elemento {
  constructor(formulario) {
    super("div");
    this.formulario = formulario;
  }

  get innerHTML() {
    return JSON.stringify(
      this.formulario.linhas.map((umaLinha) => ({
        classes: umaLinha.classes,
        campos: umaLinha.filhos.map((campo) => ({ ...campo.atributos, marcado: campo.marcadoNoHtml })),
      }))
    );
  }

  set innerHTML(html) {
    this.formulario.linhas = JSON.parse(html).map((descrita) => {
      const umaLinha = new Elemento("fieldset");
      umaLinha.classes = descrita.classes;
      umaLinha.filhos = descrita.campos.map(({ marcado, ...atributos }) => {
        const campo = new Elemento("input", atributos);
        campo.checked = Boolean(marcado);
        campo.marcadoNoHtml = Boolean(marcado);
        campo.parentNode = umaLinha;
        return campo;
      });
      return umaLinha;
    });
  }
}

/** O Perfil como o servidor o renderiza: gravado, sem Modalidade nenhuma, reserva "NONE". */
function perfilDoServidor() {
  const formulario = new Formulario(
    [
      linha("perfil", 0, {
        id: "p1",
        name: "Renderizado pelo servidor",
        reserveType: [
          { type: "radio", value: "NONE", checked: true },
          { type: "radio", value: "LIMITED", checked: false },
        ],
      }),
    ],
    { rascunho: "edital:perfis:ana", lista: "#perfis" }
  );
  // O que o HTML traz marcado é o que o servidor renderizou, e não o que a pessoa clicou depois.
  formulario.elements.forEach((campo) => (campo.marcadoNoHtml = campo.checked));
  return formulario;
}

/** Monta a tela com a lista observável e devolve os elementos que o script criar. */
function abrir(formulario, armazem) {
  const lista = new ListaDoFormulario(formulario);
  montar({ formulario, armazem, porId: { perfis: lista } });
  const processadas = [];
  globalThis.window.htmx = { process: (no) => processadas.push(no) };
  const criados = [];
  const criar = globalThis.document.createElement;
  globalThis.document.createElement = (tag) => {
    const elemento = criar(tag);
    criados.push(elemento);
    return elemento;
  };
  carregar(SCRIPT);
  return { lista, processadas, criados };
}

function campo(formulario, nome) {
  return formulario.elements.find((item) => item.name === nome && item.type !== "radio");
}

function escolhido(formulario, nome) {
  const marcado = formulario.elements.find((item) => item.name === nome && item.checked);
  return marcado ? marcado.value : null;
}

const esperar = () => new Promise((pronto) => setTimeout(pronto, 450));

/** Preenche, na primeira visita, um Perfil com uma Modalidade que o servidor ainda não conhece. */
async function preencherSemEnviar(armazem) {
  const formulario = perfilDoServidor();
  abrir(formulario, armazem);
  // "Acrescentar Modalidade": a linha nasce do fragmento com quatro segmentos no nome, e o valor
  // digitado depois é propriedade, não atributo.
  const modalidade = linha("modalidade", "0-7", { code: "", percentage: "" });
  modalidade.filhos.forEach((item) => (item.marcadoNoHtml = false));
  formulario.linhas.push(modalidade);
  campo(formulario, "modalidade-0-7-code").value = "PPP";
  campo(formulario, "modalidade-0-7-percentage").value = "25";
  campo(formulario, "perfil-0-name").value = "O que a pessoa digitou";
  formulario.elements.find((item) => item.value === "NONE").checked = false;
  formulario.elements.find((item) => item.value === "LIMITED").checked = true;
  formulario.disparar("input");
  await esperar();
}

/** A segunda visita: a sessão caiu, a tela volta como o servidor a tem, e a pessoa restaura. */
function voltarERestaurar(armazem) {
  const formulario = perfilDoServidor();
  const tela = abrir(formulario, armazem);
  const botao = tela.criados.find((item) => item.textContent === "Restaurar o que eu havia digitado");
  assert.ok(botao, "o preenchimento não enviado precisa ser oferecido");
  botao.disparar("click");
  return { formulario, ...tela };
}

test("restaurar devolve a Modalidade acrescentada e o que foi digitado nela", async () => {
  const armazem = new Armazem();
  await preencherSemEnviar(armazem);

  const { formulario } = voltarERestaurar(armazem);

  assert.equal(campo(formulario, "modalidade-0-7-code")?.value, "PPP");
  assert.equal(campo(formulario, "modalidade-0-7-percentage")?.value, "25");
  assert.equal(campo(formulario, "perfil-0-name").value, "O que a pessoa digitou");
});

test("restaurar devolve a opção escolhida no rádio, e não a que o servidor marcou", async () => {
  const armazem = new Armazem();
  await preencherSemEnviar(armazem);

  const { formulario } = voltarERestaurar(armazem);

  assert.equal(escolhido(formulario, "perfil-0-reserveType"), "LIMITED");
  const opcoes = formulario.elements.filter((item) => item.name === "perfil-0-reserveType");
  assert.deepEqual(
    opcoes.map((item) => item.value),
    ["NONE", "LIMITED"],
    "o valor de cada opção continua sendo a opção que ela representa"
  );
});

test("a lista restaurada passa pelo htmx, e os botões dela não ficam inertes", async () => {
  const armazem = new Armazem();
  await preencherSemEnviar(armazem);

  const { lista, processadas } = voltarERestaurar(armazem);

  assert.deepEqual(processadas, [lista]);
});

test("o autosave depois de restaurar guarda a Modalidade, e não regrava a perda", async () => {
  const armazem = new Armazem();
  await preencherSemEnviar(armazem);
  const { formulario } = voltarERestaurar(armazem);

  // No navegador é a mutação da lista que agenda a gravação; o shim não observa mutação.
  formulario.disparar("change");
  await esperar();

  const regravado = JSON.parse(armazem.getItem(CHAVE));
  assert.deepEqual(regravado.copia.valores["modalidade-0-7-code"], ["PPP"]);
});
