"""O alcance da Etapa por Modalidade (163): a resposta pura e os achados de publicação.

O exemplo é o da spec: três Perfis com `AC` (a ampla de cada um), `PPI` e, em dois deles, `PcD`; a
Heteroidentificação alcança só `PPI`. Puro: nada aqui toca o banco.
"""

import copy

import pytest

from processo_seletivo.editais.domain import alcance
from processo_seletivo.editais.domain.etapas import StageValidationError, validate_stage
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication

ETAPA_ID = "00000000-0000-0000-0000-00000000163a"
PROVA_ID = "00000000-0000-0000-0000-00000000163b"
MARCO_ID = "00000000-0000-0000-0000-00000000163c"


def _modalidade(perfil, codigo, nome):
    return {"id": f"{perfil}-{codigo}", "code": codigo, "name": nome}


def _perfil(codigo, *, pcd=True, ppi_nome="Pretos e pardos"):
    modalidades = [
        _modalidade(codigo, "AC", "Ampla concorrência"),
        _modalidade(codigo, "PPI", ppi_nome),
    ]
    if pcd:
        modalidades.append(_modalidade(codigo, "PcD", "Pessoas com deficiência"))
    return {
        "id": f"perfil-{codigo}",
        "code": codigo,
        "name": f"Curso {codigo}",
        "competitionModalities": modalidades,
        "generalCompetitionModalityId": f"{codigo}-AC",
        "classificationMilestones": [],
    }


def _etapa(**extra):
    return {
        "id": ETAPA_ID,
        "name": "Heteroidentificação",
        "order": 2,
        "weight": None,
        "eliminatory": True,
        "classificatory": False,
        "minimumScore": None,
        "evaluationsPerRegistration": 1,
        "maximumScore": None,
        "forma": "DECISORIA",
        "rotuloFavoravel": "Confirmada",
        "rotuloDesfavoravel": "Não confirmada",
        "scheduleEventId": None,
        "criteria": [],
        "modalityCodes": ["PPI"],
        **extra,
    }


def _conteudo(*, etapa=None, perfis=None):
    return {
        "schemaVersion": 22,
        "profiles": perfis
        if perfis is not None
        else [_perfil("C1"), _perfil("C2"), _perfil("C3", pcd=False)],
        "stages": [etapa if etapa is not None else _etapa()],
    }


def _codigos_do_alcance(conteudo):
    return sorted(
        achado.code
        for achado in blocking_findings(validate_for_publication(conteudo))
        if achado.code.startswith("alcance_")
    )


# ---------------------------------------------------------------- a resposta pura (T-003)


def test_sem_alcance_declarado_e_todas_as_inscricoes():
    """D-002: a ausência é "todas", e é o que toda Etapa anterior ao degrau 22 significa."""
    etapa = _etapa(modalityCodes=None)

    assert alcance.codigos(etapa) is None
    assert not alcance.restrita(etapa)
    assert alcance.alcanca(etapa, None)
    assert alcance.alcanca(etapa, "PPI")
    assert alcance.modalidades_alcancadas(_conteudo(etapa=etapa), etapa) is None


def test_a_etapa_restrita_nunca_alcanca_a_inscricao_sem_modalidade():
    """FR-6968: a ampla, na grafia sem Modalidade, nunca é alcançada por Etapa restrita."""
    etapa = _etapa()

    assert not alcance.alcanca(etapa, None)
    assert not alcance.alcanca(etapa, "AC")
    assert alcance.alcanca(etapa, "PPI")


def test_o_codigo_alcanca_a_modalidade_em_todos_os_perfis_que_o_tem():
    """D-001: um código, três Modalidades — as identidades saem do conteúdo."""
    conteudo = _conteudo()

    assert alcance.modalidades_alcancadas(conteudo, _etapa()) == {"C1-PPI", "C2-PPI", "C3-PPI"}
    assert alcance.alcanca_a_inscricao(conteudo, _etapa(), "C2-PPI")
    assert not alcance.alcanca_a_inscricao(conteudo, _etapa(), "C2-AC")
    assert not alcance.alcanca_a_inscricao(conteudo, _etapa(), None)


def test_o_codigo_que_so_alguns_perfis_tem_alcanca_onde_existe():
    conteudo = _conteudo()
    etapa = _etapa(modalityCodes=["PcD"])

    assert alcance.modalidades_alcancadas(conteudo, etapa) == {"C1-PcD", "C2-PcD"}
    assert alcance.perfis_sem_alcancado(conteudo, etapa) == ["C3"]


def test_a_forma_publicada_e_ordenada_e_sem_repeticao():
    """T-002: o resumo canônico não depende da ordem em que alguém marcou."""
    assert alcance.normalizar(["PcD", "PPI", "PcD"]) == ["PPI", "PcD"]
    assert alcance.normalizar(None) is None


def test_a_frase_do_documento_so_existe_na_etapa_restrita():
    """FR-6983, SC-2310: a Etapa para todas não ganha texto, e o acervo se recompõe igual."""
    conteudo = _conteudo()

    assert alcance.frase_do_alcance(conteudo, _etapa(modalityCodes=None)) == ""
    assert alcance.frase_do_alcance(conteudo, _etapa()) == (
        "Aplica-se somente aos candidatos inscritos na modalidade Pretos e pardos (PPI)."
    )
    assert alcance.frase_do_alcance(conteudo, _etapa(modalityCodes=["PcD", "PPI"])) == (
        "Aplica-se somente aos candidatos inscritos nas modalidades Pretos e pardos (PPI) e "
        "Pessoas com deficiência (PcD)."
    )


