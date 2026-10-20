"""A apresentação da prévia da classificação: o que o painel diz, a partir do que o motor calculou.

Nada aqui calcula classificação, corte nem apuração. `simular` (classificacao) já fez isso com o
motor oficial; este módulo lê o resultado e o põe em frases e linhas, no vocabulário de D-012 e
D-016 da `094`: "avança", "não avança nesta faixa", "poderiam participar", "posições adicionais
(suplentes)".

**A ordem do painel é a da terceira rodada.** A visão principal é a jornada do Perfil, com o marco
simulado aberto; o detalhe — manchete, fluxo, apuração das vagas como hipótese, fronteira, empates
lado a lado, classificação completa e explicação técnica — fica a um clique (FR-2247, FR-2252).

**A fronteira das vagas é injetada aqui.** `classificacao` não importa `ocupacao`, e quem pode
importar os dois é a interface: `apurar_vagas` é a verificação que `simular` recebe.
"""

from django.urls import reverse

from processo_seletivo.classificacao.application import previa as calculo
from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.classificacao.domain import jornada as jornada_do_perfil
from processo_seletivo.classificacao.domain.desempate import _valor_do_criterio
from processo_seletivo.ocupacao.domain import apuracao

C = calculo

CONSEQUENCIA = {
    C.AVANCA: ("avanca", "Avança"),
    C.PELO_EMPATE: ("pelo-empate", "Avança pelo empate"),
    C.NAO_AVANCA: ("nao-avanca", "Não avança"),
    C.AGUARDA: ("aguarda", "Aguarda desempate"),
    C.SEM_POSICAO: ("sem-posicao", "Sem posição"),
    C.SEGUE: ("segue", "Segue — sem corte"),
}
PLURAL = {
    C.AVANCA: "avançam",
    C.PELO_EMPATE: "avançam pelo empate",
    C.NAO_AVANCA: "não avançam",
    C.AGUARDA: "aguardam o desempate",
    C.SEM_POSICAO: "sem posição",
    C.SEGUE: "seguem, sem corte",
}
#: Num marco que não alimenta Etapa não há para onde avançar: o que ele diz é dentro ou fora da
#: faixa (D-016).
TERMINAL = {
    C.AVANCA: "Na faixa",
    C.PELO_EMPATE: "Na faixa pelo empate",
    C.NAO_AVANCA: "Fora da faixa",
}
DESFECHO = {"ADMITS_SURPLUS": "“Todos os empatados progridem”", "STRICT": "“A faixa para no alvo”"}


def apurar_vagas(progrediram, vagas, empates):
    """A apuração das vagas, só a parte que a prévia antecipa: pararia? (D-006)"""
    try:
        apuracao.titulares_iniciais(
            progrediram_em_ordem=progrediram, efetivas=vagas, empates_residuais=empates
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return erro.posicao, erro.quantas
    return None


# --- Formatação ---------------------------------------------------------------------------------


def numero(valor, escala=2):
    if valor is None:
        return "—"
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, int):
        return str(valor)
    texto = f"{valor:,.{escala}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _lista(nomes):
    nomes = list(nomes)
    if len(nomes) <= 1:
        return "".join(nomes)
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def _terminal(p):
    return (p["regra"] or {}).get("governedStage") == "NONE"


def _marca(codigo, p):
    classe, rotulo = CONSEQUENCIA[codigo]
    if _terminal(p):
        rotulo = TERMINAL.get(codigo, rotulo)
    return {"classe": classe, "rotulo": rotulo}


def _contagens(p):
    codigos = list(p["consequencias"].values())
    return {
        "total": p["total"],
        "com_posicao": len(p["ordem"]),
        "sem_posicao": len(p["sem_posicao"]),
        "avancam": sum(1 for c in codigos if c in (C.AVANCA, C.PELO_EMPATE, C.SEGUE)),
        "nao_avancam": sum(1 for c in codigos if c == C.NAO_AVANCA),
        # Quantos entraram **além da faixa** — o número que o corte registra (FR-196 da `014`), e
        # não o tamanho do grupo empatado.
        "alem_da_faixa": len(p["corte"].get("excedentes") or []),
        "empates": len(_grupos(p, so_residuais=True)),
    }


def _etapa_seguinte(p):
    governada = (p["regra"] or {}).get("governedStage")
    if governada == "NONE":
        return None, "Nenhuma Etapa"
    nome = (p["etapas"].get(governada) or {}).get("name")
    return nome, nome or "Etapa seguinte não declarada"


def _criterio(criterio, p):
    parametros = criterio.get("parameters") or {}
    alvo = str(parametros.get("stageId") or parametros.get("factId") or "")
    nome = (p["etapas"].get(alvo) or {}).get("name") or p["fatos_por_id"].get(alvo) or alvo
    tipo = {
        "MAIOR_PONTUACAO_NA_ETAPA": f"maior nota na {nome}",
        "MAIOR_VALOR_DE_FATO": f"maior {nome.lower()}",
        "MENOR_VALOR_DE_FATO": f"menor {nome.lower()}",
    }.get(criterio.get("type"), criterio.get("type"))
    return f"{criterio.get('order')}º · {tipo}"


