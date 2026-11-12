/* O envio dos documentos da convocação: um seletor por documento, um botão de envio só (150).

   Cada cartão da convocação é um formulário que envia só o seu arquivo e recarrega a página. Quem
   escolhia os quatro arquivos e clicava em "Enviar" num deles via um chegar e os outros três
   voltarem a "Nenhum arquivo escolhido", sem aviso nenhum — e o prazo corria.

   **Um botão só, no fim da lista** (D-001, revista em 12/11/2026). A primeira versão desta spec
   transformava o botão de cada cartão escolhido em "Enviar os N documentos escolhidos": com dois
   escolhidos, a pessoa via dois botões iguais para uma operação só, e lia cada um como o envio
   daquele cartão. Agora o botão do cartão sai de vista; o cartão diz o arquivo escolhido e que
   ainda não foi enviado, e oferece trocá-lo ou remover a escolha (FR-5603). O envio é o do fim da
   lista, que diz quantos vão — e com um só escolhido também: o caminho é o mesmo.

   **Um por requisição, em sequência** (D-002): o proxy limita o corpo do portal a um arquivo, e
   cada documento continua um envio próprio, com a validação, o prazo e a trilha de hoje. A rota é
   a mesma do envio de um; o cabeçalho `X-Envio-De-Varios: k/n` só troca o redirecionamento por
   JSON, que o `fetch` consegue ler (R-002). Com `n = 1` o servidor monta a confirmação de hoje.

   **A recusa de um não para os seguintes** (FR-5606). O arquivo acima do limite nem viaja: vai só o
   tamanho, e o servidor recusa com a frase de hoje (R-009). Terminado o lote, a página é recarregada
   na âncora que o servidor indicou — a confirmação, ou o cartão do primeiro recusado (R-004).

   **Queda de conexão ou acesso expirado no meio** (FR-5610): a página fica, diz junto do botão o
   que chegou e o que não foi enviado, e o que não foi continua escolhido. Do documento que estava
   subindo quando a conexão caiu não se sabe se chegou: a frase diz isso, e não "não recebido"
   (R-010).

   Sem script, nada disto existe: a área do envio nasce escondida, e cada cartão envia o seu, como
   antes (FR-5612).

   **O mesmo arquivo em dois documentos** (FR-5615 a FR-5619, D-006; achado 11 do estudo da jornada
   final): escolhido o arquivo, o script calcula o resumo SHA-256 dele aqui mesmo e o compara com o
   dos outros escolhidos e com o `data-resumo-recebido` dos outros cartões. Coincidindo, o cartão
   avisa, e o envio continua possível: um documento pode servir a dois itens. Sem `crypto.subtle`, ou
   com a leitura recusada, não há aviso, e nada diz que se comparou. O envio nunca espera o cálculo.

   **Nada é guardado no navegador** (FR-5611): nem nome de arquivo, nem progresso, nem resumo. */
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
  var SEM_ARQUIVO = "Escolha um arquivo PDF antes de enviar.";
  var RECEBIDO_AGORA = "Recebido agora.";
  var NENHUM = "Nenhum arquivo escolhido";
  var AINDA_NAO_UM = "O arquivo ainda não foi enviado à comissão.";
  var AINDA_NAO_VARIOS = "Os arquivos ainda não foram enviados à comissão.";

  var formularios = Array.prototype.slice.call(document.querySelectorAll("form[data-envio]"));
  var area = document.querySelector("[data-envio-dos-documentos]");
  if (!formularios.length || !area) return;
  var anuncio = document.querySelector("[data-anuncio-de-varios]");
  var botaoDoEnvio = area.querySelector("[data-enviar-os-escolhidos]");
  var contagem = area.querySelector("[data-contagem-da-escolha]");
  var orientacao = area.querySelector("[data-orientacao-da-escolha]");
  var progresso = area.querySelector("[data-progresso-do-lote]");
  var ajudaDoProgresso = progresso ? progresso.querySelector(".ajuda") : null;
  var progressoOriginal = ajudaDoProgresso ? ajudaDoProgresso.textContent : "";
  var recado = area.querySelector("[data-recado-do-lote]");
  /* A orientação sem escolha vem do servidor, que sabe se há um documento ou vários. */
  var orientacaoVazia = orientacao ? orientacao.textContent : "";
  /* Só com substituição, o rodapé aparece depois da escolha (`_envio_dos_documentos.html`). */
  var soComEscolha = Boolean(area.hasAttribute && area.hasAttribute("data-so-com-escolha"));
  var emCurso = false;
  var ultimaContagem = 0;
  /* O resumo de cada campo, preso ao arquivo de que veio: escolhido outro, o velho não vale. */
  var resumos = formularios.map(function () {
    return null;
  });

  function no(formulario, seletor) {
    return formulario.querySelector(seletor);
  }

  function campoDe(formulario) {
    return no(formulario, "[data-arquivo]");
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

  /* O "de M" conta as tarefas — o que falta enviar e o que a comissão pediu para corrigir —, e não
     a substituição espontânea nem o opcional: "1 de 4" com três substituições possíveis leria como
     três faltando. O servidor marca a tarefa no cartão. */
  function pendente(formulario) {
    var cartao = cartaoDe(formulario);
    return Boolean(cartao && cartao.hasAttribute && cartao.hasAttribute("data-tarefa"));
  }

  function escolhidos() {
    return formularios.filter(arquivoDe);
  }

  function anunciar(texto) {
    if (anuncio) anuncio.textContent = texto;
  }

  function mostrar(elemento, sim) {
    if (elemento) elemento.hidden = !sim;
  }

  function documentos(quantos) {
    return quantos === 1 ? "1 documento" : quantos + " documentos";
  }

  function emLista(nomesDosDocumentos) {
    if (nomesDosDocumentos.length < 2) return nomesDosDocumentos.join("");
    return (
      nomesDosDocumentos.slice(0, -1).join(", ") +
      " e " +
      nomesDosDocumentos[nomesDosDocumentos.length - 1]
    );
  }

  function resumoDe(formulario) {
    var calculado = resumos[formularios.indexOf(formulario)];
    var arquivo = arquivoDe(formulario);
    return calculado && arquivo && calculado.arquivo === arquivo ? calculado.resumo : "";
  }

  /* O aviso de cada cartão, refeito inteiro a cada mudança: a troca ou a remoção num cartão tira o
     aviso do outro também (FR-5617). O próprio cartão não conta — o mesmo arquivo de novo no mesmo
     documento o servidor já reconhece (FR-3581 da `115`). */
  function avisarRepetidos() {
    var recebidos = Array.prototype.slice.call(
      document.querySelectorAll("[data-resumo-recebido]")
    );
    formularios.forEach(function (formulario) {
      var aviso = no(formulario, "[data-arquivo-repetido]");
      if (!aviso) return;
      var resumo = resumoDe(formulario);
      var cartao = cartaoDe(formulario);
      var escolhidoPara = [];
      var enviadoPara = [];
      if (resumo) {
        formularios.forEach(function (outro) {
          if (outro !== formulario && resumoDe(outro) === resumo) escolhidoPara.push(nomeDe(outro));
        });
        recebidos.forEach(function (outro) {
          if (outro !== cartao && outro.getAttribute("data-resumo-recebido") === resumo) {
            enviadoPara.push(outro.getAttribute("data-documento") || "");
          }
        });
      }
      var frases = [];
      if (escolhidoPara.length) {
        frases.push(
          "Atenção: este arquivo é o mesmo que você escolheu para " + emLista(escolhidoPara) + "."
        );
      }
      if (enviadoPara.length) {
        frases.push(
          "Atenção: este arquivo é o mesmo que você já enviou para " + emLista(enviadoPara) + "."
        );
      }
      var texto = frases.join(" ");
      /* Anunciado quando aparece ou muda, pela região viva, sem mover o foco (UX-504). */
      if (texto && texto !== aviso.textContent) anunciar(texto);
      aviso.textContent = texto;
      aviso.hidden = !texto;
    });
  }

  function hexadecimal(digest) {
    return Array.prototype.map
      .call(new Uint8Array(digest), function (byte) {
        return ("0" + byte.toString(16)).slice(-2);
      })
      .join("");
  }

  /* No navegador, sem enviar nada (FR-5618): o arquivo, o resumo e o nome não saem daqui. */
  function calcularResumo(formulario) {
    var arquivo = arquivoDe(formulario);
    var sutil = window.crypto && window.crypto.subtle;
    if (!arquivo || !sutil || !arquivo.arrayBuffer) return;
    var indice = formularios.indexOf(formulario);
    arquivo
      .arrayBuffer()
      .then(function (bytes) {
        return sutil.digest("SHA-256", bytes);
      })
      .then(
        function (digest) {
          /* A escolha mudou enquanto o cálculo corria: o resultado é de um arquivo que já saiu. */
          if (arquivoDe(formulario) !== arquivo) return;
          resumos[indice] = { arquivo: arquivo, resumo: hexadecimal(digest) };
          avisarRepetidos();
        },
        function () {
          /* Sem resumo, sem aviso (FR-5619). */
        }
      );
  }

  /* O que a área e cada cartão dizem, a cada escolha (FR-5601, FR-5602, FR-5603, UX-501). */
  function rotular() {
    var lote = escolhidos();
    var quantos = lote.length;
    var pendentes = formularios.filter(pendente).length;
    var escolhidosPendentes = lote.filter(pendente).length;

    formularios.forEach(function (formulario) {
      var tem = Boolean(arquivoDe(formulario));
      mostrar(no(formulario, "[data-estado-da-escolha]"), tem);
      mostrar(no(formulario, "[data-remover-escolha]"), tem);
      mostrar(no(formulario, "[data-rotulo-escolher]"), !tem);
      mostrar(no(formulario, "[data-rotulo-trocar]"), tem);
      var cartao = cartaoDe(formulario);
      if (cartao && cartao.classList) cartao.classList.toggle("com-escolha", tem);
      var situacao = cartao ? cartao.querySelector("[data-some-com-a-escolha]") : null;
      if (situacao && situacao.classList) situacao.classList.toggle("oculto", tem);
    });

    /* Sem escolha, a área fica leve — contorno tracejado, sem a contagem —, e diz só o que fazer:
       uma caixa cinza com "Nenhum arquivo selecionado" pesava como um aviso. */
    if (area.classList) area.classList.toggle("vazia", quantos === 0);
    /* Durante o lote, e com o recado de um lote que parou, o rodapé fica: é onde a frase está. */
    if (soComEscolha) area.hidden = quantos === 0 && !emCurso && !(recado && !recado.hidden);
    mostrar(contagem, quantos > 0);

    if (contagem) {
      contagem.textContent =
        quantos === 0
          ? "Nenhum arquivo selecionado"
          : quantos === escolhidosPendentes && pendentes > 1
            ? /* "1 de 2 arquivos": concorda com o total, como se lê em voz alta. */
              quantos + " de " + pendentes + " arquivos selecionados"
            : quantos === 1
              ? "1 arquivo selecionado"
              : quantos + " arquivos selecionados";
    }
    if (orientacao) {
      orientacao.textContent =
        quantos === 0 ? orientacaoVazia : quantos === 1 ? AINDA_NAO_UM : AINDA_NAO_VARIOS;
    }
    if (botaoDoEnvio) {
      botaoDoEnvio.textContent = quantos === 0 ? "Enviar documentos" : "Enviar " + documentos(quantos);
      botaoDoEnvio.disabled = emCurso || quantos === 0;
    }
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
    avisarRepetidos();
    return quantos;
  }

  function travar(sim) {
    formularios.forEach(function (formulario) {
      var campo = campoDe(formulario);
      var remover = no(formulario, "[data-remover-escolha]");
      if (campo) campo.disabled = sim;
      if (remover) remover.disabled = sim;
    });
    if (botaoDoEnvio) botaoDoEnvio.disabled = sim;
  }

  function mostrarProgresso(texto) {
    if (progresso) {
      progresso.hidden = false;
      var barra = progresso.querySelector("progress");
      if (barra) barra.removeAttribute("value");
    }
    if (ajudaDoProgresso) ajudaDoProgresso.textContent = texto;
    anunciar(texto);
  }

  function esconderProgresso() {
    mostrar(progresso, false);
    if (ajudaDoProgresso) ajudaDoProgresso.textContent = progressoOriginal;
  }

  /* A frase no cartão — a recusa de um documento —, com a mesma marca de `envio.js`. */
  function dizerNoCartao(formulario, texto) {
    var alvo = cartaoDe(formulario) || formulario;
    var frase = alvo.querySelector(".recusa-do-envio");
    if (!frase) {
      frase = document.createElement("p");
      frase.className = "recusa recusa-do-envio";
      frase.setAttribute("role", "alert");
      alvo.appendChild(frase);
    }
    frase.textContent = texto;
  }

  function dizerNoEnvio(texto) {
    if (!recado) return;
    recado.textContent = texto;
    recado.hidden = !texto;
  }

  function limparEscolha(formulario, texto) {
    var campo = campoDe(formulario);
    if (campo) campo.value = "";
    var nome = no(formulario, "[data-nome-do-arquivo]");
    if (nome) {
      nome.textContent = texto || NENHUM;
      if (nome.classList) nome.classList.remove("escolhido");
    }
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
    var ficha = no(formulario, "[name=csrfmiddlewaretoken]");
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

  /* O lote parou no meio (FR-5610): a página fica, e a frase, junto do botão, diz o que chegou e o
     que não. */
  function parar(recebidos, recusados, naoEnviados, emVoo, frase) {
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
    dizerNoEnvio(partes.join(" "));
    rotular();
  }

  /* A volta precisa ser **outro** endereço, ou o navegador não recarrega: ir da página para ela
     mesma com âncora só rola a tela (R-004). O `?lote=N` do servidor resolve a primeira vez, e não a
     segunda — dois envios seguidos do mesmo tamanho, o caso comum com um documento por vez,
     voltavam ao endereço em que a página já estava, e ela ficava parada com o progresso à mostra.
     Quando coincide, a volta ganha `de-novo=1`; na vez seguinte, sem ele, já é outro endereço. */
  function voltar(volta) {
    var local = window.location;
    var atual = local && local.pathname !== undefined ? local.pathname + local.search : null;
    if (atual !== null && volta.split("#")[0] === atual) {
      volta = volta.replace("?", "?de-novo=1&");
    }
    local.assign(volta);
  }

  function enviarTodos(lote) {
    emCurso = true;
    travar(true);
    dizerNoEnvio("");
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
        voltar(volta);
        return null;
      }
      var formulario = lote[indice];
      mostrarProgresso(
        total === 1
          ? "Enviando " + nomeDe(formulario) + "… Não feche esta página."
          : "Enviando " + (indice + 1) + " de " + total + ": " + nomeDe(formulario) +
              "… Não feche esta página."
      );
      return pedir(formulario, indice + 1, total).then(
        function (resultado) {
          if (!resultado.dados) {
            parar(recebidos, recusados, lote.slice(indice), null, resultado.frase);
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
          parar(recebidos, recusados, lote.slice(indice + 1), formulario, CONEXAO);
          return null;
        }
      );
    }

    return passo(0);
  }

  /* Com script, a área aparece, a frase do envio único também, e o botão de cada cartão sai de
     vista: o envio é um só. O limite do arquivo, dito na frase de cima, deixa de se repetir em cada
     cartão — e continua na descrição acessível do campo (FR-3745 da `118`). */
  area.hidden = soComEscolha;
  Array.prototype.slice
    .call(document.querySelectorAll("[data-instrucao-com-script]"))
    .forEach(function (frase) {
      frase.hidden = false;
    });

  formularios.forEach(function (formulario) {
    mostrar(no(formulario, "[data-envio-do-cartao]"), false);
    var limite = no(formulario, "[data-limite-do-cartao]");
    if (limite && limite.classList) limite.classList.add("oculto");

    var campo = campoDe(formulario);
    if (campo) {
      campo.addEventListener("change", function () {
        rotular();
        calcularResumo(formulario);
      });
    }

    var remover = no(formulario, "[data-remover-escolha]");
    if (remover) {
      remover.addEventListener("click", function () {
        limparEscolha(formulario);
        rotular();
        /* O foco volta ao campo, e não se perde no botão que acabou de sumir. */
        if (campo && campo.focus) campo.focus();
      });
    }

    /* O formulário não tem mais botão à vista, mas ainda é formulário: um envio que escape por ele
       — o Enter de algum navegador, uma extensão — também vai pelo lote, e nunca leva um só e
       descarta os outros (FR-5600). Sem nada escolhido, a frase de hoje, no cartão (FR-5604). */
    formulario.addEventListener("submit", function (evento) {
      evento.preventDefault();
      evento.stopPropagation();
      if (emCurso) return;
      var lote = escolhidos();
      if (!lote.length) {
        dizerNoCartao(formulario, SEM_ARQUIVO);
        return;
      }
      enviarTodos(lote);
    });
  });

  if (botaoDoEnvio) {
    botaoDoEnvio.addEventListener("click", function () {
      if (emCurso) return;
      var lote = escolhidos();
      if (lote.length) enviarTodos(lote);
    });
  }

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
