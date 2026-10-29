"""A publicação recusa a extração que o sorteio nunca aceitaria (102, FR-2652–FR-2657).

**O caso é o Edital 72/2026.** Inscrições até 28/10 às 9h; Loteria Federal, concurso 6113, extração
declarada para 28/10 às 20h05. A Caixa publica só a data, a data vale a partir de 00h00, e a relação
só se congela depois do fim das inscrições: o sorteio estava condenado desde a publicação. Aqui a
conferência é chamada sobre o conteúdo, sem banco e sem rede — ela lê o que o Edital declara, e não
consulta fonte nenhuma.
"""

import copy

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)
from tests.fixtures.edital import DRAW_METHOD, complete_draft, identidade_do_marco, identificador

NA_PUBLICACAO = "draw_occurrence_not_after_registration"
NA_RETIFICACAO = "draw_occurrence_not_after_registration_on_retification"
CODIGOS = {NA_PUBLICACAO, NA_RETIFICACAO}

FIM = "2026-10-28T09:00:00-03:00"
NO_DIA_DO_FIM = "2026-10-28T20:05:00-03:00"
NO_DIA_SEGUINTE = "2026-10-29T20:05:00-03:00"


def _metodo(ocorre_em=NO_DIA_DO_FIM, fonte="Loteria Federal"):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": "6113", "occurrenceAt": ocorre_em})
    return metodo


def _edital_72(*, ocorre_em=NO_DIA_DO_FIM, fonte="Loteria Federal", fim=FIM):
    rascunho = complete_draft()
    evento = rascunho["schedule"][0]
    evento.update(
        {
            "startAt": "2026-10-01T09:00:00-03:00",
            "endAt": fim,
            "isRegistrationPeriod": True,
            "status": "PLANEJADO",
        }
    )
    marco = rascunho["profiles"][0]["classificationMilestones"][0]
    marco["drawMethod"] = _metodo(ocorre_em, fonte)
    return rascunho


def _achados(conteudo, ato=ATO_DE_PUBLICACAO, **opcoes):
    return [
        item
        for item in validate_for_publication(conteudo, ato=ato, **opcoes)
        if item.code in CODIGOS
    ]


def _marco_id(conteudo, perfil=0):
    return conteudo["profiles"][perfil]["classificationMilestones"][0]["id"]


# --- o caso, e a contraprova ----------------------------------------------------------------


def test_a_extracao_no_dia_do_fim_das_inscricoes_impede_a_publicacao():
    (achado,) = _achados(_edital_72())

    assert achado.code == NA_PUBLICACAO
    assert achado.severity == Severity.BLOCKING_ERROR
    assert achado.path.endswith(
        f"/classificationMilestones/id={_marco_id(_edital_72())}/drawMethod"
    )


def test_a_mensagem_diz_o_marco_a_fonte_o_dia_o_fim_e_o_que_mudar():
    """Seção 1 do contrato de mensagens: tudo o que quem elabora precisa para corrigir."""
    (achado,) = _achados(_edital_72())

    assert "O marco M1" in achado.message
    assert "Loteria Federal" in achado.message
    assert "28/10/2026" in achado.message
    assert "28/10/2026 às 09:00" in achado.message, "o fim por extenso, no fuso institucional"
    assert "publica só a data" in achado.message
    assert "00h00" in achado.message
    assert "dia posterior a 28/10/2026" in achado.message
    assert "encerre as inscrições antes de 28/10/2026" in achado.message


@pytest.mark.parametrize(
    ("ocorre_em", "acusa"),
    [
        ("2026-10-27T20:05:00-03:00", True),
        ("2026-10-28T08:00:00-03:00", True),
        (NO_DIA_DO_FIM, True),
        ("2026-10-29T00:00:00-03:00", False),
        (NO_DIA_SEGUINTE, False),
    ],
)
def test_a_matriz_do_fim_das_inscricoes(ocorre_em, acusa):
    """SC-954 pela conferência inteira, e não só pela regra pura."""
    assert bool(_achados(_edital_72(ocorre_em=ocorre_em))) is acusa


def test_o_metodo_comum_e_acusado_uma_vez_no_caminho_dele():
    rascunho = _edital_72()
    rascunho["profiles"][0]["classificationMilestones"][0].pop("drawMethod")
    segundo = copy.deepcopy(rascunho["profiles"][0])
    segundo["id"] = identificador(401, 7)
    segundo["code"] = "P2"
    segundo["classificationMilestones"][0]["id"] = identidade_do_marco(segundo["id"])
    rascunho["profiles"].append(segundo)
    rascunho["drawMethod"] = {
        chave: valor for chave, valor in _metodo().items() if chave != "qualifyingStageId"
    }

    (achado,) = _achados(rascunho)

    assert achado.path == "/drawMethod"
    assert "O método comum a este Edital" in achado.message


