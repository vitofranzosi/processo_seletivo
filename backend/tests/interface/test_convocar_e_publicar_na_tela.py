"""A conferência única e a confirmação única, pela tela (159, FR-6801 a FR-6804, FR-6808).

O caminho do botão: o POST sem `etapa` responde a conferência, e o POST de confirmação, com o resumo
do texto conferido, pratica — convocar, comunicar e publicar.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.models import ConvocacaoPublicada, PublicacaoDeConvocados
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture(autouse=True)
def correio(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"


def montar(gestor, api_client, manager_headers, process_payload, *, forma, prefixo):
    edital, _, _ = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        forma=forma,
        geral=2,
        cut=regra(surplusCount=1),
    )
    return edital


def campos(edital, chave):
    return {
        "lista": "",
        "chave": chave,
        "alcance": fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
            "assinatura"
        ],
        "vencimento": (timezone.localtime() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M"),
        "evento": "",
    }


def texto(resposta):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", resposta.content.decode()))


def test_por_mensagem_a_conferencia_mostra_o_publico_e_a_confirmacao_publica(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    edital = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
        prefixo="t159-msg",
    )
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:convocar-titulares", args=[edital.id, MARCO])
    dados = campos(edital, "t159-msg-chave")

    conferencia = client.post(endereco, dados)

    corpo = texto(conferencia)
    assert "Na página pública da seleção" in corpo and "Relação informativa" in corpo
    assert "nome e protocolo de cada pessoa" in corpo
    assert "Convocar as 2, enviar 2 mensagens e publicar a relação" in corpo
    assert 'name="autoridade"' in conferencia.content.decode()
    assert PublicacaoDeConvocados.objects.count() == 0, "a conferência não publica nada"
    resumo = re.search(r'name="texto_conferido" value="([^"]*)"', conferencia.content.decode())

    confirmada = client.post(
        endereco,
        {
            **dados,
            "etapa": "confirmar",
            "texto_conferido": resumo.group(1),
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
        },
    )

    assert confirmada.status_code == 302
    [ato] = PublicacaoDeConvocados.objects.filter(edital=edital)
    assert ConvocacaoPublicada.objects.filter(publicacao=ato, efeito="DIVULGA").count() == 2
    recorte = texto(client.get(confirmada["Location"]))
    assert "A relação foi publicada na página pública" in recorte
    publica = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    assert 'id="convocacoes-titulo"' in publica, "SC-2251: a relação está na página pública"


def test_por_publicacao_dois_botoes_e_o_gps_publica_como_ato_oficial(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    edital = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        forma=FORMA_POR_PUBLICACAO,
        prefixo="t159-gps",
    )
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:convocar-titulares", args=[edital.id, MARCO])
    dados = campos(edital, "t159-gps-chave")

    conferencia = client.post(endereco, dados).content.decode()

    assert 'value="confirmar-gps"' in conferencia and 'value="confirmar-externo"' in conferencia
    assert "Convocar as 2 e publicar no GPS" in conferencia
    assert "Convocar as 2 (a publicação será registrada depois)" in conferencia
    assert 'name="declaracao_do_veiculo"' in conferencia
    resumo = re.search(r'name="texto_conferido" value="([^"]*)"', conferencia).group(1)

    confirmada = client.post(
        endereco,
        {
            **dados,
            "etapa": "confirmar-gps",
            "texto_conferido": resumo,
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
            "declaracao_do_veiculo": "item 7.2 do Edital",
        },
    )

    assert confirmada.status_code == 302
    [ato] = PublicacaoDeConvocados.objects.filter(edital=edital)
    assert ato.declaracao_do_veiculo == "item 7.2 do Edital"
    assert ConvocacaoPublicada.objects.filter(publicacao=ato, efeito="CONVOCA").count() == 2
    assert "publicadas no GPS" in texto(client.get(confirmada["Location"]))
