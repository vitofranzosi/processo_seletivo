"""A regra única do "aplicar a todos" (051, `DP-13`), unidade a unidade.

O risco é o do duplicar, num lugar novo: o destino **já existe**, e a referência que continuasse
apontando a origem seria coerente com os vizinhos e atravessaria a gravação. Aqui a guarda é que o
fato é achado pelo código e pelo tipo no destino, e que nada do destino fora da unidade muda.

A forma dos Perfis é a da etapa: `classificationMilestones` e `declaredFacts` como o formulário
entrega.
"""

import copy
import itertools
import uuid

import pytest

from processo_seletivo.editais.domain import aplicacao
from processo_seletivo.editais.domain.aplicacao import FORA, NASCE, SEM_MUDANCA, SUBSTITUI

ETAPA = "00000000-0000-4000-8000-000000051001"


def _sequencia():
    contador = itertools.count(1)
    return lambda: uuid.UUID(int=next(contador))


def _perfil(codigo, *, marcos=(), fatos=None, **extra):
    return {
        "id": f"perfil-{codigo}",
        "code": codigo,
        "name": f"Polo {codigo}",
        "declaredFacts": (
            [{"id": f"nasc-{codigo}", "code": "NASC", "label": "Nascimento", "type": "DATA"}]
            if fatos is None
            else fatos
        ),
        "classificationMilestones": list(marcos),
        **extra,
    }


def _marco(perfil_codigo, **extra):
    marco = {
        "id": f"marco-{perfil_codigo}",
        "code": perfil_codigo,
        "name": f"Classificação final — Polo {perfil_codigo}",
        "orderProduction": "POR_PONTUACAO",
        "stages": [ETAPA],
        "operation": "MEDIA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "appealWindow": {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"},
        "drawMethod": None,
        "cutRule": {
            "targetKind": "FROM_VACANCY_TABLE",
            "targetCount": None,
            "surplusCount": 0,
            "tieOutcome": "STRICT",
            "governedStage": "NONE",
            "continuation": "ALLOWED",
        },
        "tiebreakers": [
            {
                "id": f"crit-{perfil_codigo}",
                "order": 1,
                "type": "MENOR_VALOR_DE_FATO",
                "parameters": {"factId": f"nasc-{perfil_codigo}"},
                "whenMissing": "ULTIMO_NO_CRITERIO",
            }
        ],
    }
    marco.update(extra)
    return marco


def _por_codigo(efeitos):
    return {item.codigo: item for item in efeitos}


