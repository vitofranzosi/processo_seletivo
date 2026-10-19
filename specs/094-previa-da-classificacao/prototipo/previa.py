"""O cálculo da prévia do protótipo da 094 — o motor oficial de verdade, e a cola em esboço.

**O que executa o motor oficial**, importado do produto e chamado sem cópia:
`combinacao.combinar`, `desempate.ordenar`, `desempate.particiona_o_grupo`, `faixa.calcular` e
`apuracao.titulares_iniciais`. As exceções que eles levantam — `RegraIncompleta`,
`EmpateAtravessaOCorte`, `EmpateNaFronteiraDoAlvo` — são as do produto.

**O que é demonstrativo**, e a tela diz que é: a geração dos cenários (`cenario`), a função que a
spec manda extrair de `calcular_ordem` (`preparar_universo`, esboço da T006), a trajetória da
partição (`ordenar_com_trajetoria`, esboço da T008) e as frases. A trajetória é conferida contra
`desempate.ordenar` a cada cálculo: se divergir, a prévia diz, em vez de mostrar uma ordem própria.

Sem Django e sem banco: os núcleos puros não importam nada do framework, e é o que permite este
protótipo rodar num servidor da biblioteca padrão.
"""

from __future__ import annotations

import datetime
from decimal import Decimal

from processo_seletivo.classificacao.domain import combinacao, desempate, faixa
from processo_seletivo.ocupacao.domain import apuracao

HABILITADA, ELIMINADA = "HABILITADA", "ELIMINADA"
DECISORIA = combinacao.DECISORIA

# O Edital do protótipo. No produto, Etapas e pesos vêm do passo Etapas, e fatos e quadro do passo
# Perfis — todos gravados no rascunho. Aqui são editáveis só para a avaliação.
ETAPAS = [
    {"id": "e-escrita", "name": "Prova Escrita", "weight": "2", "forma": "NOTA", "order": 1},
    {"id": "e-titulos", "name": "Prova de Títulos", "weight": "1", "forma": "NOTA", "order": 2},
    {
        "id": "e-documentos",
        "name": "Análise documental",
        "weight": None,
        "forma": DECISORIA,
        "order": 3,
    },
    {"id": "e-entrevista", "name": "Entrevista", "weight": "1", "forma": "NOTA", "order": 4},
]
FATOS = [
    {"id": "f-nascimento", "name": "Data de nascimento", "type": "DATA"},
    {"id": "f-servico", "name": "Tempo de serviço (meses)", "type": "INTEIRO"},
]

CENARIOS = {
    "sem_empate": (
        "Classificação sem empate",
        "Pontuações distintas para todos: nenhum critério de desempate é usado.",
    ),
    "criterios_sucessivos": (
        "Desempate por critérios sucessivos",
        "Três candidatos com as mesmas notas em todas as Etapas, perto do fim do alvo. Diferem só "
        "nos fatos: um é mais velho que os outros dois, que diferem no tempo de serviço.",
    ),
    "empate_na_faixa": (
        "Corte impedido: empate na última posição da faixa",
        "Dois candidatos iguais em tudo — notas e fatos —, na última posição de alvo + suplentes. "
        "Um cabe na faixa pela contagem, o outro não.",
    ),
    "empate_nas_vagas": (
        "Empate na fronteira das vagas",
        "Dois candidatos iguais em tudo na última posição das vagas do quadro. Com suplentes, o "
        "empate fica dentro da faixa: o corte sai, e é a apuração das vagas que para.",
    ),
    "valor_ausente": (
        "Valor ausente",
        "Uma candidata sem nota numa Etapa enumerada, um candidato eliminado na Etapa do marco, e "
        "dois empatados na pontuação em que um deles não declarou a data de nascimento.",
    ),
}

NOMES = (
    "Alice Bruno Carla Diego Elisa Fábio Gabriela Heitor Íris João Karina Lucas Marina Nuno "
    "Olívia Paulo Quitéria Rafael Sofia Tiago Úrsula Vítor Wanda Xavier Yara Zeca"
).split()


class Incompleto(Exception):
    """O que falta declarar para a prévia calcular — nomeado, e nunca presumido (FR-2227)."""

    def __init__(self, faltas):
        self.faltas = faltas
        super().__init__("; ".join(faltas))


