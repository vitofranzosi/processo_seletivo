"""US3 da 020 — a Retificação substitui um anexo, e os dois coexistem.

É o passo que separa esta feature de um gerenciador de arquivos, e é exatamente o que a prática
observada perde: o Ifes substitui o arquivo no mesmo caminho, e o artefato anterior desaparece.
Depois disso, ninguém consegue responder o que estava valendo quando alguém se inscreveu.

O teste percorre a jornada pelos canais de cada ator — quem elabora publica, quem retifica
substitui, quem consulta baixa os dois — e não por escrita direta no banco.
"""

from urllib.parse import quote

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.anexos import criar_artefato
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.fixtures.snapshot import rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


def anexo_do(edital):
    return AnexoEdital.objects.get(edital=edital)


def substituir_por_retificacao(api_client, edital, *, suffix="a"):
    """Quem retifica sobe o novo; o ato referencia identidade e resumo, nunca os bytes."""
    anexo = anexo_do(edital)
    novo = criar_artefato(marca="Z", nome="requerimento-retificado.pdf")
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"/attachments/id={anexo.id}/artifactId",
                    "operation": "REPLACE",
                    "newValue": str(novo.id),
                },
                {
                    "targetPath": f"/attachments/id={anexo.id}/artifactHash",
                    "operation": "REPLACE",
                    "newValue": novo.document_hash,
                },
            ],
            suffix=suffix,
        ),
        suffix=suffix,
    )
    return novo


def test_a_retificacao_substitui_o_artefato_e_preserva_a_identidade(api_client, publicado):
    """D-001 — substituir o arquivo não cria um "Anexo VII" em silêncio."""
    anexo = anexo_do(publicado)
    antes = anexo.artefato_id

    novo = substituir_por_retificacao(api_client, publicado)

    vigente = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at").content
    publicado_agora = vigente["attachments"][0]
    assert publicado_agora["id"] == str(anexo.id), "a identidade normativa é a mesma"
    assert publicado_agora["artifactId"] == str(novo.id) != str(antes)
    assert publicado_agora["artifactHash"] == novo.document_hash


def test_os_dois_artefatos_coexistem_e_os_dois_respondem(client, api_client, publicado):
    """O passo emblemático (FR-042, SC-002): nenhum artefato anterior se perde."""
    antigo = anexo_do(publicado).artefato

    novo = substituir_por_retificacao(api_client, publicado)

    respostas = [client.get(reverse("public-anexo", args=[item.id])) for item in (antigo, novo)]
    assert [resposta.status_code for resposta in respostas] == [200, 200]
    assert respostas[0].content != respostas[1].content
    assert antigo.document_hash != novo.document_hash
    assert respostas[0]["ETag"] != respostas[1]["ETag"]


def test_a_retificacao_congela_o_artefato_novo(api_client, publicado):
    """FR-010 e FR-025 — sem isto, o link publicado pela Retificação responderia 404."""
    novo = substituir_por_retificacao(api_client, publicado)

    assert ArtefatoAnexo.objects.get(pk=novo.id).congelado_em is not None


def test_o_artefato_anterior_continua_congelado_e_intocado(api_client, publicado):
    """Congelar o congelado é no-op: a coleção inteira atravessa cada publicação."""
    antigo = anexo_do(publicado).artefato
    congelado_em = ArtefatoAnexo.objects.get(pk=antigo.id).congelado_em

    substituir_por_retificacao(api_client, publicado)

    assert ArtefatoAnexo.objects.get(pk=antigo.id).congelado_em == congelado_em


def test_a_consulta_por_um_instante_anterior_devolve_o_anexo_de_entao(api_client, publicado):
    """FR-040 e SC-003 — perguntar pelo passado devolve o passado, e não o presente."""
    from django.utils import timezone

    anexo = anexo_do(publicado)
    antigo = anexo.artefato_id
    antes = timezone.now()

    novo = substituir_por_retificacao(api_client, publicado)

    vigente = api_client.get(f"/api/v1/public/editais/{publicado.id}/versao-vigente").json()[
        "content"
    ]["attachments"][0]
    # `quote` porque `+00:00` numa query string significa espaço, e o instante chegaria inválido.
    de_entao = api_client.get(
        f"/api/v1/public/editais/{publicado.id}/versao-vigente?em={quote(antes.isoformat())}"
    ).json()["content"]["attachments"][0]

    assert vigente["artifactId"] == str(novo.id)
    assert de_entao["artifactId"] == str(antigo)
    assert de_entao["id"] == vigente["id"], "a identidade é a mesma; o artefato é que mudou"


def test_a_publicacao_historica_continua_entregando_o_artefato_daquela_versao(
    client, api_client, publicado
):
    """FR-041 — abrir a publicação de então não redireciona para o vigente."""
    antigo = anexo_do(publicado).artefato_id

    substituir_por_retificacao(api_client, publicado)

    # A publicação **original** é a que tem revisão; a da Retificação nasce com `revisao=None`.
    original_id = Publicacao.objects.get(edital=publicado, revisao__isnull=False).id
    original = api_client.get(f"/api/v1/public/publicacoes/{original_id}").json()
    assert original["content"]["attachments"][0]["artifactId"] == str(antigo)
    assert client.get(reverse("public-anexo", args=[antigo])).status_code == 200


def test_duas_retificacoes_sobre_o_mesmo_anexo_e_a_segunda_obsoleta_e_recusada(
    api_client, publicado
):
    """FR-036 — a concorrência é a que já existe, e esta feature a herda sem desenhar nada.

    As duas partem da mesma versão base, então a segunda carrega uma precondição de conteúdo que
    deixou de valer quando a primeira publicou. `expected_previous_hash` a recusa.
    """
    from tests.fixtures.publicacao import try_publish_retification

    anexo = anexo_do(publicado)
    base = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")
    primeira_troca = criar_artefato(marca="Y")
    segunda_troca = criar_artefato(marca="W")

    def alteracao(artefato):
        # As duas, sempre: substituir a identidade sem o resumo faria a versão afirmar bytes que
        # não são os que ela entrega, e `congelar_artefatos` recusa antes de publicar (FR-026).
        return [
            {
                "targetPath": f"/attachments/id={anexo.id}/artifactId",
                "operation": "REPLACE",
                "newValue": str(artefato.id),
            },
            {
                "targetPath": f"/attachments/id={anexo.id}/artifactHash",
                "operation": "REPLACE",
                "newValue": artefato.document_hash,
            },
        ]

    primeira = create_retification(
        api_client, publicado, alteracao(primeira_troca), suffix="a", base=base
    )
    segunda = create_retification(
        api_client, publicado, alteracao(segunda_troca), suffix="b", base=base
    )
    publish_retification(api_client, primeira, suffix="a")

    recusa = try_publish_retification(api_client, segunda, suffix="b")

    assert recusa.status_code == 409, recusa.content


def test_enderecar_o_anexo_por_posicao_e_recusado(api_client, publicado):
    """FR-032 — coleção endereçável por posição é coleção que a Retificação move sem querer."""
    recusa = create_retification(
        api_client,
        publicado,
        [{"targetPath": "/attachments/0/label", "operation": "REPLACE", "newValue": "OUTRO"}],
        suffix="c",
        esperar=422,
    )

    assert recusa["code"] == "positional_addressing_refused"
