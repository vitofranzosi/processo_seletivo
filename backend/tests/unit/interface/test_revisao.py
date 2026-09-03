"""A conferência da submissão não pode envelhecer quando o Edital ganha conteúdo.

A `006` acrescentou Etapas, modalidades e Seções ao conteúdo publicado e a Revisão continuou
mostrando Perfis e Cronograma, porque cada coleção era um bloco escrito à mão no template. Este
teste é o que impede a repetição: a Revisão é lida do snapshot, e toda coleção-raiz de entidades
precisa estar declarada.
"""

import pytest

from processo_seletivo.interface import revisao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_com_etapas


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_toda_colecao_do_snapshot_esta_declarada_na_conferencia(
    api_client, manager_headers, process_payload
):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    snapshot = edital_snapshot(Edital.objects.get(pk=edital.pk))

    de_entidades = {
        chave
        for chave, valor in snapshot.items()
        if isinstance(valor, list)
        and valor
        and all(isinstance(item, dict) and "id" in item for item in valor)
    }
    declaradas = {chave for chave, _, _, _ in revisao.COLECOES}

    assert de_entidades == declaradas, (
        "coleção do conteúdo publicado que a Revisão não mostra, ou o contrário: "
        f"{sorted(de_entidades ^ declaradas)}"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conferencia_mostra_cota_etapa_e_texto(api_client, manager_headers, process_payload):
    """O percentual é a informação mais sensível do documento e era a que não aparecia."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    # A forma canônica é a do conteúdo publicado. Humanizá-la para leitura é assunto da
    # materialização, e a `007` a trata — aqui o que importa é a cota aparecer na conferência.
    assert "Modalidade: PPI" in tudo and "20.0000%" in tudo
    assert "Lei 12.711/2012" in tudo
    assert "Prova didática" in "\n".join(
        item["titulo"] for bloco in blocos for item in bloco["itens"]
    )
    assert "Caráter: eliminatória e classificatória" in tudo
    assert "Peso: 2.0000" in tudo
    assert "O presente Edital estabelece as normas" in tudo, "o texto da seção, não só o título"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conferencia_mostra_o_que_a_012_acrescentou_a_etapa(
    api_client, manager_headers, process_payload
):
    """FR-007 da `012`: o que é congelado precisa aparecer em "o que será congelado".

    A pontuação máxima é o teto contra o qual cada avaliação da Etapa é validada depois, e as
    avaliações por inscrição são o que a distribuição cobra. O formulário coletava as duas e o
    documento publicado as imprimia; a conferência da submissão era o único lugar do caminho que
    as omitia — justamente o que existe para dizer o que está prestes a ficar imutável.
    """
    rascunho = rascunho_com_etapas()
    rascunho["stages"][0].update(evaluationsPerRegistration=2, maximumScore="100.0000")
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    assert "Pontuação máxima: 100.0000" in tudo
    assert "Avaliações por inscrição: 2" in tudo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_etapa_que_nada_declara_nao_inventa_o_padrao(
    api_client, manager_headers, process_payload
):
    """Ausência é "o Edital não declarou", e não "declarou o padrão" — como no documento."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    assert "Pontuação máxima" not in tudo
    assert "Avaliações por inscrição" not in tudo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cada_bloco_aponta_para_a_etapa_que_o_corrige(api_client, manager_headers, process_payload):
    from processo_seletivo.interface.views import CHAVES_ETAPA

    edital = publish_original(api_client, manager_headers, process_payload)
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))

    assert [bloco["etapa"] for bloco in blocos if bloco["etapa"] not in CHAVES_ETAPA] == []