class TestMarco:
    def test_nasce_onde_falta_com_identidade_do_destino_e_o_fato_do_destino(self):
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02")]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == NASCE
        assert efeito.depois["code"] == "LP02"
        assert efeito.depois["name"] == "Classificação final — Polo LP02"
        assert efeito.depois["id"] != "marco-LP01"
        (criterio,) = efeito.depois["tiebreakers"]
        assert criterio["parameters"] == {"factId": "nasc-LP02"}
        assert criterio["id"] != "crit-LP01"

    def test_a_copia_e_independente_da_origem(self):
        origem = _marco("LP01")
        perfis = [_perfil("LP01", marcos=[origem]), _perfil("LP02")]
        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        efeito.depois["cutRule"]["surplusCount"] = 9
        efeito.depois["stages"].append("outra")

        assert origem["cutRule"]["surplusCount"] == 0
        assert origem["stages"] == [ETAPA]

    def test_substitui_os_campos_e_mantem_identidade_codigo_e_denominacao(self):
        destino = _marco("LP02", name="Escrita à mão", appealWindow=None)
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02", marcos=[destino])]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == SUBSTITUI
        assert efeito.depois["id"] == "marco-LP02"
        assert efeito.depois["code"] == "LP02"
        assert efeito.depois["name"] == "Escrita à mão"
        assert efeito.depois["appealWindow"]["durationDays"] == 2
        # A lista de critérios é a mesma (pelo código do fato): ela fica com a identidade que tem.
        assert efeito.depois["tiebreakers"][0]["id"] == "crit-LP02"

    def test_ausencia_na_origem_e_aplicada_como_ausencia(self):
        perfis = [
            _perfil("LP01", marcos=[_marco("LP01", appealWindow=None)]),
            _perfil("LP02", marcos=[_marco("LP02")]),
        ]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == SUBSTITUI
        assert efeito.depois["appealWindow"] is None

    def test_marco_igual_nao_muda(self):
        perfis = [
            _perfil("LP01", marcos=[_marco("LP01")]),
            _perfil("LP02", marcos=[_marco("LP02")]),
        ]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == SEM_MUDANCA

    def test_a_lista_de_criterios_e_substituida_inteira(self):
        destino = _marco("LP02")
        destino["tiebreakers"].append(
            {
                "id": "crit-2",
                "order": 2,
                "type": "MAIOR_PONTUACAO_NA_ETAPA",
                "parameters": {"stageId": ETAPA},
                "whenMissing": "ULTIMO_NO_CRITERIO",
            }
        )
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02", marcos=[destino])]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == SUBSTITUI
        assert len(efeito.depois["tiebreakers"]) == 1

    def test_dois_marcos_no_destino_ficam_fora(self):
        perfis = [
            _perfil("LP01", marcos=[_marco("LP01")]),
            _perfil("LP02", marcos=[_marco("LP02"), _marco("LP02", id="x", code="LP02-2")]),
        ]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == FORA
        assert "2 marcos" in efeito.motivo

    def test_fato_ausente_deixa_fora_e_nomeia_o_fato(self):
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02", fatos=[])]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == FORA
        assert "NASC" in efeito.motivo

    def test_fato_de_mesmo_codigo_e_outro_tipo_nao_corresponde(self):
        numero = [{"id": "n", "code": "NASC", "label": "x", "type": "INTEIRO"}]
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02", fatos=numero)]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == FORA
        assert "data" in efeito.motivo

    @pytest.mark.parametrize("onde", ["origem", "destino"])
    def test_metodo_proprio_de_sorteio_deixa_fora(self, onde):
        metodo = {"algorithm": "x", "source": "y"}
        sorteio = {"orderProduction": "POR_SORTEIO", "drawMethod": metodo}
        origem = _marco("LP01", **(sorteio if onde == "origem" else {}))
        destino = _marco("LP02", **(sorteio if onde == "destino" else {}))
        perfis = [_perfil("LP01", marcos=[origem]), _perfil("LP02", marcos=[destino])]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == FORA
        assert "método próprio" in efeito.motivo

    def test_metodo_guardado_em_marco_de_pontuacao_nao_e_proprio_e_fica_com_o_destino(self):
        guardado = {"algorithm": "x"}
        perfis = [
            _perfil("LP01", marcos=[_marco("LP01")]),
            _perfil("LP02", marcos=[_marco("LP02", drawMethod=guardado, appealWindow=None)]),
        ]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.efeito == SUBSTITUI
        assert efeito.depois["drawMethod"] == guardado

    def test_quantidade_fixa_e_destacada(self):
        fixo = {"targetKind": "FIXED", "targetCount": 30}
        origem = _marco("LP01")
        origem["cutRule"] = {**origem["cutRule"], **fixo}
        destino = _marco("LP02")
        destino["cutRule"] = {**destino["cutRule"], "targetKind": "FIXED", "targetCount": 12}
        perfis = [_perfil("LP01", marcos=[origem]), _perfil("LP02", marcos=[destino])]

        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        assert efeito.quantidade_fixa == (12, 30)

    def test_a_origem_inexistente_e_recusada(self):
        with pytest.raises(LookupError):
            aplicacao.efeitos_do_marco([_perfil("LP01")], origem="perfil-LP01", sub=0)

    def test_a_assinatura_e_estavel_e_muda_quando_o_efeito_muda(self):
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02")]
        primeira = aplicacao.assinatura(
            aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0, nova=_sequencia())
        )
        segunda = aplicacao.assinatura(
            aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)
        )
        assert primeira == segunda

        perfis[0]["classificationMilestones"][0]["cutRule"]["surplusCount"] = 3
        terceira = aplicacao.assinatura(
            aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)
        )
        assert terceira != primeira

    def test_aplicar_toca_so_os_incluidos_e_aplicaveis(self):
        perfis = [
            _perfil("LP01", marcos=[_marco("LP01")]),
            _perfil("LP02"),
            _perfil("LP03"),
            _perfil("LP04", fatos=[]),
        ]
        efeitos = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

        depois = aplicacao.aplicar_marcos(perfis, efeitos, incluidos={"perfil-LP02", "perfil-LP04"})

        por_codigo = {perfil["code"]: perfil for perfil in depois}
        assert len(por_codigo["LP02"]["classificationMilestones"]) == 1
        assert por_codigo["LP03"]["classificationMilestones"] == []
        assert por_codigo["LP04"]["classificationMilestones"] == []

    def test_a_impressao_do_destino_e_a_da_unidade_gravada(self):
        perfis = [_perfil("LP01", marcos=[_marco("LP01")]), _perfil("LP02")]
        (efeito,) = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)
        (depois,) = [
            perfil
            for perfil in aplicacao.aplicar_marcos(perfis, [efeito], {"perfil-LP02"})
            if perfil["code"] == "LP02"
        ]

        assert efeito.impressao == aplicacao.impressao(
            aplicacao.unidade_do_marco(depois["classificationMilestones"][0], depois)
        )


