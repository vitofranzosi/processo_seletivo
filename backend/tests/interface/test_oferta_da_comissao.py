"""A tela não oferece porta que o ator não abre.

O painel do Processo mostrava "Comissão" e "Alocação por Etapa" a qualquer identidade que
enxergasse o Processo, e as duas telas exigem **gerir** (011, FR-016): quem não gere clicava e
recebia um 404 sem explicação. A lista tinha o erro simétrico — oferecia as mesmas portas a
quem apenas integra a comissão. A oferta agora repete a decisão que a view de destino toma.
"""

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

COMISSAO = "Alocação por Etapa"


def detalhe(processo):
    return reverse("interface:processo-detalhe", args=[processo.id])


def test_quem_nao_gere_nao_recebe_a_oferta_no_painel(client, seletor_ligado, processo_a):
    """O elaborador enxerga o Processo e não gere a comissão: o link era um 404 anunciado."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(detalhe(processo_a)).content.decode()

    assert COMISSAO not in corpo
    assert reverse("interface:alocacoes", args=[processo_a.id]) not in corpo
    # E a recusa da rota permanece: esconder o link é conveniência, não fronteira (FR-002).
    assert client.get(reverse("interface:alocacoes", args=[processo_a.id])).status_code == 404


def test_o_gestor_continua_recebendo_a_oferta_no_painel(client, seletor_ligado, processo_a):
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(detalhe(processo_a)).content.decode()

    assert reverse("interface:alocacoes", args=[processo_a.id]) in corpo
    assert client.get(reverse("interface:alocacoes", args=[processo_a.id])).status_code == 200


def test_a_presidente_sem_papel_sistemico_recebe_a_oferta_no_painel(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """A base contextual da 011 vale aqui como vale na rota: presidir é gerir esta comissão."""
    identificar(client, "maria", [])

    corpo = client.get(detalhe(processo_a)).content.decode()

    assert reverse("interface:alocacoes", args=[processo_a.id]) in corpo


def test_quem_apenas_integra_a_comissao_nao_recebe_a_oferta_na_lista(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """Integrar não é gerir: os dois links da lista levavam João ao 404."""
    identificar(client, "joao", [])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Você integra a comissão" in corpo
    assert COMISSAO not in corpo
    assert reverse("interface:comissao", args=[processo_a.id]) not in corpo


def test_o_gestor_alcanca_a_comissao_pela_lista(client, seletor_ligado, processo_a):
    """A lista decidia por vínculo, e quem gere sem integrar não tinha rota nenhuma ali."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo
