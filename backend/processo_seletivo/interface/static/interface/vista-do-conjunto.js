/* A visão do conjunto e um cartão à vista por vez — o que as etapas Perfis (052) e Classificação
   (053) fazem igual.

   **Isto é uma vista, e não um formulário** (D-001 das duas specs). Os cartões continuam todos na
   lista, com todo o conteúdo, e continuam indo em todo envio da etapa; o que está fora de vista
   recebe `hidden`, e nada mais. Este script não cria, move, clona nem remove controle com `name` —
   é o que torna o envio o mesmo com a vista e sem ela, e o que deixa intactos o duplicar da 043, o
   gesto da 051, os fragmentos que o htmx reconstrói e o rascunho local. A gravação continua
   substituindo o rascunho inteiro; um editor que carregasse e gravasse um cartão por vez reabriria as
   decisões que existem por causa disso.

   **Saiu do `perfis.js` quando a segunda tela entrou**, como a 052 previu. O que ficou aqui é o que
   custou percurso no navegador e que duas cópias deixariam divergir: o campo inválido escondido, o
   fragmento do endereço, a rolagem ao carregar. O que **não** está aqui é o que a linha lê: cada tela
   declara as colunas e como ler um cartão, e este script não sabe o que é Perfil, marco ou
   Modalidade. Não há API para criar, remover ou reordenar item — não é componente de coleção.

   **O modo de falha que decide se isto funciona é o campo inválido escondido.** O navegador recusa o
   envio e não consegue focar um campo dentro de `hidden` nem de `details` fechado: o operador clica
   *Salvar* e nada acontece. A 030 pagou por isso nos blocos do marco. O ouvinte de `invalid`, em
   captura, abre o cartão — e o bloco — antes de o navegador procurar onde mostrar a mensagem.

   As regras puras vêm primeiro e são exportadas para `node --test`; o resto é a montagem, que o shim
   não reproduz e que se verifica no navegador (quickstart.md das duas specs). */