def _modalidade(codigo, identidade, *, percentual="5", nome=None):
    return {
        "id": identidade,
        "code": codigo,
        "name": nome or codigo,
        "description": "",
        "normativeRule": {
            "id": f"regra-{identidade}",
            "foundation": "Lei 12.711",
            "version": "2016",
            "percentage": percentual,
            "rounding": {"mode": "PARA_CIMA"},
        },
    }


class TestModalidade:
    def test_nasce_onde_o_codigo_falta_e_lista_o_que_o_destino_tem(self):
        origem = _perfil("LP01", competitionModalities=[_modalidade("PCD", "m1")])
        destino = _perfil("LP02", competitionModalities=[_modalidade("DEF", "m2")])

        (efeito,) = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        assert efeito.efeito == NASCE
        assert efeito.ja_declara == ("DEF",)
        assert efeito.depois["id"] != "m1"
        assert efeito.depois["normativeRule"]["id"] != "regra-m1"

    def test_substitui_os_campos_e_nunca_o_codigo_nem_a_identidade(self):
        origem = _perfil("LP01", competitionModalities=[_modalidade("PCD", "m1", percentual="5")])
        destino = _perfil("LP02", competitionModalities=[_modalidade("PCD", "m2", percentual="10")])

        (efeito,) = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        assert efeito.efeito == SUBSTITUI
        assert efeito.depois["id"] == "m2"
        assert efeito.depois["normativeRule"]["id"] == "regra-m2"
        assert efeito.depois["normativeRule"]["percentage"] == "5"

    def test_nunca_remove_nem_toca_o_quadro(self):
        quadro = [{"id": "l", "modalityId": "m3", "immediateVacancies": 2}]
        origem = _perfil("LP01", competitionModalities=[_modalidade("PCD", "m1")])
        destino = _perfil(
            "LP02",
            competitionModalities=[_modalidade("PPI", "m3")],
            vacancyTable=quadro,
        )
        efeitos = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        _, depois = aplicacao.aplicar_modalidades([origem, destino], efeitos, {"1"})

        assert [item["code"] for item in depois["competitionModalities"]] == ["PPI", "PCD"]
        assert depois["vacancyTable"] == quadro

    def test_a_ampla_da_origem_substitui_a_do_destino(self):
        origem = _perfil(
            "LP01",
            competitionModalities=[_modalidade("AC", "m1")],
            generalCompetitionModalityId="m1",
        )
        destino = _perfil(
            "LP02",
            competitionModalities=[_modalidade("OUTRA", "m9")],
            generalCompetitionModalityId="m9",
        )
        efeitos = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        assert efeitos[0].ampla == ("OUTRA", "AC")
        _, depois = aplicacao.aplicar_modalidades([origem, destino], efeitos, {"1"})
        nova = next(item for item in depois["competitionModalities"] if item["code"] == "AC")
        assert depois["generalCompetitionModalityId"] == nova["id"]

    def test_a_origem_que_nao_e_a_ampla_desmarca_o_destino_que_a_apontava(self):
        origem = _perfil("LP01", competitionModalities=[_modalidade("AC", "m1")])
        destino = _perfil(
            "LP02",
            competitionModalities=[_modalidade("AC", "m2")],
            generalCompetitionModalityId="m2",
        )
        efeitos = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        assert efeitos[0].efeito == SUBSTITUI
        assert efeitos[0].ampla == ("AC", "")
        _, depois = aplicacao.aplicar_modalidades([origem, destino], efeitos, {"1"})
        assert depois["generalCompetitionModalityId"] is None

    def test_igual_nao_muda(self):
        origem = _perfil("LP01", competitionModalities=[_modalidade("PCD", "m1")])
        destino = _perfil("LP02", competitionModalities=[_modalidade("PCD", "m2")])

        (efeito,) = aplicacao.efeitos_da_modalidade([origem, destino], origem=0, indice=0)

        assert efeito.efeito == SEM_MUDANCA


