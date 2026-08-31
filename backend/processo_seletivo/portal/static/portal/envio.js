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
})();
