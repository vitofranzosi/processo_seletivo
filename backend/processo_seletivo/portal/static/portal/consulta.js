// Os filtros recolhidos da vitrine (072, FR-1602, research T-002).
//
// No celular, unidade, situação, Perfil e ordenação ficam num <details> fechado; em tela larga a
// barra inteira cabe numa linha, e recolhê-la não ganharia nada. Este script só abre o grupo quando
// a tela é larga — não filtra, não envia, não guarda nada. Carregado sem `defer`, logo depois do
// <details>, para rodar antes da primeira pintura e não deslocar a página. Sem ele, o grupo fica
// fechado também em tela larga, e continua funcionando.
(function () {
  var grupo = document.currentScript && document.currentScript.previousElementSibling;
  if (!grupo || grupo.tagName !== "DETAILS" || !window.matchMedia) return;
  var larga = window.matchMedia("(min-width: 60rem)");
  function ajustar() {
    if (larga.matches) {
      grupo.open = true;
      grupo.classList.add("sempre-aberto");
    } else {
      grupo.classList.remove("sempre-aberto");
    }
  }
  ajustar();
  if (larga.addEventListener) larga.addEventListener("change", ajustar);
})();
