"""A rodada de ocupação da prévia, sem banco (095, R-001, R-004).

O Perfil de referência é o da R-001: 10 vagas na linha geral, 3 na PPI e 2 na PcD. A ordem da
ampla é `a01` a `a20`; os autodeclarados PPI estão na 3ª, 8ª, 15ª e 16ª posições da ampla, e os
PcD na 5ª e na 18ª. Os números esperados são os que a medição de 20/10 tirou do motor, e estão
escritos à mão.
"""

import pytest

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.domain.rodada_da_previa import (
    AVALIADA,
    CORTE_NAO_EMITIDO,
    DEPENDE_DA_AMPLA,
    PAROU_NA_FRONTEIRA,
    SEM_LINHA,
    rodada,
)

AMPLA = [f"a{n:02d}" for n in range(1, 21)]
PPI = ["a03", "a08", "a15", "a16"]
PCD = ["a05", "a18"]


def entrada(lista_id, ordem, *, vagas, faixa, impedido=False, empates=None):
    return {
        "lista_id": lista_id,
        "vagas": vagas,
        "impedido": impedido,
        "progrediram": ordem[:faixa],
        "posicoes": list(range(1, len(ordem) + 1)),
        "membros": ordem,
        "empates": empates or {},
    }


def referencia(especie=None, *, faixa_ppi=3, faixa_pcd=2):
    return rodada(
        [
            entrada(None, AMPLA, vagas=10, faixa=10),
            entrada("PPI", PPI, vagas=3, faixa=faixa_ppi),
            entrada("PCD", PCD, vagas=2, faixa=faixa_pcd),
        ],
        especie=especie,
    )


def quantidades(apurado):
    return (apurado["publicadas"], apurado["efetivas"], apurado["ocupadas"], apurado["faltando"])


class TestConcomitancia:
    def test_a_ampla_ocupa_as_dez_vagas(self):
        ampla = referencia()["recortes"][None]

        assert ampla["estado"] == AVALIADA
        assert quantidades(ampla) == (10, 10, 10, 0)
        assert ampla["ocupantes"] == set(AMPLA[:10])

    def test_quem_ocupa_pela_ampla_nao_conta_na_reservada(self):
        """DP-1: a faixa da PPI tem 3 posições, e duas são de quem ocupa pela ampla."""
        ppi = referencia()["recortes"]["PPI"]

        assert ppi["ocupam_pela_ampla"] == {"a03", "a08"}
        assert ppi["tomadas_pela_ampla"] == 2
        assert ppi["alem_da_faixa"] == 1
        assert quantidades(ppi) == (3, 3, 1, 2)

    def test_a_vaga_reservada_nao_muda_de_lista(self):
        """`FR-253`: sem reversão, a PPI continua com as 3 efetivas, e nada é cedido."""
        resultado = referencia()

        assert resultado["recortes"]["PPI"]["cederia"] == 0
        assert resultado["cedido"] == 0
        assert resultado["efetivas_da_proxima_ampla"] is None


class TestReversao:
    def test_por_saldo_cede_as_vagas_sem_ocupante_na_primeira_apuracao(self):
        resultado = referencia(nomes.REVERSAO_POR_SALDO)
        ppi, pcd = resultado["recortes"]["PPI"], resultado["recortes"]["PCD"]

        assert (ppi["cederia"], pcd["cederia"]) == (2, 1)
        # A apuração nasce com a efetiva líquida, como `emissao._apurar` grava.
        assert quantidades(ppi) == (3, 1, 1, 0)
        assert ppi["sem_ocupante_antes"] == 2
        assert resultado["efetivas_da_proxima_ampla"] == 13

    def test_por_esgotamento_nao_cede_porque_a_conta_inclui_quem_ocupa_pela_ampla(self):
        """DP-2, como o motor faz hoje."""
        ppi = referencia(nomes.REVERSAO_POR_ESGOTAMENTO)["recortes"]["PPI"]

        assert ppi["ha_quem_ocupar"] is True
        assert (ppi["pessoas_com_posicao"], ppi["ocupadas"], ppi["cederia"]) == (4, 1, 0)

    def test_reservada_toda_ocupando_pela_ampla_nunca_esgota(self):
        resultado = rodada(
            [
                entrada(None, AMPLA, vagas=10, faixa=10),
                entrada("PCD", ["a02", "a06"], vagas=2, faixa=2),
            ],
            especie=nomes.REVERSAO_POR_ESGOTAMENTO,
        )
        pcd = resultado["recortes"]["PCD"]

        assert (pcd["ocupadas"], pcd["ha_quem_ocupar"], pcd["cederia"]) == (0, True, 0)

    def test_reserva_vazia_esgota_e_cede_tudo(self):
        resultado = rodada(
            [entrada(None, AMPLA, vagas=10, faixa=10), entrada("PCD", [], vagas=2, faixa=2)],
            especie=nomes.REVERSAO_POR_ESGOTAMENTO,
        )

        assert resultado["recortes"]["PCD"]["cederia"] == 2
        assert resultado["efetivas_da_proxima_ampla"] == 12

    def test_nao_ha_reversao_para_a_propria_ampla(self):
        assert "cederia" not in referencia(nomes.REVERSAO_POR_SALDO)["recortes"][None]