# --- A manchete, o fluxo e a ocupação ----------------------------------------------------------


def manchete(p):
    n = _contagens(p)
    corte = p["corte"]
    nome, _ = _etapa_seguinte(p)
    if not corte["declarado"]:
        return {
            "estado": "emitivel",
            "forte": "Este marco não corta:",
            "resto": f"os {n['com_posicao']} classificados seguem, e {n['sem_posicao']} ficam "
            "sem posição.",
            "anuncio": f"Sem corte: {n['com_posicao']} classificados seguem.",
        }
    if corte.get("recusado"):
        return {
            "estado": "impedido",
            "forte": "O corte não seria emitido.",
            "resto": f"{corte['quantas']} candidatos empatam na {corte['posicao']}ª posição, a "
            "última da faixa, e o desfecho declarado não deixa todos entrarem. Ninguém avança até "
            "o desempate ser julgado ou o desfecho ser retificado.",
            "anuncio": f"Corte impedido: empate na {corte['posicao']}ª posição.",
        }
    if corte.get("sem_desfecho") and corte.get("atravessa"):
        estrito = corte["comparacao"]["estrito"]
        return {
            "estado": "impedido",
            "forte": "Falta declarar o desfecho do empate.",
            "resto": f"Há empate na {estrito['posicao']}ª posição, a última da faixa, e o "
            "resultado depende dele.",
            "anuncio": "Desfecho do empate não declarado.",
        }
    destino = f"para a {nome}" if nome else "na faixa"
    alem = (
        f", {n['alem_da_faixa']} além da faixa pelo empate na {corte['ultima']}ª"
        if n["alem_da_faixa"]
        else ""
    )
    sem = f"; {n['sem_posicao']} ficam sem posição." if n["sem_posicao"] else "."
    return {
        "estado": "emitivel",
        # A pontuação fecha dentro do negrito: o modelo junta as duas partes com um espaço, e o
        # resto que começava por vírgula ou ponto saía "Entrevista , 1 além".
        "forte": f"{n['avancam']} de {n['total']} candidatos avançam {destino}{alem}.",
        "resto": f"{n['nao_avancam']} não avançam{sem}",
        "anuncio": f"{n['avancam']} de {n['total']} avançam.",
    }


def fluxo(p):
    n = _contagens(p)
    corte = p["corte"]
    regra = p["regra"] or {}
    nome, rotulo = _etapa_seguinte(p)
    plural = "s" if n["empates"] > 1 else ""
    passos = [
        {
            "nome": "Classificação",
            "classe": "",
            "valor": f"{n['com_posicao']} com posição",
            "linhas": [
                f"{n['sem_posicao']} sem posição · "
                + (
                    f"{n['empates']} empate{plural} não resolvido{plural}"
                    if n["empates"]
                    else "nenhum empate não resolvido"
                )
            ],
        }
    ]
    if not corte["declarado"]:
        passos.append(
            {
                "nome": "Corte",
                "classe": "passo-neutro",
                "valor": "Não corta",
                "linhas": ["ninguém é excluído por este marco"],
            }
        )
        passos.append(
            {
                "nome": "Depois",
                "classe": "",
                "valor": f"{n['com_posicao']} seguem",
                "linhas": ["na ordem acima"],
            }
        )
        return {"passos": passos, "ramo": ""}
    alvo, suplentes = p["alvo"], p["suplentes"]
    tamanho = f"faixa de {alvo + suplentes} = alvo {alvo}" + (
        f" + {suplentes} suplentes" if suplentes else ""
    )
    if corte.get("recusado"):
        classe, valor, detalhe = "passo-impedido", "Impedido", f"empate na {corte['posicao']}ª"
    elif corte.get("sem_desfecho") and corte.get("atravessa"):
        classe, valor, detalhe = "passo-impedido", "Depende do desfecho", "não declarado"
    else:
        classe, valor = "passo-emitivel", "Pode ser emitido"
        detalhe = (
            f"+{n['alem_da_faixa']} além da faixa, pelo empate na {corte['ultima']}ª"
            if n["alem_da_faixa"]
            else "nenhum empate na última posição"
        )
        if alvo + suplentes >= n["com_posicao"]:
            # Na população estável a faixa pode passar do total depois de uma mudança: dizer isso
            # evita ler "todos avançam" como efeito da regra, e não da amostra (FR-2246).
            detalhe = f"a faixa passa dos {n['com_posicao']} classificados: todos cabem"
            if p["modo"] == C.ESTAVEL:
                detalhe += " — remonte a população para ver a fronteira"
    passos.append({"nome": "Corte", "classe": classe, "valor": valor, "linhas": [tamanho, detalhe]})
    if calculo.impedido(corte):
        quantos, sub = "Ninguém, por enquanto", "até o desempate ou a Retificação"
    elif nome is None and regra.get("governedStage") == "NONE":
        quantos, sub = f"{n['avancam']} na faixa", "o corte não alimenta Etapa"
    else:
        quantos, sub = f"{n['avancam']} participam", "os que avançam no corte"
    passos.append({"nome": rotulo, "classe": "", "valor": quantos, "linhas": [sub]})
    ramo = ""
    if not calculo.impedido(corte) and n["nao_avancam"] and not _terminal(p):
        texto = {
            "ALLOWED": "o Edital admite faixa seguinte: um novo corte, emitido depois, pode "
            "alcançá-los.",
            "NONE": "o Edital não admite faixa seguinte: a participação deles termina aqui.",
        }.get(regra.get("continuation"), "a continuação não foi declarada.")
        ramo = f"Os {n['nao_avancam']} que não avançam: {texto}"
    return {"passos": passos, "ramo": ramo}


