"""A espécie da convocação sai da posição da pessoa, e não de um seletor (050, `D-008`)."""

from processo_seletivo.convocacao.domain import especie, nomes

OCUPANDO = {"t1", "t2"}
ALCANCADOS = ["t1", "t2", "s1", "s2"]
REGULARIZAVEIS = ["i1"]


def derivar(inscricao):
    return especie.derivada(
        inscricao, ocupando=OCUPANDO, alcancados=ALCANCADOS, regularizaveis=REGULARIZAVEIS
    )


def test_quem_ocupa_pela_contagem_e_chamado_para_vaga_inicial():
    assert derivar("t1") == nomes.VAGA_INICIAL


def test_quem_esta_na_faixa_e_nao_ocupa_e_chamado_para_vaga_que_vagou():
    """O suplente **acrescenta** alguém à contagem.

    Chamá-lo "para vaga inicial" gravaria um fato falso num ato append-only.
    """
    assert derivar("s2") == nomes.SUPLENCIA


def test_o_indeferido_da_faixa_e_chamado_para_regularizar():
    assert derivar("i1") == nomes.PARA_REGULARIZAR


def test_quem_nao_esta_em_lugar_nenhum_nao_tem_especie():
    """`None` não é recusa: a recusa própria é `fora_da_faixa`, e ela diz o que fazer."""
    assert derivar("x9") is None


def test_ocupar_decide_antes_de_estar_na_faixa():
    """Uma suplente que aceitou passa a ocupar; chamada de novo, seria para vaga inicial."""
    assert (
        especie.derivada("s1", ocupando={"s1"}, alcancados=ALCANCADOS, regularizaveis=())
        == nomes.VAGA_INICIAL
    )
