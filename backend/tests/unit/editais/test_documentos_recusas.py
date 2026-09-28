"""As recusas do recorte transversal na gravação do rascunho (044, FR-702 a FR-704, D-010).

A gravação confere os documentos contra os Perfis **da própria gravação**, em qualquer etapa. Por
isso as mensagens nomeiam o documento: quem está na etapa Perfis, renomeando ou declarando a
ampla, não está olhando para a lista de documentos.
"""

import pytest

from processo_seletivo.editais.domain.documentos import (
    DocumentRequirementValidationError,
    validate_document_requirements,
)

C1 = {
    "id": "c1",
    "code": "C1",
    "competitionModalities": [
        {"id": "c1-ac", "code": "AC", "name": "Ampla concorrência"},
        {"id": "c1-pcd", "code": "PcD", "name": "Pessoas com Deficiência"},
    ],
    "generalCompetitionModalityId": "c1-ac",
}
C2 = {
    "id": "c2",
    "code": "C2",
    "competitionModalities": [
        {"id": "c2-ac", "code": "AC", "name": "Ampla concorrência"},
        {"id": "c2-pcd", "code": "PcD", "name": "Pessoas com Deficiência"},
    ],
    "generalCompetitionModalityId": "c2-ac",
}


def _laudo(**campos):
    return {"id": "d1", "key": "laudo", "name": "Laudo médico", "order": 1, **campos}


def test_o_recorte_transversal_coerente_grava():
    validate_document_requirements([_laudo(modalityCode="PcD")], profiles=[C1, C2])


@pytest.mark.parametrize(
    "campos",
    [{"profileId": "c1"}, {"modalityId": "c1-pcd"}, {"profileId": "c1", "modalityId": "c1-pcd"}],
)
def test_codigo_junto_de_perfil_ou_modalidade_exata_e_recusado(campos):
    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements([_laudo(modalityCode="PcD", **campos)], profiles=[C1, C2])

    assert recusa.value.campo == "modalityCode"
    assert "'Laudo médico'" in str(recusa.value)


def test_codigo_que_nenhum_perfil_tem_e_recusado():
    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements([_laudo(modalityCode="PTT")], profiles=[C1, C2])

    assert recusa.value.campo == "modalityCode"
    assert "nenhum Perfil" in str(recusa.value)


def test_codigo_da_ampla_e_recusado():
    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements([_laudo(modalityCode="AC")], profiles=[C1, C2])

    assert recusa.value.campo == "modalityCode"
    assert "ampla concorrência" in str(recusa.value)


def test_remover_o_codigo_de_todos_os_perfis_e_recusado_nomeando_o_documento():
    """É o que a etapa Perfis faz quando tira a última PcD: a mensagem diz qual documento sobra."""
    sem_pcd = [
        {**perfil, "competitionModalities": perfil["competitionModalities"][:1]}
        for perfil in (C1, C2)
    ]

    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements([_laudo(modalityCode="PcD")], profiles=sem_pcd)

    assert "'Laudo médico'" in str(recusa.value)


def test_remover_o_codigo_de_alguns_perfis_grava():
    so_c1 = [C1, {**C2, "competitionModalities": C2["competitionModalities"][:1]}]

    validate_document_requirements([_laudo(modalityCode="PcD")], profiles=so_c1)


def test_declarar_ampla_a_modalidade_do_codigo_na_etapa_perfis_e_recusado():
    c2_com_pcd_ampla = {**C2, "generalCompetitionModalityId": "c2-pcd"}

    with pytest.raises(DocumentRequirementValidationError) as recusa:
        validate_document_requirements(
            [_laudo(modalityCode="PcD")], profiles=[C1, c2_com_pcd_ampla]
        )

    assert "Perfil 'C2'" in str(recusa.value)
