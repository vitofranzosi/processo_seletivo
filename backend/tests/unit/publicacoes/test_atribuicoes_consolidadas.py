"""064 — As atribuições idênticas saem uma vez no documento do Edital.

Quando dois ou mais Perfis têm o mesmo texto de atribuições, o documento o imprime uma vez, numa
subseção comum ao fim da seção de Perfis, e cada Perfil remete ao número dela. Nada fora da
composição muda: nem o cadastro, nem o conteúdo, nem tela, nem documento já guardado.

**Duas famílias de teste, e a separação é de propósito.** A regra de identidade (FR-1187, FR-1188)
é provada sobre a função de agrupamento, sem compor PDF — é ali que o caractere que o documento não
representa pode entrar, porque nada é impresso. Todo o resto é provado **lendo o documento
composto**, com o leitor `atribuicoes_no_documento`: o que o FR-1191 afirma é sobre o artefato que o
candidato lê, e provar só a função provaria a regra, e não o documento (D-006).

**Os cenários que compõem PDF usam só caracteres que o documento representa.** A troca do que ele
não representa por "?" é defeito tratado fora desta feature, e não pode entrar no resultado destes.
"""

import copy
import re

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import (
    CORPO_TEXTO,
    MODO_PREVIA,
    NEGRITO,
    grupos_de_atribuicoes,
    numeracao,
)
from tests.unit.publicacoes.test_pdf import (
    documento,
    linhas_desenhadas,
    paginas_de,
    snapshot,
    texto_de,
)

# ---------------------------------------------------------------------------
# Cenários
# ---------------------------------------------------------------------------

ITENS = (
    "Conhecer a proposta da Instituição e o projeto pedagógico do curso.",
    "Contribuir nas atividades síncronas e assíncronas do ambiente virtual.",
    "Elaborar relatórios das suas atividades conforme o modelo do curso.",
)
OUTROS = (
    "Orientar os estudantes nas atividades presenciais do polo.",
    "Organizar salas e equipamentos para as atividades presenciais.",
)


def texto(*itens):
    return "\n".join(itens)


def perfil(codigo, atribuicoes, *, denominacao="Tutor presencial", numero=1, **outros):
    """Um Perfil do cenário-base de `test_pdf`, com identidade, código e atribuições próprios."""
    base = snapshot()["profiles"][0]
    return {
        **base,
        "id": f"33333333-3333-3333-3333-{numero:012d}",
        "code": codigo,
        "name": denominacao,
        "duties": atribuicoes,
        **outros,
    }


def edital(*perfis):
    return snapshot(profiles=list(perfis))


def codigos(grupos):
    return [[item["code"] for item in grupo] for grupo in grupos]


def agrupados(*pares):
    """Os grupos de uma lista de `(código, atribuições)`, pelos códigos."""
    return codigos(grupos_de_atribuicoes([{"code": c, "duties": d} for c, d in pares]))


# ---------------------------------------------------------------------------
# A leitura do documento (D-006)
# ---------------------------------------------------------------------------

# O corpo de texto é o menor corpo do que interessa aqui. O que é menor — rodapé, marca de prévia,
# célula de tabela — fica de fora, e é isso que deixa o leitor atravessar páginas e quadros.
TITULO_DE_SECAO = re.compile(r"^\d+\. ")


def secao_de_perfis(conteudo):
    chave = next(item["key"] for item in conteudo["sections"] if item.get("source") == "profiles")
    return numeracao(conteudo)[chave]


def _corpo(pdf):
    return [
        (texto_da_linha, fonte, recuo)
        for texto_da_linha, fonte, tamanho, recuo in linhas_desenhadas(pdf)
        if tamanho >= CORPO_TEXTO
    ]


def _e_titulo(linha, secao):
    texto_da_linha, fonte, recuo = linha
    if fonte != NEGRITO or recuo != 0:
        return False
    return bool(
        re.match(rf"^{secao}\.\d+ ", texto_da_linha) or TITULO_DE_SECAO.match(texto_da_linha)
    )


