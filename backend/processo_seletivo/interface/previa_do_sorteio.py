"""A prévia do marco por sorteio, no painel da prévia da classificação (098).

**A aleatoriedade mora aqui, e só aqui.** O app do sorteio é proibido de importar gerador (021,
FR-026; `test_sem_gerador_pseudoaleatorio.py`): a ordem oficial tem de ser reproduzível. A semente
fictícia da prévia nasce nesta camada, por `secrets`, e entra no sorteio como material pronto — o
app continua sem gerador, e a varredura continua verde sem emenda (R-004).

**A semente viaja assinada, e não digitável** (D-001, FR-2483). O material vai no formulário do
painel como token de `django.core.signing`, com o Edital, o Perfil e o marco dentro do conteúdo
assinado. O servidor só aceita o que ele assinou para aquele marco: um campo oculto é um campo, e
sem a prova de origem a decisão do usuário valeria só na tela. Assinar, e não guardar na sessão,
porque a prévia não grava nada (FR-2509) e duas abas não podem disputar a mesma chave.

**Nenhuma regra própria.** A ordem, o corte, a ocupação e o resumo vêm de
`sorteios/application/simulacao.py`; o bloco da ocupação é o da `095`, por
`previa_da_classificacao.ocupacao_dos_recortes`, com as mesmas frases — inclusive a do comportamento
atual da DP-1. O que este módulo acrescenta é o que só a tela precisa: ler o formulário, gerar e
conferir a semente, e dizer em palavras o que o cálculo devolveu.
"""

import secrets

from django.core import signing
from django.urls import reverse

from processo_seletivo.classificacao.application import previa as calculo
from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.interface import previa_da_classificacao as pontuacao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application import simulacao as aplicacao
from processo_seletivo.sorteios.domain import simulacao

SAL = "previa-do-sorteio"
PREFIXO_DA_LISTA = "inscritos-"
CAMPO_DA_AMPLA = "inscritos-ampla"

#: Os estados do painel que não calculam (contrato do fragmento).
SEMENTE_RECUSADA, ACIMA_DO_LIMITE, REGRA_DESCONHECIDA = "recusada", "limite", "regra"


# --- A semente fictícia (R-004) ------------------------------------------------------------------


def material_ficticio():
    """Cinco números de seis dígitos: a forma do material da Loteria Federal (D-007)."""
    return " ".join(f"{secrets.randbelow(10**6):06d}" for _ in range(5))


def _alcance(edital, perfil_id, marco_id):
    return {"edital": str(edital.id), "perfil": str(perfil_id), "marco": str(marco_id)}


def assinar(material, *, edital, perfil_id, marco_id):
    return signing.dumps({**_alcance(edital, perfil_id, marco_id), "material": material}, salt=SAL)


def semente_do_pedido(dados, *, edital, perfil_id, marco_id):
    """`(material, token, nova)` — ou `None`, quando o token não é deste servidor para este marco.

    Sem token, ou com "Sortear de novo", a semente é nova, e assinada agora. Com token válido, a
    mesma, **com o mesmo token** (D-006): `signing.dumps` carimba o instante, e reassinar a cada
    pedido mudaria o painel de um segundo para o outro sem que nada tivesse mudado.
    """
    token = (dados.get("semente") or "").strip()
    if dados.get("sortear") or not token:
        material = material_ficticio()
        return (
            material,
            assinar(material, edital=edital, perfil_id=perfil_id, marco_id=marco_id),
            True,
        )
    try:
        conteudo = signing.loads(token, salt=SAL)
    except signing.BadSignature:
        return None
    if not isinstance(conteudo, dict) or any(
        conteudo.get(chave) != valor
        for chave, valor in _alcance(edital, perfil_id, marco_id).items()
    ):
        return None
    material = conteudo.get("material")
    return (material, token, False) if isinstance(material, str) and material else None


# --- A população informada (FR-2487 a FR-2491) ---------------------------------------------------


def _quantidade(dados, campo, sugestao):
    bruto = (dados.get(campo) or "").strip()
    if not bruto:
        return sugestao, True, False
    try:
        valor = int(bruto)
    except ValueError:
        return sugestao, True, True
    if valor < 0:
        return sugestao, True, True
    return valor, False, False


