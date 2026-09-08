/* Orientação dentro de uma Retificação longa.

   Um Edital institucional publicado rende sessenta linhas editáveis — Perfis com Modalidades,
   Marcos e Critérios, um Cronograma de doze Eventos, Etapas, Documentos, Anexos e as Seções do
   texto. A tela mostrava todas de uma vez, sem sumário, sem busca e sem qualquer distinção entre
   o campo que alguém acabou de alterar e os outros noventa. Quem retifica **um** prazo rolava a
   página inteira para achá-lo, e depois rolava de novo para conferir se tinha mexido no certo.

   Três coisas, e nada além:

   1. **O que já mudou fica marcado**, campo a campo e linha a linha, comparando com o valor que
      o servidor entregou. Não é validação e não bloqueia nada: é a memória que o formulário não
      tinha. O resumo "antes e depois" continua vindo do servidor, que é quem sabe traduzir a
      alteração em ato — aqui só se diz onde ela está.
   2. **A contagem** aparece na barra de ações, que acompanha a rolagem. "3 campos alterados" é a
      resposta à pergunta que se faz antes de enviar.
   3. **Um filtro** por nome e um "só o que eu mudei", para reencontrar uma linha entre sessenta.

   **O filtro nasce aqui, e não no template.** Sem script ele não filtraria nada, e um controle
   que existe no HTML e só funciona com JavaScript é pior que a ausência dele, porque promete. O
   sumário do topo é o contrário: são âncoras comuns, funcionam sem script, e por isso ficam no
   HTML.

   Filtrar **esconde**, e não remove: o campo escondido continua no formulário e continua sendo
   enviado. Esconder o que se envia mudaria a Retificação por causa de uma busca, que seria a
   pior coisa que uma lupa poderia fazer. */
(function () {
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

  /* Mudou em relação ao que o servidor entregou — e não em relação ao que estava aqui há um
     segundo. O ponto de comparação é o `default*` do DOM, que guarda o valor declarado no HTML e
     não acompanha a digitação. Depois de um envio o servidor reexibe o que foi digitado, e o
     digitado passa a **ser** o declarado: as marcas somem, e é o correto — a partir dali quem
     responde "o que vai mudar" é a tabela do resumo, que veio do servidor. */
  function alterado(campo) {
    if (campo.type === "checkbox" || campo.type === "radio") {
      return campo.checked !== campo.defaultChecked;
    }
    if (campo.type === "file") return campo.files && campo.files.length > 0;
    if (campo.tagName === "SELECT") {
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

  var contagem = document.createElement("span");
  contagem.className = "contagem";
  /* `polite`: a contagem muda a cada tecla digitada, e `assertive` interromperia a leitura do
     próprio campo que se está preenchendo. */
  contagem.setAttribute("aria-live", "polite");
  var barra = form.querySelector(".barra-de-acoes");
  if (barra) barra.appendChild(contagem);

  var filtro = null;
  var somenteAlteradas = null;
  var achados = null;

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

    if (total === 0) contagem.textContent = "Nenhum campo alterado ainda";
    else if (total === 1) contagem.innerHTML = "<strong>1</strong> campo alterado";
    else contagem.innerHTML = "<strong>" + total + "</strong> campos alterados";
    /* O recorte acompanha a contagem: com "só o que eu alterei" ligado, a linha que acabou de
       mudar precisa aparecer; e a linha recém-acrescentada por HTMX precisa reabrir a seção que
       o filtro havia fechado — sem isto ela nascia dentro de uma seção escondida. */
    aplicar();
    return total;
  }

  /* ── O filtro ──────────────────────────────────────────────────────────────────────────────
     Duas perguntas, e as duas se respondem sobre a mesma lista: "onde está a Etapa de títulos" e
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
    filtro.placeholder = "nome do Perfil, do Evento, da Etapa…";
    /* Fora do formulário do POST não dá — ele é filho dele —, mas fora do **envio** dá: sem
       `name`, o campo não vira dado da Retificação. E `Enter` numa busca não pode disparar o
       envio do formulário, que é o que o navegador faz com um `input` solto. */
    filtro.addEventListener("keydown", function (evento) {
      if (evento.key === "Enter") evento.preventDefault();
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

    caixa.appendChild(rotulo);
    caixa.appendChild(filtro);
    caixa.appendChild(marca);
    caixa.appendChild(achados);
    form.parentNode.insertBefore(caixa, form);

    filtro.addEventListener("input", aplicar);
    somenteAlteradas.addEventListener("change", aplicar);
  }

  function aplicar() {
    if (!filtro) return;
    var termo = filtro.value.trim().toLowerCase();
    var so = somenteAlteradas.checked;
    var visiveis = 0;

    [].forEach.call(form.querySelectorAll("fieldset.linha[data-linha]"), function (linha) {
      var nome = (linha.getAttribute("data-nome") || "").toLowerCase();
      var combina = !termo || nome.indexOf(termo) >= 0;
      var mostra = combina && (!so || linha.hasAttribute("data-alterado"));
      /* A linha onde está o cursor nunca some. Com "só o que eu alterei" ligado, apagar de volta
         o valor original deixava de "ser alteração" no meio da digitação, e o campo desaparecia
         de baixo do cursor de quem estava corrigindo — o filtro é para reencontrar trabalho, e
         não para tirá-lo da frente enquanto ele acontece. */
      if (!mostra && linha.contains(document.activeElement)) mostra = true;
      linha.hidden = !mostra;
      if (mostra) visiveis += 1;
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

    // Vazio quando não há recorte: dizer "24 linhas" sobre a lista inteira não informa nada.
    if (!termo && !so) achados.textContent = "";
    else if (visiveis === 0) achados.textContent = "Nenhuma linha corresponde";
    else if (visiveis === 1) achados.textContent = "1 linha";
    else achados.textContent = visiveis + " linhas";
  }

  form.addEventListener("input", recontar);
  form.addEventListener("change", recontar);
  /* Linha acrescentada por HTMX entra depois da contagem inicial, e os campos dela nascem sem
     marca. `htmx:afterSwap` é o momento em que ela já está no documento. */
  document.body.addEventListener("htmx:afterSwap", recontar);

  montarFiltro();
  recontar();
})();
