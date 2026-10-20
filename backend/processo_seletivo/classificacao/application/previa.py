"""A prévia da classificação: o motor oficial sobre candidatos fictícios, sem gravar nada (094).

**Nenhuma consulta e nenhuma escrita.** Quem chama entrega o marco digitado, as Etapas e os fatos do
rascunho e as vagas do quadro; daqui sai o que o painel mostra. Não há ato, não há posição gravada,
não há trilha: a prévia existe só na resposta (FR-2234).

**Nenhuma regra própria.** A preparação do universo é `universo_classificavel.preparar`, a mesma
que `calcular_ordem` chama; a ordem é `desempate.ordenar_com_trajetoria`, de que `ordenar` deriva;
a faixa é `faixa.calcular`. O que este módulo acrescenta é a escolha dos candidatos
(`cenarios_da_previa`), a leitura das recusas como resultado e o estado comparável que diz o que
mudou (FR-2230, FR-2244).

**A fronteira das vagas chega por parâmetro.** Ela é `apuracao.titulares_iniciais`, da `ocupacao`, e
`classificacao` nunca importa `ocupacao` — é a fronteira de 11/09/2026 que
`tests/test_dependencia_da_ocupacao.py` prende. Quem chama a prévia (a interface, que pode importar
os dois) entrega a verificação pronta em `apurar_vagas`; sem ela, o aviso sai "não avaliado".
"""

from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.classificacao.domain import desempate, faixa
from processo_seletivo.classificacao.domain.combinacao import RegraIncompleta
from processo_seletivo.classificacao.domain.universo_classificavel import preparar

POR_PONTUACAO = "POR_PONTUACAO"
ESTAVEL, CASO_LIMITE = "estavel", "caso"

#: A consequência curta de cada candidato — a resposta a "esta pessoa avança?" (D-012, D-016).
AVANCA, PELO_EMPATE, NAO_AVANCA, AGUARDA, SEM_POSICAO, SEGUE = "PENASC"


class Incompleto(Exception):
    """O que falta declarar para a prévia calcular — nomeado, e nunca presumido (FR-2227)."""

    def __init__(self, faltas):
        self.faltas = list(faltas)
        super().__init__("; ".join(self.faltas))


class ForaDaFatia(Exception):
    """O marco não ordena pela pontuação, e a fatia 1 não simula sorteio (D-007)."""


def _ultima_enumerada(marco, etapas):
    enumeradas = [etapas[e] for e in marco.get("stages") or [] if e in etapas]
    return max(enumeradas, key=lambda e: e.get("order") or 0) if enumeradas else None


def _faltas(marco, etapas, regra, vagas):
    faltas = []
    enumeradas = [etapas[e] for e in marco.get("stages") or [] if e in etapas]
    if not enumeradas:
        faltas.append("Enumere ao menos uma Etapa: um marco pela pontuação precisa de uma.")
    com_nota = [e for e in enumeradas if e.get("forma") != cenarios.DECISORIA]
    if len(com_nota) > cenarios.ETAPAS_COM_NOTA:
        faltas.append(
            f"A prévia cobre até {cenarios.ETAPAS_COM_NOTA} Etapas com nota enumeradas; este marco "
            f"enumera {len(com_nota)}."
        )
    for criterio in marco.get("tiebreakers") or []:
        ordem = criterio.get("order") or "?"
        if not criterio.get("type"):
            faltas.append(f"O {ordem}º critério de desempate não diz qual é.")
        elif not (criterio.get("parameters") or {}):
            faltas.append(f"O {ordem}º critério de desempate não diz o que compara.")
    if regra:
        if regra.get("targetKind") == faixa.ALVO_FIXO and regra.get("targetCount") is None:
            faltas.append("Declare o alvo: a quantidade fixa está vazia.")
        if regra.get("targetKind") == faixa.ALVO_DO_QUADRO and vagas is None:
            faltas.append(
                "O alvo vem do quadro, e o quadro do Perfil não tem linha geral: o alvo não é "
                "apurável, e ausência não vira zero."
            )
    return faltas


