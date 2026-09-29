"""A regra do "aplicar a todos" na Retificação, unidade a unidade (051, US5, FR-938 a FR-940).

Função pura sobre o conteúdo proposto. O que se prende aqui é o que erra em silêncio: a Alteração
que alcança campo não retificável, a aplicação parcial, o objeto que nasce sem a guarda da `048`, a
declaração publicada que sumiria em lote, e a identidade que mudaria entre conferir e confirmar.
"""

import copy

import pytest

from processo_seletivo.publicacoes.domain import aplicacao as gesto
from processo_seletivo.publicacoes.domain.changes import apply_changes

ETAPA_A = "00000000-0000-4000-8000-00000000e001"
ETAPA_B = "00000000-0000-4000-8000-00000000e002"


_HEX = {"p": "a", "f": "f", "a": "ac", "b": "b", "r": "e", "l": "d", "m": "dd", "c": "c"}
_HEX |= {"t": "ee", "n": "bb", "z": "ff"}


def _id(tipo, n):
    """Identidade legível e válida: a gramática recusa elemento sem UUID por chave."""
    return f"00000000-0000-4000-8000-{_HEX[tipo]:0>4}{n:0>8}"


def _perfil(n, *, dias=2, fato=True, especie="FROM_VACANCY_TABLE", etapas=(ETAPA_A,)):
    fato_id = _id("f", n)
    ac, ppi = _id("a", n), _id("b", n)
    return {
        "id": _id("p", n),
        "code": f"P{n}",
        "name": f"Perfil {n}",
        "declaredFacts": (
            [{"id": fato_id, "code": "NASC", "label": "Nascimento", "type": "DATA"}] if fato else []
        ),
        "competitionModalities": [
            {"id": ac, "code": "AC", "name": "Ampla", "description": "", "normativeRule": None},
            {
                "id": ppi,
                "code": "PPI",
                "name": "Pretos, pardos e indígenas",
                "description": "",
                "normativeRule": {
                    "id": _id("r", n),
                    "foundation": "Lei 12.711/2012",
                    "version": "1",
                    "percentage": "20.0000",
                    "calculation": {"x": n},
                    "rounding": {},
                    "distribution": {},
                    "callRules": {},
                    "effectiveFrom": None,
                },
            },
        ],
        "generalCompetitionModalityId": ac,
        "vacancyTable": [
            {"id": _id("l", n), "modalityId": None, "immediateVacancies": 8},
            {"id": _id("m", n), "modalityId": ppi, "immediateVacancies": 2},
        ],
        "vacancyReversion": None,
        "callForm": "PUBLICATION",
        "classificationMilestones": [
            {
                "id": _id("c", n),
                "code": f"P{n}",
                "name": f"Classificação P{n}",
                "orderProduction": "POR_PONTUACAO",
                "stages": list(etapas),
                "operation": "SOMA_PONDERADA",
                "normalization": "NENHUMA",
                "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
                "appealWindow": {"admits": True, "durationDays": dias, "unit": "DIAS_CORRIDOS"},
                "drawMethod": None,
                "cutRule": {
                    "targetKind": especie,
                    "targetCount": 10 if especie == "FIXED" else None,
                    "surplusCount": 0,
                    "tieOutcome": "ADMITS_SURPLUS",
                    "governedStage": "NONE",
                    "continuation": "NONE",
                },
                "tiebreakers": [
                    {
                        "id": _id("t", n),
                        "order": 1,
                        "type": "MAIOR_PONTUACAO_NA_ETAPA",
                        "parameters": {"stageId": ETAPA_A},
                        "whenMissing": "ULTIMO_NO_CRITERIO",
                    }
                ],
            }
        ],
    }


def _conteudo(*perfis):
    return {
        "profiles": list(perfis) or [_perfil(n) for n in range(1, 5)],
        "stages": [{"id": ETAPA_A, "name": "Prova"}, {"id": ETAPA_B, "name": "Títulos"}],
    }


