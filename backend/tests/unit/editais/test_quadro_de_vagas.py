"""O quadro de vagas na elaboração: identidade, unicidade, referência e soma (025).

A conferência da soma **não** mora com as demais: ela é achado da operação de publicar, porque
precisa valer igualmente sobre o conteúdo que uma Retificação produziria (FR-161, FR-177). Por isso
metade deste arquivo chama `validate_profiles` e a outra metade chama `validate_for_publication` —
são dois momentos, e a spec exige os dois.
"""

import uuid

import pytest

from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_profiles
from processo_seletivo.editais.domain.validation import (
    Severity,
    blocking_findings,
    validate_for_publication,
)

PERFIL = str(uuid.uuid4())
OUTRO_PERFIL = str(uuid.uuid4())
PCD = str(uuid.uuid4())
PPI = str(uuid.uuid4())
DE_OUTRO_PERFIL = str(uuid.uuid4())
DE_LUGAR_NENHUM = str(uuid.uuid4())


def modalidade(identidade, code, name, *, percentual=None):
    dados = {"id": identidade, "code": code, "name": name}
    if percentual is not None:
        dados["normativeRule"] = {
            "id": str(uuid.uuid4()),
            "foundation": "Lei 12.711/2012",
            "version": "2012",
            "percentage": percentual,
        }
    return dados


def linha(quantidade, modalidade_id=None, identidade=None):
    return {
        "id": identidade or str(uuid.uuid4()),
        "modalityId": modalidade_id,
        "immediateVacancies": quantidade,
    }


def perfil(**overrides):
    dados = {
        "id": PERFIL,
        "code": "C1",
        "name": "Curso",
        "immediateVacancies": 80,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [
            modalidade(PCD, "PCD", "Pessoa com deficiência"),
            modalidade(PPI, "PPI", "Preto, pardo ou indígena"),
        ],
    }
    return {**dados, **overrides}


def outro_perfil():
    return {
        "id": OUTRO_PERFIL,
        "code": "C2",
        "name": "Outro curso",
        "immediateVacancies": 10,
        "reserveType": "NONE",
        "reserveLimit": None,
        "competitionModalities": [modalidade(DE_OUTRO_PERFIL, "PPI", "Preto, pardo ou indígena")],
    }


def snapshot(*perfis):
    return {
        "title": "Edital",
        "description": "…",
        "schedule": [{"id": str(uuid.uuid4()), "type": "X", "description": "…"}],
        "profiles": list(perfis),
    }


def codigos_impeditivos(*perfis):
    """Só os achados do quadro.

    O snapshot destes casos é mínimo de propósito — o que se está verificando é a conferência do
    quadro, e não a forma publicada inteira do Perfil, que tem catálogo próprio de testes.
    """
    findings = blocking_findings(validate_for_publication(snapshot(*perfis)))
    return {item.code for item in findings if item.code.startswith("vacancy_")}


def impeditivos_do_quadro(*perfis):
    findings = blocking_findings(validate_for_publication(snapshot(*perfis)))
    return [item for item in findings if item.code.startswith("vacancy_")]


# --- T009 · a linha existe, e cada uma tem identidade própria (FR-153) -----------------------


def test_tres_linhas_declaradas_com_identidade_propria():
    geral, pcd, ppi = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    payload = perfil(
        vacancyTable=[
            linha(56, None, geral),
            linha(4, PCD, pcd),
            linha(20, PPI, ppi),
        ]
    )
    validate_profiles([payload])
    assert [item["id"] for item in payload["vacancyTable"]] == [geral, pcd, ppi]
    assert len({item["id"] for item in payload["vacancyTable"]}) == 3


# --- T010 · a ampla concorrência tem uma linha só (FR-154) -----------------------------------


def test_segunda_linha_geral_e_recusada():
    payload = perfil(vacancyTable=[linha(56), linha(20)])
    with pytest.raises(ProfileValidationError) as recusa:
        validate_profiles([payload])
    assert "uma linha só" in str(recusa.value)
    assert recusa.value.campo == "modalityId"