def ocupacao(p):
    """A apuração das vagas — separada do corte, e sempre como hipótese (D-006, D-013)."""
    aviso, vagas = p["aviso_das_vagas"], p["vagas"]
    if not aviso["avaliado"]:
        return {"estado": "neutro", "forte": "Não avaliada:", "texto": aviso["motivo"]}
    if aviso["para"]:
        return {
            "estado": "aviso",
            "forte": f"Pararia na {aviso['posicao']}ª posição.",
            "texto": f"{aviso['quantas']} empatados disputam a última das {vagas} vagas do "
            "quadro, e a apuração não escolhe entre eles — qualquer que seja o desfecho "
            "declarado para o corte. Nenhum campo deste cartão trata disso.",
        }
    return {
        "estado": "ok",
        "forte": "Seria possível:",
        "texto": f"nenhum empate atravessa a última das {vagas} vagas.",
    }


def o_que_mudou(diff, p, onde):
    if diff is None:
        return None
    if not diff["mudancas"] and not diff["mudaram"]:
        return {"nada": True, "itens": []}
    nomes = {i["inscricao_id"]: i["nome"] for i in p["ordem"] + p["sem_posicao"]}
    quem = sorted(nomes[i] for i in diff["mudaram"] if i in nomes)
    itens = list(diff["mudancas"])
    if len(quem) > 5:
        itens.append(f"{len(quem)} candidatos mudaram de situação ({onde}).")
    elif quem:
        itens.append(f"Mudaram de situação: {_lista(quem)} ({onde}).")
    return {"nada": False, "itens": itens}


# --- A fronteira -------------------------------------------------------------------------------


def _limites(p):
    """`[(quantos, rótulo)]` — onde a tabela traça uma linha: alvo, fim da faixa, última vaga.

    O artigo vai em cada rótulo, e não no "Linha" que os junta: "Linha do última vaga" saiu assim
    enquanto ele morava lá.
    """
    limites = {}
    if p["corte"]["declarado"]:
        alvo, suplentes = p["alvo"], p["suplentes"]
        limites.setdefault(alvo, []).append(f"do alvo ({alvo})")
        if suplentes:
            limites.setdefault(alvo + suplentes, []).append(
                f"do fim da faixa ({alvo} + {suplentes} suplentes)"
            )
    if p["vagas"]:
        limites.setdefault(p["vagas"], []).append(f"da última vaga ({p['vagas']})")
    return sorted((k, " · ".join(v)) for k, v in limites.items() if k)


def _grupos(p, *, so_residuais=False):
    por_id = {i["inscricao_id"]: i for i in p["ordem"]}
    vistos, grupos = set(), []
    for item in p["ordem"]:
        if so_residuais:
            grupo = [i for i in p["ordem"] if i["posicao"] == item["posicao"]]
        else:
            grupo = [por_id[i["inscricao_id"]] for i in item["grupo_da_pontuacao"]]
        chave = tuple(sorted(i["inscricao_id"] for i in grupo))
        if len(grupo) > 1 and chave not in vistos:
            vistos.add(chave)
            grupos.append(grupo)
    return grupos


def _posicao(item, p):
    juntos = sum(1 for o in p["ordem"] if o["posicao"] == item["posicao"])
    return {"numero": f"{item['posicao']}ª", "dividida": juntos if juntos > 1 else 0}


def _motivo_curto(item):
    motivo = item.get("motivo") or ""
    if item.get("consequencia") == "ELIMINADA":
        return "eliminado na Etapa do marco"
    if motivo.startswith("Sem pontuação nas Etapas enumeradas:"):
        return "sem nota em " + motivo.split(":", 1)[1].strip().rstrip(".")
    return motivo