def populacao_do_pedido(dados, recortes):
    """As quantidades por lista, com a sugestão onde o elaborador não escreveu (ou escreveu errado).

    `recortes` é a derivação oficial, a ampla primeiro. Devolve as linhas para o formulário, o par
    `(so_ampla, [(lista_id, quantos)])` para o cálculo, e os rótulos das listas com valor recusado.
    """
    ampla = recortes[0]
    linhas, invalidos = [], []
    so_ampla, sugerida, invalido = _quantidade(
        dados, CAMPO_DA_AMPLA, simulacao.sugestao(ampla["vagas"])
    )
    linhas.append(
        {
            "campo": CAMPO_DA_AMPLA,
            "rotulo": "Só na ampla concorrência",
            "valor": so_ampla,
            "sugerida": sugerida,
        }
    )
    if invalido:
        invalidos.append("ampla concorrência")
    por_reservada = []
    for recorte in recortes[1:]:
        campo = f"{PREFIXO_DA_LISTA}{recorte['lista_id']}"
        quantos, sugerida, invalido = _quantidade(
            dados, campo, simulacao.sugestao(recorte["vagas"])
        )
        linhas.append(
            {
                "campo": campo,
                "rotulo": f"Autodeclarados {recorte['rotulo']}",
                "valor": quantos,
                "sugerida": sugerida,
            }
        )
        if invalido:
            invalidos.append(recorte["rotulo"])
        por_reservada.append((recorte["lista_id"], quantos))
    return linhas, (so_ampla, por_reservada), invalidos


# --- O contexto do painel ------------------------------------------------------------------------


def contexto(*, perfil, marco, sub, snapshot, edital, indice, recortes, especie, dados):
    """Tudo o que `_previa_do_sorteio.html` desenha, ou o estado que impede de desenhar."""
    vista = "detalhe" if dados.get("vista") == "detalhe" else "processo"
    previa_url = (
        reverse("interface:fragmento-previa-da-classificacao", args=[indice, sub])
        + f"?edital={edital.id}"
    )
    base = {
        "indice": indice,
        "vista": vista,
        "perfil": {"code": perfil.get("code", ""), "name": perfil.get("name", "")},
        "marco_nome": marco.get("name") or "Marco sem denominação",
        "previa_url": previa_url,
        "fechar_url": reverse("interface:fragmento-previa-da-classificacao-fechar"),
    }
    linhas, (so_ampla, por_reservada), invalidos = populacao_do_pedido(dados, recortes)
    base["populacao"] = {
        "linhas": linhas,
        "soma": so_ampla + sum(q for _, q in por_reservada),
        "invalidos": invalidos,
    }
    pedido = semente_do_pedido(dados, edital=edital, perfil_id=perfil["id"], marco_id=marco["id"])
    if pedido is None:
        return {
            **base,
            "estado": SEMENTE_RECUSADA,
            "anuncio": "A semente desta prévia não foi reconhecida. Sorteie de novo.",
        }
    material, token, nova = pedido
    base["semente"] = {
        "material": material,
        "grupos": material.split(),
        "token": token,
        "nova": nova,
    }
    limite = aplicacao.acima_do_limite(so_ampla, por_reservada)
    if limite:
        return {**base, "estado": ACIMA_DO_LIMITE, "limite": limite, "anuncio": limite}
    candidatos = simulacao.populacao(so_ampla, por_reservada, nomear=cenarios.nome_ficticio)
    metodo = marco.get("drawMethod") or (snapshot or {}).get("drawMethod") or {}
    apurar = pontuacao.apurar_recortes_com(especie)
    try:
        p = aplicacao.simular_sorteio(
            marco,
            perfil_id=perfil["id"],
            metodo=metodo,
            material=material,
            candidatos=candidatos,
            recortes=recortes,
            apurar_recortes=apurar,
        )
        # **O resumo só na vista do processo**: o detalhe não o desenha, e as 1.000 rodadas custam
        # até ~1,4 s por pedido (revisão do #328).
        resumo = (
            aplicacao.resumir(
                marco,
                perfil_id=perfil["id"],
                semente=p["semente"],
                candidatos=candidatos,
                recortes=recortes,
                apurar_recortes=apurar,
                preparo=p["preparo"],
            )
            if len(recortes) > 1 and vista == "processo"
            else None
        )
    except calculo.Incompleto as erro:
        return {
            **base,
            "faltas": erro.faltas,
            "anuncio": f"Prévia não calculada: falta declarar {len(erro.faltas)}.",
        }
    except DomainError as recusa:
        return {
            **base,
            "estado": REGRA_DESCONHECIDA,
            "recusa": recusa.detail,
            "anuncio": recusa.detail,
        }
    nomes = {c.id: c.nome for c in candidatos}
    listas = {c.id: c.lista_id for c in candidatos}
    rotulos = {r["lista_id"]: r["rotulo"] for r in recortes}
    p["nomes"], p["listas"], p["rotulos"] = nomes, listas, rotulos
    p["especie"] = especie
    resumo_por_recorte = _resumo_por_recorte(p)
    contexto_ = {
        **base,
        "estado": "calculada",
        "frases_da_semente": _frases_da_semente(p, perfil),
        "regra_do_marco": _regra_do_marco(p),
        "recortes": resumo_por_recorte,
        "ocupacao_dos_recortes": _ocupacao(p),
        "rodadas": _rodadas(resumo, p, recortes) if vista == "processo" else None,
    }
    contexto_["anuncio"] = _anuncio(nova, resumo_por_recorte, contexto_["rodadas"])
    if vista == "detalhe":
        contexto_.update(_detalhe(p, dados.get("recorte")))
    return contexto_


