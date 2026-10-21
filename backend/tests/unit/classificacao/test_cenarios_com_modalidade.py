"""A Modalidade dos candidatos fictícios (095, D-003, R-005).

A atribuição é sobre candidatos que já existem: não muda nota, não muda a ordem da ampla, e não
mexe nos que a população da fatia 1 plantou para outra explicação — os empates, o trio, a candidata
sem nota e o candidato eliminado.
"""

import copy

import pytest

from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios

ETAPA = {"id": "e1", "name": "Prova Escrita", "order": 1, "forma": "PONTUADA"}
FATOS = [{"id": "f1", "code": "NASC", "label": "Data de nascimento", "type": "DATA"}]
RESERVADAS = [
    ("m-pcd", "Pessoas com deficiência (PCD)"),
    ("m-ppi", "Pretos, pardos e indígenas (PPI)"),
]


def estavel(*, alvo=10, faixa=10, vagas=10):
    candidatos, _ = cenarios.populacao_estavel(
        etapas_enumeradas=[ETAPA],
        etapa_do_marco=ETAPA,
        fatos=FATOS,
        alvo=alvo,
        faixa=faixa,
        vagas=vagas,
    )
    return candidatos


def atribuir(candidatos, faixas=None, **fronteiras):
    return cenarios.atribuir_modalidades(
        candidatos,
        RESERVADAS,
        vagas_da_ampla=fronteiras.get("vagas", 10),
        faixa_da_ampla=fronteiras.get("faixa", 10),
        faixas=faixas or {"m-pcd": 2, "m-ppi": 3},
    )


def por_modalidade(candidatos, lista_id):
    return [i for i, c in enumerate(candidatos) if c.get("modalidade") == lista_id]


def test_e_deterministica():
    a, plantados_a = atribuir(estavel())
    b, plantados_b = atribuir(estavel())

    assert [c.get("modalidade") for c in a] == [c.get("modalidade") for c in b]
    assert plantados_a == plantados_b


def test_nao_muda_nota_nem_fato():
    antes = estavel()
    depois, _ = atribuir(copy.deepcopy(antes))

    assert [(c["notas"], c["fatos"]) for c in antes] == [(c["notas"], c["fatos"]) for c in depois]


def test_cada_reservada_tem_um_dentro_das_vagas_da_ampla_e_um_alem_da_propria_faixa():
    candidatos, _ = atribuir(estavel())

    for lista_id, faixa in (("m-pcd", 2), ("m-ppi", 3)):
        indices = por_modalidade(candidatos, lista_id)
        assert indices[0] < 10, "a concomitância: um entre as vagas da ampla"
        assert len(indices) == faixa + 1, "a faixa da reservada e um além dela"


def test_com_suplentes_a_reservada_ganha_o_suplente_da_ampla():
    candidatos, _ = atribuir(estavel(faixa=15), faixa=15)

    entre = [i for i in por_modalidade(candidatos, "m-pcd") if 10 <= i < 15]
    assert entre, "um na faixa da ampla e além das vagas dela — o suplente, que não ocupa"


def test_uma_modalidade_por_candidato():
    candidatos, _ = atribuir(estavel())

    assert not set(por_modalidade(candidatos, "m-pcd")) & set(por_modalidade(candidatos, "m-ppi"))


def test_os_plantados_da_fatia_1_ficam_sem_modalidade():
    candidatos, _ = atribuir(estavel())

    for indice, candidato in enumerate(candidatos):
        if not candidato.get("modalidade"):
            continue
        assert candidato["eliminado_em"] is None
        assert all(n is not None for n in candidato["notas"].values())
        vizinhos = candidatos[max(indice - 1, 0) : indice] + candidatos[indice + 1 : indice + 2]
        assert all(v["notas"] != candidato["notas"] for v in vizinhos), "nenhum empatado"


def test_nenhum_nome_marca_a_modalidade():
    """FR-2342: o nome fictício não associa pessoa a grupo."""
    candidatos, _ = atribuir(estavel())

    for candidato in candidatos:
        for _, rotulo in RESERVADAS:
            assert rotulo.split(" (")[0].lower() not in candidato["nome"].lower()
        assert "PPI" not in candidato["nome"] and "PCD" not in candidato["nome"]


def test_os_inscritos_levam_a_modalidade():
    candidatos, _ = atribuir(estavel())
    inscritos = cenarios.inscritos(candidatos)

    assert {i["modalidade_id"] for i in inscritos} == {None, "m-pcd", "m-ppi"}


def test_o_que_nao_cabe_e_dito():
    candidatos, plantados = atribuir(estavel(), faixas={"m-pcd": 2, "m-ppi": 40})

    assert any("não comporta" in frase for frase in plantados)
    assert por_modalidade(candidatos, "m-ppi"), "o que cabe é plantado mesmo assim"


@pytest.mark.parametrize("chave", sorted(cenarios.CASOS_DE_RESERVA))
def test_cada_caso_de_reserva_planta_na_primeira_reservada(chave):
    base, _ = cenarios.caso_limite(
        "sem_empate",
        etapas_enumeradas=[ETAPA],
        etapa_do_marco=ETAPA,
        fatos=FATOS,
        alvo=10,
        suplentes=0,
        vagas=10,
        corta=True,
    )
    candidatos, onde = cenarios.caso_de_reserva(
        chave,
        base,
        RESERVADAS,
        vagas_da_ampla=10,
        faixa_da_ampla=10,
        vagas={"m-pcd": 2, "m-ppi": 3},
        faixas={"m-pcd": 2, "m-ppi": 3},
    )
    primeira = por_modalidade(candidatos, "m-pcd")

    assert onde
    if chave == "reserva_vazia":
        assert primeira == []
    elif chave == "reserva_curta":
        assert 0 < len(primeira) < 2
    elif chave == "concomitante":
        assert primeira[0] < 10 and all(i >= 10 for i in primeira[1:])
    elif chave == "empate_vaga_reservada":
        assert candidatos[primeira[-1]]["notas"] == candidatos[primeira[-2]]["notas"]
    elif chave == "alvo_fixo_reservada":
        assert len(primeira) > 2
    else:
        assert candidatos[10]["notas"] == candidatos[9]["notas"], "o empate da última vaga"
    assert por_modalidade(candidatos, "m-ppi"), "a outra reservada recebe a atribuição comum"
