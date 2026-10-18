"""As regras que a página aplica, como o navegador as leu, para o inventário (089).

Todas as folhas do documento, na ordem — externas e `<style>` —, regra a regra, pelo `cssText` que o
Chrome devolve depois de interpretar: a soma num FNV-1a de 32 bits, e a contagem. Mover a folha sem
mudar regra nenhuma tem de deixar os dois números iguais em todas as variantes. É a prova que o pixel
não dá sozinho — a hora na tela e a suavização do texto mudam entre duas capturas do mesmo código — e
que o estilo computado também não dá: larguras usadas e transições em curso variam de uma passada para
outra. A regra interpretada não varia, e pega também o que o navegador descartou: um comentário que
fechasse antes do fim levaria a regra seguinte junto, e a contagem cairia.
"""

ESTILOS = r"""() => {
  let h = 2166136261, n = 0;
  const mistura = (t) => { for (let i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619); } };
  for (const folha of document.styleSheets) {
    for (const regra of folha.cssRules) { mistura(regra.cssText + '\n'); n++; }
  }
  return (h >>> 0).toString(16) + ' / ' + n + ' regras';
}"""