(function () {
  "use strict";

  /* ── Regras ──────────────────────────────────────────────────────────────────────────────── */

  /** Dois fatos, em texto (D-003): as pendências que o cartão tem por objeto, e se difere do gravado. */
  function situacao(pendencias, alterado) {
    var quantas = parseInt(pendencias, 10) || 0;
    var partes = [
      quantas === 0 ? "sem pendência" : quantas === 1 ? "1 pendência" : quantas + " pendências",
    ];
    if (alterado) partes.push("alterado — não salvo");
    return partes.join(" · ");
  }

  /** Qual cartão abre quando a etapa carrega (FR-953 da 052, FR-971 da 053). `null` é nenhum. */
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

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  /** Monta a vista sobre a lista de cartões que a tela declara (contracts/tela-da-etapa.md, 053). */
  function montar(config) {
    var formulario = config.formulario;
    var lista = config.lista;
    var lugar = config.lugar;
    var contador = config.contador;
    var CARTAO = ":scope > " + config.item;
    var COLUNAS = config.colunas;
    var novos = new WeakSet();
    var mexidos = new WeakSet();
    var aberto = null;
    var corpo = null;
    var editor = montarEditor();

    function cartoes() {
      return [].slice.call(lista.querySelectorAll(CARTAO));
    }

    function donoDe(no) {
      var cartao = no && no.closest && no.closest(config.item);
      return cartao && cartao.parentNode === lista ? cartao : null;
    }

    /* Difere do gravado (FR-949 da 052, FR-967 da 053): o servidor diz quando devolveu o digitado;
       a tela sabe o resto — o controle mexido, o cartão que nasceu aqui, o item que entrou ou saiu. */
    function alterado(cartao) {
      if (cartao.hasAttribute("data-nao-salvo") || novos.has(cartao) || mexidos.has(cartao)) {
        return true;
      }
      return [].some.call(cartao.querySelectorAll("input, select, textarea"), function (controle) {
        // Os campos do *Duplicar* moram fora do formulário (`form=`), e não são do cartão.
        return controle.name && controle.form === formulario && controleAlterado(controle);
      });
    }

    function elemento(tag, texto, classe) {
      var no = document.createElement(tag);
      if (texto != null) no.textContent = texto;
      if (classe) no.className = classe;
      return no;
    }

    /* ── A tabela ── */

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
      var legenda = elemento("caption", config.legenda(todos.length));
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

    /* A célula de uma lista — os marcos de um Perfil — tem um bloco por item, na ordem do cartão, e
       o 1º de uma linha fica sobre o 1º das outras (R-002 da 053). */
    function preencherCelula(td, valor) {
      if (Array.isArray(valor)) {
        td.replaceChildren.apply(
          td,
          valor.map(function (item) {
            return elemento("div", item);
          })
        );
      } else {
        td.textContent = valor == null ? "" : valor;
      }
    }

    function preencherLinha(linha, cartao) {
      var lido = config.ler(cartao);
      var celulas = lido.celulas;
      celulas.situacao = situacao(cartao.dataset.pendencias, alterado(cartao));
      linha.firstChild.textContent = lido.codigo;
      COLUNAS.forEach(function (coluna, i) {
        var td = linha.children[i + 1];
        preencherCelula(td, celulas[coluna[0]]);
        if (coluna[0] === "situacao") {
          td.classList.toggle("situacao-pendente", celulas.situacao !== "sem pendência");
        }
      });
      var botao = linha.lastChild.firstChild;
      var emEdicao = cartao === aberto;
      // O nome acessível leva o código (UX-117 da 052, UX-124 da 053), e o texto visível diz qual
      // está aberto (UX-118, UX-125).
      botao.replaceChildren(
        emEdicao ? "Em edição" : "Editar",
        elemento("span", " " + lido.rotulo, "oculto")
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
      if (cartao === aberto) editor.titulo.textContent = "Editando " + config.ler(cartao).titulo;
    }

    /* ── O editor ── */

    function montarEditor() {
      var cabecalho = elemento("div", null, "editor-do-perfil");
      cabecalho.hidden = true;
      var titulo = elemento("h3");
      titulo.id = lista.id + "-em-edicao";
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
      // Fora da lista: o `assistente.js` trata toda inserção em `#perfis` como linha nova e leva o
      // foco a ela.
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

    /* O cartão aberto mora no fragmento do endereço (R-007 da 052). O formulário não tem `action`,
       e o envio vai ao endereço do documento, fragmento incluso: a tela que volta sem gravar reabre o
       mesmo cartão sem campo novo no formulário — que o rascunho local tomaria por preenchimento.
       `salvo` e `aplicado` são notícias de uma vez, e saem do endereço junto. */
    function lembrar(cartao) {
      if (!window.history || !window.history.replaceState) return;
      // Com um cartão só não há o que lembrar: ele é sempre o aberto.
      if (cartao && cartoes().length <= 1) return;
      var endereco = new URL(window.location.href);
      endereco.searchParams.delete("salvo");
      endereco.searchParams.delete("aplicado");
      endereco.hash = cartao ? cartao.id : "";
      window.history.replaceState(window.history.state, "", endereco.toString());
    }

    /* ── O campo inválido escondido (FR-954 da 052, FR-972 da 053) ── */

    var rodada = false;
    formulario.addEventListener(
      "invalid",
      function (evento) {
        // Um cartão por rodada: a validação dispara `invalid` em cada controle, em ordem, e o
        // navegador mostra o primeiro. `setTimeout`, e não microtarefa: ela rodaria entre um
        // evento e outro da mesma rodada.
        if (rodada) return;
        rodada = true;
        window.setTimeout(function () {
          rodada = false;
        }, 0);
        var controle = evento.target;
        var cartao = donoDe(controle);
        if (cartao && cartao.hidden) abrir(cartao, { foco: false });
        // **E o bloco que fecha** (R-007 da 053). A 030 tirou dele todo `required`, mas não os
        // limites: o prazo do recurso tem `min=1`, e um `-1` digitado com o bloco aberto e o bloco
        // fechado depois é o mesmo envio recusado em silêncio.
        var bloco = controle.closest && controle.closest("details:not([open])");
        while (bloco) {
          bloco.open = true;
          bloco = bloco.parentNode && bloco.parentNode.closest("details:not([open])");
        }
      },
      true
    );

    /* ── O que acontece na lista ── */

    /* Um item que entrou ou saiu de dentro do cartão muda o cartão; o diálogo do *Duplicar*, que o
       htmx troca fora de banda, não: os campos dele moram fora do formulário (`form=`). O nó
       removido já não tem `form`, e por isso a pergunta é pelo atributo. */
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
      var cartao = donoDe(evento.target);
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
            if (no.nodeType === 1 && no.matches(config.item)) {
              novos.add(no);
              inserido = no;
              conjuntoMudou = true;
            }
          });
          [].forEach.call(registro.removedNodes, function (no) {
            if (no.nodeType === 1 && no.matches(config.item)) {
              conjuntoMudou = true;
              var linha = linhaDe(no);
              if (linha) posicaoDoRemovido = [].indexOf.call(corpo.children, linha);
              if (no === aberto) removidoAberto = no;
            }
          });
          return;
        }
        var cartao = donoDe(registro.target);
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
        // O foco no primeiro campo é do `assistente.js`, que já o põe ali (FR-956 da 052).
        abrir(inserido, { foco: false });
      } else if (todos.length === 1) {
        abrir(todos[0], { foco: false });
      } else {
        if (aberto) abrir(aberto, { foco: false });
        else mostrar(null);
        if (posicaoDoRemovido >= 0 && corpo) {
          // O foco vai ao *Editar* da linha que ocupou o lugar, ou da anterior (FR-958 da 052).
          var linha = corpo.children[Math.min(posicaoDoRemovido, corpo.children.length - 1)];
          if (linha && (document.activeElement === document.body || !document.activeElement)) {
            linha.lastChild.firstChild.focus();
          }
        }
      }
    }).observe(lista, { childList: true, subtree: true });

    /* ── Ao carregar ── */

    function alvoDoEndereco(hash) {
      if (!hash || hash.length < 2) return null;
      var alvo = document.getElementById(decodeURIComponent(hash.slice(1)));
      return alvo && lista.contains(alvo) ? alvo : null;
    }

    /* O primeiro campo recusado pelo servidor. **O resumo da recusa primeiro**: é ele que diz qual
       é o primeiro, e na Classificação é o único que o diz — a recusa de marco não tem `.recusa`
       junto do campo, só a âncora (R-006 da 053). Na etapa Perfis os dois apontam o mesmo cartão. */
    function recusadoAoCarregar(todos) {
      var links = document.querySelectorAll('.erro[role=alert] a[href^="#"]');
      for (var i = 0; i < links.length; i++) {
        var dono = donoDe(alvoDoEndereco(links[i].getAttribute("href")));
        if (dono) return { cartao: dono, alvo: alvoDoEndereco(links[i].getAttribute("href")) };
      }
      var comRecusa = todos.find(function (cartao) {
        return cartao.querySelector(".recusa");
      });
      return comRecusa ? { cartao: comRecusa, alvo: comRecusa.querySelector(".recusa") } : null;
    }

    montarTabela();
    var todos = cartoes();
    var recusa = recusadoAoCarregar(todos);
    var alvo = alvoDoEndereco(window.location.hash);
    var apontado = alvo ? todos.indexOf(donoDe(alvo)) : -1;
    var consulta = new URLSearchParams(window.location.search);
    var indice = cartaoAAbrir({
      quantos: todos.length,
      recusado: recusa ? todos.indexOf(recusa.cartao) : null,
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
          document.querySelector(config.noticia);
        // O endereço que aponta o **cartão**, e não um campo dentro dele, é o de quem estava
        // editando: o que se mostra é o título do editor, no alto. Centralizar o cartão — 1,6 mil
        // px na Classificação — deixava o título 350 px acima da tela (053, medido no preview).
        var campoApontado = apontado === indice && alvo !== todos[indice] && alvo;
        var mostrado =
          noticia ||
          (recusa && recusa.cartao === todos[indice] && recusa.alvo) ||
          campoApontado ||
          editor.titulo;
        // Depois do `load`: o navegador refaz a rolagem até o fragmento enquanto a página carrega,
        // e a nossa precisa ser a última.
        var posicionar = function () {
          mostrado.scrollIntoView({
            block: noticia || mostrado === editor.titulo ? "start" : "center",
          });
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
      var destino = alvoDoEndereco(window.location.hash);
      var cartao = donoDe(destino);
      if (!cartao) return;
      if (cartao.hidden) abrir(cartao, { foco: false });
      var bloco = destino.closest("details:not([open])");
      while (bloco) {
        bloco.open = true;
        bloco = bloco.parentNode && bloco.parentNode.closest("details:not([open])");
      }
      destino.scrollIntoView({ block: "center" });
      if (destino.focus) destino.focus();
    });

    /* O que a tela pode pedir depois de montada: reler todas as linhas, quando muda algo que elas
       leem e que mora fora dos cartões — o método comum do sorteio, na Classificação (053). */
    return {
      atualizarTodas: function () {
        cartoes().forEach(atualizar);
      },
    };
  }

  var api = {
    situacao: situacao,
    cartaoAAbrir: cartaoAAbrir,
    controleAlterado: controleAlterado,
    montar: montar,
  };
  if (typeof module === "object" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.VistaDoConjunto = api;
})();
