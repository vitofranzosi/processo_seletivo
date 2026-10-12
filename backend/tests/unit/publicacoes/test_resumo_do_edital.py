"""O resumo do Edital, feito só de dado (069, FR-1370, FR-1371, R-010).

O resumo diz, nas palavras do candidato, quantas vagas há e onde, se há cadastro de reserva, quando
são as inscrições, quantas cada um pode fazer e como será a seleção — cada linha com o item em que
a regra completa está. Não diz nada que o snapshot não diga: a linha que dependeria de uma
generalização que o dado não sustenta não sai.
"""

import copy

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.publicacoes.infrastructure import apresentacao, pdf
from tests.unit.publicacoes.cenarios_da_auditoria import congelado, levado_ao_catalogo_novo
from tests.unit.publicacoes.test_pdf import secoes, snapshot


def _do_cenario(cenario):
    return levado_ao_catalogo_novo(congelado(cenario)["content"])


def _resumo(conteudo):
    conteudo = pdf._grafado(conteudo, previa=False)
    return dict(apresentacao.linhas_do_resumo(conteudo, apresentacao.plano(conteudo)))


def _numero(conteudo, titulo):
    return apresentacao.plano(pdf._grafado(conteudo, previa=False)).numero_da(titulo)


def test_em_a_as_vagas_por_localidade_e_o_cadastro_por_extenso():
    conteudo = _do_cenario("A")
    resumo = _resumo(conteudo)
    item = _numero(conteudo, "Quantas vagas há, e onde?")
    assert resumo["Vagas"] == (
        "160 vagas em quatro localidades: Polo Bom Jesus do Norte, Polo Iúna, Polo São Mateus e "
        f"Polo Vargem Alta (item {item})."
    )
    assert resumo["Cadastro de reserva"] == f"não há (item {item})."


def test_em_b_as_vagas_imediatas_pelos_codigos_e_os_demais_em_cadastro():
    conteudo = _do_cenario("B")
    resumo = _resumo(conteudo)
    item = _numero(conteudo, "Quantas vagas há, e onde?")
    assert resumo["Vagas"] == (
        "10 vagas imediatas, nos Perfis TD-ADM e TD-INFO-EDU; os demais formam cadastro de "
        f"reserva (item {item})."
    )
    assert (
        resumo["Cadastro de reserva"] == f"até 15 (quinze) classificados por Perfil (item {item})."
    )


def test_acima_de_cinco_localidades_so_a_contagem():
    conteudo = snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069))
    base = conteudo["profiles"][0]
    conteudo["profiles"] = []
    for indice in range(6):
        perfil = copy.deepcopy(base)
        perfil["id"] = f"33333333-3333-3333-3333-33333333333{indice}"
        perfil["code"] = f"DOC-{indice}"
        perfil["locality"] = f"Campus {indice}"
        perfil["immediateVacancies"] = 2
        conteudo["profiles"].append(perfil)
    vagas = _resumo(conteudo)["Vagas"]
    assert vagas.startswith("12 vagas em seis localidades (item ")
    assert "Campus" not in vagas


def test_cinco_localidades_ainda_nomeadas():
    conteudo = snapshot(sections=secoes(catalogo_=catalogo.CATALOGO_DA_069))
    base = conteudo["profiles"][0]
    conteudo["profiles"] = []
    for indice in range(5):
        perfil = copy.deepcopy(base)
        perfil["id"] = f"33333333-3333-3333-3333-33333333333{indice}"
        perfil["code"] = f"DOC-{indice}"
        perfil["locality"] = f"Campus {indice}"
        conteudo["profiles"].append(perfil)
    assert (
        "cinco localidades: Campus 0, Campus 1, Campus 2, Campus 3 e Campus 4"
        in (_resumo(conteudo)["Vagas"])
    )