# --- As frases -----------------------------------------------------------------------------------


def _media(valor):
    """Uma casa decimal, com vírgula — o `numero` da prévia da pontuação."""
    return pontuacao.numero(float(valor), 1)


def _frases_da_semente(p, perfil):
    frases = []
    if p["supos_regra"]:
        frases.append(
            "O método ainda não escolheu a regra que transforma os números em semente; a prévia "
            "supôs a da Loteria Federal, os dígitos em sequência."
        )
    elif p["semente"] != p["material"]:
        frases.append(f"Pela regra declarada no método, a semente é {p['semente']}.")
    ampla = perfil.get("generalCompetitionModalityId")
    if ampla:
        nome = next(
            (
                m.get("name") or m.get("code")
                for m in perfil.get("competitionModalities") or []
                if str(m.get("id")) == str(ampla)
            ),
            "apontada como ampla",
        )
        frases.append(
            f"A Modalidade “{nome}”, que este Perfil aponta como a ampla concorrência, ganha "
            "uma lista própria no sorteio do certame, e esta prévia não a sorteia: a ocupação das "
            "vagas não tem linha para ela, e a quantidade dela mora na linha geral."
        )
    return frases


def _regra_do_marco(p):
    regra = p["regra"]
    if not regra:
        return (
            "Este marco não declara regra de corte: o sorteio daria a ordem, mas sem corte não há "
            "faixa, e o marco não chamaria ninguém. A ocupação das vagas não é calculada."
        )
    partes = [
        "as vagas do quadro de cada lista"
        if regra["targetKind"] == "FROM_VACANCY_TABLE"
        else f"alvo de {p['alvo']}, o mesmo em toda lista"
    ]
    if p["suplentes"]:
        partes.append(f"{p['suplentes']} posições adicionais (suplentes)")
    return f"A faixa de cada lista: {' + '.join(partes)}. O sorteio não empata."


def _resumo_por_recorte(p):
    linhas = []
    for indice, r in enumerate(p["recortes"]):
        rotulo = r["rotulo"] or "Ampla concorrência"
        if indice == 0:
            universo = f"todos os {p['total']} inscritos, autodeclarados inclusive"
            rotulo = r["rotulo"] or "Ampla concorrência"
        else:
            universo = pontuacao.contagem(r["total"], "autodeclarado", "autodeclarados")
        if not r["total"]:
            texto = (
                "ninguém concorreu nesta lista na população fictícia. O sistema não sorteia lista "
                "vazia — ele recusa a relação sem participante —, e por isso ela não seria cortada "
                "nem apurada."
            )
        elif r["corte"].get("sem_linha"):
            texto = f"{universo}; o corte não é apurável: o alvo vem do quadro, e falta a linha."
        elif not r["corte"]["declarado"]:
            texto = f"{universo}; todos sorteados, e o marco não corta."
        else:
            avancam = len(r["corte"]["progrediram"])
            texto = f"{universo}; {avancam} {'avançaria' if avancam == 1 else 'avançariam'}."
            if r["vagas"] is not None and r["total"] <= r["vagas"]:
                quantos = (
                    "menos inscritos que vagas"
                    if r["total"] < r["vagas"]
                    else "tantos inscritos quantas vagas"
                )
                texto += (
                    f" Há {quantos}, e o sistema sorteia mesmo assim: a posição decide a ordem "
                    "de chamada"
                    + (", e quem também concorre por uma reservada." if indice == 0 else ".")
                )
        linhas.append({"lista_id": r["lista_id"], "rotulo": rotulo, "texto": texto})
    return linhas