def fronteira(p, mudaram):
    """Só quem ajuda a entender: perto de cada limite, nos empates, e quem mudou (R-011)."""
    ordem = p["ordem"]
    limites = _limites(p)
    relevantes = set()
    for quantos, _ in limites:
        relevantes.update(range(max(quantos - 2, 0), min(quantos + 2, len(ordem))))
    for indice, item in enumerate(ordem):
        if len(item["grupo_da_pontuacao"]) > 1 or item["inscricao_id"] in mudaram:
            relevantes.add(indice)
    if not limites:
        relevantes.update(range(min(5, len(ordem))))
    linhas, pulados = [], []

    def fechar():
        if not pulados:
            return
        codigo = p["consequencias"][pulados[0]["inscricao_id"]]
        if len(pulados) == 1:
            intervalo = f"{pulados[0]['posicao']}ª: 1 candidato"
            rotulo = _marca(codigo, p)["rotulo"].lower()
        else:
            intervalo = (
                f"{pulados[0]['posicao']}ª a {pulados[-1]['posicao']}ª: {len(pulados)} candidatos"
            )
            rotulo = PLURAL[codigo]
        linhas.append({"tipo": "agrupada", "texto": f"{intervalo} sem empate — {rotulo}"})
        pulados.clear()

    por_limite = dict(limites)
    for indice, item in enumerate(ordem):
        codigo = p["consequencias"][item["inscricao_id"]]
        if indice not in relevantes:
            if pulados and p["consequencias"][pulados[-1]["inscricao_id"]] != codigo:
                fechar()
            pulados.append(item)
        else:
            fechar()
            linhas.append(
                {
                    "tipo": "linha",
                    "posicao": _posicao(item, p),
                    "nome": item["nome"],
                    "etiqueta": (
                        "empate não resolvido"
                        if item["empate_residual"]
                        else "desempatado"
                        if len(item["grupo_da_pontuacao"]) > 1
                        else ""
                    ),
                    "pontuacao": numero(item["pontuacao"], p["escala"]),
                    "marca": _marca(codigo, p),
                    "mudou": item["inscricao_id"] in mudaram,
                }
            )
        if indice + 1 in por_limite:
            fechar()
            proximo = ordem[indice + 1] if indice + 1 < len(ordem) else None
            atravessa = proximo is not None and proximo["posicao"] == item["posicao"]
            linhas.append(
                {
                    "tipo": "limite",
                    "texto": f"Linha {por_limite[indice + 1]}"
                    + (
                        f" — o empate da {item['posicao']}ª atravessa esta linha"
                        if atravessa
                        else ""
                    ),
                }
            )
    fechar()
    for item in p["sem_posicao"]:
        linhas.append(
            {
                "tipo": "sem-posicao",
                "nome": item["nome"],
                "etiqueta": _motivo_curto(item),
                "marca": _marca(C.SEM_POSICAO, p),
                "mudou": item["inscricao_id"] in mudaram,
            }
        )
    return linhas


# --- Os empates, lado a lado -------------------------------------------------------------------


def _efeito(criterio, membros, p):
    """O que este critério fez **com este grupo**, lido da trajetória do motor (D-011, D-014)."""
    por_id = {i["inscricao_id"]: i for i in p["ordem"]}
    passos = [
        (passo, sub)
        for item in membros
        for passo, c, sub in item["trajetoria"]
        if c is criterio or c == criterio
    ]
    if not passos:
        return "nao-usado", "Não chegou a ser usado: o grupo já estava separado"
    separou = [sub for passo, sub in passos if passo == "separou"]
    if separou:
        sub = sorted(
            (por_id[i["inscricao_id"]] for i in max(separou, key=len)),
            key=lambda i: i["posicao"],
        )
        blocos, atual = [], [sub[0]]
        for anterior, item in zip(sub, sub[1:], strict=False):
            if _valor_do_criterio(criterio, item) == _valor_do_criterio(criterio, anterior):
                atual.append(item)
            else:
                blocos.append(atual)
                atual = [item]
        blocos.append(atual)
        return "separou", "Separou: " + " › ".join(
            " = ".join(i["nome"] for i in bloco) for bloco in blocos
        )
    _, sub = passos[0]
    valores = [_valor_do_criterio(criterio, i) for i in sub]
    if None in valores and criterio.get("whenMissing") == "CRITERIO_NAO_SE_APLICA":
        faltam = _lista(i["nome"] for i in sub if _valor_do_criterio(criterio, i) is None)
        return "nao-separou", f"Não se aplica: falta o valor de {faltam}"
    if all(v is None for v in valores):
        return "nao-separou", "Ninguém no grupo tem o valor"
    return "nao-separou", "Não separou: valores iguais"


