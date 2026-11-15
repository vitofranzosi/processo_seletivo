"""O cenário C18: a Etapa restrita em curso, para a equipe percorrer a orientação (171, US5).

FR-7333 a FR-7335; SC-2410. O teste confere os estados que o cenário promete — no Centro da
presidência, em Minhas atividades de quem avalia e no acompanhamento de quem a Etapa alcança —, pelo
comando de carga, como os outros cenários (FR-7334).
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import andamento as a
from processo_seletivo.processos.models import Edital
from processo_seletivo.treinamento import catalogo
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.conftest import ator_institucional
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.treinamento import carregar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def c18(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True
    saida = carregar("C18", autoridade=str(AUTORIDADE_DA_SUITE))
    assert "C18  CRIADO" in saida, saida
    manifesto = CenarioDeTreinamento.objects.get(codigo="C18")
    edital = Edital.objects.get(processo=manifesto.processo)
    inscricoes = list(Inscricao.objects.filter(edital=edital).order_by("submitted_at", "id"))
    return edital, inscricoes


def _da_verificacao(edital, ator):
    """As providências da Etapa restrita: o `onde` é o nome dela, que o cenário fixa."""
    return [p for p in a.do_edital(edital, ator).providencias if p.onde == k.NOME_DA_VERIFICACAO]


def test_o_centro_da_presidencia_tem_as_pendencias_da_etapa_restrita(c18):
    """FR-7333: avisar os quatro, distribuir o 01, os pareceres que faltam, consolidar o 04."""
    edital, _ = c18
    atos = {p.ato for p in _da_verificacao(edital, ator_institucional(k.PRESIDENCIA))}
    assert f"Avisar 4 inscrições sobre {k.NOME_DA_VERIFICACAO}" in atos
    assert "Distribuir 1 inscrição sem avaliador suficiente" in atos
    assert "Consolidar 1 inscrição pronta" in atos
    (avaliar,) = [
        p
        for p in _da_verificacao(edital, ator_institucional(k.PRESIDENCIA))
        if p.natureza == a.AVALIAR
    ]
    assert "; faltam 3 pareceres: " in avaliar.ato
    assert avaliar.ate is not None


def test_o_acompanhamento_de_quem_a_etapa_alcanca_e_de_quem_nao(c18, client):
    """SC-2410: o 01 vê o passo; o 05, na ampla, não vê."""
    _, inscricoes = c18
    primeiro, quinto = inscricoes[0], inscricoes[catalogo.NA_AMPLA_DO_C18 - 1]
    entrar_como_titular(client, primeiro)
    corpo = client.get(reverse("portal:acompanhamento", args=[primeiro.id])).content.decode()
    assert "Falta um passo seu" in corpo
    assert k.NOME_DA_VERIFICACAO in corpo
    entrar_como_titular(client, quinto)
    corpo = client.get(reverse("portal:acompanhamento", args=[quinto.id])).content.decode()
    assert "Falta um passo seu" not in corpo


def test_minhas_atividades_de_quem_avalia(c18, client):
    """FR-7326: a linha de avaliar com o prazo da Etapa."""
    identificar(client, k.AVALIACAO_2, [])
    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()
    assert "Avaliar 2 inscrições" in corpo
    assert " · até " in corpo