# --- T011 · uma linha por Modalidade, e quantidade inteira ≥ 0 (FR-155, FR-156) --------------


def test_segunda_linha_para_a_mesma_modalidade_e_recusada():
    payload = perfil(vacancyTable=[linha(4, PCD), linha(6, PCD)])
    with pytest.raises(ProfileValidationError) as recusa:
        validate_profiles([payload])
    assert "no máximo uma linha" in str(recusa.value)


@pytest.mark.parametrize("quantidade", [-1, 1.5, "4", None, True])
def test_quantidade_negativa_ou_nao_inteira_e_recusada(quantidade):
    payload = perfil(vacancyTable=[linha(quantidade, PCD)])
    with pytest.raises(ProfileValidationError) as recusa:
        validate_profiles([payload])
    assert recusa.value.campo == "immediateVacancies"


# --- T012 · as duas frases literais da referência cruzada (FR-158) ---------------------------


def test_modalidade_de_outro_perfil_diz_que_nao_pertence_ao_perfil_declarado():
    payload = perfil(vacancyTable=[linha(4, DE_OUTRO_PERFIL)])
    with pytest.raises(ProfileValidationError) as recusa:
        validate_profiles([payload, outro_perfil()])
    assert "não pertence ao Perfil declarado" in str(recusa.value)


def test_modalidade_de_perfil_nenhum_diz_que_nao_e_de_nenhum_perfil_deste_edital():
    payload = perfil(vacancyTable=[linha(4, DE_LUGAR_NENHUM)])
    with pytest.raises(ProfileValidationError) as recusa:
        validate_profiles([payload, outro_perfil()])
    assert "não é de nenhum Perfil deste Edital" in str(recusa.value)


# --- T013 · a divergência dita em três números (FR-161, UX-023, SC-054) ----------------------


def test_quadro_completo_com_soma_divergente_e_recusado_com_os_tres_numeros():
    payload = perfil(vacancyTable=[linha(55), linha(4, PCD), linha(20, PPI)])
    findings = impeditivos_do_quadro(payload)
    assert [item.code for item in findings] == ["vacancy_sum_mismatch"]
    mensagem = findings[0].message
    assert "79" in mensagem and "80" in mensagem and "diferença de 1" in mensagem


def test_quadro_completo_que_fecha_nao_produz_achado():
    payload = perfil(vacancyTable=[linha(56), linha(4, PCD), linha(20, PPI)])
    assert codigos_impeditivos(payload) == set()


# --- T014 · quadro parcial não dispara a conferência; sem quadro é submetível ----------------


def test_quadro_parcial_nao_dispara_a_conferencia_de_igualdade():
    """Somar linhas incompletas produziria acusação falsa (D-006, D-007)."""
    payload = perfil(vacancyTable=[linha(56), linha(4, PCD)])
    assert codigos_impeditivos(payload) == set()


def test_linha_geral_sozinha_e_quadro_legitimo():
    """Edital sem reserva de vaga publica só a ampla concorrência.

    Quadro **completo** sem Modalidade nenhuma: a linha geral está lá e nenhuma Modalidade ficou
    sem linha, de modo que a conferência de igualdade roda — e é ela que exige que a linha geral
    carregue o total, e não um pedaço dele.
    """
    payload = perfil(immediateVacancies=56, competitionModalities=[], vacancyTable=[linha(56)])
    assert codigos_impeditivos(payload) == set()

    divergente = perfil(immediateVacancies=80, competitionModalities=[], vacancyTable=[linha(56)])
    assert codigos_impeditivos(divergente) == {"vacancy_sum_mismatch"}


def test_so_reservadas_sem_linha_geral_e_quadro_parcial_aceito():
    payload = perfil(vacancyTable=[linha(4, PCD), linha(20, PPI)])
    assert codigos_impeditivos(payload) == set()


def test_perfil_sem_quadro_permanece_publicavel():
    """É o que **todo** Edital publicado até esta feature afirma (FR-160, D-005)."""
    payload = perfil()
    validate_profiles([payload])
    assert codigos_impeditivos(payload) == set()


