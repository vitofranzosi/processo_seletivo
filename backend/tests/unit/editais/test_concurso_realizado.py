"""A validação de publicação recebe as situações já consultadas (116, FR-3634, FR-3638).

Sem banco e sem rede: as situações são montadas aqui, como o orquestrador as entregaria. A
validação continua pura — ela não consulta fonte nenhuma, e `situacoes=None` quer dizer que a
conferência não rodou, como na revisão e na tela de confirmar, que não podem consultar (FR-3644).
"""

import copy
from datetime import UTC, date, datetime

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)
from processo_seletivo.sorteios.application import conferencia
from processo_seletivo.sorteios.domain import conferencia as dominio
from tests.fixtures.edital import DRAW_METHOD, complete_draft, identidade_do_marco, identificador

LF = "Loteria Federal"
AGORA = datetime(2026, 11, 3, 22, 3, tzinfo=UTC)
ULTIMO = dominio.ConsultaDoUltimo(dominio.UltimoConcurso(6114, date(2026, 11, 1), proximo=6115))
CODIGOS = {
    "draw_occurrence_already_drawn",
    "draw_occurrence_not_checked",
    "draw_occurrence_not_drawn_yet",
    "draw_occurrence_malformed",
}


def _edital(*ocorrencias, ocorre_em="2026-12-06T19:00:00-03:00"):
    rascunho = complete_draft()
    modelo = rascunho["profiles"][0]
    rascunho["profiles"] = []
    for indice, ocorrencia in enumerate(ocorrencias):
        perfil = copy.deepcopy(modelo)
        perfil["id"] = identificador(401, 20 + indice)
        perfil["code"] = f"P{indice}"
        marco = perfil["classificationMilestones"][0]
        marco["id"] = identidade_do_marco(perfil["id"])
        marco["code"] = f"M{indice}"
        metodo = copy.deepcopy(DRAW_METHOD)
        metodo.update({"source": LF, "occurrence": ocorrencia, "occurrenceAt": ocorre_em})
        marco["drawMethod"] = metodo
        rascunho["profiles"].append(perfil)
    return rascunho


def _situacoes(conteudo, consulta=ULTIMO, datas=None, ato=ATO_DE_PUBLICACAO):
    referencias = conferencia.referencias_a_conferir(conteudo)
    consultadas = {
        referencia.chave: dominio.situacao(
            fonte=referencia.fonte,
            referencia=referencia.referencia,
            consulta=consulta,
            consultada_em=AGORA,
            data_da_referencia=(datas or {}).get(dominio.numero_do_concurso(referencia.referencia)),
        )
        for referencia in referencias
    }
    return conferencia.conferidas(referencias, consultadas, agora=AGORA)


def _achados(conteudo, situacoes, ato=ATO_DE_PUBLICACAO):
    return [
        item
        for item in validate_for_publication(conteudo, ato=ato, situacoes=situacoes)
        if item.code in CODIGOS
    ]


def test_realizado_e_impeditivo_no_caminho_do_metodo():
    conteudo = _edital("5000")
    (achado,) = _achados(conteudo, _situacoes(conteudo, datas={5000: date(2015, 8, 26)}))
    assert achado.code == "draw_occurrence_already_drawn"
    assert achado.severity == Severity.BLOCKING_ERROR
    marco = conteudo["profiles"][0]["classificationMilestones"][0]["id"]
    assert achado.path.endswith(f"/classificationMilestones/id={marco}/drawMethod")
    assert "O marco M0" in achado.message
    assert "26/08/2015" in achado.message
    assert "6114, de 01/11/2026" in achado.message


def test_um_impeditivo_por_metodo_e_so_no_realizado():
    """Cenário G: 6116 e 6113 — um achado, e só no marco do 6113."""
    conteudo = _edital("6116", "6113")
    achados = _achados(conteudo, _situacoes(conteudo))
    impeditivos = [a for a in achados if a.severity == Severity.BLOCKING_ERROR]
    assert len(impeditivos) == 1
    assert "6113" in impeditivos[0].message
    assert f"id={conteudo['profiles'][1]['id']}" in impeditivos[0].path


def test_inconclusivo_e_advertencia():
    conteudo = _edital("6116")
    consulta = dominio.ConsultaDoUltimo(None, dominio.SEM_RESPOSTA_A_TEMPO)
    (achado,) = _achados(conteudo, _situacoes(conteudo, consulta))
    assert (achado.code, achado.severity) == ("draw_occurrence_not_checked", Severity.WARNING)
    assert "a Caixa não respondeu a tempo" in achado.message


def test_ainda_nao_realizado_e_informacao():
    conteudo = _edital("6116")
    (achado,) = _achados(conteudo, _situacoes(conteudo))
    assert (achado.code, achado.severity) == ("draw_occurrence_not_drawn_yet", Severity.INFO)
    assert "06/12/2026" in achado.message


def test_sem_situacoes_nao_ha_achado_desta_feature():
    """`None` é "a conferência não rodou": a revisão e a tela de confirmar não consultam."""
    assert _achados(_edital("5000"), None) == []


def test_a_forma_invalida_na_publicacao_e_acusada_uma_vez():
    """Na publicação, a forma já é conferida pelo método (FR-3624); a situação não repete."""
    conteudo = _edital("6106-9")
    achados = validate_for_publication(conteudo, situacoes=_situacoes(conteudo))
    assert [a.code for a in achados if a.code in CODIGOS] == []
    (invalido,) = [a for a in achados if a.code == "draw_method_invalid"]
    assert '"6106-9"' in invalido.message


def test_a_forma_invalida_na_retificacao_e_impeditiva():
    """Na Retificação a forma não é reconferida no método (FR-514 da `035`): é a situação."""
    conteudo = _edital("6106-9")
    (achado,) = _achados(conteudo, _situacoes(conteudo), ato=ATO_DE_RETIFICACAO)
    assert (achado.code, achado.severity) == (
        "draw_occurrence_malformed",
        Severity.BLOCKING_ERROR,
    )


def test_a_102_continua_impeditiva():
    """A data inviável impede com qualquer situação, inclusive "ainda não realizado" (FR-3638)."""
    conteudo = _edital("6116", ocorre_em="2026-10-28T20:05:00-03:00")
    conteudo["schedule"][0].update(
        {
            "startAt": "2026-10-01T09:00:00-03:00",
            "endAt": "2026-10-28T09:00:00-03:00",
            "isRegistrationPeriod": True,
            "status": "PLANEJADO",
        }
    )
    for situacoes in (None, _situacoes(conteudo)):
        codigos = {
            a.code
            for a in validate_for_publication(
                conteudo, situacoes=situacoes, agora=datetime(2026, 9, 1, tzinfo=UTC)
            )
            if a.severity == Severity.BLOCKING_ERROR
        }
        assert "draw_occurrence_not_after_registration" in codigos
