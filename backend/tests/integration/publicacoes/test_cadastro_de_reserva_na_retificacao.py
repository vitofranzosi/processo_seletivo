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
from tests.fixtures.snapshot import PERFIL, com_cadastro, rascunho_completo
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _rascunho():
    """P2 só de cadastro de reserva, P3 com vaga e cadastro, P1 como vem."""
    rascunho = rascunho_completo()
    for perfil in rascunho["profiles"]:
        if perfil["id"] == PERFIL["B"]:
            perfil.update(immediateVacancies=0)
            for linha in perfil.get("vacancyTable") or []:
                linha["immediateVacancies"] = 0
            com_cadastro(perfil, "LIMITED", 10)
        elif perfil["id"] == PERFIL["C"]:
            com_cadastro(perfil, "LIMITED", 10)
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


# --- 162: a Retificação muda o número pelo corte (FR-6948, FR-6950, FR-6951) --------------------


def _marco_que_convoca(edital, perfil):
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    (alvo,) = [p for p in vigente["profiles"] if p["id"] == PERFIL[perfil]]
    return alvo["classificationMilestones"][0]["id"]


def test_o_campo_do_limite_so_existe_no_perfil_legado(edital):
    """FR-6950: o número do limitado não se retifica pelo campo; ele vem do corte."""
    from processo_seletivo.interface.retificacao import campos_editaveis

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    grupos = campos_editaveis(vigente)
    caminhos = {campo["caminho"] for grupo in grupos for campo in grupo["campos"]}
    assert not any(caminho.endswith("/reserveLimit") for caminho in caminhos)

    legado = {**vigente, "profiles": [dict(p) for p in vigente["profiles"]]}
    for perfil in legado["profiles"]:
        if perfil["id"] == PERFIL["C"]:
            perfil["reserveLimit"] = 10
    caminhos = {campo["caminho"] for grupo in campos_editaveis(legado) for campo in grupo["campos"]}
    assert f"/profiles/id={PERFIL['C']}/reserveLimit" in caminhos


def test_o_perfil_acrescentado_por_retificacao_nao_tem_o_campo():
    from processo_seletivo.interface.retificacao import NOVO_PERFIL, _perfil_completo

    assert "reserveLimit" not in {chave for chave, _, _ in NOVO_PERFIL}
    assert _perfil_completo({"reserveLimit": 7})["reserveLimit"] is None


def test_retificar_o_excedente_muda_o_numero_e_a_conferencia_o_diz(api_client, edital):
    """FR-6950, SC-2303: a conferência ganha a linha derivada, e o documento diz o número novo."""
    from processo_seletivo.interface.retificacao import _cadastro_retificado

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content
    caminho = (
        f"/profiles/id={PERFIL['C']}/classificationMilestones/id="
        f"{_marco_que_convoca(edital, 'C')}/cutRule/surplusCount"
    )
    alteracao = {"targetPath": caminho, "operation": "REPLACE", "newValue": 12}
    linhas = _cadastro_retificado(vigente, [alteracao])
    assert [(linha["rotulo"], linha["antes"], linha["depois"]) for linha in linhas] == [
        ("Cadastro de reserva", "Limitado: até 10", "Limitado: até 12")
    ]

    retificacao = create_retification(api_client, edital, [alteracao], suffix="exc-12")
    publish_retification(api_client, retificacao, suffix="exc-12")
    # A frase quebra entre linhas do PDF: confere-se o texto corrido.
    # O consolidado diz o número novo na unidade do corte do Perfil, com a frase da FR-6942. A frase
    # "até N" do cadastro só sai na tabela de características, que este Edital não compõe.
    corrido = " ".join(_linhas(_documento(edital, 2)))
    assert "mais 12 suplentes" in corrido
    assert pdf.SUPLENTES_DO_CADASTRO in corrido


def test_levar_o_numero_a_zero_e_recusado(api_client, edital):
    """FR-6951: a Retificação não leva o número derivado a zero."""
    caminho = (
        f"/profiles/id={PERFIL['C']}/classificationMilestones/id="
        f"{_marco_que_convoca(edital, 'C')}/cutRule/surplusCount"
    )
    # A recusa vem já na elaboração: o conteúdo que o ato produziria tem o impedimento.
    problema = create_retification(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": 0}],
        suffix="exc-0",
        esperar=422,
    )
    assert "o cadastro seria de zero classificados" in problema["detail"]