def _marco(conteudo, n):
    return conteudo["profiles"][n - 1]["classificationMilestones"][0]


def _efeitos(conteudo, unidade, *, n=1, alvo=None, **kwargs):
    perfil = conteudo["profiles"][n - 1]
    if alvo is None and unidade in gesto.UNIDADES_DO_MARCO:
        alvo = perfil["classificationMilestones"][0]["id"]
    return gesto.efeitos(conteudo, unidade=unidade, perfil=perfil["id"], alvo=alvo, **kwargs)


def _por_codigo(efeitos):
    return {item.codigo: item for item in efeitos}


# ---- a janela recursal --------------------------------------------------------------------------


def test_a_janela_corrigida_vira_uma_alteracao_por_destino():
    """O *Independent Test* da US5: 2 → 3 dias, uma Alteração por destino e campo."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 3

    efeitos = _efeitos(conteudo, gesto.JANELA)

    assert [item.codigo for item in efeitos] == ["P2", "P3", "P4"]
    for item in efeitos:
        assert item.efeito == gesto.SUBSTITUI
        assert item.alteracoes == (
            {
                "targetPath": f"/profiles/id={item.perfil}/classificationMilestones/"
                f"id={_marco(conteudo, int(item.codigo[1:]))['id']}/appealWindow/durationDays",
                "operation": "REPLACE",
                "newValue": 3,
            },
        )


def test_a_janela_nasce_so_concedendo():
    """FR-940, FR-787 da `048`: a janela que nasce admite recurso."""
    conteudo = _conteudo()
    _marco(conteudo, 2)["appealWindow"] = None
    efeito = _por_codigo(_efeitos(conteudo, gesto.JANELA))["P2"]
    assert efeito.efeito == gesto.NASCE
    assert efeito.alteracoes[0]["newValue"] == {
        "admits": True,
        "durationDays": 2,
        "unit": "DIAS_CORRIDOS",
    }

    _marco(conteudo, 1)["appealWindow"] = {"admits": False, "durationDays": None, "unit": ""}
    fora = _por_codigo(_efeitos(conteudo, gesto.JANELA))["P2"]
    assert fora.efeito == gesto.FORA
    assert "precisa admitir recurso" in fora.motivo
    assert fora.alteracoes == ()


def test_janela_igual_fica_sem_mudanca():
    efeitos = _efeitos(_conteudo(), gesto.JANELA)
    assert {item.efeito for item in efeitos} == {gesto.SEM_MUDANCA}
    assert gesto.alteracoes_alcancadas(efeitos, [item.perfil for item in efeitos]) == []


def test_a_origem_sem_janela_nao_tem_o_que_aplicar():
    """R-013: na Retificação a ausência na origem não se aplica."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"] = None
    with pytest.raises(gesto.SemOrigem, match="não declara janela recursal"):
        _efeitos(conteudo, gesto.JANELA)


# ---- a regra de corte ---------------------------------------------------------------------------


def test_campo_nao_retificavel_diferente_deixa_o_destino_inteiro_fora():
    """FR-939: a espécie do alvo difere em P3, e nem os suplentes, que se retificam, vão."""
    conteudo = _conteudo(_perfil(1), _perfil(2), _perfil(3, especie="FIXED"))
    _marco(conteudo, 1)["cutRule"]["surplusCount"] = 2

    efeitos = _por_codigo(_efeitos(conteudo, gesto.CORTE))

    assert efeitos["P2"].efeito == gesto.SUBSTITUI
    assert [item["targetPath"].rsplit("/", 1)[-1] for item in efeitos["P2"].alteracoes] == [
        "surplusCount"
    ]
    fora = efeitos["P3"]
    assert fora.efeito == gesto.FORA
    assert fora.alteracoes == ()
    assert fora.motivo.startswith("a espécie do alvo do corte difere da origem")
    assert fora.campo_fora == (
        "classificationMilestones",
        "cutRule/targetKind",
        "FIXED",
        "FROM_VACANCY_TABLE",
    )


