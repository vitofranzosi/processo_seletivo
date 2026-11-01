/*
As três alternativas leem a mesma projeção (dados.js), exportada pelas funções da agenda: fase,
espécie e período vêm do backend, e o navegador só recorta o mês e posiciona.

A posição é por dia, e não por hora. A primeira versão do estudo somava a fração do dia à meia
coluna de centralização, e todo evento depois do meio-dia caía na coluna do dia seguinte. Aqui um
marco ocupa o centro da coluna do seu dia e um período vai da coluna do primeiro dia à do último,
inclusive — a mesma pertinência de `Periodo.abrange`, que dá o número da grade (FR-2669).
*/
"use strict";
const $ = (id) => document.getElementById(id);
const P = new URLSearchParams(location.search);
const visao = ["a", "b", "c"].includes(P.get("visao")) ? P.get("visao") : "c";
const cenario = ["denso", "demo", "sucessao", "retificacao"].includes(P.get("cenario")) ? P.get("cenario") : "denso";
const referencia = P.get("referencia") === "2026-11-05" ? "2026-11-05" : "2026-11-01";
const mes = /^20\d\d-(0[1-9]|1[0-2])$/.test(P.get("mes") || "") ? P.get("mes") : "2026-11";
const ordem = P.get("ordem") === "numero" ? "numero" : "proximo";
// O filtro seleciona Editais e mostra todas as etapas deles, ou mostra só os eventos que o
// atendem. As duas leituras servem a tarefas diferentes, e a tela diz qual está valendo.
const alcance = P.get("alcance") === "eventos" ? "eventos" : "editais";
const [ano, numMes] = mes.split("-").map(Number);
const diasNoMes = new Date(Date.UTC(ano, numMes, 0)).getUTCDate();
const inicioMes = `${mes}-01`, fimMes = `${mes}-${String(diasNoMes).padStart(2, "0")}`;
const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];

