"""O fecho do ato, do banco ao papel (054, FR-989 a FR-994; SC-364, SC-365).

O compositor está provado em `tests/unit/publicacoes/test_fecho_e_normas_da_054.py`. Aqui o que se
prova é o caminho: a data sai do `now` da Publicação, no fuso institucional; o ato de nomeação é
registrado na Publicação e chega ao documento; e a consulta pública o devolve.
"""

import pytest

from processo_seletivo.publicacoes.domain.autoridades import quem_assinou
from processo_seletivo.publicacoes.infrastructure.humano import data_por_extenso
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.publicacao import SIGNATORY, publish_original
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ASSINANTE = {
    **SIGNATORY,
    "name": "Maria Exemplo",
    "role": "Diretora-Geral do Cefor",
    "appointment": "Portaria nº 1, de 2 de janeiro de 2026",
}


def _publicacao(api_client, manager_headers, process_payload, signatory=None):
    edital = publish_original(api_client, manager_headers, process_payload, signatory=signatory)
    return Publicacao.objects.get(edital=edital)


def test_o_documento_publicado_traz_a_data_da_publicacao_no_fuso_institucional(
    api_client, manager_headers, process_payload
):
    publicacao = _publicacao(api_client, manager_headers, process_payload)
    texto = texto_de(bytes(publicacao.documento.bytes))

    dia = data_por_extenso(publicacao.published_at.astimezone(ZONA).date())
    assert f"Vitória (ES), {dia}." in texto


def test_o_ato_de_nomeacao_e_registrado_na_publicacao_e_impresso(
    api_client, manager_headers, process_payload
):
    publicacao = _publicacao(api_client, manager_headers, process_payload, ASSINANTE)

    assert publicacao.signatory_appointment == ASSINANTE["appointment"]
    texto = texto_de(bytes(publicacao.documento.bytes))
    assert texto.index("Maria Exemplo") < texto.index("Diretora-Geral do Cefor")
    assert texto.index("Diretora-Geral do Cefor") < texto.index(ASSINANTE["appointment"])

    corpo = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}").json()
    assert corpo["signatory"]["appointment"] == ASSINANTE["appointment"]


def test_sem_ato_de_nomeacao_a_publicacao_o_registra_vazio(
    api_client, manager_headers, process_payload
):
    publicacao = _publicacao(api_client, manager_headers, process_payload)
    assert publicacao.signatory_appointment == ""
    corpo = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}").json()
    assert corpo["signatory"]["appointment"] == ""


def test_quem_assinou_nas_telas_nao_deixa_separador_pendurado():
    """FR-994: a Publicação feita pela interface com o catálogo sem nome registra o nome vazio."""
    assert quem_assinou("", "Diretora-Geral do Cefor") == "Diretora-Geral do Cefor"
