/* Navegação compartilhada do piloto. Os dados ficam aqui para que as quatro páginas
   não repitam o menu — e para que abrir o arquivo direto no navegador funcione. */

const SUMARIO = [
  { parte: 'Parte 1 — Entender o sistema', itens: [
    ['C-01', 'O que este sistema faz (e o que ele não faz)', null],
    ['C-02', 'As duas portas: a área de gestão e o portal público', null],
    ['C-03', 'O ciclo completo em um mapa', 'c-03-o-ciclo-em-um-mapa.html'],
    ['C-04', 'Quem faz o quê — e por que ninguém faz tudo', null],
    ['C-05', 'Cinco ideias que explicam todo o resto', null],
  ]},
  { parte: 'Parte 2 — As fases do processo', itens: [
    ['C-06', 'Abrir o Processo Seletivo e criar o Edital', null],
    ['C-07', 'Elaborar o Edital I — identificação, perfis, vagas e cronograma', null],
    ['C-08', 'Elaborar o Edital II — etapas de avaliação e regra de classificação', 'c-08-especimen-desempate.html'],
    ['C-09', 'Elaborar o Edital III — inscrição, anexos, conteúdo e revisão final', null],
    ['C-10', 'Submeter, homologar e publicar', null],
    ['C-11', 'O período de inscrições, visto de dentro', null],
    ['C-12', 'Inscrever-se — o manual do candidato', 'c-12-inscrever-se.html'],
    ['C-13', 'Montar a comissão e alocar por Etapa', null],
    ['C-14', 'Distribuir o trabalho', null],
    ['C-15', 'Avaliar — o manual do avaliador', null],
    ['C-16', 'Consolidar o resultado de cada Etapa', null],
    ['C-17', 'Classificar', null],
    ['C-18', 'Divulgar o resultado', 'c-18-divulgar-o-resultado.html'],
    ['C-19', 'Recursos — interpor, admitir e julgar', null],
    ['C-20', 'Refazer e republicar depois de um recurso', null],
    ['C-21', 'Encerrar o certame', null],
  ]},
  { parte: 'Parte 3 — Trilhas por papel', itens: [
    ['T-01', 'Gestor', null], ['T-02', 'Elaborador', null], ['T-03', 'Homologador', null],
    ['T-04', 'Publicador', null], ['T-05', 'Presidente da comissão', null],
    ['T-06', 'Avaliador', null], ['T-07', 'Julgador de recursos', null], ['T-08', 'Candidato', null],
  ]},
  { parte: 'Parte 4 — Tarefas frequentes', itens: [['R-01 a R-10', 'Dez receitas curtas, entrada por verbo', null]] },
  { parte: 'Parte 5 — Situações excepcionais', itens: [['X-01 a X-10', 'O que fazer quando dá errado', null]] },
  { parte: 'Parte 6 — Referência', itens: [
    ['G-01', 'Glossário', null], ['G-02', 'Mapa de todas as telas', null],
    ['G-03', 'O que o sistema não faz hoje', null], ['G-04', 'Perguntas frequentes', null],
    ['G-05', 'Nota para administradores', null],
  ]},
];

/* As 16 fases, para o quadro "onde estou". */
const FASES = [
  'Abrir', 'Elaborar', 'Aprovar', 'Publicar', 'Receber inscrições', 'Organizar a comissão',
  'Distribuir', 'Avaliar', 'Consolidar', 'Classificar', 'Divulgar', 'Recorrer', 'Julgar',
  'Refazer e republicar', 'Definitivo', 'Encerrar',
];

function montarMenu() {
  const alvo = document.querySelector('.lateral nav');
  if (!alvo) return;
  const aqui = document.body.dataset.capitulo || '';
  alvo.innerHTML = SUMARIO.map(({ parte, itens }) => `
    <div class="parte">
      <p>${parte}</p>
      <ul>${itens.map(([cod, nome, href]) => {
        const atual = cod === aqui;
        const link = href ? `href="${href}"` : 'href="#" aria-disabled="true"';
        return `<li class="${href ? '' : 'vazia'}"><a ${link}${atual ? ' aria-current="page"' : ''}>
          <span class="cod">${cod}</span>${nome}</a></li>`;
      }).join('')}</ul>
    </div>`).join('');
}

function montarOndeEstou() {
  document.querySelectorAll('.onde-estou[data-fase]').forEach(caixa => {
    const n = Number(caixa.dataset.fase);
    const ator = caixa.dataset.ator || '';
    caixa.innerHTML = `
      <p class="dizer">Fase <b>${n} de 16</b> · <b>${FASES[n - 1]}</b>${ator ? ` · o trabalho é ${ator}` : ''}</p>
      <div class="fita" role="img" aria-label="Fase ${n} de 16 do certame: ${FASES[n - 1]}">
        ${FASES.map((_, i) => `<i class="${i + 1 < n ? 'feita' : i + 1 === n ? 'atual' : ''}"></i>`).join('')}
      </div>
      <div class="legenda"><span>1 · Abrir</span><span>16 · Encerrar</span></div>`;
  });
}

/* Anotação sobre a imagem: as coordenadas vêm em porcentagem da própria captura,
   para que o retângulo acompanhe a imagem em qualquer largura de tela. */
function montarAlvos() {
  /* A imagem ganha uma moldura interna própria — é ela, e não o quadro, que dá as
     coordenadas dos retângulos. Sem isso, uma captura larga que rola dentro do quadro
     numa tela estreita levaria a anotação para longe do que ela aponta. */
  document.querySelectorAll('figure.captura .quadro').forEach(quadro => {
    const img = quadro.querySelector('img');
    if (!img) return;
    const tela = document.createElement('span');
    tela.className = 'tela';
    img.replaceWith(tela);
    tela.appendChild(img);
    if (!quadro.dataset.alvos) return;
    JSON.parse(quadro.dataset.alvos).forEach(([x, y, l, a, numero]) => {
      const caixa = document.createElement('span');
      caixa.className = 'alvo';
      caixa.style.cssText = `left:${x}%;top:${y}%;width:${l}%;height:${a}%`;
      if (numero) caixa.innerHTML = `<span class="numero">${numero}</span>`;
      tela.appendChild(caixa);
    });
  });
}

function ligarMenuEstreito() {
  const botao = document.querySelector('.abre-menu');
  if (!botao) return;
  botao.addEventListener('click', () => {
    const lateral = document.querySelector('.lateral');
    const aberta = lateral.classList.toggle('aberta');
    botao.setAttribute('aria-expanded', String(aberta));
    botao.textContent = aberta ? 'Fechar o sumário' : 'Sumário do manual';
  });
}

montarMenu();
montarOndeEstou();
montarAlvos();
ligarMenuEstreito();
