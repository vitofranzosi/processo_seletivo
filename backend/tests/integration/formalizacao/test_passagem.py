"""A passagem ao setor, em contagens (153, FR-6100 a FR-6107, FR-6130, SC-1951).

O que se prova: cada pessoa apta numa situação só, na ordem da FR-6106; a definição gravada sem
documento como decisão (D-003); a designação efetiva só com o papel vigente e a pessoa ativa
(FR-6107); a pessoa incluída num pacote como disponibilizada (P-2); e o Edital sem pessoa apta sem
passagem nenhuma (FR-6130).
"""

import pytest

from processo_seletivo.formalizacao.application import passagem as pa
from processo_seletivo.formalizacao.domain import nomes
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    montar_cenario_da_formalizacao,
    servido,
)
from tests.integration.formalizacao.apoio import exportar_pessoa
from tests.interface.conftest import identificar
from tests.seguranca.apoio import pessoa, vincular

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

OUTRO_PERFIL = "00000000-0000-0000-0000-00000000abcd"


@pytest.fixture
def com_papel(db):
    rui = pessoa("rui", nome="Rui Registro", email="rui@ifes.edu.br")
    vincular(rui, "cefor", nomes.PAPEL)
    return rui


def _soma(passagem):
    return passagem.disponibilizadas + passagem.sem_documento + passagem.total_pendentes


def test_sem_pessoa_apta_nao_ha_passagem(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """FR-6130: a indeferida e a sem resposta não dão aptidão, e a definição vazia não pesa."""
    cenario = montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=0, indeferidas=1, sem_resposta=1
    )
    assert pa.da_passagem(cenario.edital) is None


def test_sem_definicao_todas_as_aptas_esperam_a_definicao(cenario, com_papel):
    """FR-6106: a primeira causa prende, ainda que haja designação efetiva."""
    designar_direto(cenario.edital, com_papel.username)
    passagem = pa.da_passagem(cenario.edital)
    assert passagem.aptas == 5
    assert passagem.causas == ((pa.SEM_DEFINICAO, 5),)
    assert not passagem.definida
    assert passagem.designadas == 1
    assert _soma(passagem) == passagem.aptas


def test_definida_e_sem_designacao_esperam_quem_receba(cenario, gestor, com_papel):
    definir_documentos(cenario.edital, gestor)
    passagem = pa.da_passagem(cenario.edital)
    assert passagem.causas == ((pa.SEM_QUEM_RECEBA, 5),)
    assert passagem.designadas == 0
    assert passagem.com_o_papel == 1


def test_designacao_de_quem_nao_tem_o_papel_nao_conta(cenario, gestor):
    """FR-6107: vigente, mas sem o papel na unidade, não é efetiva."""
    definir_documentos(cenario.edital, gestor)
    sem_papel = pessoa("carla", nome="Carla", email="carla@ifes.edu.br")
    designar_direto(cenario.edital, sem_papel.username)
    passagem = pa.da_passagem(cenario.edital)
    assert passagem.causas == ((pa.SEM_QUEM_RECEBA, 5),)
    assert passagem.designadas == 0
    assert passagem.com_o_papel == 0


def test_designacao_de_pessoa_suspensa_nao_conta(cenario, gestor, com_papel):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    com_papel.is_active = False
    com_papel.save(update_fields=["is_active"])
    assert pa.da_passagem(cenario.edital).causas == ((pa.SEM_QUEM_RECEBA, 5),)


def test_designacao_de_outro_perfil_nao_cobre(cenario, gestor, com_papel):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username, perfis=[OUTRO_PERFIL])
    assert pa.da_passagem(cenario.edital).causas == ((pa.SEM_QUEM_RECEBA, 5),)


def test_designacao_do_perfil_cobre(cenario, gestor, com_papel):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username, perfis=[PROFILE_ID])
    passagem = pa.da_passagem(cenario.edital)
    assert passagem.causas == ((pa.A_EXPORTAR, 5),)
    assert not passagem.completa


def test_definicao_sem_documento_e_decisao(cenario, gestor):
    """D-003: gravada vazia, com motivo, ninguém fica pendente — nem por falta de designação."""
    definir_documentos(cenario.edital, gestor, requisitos=[], motivo="O setor não pede documento")
    passagem = pa.da_passagem(cenario.edital)
    assert passagem.definida
    assert passagem.definicao_vazia
    assert passagem.sem_documento == 5
    assert passagem.causas == ()
    assert passagem.completa


def test_a_pessoa_incluida_num_pacote_esta_disponibilizada(
    cenario, gestor, com_papel, client, seletor
):
    """P-2: incluída em algum pacote do Edital. A contagem cai na leitura seguinte."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    identificar(client, com_papel.username, ["formalizacao"])
    for inscricao in cenario.inscricoes_aptas[:2]:
        assert servido(exportar_pessoa(client, cenario.edital, inscricao))

    passagem = pa.da_passagem(cenario.edital)
    assert passagem.disponibilizadas == 2
    assert passagem.causas == ((pa.A_EXPORTAR, 3),)
    assert passagem.ultimo_pacote_em is not None
    assert _soma(passagem) == passagem.aptas


def test_definicao_nova_nao_reabre_quem_ja_foi_disponibilizado(
    cenario, gestor, com_papel, client, seletor
):
    """P-2: qualquer versão da definição. A versão nova vale para as exportações seguintes."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    identificar(client, com_papel.username, ["formalizacao"])
    assert servido(exportar_pessoa(client, cenario.edital, cenario.inscricoes_aptas[0]))
    definir_documentos(cenario.edital, gestor, motivo="Portaria 2/2026, com o histórico")

    assert pa.da_passagem(cenario.edital).disponibilizadas == 1


def test_o_edital_cancelado_nao_tem_passagem(cenario):
    """FR-6100."""
    cenario.edital.status = "CANCELADO"
    assert pa.da_passagem(cenario.edital) is None