def test_o_corte_nasce_inteiro_e_nao_sobre_etapa_com_resultado():
    """FR-940, FR-789 da `048`."""
    conteudo = _conteudo()
    _marco(conteudo, 2)["cutRule"] = None
    _marco(conteudo, 1)["cutRule"]["governedStage"] = ETAPA_B

    nasce = _por_codigo(_efeitos(conteudo, gesto.CORTE))["P2"]
    assert nasce.efeito == gesto.NASCE
    assert nasce.alteracoes[0]["targetPath"].endswith("/cutRule")
    assert nasce.alteracoes[0]["newValue"]["governedStage"] == ETAPA_B

    fora = _por_codigo(_efeitos(conteudo, gesto.CORTE, tem_resultado=lambda e: e == ETAPA_B))["P2"]
    assert fora.efeito == gesto.FORA
    assert "Títulos" in fora.motivo and "Resultado" in fora.motivo


def test_a_quantidade_fixa_e_destacada():
    """FR-917."""
    conteudo = _conteudo(_perfil(1, especie="FIXED"), _perfil(2, especie="FIXED"))
    _marco(conteudo, 1)["cutRule"]["targetCount"] = 12
    efeito = _efeitos(conteudo, gesto.CORTE)[0]
    assert efeito.quantidade_fixa == (10, 12)


# ---- os campos do marco -------------------------------------------------------------------------


def test_as_etapas_diferentes_deixam_o_destino_fora():
    """US5, cenário 2: as Etapas do marco não se retificam."""
    conteudo = _conteudo(_perfil(1), _perfil(2, etapas=(ETAPA_A, ETAPA_B)), _perfil(3))
    _marco(conteudo, 1)["operation"] = "MEDIA_PONDERADA"

    efeitos = _por_codigo(_efeitos(conteudo, gesto.CAMPOS_DO_MARCO))

    assert efeitos["P2"].efeito == gesto.FORA
    assert "as Etapas que o marco mede" in efeitos["P2"].motivo
    assert efeitos["P3"].efeito == gesto.SUBSTITUI
    assert efeitos["P3"].alteracoes[0]["targetPath"].endswith("/operation")


def test_o_campo_que_falta_no_destino_nao_nasce():
    conteudo = _conteudo()
    del _marco(conteudo, 2)["orderProduction"]
    _marco(conteudo, 1)["orderProduction"] = "POR_SORTEIO"
    efeito = _por_codigo(_efeitos(conteudo, gesto.CAMPOS_DO_MARCO))["P2"]
    assert efeito.efeito == gesto.FORA
    assert "não nasce por Retificação" in efeito.motivo


def test_o_metodo_guardado_nao_passa_a_governar_a_ordem():
    """FR-922: a forma virando sorteio faria o método guardado do destino ser próprio."""
    conteudo = _conteudo()
    _marco(conteudo, 2)["drawMethod"] = {"algorithm": "IFES-SORTEIO-SHA256-v1"}
    _marco(conteudo, 1)["orderProduction"] = "POR_SORTEIO"
    efeito = _por_codigo(_efeitos(conteudo, gesto.CAMPOS_DO_MARCO))["P2"]
    assert efeito.efeito == gesto.FORA
    assert "método de sorteio próprio" in efeito.motivo


def test_dois_marcos_no_destino_ficam_fora():
    conteudo = _conteudo()
    segundo = copy.deepcopy(_marco(conteudo, 2))
    segundo["id"] = _id("z", 2)
    conteudo["profiles"][1]["classificationMilestones"].append(segundo)
    efeito = _por_codigo(_efeitos(conteudo, gesto.JANELA))["P2"]
    assert efeito.efeito == gesto.FORA
    assert "2 marcos" in efeito.motivo


# ---- os critérios de desempate ------------------------------------------------------------------


