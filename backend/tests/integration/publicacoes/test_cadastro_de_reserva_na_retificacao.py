"""A Retificação que mexe nas vagas de um Perfil de cadastro de reserva (096, FR-2411 a FR-2413).

Pelo caminho da publicação, e não compondo o PDF à mão: o consolidado é um documento novo, composto
pela regra vigente quando é composto (o princípio da FR-1196 da `064`), e é ele que passa a dizer
`CR` ou o número. A tela de homologação continua dizendo o antes e o depois com os números, porque
registra o campo como ele mudou (D-003); e o documento já publicado não muda.
"""

import pytest

from processo_seletivo.interface.views import _alteracoes_legiveis
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import PERFIL, rascunho_completo
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _rascunho():
    """P2 só de cadastro de reserva, P3 com vaga e cadastro, P1 como vem."""
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        if perfil["id"] == PERFIL["B"]:
            perfil.update(immediateVacancies=0, reserveType="LIMITED", reserveLimit=10)
        elif perfil["id"] == PERFIL["C"]:
            perfil.update(reserveType="LIMITED", reserveLimit=10)
    return rascunho


def _documento(edital, ordem):
    publicacao = Publicacao.objects.get(edital=edital, publication_order=ordem)
    return bytes(publicacao.documento.bytes)


def _linhas(documento):
    return [linha.strip() for linha in texto_de(documento).splitlines() if linha.strip()]


def _vagas_de(linhas, codigo):
    """A célula de vagas imediatas da linha do Perfil, onde quer que a tabela de Perfis o liste."""
    indice = linhas.index(codigo)
    return next(
        linha for linha in linhas[indice + 1 : indice + 6] if linha in ("CR", "0", "1", "2")
    )


def _linha_geral(edital, perfil):
    """A linha da ampla concorrência que a publicação derivou do total (027), já vigente."""
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    (alvo,) = [p for p in vigente["profiles"] if p["id"] == PERFIL[perfil]]
    (geral,) = [linha for linha in alvo["vacancyTable"] if not linha.get("modalityId")]
    return geral["id"]


def _retificar_vagas(api_client, edital, perfil, valor, suffix):
    """Retifica as vagas imediatas de um Perfil; devolve o antes e o depois da homologação.

    O total e a linha geral mudam no mesmo ato: sem lista reservada, os dois são o mesmo número, e
    a validação recusa um sem o outro (027).
    """
    base = f"/profiles/id={PERFIL[perfil]}"
    retificacao = create_retification(
        api_client,
        edital,
        [
            {"targetPath": f"{base}/immediateVacancies", "operation": "REPLACE", "newValue": valor},
            {
                "targetPath": f"{base}/vacancyTable/id={_linha_geral(edital, perfil)}"
                "/immediateVacancies",
                "operation": "REPLACE",
                "newValue": valor,
            },
        ],
        suffix=suffix,
    )
    legiveis = _alteracoes_legiveis(retificacao)
    publish_retification(api_client, retificacao, suffix=suffix)
    return legiveis


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload, draft=_rascunho())
    linhas = _linhas(_documento(edital, 1))
    assert _vagas_de(linhas, "P2") == "CR", "o original já sai com a regra da 096"
    assert pdf.NOTA_DO_CADASTRO in linhas
    return edital


def test_a_retificacao_que_da_vagas_ao_cr_imprime_o_numero_e_tira_a_nota(api_client, edital):
    """FR-2411: de 0 para 2, o consolidado diz 2, e sem outro `CR` a nota sai."""
    legiveis = _retificar_vagas(api_client, edital, "B", 2, "cr-para-2")

    linhas = _linhas(_documento(edital, 2))
    assert _vagas_de(linhas, "P2") == "2"
    assert pdf.NOTA_DO_CADASTRO not in linhas
    # FR-2412, D-003: a tela de homologação diz o campo como ele mudou, com os números.
    total = next(
        item for item in legiveis if item["caminho"].endswith(f"{PERFIL['B']}/immediateVacancies")
    )
    assert (total["antes"], total["depois"]) == (0, 2)


def test_a_retificacao_que_zera_um_perfil_com_cadastro_imprime_cr(api_client, edital):
    """FR-2411: de 1 para 0, num Perfil que declara cadastro, o consolidado diz `CR` e a nota."""
    legiveis = _retificar_vagas(api_client, edital, "C", 0, "c-para-0")

    linhas = _linhas(_documento(edital, 2))
    assert _vagas_de(linhas, "P3") == "CR"
    assert pdf.NOTA_DO_CADASTRO in linhas
    total = next(
        item for item in legiveis if item["caminho"].endswith(f"{PERFIL['C']}/immediateVacancies")
    )
    assert (total["antes"], total["depois"]) == (1, 0)


def test_o_documento_ja_publicado_nao_muda(api_client, edital):
    """FR-2413: a Retificação compõe um documento novo, e o do original fica como foi gravado."""
    original = Publicacao.objects.get(edital=edital, publication_order=1)
    antes = (bytes(original.documento.bytes), original.documento.document_hash)

    _retificar_vagas(api_client, edital, "B", 2, "cr-para-2")

    original = Publicacao.objects.get(edital=edital, publication_order=1)
    assert (bytes(original.documento.bytes), original.documento.document_hash) == antes
    assert _vagas_de(_linhas(antes[0]), "P2") == "CR"