def test_a_selecao_em_poucas_palavras():
    """FR-1371: nome curto da Etapa (A) ou a natureza dela (B), sem reproduzir nome longo.

    "com", e não "seguido de": em A a Análise documental habilita ao sorteio, e vem antes dele —
    o resumo não afirma uma ordem que o dado não diz (FR-1370).
    """
    a, b = _do_cenario("A"), _do_cenario("B")
    assert _resumo(a)["Seleção"] == (
        f"sorteio, com Análise documental (item {_numero(a, 'Como será a seleção?')})."
    )
    assert _resumo(b)["Seleção"] == (
        "pontuação em uma etapa classificatória, com uma etapa eliminatória "
        f"(item {_numero(b, 'Como será a seleção?')})."
    )
    for etapa in b["stages"]:
        assert etapa["name"] not in _resumo(b)["Seleção"]


def test_a_selecao_nao_sai_quando_os_marcos_tem_formas_diferentes():
    conteudo = _do_cenario("B")
    marcos = [
        marco for perfil in conteudo["profiles"] for marco in perfil["classificationMilestones"]
    ]
    marcos[0]["orderProduction"] = "POR_SORTEIO"
    assert "Seleção" not in _resumo(conteudo)


def test_o_cadastro_nao_sai_quando_difere_entre_os_perfis():
    conteudo = _do_cenario("B")
    conteudo["profiles"][0]["reserveLimit"] = 3
    assert "Cadastro de reserva" not in _resumo(conteudo)


def test_cada_linha_aponta_o_item_certo():
    for cenario in "AB":
        conteudo = _do_cenario(cenario)
        resumo = _resumo(conteudo)
        assert resumo["Inscrições"].endswith(f"(item {_numero(conteudo, 'Como se inscrever?')}).")
        assert resumo["Por candidato"].endswith(
            f"(item {_numero(conteudo, 'Como se inscrever?')})."
        )
        assert resumo["Datas"] == f"no Cronograma (item {_numero(conteudo, 'Cronograma')})."


def test_o_resumo_sai_no_documento_com_a_nota_de_nao_substituicao():
    from tests.unit.publicacoes.cenarios_da_auditoria import por_perguntas
    from tests.unit.publicacoes.test_pdf import texto_de

    texto = texto_de(por_perguntas("A"))
    assert "Resumo deste Edital" in texto
    assert apresentacao.NOTA_DO_RESUMO in " ".join(texto.split())
    assert texto.index("Resumo deste Edital") < texto.index("Sumário")


def test_o_resumo_so_repete_dado_do_snapshot():
    """As localidades são as dos Perfis; o período, o do Evento; a soma, a dos quadros."""
    conteudo = _do_cenario("A")
    resumo = _resumo(conteudo)
    for perfil in conteudo["profiles"]:
        assert perfil["locality"] in resumo["Vagas"]
    total = sum(
        linha["immediateVacancies"]
        for perfil in conteudo["profiles"]
        for linha in perfil["vacancyTable"]
    )
    assert resumo["Vagas"].startswith(f"{total} vagas")
    [evento] = [e for e in conteudo["schedule"] if e.get("isRegistrationPeriod")]
    assert resumo["Inscrições"].startswith(pdf._periodo_do_evento(evento))


def test_a_plana_nao_tem_resumo():
    """R-016: o consolidado de um Edital publicado antes sai sem resumo."""
    from tests.unit.publicacoes.cenarios_da_auditoria import composto
    from tests.unit.publicacoes.test_pdf import texto_de

    assert "Resumo deste Edital" not in texto_de(composto("A"))


def test_todos_os_perfis_sem_vaga_imediata():
    """Caso-limite: só cadastro de reserva — o resumo diz isso, e não "0 vagas"."""
    conteudo = _do_cenario("B")
    for perfil in conteudo["profiles"]:
        perfil["immediateVacancies"] = 0
        for linha in perfil.get("vacancyTable") or []:
            linha["immediateVacancies"] = 0
    vagas = _resumo(conteudo)["Vagas"]
    assert vagas.startswith("não há vaga imediata; há cadastro de reserva (item ")