def _por_fato(conteudo, n):
    perfil = conteudo["profiles"][n - 1]
    return {
        "id": _id("n", n),
        "order": 1,
        "type": "MENOR_VALOR_DE_FATO",
        "parameters": {"factId": perfil["declaredFacts"][0]["id"]},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }


def test_o_criterio_trocado_vira_remocao_e_acrescimo_com_o_fato_do_destino():
    """US5, cenário 1; FR-792 da `048`; FR-914."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["tiebreakers"] = [_por_fato(conteudo, 1)]

    efeito = _por_codigo(_efeitos(conteudo, gesto.CRITERIOS))["P2"]

    assert efeito.efeito == gesto.SUBSTITUI
    remocao, acrescimo = efeito.alteracoes
    assert remocao["operation"] == "REMOVE"
    assert remocao["targetPath"].endswith(f"/tiebreakers/id={_id('t', 2)}")
    assert acrescimo["operation"] == "ADD"
    assert acrescimo["targetPath"].endswith("/tiebreakers/-")
    assert acrescimo["newValue"]["parameters"] == {"factId": _id("f", 2)}, "o fato é o do destino"
    assert acrescimo["newValue"]["id"] not in {_id("n", 1), _id("t", 2)}


def test_o_fato_sem_correspondente_deixa_fora():
    conteudo = _conteudo(_perfil(1), _perfil(2, fato=False))
    _marco(conteudo, 1)["tiebreakers"] = [_por_fato(conteudo, 1)]
    efeito = _efeitos(conteudo, gesto.CRITERIOS)[0]
    assert efeito.efeito == gesto.FORA
    assert "NASC" in efeito.motivo


def test_so_a_ordem_diferente_vira_replace_da_ordem():
    conteudo = _conteudo()
    _marco(conteudo, 1)["tiebreakers"][0]["order"] = 2
    efeito = _por_codigo(_efeitos(conteudo, gesto.CRITERIOS))["P2"]
    assert efeito.alteracoes == (
        {
            "targetPath": f"/profiles/id={_id('p', 2)}/classificationMilestones/id={_id('c', 2)}"
            f"/tiebreakers/id={_id('t', 2)}/order",
            "operation": "REPLACE",
            "newValue": 2,
        },
    )


def test_a_identidade_do_que_nasce_e_estavel():
    """R-011: conferir e confirmar calculam duas vezes, e o ato precisa ser o mesmo."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["tiebreakers"] = [_por_fato(conteudo, 1)]
    primeira = _efeitos(conteudo, gesto.CRITERIOS)
    segunda = _efeitos(copy.deepcopy(conteudo), gesto.CRITERIOS)
    assert [item.alteracoes for item in primeira] == [item.alteracoes for item in segunda]
    assert gesto.assinatura(primeira) == gesto.assinatura(segunda)


# ---- a forma de convocação e a reversão ----------------------------------------------------------


def test_a_forma_de_convocacao_nasce_substitui_ou_fica():
    conteudo = _conteudo()
    conteudo["profiles"][0]["callForm"] = "INDIVIDUAL_MESSAGE"
    conteudo["profiles"][2]["callForm"] = None
    conteudo["profiles"][3]["callForm"] = "INDIVIDUAL_MESSAGE"
    efeitos = _por_codigo(_efeitos(conteudo, gesto.FORMA_DE_CONVOCACAO))
    assert efeitos["P2"].efeito == gesto.SUBSTITUI
    assert efeitos["P3"].efeito == gesto.NASCE
    assert efeitos["P4"].efeito == gesto.SEM_MUDANCA
    assert efeitos["P2"].alteracoes == (
        {
            "targetPath": f"/profiles/id={_id('p', 2)}/callForm",
            "operation": "REPLACE",
            "newValue": "INDIVIDUAL_MESSAGE",
        },
    )

    conteudo["profiles"][0]["callForm"] = None
    with pytest.raises(gesto.SemOrigem, match="não declara forma de convocação"):
        _efeitos(conteudo, gesto.FORMA_DE_CONVOCACAO)