def simular(
    marco,
    etapas_publicadas,
    fatos,
    *,
    vagas,
    modo=ESTAVEL,
    caso="",
    populacao=None,
    apurar_vagas=None,
):
    """Tudo o que o painel mostra do marco `marco`, ou `Incompleto` com o que falta.

    `etapas_publicadas` são as Etapas do conteúdo do rascunho; `fatos`, os fatos declarados do
    Perfil; `vagas`, a quantidade da linha geral do quadro, ou `None` quando não há. `populacao` é
    `(alvo, faixa, vagas)` com que a população estável foi montada — `None` monta agora.

    `apurar_vagas(progrediram, vagas, empates)` devolve `None`, quando a apuração das vagas seria
    possível, ou `(posicao, quantas)` do empate que a pararia.
    """
    if (marco.get("orderProduction") or POR_PONTUACAO) != POR_PONTUACAO:
        raise ForaDaFatia
    etapas = {str(e["id"]): e for e in etapas_publicadas}
    regra = faixa.normalizar(marco.get("cutRule"))
    faltas = _faltas(marco, etapas, regra, vagas)
    if faltas:
        raise Incompleto(faltas)

    alvo = suplentes = None
    origem_do_alvo = ""
    if regra:
        suplentes = regra["surplusCount"]
        if regra["targetKind"] == faixa.ALVO_FIXO:
            alvo = int(regra["targetCount"])
            origem_do_alvo = "número publicado no marco"
        else:
            alvo = int(vagas)
            origem_do_alvo = "linha geral do quadro de vagas do Perfil"
    faixa_total = (alvo or 0) + (suplentes or 0) if regra else 0
    fronteiras = (alvo or 0, faixa_total, vagas or 0)

    enumeradas = [etapas[e] for e in marco.get("stages") or [] if e in etapas]
    etapa_do_marco = _ultima_enumerada(marco, etapas)
    if modo == CASO_LIMITE and caso in cenarios.CASOS:
        candidatos, onde = cenarios.caso_limite(
            caso,
            etapas_enumeradas=enumeradas,
            etapa_do_marco=etapa_do_marco,
            fatos=fatos,
            alvo=alvo,
            suplentes=suplentes,
            vagas=vagas,
            corta=bool(regra),
        )
        ancoras, plantados = fronteiras, [onde] if onde else []
    else:
        modo, caso = ESTAVEL, ""
        ancoras = tuple(populacao) if populacao else fronteiras
        candidatos, plantados = cenarios.populacao_estavel(
            etapas_enumeradas=enumeradas,
            etapa_do_marco=etapa_do_marco,
            fatos=fatos,
            alvo=ancoras[0],
            faixa=ancoras[1],
            vagas=ancoras[2],
        )
        onde = None

    try:
        classificaveis, sem_posicao = preparar(marco, etapas, cenarios.inscritos(candidatos))
    except RegraIncompleta as erro:
        raise Incompleto([str(erro)]) from erro

    criterios = sorted(marco.get("tiebreakers") or [], key=lambda c: c.get("order") or 0)
    sem_declaracao = [
        c
        for c in criterios
        if not c.get("whenMissing")
        and any(desempate._valor_do_criterio(c, p) is None for p in classificaveis)
    ]
    if sem_declaracao:
        raise Incompleto(
            [
                f"O {c.get('order')}º critério não declara o que fazer quando o valor não existe, "
                "e um candidato fictício não o tem. A prévia não presume nenhuma das duas."
                for c in sem_declaracao
            ]
        )

    ordem = desempate.ordenar_com_trajetoria(classificaveis, criterios)
    corte = _corte(regra, ordem, sem_posicao, alvo=alvo, suplentes=suplentes)
    previa = {
        "marco": marco,
        "modo": modo,
        "caso": caso,
        "onde": onde,
        "plantados": plantados,
        "ancoras": tuple(ancoras),
        "fronteiras": fronteiras,
        "total": len(candidatos),
        "ordem": ordem,
        "sem_posicao": sem_posicao,
        "regra": regra,
        "alvo": alvo,
        "suplentes": suplentes,
        "origem_do_alvo": origem_do_alvo,
        "corte": corte,
        "vagas": vagas,
        "aviso_das_vagas": _fronteira_das_vagas(corte, ordem, vagas, apurar_vagas),
        "etapas": etapas,
        "etapas_do_marco": enumeradas,
        "criterios": criterios,
    }
    previa["consequencias"] = consequencias(ordem, sem_posicao, corte)
    return previa