class TestCampoDoPerfil:
    def test_forma_de_convocacao_nasce_substitui_e_nao_muda(self):
        perfis = [
            _perfil("LP01", callForm=None),
            _perfil("LP02", callForm="PUBLICATION"),
            _perfil("LP03", callForm="INDIVIDUAL_MESSAGE"),
        ]

        efeitos = aplicacao.efeitos_do_campo_do_perfil(
            perfis, campo="callForm", valor="INDIVIDUAL_MESSAGE"
        )

        assert [item.efeito for item in efeitos] == [NASCE, SUBSTITUI, SEM_MUDANCA]
        depois = aplicacao.aplicar_campo_do_perfil(
            perfis, efeitos, {"0", "1", "2"}, campo="callForm", valor="INDIVIDUAL_MESSAGE"
        )
        assert {perfil["callForm"] for perfil in depois} == {"INDIVIDUAL_MESSAGE"}

    def test_reversao_fica_fora_sem_lista_reservada(self):
        com_lista = _perfil(
            "LP01",
            competitionModalities=[_modalidade("PPI", "m1")],
            generalCompetitionModalityId=None,
        )
        sem_lista = _perfil("LP02", competitionModalities=[])

        efeitos = aplicacao.efeitos_do_campo_do_perfil(
            [com_lista, sem_lista], campo="vacancyReversion", valor="GERAL"
        )

        assert efeitos[0].efeito == NASCE
        assert efeitos[1].efeito == FORA

    def test_valor_comum_so_quando_todos_concordam(self):
        iguais = [_perfil("A", callForm="PUBLICATION"), _perfil("B", callForm="PUBLICATION")]
        diferentes = [*iguais, _perfil("C", callForm=None)]

        assert aplicacao.valor_comum(iguais, "callForm") == "PUBLICATION"
        assert aplicacao.valor_comum(diferentes, "callForm") == ""


def test_nada_fora_da_unidade_muda_no_destino():
    destino = _perfil("LP02", locality="Vitória", callForm="PUBLICATION")
    perfis = [_perfil("LP01", marcos=[_marco("LP01")]), copy.deepcopy(destino)]
    efeitos = aplicacao.efeitos_do_marco(perfis, origem="perfil-LP01", sub=0)

    _, depois = aplicacao.aplicar_marcos(perfis, efeitos, {"perfil-LP02"})

    assert {k: v for k, v in depois.items() if k != "classificationMilestones"} == {
        k: v for k, v in destino.items() if k != "classificationMilestones"
    }
