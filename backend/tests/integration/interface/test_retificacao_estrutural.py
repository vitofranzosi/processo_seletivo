"""O que a tela de Retificação produz precisa atravessar o domínio até a consulta pública.

Os testes unitários provam a semântica das operações contra `apply_changes`. Este prova o resto
da cadeia: o valor de um Perfil acrescentado passa pela serialização canônica, pelo documento
publicado e pela projeção pública sem quebrar — que é onde um subconjunto de campos apareceria.
"""

import pytest

from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
    try_publish_retification,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_remover_e_acrescentar_perfil_chega_a_consulta_publica(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    codigos_antes = [p["code"] for p in vigente.content["profiles"]]
    assert len(codigos_antes) >= 1, "o Edital precisa ter Perfil para haver o que remover"

    grupos = retificacao_ui.campos_editaveis(vigente.content)
    primeiro_perfil = next(
        grupo["referencia"] for grupo in grupos if grupo["caminho"].startswith("/profiles/")
    )
    alteracoes, resumo = retificacao_ui.diferencas(
        vigente.content,
        {
            f"remover:{primeiro_perfil}": "1",
            "novo-perfil-42-code": "ENF-01",
            "novo-perfil-42-name": "Enfermeiro do Trabalho",
            "novo-perfil-42-locality": "Campus Serra",
            "novo-perfil-42-immediateVacancies": "2",
            "novo-perfil-42-requirements": "Graduação em Enfermagem\nCOREN ativo",
        },
    )
    assert sorted(a["operation"] for a in alteracoes) == ["ADD", "REMOVE"]
    assert all("id=" in a["targetPath"] or a["targetPath"].endswith("/-") for a in alteracoes), (
        "a tela emite pela chave da entidade, nunca pela posição"
    )
    assert len(resumo) == 2

    retificacao = create_retification(api_client, edital, alteracoes)
    publish_retification(api_client, retificacao)

    resposta = api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente")
    assert resposta.status_code == 200, resposta.content
    perfis = resposta.json()["content"]["profiles"]

    codigos = [p["code"] for p in perfis]
    assert codigos_antes[0] not in codigos, "o Perfil removido continua na projeção pública"
    assert "ENF-01" in codigos

    acrescentado = next(p for p in perfis if p["code"] == "ENF-01")
    assert acrescentado["requirements"] == ["Graduação em Enfermagem", "COREN ativo"]
    assert set(acrescentado) == set(perfis[0]), (
        "o Perfil acrescentado precisa ter a mesma forma dos demais"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_publicado_traz_o_perfil_acrescentado(
    api_client, manager_headers, process_payload
):
    """FR-023: o documento deriva do snapshot, então precisa acompanhar a estrutura nova."""
    from processo_seletivo.publicacoes.models import DocumentoPublicado

    edital = publish_original(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    alteracoes, _ = retificacao_ui.diferencas(
        vigente.content,
        {
            "novo-perfil-7-code": "ENF-01",
            "novo-perfil-7-name": "Enfermeiro do Trabalho",
            "novo-perfil-7-immediateVacancies": "2",
        },
    )
    retificacao = create_retification(api_client, edital, alteracoes)
    publicada = publish_retification(api_client, retificacao)

    documento = DocumentoPublicado.objects.get(publicacao=publicada.publication)
    assert b"Enfermeiro do Trabalho" in documento.bytes or b"ENF-01" in documento.bytes


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_evento_acrescentado_pela_tela_publica_com_a_forma_dos_demais(
    api_client, manager_headers, process_payload
):
    """O Evento acrescentado pela tela precisa atravessar a conferência de forma, e publicar.

    `EVENTO_PUBLICADO` exige `location` e `isRegistrationPeriod` em todo Evento, e a conferência
    roda **já na elaboração**, sobre o conteúdo que o ato produziria: sem as duas chaves, a
    Retificação nem nascia — a criação devolvia 422 antes de haver o que submeter. Os testes do
    domínio declaravam o Evento inteiro à mão, e por isso nenhum deles via o que a tela emitia.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    alteracoes, _ = retificacao_ui.diferencas(
        vigente.content,
        {
            "novo-evento-3-type": "RESULTADO",
            "novo-evento-3-description": "Divulgação do resultado final",
            "novo-evento-3-startAt": "2026-12-01T09:00",
            "novo-evento-3-location": "Página da chamada pública",
        },
    )
    retificacao = create_retification(api_client, edital, alteracoes)
    resposta = try_publish_retification(api_client, retificacao)
    assert resposta.status_code == 201, resposta.content

    publico = api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente")
    assert publico.status_code == 200, publico.content
    assert any(
        evento["location"] == "Página da chamada pública"
        for evento in publico.json()["content"]["schedule"]
    ), "o local declarado no acréscimo precisa chegar à consulta pública"

    eventos = (
        VersaoConsolidada.objects.filter(edital=edital)
        .latest("materialized_at")
        .content["schedule"]
    )
    acrescentado = next(e for e in eventos if e["description"] == "Divulgação do resultado final")
    assert set(acrescentado) == set(eventos[0]), (
        "o Evento acrescentado precisa ter a mesma forma dos demais"
    )
    assert acrescentado["location"] == "Página da chamada pública"
    assert acrescentado["isRegistrationPeriod"] is False
