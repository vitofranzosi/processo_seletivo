"""O papel do recorte e a origem do registro excedente (122, FR-3894, FR-3911, FR-3903).

São funções puras sobre o conteúdo publicado: a pergunta "este recorte é da operação?" é feita à
versão, e não a uma marca gravada (D-002). Por isso cabem em teste de unidade, sem banco.
"""

import pytest

from processo_seletivo.editais.domain.recortes import (
    AUSENTE,
    CODIGO_DA_RECUSA,
    EXCEDENTE,
    NASCIDO,
    OPERACIONAL,
    TORNADO,
    exigir_recorte_operacional,
    frase_da_origem,
    origem_do_registro,
    papel_do_recorte,
    retificacao_que_mudou_o_papel,
)
from processo_seletivo.shared.api.problems import DomainError

PERFIL = "00000000-0000-4000-8000-000000000a01"
AC = "00000000-0000-4000-8000-000000000a02"
PPI = "00000000-0000-4000-8000-000000000a03"
OUTRA = "00000000-0000-4000-8000-000000000a04"


def conteudo(*, apontada=None):
    perfil = {
        "id": PERFIL,
        "competitionModalities": [
            {"id": AC, "code": "AC", "name": "Ampla Concorrência"},
            {"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"},
        ],
    }
    if apontada is not None:
        perfil["generalCompetitionModalityId"] = apontada
    return {"profiles": [perfil]}


def papel(lista_id, **kwargs):
    return papel_do_recorte(conteudo(**kwargs), perfil_id=PERFIL, lista_id=lista_id)


# --- FR-3894 · o papel sai do apontamento ------------------------------------------------------


def test_a_ampla_e_sempre_operacional():
    assert papel(None, apontada=AC) == OPERACIONAL


def test_a_modalidade_apontada_e_excedente():
    assert papel(AC, apontada=AC) == EXCEDENTE


def test_a_reserva_continua_operacional_com_o_apontamento():
    assert papel(PPI, apontada=AC) == OPERACIONAL


def test_a_modalidade_chamada_ampla_sem_apontamento_e_operacional():
    """`FR-3894`: o nome "Ampla Concorrência" e o código "AC" não decidem nada."""
    assert papel(AC) == OPERACIONAL


def test_identidade_fora_do_perfil_e_ausente():
    assert papel(OUTRA, apontada=AC) == AUSENTE


# --- FR-3897 a FR-3899 · a recusa única ----------------------------------------------------------


def test_a_recusa_nomeia_a_modalidade_e_manda_para_a_ampla():
    with pytest.raises(DomainError) as erro:
        exigir_recorte_operacional(conteudo(apontada=AC), perfil_id=PERFIL, lista_id=AC)

    assert erro.value.code == CODIGO_DA_RECUSA
    assert erro.value.status == 422
    assert "«Ampla Concorrência (AC)»" in erro.value.detail
    assert "Use o recorte da ampla concorrência" in erro.value.detail


@pytest.mark.parametrize(
    "lista_id, apontada",
    [(None, AC), (PPI, AC), (AC, None), (OUTRA, AC)],
    ids=["ampla", "reserva", "sem-apontamento", "ausente"],
)
def test_so_o_excedente_e_recusado(lista_id, apontada):
    exigir_recorte_operacional(conteudo(apontada=apontada), perfil_id=PERFIL, lista_id=lista_id)


# --- FR-3903 e FR-3911 · a origem é a da versão do registro ---------------------------------------


def versoes(*apontamentos):
    return [(f"v{i}", conteudo(apontada=a), i) for i, a in enumerate(apontamentos, start=1)]


def test_registro_feito_sob_o_apontamento_nasceu_excedente():
    assert origem_do_registro(
        versoes(AC, AC), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
    ) == (NASCIDO, None)


def test_registro_operacional_que_uma_retificacao_apontou_se_tornou_excedente():
    assert origem_do_registro(
        versoes(None, AC), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
    ) == (TORNADO, 2)


def test_o_tornado_nomeia_a_primeira_retificacao_e_nao_a_ultima():
    """T5 da `research.md`: apontar, retirar e apontar de novo não reescreve a origem."""
    assert origem_do_registro(
        versoes(None, AC, None, AC), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
    ) == (TORNADO, 2)


def test_uma_retificacao_alheia_ao_apontamento_nao_muda_a_origem():
    """T4: o nascido continua nascido, qualquer que seja a vigente."""
    assert origem_do_registro(
        versoes(AC, AC, AC), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
    ) == (NASCIDO, None)


def test_as_duas_frases_dizem_a_origem():
    assert "dava lista própria" in frase_da_origem(NASCIDO)
    tornado = frase_da_origem(TORNADO, 3)
    assert "A Retificação nº 3 passou a apontá-la como a ampla concorrência" in tornado
    assert "tinha recorte próprio" in tornado


def test_a_retificacao_que_mudou_o_papel_e_a_primeira_diferente():
    """FR-3912: o ato nascido excedente que volta à operação aponta a Retificação que o devolveu."""
    assert (
        retificacao_que_mudou_o_papel(
            versoes(AC, AC, None), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
        )
        == 3
    )
    assert (
        retificacao_que_mudou_o_papel(
            versoes(AC, AC), perfil_id=PERFIL, lista_id=AC, versao_do_registro="v1"
        )
        is None
    )
