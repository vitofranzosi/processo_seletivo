/*
 * Protótipo de estudo — NÃO executa as regras do GPS.
 *
 * Este arquivo reproduz, de forma simplificada e para demonstração, regras que no produto moram no
 * servidor. Cada regra cita a fonte real. Num produto, nada disto seria reescrito em JavaScript: a
 * interface pediria ao servidor a projeção (o parser da prévia já lê o formulário não salvo) e as
 * frases viriam de `publicacoes/infrastructure/pdf.py`, as mesmas do documento publicado.
 */
(function () {
  "use strict";

  const G = (window.GPS2 = window.GPS2 || {});

  // ---------------------------------------------------------------- cenário base (sintético)

  function etapa(id, nome, forma, extra) {
    return Object.assign(
      { id, nome, forma, minima: null, maxima: 10, eliminatoria: false, peso: null,
        favoravel: "Deferido", desfavoravel: "Indeferido", classificatoriaManual: true },
      extra || {}
    );
  }

  function corte(extra) {
    return Object.assign(
      { tipo: null, alvo: null, suplentes: 0, empate: null, destino: null, continuacao: null },
      extra || {}
    );
  }

  function marco(id, codigo, nome, entradas, extra) {
    return Object.assign(
      { id, codigo, nome, entradas, divide: true, corte: corte(), criterios: [] },
      extra || {}
    );
  }

  G.base = function () {
    return {
      etapas: [
        etapa("obj", "Prova objetiva", "nota", { minima: 6, eliminatoria: true, peso: 2 }),
        etapa("tit", "Análise de títulos", "nota", { peso: 1 }),
        etapa("doc", "Análise documental", "decisao", { eliminatoria: true, classificatoriaManual: false }),
        etapa("did", "Prova didática", "nota", { minima: 6, eliminatoria: true, peso: 3 }),
        etapa("ent", "Entrevista", "nota", { peso: 1 }),
        etapa("apt", "Exame de aptidão", "decisao", { eliminatoria: true, favoravel: "Apto",
          desfavoravel: "Inapto", classificatoriaManual: false }),
      ],
      perfis: [
        {
          id: "docinfo", codigo: "DOC-INFO", nome: "Professor Substituto de Informática", vagas: 2,
          fatos: [{ id: "nasc", codigo: "NASC", rotulo: "Data de nascimento", tipo: "data" }],
          marcos: [
            marco("pre", "PRE", "Seleção para análise de títulos", ["obj"], {
              corte: corte({ tipo: "fixo", alvo: 12, empate: "todos", destino: "tit", continuacao: "nao" }),
            }),
            marco("postit", "POS-TIT", "Seleção para análise documental", ["obj", "tit"], {
              corte: corte({ tipo: "fixo", alvo: 6, suplentes: 2, empate: "todos", destino: "doc", continuacao: "nao" }),
            }),
            marco("final", "FINAL", "Classificação final", ["obj", "tit", "did", "ent"], {
              corte: corte({ tipo: "quadro", empate: "todos", destino: "nenhuma", continuacao: "sim" }),
              criterios: [
                { tipo: "pontuacao", alvo: "did", ausente: "ultimo" },
                { tipo: "menor_fato", alvo: "nasc", ausente: "ultimo" },
              ],
            }),
          ],
        },
        {
          id: "docmat", codigo: "DOC-MAT", nome: "Professor Substituto de Matemática", vagas: 1,
          fatos: [],
          marcos: [
            marco("matpre", "PRE", "Seleção para análise de títulos", ["obj"], {
              corte: corte({ tipo: "fixo", alvo: 8, empate: "todos", destino: "tit", continuacao: "nao" }),
            }),
            marco("matfinal", "FINAL", "Classificação final", ["obj", "tit", "did"], {
              corte: corte({ tipo: "quadro", empate: "todos", destino: "nenhuma", continuacao: "sim" }),
              criterios: [{ tipo: "pontuacao", alvo: "did", ausente: "ultimo" }],
            }),
          ],
        },
        {
          id: "teclab", codigo: "TEC-LAB", nome: "Técnico de Laboratório de Informática", vagas: 1,
          fatos: [],
          marcos: [
            marco("tecfinal", "FINAL", "Classificação final", ["obj", "tit"], {
              divide: false,
              corte: corte({ tipo: "quadro", empate: "todos", destino: "nenhuma", continuacao: "sim" }),
            }),
          ],
        },
      ],
    };
  };

  /** Cenários do estudo: a mesma base, alterada para mostrar um estado. */
  G.cenarios = {
    pronto: { rotulo: "Pronto (por hipótese)", aplicar: function () {} },
    diario: {
      rotulo: "Como ficou no diário",
      aplicar: function (m) {
        // O desempate "maior idade" virou "maior valor" da data; TEC-LAB sem faixa seguinte.
        m.perfis[0].marcos[2].criterios[1].tipo = "maior_fato";
        m.perfis[2].marcos[0].corte.continuacao = null;
      },
    },
    zero: {
      rotulo: "Do zero",
      aplicar: function (m) {
        m.perfis[0].marcos = [];
      },
    },
    desempateFora: {
      rotulo: "Porta e desempate fora da ordem",
      aplicar: function (m) {
        m.perfis[1].marcos[1].entradas = ["obj", "tit", "doc", "did"];
        m.perfis[1].marcos[1].criterios.push({ tipo: "pontuacao", alvo: "ent", ausente: "ultimo" });
      },
    },
    circular: {
      rotulo: "Destino circular",
      aplicar: function (m) {
        m.perfis[0].marcos[1].corte.destino = "tit";
      },
    },
    peso: {
      rotulo: "Peso ausente",
      aplicar: function (m) {
        m.etapas[1].peso = null;
      },
    },
  };

  G.clonar = function (x) {
    return JSON.parse(JSON.stringify(x));
  };

  // ---------------------------------------------------------------- leitura estrutural

  G.etapa = function (m, id) {
    return m.etapas.find(function (e) { return e.id === id; });
  };
  G.indice = function (m, id) {
    return m.etapas.findIndex(function (e) { return e.id === id; });
  };

  /** Todos os usos de uma Etapa: enumeração e alvo de desempate, em todos os Perfis. */
  G.usos = function (m, etapaId) {
    const usos = [];
    m.perfis.forEach(function (p) {
      p.marcos.forEach(function (mc) {
        if (mc.entradas.indexOf(etapaId) >= 0) usos.push({ perfil: p, marco: mc, como: "entrada" });
        mc.criterios.forEach(function (c) {
          if (c.tipo === "pontuacao" && c.alvo === etapaId) usos.push({ perfil: p, marco: mc, como: "desempate" });
        });
      });
    });
    return usos;
  };

  /**
   * A marca classificatória. No GPS ela é declarada à mão (`EtapaAvaliacao.classificatory`) e só
   * habilita a enumeração (validation.py:794) e o seletor de alvos (views.py:3142). No modo
   * "derivada" — uma das opções da decisão D-1 — ela é deduzida dos usos.
   */
  G.classificatoria = function (m, e, modoMarca) {
    if (modoMarca === "derivada") return G.usos(m, e.id).length > 0;
    return !!e.classificatoriaManual;
  };

  /** Posição do marco na jornada: depois da última Etapa que ele usa (jornada.py, `_ultima`). */
  G.posicao = function (m, mc) {
    let pos = -1;
    mc.entradas.forEach(function (id) {
      pos = Math.max(pos, G.indice(m, id));
    });
    return pos;
  };

  G.ePorta = function (m, id) {
    const e = G.etapa(m, id);
    return e && e.forma === "decisao";
  };

  // ---------------------------------------------------------------- tradução (texto do documento)

  function aspas(t) {
    return "“" + t + "”";
  }

  function lista(itens) {
    if (itens.length <= 1) return itens.join("");
    return itens.slice(0, -1).join(", ") + " e " + itens[itens.length - 1];
  }

  /**
   * Redação aproximada das frases de pdf.py (frases_da_combinacao, frases_do_corte,
   * frase_da_continuacao, frases_do_desempate). No produto, seriam as próprias funções.
   */
  G.frases = function (m, perfil, mc) {
    const fr = { ordem: "", porta: "", corte: [], desempate: [] };
    const pontuadas = mc.entradas.filter(function (id) { return !G.ePorta(m, id); });
    const portas = mc.entradas.filter(function (id) { return G.ePorta(m, id); });
    const comPeso = pontuadas.map(function (id) {
      const e = G.etapa(m, id);
      return aspas(e.nome) + " (peso " + (e.peso == null ? "?" : e.peso) + ")";
    });
    if (pontuadas.length === 0) {
      fr.ordem = mc.entradas.length ? "Não há nota a combinar: a ordem sai só dos critérios de desempate." : "";
    } else if (pontuadas.length === 1 && mc.divide) {
      fr.ordem = "A nota final é a pontuação obtida na Etapa " + aspas(G.etapa(m, pontuadas[0]).nome) + ".";
    } else if (mc.divide) {
      fr.ordem = "A nota final é a média ponderada das pontuações nas Etapas " + lista(comPeso) + ".";
    } else {
      fr.ordem = "A nota final é a soma das pontuações nas Etapas " + lista(comPeso) +
        ", cada uma multiplicada pelo seu peso.";
    }
    if (portas.length) {
      fr.porta = "Só entra nesta ordem quem obtiver " + lista(portas.map(function (id) {
        const e = G.etapa(m, id);
        return aspas(e.favoravel) + " na Etapa " + aspas(e.nome);
      })) + ".";
    }
    const c = mc.corte;
    if (c.tipo === "fixo" && c.alvo) {
      const quem = "os " + c.alvo + " primeiros classificados de cada lista de concorrência" + (c.suplentes ? ", mais " + c.suplentes + " suplentes" : "");
      if (c.destino && c.destino !== "nenhuma") fr.corte.push("Passam para a Etapa " + aspas(G.etapa(m, c.destino).nome) + " " + quem + ".");
      else fr.corte.push("São classificados " + quem + ".");
    } else if (c.tipo === "quadro") {
      fr.corte.push("Seguem os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista (" + perfil.vagas + " na ampla).");
    } else if (c.tipo === "nao") {
      fr.corte.push("Esta ordem não corta: a Etapa seguinte recebe todos os habilitados.");
    }
    if (c.tipo && c.tipo !== "nao") {
      if (c.empate === "todos") fr.corte.push("Se houver empate na última posição, passam todos os empatados, mesmo que ultrapassem esse número.");
      if (c.empate === "para") fr.corte.push("Se houver empate na última posição, esse número não é ultrapassado.");
      if (c.continuacao === "sim") fr.corte.push("Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem.");
      if (c.continuacao === "nao") fr.corte.push("Não serão chamados candidatos além desses.");
    }
    mc.criterios.forEach(function (cr) {
      fr.desempate.push(G.fraseDoCriterio(m, perfil, cr));
    });
    return fr;
  };

  G.fraseDoCriterio = function (m, perfil, cr) {
    let t = "";
    if (cr.tipo === "pontuacao") {
      const e = G.etapa(m, cr.alvo);
      t = e ? "maior pontuação na Etapa " + aspas(e.nome) : "maior pontuação na Etapa (escolha)";
    } else {
      const f = perfil.fatos.find(function (x) { return x.id === cr.alvo; });
      if (!f) t = "valor de um fato (escolha)";
      else if (f.tipo === "data" && cr.tipo === "menor_fato") t = "data de nascimento mais antiga — <strong>o candidato mais velho</strong> tem preferência";
      else if (f.tipo === "data" && cr.tipo === "maior_fato") t = "data de nascimento mais recente — <strong>o candidato mais novo</strong> tem preferência";
      else t = (cr.tipo === "maior_fato" ? "maior" : "menor") + " valor de " + aspas(f.rotulo);
    }
    if (cr.ausente === "ultimo") t += "; quem não o tiver fica em último lugar neste critério";
    if (cr.ausente === "naoaplica") t += "; se alguém do grupo não o tiver, o critério não se aplica ao grupo";
    return t;
  };

  /** A regra local da Etapa, como tabela de decisão (regra.py: `consequencia`, `impedimento_da_regra`). */
  G.tabelaLocal = function (e) {
    if (e.forma === "decisao") {
      return e.eliminatoria
        ? { linhas: [[e.favoravel, "habilitado — segue"], [e.desfavoravel, "eliminado"]] }
        : { linhas: [[e.favoravel, "segue"], [e.desfavoravel, "efeito não declarado"]],
            impede: "Decisória não eliminatória: o resultado desfavorável não tem consequência declarada, e a consolidação é impedida." };
    }
    if (e.eliminatoria && e.minima != null) {
      return { linhas: [["nota menor que " + fmt(e.minima), "eliminado"], ["nota " + fmt(e.minima) + " ou maior", "habilitado — segue"]] };
    }
    if (e.eliminatoria) {
      return { linhas: [["qualquer nota", "?"]],
        impede: "Eliminatória sem nota mínima: não há regra para decidir quem é eliminado, e a consolidação é impedida." };
    }
    return { linhas: [["qualquer nota", "segue — a nota só pesa onde for usada"]],
      nota: e.minima != null ? "A mínima de " + fmt(e.minima) + " não elimina: a Etapa não é eliminatória." : "" };
  };

  function fmt(n) {
    return String(n).replace(".", ",");
  }
  G.fmt = fmt;

  // ---------------------------------------------------------------- diagnóstico

  /**
   * Níveis, nos dois eixos da rodada 1:
   *   naoRespondida — pergunta ainda não respondida (sem alarme)
   *   incompleta    — falta uma parte; o documento não publica (IMPEDE)
   *   invalida      — contradiz uma regra do domínio
   *   execucao      — publica, mas a consolidação ou o cálculo serão impedidos
   *   leitura       — não é regra: uma pista sobre o que a configuração diz
   */
  G.diagnostico = function (m, modoMarca) {
    const d = [];
    function add(nivel, perfil, alvo, texto, campo) {
      d.push({ nivel, perfil: perfil && perfil.id, alvo, texto, campo });
    }
    m.etapas.forEach(function (e) {
      const t = G.tabelaLocal(e);
      if (t.impede) add("execucao", null, { tipo: "etapa", id: e.id }, e.nome + ": " + t.impede, "eliminatoria");
    });
    m.perfis.forEach(function (p) {
      const governadas = {};
      if (!p.marcos.length) add("incompleta", p, null, p.codigo + " não declara ordem alguma: ninguém é classificado.", null);
      p.marcos.forEach(function (mc) {
        const rot = p.codigo + " · " + mc.codigo;
        const alvo = { tipo: "marco", id: mc.id, perfil: p.id };
        if (!mc.entradas.length) add("naoRespondida", p, alvo, rot + ": escolha as Etapas que formam a ordem.", "entradas");
        mc.entradas.forEach(function (id) {
          const e = G.etapa(m, id);
          if (!e) return;
          // validation.py:794 — milestone_stage_not_classificatory
          if (!G.classificatoria(m, e, modoMarca))
            add("invalida", p, alvo, rot + " usa " + aspas(e.nome) + ", que não está marcada como classificatória.", "marca:" + e.id);
          if (e.forma === "nota" && e.peso == null)
            add("incompleta", p, alvo, rot + " usa " + aspas(e.nome) + ", que não declara peso.", "peso:" + e.id);
        });
        const pontuadas = mc.entradas.filter(function (id) { return !G.ePorta(m, id); });
        if (mc.entradas.length && !pontuadas.length && mc.divide)
          add("invalida", p, alvo, rot + ": média de Etapas que não têm nota — não há divisor.", "divide");
        const c = mc.corte;
        const corta = c.tipo !== "nao";
        if (corta && c.destino === "") add("naoRespondida", p, alvo, rot + ": escolha a Etapa que recebe quem passar.", "destino");
        else if (corta && !c.destino) add("naoRespondida", p, alvo, rot + ": diga o que acontece depois desta ordem.", "destino");
        if (corta && c.destino && c.destino !== "nenhuma" && mc.entradas.indexOf(c.destino) >= 0)
          // validation.py `_regra_de_corte_do_marco`: circularidade direta
          add("invalida", p, alvo, rot + " decide quem faz " + aspas(G.etapa(m, c.destino).nome) + ", mas usa a nota dessa mesma Etapa.", "destino");
        if (corta && c.destino && c.destino !== "nenhuma") {
          // validation.py `_corte_em_dois_marcos`
          if (governadas[c.destino])
            add("invalida", p, alvo, rot + " e " + governadas[c.destino] + " decidem, os dois, quem faz " + aspas(G.etapa(m, c.destino).nome) + ".", "destino");
          governadas[c.destino] = mc.codigo;
        }
        if (corta && c.destino && !c.tipo) add("naoRespondida", p, alvo, rot + ": quantos seguem?", "tipo");
        if (c.tipo === "fixo" && !c.alvo) add("incompleta", p, alvo, rot + ": falta o número dos que seguem.", "alvo");
        if (c.tipo && c.tipo !== "nao" && !c.empate) add("incompleta", p, alvo, rot + ": falta dizer o que acontece com o empate na última posição.", "empate");
        if (c.tipo && c.tipo !== "nao" && !c.continuacao) add("incompleta", p, alvo, rot + ": falta dizer se a faixa pode avançar quando alguém não assume.", "continuacao");
        mc.criterios.forEach(function (cr, i) {
          const okAlvo = cr.tipo === "pontuacao" ? !!G.etapa(m, cr.alvo) : !!p.fatos.find(function (f) { return f.id === cr.alvo; });
          if (!okAlvo) add("incompleta", p, alvo, rot + ": o " + (i + 1) + "º critério de desempate não diz o que compara.", "criterio:" + i);
          if (!cr.ausente) add("incompleta", p, alvo, rot + ": o " + (i + 1) + "º critério não diz o que fazer quando o valor falta.", "criterio:" + i);
          // calculo.py lê só os Resultados das Etapas enumeradas (`etapa_id__in=enumeradas`), e
          // universo_classificavel.py monta as pontuações deles: a nota de outra Etapa chega vazia.
          if (cr.tipo === "pontuacao" && okAlvo && mc.entradas.indexOf(cr.alvo) < 0)
            add("execucao", p, alvo, rot + ": o " + (i + 1) + "º critério compara a nota de " + aspas(G.etapa(m, cr.alvo).nome) +
              ", que esta ordem não usa. O cálculo só lê as notas das Etapas usadas: o valor faltará para todos, e o critério não separa ninguém.", "criterio:" + i);
        });
      });
      // ---- leituras: não são regras do GPS, são o que a estrutura diz
      const rel = G.relacoes(m, p);
      if (p.marcos.length && !rel.temFinal)
        add("leitura", p, null, p.codigo + ": todas as ordens alimentam outra Etapa — nenhuma é a classificação final.", null);
      rel.saltos.forEach(function (s) {
        add("leitura", p, { tipo: "marco", id: s.marco.id, perfil: p.id },
          p.codigo + " · " + s.marco.codigo + " corta para " + aspas(G.etapa(m, s.destino).nome) + ", mas antes dela acontece " +
          lista(s.puladas.map(function (id) { return aspas(G.etapa(m, id).nome); })) + " — que recebe todos os habilitados, sem corte.", null);
      });
      const porMarco = {};
      rel.eliminatoriasDepois.forEach(function (x) {
        (porMarco[x.marco.id] = porMarco[x.marco.id] || { marco: x.marco, etapas: [] }).etapas.push(x.etapa);
      });
      Object.keys(porMarco).forEach(function (id) {
        const x = porMarco[id];
        const nomes = x.etapas.map(function (e) { return aspas(G.etapa(m, e).nome); });
        add("leitura", p, { tipo: "marco", id: x.marco.id, perfil: p.id },
          p.codigo + " · " + x.marco.codigo + " fecha a classificação antes de " + lista(nomes) +
          (nomes.length > 1 ? ", que eliminam" : ", que elimina") + ": quem for eliminado depois já estará classificado.", null);
      });
    });
    return d;
  };

  /** Relações derivadas da ordem das Etapas — o que a reordenação pode mudar. */
  G.relacoes = function (m, p) {
    const r = { temFinal: false, saltos: [], eliminatoriasDepois: [], posicoes: {} };
    p.marcos.forEach(function (mc) {
      const pos = G.posicao(m, mc);
      r.posicoes[mc.id] = pos;
      const c = mc.corte;
      if (c.tipo === "nao") return;
      if (c.destino === "nenhuma") {
        r.temFinal = true;
        m.etapas.forEach(function (e, i) {
          if (i > pos && e.eliminatoria) r.eliminatoriasDepois.push({ marco: mc, etapa: e.id });
        });
      } else if (c.destino) {
        const di = G.indice(m, c.destino);
        if (di > pos + 1) {
          const puladas = m.etapas.slice(pos + 1, di).map(function (e) { return e.id; });
          r.saltos.push({ marco: mc, destino: c.destino, puladas });
        }
      }
    });
    return r;
  };

  /** Compara duas versões e diz, em frases, o que mudou na estrutura (sem dado pessoal). */
  G.impacto = function (antes, depois, modoMarca) {
    const chave = function (x) { return x.nivel + "|" + x.texto; };
    const a = G.diagnostico(antes, modoMarca).filter(function (x) { return x.nivel !== "naoRespondida"; });
    const b = G.diagnostico(depois, modoMarca).filter(function (x) { return x.nivel !== "naoRespondida"; });
    const ka = new Set(a.map(chave));
    const kb = new Set(b.map(chave));
    const novas = b.filter(function (x) { return !ka.has(chave(x)); });
    const resolvidas = a.filter(function (x) { return !kb.has(chave(x)); });
    const posicoes = [];
    depois.perfis.forEach(function (p, i) {
      const pa = antes.perfis[i];
      p.marcos.forEach(function (mc) {
        const ma = pa.marcos.find(function (x) { return x.id === mc.id; });
        if (!ma) return;
        const ia = G.posicao(antes, ma);
        const ib = G.posicao(depois, mc);
        const ea = antes.etapas[ia];
        const eb = depois.etapas[ib];
        if (ea && eb && ea.id !== eb.id)
          posicoes.push(p.codigo + " · " + mc.codigo + " passa a fechar depois de " + aspas(eb.nome) + " (antes: depois de " + aspas(ea.nome) + ").");
      });
    });
    return { novas, resolvidas, posicoes };
  };
})();