def atribuicoes_no_documento(pdf, conteudo):
    """De onde cada Perfil tira as atribuições no documento, e quais são.

    Devolve `({código: (fonte, [parágrafos])}, {número: título})`. `fonte` é `"própria"` quando o
    Perfil traz o próprio bloco, o número do item quando remete, e `None` quando não há atribuição
    nenhuma. O segundo dicionário são as subseções comuns que o documento imprime.

    **A delimitação é pelo recuo**, que é como o documento distingue os níveis. O bloco próprio são
    as linhas depois do rótulo "Atribuições" (negrito, recuo 18) até a primeira com recuo menor que
    32 — os requisitos também saem com recuo 32, mas o rótulo "Requisitos", com recuo 18, os separa.
    A remissão é o rótulo "Atribuições:" seguido do valor na mesma linha. A subseção comum são as
    linhas de recuo 18 depois do título dela, até o próximo título.

    Os cenários que passam por aqui usam itens de uma linha cada: cada linha desenhada é um
    parágrafo.
    """
    secao = secao_de_perfis(conteudo)
    linhas = _corpo(pdf)
    titulos = [indice for indice, linha in enumerate(linhas) if _e_titulo(linha, secao)]

    def trecho(inicio):
        seguintes = [indice for indice in titulos if indice > inicio]
        return linhas[inicio + 1 : seguintes[0] if seguintes else len(linhas)]

    comuns, por_numero = {}, {}
    for indice in titulos:
        numero, _, resto = linhas[indice][0].partition(" ")
        if not numero.startswith(f"{secao}."):
            continue
        por_numero[numero] = indice
        if resto.startswith("Atribuições comuns aos Perfis "):
            # O título longo quebra em mais de uma linha, todas em negrito e sem recuo.
            corpo = trecho(indice)
            continuacao = []
            while corpo and corpo[0][1] == NEGRITO and corpo[0][2] == 0:
                continuacao.append(corpo.pop(0)[0])
            titulo = " ".join([resto, *continuacao])
            paragrafos = []
            for texto_da_linha, fonte, recuo in corpo:
                if fonte == NEGRITO or recuo < 18:
                    break
                paragrafos.append(texto_da_linha)
            comuns[numero] = (titulo, paragrafos)

    resultado = {}
    for ordem, item in enumerate(conteudo["profiles"], 1):
        corpo = trecho(por_numero[f"{secao}.{ordem}"])
        fonte, paragrafos = None, []
        for posicao, (texto_da_linha, fonte_da_linha, recuo) in enumerate(corpo):
            if fonte_da_linha != NEGRITO or recuo != 18:
                continue
            if texto_da_linha == "Atribuições":
                fonte = "própria"
                for seguinte, _, recuo_seguinte in corpo[posicao + 1 :]:
                    if recuo_seguinte < 32:
                        break
                    paragrafos.append(seguinte)
                break
            if texto_da_linha == "Atribuições:":
                valor = corpo[posicao + 1][0]
                encontrado = re.fullmatch(r"as descritas no item (\S+)\.", valor)
                assert encontrado, f"remissão em forma inesperada: {valor!r}"
                fonte = encontrado.group(1)
                paragrafos = list(comuns.get(fonte, (None, []))[1])
                break
        resultado[item["code"]] = (fonte, paragrafos)
    return resultado, {numero: titulo for numero, (titulo, _) in comuns.items()}


def codigos_do_titulo(titulo):
    """Os códigos que o título da subseção comum nomeia, na ordem.

    Entre aspas quando algum código tem a vírgula ou o " e " da enumeração; sem elas, separados por
    esses dois.
    """
    lista = titulo.removeprefix("Atribuições comuns aos Perfis ")
    if "“" in lista:
        return re.findall(r"“(.*?)”", lista)
    *iniciais, ultimo = lista.split(" e ")
    return [parte for trecho in iniciais for parte in trecho.split(", ")] + [ultimo]


def paragrafos_do_snapshot(atribuicoes):
    """Os parágrafos do FR-1187, escritos aqui de novo, e não importados.

    Reusar a função do renderizador faria um defeito dela aparecer dos dois lados da comparação, e
    o teste de integridade passaria comparando o erro com ele mesmo.
    """
    return [
        " ".join(linha.split())
        for linha in re.split(r"[\r\n]+", atribuicoes or "")
        if linha.strip()
    ]


# ---------------------------------------------------------------------------
# A regra de identidade (FR-1187, FR-1188) — sem compor documento
# ---------------------------------------------------------------------------


def test_textos_identicos_agrupam():
    assert agrupados(("A", texto(*ITENS)), ("B", texto(*ITENS))) == [["A", "B"]]


@pytest.mark.parametrize(
    "variante",
    [
        "Conhecer  a   proposta.\nContribuir nas atividades.",
        "Conhecer a proposta.   \n   Contribuir nas atividades.  ",
        "Conhecer a proposta.\n\n\nContribuir nas atividades.",
        "Conhecer a proposta.\n   \n\t\nContribuir nas atividades.",
        "\n\nConhecer a proposta.\r\nContribuir nas atividades.\n\n",
    ],
    ids=["espaco-repetido", "espaco-nas-pontas", "linhas-em-branco", "linha-so-de-espaco", "crlf"],
)
def test_o_que_o_documento_nao_distingue_nao_impede(variante):
    """FR-1187: quanto espaço e quantas linhas em branco não conta; o documento não os imprime."""
    canonico = "Conhecer a proposta.\nContribuir nas atividades."
    assert agrupados(("A", canonico), ("B", variante)) == [["A", "B"]]


