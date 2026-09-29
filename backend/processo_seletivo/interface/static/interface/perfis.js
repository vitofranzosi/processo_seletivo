/* A visão do conjunto dos Perfis e um cartão à vista por vez (052).

   **Isto é uma vista, e não um formulário** (D-001 da spec). Os cartões continuam todos em
   `#perfis`, com todo o conteúdo, e continuam indo em todo envio da etapa; o que está fora de
   vista recebe `hidden`, e nada mais. Este script não cria, move, clona nem remove controle com
   `name` — é o que torna o envio o mesmo com a vista e sem ela, e o que deixa intactos o duplicar
   da 043, o gesto da 051, o quadro que o htmx reconstrói e o rascunho local. A gravação continua
   substituindo o rascunho inteiro; um editor que carregasse e gravasse um Perfil por vez reabriria
   as três decisões que existem por causa disso.

   **A linha é leitura do cartão.** Um desenho da linha no servidor e outro aqui envelheceriam
   separados; por isso a tabela só existe onde este script existe, como o filtro da Retificação. O
   servidor entrega o que a tela não sabe: `data-pendencias` e `data-nao-salvo` no cartão, e as
   frases curtas em `data-resumo`, que mantêm o vocabulário no template.

   **O modo de falha que decide se isto funciona é o campo inválido escondido.** O navegador recusa
   o envio e não consegue focar um campo dentro de `hidden`: o operador clica *Salvar* e nada
   acontece. A 030 pagou por isso nos blocos do marco. O ouvinte de `invalid`, em captura, abre o
   cartão antes de o navegador procurar onde mostrar a mensagem.

   As regras puras vêm primeiro e são exportadas para `node --test`; o resto é a montagem, que o
   shim não reproduz e que se verifica no navegador (quickstart.md). */
