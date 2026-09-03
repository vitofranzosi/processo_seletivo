/* Rascunho local do assistente — FR-020.

   O servidor só conhece o que foi enviado. Expiração de sessão e queda de conexão são
   exatamente os casos em que o envio não chega, e sem isto o preenchimento se perde: a
   preservação que já existia atua na recusa do domínio, que pressupõe a requisição ter
   chegado.

   O que fica no navegador não é fonte normativa e não substitui o rascunho estruturado do
   Edital, que continua no backend. Por isso nada é restaurado em silêncio: o conteúdo guardado
   pode ser mais velho que o do servidor, e sobrescrever sem perguntar trocaria uma perda por
   outra. A pessoa vê que existe, de quando é, e decide.

   A comparação é por conteúdo canônico, não pelo nome dos campos: o índice de cada linha nasce
   no cliente (`Date.now()`) e o servidor renumera ao reexibir. Comparar nomes acusaria
   diferença logo depois de um salvamento bem-sucedido.

   O rascunho expira (FR-022 da 003). O conteúdo de um Edital em elaboração fica no computador
   de quem preencheu, que num órgão público costuma ser compartilhado, e `localStorage` não
   caduca sozinho: sem prazo, o preenchimento de meses atrás continuaria lá, oferecido a quem
   sentar na máquina depois. Um dia é mais que suficiente para o caso que justifica guardar —
   sessão expirada, conexão caída, navegador fechado por engano — e curto o bastante para não
   virar arquivo. Vencido, é apagado sem ser oferecido: restaurar um preenchimento antigo sobre
   um Edital que mudou no servidor trocaria uma perda por outra. */