def test_a_reversao_nasce_pelo_objeto_e_fica_fora_sem_lista_reservada():
    conteudo = _conteudo()
    conteudo["profiles"][0]["vacancyReversion"] = {"kind": "ON_BALANCE"}
    conteudo["profiles"][2]["vacancyReversion"] = {"kind": "ON_EXHAUSTION"}
    sem_reserva = conteudo["profiles"][3]
    sem_reserva["competitionModalities"] = sem_reserva["competitionModalities"][:1]
    efeitos = _por_codigo(_efeitos(conteudo, gesto.REVERSAO))
    assert efeitos["P2"].efeito == gesto.NASCE
    assert efeitos["P2"].alteracoes[0]["targetPath"].endswith("/vacancyReversion")
    assert efeitos["P2"].alteracoes[0]["newValue"] == {"kind": "ON_BALANCE"}
    assert efeitos["P3"].alteracoes[0]["targetPath"].endswith("/vacancyReversion/kind")
    assert efeitos["P4"].efeito == gesto.FORA


# ---- a Modalidade --------------------------------------------------------------------------------


def _ppi(conteudo, n):
    return conteudo["profiles"][n - 1]["competitionModalities"][1]


def test_a_modalidade_substitui_campo_a_campo_e_mantem_os_opacos():
    """FR-924: percentual `20` e `20.0000` são o mesmo; o cálculo do destino fica."""
    conteudo = _conteudo()
    _ppi(conteudo, 1)["normativeRule"]["percentage"] = "25.0000"
    _ppi(conteudo, 3)["normativeRule"]["percentage"] = "25"
    efeitos = _por_codigo(_efeitos(conteudo, gesto.MODALIDADE, alvo=_ppi(conteudo, 1)["id"]))
    assert efeitos["P2"].alteracoes == (
        {
            "targetPath": f"/profiles/id={_id('p', 2)}/competitionModalities/id={_id('b', 2)}"
            "/normativeRule/percentage",
            "operation": "REPLACE",
            "newValue": "25.0000",
        },
    )
    assert efeitos["P3"].efeito == gesto.SEM_MUDANCA
    assert efeitos["P2"].ja_declara == ("AC", "PPI")


def test_a_modalidade_nasce_pelo_acrescimo_sem_linha_do_quadro():
    """FR-924, FR-777 da `048`; o acréscimo de outra Modalidade digitado não é o mesmo campo."""
    conteudo = _conteudo()
    conteudo["profiles"][1]["competitionModalities"].pop()
    outra = {
        "targetPath": f"/profiles/id={_id('p', 2)}/competitionModalities/-",
        "operation": "ADD",
        "newValue": {"code": "PCD"},
    }
    efeito = _por_codigo(
        _efeitos(conteudo, gesto.MODALIDADE, alvo=_ppi(conteudo, 1)["id"], alterados=[outra])
    )["P2"]
    assert efeito.efeito == gesto.NASCE
    (acrescimo,) = efeito.alteracoes
    assert acrescimo["operation"] == "ADD"
    nova = acrescimo["newValue"]
    assert nova["code"] == "PPI"
    assert nova["normativeRule"]["calculation"] == {}, "o opaco não viaja"
    assert nova["id"] == gesto.derivada("modalidade", _id("p", 2), "PPI")


def test_a_ampla_da_origem_vai_ao_destino():
    """FR-925."""
    conteudo = _conteudo()
    conteudo["profiles"][1]["generalCompetitionModalityId"] = None
    efeito = _por_codigo(
        _efeitos(
            conteudo,
            gesto.MODALIDADE,
            alvo=conteudo["profiles"][0]["competitionModalities"][0]["id"],
        )
    )["P2"]
    assert efeito.alteracoes == (
        {
            "targetPath": f"/profiles/id={_id('p', 2)}/generalCompetitionModalityId",
            "operation": "REPLACE",
            "newValue": _id("a", 2),
        },
    )


