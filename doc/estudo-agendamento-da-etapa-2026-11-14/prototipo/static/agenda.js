/*
 * Protótipo do agendamento da Etapa (estudo de 14/11/2026). Nada aqui fala com o GPS.
 *
 * O estado do percurso mora no sessionStorage, para que a montagem, a conferência, a publicação e a
 * remarcação sejam um caminho só, de página em página, como seriam no sistema. Cada regra que o
 * estudo propõe para o backend está aqui na forma mais curta que a demonstra, e o comentário
 * aponta a regra (R-NN, em 02-proposta.md). Ela não é o código de produção: é a prova de que a
 * tela consegue dizer o que a regra exige.
 */
(function () {
  "use strict";

  var CHAVE = "gps-prototipo-agenda-v1";

  /* ---------------------------------------------------------------- dados fictícios */

  var PRIMEIROS = ["Ana", "Bruno", "Carla", "Daniel", "Elisa", "Fábio", "Gabriela", "Heitor",
    "Isabela", "João", "Karina", "Lucas", "Mariana", "Nicolas", "Olívia", "Paulo", "Quitéria",
    "Rafael", "Sofia", "Tiago", "Valéria", "Vitor", "Wanessa", "Yago", "Zilda", "Adriano",
    "Beatriz", "Caio", "Débora", "Eduardo", "Fernanda", "Gustavo", "Helena", "Igor", "Júlia",
    "Kleber", "Larissa", "Marcos", "Natália", "Otávio", "Priscila", "Renato", "Simone", "Talita"];
  var SOBRENOMES = ["Souza", "Lima", "Costa", "Silva", "Pereira", "Almeida", "Ribeiro", "Gomes",
    "Martins", "Rocha", "Carvalho", "Barbosa", "Araújo", "Dias", "Moreira", "Nunes", "Teixeira",
    "Cardoso", "Correia", "Pinto", "Vieira", "Monteiro"];
  var ALFABETO = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";

  function semente(n) {
    var x = n;
    return function () {
      x = (x * 1103515245 + 12345) % 2147483648;
      return x / 2147483648;
    };
  }

  function pessoas(quantas, base) {
    var sorte = semente(base);
    var lista = [];
    for (var i = 0; i < quantas; i++) {
      var nome = PRIMEIROS[(i * 7 + base) % PRIMEIROS.length] + " " +
        SOBRENOMES[Math.floor(sorte() * SOBRENOMES.length)] + " " +
        SOBRENOMES[Math.floor(sorte() * SOBRENOMES.length)];
      var protocolo = "INS-2026-";
      for (var j = 0; j < 8; j++) protocolo += ALFABETO[Math.floor(sorte() * ALFABETO.length)];
      lista.push({ id: "p" + base + "-" + i, nome: nome, protocolo: protocolo });
    }
    return lista;
  }

  var CENARIOS = {
    a: {
      rotulo: "Entrevista",
      etapa: "Etapa 2 · Entrevista",
      etapaCurta: "Entrevista",
      edital: "Edital 81/2026",
      oferta: "Especialização em Informática na Educação",
      anterior: "Etapa 1 · Análise documental",
      evento: { inicio: "2026-11-23", fim: "2026-11-25", rotulo: "Entrevistas, de 23 a 25/11/2026" },
      identificacao: "nome",
      config: {
        modalidade: "remota", duracao: 10, intervalo: 5,
        dias: [{ data: "2026-11-23", janelas: [["08:00", "12:00"], ["13:00", "17:00"]] }],
        bancas: [{ id: "b1", nome: "Banca 1", acesso: "https://conferenciaweb.rnp.br/sala/cefor-entrevista-1" }],
        orientacoes: "Entre na sala com até 5 minutos de antecedência, com documento de identificação com foto. A entrevista dura cerca de 10 minutos e segue a ficha do Anexo IV do Edital."
      },
      participantes: pessoas(43, 3),
      novo: { id: "pnovo", nome: "Rebeca Andrade Nunes", protocolo: "INS-2026-Q8M2KX7T" }
    },
    b: {
      rotulo: "Verificação da autodeclaração",
      etapa: "Etapa 3 · Verificação da autodeclaração (heteroidentificação)",
      etapaCurta: "Verificação da autodeclaração",
      edital: "Edital 81/2026",
      oferta: "Especialização em Informática na Educação",
      anterior: "Etapa 2 · Entrevista",
      evento: { inicio: "2026-11-23", fim: "2026-11-24", rotulo: "Verificação da autodeclaração, de 23 a 24/11/2026" },
      identificacao: "protocolo",
      config: {
        modalidade: "remota", duracao: 20, intervalo: 10,
        dias: [{ data: "2026-11-23", janelas: [["08:00", "12:00"]] }],
        bancas: [
          { id: "b1", nome: "Banca 1", acesso: "https://conferenciaweb.rnp.br/sala/cefor-clva-1" },
          { id: "b2", nome: "Banca 2", acesso: "https://conferenciaweb.rnp.br/sala/cefor-clva-2" }
        ],
        orientacoes: "Entre na sala com até 5 minutos de antecedência. No campo do nome, informe o número do seu documento de identificação, e não o seu nome. Tenha em mãos o documento original com foto. Esteja num ambiente iluminado, sem boné, chapéu ou maquiagem. Se você tem menos de 18 anos, um responsável legal deve acompanhar a entrevista. A entrevista é gravada em áudio e vídeo."
      },
      participantes: pessoas(23, 11),
      novo: { id: "pnovo", nome: "Rebeca Andrade Nunes", protocolo: "INS-2026-Q8M2KX7T" }
    }
  };

  /* ---------------------------------------------------------------- estado */

  function novoEstado(cenario) {
    var c = CENARIOS[cenario];
    return {
      cenario: cenario,
      configurada: false,
      config: JSON.parse(JSON.stringify(c.config)),
      alocacoes: {},
      versao: 1,
      previa: null,
      concorrente: null,
      novoParticipa: false,
      publicada: null,
      remarcacoes: [],
      avisos: {},
      mensagem: null
    };
  }

  function ler() {
    try {
      var bruto = window.sessionStorage.getItem(CHAVE);
      if (bruto) return JSON.parse(bruto);
    } catch (e) { /* o protótipo funciona sem armazenamento: recomeça a cada página */ }
    return novoEstado("a");
  }

  function gravar(estado) {
    try { window.sessionStorage.setItem(CHAVE, JSON.stringify(estado)); } catch (e) { /* idem */ }
  }

  var estado = ler();
  var parametros = new URLSearchParams(window.location.search);
  if (parametros.get("cenario") && CENARIOS[parametros.get("cenario")] &&
      parametros.get("cenario") !== estado.cenario) {
    estado = novoEstado(parametros.get("cenario"));
    gravar(estado);
  }
  var C = CENARIOS[estado.cenario];

  function participantes() {
    var lista = C.participantes.slice();
    if (estado.novoParticipa) lista.push(C.novo);
    return lista;
  }

  function pessoa(id) {
    var lista = C.participantes.concat([C.novo]);
    for (var i = 0; i < lista.length; i++) if (lista[i].id === id) return lista[i];
    return null;
  }

  /* ---------------------------------------------------------------- horários (R-03 a R-06) */

  function minutos(hhmm) {
    var p = hhmm.split(":");
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
  }

  function hhmm(m) {
    var h = Math.floor(m / 60), mm = m % 60;
    return (h < 10 ? "0" : "") + h + ":" + (mm < 10 ? "0" : "") + mm;
  }

  var DIAS_DA_SEMANA = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado"];

  function dataPorExtenso(iso, curta) {
    var p = iso.split("-");
    var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
    var dia = DIAS_DA_SEMANA[d.getUTCDay()];
    if (curta) dia = dia.slice(0, 3) + ".";
    return dia.charAt(0).toUpperCase() + dia.slice(1) + ", " + p[2] + "/" + p[1];
  }

  /* Os horários não são gravados: derivam da configuração (R-04). Cada um vale para uma banca. */
  function horarios(config) {
    var lista = [];
    config.dias.forEach(function (dia) {
      dia.janelas.forEach(function (janela) {
        var ini = minutos(janela[0]), fim = minutos(janela[1]);
        for (var t = ini; t + config.duracao <= fim; t += config.duracao + config.intervalo) {
          config.bancas.forEach(function (banca, ordem) {
            lista.push({
              id: dia.data + "T" + hhmm(t) + "|" + banca.id,
              data: dia.data, inicio: hhmm(t), fim: hhmm(t + config.duracao),
              banca: banca.id, bancaNome: banca.nome, ordemBanca: ordem, minuto: t
            });
          });
        }
      });
    });
    lista.sort(function (a, b) {
      return a.data < b.data ? -1 : a.data > b.data ? 1 : a.minuto - b.minuto || a.ordemBanca - b.ordemBanca;
    });
    return lista;
  }

  /* Recusas da configuração (R-05). Cada frase diz o que fazer, e não só o que está errado. */
  function problemasDaConfiguracao(config) {
    var problemas = [];
    if (!(config.duracao > 0)) problemas.push("Informe a duração de cada atendimento, em minutos.");
    if (!(config.intervalo >= 0)) problemas.push("O intervalo entre atendimentos não pode ser negativo. Use 0 para nenhum intervalo.");
    if (!config.dias.length) problemas.push("Acrescente ao menos um dia de atendimento.");
    if (!config.bancas.length) problemas.push("Acrescente ao menos uma banca.");
    config.dias.forEach(function (dia) {
      if (dia.data < C.evento.inicio || dia.data > C.evento.fim) {
        problemas.push(dataPorExtenso(dia.data) + " está fora do período da Etapa no cronograma publicado (" +
          C.evento.rotulo.split(", ")[1] + "). Escolha um dia dentro dele; mudar o período pede Retificação.");
      }
      var ordenadas = dia.janelas.slice().sort(function (a, b) { return minutos(a[0]) - minutos(b[0]); });
      ordenadas.forEach(function (j, i) {
        var ini = minutos(j[0]), fim = minutos(j[1]);
        if (fim <= ini) {
          problemas.push("Em " + dataPorExtenso(dia.data, true) + ", a janela " + j[0] + "–" + j[1] + " termina antes de começar.");
        } else if (fim - ini < config.duracao) {
          problemas.push("Em " + dataPorExtenso(dia.data, true) + ", a janela " + j[0] + "–" + j[1] +
            " não comporta um atendimento de " + config.duracao + " minutos. Amplie a janela ou reduza a duração.");
        }
        if (i > 0 && minutos(ordenadas[i - 1][1]) > ini) {
          problemas.push("Em " + dataPorExtenso(dia.data, true) + ", as janelas " + ordenadas[i - 1].join("–") +
            " e " + j.join("–") + " se sobrepõem. Ajuste uma delas.");
        }
      });
    });
    var nomes = {};
    config.bancas.forEach(function (b) {
      if (!b.nome.trim()) problemas.push("Dê um nome a cada banca, como \"Banca 1\".");
      if (nomes[b.nome.trim()]) problemas.push("Duas bancas se chamam \"" + b.nome + "\". Os nomes aparecem para o candidato e precisam ser distintos.");
      nomes[b.nome.trim()] = true;
    });
    return problemas;
  }

  /* As sobras não são erro: são informação que explica a capacidade (R-05). */
  function sobras(config) {
    var frases = [];
    config.dias.forEach(function (dia) {
      dia.janelas.forEach(function (j) {
        var ini = minutos(j[0]), fim = minutos(j[1]), passo = config.duracao + config.intervalo;
        if (fim <= ini || passo <= 0) return;
        var n = 0;
        for (var t = ini; t + config.duracao <= fim; t += passo) n++;
        var ultimoFim = ini + (n - 1) * passo + config.duracao;
        if (n > 0 && fim - ultimoFim > config.intervalo && fim - ultimoFim < config.duracao + config.intervalo) {
          frases.push("Em " + dataPorExtenso(dia.data, true) + ", o último atendimento da janela " + j.join("–") +
            " termina às " + hhmm(ultimoFim) + ": sobram " + (fim - ultimoFim) + " minutos, que não cabem outro atendimento.");
        }
      });
    });
    return frases;
  }

  function mapaDeOcupacao() {
    var mapa = {};
    Object.keys(estado.alocacoes).forEach(function (pid) {
      mapa[estado.alocacoes[pid].horario] = pid;
    });
    return mapa;
  }

  function semHorario() {
    return participantes().filter(function (p) { return !estado.alocacoes[p.id]; });
  }

  /* A ordem do preenchimento automático é uma só e está escrita na tela (R-09): nome, e o
     protocolo no empate; horários do mais cedo ao mais tarde, e as bancas lado a lado. */
  function ordemDoPreenchimento(lista) {
    return lista.slice().sort(function (a, b) {
      return a.nome.localeCompare(b.nome, "pt-BR") || (a.protocolo < b.protocolo ? -1 : 1);
    });
  }

  function previaDoPreenchimento() {
    var ocupado = mapaDeOcupacao();
    var livres = horarios(estado.config).filter(function (h) {
      return !ocupado[h.id] && estado.concorrente !== h.id;
    });
    var fila = ordemDoPreenchimento(semHorario());
    var pares = [];
    for (var i = 0; i < fila.length && i < livres.length; i++) pares.push({ pessoa: fila[i].id, horario: livres[i].id });
    return { versao: estado.versao, pares: pares, restam: fila.length - pares.length };
  }

  function horarioPorId(id) {
    var lista = horarios(estado.config);
    for (var i = 0; i < lista.length; i++) if (lista[i].id === id) return lista[i];
    return null;
  }

  function rotuloDoHorario(id, curto) {
    var h = horarioPorId(id);
    if (!h) {
      var partes = id.split("|"), dt = partes[0].split("T");
      return dataPorExtenso(dt[0], curto) + ", " + dt[1];
    }
    var texto = dataPorExtenso(h.data, curto) + ", " + h.inicio;
    if (estado.config.bancas.length > 1) texto += " · " + h.bancaNome;
    return texto;
  }

  /* ---------------------------------------------------------------- utilidades de tela */

  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function plural(n, um, varios) { return n + " " + (n === 1 ? um : varios); }

  function preencher(seletor, html) {
    var alvo = document.querySelector(seletor);
    if (alvo) alvo.innerHTML = html;
    return alvo;
  }

  function textos() {
    document.querySelectorAll("[data-texto]").forEach(function (el) {
      var chave = el.getAttribute("data-texto");
      var valor = {
        etapa: C.etapa, etapaCurta: C.etapaCurta, edital: C.edital, oferta: C.oferta,
        anterior: C.anterior, evento: C.evento.rotulo, rotulo: C.rotulo,
        identificacao: C.identificacao === "nome" ? "nome e protocolo" : "só o protocolo"
      }[chave];
      if (valor !== undefined) el.textContent = valor;
    });
    document.querySelectorAll("[data-so-cenario]").forEach(function (el) {
      el.hidden = el.getAttribute("data-so-cenario") !== estado.cenario;
    });
  }

  function mensagem() {
    if (!estado.mensagem) return "";
    var m = estado.mensagem;
    estado.mensagem = null;
    gravar(estado);
    return '<p class="' + m.tipo + '" role="' + (m.tipo === "erro" ? "alert" : "status") + '">' + m.texto + "</p>";
  }

  function avisar(tipo, texto) { estado.mensagem = { tipo: tipo, texto: texto }; }

  function mudou() { estado.versao += 1; gravar(estado); }

  function resumoDaCapacidade() {
    var total = participantes().length;
    var capacidade = horarios(estado.config).length;
    var agendadas = Object.keys(estado.alocacoes).length;
    return { total: total, capacidade: capacidade, agendadas: agendadas, sem: total - agendadas,
      livres: capacidade - agendadas, falta: Math.max(0, total - capacidade) };
  }

  function faixaDeResumo(r) {
    return '<ul class="resumo resumo-da-agenda">' +
      "<li><strong>" + r.total + "</strong> participam da Etapa</li>" +
      "<li><strong>" + r.capacidade + "</strong> horários na agenda</li>" +
      "<li><strong>" + r.agendadas + "</strong> com horário</li>" +
      '<li class="' + (r.sem ? "pendente" : "") + '"><strong>' + r.sem + "</strong> sem horário</li>" +
      "<li><strong>" + Math.max(0, r.livres) + "</strong> horários livres</li></ul>";
  }

  function avisoDeCapacidade(r, comLink) {
    if (!r.falta) return "";
    return '<p class="aviso" role="status"><strong>Faltam ' + plural(r.falta, "horário", "horários") +
      ".</strong> São " + r.total + " pessoas e " + r.capacidade + " horários. Acrescente um dia, uma janela ou uma banca, ou reduza a duração ou o intervalo." +
      (comLink ? ' <a href="configurar.html">Ajustar a configuração</a>' : "") + "</p>";
  }

  /* ---------------------------------------------------------------- página: Etapa */

  function paginaEtapa() {
    var r = resumoDaCapacidade();
    var html;
    if (estado.publicada) {
      html = '<p><span class="situacao s-PUBLICADO">Agenda publicada</span> em ' + estado.publicada.em +
        " por " + esc(estado.publicada.autoridade) + ".</p>" + faixaDeResumo(r) +
        '<p class="acoes"><a class="botao" href="publicada.html">Ver a agenda publicada</a></p>';
    } else if (estado.configurada) {
      html = '<p><span class="situacao s-EM_ELABORACAO">Agenda em montagem</span> Nada é público até você conferir e publicar.</p>' +
        faixaDeResumo(r) + avisoDeCapacidade(r, true) +
        '<p class="acoes"><a class="botao" href="montar.html">Montar a agenda</a> <a class="acao" href="configurar.html">Ajustar a configuração</a></p>';
    } else {
      html = '<div class="vazio"><p><strong>Esta Etapa ainda não tem agenda.</strong></p>' +
        "<p>Se a Etapa exige que cada pessoa compareça num dia e horário, configure os dias, as janelas e as bancas. Dá para fazer isso antes de a lista de participantes estar fechada: a agenda acompanha a lista.</p>" +
        '<p><a class="botao" href="configurar.html">Configurar a agenda</a></p></div>';
    }
    preencher("#agenda-da-etapa", html);
  }

  /* ---------------------------------------------------------------- página: configurar */

  function paginaConfigurar() {
    var form = document.querySelector("#form-da-agenda");
    function desenhar() {
      var cfg = estado.config;
      form.querySelector("[name=modalidade][value=" + cfg.modalidade + "]").checked = true;
      form.querySelector("[name=duracao]").value = cfg.duracao;
      form.querySelector("[name=intervalo]").value = cfg.intervalo;
      form.querySelector("[name=orientacoes]").value = cfg.orientacoes;
      var dias = cfg.dias.map(function (dia, i) {
        var janelas = dia.janelas.map(function (j, k) {
          return '<li class="janela"><label><span class="oculto">Início da janela ' + (k + 1) + "</span>" +
            '<input type="time" step="300" data-dia="' + i + '" data-janela="' + k + '" data-ponta="0" value="' + j[0] + '"></label>' +
            '<span aria-hidden="true">–</span><label><span class="oculto">Fim da janela ' + (k + 1) + "</span>" +
            '<input type="time" step="300" data-dia="' + i + '" data-janela="' + k + '" data-ponta="1" value="' + j[1] + '"></label>' +
            (dia.janelas.length > 1 ? ' <button type="button" class="acao" data-remover-janela="' + i + ":" + k + '">Remover</button>' : "") + "</li>";
        }).join("");
        return '<fieldset class="dia-de-atendimento"><legend>' + dataPorExtenso(dia.data) + "</legend>" +
          '<ul class="janelas">' + janelas + "</ul>" +
          '<p class="acoes"><button type="button" class="acao" data-acrescentar-janela="' + i + '">Acrescentar janela</button>' +
          (cfg.dias.length > 1 ? ' <button type="button" class="acao" data-remover-dia="' + i + '">Remover o dia</button>' : "") + "</p></fieldset>";
      }).join("");
      preencher("#dias", dias);
      var remota = cfg.modalidade === "remota";
      var bancas = cfg.bancas.map(function (b, i) {
        return '<li class="banca"><p class="campo"><label for="banca-nome-' + i + '">Nome</label>' +
          '<input id="banca-nome-' + i + '" data-banca="' + i + '" data-campo="nome" value="' + esc(b.nome) + '"></p>' +
          '<p class="campo"><label for="banca-acesso-' + i + '">' + (remota ? "Endereço da sala virtual" : "Local") + "</label>" +
          '<input id="banca-acesso-' + i + '" data-banca="' + i + '" data-campo="acesso" value="' + esc(b.acesso) + '" aria-describedby="ajuda-acesso">' +
          "</p>" + (cfg.bancas.length > 1 ? '<button type="button" class="acao" data-remover-banca="' + i + '">Remover</button>' : "") + "</li>";
      }).join("");
      preencher("#bancas", bancas);
      preencher("#ajuda-acesso-texto", remota
        ? "O endereço da sala vai só para a área de cada pessoa e para o e-mail dela. A página pública mostra o nome da banca, nunca o endereço."
        : "O local aparece na área de cada pessoa, no e-mail e na página pública.");
      calcular();
    }

    function calcular() {
      var cfg = estado.config;
      var problemas = problemasDaConfiguracao(cfg);
      var lista = horarios(cfg);
      var porBanca = cfg.bancas.length ? lista.length / cfg.bancas.length : 0;
      var r = resumoDaCapacidade();
      var html = "";
      if (problemas.length) {
        html += '<div class="erro" role="alert"><strong>Corrija antes de continuar:</strong><ul>' +
          problemas.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul></div>";
      }
      html += '<p class="capacidade"><strong class="numero-grande">' + lista.length + "</strong> horários: " +
        plural(porBanca, "atendimento", "atendimentos") + " por banca × " + plural(cfg.bancas.length, "banca", "bancas") +
        ", em " + plural(cfg.dias.length, "dia", "dias") + ". Um atendimento começa a cada " + (cfg.duracao + cfg.intervalo) + " minutos.</p>";
      html += r.falta
        ? '<p class="aviso"><strong>Faltam ' + plural(r.falta, "horário", "horários") + "</strong> para as " + r.total + " pessoas que hoje participam da Etapa.</p>"
        : '<p class="sucesso">Cabem as ' + r.total + " pessoas que hoje participam da Etapa, e sobram " + plural(r.capacidade - r.total, "horário", "horários") + ".</p>";
      sobras(cfg).forEach(function (s) { html += '<p class="ajuda">' + esc(s) + "</p>"; });
      preencher("#calculo", html);
      form.querySelector("[data-salvar]").disabled = problemas.length > 0;
    }

    form.addEventListener("input", function (ev) {
      var el = ev.target, cfg = estado.config;
      if (el.name === "duracao") cfg.duracao = parseInt(el.value, 10) || 0;
      else if (el.name === "intervalo") cfg.intervalo = el.value === "" ? 0 : parseInt(el.value, 10);
      else if (el.name === "orientacoes") cfg.orientacoes = el.value;
      else if (el.name === "modalidade") { cfg.modalidade = el.value; desenhar(); gravar(estado); return; }
      else if (el.hasAttribute("data-janela")) {
        cfg.dias[+el.dataset.dia].janelas[+el.dataset.janela][+el.dataset.ponta] = el.value;
      } else if (el.hasAttribute("data-banca")) cfg.bancas[+el.dataset.banca][el.dataset.campo] = el.value;
      gravar(estado);
      calcular();
    });
    form.addEventListener("change", function (ev) {
      if (ev.target.name === "modalidade") { estado.config.modalidade = ev.target.value; gravar(estado); desenhar(); }
    });
    form.addEventListener("click", function (ev) {
      var el = ev.target, cfg = estado.config, d;
      if (el.hasAttribute("data-acrescentar-janela")) {
        d = cfg.dias[+el.dataset.acrescentarJanela];
        var ultima = d.janelas[d.janelas.length - 1];
        var ini = Math.min(minutos(ultima[1]) + 60, 22 * 60);
        d.janelas.push([hhmm(ini), hhmm(Math.min(ini + 120, 23 * 60))]);
      } else if (el.hasAttribute("data-remover-janela")) {
        var p = el.dataset.removerJanela.split(":");
        cfg.dias[+p[0]].janelas.splice(+p[1], 1);
      } else if (el.hasAttribute("data-remover-dia")) {
        cfg.dias.splice(+el.dataset.removerDia, 1);
      } else if (el.hasAttribute("data-acrescentar-dia")) {
        var datas = cfg.dias.map(function (x) { return x.data; });
        var ultimaData = datas.length ? datas[datas.length - 1] : C.evento.inicio;
        var q = ultimaData.split("-");
        var prox = new Date(Date.UTC(+q[0], +q[1] - 1, +q[2] + (datas.length ? 1 : 0)));
        var iso = prox.toISOString().slice(0, 10);
        var modelo = cfg.dias.length ? cfg.dias[cfg.dias.length - 1].janelas : [["08:00", "12:00"]];
        cfg.dias.push({ data: iso, janelas: JSON.parse(JSON.stringify(modelo)) });
      } else if (el.hasAttribute("data-acrescentar-banca")) {
        var n = cfg.bancas.length + 1;
        cfg.bancas.push({ id: "b" + Date.now(), nome: "Banca " + n, acesso: "" });
      } else if (el.hasAttribute("data-remover-banca")) {
        cfg.bancas.splice(+el.dataset.removerBanca, 1);
      } else return;
      gravar(estado);
      desenhar();
    });
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (problemasDaConfiguracao(estado.config).length) return;
      /* Mudar a configuração não move ninguém em silêncio (R-07): quem estava num horário que
         deixou de existir volta para "sem horário", e a tela da montagem diz quem foi. */
      var existentes = {};
      horarios(estado.config).forEach(function (h) { existentes[h.id] = true; });
      var devolvidas = [];
      Object.keys(estado.alocacoes).forEach(function (pid) {
        if (!existentes[estado.alocacoes[pid].horario]) { devolvidas.push(pessoa(pid).nome); delete estado.alocacoes[pid]; }
      });
      estado.configurada = true;
      if (devolvidas.length) {
        avisar("aviso", "<strong>A configuração foi salva, e " + plural(devolvidas.length, "pessoa voltou", "pessoas voltaram") +
          " para \"sem horário\"</strong>, porque o horário delas deixou de existir: " + esc(devolvidas.join(", ")) + ".");
      } else {
        avisar("sucesso", "Configuração salva. A agenda continua em montagem: nada é público até você conferir e publicar.");
      }
      mudou();
      window.location.href = "montar.html";
    });
    if (estado.publicada) {
      preencher("#trava-publicada", '<p class="imutavel">A agenda já foi publicada. Você pode acrescentar dias, janelas ou bancas para abrir horários novos; um horário já publicado só muda pela remarcação da pessoa.</p>');
    }
    desenhar();
  }

  /* ---------------------------------------------------------------- página: montar */

  var selecionada = null;

  function paginaMontar() {
    var diaAtual = parametros.get("dia");
    if (!estado.configurada) { window.location.href = "etapa.html"; return; }

    function desenhar() {
      var r = resumoDaCapacidade();
      var lista = horarios(estado.config);
      var ocupado = mapaDeOcupacao();
      var dias = estado.config.dias.map(function (d) { return d.data; });
      if (!diaAtual || dias.indexOf(diaAtual) < 0) diaAtual = dias[0];
      preencher("#mensagem", mensagem());
      preencher("#resumo", faixaDeResumo(r) + avisoDeCapacidade(r, true));

      var abas = dias.map(function (d) {
        var doDia = lista.filter(function (h) { return h.data === d; });
        var ocup = doDia.filter(function (h) { return ocupado[h.id]; }).length;
        return '<li><a href="?dia=' + d + '"' + (d === diaAtual ? ' aria-current="page"' : "") + ">" +
          dataPorExtenso(d, true) + ' <span class="contagem">' + ocup + "/" + doDia.length + "</span></a></li>";
      }).join("");
      preencher("#dias-da-agenda", abas);

      var bancas = estado.config.bancas;
      var doDia = lista.filter(function (h) { return h.data === diaAtual; });
      var porInicio = {};
      var ordem = [];
      doDia.forEach(function (h) {
        if (!porInicio[h.inicio]) { porInicio[h.inicio] = {}; ordem.push(h.inicio); }
        porInicio[h.inicio][h.banca] = h;
      });
      var cab = "<tr><th scope=\"col\">Horário</th>" + bancas.map(function (b) {
        return '<th scope="col">' + esc(b.nome) + "</th>";
      }).join("") + "</tr>";
      var corpo = ordem.map(function (ini) {
        var linha = '<tr><th scope="row">' + ini + '<span class="ate">até ' + porInicio[ini][bancas[0].id].fim + "</span></th>";
        bancas.forEach(function (b) {
          var h = porInicio[ini][b.id];
          var pid = ocupado[h.id];
          var rotuloBanca = bancas.length > 1 ? '<span class="banca-no-estreito">' + esc(b.nome) + "</span>" : "";
          if (pid) {
            var p = pessoa(pid);
            var origem = estado.alocacoes[pid].origem === "automatica" ? "preenchida automaticamente" : "escolhida à mão";
            var publicadaAqui = estado.publicada && estado.publicada.itens[pid] === h.id;
            linha += '<td class="ocupado' + (selecionada === pid ? " em-movimento" : "") + '">' + rotuloBanca +
              '<span class="quem">' + esc(p.nome) + '</span><span class="inscricao">' + p.protocolo + " · " + origem + "</span>" +
              (publicadaAqui
                ? '<span class="acoes"><a class="acao" href="remarcar.html?pessoa=' + pid + '">Remarcar</a></span>'
                : '<span class="acoes"><button type="button" class="acao" data-mover="' + pid + '">' + (selecionada === pid ? "Escolha o novo horário" : "Mudar de horário") + "</button>" +
                  '<button type="button" class="acao" data-liberar="' + pid + '">Liberar</button></span>') + "</td>";
          } else if (selecionada) {
            linha += '<td class="livre escolhendo">' + rotuloBanca + '<button type="button" class="acao" data-ocupar="' + h.id + '">Agendar ' +
              esc(pessoa(selecionada).nome.split(" ")[0]) + " aqui</button></td>";
          } else {
            linha += '<td class="livre">' + rotuloBanca + '<span class="livre-rotulo">Livre</span></td>';
          }
        });
        return linha + "</tr>";
      }).join("");
      preencher("#grade", '<caption>' + dataPorExtenso(diaAtual) + " · " + doDia.length + " horários, " +
        doDia.filter(function (h) { return ocupado[h.id]; }).length + " ocupados</caption><thead>" + cab + "</thead><tbody>" + corpo + "</tbody>");

      var sem = semHorario();
      var semHtml;
      if (!participantes().length) {
        semHtml = '<p class="vazio">Ninguém participa desta Etapa ainda. A lista sai do resultado da ' + esc(C.anterior) + ".</p>";
      } else if (!sem.length) {
        semHtml = '<p class="sucesso">Todas as ' + participantes().length + " pessoas têm horário. O próximo passo é conferir.</p>";
      } else {
        semHtml = '<fieldset class="escolha-de-pessoa"><legend class="oculto">Escolha uma pessoa e depois um horário livre</legend><ul class="sem-horario">' +
          ordemDoPreenchimento(sem).map(function (p) {
            return '<li><label><input type="radio" name="pessoa" value="' + p.id + '"' + (selecionada === p.id ? " checked" : "") + ">" +
              '<span class="quem">' + esc(p.nome) + '</span><span class="inscricao">' + p.protocolo + "</span></label></li>";
          }).join("") + "</ul></fieldset>";
      }
      preencher("#sem-horario-titulo", "Pessoas sem horário (" + sem.length + ")");
      preencher("#sem-horario", semHtml);
      preencher("#instrucao-manual", selecionada
        ? "Agora escolha um horário <strong>Livre</strong> na grade para " + esc(pessoa(selecionada).nome) + '. <button type="button" class="acao" data-cancelar-escolha>Cancelar</button>'
        : "Escolha uma pessoa e depois um horário livre na grade. Para trocar alguém de horário, use \"Mudar de horário\" na grade.");

      /* A ação principal é a que falta fazer: preencher enquanto há gente sem horário, conferir
         depois. Publicada a agenda, o preenchimento em bloco sai de cena (R-19): quem chega
         depois é agendado um a um, com aviso só para essa pessoa. */
      var botaoPreencher = document.querySelector("[data-preencher]");
      if (botaoPreencher) {
        botaoPreencher.hidden = !!estado.publicada;
        botaoPreencher.disabled = !sem.length || !r.livres;
        botaoPreencher.className = sem.length && r.livres ? "botao" : "botao secundario";
      }
      desenharPrevia();
      var conferir = document.querySelector("[data-ir-conferir]");
      if (conferir) conferir.className = sem.length && r.livres && !estado.publicada ? "botao secundario" : "botao";
      if (conferir) conferir.textContent = estado.publicada ? "Ver a agenda publicada" : "Conferir antes de publicar";
      if (conferir) conferir.setAttribute("href", estado.publicada ? "publicada.html" : "conferir.html");
    }

    function desenharPrevia() {
      var alvo = document.querySelector("#previa");
      if (!estado.previa) { alvo.hidden = true; alvo.innerHTML = ""; return; }
      var p = estado.previa;
      var linhas = p.pares.slice(0, 8).map(function (par) {
        return "<li>" + esc(pessoa(par.pessoa).nome) + " → " + rotuloDoHorario(par.horario, true) + "</li>";
      }).join("");
      alvo.hidden = false;
      alvo.innerHTML = '<h2 id="previa-titulo">Prévia do preenchimento</h2>' +
        "<p><strong>" + plural(p.pares.length, "pessoa receberá", "pessoas receberão") + " horário.</strong> " +
        (p.restam ? plural(p.restam, "pessoa continuará", "pessoas continuarão") + " sem horário, porque os horários livres acabam. " : "") +
        "Quem já tem horário não muda. Nada foi gravado ainda.</p>" +
        '<ol class="pares">' + linhas + (p.pares.length > 8 ? '<li class="mais">e mais ' + (p.pares.length - 8) + "</li>" : "") + "</ol>" +
        '<p class="ajuda">Ordem: pessoas por nome, e pelo protocolo no empate; horários do mais cedo ao mais tarde, ' +
        (estado.config.bancas.length > 1 ? "as bancas lado a lado em cada horário. " : "") + "Ajustes à mão continuam possíveis depois.</p>" +
        '<p class="acoes"><button type="button" class="botao" data-aplicar>Aplicar o preenchimento</button> <button type="button" class="acao" data-descartar>Descartar a prévia</button></p>';
    }

    document.addEventListener("change", function (ev) {
      if (ev.target.name === "pessoa") { selecionada = ev.target.value; desenhar(); }
    });

    document.addEventListener("click", function (ev) {
      var el = ev.target.closest("button");
      if (!el) return;
      if (el.hasAttribute("data-ocupar")) {
        var h = el.getAttribute("data-ocupar");
        /* Dois operadores no mesmo horário (R-11): quem chega depois é recusado pela unicidade
           do horário, e a tela diz quem ocupou e mostra a grade atual. */
        if (estado.concorrente === h) {
          var outra = semHorario().filter(function (x) { return x.id !== selecionada; }).pop();
          if (outra) estado.alocacoes[outra.id] = { horario: h, origem: "manual" };
          estado.concorrente = null;
          avisar("erro", "<strong>Esse horário acabou de ser ocupado</strong> por outra pessoa da comissão, noutra sessão. A grade foi atualizada; escolha outro horário para " +
            esc(pessoa(selecionada).nome) + ".");
          mudou();
          desenhar();
          return;
        }
        delete estado.alocacoes[selecionada];
        estado.alocacoes[selecionada] = { horario: h, origem: "manual" };
        avisar("sucesso", esc(pessoa(selecionada).nome) + " agendada para " + rotuloDoHorario(h) + ".");
        selecionada = null;
        estado.previa = null;
        mudou();
        desenhar();
      } else if (el.hasAttribute("data-liberar")) {
        var pid = el.getAttribute("data-liberar");
        var nome = pessoa(pid).nome;
        delete estado.alocacoes[pid];
        avisar("sucesso", "Horário liberado. " + esc(nome) + " voltou para \"Pessoas sem horário\".");
        estado.previa = null;
        mudou();
        desenhar();
      } else if (el.hasAttribute("data-mover")) {
        selecionada = el.getAttribute("data-mover");
        desenhar();
      } else if (el.hasAttribute("data-cancelar-escolha")) {
        selecionada = null;
        desenhar();
      } else if (el.hasAttribute("data-preencher")) {
        estado.previa = previaDoPreenchimento();
        gravar(estado);
        desenhar();
        document.querySelector("#previa").focus();
      } else if (el.hasAttribute("data-aplicar")) {
        /* A prévia leva a versão da agenda. Se a agenda mudou desde ela, a aplicação recusa, em
           vez de gravar pares calculados sobre um estado que não existe mais (R-10). */
        if (estado.previa.versao !== estado.versao) {
          avisar("aviso", "A agenda mudou desde a prévia. Veja a prévia nova antes de aplicar.");
          estado.previa = previaDoPreenchimento();
          gravar(estado);
          desenhar();
          return;
        }
        var ocupado = mapaDeOcupacao();
        var aplicados = 0;
        estado.previa.pares.forEach(function (par) {
          if (!ocupado[par.horario] && !estado.alocacoes[par.pessoa]) {
            estado.alocacoes[par.pessoa] = { horario: par.horario, origem: "automatica" };
            aplicados++;
          }
        });
        estado.previa = null;
        avisar("sucesso", plural(aplicados, "pessoa recebeu", "pessoas receberam") + " horário. Confira a grade dia a dia; você ainda pode ajustar qualquer uma à mão.");
        mudou();
        desenhar();
      } else if (el.hasAttribute("data-descartar")) {
        estado.previa = null;
        gravar(estado);
        desenhar();
      } else if (el.hasAttribute("data-simular-concorrente")) {
        var ocup = mapaDeOcupacao();
        var livre = horarios(estado.config).filter(function (x) { return !ocup[x.id] && x.data === diaAtual; })[0];
        if (livre) {
          estado.concorrente = livre.id;
          gravar(estado);
          preencher("#mensagem", '<p class="ajuda">Simulação armada: outra sessão vai ocupar ' + rotuloDoHorario(livre.id) + " no instante em que você escolher esse horário.</p>");
        }
      }
    });
    desenhar();
  }

  /* ---------------------------------------------------------------- conferência (R-12 a R-16) */

  function impedimentos() {
    var lista = [];
    var r = resumoDaCapacidade();
    if (r.sem) {
      lista.push({ titulo: plural(r.sem, "pessoa está", "pessoas estão") + " sem horário",
        texto: "Toda pessoa que participa da Etapa precisa de um horário antes da publicação: a ausência tem consequência no Edital. Volte à montagem e agende " + (r.sem === 1 ? "essa pessoa" : "essas pessoas") + ".",
        pessoas: semHorario().map(function (p) { return p.nome + " (" + p.protocolo + ")"; }) });
    }
    var problemas = problemasDaConfiguracao(estado.config);
    if (problemas.length) lista.push({ titulo: "A configuração tem problemas", texto: problemas.join(" ") });
    estado.config.bancas.forEach(function (b) {
      if (!b.acesso.trim()) {
        lista.push({ titulo: b.nome + " sem " + (estado.config.modalidade === "remota" ? "endereço da sala" : "local"),
          texto: "Quem for atendido nessa banca não saberia aonde ir. Informe na configuração." });
      }
    });
    return lista;
  }

  function assinatura() {
    var itens = Object.keys(estado.alocacoes).sort().map(function (pid) { return pid + "=" + estado.alocacoes[pid].horario; });
    var texto = JSON.stringify([estado.config, itens]);
    var h = 0;
    for (var i = 0; i < texto.length; i++) h = (h * 31 + texto.charCodeAt(i)) | 0;
    return (h >>> 0).toString(16);
  }

  function paginaConferir() {
    if (estado.publicada) { window.location.href = "publicada.html"; return; }
    var r = resumoDaCapacidade();
    var imp = impedimentos();
    var dias = estado.config.dias.map(function (d) { return dataPorExtenso(d.data, true); }).join(", ");
    preencher("#fatos", "<div><dt>Etapa</dt><dd>" + esc(C.etapa) + "</dd></div>" +
      "<div><dt>Período no cronograma</dt><dd>" + esc(C.evento.rotulo) + "</dd></div>" +
      "<div><dt>Dias da agenda</dt><dd>" + dias + "</dd></div>" +
      "<div><dt>Atendimento</dt><dd>" + estado.config.duracao + " minutos, com " + estado.config.intervalo + " de intervalo · " +
      plural(estado.config.bancas.length, "banca", "bancas") + " · " + (estado.config.modalidade === "remota" ? "por videoconferência" : "presencial") + "</dd></div>" +
      "<div><dt>Pessoas</dt><dd>" + r.agendadas + " de " + r.total + " com horário · " + r.capacidade + " horários, " + Math.max(0, r.livres) + " ficam livres</dd></div>");
    if (imp.length) {
      preencher("#impedimentos", '<h2 id="impedimentos-titulo">Antes de publicar, resolva</h2>' + imp.map(function (i) {
        return "<div class=\"impedimento\"><h3>" + esc(i.titulo) + "</h3><p>" + esc(i.texto) + "</p>" +
          (i.pessoas ? "<ul>" + i.pessoas.slice(0, 12).map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") +
            (i.pessoas.length > 12 ? "<li>e mais " + (i.pessoas.length - 12) + "</li>" : "") + "</ul>" : "") + "</div>";
      }).join("") + '<p><a class="botao" href="montar.html">Voltar à montagem</a></p>');
    } else {
      document.querySelector("#impedimentos").hidden = true;
    }
    var amostra = publicoPorDia(true);
    preencher("#previa-publica", amostra);
    var primeira = Object.keys(estado.alocacoes)[0];
    preencher("#previa-mensagem", primeira ? textoDaMensagem(primeira, false).replace(/\n/g, "<br>") : "");
    preencher("#assunto", esc(assuntoDaMensagem(false)));
    var botao = document.querySelector("[data-publicar]");
    botao.disabled = imp.length > 0;
    document.querySelector("[name=assinatura]").value = assinatura();
    document.querySelector("#form-publicar").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var autoridade = document.querySelector("[name=autoridade]").value;
      if (!autoridade) {
        preencher("#erro-autoridade", '<p class="erro" role="alert">Escolha a autoridade signatária: o nome e o cargo ficam gravados na publicação.</p>');
        return;
      }
      /* A assinatura da conferência é a que a confirmação confere (R-14): se a agenda mudou noutra
         aba depois desta tela, a publicação recusa, e a conferência é refeita. */
      if (document.querySelector("[name=assinatura]").value !== assinatura()) {
        avisar("aviso", "A agenda mudou desde esta conferência. Confira de novo.");
        window.location.reload();
        return;
      }
      var itens = {};
      Object.keys(estado.alocacoes).forEach(function (pid) { itens[pid] = estado.alocacoes[pid].horario; });
      estado.publicada = { em: "14/11/2026 às 15:42", autoridade: autoridade, numero: 1, itens: itens };
      /* Os avisos saem pelo despacho, depois da publicação, e um por pessoa (R-17). O protótipo
         sorteia um endereço recusado para mostrar a falha sem desfazer o ato (R-18). */
      Object.keys(itens).forEach(function (pid, i) { estado.avisos[pid] = i === 5 ? "falhou" : i === 9 ? "na_fila" : "enviado"; });
      avisar("sucesso", "<strong>Agenda publicada.</strong> A página pública e a área de cada pessoa já mostram o horário. Os avisos por e-mail saem em seguida, um por pessoa.");
      mudou();
      window.location.href = "publicada.html";
    });
  }

  /* ---------------------------------------------------------------- textos que o candidato lê */

  function identificacaoPublica(p) {
    return C.identificacao === "nome" ? esc(p.nome) + ' <span class="inscricao">' + p.protocolo + "</span>" : '<span class="inscricao-so">' + p.protocolo + "</span>";
  }

  function itensVigentes() {
    if (!estado.publicada) {
      var itens = {};
      Object.keys(estado.alocacoes).forEach(function (pid) { itens[pid] = estado.alocacoes[pid].horario; });
      return itens;
    }
    return estado.publicada.itens;
  }

  function remarcacaoDe(pid) {
    for (var i = estado.remarcacoes.length - 1; i >= 0; i--) if (estado.remarcacoes[i].pessoa === pid) return estado.remarcacoes[i];
    return null;
  }

  function publicoPorDia(previa) {
    var itens = itensVigentes();
    var porDia = {};
    Object.keys(itens).forEach(function (pid) {
      var h = horarioPorId(itens[pid]);
      if (!h) return;
      (porDia[h.data] = porDia[h.data] || []).push({ h: h, p: pessoa(pid) });
    });
    var dias = Object.keys(porDia).sort();
    if (!dias.length) return '<p class="vazio">Nenhum horário publicado ainda.</p>';
    return dias.map(function (d, i) {
      var linhas = porDia[d].sort(function (a, b) { return a.h.minuto - b.h.minuto || a.h.ordemBanca - b.h.ordemBanca; });
      if (previa) linhas = linhas.slice(0, 6);
      return '<section class="dia-publico"><h3>' + dataPorExtenso(d) + "</h3><ol class=\"horarios-publicos\">" +
        linhas.map(function (x) {
          var rem = remarcacaoDe(x.p.id);
          return '<li data-protocolo="' + x.p.protocolo + '" data-nome="' + esc(x.p.nome.toLowerCase()) + '"><span class="hora">' + x.h.inicio + "</span>" +
            '<span class="quem">' + identificacaoPublica(x.p) + "</span>" +
            (estado.config.bancas.length > 1 ? '<span class="banca">' + esc(x.h.bancaNome) + "</span>" : "") +
            (rem ? '<span class="remarcado">remarcado em ' + rem.em + "</span>" : "") + "</li>";
        }).join("") + (previa && porDia[d].length > 6 ? '<li class="mais">e mais ' + (porDia[d].length - 6) + " neste dia</li>" : "") +
        "</ol></section>" + (previa && i >= 0 ? "" : "");
    }).slice(0, previa ? 2 : 99).join("");
  }

  function assuntoDaMensagem(remarcacao) {
    return (remarcacao ? "Seu horário mudou: " : "Seu horário: ") + C.etapaCurta + " — " + C.edital;
  }

  function textoDaMensagem(pid, remarcacao) {
    var p = pessoa(pid);
    var itens = itensVigentes();
    var h = horarioPorId(itens[pid]);
    var banca = estado.config.bancas.filter(function (b) { return h && b.id === h.banca; })[0] || estado.config.bancas[0];
    var rem = remarcacao ? remarcacaoDe(pid) : null;
    var linhas = ["Olá, " + p.nome.split(" ")[0] + ".", ""];
    if (rem) linhas.push("A comissão remarcou o seu horário na " + C.etapaCurta + ". O horário anterior (" + rem.deRotulo + ") não vale mais.", "");
    else linhas.push("A comissão publicou a agenda da " + C.etapaCurta + " do " + C.edital + " (" + C.oferta + "). Este é o seu horário:", "");
    linhas.push("Dia: " + (h ? dataPorExtenso(h.data) : "—"));
    linhas.push("Horário: " + (h ? h.inicio + " (duração prevista de " + estado.config.duracao + " minutos)" : "—"));
    if (estado.config.bancas.length > 1) linhas.push("Banca: " + banca.nome);
    linhas.push(estado.config.modalidade === "remota" ? "Sala virtual: " + banca.acesso : "Local: " + banca.acesso);
    linhas.push("", "Orientações: " + estado.config.orientacoes, "",
      "Este e-mail é um aviso. O que vale é a agenda publicada na página da seleção, também na sua área: Minhas inscrições.",
      "Inscrição " + p.protocolo + ".");
    return esc(linhas.join("\n"));
  }

  /* ---------------------------------------------------------------- página: publicada */

  function paginaPublicada() {
    if (!estado.publicada) { window.location.href = "conferir.html"; return; }
    preencher("#mensagem", mensagem());
    var itens = estado.publicada.itens;
    var r = resumoDaCapacidade();
    var contagem = { enviado: 0, na_fila: 0, falhou: 0 };
    Object.keys(estado.avisos).forEach(function (pid) { contagem[estado.avisos[pid]]++; });
    preencher("#estado-publicado", '<p><span class="situacao s-PUBLICADO">Publicada</span> em ' + estado.publicada.em + ", assinada por " + esc(estado.publicada.autoridade) +
      (estado.remarcacoes.length ? " · " + plural(estado.remarcacoes.length, "remarcação", "remarcações") + " depois" : "") + ".</p>" +
      '<ul class="resumo"><li><strong>' + Object.keys(itens).length + "</strong> horários publicados</li>" +
      "<li><strong>" + contagem.enviado + "</strong> avisos enviados</li>" +
      "<li><strong>" + contagem.na_fila + "</strong> na fila</li>" +
      '<li class="' + (contagem.falhou ? "pendente" : "") + '"><strong>' + contagem.falhou + "</strong> não entregues</li></ul>");

    var falhas = Object.keys(estado.avisos).filter(function (pid) { return estado.avisos[pid] === "falhou"; });
    preencher("#falhas", falhas.length
      ? '<div class="aviso"><p><strong>' + plural(falhas.length, "aviso não foi entregue", "avisos não foram entregues") + ".</strong> A agenda continua publicada e vale para " +
        (falhas.length === 1 ? "essa pessoa" : "essas pessoas") + " do mesmo jeito: o e-mail é aviso, e não o ato.</p><ul>" +
        falhas.map(function (pid) {
          return "<li>" + esc(pessoa(pid).nome) + " (" + pessoa(pid).protocolo + ") — o servidor do destinatário recusou o endereço. " +
            '<button type="button" class="acao" data-reenviar="' + pid + '">Reenviar o aviso</button></li>';
        }).join("") + "</ul></div>"
      : "");

    var novas = participantes().filter(function (p) { return !itens[p.id]; });
    preencher("#novas", novas.length
      ? '<section class="consequencias" aria-labelledby="novas-titulo"><h2 id="novas-titulo">Passou a participar depois da publicação (' + novas.length + ")</h2>" +
        "<p>Um recurso deferido trouxe esta pessoa para a Etapa. Ela ainda não tem horário, e a agenda publicada não muda para mais ninguém.</p><ul>" +
        novas.map(function (p) {
          return "<li><strong>" + esc(p.nome) + "</strong> " + p.protocolo + ' <a class="acao" href="remarcar.html?pessoa=' + p.id + '">Agendar esta pessoa</a></li>';
        }).join("") + "</ul></section>"
      : "");

    var linhas = Object.keys(itens).map(function (pid) { return { p: pessoa(pid), h: horarioPorId(itens[pid]) }; })
      .filter(function (x) { return x.h; })
      .sort(function (a, b) { return a.h.data < b.h.data ? -1 : a.h.data > b.h.data ? 1 : a.h.minuto - b.h.minuto || a.h.ordemBanca - b.h.ordemBanca; });
    var rotulos = { enviado: "enviado", na_fila: "na fila", falhou: "não entregue" };
    preencher("#lista-publicada", "<thead><tr><th scope=\"col\">Quando</th><th scope=\"col\">Pessoa</th><th scope=\"col\">Aviso</th><th scope=\"col\"><span class=\"oculto\">Ações</span></th></tr></thead><tbody>" +
      linhas.map(function (x) {
        var rem = remarcacaoDe(x.p.id);
        var av = estado.avisos[x.p.id] || "na_fila";
        return "<tr><td>" + rotuloDoHorario(itens[x.p.id], true) + (rem ? ' <span class="remarcado">remarcado em ' + rem.em + "</span>" : "") + "</td>" +
          "<td>" + esc(x.p.nome) + ' <span class="inscricao">' + x.p.protocolo + "</span></td>" +
          '<td><span class="estado-do-aviso a-' + av + '">' + rotulos[av] + "</span></td>" +
          '<td><a class="acao" href="remarcar.html?pessoa=' + x.p.id + '">Remarcar</a></td></tr>';
      }).join("") + "</tbody>");

    document.addEventListener("click", function (ev) {
      var el = ev.target.closest("button");
      if (!el) return;
      if (el.hasAttribute("data-reenviar")) {
        estado.avisos[el.getAttribute("data-reenviar")] = "na_fila";
        avisar("sucesso", "Reenvio registrado. O aviso volta para a fila, com o mesmo texto; a trilha guarda quem pediu.");
        gravar(estado);
        paginaPublicada();
      } else if (el.hasAttribute("data-simular-recurso")) {
        estado.novoParticipa = true;
        gravar(estado);
        paginaPublicada();
      }
    });
  }

  /* ---------------------------------------------------------------- página: remarcar (R-19 a R-22) */

  function paginaRemarcar() {
    var pid = parametros.get("pessoa");
    var p = pid && pessoa(pid);
    if (!p) { window.location.href = "publicada.html"; return; }
    var atual = estado.publicada ? estado.publicada.itens[pid] : (estado.alocacoes[pid] || {}).horario;
    var inclusao = !atual;
    textos();
    preencher("#titulo-da-remarcacao", inclusao ? "Agendar uma pessoa depois da publicação" : "Remarcar uma pessoa");
    preencher("#quem", "<div><dt>Pessoa</dt><dd>" + esc(p.nome) + " · " + p.protocolo + "</dd></div>" +
      "<div><dt>Horário publicado</dt><dd>" + (atual ? rotuloDoHorario(atual) : "nenhum: passou a participar depois da publicação") + "</dd></div>");
    var ocupado = mapaDeOcupacao();
    var livres = horarios(estado.config).filter(function (h) { return !ocupado[h.id]; });
    var porDia = {};
    livres.forEach(function (h) { (porDia[h.data] = porDia[h.data] || []).push(h); });
    var opcoes = Object.keys(porDia).sort().map(function (d) {
      return '<optgroup label="' + dataPorExtenso(d) + '">' + porDia[d].map(function (h) {
        return '<option value="' + h.id + '">' + dataPorExtenso(h.data, true) + " · " + h.inicio + (estado.config.bancas.length > 1 ? " · " + esc(h.bancaNome) : "") + "</option>";
      }).join("") + "</optgroup>";
    }).join("");
    var select = document.querySelector("[name=novo]");
    select.innerHTML = '<option value="">— escolha um horário livre —</option>' + opcoes;
    if (!livres.length) {
      preencher("#sem-livres", '<p class="aviso">Não há horário livre. Acrescente uma janela, um dia ou uma banca na <a href="configurar.html">configuração</a>: os horários publicados não mudam.</p>');
    }
    preencher("#botao-remarcar", inclusao ? "Agendar e avisar esta pessoa" : "Remarcar e avisar esta pessoa");
    document.querySelector("#form-remarcar").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var novo = select.value;
      var motivo = document.querySelector("[name=motivo]").value.trim();
      var erros = [];
      if (!novo) erros.push("Escolha o novo horário.");
      if (!motivo) erros.push("Escreva o motivo. Ele fica na trilha e não aparece para o candidato.");
      if (erros.length) {
        preencher("#erros", '<div class="erro" role="alert"><ul>' + erros.map(function (e) { return "<li>" + e + "</li>"; }).join("") + "</ul></div>");
        return;
      }
      if (atual) estado.remarcacoes.push({ pessoa: pid, de: atual, deRotulo: rotuloDoHorario(atual), para: novo, motivo: motivo, em: "14/11" });
      else estado.remarcacoes.push({ pessoa: pid, de: null, deRotulo: "", para: novo, motivo: motivo, em: "14/11", inclusao: true });
      estado.alocacoes[pid] = { horario: novo, origem: "manual" };
      if (estado.publicada) estado.publicada.itens[pid] = novo;
      estado.avisos[pid] = "na_fila";
      avisar("sucesso", "<strong>" + esc(p.nome) + (atual ? " foi remarcada" : " foi agendada") + "</strong> para " + rotuloDoHorario(novo) +
        ". Só ela recebe aviso; a página pública mostra o horário novo" + (atual ? ", com a marca \"remarcado em 14/11\"" : "") + ".");
      mudou();
      window.location.href = "publicada.html";
    });
  }

  /* ---------------------------------------------------------------- portal */

  function paginaPublica() {
    if (!estado.publicada) {
      preencher("#agenda-publica", '<p class="vazio">A agenda desta Etapa ainda não foi publicada. Volte ao <a href="/">roteiro</a> e publique-a pela gestão.</p>');
      return;
    }
    preencher("#publicada-em", "Publicada em " + estado.publicada.em + ", assinada por " + esc(estado.publicada.autoridade) +
      (estado.remarcacoes.length ? ". Depois, " + plural(estado.remarcacoes.length, "remarcação individual", "remarcações individuais") + ", marcadas na lista." : "."));
    preencher("#agenda-publica", publicoPorDia(false));
    var busca = document.querySelector("#busca");
    busca.addEventListener("input", function () {
      var termo = busca.value.trim().toLowerCase();
      var achados = 0;
      document.querySelectorAll(".horarios-publicos li[data-protocolo]").forEach(function (li) {
        var casa = !termo || li.getAttribute("data-protocolo").toLowerCase().indexOf(termo) >= 0 ||
          (C.identificacao === "nome" && li.getAttribute("data-nome").indexOf(termo) >= 0);
        li.hidden = !casa;
        if (casa) achados++;
      });
      document.querySelectorAll(".dia-publico").forEach(function (s) {
        s.hidden = !s.querySelector("li[data-protocolo]:not([hidden])");
      });
      preencher("#resultado-da-busca", termo ? plural(achados, "horário encontrado", "horários encontrados") + "." : "");
    });
  }

  function paginaCandidato() {
    var pid = estado.remarcacoes.length ? estado.remarcacoes[estado.remarcacoes.length - 1].pessoa : C.participantes[0].id;
    var p = pessoa(pid);
    preencher("[data-nome-candidato]", esc(p.nome));
    if (!estado.publicada || !estado.publicada.itens[pid]) {
      preencher("#horario-do-candidato", '<p class="situacao futuro">Seu horário ainda não foi publicado.</p><p class="meta">A comissão publica a agenda dentro do período da Etapa no cronograma: ' + esc(C.evento.rotulo) + ". Você recebe um aviso por e-mail quando ela sair.</p>");
      return;
    }
    var h = horarioPorId(estado.publicada.itens[pid]);
    var banca = estado.config.bancas.filter(function (b) { return b.id === h.banca; })[0];
    var rem = remarcacaoDe(pid);
    var remota = estado.config.modalidade === "remota";
    preencher("#horario-do-candidato",
      (rem && !rem.inclusao ? '<p class="aviso remarcacao"><strong>Seu horário mudou em ' + rem.em + ".</strong> O horário anterior, " + esc(rem.deRotulo) + ", não vale mais.</p>" : "") +
      '<p class="quando-grande">' + dataPorExtenso(h.data) + ', às <strong>' + h.inicio + "</strong></p>" +
      '<dl class="campos"><dt>Duração prevista</dt><dd>' + estado.config.duracao + " minutos</dd>" +
      (estado.config.bancas.length > 1 ? "<dt>Banca</dt><dd>" + esc(banca.nome) + "</dd>" : "") +
      "<dt>" + (remota ? "Como participar" : "Local") + "</dt><dd>" + (remota ? "Por videoconferência" : esc(banca.acesso)) + "</dd></dl>" +
      (remota ? '<p><a class="acao-principal" href="#entrar">Entrar na sala virtual</a></p><p class="meta">O endereço da sala é só seu: ele não aparece na página pública. A sala abre poucos minutos antes do horário.</p>' : "") +
      '<h3>Orientações</h3><p>' + esc(estado.config.orientacoes) + "</p>" +
      '<p class="meta">Se você faltar, vale o que o Edital diz sobre a ausência nesta Etapa. Se a conexão falhar, siga o item do Edital sobre falha técnica.</p>');
  }

  function paginaEmail() {
    var pid = estado.remarcacoes.length ? estado.remarcacoes[estado.remarcacoes.length - 1].pessoa : Object.keys(itensVigentes())[0];
    if (!pid) {
      preencher("#corpo", "<p>Monte e publique a agenda para ver o aviso que cada pessoa recebe.</p>");
      return;
    }
    var remarcacao = !!estado.remarcacoes.length && !remarcacaoDe(pid).inclusao;
    preencher("#assunto", esc(assuntoDaMensagem(remarcacao)));
    var p = pessoa(pid);
    var h = horarioPorId(itensVigentes()[pid]);
    var banca = estado.config.bancas.filter(function (b) { return h && b.id === h.banca; })[0] || estado.config.bancas[0];
    var rem = remarcacao ? remarcacaoDe(pid) : null;
    var remota = estado.config.modalidade === "remota";
    preencher("#corpo",
      '<h1 class="titulo">' + (rem ? "Seu horário mudou" : "Seu horário na " + esc(C.etapaCurta)) + "</h1>" +
      '<p class="texto">Olá, ' + esc(p.nome.split(" ")[0]) + ". " + (rem
        ? "A comissão remarcou o seu horário. O anterior, " + esc(rem.deRotulo) + ", não vale mais."
        : "A comissão publicou a agenda da " + esc(C.etapaCurta) + " do " + esc(C.edital) + ". Este é o seu horário:") + "</p>" +
      '<table class="quadro" role="presentation"><tr><td class="destaque-acao">' +
      '<p class="rotulo">Dia e horário</p><p class="valor">' + (h ? dataPorExtenso(h.data) + ", às " + h.inicio : "—") + "</p>" +
      '<p class="rotulo">Duração prevista</p><p class="valor">' + estado.config.duracao + " minutos</p>" +
      (estado.config.bancas.length > 1 ? '<p class="rotulo">Banca</p><p class="valor">' + esc(banca.nome) + "</p>" : "") +
      '<p class="rotulo">' + (remota ? "Sala virtual" : "Local") + '</p><p class="valor endereco">' + esc(banca.acesso) + "</p>" +
      "</td></tr></table>" +
      '<p class="texto"><strong>Orientações.</strong> ' + esc(estado.config.orientacoes) + "</p>" +
      '<p class="botao-linha"><a class="botao" href="candidato.html">Ver na minha área</a></p>' +
      '<p class="nota">Este e-mail é um aviso. O que vale é a agenda publicada na página da seleção. Inscrição ' + p.protocolo + ".</p>");
  }

  /* ---------------------------------------------------------------- roteiro */

  function paginaIndice() {
    document.querySelectorAll("[data-cenario-atual]").forEach(function (el) {
      el.textContent = estado.cenario === "a" ? "A — Entrevista" : "B — Verificação da autodeclaração";
    });
  }

  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-recomecar]");
    if (!el) return;
    estado = novoEstado(estado.cenario);
    gravar(estado);
    window.location.href = "/";
  });

  textos();
  var pagina = document.body.getAttribute("data-pagina");
  ({
    index: paginaIndice, etapa: paginaEtapa, configurar: paginaConfigurar, montar: paginaMontar,
    conferir: paginaConferir, publicada: paginaPublicada, remarcar: paginaRemarcar,
    publica: paginaPublica, candidato: paginaCandidato, email: paginaEmail
  }[pagina] || function () {})();
})();
