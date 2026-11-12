/* O envio de vários documentos da convocação (150, FR-5600 a FR-5611).

   Cada cartão da convocação é um formulário que envia só o seu arquivo e recarrega a página. Quem
   escolhia os quatro arquivos e clicava em "Enviar" num deles via um chegar e os outros três
   voltarem a "Nenhum arquivo escolhido", sem aviso nenhum — e o prazo corria.

   Com dois ou mais arquivos escolhidos, o botão de cada cartão escolhido passa a dizer "Enviar os N
   documentos escolhidos" e envia todos (D-001). **Um por requisição, em sequência** (D-002): o
   proxy limita o corpo do portal a um arquivo, e cada documento continua um envio próprio, com a
   validação, o prazo e a trilha de hoje. A rota é a mesma do envio de um; o cabeçalho
   `X-Envio-De-Varios: k/n` só troca o redirecionamento por JSON, que o `fetch` consegue ler (R-002).

   **A recusa de um não para os seguintes** (FR-5606). O arquivo acima do limite nem viaja: vai só o
   tamanho, e o servidor recusa com a frase de hoje (R-009). Terminado o lote, a página é recarregada
   na âncora que o servidor indicou — a confirmação, ou o cartão do primeiro recusado (R-004).

   **Queda de conexão ou acesso expirado no meio** (FR-5610): a página fica, diz o que chegou e o que
   não foi enviado, e o que não foi continua escolhido. Do documento que estava subindo quando a
   conexão caiu não se sabe se chegou: a frase diz isso, e não "não recebido" (R-010).

   Com um arquivo só, nada muda: o envio é o de hoje, com o progresso de `envio.js`.

   **Nada é guardado no navegador** (FR-5611): nem nome de arquivo, nem progresso. */
