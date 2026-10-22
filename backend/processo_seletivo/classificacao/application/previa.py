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

**Os recortes, pela mesma porta** (095). A ampla é o universo inteiro, e cada Modalidade reservada
tem a sua ordem e o seu corte, pela mesma `preparar` com o recorte como parâmetro. A rodada de
ocupação — quem ocupa pela ampla, as quatro quantidades, a reversão — é da `ocupacao`, e chega
injetada em `apurar_recortes`, como a fronteira das vagas.
"""

from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.classificacao.domain import desempate, faixa
from processo_seletivo.classificacao.domain.combinacao import RegraIncompleta
from processo_seletivo.classificacao.domain.universo_classificavel import preparar

POR_PONTUACAO = "POR_PONTUACAO"

#: Quantas Modalidades reservadas a prévia cobre, além da ampla (095, R-006, FR-2343).
RESERVADAS_COBERTAS = 6
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
    recortes=None,
    apurar_recortes=None,
):
    """Tudo o que o painel mostra do marco `marco`, ou `Incompleto` com o que falta.

    `etapas_publicadas` são as Etapas do conteúdo do rascunho; `fatos`, os fatos declarados do
    Perfil; `vagas`, a quantidade da linha geral do quadro, ou `None` quando não há. `populacao` é
    `(alvo, faixa, vagas)` com que a população estável foi montada — `None` monta agora.

    `apurar_vagas(progrediram, vagas, empates)` devolve `None`, quando a apuração das vagas seria
    possível, ou `(posicao, quantas)` do empate que a pararia.

    `recortes` é `[{lista_id, rotulo, vagas}]`, a ampla primeiro, na derivação oficial (095,
    FR-2301); `None` é só a ampla. `apurar_recortes(entradas)` é a rodada de ocupação da `ocupacao`,
    e sem ela a prévia não fala de ocupação por recorte.
    """
    if (marco.get("orderProduction") or POR_PONTUACAO) != POR_PONTUACAO:
        raise ForaDaFatia
    etapas = {str(e["id"]): e for e in etapas_publicadas}
    regra = faixa.normalizar(marco.get("cutRule"))
    recortes = list(recortes or [{"lista_id": None, "rotulo": "", "vagas": vagas}])
    reservadas = [r for r in recortes if r["lista_id"] is not None]
    faltas = _faltas(marco, etapas, regra, vagas)
    if len(reservadas) > RESERVADAS_COBERTAS:
        faltas.append(
            f"A prévia cobre até {RESERVADAS_COBERTAS} Modalidades reservadas; este Perfil declara "
            f"{len(reservadas)}."
        )
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
    faixas_reservadas = tuple(
        _faixa_do_recorte(regra, alvo, suplentes, r["vagas"]) for r in reservadas
    )
    fronteiras = (alvo or 0, faixa_total, vagas or 0, *faixas_reservadas)

    enumeradas = [etapas[e] for e in marco.get("stages") or [] if e in etapas]
    etapa_do_marco = _ultima_enumerada(marco, etapas)
    caso_de_reserva = caso in cenarios.CASOS_DE_RESERVA and bool(reservadas)
    if modo == CASO_LIMITE and caso_de_reserva:
        candidatos, _ = cenarios.caso_limite(
            "sem_empate",
            etapas_enumeradas=enumeradas,
            etapa_do_marco=etapa_do_marco,
            fatos=fatos,
            alvo=alvo,
            suplentes=suplentes,
            vagas=vagas,
            corta=bool(regra),
        )
        candidatos, onde = cenarios.caso_de_reserva(
            caso,
            candidatos,
            [(r["lista_id"], r["rotulo"]) for r in reservadas],
            vagas_da_ampla=vagas or alvo,
            faixa_da_ampla=faixa_total,
            vagas={r["lista_id"]: r["vagas"] for r in reservadas},
            faixas=dict(zip((r["lista_id"] for r in reservadas), faixas_reservadas, strict=True)),
        )
        ancoras, plantados = fronteiras, [onde] if onde else []
    elif modo == CASO_LIMITE and caso in cenarios.CASOS:
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
        candidatos, _ = _com_modalidades(candidatos, reservadas, ancoras)
    else:
        modo, caso = ESTAVEL, ""
        # A população da fatia 1 tinha três âncoras; a da fatia 2 leva também a faixa de cada
        # reservada. Uma população montada antes de o Perfil declarar a Modalidade — ou com outra
        # quantidade de reservadas — não tem as âncoras dela, e é montada de novo.
        ancoras = (
            tuple(populacao) if populacao and len(populacao) == len(fronteiras) else fronteiras
        )
        candidatos, plantados = cenarios.populacao_estavel(
            etapas_enumeradas=enumeradas,
            etapa_do_marco=etapa_do_marco,
            fatos=fatos,
            alvo=ancoras[0],
            faixa=ancoras[1],
            vagas=ancoras[2],
        )
        candidatos, plantados_da_reserva = _com_modalidades(candidatos, reservadas, ancoras)
        plantados = plantados + plantados_da_reserva
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
    corte = corte_da_ordem(regra, ordem, sem_posicao, alvo=alvo, suplentes=suplentes)
    inscritos = cenarios.inscritos(candidatos)
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
    previa.update(
        por_recorte(
            marco,
            etapas,
            inscritos,
            recortes,
            criterios=criterios,
            regra=regra,
            alvo=alvo,
            suplentes=suplentes,
            ampla=previa,
            apurar_recortes=apurar_recortes,
        )
    )
    return previa


def _faixa_do_recorte(regra, alvo, suplentes, vagas_do_recorte):
    """A faixa de uma reservada: o alvo fixo vale em todo recorte; o do quadro é a linha dela."""
    if not regra:
        return 0
    if regra["targetKind"] == faixa.ALVO_FIXO:
        return (alvo or 0) + (suplentes or 0)
    return (vagas_do_recorte or 0) + (suplentes or 0)


def _com_modalidades(candidatos, reservadas, ancoras):
    if not reservadas:
        return candidatos, []
    alvo, faixa_da_ampla, vagas = ancoras[:3]
    return cenarios.atribuir_modalidades(
        candidatos,
        [(r["lista_id"], r["rotulo"]) for r in reservadas],
        vagas_da_ampla=vagas or alvo,
        faixa_da_ampla=faixa_da_ampla,
        faixas=dict(zip((r["lista_id"] for r in reservadas), ancoras[3:], strict=False)),
    )


def _recorte(
    marco, etapas, inscritos, *, lista_id, vagas_do_recorte, criterios, regra, alvo, suplentes
):
    """A ordem e o corte de uma reservada — a mesma conta da ampla, sobre o recorte (FR-2303)."""
    classificaveis, sem_posicao = preparar(marco, etapas, inscritos, recorte=lista_id)
    ordem = desempate.ordenar_com_trajetoria(classificaveis, criterios)
    alvo_do_recorte, origem = alvo, "número publicado no marco, o mesmo em todo recorte"
    if regra and regra["targetKind"] == faixa.ALVO_DO_QUADRO:
        alvo_do_recorte, origem = vagas_do_recorte, "linha desta Modalidade no quadro de vagas"
    if regra and alvo_do_recorte is None:
        # Sem linha, o alvo do quadro não é apurável neste recorte — e ausência não vira zero
        # (`recorte_sem_linha_de_quadro`, como no corte oficial).
        corte = {
            "declarado": True,
            "sem_linha": True,
            "recusado": False,
            "progrediram": [],
            "excedentes": [],
        }
    else:
        corte = corte_da_ordem(regra, ordem, sem_posicao, alvo=alvo_do_recorte, suplentes=suplentes)
    return {
        "ordem": ordem,
        "sem_posicao": sem_posicao,
        "corte": corte,
        "alvo": alvo_do_recorte,
        "origem_do_alvo": origem,
        "consequencias": consequencias(ordem, sem_posicao, corte),
    }


def entrada_da_rodada(lista_id, vagas_do_recorte, ordem, sem_posicao, corte):
    """O que a rodada de ocupação lê de um recorte — pública desde a `098`, como o corte."""
    return {
        "lista_id": lista_id,
        "vagas": vagas_do_recorte,
        "impedido": impedido(corte),
        "progrediram": list(corte.get("progrediram") or []),
        "posicoes": [i["posicao"] for i in ordem] + [None for _ in sem_posicao],
        "membros": [i["inscricao_id"] for i in ordem + sem_posicao],
        "empates": {i["inscricao_id"]: i["posicao"] for i in ordem if i["empate_residual"]},
    }


def por_recorte(
    marco,
    etapas,
    inscritos,
    recortes,
    *,
    criterios,
    regra,
    alvo,
    suplentes,
    ampla,
    apurar_recortes=None,
):
    """As reservadas, a rodada de ocupação e os participantes da Etapa seguinte (095).

    `ampla` é o cálculo do recorte sem lista, já feito — com `ordem`, `sem_posicao`, `corte` e
    `vagas`. Pública porque a equivalência com o caminho oficial a chama sobre os mesmos inscritos
    que grava no banco (FR-2340).
    """
    reservadas = []
    entradas = [
        entrada_da_rodada(
            None, ampla["vagas"], ampla["ordem"], ampla["sem_posicao"], ampla["corte"]
        )
    ]
    posicao_na_ampla = {i["inscricao_id"]: i["posicao"] for i in ampla["ordem"]}
    for recorte in recortes:
        if recorte["lista_id"] is None:
            continue
        calculado = _recorte(
            marco,
            etapas,
            inscritos,
            lista_id=recorte["lista_id"],
            vagas_do_recorte=recorte["vagas"],
            criterios=criterios,
            regra=regra,
            alvo=alvo,
            suplentes=suplentes,
        )
        reservadas.append(
            {
                **calculado,
                "lista_id": recorte["lista_id"],
                "rotulo": recorte["rotulo"],
                "vagas": recorte["vagas"],
                "suplentes": suplentes,
                "total": len(calculado["ordem"]) + len(calculado["sem_posicao"]),
            }
        )
        entradas.append(
            entrada_da_rodada(
                recorte["lista_id"],
                recorte["vagas"],
                calculado["ordem"],
                calculado["sem_posicao"],
                calculado["corte"],
            )
        )
    ocupacao = apurar_recortes(entradas) if apurar_recortes else None
    dependentes = [r["rotulo"] for r in reservadas if impedido(r["corte"])]
    if impedido(ampla["corte"]):
        dependentes.insert(0, recortes[0].get("rotulo") or "ampla concorrência")
    uniao = {i for e in entradas if not e["impedido"] for i in e["progrediram"]}
    return {
        "rotulo_da_ampla": recortes[0].get("rotulo") or "",
        "recortes": reservadas,
        "posicao_na_ampla": posicao_na_ampla,
        "ocupacao_por_recorte": ocupacao,
        "participantes": {
            "uniao": len(uniao),
            "so_pela_ampla": len(entradas[0]["progrediram"]) if not entradas[0]["impedido"] else 0,
            "depende_de": dependentes,
        },
    }


def corte_da_ordem(regra, ordem, sem_posicao, *, alvo, suplentes):
    """O corte, com as recusas como resultado (D-005) — e o outro desfecho, como comparação.

    Pública desde a `098`, sem mudar de corpo: a prévia do sorteio corta a ordem sorteada por aqui,
    e um corte próprio lá seria a segunda resposta para a mesma pergunta.
    """
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
    """O corte não seria emitido — recusado, dependente de um desfecho que falta, sem a linha do
    quadro de que o alvo do recorte depende (095), ou sem ordem a cortar (098: o sorteio não sorteia
    lista vazia, e sem ordem o corte oficial recusa por `sem_ato_vigente`)."""
    return bool(
        corte.get("recusado")
        or corte.get("sem_linha")
        or corte.get("sem_ordem")
        or (corte.get("sem_desfecho") and corte.get("atravessa"))
    )


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
    situacao_do_corte = _situacao_do_corte(previa["corte"])
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
    partes = [chave, populacao, situacao_do_corte, vagas, codigos]
    if previa.get("recortes"):
        partes.append(_estado_dos_recortes(previa))
    return "~".join(partes)


def _situacao_do_corte(corte):
    if not corte["declarado"]:
        return "sem-corte"
    if corte.get("recusado"):
        return f"impedido-{corte['posicao']}"
    if corte.get("sem_linha"):
        return "sem-linha"
    if corte.get("sem_desfecho") and corte.get("atravessa"):
        return "sem-desfecho"
    return "emitivel"


def _estado_dos_recortes(previa):
    """Um trecho por recorte — a ampla primeiro: corte, quantos avançam, ocupadas, sem ocupante e
    cedidas. O que a fatia 2 acrescenta ao "o que mudou" (FR-2334)."""
    ocupacao = (previa.get("ocupacao_por_recorte") or {}).get("recortes") or {}
    trechos = []
    for lista_id, calculado in [(None, previa), *((r["lista_id"], r) for r in previa["recortes"])]:
        apurado = ocupacao.get(lista_id) or {}
        quantidades = (
            f"{apurado['ocupadas']}:{apurado['faltando']}:{apurado.get('cederia') or 0}"
            if apurado.get("estado") == "avaliada"
            else f"{apurado.get('estado') or 'nao-avaliada'}::"
        )
        avancam = sum(
            1 for c in calculado["consequencias"].values() if c in (AVANCA, PELO_EMPATE, SEGUE)
        )
        trechos.append(f"{_situacao_do_corte(calculado['corte'])}:{avancam}:{quantidades}")
    trechos.append(str(previa["participantes"]["uniao"]))
    return "|".join(trechos)


_CORTE_LEGIVEL = {
    "emitivel": "emitível",
    "sem-corte": "sem corte",
    "sem-desfecho": "sem desfecho",
    "sem-linha": "não apurável, sem linha no quadro",
}
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


def comparar(anterior, atual, rotulos=()):
    """O que mudou entre dois estados da **mesma** população — ou `None` se não são comparáveis.

    Entre populações ou modos diferentes, a diferença seria dos dados, e não da regra (FR-2244).
    `rotulos` nomeia os recortes, a ampla primeiro, quando o estado os traz (095).
    """
    if not anterior:
        return None
    a_partes, b_partes = anterior.split("~"), atual.split("~")
    if len(a_partes) != len(b_partes) or len(a_partes) not in (5, 6):
        return None
    a_chave, a_pop, a_corte, a_vagas, a_cod = a_partes[:5]
    b_chave, b_pop, b_corte, b_vagas, b_cod = b_partes[:5]
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
    if len(a_partes) == 6:
        mudancas += _mudancas_por_recorte(a_partes[5], b_partes[5], rotulos)
    mudaram = {f"F{i:03d}" for i, (x, y) in enumerate(zip(a_cod, b_cod, strict=True)) if x != y}
    return {"mudancas": mudancas, "mudaram": mudaram}


def _mudancas_por_recorte(anterior, atual, rotulos):
    a_trechos, b_trechos = anterior.split("|"), atual.split("|")
    if len(a_trechos) != len(b_trechos):
        return []
    mudancas = []
    *a_recortes, a_uniao = a_trechos
    *b_recortes, b_uniao = b_trechos
    for indice, (a, b) in enumerate(zip(a_recortes, b_recortes, strict=True)):
        if a == b:
            continue
        nome = rotulos[indice] if indice < len(rotulos) else f"Recorte {indice + 1}"
        a_corte, a_avancam, a_ocu, a_falta, a_cede = a.split(":")
        b_corte, b_avancam, b_ocu, b_falta, b_cede = b.split(":")
        # A ampla já tem as linhas da fatia 1 — corte e avançam —, e não as repete.
        if indice and a_corte != b_corte:
            mudancas.append(f"{nome}: corte {_corte_legivel(a_corte)} → {_corte_legivel(b_corte)}.")
        if indice and a_avancam != b_avancam:
            mudancas.append(f"{nome}: avançam {a_avancam} → {b_avancam}.")
        if (a_ocu, a_falta) != (b_ocu, b_falta):
            antes = f"{a_ocu} ocupadas" if a_falta else "não avaliada"
            depois = f"{b_ocu} ocupadas" if b_falta else "não avaliada"
            if a_falta and b_falta:
                antes += f", {a_falta} sem ocupante"
                depois += f", {b_falta} sem ocupante"
            mudancas.append(f"{nome}: {antes} → {depois}.")
        if a_cede != b_cede and indice:
            mudancas.append(f"{nome}: cederia {a_cede or 0} → {b_cede or 0} à ampla.")
    if a_uniao != b_uniao:
        mudancas.append(f"Poderiam participar da Etapa seguinte: {a_uniao} → {b_uniao}.")
    return mudancas


__all__ = [
    "AGUARDA",
    "RESERVADAS_COBERTAS",
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
    "corte_da_ordem",
    "entrada_da_rodada",
    "estado",
    "impedido",
    "por_recorte",
    "simular",
]
