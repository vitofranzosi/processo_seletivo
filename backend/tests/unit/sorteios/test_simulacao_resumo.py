"""A rodada e o resumo da prévia do sorteio, sobre o motor oficial (098, R-001, R-003).

**A população da história 1 da spec é a da R-001**: 20 só na ampla, 6 PPI e 4 PcD, com 10, 3 e 2
vagas, alvo do quadro e nenhum suplente. As porcentagens se conferem com margem, porque são de
amostragem; as cessões se conferem exatas, porque são consequência da regra, e não da sorte.
"""

import time

import pytest

from processo_seletivo.classificacao.domain.cenarios_da_previa import nome_ficticio
from processo_seletivo.ocupacao.domain import rodada_da_previa
from processo_seletivo.sorteios.application import simulacao as aplicacao
from processo_seletivo.sorteios.domain import simulacao

PERFIL = "00000000-0000-4000-8000-000000000980"
PPI = "00000000-0000-4000-8000-000000000981"
PCD = "00000000-0000-4000-8000-000000000982"
MATERIAL = "048213 771904 302558 919007 116482"
QUADRO = {"targetKind": "FROM_VACANCY_TABLE", "surplusCount": 0}
MARCO = {"orderProduction": "POR_SORTEIO", "cutRule": QUADRO}
RECORTES = [
    {"lista_id": None, "rotulo": "", "vagas": 10},
    {"lista_id": PPI, "rotulo": "PPI", "vagas": 3},
    {"lista_id": PCD, "rotulo": "PcD", "vagas": 2},
]


def _candidatos(so_ampla=20, ppi=6, pcd=4):
    return simulacao.populacao(so_ampla, [(PPI, ppi), (PCD, pcd)], nomear=nome_ficticio)


def _apurar(especie):
    return lambda entradas: rodada_da_previa.rodada(entradas, especie=especie)


def _resumo(especie=None, *, semente="semente-ficticia", rodadas=1000, **populacao):
    return aplicacao.resumir(
        MARCO,
        perfil_id=PERFIL,
        semente=semente,
        candidatos=_candidatos(**populacao),
        recortes=RECORTES,
        apurar_recortes=_apurar(especie),
        rodadas=rodadas,
    )


def _rodada(especie=None, *, material=MATERIAL, marco=MARCO, recortes=RECORTES, **populacao):
    return aplicacao.simular_sorteio(
        marco,
        perfil_id=PERFIL,
        metodo={"normalization": {"rule": "DIGITOS_EM_SEQUENCIA"}},
        material=material,
        candidatos=_candidatos(**populacao),
        recortes=recortes,
        apurar_recortes=_apurar(especie),
    )


def test_o_estado_avaliado_e_o_mesmo_da_rodada_da_ocupacao():
    assert aplicacao.AVALIADA == rodada_da_previa.AVALIADA


def test_a_rodada_tem_a_ampla_com_todos_e_cada_reservada_com_os_seus():
    previa = _rodada()

    assert [r["total"] for r in previa["recortes"]] == [30, 6, 4]
    assert [len(r["corte"]["progrediram"]) for r in previa["recortes"]] == [10, 3, 2]
    # `DIGITOS_EM_SEQUENCIA` guarda os grupos de dígitos na ordem, separados por espaço.
    assert previa["semente"] == MATERIAL
    assert previa["supos_regra"] is False
    assert set(previa["posicao_na_ampla"]) == {c.id for c in _candidatos()}


def test_sem_regra_de_normalizacao_a_prevista_e_a_da_loteria_federal_e_e_dita():
    previa = aplicacao.simular_sorteio(
        MARCO,
        perfil_id=PERFIL,
        metodo={},
        material=MATERIAL,
        candidatos=_candidatos(),
        recortes=RECORTES,
    )

    assert previa["supos_regra"] is True
    assert previa["regra_de_normalizacao"] == "DIGITOS_EM_SEQUENCIA"
    assert previa["ocupacao_por_recorte"] is None