# ---------------------------------------------------------------------------------------------
# Os candidatos fictícios (demonstrativo — D-003)
# ---------------------------------------------------------------------------------------------


def _nome(slot):
    base = NOMES[slot % len(NOMES)]
    volta = slot // len(NOMES)
    return base if volta == 0 else f"{base} {volta + 1}"


def _nota(slot, total):
    """Notas inteiras e distintas enquanto couberem; com mais gente, duas casas."""
    if total <= 90:
        return Decimal(95 - slot)
    passo = Decimal(90) / Decimal(total)
    return (Decimal(95) - passo * slot).quantize(Decimal("0.01"))


def _fatos_padrao(slot):
    nascimento = datetime.date(1965, 1, 1) + datetime.timedelta(days=211 * slot)
    return {"f-nascimento": nascimento, "f-servico": 12 + (slot * 7) % 97}


def cenario(chave, *, enumeradas, etapa_do_marco, alvo, suplentes, vagas, corta):
    """Os candidatos fictícios — função do cenário, das Etapas e das fronteiras, e de nada mais.

    Pesos, critérios, desfecho, Etapa governada e continuação **não** entram: é o que faz dois
    recálculos com o mesmo alvo compararem as mesmas pessoas (FR-2205).
    """
    faixa_total = (alvo or 0) + (suplentes or 0) if corta else 0
    referencia = max(faixa_total, vagas or 0, alvo or 0, 8)
    total = min(referencia + 4, 600)
    notas = [etapa for etapa in enumeradas if etapa["forma"] != DECISORIA]
    portas = [etapa for etapa in enumeradas if etapa["forma"] == DECISORIA]

    candidatos = []
    for slot in range(total):
        nota = _nota(slot, total)
        candidatos.append(
            {
                "slot": slot,
                "nome": _nome(slot),
                "notas": {etapa["id"]: nota for etapa in notas},
                "portas": [etapa["id"] for etapa in portas],
                "eliminado_em": None,
                "fatos": _fatos_padrao(slot),
            }
        )

    def igualar(destino, origem, *, fatos=True):
        candidatos[destino]["notas"] = dict(candidatos[origem]["notas"])
        if fatos:
            candidatos[destino]["fatos"] = dict(candidatos[origem]["fatos"])

    ancora_nota = None
    if chave == "criterios_sucessivos":
        primeiro = max(min((alvo or 6) - 2, total - 4), 0)
        for slot in (primeiro + 1, primeiro + 2):
            igualar(slot, primeiro, fatos=False)
        x, y, z = (candidatos[primeiro + i]["fatos"] for i in range(3))
        x["f-nascimento"] = datetime.date(1961, 5, 4)
        y["f-nascimento"] = z["f-nascimento"] = datetime.date(1979, 8, 19)
        y["f-servico"], z["f-servico"] = 84, 60
        ancora_nota = f"o trio começa na {primeiro + 1}ª posição"
    elif chave == "empate_na_faixa":
        ultima = faixa_total if corta and faixa_total else 5
        ultima = max(min(ultima, total - 1), 1)
        igualar(ultima, ultima - 1)
        ancora_nota = (
            f"o empate fica na {ultima}ª posição, a última da faixa"
            if corta and faixa_total
            else "sem regra de corte, o empate fica na 5ª posição"
        )
    elif chave == "empate_nas_vagas":
        ultima = vagas or alvo or 5
        ultima = max(min(ultima, total - 1), 1)
        igualar(ultima, ultima - 1)
        ancora_nota = (
            f"o empate fica na {ultima}ª posição, a última das vagas"
            if vagas
            else "sem quadro de vagas, o empate fica na posição do alvo"
        )
    elif chave == "valor_ausente":
        if notas:
            candidatos[1]["notas"][notas[-1]["id"]] = None
        if etapa_do_marco is not None:
            candidatos[3]["eliminado_em"] = etapa_do_marco["id"]
        igualar(6, 5, fatos=False)
        candidatos[6]["fatos"].pop("f-nascimento")
        candidatos[5]["fatos"]["f-servico"], candidatos[6]["fatos"]["f-servico"] = 30, 72
        ancora_nota = "as ausências ficam na 2ª, na 4ª e na 7ª linha"
    return candidatos, ancora_nota


# ---------------------------------------------------------------------------------------------
# A função extraída de `calcular_ordem` (esboço da T006 — D-004)
# ---------------------------------------------------------------------------------------------


