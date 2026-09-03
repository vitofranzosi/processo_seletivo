"""A devolução da Retificação, que o domínio tinha e a tela não oferecia (FR-027).

**Por que existe.** `transition_retification` admite `devolver` desde a `001`, a API o expõe em
`/retificacoes/{id}/devolucoes`, e a própria tela de submissão promete o ato ao dizer que a
Retificação "deixa de poder ser editada até ser **devolvida** ou homologada". A tabela de atos da
interface simplesmente não tinha a entrada, e quem revisava via só "Homologar" — a promessa do
texto sem o botão que a cumpre.

O ato parte de **duas** situações, e é isso que ele acrescenta à tabela: desfazer a revisão e
desfazer a homologação são o mesmo ato, com o mesmo motivo obrigatório.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

VAGAS = caminho_perfil("immediateVacancies")
MOTIVO = "A justificativa não menciona a autorização da Diretoria."


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


@pytest.fixture
def em_revisao(client, seletor_ligado, edital, vigente):
    """Uma Retificação submetida, composta pela própria tela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**campos(vigente, **{VAGAS: "9"}), "justificativa": "Ampliação", "confirmar": "1"},
    )
    retificacao = Retificacao.objects.get()
    ato(client, retificacao, "submeter")
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.EM_REVISAO
    return retificacao


def ato(client, retificacao, acao, **campos_extra):
    url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
    chave = client.get(url).context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, **campos_extra})


def test_quem_revisa_encontra_a_devolucao_prometida_pelo_texto(client, em_revisao):
    identificar(client, "bruno.homologador", ["homologador"])

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[em_revisao.id])
    ).content.decode()

    assert "Devolver para elaboração" in corpo


def test_devolver_reabre_a_elaboracao_e_registra_o_motivo(client, em_revisao):
    identificar(client, "bruno.homologador", ["homologador"])

    resposta = ato(client, em_revisao, "devolver", motivo=MOTIVO)

    assert resposta.status_code == 302
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.EM_ELABORACAO
    assert em_revisao.return_reason == MOTIVO


def test_a_homologada_tambem_e_devolvida(client, em_revisao):
    """O ato parte de duas situações, e é por isso que a tabela precisou de conjunto."""
    identificar(client, "bruno.homologador", ["homologador"])
    ato(client, em_revisao, "homologar", motivo="Conferido")
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.HOMOLOGADA

    resposta = ato(client, em_revisao, "devolver", motivo=MOTIVO)

    assert resposta.status_code == 302
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.EM_ELABORACAO
    assert em_revisao.homologated_by == "", "a homologação desfeita não descreve mais o ato"


def test_devolvida_a_retificacao_volta_a_aceitar_edicao(client, edital, vigente, em_revisao):
    """A prova de que a volta é real: a tela de edição recusa o que não está em elaboração."""
    identificar(client, "bruno.homologador", ["homologador"])
    ato(client, em_revisao, "devolver", motivo=MOTIVO)

    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:retificar", args=[edital.id]))

    assert resposta.status_code == 200


def test_o_motivo_e_exigido_antes_do_command(client, em_revisao):
    identificar(client, "bruno.homologador", ["homologador"])
    url = reverse("interface:retificacao-ato", args=[em_revisao.id, "devolver"])
    chave = client.get(url).context["chave_idempotencia"]

    resposta = client.post(url, {"chave_idempotencia": chave, "motivo": "  "})

    assert resposta.status_code == 422
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.EM_REVISAO


def test_quem_elabora_nao_devolve(client, em_revisao):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[em_revisao.id])
    ).content.decode()
    recusa = ato(client, em_revisao, "devolver", motivo=MOTIVO)

    assert "Devolver para elaboração" not in corpo
    assert recusa.status_code == 403
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.EM_REVISAO


def test_a_publicada_nao_e_devolvida(client, em_revisao):
    """Publicada é imutável: a volta existe até a Publicação, e não depois dela.

    A tela esconde o botão, e é o servidor que recusa — as duas coisas, porque só a primeira
    seria a recusa da tela, e não a do domínio.
    """
    identificar(client, "bruno.homologador", ["homologador"])
    ato(client, em_revisao, "homologar", motivo="Conferido")
    identificar(client, "carla.publicadora", ["publicador"])
    em_revisao.refresh_from_db()
    ato(client, em_revisao, "publicar", signatario="reitoria")
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.PUBLICADA

    identificar(client, "bruno.homologador", ["homologador"])
    url = reverse("interface:retificacao-ato", args=[em_revisao.id, "devolver"])
    corpo = client.get(url).content.decode()
    forcado = client.post(url, {"chave_idempotencia": "devolver-publicada", "motivo": MOTIVO})

    assert "Confirmar: Devolver para elaboração" not in corpo
    assert forcado.status_code == 409, "o POST direto também é recusado"
    em_revisao.refresh_from_db()
    assert em_revisao.status == Retificacao.Status.PUBLICADA
