/* Validação antes do envio (FR-026 da 003 / FR-006 da 002).

   Isto NÃO é fronteira de segurança e não substitui invariante nenhuma: quem decide continua
   sendo `editais.domain`, invocado pelo command, que recusa exatamente as mesmas coisas e mais
   as que só o servidor conhece. O que existe aqui é poupar uma ida ao servidor para descobrir o
   que já dava para saber na tela — e dizer onde está o problema, e não só que ele existe.

   Usa a Constraint Validation API em vez de mensagens próprias: `setCustomValidity` faz o
   navegador bloquear o envio, mover o foco para o campo e anunciar a mensagem pelo leitor de
   tela, sem que nada disto precise ser reimplementado. `aria-invalid` acompanha, porque a
   validade nativa não é exposta como estado ARIA em todos os leitores.

   As regras abaixo espelham `editais/domain/perfis.py` e `editais/domain/cronograma.py`. Quando
   o domínio mudar, elas ficam desatualizadas e o servidor continua correto — o pior que
   acontece é a pessoa descobrir no envio, que é como era antes. */
(function () {
  var formulario = document.getElementById("formulario");
  if (!formulario) return;

  function campo(linha, sufixo) {
    return linha.querySelector('[name$="-' + sufixo + '"]');
  }

  function texto(elemento) {
    return elemento ? elemento.value.trim() : "";
  }

  function marcar(elemento, mensagem) {
    if (!elemento) return;
    elemento.setCustomValidity(mensagem || "");
    if (mensagem) {
      elemento.setAttribute("aria-invalid", "true");
    } else {
      elemento.removeAttribute("aria-invalid");
    }
  }

  function linhas(classe) {
    return [].slice.call(formulario.querySelectorAll("fieldset.linha." + classe));
  }

  /* `NONE` e `UNLIMITED` não admitem limite; `LIMITED` exige um não negativo. É a dependência
     condicional que a pessoa mais erra: escolhe o tipo e esquece o campo ao lado. */
  function reservaDoPerfil(linha) {
    var tipo = texto(campo(linha, "reserveType")) || "NONE";
    var limite = campo(linha, "reserveLimit");
    if (!limite) return;
    var valor = texto(limite);
    if (tipo === "LIMITED") {
      if (valor === "") {
        marcar(limite, "Cadastro Reserva limitado exige um limite.");
      } else if (Number(valor) < 0) {
        marcar(limite, "O limite do Cadastro Reserva não pode ser negativo.");
      } else {
        marcar(limite, "");
      }
      return;
    }
    marcar(
      limite,
      valor === ""
        ? ""
        : tipo === "NONE"
          ? "Cadastro Reserva inexistente não admite limite. Apague o valor ou mude o tipo."
          : "Cadastro Reserva ilimitado não admite limite. Apague o valor ou mude o tipo."
    );
  }

  function vagasDoPerfil(linha) {
    var vagas = campo(linha, "immediateVacancies");
    var valor = texto(vagas);
    marcar(vagas, valor !== "" && Number(valor) < 0 ? "Vagas imediatas não podem ser negativas." : "");
  }

  /* Códigos de Perfil e de Modalidade são identidade dentro do seu escopo; repetir não é erro
     de digitação inofensivo, é dois Perfis que o Edital não consegue distinguir. */
  function codigosRepetidos(todas) {
    var vistos = {};
    todas.forEach(function (linha) {
      var codigo = campo(linha, "code");
      var valor = texto(codigo);
      if (!valor) return marcar(codigo, "");
      vistos[valor] = (vistos[valor] || 0) + 1;
    });
    todas.forEach(function (linha) {
      var codigo = campo(linha, "code");
      var valor = texto(codigo);
      if (!valor) return;
      marcar(codigo, vistos[valor] > 1 ? "Já há outro Perfil com o código " + valor + "." : "");
    });
  }

  function modalidadesDoPerfil(linha) {
    var area = campo(linha, "modalidades");
    if (!area) return;
    var vistos = {};
    var repetido = "";
    area.value.split("\n").forEach(function (bruta) {
      var conteudo = bruta.trim();
      if (!conteudo) return;
      // Mesma leitura de `forms._modalidades`: código antes do travessão, ou do hífen.
      var separador = conteudo.indexOf("—") >= 0 ? "—" : "-";
      var posicao = conteudo.indexOf(separador);
      var codigo = (posicao >= 0 ? conteudo.slice(0, posicao) : conteudo).trim() || conteudo;
      if (vistos[codigo] && !repetido) repetido = codigo;
      vistos[codigo] = true;
    });
    marcar(
      area,
      repetido ? "A modalidade " + repetido + " aparece mais de uma vez neste Perfil." : ""
    );
  }

  function datasDoEvento(linha) {
    var inicio = campo(linha, "startAt");
    var fim = campo(linha, "endAt");
    if (!inicio || !fim) return;
    var comeco = texto(inicio);
    var termino = texto(fim);
    marcar(
      fim,
      comeco && termino && comeco > termino
        ? "O término do Evento não pode ser anterior ao início."
        : ""
    );
  }

  function validar() {
    var perfis = linhas("perfil");
    perfis.forEach(function (linha) {
      reservaDoPerfil(linha);
      vagasDoPerfil(linha);
      modalidadesDoPerfil(linha);
    });
    codigosRepetidos(perfis);
    linhas("evento").forEach(datasDoEvento);
  }

  // Delegação no formulário: as linhas nascem e morrem pelo HTMX, e ouvir cada campo exigiria
  // religar tudo a cada troca. `input` e `change` sobem até aqui de qualquer profundidade.
  formulario.addEventListener("input", validar);
  formulario.addEventListener("change", validar);

  /* A validação nativa roda antes do evento `submit`, então revalidar aqui chegaria tarde para
     o que já estava marcado. O que este ouvinte resolve é o contrário: linha inserida pelo HTMX
     com valor inválido de origem, que nunca disparou `input`. Revalida e devolve a decisão ao
     navegador, que move o foco e anuncia a mensagem. */
  formulario.addEventListener("submit", function (evento) {
    validar();
    if (!formulario.checkValidity()) {
      evento.preventDefault();
      formulario.reportValidity();
    }
  });
  validar();
})();
