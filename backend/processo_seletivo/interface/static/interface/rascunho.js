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
   um Edital que mudou no servidor trocaria uma perda por outra.

   **Quem remonta a tela restaurada é o servidor, e não este script** (RC-08, AX-16 de 15/09). A
   restauração recriava cada linha a partir do fragmento vazio da linha de topo e casava os nomes
   pela forma `prefixo-índice-campo`: tudo que era aninhado — a Modalidade, o fato, a linha do
   quadro, os marcos em trânsito da cópia — não tinha onde cair e sumia em silêncio; o HTML inserido
   não passava pelo htmx, e "Acrescentar Modalidade" deixava de responder; e o autosave seguinte
   regravava o que restou por cima do guardado, tornando a perda irreversível. Remontar no navegador
   exigiria saber, para cada coleção de cada etapa, que fragmento a cria — uma segunda cópia da
   estrutura do formulário, que envelheceria a cada coleção nova. O servidor já sabe reexibir
   exatamente o que foi digitado, porque é o que ele faz depois de uma recusa: restaurar é enviar-lhe
   os campos guardados pedindo só isso. */
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
  var IGNORADOS = ["csrfmiddlewaretoken", "destino"];

  function guarda() {
    return armazenamento(CHAVE + ":teste");
  }

  /* A lista de escolha múltipla — as Etapas que o marco enumera — vale pelas opções marcadas, e não
     pelo `value`, que é só a primeira delas. Guardar o `value` perdia as demais em silêncio, e a
     tela restaurada gravaria o marco com uma Etapa a menos (053, medido no preview: nenhuma etapa
     com rascunho tinha lista múltipla até a Classificação ganhar o dela). */
  function escolhidas(campo) {
    return [].filter
      .call(campo.options, function (opcao) {
        return opcao.selected;
      })
      .map(function (opcao) {
        return opcao.value;
      });
  }

  function valorDe(campo) {
    if (campo.type === "select-multiple") return escolhidas(campo);
    return campo.type === "checkbox" ? (campo.checked ? campo.value : "") : campo.value;
  }

  function ler() {
    var linhas = {};
    var ordem = [];
    var simples = {};
    Array.prototype.forEach.call(form.elements, function (campo) {
      if (!campo.name || IGNORADOS.indexOf(campo.name) >= 0) return;
      // Rádio não marcado não tem escolha a guardar: os do grupo dividem o `name`, e ler todos
      // fazia o último sobrescrever o escolhido — o rascunho registrava sempre a última opção da
      // lista, e mudar de opção nem marcava o formulário como não enviado.
      if (campo.type === "radio" && !campo.checked) return;
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

  /* Os campos como o navegador os enviaria: rádio e caixa só quando marcados, na ordem do
     formulário, com os nomes exatos. `ler` não serve para isto — ele descarta o prefixo e o índice,
     que é o que o torna comparável ao renderizado, e é justamente o que o servidor precisa para
     saber de que Perfil é cada Modalidade. */
  function campos() {
    var pares = [];
    Array.prototype.forEach.call(form.elements, function (campo) {
      if (!campo.name || IGNORADOS.indexOf(campo.name) >= 0 || campo.disabled) return;
      if (campo.type === "submit" || campo.type === "button" || campo.type === "file") return;
      if ((campo.type === "radio" || campo.type === "checkbox") && !campo.checked) return;
      if (campo.type === "select-multiple") {
        escolhidas(campo).forEach(function (valor) {
          pares.push([campo.name, valor]);
        });
        return;
      }
      pares.push([campo.name, campo.value]);
    });
    return pares;
  }

  function oculto(nome, valor) {
    var campo = document.createElement("input");
    campo.type = "hidden";
    campo.setAttribute("name", nome);
    campo.value = valor;
    return campo;
  }

  /* Um envio de página inteira, e não um `fetch` que troca pedaços: a tela que volta é a que o
     servidor renderiza, com o htmx processando tudo no carregamento — nada fica inerte.

     Para o **caminho** da etapa, sem a consulta: `?salvo=` na tela atual faria a resposta trazer o
     recibo de uma gravação que não aconteceu, e o recibo apaga o guardado. */
  function restaurar(guardado) {
    var envio = document.createElement("form");
    envio.setAttribute("method", "post");
    envio.setAttribute("action", window.location.pathname);
    envio.hidden = true;
    var token = Array.prototype.find.call(form.elements, function (campo) {
      return campo.name === "csrfmiddlewaretoken";
    });
    if (token) envio.append(oculto(token.name, token.value));
    envio.append(oculto("restaurar", "1"));
    guardado.campos.forEach(function (par) {
      envio.append(oculto(par[0], par[1]));
    });
    document.body.append(envio);
    envio.submit();
  }

  var armazem = guarda();
  /* Na tela restaurada, o renderizado **não** é o que o servidor tem: é o guardado, reexibido.
     Tomá-lo como referência faria o guardado parecer igual à tela e ser apagado, e o marcador
     dizer que nada falta enviar — quando tudo falta. Sem referência, a tela se declara não enviada
     e cada alteração regrava o guardado inteiro, até a pessoa salvar e o recibo o apagar. */
  var restaurado = document.querySelector("[data-rascunho-restaurado]");
  var renderizado = restaurado ? null : ler();
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
    else
      armazem.setItem(
        CHAVE,
        JSON.stringify({ em: new Date().toISOString(), dados: atual, campos: campos() })
      );
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
      restaurar(guardado);
    });
    descarta.addEventListener("click", function () {
      if (armazem) armazem.removeItem(CHAVE);
      caixa.remove();
      marcar();
    });

    caixa.append(texto, restaura, descarta);
    form.parentNode.insertBefore(caixa, form);
  }

  if (armazem && !restaurado) {
    var bruto = armazem.getItem(CHAVE);
    if (bruto) {
      try {
        var guardado = JSON.parse(bruto);
        // Sem `campos` é o formato de antes do RC-08, que só a restauração defeituosa sabia ler.
        // Oferecê-lo seria oferecer a perda de novo; e ele tem no máximo um dia.
        var legivel = Array.isArray(guardado.campos);
        if (vencido(guardado) || !legivel || mesmo(guardado.dados, renderizado))
          armazem.removeItem(CHAVE);
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