# --- T015 · o limite superior não espera pela completude (FR-177) ----------------------------


def test_quadro_parcial_que_excede_o_total_e_recusado_com_os_tres_numeros():
    payload = perfil(vacancyTable=[linha(4, PCD), linha(200, PPI)])
    findings = impeditivos_do_quadro(payload)
    assert [item.code for item in findings] == ["vacancy_sum_exceeds_total"]
    mensagem = findings[0].message
    assert "204" in mensagem and "80" in mensagem and "excesso de 124" in mensagem


def test_quadro_parcial_que_soma_menos_continua_aceito():
    payload = perfil(vacancyTable=[linha(4, PCD), linha(20, PPI)])
    assert codigos_impeditivos(payload) == set()


# --- T016 · total zero, quadro completo: a soma tem de dar zero ------------------------------


def test_total_zero_com_quadro_completo_exige_soma_zero():
    payload = perfil(immediateVacancies=0, vacancyTable=[linha(0), linha(0, PCD), linha(1, PPI)])
    assert codigos_impeditivos(payload) == {"vacancy_sum_exceeds_total"}


def test_total_zero_com_quadro_completo_que_soma_zero_passa():
    payload = perfil(immediateVacancies=0, vacancyTable=[linha(0), linha(0, PCD), linha(0, PPI)])
    assert codigos_impeditivos(payload) == set()


# --- T017 · o total do Perfil não é sobrescrito pela soma (FR-162) ---------------------------


def test_o_total_do_perfil_nao_e_sobrescrito_pela_soma():
    """Calcular o total a partir das linhas apagaria o caso que o sistema precisa saber recusar."""
    payload = perfil(vacancyTable=[linha(55), linha(4, PCD), linha(20, PPI)])
    validate_for_publication(snapshot(payload))
    assert payload["immediateVacancies"] == 80


# --- FR-157 e FR-163 · o percentual adverte, e nunca calcula ---------------------------------


def test_a_divergencia_do_percentual_e_aviso_e_nunca_impeditivo():
    payload = perfil(
        competitionModalities=[
            modalidade(PCD, "PCD", "Pessoa com deficiência", percentual="5"),
            modalidade(PPI, "PPI", "Preto, pardo ou indígena", percentual="20"),
        ],
        vacancyTable=[linha(56), linha(4, PCD), linha(20, PPI)],
    )
    findings = validate_for_publication(snapshot(payload))
    avisos = [item for item in findings if item.code == "vacancy_row_percentage_divergence"]
    assert [item.severity for item in avisos] == [Severity.WARNING]
    assert "PPI" in avisos[0].message
    # A PcD declara 4 sobre 5% de 80, que é exatamente 4: quantidade que fecha não adverte.
    assert all("PCD" not in item.message for item in avisos)
    assert [item for item in blocking_findings(findings) if item.code.startswith("vacancy_")] == []


def test_a_advertencia_nunca_altera_a_quantidade_declarada():
    """FR-157: o percentual fundamenta e não calcula.

    `Q 1` e `PCD 1` de um Edital real saem de arredondamento sobre censo, e não de conta alguma.
    """
    payload = perfil(
        competitionModalities=[
            modalidade(PCD, "PCD", "Pessoa com deficiência", percentual="5"),
            modalidade(PPI, "PPI", "Preto, pardo ou indígena", percentual="20"),
        ],
        vacancyTable=[linha(56), linha(4, PCD), linha(20, PPI)],
    )
    validate_for_publication(snapshot(payload))
    assert [item["immediateVacancies"] for item in payload["vacancyTable"]] == [56, 4, 20]


def test_arredondamento_do_percentual_em_qualquer_direcao_nao_adverte():
    payload = perfil(
        immediateVacancies=36,
        competitionModalities=[modalidade(PPI, "PPI", "Preto, pardo ou indígena", percentual="18")],
        vacancyTable=[linha(6, PPI)],
    )
    findings = validate_for_publication(snapshot(payload))
    assert [item for item in findings if item.code == "vacancy_row_percentage_divergence"] == []
