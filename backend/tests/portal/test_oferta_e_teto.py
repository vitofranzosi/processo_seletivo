"""A oferta de cada Perfil e o teto do que se mostra (072, FR-1607 a FR-1610).

Sem banco: as duas funções recebem números e textos, e é aqui que mora a redação que o cartão da
vitrine e o resumo da página da seleção compartilham.
"""

from processo_seletivo.portal.leitura import os_primeiros, quantidade_da_oferta


def test_a_quantidade_vem_com_o_numero_e_concorda_com_ele():
    assert quantidade_da_oferta(1, "NONE") == "1 vaga"
    assert quantidade_da_oferta(3, "NONE") == "3 vagas"


def test_reserva_com_vaga_imediata_e_dita_depois_do_numero():
    assert quantidade_da_oferta(3, "LIMITED") == "3 vagas e cadastro reserva"
    assert quantidade_da_oferta(1, "UNLIMITED") == "1 vaga e cadastro reserva"


def test_sem_vaga_imediata_a_reserva_e_a_oferta_e_o_zero_nao_e_escrito():
    """A leitura da 024 (FR-136): "0 vagas" em destaque leria como ausência."""
    assert quantidade_da_oferta(0, "UNLIMITED") == "cadastro reserva"
    assert quantidade_da_oferta(None, "LIMITED") == "cadastro reserva"


def test_sem_vaga_e_sem_reserva_nada_e_inventado():
    assert quantidade_da_oferta(0, "NONE") == ""
    assert quantidade_da_oferta(0, None) == ""


def test_o_teto_corta_e_diz_quantos_sobraram():
    assert os_primeiros(["a", "b", "c", "d", "e"], 3) == (["a", "b", "c"], 2)
    assert os_primeiros(["a", "b", "c"], 3) == (["a", "b", "c"], 0)
    assert os_primeiros([], 3) == ([], 0)


def test_com_busca_o_que_casa_vem_primeiro_mesmo_alem_do_teto():
    """Sem esta ordem, o teto esconderia o Perfil que fez o cartão ser encontrado (FR-1610)."""
    polos = ["Polo Serra", "Polo Vila Velha", "Polo Cariacica", "Polo Guarapari", "Polo Linhares"]

    mostrados, sobram = os_primeiros(polos, 3, termo="linhares")

    assert mostrados[0] == "Polo Linhares"
    assert mostrados[1:] == ["Polo Serra", "Polo Vila Velha"]
    assert sobram == 2


def test_a_busca_ignora_acento_e_caixa():
    mostrados, _ = os_primeiros(["Campus Serra", "Campus Vitória"], 1, termo="VITORIA")

    assert mostrados == ["Campus Vitória"]


def test_o_texto_comparado_pode_vir_de_um_campo_do_item():
    perfis = [{"nome": "Professor"}, {"nome": "Técnico de Laboratório"}]

    mostrados, _ = os_primeiros(perfis, 1, termo="laboratorio", texto=lambda p: p["nome"])

    assert mostrados == [{"nome": "Técnico de Laboratório"}]
