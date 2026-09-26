"""O que a publicação recusa no contrato de inscrição, e o que ela apenas avisa (US2 da 009).

A elaboração já recusa o incoerente, e o banco garante um período por Cronograma. Nenhuma das
duas alcança o conteúdo que **passa a vigorar**: duas Retificações sucessivas produzem o estado
que a interface impede, cada uma partindo de uma versão em que ele não existia. A publicação é
onde esse estado para.
"""

import pytest

from processo_seletivo.editais.domain.validation import Severity, validate_for_publication
from tests.fixtures.snapshot import DOCUMENTO, MODALIDADE, rascunho_completo

# Fora do conjunto de Perfis do construtor — que tem três, e todos os três são deste Edital.
PERFIL_DE_OUTRO_EDITAL = "00000000-0000-0000-0000-0000000009fe"


def _conteudo(**ajustes):
    base = rascunho_completo()
    base.update({"title": "Edital", "description": "Descrição"})
    base.update(ajustes)
    return base


def _codigos(conteudo, severidade):
    return [
        achado.code
        for achado in validate_for_publication(conteudo)
        if achado.severity == severidade
    ]


def test_dois_eventos_designados_produzem_achado_impeditivo():
    conteudo = _conteudo()
    for evento in conteudo["schedule"][:2]:
        evento["isRegistrationPeriod"] = True

    assert "registration_period_ambiguous" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_um_evento_designado_nao_produz_achado():
    conteudo = _conteudo()
    conteudo["schedule"][0]["isRegistrationPeriod"] = True

    achados = validate_for_publication(conteudo)

    assert [a.code for a in achados if a.code.startswith("registration_period")] == []


def test_nenhum_evento_designado_e_aviso_e_nao_impedimento():
    """FR-004: nem todo Edital abre inscrição por este sistema, e isso não impede publicar."""
    conteudo = _conteudo()

    assert "registration_period_missing" in _codigos(conteudo, Severity.WARNING)
    assert "registration_period_missing" not in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_documento_restrito_a_perfil_inexistente_e_impeditivo():
    conteudo = _conteudo()
    conteudo["documentRequirements"][1]["profileId"] = PERFIL_DE_OUTRO_EDITAL

    assert "document_requirement_profile_unknown" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_documento_restrito_a_modalidade_fora_do_alcance_e_impeditivo():
    conteudo = _conteudo()
    conteudo["documentRequirements"][0]["modalityId"] = "00000000-0000-0000-0000-0000000009ff"

    assert "document_requirement_modality_unknown" in _codigos(conteudo, Severity.BLOCKING_ERROR)


def test_modalidade_do_perfil_declarado_passa():
    conteudo = _conteudo()
    conteudo["documentRequirements"][1]["modalityId"] = MODALIDADE["A"]

    assert [
        codigo
        for codigo in _codigos(conteudo, Severity.BLOCKING_ERROR)
        if codigo.startswith("document_requirement")
    ] == []


# A PPI de um segundo Perfil: outra identidade, mesmo nome. É o par que a conferência do portal
# encontrou — o PcD do C1 e o PcD do C2 são objetos distintos com o mesmo rótulo publicado.
PPI_DO_PERFIL_B = "00000000-0000-0000-0000-0000000009fd"
REGRA_DA_PPI_DO_PERFIL_B = "00000000-0000-0000-0000-0000000009fc"


def _com_a_ppi_tambem_no_perfil_b(conteudo):
    principal, segundo = conteudo["profiles"][0], conteudo["profiles"][1]
    ppi = next(m for m in principal["competitionModalities"] if m["id"] == MODALIDADE["B"])
    copia = {**ppi, "id": PPI_DO_PERFIL_B}
    copia["normativeRule"] = {**ppi["normativeRule"], "id": REGRA_DA_PPI_DO_PERFIL_B}
    segundo["competitionModalities"] = [*(segundo.get("competitionModalities") or []), copia]
    return conteudo


def _achados_de_recorte(conteudo):
    return [
        achado
        for achado in validate_for_publication(conteudo)
        if achado.code == "document_requirement_modality_scope_ambiguous"
    ]


