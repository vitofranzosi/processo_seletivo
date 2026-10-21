"""A prévia por recorte: ampla, reservadas, rodada de ocupação e participantes (095).

`simular` recebe os recortes como a interface os deriva e a rodada da `ocupacao` injetada, como a
interface a injeta. O que se confere aqui é a composição — que cada recorte passa pela mesma
`preparar` com o recorte, que o alvo fixo e os suplentes valem em todo recorte, que a Etapa seguinte
recebe a união das faixas, que o "o que mudou" passa a falar dos recortes — e que um Perfil sem
reservada continua igual à fatia 1.
"""

import time

import pytest

from processo_seletivo.classificacao.application import previa
from processo_seletivo.ocupacao.domain import nomes, rodada_da_previa
from tests.unit.classificacao.test_previa import ETAPAS, FATOS, apurar_vagas, marco

PPI, PCD = "m-ppi", "m-pcd"
RECORTES = [
    {"lista_id": None, "rotulo": "Ampla concorrência (linha geral do quadro)", "vagas": 10},
    {"lista_id": PCD, "rotulo": "Pessoas com deficiência (PCD)", "vagas": 2},
    {"lista_id": PPI, "rotulo": "Pretos, pardos e indígenas (PPI)", "vagas": 3},
]


def rodada_com(especie):
    return lambda entradas: rodada_da_previa.rodada(entradas, especie=especie)


def simular(m, *, recortes=RECORTES, especie=None, **opcoes):
    return previa.simular(
        m,
        ETAPAS,
        FATOS,
        vagas=recortes[0]["vagas"],
        apurar_vagas=apurar_vagas,
        recortes=recortes,
        apurar_recortes=rodada_com(especie),
        **opcoes,
    )


def do_quadro(suplentes=0, **regra):
    return marco(targetKind="FROM_VACANCY_TABLE", targetCount=None, suplentes=suplentes, **regra)


def membros(calculado):
    return {i["inscricao_id"] for i in calculado["ordem"] + calculado["sem_posicao"]}


def reservada(p, lista_id):
    return next(r for r in p["recortes"] if r["lista_id"] == lista_id)


class TestOsRecortes:
    def test_a_ampla_e_o_universo_inteiro(self):
        p = simular(do_quadro())

        assert len(p["ordem"]) + len(p["sem_posicao"]) == p["total"]
        modalidades = {i["modalidade_id"] for i in p["ordem"]}
        assert {PPI, PCD} <= modalidades, "os autodeclarados continuam na ampla (FR-492)"

    def test_cada_reservada_tem_so_os_autodeclarados_e_ordem_propria(self):
        p = simular(do_quadro())
        ppi = reservada(p, PPI)

        assert all(i["modalidade_id"] == PPI for i in ppi["ordem"] + ppi["sem_posicao"])
        assert [i["posicao"] for i in ppi["ordem"]] == list(range(1, len(ppi["ordem"]) + 1))
        na_ampla = [p["posicao_na_ampla"][i["inscricao_id"]] for i in ppi["ordem"]]
        assert na_ampla == sorted(na_ampla), "a ordem reservada segue a da ampla"

    def test_cada_pessoa_tem_no_maximo_uma_modalidade(self):
        p = simular(do_quadro())

        assert not membros(reservada(p, PPI)) & membros(reservada(p, PCD))

    def test_perfil_sem_reservada_fica_igual_a_fatia_1(self):
        """FR-2304: só a ampla, e o estado comparável no formato da fatia 1."""
        sem = previa.simular(marco(), ETAPAS, FATOS, vagas=10, apurar_vagas=apurar_vagas)
        com_rodada = simular(marco(), recortes=RECORTES[:1])

        assert com_rodada["recortes"] == []
        assert previa.estado(com_rodada) == previa.estado(sem)
        assert [i["inscricao_id"] for i in com_rodada["ordem"]] == [
            i["inscricao_id"] for i in sem["ordem"]
        ]

    def test_declarar_modalidade_nao_muda_a_ordem_da_ampla(self):
        """D-003: a Modalidade é atribuída a quem já existe, e ninguém novo entra."""
        sem = simular(do_quadro(), recortes=[{**RECORTES[0]}])
        com = simular(do_quadro())

        def retrato(p):
            return [(i["inscricao_id"], i["posicao"]) for i in p["ordem"]]

        assert retrato(sem) == retrato(com)

    def test_acima_do_limite_de_reservadas_nao_calcula(self):
        demais = [
            {"lista_id": f"m{n}", "rotulo": f"M{n}", "vagas": 1}
            for n in range(previa.RESERVADAS_COBERTAS + 1)
        ]

        with pytest.raises(previa.Incompleto) as erro:
            simular(do_quadro(), recortes=[RECORTES[0], *demais])

        assert "até 6 Modalidades reservadas" in erro.value.faltas[-1]


class TestOCortePorRecorte:
    def test_alvo_do_quadro_e_a_linha_de_cada_recorte(self):
        p = simular(do_quadro())

        assert reservada(p, PPI)["alvo"] == 3
        assert reservada(p, PCD)["alvo"] == 2

    def test_alvo_fixo_e_suplentes_valem_em_todo_recorte(self):
        p = simular(marco(alvo=10, suplentes=5))

        assert reservada(p, PPI)["alvo"] == 10
        assert reservada(p, PPI)["suplentes"] == 5

    def test_recorte_sem_linha_tem_ordem_e_corte_nao_apuravel(self):
        recortes = [*RECORTES[:2], {**RECORTES[2], "vagas": None}]
        p = simular(do_quadro(), recortes=recortes)
        ppi = reservada(p, PPI)

        assert ppi["ordem"], "a ordem existe"
        assert ppi["corte"]["sem_linha"] and previa.impedido(ppi["corte"])
        assert reservada(p, PCD)["corte"].get("sem_linha") is None

    def test_a_recusa_numa_reservada_nao_impede_as_outras(self):
        """Caso de reserva com empate na última vaga e `STRICT`: só aquele recorte para."""
        p = simular(do_quadro(desfecho="STRICT"), modo="caso", caso="empate_vaga_reservada")
        primeira = p["recortes"][0]

        assert previa.impedido(primeira["corte"])
        assert not previa.impedido(p["corte"])
        assert not previa.impedido(p["recortes"][1]["corte"])


class TestAOcupacao:
    def test_a_rodada_recebe_ampla_e_reservadas_na_ordem(self):
        p = simular(do_quadro(), especie=nomes.REVERSAO_POR_SALDO)
        apurados = p["ocupacao_por_recorte"]["recortes"]

        assert list(apurados) == [None, PCD, PPI]

    def test_sem_rodada_injetada_nao_ha_ocupacao_por_recorte(self):
        p = previa.simular(
            do_quadro(), ETAPAS, FATOS, vagas=10, apurar_vagas=apurar_vagas, recortes=RECORTES
        )

        assert p["ocupacao_por_recorte"] is None

    def test_concomitancia_no_caso_limite(self):
        p = simular(do_quadro(), modo="caso", caso="concomitante", especie=nomes.REVERSAO_POR_SALDO)
        primeira = p["recortes"][0]
        apurado = p["ocupacao_por_recorte"]["recortes"][primeira["lista_id"]]

        assert apurado["estado"] == "avaliada"
        assert len(apurado["ocupam_pela_ampla"]) == 1
        assert apurado["tomadas_pela_ampla"] == 1

    def test_reserva_vazia_e_ordem_vazia(self):
        p = simular(do_quadro(), modo="caso", caso="reserva_vazia")

        assert not membros(p["recortes"][0])


class TestParticipantes:
    def test_a_etapa_seguinte_recebe_a_uniao_por_pessoa(self):
        p = simular(do_quadro())
        faixas = [set(p["corte"]["progrediram"])] + [
            set(r["corte"]["progrediram"]) for r in p["recortes"]
        ]

        assert p["participantes"]["uniao"] == len(set().union(*faixas))
        assert p["participantes"]["so_pela_ampla"] == len(faixas[0])

    def test_corte_impedido_deixa_o_numero_dependente(self):
        p = simular(do_quadro(desfecho="STRICT"), modo="caso", caso="empate_vaga_reservada")

        assert p["participantes"]["depende_de"] == [p["recortes"][0]["rotulo"]]


class TestOQueMudou:
    def test_o_estado_ganha_um_trecho_por_recorte(self):
        p = simular(do_quadro())

        assert len(previa.estado(p).split("~")) == 6

    def test_mudar_o_desfecho_diz_o_que_mudou_na_reservada(self):
        rotulos = [r["rotulo"] for r in RECORTES]
        antes = simular(do_quadro(), modo="caso", caso="empate_vaga_reservada")
        depois = simular(do_quadro(desfecho="STRICT"), modo="caso", caso="empate_vaga_reservada")

        diferenca = previa.comparar(previa.estado(antes), previa.estado(depois), rotulos)

        assert any(
            m.startswith("Pessoas com deficiência (PCD): corte") for m in diferenca["mudancas"]
        )

    def test_entre_populacoes_diferentes_nao_compara(self):
        a = simular(do_quadro())
        b = simular(do_quadro(), recortes=RECORTES[:2])

        assert previa.comparar(previa.estado(a), previa.estado(b)) is None


def test_quinhentos_candidatos_e_sete_recortes_em_um_segundo():
    """SC-876: a ampla domina, e cada reservada reordena um subconjunto dela."""
    recortes = [{"lista_id": None, "rotulo": "Ampla", "vagas": 400}] + [
        {"lista_id": f"m{n}", "rotulo": f"M{n}", "vagas": 15} for n in range(6)
    ]
    inicio = time.perf_counter()
    p = simular(do_quadro(suplentes=100), recortes=recortes, especie=nomes.REVERSAO_POR_SALDO)
    duracao = time.perf_counter() - inicio

    assert p["total"] >= 500
    assert duracao < 1.0
