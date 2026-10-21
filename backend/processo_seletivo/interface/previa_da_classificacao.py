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

**E a rodada de ocupação por recorte também** (095): `apurar_recortes` liga `simular` à rodada da
`ocupacao` — quem ocupa pela ampla, as quatro quantidades de cada recorte e a reversão declarada. O
que o painel diz dela é comportamento atual do motor, inclusive onde a spec 095 o registra como
pendente (DP-1, DP-2), e nunca leitura definitiva da norma.
"""

from django.urls import reverse

from processo_seletivo.classificacao.application import previa as calculo
from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.classificacao.domain import jornada as jornada_do_perfil
from processo_seletivo.classificacao.domain.desempate import _valor_do_criterio
from processo_seletivo.ocupacao.domain import apuracao, rodada_da_previa

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
#: A espécie de reversão pelo rótulo do passo Perfis (`_perfil.html`), e não pelo código.
REVERSAO = {
    "ON_EXHAUSTION": "“Só quando a lista reservada esgota”",
    "ON_BALANCE": "“A quantidade que ficou sem preencher”",
}


def apurar_vagas(progrediram, vagas, empates):
    """A apuração das vagas, só a parte que a prévia antecipa: pararia? (D-006)"""
    try:
        apuracao.titulares_iniciais(
            progrediram_em_ordem=progrediram, efetivas=vagas, empates_residuais=empates
        )
    except apuracao.EmpateNaFronteiraDoAlvo as erro:
        return erro.posicao, erro.quantas
    return None


def apurar_recortes_com(especie):
    """A rodada de ocupação da `ocupacao`, com a reversão declarada no Perfil gravado (095)."""

    def apurar(entradas):
        return rodada_da_previa.rodada(entradas, especie=especie)

    return apurar


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
    if corte.get("sem_linha"):
        return {
            "estado": "impedido",
            "forte": "O corte deste recorte não é apurável.",
            "resto": "O alvo vem do quadro de vagas, e esta Modalidade não tem linha nele: "
            "ausência não vira zero.",
            "anuncio": "Corte não apurável: sem linha no quadro.",
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
    if corte.get("sem_linha"):
        passos.append(
            {
                "nome": "Corte",
                "classe": "passo-impedido",
                "valor": "Não apurável",
                "linhas": ["o alvo vem do quadro, e esta Modalidade não tem linha"],
            }
        )
        passos.append(
            {
                "nome": rotulo,
                "classe": "",
                "valor": "Ninguém deste recorte",
                "linhas": ["sem faixa, ninguém avança por ele"],
            }
        )
        return {"passos": passos, "ramo": ""}
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
            "texto": f"{aviso['quantas']} empatados disputam "
            + ("a única vaga do " if vagas == 1 else f"a última das {vagas} vagas do ")
            + "quadro, e a apuração não escolhe entre eles — qualquer que seja o desfecho "
            "declarado para o corte. Nenhum campo deste cartão trata disso.",
        }
    return {
        "estado": "ok",
        "forte": "Seria possível:",
        "texto": "nenhum empate atravessa "
        + ("a única vaga." if vagas == 1 else f"a última das {vagas} vagas."),
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


def fronteira(p, mudaram, destacar=frozenset()):
    """Só quem ajuda a entender: perto de cada limite, nos empates, e quem mudou (R-011).

    `destacar` são linhas que outra explicação aponta — na reservada, quem ocuparia pela ampla
    (095, FR-2314) — e que por isso não podem sumir num trecho agrupado.
    """
    ordem = p["ordem"]
    limites = _limites(p)
    relevantes = set()
    for quantos, _ in limites:
        relevantes.update(range(max(quantos - 2, 0), min(quantos + 2, len(ordem))))
    for indice, item in enumerate(ordem):
        if (
            len(item["grupo_da_pontuacao"]) > 1
            or item["inscricao_id"] in mudaram
            or item["inscricao_id"] in destacar
        ):
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
                    "id": item["inscricao_id"],
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
                "id": item["inscricao_id"],
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
    if aberto["impedido"] and corte.get("sem_linha"):
        aberto["bloqueio"] = "O alvo vem do quadro de vagas, e este recorte não tem linha nele."
    elif aberto["impedido"]:
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
            if ponto["do_selecionado"] and p.get("recortes"):
                item["destaque"], frases = _participantes(p, ponto)
                item["frases"].extend(frases)
                item["frases"].append(f"As notas da {etapa['name']} não são simuladas aqui.")
            elif ponto["do_selecionado"]:
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
                item["aberto"]["recortes"] = resumo_dos_recortes(p)
            else:
                if ponto["por_sorteio"]:
                    # Desde a `098`, o sorteio tem prévia própria, pela mesma rota: o link abre a
                    # dele, com semente fictícia (FR-2480).
                    item["frases"].append(
                        "Ordena por sorteio: tem prévia própria, com semente fictícia — simule-o "
                        "pelo cartão dele, ou por aqui."
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
                item["simular"] = url_do_marco(marco["sub"])
        saida.append(item)
    return saida


# --- Os recortes, a ocupação e a reversão (095) -------------------------------------------------

RODADA = rodada_da_previa


def _n(quantos, singular, plural):
    return f"{quantos} {singular if quantos == 1 else plural}"


def _nomes(ids, p):
    nomes = {i["inscricao_id"]: i["nome"] for i in p["ordem"] + p["sem_posicao"]}
    return _lista(sorted(nomes[i] for i in ids if i in nomes))


def _avancam(calculado):
    return sum(
        1 for c in calculado["consequencias"].values() if c in (C.AVANCA, C.PELO_EMPATE, C.SEGUE)
    )


def _rotulo_da_ampla(p):
    return f"{p.get('rotulo_da_ampla') or 'Ampla concorrência'}, todos os candidatos"


def resumo_dos_recortes(p):
    """Uma linha por recorte, no marco aberto da jornada (FR-2310). Vazio sem reservada."""
    if not p.get("recortes"):
        return []
    linhas = [
        {
            "rotulo": _rotulo_da_ampla(p),
            "texto": _resumo_do_recorte(p, f"{p['total']} candidatos"),
        }
    ]
    for r in p["recortes"]:
        quantos = len(r["ordem"]) + len(r["sem_posicao"])
        universo = f"{quantos} autodeclarado{'s' if quantos != 1 else ''}"
        linhas.append({"rotulo": r["rotulo"], "texto": _resumo_do_recorte(r, universo)})
    return linhas


def _resumo_do_recorte(calculado, universo):
    corte = calculado["corte"]
    if not (calculado["ordem"] or calculado["sem_posicao"]):
        return "ninguém concorreu neste recorte na população fictícia."
    if corte.get("sem_linha"):
        return f"{universo}; o corte não é apurável: o alvo vem do quadro, e falta a linha."
    if corte.get("recusado"):
        return f"{universo}; o corte não seria emitido (empate na {corte['posicao']}ª)."
    if calculo.impedido(corte):
        return f"{universo}; o resultado depende do desfecho do empate, que não está declarado."
    if not corte["declarado"]:
        return f"{universo}; o marco não corta."
    avancam = _avancam(calculado)
    return f"{universo}; {avancam} {'avançaria' if avancam == 1 else 'avançariam'}."


def _participantes(p, ponto):
    """A Etapa alimentada recebe a união das faixas, contando cada pessoa uma vez (FR-2311)."""
    dados = p["participantes"]
    frases = []
    ate = "Até " if ponto["portas_antes"] else ""
    if dados["depende_de"]:
        destaque = "O número depende de um corte que não seria emitido."
        frases.append(
            f"O corte de {_lista(dados['depende_de'])} não seria emitido: quem chega à "
            f"{ponto['etapa']['name']} por ele só se sabe depois do desempate."
        )
        return destaque, frases
    acrescentados = dados["uniao"] - dados["so_pela_ampla"]
    destaque = f"{ate}{dados['uniao']} candidatos poderiam participar"
    frases.append(
        f"Os {dados['so_pela_ampla']} da faixa da ampla"
        + (
            f" e mais {acrescentados} que só a faixa de uma reservada alcança"
            if acrescentados
            else "; nenhuma reservada acrescenta alguém"
        )
        + ". Quem está em duas faixas conta uma vez."
    )
    if ponto["portas_antes"]:
        frases.append(
            f"Menos, se alguém for eliminado em {_nomes_das_etapas(ponto['portas_antes'])}."
        )
    return destaque, frases


def _frase_da_reversao(apurado, rotulo, especie):
    if apurado.get("sem_ocupante_antes", 0) == 0:
        return "Não há o que reverter: nenhuma vaga ficaria sem ocupante." if especie else ""
    if not especie:
        return "Este Perfil não declara reversão: a vaga reservada sem ocupante continua reservada."
    nome = REVERSAO.get(especie, especie)
    if apurado["cederia"]:
        cede = apurado["cederia"]
        verbo = "seria cedida" if cede == 1 else "seriam cedidas"
        return (
            f"Pela reversão declarada, {nome}, {_n(cede, 'vaga', 'vagas')} {verbo} à ampla "
            f"concorrência deste Perfil, e a apuração de {rotulo} registraria "
            f"{_n(apurado['efetivas'], 'efetiva', 'efetivas')}, "
            + (
                f"{apurado['faltando']} sem ocupante."
                if apurado["faltando"]
                else "nenhuma sem ocupante."
            )
        )
    return (
        f"Pela reversão declarada, {nome}, nenhuma vaga seria cedida: pela regra de hoje, "
        f"{rotulo} ainda tem quem ocupar — "
        f"{_n(apurado['pessoas_com_posicao'], 'pessoa', 'pessoas')} com posição para "
        f"{_n(apurado['ocupadas'], 'vaga ocupada', 'vagas ocupadas')} —, e a conta inclui quem "
        "ocupa pela ampla. "
        "É o comportamento atual do sistema, registrado como pendente de decisão na spec 095."
    )


def _quantidades(apurado):
    """As quatro quantidades, com as vagas sem ocupante **antes** da cessão: a reversão vem dita à
    parte, com o que a apuração registraria depois dela (095, R-004)."""
    sem = apurado.get("sem_ocupante_antes", apurado["faltando"])
    return (
        f"{_n(apurado['publicadas'], 'publicada', 'publicadas')}, "
        f"{_n(apurado['ocupadas'], 'ocupada', 'ocupadas')}, "
        + (f"{sem} sem ocupante nesta hipótese" if sem else "nenhuma sem ocupante nesta hipótese")
        + "."
    )


def _motivo_nao_avaliado(apurado):
    estado = apurado["estado"]
    if estado == RODADA.SEM_LINHA:
        return "este recorte não tem linha no quadro de vagas, e ausência não vira zero."
    if estado == RODADA.CORTE_NAO_EMITIDO:
        return "o corte deste recorte não seria emitido, e não há quem apurar."
    return "depende de quem ocupa pela ampla, e a apuração da ampla não seria possível."


def _estado_nao_avaliado(apurado, rotulo):
    if apurado["estado"] == RODADA.PAROU_NA_FRONTEIRA:
        return (
            f"Pararia na {apurado['posicao']}ª posição: {apurado['quantas']} empatados disputam a "
            "última vaga, e a apuração não escolhe entre eles."
        )
    return "Não avaliada: " + _motivo_nao_avaliado(apurado)


def ocupacao_dos_recortes(p):
    """O bloco da ocupação por recorte, sempre como hipótese (FR-2320 a FR-2330)."""
    rodada = p.get("ocupacao_por_recorte")
    if not rodada:
        return None
    apurados, especie = rodada["recortes"], rodada["especie"]
    recortes = [(None, p.get("rotulo_da_ampla") or "Ampla concorrência", p)] + [
        (r["lista_id"], r["rotulo"], r) for r in p.get("recortes") or []
    ]
    linhas = []
    for lista_id, rotulo, calculado in recortes:
        apurado = apurados.get(lista_id) or {"estado": RODADA.SEM_LINHA}
        linha = {"rotulo": rotulo, "frases": []}
        if apurado["estado"] != RODADA.AVALIADA:
            linha["estado"] = (
                "neutro" if apurado["estado"] != RODADA.PAROU_NA_FRONTEIRA else "aviso"
            )
            linha["texto"] = _estado_nao_avaliado(apurado, rotulo)
            linhas.append(linha)
            continue
        linha["estado"] = (
            "aviso" if apurado.get("sem_ocupante_antes", apurado["faltando"]) else "ok"
        )
        linha["texto"] = _quantidades(apurado)
        if lista_id is not None:
            if apurado["ocupam_pela_ampla"]:
                quem = apurado["ocupam_pela_ampla"]
                linha["frases"].append(
                    f"{_nomes(quem, calculado)} ocupa{'m' if len(quem) > 1 else ''} pela ampla: "
                    f"não conta{'m' if len(quem) > 1 else ''} aqui, e a vaga reservada continua "
                    f"de {rotulo}."
                )
            if apurado["tomadas_pela_ampla"]:
                faixa = len(calculado["corte"].get("progrediram") or [])
                tomadas, alem = apurado["tomadas_pela_ampla"], apurado["alem_da_faixa"]
                linha["frases"].append(
                    f"Das {_n(faixa, 'posição', 'posições')} da faixa de {rotulo}, {tomadas} "
                    + ("é de quem ocupa" if tomadas == 1 else "são de quem ocupa")
                    + " pela ampla"
                    + (
                        f"; {_n(alem, 'autodeclarado', 'autodeclarados')} com posição "
                        + ("ficou" if alem == 1 else "ficaram")
                        + " além da faixa, e alcançá-"
                        + ("lo" if alem == 1 else "los")
                        + " seria faixa seguinte, que a prévia não simula"
                        if alem
                        else ""
                    )
                    + ". É como o sistema calcula hoje: a faixa da reservada conta quem ocupa pela "
                    "ampla, e a apuração o tira depois."
                )
            reversao = _frase_da_reversao(apurado, rotulo, especie)
            if reversao:
                linha["frases"].append(reversao)
        linhas.append(linha)
    proxima = (
        f"A próxima apuração da ampla leria {rodada['efetivas_da_proxima_ampla']} vagas efetivas, "
        "com as cedidas; a prévia não a refaz."
        if rodada["efetivas_da_proxima_ampla"]
        else ""
    )
    # A população estável planta um empate na última vaga da ampla (decisão 003 da `094`), e ele
    # para também as reservadas. É o que o motor faria; o painel diz como ver o resto, e não o
    # inventa.
    dependentes = any(
        (apurados.get(r["lista_id"]) or {}).get("estado") == RODADA.DEPENDE_DA_AMPLA
        for r in p.get("recortes") or []
    )
    caminho = (
        "Para ver a ocupação das reservadas e quem ocuparia pela ampla, escolha o caso-limite "
        "“Autodeclarado dentro das vagas da ampla”, ou julgue o empate da ampla."
        if dependentes
        else ""
    )
    return {
        "linhas": linhas,
        "proxima": proxima,
        "caminho": caminho,
        "concomitancia": (
            "Quem concorre por uma reservada concorre também pela ampla; se ocupar vaga pela "
            "ampla, não conta na reservada. Vale para todo Perfil com reserva, e não é campo "
            "do Edital."
            if p.get("recortes")
            else ""
        ),
    }


def recorte_em_vista(p, pedido):
    """O cálculo do recorte escolhido no detalhe, na forma que as funções do painel leem (FR-2313).

    Devolve `(cálculo, escolhido, aviso)`. Recorte que não existe mais no rascunho volta à ampla, e
    o painel diz isso, em vez de 404: a Modalidade pode ter saído entre dois recálculos (R-007).
    """
    if not pedido or not p.get("recortes"):
        return p, "", ""
    r = next((r for r in p["recortes"] if str(r["lista_id"]) == str(pedido)), None)
    if r is None:
        return p, "", "O recorte pedido não existe mais no rascunho; a prévia mostra a ampla."
    apurado = ((p.get("ocupacao_por_recorte") or {}).get("recortes") or {}).get(r["lista_id"])
    apurado = apurado or {"estado": RODADA.SEM_LINHA}
    if apurado["estado"] == RODADA.PAROU_NA_FRONTEIRA:
        aviso = {
            "avaliado": True,
            "para": True,
            "posicao": apurado["posicao"],
            "quantas": apurado["quantas"],
        }
    elif apurado["estado"] == RODADA.AVALIADA:
        aviso = {"avaliado": True, "para": False}
    else:
        aviso = {"avaliado": False, "motivo": _motivo_nao_avaliado(apurado)}
    return {**p, **r, "aviso_das_vagas": aviso}, str(r["lista_id"]), ""


def _ocupam_pela_ampla(p, em_vista):
    if not em_vista.get("lista_id"):
        return frozenset()
    apurado = ((p.get("ocupacao_por_recorte") or {}).get("recortes") or {}).get(
        em_vista["lista_id"]
    ) or {}
    return frozenset(apurado.get("ocupam_pela_ampla") or ())


def decorar_completa(tabela, p, em_vista):
    """A classificação completa ganha a coluna do recorte: a Modalidade, na ampla; a posição na
    ampla, na reservada (FR-2314)."""
    if not p.get("recortes"):
        return tabela
    rotulos = {r["lista_id"]: r["rotulo"] for r in p["recortes"]}
    itens = em_vista["ordem"] + em_vista["sem_posicao"]
    if em_vista.get("lista_id"):
        coluna = "Na ampla"
        valores = [
            f"{p['posicao_na_ampla'][i['inscricao_id']]}ª"
            if i["inscricao_id"] in p["posicao_na_ampla"]
            else "—"
            for i in itens
        ]
    else:
        coluna = "Modalidade"
        valores = [rotulos.get(i.get("modalidade_id")) or "—" for i in itens]
    cabeca = list(tabela["cabeca"])
    cabeca.insert(2, coluna)
    linhas = [
        {**linha, "celulas": [*linha["celulas"][:2], (coluna, valor), *linha["celulas"][2:]]}
        for linha, valor in zip(tabela["linhas"], valores, strict=True)
    ]
    return {"cabeca": cabeca, "linhas": linhas}


def _fluxo_do_recorte(passos, p, em_vista):
    """Com alvo fixo, a faixa de uma reservada não é a linha dela, e o painel diz os dois números
    (FR-2307)."""
    regra = p["regra"] or {}
    corte = em_vista["corte"]
    if not em_vista.get("lista_id") or regra.get("targetKind") != "FIXED" or not corte["declarado"]:
        return passos
    if corte.get("sem_linha") or em_vista["vagas"] is None:
        return passos
    tamanho = (em_vista["alvo"] or 0) + (em_vista["suplentes"] or 0)
    if tamanho != em_vista["vagas"]:
        passos["passos"][1]["linhas"].append(
            f"o alvo fixo vale em todo recorte: a faixa é de {tamanho}, e esta reservada tem "
            f"{em_vista['vagas']} vagas na linha dela"
        )
    return passos


def decorar_fronteira(linhas, p, em_vista):
    """A Modalidade na ampla; a posição na ampla e "ocuparia pela ampla" na reservada (FR-2314)."""
    if not p.get("recortes"):
        return linhas
    rotulos = {r["lista_id"]: r["rotulo"] for r in p["recortes"]}
    modalidade = {
        i["inscricao_id"]: rotulos.get(i.get("modalidade_id"))
        for i in p["ordem"] + p["sem_posicao"]
    }
    apurado = {}
    if em_vista.get("lista_id"):
        apurado = ((p.get("ocupacao_por_recorte") or {}).get("recortes") or {}).get(
            em_vista["lista_id"]
        ) or {}
    pela_ampla = apurado.get("ocupam_pela_ampla") or set()
    for linha in linhas:
        ident = linha.get("id")
        if not ident:
            continue
        if em_vista.get("lista_id"):
            posicao = p["posicao_na_ampla"].get(ident)
            linha["na_ampla"] = f"{posicao}ª na ampla" if posicao else "sem posição na ampla"
            linha["pela_ampla"] = ident in pela_ampla
        else:
            linha["modalidade"] = modalidade.get(ident) or ""
    return linhas


# --- O painel inteiro ---------------------------------------------------------------------------


def candidatos(p, escolha, *, com_reservas=False):
    opcoes = [("estavel", "População estável — testar a regra")]
    casos = [(f"caso:{k}", v[0]) for k, v in cenarios.CASOS.items()]
    reservas = (
        [(f"caso:{k}", v[0]) for k, v in cenarios.CASOS_DE_RESERVA.items()] if com_reservas else []
    )
    bloco = {"escolha": escolha, "opcoes": opcoes, "casos": casos, "reservas": reservas}
    if p is None:
        return bloco
    if p["modo"] == C.CASO_LIMITE:
        descricao = (cenarios.CASOS.get(p["caso"]) or cenarios.CASOS_DE_RESERVA[p["caso"]])[1]
        onde = p["onde"] or ""
        if p["caso"] == "alvo_fixo_reservada" and (p["regra"] or {}).get("targetKind") != "FIXED":
            # O caso diz quando a configuração o desfaz, e por quê (FR-2332).
            onde += (
                " — e com o alvo do quadro a situação não ocorre: a faixa de cada reservada é a "
                "linha dela"
            )
        bloco.update(caso=True, descricao=descricao, onde=onde)
        return bloco
    alvo, faixa, vagas = p["ancoras"][:3]
    bloco.update(
        caso=False,
        total=p["total"],
        montagem=f"Para alvo {alvo}, faixa de {faixa} e {vagas} vagas, com "
        + (_lista(p["plantados"]) if p["plantados"] else "nenhum empate plantado")
        + ", mais uma candidata sem nota e um candidato eliminado.",
        populacao=":".join(str(n) for n in p["ancoras"]),
        remontar=tuple(p["fronteiras"]) != tuple(p["ancoras"]),
    )
    return bloco


def escolha_de_candidatos(dados):
    escolha = (dados.get("candidatos") or "estavel").strip()
    casos = {**cenarios.CASOS, **cenarios.CASOS_DE_RESERVA}
    if escolha.startswith("caso:") and escolha[5:] in casos:
        return escolha, C.CASO_LIMITE, escolha[5:]
    return "estavel", C.ESTAVEL, ""


def populacao_digitada(dados):
    try:
        ancoras = tuple(int(n) for n in (dados.get("populacao") or "").split(":"))
    except ValueError:
        return None
    # As três da fatia 1 — alvo, faixa e vagas da ampla — e, na fatia 2, a faixa de cada reservada.
    return ancoras if len(ancoras) >= 3 else None


def contexto(
    *, perfil, marcos, sub, etapas, fatos, vagas, dados, edital, indice, recortes=None, especie=None
):
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
            recortes=recortes,
            apurar_recortes=apurar_recortes_com(especie),
        )
    except calculo.ForaDaFatia:
        return {**base, "fora_da_fatia": True, "anuncio": "A prévia cobre marcos pela pontuação."}
    except calculo.Incompleto as erro:
        return {
            **base,
            "faltas": erro.faltas,
            "candidatos": candidatos(None, escolha, com_reservas=len(recortes or []) > 1),
            "anterior": dados.get("anterior") or "",
            "anuncio": f"Prévia não calculada: falta declarar {len(erro.faltas)}.",
        }
    p["escala"] = (marco.get("rounding") or {}).get("scale") or 0
    p["fatos"] = fatos
    p["fatos_por_id"] = {str(f["id"]): f.get("label") or f.get("code") for f in fatos}
    atual = calculo.estado(p)
    rotulos = [p.get("rotulo_da_ampla") or "Ampla", *(r["rotulo"] for r in p["recortes"])]
    diff = calculo.comparar(dados.get("anterior") or "", atual, rotulos)
    mudaram = diff["mudaram"] if diff else set()
    cabeca = manchete(p)
    anuncio = cabeca["anuncio"]
    if diff and diff["mudancas"]:
        anuncio += " Mudou: " + " ".join(diff["mudancas"])
    resumo = resumo_dos_recortes(p)
    if resumo:
        anuncio += " " + " ".join(f"{linha['rotulo']}: {linha['texto']}" for linha in resumo[1:])
    contexto_ = {
        **base,
        "candidatos": candidatos(p, escolha, com_reservas=bool(p["recortes"])),
        "ocupacao_dos_recortes": ocupacao_dos_recortes(p),
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
    em_vista, escolhido, aviso_do_recorte = recorte_em_vista(p, dados.get("recorte"))
    contexto_.update(
        manchete=manchete(em_vista),
        mudou=o_que_mudou(diff, p, "marcados na tabela"),
        fluxo=_fluxo_do_recorte(fluxo(em_vista), p, em_vista),
        ocupacao=ocupacao(em_vista),
        fronteira=decorar_fronteira(
            fronteira(em_vista, mudaram, _ocupam_pela_ampla(p, em_vista)), p, em_vista
        ),
        empates=empates(em_vista),
        completa=decorar_completa(completa(em_vista, mudaram), p, em_vista),
        como_calcula=como_calcula(em_vista),
        seletor_de_recorte=(
            {
                "escolhido": escolhido,
                "opcoes": [("", _rotulo_da_ampla(p))]
                + [(str(r["lista_id"]), r["rotulo"]) for r in p["recortes"]],
                "aviso": aviso_do_recorte,
            }
            if p["recortes"]
            else None
        ),
        em_reservada=bool(escolhido),
        # A classificação completa conta o recorte em vista, e não a ampla.
        total=em_vista["total"],
    )
    return contexto_
