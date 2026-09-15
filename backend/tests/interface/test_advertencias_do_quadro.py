"""US3 da `027`: o que ficará sem quantidade a apurar é dito **antes** de a publicação congelar.

A auditoria mediu seis pontos em que a cadeia podia ter avisado e não avisou — a etapa dos Perfis
dizia CONCLUÍDA, a Revisão dizia "Nada pendente", a confirmação da publicação não dizia nada, o
portal e o PDF publicavam "2 vagas imediatas", e a Ocupação respondia meses depois, quando corrigir
já não é digitar de novo e sim Retificar.

**Advertência, e não recusa.** Quadro parcial é legítimo: a `025` decidiu que ausência de linha diz
"o Edital não declarou", e recusar transformaria isso em "o Edital não pode existir". O que a `027`
acrescenta é que o sistema **diga**, em números, e na etapa que resolve.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import Severity, validate_for_publication
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.interface.conftest import identificar
from tests.interface.test_compor_quadro import _id, compor, perfil

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def advertencias(edital, codigo):
    edital.refresh_from_db()
    return [
        item
        for item in validate_for_publication(edital_snapshot(edital))
        if item.code == codigo and item.severity == Severity.WARNING
    ]


def com_ampla_apontada(**extras):
    """O Perfil do arquivo vizinho, com a AC declarada como a da ampla concorrência."""
    return perfil(**{"perfil-0-generalCompetitionModalityId": _id("2510", sub=1), **extras})


# --- A9 · lista reservada sem linha ----------------------------------------------------------


def test_a9_a_lista_reservada_sem_linha_e_advertida_em_numeros(client, seletor_ligado, edital):
    """FR-324 e UX-044: diz o que o Perfil publica, o que o quadro reparte e qual recorte falta."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    # A PPI perde a linha: o Perfil declara a lista e não declara a quantidade dela.
    dados = com_ampla_apontada(total="80", quantidades=("56", "4", "20"))
    dados["linha-0-1-immediateVacancies"] = ""
    dados["linha-0-3-immediateVacancies"] = ""

    assert compor(client, edital, dados).status_code == 302, "quadro parcial é legítimo"

    achado = advertencias(edital, "vacancy_reserved_list_without_row")
    assert achado, "a lista declarada sem quantidade não pode passar em silêncio"
    mensagem = achado[0].message
    assert "80 vaga(s) imediata(s)" in mensagem, "o que o Perfil publica"
    assert "reparte 60" in mensagem, "o que o quadro reparte"
    assert "Pretos, pardos e indígenas" in mensagem, "e qual recorte fica de fora"
    assert "não terão quantidade a apurar" in mensagem


def test_a9_a_advertencia_nao_impede_a_submissao(client, seletor_ligado, edital):
    """A metade que faz dela advertência: o Edital continua submetível (D-003)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = com_ampla_apontada()
    dados["linha-0-1-immediateVacancies"] = ""
    dados["linha-0-3-immediateVacancies"] = ""
    compor(client, edital, dados)

    edital.refresh_from_db()
    impeditivos = [
        item
        for item in validate_for_publication(edital_snapshot(edital))
        if item.severity == Severity.BLOCKING_ERROR and item.code.startswith("vacancy_")
    ]
    assert impeditivos == []


def test_a9_a_revisao_deixa_de_dizer_que_nada_esta_pendente(client, seletor_ligado, edital):
    """FR-327, e é o segundo dos seis pontos de silêncio que a auditoria mediu.

    "Nada pendente — o Edital pode ser submetido" era verdadeiro pelo que o sistema conferia e
    falso pelo que importava: o Perfil declarava uma lista sem quantidade, e ninguém dizia.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = com_ampla_apontada()
    dados["linha-0-1-immediateVacancies"] = ""
    dados["linha-0-3-immediateVacancies"] = ""
    compor(client, edital, dados)

    edital.refresh_from_db()
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    assert "Nada pendente" not in corpo
    assert "Pretos, pardos e indígenas" in corpo


# --- A10 · a confirmação do ato repete ---------------------------------------------------------


def test_a10_a_confirmacao_da_submissao_repete_a_advertencia(client, seletor_ligado, edital):
    """FR-328: o último momento em que corrigir ainda é barato."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = com_ampla_apontada()
    dados["linha-0-1-immediateVacancies"] = ""
    dados["linha-0-3-immediateVacancies"] = ""
    compor(client, edital, dados)

    edital.refresh_from_db()
    corpo = client.get(reverse("interface:ato", args=[edital.id, "submeter"])).content.decode()

    assert "Aviso:" in corpo
    assert "não terão quantidade a apurar" in corpo


# --- A11 · a ampla não apontada é advertência própria ------------------------------------------


def test_a11_declarar_modalidade_sem_apontar_a_ampla_tem_advertencia_propria(
    client, seletor_ligado, edital
):
    """FR-325: duas advertências, porque os atos que as resolvem são diferentes.

    Uma se resolve escrevendo uma quantidade; a outra, escolhendo num campo que já existe. Somar os
    dois casos numa frase só mandaria metade das pessoas ao lugar errado.

    É também a promessa que a `025` deixou escrita na FR-176 e não teve como cumprir: identificar a
    ampla concorrência exigiria casar o nome, e a `R-006` recusou isso por escrito.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, perfil())

    achado = advertencias(edital, "general_competition_modality_undeclared")
    assert achado, "sem o apontamento, toda Modalidade conta como lista reservada"
    assert "3 Modalidade(s)" in achado[0].message
    assert achado[0].path.endswith("/generalCompetitionModalityId"), (
        "a âncora aponta o campo que resolve, e não o quadro"
    )


def test_a11_apontada_a_ampla_a_advertencia_propria_some(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, com_ampla_apontada())

    assert advertencias(edital, "general_competition_modality_undeclared") == []


def test_as_duas_advertencias_convivem_sem_se_confundir(client, seletor_ligado, edital):
    """Um Perfil pode ter os dois problemas, e cada um tem a sua frase e o seu destino."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = perfil()
    dados["linha-0-3-immediateVacancies"] = ""
    compor(client, edital, dados)

    edital.refresh_from_db()
    codigos = {
        item.code
        for item in validate_for_publication(edital_snapshot(edital))
        if item.severity == Severity.WARNING and item.code.startswith(("vacancy_", "general_"))
    }
    assert codigos == {
        "vacancy_reserved_list_without_row",
        "general_competition_modality_undeclared",
    }


# --- FR-326 · a Revisão mostra o total e o quadro lado a lado ----------------------------------


def test_a_revisao_mostra_o_total_e_o_que_o_quadro_reparte(client, seletor_ligado, edital):
    """UX-043: os dois números juntos, no bloco do Perfil.

    A Revisão exibia "2 vaga(s) imediata(s)" e nunca mencionava o quadro. Quem submetia lia o
    número que o Edital publica sem ver o que a apuração usaria, e os dois podiam não ter relação
    alguma — que é exatamente o achado.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, com_ampla_apontada(total="80", quantidades=("56", "4", "20")))

    edital.refresh_from_db()
    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "revisao"])
    ).content.decode()

    assert re.search(r"80 vaga\(s\) imediata\(s\)[^<]*·[^<]*o quadro reparte 80", corpo)