def _por_que_importa(membros, p):
    """Que linha este empate atravessa, e o que isso causa."""
    antes = sum(1 for o in p["ordem"] if o["posicao"] < membros[0]["posicao"])
    juntos, corte = len(membros), p["corte"]
    linhas = []
    if corte["declarado"]:
        linhas.append(("alvo", p["alvo"]))
        if p["suplentes"]:
            linhas.append(("faixa", p["alvo"] + p["suplentes"]))
    if p["vagas"]:
        linhas.append(("vagas", p["vagas"]))
    frases = []
    for tipo, k in linhas:
        if not antes < k < antes + juntos:
            continue
        if tipo == "vagas":
            frases.append(
                f"Atravessa a última das {k} vagas: é ele que pararia a apuração das vagas."
            )
        elif tipo == "faixa" or (tipo == "alvo" and not p["suplentes"]):
            if calculo.impedido(corte):
                frases.append(
                    f"Atravessa a última posição da faixa ({k}): é ele que impede o corte."
                )
            else:
                verbo = "ficarem na faixa" if _terminal(p) else "avançarem"
                frases.append(
                    f"Atravessa a última posição da faixa ({k}): o desfecho declarado faz todos "
                    f"{verbo}."
                )
        else:
            frases.append(f"Atravessa a linha do alvo ({k}), dentro da faixa: não muda o corte.")
    if not frases:
        return "Não atravessa nenhuma linha: o empate não muda a consequência de ninguém."
    return " ".join(frases)


def empates(p):
    blocos = []
    for grupo in _grupos(p):
        membros = sorted(grupo, key=lambda i: (i["posicao"], i["inscricao_id"]))
        posicoes = {i["posicao"] for i in membros}
        if len(posicoes) == 1:
            forte = f"Dividem a {membros[0]['posicao']}ª posição:"
            resultado = "nenhum critério declarado os separa, e o sistema não escolhe entre eles."
            importa = _por_que_importa(membros, p)
        else:
            forte = "Separados:" if len(posicoes) == len(membros) else "Separados em parte:"
            resultado = ", ".join(f"{i['nome']} {i['posicao']}ª" for i in membros)
            importa = ""
        linhas = [
            {
                "criterio": "Pontuação combinada",
                "valores": [numero(i["pontuacao"], p["escala"]) for i in membros],
                "efeito": "Iguais: empate",
                "classe": "base",
            }
        ]
        for criterio in p["criterios"]:
            classe, efeito = _efeito(criterio, membros, p)
            linhas.append(
                {
                    "criterio": _criterio(criterio, p),
                    "valores": [numero(_valor_do_criterio(criterio, i)) for i in membros],
                    "efeito": efeito,
                    "classe": f"efeito-{classe}",
                }
            )
        blocos.append(
            {
                "titulo": _lista(i["nome"] for i in membros),
                "forte": forte,
                "resultado": resultado,
                "importa": importa,
                "nomes": [i["nome"] for i in membros],
                "linhas": linhas,
                "sem_criterios": not p["criterios"],
            }
        )
    return blocos


# --- A classificação completa e a explicação ---------------------------------------------------


def completa(p, mudaram):
    notas = [e for e in p["etapas_do_marco"] if e.get("forma") != cenarios.DECISORIA]
    fatos_usados = [
        fato
        for fato in p["fatos"]
        if any(
            str((c.get("parameters") or {}).get("factId")) == str(fato["id"])
            for c in p["criterios"]
        )
    ]
    cabeca = [
        "Posição",
        "Candidato",
        *(e["name"] for e in notas),
        "Pontuação",
        *(f["label"] for f in fatos_usados),
        "Por quê",
        "Consequência",
    ]
    linhas = []
    for item in p["ordem"]:
        if item["empate_residual"]:
            motivo = "empate não resolvido"
        elif item["separado_por"] is not None:
            motivo = f"desempate pelo {item['separado_por'].get('order')}º critério"
        else:
            motivo = "pontuação"
        valores = [
            f"{item['posicao']}ª",
            item["nome"],
            *(numero(item["pontuacoes"].get(e["id"]), p["escala"]) for e in notas),
            numero(item["pontuacao"], p["escala"]),
            *(numero(item["fatos"].get(str(f["id"]))) for f in fatos_usados),
            motivo,
        ]
        linhas.append(
            {
                "celulas": list(zip(cabeca[:-1], valores, strict=True)),
                "marca": _marca(p["consequencias"][item["inscricao_id"]], p),
                "mudou": item["inscricao_id"] in mudaram,
            }
        )
    for item in p["sem_posicao"]:
        valores = [
            "—",
            item["nome"],
            *(numero(item["pontuacoes"].get(e["id"]), p["escala"]) for e in notas),
            "—",
            *("—" for _ in fatos_usados),
            _motivo_curto(item),
        ]
        linhas.append(
            {
                "celulas": list(zip(cabeca[:-1], valores, strict=True)),
                "marca": _marca(C.SEM_POSICAO, p),
                "mudou": item["inscricao_id"] in mudaram,
            }
        )
    return {"cabeca": cabeca, "linhas": linhas}