(function () {
  var ACESSO_EXPIRADO =
    "Não foi possível enviar: o seu acesso expirou. Recarregue a página e entre de novo — o que " +
    "você já enviou continua guardado.";
  var FALHA =
    "Não foi possível enviar agora. Tente de novo; o que você já enviou continua guardado.";
  var CONEXAO =
    "Não foi possível enviar: a conexão falhou. Verifique a internet e tente de novo — o que " +
    "você já enviou continua guardado.";
  var EM_VOO =
    ": não é possível saber se chegou — a conexão caiu durante o envio. Recarregue a página para " +
    "conferir, ou envie de novo: se já tinha chegado, o sistema reconhece o mesmo arquivo.";
  var RECEBIDO_AGORA = "Recebido agora.";
  var NENHUM = "Nenhum arquivo escolhido";

  var formularios = Array.prototype.slice.call(document.querySelectorAll("form[data-envio]"));
  if (!formularios.length) return;
  var anuncio = document.querySelector("[data-anuncio-de-varios]");
  /* O rótulo e a frase de progresso de cada cartão, como vieram do servidor: com um escolhido, ou
     nenhum, o botão volta a ser exatamente o de hoje, com o nome do documento para o leitor de
     tela (FR-3745 da `118`). */
  var originais = formularios.map(function (formulario) {
    var botao = botaoDe(formulario);
    var ajuda = ajudaDoProgresso(formulario);
    return {
      rotulo: botao ? botao.innerHTML : "",
      progresso: ajuda ? ajuda.textContent : "",
    };
  });
  var emCurso = false;
  var ultimaContagem = 0;

  function botaoDe(formulario) {
    return formulario.querySelector("button[type=submit]");
  }

  function campoDe(formulario) {
    return formulario.querySelector("[data-arquivo]");
  }

  function ajudaDoProgresso(formulario) {
    var bloco = formulario.querySelector(".progresso");
    return bloco ? bloco.querySelector(".ajuda") : null;
  }

  function arquivoDe(formulario) {
    var campo = campoDe(formulario);
    return campo && campo.files && campo.files.length ? campo.files[0] : null;
  }

  function cartaoDe(formulario) {
    return formulario.closest ? formulario.closest(".cartao-do-documento") : null;
  }

  function nomeDe(formulario) {
    var cartao = cartaoDe(formulario);
    return (cartao && cartao.getAttribute("data-documento")) || "";
  }

  function escolhidos() {
    return formularios.filter(arquivoDe);
  }

  function anunciar(texto) {
    if (anuncio) anuncio.textContent = texto;
  }

  /* O rótulo de cada botão segue a contagem (FR-5601, FR-5613). Com dois ou mais, o nome acessível
     é o texto visível: todos os botões fazem então a mesma coisa. */
  function rotular() {
    var quantos = escolhidos().length;
    formularios.forEach(function (formulario, indice) {
      var botao = botaoDe(formulario);
      if (!botao) return;
      if (quantos >= 2 && arquivoDe(formulario)) {
        botao.textContent = "Enviar os " + quantos + " documentos escolhidos";
      } else {
        botao.innerHTML = originais[indice].rotulo;
      }
    });
    if (quantos !== ultimaContagem) {
      ultimaContagem = quantos;
      anunciar(
        quantos === 0
          ? ""
          : quantos === 1
            ? "1 documento escolhido para enviar."
            : quantos + " documentos escolhidos para enviar."
      );
    }
    return quantos;
  }

  function travar(sim) {
    formularios.forEach(function (formulario) {
      var botao = botaoDe(formulario);
      var campo = campoDe(formulario);
      if (botao) botao.disabled = sim;
      if (campo) campo.disabled = sim;
    });
  }

  function mostrarProgresso(formulario, texto) {
    var bloco = formulario.querySelector(".progresso");
    if (!bloco) return;
    bloco.hidden = false;
    var barra = bloco.querySelector("progress");
    if (barra) barra.removeAttribute("value");
    var ajuda = ajudaDoProgresso(formulario);
    if (ajuda) ajuda.textContent = texto;
    anunciar(texto);
  }

  function esconderProgresso() {
    formularios.forEach(function (formulario, indice) {
      var bloco = formulario.querySelector(".progresso");
      if (bloco) bloco.hidden = true;
      var ajuda = ajudaDoProgresso(formulario);
      if (ajuda) ajuda.textContent = originais[indice].progresso;
    });
  }

  /* A frase no cartão, no lugar onde a pessoa está olhando — a mesma marca de `envio.js`. */
  function dizerNoCartao(formulario, texto) {
    var alvo = cartaoDe(formulario) || formulario;
    var recado = alvo.querySelector(".recusa-do-envio");
    if (!recado) {
      recado = document.createElement("p");
      recado.className = "recusa recusa-do-envio";
      recado.setAttribute("role", "alert");
      alvo.appendChild(recado);
    }
    recado.textContent = texto;
  }

  function limparEscolha(formulario, texto) {
    var campo = campoDe(formulario);
    if (campo) campo.value = "";
    var nome = formulario.querySelector("[data-nome-do-arquivo]");
    if (nome) {
      nome.textContent = texto || NENHUM;
      if (nome.classList) nome.classList.remove("escolhido");
    }
    var botao = botaoDe(formulario);
    if (botao && botao.classList) botao.classList.remove("pronta");
  }

  function nomes(lista) {
    return lista.map(nomeDe).join(", ");
  }

  /* Um documento do lote. O arquivo acima do limite vai sem o arquivo, só com o tamanho (R-009).

     **O corpo é montado à mão, e não com `new FormData(formulario)`**: durante o lote os campos
     estão desabilitados, e o navegador deixa campo desabilitado fora do `FormData` — o servidor
     recebia o envio sem arquivo e recusava com "Escolha um arquivo PDF antes de enviar.". Achado na
     verificação no navegador, que o teste com objetos simples não via. */
  function pedir(formulario, posicao, total) {
    var arquivo = arquivoDe(formulario);
    var limite = parseInt(formulario.getAttribute("data-limite-em-bytes"), 10);
    var ficha = formulario.querySelector("[name=csrfmiddlewaretoken]");
    var corpo = new FormData();
    corpo.append("csrfmiddlewaretoken", ficha ? ficha.value : "");
    if (limite && arquivo.size > limite) {
      corpo.append("tamanho_declarado", String(arquivo.size));
    } else {
      corpo.append("arquivo", arquivo, arquivo.name);
    }
    return fetch(formulario.action, {
      method: "POST",
      body: corpo,
      credentials: "same-origin",
      headers: { "X-Envio-De-Varios": posicao + "/" + total },
    }).then(function (resposta) {
      var tipo = (resposta.headers && resposta.headers.get("Content-Type")) || "";
      if (resposta.ok && tipo.indexOf("application/json") === 0) {
        return resposta.json().then(function (dados) {
          return { dados: dados };
        });
      }
      /* Sem JSON, o servidor não decidiu sobre o documento: a página de acesso (a sessão caiu e o
         `fetch` seguiu o redirecionamento), a 404 ou uma falha. */
      var expirou = resposta.status === 404 || (resposta.ok && tipo.indexOf("text/html") === 0);
      return { dados: null, frase: expirou ? ACESSO_EXPIRADO : FALHA };
    });
  }

  /* O lote parou no meio (FR-5610): a página fica, e a frase diz o que chegou e o que não. */
  function parar(acionado, recebidos, recusados, naoEnviados, emVoo, frase) {
    emCurso = false;
    travar(false);
    esconderProgresso();
    recebidos.forEach(function (formulario) {
      limparEscolha(formulario, RECEBIDO_AGORA);
      /* A recusa que a volta anterior pôs no cartão já não vale: o documento acabou de chegar. */
      var cartao = cartaoDe(formulario);
      var antiga = cartao ? cartao.querySelector("[data-recusa]") : null;
      if (antiga && antiga.remove) antiga.remove();
    });
    recusados.forEach(function (recusado) {
      limparEscolha(recusado.formulario);
      dizerNoCartao(recusado.formulario, recusado.frase);
    });
    var partes = [frase];
    if (recebidos.length) partes.push("Recebemos: " + nomes(recebidos) + ".");
    if (naoEnviados.length) partes.push("Não foram enviados: " + nomes(naoEnviados) + ".");
    if (emVoo) partes.push(nomeDe(emVoo) + EM_VOO);
    dizerNoCartao(acionado, partes.join(" "));
    rotular();
  }

  function enviarTodos(lote, acionado) {
    emCurso = true;
    travar(true);
    /* A confirmação no topo é a da volta anterior. Se o lote parar no meio, a página fica, e ela
       contradiria a frase nova — "não foi recebido" de um documento que acabou de chegar. */
    var anterior = document.querySelector("#confirmacao");
    if (anterior) anterior.hidden = true;
    var total = lote.length;
    var recebidos = [];
    var recusados = [];
    var volta = "";

    function passo(indice) {
      if (indice >= total) {
        window.location.assign(volta);
        return null;
      }
      var formulario = lote[indice];
      mostrarProgresso(
        acionado,
        "Enviando " + (indice + 1) + " de " + total + ": " + nomeDe(formulario) +
          "… Não feche esta página."
      );
      return pedir(formulario, indice + 1, total).then(
        function (resultado) {
          if (!resultado.dados) {
            parar(acionado, recebidos, recusados, lote.slice(indice), null, resultado.frase);
            return null;
          }
          volta = resultado.dados.volta;
          if (resultado.dados.resultado === "recusado") {
            recusados.push({ formulario: formulario, frase: resultado.dados.frase });
          } else {
            recebidos.push(formulario);
          }
          return passo(indice + 1);
        },
        function () {
          parar(acionado, recebidos, recusados, lote.slice(indice + 1), formulario, CONEXAO);
          return null;
        }
      );
    }

    return passo(0);
  }

  formularios.forEach(function (formulario) {
    var campo = campoDe(formulario);
    if (campo) campo.addEventListener("change", rotular);
    /* No próprio formulário, e não no `document.body` como `envio.js`: este ouvinte corre antes, e
       com dois ou mais escolhidos o envio nativo — que levaria um e descartaria os outros — não
       acontece. */
    formulario.addEventListener("submit", function (evento) {
      if (emCurso) {
        evento.preventDefault();
        return;
      }
      var lote = escolhidos();
      if (lote.length < 2 || !arquivoDe(formulario)) return;
      evento.preventDefault();
      evento.stopPropagation();
      enviarTodos(lote, formulario);
    });
  });

  /* A volta pelo "voltar" do navegador restaura a página como estava no instante da navegação —
     com os botões travados e o progresso à mostra. */
  window.addEventListener("pageshow", function () {
    emCurso = false;
    travar(false);
    esconderProgresso();
    rotular();
  });

  rotular();
})();