@pytest.mark.parametrize(
    "variante",
    [
        "Conhecer a proposta. Contribuir nas atividades.",
        "Conhecer a\nproposta.\nContribuir nas atividades.",
        "Conhecer a proposta;\nContribuir nas atividades.",
        "conhecer a proposta.\nContribuir nas atividades.",
        "Conhecer a propôsta.\nContribuir nas atividades.",
        "Contribuir nas atividades.\nConhecer a proposta.",
        "Conhecer a proposta.",
    ],
    ids=[
        "quebra-a-menos",
        "quebra-a-mais",
        "pontuacao",
        "maiuscula",
        "acento",
        "outra-ordem",
        "subconjunto",
    ],
)
def test_o_que_o_documento_distingue_impede(variante):
    """FR-1187, FR-1188: a quebra de linha é fronteira de parágrafo e conta, como letra e ordem."""
    canonico = "Conhecer a proposta.\nContribuir nas atividades."
    assert agrupados(("A", canonico), ("B", variante)) == []


@pytest.mark.parametrize(
    ("um", "outro"),
    [
        ("● Conhecer a proposta.", "▪ Conhecer a proposta."),
        ("● Conhecer a proposta.", "• Conhecer a proposta."),
        ("●\u200b Conhecer a proposta.", "● Conhecer a proposta."),
        ("Seleção do curso.", "Selec\u0327a\u0303o do curso."),
    ],
    ids=["bolinha-e-quadrado", "bolinha-e-marcador", "largura-zero", "nfc-e-nfd"],
)
def test_o_que_a_grafia_normaliza_nao_impede(um, outro):
    """FR-1187: a comparação é do texto normalizado, que é o que o documento imprime.

    Marcadores cheios viram `•`, o invisível some e o decomposto se compõe — o significado
    sobrevive, e o documento imprime os dois iguais. Agrupam, na função e no documento.
    """
    assert agrupados(("A", um), ("B", outro)) == [["A", "B"]]
    conteudo = edital(perfil("A", um, numero=1), perfil("B", outro, numero=2))
    assert "Atribuições comuns aos Perfis A e B" in texto_de(documento(conteudo, modo=MODO_PREVIA))


def test_caracteres_sem_grafia_diferentes_nao_se_juntam():
    """Caso-limite: o que a grafia não normaliza continua distinto — `≥` não é `≤`.

    Na prévia, cada um aparece como o próprio código, e não como o mesmo "?"; na publicação, os
    dois são recusados antes de compor.
    """
    um, outro = "Nota ≥ 7 no curso.", "Nota ≤ 7 no curso."
    assert agrupados(("A", um), ("B", outro)) == []
    conteudo = edital(perfil("A", um, numero=1), perfil("B", outro, numero=2))
    previa = texto_de(documento(conteudo, modo=MODO_PREVIA))
    assert "Atribuições comuns" not in previa
    assert "[U+2265]" in previa and "[U+2264]" in previa


def test_texto_vazio_nunca_agrupa():
    assert agrupados(("A", ""), ("B", ""), ("C", "  \n \n")) == []


def test_edital_de_um_perfil_nao_tem_grupo():
    assert agrupados(("A", texto(*ITENS))) == []


def test_mesma_denominacao_e_textos_diferentes_nao_agrupam():
    perfis = [
        {"code": "A", "name": "Tutor presencial", "duties": texto(*ITENS)},
        {"code": "B", "name": "Tutor presencial", "duties": texto(*OUTROS)},
    ]
    assert grupos_de_atribuicoes(perfis) == []


def test_denominacoes_diferentes_e_o_mesmo_texto_agrupam():
    """A denominação nunca entra na pergunta: o título da subseção nomeia os códigos (FR-1188)."""
    perfis = [
        {"code": "A", "name": "Tutor presencial", "duties": texto(*ITENS)},
        {"code": "B", "name": "Tutor a distância", "duties": texto(*ITENS)},
    ]
    assert codigos(grupos_de_atribuicoes(perfis)) == [["A", "B"]]


def test_os_grupos_seguem_a_ordem_do_primeiro_perfil_de_cada_um():
    """D-003: o grupo nasce no primeiro Perfil que o tem; os Perfis dele, na ordem do snapshot."""
    x, y = texto(*ITENS), texto(*OUTROS)
    assert agrupados(("A", y), ("B", x), ("C", y), ("D", "próprio"), ("E", x), ("F", y)) == [
        ["A", "C", "F"],
        ["B", "E"],
    ]


def test_cada_perfil_esta_em_no_maximo_um_grupo():
    x, y = texto(*ITENS), texto(*OUTROS)
    grupos = agrupados(("A", x), ("B", y), ("C", x), ("D", y), ("E", x))
    todos = [codigo for grupo in grupos for codigo in grupo]
    assert sorted(todos) == sorted(set(todos))


def test_agrupar_nao_altera_os_perfis():
    perfis = [{"code": "A", "duties": texto(*ITENS)}, {"code": "B", "duties": texto(*ITENS)}]
    antes = copy.deepcopy(perfis)
    grupos_de_atribuicoes(perfis)
    assert perfis == antes