def como_calcula(p):
    corte = p["corte"]
    itens = [
        "As posições seguem a numeração do sistema: empatados dividem a posição, e a seguinte é "
        "pulada (10ª, 10ª, 12ª).",
        "Quem não tem nota numa Etapa enumerada fica sem posição: ausência não vira zero.",
    ]
    if corte["declarado"]:
        itens.append(
            f"O desfecho do empate declarado é {DESFECHO.get(corte.get('desfecho'), 'nenhum')}. "
            "A prévia mostra o comportamento atual do sistema: com “A faixa para no alvo”, um "
            "empate na última posição da faixa — alvo mais suplentes, e não só o alvo — impede a "
            "emissão do corte. O rótulo do campo e a frase do Edital sobre este caso estão em "
            "revisão (DP-1 e DP-2 da spec 094), e esta prévia não os substitui."
        )
        alternativo = corte.get("alternativo")
        if alternativo:
            efeito = (
                f"o corte não seria emitido (empate na {alternativo['posicao']}ª)"
                if alternativo.get("recusado")
                else f"{len(alternativo['progrediram'])} avançariam"
            )
            itens.append(f"Com o outro desfecho, {DESFECHO[alternativo['desfecho']]}, {efeito}.")
        if corte.get("sem_desfecho") and corte.get("atravessa"):
            admite = corte["comparacao"]["admite"]
            itens.append(
                "Sem desfecho declarado: com “Todos os empatados progridem”, "
                f"{len(admite['progrediram'])} avançam; com “A faixa para no alvo”, o corte não "
                "seria emitido. Sem a declaração, o Edital não publica."
            )
    itens.append(
        "Calculado pelo motor oficial da classificação, sobre candidatos fictícios. Nada foi "
        "gravado: nem candidatos, nem configuração, nem ato."
    )
    return itens


# --- A jornada ----------------------------------------------------------------------------------

SELO = {
    jornada_do_perfil.SIMULADO: ("simulado", "simulado"),
    jornada_do_perfil.PARCIAL: ("parcial", "quem chega é calculado"),
    jornada_do_perfil.CONTEXTO: ("contexto", "não calculado aqui"),
    jornada_do_perfil.INDETERMINADO: ("indeterminado", "indeterminado"),
}


def _nomes_das_etapas(etapas):
    return _lista(e["name"] for e in etapas)


def _selecionado(p):
    """O marco simulado, aberto: os números grandes e a regra em uma frase."""
    n = _contagens(p)
    corte, regra = p["corte"], p["regra"] or {}
    terminal = _terminal(p)
    aberto = {"impedido": calculo.impedido(corte), "terminal": terminal, "numeros": []}
    if aberto["impedido"]:
        aberto["bloqueio"] = (
            f"Há empate na {corte['posicao']}ª posição, a última da faixa, e a regra não deixa "
            "todos os empatados entrarem: a lista de quem avança não pode ser emitida até o "
            "desempate ser julgado ou a regra ser retificada."
            if corte.get("recusado")
            else "O desfecho do empate não está declarado, e há empate na última posição: o "
            "resultado depende dele."
        )
    else:
        if not corte["declarado"]:
            dentro, fora = "Seguem — o marco não corta", "Excluídos por este marco"
        elif terminal:
            dentro, fora = "Ficariam dentro da faixa", "Ficariam fora da faixa"
        else:
            dentro, fora = "Avançariam", "Não avançariam nesta faixa"
        aberto["numeros"] = [
            {"valor": n["avancam"], "rotulo": dentro, "classe": "numero-dentro"},
            {"valor": n["nao_avancam"], "rotulo": fora, "classe": ""},
        ]
        if n["sem_posicao"]:
            aberto["numeros"].append(
                {"valor": n["sem_posicao"], "rotulo": "Sem posição", "classe": "numero-fraco"}
            )
    if corte["declarado"]:
        partes = [
            f"alvo de {p['alvo']}"
            + (" (as vagas do quadro)" if regra.get("targetKind") == "FROM_VACANCY_TABLE" else "")
        ]
        if p["suplentes"]:
            partes.append(f"{p['suplentes']} posições adicionais (suplentes)")
        desfecho = {
            "ADMITS_SURPLUS": "com empate na última posição, todos os empatados "
            + ("ficam na faixa" if terminal else "avançam"),
            "STRICT": "com empate na última posição, a lista não sai até o desempate",
        }.get(regra.get("tieOutcome"), "o desfecho do empate não está declarado")
        aberto["regra"] = f"{' + '.join(partes)}; {desfecho}."
    else:
        aberto["regra"] = ""
    aviso = p["aviso_das_vagas"]
    aberto["aviso_das_vagas"] = (
        # Condicional, como a D-006 manda: a apuração é pedida por marco, e o intermediário pode
        # não ser o que ela usa. Sem o "se", o cartão afirmava um efeito que talvez não exista.
        f"Atenção às vagas: se forem apuradas sobre este marco, um empate na "
        f"{aviso['posicao']}ª pararia a apuração das {p['vagas']} vagas (hipótese; veja o detalhe)."
        if aviso.get("para")
        else ""
    )
    aberto["ramo"] = ""
    if corte["declarado"] and not aberto["impedido"] and n["nao_avancam"] and not terminal:
        texto = {
            "ALLOWED": "uma faixa seguinte, emitida depois, pode alcançá-los",
            "NONE": "o Edital não admite faixa seguinte, e a participação deles termina aqui",
        }.get(regra.get("continuation"), "a continuação não foi declarada")
        aberto["ramo"] = f"Os {n['nao_avancam']} que não avançam: {texto}."
    return aberto