def _ordem_com_nomes(r, p):
    return [{**item, "nome": p["nomes"][item["inscricao_id"]]} for item in r["ordem"]]


def _ocupacao(p):
    """O bloco da `095`, sobre a rodada do sorteio, com o que é próprio do sorteio corrigido."""
    if not p.get("ocupacao_por_recorte"):
        return None
    ampla = p["recortes"][0]
    forma = {
        "ocupacao_por_recorte": p["ocupacao_por_recorte"],
        "rotulo_da_ampla": ampla["rotulo"] or "Ampla concorrência",
        "ordem": _ordem_com_nomes(ampla, p),
        "sem_posicao": [],
        "recortes": [
            {**r, "ordem": _ordem_com_nomes(r, p), "sem_posicao": []} for r in p["recortes"][1:]
        ],
    }
    bloco = pontuacao.ocupacao_dos_recortes(forma)
    # O caminho da `095` manda escolher um caso-limite ou julgar o empate da ampla, e o sorteio não
    # tem nem um nem outro: a ampla só deixa de ser apurável por falta de linha no quadro.
    bloco["caminho"] = ""
    vazias = {r["lista_id"] for r in p["recortes"][1:] if not r["total"]}
    for linha in bloco["linhas"]:
        if linha["lista_id"] is not None and linha["lista_id"] in vazias:
            linha["texto"] = (
                "Não apurada: ninguém concorreu, e a lista não seria sorteada. Por isso a vaga "
                "dela ficaria sem ocupante e não seria cedida à ampla, nem pela reversão "
                "declarada. É o comportamento atual do sistema, registrado como achado de "
                "21/10/2026 para decisão."
            )
            linha["estado"] = "aviso"
    return bloco


def _rodadas(resumo, p, recortes):
    if resumo is None:
        return {
            "sem_cotas": (
                "Este Perfil não declara reserva: na ampla, toda rodada ocupa as vagas até onde "
                "houver inscritos. O sorteio muda quem ocupa, e não quantas."
            )
        }
    if resumo.get("sem_corte"):
        return None
    especie = p["especie"]
    linhas = []
    for recorte in recortes[1:]:
        dados = resumo["reservadas"][recorte["lista_id"]]
        rotulo = recorte["rotulo"]
        if not dados.get("avaliadas"):
            frase = (
                "nenhuma rodada a apura: ninguém concorreu nela"
                if dados["estado"] == "corte_nao_emitido"
                and not next(r for r in p["recortes"] if r["lista_id"] == recorte["lista_id"])[
                    "total"
                ]
                else "não avaliada em rodada nenhuma: "
                + pontuacao.motivo_nao_avaliado(dados).rstrip(".")
            )
            linhas.append({"rotulo": rotulo, "frases": [frase], "destaque": False})
            continue
        frases = []
        sobra = dados["com_sobra"]
        if sobra["constante"]:
            frases.append(
                "sobraria vaga sem ocupante em todas as rodadas"
                if sobra["valor"]
                else "nenhuma rodada deixaria vaga sem ocupante"
            )
        else:
            frases.append(
                f"sobraria ao menos uma vaga sem ocupante em {round(sobra['porcentagem'])}% "
                "das rodadas"
            )
        sem = dados["sem_ocupante"]
        if sem["media"]:
            frases.append(
                f"{pontuacao.contagem(sem['valor'], 'vaga', 'vagas')} sem ocupante em todas"
                if sem["constante"]
                else f"em média, {_media(sem['media'])} sem ocupante"
            )
        pela = dados["pela_ampla"]["media"]
        frases.append(
            f"em média, {_media(pela)} "
            + ("autodeclarado ocuparia" if pela == 1 else "autodeclarados ocupariam")
            + " pela ampla"
        )
        if especie:
            cedidas = dados["cedidas"]
            if cedidas["constante"] and not cedidas["valor"]:
                frases.append(
                    "nenhuma vaga seria cedida à ampla em rodada nenhuma"
                    + (
                        " — pela regra de hoje, a lista sempre tem “quem ocupar”, porque a conta "
                        "inclui quem ocupa pela ampla (comportamento atual, pendente de decisão "
                        "na spec 095)"
                        if sem["media"] and especie == "ON_EXHAUSTION"
                        else ""
                    )
                )
            else:
                media = cedidas["media"]
                frases.append(
                    f"em média, {_media(media)} "
                    + ("vaga seria cedida" if media == 1 else "vagas seriam cedidas")
                    + f" à ampla, em {round(dados['com_cessao']['porcentagem'])}% das rodadas"
                )
        else:
            frases.append("o Perfil não declara reversão, e a vaga sem ocupante continua reservada")
        destaque = bool(sem["media"] and pela)
        linhas.append({"rotulo": rotulo, "frases": frases, "destaque": destaque})
    ampla = resumo["ampla"]
    vagas = recortes[0]["vagas"]
    frase_da_ampla = (
        f"Em média, {_media(ampla['autodeclarados_ocupando']['media'])} das {vagas} vagas da "
        "ampla seriam ocupadas por autodeclarados."
        if ampla.get("avaliadas")
        else ""
    )
    return {
        "quantas": f"{resumo['rodadas']:,}".replace(",", "."),
        "linhas": linhas,
        "ampla": frase_da_ampla,
        "dp1": any(linha["destaque"] for linha in linhas),
    }


