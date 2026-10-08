"""O fecho do ato, do banco ao papel (054, FR-989 a FR-994; SC-364, SC-365).

O compositor está provado em `tests/unit/publicacoes/test_fecho_e_normas_da_054.py`. Aqui o que se
prova é o caminho: a data sai do `now` da Publicação, no fuso institucional; o ato de nomeação é
registrado na Publicação e chega ao documento; e a consulta pública o devolve.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure.humano import data_por_extenso
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.domain.rotulos import quem_assinou
from tests.fixtures.autoridades import registrar_autoridade
from tests.fixtures.publicacao import publish_original
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Desde a 060 o ato de nomeação vem do registro de autoridades, e não de quem publica: a autoridade
# com nome e portaria é cadastrada no Cefor, e a publicação a escolhe pelo identificador.
ASSINANTE = {
    "nome": "Maria Exemplo",
    "cargo": "Diretora-Geral do Cefor",
    "ato_de_nomeacao": "Portaria nº 1, de 2 de janeiro de 2026",
}


def _so_com_o_cargo():
    from processo_seletivo.unidades.models import Unidade

    autoridade = registrar_autoridade(Unidade.objects.get(codigo="cefor"), cargo="Diretora-Geral")
    return {"authorityId": str(autoridade.pk)}


def _com_nome_e_portaria():
    from processo_seletivo.unidades.models import Unidade

    autoridade = registrar_autoridade(Unidade.objects.get(codigo="cefor"), **ASSINANTE)
    return {"authorityId": str(autoridade.pk)}


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
    publicacao = _publicacao(api_client, manager_headers, process_payload, _com_nome_e_portaria())

    assert publicacao.signatory_appointment == ASSINANTE["ato_de_nomeacao"]
    texto = texto_de(bytes(publicacao.documento.bytes))
    assert texto.index("Maria Exemplo") < texto.index("Diretora-Geral do Cefor")
    assert texto.index("Diretora-Geral do Cefor") < texto.index(ASSINANTE["ato_de_nomeacao"])

    corpo = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}").json()
    assert corpo["signatory"]["appointment"] == ASSINANTE["ato_de_nomeacao"]


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


def test_a_autoridade_sem_nome_publica_so_com_o_cargo(api_client, manager_headers, process_payload):
    """FR-992: o registro admite autoridade só com o cargo, e o fecho a imprime assim.

    Até a 060 o caso passava pela API, que aceitava nome vazio; desde ela o nome vem do registro, e
    é o registro que o admite vazio enquanto o Cefor não o fornece.
    """
    publicacao = _publicacao(
        api_client,
        manager_headers,
        process_payload,
        _so_com_o_cargo(),
    )
    assert publicacao.signatory_name == ""
    linhas = texto_de(bytes(publicacao.documento.bytes)).splitlines()
    assert linhas[linhas.index("Autoridade responsável pelo ato") + 1] == "Diretora-Geral"