def jornada(p, marcos, sub, url_do_marco):
    """Os pontos da jornada, prontos para a tela: título, selo, frases e os números do simulado."""
    sel = next(m for m in marcos if m["sub"] == sub)
    pontos = jornada_do_perfil.jornada(list(p["etapas"].values()), marcos, sub)
    total, passo = p["total"], 0
    saida = []
    for ponto in pontos:
        classe_selo, rotulo_selo = SELO[ponto["estado"]]
        item = {"selo": {"classe": classe_selo, "rotulo": rotulo_selo}, "frases": []}
        tipo = ponto["tipo"]
        if tipo != "marco":
            passo += 1
        if tipo == "avaliacoes":
            item.update(
                classe="ponto-etapa",
                titulo=f"{passo}. " + " + ".join(e["name"] for e in ponto["etapas"]),
            )
            item["frases"].append(
                f"{total} candidatos fictícios, com notas fictícias "
                + ("nesta Etapa" if len(ponto["etapas"]) == 1 else "nestas Etapas")
                + f", considerados na {sel['name']}."
                if ponto["usadas_no_selecionado"]
                else "Não entram no marco simulado."
            )
        elif tipo == "porta":
            item.update(
                classe="ponto-etapa ponto-porta", titulo=f"{passo}. {ponto['etapa']['name']}"
            )
            item["frases"].append(
                f"Etapa decisória: só quem for habilitado nela faz a {ponto['governada']['name']}. "
                "A prévia não simula quantos seriam eliminados aqui."
                if ponto["antes_da_governada"]
                else "Etapa decisória: habilita ou elimina, e não entra em classificação."
            )
        elif tipo == "fora":
            item.update(classe="ponto-etapa", titulo=f"{passo}. {ponto['etapa']['name']}")
            item["frases"].append("Não entra em classificação nenhuma deste Perfil.")
        elif tipo == "etapa_alimentada":
            etapa, por = ponto["etapa"], ponto["por"]
            item.update(classe="ponto-etapa", titulo=f"{passo}. {etapa['name']}")
            if ponto["do_selecionado"]:
                if calculo.impedido(p["corte"]):
                    item["destaque"] = "Ninguém, por enquanto."
                    item["frases"].append("A lista de quem avança não pode ser emitida.")
                else:
                    ate = "Até " if ponto["portas_antes"] else ""
                    item["destaque"] = (
                        f"{ate}{_contagens(p)['avancam']} candidatos poderiam participar"
                    )
                    if ponto["portas_antes"]:
                        item["frases"].append(
                            "Menos, se alguém for eliminado em "
                            f"{_nomes_das_etapas(ponto['portas_antes'])}."
                        )
                    item["frases"].append(f"As notas da {etapa['name']} não são simuladas aqui.")
            elif ponto["usada_no_selecionado"]:
                item["frases"].append(
                    f"Participam os que avançarem na {por['name']}, que esta prévia não simula. "
                    f"Para a {sel['name']}, a prévia dá nota fictícia de {etapa['name']} a todos "
                    f"os {total} — no Edital real, só quem chegar a ela."
                )
            else:
                item["frases"].append(
                    f"Participam os que avançarem na {por['name']}: não simulado nesta prévia."
                )
        else:
            marco = ponto["marco"]
            item.update(classe="ponto-marco", titulo=marco.get("name") or "Marco sem denominação")
            if ponto["estado"] == jornada_do_perfil.SIMULADO:
                item["classe"] = "ponto-marco ponto-selecionado"
                item["aberto"] = _selecionado(p)
            else:
                if ponto["por_sorteio"]:
                    item["frases"].append(
                        "Ordena por sorteio: a prévia não o simula (a fatia 1 cobre só a "
                        "pontuação)."
                    )
                elif ponto["antes_do_selecionado"]:
                    destino = (
                        ponto["governada"]["name"] if ponto["governada"] else "a Etapa seguinte"
                    )
                    item["frases"].append(
                        f"Decide quem chega à {destino}. Não é calculado nesta prévia: a da "
                        f"{sel['name']} supõe que todos chegaram."
                    )
                else:
                    faltam = ponto["nao_simuladas"]
                    item["indeterminado"] = True
                    item["frases"].append(
                        "Depende "
                        + (
                            f"das notas de {_nomes_das_etapas(faltam)}, que não foram simuladas, e "
                            if faltam
                            else ""
                        )
                        + "da regra deste marco."
                    )
                if not ponto["por_sorteio"]:
                    item["simular"] = url_do_marco(marco["sub"])
        saida.append(item)
    return saida


