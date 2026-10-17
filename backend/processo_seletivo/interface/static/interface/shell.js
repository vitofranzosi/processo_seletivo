/* A barra lateral retrátil do shell da gestão (076, FR-1725 a FR-1729).

   **Carregado sem `defer`, de dentro da própria `.shell`**, logo depois de ela abrir: o atributo
   `data-barra` precisa estar no lugar antes de a barra ser lida pelo navegador, ou ela apareceria
   expandida e recolheria diante de quem acabou de chegar (FR-1728). Daqui, `currentScript` é o
   próprio elemento, e o pai dele é a `.shell` — sem procurar nada no documento.

   Sem este script nada some: a barra fica expandida, que é o desenho sem atributo, e o controle
   continua escondido (FR-1729). A escolha mora no armazenamento do navegador, e não no servidor —
   é preferência de apresentação, e não toca autenticação, autorização nem endereço. Navegação
   privada que recusa gravar não impede recolher; só a memória entre telas se perde. */
(function () {
  var CHAVE = "gps.barra";
  var RECOLHIDA = "recolhida";
  var EXPANDIDA = "expandida";
  // Sem escolha guardada, a barra começa recolhida em janela estreita: entre 64 e 80rem ela
  // comeria um quinto da largura de uma tela que já cabe com folga pequena (FR-1728).
  var JANELA_LARGA = "(min-width: 80rem)";

  function estadoInicial(guardado, larga) {
    if (guardado === RECOLHIDA || guardado === EXPANDIDA) return guardado;
    return larga ? EXPANDIDA : RECOLHIDA;
  }

  function alternar(estado) {
    return estado === RECOLHIDA ? EXPANDIDA : RECOLHIDA;
  }

  function ler(armazenamento) {
    try {
      return armazenamento ? armazenamento.getItem(CHAVE) : null;
    } catch (erro) {
      return null;
    }
  }

  function gravar(armazenamento, estado) {
    try {
      if (armazenamento) armazenamento.setItem(CHAVE, estado);
    } catch (erro) {
      // Armazenamento cheio ou recusado: a troca já valeu nesta tela, e é o que importa.
    }
  }

  /** O controle diz o que fará, e não o que a barra é (FR-1727). */
  function descrever(controle, estado) {
    var recolhida = estado === RECOLHIDA;
    controle.setAttribute("aria-expanded", recolhida ? "false" : "true");
    controle.rotulo.textContent = recolhida ? "Expandir a barra lateral" : "Recolher a barra lateral";
  }

  function armazenamentoDoNavegador() {
    try {
      return window.localStorage;
    } catch (erro) {
      return null;
    }
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      CHAVE: CHAVE,
      estadoInicial: estadoInicial,
      alternar: alternar,
      ler: ler,
      gravar: gravar,
      descrever: descrever,
    };
    return;
  }

  var shell = document.currentScript && document.currentScript.parentElement;
  if (!shell) return;
  var armazenamento = armazenamentoDoNavegador();
  shell.setAttribute(
    "data-barra",
    estadoInicial(ler(armazenamento), window.matchMedia(JANELA_LARGA).matches)
  );

  document.addEventListener("DOMContentLoaded", function () {
    var botao = shell.querySelector("[data-alternar-barra]");
    if (!botao) return;
    var controle = { setAttribute: botao.setAttribute.bind(botao), rotulo: botao.querySelector("[data-rotulo]") };
    descrever(controle, shell.getAttribute("data-barra"));
    botao.hidden = false;
    botao.addEventListener("click", function () {
      var novo = alternar(shell.getAttribute("data-barra"));
      // A transição só existe a partir de um gesto: no carregamento, a barra já nasce no estado.
      shell.setAttribute("data-animar", "");
      shell.setAttribute("data-barra", novo);
      descrever(controle, novo);
      gravar(armazenamento, novo);
    });
  });
})();