# ---------------------------------------------------------------------------
# US1 — Quem elabora vê, na prévia, as atribuições comuns uma vez só
# ---------------------------------------------------------------------------


def _remissoes(pdf):
    """Os pares `Atribuições:` → valor, na ordem em que aparecem."""
    linhas = _corpo(pdf)
    return [
        linhas[indice + 1][0]
        for indice, (texto_da_linha, fonte, _) in enumerate(linhas)
        if texto_da_linha == "Atribuições:" and fonte == NEGRITO
    ]


def test_dois_perfis_iguais_saem_numa_subsecao_comum_com_remissao():
    """US1/1, FR-1186, FR-1189, FR-1190: o texto uma vez, ao fim da seção, nomeando os códigos."""
    conteudo = edital(
        perfil("TUT-ALE", texto(*ITENS), numero=1), perfil("TUT-BGU", texto(*ITENS), numero=2)
    )
    pdf = documento(conteudo)
    secao = secao_de_perfis(conteudo)

    fontes, comuns = atribuicoes_no_documento(pdf, conteudo)

    assert comuns == {f"{secao}.3": "Atribuições comuns aos Perfis TUT-ALE e TUT-BGU"}
    assert fontes == {
        "TUT-ALE": (f"{secao}.3", list(ITENS)),
        "TUT-BGU": (f"{secao}.3", list(ITENS)),
    }
    assert _remissoes(pdf) == [f"as descritas no item {secao}.3."] * 2
    for item in ITENS:
        assert texto_de(pdf).count(item) == 1, item


@pytest.mark.parametrize(
    "segundo",
    [
        pytest.param(texto(*OUTROS), id="textos-diferentes"),
        pytest.param(texto(*ITENS[:2]), id="subconjunto"),
    ],
)
def test_o_que_nao_e_identico_sai_inteiro_em_cada_perfil(segundo):
    """US1/2 e US1/3, FR-1188: sem subseção comum, e cada texto inteiro no próprio Perfil."""
    conteudo = edital(perfil("A", texto(*ITENS), numero=1), perfil("B", segundo, numero=2))
    pdf = documento(conteudo)

    fontes, comuns = atribuicoes_no_documento(pdf, conteudo)

    assert comuns == {}
    assert _remissoes(pdf) == []
    assert fontes == {
        "A": ("própria", paragrafos_do_snapshot(texto(*ITENS))),
        "B": ("própria", paragrafos_do_snapshot(segundo)),
    }


def test_a_mesma_denominacao_nao_junta_textos_diferentes():
    """US1/4: dois "Tutor presencial" de textos diferentes continuam cada um com o seu."""
    conteudo = edital(
        perfil("A", texto(*ITENS), denominacao="Tutor presencial", numero=1),
        perfil("B", texto(*OUTROS), denominacao="Tutor presencial", numero=2),
    )
    fontes, comuns = atribuicoes_no_documento(documento(conteudo), conteudo)
    assert comuns == {}
    assert {codigo: fonte for codigo, (fonte, _) in fontes.items()} == {
        "A": "própria",
        "B": "própria",
    }


def test_dois_grupos_saem_em_duas_subsecoes_na_ordem_do_primeiro_perfil():
    """Caso-limite, FR-1189: numeradas em continuação aos Perfis, cada Perfil remetendo à sua."""
    x, y = texto(*ITENS), texto(*OUTROS)
    conteudo = edital(
        perfil("A", y, numero=1),
        perfil("B", x, numero=2),
        perfil("C", y, numero=3),
        perfil("D", x, numero=4),
    )
    secao = secao_de_perfis(conteudo)

    fontes, comuns = atribuicoes_no_documento(documento(conteudo), conteudo)

    assert comuns == {
        f"{secao}.5": "Atribuições comuns aos Perfis A e C",
        f"{secao}.6": "Atribuições comuns aos Perfis B e D",
    }
    assert {codigo: fonte for codigo, (fonte, _) in fontes.items()} == {
        "A": f"{secao}.5",
        "B": f"{secao}.6",
        "C": f"{secao}.5",
        "D": f"{secao}.6",
    }


def test_todos_os_perfis_no_mesmo_grupo_sao_nomeados_no_titulo():
    conteudo = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate("ABC", 1)))
    secao = secao_de_perfis(conteudo)
    _, comuns = atribuicoes_no_documento(documento(conteudo), conteudo)
    assert comuns == {f"{secao}.4": "Atribuições comuns aos Perfis A, B e C"}