def test_todos_os_perfis_com_a_modalidade_de_um_so_e_impeditivo_quando_o_nome_se_repete():
    """O Edital publicado diria "todos da PPI"; a inscrição pediria só aos do Perfil A."""
    conteudo = _com_a_ppi_tambem_no_perfil_b(_conteudo())
    conteudo["documentRequirements"][0]["modalityId"] = MODALIDADE["B"]

    achados = _achados_de_recorte(conteudo)

    assert [a.severity for a in achados] == [Severity.BLOCKING_ERROR]
    assert achados[0].path == "/documentRequirements/0"
    assert "Perfil 'P1'" in achados[0].message
    assert "'Modalidade PPI'" in achados[0].message


def test_o_mesmo_recorte_com_o_perfil_declarado_passa():
    """Declarado o Perfil, o documento publicado nomeia o Perfil — e diz o que o portal faz."""
    conteudo = _com_a_ppi_tambem_no_perfil_b(_conteudo())
    conteudo["documentRequirements"][0]["modalityId"] = MODALIDADE["B"]
    conteudo["documentRequirements"][0]["profileId"] = conteudo["profiles"][0]["id"]

    assert _achados_de_recorte(conteudo) == []


def test_modalidade_que_so_um_perfil_tem_nao_e_acusada():
    """Sem outra modalidade de mesmo nome, "todos da PPI" são exatamente os do Perfil A."""
    conteudo = _conteudo()
    conteudo["documentRequirements"][0]["modalityId"] = MODALIDADE["B"]

    assert _achados_de_recorte(conteudo) == []


@pytest.mark.parametrize("valor", ["texto", {"a": 1}, None])
def test_colecao_malformada_nao_faz_a_coerencia_explodir(valor):
    """Forma é assunto da declaração, que já reporta. A coerência ignora, e não levanta exceção."""
    conteudo = _conteudo(documentRequirements=valor)

    achados = validate_for_publication(conteudo)

    assert all(a.code != "document_requirement_profile_unknown" for a in achados)


def test_a_identidade_do_documento_e_a_declarada():
    conteudo = _conteudo()

    identidades = [documento["id"] for documento in conteudo["documentRequirements"]]

    assert identidades == [DOCUMENTO["A"], DOCUMENTO["B"]]


# ---------------------------------------------------------------------------
# 044 — o recorte transversal na publicação
# ---------------------------------------------------------------------------

PCD = {
    "A": "00000000-0000-0000-0000-0000000044a1",
    "B": "00000000-0000-0000-0000-0000000044b1",
}


def _com_pcd(conteudo, denominacoes=("Pessoas com Deficiência", "Pessoas com Deficiência")):
    """Uma Modalidade de código `PcD` nos Perfis A e B, cada uma com a sua identidade."""
    for perfil, identidade, denominacao in zip(
        conteudo["profiles"][:2], (PCD["A"], PCD["B"]), denominacoes, strict=True
    ):
        base = perfil["competitionModalities"][0] if perfil.get("competitionModalities") else None
        regra = dict(base["normativeRule"]) if base else {"id": None}
        regra["id"] = f"{identidade[:-2]}ff"
        regra["percentage"] = "5"
        perfil["competitionModalities"] = [
            *(perfil.get("competitionModalities") or []),
            {
                **(base or {}),
                "id": identidade,
                "code": "PcD",
                "name": denominacao,
                "description": "",
                "normativeRule": regra,
            },
        ]
    return conteudo


def _transversal(conteudo, codigo="PcD", indice=0):
    documento = conteudo["documentRequirements"][indice]
    documento.pop("profileId", None)
    documento.pop("modalityId", None)
    documento["modalityCode"] = codigo
    return conteudo


def _achados(conteudo, codigo):
    return [achado for achado in validate_for_publication(conteudo) if achado.code == codigo]


def test_o_recorte_transversal_coerente_passa():
    conteudo = _transversal(_com_pcd(_conteudo()))

    assert [
        codigo
        for codigo in _codigos(conteudo, Severity.BLOCKING_ERROR)
        if codigo.startswith(("document_requirement", "modality_code"))
    ] == []


