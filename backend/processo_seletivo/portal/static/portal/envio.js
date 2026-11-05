/* O progresso do envio, e o aviso de não fechar a página (FR-048).

   Dez megabytes em rede móvel levam dezenas de segundos. Sem sinal nenhum, a pessoa reenvia,
   fecha ou desiste — e é o único momento da jornada em que ela fica esperando sem saber se algo
   está acontecendo.

   Usa o evento de progresso do próprio htmx, que já está embarcado: nenhuma biblioteca nova,
   nenhum envio em pedaços, nenhuma retomada. O alvo é informar, não medir com precisão.

   Sem JavaScript a página continua funcionando: os formulários têm `action` e `method`, e o envio
   acontece pelo caminho normal do navegador — sem barra de progresso, que é degradação aceitável.

   **Nada é guardado no navegador.** Nem rascunho, nem identificação, nem nome de arquivo: a tela
   carrega CPF e documentos, e num computador compartilhado o que fica guardado é o que vaza
   (FR-042). */
(function () {
  function progressoDe(formulario) {
    return formulario.querySelector ? formulario.querySelector(".progresso") : null;
  }

  function botoesDe(formulario) {
    return formulario.querySelectorAll ? formulario.querySelectorAll("button") : [];
  }

  document.body.addEventListener("htmx:xhr:progress", function (evento) {
    var bloco = progressoDe(evento.target);
    if (!bloco || !evento.detail.lengthComputable) return;
    bloco.hidden = false;
    bloco.querySelector("progress").value = (evento.detail.loaded / evento.detail.total) * 100;
  });

  document.body.addEventListener("htmx:beforeRequest", function (evento) {
    var bloco = progressoDe(evento.target);
    if (!bloco) return;
    bloco.hidden = false;
    // Desabilitar durante o envio evita o segundo clique que produziria dois envios do mesmo
    // arquivo — o mesmo cuidado que a submissão tem no servidor, aqui só para não confundir.
    botoesDe(evento.target).forEach(function (botao) {
      botao.disabled = true;
    });
  });

  document.body.addEventListener("htmx:afterRequest", function (evento) {
    var bloco = progressoDe(evento.target);
    if (bloco) bloco.hidden = true;
    botoesDe(evento.target).forEach(function (botao) {
      botao.disabled = false;
    });
  });

  /* O formulário sem htmx: o envio de documento da convocação (121, FR-3872, R-007).

     Ali o envio é POST comum, porque a volta precisa ser a âncora `#confirmacao`, com o foco dado
     pelo próprio navegador, sem script — trocar a resposta por fragmento perderia isso. Só que os
     ouvintes acima são do htmx, e com eles o "Enviando… não feche esta página." que o cartão já
     traz nunca aparecia. Aqui ele aparece no `submit`, e o botão fica desabilitado até a página
     seguinte; a barra fica indeterminada, porque sem o htmx não há evento de progresso a medir.

     Só no formulário marcado com `data-envio` e sem `hx-post`: o da inscrição continua no ramo do
     htmx, que mede o percentual. */
  function semHtmx(formulario) {
    return (
      formulario &&
      formulario.hasAttribute &&
      formulario.hasAttribute("data-envio") &&
      !formulario.hasAttribute("hx-post")
    );
  }

  document.body.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!semHtmx(formulario)) return;
    var bloco = progressoDe(formulario);
    if (bloco) {
      bloco.hidden = false;
      var barra = bloco.querySelector("progress");
      if (barra) barra.removeAttribute("value");
    }
    botoesDe(formulario).forEach(function (botao) {
      botao.disabled = true;
    });
  });

  /* A volta pelo botão "voltar" do navegador restaura a página do cache como estava no instante do
     envio — com o botão desabilitado e o aviso à mostra. Sem isto, a pessoa ficaria sem como enviar
     de novo. */
  if (typeof window !== "undefined" && window.addEventListener) {
    window.addEventListener("pageshow", function () {
      var formularios = document.querySelectorAll("form[data-envio]");
      for (var i = 0; i < formularios.length; i++) {
        if (!semHtmx(formularios[i])) continue;
        var bloco = progressoDe(formularios[i]);
        if (bloco) bloco.hidden = true;
        botoesDe(formularios[i]).forEach(function (botao) {
          botao.disabled = false;
        });
      }
    });
  }

  /* A falha que não aparecia.

     O htmx só troca conteúdo em resposta bem-sucedida — o que está certo, e por isso mesmo uma
     resposta de erro não muda nada na tela: o nome do arquivo continua ali, a contagem continua
     igual, e nada acusa. A pessoa acredita que anexou. Aconteceu de verdade no percurso da
     jornada: a sessão tinha caído noutra aba, o envio voltou 404, e a página não piscou.

     Uma frase, no lugar onde ela estava olhando, dizendo o que houve e o que fazer. Não tenta
     reenviar sozinho: reenviar dez megabytes sem a pessoa pedir é decisão dela, não do script. */
  function avisar(formulario, texto) {
    var alvo = formulario.closest ? formulario.closest(".requisito") || formulario : formulario;
    var recado = alvo.querySelector(".recusa-do-envio");
    if (!recado) {
      recado = document.createElement("p");
      recado.className = "recusa recusa-do-envio";
      recado.setAttribute("role", "alert");
      alvo.appendChild(recado);
    }
    recado.textContent = texto;
  }

  document.body.addEventListener("htmx:responseError", function (evento) {
    avisar(
      evento.target,
      evento.detail.xhr && evento.detail.xhr.status === 404
        ? "Não foi possível enviar: o seu acesso expirou. Recarregue a página e entre de novo — o " +
            "que você já enviou continua guardado."
        : "Não foi possível enviar agora. Tente de novo; o que você já enviou continua guardado."
    );
  });

  document.body.addEventListener("htmx:sendError", function (evento) {
    avisar(
      evento.target,
      "Não foi possível enviar: a conexão falhou. Verifique a internet e tente de novo — o que " +
        "você já enviou continua guardado."
    );
  });
})();
