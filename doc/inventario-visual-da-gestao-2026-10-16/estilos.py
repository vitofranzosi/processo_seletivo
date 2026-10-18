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

# A 091 divide a folha comum por área e muda regras de lugar onde a ordem não importa (R-003 da
# `091`): a sequência de `ESTILOS` muda por construção. `CONJUNTO` é a mesma soma sobre as regras
# **ordenadas**, cada uma com a cadeia de `@media`/`@supports` que a envolve — mover uma regra para
# outro arquivo, dentro de um `@media` igual, não muda o conjunto; mudar uma regra, sim.
CONJUNTO = r"""() => {
  const linhas = [];
  const andar = (regras, prefixo) => {
    for (const regra of regras) {
      if (regra.cssRules && regra.conditionText !== undefined) {
        andar(regra.cssRules, prefixo + '@' + regra.constructor.name + ' ' + regra.conditionText + ' | ');
      } else {
        linhas.push(prefixo + regra.cssText);
      }
    }
  };
  for (const folha of document.styleSheets) andar(folha.cssRules, '');
  // As regras que a 091 acrescenta no lugar dos `style=""` (`.simbolos`, `.largura-N`, `.altura-N`)
  // não existiam antes; contadas, o conjunto mudaria em toda tela. Ficam de fora da soma, e a
  // contagem as declara à parte. A 092 acrescenta as `.largura-N` do portal, que caem no mesmo
  // filtro; o rótulo "da 091" ficou, para os `resultados.json` das duas continuarem comparáveis, e
  // numa tela do portal ele quer dizer "da 092".
  const novas = linhas.filter((t) => /^\.(simbolos|largura-\d+|altura-\d+) \{/.test(t)).length;
  const antigas = linhas.filter((t) => !/^\.(simbolos|largura-\d+|altura-\d+) \{/.test(t));
  linhas.length = 0; linhas.push(...antigas);
  linhas.sort();
  let h = 2166136261;
  for (const t of linhas) { for (let i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 16777619); } h ^= 10; h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(16) + ' / ' + linhas.length + ' regras' + (novas ? ' + ' + novas + ' da 091' : '');
}"""

# As violações da política de segurança de conteúdo (091), em recusa e em observação: o evento que o
# documento dispara para cada uma. Registrado por `add_init_script`, antes de qualquer script da
# página — o `<style>` que o htmx injeta ao carregar dispara cedo.
ESCUTAR_VIOLACOES = r"""
window.__violacoes = [];
document.addEventListener('securitypolicyviolation', (e) => {
  window.__violacoes.push([e.disposition, e.effectiveDirective, e.blockedURI,
    (e.sourceFile || '').replace(location.origin, '') + ':' + e.lineNumber,
    (e.sample || '').slice(0, 60)].join(' '));
});
"""
VIOLACOES = "() => window.__violacoes || ['sem escuta']"