def test_o_perfil_de_texto_proprio_entre_os_agrupados_continua_no_lugar():
    """Caso-limite: o de texto próprio fica intacto, e a numeração dos Perfis não se move."""
    conteudo = edital(
        perfil("A", texto(*ITENS), numero=1),
        perfil("B", texto(*OUTROS), numero=2),
        perfil("C", texto(*ITENS), numero=3),
        perfil("D", texto(*ITENS), numero=4),
    )
    secao = secao_de_perfis(conteudo)
    pdf = documento(conteudo)

    fontes, comuns = atribuicoes_no_documento(pdf, conteudo)

    assert fontes["B"] == ("própria", list(OUTROS))
    assert comuns == {f"{secao}.5": "Atribuições comuns aos Perfis A, C e D"}
    titulos = [t for t, _, _ in _corpo(pdf) if re.match(rf"^{secao}\.[1-4] ", t)]
    assert titulos == [f"{secao}.{n} {c} — Tutor presencial" for n, c in enumerate("ABCD", 1)]


def test_texto_vazio_nao_imprime_rotulo_nem_subsecao():
    """Caso-limite, FR-1188: como hoje, nenhum "Atribuições" sobre nada."""
    conteudo = edital(perfil("A", "", numero=1), perfil("B", "", numero=2))
    pdf = documento(conteudo)
    assert "Atribuições" not in texto_de(pdf)


def test_dez_perfis_de_mesmo_texto_imprimem_o_texto_uma_vez():
    """SC-457: o caso do Edital 90/2026 — dez polos, o mesmo texto, uma vez, dez remissões."""
    conteudo = edital(*(perfil(f"P{n:02d}", texto(*ITENS), numero=n) for n in range(1, 11)))
    secao = secao_de_perfis(conteudo)
    pdf = documento(conteudo)

    for item in ITENS:
        assert texto_de(pdf).count(item) == 1, item
    assert _remissoes(pdf) == [f"as descritas no item {secao}.11."] * 10


def _distintos(conteudo):
    """O mesmo Edital, com o texto de cada Perfil tornado próprio — a mesma quantidade de itens."""
    return {
        **conteudo,
        "profiles": [
            {
                **item,
                "duties": "\n".join(
                    f"{linha} ({item['code']})" for linha in item["duties"].split("\n")
                ),
            }
            for item in conteudo["profiles"]
        ],
    }


def _numeros(pdf, secao, quantidade):
    """Os títulos de subseção de Perfil, os de seção e as legendas de tabela, na ordem."""
    corpo = _corpo(pdf)
    subsecao = re.compile(rf"^{secao}\.(\d+) ")
    return {
        "perfis": [
            t for t, _, _ in corpo if (m := subsecao.match(t)) and int(m.group(1)) <= quantidade
        ],
        "secoes": [t for t, f, r in corpo if f == NEGRITO and r == 0 and TITULO_DE_SECAO.match(t)],
        "tabelas": [t for t in texto_de(pdf).splitlines() if t.startswith("Tabela ")],
    }


def test_a_numeracao_dos_perfis_das_secoes_e_das_tabelas_nao_se_move():
    """FR-1192, SC-459: com e sem consolidação, os mesmos números — e a subseção não abre tabela."""
    agrupado = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate("ABC", 1)))
    distinto = _distintos(agrupado)
    secao = secao_de_perfis(agrupado)

    com, sem = documento(agrupado), documento(distinto)

    assert "Atribuições comuns" in texto_de(com) and "Atribuições comuns" not in texto_de(sem)
    assert _numeros(com, secao, 3) == _numeros(sem, secao, 3)
    assert numeracao(agrupado) == numeracao(distinto)


def test_os_demais_blocos_continuam_em_cada_perfil():
    """FR-1197: requisitos, remuneração, quadros e modalidades não se consolidam."""
    agrupado = edital(
        *(
            perfil(c, texto(*ITENS), numero=n, compensation="R$ 1.100,00 mensais")
            for n, c in enumerate("ABC", 1)
        )
    )
    com, sem = texto_de(documento(agrupado)), texto_de(documento(_distintos(agrupado)))
    for marca in ("Requisitos", "• Mestrado em Computação", "Remuneração: R$ 1.100,00 mensais"):
        assert com.count(marca) == sem.count(marca) == 3, marca
    assert com.count("Modalidades de concorrência") == sem.count("Modalidades de concorrência") == 3


def _pagina_de(paginas, predicado):
    return [numero for numero, pagina in enumerate(paginas, 1) if any(predicado(t) for t in pagina)]


def test_a_subsecao_comum_maior_que_a_pagina_quebra_entre_paragrafos_e_conclui():
    """FR-1193: o último degrau da cascata existe também para ela."""
    itens = [
        f"Atribuição {n}: acompanhar os estudantes nas atividades do curso." for n in range(1, 81)
    ]
    conteudo = edital(perfil("A", texto(*itens), numero=1), perfil("B", texto(*itens), numero=2))
    paginas = paginas_de(documento(conteudo))

    onde = _pagina_de(paginas, lambda t: t.startswith("Atribuição "))
    assert len(onde) >= 2, "oitenta itens deveriam ocupar mais de uma página"
    todas = [t for pagina in paginas for t in pagina if t.startswith("Atribuição ")]
    assert todas == itens, "nenhum item perdido nem repetido entre as páginas"
    titulo = _pagina_de(paginas, lambda t: "Atribuições comuns aos Perfis" in t)
    assert len(titulo) == 1 and titulo[0] in onde, "o título ficou sozinho, longe do primeiro item"


