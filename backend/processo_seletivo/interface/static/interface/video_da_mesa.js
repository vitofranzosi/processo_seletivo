/* Os controles do vídeo da verificação na Mesa (166, FR-7132, UX-774).

   Os saltos para o instante de cada passo do roteiro, o recuo e o avanço de 10 s e a velocidade de
   0,5×. Nada aqui registra: a abertura já foi registrada, uma vez, pelo botão que trouxe o vídeo
   (D-007), e os pedidos do reprodutor são só a entrega dela. */
(function () {
  "use strict";
  var secao = document.querySelector(".video-da-mesa");
  if (!secao) return;
  var video = secao.querySelector("[data-reprodutor]");
  if (!video) return;

  function para(segundos) {
    // O instante vem do atributo, em segundos com ponto; um valor que não é número não move nada.
    if (!Number.isFinite(segundos)) return;
    var fim = Number.isFinite(video.duration) ? video.duration : segundos;
    video.currentTime = Math.max(0, Math.min(segundos, fim));
  }

  secao.addEventListener("click", function (evento) {
    var botao = evento.target.closest("button");
    if (!botao) return;
    if (botao.hasAttribute("data-saltar")) {
      para(Number(botao.getAttribute("data-saltar")));
      video.focus();
    } else if (botao.hasAttribute("data-recuar")) {
      para(video.currentTime - 10);
    } else if (botao.hasAttribute("data-avancar")) {
      para(video.currentTime + 10);
    } else if (botao.hasAttribute("data-lento")) {
      var lento = video.playbackRate !== 0.5;
      video.playbackRate = lento ? 0.5 : 1;
      botao.setAttribute("aria-pressed", lento ? "true" : "false");
    }
  });

  // O menu "baixar" do próprio reprodutor, onde o navegador o oferece fora do `controlslist`.
  video.addEventListener("contextmenu", function (evento) {
    evento.preventDefault();
  });
})();