def preparar_universo(marco, etapas, inscritos, *, recorte=None):
    """Classificáveis e sem posição, sem banco — o laço de `calcular_ordem`, fora dele.

    Esboço: a implementação mora em `classificacao/domain`, e `calcular_ordem` passa a chamá-la.
    `recorte` nulo é a ampla, o universo inteiro (fatia 2).
    """
    enumeradas = [str(item) for item in marco.get("stages") or []]
    classificaveis, sem_posicao = [], []
    for inscrito in inscritos:
        if recorte is not None and inscrito.get("modalidade_id") != recorte:
            continue
        resultados = inscrito["resultados"]
        pontuacoes = {r["etapa_id"]: r["pontuacao"] for r in resultados}
        base = {
            "inscricao_id": inscrito["inscricao_id"],
            "nome": inscrito["nome"],
            "modalidade_id": inscrito.get("modalidade_id"),
            "pontuacoes": pontuacoes,
            "fatos": inscrito["fatos"],
        }
        eliminadas = [r for r in resultados if r["consequencia"] == ELIMINADA]
        if eliminadas:
            mais_recente = max(
                eliminadas, key=lambda r: (etapas.get(r["etapa_id"]) or {}).get("order") or 0
            )
            nome = (etapas.get(mais_recente["etapa_id"]) or {}).get("name")
            sem_posicao.append({**base, "posicao": None, "motivo": f"Eliminado na {nome}."})
            continue
        pontuacao = combinacao.combinar(marco, etapas, pontuacoes)
        if pontuacao is combinacao.SEM_PONTUACAO:
            faltantes = [
                (etapas.get(e) or {}).get("name") or e
                for e in enumerate_notas(enumeradas, etapas)
                if pontuacoes.get(e) is None
            ]
            sem_posicao.append(
                {
                    **base,
                    "posicao": None,
                    "motivo": "Sem nota em " + ", ".join(faltantes) + ": quem não tem pontuação "
                    "numa Etapa enumerada não é classificável — ausência não vira zero.",
                }
            )
            continue
        classificaveis.append({**base, "pontuacao": pontuacao})
    return classificaveis, sem_posicao


def enumerate_notas(enumeradas, etapas):
    return [e for e in enumeradas if not combinacao.e_porta(etapas.get(e) or {})]


# ---------------------------------------------------------------------------------------------
# A trajetória da partição (esboço da T008 — D-011), conferida contra `desempate.ordenar`
# ---------------------------------------------------------------------------------------------


def _particionar(grupo, criterios, caminho):
    if len(grupo) <= 1:
        return [(grupo, caminho)]
    for indice, criterio in enumerate(criterios):
        if not desempate.particiona_o_grupo(criterio, grupo):
            caminho = [*caminho, ("nao_separou", criterio, list(grupo))]
            continue
        saida = []
        # `_grupos_por_valor` é privado no produto: a T008 o usa de dentro do módulo, e não daqui.
        for sub in desempate._grupos_por_valor(criterio, grupo):
            saida.extend(
                _particionar(sub, criterios[indice + 1 :], [*caminho, ("separou", criterio, grupo)])
            )
        return saida
    return [(grupo, caminho)]


def ordenar_com_trajetoria(participantes, criterios):
    ordenados = sorted(criterios, key=lambda item: item.get("order") or 0)
    por_pontuacao = {}
    for participante in participantes:
        por_pontuacao.setdefault(str(participante.get("pontuacao")), []).append(participante)

    def chave(par):
        valor = par[1][0].get("pontuacao")
        return Decimal("0") if valor is None else Decimal(str(valor))

    resultado = []
    for _, grupo in sorted(por_pontuacao.items(), key=chave, reverse=True):
        empatados_na_pontuacao = list(grupo)
        for sub, caminho in _particionar(grupo, ordenados, []):
            posicao = len(resultado) + 1
            for item in sub:
                resultado.append(
                    {
                        **item,
                        "posicao": posicao,
                        "empate_residual": len(sub) > 1,
                        "trajetoria": caminho,
                        "grupo_da_pontuacao": empatados_na_pontuacao,
                        "grupo_final": sub,
                    }
                )
    return resultado