@pytest.mark.parametrize("enchimento", range(0, 40, 3))
def test_a_subsecao_comum_que_cabe_numa_pagina_sai_inteira_e_o_titulo_nunca_fica_sozinho(
    enchimento,
):
    """FR-1193: inteira na página seguinte quando couber nela; título nunca no fim da página.

    O enchimento varia o quanto da página o último Perfil ocupa, para que em alguma das variantes a
    subseção comum comece perto do rodapé — que é onde um bloco que não salta inteiro se partiria.
    """
    itens = [
        f"Atribuição {n}: acompanhar os estudantes nas atividades do curso." for n in range(1, 26)
    ]
    proprio = [f"Tarefa própria {n} do último Perfil." for n in range(1, enchimento + 2)]
    conteudo = edital(
        perfil("A", texto(*itens), numero=1),
        perfil("B", texto(*itens), numero=2),
        perfil("C", texto(*proprio), numero=3),
    )
    paginas = paginas_de(documento(conteudo))

    titulo = _pagina_de(paginas, lambda t: "Atribuições comuns aos Perfis" in t)
    corpo = _pagina_de(paginas, lambda t: t.startswith("Atribuição "))
    assert len(titulo) == 1
    assert corpo == titulo, f"a subseção que cabe numa página saiu partida: {titulo} e {corpo}"


def test_edital_de_um_perfil_nao_tem_subsecao_comum_nem_remissao():
    """FR-1194: o documento de um Perfil é o de antes — a fixture byte a byte prende os bytes."""
    conteudo = edital(perfil("A", texto(*ITENS), numero=1))
    pdf = documento(conteudo)
    assert "Atribuições comuns" not in texto_de(pdf)
    assert _remissoes(pdf) == []
    fontes, _ = atribuicoes_no_documento(pdf, conteudo)
    assert fontes == {"A": ("própria", list(ITENS))}


# ---------------------------------------------------------------------------
# US2 — O candidato encontra as atribuições do seu Perfil, sem ambiguidade (FR-1191)
# ---------------------------------------------------------------------------

X, Y, Z = texto(*ITENS), texto(*OUTROS), texto(ITENS[0], OUTROS[1])
CENARIOS_DE_INTEGRIDADE = {
    "dois-iguais": [("A", X), ("B", X)],
    "diferentes": [("A", X), ("B", Y)],
    "subconjunto": [("A", X), ("B", texto(*ITENS[:2]))],
    "dois-grupos": [("A", Y), ("B", X), ("C", Y), ("D", X)],
    "todos": [("A", X), ("B", X), ("C", X)],
    "proprio-entre-agrupados": [("A", X), ("B", Y), ("C", X), ("D", X)],
    "vazios-e-agrupados": [("A", ""), ("B", X), ("C", ""), ("D", X)],
    "dez-polos": [(f"P{n:02d}", X) for n in range(1, 11)],
    "misto": [
        ("A", X),
        ("B", Y),
        ("C", "Tarefa só do C."),
        ("D", Z),
        ("E", X),
        ("F", Z),
        ("G", Y),
        ("H", "Tarefa só do H."),
    ],
}


@pytest.mark.parametrize("nome", list(CENARIOS_DE_INTEGRIDADE))
def test_cada_perfil_tem_no_documento_exatamente_as_atribuicoes_da_versao(nome):
    """FR-1191, SC-458: reconstruídas pelo documento, as atribuições são as da versão.

    Para cada Perfil: (a) uma fonte só — o próprio bloco ou uma remissão —, e nenhuma quando o texto
    é vazio; (b) os parágrafos lidos são os do snapshot, na mesma ordem, nenhum acrescentado,
    omitido ou trocado; (c) a remissão aponta subseção do mesmo documento cujo título nomeia o
    Perfil; (d) cada subseção comum é apontada por todos os Perfis que o título dela nomeia, e por
    nenhum outro.
    """
    conteudo = edital(
        *(
            perfil(codigo, atribuicoes, numero=n)
            for n, (codigo, atribuicoes) in enumerate(CENARIOS_DE_INTEGRIDADE[nome], 1)
        )
    )
    pdf = documento(conteudo)

    fontes, comuns = atribuicoes_no_documento(pdf, conteudo)

    for item in conteudo["profiles"]:
        fonte, lidos = fontes[item["code"]]
        esperados = paragrafos_do_snapshot(item["duties"])
        if not esperados:
            assert fonte is None and lidos == [], item["code"]
            continue
        assert fonte is not None, f"{item['code']} ficou sem atribuições no documento"
        # O alvo antes do conteúdo: uma remissão para item que não existe deixa o leitor sem
        # parágrafo nenhum, e a falha tem de dizer isso, e não que os parágrafos diferem.
        if fonte != "própria":
            assert fonte in comuns, f"{item['code']} remete a {fonte}, que não existe"
            assert item["code"] in codigos_do_titulo(comuns[fonte]), item["code"]
        assert lidos == esperados, item["code"]
    for numero, titulo in comuns.items():
        nomeados = codigos_do_titulo(titulo)
        apontam = [codigo for codigo, (fonte, _) in fontes.items() if fonte == numero]
        assert nomeados == apontam, numero
    # E o documento não tem atribuição que a versão não tenha: cada rótulo é de um Perfil.
    rotulos = [
        t for t, f, r in _corpo(pdf) if f == NEGRITO and r == 18 and t.startswith("Atribuições")
    ]
    assert len(rotulos) == sum(1 for item in conteudo["profiles"] if item["duties"].strip())