def test_dois_marcos_com_metodo_proprio_tem_um_achado_cada():
    rascunho = _edital_72()
    segundo = copy.deepcopy(rascunho["profiles"][0])
    segundo["id"] = identificador(401, 7)
    segundo["code"] = "P2"
    segundo["classificationMilestones"][0]["id"] = identidade_do_marco(segundo["id"])
    segundo["classificationMilestones"][0]["code"] = "M2"
    rascunho["profiles"].append(segundo)

    achados = _achados(rascunho)

    assert len(achados) == 2
    assert {a.path.split("/classificationMilestones/")[0] for a in achados} == {
        f"/profiles/id={rascunho['profiles'][0]['id']}",
        f"/profiles/id={segundo['id']}",
    }


# --- onde a conferência se cala (FR-2655, FR-2657) -----------------------------------------


def test_sem_periodo_designado_nao_ha_achado():
    rascunho = _edital_72()
    rascunho["schedule"][0]["isRegistrationPeriod"] = False

    assert _achados(rascunho) == []


def test_periodo_sem_termino_nao_ha_achado():
    rascunho = _edital_72()
    rascunho["schedule"][0]["endAt"] = None

    assert _achados(rascunho) == []


def test_periodo_cancelado_nao_ha_achado():
    rascunho = _edital_72()
    rascunho["schedule"][0]["status"] = "CANCELADO"

    assert _achados(rascunho) == []


def test_dois_eventos_marcados_deixam_a_resposta_ao_achado_de_ambiguidade():
    rascunho = _edital_72()
    outro = copy.deepcopy(rascunho["schedule"][0])
    outro["id"] = identificador(402, 7)
    outro["order"] = 2
    rascunho["schedule"].append(outro)

    codigos = {item.code for item in validate_for_publication(rascunho)}

    assert "registration_period_ambiguous" in codigos
    assert not codigos & CODIGOS


def test_fonte_fora_do_vocabulario_tem_so_o_achado_dela():
    rascunho = _edital_72(fonte="Random.org")

    codigos = {item.code for item in validate_for_publication(rascunho)}

    assert "draw_method_invalid" in codigos
    assert not codigos & CODIGOS


def test_metodo_invalido_por_outro_campo_nao_soma_este_achado():
    rascunho = _edital_72()
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"]["normalization"] = {
        "rule": "INVENTADA",
        "text": "x",
    }

    codigos = {item.code for item in validate_for_publication(rascunho)}

    assert "draw_method_invalid" in codigos
    assert not codigos & CODIGOS


def test_fonte_com_horario_nao_e_conferida():
    """D-006: a demonstração atual, com extração em 2020, é o que a suíte inteira usa."""
    assert _achados(_edital_72(fonte="Fonte de demonstração")) == []
    assert (
        _achados(_edital_72(ocorre_em="2020-01-01T20:00:00-03:00", fonte="Fonte de demonstração"))
        == []
    )


# --- na Retificação (FR-2656, D-003, D-005) --------------------------------------------------


def test_na_retificacao_e_advertencia_com_codigo_proprio():
    """Código próprio: `advertencias_do_ato` subtrai os impeditivos da publicação (R-004)."""
    (achado,) = _achados(_edital_72(), ATO_DE_RETIFICACAO)

    assert achado.code == NA_RETIFICACAO
    assert achado.severity == Severity.WARNING
    assert "Se a relação ainda não foi congelada" in achado.message
    assert "retificar o método e depois publicar relação nova, sucedendo a atual" in achado.message


def test_na_retificacao_o_marco_ja_sorteado_nao_e_advertido():
    rascunho = _edital_72()

    achados = _achados(
        rascunho, ATO_DE_RETIFICACAO, marcos_sorteados=frozenset({_marco_id(rascunho)})
    )

    assert achados == []


def test_na_publicacao_o_marco_sorteado_nao_muda_nada():
    """Só a Retificação passa o conjunto; na publicação não há sorteio a constituir antes."""
    rascunho = _edital_72()

    assert _achados(rascunho, marcos_sorteados=frozenset({_marco_id(rascunho)}))


def test_o_metodo_comum_adverte_enquanto_algum_marco_dele_nao_estiver_sorteado():
    rascunho = _edital_72()
    rascunho["profiles"][0]["classificationMilestones"][0].pop("drawMethod")
    segundo = copy.deepcopy(rascunho["profiles"][0])
    segundo["id"] = identificador(401, 7)
    segundo["code"] = "P2"
    segundo["classificationMilestones"][0]["id"] = identidade_do_marco(segundo["id"])
    rascunho["profiles"].append(segundo)
    rascunho["drawMethod"] = {
        chave: valor for chave, valor in _metodo().items() if chave != "qualifyingStageId"
    }
    um = _marco_id(rascunho, 0)
    outro = _marco_id(rascunho, 1)

    assert _achados(rascunho, ATO_DE_RETIFICACAO, marcos_sorteados=frozenset({um}))
    assert _achados(rascunho, ATO_DE_RETIFICACAO, marcos_sorteados=frozenset({um, outro})) == []