def conferir_com_o_motor(com_trajetoria, participantes, criterios):
    """A ordem do esboço é a de `desempate.ordenar`? Posição, empate e quem separou, um a um."""
    oficial = desempate.ordenar(participantes, criterios)
    if len(oficial) != len(com_trajetoria):
        return False
    for a, b in zip(oficial, com_trajetoria, strict=True):
        separou_b = next(
            (c for passo, c, _ in reversed(b["trajetoria"]) if passo == "separou"), None
        )
        if (
            a["inscricao_id"] != b["inscricao_id"]
            or a["posicao"] != b["posicao"]
            or a["empate_residual"] != b["empate_residual"]
            or (a["separado_por"] or {}).get("order") != (separou_b or {}).get("order")
        ):
            return False
    return True


# ---------------------------------------------------------------------------------------------
# A prévia
# ---------------------------------------------------------------------------------------------


def _faltas_do_marco(marco, etapas):
    faltas = []
    enumeradas = [etapas[e] for e in marco.get("stages") or [] if e in etapas]
    if not enumeradas:
        faltas.append("Enumere ao menos uma Etapa: um marco pela pontuação precisa de uma.")
    if len([e for e in enumeradas if e["forma"] != DECISORIA]) > 4:
        faltas.append("A prévia cobre até quatro Etapas com nota enumeradas.")
    for criterio in marco.get("tiebreakers") or []:
        if not (criterio.get("parameters") or {}):
            faltas.append(f"O {criterio['order']}º critério não diz o que compara.")
    return faltas


def calcular(marco, etapas_publicadas, *, chave_do_cenario, vagas):
    """Tudo o que o painel mostra, ou `Incompleto` com o que falta."""
    etapas = {e["id"]: e for e in etapas_publicadas}
    faltas = _faltas_do_marco(marco, etapas)
    regra = marco.get("cutRule")
    alvo = suplentes = None
    origem_do_alvo = None
    if regra:
        suplentes = regra.get("surplusCount") or 0
        if regra.get("targetKind") == faixa.ALVO_FIXO:
            alvo = regra.get("targetCount")
            origem_do_alvo = "número publicado no marco"
            if alvo is None:
                faltas.append("Declare o alvo: a quantidade fixa está vazia.")
        elif regra.get("targetKind") == faixa.ALVO_DO_QUADRO:
            alvo = vagas
            origem_do_alvo = "linha geral do quadro de vagas do Perfil"
            if vagas is None:
                faltas.append(
                    "O alvo vem do quadro, e o quadro do Perfil não tem linha geral: o alvo não é "
                    "apurável, e ausência não vira zero."
                )
    if faltas:
        raise Incompleto(faltas)

    enumeradas = [etapas[e] for e in marco["stages"] if e in etapas]
    etapa_do_marco = max(enumeradas, key=lambda e: e["order"]) if enumeradas else None
    chave = chave_do_cenario if chave_do_cenario in CENARIOS else "sem_empate"
    candidatos, ancora = cenario(
        chave,
        enumeradas=enumeradas,
        etapa_do_marco=etapa_do_marco,
        alvo=alvo,
        suplentes=suplentes,
        vagas=vagas,
        corta=bool(regra),
    )
    inscritos = [
        {
            "inscricao_id": f"F{c['slot']:03d}",
            "nome": c["nome"],
            "modalidade_id": None,
            "fatos": c["fatos"],
            "resultados": [
                {"etapa_id": e, "pontuacao": nota, "consequencia": _consequencia(c, e)}
                for e, nota in c["notas"].items()
                if nota is not None
            ]
            + [
                {"etapa_id": e, "pontuacao": None, "consequencia": _consequencia(c, e)}
                for e in c["portas"]
            ],
        }
        for c in candidatos
    ]
    etapas_do_motor = {
        e["id"]: {**e, "weight": e["weight"] if e["weight"] not in ("", None) else None}
        for e in etapas_publicadas
    }
    try:
        classificaveis, sem_posicao = preparar_universo(marco, etapas_do_motor, inscritos)
    except combinacao.RegraIncompleta as erro:
        raise Incompleto([str(erro)]) from erro

    criterios = marco.get("tiebreakers") or []
    precisa_de_valor_ausente = [
        c for c in criterios if not c.get("whenMissing") and _alguem_sem_valor(c, classificaveis)
    ]
    if precisa_de_valor_ausente:
        raise Incompleto(
            [
                f"O {c['order']}º critério não declara o que fazer quando o valor não existe, e "
                "neste cenário alguém não o tem. A prévia não presume nenhuma das duas."
                for c in precisa_de_valor_ausente
            ]
        )
    ordem = ordenar_com_trajetoria(classificaveis, criterios)
    conferida = conferir_com_o_motor(ordem, classificaveis, criterios)

    corte = _corte(regra, ordem, sem_posicao, alvo=alvo, suplentes=suplentes)
    vagas_aviso = _fronteira_das_vagas(corte, ordem, vagas)
    return {
        "cenario": chave,
        "ancora": ancora,
        "ordem": ordem,
        "sem_posicao": sem_posicao,
        "conferida": conferida,
        "regra": regra,
        "alvo": alvo,
        "suplentes": suplentes,
        "origem_do_alvo": origem_do_alvo,
        "corte": corte,
        "vagas": vagas,
        "aviso_das_vagas": vagas_aviso,
        "etapas": etapas,
        "criterios": sorted(criterios, key=lambda c: c.get("order") or 0),
    }