def test_o_item_de_varias_linhas_sai_palavra_a_palavra():
    """FR-1191: o parágrafo que quebra em várias linhas chega inteiro à subseção comum."""
    longo = (
        "Participar de reuniões e capacitações ofertadas pelo Ifes e pelos polos, presenciais ou "
        "não, com o Coordenador de Tutoria, o Professor Formador e a Coordenação do Curso, nos "
        "campi do Ifes, sendo o custo do deslocamento para os encontros de responsabilidade "
        "do tutor."
    )
    atribuicoes = texto(ITENS[0], longo, ITENS[1])
    conteudo = edital(perfil("A", atribuicoes, numero=1), perfil("B", atribuicoes, numero=2))
    linhas = _corpo(documento(conteudo))

    inicio = next(i for i, (t, _, _) in enumerate(linhas) if "Atribuições comuns aos Perfis" in t)
    corpo = []
    for texto_da_linha, fonte, recuo in linhas[inicio + 1 :]:
        if fonte == NEGRITO or recuo < 18:
            break
        corpo.append(texto_da_linha)

    assert len(corpo) > 3, "o item longo deveria ocupar mais de uma linha"
    assert " ".join(corpo).split() == atribuicoes.split()


def test_as_remissoes_do_texto_livre_continuam_apontando_o_mesmo_lugar():
    """US2/3: "item 11.2" e "Tabela 3" no texto do Edital apontam o que apontavam."""
    agrupado = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate("ABC", 1)))
    for secao in agrupado["sections"]:
        if secao.get("content") and secao["key"] != "apresentacao":
            secao["content"] = "Conforme o item 11.2 e a Tabela 3 deste Edital."
            break
    secao = secao_de_perfis(agrupado)
    com, sem = documento(agrupado), documento(_distintos(agrupado))

    assert "Conforme o item 11.2 e a Tabela 3 deste Edital." in texto_de(com)
    assert _numeros(com, secao, 3) == _numeros(sem, secao, 3)


# ---------------------------------------------------------------------------
# US3 — O que já foi publicado não muda, e o que se publicar depois é coerente
# ---------------------------------------------------------------------------


def test_o_perfil_acrescentado_com_o_mesmo_texto_entra_no_grupo():
    """Caso-limite: a Retificação que acrescenta Perfil compõe a versão resultante pela regra."""
    base = edital(perfil("A", texto(*ITENS), numero=1), perfil("B", texto(*ITENS), numero=2))
    retificado = {**base, "profiles": [*base["profiles"], perfil("C", texto(*ITENS), numero=3)]}
    secao = secao_de_perfis(retificado)

    _, antes = atribuicoes_no_documento(documento(base), base)
    _, depois = atribuicoes_no_documento(documento(retificado), retificado)

    assert antes == {f"{secao}.3": "Atribuições comuns aos Perfis A e B"}
    assert depois == {f"{secao}.4": "Atribuições comuns aos Perfis A, B e C"}


def test_o_grupo_reduzido_a_um_perfil_se_desfaz():
    """Caso-limite: sobrando um, ele volta a trazer o próprio texto, e não há subseção comum."""
    base = edital(perfil("A", texto(*ITENS), numero=1), perfil("B", texto(*ITENS), numero=2))
    retificado = {
        **base,
        "profiles": [base["profiles"][0], {**base["profiles"][1], "duties": texto(*OUTROS)}],
    }

    fontes, comuns = atribuicoes_no_documento(documento(retificado), retificado)

    assert comuns == {}
    assert fontes == {"A": ("própria", list(ITENS)), "B": ("própria", list(OUTROS))}


def test_compor_nao_toca_o_conteudo_nem_a_impressao_digital_dele():
    """FR-1195: a consolidação existe só na composição — o conteúdo que entra é o que sai."""
    from processo_seletivo.shared.canonical import canonical_sha256

    conteudo = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate("ABC", 1)))
    antes, resumo = copy.deepcopy(conteudo), canonical_sha256(conteudo)

    documento(conteudo)
    documento(conteudo, modo=MODO_PREVIA)

    assert conteudo == antes
    assert canonical_sha256(conteudo) == resumo