(function () {
  var PREFIXO = "ps:rascunho:";

  function armazenamento(sonda) {
    // Janela anônima, cookies bloqueados, cota estourada: sem armazenamento a tela funciona
    // igual, só não protege o preenchimento.
    try {
      window.localStorage.setItem(sonda, "1");
      window.localStorage.removeItem(sonda);
      return window.localStorage;
    } catch (erro) {
      return null;
    }
  }

  /* O que o servidor acabou de receber deixa de existir só neste navegador.

     Roda **antes** de tudo, e fora do formulário desta tela, por duas razões. A primeira é que
     "Avançar" grava uma etapa e abre outra — que pode nem guardar rascunho —, e sem isto a
     etapa gravada continuaria oferecendo, na próxima visita, o que já foi enviado. A segunda é
     que a comparação por conteúdo não resolve o caso: o servidor normaliza o que recebe (`2`
     volta `2.0000`, a ordem é renumerada), e o digitado nunca é textualmente igual ao
     reexibido. Era isso que fazia o aviso "há preenchimento não enviado" aparecer na mesma tela
     que anunciava "Rascunho salvo". */
  var confirmado = document.querySelector("[data-rascunho-salvo]");
  if (confirmado && confirmado.dataset.rascunhoSalvo) {
    var recibo = armazenamento(PREFIXO + "sonda");
    if (recibo) recibo.removeItem(PREFIXO + confirmado.dataset.rascunhoSalvo);
  }

  var form = document.getElementById("formulario");
  if (!form || !form.dataset.rascunho) return;

  var CHAVE = PREFIXO + form.dataset.rascunho;
  var VALIDADE_MS = 24 * 60 * 60 * 1000;
  var lista = document.querySelector(form.dataset.lista);
  var fragmento = form.dataset.fragmento;
  var IGNORADOS = ["csrfmiddlewaretoken", "destino"];

  function guarda() {
    return armazenamento(CHAVE + ":teste");
  }

  function valorDe(campo) {
    return campo.type === "checkbox" ? (campo.checked ? campo.value : "") : campo.value;
  }

  function ler() {
    var linhas = {};
    var ordem = [];
    var simples = {};
    Array.prototype.forEach.call(form.elements, function (campo) {
      if (!campo.name || IGNORADOS.indexOf(campo.name) >= 0) return;
      var partes = campo.name.match(/^([a-z]+)-(\d+)-(\w+)$/);
      if (!partes) {
        simples[campo.name] = valorDe(campo);
        return;
      }
      if (!linhas[partes[2]]) {
        linhas[partes[2]] = {};
        ordem.push(partes[2]);
      }
      linhas[partes[2]][partes[3]] = valorDe(campo);
    });
    return {
      simples: simples,
      linhas: ordem.map(function (indice) {
        return linhas[indice];
      }),
    };
  }

  function mesmo(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
  }

  function preencher(linha, valores) {
    Array.prototype.forEach.call(linha.querySelectorAll("[name]"), function (campo) {
      var partes = campo.name.match(/^[a-z]+-\d+-(\w+)$/);
      if (partes && valores[partes[1]] !== undefined) campo.value = valores[partes[1]];
    });
  }

  async function restaurar(dados) {
    if (lista) {
      lista.replaceChildren();
      for (var i = 0; i < dados.linhas.length; i++) {
        var resposta = await fetch(fragmento + "?indice=" + (Date.now() + i));
        if (!resposta.ok) break;
        lista.insertAdjacentHTML("beforeend", await resposta.text());
        preencher(lista.lastElementChild, dados.linhas[i]);
      }
    }
    Object.keys(dados.simples).forEach(function (nome) {
      var campo = form.elements[nome];
      if (campo) campo.value = dados.simples[nome];
    });
    var primeiro = form.querySelector("input:not([type=hidden]), select, textarea");
    if (primeiro) primeiro.focus();
  }

  var armazem = guarda();
  var renderizado = ler();
  var marcador = document.querySelector("[data-nao-enviado]");

  function marcar() {
    if (marcador) marcador.hidden = mesmo(ler(), renderizado);
  }

  function gravar() {
    if (!armazem) return;
    var atual = ler();
    // Igual ao que o servidor já tem: não há nada por enviar, e guardar só criaria um aviso
    // falso na próxima visita.
    if (mesmo(atual, renderizado)) armazem.removeItem(CHAVE);
    else armazem.setItem(CHAVE, JSON.stringify({ em: new Date().toISOString(), dados: atual }));
    marcar();
  }

  function quando(iso) {
    var d = new Date(iso);
    return isNaN(d) ? "" : " de " + d.toLocaleString("pt-BR");
  }

  function vencido(guardado) {
    var gravado = new Date(guardado && guardado.em);
    // Sem carimbo de tempo utilizável não há como saber a idade — e o que não se sabe a idade
    // é tratado como vencido, que é o lado seguro num computador compartilhado.
    if (isNaN(gravado)) return true;
    return Date.now() - gravado.getTime() > VALIDADE_MS;
  }

  function oferecer(guardado) {
    var caixa = document.createElement("div");
    caixa.className = "aviso";
    caixa.setAttribute("role", "status");
    var texto = document.createElement("p");
    texto.style.margin = "0 0 .6rem";
    texto.innerHTML =
      "<strong>Há preenchimento não enviado neste navegador</strong>" +
      quando(guardado.em) +
      ". Ele não chegou ao servidor — o que está na tela é o que foi enviado por último.";
    var restaura = document.createElement("button");
    restaura.type = "button";
    restaura.className = "botao secundario";
    restaura.textContent = "Restaurar o que eu havia digitado";
    var descarta = document.createElement("button");
    descarta.type = "button";
    descarta.className = "acao";
    descarta.style.marginLeft = ".5rem";
    descarta.textContent = "Descartar";

    restaura.addEventListener("click", function () {
      restaurar(guardado.dados).then(function () {
        caixa.remove();
        marcar();
      });
    });
    descarta.addEventListener("click", function () {
      if (armazem) armazem.removeItem(CHAVE);
      caixa.remove();
      marcar();
    });

    caixa.append(texto, restaura, descarta);
    form.parentNode.insertBefore(caixa, form);
  }

  if (armazem) {
    var bruto = armazem.getItem(CHAVE);
    if (bruto) {
      try {
        var guardado = JSON.parse(bruto);
        if (vencido(guardado) || mesmo(guardado.dados, renderizado)) armazem.removeItem(CHAVE);
        else oferecer(guardado);
      } catch (erro) {
        armazem.removeItem(CHAVE);
      }
    }
  }

  var adiado;
  function agendar() {
    clearTimeout(adiado);
    adiado = setTimeout(gravar, 400);
  }
  form.addEventListener("input", agendar);
  form.addEventListener("change", agendar);
  if (lista) new MutationObserver(agendar).observe(lista, { childList: true });
  marcar();
})();