# ---------------------------------------------------------------- a gravação (FR-6962)


@pytest.mark.parametrize(
    ("valor", "trecho"),
    [
        ([], "nenhuma foi escolhida"),
        (["PPI", "PPI"], "repete a Modalidade «PPI»"),
        (["  "], "código de Modalidade inválido"),
        ("PPI", "código de Modalidade inválido"),
    ],
)
def test_a_gravacao_recusa_o_alcance_mal_formado(valor, trecho):
    with pytest.raises(StageValidationError, match=trecho) as recusa:
        validate_stage(_etapa(modalityCodes=valor), event_ids=frozenset())

    assert recusa.value.campo == "modalityCodes"


def test_a_gravacao_aceita_codigo_que_nenhum_perfil_tem():
    """FR-6963: o rascunho pode estar pela metade; quem impede é a publicação."""
    validate_stage(_etapa(modalityCodes=["XYZ"]), event_ids=frozenset())


# ---------------------------------------------------------------- a publicação (FR-6963 a 6965)


def test_a_heteroidentificacao_restrita_a_ppi_publica():
    """A contraprova: sem ela, os testes abaixo passariam por acidente."""
    assert _codigos_do_alcance(_conteudo()) == []


def test_codigo_que_nenhum_perfil_tem_impede_a_publicacao():
    assert _codigos_do_alcance(_conteudo(etapa=_etapa(modalityCodes=["XYZ"]))) == [
        "alcance_codigo_inexistente"
    ]


def test_o_codigo_da_ampla_nao_restringe_etapa():
    """FR-6968: o código que um Perfil declara como a sua ampla fica fora do alcance (D-003)."""
    assert _codigos_do_alcance(_conteudo(etapa=_etapa(modalityCodes=["AC"]))) == [
        "alcance_alcanca_a_ampla"
    ]


def test_denominacao_divergente_do_codigo_alcancado_impede():
    """FR-6965: o alcance afirma que o código significa o mesmo em todos os Perfis."""
    perfis = [_perfil("C1"), _perfil("C2", ppi_nome="Pretos, pardos e indígenas")]

    assert _codigos_do_alcance(_conteudo(perfis=perfis)) == ["alcance_denominacao_divergente"]


@pytest.mark.parametrize(
    "extra",
    [{"classificatory": True}, {"weight": "1.0000"}],
    ids=["classificatoria", "com-peso"],
)
def test_a_etapa_restrita_nao_compoe_a_ordem(extra):
    """FR-6964, D-005: a ordem compararia candidatos sob regras diferentes."""
    assert _codigos_do_alcance(_conteudo(etapa=_etapa(**extra))) == ["alcance_em_papel_de_todos"]


def _com_marco(**marco_extra):
    conteudo = _conteudo()
    marco = {
        "id": MARCO_ID,
        "code": "FINAL",
        "name": "Classificação final",
        "stages": [],
        "tiebreakers": [],
        **marco_extra,
    }
    conteudo["profiles"][0]["classificationMilestones"] = [copy.deepcopy(marco)]
    return conteudo


@pytest.mark.parametrize(
    ("marco", "trecho"),
    [
        ({"cutRule": {"governedStage": ETAPA_ID}}, "corte do marco FINAL governa"),
        (
            {
                "tiebreakers": [
                    {"type": "MAIOR_PONTUACAO_NA_ETAPA", "parameters": {"stageId": ETAPA_ID}}
                ]
            },
            "critério de desempate do marco FINAL",
        ),
        ({"drawMethod": {"qualifyingStageId": ETAPA_ID}}, "habilitação ao sorteio do marco FINAL"),
    ],
    ids=["governada-pelo-corte", "desempate", "habilitacao-ao-sorteio"],
)
def test_a_etapa_restrita_nao_decide_por_todas_as_listas(marco, trecho):
    """FR-6964, D-005: o `HABILITADA` dessas Etapas vale para todas as listas."""
    achados = [
        achado
        for achado in blocking_findings(validate_for_publication(_com_marco(**marco)))
        if achado.code == "alcance_em_papel_de_todos"
    ]

    assert len(achados) == 1
    assert trecho in achados[0].message


def test_a_restrita_pontuada_nao_e_medida_por_marco():
    """FR-6964 (refinada no plano, T-006): quem ela não alcança iria a "sem posição"."""
    conteudo = _com_marco(stages=[ETAPA_ID])
    conteudo["stages"] = [
        _etapa(forma="PONTUADA", rotuloFavoravel=None, rotuloDesfavoravel=None, eliminatory=False)
    ]
    mensagens = [
        achado.message
        for achado in blocking_findings(validate_for_publication(conteudo))
        if achado.code == "alcance_em_papel_de_todos"
    ]

    assert any("pontuada e medida pelo marco FINAL" in mensagem for mensagem in mensagens)


def test_a_decisoria_restrita_pode_ser_enumerada_por_marco():
    """A porta não pontua, e a combinação a salta: quem ela não alcança é posicionado igual."""
    conteudo = _com_marco(stages=[ETAPA_ID])

    assert "alcance_em_papel_de_todos" not in _codigos_do_alcance(conteudo)


def test_a_etapa_para_todas_ocupa_qualquer_papel():
    """Nada muda para o Edital de hoje (FR-6961)."""
    conteudo = _com_marco(cutRule={"governedStage": ETAPA_ID})
    conteudo["stages"] = [_etapa(modalityCodes=None, classificatory=True, weight="1.0000")]

    assert _codigos_do_alcance(conteudo) == []