class TestOQueNaoSeAvalia:
    def test_empate_na_ultima_vaga_da_ampla_para_a_ampla_e_as_reservadas(self):
        resultado = rodada(
            [
                entrada(None, AMPLA, vagas=10, faixa=11, empates={"a10": 10, "a11": 10}),
                entrada("PPI", PPI, vagas=3, faixa=3),
            ],
            especie=nomes.REVERSAO_POR_SALDO,
        )

        assert resultado["recortes"][None] == {
            "estado": PAROU_NA_FRONTEIRA,
            "posicao": 10,
            "quantas": 2,
        }
        assert resultado["recortes"]["PPI"]["estado"] == DEPENDE_DA_AMPLA
        assert "publicadas" not in resultado["recortes"]["PPI"]
        assert resultado["cedido"] == 0

    def test_empate_na_ultima_vaga_da_reservada_para_so_ela(self):
        resultado = rodada(
            [
                entrada(None, AMPLA, vagas=10, faixa=10),
                entrada(
                    "PPI",
                    ["a15", "a16", "a17", "a18"],
                    vagas=3,
                    faixa=4,
                    empates={"a17": 3, "a18": 3},
                ),
                entrada("PCD", PCD, vagas=2, faixa=2),
            ],
            especie=None,
        )

        assert resultado["recortes"]["PPI"]["estado"] == PAROU_NA_FRONTEIRA
        assert resultado["recortes"][None]["estado"] == AVALIADA
        assert resultado["recortes"]["PCD"]["estado"] == AVALIADA

    @pytest.mark.parametrize("lista_id", [None, "PPI"])
    def test_sem_linha_nao_e_zero(self, lista_id):
        recortes = [
            entrada(None, AMPLA, vagas=10, faixa=10),
            entrada("PPI", PPI, vagas=3, faixa=3),
        ]
        alvo = next(r for r in recortes if r["lista_id"] == lista_id)
        alvo["vagas"] = None

        apurado = rodada(recortes, especie=None)["recortes"][lista_id]

        assert apurado == {"estado": SEM_LINHA}

    def test_corte_nao_emitido_na_ampla_deixa_as_reservadas_dependentes(self):
        resultado = rodada(
            [
                entrada(None, AMPLA, vagas=10, faixa=10, impedido=True),
                entrada("PPI", PPI, vagas=3, faixa=3),
            ],
            especie=None,
        )

        assert resultado["recortes"][None] == {"estado": CORTE_NAO_EMITIDO}
        assert resultado["recortes"]["PPI"]["estado"] == DEPENDE_DA_AMPLA

    def test_corte_nao_emitido_numa_reservada_nao_alcanca_as_outras(self):
        resultado = rodada(
            [
                entrada(None, AMPLA, vagas=10, faixa=10),
                entrada("PPI", PPI, vagas=3, faixa=3, impedido=True),
                entrada("PCD", PCD, vagas=2, faixa=2),
            ],
            especie=None,
        )

        assert resultado["recortes"]["PPI"] == {"estado": CORTE_NAO_EMITIDO}
        assert resultado["recortes"]["PCD"]["estado"] == AVALIADA


def test_ocupadas_nunca_passam_das_efetivas():
    """`FR-253a`: a faixa da reservada pode ser maior que as vagas, e o teto vale."""
    ppi = referencia(faixa_ppi=4)["recortes"]["PPI"]

    assert ppi["ocupadas"] <= ppi["efetivas"]
    assert ppi["faltando"] >= 0