def test_o_arredondamento_da_reserva_diferente_deixa_fora():
    conteudo = _conteudo()
    _ppi(conteudo, 1)["normativeRule"]["rounding"] = {"mode": "PARA_CIMA"}
    efeito = _efeitos(conteudo, gesto.MODALIDADE, alvo=_ppi(conteudo, 1)["id"])[0]
    assert efeito.efeito == gesto.FORA
    assert "o arredondamento da reserva" in efeito.motivo


def test_a_regra_normativa_nao_nasce_em_modalidade_publicada():
    """FR-940."""
    conteudo = _conteudo()
    _ppi(conteudo, 2)["normativeRule"] = None
    efeito = _efeitos(conteudo, gesto.MODALIDADE, alvo=_ppi(conteudo, 1)["id"])[0]
    assert efeito.efeito == gesto.FORA
    assert "não nasce em Modalidade publicada" in efeito.motivo


# ---- o ato ---------------------------------------------------------------------------------------


def test_o_destino_ja_alterado_no_ato_fica_fora():
    """R-014: duas Alterações no mesmo caminho, e a última venceria em silêncio."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 3
    digitada = {
        "targetPath": f"/profiles/id={_id('p', 3)}/classificationMilestones/id={_id('c', 3)}"
        "/appealWindow/durationDays",
        "operation": "REPLACE",
        "newValue": 5,
    }
    _marco(conteudo, 3)["appealWindow"]["durationDays"] = 5
    efeitos = _por_codigo(_efeitos(conteudo, gesto.JANELA, alterados=[digitada]))
    assert efeitos["P3"].efeito == gesto.FORA
    assert "já tem, nesta Retificação" in efeitos["P3"].motivo
    assert efeitos["P2"].efeito == gesto.SUBSTITUI


def test_o_perfil_removido_no_ato_fica_fora():
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 3
    removido = {"targetPath": f"/profiles/id={_id('p', 4)}", "operation": "REMOVE"}
    efeito = _por_codigo(_efeitos(conteudo, gesto.JANELA, alterados=[removido]))["P4"]
    assert efeito.efeito == gesto.FORA
    assert efeito.motivo == "é removido por esta Retificação"


def test_so_os_marcados_e_aplicaveis_entram_no_ato():
    """FR-918, SC-342."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 3
    efeitos = _efeitos(conteudo, gesto.JANELA)
    alteracoes = gesto.alteracoes_alcancadas(efeitos, [_id("p", 2), _id("p", 4)])
    assert len(alteracoes) == 2
    assert all(_id("p", 3) not in item["targetPath"] for item in alteracoes)


def test_a_assinatura_muda_quando_o_valor_da_origem_muda():
    """FR-919."""
    conteudo = _conteudo()
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 3
    antes = gesto.assinatura(_efeitos(conteudo, gesto.JANELA))
    _marco(conteudo, 1)["appealWindow"]["durationDays"] = 4
    assert gesto.assinatura(_efeitos(conteudo, gesto.JANELA)) != antes


@pytest.mark.parametrize(
    "unidade", [gesto.JANELA, gesto.CORTE, gesto.CRITERIOS, gesto.CAMPOS_DO_MARCO]
)
def test_as_alteracoes_do_gesto_se_aplicam_ao_conteudo(unidade):
    """O que o gesto produz é o que a gramática aceita: aplicado, o destino fica igual à origem."""
    conteudo = _conteudo()
    marco = _marco(conteudo, 1)
    marco["appealWindow"]["durationDays"] = 4
    marco["cutRule"]["surplusCount"] = 3
    marco["tiebreakers"] = [_por_fato(conteudo, 1)]
    marco["operation"] = "MEDIA_PONDERADA"
    efeitos = _efeitos(conteudo, unidade)
    alteracoes = gesto.alteracoes_alcancadas(efeitos, [item.perfil for item in efeitos])

    resultado, _ = apply_changes(conteudo, alteracoes, publication_id="teste")

    assert {item.efeito for item in _efeitos(resultado, unidade)} == {gesto.SEM_MUDANCA}