def test_a_rodada_e_a_soma_que_o_resumo_faz():
    """FR-2504: refazer três rodadas à mão dá o que o resumo de três rodadas soma."""
    semente = "base-da-conferencia"
    resumo = _resumo(semente=semente, rodadas=3)
    sobras, pela_ampla = [], []
    for indice in range(3):
        rodada = aplicacao.simular_sorteio(
            MARCO,
            perfil_id=PERFIL,
            metodo={"normalization": {"rule": "TEXTO_LITERAL"}},
            material=simulacao.semente_da_rodada(semente, indice),
            candidatos=_candidatos(),
            recortes=RECORTES,
            apurar_recortes=_apurar(None),
        )
        ppi = rodada["ocupacao_por_recorte"]["recortes"][PPI]
        sobras.append(ppi["sem_ocupante_antes"])
        pela_ampla.append(len(ppi["ocupam_pela_ampla"]))

    assert resumo["reservadas"][PPI]["sem_ocupante"]["media"] == pytest.approx(sum(sobras) / 3)
    assert resumo["reservadas"][PPI]["pela_ampla"]["media"] == pytest.approx(sum(pela_ampla) / 3)


def test_na_populacao_da_historia_sobra_vaga_de_ppi_na_maioria_das_rodadas():
    """R-001: 72% e 54% medidos; a margem é a da SC-929."""
    resumo = _resumo()

    ppi, pcd = resumo["reservadas"][PPI], resumo["reservadas"][PCD]
    assert ppi["com_sobra"]["porcentagem"] == pytest.approx(72, abs=5)
    assert pcd["com_sobra"]["porcentagem"] == pytest.approx(54, abs=5)
    # O esperado de PPI entre os 10 primeiros da ampla é 10 × 6/30 = 2.
    assert ppi["pela_ampla"]["media"] == pytest.approx(2, abs=0.15)
    assert resumo["ampla"]["autodeclarados_ocupando"]["media"] == pytest.approx(10 / 3, abs=0.2)


def test_por_saldo_cede_toda_vaga_sem_ocupante_e_por_esgotamento_nunca_cede():
    """DP-1 e DP-2 da `095`, como comportamento atual: a cessão é regra, e não sorte."""
    saldo = _resumo("ON_BALANCE")["reservadas"][PPI]
    esgotamento = _resumo("ON_EXHAUSTION")["reservadas"][PPI]
    sem_reversao = _resumo(None)["reservadas"][PPI]

    assert saldo["cedidas"]["media"] == pytest.approx(saldo["sem_ocupante"]["media"])
    assert saldo["com_cessao"]["porcentagem"] == pytest.approx(saldo["com_sobra"]["porcentagem"])
    assert esgotamento["cedidas"] == {"media": 0, "constante": True, "valor": 0}
    assert sem_reversao["cedidas"]["constante"] is True


def test_menos_inscritos_que_vagas_sobra_em_toda_rodada_mas_nao_sempre_o_mesmo_tanto():
    """Uma PPI para 3 vagas: sobram 2, ou 3 quando ela cai entre os 10 da ampla (FR-2503)."""
    ppi = _resumo(ppi=1, pcd=4)["reservadas"][PPI]

    assert ppi["com_sobra"]["porcentagem"] == 100
    assert ppi["com_sobra"]["constante"] is True
    assert ppi["sem_ocupante"]["constante"] is False
    assert ppi["sem_ocupante"]["valor"] == 2


def test_reservada_sem_inscritos_nao_e_sorteada_nem_apurada_e_nao_reverte():
    """O comportamento atual, medido no caminho oficial em 21/10/2026: relação vazia é recusada, o
    corte e a apuração também, e a vaga não é cedida nem sob "por saldo" (FR-2489, FR-2507)."""
    previa = _rodada("ON_BALANCE", ppi=0)
    ppi = next(r for r in previa["recortes"] if r["lista_id"] == PPI)

    assert ppi["ordem"] == [] and ppi["corte"]["sem_relacao"] is True
    assert previa["ocupacao_por_recorte"]["recortes"][PPI] == {"estado": "corte_nao_emitido"}
    assert previa["ocupacao_por_recorte"]["cedido"] == previa["ocupacao_por_recorte"]["recortes"][
        PCD
    ].get("cederia")
    resumo = _resumo("ON_BALANCE", ppi=0)
    assert resumo["reservadas"][PPI] == {"estado": "corte_nao_emitido", "avaliadas": 0}


