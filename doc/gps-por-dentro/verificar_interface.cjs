// Conferência sem navegador: exercita as composições contra os estados oficiais embutidos.
// A inspeção real de layout e controles é registrada separadamente em validacao.md.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const caminho = require('node:path');
const html = fs.readFileSync(caminho.join(__dirname, 'index.html'), 'utf8');
const dados = JSON.parse(html.match(/<script type="application\/json" id="dados">([\s\S]*?)<\/script>/)[1]);
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].slice(1);
const elementos = {};
const elemento = id => elementos[id] ||= { innerHTML: '', textContent: '', addEventListener() {}, focus() {} };
const contexto = vm.createContext({
  document: {
    getElementById(id) { return id === 'dados' ? { textContent: JSON.stringify(dados) } : elemento(id); },
    querySelector: elemento,
    querySelectorAll() { return []; },
    addEventListener() {},
  },
  location: { hash: '#inicio' },
  window: { addEventListener() {}, scrollTo() {} },
});
for (const script of scripts) new vm.Script(script[1]).runInContext(contexto);
let estados = 0;
const maximos = [1,1,1,3,1,1,2,2,6,3,1];
for (let cena = 0; cena < maximos.length; cena++) {
  for (let passo = 0; passo <= maximos[cena]; passo++) {
    const resultado = vm.runInContext(`estado.passo=${passo}; demos[${cena}]()`, contexto);
    assert.ok(resultado.length > 100);
    assert.doesNotMatch(resultado, /undefined|NaN/);
    if (passo === maximos[cena]) assert.match(resultado, /Efeito observado/);
    estados++;
  }
}
assert.match(vm.runInContext('estado.passo=1; demoCorte()', contexto), /5 pessoas distintas/);
assert.match(vm.runInContext('estado.passo=2; demoApuracao()', contexto), /nenhuma convocação feita ainda/);
assert.match(vm.runInContext('estado.passo=2; demoNova()', contexto), /vaga ainda falta/);
assert.match(vm.runInContext('estado.passo=3; demoNova()', contexto), /2 ocupadas/);
assert.doesNotMatch(vm.runInContext('estado.passo=0; demoMarco()', contexto), /—º|NaN/);
for (const id of vm.runInContext('conceitos.map(c=>c.id)', contexto)) {
  const resultado = vm.runInContext(`estado.passo=0; laboratorio(${JSON.stringify(id)})`, contexto);
  assert.match(resultado, /Serve para:/);
  assert.match(resultado, /Onde encontro no GPS/i);
  assert.match(resultado, /O que costuma confundir/i);
}
for (let i=0; i<7; i++) {
  assert.match(vm.runInContext(`estado.quiz[${i}]=perguntas[${i}].certa; desafio(${i})`, contexto), /Esse é o raciocínio/);
  assert.match(vm.runInContext(`estado.quiz[${i}]=(perguntas[${i}].certa+1)%perguntas[${i}].opcoes.length; desafio(${i})`, contexto), /Vale olhar para o efeito/);
}
assert.match(vm.runInContext("resultadosBusca('apuração')", contexto), /Apuração de ocupação/);
assert.match(vm.runInContext("resultadosBusca('zzzxq')", contexto), /Nenhum conceito encontrado/);
assert.match(html, /prefers-reduced-motion:reduce/);
assert.doesNotMatch(html, /<script[^>]+src=|<link[^>]+href=["']https?:/);
for (const alvo of [...html.matchAll(/href="(inventario|roteiro-pedagogico|validacao|avaliacao-critica)\.md"/g)]) {
  assert.ok(fs.existsSync(caminho.join(__dirname, alvo[1]+'.md')), alvo[1]+' ausente');
}
console.log(`${estados} estados de demonstração, 17 conceitos, 14 feedbacks, busca e ausência de dependências externas: OK.`);