def _corte(regra, ordem, sem_posicao, *, alvo, suplentes):
    """O corte, com as recusas como resultado (D-005) — e o outro desfecho, como comparação."""
    if not regra:
        return {"declarado": False, "progrediram": [i["inscricao_id"] for i in ordem]}
    posicoes = [(i["inscricao_id"], i["posicao"]) for i in ordem] + [
        (i["inscricao_id"], None) for i in sem_posicao
    ]

    def rodar(desfecho):
        try:
            progrediram, excedentes, _, ultima = faixa.calcular(
                posicoes, alvo=alvo, excedente=suplentes, desfecho=desfecho
            )
        except faixa.EmpateAtravessaOCorte as erro:
            return {"recusado": True, "posicao": erro.posicao, "quantas": erro.quantas}
        return {
            "recusado": False,
            "progrediram": progrediram,
            "excedentes": excedentes,
            "ultima": ultima,
        }

    desfecho = regra.get("tieOutcome") or None
    if desfecho in faixa.DESFECHOS_DE_EMPATE:
        principal = rodar(desfecho)
        outro = (
            faixa.EMPATE_ESTRITO
            if desfecho == faixa.EMPATE_ADMITE_EXCEDENTE
            else faixa.EMPATE_ADMITE_EXCEDENTE
        )
        atravessa = principal["recusado"] or bool(principal.get("excedentes"))
        return {
            "declarado": True,
            "desfecho": desfecho,
            **principal,
            "atravessa": atravessa,
            "alternativo": {**rodar(outro), "desfecho": outro} if atravessa else None,
        }
    # Sem desfecho declarado: as duas consequências, e nenhuma escolhida (FR-2216). `faixa.calcular`
    # com `desfecho=None` admitiria o excedente em silêncio — por isso as duas rodam explícitas.
    admite = rodar(faixa.EMPATE_ADMITE_EXCEDENTE)
    estrito = rodar(faixa.EMPATE_ESTRITO)
    atravessa = estrito["recusado"]
    return {
        "declarado": True,
        "desfecho": None,
        "recusado": False,
        "sem_desfecho": True,
        "atravessa": atravessa,
        "progrediram": [] if atravessa else admite["progrediram"],
        "excedentes": [],
        "ultima": admite.get("ultima"),
        "comparacao": {"admite": admite, "estrito": estrito} if atravessa else None,
    }


def impedido(corte):
    """O corte não seria emitido — recusado, ou dependente de um desfecho que falta."""
    return bool(corte.get("recusado") or (corte.get("sem_desfecho") and corte.get("atravessa")))


def _fronteira_das_vagas(corte, ordem, vagas, apurar_vagas):
    """A recusa da apuração, antecipada como hipótese (D-006, R-007)."""
    if not vagas:
        return {"avaliado": False, "motivo": "o Perfil não tem quadro de vagas com linha geral."}
    if impedido(corte):
        return {"avaliado": False, "motivo": "o corte não sairia, e não há quem apurar."}
    if apurar_vagas is None:
        return {"avaliado": False, "motivo": "a apuração das vagas não foi pedida."}
    empates = {i["inscricao_id"]: i["posicao"] for i in ordem if i["empate_residual"]}
    parada = apurar_vagas(corte["progrediram"], vagas, empates)
    if parada is None:
        return {"avaliado": True, "para": False}
    posicao, quantas = parada
    return {"avaliado": True, "para": True, "posicao": posicao, "quantas": quantas}


def consequencias(ordem, sem_posicao, corte):
    """`{inscricao_id: código}`.

    O empate que entra pelo desfecho marca o **grupo** inteiro: o motor não ordena os empatados
    entre si, e marcar um como "avança" e o outro como "pelo empate" seria escolher entre eles
    (FR-2212).
    """
    saida = {i["inscricao_id"]: SEM_POSICAO for i in sem_posicao}
    if not corte["declarado"]:
        saida.update({i["inscricao_id"]: SEGUE for i in ordem})
        return saida
    if impedido(corte):
        saida.update({i["inscricao_id"]: AGUARDA for i in ordem})
        return saida
    dentro = set(corte["progrediram"])
    excedentes = set(corte.get("excedentes") or [])
    por_posicao = {}
    for item in ordem:
        por_posicao.setdefault(item["posicao"], []).append(item["inscricao_id"])
    for item in ordem:
        ident = item["inscricao_id"]
        if ident not in dentro:
            saida[ident] = NAO_AVANCA
        elif excedentes and excedentes & set(por_posicao[item["posicao"]]):
            saida[ident] = PELO_EMPATE
        else:
            saida[ident] = AVANCA
    return saida