# --- O painel inteiro ---------------------------------------------------------------------------


def candidatos(p, escolha):
    opcoes = [("estavel", "População estável — testar a regra")]
    casos = [(f"caso:{k}", v[0]) for k, v in cenarios.CASOS.items()]
    bloco = {"escolha": escolha, "opcoes": opcoes, "casos": casos}
    if p is None:
        return bloco
    if p["modo"] == C.CASO_LIMITE:
        bloco.update(
            caso=True,
            descricao=cenarios.CASOS[p["caso"]][1],
            onde=p["onde"] or "",
        )
        return bloco
    alvo, faixa, vagas = p["ancoras"]
    bloco.update(
        caso=False,
        total=p["total"],
        montagem=f"Para alvo {alvo}, faixa de {faixa} e {vagas} vagas, com "
        + (_lista(p["plantados"]) if p["plantados"] else "nenhum empate plantado")
        + ", mais uma candidata sem nota e um candidato eliminado.",
        populacao=f"{alvo}:{faixa}:{vagas}",
        remontar=tuple(p["fronteiras"]) != tuple(p["ancoras"]),
    )
    return bloco


def escolha_de_candidatos(dados):
    escolha = (dados.get("candidatos") or "estavel").strip()
    if escolha.startswith("caso:") and escolha[5:] in cenarios.CASOS:
        return escolha, C.CASO_LIMITE, escolha[5:]
    return "estavel", C.ESTAVEL, ""


def populacao_digitada(dados):
    try:
        alvo, faixa, vagas = (int(n) for n in (dados.get("populacao") or "").split(":"))
    except ValueError:
        return None
    return alvo, faixa, vagas


def contexto(*, perfil, marcos, sub, etapas, fatos, vagas, dados, edital, indice):
    """Tudo o que `_previa_da_classificacao.html` desenha, ou o que falta para desenhar."""
    marco = next(m for m in marcos if m["sub"] == sub)
    escolha, modo, caso = escolha_de_candidatos(dados)
    vista = "detalhe" if dados.get("vista") == "detalhe" else "processo"

    def url_do_marco(outro):
        caminho = reverse("interface:fragmento-previa-da-classificacao", args=[indice, outro])
        return f"{caminho}?edital={edital.id}"

    base = {
        "indice": indice,
        "sub": sub,
        "vista": vista,
        "edital": edital,
        "perfil": {"code": perfil.get("code", ""), "name": perfil.get("name", "")},
        "marco_nome": marco.get("name") or "Marco sem denominação",
        "previa_url": url_do_marco(sub),
        "fechar_url": reverse("interface:fragmento-previa-da-classificacao-fechar"),
    }
    try:
        p = calculo.simular(
            marco,
            etapas,
            fatos,
            vagas=vagas,
            modo=modo,
            caso=caso,
            populacao=populacao_digitada(dados) if modo == C.ESTAVEL else None,
            apurar_vagas=apurar_vagas,
        )
    except calculo.ForaDaFatia:
        return {**base, "fora_da_fatia": True, "anuncio": "A prévia cobre marcos pela pontuação."}
    except calculo.Incompleto as erro:
        return {
            **base,
            "faltas": erro.faltas,
            "candidatos": candidatos(None, escolha),
            "anterior": dados.get("anterior") or "",
            "anuncio": f"Prévia não calculada: falta declarar {len(erro.faltas)}.",
        }
    p["escala"] = (marco.get("rounding") or {}).get("scale") or 0
    p["fatos"] = fatos
    p["fatos_por_id"] = {str(f["id"]): f.get("label") or f.get("code") for f in fatos}
    atual = calculo.estado(p)
    diff = calculo.comparar(dados.get("anterior") or "", atual)
    mudaram = diff["mudaram"] if diff else set()
    cabeca = manchete(p)
    anuncio = cabeca["anuncio"]
    if diff and diff["mudancas"]:
        anuncio += " Mudou: " + " ".join(diff["mudancas"])
    contexto_ = {
        **base,
        "candidatos": candidatos(p, escolha),
        "anterior": atual,
        "anuncio": anuncio,
        "total": p["total"],
    }
    if vista == "processo":
        contexto_.update(
            mudou=o_que_mudou(diff, p, "veja no detalhe"),
            jornada=jornada(p, marcos, sub, url_do_marco),
        )
        return contexto_
    contexto_.update(
        manchete=cabeca,
        mudou=o_que_mudou(diff, p, "marcados na tabela"),
        fluxo=fluxo(p),
        ocupacao=ocupacao(p),
        fronteira=fronteira(p, mudaram),
        empates=empates(p),
        completa=completa(p, mudaram),
        como_calcula=como_calcula(p),
    )
    return contexto_