def _consequencia(candidato, etapa_id):
    return ELIMINADA if candidato["eliminado_em"] == etapa_id else HABILITADA


def _alguem_sem_valor(criterio, participantes):
    return any(desempate._valor_do_criterio(criterio, p) is None for p in participantes)


def _corte(regra, ordem, sem_posicao, *, alvo, suplentes):
    if not regra:
        return {"declarado": False, "progrediram": [i["inscricao_id"] for i in ordem]}
    posicoes = [(i["inscricao_id"], i["posicao"]) for i in ordem] + [
        (i["inscricao_id"], None) for i in sem_posicao
    ]
    desfecho = regra.get("tieOutcome") or None

    def rodar(com):
        try:
            progrediram, excedentes, _, ultima = faixa.calcular(
                posicoes, alvo=alvo, excedente=suplentes, desfecho=com
            )
        except faixa.EmpateAtravessaOCorte as erro:
            return {"recusado": True, "posicao": erro.posicao, "quantas": erro.quantas}
        return {
            "recusado": False,
            "progrediram": progrediram,
            "excedentes": excedentes,
            "ultima": ultima,
        }

    if desfecho in faixa.DESFECHOS_DE_EMPATE:
        principal = rodar(desfecho)
        outro = (
            faixa.EMPATE_ESTRITO
            if desfecho == faixa.EMPATE_ADMITE_EXCEDENTE
            else faixa.EMPATE_ADMITE_EXCEDENTE
        )
        alternativo = rodar(outro)
        atravessa = principal["recusado"] or bool(principal.get("excedentes"))
        return {
            "declarado": True,
            "desfecho": desfecho,
            **principal,
            "atravessa": atravessa,
            "alternativo": {**alternativo, "desfecho": outro} if atravessa else None,
        }
    # Sem desfecho declarado: as duas consequências, e nenhuma escolhida (FR-2216).
    admite = rodar(faixa.EMPATE_ADMITE_EXCEDENTE)
    estrito = rodar(faixa.EMPATE_ESTRITO)
    atravessa = estrito["recusado"]
    return {
        "declarado": True,
        "desfecho": None,
        "recusado": False,
        "sem_desfecho": True,
        "atravessa": atravessa,
        "progrediram": admite["progrediram"] if not atravessa else [],
        "excedentes": [],
        "comparacao": {"admite": admite, "estrito": estrito} if atravessa else None,
    }


def _fronteira_das_vagas(corte, ordem, vagas):
    if vagas is None:
        return {"avaliado": False, "motivo": "o Perfil não tem quadro de vagas com linha geral."}
    if corte.get("recusado") or (corte.get("sem_desfecho") and corte.get("atravessa")):
        return {"avaliado": False, "motivo": "o corte não sairia, e não há quem apurar."}
    progrediram = corte["progrediram"]
    empates = {i["inscricao_id"]: i["posicao"] for i in ordem if i["empate_residual"]}
    try:
        apuracao.titulares_iniciais(
            progrediram_em_ordem=progrediram, efetivas=vagas, empates_residuais=empates
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return {"avaliado": True, "para": True, "posicao": erro.posicao, "quantas": erro.quantas}
    return {"avaliado": True, "para": False}