const formatoDia = new Intl.DateTimeFormat("sv-SE", {timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit"});
const formatoInstante = new Intl.DateTimeFormat("pt-BR", {timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit"});
const formatoHora = new Intl.DateTimeFormat("pt-BR", {timeZone: "America/Sao_Paulo", hour: "2-digit", minute: "2-digit"});
const hora = (iso) => { const [h, m] = formatoHora.format(new Date(iso)).split(":"); return m === "00" ? `${+h}h` : `${+h}h${m}`; };
const dia = (iso) => iso ? formatoDia.format(new Date(iso)) : null;
const curta = (d) => d.slice(8) + "/" + d.slice(5, 7);
const entre = (a, b) => Math.round((Date.parse(b + "T00:00Z") - Date.parse(a + "T00:00Z")) / 864e5);
const contar = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;
const diaSemana = (d) => new Date(d + "T12:00Z").getUTCDay();

function el(tag, attrs = {}, filhos = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "texto") e.textContent = v; else e.setAttribute(k, v === true ? "" : v);
  }
  for (const f of [].concat(filhos)) if (f) e.append(f);
  return e;
}
function endereco(mudancas) {
  const p = new URLSearchParams(P);
  for (const [k, v] of Object.entries({visao, cenario, referencia, mes, ...mudancas})) {
    if (v === null || v === "") p.delete(k); else p.set(k, v);
  }
  return "?" + p;
}

// Um evento visto no mês: dias inteiros, recortados nas bordas, com o que ficou de fora dito.
function noMes(item) {
  const i = dia(item.inicio);
  const f = item.tipo === "pontual" ? i : dia(item.fim);
  if (i > fimMes || (f && f < inicioMes)) return null;
  return {
    ...item,
    diaInicio: i,
    diaFim: f,
    de: Math.max(1, i < inicioMes ? 1 : +i.slice(8)),
    ate: !f || f > fimMes ? diasNoMes : +f.slice(8),
    vemDeAntes: i < inicioMes,
    segueDepois: item.tipo === "periodo" && (!f || f > fimMes),
  };
}
function datas(item) {
  if (item.tipo === "pontual") return curta(item.diaInicio);
  return curta(item.diaInicio) + " a " + (item.diaFim ? curta(item.diaFim) : "sem término declarado");
}
// A régua é diária, mas o prazo que alguém cumpre tem hora: ela vai no texto.
const quando = (iso) => `${curta(dia(iso))} às ${hora(iso)}`;
const fase = (item) => item.cancelado ? "cancelado" : item.faseRotulo;
const rotuloEdital = (e) => `Edital ${e.numero}/${e.ano}`;

// O que está em jogo agora num Edital, a partir das fases do backend — nunca da data passada,
// que não prova realização.
function situacao(edital) {
  const ativos = edital.todos.filter((i) => !i.cancelado);
  const correndo = ativos.filter((i) => i.fase === "em_curso" && i.tipo === "periodo")
    .sort((a, b) => (a.fim || "9").localeCompare(b.fim || "9"));
  const proximo = ativos.filter((i) => i.fase === "por_vir").sort((a, b) => a.inicio.localeCompare(b.inicio))[0];
  const linhas = [];
  let chave = "9999";
  if (correndo.length) {
    const c = correndo[0];
    linhas.push(`Em curso: ${c.nome} — ${c.fim ? "encerra " + quando(c.fim) : "sem término definido"}`);
    if (c.fim) chave = dia(c.fim);
  }
  if (proximo) {
    linhas.push(`Próximo: ${proximo.nome} — ${proximo.tipo === "periodo" ? "começa " : ""}${quando(proximo.inicio)}`);
    if (dia(proximo.inicio) < chave) chave = dia(proximo.inicio);
  }
  if (!linhas.length) linhas.push("Nenhuma data futura no cronograma");
  return {linhas, chave};
}

function abrirDetalhes(edital, item) {
  $("origem-detalhe").textContent = `${rotuloEdital(edital)} · ${edital.processo}`;
  $("titulo-detalhe").textContent = item.nome;
  const campos = [
    ["Início previsto", formatoInstante.format(new Date(item.inicio))],
    ["Término previsto", item.fim ? formatoInstante.format(new Date(item.fim)) : item.tipo === "periodo" ? "Sem término declarado" : "Evento pontual"],
    ["Fase na referência", fase(item)],
    ["Espécie", {inscricoes: "Período de inscrições", etapa: "Ligado a uma Etapa", demais: "Demais Eventos"}[item.especie]],
    ["Local", item.local || "Não informado"],
    ["Origem", edital.origem],
  ];
  if (edital.aviso) campos.push(["Retificação a vigorar", edital.aviso]);
  const dl = el("dl");
  for (const [k, v] of campos) dl.append(el("dt", {texto: k}), el("dd", {texto: v}));
  $("corpo-detalhe").replaceChildren(dl, el("p", {class: "nota", texto: "No produto, este botão levaria ao detalhe do Edital. Datas previstas não comprovam realização."}));
  $("detalhes").showModal();
}
function botaoEvento(edital, item, conteudo, classe) {
  const b = el("button", {type: "button", class: classe}, conteudo);
  b.addEventListener("click", () => abrirDetalhes(edital, item));
  return b;
}

// --- A régua comum de A e C: colunas em porcentagem, e não em pixels, para caber em 343 px
// sem rolagem horizontal. A primeira A fixava 960 px e deixava 51 px de régua no celular.
const pos = (d) => ((d - 1) / diasNoMes * 100).toFixed(3) + "%";
const larg = (n) => (n / diasNoMes * 100).toFixed(3) + "%";
function regua() {
  const r = el("div", {class: "regua", "aria-hidden": "true"});
  for (let d = 1; d <= diasNoMes; d++) {
    const iso = `${mes}-${String(d).padStart(2, "0")}`;
    const classes = ["dia-regua"];
    if ([0, 6].includes(diaSemana(iso))) classes.push("fim-de-semana");
    if (iso === referencia) classes.push("referencia");
    if (d === 1 || (d % 5 === 0 && d <= diasNoMes - 2)) classes.push("marcado");
    r.append(el("span", {class: classes.join(" "), style: null, "data-dia": d, texto: d}));
  }
  return r;
}
function trilha(itens, {rotulos}) {
  const t = el("div", {class: "trilha", "aria-hidden": "true"});
  // Períodos que se sobrepõem no mesmo Edital vão a faixas distintas; o pontual tem a sua.
  const faixas = [];
  const periodos = itens.filter((i) => i.tipo === "periodo").sort((a, b) => a.de - b.de);
  for (const p of periodos) {
    let f = faixas.findIndex((fim) => fim < p.de);
    if (f < 0) { f = faixas.length; faixas.push(0); }
    faixas[f] = p.ate;
    const barra = el("span", {class: `barra ${p.fase}${p.vemDeAntes ? " vem-de-antes" : ""}${!p.diaFim ? " sem-termino" : p.segueDepois ? " segue-depois" : ""}`, "data-faixa": f, "data-de": p.de, "data-ate": p.ate}, rotulos ? el("span", {class: "rotulo-barra", texto: p.nome}) : null);
    barra.dataset.left = pos(p.de); barra.dataset.width = larg(p.ate - p.de + 1);
    t.append(barra);
  }
  // Pontuais no mesmo dia, ou em dias vizinhos, vão a faixas distintas: dois losangos
  // sobrepostos pareciam um evento só (T07, sorteio e resultado em 01/11).
  const pontuais = itens.filter((i) => i.tipo === "pontual").sort((a, b) => a.de - b.de);
  const faixasDosPontuais = [];
  for (const m of pontuais) {
    let f = faixasDosPontuais.findIndex((ultimo) => ultimo < m.de - 1);
    if (f < 0) { f = faixasDosPontuais.length; faixasDosPontuais.push(0); }
    faixasDosPontuais[f] = m.de;
    const marco = el("span", {class: `marco ${m.cancelado ? "anulado" : m.fase}`, "data-faixa": faixas.length + f, "data-dia": m.de});
    marco.dataset.left = ((m.de - 0.5) / diasNoMes * 100).toFixed(3) + "%";
    t.append(marco);
  }
  t.dataset.faixas = faixas.length + faixasDosPontuais.length;
  const refMes = referencia.slice(0, 7) === mes;
  if (refMes) {
    const linha = el("span", {class: "linha-referencia"});
    linha.dataset.left = ((+referencia.slice(8) - 0.5) / diasNoMes * 100).toFixed(3) + "%";
    t.append(linha);
  }
  return t;
}
// A CSP da gestão recusa style="" (091/092); a POC segue a mesma regra e posiciona pelo CSSOM.
function aplicarPosicoes(raiz) {
  for (const e of raiz.querySelectorAll("[data-left]")) {
    e.style.left = e.dataset.left;
    if (e.dataset.width) e.style.width = e.dataset.width;
    if (e.dataset.faixa) e.style.setProperty("--faixa", e.dataset.faixa);
  }
  for (const t of raiz.querySelectorAll(".trilha")) t.style.setProperty("--faixas", t.dataset.faixas);
  for (const t of raiz.querySelectorAll(".regua,.trilha")) t.style.setProperty("--dias", diasNoMes);
}

// Uma linha por evento: o nome inteiro, com quebra, e as datas com hora ao lado da régua.
// É a linha de A, e é o que C mostra ao abrir um Edital.
function continuidade(i) {
  if (i.tipo !== "periodo") return "";
  const partes = [];
  if (i.vemDeAntes) partes.push(`começou em ${curta(i.diaInicio)}`);
  if (!i.diaFim) partes.push("sem término definido");
  else if (i.diaFim > fimMes) partes.push(`continua até ${curta(i.diaFim)}`);
  return partes.join(" · ");
}
function linhaEvento(e, i) {
  const datasComHora = i.tipo === "pontual" ? quando(i.inicio) : `${quando(i.inicio)} a ${i.fim ? quando(i.fim) : "—"}`;
  const resto = continuidade(i);
  return botaoEvento(e, i, [
    el("span", {class: "coluna-identidade"}, [
      el("span", {class: "nome", texto: i.nome}),
      el("span", {class: "situacao", texto: `${datasComHora} · ${fase(i)}`}),
      resto ? el("span", {class: "continuidade", texto: resto}) : null,
    ]),
    trilha([i], {rotulos: false}),
  ], "linha-evento");
}

// --- C: uma linha por Edital. O desenho é a visão geral; a sequência textual abre embaixo.
function visaoC(editais) {
  const lista = el("div", {class: "faixas"});
  lista.append(el("div", {class: "cabecalho-faixas"}, [el("span", {class: "coluna-identidade", texto: `Edital · situação em ${curta(referencia)}`}), regua()]));
  for (const e of editais) {
    const s = situacao(e);
    const det = el("details", {class: "linha-edital"});
    const rotuloAbrir = () => det.open ? "Ocultar os eventos" : e.itens.length === 1 ? "Ver o evento do mês" : `Ver os ${e.itens.length} eventos do mês`;
    const abrir = el("span", {class: "abrir", texto: rotuloAbrir()});
    det.addEventListener("toggle", () => { abrir.textContent = rotuloAbrir(); });
    const ident = el("span", {class: "coluna-identidade"}, [
      el("strong", {texto: rotuloEdital(e)}),
      el("span", {class: "nome-do-processo", texto: e.processo}),
      ...s.linhas.map((t) => el("span", {class: "situacao-edital", texto: t})),
      abrir,
    ]);
    det.append(el("summary", {}, [ident, trilha(e.itens, {rotulos: true})]));
    if (e.aviso) det.append(el("p", {class: "aviso-edital", texto: e.aviso}));
    det.append(el("div", {class: "etapas"}, e.itens.map((i) => linhaEvento(e, i))));
    lista.append(det);
  }
  return lista;
}

// --- A: uma linha por evento, agrupadas por Edital.
function visaoA(editais) {
  const lista = el("div", {class: "faixas gantt"});
  lista.append(el("div", {class: "cabecalho-faixas"}, [el("span", {class: "coluna-identidade", texto: "Edital / evento"}), regua()]));
  for (const e of editais) {
    const grupo = el("details", {class: "grupo-gantt", open: true});
    grupo.append(el("summary", {}, [el("span", {class: "coluna-identidade"}, [el("strong", {texto: rotuloEdital(e)}), el("span", {class: "nome-do-processo", texto: e.processo})]), trilha(e.itens, {rotulos: false})]));
    if (e.aviso) grupo.append(el("p", {class: "aviso-edital", texto: e.aviso}));
    for (const i of e.itens) grupo.append(linhaEvento(e, i));
    lista.append(grupo);
  }
  return lista;
}

// --- B: cartões. Sem a faixa horizontal de largura fixa da primeira versão: parecia duração e
// não era. A duração vai em texto, e a distância até o próximo início também.
function visaoB(editais) {
  const lista = el("div", {class: "cartoes"});
  for (const e of editais) {
    const s = situacao(e);
    const ol = el("ol", {class: "linha-do-tempo"});
    e.itens.forEach((i, n) => {
      const li = el("li", {class: `${i.tipo} ${i.cancelado ? "anulado" : i.fase}`}, [
        el("span", {class: "data", texto: datas(i)}),
        botaoEvento(e, i, el("span", {texto: i.nome}), "nome-evento"),
        el("span", {class: "fase", texto: fase(i) + (i.tipo === "periodo" && i.diaFim ? ` · ${entre(i.diaInicio, i.diaFim) + 1} dias` : "")}),
      ]);
      const seg = e.itens[n + 1];
      if (seg && !i.cancelado) {
        const gap = entre(i.diaFim || i.diaInicio, seg.diaInicio);
        li.append(el("span", {class: "intervalo", texto: gap < 0 ? "o seguinte começa antes deste terminar" : gap === 0 ? "o seguinte, no mesmo dia" : `${contar(gap, "dia", "dias")} até o seguinte`}));
      }
      ol.append(li);
    });
    lista.append(el("article", {class: "cartao"}, [
      el("h3", {}, [el("span", {class: "sobretitulo", texto: rotuloEdital(e)}), el("span", {texto: e.processo})]),
      ...s.linhas.map((t) => el("p", {class: "situacao", texto: t})),
      e.aviso ? el("p", {class: "aviso-edital", texto: e.aviso}) : null,
      ol,
    ]));
  }
  return lista;
}

function iniciar() {
  const fonte = window.DADOS.referencias[referencia];
  let editais = [...fonte.demonstrativos, ...(cenario === "demo" ? [] : fonte.sinteticos)];
  if (cenario === "sucessao") editais = editais.filter((e) => e.numero === "T03");
  if (cenario === "retificacao") editais = editais.filter((e) => e.numero === "106");

  for (const id of ["especie", "fase", "ordem", "alcance"]) if (P.has(id)) $(id).value = P.get(id);
  $("cenario").value = cenario; $("referencia").value = referencia; $("visao").value = visao; $("mes").value = mes;
  $("filtros").open = window.innerWidth > 640;
  $("recorte").textContent = "· " + $("cenario").selectedOptions[0].textContent + (P.get("especie") || P.get("fase") ? " · com filtros" : "");
  for (const v of ["a", "b", "c"]) {
    $("link-" + v).href = endereco({visao: v});
    if (v === visao) $("link-" + v).setAttribute("aria-current", "page");
  }
  $("limpar").href = endereco({especie: null, fase: null, ordem: null, alcance: null});
  $("anterior").href = endereco({mes: new Date(Date.UTC(ano, numMes - 2, 1)).toISOString().slice(0, 7)});
  $("seguinte").href = endereco({mes: new Date(Date.UTC(ano, numMes, 1)).toISOString().slice(0, 7)});
  $("hoje").href = endereco({mes: referencia.slice(0, 7)});
  $("titulo-mes").textContent = MESES[numMes - 1][0].toUpperCase() + MESES[numMes - 1].slice(1) + " de " + ano;
  $("proveniencia").textContent = `Versão publicada vigente em ${curta(referencia)}/2026 às 12h. Editais 101 a 107: banco de demonstração ps_demo_101. T01 a T16: casos de teste, só em memória, com o formato de cronogramas públicos do Cefor e datas deslocadas.`;
  $("nome-alternativa").textContent = {
    c: "C · Uma faixa por Edital, sequência ao abrir",
    a: "A · Gantt, uma linha por evento",
    b: "B · Timeline em cartões",
  }[visao];
  legenda();

  const especie = $("especie").value, faseFiltro = $("fase").value;
  const filtrando = Boolean(especie || faseFiltro);
  const atende = (i) => (!especie || i.especie === especie) && (!faseFiltro || (!i.cancelado && i.fase === faseFiltro));
  const visiveis = editais.map((e) => {
    const doMes = e.itens.map(noMes).filter(Boolean);
    return {...e, todos: e.itens, atende: doMes.some(atende), itens: alcance === "eventos" ? doMes.filter(atende) : doMes};
  }).filter((e) => e.atende && e.itens.length);
  if (ordem === "proximo") visiveis.sort((a, b) => situacao(a).chave.localeCompare(situacao(b).chave) || a.numero.localeCompare(b.numero, "pt", {numeric: true}));

  const eventos = visiveis.flatMap((e) => e.itens);
  const nomeMes = MESES[numMes - 1];
  $("periodo-exibido").textContent = `Período exibido: ${nomeMes} de ${ano}. Situação calculada em ${curta(referencia)}/2026, 12h — não muda ao trocar de mês.`;
  $("resultado").textContent = `${contar(visiveis.length, "Edital", "Editais")} · ${contar(eventos.length, "evento", "eventos")} em ${nomeMes}` + (filtrando
    ? (alcance === "editais" ? " · o filtro escolhe os Editais; todos os eventos deles aparecem." : " · só os eventos que atendem ao filtro aparecem.")
    : ".");
  if (cenario === "retificacao") {
    const h = fonte.historico106;
    $("aviso").hidden = false;
    $("aviso").textContent = `Retificação do banco demonstrativo: a Prova objetiva passa de ${curta(dia(h[0].prova))} para ${curta(dia(h[1].prova))}, vigente a partir de ${formatoInstante.format(new Date(h[1].vigoraEm))}. Troque a referência para ver a outra versão.`;
  }
  // Na página completa, a grade real do produto vem antes de C, no lugar em que ela está hoje.
  if ($("grade") && window.GRADE) {
    const chave = cenario === "demo" ? "7" : "23";
    const igual = mes === "2026-11" && referencia === "2026-11-01" && ["demo", "denso"].includes(cenario);
    if (igual) $("grade").innerHTML = window.GRADE[chave];
    else $("grade").replaceChildren(el("p", {class: "nota", texto: "A grade real foi renderizada só para novembro, em 01/11, com 7 ou 23 Editais."}));
    $("titulo-mes").textContent = "Cronogramas dos Editais em " + MESES[numMes - 1];
  }
  const painel = $("painel");
  painel.replaceChildren(visiveis.length
    ? {a: visaoA, b: visaoB, c: visaoC}[visao](visiveis)
    : el("p", {class: "vazio", texto: "Nenhum evento toca este mês com estes filtros."}));
  aplicarPosicoes(painel);
}
function amostra(classe) { return el("span", {class: "amostra " + classe, "aria-hidden": "true"}); }
function legenda() {
  if (visao === "b") {
    $("legenda").replaceChildren(el("p", {texto: "Cartões em ordem de início. Sem escala comum entre cartões: a mesma altura não é a mesma data."}));
    return;
  }
  const itens = [
    [amostra("amostra-periodo"), "período"],
    [amostra("amostra-marco"), "evento pontual"],
    [amostra("amostra-hoje"), `dia da situação (${curta(referencia)})`],
    [el("span", {class: "amostra-texto", "aria-hidden": "true", texto: "‹ ›"}), "continua em outro mês"],
  ];
  $("legenda").replaceChildren(
    el("ul", {}, itens.map(([a, t]) => el("li", {}, [a, el("span", {texto: t})]))),
    el("p", {class: "legenda-secundaria", texto: "O preenchimento acompanha a fase, que também vem escrita: cheio, em curso; tracejado, ainda não começou; cinza, data passada."}),
  );
}
iniciar();