@pytest.mark.parametrize("campo", ["profileId", "modalityId"])
def test_codigo_com_perfil_ou_modalidade_exata_e_impeditivo(campo):
    conteudo = _transversal(_com_pcd(_conteudo()))
    valor = conteudo["profiles"][0]["id"] if campo == "profileId" else PCD["A"]
    conteudo["documentRequirements"][0][campo] = valor

    assert len(_achados(conteudo, "document_requirement_scope_conflict")) == 1


def test_codigo_que_nenhum_perfil_tem_e_impeditivo():
    conteudo = _transversal(_com_pcd(_conteudo()), codigo="PTT")

    achados = _achados(conteudo, "document_requirement_modality_code_unknown")

    assert [a.severity for a in achados] == [Severity.BLOCKING_ERROR]
    assert "'PTT'" in achados[0].message


def test_codigo_da_ampla_em_um_perfil_so_e_impeditivo():
    """Basta um Perfil declarar ampla a Modalidade do código (D1a, FR-704)."""
    conteudo = _transversal(_com_pcd(_conteudo()))
    conteudo["profiles"][1]["generalCompetitionModalityId"] = PCD["B"]

    achados = _achados(conteudo, "document_requirement_modality_code_general")

    assert len(achados) == 1
    assert "ampla concorrência" in achados[0].message


def test_denominacoes_diferentes_para_o_codigo_referido_dao_um_achado_so():
    conteudo = _transversal(
        _com_pcd(_conteudo(), denominacoes=("Pessoas com Deficiência", "Pessoa com Deficiência"))
    )

    achados = _achados(conteudo, "modality_code_name_divergent")

    assert [a.severity for a in achados] == [Severity.BLOCKING_ERROR]
    assert achados[0].path == "/profiles"
    assert "'Pessoas com Deficiência' em P1" in achados[0].message
    assert "'Pessoa com Deficiência' em P2" in achados[0].message


def test_dois_documentos_do_mesmo_codigo_nao_duplicam_o_achado():
    conteudo = _com_pcd(_conteudo(), denominacoes=("Pessoas com Deficiência", "PcD"))
    _transversal(conteudo, indice=0)
    _transversal(conteudo, indice=1)

    assert len(_achados(conteudo, "modality_code_name_divergent")) == 1


def test_codigo_repetido_sem_documento_transversal_nao_e_acusado():
    """Um Edital que não usa o recorte transversal não afirma identidade nenhuma (D-001)."""
    conteudo = _com_pcd(_conteudo(), denominacoes=("Pessoas com Deficiência", "PcD"))

    assert _achados(conteudo, "modality_code_name_divergent") == []


@pytest.mark.parametrize(
    ("denominacoes", "acusa", "porque"),
    [
        (("Pessoas com Deficiência", "pessoas com deficiência"), True, "maiúscula conta (D-005)"),
        (("Pessoas com Deficiência", "  Pessoas com Deficiência "), False, "pontas não contam"),
    ],
)
def test_a_denominacao_se_compara_como_esta_escrita(denominacoes, acusa, porque):
    conteudo = _transversal(_com_pcd(_conteudo(), denominacoes=denominacoes))

    assert bool(_achados(conteudo, "modality_code_name_divergent")) is acusa, porque


def test_percentual_diferente_nao_e_acusado():
    """A cota é por Perfil: a coerência cobre a identidade, nunca o percentual (FR-707)."""
    conteudo = _transversal(_com_pcd(_conteudo()))
    modalidade_b = conteudo["profiles"][1]["competitionModalities"][-1]
    modalidade_b["normativeRule"]["percentage"] = "10"
    modalidade_b["normativeRule"]["foundation"] = "Outro fundamento"

    assert _achados(conteudo, "modality_code_name_divergent") == []


def test_a_mensagem_da_161_oferece_as_tres_saidas():
    conteudo = _com_a_ppi_tambem_no_perfil_b(_conteudo())
    conteudo["documentRequirements"][0]["modalityId"] = MODALIDADE["B"]

    mensagem = _achados_de_recorte(conteudo)[0].message

    assert "Declare o Perfil 'P1'" in mensagem
    assert "em todos os Perfis" in mensagem
    assert "repita-o com a modalidade de cada um" in mensagem
