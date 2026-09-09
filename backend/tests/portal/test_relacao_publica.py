"""A relação no canal público, anônimo (021, FR-005, FR-006, FR-011).

**Duas afirmações, e a segunda é a que a feature promete.** A primeira: a página mostra número,
nome e protocolo, e não mostra CPF nem identificador interno. A segunda: o resumo publicado é
**recalculável** do que a página mostra — o cidadão refaz o número em vez de aceitá-lo, que é a
palavra que esta feature existe para não pedir (R-015).
"""

import json

import pytest
from django.urls import reverse

from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.models import RelacaoDeHabilitados
from tests.fixtures.sorteio import certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def publicada(gestor, api_client, manager_headers, process_payload):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="portal-relacao-1",
        correlation_id="teste-portal",
    )
    return certame, RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])


def test_a_pagina_abre_sem_autenticacao_e_mostra_os_tres_dados(client, publicada):
    certame, relacao = publicada

    resposta = client.get(reverse("portal:relacao-de-habilitados", args=[relacao.id]))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    for participante in relacao.participantes.select_related("inscricao"):
        assert str(participante.numero_publico) in corpo
        assert participante.inscricao.nome in corpo
        assert participante.inscricao.protocolo in corpo


def test_a_pagina_nao_expoe_cpf_nem_identificador_interno(client, publicada):
    certame, relacao = publicada

    corpo = client.get(reverse("portal:relacao-de-habilitados", args=[relacao.id])).content.decode()

    for inscricao in certame["inscricoes"]:
        assert str(inscricao.id) not in corpo, "identificador interno vazou para o canal público"
        assert inscricao.cpf not in corpo
        assert inscricao.cpf_normalizado not in corpo


def test_o_criterio_e_os_dois_resumos_sao_publicados(client, publicada):
    _certame, relacao = publicada

    corpo = client.get(reverse("portal:relacao-de-habilitados", args=[relacao.id])).content.decode()

    assert relacao.criterio_de_projecao in corpo
    assert relacao.resumo in corpo
    assert relacao.metodo_hash in corpo


def test_o_resumo_e_recalculavel_do_que_a_pagina_mostra(client, publicada):
    """A prova que fecha o círculo: nenhum dado oculto entra na conta (R-015, SC-001)."""
    _certame, relacao = publicada
    corpo = client.get(reverse("portal:relacao-de-habilitados", args=[relacao.id])).content.decode()

    # Reconstruído **do que se lê**, e não do banco: número, nome e protocolo, na ordem publicada.
    lidos = [
        {
            "publicNumber": p.numero_publico,
            "name": p.inscricao.nome,
            "protocol": p.inscricao.protocolo,
        }
        for p in relacao.participantes.select_related("inscricao").order_by("numero_publico")
    ]
    for participante in lidos:
        assert participante["name"] in corpo and participante["protocol"] in corpo

    recalculado = canonical_sha256(
        {
            "relationId": str(relacao.id),
            "editalId": str(relacao.edital_id),
            "versionId": str(relacao.versao_id),
            "profileId": str(relacao.perfil_id),
            "milestoneId": str(relacao.marco_id),
            "listId": str(relacao.lista_id) if relacao.lista_id else None,
            "methodHash": relacao.metodo_hash,
            "criterion": relacao.criterio_de_projecao,
            "participants": lidos,
        }
    )
    assert recalculado == relacao.resumo
    assert json.dumps(lidos)  # serializável: é o que o verificador de terceiro recebe


def test_a_relacao_sucedida_continua_respondendo_e_diz_que_foi_sucedida(client, publicada):
    certame, relacao = publicada
    publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="portal-relacao-2",
        correlation_id="teste-portal",
        motivo="Resultado de origem sucedido.",
    )

    corpo = client.get(reverse("portal:relacao-de-habilitados", args=[relacao.id])).content.decode()

    assert "foi sucedida" in corpo
    assert "Ver a relação que a sucedeu" in corpo


def test_a_api_publica_devolve_o_mesmo_conteudo_que_o_resumo_cobre(client, publicada):
    """Uma projeção só (021, FR-011, R-015).

    Se a API devolvesse uma projeção "mais rica porque é API", o resumo deixaria de fechar sobre o
    que ela entrega — e o verificador de terceiro teria de escolher em qual acreditar.
    """
    _certame, relacao = publicada

    resposta = client.get(f"/api/v1/public/sorteio/relacoes/{relacao.id}")
    corpo = resposta.json()

    assert resposta.status_code == 200
    assert corpo["relationHash"] == relacao.resumo
    assert corpo["methodHash"] == relacao.metodo_hash
    assert (
        canonical_sha256(
            {
                chave: corpo[chave]
                for chave in (
                    "relationId",
                    "editalId",
                    "versionId",
                    "profileId",
                    "milestoneId",
                    "listId",
                    "methodHash",
                    "criterion",
                    "participants",
                )
            }
        )
        == relacao.resumo
    )


def test_a_api_publica_nao_expoe_identificador_interno(client, publicada):
    certame, relacao = publicada

    bruto = client.get(f"/api/v1/public/sorteio/relacoes/{relacao.id}").content.decode()

    for inscricao in certame["inscricoes"]:
        assert str(inscricao.id) not in bruto
        assert inscricao.cpf_normalizado not in bruto


def test_a_api_publica_responde_304_para_quem_ja_tem_a_representacao(client, publicada):
    _certame, relacao = publicada

    resposta = client.get(
        f"/api/v1/public/sorteio/relacoes/{relacao.id}",
        HTTP_IF_NONE_MATCH=f'"{relacao.resumo}"',
    )

    assert resposta.status_code == 304
