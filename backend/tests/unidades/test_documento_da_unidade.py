"""O documento diz a unidade que praticou o ato (060, US1; FR-1112 a FR-1115, FR-1128 a FR-1130).

Duas unidades, cada Edital publicado na sua, com os seus atores e a sua autoridade. O Cefor sai
como saía — é o teste de bytes da `054` que o prova (`tests/contract/test_documento_publicado.py`);
aqui se prova que a outra unidade não sai com nada do Cefor, e que o que foi publicado guarda a
unidade do dia.
"""

import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import registrar_autoridade, registrar_unidade
from tests.fixtures.edital import caminho_perfil, complete_draft
from tests.fixtures.publicacao import levar_a_publicacao, publish_original, retify
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CABECALHO_DA_SERRA = [
    "Ministério da Educação",
    "Instituto Federal do Espírito Santo",
    "Campus Serra",
]


def _serra():
    unidade = registrar_unidade(
        "serra", sigla="Serra", nome="Campus Serra", cabecalho=["Campus Serra"], local="Serra (ES)"
    )
    return unidade, registrar_autoridade(unidade, cargo="Diretor-Geral do Campus Serra")


def _publicar_na_serra(api_client, process_payload, autoridade):
    headers = {
        "HTTP_AUTHORIZATION": "Bearer gestor-s|serra|processo:criar,processo:ativar,edital:criar",
        "HTTP_IDEMPOTENCY_KEY": "serra-processo-0001",
        "HTTP_X_CORRELATION_ID": "serra",
    }
    criado = api_client.post("/api/v1/admin/processos", process_payload, format="json", **headers)
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    # Outra semente: Perfil e Evento têm identificador global, e o mesmo rascunho nas duas unidades
    # seria recusado por identificador já vinculado.
    return levar_a_publicacao(
        api_client,
        edital,
        draft=complete_draft(seed=1),
        escopo="serra",
        signatory={"authorityId": str(autoridade.pk)},
    )


def _texto(edital, ordem=1):
    publicacao = Publicacao.objects.get(edital=edital, publication_order=ordem)
    return publicacao, texto_de(bytes(publicacao.documento.bytes))


def test_cada_documento_diz_a_propria_unidade_e_nada_da_outra(
    api_client, manager_headers, process_payload
):
    """SC-429: o documento do Campus Serra não tem o nome, a sigla nem o local do Cefor."""
    _unidade, autoridade = _serra()
    do_cefor = publish_original(api_client, manager_headers, process_payload)
    da_serra = _publicar_na_serra(api_client, process_payload, autoridade)

    _, texto_do_cefor = _texto(do_cefor)
    publicacao, texto_da_serra = _texto(da_serra)

    assert texto_da_serra.splitlines()[:3] == CABECALHO_DA_SERRA
    assert any(linha.startswith("Serra (ES), ") for linha in texto_da_serra.splitlines())
    for do_outro in ("Cefor", "Centro de Referência", "Vitória (ES)"):
        assert do_outro not in texto_da_serra
    assert texto_do_cefor.splitlines()[2:4] == [
        "Centro de Referência em Formação",
        "e em Educação a Distância",
    ]
    assert (publicacao.unidade_codigo, publicacao.unidade_local) == ("serra", "Serra (ES)")
    assert publicacao.signatory_role == "Diretor-Geral do Campus Serra"


def test_a_retificacao_diz_a_unidade_do_dia_dela_e_o_original_a_do_seu(
    api_client, manager_headers, process_payload
):
    """FR-1129, FR-1130: renomear a unidade entre os dois atos não reescreve o primeiro."""
    edital = publish_original(api_client, manager_headers, process_payload)
    original_antes = bytes(Publicacao.objects.get(edital=edital).documento.bytes)

    Unidade.objects.filter(codigo="cefor").update(
        nome="Cefor Renomeado", cabecalho=["Cefor Renomeado"], local="Serra (ES)"
    )
    retify(
        api_client,
        edital,
        [{"targetPath": caminho_perfil("name"), "operation": "REPLACE", "newValue": "Outro"}],
    )

    original, texto_original = _texto(edital, 1)
    retificada, texto_retificado = _texto(edital, 2)
    assert bytes(original.documento.bytes) == original_antes
    assert original.unidade_nome != retificada.unidade_nome == "Cefor Renomeado"
    assert "Centro de Referência em Formação" in texto_original
    assert texto_retificado.splitlines()[2] == "Cefor Renomeado"
    assert any(linha.startswith("Serra (ES), ") for linha in texto_retificado.splitlines())


def test_a_previa_compoe_com_a_unidade_registrada_agora(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A prévia não é ato e não congela nada: abre com o cabeçalho que o publicado vai ter."""
    from django.urls import reverse

    from tests.interface.conftest import identificar

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    Unidade.objects.filter(codigo="cefor").update(cabecalho=["Cabeçalho de Agora"])
    identificar(client, "auditor", ["auditor"])

    resposta = client.get(reverse("interface:previa-documento", args=[edital.id]))
    assert resposta.status_code == 200
    linhas = texto_de(resposta.content).splitlines()
    institucional = linhas.index("Instituto Federal do Espírito Santo")
    assert linhas[institucional + 1] == "Cabeçalho de Agora"


def test_o_resultado_congela_a_unidade_e_o_documento_a_le_dos_bytes(
    gestor, api_client, manager_headers, process_payload
):
    """FR-1112, FR-1128: a unidade entra no conteúdo divulgado, e o documento a lê de lá."""
    import json

    from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
    from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=65,
        codigo="0765",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1301,
    )
    publicacao = publicar_o_ato(cenario, chave="publicar-0765")
    conteudo = json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))

    assert conteudo["cabecalho"]["unidade"]["sigla"] == "Cefor"
    assert (publicacao.unidade_codigo, publicacao.unidade_sigla) == ("cefor", "Cefor")
    outra = {
        **conteudo["cabecalho"],
        "unidade": {"sigla": "Serra", "nome": "Campus Serra", "cabecalho": ["Campus Serra"]},
    }
    texto = texto_de_pdf_bytes(render_resultado_pdf({**conteudo, "cabecalho": outra}))
    linhas = texto.splitlines()
    institucional = linhas.index("Instituto Federal do Espírito Santo")
    assert linhas[institucional + 1] == "Campus Serra"
    assert "e em Educação a Distância" not in linhas[: institucional + 3]


def test_o_comprovante_diz_a_unidade_da_publicacao_aceita_e_nao_a_de_agora(
    client, inscricao_de_maria
):
    """FR-1115: o comprovante prova o que o candidato aceitou.

    A unidade é renomeada depois do envio; a página e o PDF continuam dizendo a unidade que a
    Publicação da versão aceita congelou — um comprovante que se reescreve não prova nada.
    """
    from django.urls import reverse

    from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
    from tests.fixtures.candidato import MARIA, identificar
    from tests.integration.portal.test_revisao_e_comprovante import _completar
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=_completar(inscricao_de_maria),
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-unidade-060",
    )
    Unidade.objects.filter(codigo="cefor").update(
        nome="Nome Novo", sigla="Novo", cabecalho=["Nome Novo"]
    )
    identificar(client, MARIA)

    pagina = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()
    arquivo = client.get(reverse("portal:comprovante-pdf", args=[enviada.id])).content

    assert "Cefor — Centro de Referência em Formação e em Educação a Distância" in pagina
    assert "Nome Novo" not in pagina
    texto = texto_de_pdf_bytes(arquivo)
    assert "Centro de Referência em Formação" in texto
    assert "Nome Novo" not in texto
