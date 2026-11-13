/* Orientação dentro de uma Retificação longa.

   Um Edital institucional publicado rende sessenta linhas editáveis — Perfis com Modalidades,
   Marcos e Critérios, um Cronograma de doze Eventos, Etapas, Documentos, Anexos e as Seções do
   texto. A tela mostrava todas de uma vez, sem sumário, sem busca e sem qualquer distinção entre
   o campo que alguém acabou de alterar e os outros noventa. Quem retifica **um** prazo rolava a
   página inteira para achá-lo, e depois rolava de novo para conferir se tinha mexido no certo.

   Quatro coisas, e nada além:

   1. **O que já mudou fica marcado**, e em dois estados distintos (123, M2). «na proposta» vem do
      servidor: é o que o ato gravaria, e sobrevive à conferência. «alterada» é daqui: o campo que
      mudou nesta tela desde a última conferência — ou desde a abertura —, comparado com o valor que
      o servidor entregou. Não é validação e não bloqueia nada.
   2. **As duas contagens** aparecem na barra de ações, que acompanha a rolagem, uma frase por
      estado: o que a proposta contém, e o que mudou desde a conferência.
   3. **Uma busca por campo** (123, M1): pelo rótulo, pelo valor curto e pelo cartão, com a lista
      dos campos achados e o caminho até cada um. E o "só o que eu alterei".
   4. **O caminho de volta**: todo `a.ir-ao-campo` da tela — o da busca, o da linha do resumo e o do
      impeditivo — desesconde o que o filtro escondeu e põe o foco no campo.

   **O filtro nasce aqui, e não no template.** Sem script ele não filtraria nada, e um controle
   que existe no HTML e só funciona com JavaScript é pior que a ausência dele, porque promete. O
   sumário do topo, a marca «na proposta» e os links do resumo são o contrário: funcionam sem
   script, e por isso vêm do servidor.

   Filtrar **esconde**, e não remove: o campo escondido continua no formulário e continua sendo
   enviado. Esconder o que se envia mudaria a Retificação por causa de uma busca, que seria a
   pior coisa que uma lupa poderia fazer.

   **As regras ficam separadas da montagem**, como em `classificacao.js`: o que a busca acha e o que
   a barra diz são funções puras, exportadas para o teste em Node; o resto mexe no DOM, e é
   verificado no navegador. */
