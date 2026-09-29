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
    { rascunho: "edital:perfis:ana", lista: "#perfis", fragmento: "/fragmentos/perfil" }
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
    campos: Object.prototype.hasOwnProperty.call(opcoes, "campos")
      ? opcoes.campos
      : [
          ["perfil-0-id", "p1"],
          ["perfil-0-code", "P1"],
          ["perfil-0-name", "O que a pessoa digitou e não enviou"],
        ],
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

   A outra metade, `preencher`, restaurava escrevendo no `value` do rádio — e `value`, no rádio, é
   a opção que ele **representa**, não a escolhida. Ela deixou de existir com o RC-08: quem
   remonta a tela é o servidor, e a marcação volta como volta de uma recusa. */

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
    { rascunho: "edital:etapas:ana", lista: "#etapas", fragmento: "/fragmentos/etapa" }
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

/* RC-08 da auditoria de consolidação (AX-16 de 15/09) — restaurar perdia o que era aninhado.

   A restauração remontava cada linha a partir do fragmento **vazio** do Perfil e casava os nomes
   pela forma de três segmentos: Modalidade, fato, linha do quadro e marcos em trânsito não tinham
   onde cair e sumiam em silêncio; o HTML inserido não passava pelo htmx, e os botões de acrescentar
   ficavam inertes; e o autosave regravava o que restou por cima do guardado. Medido pela tela em
   28/09: `PPIQ` guardada, zero campos de Modalidade restaurados, `PPIQ` fora do armazenamento logo
   depois.

   Agora o guardado leva os campos **como o formulário os enviaria**, e restaurar é enviá-los ao
   servidor pedindo só reexibição. O que estes testes provam é o lado do script — o que é guardado
   e o que é enviado; o lado do servidor está em `tests/interface/test_rascunho_local.py`. */

function comModalidade() {
  const csrf = new Elemento("fieldset");
  const token = new Elemento("input", { name: "csrfmiddlewaretoken", value: "tok", type: "hidden" });
  token.parentNode = csrf;
  csrf.filhos.push(token);
  csrf.classes = [];
  return new Formulario(
    [
      csrf,
      linha("perfil", 0, { id: "p1", code: "LP99", name: "Professor de Libras" }),
      linha("modalidade", "0-31", { code: "PPIQ", percentage: "30" }),
      linha("perfil", 0, {
        reserveType: [
          { type: "radio", value: "NONE", checked: true },
          { type: "radio", value: "LIMITED", checked: false },
        ],
      }),
    ],
    { rascunho: "edital:perfis:ana", lista: "#perfis" }
  );
}

test("o guardado leva os campos aninhados com o nome com que o formulário os envia", async () => {
  const formulario = comModalidade();
  const armazem = new Armazem();
  montar({ formulario, armazem });
  carregar(SCRIPT);
  formulario.elements.find((campo) => campo.name === "modalidade-0-31-code").value = "PPIQ2";
  formulario.disparar("input");
  await new Promise((pronto) => setTimeout(pronto, 450));

  const campos = JSON.parse(armazem.getItem(CHAVE)).campos;
  assert.deepEqual(
    campos.filter(([nome]) => nome.startsWith("modalidade-")),
    [
      ["modalidade-0-31-code", "PPIQ2"],
      ["modalidade-0-31-percentage", "30"],
    ]
  );
  // O rádio vai como o navegador o envia — só o marcado —, e o token não é guardado: ele é da
  // sessão em que a página foi aberta, e restaurar usa o da tela atual.
  assert.deepEqual(
    campos.filter(([nome]) => nome.endsWith("-reserveType")),
    [["perfil-0-reserveType", "NONE"]]
  );
  assert.equal(
    campos.some(([nome]) => nome === "csrfmiddlewaretoken"),
    false
  );
});

/** Carrega com um guardado, e devolve o que o script criou — o botão e o envio. */
function restaurando(bruto, { restaurado = false } = {}) {
  const armazem = new Armazem({ [CHAVE]: bruto });
  montar({ formulario: comModalidade(), armazem, restaurado });
  globalThis.window.location = { pathname: "/gestao/editais/e/compor/perfis" };
  const criados = [];
  const criar = globalThis.document.createElement;
  globalThis.document.createElement = (tag) => {
    const elemento = criar(tag);
    if (tag === "form") elemento.submit = () => (elemento.enviado = true);
    criados.push(elemento);
    return elemento;
  };
  carregar(SCRIPT);
  const botao = criados.find((e) => e.textContent === "Restaurar o que eu havia digitado");
  return { armazem, criados, botao };
}

test("restaurar envia ao servidor o que foi guardado, com os aninhados", () => {
  const campos = [
    ["perfil-0-code", "LP99"],
    ["modalidade-0-31-code", "PPIQ"],
    ["fato-0-52-code", "NASCIMENTO"],
    ["perfil-0-marcosEmTransito", "[]"],
  ];
  const { criados, botao } = restaurando(guardado(60_000, { campos }));
  botao.disparar("click");

  const envio = criados.find((e) => e.tagName === "form");
  assert.equal(envio.enviado, true);
  assert.equal(envio.getAttribute("method"), "post");
  // O caminho, e não o endereço inteiro: `?salvo=` na tela atual faria a resposta trazer um recibo
  // de gravação que não aconteceu.
  assert.equal(envio.getAttribute("action"), "/gestao/editais/e/compor/perfis");
  const enviados = envio.filhos.map((campo) => [campo.getAttribute("name"), campo.value]);
  assert.deepEqual(enviados, [
    ["csrfmiddlewaretoken", "tok"],
    ["restaurar", "1"],
    ...campos,
  ]);
});

test("guardado sem os campos de envio é descartado, e não oferecido pela metade", () => {
  const { armazem, botao } = restaurando(guardado(60_000, { campos: undefined }));

  assert.equal(botao, undefined);
  assert.equal(armazem.getItem(CHAVE), null);
});

test("a tela restaurada não oferece de novo, e não apaga o guardado", () => {
  const { armazem, botao } = restaurando(guardado(60_000), { restaurado: true });

  // O que está na tela ainda não chegou ao servidor: apagar o guardado aqui seria a perda de
  // antes, só que um passo depois.
  assert.equal(botao, undefined);
  assert.notEqual(armazem.getItem(CHAVE), null);
});
