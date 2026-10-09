"""O aviso de conferência de recurso: prazos dos marcos ao lado do Cronograma (067, ED-02, D-002).

O sistema não relaciona Evento a marco — o tipo do Evento é texto livre — e por isso não prova que
um prazo corresponde ao outro. O que ele faz é pôr os dois lados na frente de quem elabora, sempre
que algum marco publica regra de recurso, e nunca impedir: no cenário A da auditoria, o único
período de recurso do Cronograma é o da análise documental, e falta o do sorteio — só quem lê os
dois lados percebe. `FR-1305` a `FR-1310`, `UX-190`.
"""

import copy

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    eventos_de_recurso,
    validate_for_publication,
)
from tests.unit.publicacoes.cenarios_da_auditoria import congelado

CODIGO = "appeal_schedule_review"
ORIENTACAO = (
    "O sistema não relaciona o Cronograma aos marcos: confira se há período de recurso para o "
    "resultado de cada marco e se os demais períodos são contra outros atos, ditos assim no texto "
    "do Edital."
)


def _avisos(conteudo, ato=ATO_DE_PUBLICACAO):
    achados = validate_for_publication(conteudo, ato=ato)
    return [achado for achado in achados if achado.code == CODIGO]


def _evento(ordem, tipo, descricao, inicio, fim=None):
    return {
        "id": f"00000000-0000-4000-8000-0000000067{ordem:02d}",
        "type": tipo,
        "description": descricao,
        "startAt": inicio,
        "endAt": fim,
        "order": ordem,
        "status": "PLANEJADO",
        "location": "",
        "isRegistrationPeriod": False,
    }


def _a(**alteracoes):
    """O cenário A da auditoria, com o Cronograma e os marcos que o caso pedir."""
    conteudo = copy.deepcopy(congelado("A")["content"])
    if "schedule" in alteracoes:
        conteudo["schedule"] = alteracoes["schedule"]
    if "janela" in alteracoes:
        for perfil in conteudo["profiles"]:
            for marco in perfil["classificationMilestones"]:
                marco["appealWindow"] = copy.deepcopy(alteracoes["janela"])
    return conteudo


# ---- o Evento de recurso (FR-1305) --------------------------------------------------------------


@pytest.mark.parametrize(
    ("tipo", "descricao", "e_recurso"),
    [
        ("Recurso", "Prazo para interposição de recurso", True),
        ("Prazo", "Interposição de recursos", True),
        ("Prazo recursal", "", True),
        ("RESULTADO", "RECURSO CONTRA O RESULTADO", True),
        ("Concurso", "Concurso de remoção", False),
        ("Percurso", "Percurso formativo", False),
        ("Aula", "Discurso de abertura", False),
        ("Resultado", "Resultado final", False),
    ],
)
def test_o_evento_de_recurso_e_o_que_tem_palavra_iniciada_por_recurs(tipo, descricao, e_recurso):
    evento = _evento(1, tipo, descricao, "2026-11-26T03:00:00+00:00")
    assert bool(eventos_de_recurso({"schedule": [evento]})) is e_recurso


# ---- quando o aviso existe (FR-1306, FR-1308, FR-1309) ------------------------------------------


def test_o_cenario_a_tem_um_aviso_so_com_os_dois_lados():
    (aviso,) = _avisos(_a())

    assert aviso.severity == Severity.WARNING
    assert aviso.path == "schedule"
    assert aviso.message == (
        "Prazos de recurso a conferir. Os marcos publicam recurso: “Classificação por sorteio "
        "eletrônico” (INF-BJN, INF-IUN, INF-SMT, INF-VAL) — 2 (dois) dias corridos, contados da "
        "divulgação desse resultado. O Cronograma tem 1 Evento de recurso: Prazo para interposição "
        "de recurso — de 26/11/2026, às 00h, a 27/11/2026, às 23h59. " + ORIENTACAO
    )


