"""As telas preveem a recusa do marco intermediário (133, FR-4538, SC-1420 "pela tela").

A ocupação e a convocação da *Classificação para a entrevista* abrem com o aviso e o link do marco
que apura, sem formulário de ato; o POST direto às rotas volta com a recusa, e nada é gravado; o
gesto "Apurar" da condução põe os recortes entre os impedidos.
"""

import pytest
from django.urls import reverse

from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.interface import conducao_do_marco
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures import marco_intermediario as m900
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

FRASE = "decide quem participa da Etapa Entrevista"


@pytest.fixture
def cenario(client, gestor, api_client, manager_headers, process_payload, seletor_ligado):
    cenario = m900.ate_a_apuracao_m2(
        m900.montar(gestor, api_client, manager_headers, process_payload)
    )
    identificar(client, "carlos", ["gestor"])
    return cenario


def _abrir(client, rota, edital, marco):
    resposta = client.get(reverse(rota, args=[edital.id, marco]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_a_ocupacao_do_marco_intermediario_nao_oferece_ato(client, cenario):
    edital = cenario["edital"]
    corpo = _abrir(client, "interface:ocupacao", edital, m900.MARCO_1)

    assert FRASE in corpo
    assert reverse("interface:ocupacao", args=[edital.id, m900.MARCO_2]) in corpo
    for rota in ("emitir-apuracao", "acrescentar-vagas", "causar-faixa"):
        assert reverse(f"interface:{rota}", args=[edital.id, m900.MARCO_1]) not in corpo


def test_a_convocacao_do_marco_intermediario_nao_oferece_ato(client, cenario):
    edital = cenario["edital"]
    corpo = _abrir(client, "interface:convocacao", edital, m900.MARCO_1)

    assert FRASE in corpo
    assert reverse("interface:convocacao", args=[edital.id, m900.MARCO_2]) in corpo
    assert reverse("interface:convocar", args=[edital.id, m900.MARCO_1]) not in corpo
    assert "Convocar os titulares num ato só" not in corpo


def test_as_telas_do_marco_final_continuam_iguais(client, cenario):
    edital = cenario["edital"]
    corpo = _abrir(client, "interface:convocacao", edital, m900.MARCO_2)

    assert FRASE not in corpo
    assert "Convocar os titulares num ato só" in corpo


def test_o_post_direto_a_apuracao_e_recusado_e_nada_e_gravado(client, cenario):
    edital = cenario["edital"]
    antes = ApuracaoDeOcupacao.objects.count()

    client.post(
        reverse("interface:emitir-apuracao", args=[edital.id, m900.MARCO_1]),
        {"lista": "", "chave": "post-direto-apurar"},
    )
    corpo = _abrir(client, "interface:ocupacao", edital, m900.MARCO_1)

    assert ApuracaoDeOcupacao.objects.count() == antes
    assert "Não foi possível apurar" in corpo


def test_o_post_direto_a_convocacao_e_recusado_e_nada_e_gravado(client, cenario):
    edital = cenario["edital"]
    antes = Convocacao.objects.count()

    client.post(
        reverse("interface:convocar", args=[edital.id, m900.MARCO_1]),
        {
            "lista": "",
            "chave": "post-direto-convocar",
            "inscricao": str(cenario["inscricoes"][0].id),
        },
    )

    assert Convocacao.objects.count() == antes


def test_o_gesto_apurar_da_conducao_poe_os_recortes_entre_os_impedidos(cenario):
    edital = cenario["edital"]
    conteudo = effective_version(edital_id=edital.id).content
    perfil = conteudo["profiles"][0]
    marco = next(m for m in perfil["classificationMilestones"] if str(m["id"]) == m900.MARCO_1)

    itens = conducao_do_marco.alcance(edital, conteudo, perfil, marco, conducao_do_marco.APURAR)

    assert itens
    assert {item["situacao"] for item in itens} == {conducao_do_marco.IMPEDIDO}
    assert all(FRASE in item["razao"] for item in itens)


def test_a_convocacao_do_marco_intermediario_nao_lista_a_fila(client, cenario):
    """Revisão do PR #432: a fila, com "próxima da fila", contradizia o aviso do topo."""
    corpo = _abrir(client, "interface:convocacao", cenario["edital"], m900.MARCO_1)

    assert 'id="fila"' not in corpo
    assert 'id="regularizar"' not in corpo
