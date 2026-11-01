"""A prova de que texto e imagem dizem a mesma coisa — e de que nenhum dos dois diz o que não pode.

Três conferências, todas sobre o **material produzido**, e não sobre o template:

1. **Peça ⊂ ficha.** Cada `<text>` da peça declara o campo de onde veio, e o conteúdo precisa ser o
   valor daquele campo — ou, se o valor quebrou em linhas, as linhas juntas precisam reconstituí-lo.
   Frase fixa só passa se for uma das `FIXOS`. Texto sem campo reprova.
2. **Peça ⊂ texto.** Toda data e toda quantidade que a peça mostra aparecem também no kit textual: a
   comunicação que usar só os textos não fica sem um dado que a imagem dava.
3. **Vocabulário.** Nem a peça nem os textos dizem tempo relativo, estado do momento ou promessa; e,
   sem período designado, nenhum dos dois fala de inscrição.
"""

import re
import xml.etree.ElementTree as ET
from collections import defaultdict

from .ficha import NEUTRO
from .peca import FIXOS
from .textos import assinatura, rotulo_da_oferta

SVG = "{http://www.w3.org/2000/svg}"

# Juízo, promessa e tempo relativo: o material circula depois de gerado, e cada uma destas fica
# falsa ou indevida em algum dia da circulação. A lista do portal (`PROIBIDAS`) entra junto.
PROIBIDAS = (
    r"\bfaltam?\b",
    r"\bamanhã\b",
    r"\bhoje\b",
    r"\búltimos? dias?\b",
    r"\búltima oportunidade\b",
    r"\bnão perca\b",
    r"\bgaranta\b",
    r"\bgarantid[ao]s?\b",
    r"\binscrições abertas\b",
    r"\bestão abertas\b",
    r"\bresultado (?:final|disponível)\b",
    r"\baprovad[ao]s?\b",
    r"(?<!não )\bclassificad[ao]s?\b",
    r"\bmarco\b",
    r"\brecorte\b",
    r"\bapuração\b",
    r"\bhomologa",
)


def _do_portal():
    # A lista que as telas públicas já obedecem (`tests/portal/test_acompanhamento_pela_situacao.py`).
    from tests.portal.test_acompanhamento_pela_situacao import PROIBIDAS as DO_PORTAL

    return tuple(DO_PORTAL)


def textos_da_peca(svg):
    raiz = ET.fromstring(svg)
    return [(no.get("data-campo"), no.text or "") for no in raiz.iter(f"{SVG}text")]


def _esperado(campo, ficha):
    ofertas = {o["perfil_id"]: o for o in ficha["ofertas"]}
    if campo == "assinatura":
        return assinatura(ficha)
    if campo == "identificacao":
        return ficha["identificacao"]
    if campo == "titulo_sem_numero":
        return ficha["titulo_sem_numero"] or ficha["titulo"]
    if campo == "titulo_do_processo":
        return ficha["titulo_do_processo"]
    if campo == "periodo_curto":
        return ficha["periodo_curto"]
    if campo == "fim_hora":
        return f"até as {ficha['fim_hora']} · {FIXOS['horario']}"
    if campo == "oferta_nome":
        return ficha["ofertas"][0]["nome"]
    if campo == "contagem":
        return f"{len(ficha['ofertas'])} opções"
    if campo == "total_de_vagas":
        return f"{ficha['total_de_vagas']} vagas no total"
    if campo == "destino":
        return f"{ficha['caminho_curto']} · busque por {ficha['numero']}/{ficha['ano']}"
    if campo == "selo":
        return (
            f"Versão vigente desde {ficha['versao_desde_texto']} · {ficha['versao_ato']} · "
            f"ref. {ficha['impressao'][:8]}"
        )
    tipo, _, perfil = campo.partition(":")
    if tipo == "oferta_rotulo":
        return rotulo_da_oferta(ofertas[perfil], ficha)
    if tipo == "oferta_quantidade":
        return ofertas[perfil]["quantidade"]
    raise KeyError(campo)


def peca_contida_na_ficha(svg, ficha):
    """`[problema]` — vazio quando cada texto da peça é valor da ficha ou frase fixa."""
    problemas = []
    por_campo = defaultdict(list)
    for campo, texto in textos_da_peca(svg):
        if not campo:
            problemas.append(f"texto sem campo: {texto!r}")
        elif campo == "fixo":
            if texto not in FIXOS.values():
                problemas.append(f"frase fixa fora do template: {texto!r}")
        else:
            por_campo[campo].append(texto)
    for campo, linhas in por_campo.items():
        try:
            esperado = _esperado(campo, ficha)
        except KeyError:
            problemas.append(f"campo desconhecido na peça: {campo}")
            continue
        if " ".join(linhas) != esperado:
            problemas.append(f"{campo}: a peça diz {' '.join(linhas)!r}, a ficha diz {esperado!r}")
    return problemas


def peca_contida_nos_textos(svg, ficha, textos):
    """Os dados que a peça mostra também estão no kit textual (datas, quantidades, número)."""
    corpo = "\n".join(textos.values())
    problemas = []
    campos = {campo for campo, _ in textos_da_peca(svg)}
    obrigatorios = [ficha["identificacao"]]
    if "periodo_curto" in campos:
        obrigatorios += [
            v for v in (ficha["inicio_data"], ficha["fim_data"], ficha["fim_hora"]) if v
        ]
    for campo in campos:
        if campo.startswith("oferta_quantidade:"):
            perfil = campo.partition(":")[2]
            oferta = next(o for o in ficha["ofertas"] if o["perfil_id"] == perfil)
            obrigatorios.append(f"{rotulo_da_oferta(oferta, ficha)}: {oferta['quantidade']}")
    if "total_de_vagas" in campos:
        obrigatorios.append(f"{ficha['total_de_vagas']} vagas")
    for valor in obrigatorios:
        if valor not in corpo:
            problemas.append(f"a peça mostra {valor!r}, e o kit textual não")
    return problemas


def vocabulario(ficha, textos, svg=None):
    """`[problema]` — juízo, tempo relativo, estado do momento; e inscrição onde não há período."""
    pedacos = list(textos.values())
    if svg:
        pedacos += [texto for _, texto in textos_da_peca(svg)]
    corpo = "\n".join(pedacos)
    problemas = [
        f"proibida: {padrao}" for padrao in PROIBIDAS if re.search(padrao, corpo, re.IGNORECASE)
    ]
    # As do portal já são expressões, com a caixa que cada uma decidiu: usadas como estão.
    problemas += [
        f"proibida pelo portal: {padrao}" for padrao in _do_portal() if re.search(padrao, corpo)
    ]
    if ficha["modo"] == NEUTRO and re.search(r"inscri", corpo, re.IGNORECASE):
        problemas.append("fala de inscrição num Edital sem período designado")
    return problemas
