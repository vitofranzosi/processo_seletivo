"""Caractere sem grafia na tela — a prévia diz o que o documento não imprime, e a submissão para.

O Edital 90/2026 chegou à prévia com `?` no lugar dos marcadores, e nada na tela dizia por quê nem
onde corrigir. O caminho aqui é o real: o texto entra pelo formulário da etapa Perfis, como entraria
colado do Word.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import CARACTERE_SEM_GRAFIA
from processo_seletivo.interface.views import _destino
from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_fluxo import (
    EVENTOS,
    MARCOS,
    PERFIS,
    praticar,
    texto_do_pdf,
)


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


ATRIBUICOES = "●\u200b Conhecer o curso;\n●\u200b Experiência ≥ 2 anos."


def _compor_com_atribuicoes(client, edital, atribuicoes):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client, edital, dict(PERFIS, **{"perfil-0-duties": atribuicoes}), EVENTOS, marcos=MARCOS
    )
    edital.refresh_from_db()


@pytest.mark.django_db
@pytest.mark.integration
def test_a_previa_nomeia_o_caractere_e_o_documento_o_mostra_pelo_codigo(
    client,
    seletor_ligado,
    edital,
):
    _compor_com_atribuicoes(client, edital, ATRIBUICOES)

    tela = client.get(reverse("interface:previa", args=[edital.id]))
    html = tela.content.decode()
    assert "O que o documento não consegue imprimir" in html
    assert "Nas atribuições do Perfil «Perfil», há «≥» (U+2265)" in html
    assert reverse("interface:compor-etapa", args=[edital.id, "perfis"]) in html

    documento = texto_do_pdf(client.get(reverse("interface:previa-documento", args=[edital.id])))
    # O que a lista resolve sai resolvido; o que sobra aparece pelo código, nunca como `?`.
    assert "• Conhecer o curso;" in documento
    assert "• Experiência [U+2265] 2 anos." in documento
    assert "?" not in documento


@pytest.mark.django_db
@pytest.mark.integration
def test_a_previa_nao_fala_do_assunto_quando_nao_ha_o_que_dizer(
    client,
    seletor_ligado,
    edital,
):
    """Só o marcador do Word, que a lista resolve: nada a reescrever, e a seção não aparece."""
    _compor_com_atribuicoes(client, edital, "●\u200b Conhecer o curso.")

    html = client.get(reverse("interface:previa", args=[edital.id])).content.decode()
    assert "O que o documento não consegue imprimir" not in html


@pytest.mark.django_db
@pytest.mark.integration
def test_a_submissao_e_recusada_e_a_revisao_leva_ao_perfil(
    client,
    seletor_ligado,
    edital,
):
    _compor_com_atribuicoes(client, edital, ATRIBUICOES)

    revisao = client.get(reverse("interface:compor-etapa", args=[edital.id, "revisao"]))
    pendencia = next(
        item for item in revisao.context["pendencias"] if item["codigo"] == CARACTERE_SEM_GRAFIA
    )
    assert pendencia["severidade"] == "erro"
    assert (pendencia["etapa"], pendencia["corrigivel"]) == ("perfis", True)

    praticar(client, edital, "submeter")
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO

    # O controle: o mesmo Edital, com o trecho reescrito, submete — a recusa era do caractere.
    _compor_com_atribuicoes(client, edital, "\u25cf\u200b Experiência mínima de 2 anos.")
    praticar(client, edital, "submeter")
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_REVISAO


@pytest.mark.parametrize(
    ("caminho", "destino"),
    [
        ("/sections/id=x/content", "conteudo"),
        ("/profiles/id=x/classificationMilestones/id=y/drawMethod/source", "classificacao"),
        ("/drawMethod/source", "classificacao"),
        ("/schedule/id=x/location", "cronograma"),
        ("/attachments/id=x/label", "anexos"),
        ("matriculationRequest/declarationText", "inscricao"),
    ],
)
def test_cada_achado_leva_a_etapa_que_o_corrige(caminho, destino):
    etapa, _, corrigivel = _destino(caminho, CARACTERE_SEM_GRAFIA)
    assert (etapa, corrigivel) == (destino, True)


def test_o_titulo_da_secao_nao_se_corrige_em_etapa_nenhuma():
    """É do catálogo: dizer "Ir para Conteúdo" mandaria a pessoa a um campo que não existe."""
    assert _destino("/sections/id=x/title", CARACTERE_SEM_GRAFIA) == (None, "", False)
