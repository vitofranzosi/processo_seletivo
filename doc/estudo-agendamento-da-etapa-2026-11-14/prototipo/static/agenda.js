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

  /* ---------------------------------------------------------------- componentes comuns */

  /* O medidor real da gestão (`telas.css`, `.medidor`), com as larguras de `.largura-N` da
     `minhas-etapas.css`: a CSP não deixa a largura ir em `style=""`. */
  function medidor(feitos, total, rotuloRestante, detalhe, completo) {
    var pct = total ? Math.min(100, Math.round(feitos / total * 100)) : 0;
    return '<div class="medidor' + (completo ? " completo" : "") + '">' +
      '<p class="numeros"><span class="restante">' + rotuloRestante + '</span><span class="taxa">' + pct + "%</span></p>" +
      '<div class="trilha-do-medidor" aria-hidden="true"><div class="feito largura-' + pct + '"></div></div>' +
      (detalhe ? '<p class="detalhe">' + detalhe + "</p>" : "") + "</div>";
  }

  /* O seletor de horário livre: dia, depois os horários livres de cada banca, como opções. Serve
     à alocação à mão e à remarcação — uma interação só, e nunca um botão repetido em cada linha da
     grade (redesign de 14/11). */
  function seletorDeHorario(nome, livres, diaInicial, escolhido) {
    var porDia = {};
    livres.forEach(function (h) { (porDia[h.data] = porDia[h.data] || []).push(h); });
    var dias = Object.keys(porDia).sort();
    if (!dias.length) return '<p class="aviso">Não há horário livre. Acrescente um dia, uma janela ou uma banca na <a href="configurar.html">configuração</a>.</p>';
    var dia = dias.indexOf(diaInicial) >= 0 ? diaInicial : dias[0];
    var abas = '<div class="dias-do-seletor" role="group" aria-label="Dia">' + dias.map(function (d) {
      return '<button type="button" class="dia-do-seletor" data-dia-do-seletor="' + d + '" aria-pressed="' + (d === dia) + '">' +
        dataPorExtenso(d, true) + ' <span class="contagem">' + porDia[d].length + "</span></button>";
    }).join("") + "</div>";
    var bancas = estado.config.bancas;
    var grupos = bancas.map(function (b) {
      var opcoes = porDia[dia].filter(function (h) { return h.banca === b.id; });
      if (!opcoes.length) return "";
      return '<fieldset class="horarios-livres"><legend>' + (bancas.length > 1 ? esc(b.nome) : "Horários livres") + "</legend>" +
        opcoes.map(function (h) {
          return '<label class="opcao-de-horario"><input type="radio" name="' + nome + '" value="' + h.id + '"' +
            (escolhido === h.id ? " checked" : "") + "><span>" + h.inicio + "</span></label>";
        }).join("") + "</fieldset>";
    }).join("");
    return abas + grupos;
  }

  function livresAgora() {
    var ocupado = mapaDeOcupacao();
    return horarios(estado.config).filter(function (h) { return !ocupado[h.id]; });
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
      var lista = horarios(cfg);
      var dias = cfg.dias.map(function (dia, i) {
        var doDia = lista.filter(function (h) { return h.data === dia.data; }).length;
        var janelas = dia.janelas.map(function (j, k) {
          return '<span class="janela"><input type="time" step="300" aria-label="Início da janela ' + (k + 1) + " de " + dataPorExtenso(dia.data, true) +
            '" data-dia="' + i + '" data-janela="' + k + '" data-ponta="0" value="' + j[0] + '"><span aria-hidden="true">–</span>' +
            '<input type="time" step="300" aria-label="Fim da janela ' + (k + 1) + '" data-dia="' + i + '" data-janela="' + k + '" data-ponta="1" value="' + j[1] + '">' +
            (dia.janelas.length > 1 ? '<button type="button" class="remover" data-remover-janela="' + i + ":" + k + '" aria-label="Remover a janela ' + j.join("–") + '">×</button>' : "") + "</span>";
        }).join("");
        return '<li class="linha-de-dia"><span class="rotulo-do-dia">' + dataPorExtenso(dia.data, true) + "</span>" +
          '<span class="janelas-do-dia">' + janelas + '<button type="button" class="acao" data-acrescentar-janela="' + i + '">+ janela</button></span>' +
          '<span class="horarios-do-dia">' + plural(doDia, "horário", "horários") + "</span>" +
          (cfg.dias.length > 1 ? '<button type="button" class="remover" data-remover-dia="' + i + '" aria-label="Remover ' + dataPorExtenso(dia.data) + '">×</button>' : '<span></span>') + "</li>";
      }).join("");
      preencher("#dias", dias);
      var remota = cfg.modalidade === "remota";
      preencher("#cabecalho-bancas", "<span>Nome</span><span>" + (remota ? "Endereço da sala virtual" : "Local") + "</span><span></span>");
      preencher("#bancas", cfg.bancas.map(function (b, i) {
        return '<li class="linha-de-banca"><input aria-label="Nome da banca ' + (i + 1) + '" data-banca="' + i + '" data-campo="nome" value="' + esc(b.nome) + '">' +
          '<input aria-label="' + (remota ? "Endereço da sala" : "Local") + " da banca " + (i + 1) + '" data-banca="' + i + '" data-campo="acesso" value="' + esc(b.acesso) + '" placeholder="' + (remota ? "https://…" : "Sala, prédio") + '">' +
          (cfg.bancas.length > 1 ? '<button type="button" class="remover" data-remover-banca="' + i + '" aria-label="Remover ' + esc(b.nome) + '">×</button>' : "<span></span>") + "</li>";
      }).join(""));
      preencher("#ajuda-acesso-texto", remota
        ? "O endereço da sala vai só para a área de cada pessoa e para o e-mail dela; a página pública mostra só o nome da banca."
        : "O local aparece na área de cada pessoa, no e-mail e na página pública.");
      calcular();
    }

    /* Sugestões que resolvem a falta num clique: o próximo dia dentro do período do cronograma,
       uma banca a mais, ou intervalo nenhum. Cada uma diz quantos horários acrescenta. */
    function sugestoes(falta) {
      var cfg = estado.config, lista = [];
      var porDia = cfg.dias.length ? horarios({ dias: [cfg.dias[cfg.dias.length - 1]], duracao: cfg.duracao, intervalo: cfg.intervalo, bancas: cfg.bancas }).length : 0;
      var ultimo = cfg.dias.length ? cfg.dias[cfg.dias.length - 1].data : null;
      if (ultimo) {
        var q = ultimo.split("-");
        var prox = new Date(Date.UTC(+q[0], +q[1] - 1, +q[2] + 1)).toISOString().slice(0, 10);
        if (prox <= C.evento.fim) lista.push({ acao: "dia", rotulo: "Acrescentar " + dataPorExtenso(prox, true), ganho: porDia });
      }
      var semBanca = horarios(cfg).length / Math.max(1, cfg.bancas.length);
      lista.push({ acao: "banca", rotulo: "Acrescentar uma banca", ganho: semBanca });
      if (cfg.intervalo > 0) {
        var semIntervalo = horarios({ dias: cfg.dias, duracao: cfg.duracao, intervalo: 0, bancas: cfg.bancas }).length - horarios(cfg).length;
        if (semIntervalo > 0) lista.push({ acao: "intervalo", rotulo: "Tirar o intervalo", ganho: semIntervalo });
      }
      return lista.map(function (s) {
        return '<li><button type="button" class="acao sugestao' + (s.ganho >= falta ? " resolve" : "") + '" data-sugestao="' + s.acao + '">' +
          s.rotulo + ' <span class="ganho">+' + s.ganho + "</span></button></li>";
      }).join("");
    }

    function calcular() {
      var cfg = estado.config;
      var problemas = problemasDaConfiguracao(cfg);
      var lista = horarios(cfg);
      var r = resumoDaCapacidade();
      var html = "";
      if (problemas.length) {
        html += '<div class="veredito invalido" role="alert"><p class="titulo-do-veredito">Corrija para continuar</p><ul>' +
          problemas.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul></div>";
      } else if (r.falta) {
        html += '<div class="veredito falta"><p class="titulo-do-veredito">Faltam ' + plural(r.falta, "horário", "horários") + "</p>" +
          "<p>" + r.total + " pessoas participam, e a agenda tem " + r.capacidade + " horários.</p>" +
          '<p class="resolver">Resolva com um clique:</p><ul class="sugestoes">' + sugestoes(r.falta) + "</ul></div>";
      } else {
        html += '<div class="veredito cabe"><p class="titulo-do-veredito">Cabem todas as ' + r.total + " pessoas</p>" +
          "<p>Sobram " + plural(r.capacidade - r.total, "horário", "horários") + " para remarcações e inclusões.</p></div>";
      }
      html += medidor(Math.min(lista.length, r.total), r.total, "<strong>" + lista.length + "</strong> horários para " + r.total + " pessoas", null, !r.falta && !problemas.length);
      var porBanca = cfg.bancas.length ? lista.length / cfg.bancas.length : 0;
      html += '<p class="conta-da-capacidade">' + porBanca + " por banca × " + plural(cfg.bancas.length, "banca", "bancas") +
        " · um atendimento a cada " + (cfg.duracao + cfg.intervalo) + " min</p>";
      sobras(cfg).forEach(function (s) { html += '<p class="ajuda">' + esc(s) + "</p>"; });
      preencher("#calculo", html);
      form.querySelector("[data-salvar]").disabled = problemas.length > 0;
    }

    form.addEventListener("input", function (ev) {
      var el = ev.target, cfg = estado.config;
      if (el.name === "duracao") cfg.duracao = parseInt(el.value, 10) || 0;
      else if (el.name === "intervalo") cfg.intervalo = el.value === "" ? 0 : parseInt(el.value, 10);
      else if (el.name === "orientacoes") cfg.orientacoes = el.value;
      else if (el.name === "modalidade") return;
      else if (el.hasAttribute("data-janela")) cfg.dias[+el.dataset.dia].janelas[+el.dataset.janela][+el.dataset.ponta] = el.value;
      else if (el.hasAttribute("data-banca")) cfg.bancas[+el.dataset.banca][el.dataset.campo] = el.value;
      gravar(estado);
      calcular();
    });
    form.addEventListener("change", function (ev) {
      if (ev.target.name === "modalidade") { estado.config.modalidade = ev.target.value; gravar(estado); desenhar(); }
      else if (ev.target.hasAttribute("data-janela")) desenhar();
    });
    form.addEventListener("click", function (ev) {
      var el = ev.target.closest("button");
      if (!el) return;
      var cfg = estado.config, d;
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
      } else if (el.hasAttribute("data-acrescentar-dia") || el.dataset.sugestao === "dia") {
        var ultimaData = cfg.dias.length ? cfg.dias[cfg.dias.length - 1].data : null;
        var iso = C.evento.inicio;
        if (ultimaData) {
          var q = ultimaData.split("-");
          iso = new Date(Date.UTC(+q[0], +q[1] - 1, +q[2] + 1)).toISOString().slice(0, 10);
        }
        var modelo = cfg.dias.length ? cfg.dias[cfg.dias.length - 1].janelas : [["08:00", "12:00"]];
        cfg.dias.push({ data: iso, janelas: JSON.parse(JSON.stringify(modelo)) });
      } else if (el.hasAttribute("data-acrescentar-banca") || el.dataset.sugestao === "banca") {
        cfg.bancas.push({ id: "b" + Date.now(), nome: "Banca " + (cfg.bancas.length + 1), acesso: "" });
      } else if (el.dataset.sugestao === "intervalo") {
        cfg.intervalo = 0;
      } else if (el.hasAttribute("data-remover-banca")) {
        cfg.bancas.splice(+el.dataset.removerBanca, 1);
      } else return;
      gravar(estado);
      desenhar();
    });
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (problemasDaConfiguracao(estado.config).length) return;
      /* Mudar a configuração não move ninguém em silêncio (R-07). */
      var existentes = {};
      horarios(estado.config).forEach(function (h) { existentes[h.id] = true; });
      var devolvidas = [];
      Object.keys(estado.alocacoes).forEach(function (pid) {
        if (!existentes[estado.alocacoes[pid].horario]) { devolvidas.push(pessoa(pid).nome); delete estado.alocacoes[pid]; }
      });
      estado.configurada = true;
      if (devolvidas.length) {
        avisar("aviso", "<strong>Configuração salva, e " + plural(devolvidas.length, "pessoa voltou", "pessoas voltaram") +
          " para \"sem horário\"</strong>, porque o horário delas deixou de existir: " + esc(devolvidas.join(", ")) + ".");
      } else {
        avisar("sucesso", "Configuração salva. A agenda continua em rascunho: nada é público até você conferir e publicar.");
      }
      mudou();
      window.location.href = "montar.html";
    });
    if (estado.publicada) {
      preencher("#trava-publicada", '<p class="imutavel">A agenda já foi publicada. Você pode acrescentar dias, janelas ou bancas para abrir horários novos; um horário publicado só muda pela remarcação da pessoa.</p>');
    }
    desenhar();
  }

  /* ---------------------------------------------------------------- página: montar (workspace) */

  /* O painel à direita é onde se age; a grade é o que se vê (redesign de 14/11). O painel tem
     quatro estados: a lista de quem está sem horário; uma pessoa escolhida; um horário livre
     escolhido; e a prévia do preenchimento. Nenhum botão se repete pelas linhas da grade. */
  var contexto = { tipo: "lista" };

  function paginaMontar() {
    var diaAtual = parametros.get("dia");
    if (!estado.configurada) { window.location.href = "etapa.html"; return; }
    var busca = "";

    function desenharResumo() {
      var r = resumoDaCapacidade();
      var completo = !r.sem && r.total > 0;
      var html = '<div class="progresso-da-agenda">' +
        medidor(r.agendadas, r.total, "<strong>" + r.agendadas + "</strong> de " + r.total + " com horário",
          null, completo) +
        '<p class="fatos-da-agenda"><span>' + r.capacidade + " horários</span><span>" +
        (r.falta ? '<strong class="falta">faltam ' + r.falta + "</strong>" : "sobram " + Math.max(0, r.capacidade - r.total)) + "</span>" +
        (r.sem ? '<span><a href="#painel" data-ver-sem-horario>' + plural(r.sem, "pessoa sem horário", "pessoas sem horário") + "</a></span>" : "") +
        "</p></div>";
      if (r.falta) html += '<p class="aviso"><strong>Faltam ' + plural(r.falta, "horário", "horários") + ".</strong> Acrescente um dia, uma janela ou uma banca. <a href=\"configurar.html\">Ajustar a configuração</a></p>";
      preencher("#resumo", html);
      var preencherBotao = document.querySelector("[data-preencher]");
      preencherBotao.hidden = !!estado.publicada || !r.sem;
      preencherBotao.disabled = !r.sem || !r.livres;
      preencherBotao.className = r.sem && r.livres ? "botao" : "botao secundario";
      var conferir = document.querySelector("[data-ir-conferir]");
      conferir.className = r.sem && r.livres && !estado.publicada ? "botao secundario" : "botao";
      conferir.textContent = estado.publicada ? "Ver a agenda publicada" : "Conferir e publicar";
      conferir.setAttribute("href", estado.publicada ? "publicada.html" : "conferir.html");
      preencher("#estado-da-agenda", estado.publicada ? '<span class="situacao s-PUBLICADO">Publicada</span>' : '<span class="situacao s-EM_ELABORACAO">Rascunho</span>');
    }

    function desenharGrade() {
      var lista = horarios(estado.config);
      var ocupado = mapaDeOcupacao();
      var dias = estado.config.dias.map(function (d) { return d.data; });
      if (!diaAtual || dias.indexOf(diaAtual) < 0) diaAtual = dias[0];
      preencher("#dias-da-agenda", dias.map(function (d) {
        var doDia = lista.filter(function (h) { return h.data === d; });
        var ocup = doDia.filter(function (h) { return ocupado[h.id]; }).length;
        return '<li><a href="?dia=' + d + '"' + (d === diaAtual ? ' aria-current="page"' : "") + ">" +
          dataPorExtenso(d, true) + ' <span class="contagem">' + ocup + "/" + doDia.length + "</span></a></li>";
      }).join(""));
      var bancas = estado.config.bancas;
      var doDia = lista.filter(function (h) { return h.data === diaAtual; });
      var porInicio = {}, ordem = [];
      doDia.forEach(function (h) {
        if (!porInicio[h.inicio]) { porInicio[h.inicio] = {}; ordem.push(h.inicio); }
        porInicio[h.inicio][h.banca] = h;
      });
      var escolhido = contexto.tipo === "horario" ? contexto.horario : contexto.tipo === "pessoa" && estado.alocacoes[contexto.pessoa] ? estado.alocacoes[contexto.pessoa].horario : null;
      var cab = '<tr><th scope="col" class="coluna-hora">Horário</th>' + bancas.map(function (b) { return '<th scope="col">' + esc(b.nome) + "</th>"; }).join("") + "</tr>";
      var corpo = ordem.map(function (ini) {
        var linha = '<tr><th scope="row" class="coluna-hora">' + ini + "</th>";
        bancas.forEach(function (b) {
          var h = porInicio[ini][b.id];
          var pid = ocupado[h.id];
          var marcado = escolhido === h.id ? " escolhido" : "";
          var naBanca = bancas.length > 1 ? '<span class="banca-no-estreito">' + esc(b.nome) + " · </span>" : "";
          if (pid) {
            var p = pessoa(pid);
            linha += '<td><button type="button" class="vaga ocupada' + marcado + '" data-abrir-pessoa="' + pid + '" aria-label="' + ini + ", " + esc(b.nome) + ": " + esc(p.nome) + '">' +
              naBanca + '<span class="quem">' + esc(p.nome) + '</span><span class="inscricao">' + p.protocolo + "</span>" +
              (estado.alocacoes[pid].origem === "manual" ? '<span class="origem" title="escolhida à mão">à mão</span>' : "") + "</button></td>";
          } else {
            linha += '<td><button type="button" class="vaga livre' + marcado + '" data-abrir-horario="' + h.id + '" aria-label="' + ini + ", " + esc(b.nome) + ': livre">' +
              naBanca + '<span class="livre-rotulo">Livre</span></button></td>';
          }
        });
        return linha + "</tr>";
      }).join("");
      preencher("#grade", '<caption class="oculto">' + dataPorExtenso(diaAtual) + "</caption><thead>" + cab + "</thead><tbody>" + corpo + "</tbody>");
    }

    function listaDeSemHorario(nomeDoCampo) {
      var sem = ordemDoPreenchimento(semHorario()).filter(function (p) {
        return !busca || p.nome.toLowerCase().indexOf(busca) >= 0 || p.protocolo.toLowerCase().indexOf(busca) >= 0;
      });
      if (!sem.length) return '<p class="nenhuma">' + (busca ? "Ninguém sem horário com esse nome ou protocolo." : "") + "</p>";
      return '<ul class="pessoas-do-painel">' + sem.map(function (p) {
        return nomeDoCampo
          ? '<li><label><input type="radio" name="' + nomeDoCampo + '" value="' + p.id + '"><span class="quem">' + esc(p.nome) + '</span><span class="inscricao">' + p.protocolo + "</span></label></li>"
          : '<li><button type="button" class="pessoa-do-painel" data-abrir-pessoa="' + p.id + '"><span class="quem">' + esc(p.nome) + '</span><span class="inscricao">' + p.protocolo + "</span></button></li>";
      }).join("") + "</ul>";
    }

    function campoDeBusca() {
      return '<p class="busca-do-painel"><label class="oculto" for="busca-no-painel">Procurar por nome ou protocolo</label>' +
        '<input type="search" id="busca-no-painel" placeholder="Procurar por nome ou protocolo" value="' + esc(busca) + '" autocomplete="off"></p>';
    }

    function desenharPainel() {
      var html;
      var r = resumoDaCapacidade();
      if (contexto.tipo === "previa") {
        html = painelDaPrevia();
      } else if (contexto.tipo === "pessoa") {
        var p = pessoa(contexto.pessoa);
        var atual = estado.alocacoes[p.id] && estado.alocacoes[p.id].horario;
        var publicadoAqui = estado.publicada && estado.publicada.itens[p.id];
        html = '<header class="cabecalho-do-painel"><button type="button" class="voltar" data-voltar aria-label="Voltar à lista">←</button><div>' +
          '<h2 id="painel-titulo">' + esc(p.nome) + '</h2><p class="inscricao">' + p.protocolo + "</p></div></header>";
        if (publicadoAqui) {
          html += '<p class="horario-atual">' + rotuloDoHorario(atual) + '</p><p class="ajuda">A agenda já foi publicada: mudar o horário é uma remarcação, com motivo, e só esta pessoa é avisada.</p>' +
            '<p class="acoes-do-painel"><a class="botao" href="remarcar.html?pessoa=' + p.id + '">Remarcar</a></p>';
        } else {
          html += (atual ? '<p class="horario-atual">Agora: ' + rotuloDoHorario(atual) + "</p>" : '<p class="sem-horario-ainda">Sem horário</p>') +
            '<form class="alocacao" data-form-pessoa><h3>' + (atual ? "Mudar para" : "Escolha um horário livre") + "</h3>" +
            seletorDeHorario("horario-escolhido", livresAgora(), contexto.dia || diaAtual, contexto.escolhido) +
            '<p class="acoes-do-painel"><button type="submit" class="botao">' + (atual ? "Mudar de horário" : "Agendar") + "</button>" +
            (atual ? ' <button type="button" class="acao perigoso" data-liberar="' + p.id + '">Liberar o horário</button>' : "") + "</p></form>";
        }
      } else if (contexto.tipo === "horario") {
        var h = horarioPorId(contexto.horario);
        html = '<header class="cabecalho-do-painel"><button type="button" class="voltar" data-voltar aria-label="Voltar à lista">←</button><div>' +
          '<h2 id="painel-titulo">' + h.inicio + " · " + dataPorExtenso(h.data, true) + '</h2><p class="inscricao">' + esc(h.bancaNome) + " · livre, até " + h.fim + "</p></div></header>";
        html += semHorario().length
          ? '<form class="alocacao" data-form-horario><h3>Quem vai para este horário?</h3>' + campoDeBusca() +
            '<div class="lista-com-rolagem">' + listaDeSemHorario("pessoa-escolhida") + "</div>" +
            '<p class="acoes-do-painel"><button type="submit" class="botao">Agendar aqui</button></p></form>'
          : '<p class="ajuda">Todas as pessoas já têm horário. Para mudar alguém para cá, escolha a pessoa na grade.</p>';
      } else {
        var sem = semHorario();
        html = '<header class="cabecalho-do-painel"><div><h2 id="painel-titulo">Sem horário <span class="contagem">' + sem.length + "</span></h2></div></header>";
        if (!participantes().length) html += '<p class="vazio">Ninguém participa desta Etapa ainda. A lista sai do resultado da ' + esc(C.anterior) + ".</p>";
        else if (!sem.length) html += '<div class="veredito cabe"><p class="titulo-do-veredito">Todas as ' + participantes().length + " pessoas têm horário</p><p>" + (estado.publicada ? "Clique numa pessoa na grade para remarcá-la." : "O próximo passo é conferir e publicar, no alto da página.") + "</p></div>";
        else html += '<p class="ajuda">Escolha uma pessoa para ver os horários livres, ou clique num horário livre da grade.</p>' + campoDeBusca() +
          '<div class="lista-com-rolagem">' + listaDeSemHorario(null) + "</div>";
      }
      preencher("#painel", html);
    }

    /* A prévia responde primeiro "posso aplicar?": quantos, onde, o que sobra e o que falta; a
       relação nominal fica recolhida (redesign de 14/11). */
    function painelDaPrevia() {
      var p = estado.previa;
      var porDiaBanca = {}, dias = [];
      p.pares.forEach(function (par) {
        var h = horarioPorId(par.horario);
        if (!porDiaBanca[h.data]) { porDiaBanca[h.data] = {}; dias.push(h.data); }
        porDiaBanca[h.data][h.banca] = (porDiaBanca[h.data][h.banca] || 0) + 1;
      });
      var bancas = estado.config.bancas;
      var tabela = '<table class="tabela distribuicao-da-previa"><thead><tr><th scope="col">Dia</th>' +
        bancas.map(function (b) { return '<th scope="col" class="numero">' + esc(b.nome) + "</th>"; }).join("") + "</tr></thead><tbody>" +
        dias.map(function (d) {
          return '<tr><th scope="row">' + dataPorExtenso(d, true) + "</th>" + bancas.map(function (b) {
            return '<td class="numero">' + (porDiaBanca[d][b.id] || 0) + "</td>";
          }).join("") + "</tr>";
        }).join("") + "</tbody></table>";
      var livres = livresAgora().length - p.pares.length;
      var html = '<header class="cabecalho-do-painel"><div><h2 id="painel-titulo">Preencher automaticamente</h2><p class="inscricao">Prévia: nada foi gravado</p></div></header>' +
        '<div class="veredito ' + (p.restam ? "falta" : "cabe") + '"><p class="titulo-do-veredito">' + plural(p.pares.length, "pessoa recebe", "pessoas recebem") + " horário</p>" +
        (p.restam ? "<p>" + plural(p.restam, "pessoa continua", "pessoas continuam") + " sem horário: faltam horários livres. <a href=\"configurar.html\">Ajustar a configuração</a></p>"
          : "<p>Ninguém fica sem horário. Quem já tinha horário não muda.</p>") + "</div>" +
        tabela +
        '<p class="ajuda">Ficam livres ' + plural(Math.max(0, livres), "horário", "horários") + ". Ordem: pessoas por nome (protocolo no empate), horários do mais cedo ao mais tarde" +
        (bancas.length > 1 ? ", bancas lado a lado" : "") + ".</p>" +
        '<details class="relacao-nominal"><summary>Ver quem vai para cada horário (' + p.pares.length + ")</summary><ol>" +
        p.pares.map(function (par) { return "<li><span>" + rotuloDoHorario(par.horario, true) + "</span> " + esc(pessoa(par.pessoa).nome) + "</li>"; }).join("") +
        "</ol></details>" +
        '<p class="acoes-do-painel"><button type="button" class="botao" data-aplicar>Aplicar</button> <button type="button" class="acao" data-descartar>Cancelar</button></p>';
      return html;
    }

    function desenhar() {
      preencher("#mensagem", mensagem());
      desenharResumo();
      desenharGrade();
      desenharPainel();
    }

    function focarPainel() {
      var painel = document.querySelector("#painel");
      if (window.matchMedia("(max-width: 64rem)").matches) painel.scrollIntoView({ block: "start" });
      var alvo = painel.querySelector("h2");
      if (alvo) { alvo.setAttribute("tabindex", "-1"); alvo.focus({ preventScroll: true }); }
    }

    function ocupar(pid, h) {
      /* Dois operadores no mesmo horário (R-11): quem chega depois é recusado pela unicidade. */
      if (estado.concorrente === h) {
        var outra = semHorario().filter(function (x) { return x.id !== pid; }).pop();
        if (outra) estado.alocacoes[outra.id] = { horario: h, origem: "manual" };
        estado.concorrente = null;
        avisar("erro", "<strong>Esse horário acabou de ser ocupado</strong> por outra pessoa da comissão, noutra sessão. A grade foi atualizada; escolha outro.");
        mudou();
        desenhar();
        return false;
      }
      var tinha = estado.alocacoes[pid];
      estado.alocacoes[pid] = { horario: h, origem: "manual" };
      avisar("sucesso", (tinha ? "Horário trocado: " : "Agendamento feito: ") + esc(pessoa(pid).nome) + ", " + rotuloDoHorario(h) + ".");
      estado.previa = null;
      mudou();
      return true;
    }

    document.addEventListener("input", function (ev) {
      if (ev.target.id === "busca-no-painel") {
        busca = ev.target.value.trim().toLowerCase();
        var alvo = document.querySelector(".lista-com-rolagem");
        if (alvo) alvo.innerHTML = listaDeSemHorario(contexto.tipo === "horario" ? "pessoa-escolhida" : null);
      }
    });

    document.addEventListener("change", function (ev) {
      if (ev.target.name === "horario-escolhido") { contexto.escolhido = ev.target.value; desenharGrade(); }
    });

    document.addEventListener("submit", function (ev) {
      var form = ev.target;
      if (form.hasAttribute("data-form-pessoa")) {
        ev.preventDefault();
        var h = form.querySelector("[name=horario-escolhido]:checked");
        if (!h) { avisar("aviso", "Escolha um horário livre antes de agendar."); desenhar(); return; }
        if (ocupar(contexto.pessoa, h.value)) { contexto = { tipo: "lista" }; desenhar(); }
      } else if (form.hasAttribute("data-form-horario")) {
        ev.preventDefault();
        var p = form.querySelector("[name=pessoa-escolhida]:checked");
        if (!p) { avisar("aviso", "Escolha quem vai para este horário."); desenhar(); return; }
        if (ocupar(p.value, contexto.horario)) { contexto = { tipo: "lista" }; desenhar(); }
      }
    });

    document.addEventListener("click", function (ev) {
      var el = ev.target.closest("button, a[data-ver-sem-horario]");
      if (!el) return;
      if (el.hasAttribute("data-abrir-pessoa")) {
        contexto = { tipo: "pessoa", pessoa: el.getAttribute("data-abrir-pessoa"), dia: diaAtual };
        desenhar(); focarPainel();
      } else if (el.hasAttribute("data-abrir-horario")) {
        contexto = { tipo: "horario", horario: el.getAttribute("data-abrir-horario") };
        desenhar(); focarPainel();
      } else if (el.hasAttribute("data-dia-do-seletor")) {
        contexto.dia = el.getAttribute("data-dia-do-seletor");
        contexto.escolhido = null;
        desenharPainel();
      } else if (el.hasAttribute("data-voltar") || el.hasAttribute("data-ver-sem-horario")) {
        if (el.tagName === "A") ev.preventDefault();
        contexto = { tipo: "lista" };
        desenhar(); focarPainel();
      } else if (el.hasAttribute("data-liberar")) {
        var pid = el.getAttribute("data-liberar");
        delete estado.alocacoes[pid];
        avisar("sucesso", "Horário liberado. " + esc(pessoa(pid).nome) + " voltou para \"Sem horário\".");
        estado.previa = null;
        contexto = { tipo: "lista" };
        mudou(); desenhar();
      } else if (el.hasAttribute("data-preencher") || el.hasAttribute("data-preencher-painel")) {
        estado.previa = previaDoPreenchimento();
        gravar(estado);
        contexto = { tipo: "previa" };
        desenhar(); focarPainel();
      } else if (el.hasAttribute("data-aplicar")) {
        /* A prévia leva a versão da agenda (R-10). */
        if (estado.previa.versao !== estado.versao) {
          avisar("aviso", "A agenda mudou desde a prévia. Veja a prévia nova antes de aplicar.");
          estado.previa = previaDoPreenchimento();
          gravar(estado);
          desenhar();
          return;
        }
        var ocupado = mapaDeOcupacao(), aplicados = 0;
        estado.previa.pares.forEach(function (par) {
          if (!ocupado[par.horario] && !estado.alocacoes[par.pessoa]) {
            estado.alocacoes[par.pessoa] = { horario: par.horario, origem: "automatica" };
            aplicados++;
          }
        });
        estado.previa = null;
        contexto = { tipo: "lista" };
        avisar("sucesso", plural(aplicados, "pessoa recebeu", "pessoas receberam") + " horário. Ajuste qualquer uma clicando nela na grade.");
        mudou(); desenhar();
        window.scrollTo({ top: 0 });
      } else if (el.hasAttribute("data-descartar")) {
        estado.previa = null;
        contexto = { tipo: "lista" };
        gravar(estado); desenhar();
      } else if (el.hasAttribute("data-simular-concorrente")) {
        var livre = livresAgora().filter(function (x) { return x.data === diaAtual; })[0];
        if (livre) {
          estado.concorrente = livre.id;
          gravar(estado);
          preencher("#mensagem", '<p class="ajuda">Simulação armada: outra sessão vai ocupar ' + rotuloDoHorario(livre.id) + " no instante em que você o escolher.</p>");
        }
      }
    });
    if (estado.previa) contexto = { tipo: "previa" };
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
    var semH = semHorario().length, semSala = estado.config.bancas.filter(function (b) { return !b.acesso.trim(); }).length;
    var itens = [
      { ok: !semH, texto: r.agendadas + " de " + r.total + " pessoas com horário" },
      { ok: !problemasDaConfiguracao(estado.config).length, texto: "Dias dentro do período do cronograma" },
      { ok: !semSala, texto: estado.config.modalidade === "remota" ? "Toda banca com endereço de sala" : "Toda banca com local" },
      { ok: null, texto: "Autoridade signatária, escolhida no fim da página" }
    ];
    preencher("#prontidao", '<ul class="lista-de-prontidao">' + itens.map(function (i) {
      return '<li class="' + (i.ok === true ? "pronto" : i.ok === false ? "pendente" : "a-fazer") + '"><span class="marca-de-prontidao" aria-hidden="true">' +
        (i.ok === true ? "✓" : i.ok === false ? "!" : "·") + '</span><span class="oculto">' + (i.ok === true ? "Pronto: " : i.ok === false ? "Pendente: " : "A fazer: ") + "</span>" + i.texto + "</li>";
    }).join("") + "</ul>");
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
    var total = Object.keys(itens).length;
    preencher("#estado-publicado", '<p class="sub"><span class="situacao s-PUBLICADO">Publicada</span> em ' + estado.publicada.em + ", assinada por " + esc(estado.publicada.autoridade) +
      (estado.remarcacoes.length ? " · " + plural(estado.remarcacoes.length, "mudança individual", "mudanças individuais") + " depois" : "") + ".</p>" +
      '<div class="progresso-da-agenda">' + medidor(contagem.enviado, total, "<strong>" + contagem.enviado + "</strong> de " + total + " avisos enviados", null, contagem.enviado === total) +
      '<p class="fatos-da-agenda"><span>' + plural(total, "horário publicado", "horários publicados") + "</span>" +
      (contagem.na_fila ? "<span>" + contagem.na_fila + " na fila</span>" : "") +
      (contagem.falhou ? '<span><strong class="falta">' + plural(contagem.falhou, "não entregue", "não entregues") + "</strong></span>" : "") + "</p></div>");
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
    var dia = atual ? horarioPorId(atual).data : null, escolhido = null;
    textos();
    preencher("#titulo-da-remarcacao", inclusao ? "Agendar " + esc(p.nome.split(" ")[0]) : "Remarcar " + esc(p.nome.split(" ")[0]));
    preencher("#quem", '<p class="quem-grande">' + esc(p.nome) + ' <span class="inscricao">' + p.protocolo + "</span></p>" +
      '<p class="horario-atual">' + (atual ? "Horário publicado: <strong>" + rotuloDoHorario(atual) + "</strong>" : "Sem horário: passou a participar depois da publicação") + "</p>");

    function desenharSeletor() {
      preencher("#seletor", seletorDeHorario("novo", livresAgora(), dia, escolhido));
      var resumo = escolhido
        ? (atual ? "<span class=\"de\">" + rotuloDoHorario(atual, true) + "</span> → " : "") + "<strong>" + rotuloDoHorario(escolhido) + "</strong>"
        : "Escolha um horário livre.";
      preencher("#resumo-da-troca", resumo);
    }

    document.addEventListener("click", function (ev) {
      var el = ev.target.closest("[data-dia-do-seletor]");
      if (!el) return;
      dia = el.getAttribute("data-dia-do-seletor");
      escolhido = null;
      desenharSeletor();
    });
    document.addEventListener("change", function (ev) {
      if (ev.target.name === "novo") { escolhido = ev.target.value; desenharSeletor(); }
    });
    preencher("#botao-remarcar", inclusao ? "Agendar e avisar esta pessoa" : "Remarcar e avisar esta pessoa");
    document.querySelector("#form-remarcar").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var motivo = document.querySelector("[name=motivo]").value.trim();
      var erros = [];
      if (!escolhido) erros.push("Escolha o novo horário.");
      if (!motivo) erros.push("Escreva o motivo. Ele fica na trilha e não aparece para o candidato.");
      if (erros.length) {
        preencher("#erros", '<div class="erro" role="alert"><ul>' + erros.map(function (e) { return "<li>" + e + "</li>"; }).join("") + "</ul></div>");
        return;
      }
      if (atual) estado.remarcacoes.push({ pessoa: pid, de: atual, deRotulo: rotuloDoHorario(atual), para: escolhido, motivo: motivo, em: "14/11" });
      else estado.remarcacoes.push({ pessoa: pid, de: null, deRotulo: "", para: escolhido, motivo: motivo, em: "14/11", inclusao: true });
      estado.alocacoes[pid] = { horario: escolhido, origem: "manual" };
      if (estado.publicada) estado.publicada.itens[pid] = escolhido;
      estado.avisos[pid] = "na_fila";
      avisar("sucesso", "<strong>" + (atual ? "Remarcação feita" : "Agendamento feito") + ":</strong> " + esc(p.nome) + ", " + rotuloDoHorario(escolhido) +
        ". Só essa pessoa recebe aviso; a página pública mostra o horário novo" + (atual ? ", com a marca \"remarcado em 14/11\"" : "") + ".");
      mudou();
      window.location.href = "publicada.html";
    });
    desenharSeletor();
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