def test_recorte_sem_linha_no_quadro_nao_e_avaliado():
    recortes = [*RECORTES[:2], {"lista_id": PCD, "rotulo": "PcD", "vagas": None}]
    resumo = aplicacao.resumir(
        MARCO,
        perfil_id=PERFIL,
        semente="s",
        candidatos=_candidatos(),
        recortes=recortes,
        apurar_recortes=_apurar(None),
        rodadas=5,
    )

    assert resumo["reservadas"][PCD] == {"estado": "sem_linha", "avaliadas": 0}
    assert resumo["reservadas"][PPI]["avaliadas"] == 5


def test_sem_regra_de_corte_ha_ordem_mas_nao_ha_faixa_nem_ocupacao():
    """FR-2500: sem corte não há geração nem faixa, e a apuração não teria o que ler."""
    marco = {"orderProduction": "POR_SORTEIO"}
    previa = _rodada(marco=marco)

    assert [r["total"] for r in previa["recortes"]] == [30, 6, 4]
    assert all(r["corte"]["declarado"] is False for r in previa["recortes"])
    assert previa["sem_corte"] is True
    assert previa["ocupacao_por_recorte"] is None
    resumo = aplicacao.resumir(
        marco,
        perfil_id=PERFIL,
        semente="s",
        candidatos=_candidatos(),
        recortes=RECORTES,
        apurar_recortes=_apurar(None),
        rodadas=5,
    )
    assert resumo == {"rodadas": 0, "semente": "s", "sem_corte": True}


def test_a_mesma_semente_e_a_mesma_populacao_dao_o_mesmo_resumo():
    assert _resumo(rodadas=50) == _resumo(rodadas=50)


def test_duas_sementes_diferem_pouco_em_cada_porcentagem():
    """SC-929: com 1.000 rodadas, a diferença entre dois resumos é de amostragem."""
    um = _resumo(semente="primeira")["reservadas"]
    outro = _resumo(semente="segunda")["reservadas"]

    for lista in (PPI, PCD):
        assert um[lista]["com_sobra"]["porcentagem"] == pytest.approx(
            outro[lista]["com_sobra"]["porcentagem"], abs=5
        )


def test_alvo_fixo_sem_quantidade_e_incompleto():
    from processo_seletivo.classificacao.application.previa import Incompleto

    with pytest.raises(Incompleto):
        _rodada(marco={"cutRule": {"targetKind": "FIXED", "surplusCount": 0}})


@pytest.mark.parametrize(
    ("so_ampla", "por_reservada"), [(500, 0), (260, 40)], ids=["sem-reserva", "seis-reservadas"]
)
def test_o_pior_caso_cabe_no_orcamento(so_ampla, por_reservada):
    """SC-928: a rodada em até 1 s e o resumo em até 5 s, com 500 inscritos."""
    listas = [(f"00000000-0000-4000-8000-00000000099{i}", por_reservada) for i in range(6)]
    listas = listas if por_reservada else []
    candidatos = simulacao.populacao(so_ampla, listas, nomear=nome_ficticio)
    recortes = [{"lista_id": None, "rotulo": "", "vagas": 10}] + [
        {"lista_id": lista, "rotulo": lista, "vagas": 3} for lista, _ in listas
    ]

    inicio = time.perf_counter()
    aplicacao.resumir(
        MARCO,
        perfil_id=PERFIL,
        semente="orcamento",
        candidatos=candidatos,
        recortes=recortes,
        apurar_recortes=_apurar("ON_BALANCE"),
    )

    assert time.perf_counter() - inicio < 5
