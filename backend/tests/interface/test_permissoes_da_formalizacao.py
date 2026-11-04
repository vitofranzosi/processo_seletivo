"""A matriz de permissões da entrega documental, linha a linha, por URL e por POST (117, SC-1104).

"404" é a recusa de inexistente; "403", a de autorização no escopo. Cada linha da matriz da spec
tenta toda porta da feature, e recebe a recusa que a matriz manda — inclusive no POST forjado e no
histórico da definição. A linha do `acesso:gerir` está em
`tests/integration/formalizacao/test_acesso.py`, porque só a entrada institucional a alcança.
"""

import pytest
from django.urls import reverse

from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    montar_cenario_da_formalizacao,
    servido,
)
from tests.integration.formalizacao.apoio import documentos_de
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

OUTRO_PERFIL = "00000000-0000-0000-0000-00000000abcd"


@pytest.fixture
def portas(
    client, settings, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=2, prefixo="matriz-117"
    )
    definir_documentos(cenario.edital, gestor)
    edital = cenario.edital
    inscricao, convocacao = cenario.aptas[0]
    documento = documentos_de(edital, inscricao)[0]
    return {
        "cenario": cenario,
        "lista": reverse("interface:formalizacao"),
        "pagina": reverse("interface:formalizacao-edital", args=[edital.id]),
        "documento": reverse(
            "interface:formalizacao-documento",
            args=[edital.id, inscricao.id, documento.origem, documento.objeto_id],
        ),
        "verificar": reverse("interface:formalizacao-verificar", args=[edital.id]),
        "baixar": reverse("interface:formalizacao-baixar", args=[edital.id]),
        "exportar": reverse(
            "interface:formalizacao-exportar-pessoa", args=[edital.id, inscricao.id]
        ),
        "definicao": reverse("interface:formalizacao-definicao", args=[edital.id]),
        "designar": reverse("interface:acessos-formalizacao"),
        "convocacao": reverse(
            "interface:documentos-da-convocacao",
            args=[edital.id, convocacao.marco_id, convocacao.id],
        ),
        "inscricao": inscricao,
    }


def _respostas(client, portas):
    pagina = client.get(portas["pagina"])
    arquivo = abrir_arquivo(client, portas["documento"])
    verificar = client.post(
        portas["verificar"], {"alcance": "selecao", "pessoa": [str(portas["inscricao"].id)]}
    )
    baixar = client.post(portas["baixar"], {"comprovante": "forjado"})
    exportar = client.post(portas["exportar"])
    if exportar.status_code == 200:
        servido(exportar)
    return {
        "pagina": pagina.status_code,
        "arquivo": arquivo.status_code,
        "verificar": verificar.status_code,
        "baixar": baixar.status_code,
        "exportar": exportar.status_code,
        "definicao": client.get(portas["definicao"]).status_code,
        "gravar_definicao": client.post(
            portas["definicao"], {"requisito": [], "motivo": "forjado"}
        ).status_code,
        "designar": client.get(portas["designar"]).status_code,
        "convocacao": client.get(portas["convocacao"]).status_code,
    }


def test_formalizacao_com_designacao_sem_restricao(client, portas):
    designar_direto(portas["cenario"].edital, "rui")
    identificar(client, "rui", ["formalizacao"])

    assert _respostas(client, portas) == {
        "pagina": 200,
        "arquivo": 200,
        "verificar": 200,
        "baixar": 409,
        "exportar": 200,
        "definicao": 403,
        "gravar_definicao": 403,
        "designar": 403,
        "convocacao": 403,
    }


def test_formalizacao_no_perfil_a_e_pessoa_do_perfil_b(client, portas):
    designar_direto(portas["cenario"].edital, "rui", perfis=[OUTRO_PERFIL])
    identificar(client, "rui", ["formalizacao"])
    respostas = _respostas(client, portas)

    assert respostas["pagina"] == 200
    assert portas["inscricao"].protocolo not in client.get(portas["pagina"]).content.decode()
    assert {k: respostas[k] for k in ("arquivo", "verificar", "exportar")} == {
        "arquivo": 404,
        "verificar": 404,
        "exportar": 404,
    }


def test_formalizacao_sem_designacao_no_edital(client, portas):
    identificar(client, "rui", ["formalizacao"])
    respostas = _respostas(client, portas)

    assert {k: respostas[k] for k in ("pagina", "arquivo", "verificar", "baixar", "exportar")} == {
        "pagina": 404,
        "arquivo": 404,
        "verificar": 404,
        "baixar": 404,
        "exportar": 404,
    }
    assert client.get(portas["lista"]).status_code == 200
    assert respostas["definicao"] == 403


def test_designacao_vigente_e_papel_revogado(client, portas):
    designar_direto(portas["cenario"].edital, "rui")
    identificar(client, "rui", [])
    respostas = _respostas(client, portas)

    for porta in ("pagina", "arquivo", "verificar", "baixar", "exportar"):
        assert respostas[porta] == 403, porta
    corpo = client.get(portas["pagina"]).content.decode()
    assert "papel Formalização" in corpo
    assert client.get(portas["lista"]).status_code == 403


@pytest.mark.parametrize(
    ("subject", "papeis", "definicao", "gravar"),
    [
        ("maria", [], 200, 302),
        ("carlos", ["gestor"], 200, 302),
        ("joao", [], 403, 403),
        ("exporta", ["exportador"], 403, 403),
        ("auditora", ["auditor"], 200, 403),
    ],
    ids=["presidencia", "gestor", "membro-da-conferencia", "matricula-exportar", "auditor"],
)
def test_as_demais_bases_nao_alcancam_a_pagina_do_setor(
    client, portas, subject, papeis, definicao, gravar
):
    """FR-3665: presidência, `comissao:gerir`, conferência, matrícula e auditoria: 403 no setor."""
    designar_direto(portas["cenario"].edital, subject)
    identificar(client, subject, papeis)
    respostas = _respostas(client, portas)

    for porta in ("pagina", "arquivo", "verificar", "baixar", "exportar"):
        assert respostas[porta] == 403, porta
    assert respostas["definicao"] == definicao
    assert respostas["gravar_definicao"] == gravar
    assert respostas["designar"] == 403
    assert client.get(portas["lista"]).status_code == 403


def test_ator_de_outra_unidade_recebe_inexistente_em_tudo(client, portas):
    designar_direto(portas["cenario"].edital, "rui")
    identificar(client, "rui", ["formalizacao", "gestor"], escopo="outra")
    respostas = _respostas(client, portas)

    for porta in ("pagina", "arquivo", "verificar", "baixar", "exportar", "definicao"):
        assert respostas[porta] == 404, porta
    assert respostas["gravar_definicao"] == 404
    assert not ExportacaoDeFormalizacao.objects.exists()


def test_as_urls_levam_so_identificadores_opacos(portas):
    """FR-3703: nada de nome, protocolo ou nome de arquivo no endereço."""
    inscricao = portas["inscricao"]
    for chave in ("pagina", "documento", "verificar", "baixar", "exportar", "definicao"):
        assert inscricao.nome not in portas[chave]
        assert inscricao.protocolo not in portas[chave]
        assert ".pdf" not in portas[chave]