def test_o_cenario_b_lista_os_quatro_eventos_na_ordem_e_resume_os_perfis():
    (aviso,) = _avisos(congelado("B")["content"])

    assert "“Classificação final pela prova de títulos” (18 Perfis) — 3 (três) dias" in (
        aviso.message
    )
    assert "O Cronograma tem 4 Eventos de recurso: " in aviso.message
    posicoes = [
        aviso.message.index(trecho)
        for trecho in (
            "Recurso contra a homologação preliminar das inscrições — de 31/10/2026,",
            "Recurso contra o resultado preliminar da prova de títulos — de 17/11/2026",
            "Recurso contra o resultado preliminar da heteroidentificação — de 27/11/2026",
            "Recurso contra o resultado preliminar da análise documental — de 08/12/2026",
        )
    ]
    assert posicoes == sorted(posicoes)


def test_a_negativa_tambem_e_regra_de_recurso():
    (aviso,) = _avisos(_a(janela={"admits": False}))

    assert (
        "“Classificação por sorteio eletrônico” (INF-BJN, INF-IUN, INF-SMT, INF-VAL) — não cabe "
        "recurso" in aviso.message
    )


def test_sem_regra_de_recurso_em_marco_nenhum_nao_ha_aviso_mesmo_com_eventos_de_recurso():
    """FR-1308: recurso contra ato fora dos marcos (homologação, heteroidentificação) é legítimo."""
    conteudo = _a(janela=None)
    assert eventos_de_recurso(conteudo), "o Cronograma continua com o Evento de recurso"
    assert _avisos(conteudo) == []


def test_cronograma_sem_evento_de_recurso_e_dito():
    conteudo = _a()
    conteudo["schedule"] = [
        evento for evento in conteudo["schedule"] if "recurso" not in evento["description"]
    ]
    (aviso,) = _avisos(conteudo)

    assert "O Cronograma não tem Evento de recurso." in aviso.message
    assert aviso.message.endswith(ORIENTACAO)


def test_mesmo_nome_e_prazos_diferentes_sao_duas_regras():
    conteudo = _a()
    conteudo["profiles"][3]["classificationMilestones"][0]["appealWindow"]["durationDays"] = 5
    (aviso,) = _avisos(conteudo)

    assert "(INF-BJN, INF-IUN, INF-SMT) — 2 (dois) dias corridos" in aviso.message
    assert "(INF-VAL) — 5 (cinco) dias corridos" in aviso.message


def test_evento_sem_termino_e_dito_pelo_inicio():
    conteudo = _a(
        schedule=[_evento(1, "Recurso", "Recurso contra o sorteio", "2026-11-17T12:00:00+00:00")]
    )
    (aviso,) = _avisos(conteudo)

    assert "Recurso contra o sorteio — em 17/11/2026, às 09h." in aviso.message


def test_evento_sem_descricao_e_dito_pelo_tipo():
    conteudo = _a(schedule=[_evento(1, "Prazo recursal", "", "2026-11-17T12:00:00+00:00")])
    (aviso,) = _avisos(conteudo)

    assert "Prazo recursal — em 17/11/2026" in aviso.message


def test_a_mensagem_nao_tem_codigo_caminho_nem_nome_de_campo():
    """UX-190."""
    (aviso,) = _avisos(congelado("B")["content"])

    for interno in ("appealWindow", "schedule", "id=", "/profiles", "durationDays", "POR_"):
        assert interno not in aviso.message, interno


def test_na_retificacao_continua_aviso():
    """FR-1309: nunca impede, em ato nenhum."""
    (aviso,) = _avisos(_a(), ATO_DE_RETIFICACAO)
    assert aviso.severity == Severity.WARNING


def test_a_conferencia_nao_altera_o_conteudo():
    """FR-1310."""
    conteudo = _a()
    antes = copy.deepcopy(conteudo)
    _avisos(conteudo)
    assert conteudo == antes
