"""A frase de recurso do marco diz de qual resultado se recorre (067, ED-02, D-001).

`FR-1300` a `FR-1304`.

O documento imprimia *"Caberá recurso no prazo de 2 (dois) dias corridos, contados da divulgação do
resultado."* — sem dizer de qual. No cenário A da auditoria, o resultado do sorteio sai em 16/11, o
único período de recurso do Cronograma é o da análise documental, e o candidato não tinha como saber
contra o quê o prazo de dois dias corria. O resultado passa a ser nomeado pelo nome do marco entre
aspas — as aspas dispensam o artigo, porque o nome não tem gênero conhecido.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import _janela_recursal, prazo_do_recurso
from tests.unit.publicacoes.cenarios_da_auditoria import composto, congelado
from tests.unit.publicacoes.test_pdf import texto_de

NOME = "Classificação por sorteio eletrônico"


def marco(janela, *, nome=NOME, codigo="SORTEIO"):
    return {"code": codigo, "name": nome, "appealWindow": janela}


def admite(dias):
    return {"admits": True, "durationDays": dias, "unit": "DIAS_CORRIDOS"}


@pytest.mark.parametrize(
    ("dias", "prazo"),
    [
        (1, "1 (um) dia corrido"),
        (2, "2 (dois) dias corridos"),
        (15, "15 (quinze) dias corridos"),
        # Fora da tabela de números por extenso, só o algarismo — como sempre (FR-030).
        (11, "11 dias corridos"),
    ],
)
def test_o_prazo_tem_a_grafia_do_documento(dias, prazo):
    assert prazo_do_recurso(marco(admite(dias))) == prazo


def test_a_afirmativa_nomeia_o_resultado_entre_aspas():
    assert _janela_recursal(marco(admite(2))) == (
        "Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”, no prazo de "
        "2 (dois) dias corridos, contados da divulgação desse resultado."
    )


def test_um_dia_e_singular():
    assert "no prazo de 1 (um) dia corrido, contados" in _janela_recursal(marco(admite(1)))


def test_a_negativa_tambem_nomeia_o_resultado():
    janela = {"admits": False, "durationDays": None}
    assert _janela_recursal(marco(janela)) == (
        "Não caberá recurso contra o resultado de “Classificação por sorteio eletrônico”."
    )


def test_sem_nome_o_resultado_e_o_do_codigo():
    assert "contra o resultado de “FINAL”, no prazo" in _janela_recursal(
        marco(admite(3), nome="  ", codigo="FINAL")
    )


def test_sem_nome_e_sem_codigo_a_frase_de_antes_e_a_previa_nao_inventa_nome():
    sem_nada = marco(admite(5), nome="", codigo="")
    assert _janela_recursal(sem_nada) == (
        "Caberá recurso no prazo de 5 (cinco) dias corridos, contados da divulgação do resultado."
    )
    negativa = marco({"admits": False}, nome="", codigo="")
    assert _janela_recursal(negativa) == "Não caberá recurso contra o resultado deste marco."


def test_o_nome_e_aparado_e_sai_como_foi_escrito_inclusive_com_aspas():
    frase = _janela_recursal(marco(admite(2), nome="  Classificação “final”  "))
    assert "contra o resultado de “Classificação “final””, no prazo" in frase


@pytest.mark.parametrize(
    "janela",
    [
        None,
        "sim",
        {},
        {"admits": None},
        {"admits": True, "durationDays": 0},
        {"admits": True, "durationDays": -2},
        {"admits": True, "durationDays": True},
        {"admits": True},
    ],
)
def test_o_silencio_e_o_prazo_invalido_continuam_sem_frase(janela):
    """FR-1303 e FR-028: onde o Edital nada disse, o documento não afirma norma."""
    assert _janela_recursal(marco(janela)) == ""


def _corrido(documento):
    return " ".join(texto_de(documento).split())


def test_o_documento_do_cenario_a_nomeia_o_resultado_nos_quatro_marcos():
    texto = _corrido(composto("A"))
    frase = (
        "Caberá recurso contra o resultado de “Classificação por sorteio eletrônico”, no prazo de "
        "2 (dois) dias corridos, contados da divulgação desse resultado."
    )
    assert texto.count(frase) == 4
    assert "contados da divulgação do resultado" not in texto


def test_a_previa_imprime_a_mesma_frase():
    """FR-1304: uma frase só, para o publicado e para a prévia."""
    previa = _corrido(composto("A", modo=pdf.MODO_PREVIA))
    assert previa.count("contra o resultado de “Classificação por sorteio eletrônico”") == 4


def test_o_nome_longo_quebra_sem_ser_truncado():
    conteudo = congelado("A")["content"]
    longo = "Classificação " + "muito " * 40 + "longa por sorteio eletrônico"
    for perfil in conteudo["profiles"]:
        for item in perfil["classificationMilestones"]:
            item["name"] = longo
    texto = _corrido(composto("A", conteudo))
    assert f"contra o resultado de “{longo}”, no prazo" in texto


def test_a_revisao_diz_o_resultado_pela_denominacao_da_linha_de_cima():
    """D-012: a Revisão agrupa marcos de Perfis diferentes; o nome dentro da frase os separaria.

    A frase é a mesma função, com o nome trocado por "deste marco" — e só quando a Revisão pede.
    """
    assert _janela_recursal(marco(admite(2)), objeto="deste marco") == (
        "Caberá recurso contra o resultado deste marco, no prazo de 2 (dois) dias corridos, "
        "contados da divulgação desse resultado."
    )
    assert (
        _janela_recursal(marco({"admits": False}), objeto="deste marco")
        == "Não caberá recurso contra o resultado deste marco."
    )
    assert _janela_recursal(marco(None), objeto="deste marco") == ""