def _anuncio(nova, recortes, rodadas):
    partes = ["Semente nova." if nova else "Semente mantida."]
    partes += [f"{linha['rotulo']}: {linha['texto']}" for linha in recortes]
    if rodadas and rodadas.get("linhas"):
        primeira = rodadas["linhas"][0]
        partes.append(
            f"Em {rodadas['quantas']} rodadas, {primeira['rotulo']}: {primeira['frases'][0]}."
        )
    return " ".join(partes)


# --- O detalhe de uma lista ----------------------------------------------------------------------


def _detalhe(p, pedido):
    opcoes = [("", p["recortes"][0]["rotulo"] or "Ampla concorrência")] + [
        (str(r["lista_id"]), r["rotulo"]) for r in p["recortes"][1:]
    ]
    em_vista = next(
        (r for r in p["recortes"][1:] if pedido and str(r["lista_id"]) == str(pedido)),
        p["recortes"][0],
    )
    aviso = (
        "A lista pedida não existe mais no rascunho; a prévia mostra a ampla."
        if pedido and em_vista is p["recortes"][0]
        else ""
    )
    apurados = (p.get("ocupacao_por_recorte") or {}).get("recortes") or {}
    ocupam = frozenset((apurados.get(em_vista["lista_id"]) or {}).get("ocupam_pela_ampla") or ())
    reservada = em_vista["lista_id"] is not None
    linhas = []
    for item in em_vista["ordem"]:
        identificador = item["inscricao_id"]
        lista = p["listas"][identificador]
        linhas.append(
            {
                "posicao": item["posicao"],
                "numero": item["numero_publico"],
                "nome": p["nomes"][identificador],
                "modalidade": "" if reservada or lista is None else p["rotulos"].get(lista, ""),
                "na_ampla": (
                    f"{p['posicao_na_ampla'][identificador]}ª na ampla" if reservada else ""
                ),
                "pela_ampla": reservada and identificador in ocupam,
                "marca": pontuacao.marca(em_vista["consequencias"][identificador], p),
            }
        )
    return {
        "seletor": {
            "opcoes": opcoes if len(opcoes) > 1 else [],
            "escolhido": str(em_vista["lista_id"]) if reservada else "",
            "aviso": aviso,
        },
        "em_vista": {
            "rotulo": em_vista["rotulo"] or "Ampla concorrência",
            "linhas": linhas,
            "reservada": reservada,
            "vazia": not em_vista["total"],
        },
    }
