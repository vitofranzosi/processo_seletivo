"""A tela que a transmissão mostra: sem semente, sem simular, sem refazer (FR-030, FR-052).

**As três ausências são a feature.** Um campo de semente permitiria escolhê-la; um botão de simular
permitiria ensaiar depois de conhecê-la; um botão de refazer permitiria repetir até o resultado
agradar. Nenhum dos três existe — e o teste afirma sobre os controles, não sobre a prosa, porque a
página fala dessas coisas justamente para explicar por que não as oferece.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _abrir(client, certame):
    identificar(client, "maria", [])
    return client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()


def test_a_tela_mostra_o_universo_o_metodo_e_o_estado_da_ocorrencia(certame, client):
    corpo = _abrir(client, certame)

    assert "Método declarado no Edital" in corpo
    assert "Ocorrência da fonte" in corpo
    assert "ainda não foi observada" in corpo
    assert "Observar a ocorrência na fonte" in corpo


def test_a_semente_fica_a_vista_antes_do_ato(certame, client):
    """É o que a transmissão precisa mostrar: o material observado, antes de sortear."""
    observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="tela-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )

    corpo = _abrir(client, certame)

    assert "Material bruto observado" in corpo
    assert "12345 67890 11223 44556 77889" in corpo


def test_nao_ha_campo_de_semente_nem_botao_de_simular_ou_refazer(certame, client):
    corpo = _abrir(client, certame)

    campos = re.findall(r'<(?:input|select|textarea)[^>]*name="([^"]+)"', corpo)
    for campo in campos:
        assert not re.search(r"semente|seed", campo, re.I), campo
    for rotulo in (">Simular", ">Pré-visualizar", ">Refazer", ">Sortear de novo", ">Recalcular"):
        assert rotulo not in corpo


def test_os_destinos_de_post_desta_tela_sao_declarados_e_finitos(certame, client):
    """Uma rota nova de simulação ou reexecução apareceria aqui como `action` a mais."""
    corpo = _abrir(client, certame)

    acoes = {
        acao
        for acao in re.findall(r'<form method="post" action="([^"]+)"', corpo)
        if "sorteio" in acao
    }
    esperadas = {
        reverse(nome, args=[certame["edital"].id, certame["marco"]])
        for nome in (
            "interface:publicar-relacao-do-sorteio",
            "interface:observar-ocorrencia-do-sorteio",
        )
    }
    assert acoes == esperadas


def test_o_botao_de_sortear_so_aparece_com_relacao_congelada_e_ocorrencia_observada(
    certame, client
):
    """A ordem dos fatos é a feature: universo comprometido, **depois** semente, depois ato."""
    antes = _abrir(client, certame)
    assert "Realizar o sorteio" not in antes

    identificar(client, "maria", [])
    client.post(
        reverse(
            "interface:publicar-relacao-do-sorteio", args=[certame["edital"].id, certame["marco"]]
        ),
        {"lista_id": "", "chave_idempotencia": "tela-sorteio-relacao"},
    )
    assert "Realizar o sorteio" not in _abrir(client, certame), "sem semente não há o que sortear"

    observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="tela-sorteio-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )

    assert "Realizar o sorteio" in _abrir(client, certame)