def estado(previa):
    """O estado comparável do cálculo: texto curto, que o painel devolve no pedido seguinte.

    `modo~população~corte~apuração~códigos`: os códigos são uma letra por candidato, na ordem de
    montagem. Nada fica na sessão nem no banco (FR-2234).
    """
    corte = previa["corte"]
    if not corte["declarado"]:
        situacao_do_corte = "sem-corte"
    elif corte.get("recusado"):
        situacao_do_corte = f"impedido-{corte['posicao']}"
    elif corte.get("sem_desfecho") and corte.get("atravessa"):
        situacao_do_corte = "sem-desfecho"
    else:
        situacao_do_corte = "emitivel"
    aviso = previa["aviso_das_vagas"]
    if not aviso["avaliado"]:
        vagas = "nao-avaliada"
    else:
        vagas = f"para-{aviso['posicao']}" if aviso["para"] else "possivel"
    codigos = "".join(
        previa["consequencias"].get(f"F{slot:03d}", "-") for slot in range(previa["total"])
    )
    populacao = ":".join(str(n) for n in previa["ancoras"])
    chave = f"caso-{previa['caso']}" if previa["modo"] == CASO_LIMITE else ESTAVEL
    return "~".join([chave, populacao, situacao_do_corte, vagas, codigos])


_CORTE_LEGIVEL = {"emitivel": "emitível", "sem-corte": "sem corte", "sem-desfecho": "sem desfecho"}
_VAGAS_LEGIVEL = {"possivel": "possível", "nao-avaliada": "não avaliada"}


def _corte_legivel(valor):
    if valor.startswith("impedido-"):
        return f"impedido na {valor.split('-')[1]}ª"
    return _CORTE_LEGIVEL.get(valor, valor)


def _vagas_legivel(valor):
    if valor.startswith("para-"):
        return f"pararia na {valor.split('-')[1]}ª"
    return _VAGAS_LEGIVEL.get(valor, valor)


def _avancam(codigos):
    return sum(1 for c in codigos if c in (AVANCA, PELO_EMPATE, SEGUE))


def comparar(anterior, atual):
    """O que mudou entre dois estados da **mesma** população — ou `None` se não são comparáveis.

    Entre populações ou modos diferentes, a diferença seria dos dados, e não da regra (FR-2244).
    """
    if not anterior:
        return None
    try:
        a_chave, a_pop, a_corte, a_vagas, a_cod = anterior.split("~")
        b_chave, b_pop, b_corte, b_vagas, b_cod = atual.split("~")
    except ValueError:
        return None
    if (a_chave, a_pop) != (b_chave, b_pop) or len(a_cod) != len(b_cod):
        return None
    mudancas = []
    if a_corte != b_corte:
        mudancas.append(f"Corte: {_corte_legivel(a_corte)} → {_corte_legivel(b_corte)}.")
    if _avancam(a_cod) != _avancam(b_cod):
        mudancas.append(f"Avançam: {_avancam(a_cod)} → {_avancam(b_cod)}.")
    if a_vagas != b_vagas:
        mudancas.append(
            f"Apuração das vagas: {_vagas_legivel(a_vagas)} → {_vagas_legivel(b_vagas)}."
        )
    mudaram = {f"F{i:03d}" for i, (x, y) in enumerate(zip(a_cod, b_cod, strict=True)) if x != y}
    return {"mudancas": mudancas, "mudaram": mudaram}


__all__ = [
    "AGUARDA",
    "AVANCA",
    "CASO_LIMITE",
    "ESTAVEL",
    "ForaDaFatia",
    "Incompleto",
    "NAO_AVANCA",
    "PELO_EMPATE",
    "SEGUE",
    "SEM_POSICAO",
    "comparar",
    "consequencias",
    "estado",
    "impedido",
    "simular",
]