# ---------------------------------------------------------------------------
# Da revisão de código: o título que nomeia os códigos, e o lugar da remissão
# ---------------------------------------------------------------------------


def _titulo_da_subsecao_comum(pdf):
    """As linhas do título da subseção comum, como foram desenhadas."""
    linhas = _corpo(pdf)
    inicio = next(i for i, (t, _, _) in enumerate(linhas) if "Atribuições comuns aos Perfis" in t)
    titulo = [linhas[inicio][0]]
    for texto_da_linha, fonte, recuo in linhas[inicio + 1 :]:
        if fonte != NEGRITO or recuo != 0:
            break
        titulo.append(texto_da_linha)
    return titulo


def test_o_titulo_quebra_entre_os_codigos_e_nunca_dentro_de_um():
    """FR-1189: "ADS - P06" não sai como "ADS" numa linha e "- P06" na outra.

    São os códigos dos polos do Edital 90/2026, com espaço dentro. Dez deles não cabem numa linha,
    e a quebra por palavra caía no meio de um.
    """
    codigos = [f"ADS - P{n:02d}" for n in range(1, 11)]
    conteudo = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate(codigos, 1)))

    titulo = _titulo_da_subsecao_comum(documento(conteudo))

    assert len(titulo) > 1, "o cenário precisa de um título em mais de uma linha"
    for codigo in codigos:
        assert sum(codigo in linha for linha in titulo) == 1, f"{codigo} partido: {titulo}"
    assert codigos_do_titulo(" ".join(titulo).partition(" ")[2]) == codigos


@pytest.mark.parametrize(
    ("codigos", "esperado"),
    [
        (["Tutor e Mediador", "TEC"], "Atribuições comuns aos Perfis “Tutor e Mediador” e “TEC”"),
        (["Polo A, Serra", "Polo B"], "Atribuições comuns aos Perfis “Polo A, Serra” e “Polo B”"),
        (["ADS - ALE", "ADS – BGU"], "Atribuições comuns aos Perfis ADS - ALE e ADS – BGU"),
    ],
    ids=["e-no-codigo", "virgula-no-codigo", "sem-ambiguidade"],
)
def test_codigo_com_o_separador_da_enumeracao_vai_entre_aspas(codigos, esperado):
    """FR-1189: "Tutor e Mediador e TEC" se lê como três Perfis; entre aspas, como dois.

    As aspas valem para o grupo inteiro, para que o título tenha uma regra de leitura só; sem
    ambiguidade, não há aspas, como antes.
    """
    conteudo = edital(*(perfil(c, texto(*ITENS), numero=n) for n, c in enumerate(codigos, 1)))
    secao = secao_de_perfis(conteudo)

    fontes, comuns = atribuicoes_no_documento(documento(conteudo), conteudo)

    assert comuns == {f"{secao}.3": esperado}
    assert codigos_do_titulo(esperado) == codigos
    assert {fonte for fonte, _ in fontes.values()} == {f"{secao}.3"}


def test_a_remissao_fica_no_lugar_do_bloco_em_negrito_e_com_o_espaco_de_sub_bloco():
    """FR-1190 e o contrato: entre a Descrição e a Remuneração, "Atribuições:" em negrito, e com o
    mesmo espaço acima que o cabeçalho "Atribuições" do Perfil de texto próprio."""
    from processo_seletivo.publicacoes.infrastructure import pdf as renderizador

    conteudo = edital(
        perfil("A", texto(*ITENS), numero=1, compensation="R$ 1.100,00 mensais"),
        perfil("B", texto(*ITENS), numero=2, compensation="R$ 1.100,00 mensais"),
        perfil("C", texto(*OUTROS), numero=3, compensation="R$ 1.100,00 mensais"),
    )
    secao = secao_de_perfis(conteudo)
    linhas = _corpo(documento(conteudo))

    inicio = next(i for i, (t, _, _) in enumerate(linhas) if t.startswith(f"{secao}.1 A — "))
    seguintes = [(t, f) for t, f, _ in linhas[inicio + 1 : inicio + 5]]
    assert seguintes == [
        ("Docência em Informática.", renderizador.REGULAR),
        ("Atribuições:", NEGRITO),
        (f"as descritas no item {secao}.4.", renderizador.REGULAR),
        ("Remuneração: R$ 1.100,00 mensais", renderizador.REGULAR),
    ]

    # O espaço acima, lido na composição: o mesmo degrau para a remissão e para o cabeçalho.
    composicao = renderizador.Composicao()
    renderizador._perfis(composicao, conteudo, secao, renderizador._Numerador())
    antes = {
        item[1]: item[5]
        for item in composicao.itens
        if item[0] == "texto" and item[1] in ("Atribuições:", "Atribuições")
    }
    assert antes["Atribuições:"] == antes["Atribuições"] == renderizador.ANTES_DE_BLOCO
