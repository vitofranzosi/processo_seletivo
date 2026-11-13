"""A publicação de convocados vista de fora: o portal, a área do candidato e a gestão (149).

Três leitores, e cada um com a sua garantia:

- **quem consulta a seleção**, sem sessão, vê a seção e a relação, e só os quatro dados de cada
  pessoa (FR-5712, SC-1859, SC-1860);
- **o convocado** lê na área dele o mesmo número, a mesma data e o mesmo prazo, e chega à publicação
  pelo *"Publicada em"* (FR-5725, FR-5726, SC-1862);
- **a comissão** vê a prévia sem gravar nada e publica pelo formulário (FR-5727 a FR-5732).
"""

import re
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application.publicar import (
    previa_da_publicacao,
    publicar_convocados,
)
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    ConvocacaoPublicada,
    PublicacaoDeConvocados,
)
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.interface.conftest import identificar
from tests.interface.test_fluxo import texto_de_pdf_bytes
from tests.interface.test_portal_convocacao import entrar_como

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

FUNDAMENTO = "No interesse da Administração, item 8.2 do Edital 77/2026."


@pytest.fixture
def publicado(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Um Edital por publicação, com a primeira da fila convocada e publicada no GPS."""
    cenario = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="i148",
        forma=FORMA_POR_PUBLICACAO,
    )
    edital = cenario[0]
    pessoa, convocacao = cenarios.convocar_primeira(
        cenario, gestor, chave="i148-c", vencimento=timezone.now() + timedelta(days=5)
    )
    declarado = publicar(edital, gestor, "i148-pub")
    return {
        "edital": edital,
        "pessoa": Inscricao.objects.get(id=pessoa.id),
        "convocacao": convocacao,
        "ato": PublicacaoDeConvocados.objects.get(id=declarado["id"]),
    }


def publicar(edital, gestor, chave):
    return publicar_convocados(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        recortes=None,
        alcance_confirmado=previa_da_publicacao(edital=edital, at=timezone.now())["assinatura"],
        autoridade=str(AUTORIDADE_DO_RESULTADO),
        declaracao_do_veiculo="item 7.2 do Edital",
        idempotency_key=chave,
        correlation_id="teste-148",
    )


def texto(resposta):
    assert resposta.status_code == 200, resposta.status_code
    corpo = resposta.content.decode()
    corpo = re.sub(r"<!--.*?-->", " ", corpo, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corpo))


# --- O portal, sem sessão (FR-5718 a FR-5724, SC-1859) --------------------------------------------


def test_sem_publicacao_a_selecao_nao_tem_a_secao(
    client, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="i148-sem"
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert 'id="convocacoes-titulo"' not in corpo


def test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao(client, publicado):
    edital, ato, pessoa = publicado["edital"], publicado["ato"], publicado["pessoa"]

    selecao = texto(client.get(reverse("portal:selecao", args=[edital.id])))
    relacao = texto(client.get(reverse("portal:convocados", args=[ato.id])))
    documento = client.get(reverse("portal:convocados-documento", args=[ato.id]))

    assert "Convocações" in selecao and "1ª publicação de convocados" in selecao
    assert "Ter uma convocação não é ter a documentação aceita" in selecao
    assert pessoa.nome in relacao and pessoa.protocolo in relacao
    assert "ato oficial de convocação" in relacao
    assert documento.status_code == 200
    assert documento["ETag"] == f'"{ato.documento.documento_hash}"'
    assert documento["Content-Disposition"].startswith("attachment;")
    assert documento.content == bytes(ato.documento.bytes), "os bytes gravados, nada recomposto"


def test_publicacao_inexistente_e_404(client, db):
    import uuid

    assert client.get(reverse("portal:convocados", args=[uuid.uuid4()])).status_code == 404
    assert (
        client.get(reverse("portal:convocados-documento", args=[uuid.uuid4()])).status_code == 404
    )


def test_a_pagina_e_o_documento_nao_publicam_dado_pessoal_alem_dos_quatro(client, publicado):
    """SC-1860: nem CPF, nem contato, nem fundamento, nem espécie — conferido contra os dados."""
    ato, pessoa = publicado["ato"], publicado["pessoa"]
    pagina = texto(client.get(reverse("portal:convocados", args=[ato.id])))
    documento = texto_de_pdf_bytes(
        client.get(reverse("portal:convocados-documento", args=[ato.id])).content
    )
    conteudo = bytes(ato.conteudo_publico).decode()

    proibidos = [
        valor
        for valor in (pessoa.cpf, pessoa.cpf_normalizado, pessoa.email, pessoa.telefone)
        if valor
    ]
    assert proibidos, "a premissa: a inscrição enviada tem CPF e contato"
    for onde, texto_lido in (("página", pagina), ("documento", documento), ("bytes", conteudo)):
        for valor in [*proibidos, FUNDAMENTO, "Para vaga inicial", "regularizar"]:
            assert valor not in texto_lido, f"{valor!r} apareceu no(a) {onde}"
    assert str(pessoa.id) not in conteudo, "nenhum identificador interno nos bytes"


def test_pagina_documento_e_area_do_candidato_dizem_o_mesmo(client, publicado):
    """SC-1862: nome, protocolo, número, data e prazo iguais nos três lugares."""
    ato, pessoa, convocacao = publicado["ato"], publicado["pessoa"], publicado["convocacao"]
    local = timezone.localtime(convocacao.vencimento)
    publicada = timezone.localtime(ato.publicado_em)
    prazo = local.strftime("%d/%m/%Y")
    pagina = texto(client.get(reverse("portal:convocados", args=[ato.id])))
    documento = texto_de_pdf_bytes(bytes(ato.documento.bytes))

    entrar_como(client, pessoa)
    area = client.get(reverse("portal:convocacao", args=[pessoa.id])).content.decode()

    for lugar in (pagina, documento):
        assert pessoa.nome in lugar and pessoa.protocolo in lugar
        assert prazo in lugar
        assert publicada.strftime("%d/%m/%Y") in lugar
    assert "1ª publicação de convocados".upper() in documento
    assert "1ª publicação de convocados" in pagina
    referencia = ComunicacaoEmitida.objects.get(convocacao=convocacao).referencia_da_publicacao
    assert "1ª publicação de convocados" in referencia
    assert f'href="{reverse("portal:convocados", args=[ato.id])}"' in area, (
        "o «Publicada em» leva à publicação"
    )
    assert prazo in area


def test_a_pagina_publica_custa_o_mesmo_com_mais_gente(client, publicado):
    """SC-1865, metade da página: o custo não acompanha o número de pessoas do conteúdo."""
    ato = publicado["ato"]
    with CaptureQueriesContext(connection) as uma:
        client.get(reverse("portal:convocados", args=[ato.id]))
    import json

    conteudo = json.loads(bytes(ato.conteudo_publico).decode())
    pessoa = conteudo["grupos"][0]["pessoas"][0]
    conteudo["grupos"][0]["pessoas"] = [
        {**pessoa, "protocolo": f"{pessoa['protocolo']}-{n}"} for n in range(5)
    ]
    from processo_seletivo.shared.canonical import canonical_bytes

    # O ato é append-only: a prova usa uma cópia dele com cinco pessoas, e não uma alteração.
    campos = {
        campo.attname: getattr(ato, campo.attname)
        for campo in PublicacaoDeConvocados._meta.concrete_fields
        if campo.attname != "id"
    }
    copia = PublicacaoDeConvocados.objects.create(
        **{**campos, "numero": 2, "conteudo_publico": canonical_bytes(conteudo)}
    )
    with CaptureQueriesContext(connection) as cinco:
        client.get(reverse("portal:convocados", args=[copia.id]))

    assert len(cinco) == len(uma)


# --- A gestão (FR-5727 a FR-5732, SC-1864) --------------------------------------------------------


def test_a_pagina_de_publicacao_pede_identificacao(client, seletor_ligado, publicado):
    resposta = client.get(
        reverse("interface:publicacao-de-convocados", args=[publicado["edital"].id])
    )
    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("interface:identificar"))


def test_a_previa_da_gestao_nao_grava_e_o_formulario_publica(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    cenario = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="i148-g",
        forma=FORMA_POR_PUBLICACAO,
    )
    edital = cenario[0]
    pessoa, convocacao = cenarios.convocar_primeira(
        cenario, gestor, chave="i148-g-c", vencimento=timezone.now() + timedelta(days=5)
    )
    identificar(client, "carlos", ["gestor"])
    endereco = reverse("interface:publicacao-de-convocados", args=[edital.id])
    antes = (PublicacaoDeConvocados.objects.count(), ComunicacaoEmitida.objects.count())

    pagina = client.get(endereco)
    nenhum = client.get(endereco, {"escolha": "1"})

    assert (PublicacaoDeConvocados.objects.count(), ComunicacaoEmitida.objects.count()) == antes
    corpo = texto(pagina)
    assert pessoa.nome in corpo and "O que será público" in corpo
    assert "1 convocação será publicada como ato oficial" in corpo
    assert "Publicar a 1ª publicação de convocados" in corpo
    assert "Nenhuma vaga ou lista escolhida" in texto(nenhum)
    assinatura = re.search(r'name="alcance" value="([^"]+)"', pagina.content.decode()).group(1)
    recorte = re.search(r'name="recorte" value="([^"]+)"', pagina.content.decode()).group(1)

    sem_veiculo = client.post(
        endereco,
        {
            "chave": "i148-g-1",
            "alcance": assinatura,
            "recorte": recorte,
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
        },
    )
    assert "A publicação não foi feita" in texto(sem_veiculo)
    assert PublicacaoDeConvocados.objects.count() == antes[0]

    publicada = client.post(
        endereco,
        {
            "chave": "i148-g-2",
            "alcance": assinatura,
            "recorte": recorte,
            "autoridade": str(AUTORIDADE_DO_RESULTADO),
            "declaracao_do_veiculo": "item 7.2 do Edital",
        },
    )
    assert publicada.status_code == 302
    depois = texto(client.get(endereco))
    assert "1ª publicação de convocados feita" in depois
    assert ConvocacaoPublicada.objects.get(convocacao=convocacao).efeito == "CONVOCA"
    assert "Não há convocação a publicar agora" in depois


def test_a_tela_do_recorte_leva_a_publicar_no_gps_e_mantem_o_registro_externo(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    from tests.fixtures.corte import MARCO

    cenario = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="i148-r",
        forma=FORMA_POR_PUBLICACAO,
    )
    edital = cenario[0]
    cenarios.convocar_primeira(
        cenario, gestor, chave="i148-r-c", vencimento=timezone.now() + timedelta(days=5)
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()

    assert "Publicar no GPS" in corpo
    assert reverse("interface:publicacao-de-convocados", args=[edital.id]) + "?" in corpo
    assert "Publicada fora do GPS?" in corpo
    assert 'name="referencia_da_publicacao"' in corpo


# --- O caminho até a publicação em qualquer forma (FR-5737, SC-1866) ------------------------------


def test_por_mensagem_a_tela_e_o_centro_levam_a_publicacao(
    client,
    seletor_ligado,
    settings,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """O caso do C10 na homologação: convocou por mensagem e não achou onde publicar a lista.

    O "Publicar no GPS" das pendentes só aparece na forma por publicação; a mensagem enviada não
    deixa pendência. A tela do recorte e o Centro de Controle passam a levar à publicação.
    """
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
        FORMA_POR_MENSAGEM_INDIVIDUAL,
    )
    from tests.fixtures.corte import MARCO

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    cenario = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="i149-msg",
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
    )
    edital = cenario[0]
    _, convocacao = cenarios.convocar_primeira(
        cenario, gestor, chave="i149-msg-c", vencimento=timezone.now() + timedelta(days=5)
    )
    cenarios.comunicar(edital, gestor, convocacao, chave="i149-msg-envio")
    identificar(client, "carlos", ["gestor"])
    publicacao = reverse("interface:publicacao-de-convocados", args=[edital.id])

    recorte = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()
    centro = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "Na página pública da seleção" in recorte
    assert "1 convocação comunicada ainda não está" in recorte
    assert f'href="{publicacao}?' in recorte
    assert f'href="{publicacao}"' in centro, "o Centro de Controle leva à publicação"

    publicar(edital, gestor, "i149-msg-pub")
    depois = client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()
    assert 'id="pagina-publica"' not in depois, "publicada, a seção sai"