(function () {
  "use strict";

  /* ── Regras ──────────────────────────────────────────────────────────────────────────────── */

  /** O texto das células de uma linha, a partir do que o cartão tem digitado. */
  function resumo(dados) {
    var reserva = dados.reserva || {};
    var modalidades = (dados.modalidades || []).filter(function (m) {
      return m.codigo;
    });
    return {
      codigo: dados.codigo || "sem código",
      perfil: [dados.denominacao, dados.localidade].filter(Boolean).join(" · "),
      vagas: dados.vagas === "" || dados.vagas == null ? "0" : String(dados.vagas),
      reserva:
        reserva.valor === "LIMITED" && reserva.limite
          ? reserva.resumo + " a " + reserva.limite
          : reserva.resumo || "",
      modalidades: modalidades.length
        ? modalidades
            .map(function (m) {
              return m.percentual ? m.codigo + " " + percentual(m.percentual) + "%" : m.codigo;
            })
            .join(" · ")
        : "nenhuma",
      convocacao: dados.convocacao || "",
      situacao: situacao(dados.pendencias, dados.alterado),
    };
  }

  /** `20.0000` → `20`, `12.5` → `12,5`: a gravação devolve o percentual com quatro casas. */
  function percentual(texto) {
    var numero = Number(String(texto).replace(",", "."));
    return isFinite(numero) ? String(numero).replace(".", ",") : texto;
  }

  /** Dois fatos, em texto (D-003): as pendências que o Perfil tem por objeto, e se difere do gravado. */
  function situacao(pendencias, alterado) {
    var quantas = parseInt(pendencias, 10) || 0;
    var partes = [
      quantas === 0 ? "sem pendência" : quantas === 1 ? "1 pendência" : quantas + " pendências",
    ];
    if (alterado) partes.push("alterado — não salvo");
    return partes.join(" · ");
  }

  /** Qual cartão abre quando a etapa carrega (FR-953). `null` é nenhum. */
  function cartaoAAbrir(estado) {
    if (estado.quantos === 1) return 0;
    if (estado.recusado != null) return estado.recusado;
    if (estado.apontado != null && !estado.gravou) return estado.apontado;
    return null;
  }

  /** O controle difere do que a página trouxe? Oculto e botão não contam: não são digitados. */
  function controleAlterado(controle) {
    var tipo = controle.type;
    if (tipo === "hidden" || tipo === "submit" || tipo === "button") return false;
    if (tipo === "checkbox" || tipo === "radio") return controle.checked !== controle.defaultChecked;
    if (controle.options && !controle.multiple) {
      // Sem opção marcada no HTML, a escolhida ao carregar é a primeira — e comparar opção a
      // opção acusaria alteração em todo `select` que nasce no vazio.
      var inicial = 0;
      [].forEach.call(controle.options, function (opcao, i) {
        if (opcao.defaultSelected) inicial = i;
      });
      return controle.selectedIndex !== inicial;
    }
    if (controle.options) {
      return [].some.call(controle.options, function (opcao) {
        return opcao.selected !== opcao.defaultSelected;
      });
    }
    return controle.value !== controle.defaultValue;
  }

  var regras = {
    percentual: percentual,
    resumo: resumo,
    situacao: situacao,
    cartaoAAbrir: cartaoAAbrir,
    controleAlterado: controleAlterado,
  };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var formulario = document.getElementById("formulario");
  var lista = document.getElementById("perfis");
  var lugar = document.getElementById("visao-dos-perfis");
  if (!formulario || !lista || !lugar) return;

  var contador = document.querySelector('[data-contador="#perfis"]');
  var novos = new WeakSet();
  var mexidos = new WeakSet();
  var aberto = null;
  var corpo = null;
  var editor = montarEditor();

  function cartoes() {
    return [].slice.call(lista.querySelectorAll(":scope > fieldset.perfil"));
  }

  function campo(cartao, sufixo) {
    return cartao.querySelector('[name^="perfil-"][name$="-' + sufixo + '"]');
  }

  function valor(cartao, sufixo) {
    var controle = campo(cartao, sufixo);
    return controle ? String(controle.value || "").trim() : "";
  }

  function lerCartao(cartao) {
    var marcada = cartao.querySelector('[name^="perfil-"][name$="-reserveType"]:checked');
    var forma = campo(cartao, "callForm");
    return {
      codigo: valor(cartao, "code"),
      denominacao: valor(cartao, "name"),
      localidade: valor(cartao, "locality"),
      vagas: valor(cartao, "immediateVacancies"),
      reserva: {
        valor: marcada ? marcada.value : "",
        resumo: marcada ? marcada.dataset.resumo || "" : "",
        limite: valor(cartao, "reserveLimit"),
      },
      convocacao: forma
        ? forma.getAttribute("data-resumo-" + (forma.value || "nenhuma").toLowerCase()) || ""
        : "",
      modalidades: [].map.call(cartao.querySelectorAll("fieldset.modalidade"), function (m) {
        var codigo = m.querySelector('[name$="-code"]');
        var percentual = m.querySelector('[name$="-percentage"]');
        return {
          codigo: codigo ? codigo.value.trim() : "",
          percentual: percentual ? percentual.value.trim() : "",
        };
      }),
      pendencias: cartao.dataset.pendencias,
      alterado: alterado(cartao),
    };
  }

  /* Difere do gravado (FR-949): o servidor diz quando devolveu o digitado; a tela sabe o resto —
     o controle mexido, o cartão que nasceu aqui, a Modalidade ou o fato que entrou ou saiu. */
  function alterado(cartao) {
    if (cartao.hasAttribute("data-nao-salvo") || novos.has(cartao) || mexidos.has(cartao)) return true;
    return [].some.call(cartao.querySelectorAll("input, select, textarea"), function (controle) {
      // Os campos do *Duplicar* moram fora do formulário (`form=`), e não são do Perfil.
      return controle.name && controle.form === formulario && controleAlterado(controle);
    });
  }

  function identificacao(dados) {
    var complemento = dados.localidade || dados.denominacao;
    if (!dados.codigo) return "Perfil novo";
    return complemento ? dados.codigo + " — " + complemento : dados.codigo;
  }

  /* ── A tabela ── */

  var COLUNAS = [
    ["perfil", "Perfil"],
    ["vagas", "Vagas imediatas", "numero"],
    ["reserva", "Cadastro reserva"],
    ["modalidades", "Modalidades"],
    ["convocacao", "Convocação"],
    ["situacao", "Situação"],
  ];

  function elemento(tag, texto, classe) {
    var no = document.createElement(tag);
    if (texto != null) no.textContent = texto;
    if (classe) no.className = classe;
    return no;
  }

  function montarTabela() {
    var todos = cartoes();
    var visivel = todos.length > 1;
    lugar.hidden = !visivel;
    if (contador) contador.hidden = visivel;
    lugar.replaceChildren();
    corpo = null;
    if (!visivel) return;

    var rolavel = elemento("div", null, "tabela-rolavel");
    var tabela = elemento("table");
    var legenda = elemento("caption", "Perfis deste Edital (" + todos.length + ")");
    var cabeca = elemento("thead");
    var linhaDoCabecalho = elemento("tr");
    var codigo = elemento("th", "Código");
    codigo.scope = "col";
    linhaDoCabecalho.append(codigo);
    COLUNAS.forEach(function (coluna) {
      var th = elemento("th", coluna[1], coluna[2]);
      th.scope = "col";
      linhaDoCabecalho.append(th);
    });
    var acoes = elemento("th");
    acoes.scope = "col";
    acoes.append(elemento("span", "Ações", "oculto"));
    linhaDoCabecalho.append(acoes);
    cabeca.append(linhaDoCabecalho);
    corpo = elemento("tbody");
    todos.forEach(function (cartao) {
      corpo.append(montarLinha(cartao));
    });
    tabela.append(legenda, cabeca, corpo);
    rolavel.append(tabela);
    lugar.append(rolavel);
  }

  function montarLinha(cartao) {
    var linha = elemento("tr");
    linha.dataset.cartao = cartao.id;
    var cabecalho = elemento("th");
    cabecalho.scope = "row";
    linha.append(cabecalho);
    COLUNAS.forEach(function (coluna) {
      linha.append(elemento("td", null, coluna[2]));
    });
    var celula = elemento("td");
    var botao = elemento("button", null, "acao");
    botao.type = "button";
    botao.addEventListener("click", function () {
      abrir(cartao, { foco: true });
    });
    celula.append(botao);
    linha.append(celula);
    preencherLinha(linha, cartao);
    return linha;
  }

  function preencherLinha(linha, cartao) {
    var celulas = resumo(lerCartao(cartao));
    var th = linha.firstChild;
    th.textContent = celulas.codigo;
    COLUNAS.forEach(function (coluna, i) {
      var td = linha.children[i + 1];
      td.textContent = celulas[coluna[0]];
      if (coluna[0] === "situacao") {
        td.classList.toggle("situacao-pendente", celulas.situacao !== "sem pendência");
      }
    });
    var botao = linha.lastChild.firstChild;
    var emEdicao = cartao === aberto;
    // O nome acessível leva o código (UX-117), e o texto visível diz qual está aberto (UX-118).
    botao.replaceChildren(
      emEdicao ? "Em edição" : "Editar",
      elemento("span", " " + (celulas.codigo === "sem código" ? "Perfil novo" : celulas.codigo), "oculto")
    );
    if (emEdicao) linha.setAttribute("aria-current", "true");
    else linha.removeAttribute("aria-current");
  }

  function linhaDe(cartao) {
    if (!corpo) return null;
    return [].find.call(corpo.children, function (linha) {
      return linha.dataset.cartao === cartao.id;
    });
  }

  function atualizar(cartao) {
    var linha = linhaDe(cartao);
    if (linha) preencherLinha(linha, cartao);
    if (cartao === aberto) editor.titulo.textContent = "Editando " + identificacao(lerCartao(cartao));
  }

  /* ── O editor ── */

  function montarEditor() {
    var cabecalho = elemento("div", null, "editor-do-perfil");
    cabecalho.hidden = true;
    var titulo = elemento("h3");
    titulo.id = "editando-o-perfil";
    titulo.tabIndex = -1;
    var anterior = elemento("button", "← Anterior", "acao");
    var proximo = elemento("button", "Próximo →", "acao");
    var voltar = elemento("button", "Voltar à lista", "acao");
    [anterior, proximo, voltar].forEach(function (botao) {
      botao.type = "button";
    });
    anterior.addEventListener("click", function () {
      vizinho(-1);
    });
    proximo.addEventListener("click", function () {
      vizinho(1);
    });
    voltar.addEventListener("click", voltarALista);
    cabecalho.append(titulo, anterior, proximo, voltar);
    // Fora de `#perfis`: o `assistente.js` trata toda inserção ali como linha nova e leva o foco a ela.
    lista.parentNode.insertBefore(cabecalho, lista);
    return { cabecalho: cabecalho, titulo: titulo, anterior: anterior, proximo: proximo };
  }

  function mostrar(cartaoVisivel) {
    var todos = cartoes();
    var umSo = todos.length <= 1;
    todos.forEach(function (cartao) {
      cartao.hidden = !umSo && cartao !== cartaoVisivel;
    });
    editor.cabecalho.hidden = umSo || !cartaoVisivel;
  }

  function abrir(cartao, opcoes) {
    var anteriorAberto = aberto;
    aberto = cartao;
    mostrar(cartao);
    var todos = cartoes();
    var posicao = todos.indexOf(cartao);
    editor.anterior.disabled = posicao <= 0;
    editor.proximo.disabled = posicao >= todos.length - 1;
    if (anteriorAberto && anteriorAberto !== cartao) atualizar(anteriorAberto);
    atualizar(cartao);
    lembrar(cartao);
    if (opcoes && opcoes.foco && !editor.cabecalho.hidden) editor.titulo.focus();
  }

  function vizinho(passo) {
    var todos = cartoes();
    var destino = todos[todos.indexOf(aberto) + passo];
    if (destino) abrir(destino, { foco: true });
  }

  function voltarALista() {
    var saiu = aberto;
    fechar();
    var linha = saiu && linhaDe(saiu);
    if (linha) linha.lastChild.firstChild.focus();
  }

  function fechar() {
    var saiu = aberto;
    aberto = null;
    mostrar(null);
    if (saiu) atualizar(saiu);
    lembrar(null);
  }

  /* O cartão aberto mora no fragmento do endereço (R-007). O formulário não tem `action`, e o envio
     vai ao endereço do documento, fragmento incluso: a tela que volta sem gravar reabre o mesmo
     Perfil sem campo novo no formulário — que o rascunho local tomaria por preenchimento. `salvo`
     e `aplicado` são notícias de uma vez, e saem do endereço junto. */
  function lembrar(cartao) {
    if (!window.history || !window.history.replaceState) return;
    // Com um Perfil só não há o que lembrar: ele é sempre o aberto.
    if (cartao && cartoes().length <= 1) return;
    var endereco = new URL(window.location.href);
    endereco.searchParams.delete("salvo");
    endereco.searchParams.delete("aplicado");
    endereco.hash = cartao ? cartao.id : "";
    window.history.replaceState(window.history.state, "", endereco.toString());
  }

  /* ── O campo inválido escondido (FR-954, R-002) ── */

  var rodada = false;
  formulario.addEventListener(
    "invalid",
    function (evento) {
      // Um cartão por rodada: a validação dispara `invalid` em cada controle, em ordem, e o
      // navegador mostra o primeiro. `setTimeout`, e não microtarefa: ela rodaria entre um evento
      // e outro da mesma rodada.
      if (rodada) return;
      rodada = true;
      window.setTimeout(function () {
        rodada = false;
      }, 0);
      var cartao = evento.target.closest && evento.target.closest("#perfis > fieldset.perfil");
      if (cartao && cartao.hidden) abrir(cartao, { foco: false });
    },
    true
  );

  /* ── O que acontece em `#perfis` ── */

  /* Uma Modalidade, um fato ou uma linha do quadro que entrou ou saiu muda o Perfil; o diálogo do
     *Duplicar*, que o htmx troca fora de banda, não: os campos dele moram fora do formulário
     (`form=`). O nó removido já não tem `form`, e por isso a pergunta é pelo atributo. */
  function trazCampoDoFormulario(no) {
    if (no.nodeType !== 1) return false;
    var campos = no.matches("input, select, textarea")
      ? [no]
      : [].slice.call(no.querySelectorAll("input, select, textarea"));
    return campos.some(function (c) {
      return c.name && !c.hasAttribute("form");
    });
  }

  function aoDigitar(evento) {
    var cartao = evento.target.closest && evento.target.closest("#perfis > fieldset.perfil");
    if (cartao) atualizar(cartao);
  }
  lista.addEventListener("input", aoDigitar);
  lista.addEventListener("change", aoDigitar);

  new MutationObserver(function (registros) {
    var conjuntoMudou = false;
    var inserido = null;
    var removidoAberto = null;
    var posicaoDoRemovido = -1;
    registros.forEach(function (registro) {
      if (registro.target === lista) {
        [].forEach.call(registro.addedNodes, function (no) {
          if (no.nodeType === 1 && no.matches("fieldset.perfil")) {
            novos.add(no);
            inserido = no;
            conjuntoMudou = true;
          }
        });
        [].forEach.call(registro.removedNodes, function (no) {
          if (no.nodeType === 1 && no.matches("fieldset.perfil")) {
            conjuntoMudou = true;
            var linha = linhaDe(no);
            if (linha) posicaoDoRemovido = [].indexOf.call(corpo.children, linha);
            if (no === aberto) removidoAberto = no;
          }
        });
        return;
      }
      var cartao = registro.target.closest && registro.target.closest("#perfis > fieldset.perfil");
      if (!cartao) return;
      var nos = [].concat([].slice.call(registro.addedNodes), [].slice.call(registro.removedNodes));
      if (nos.some(trazCampoDoFormulario)) mexidos.add(cartao);
      atualizar(cartao);
    });
    if (!conjuntoMudou) return;
    if (removidoAberto) {
      aberto = null;
      lembrar(null);
    }
    montarTabela();
    var todos = cartoes();
    if (inserido) {
      // O foco no primeiro campo é do `assistente.js`, que já o põe ali (FR-956).
      abrir(inserido, { foco: false });
    } else if (todos.length === 1) {
      abrir(todos[0], { foco: false });
    } else {
      if (aberto) abrir(aberto, { foco: false });
      else mostrar(null);
      if (posicaoDoRemovido >= 0 && corpo) {
        // O foco vai ao *Editar* da linha que ocupou o lugar, ou da anterior (FR-958).
        var linha = corpo.children[Math.min(posicaoDoRemovido, corpo.children.length - 1)];
        if (linha && (document.activeElement === document.body || !document.activeElement)) {
          linha.lastChild.firstChild.focus();
        }
      }
    }
  }).observe(lista, { childList: true, subtree: true });

  /* ── Ao carregar ── */

  montarTabela();
  var todos = cartoes();
  var recusado = todos.findIndex(function (cartao) {
    return cartao.querySelector(".recusa");
  });
  var apontado = -1;
  if (window.location.hash.length > 1) {
    var alvo = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    var dono = alvo && lista.contains(alvo) && alvo.closest("#perfis > fieldset.perfil");
    apontado = dono ? todos.indexOf(dono) : -1;
  }
  var consulta = new URLSearchParams(window.location.search);
  var indice = cartaoAAbrir({
    quantos: todos.length,
    recusado: recusado >= 0 ? recusado : null,
    apontado: apontado >= 0 ? apontado : null,
    gravou: consulta.has("salvo") || consulta.has("aplicado"),
  });
  if (indice == null) {
    fechar();
  } else {
    abrir(todos[indice], { foco: false });
    if (todos.length > 1) {
      // Depois de um envio que não gravou, a notícia é o que ele trouxe no alto — a prévia, a
      // recusa, o aviso do preenchimento —, e o cartão reaberto não a tira de vista. O navegador
      // já rolou até o fragmento; é isso que se desfaz.
      var noticia =
        lugar.hasAttribute("data-devolvido") &&
        document.querySelector(
          "#previa-da-aplicacao, .erro[role=alert], #formulario .aviso[role=status]"
        );
      var mostrado =
        noticia ||
        todos[indice].querySelector(".recusa") ||
        (apontado === indice && alvo) ||
        editor.titulo;
      // Depois do `load`: o navegador refaz a rolagem até o fragmento enquanto a página carrega,
      // e a nossa precisa ser a última.
      var posicionar = function () {
        mostrado.scrollIntoView({ block: noticia ? "start" : "center" });
      };
      if (document.readyState === "complete") posicionar();
      else
        window.addEventListener("load", function () {
          // `setTimeout`, e não `requestAnimationFrame`, que não roda em aba de fundo.
          window.setTimeout(posicionar, 0);
        });
    }
  }

  /* Um link da lista de recusas, ou qualquer âncora, para um campo de cartão fechado. */
  window.addEventListener("hashchange", function () {
    var destino = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    var cartao = destino && lista.contains(destino) && destino.closest("#perfis > fieldset.perfil");
    if (!cartao) return;
    if (cartao.hidden) abrir(cartao, { foco: false });
    destino.scrollIntoView({ block: "center" });
    if (destino.focus) destino.focus();
  });
})();
