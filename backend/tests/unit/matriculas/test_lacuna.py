"""O relatório de lacunas, agregado — e o aviso que vai em toda geração (`FR-439`, `FR-452`)."""

from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.matriculas.domain.lacuna import AVISO_DA_RENDA, Lacuna, consolidar


def test_o_aviso_da_renda_vem_em_toda_geracao_inclusive_sem_outra_lacuna():
    """`SC-153`: é o que impede o número de viajar sem etiqueta.

    Se o aviso não estiver lá, a geração falhou o critério — mesmo com o arquivo perfeito.
    """
    relatorio = consolidar([])
    assert relatorio == (AVISO_DA_RENDA,)
    assert relatorio[0].especie == nomes.DIVERGENCIA
    assert "soma" in relatorio[0].razao and "por pessoa" in relatorio[0].razao


def test_o_aviso_vem_primeiro():
    """Posto no fim, seria lido depois de quem já decidiu que entendeu o relatório."""
    lacunas = [("Joana (INS-1)", "COD_CURSO", Lacuna(nomes.EXTERNA, "Preencher no destino."))]
    assert consolidar(lacunas)[0] is AVISO_DA_RENDA


def test_a_mesma_coluna_e_contada_uma_vez_com_a_quantidade_de_linhas():
    """`FR-439`: coluna, razão e **quantas** linhas — e não uma linha de relatório por pessoa."""
    razao = "Vocabulário do sistema acadêmico."
    lacunas = [
        ("Joana (INS-1)", "COD_CURSO", Lacuna(nomes.EXTERNA, razao)),
        ("Pedro (INS-2)", "COD_CURSO", Lacuna(nomes.EXTERNA, razao)),
    ]
    item = next(item for item in consolidar(lacunas) if item.coluna == "COD_CURSO")
    assert item.quantidade == 2
    assert item.pessoas == ()


def test_a_lacuna_nominal_nomeia_quem_declarou_e_o_que_foi_declarado():
    """`FR-440`: apagar uma declaração em silêncio é o defeito que a feature existe para evitar."""
    lacunas = [
        ("Joana (INS-1)", "COR", Lacuna(nomes.NOMINAL, "O destino não comporta.", "Indígena"))
    ]
    item = next(item for item in consolidar(lacunas) if item.coluna == "COR")
    assert item.quantidade == 1
    assert item.pessoas == ("Joana (INS-1) — declarou «Indígena»",)


def test_a_ausencia_declarada_nao_nomeia_ninguem():
    """Listar quem não declarou o nome do pai exporia uma ausência legítima sem ganho nenhum."""
    lacunas = [("Joana (INS-1)", "NOME_PAI", Lacuna(nomes.AUSENCIA, "Não declarado."))]
    item = next(item for item in consolidar(lacunas) if item.coluna == "NOME_PAI")
    assert item.pessoas == ()