(function () {
  "use strict";

  /* ── Regras ──────────────────────────────────────────────────────────────────────────────── */

  // Abaixo disto o termo casa com quase tudo, e a lista seria a página inteira de novo (D-002).
  var LIMIAR = 2;
  // Cabe a lista de «vagas» do Edital ampliado (12) com folga; acima, refinar é mais rápido que ler.
  var TETO = 25;
  var TRECHO = 80;

  /** Caixa e acento não distinguem: «remuneracao» acha «Remuneração». */
  function normalizar(texto) {
    return String(texto || "")
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  /** As palavras do termo, ou nenhuma quando ele é curto demais para buscar. */
  function palavras(termo) {
    var limpo = normalizar(termo);
    if (limpo.length < LIMIAR) return [];
    return limpo.split(" ").filter(Boolean);
  }

  function trecho(valor) {
    var texto = String(valor || "").replace(/\s+/g, " ").trim();
    return texto.length > TRECHO ? texto.slice(0, TRECHO - 1) + "…" : texto;
  }

  /** O valor que a busca lê, ou "" quando o campo não se busca pelo valor (FR-3918, D-002).

      Só o texto curto e a escolha de uma lista de referência. Texto longo inundaria a lista — são
      dezessete Seções e as descrições —, e número, data e Sim/Não casariam com quase tudo. Esses
      continuam achados pelo rótulo e pelo cartão. */
  function valorElegivel(controle) {
    var tag = String(controle.tagName || "").toUpperCase();
    if (tag === "INPUT") return controle.type === "text" ? controle.value || "" : "";
    if (tag !== "SELECT") return "";
    var opcoes = [].slice.call(controle.options || []);
    var textos = opcoes.map(function (opcao) {
      return normalizar(opcao.textContent);
    });
    var simOuNao = textos.length === 2 && textos.indexOf("sim") >= 0 && textos.indexOf("nao") >= 0;
    if (simOuNao) return "";
    var escolhida = opcoes.filter(function (opcao) {
      return opcao.selected;
    })[0];
    return escolhida ? escolhida.textContent || "" : "";
  }

  function contem(texto, todas) {
    return todas.every(function (palavra) {
      return texto.indexOf(palavra) >= 0;
    });
  }

  function algumaEm(texto, todas) {
    return todas.some(function (palavra) {
      return texto.indexOf(palavra) >= 0;
    });
  }

  /** Os resultados de um termo sobre os cartões da tela (FR-3917 a FR-3920).

      `cartoes`: `[{ref, onde, contexto, campos: [{ref, rotulo, valor}]}]`, em que `contexto` é a
      seção, a legenda e o nome do cartão, e `valor` já é o elegível.

      **Dois tipos de resultado**, e um cartão produz um ou outro. O campo entra quando todas as
      palavras estão no contexto mais o campo **e** ao menos uma está no próprio campo — rótulo ou
      valor. O cartão entra uma vez quando todas as palavras estão no contexto e nenhum campo dele
      entrou. Sem a segunda condição, «vagas» casaria com a legenda "Linha do quadro de vagas" e
      listaria também a «Lista de concorrência» de cada linha, e o nome de um marco listaria os
      vinte e dois campos dele. */
  function buscar(termo, cartoes) {
    var todas = palavras(termo);
    if (!todas.length) return null;
    var resultados = [];
    var visiveis = {};
    cartoes.forEach(function (cartao) {
      var contexto = normalizar(cartao.contexto);
      var deCampo = 0;
      cartao.campos.forEach(function (campo) {
        var proprio = normalizar(campo.rotulo + " " + (campo.valor || ""));
        if (contem(contexto + " " + proprio, todas) && algumaEm(proprio, todas)) {
          deCampo += 1;
          resultados.push({
            tipo: "campo",
            cartao: cartao.ref,
            ref: campo.ref,
            onde: cartao.onde,
            rotulo: campo.rotulo,
            valor: trecho(campo.valor),
          });
        }
      });
      if (!deCampo && contem(contexto, todas)) {
        resultados.push({ tipo: "cartao", cartao: cartao.ref, ref: cartao.ref, onde: cartao.onde });
      }
      if (deCampo || resultados.length && resultados[resultados.length - 1].cartao === cartao.ref) {
        visiveis[cartao.ref] = true;
      }
    });
    return { resultados: resultados.slice(0, TETO), total: resultados.length, visiveis: visiveis };
  }

  /** A frase que conta os resultados, ou "" sem busca. */
  function fraseDosAchados(achados) {
    if (!achados) return "";
    if (!achados.total) return "Nenhum campo corresponde";
    if (achados.total > TETO) {
      return "Mostrando " + TETO + " de " + achados.total + " resultados — refine a busca";
    }
    var cartoes = Object.keys(achados.visiveis).length;
    return (
      (achados.total === 1 ? "1 resultado" : achados.total + " resultados") +
      " em " +
      (cartoes === 1 ? "1 cartão" : cartoes + " cartões")
    );
  }

  function plural(n, um, varios) {
    return n === 1 ? um : varios;
  }

  /** As duas frases da barra, uma por estado (FR-3930, contracts §1.5).

      `estado`: `{proposta, cartoes, remocoes, edicao, enviado, alterados}`. `proposta` é o
      `data-proposta` do servidor, ou `null` numa tela que não o declara — e então não há frase da
      proposta. A contagem é por campo; a proposta, por cartão (D-001). */
  function frasesDaBarra(estado) {
    var n = estado.alterados;
    var contagem;
    if (estado.enviado) {
      contagem =
        n === 0
          ? "Nenhuma alteração nova desde a última conferência"
          : "<strong>" + n + "</strong> " +
            plural(n, "campo alterado", "campos alterados") +
            " desde a última conferência";
    } else if (estado.edicao) {
      contagem =
        n === 0
          ? "Nenhuma alteração nova nesta edição"
          : "<strong>" + n + "</strong> " +
            plural(n, "campo alterado", "campos alterados") +
            " nesta edição";
    } else {
      contagem =
        n === 0
          ? "Nenhum campo alterado ainda"
          : "<strong>" + n + "</strong> " + plural(n, "campo alterado", "campos alterados");
    }

    var proposta = null;
    if (estado.proposta === "nao-conferida") proposta = "Proposta ainda não conferida";
    else if (estado.proposta === "recusada") {
      proposta = "Proposta não conferida — veja a recusa acima";
    } else if (estado.proposta === "conferida") {
      var c = estado.cartoes || 0;
      var r = estado.remocoes || 0;
      var remocoes = r === 1 ? "1 remoção já declarada" : r + " remoções já declaradas";
      if (c === 0 && r === 0) proposta = "Nenhuma alteração na proposta";
      else if (c === 0) proposta = remocoes + " na proposta";
      else {
        proposta =
          (c === 1 ? "1 cartão com alteração" : c + " cartões com alteração") + " na proposta";
        if (r) proposta += " e " + remocoes;
      }
    }
    return { contagem: contagem, proposta: proposta };
  }

  var regras = {
    LIMIAR: LIMIAR,
    TETO: TETO,
    normalizar: normalizar,
    palavras: palavras,
    valorElegivel: valorElegivel,
    buscar: buscar,
    fraseDosAchados: fraseDosAchados,
    frasesDaBarra: frasesDaBarra,
  };
  if (typeof module === "object" && module.exports) module.exports = regras;

  /* ── Montagem ────────────────────────────────────────────────────────────────────────────── */

  if (typeof document === "undefined") return;
  var form = document.getElementById("formulario-da-retificacao");
  if (!form) return;

  var IGNORADOS = ["hidden", "submit", "button", "reset"];
  /* A justificativa e a vigência descrevem o **ato**, e não o conteúdo do Edital. Contá-las como
     "campo alterado" faria a contagem dizer 1 quando nada do Edital mudou — e é justamente esse
     o caso que o servidor recusa com "nenhum campo foi alterado". */
  var FORA_DA_CONTA = ["justificativa", "vigencia"];

  function editaveis(raiz) {
    return [].filter.call(raiz.querySelectorAll("input, select, textarea"), function (campo) {
      if (IGNORADOS.indexOf(campo.type) >= 0) return false;
      return FORA_DA_CONTA.indexOf(campo.name) < 0;
    });
  }

  function tem(elemento, atributo) {
    return elemento.getAttribute(atributo) !== null;
  }

  /* Mudou em relação ao que o servidor entregou — e não em relação ao que estava aqui há um
     segundo. O ponto de comparação é o `default*` do DOM, que guarda o valor declarado no HTML e
     não acompanha a digitação. Depois de um envio o servidor reexibe o que foi digitado, e o
     digitado passa a **ser** o declarado: esta marca zera, e é o correto — ela diz o que mudou
     **desde a conferência**. O que o ato leva continua marcado pelo servidor, «na proposta». */
  function alterado(campo) {
    if (campo.type === "checkbox" || campo.type === "radio") {
      return campo.checked !== campo.defaultChecked;
    }
    if (campo.type === "file") return campo.files && campo.files.length > 0;
    if (String(campo.tagName).toUpperCase() === "SELECT") {
      return [].some.call(campo.options, function (opcao) {
        return opcao.selected !== opcao.defaultSelected;
      });
    }
    return campo.value !== campo.defaultValue;
  }

  function marcar(elemento, ligado) {
    if (ligado) elemento.setAttribute("data-alterado", "");
    else elemento.removeAttribute("data-alterado");
  }

  /* A palavra ao lado da borda verde. Cor sozinha não informa quem não a distingue (WCAG 1.4.1),
     e "alterada" na legenda é o que o leitor de tela anuncia ao entrar na linha. */
  function selo(linha, ligado) {
    var legenda = linha.querySelector(":scope > legend");
    if (!legenda) return;
    var atual = legenda.querySelector(".alterada");
    if (ligado && !atual) {
      var marca = document.createElement("span");
      marca.className = "alterada";
      marca.textContent = "alterada";
      legenda.appendChild(marca);
    } else if (!ligado && atual) {
      atual.remove();
    }
  }

  var barra = form.querySelector(".barra-de-acoes");
  var contagem = document.createElement("span");
  contagem.className = "contagem";
  /* `polite`: a contagem muda a cada tecla digitada, e `assertive` interromperia a leitura do
     próprio campo que se está preenchendo. A contagem é o primeiro filho da barra, como sempre foi;
     a frase da proposta vem depois dela. */
  contagem.setAttribute("aria-live", "polite");
  if (barra) barra.appendChild(contagem);
  var estadoDaProposta = null;
  if (barra && tem(form, "data-proposta")) {
    estadoDaProposta = document.createElement("span");
    estadoDaProposta.className = "estado-da-proposta";
    estadoDaProposta.setAttribute("aria-live", "polite");
    barra.appendChild(estadoDaProposta);
  }

  var filtro = null;
  var somenteAlteradas = null;
  var achados = null;
  var resultados = null;

  function recontar() {
    var total = 0;
    editaveis(form).forEach(function (campo) {
      var mudou = alterado(campo);
      if (mudou) total += 1;
      var celula = campo.closest(".campo") || campo.closest(".remover-linha");
      if (celula) marcar(celula, mudou);
    });

    [].forEach.call(form.querySelectorAll("fieldset.linha"), function (linha) {
      var mudou = editaveis(linha).some(alterado);
      marcar(linha, mudou);
      selo(linha, mudou);
    });

    /* "Nenhum campo alterado ainda" ao lado de "Criar Retificação (14 Alterações)" dizia o
       contrário do botão. Desde a `123` a barra diz as duas coisas separadas: o que a proposta
       contém, que veio do servidor, e o que mudou desde a conferência, que é desta tela. */
    var frases = frasesDaBarra({
      proposta: form.getAttribute("data-proposta"),
      cartoes: Number(form.getAttribute("data-proposta-cartoes") || 0),
      remocoes: Number(form.getAttribute("data-proposta-remocoes") || 0),
      edicao: form.getAttribute("data-modo") === "edicao",
      enviado: tem(form, "data-enviado") || tem(form, "data-conferido"),
      alterados: total,
    });
    if (frases.contagem.indexOf("<") >= 0) contagem.innerHTML = frases.contagem;
    else contagem.textContent = frases.contagem;
    if (estadoDaProposta) estadoDaProposta.textContent = frases.proposta || "";
    /* O recorte acompanha a contagem: com "só o que eu alterei" ligado, a linha que acabou de
       mudar precisa aparecer; e a linha recém-acrescentada por HTMX precisa reabrir a seção que
       o filtro havia fechado — sem isto ela nascia dentro de uma seção escondida. */
    aplicar();
    return total;
  }

  /* ── O caminho até o campo ────────────────────────────────────────────────────────────────── */

  /** Tira o `hidden` de tudo acima do alvo: o filtro pode ter escondido o cartão e a seção. */
  function desesconder(alvo) {
    for (var no = alvo; no && no !== document.body; no = no.parentNode) {
      if (no.hidden) no.hidden = false;
    }
  }

  /** Leva ao campo, ao cartão ou à seção, e põe o foco onde se digita (FR-3922). */
  function irAo(alvo) {
    desesconder(alvo);
    var tag = String(alvo.tagName || "").toUpperCase();
    var controle = ["INPUT", "SELECT", "TEXTAREA"].indexOf(tag) >= 0 ? alvo : editaveis(alvo)[0];
    if (alvo.scrollIntoView) alvo.scrollIntoView({ block: "center" });
    if (controle && controle.focus) controle.focus();
  }

  /* Um ouvinte só, no documento, para todo `a.ir-ao-campo`: o da busca, o do resumo e o do
     impeditivo. O link funciona sem script, como âncora; com script ele também desesconde e foca o
     controle. E não muda o endereço: a âncora na barra levaria a próxima conferência a abrir rolada
     até ela, longe do resumo. */
  document.addEventListener("click", function (evento) {
    var alvoDoClique = evento.target;
    var link = alvoDoClique && alvoDoClique.closest ? alvoDoClique.closest("a.ir-ao-campo") : null;
    if (!link) return;
    var href = link.getAttribute("href") || "";
    if (href.charAt(0) !== "#") return;
    var alvo = document.getElementById(href.slice(1));
    if (!alvo) return;
    evento.preventDefault();
    irAo(alvo);
  });

  /* ── A busca ─────────────────────────────────────────────────────────────────────────────── */

  function textoDe(no) {
    return no ? String(no.textContent || "").replace(/\s+/g, " ").trim() : "";
  }

  /** O cartão como a pessoa o vê: a categoria e o nome da legenda, sem os selos. */
  function legendaDe(linha) {
    var legenda = linha.querySelector(":scope > legend");
    if (!legenda) return "";
    var partes = [legenda.querySelector(".categoria"), legenda.querySelector(".nome")]
      .map(textoDe)
      .filter(Boolean);
    return partes.length ? partes.join(" ") : textoDe(legenda);
  }

  function rotuloDe(controle) {
    var celula = controle.closest(".campo") || controle.closest(".remover-linha");
    return textoDe(celula && celula.querySelector("label"));
  }

  /** Os cartões filtráveis, lidos **agora**: o valor é o digitado, e não o do carregamento. */
  function cartoesDaTela(so) {
    return [].filter
      .call(form.querySelectorAll("fieldset.linha[data-linha]"), function (linha) {
        return !so || tem(linha, "data-alterado") || tem(linha, "data-na-proposta");
      })
      .map(function (linha) {
        var secao = linha.closest(".secao-da-retificacao");
        var titulo = textoDe(secao && secao.querySelector("h2"));
        var legenda = legendaDe(linha);
        return {
          ref: linha.id,
          elemento: linha,
          onde: titulo ? titulo + " › " + legenda : legenda,
          contexto: [titulo, legenda, linha.getAttribute("data-nome") || ""].join(" "),
          campos: editaveis(linha)
            .filter(function (controle) {
              return controle.id;
            })
            .map(function (controle) {
              return { ref: controle.id, rotulo: rotuloDe(controle), valor: valorElegivel(controle) };
            }),
        };
      });
  }

  /* Duas perguntas, e as duas se respondem sobre a mesma lista: "onde está o campo das vagas" e
     "o que foi que eu mexi". */
  function montarFiltro() {
    var linhas = form.querySelectorAll("fieldset.linha[data-linha]");
    // Abaixo de uma dúzia de linhas a página inteira cabe na tela, e a lupa seria mais um
    // controle a ler antes de chegar ao que se veio fazer.
    if (linhas.length < 12) return;

    var caixa = document.createElement("div");
    caixa.className = "filtro-da-retificacao";

    var rotulo = document.createElement("label");
    rotulo.htmlFor = "filtro-da-retificacao";
    rotulo.textContent = "Encontrar";

    filtro = document.createElement("input");
    filtro.type = "search";
    filtro.id = "filtro-da-retificacao";
    filtro.placeholder = "campo, valor ou cartão — vagas, remuneração, Término…";
    /* Fora do formulário do POST não dá — ele é filho dele —, mas fora do **envio** dá: sem
       `name`, o campo não vira dado da Retificação. E `Enter` numa busca não pode disparar o
       envio do formulário, que é o que o navegador faz com um `input` solto: ele leva ao primeiro
       resultado, que é para onde quem tecla Enter quer ir (FR-3923). */
    filtro.addEventListener("keydown", function (evento) {
      if (evento.key !== "Enter") return;
      evento.preventDefault();
      var primeiro = resultados && resultados.querySelector("a.ir-ao-campo");
      if (primeiro) primeiro.focus();
    });

    var marca = document.createElement("span");
    marca.className = "marca";
    somenteAlteradas = document.createElement("input");
    somenteAlteradas.type = "checkbox";
    somenteAlteradas.id = "so-alteradas";
    var rotuloMarca = document.createElement("label");
    rotuloMarca.htmlFor = somenteAlteradas.id;
    rotuloMarca.textContent = "Só o que eu alterei";
    marca.appendChild(somenteAlteradas);
    marca.appendChild(rotuloMarca);

    achados = document.createElement("span");
    achados.className = "achados";
    achados.setAttribute("aria-live", "polite");

    resultados = document.createElement("ol");
    resultados.className = "resultados-da-busca";
    resultados.hidden = true;

    caixa.appendChild(rotulo);
    caixa.appendChild(filtro);
    caixa.appendChild(marca);
    caixa.appendChild(achados);
    caixa.appendChild(resultados);
    form.parentNode.insertBefore(caixa, form);

    filtro.addEventListener("input", aplicar);
    somenteAlteradas.addEventListener("change", aplicar);
  }

  function itemDoResultado(resultado) {
    var item = document.createElement("li");
    var onde = document.createElement("span");
    onde.className = "onde";
    onde.textContent = resultado.onde;
    item.appendChild(onde);
    var link = document.createElement("a");
    link.className = "ir-ao-campo";
    if (resultado.tipo === "campo") {
      var rotulo = document.createElement("span");
      rotulo.className = "rotulo";
      rotulo.textContent = resultado.rotulo;
      item.appendChild(rotulo);
      if (resultado.valor) {
        var valor = document.createElement("span");
        valor.className = "valor";
        valor.textContent = resultado.valor;
        item.appendChild(valor);
      }
      link.setAttribute("href", "#" + resultado.ref);
      link.setAttribute("aria-label", "Ir ao campo " + resultado.rotulo + " — " + resultado.onde);
      link.textContent = "Ir ao campo";
    } else {
      link.setAttribute("href", "#" + resultado.ref);
      link.setAttribute("aria-label", "Ir ao cartão " + resultado.onde);
      link.textContent = "Ir ao cartão";
    }
    item.appendChild(link);
    return item;
  }

  function aplicar() {
    if (!filtro) return;
    var so = somenteAlteradas.checked;
    var cartoes = cartoesDaTela(so);
    var achado = buscar(filtro.value, cartoes);
    var naBusca = {};
    cartoes.forEach(function (cartao) {
      naBusca[cartao.ref] = true;
    });

    [].forEach.call(form.querySelectorAll("fieldset.linha[data-linha]"), function (linha) {
      var mostra = naBusca[linha.id] === true && (!achado || achado.visiveis[linha.id] === true);
      /* A linha onde está o cursor nunca some. Com "só o que eu alterei" ligado, apagar de volta
         o valor original deixava de "ser alteração" no meio da digitação, e o campo desaparecia
         de baixo do cursor de quem estava corrigindo — o filtro é para reencontrar trabalho, e
         não para tirá-lo da frente enquanto ele acontece. */
      if (!mostra && linha.contains(document.activeElement)) mostra = true;
      linha.hidden = !mostra;
    });

    /* A seção sem nenhuma linha visível desaparece com o título. Sobrando, ela anunciaria
       "Cronograma" seguido de nada — e "Cronograma" é justamente o que se procurava.

       `#sobre-a-retificacao` nunca some: a justificativa é obrigatória, e esconder um campo
       obrigatório faz o navegador recusar o envio apontando para algo que ninguém vê. */
    [].forEach.call(form.querySelectorAll(".secao-da-retificacao"), function (secao) {
      if (secao.id === "sobre-a-retificacao") return;
      var alguma = secao.querySelector("fieldset.linha[data-linha]:not([hidden])");
      // Uma linha acrescentada agora não tem `data-linha` e não é filtrável: ela é trabalho em
      // curso, e escondê-la por causa de uma busca perderia o que se está preenchendo de vista.
      var nova = secao.querySelector("fieldset.linha:not([data-linha])");
      secao.hidden = !alguma && !nova;
    });

    resultados.textContent = "";
    if (achado) achado.resultados.forEach(function (resultado) {
      resultados.appendChild(itemDoResultado(resultado));
    });
    resultados.hidden = !achado || !achado.resultados.length;

    if (achado) achados.textContent = fraseDosAchados(achado);
    else if (!so) achados.textContent = "";
    else {
      var visiveis = cartoes.length;
      achados.textContent =
        visiveis === 0 ? "Nenhuma linha corresponde" : visiveis === 1 ? "1 linha" : visiveis + " linhas";
    }
  }

  form.addEventListener("input", recontar);
  form.addEventListener("change", recontar);
  /* Linha acrescentada por HTMX entra depois da contagem inicial, e os campos dela nascem sem
     marca. `htmx:afterSwap` é o momento em que ela já está no documento. */
  document.body.addEventListener("htmx:afterSwap", recontar);

  montarFiltro();
  recontar();
})();
