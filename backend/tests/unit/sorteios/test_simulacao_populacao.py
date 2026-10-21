"""A população informada da prévia do sorteio: sugestão, soma, nomes estáveis, limite (098)."""

import pytest

from processo_seletivo.classificacao.domain.cenarios_da_previa import nome_ficticio
from processo_seletivo.sorteios.application import simulacao as aplicacao
from processo_seletivo.sorteios.domain import simulacao

PPI = "00000000-0000-4000-8000-000000000981"
PCD = "00000000-0000-4000-8000-000000000982"


def _populacao(so_ampla, ppi, pcd):
    return simulacao.populacao(so_ampla, [(PPI, ppi), (PCD, pcd)], nomear=nome_ficticio)


@pytest.mark.parametrize(("vagas", "esperada"), [(10, 20), (3, 6), (0, 0), (None, 10)])
def test_a_sugestao_e_o_dobro_das_vagas_da_linha_e_dez_sem_linha(vagas, esperada):
    assert simulacao.sugestao(vagas) == esperada


def test_a_ampla_e_sorteada_com_a_soma_de_todas_as_listas():
    candidatos = _populacao(20, 6, 4)

    assert (
        len(simulacao.relacao_ficticia(candidatos, perfil_id="p", lista_id=None).participantes)
        == 30
    )
    assert (
        len(simulacao.relacao_ficticia(candidatos, perfil_id="p", lista_id=PPI).participantes) == 6
    )


def test_zero_numa_reservada_e_aceito_e_a_lista_fica_vazia():
    candidatos = _populacao(5, 0, 2)

    assert simulacao.relacao_ficticia(candidatos, perfil_id="p", lista_id=PPI).participantes == ()


def test_quem_existia_mantem_id_nome_e_modalidade_quando_outra_lista_cresce():
    antes = {c.id: c for c in _populacao(20, 6, 4)}
    depois = {c.id: c for c in _populacao(45, 6, 3)}

    for identificador in set(antes) & set(depois):
        assert antes[identificador] == depois[identificador]
    # A ampla cresceu no fim dela; a PcD perdeu a última; a PPI não mudou.
    assert set(depois) - set(antes) == {f"a{i}" for i in range(20, 45)}
    assert set(antes) - set(depois) == {f"{PCD}-3"}


def test_nomes_sao_distintos_e_sem_marca_de_grupo():
    candidatos = _populacao(200, 150, 100)
    nomes = [c.nome for c in candidatos]

    assert len(set(nomes)) == len(nomes)
    for nome in nomes:
        assert "PPI" not in nome and "PcD" not in nome and PPI not in nome


def test_a_setima_reservada_e_recusada_no_dominio():
    """Revisão do #327: a sétima lista usaria as vagas de nome da ampla, e repetiria nomes."""
    sete = [(f"lista-{i}", 1) for i in range(7)]

    with pytest.raises(ValueError, match="Até 6 listas reservadas"):
        simulacao.populacao(2, sete, nomear=nome_ficticio)
    assert len(simulacao.populacao(2, sete[:6], nomear=nome_ficticio)) == 8


@pytest.mark.parametrize(
    ("so_ampla", "por_reservada", "recusa"),
    [
        (600, [], None),
        (500, [(PPI, 100)], None),
        (500, [(PPI, 101)], "600"),
        (10, [(f"lista-{i}", 1) for i in range(6)], None),
        (10, [(f"lista-{i}", 1) for i in range(7)], "seis"),
    ],
)
def test_o_limite_e_600_candidatos_e_seis_reservadas(so_ampla, por_reservada, recusa):
    motivo = aplicacao.acima_do_limite(so_ampla, por_reservada)

    if recusa is None:
        assert motivo is None
    else:
        assert recusa in motivo
