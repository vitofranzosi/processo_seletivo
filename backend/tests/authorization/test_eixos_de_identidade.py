"""T046a — os dois eixos de identidade não se contaminam (§32 da spec).

A 009 trouxe um canal com identidade e sessão próprias. A afirmação de que ser candidato não dá
acesso institucional — e que ser membro de comissão não dá ownership sobre inscrição — é
falsificável desde então, e é isto que a falsifica.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def sessao_de_candidato(client, settings):
    """Identidade do canal público, e nada mais."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    resposta = client.post(
        reverse("portal:identificar"),
        {"nome": "Maria Candidata", "cpf": "111.444.777-35", "email": "m@exemplo.br"},
    )
    assert resposta.status_code in (302, 200), resposta.content
    return client


def rotas_da_comissao(processo, edital, etapa_id):
    return [
        reverse("interface:comissao", args=[processo.id]),
        reverse("interface:alocacoes", args=[processo.id]),
        reverse("interface:auditoria-comissao", args=[processo.id]),
        reverse("interface:minhas-etapas"),
        reverse("interface:atribuicao", args=[edital.id, etapa_id]),
    ]


def test_sessao_de_candidato_nao_alcanca_as_rotas_da_comissao(
    sessao_de_candidato, seletor_ligado, processo_a, edital_a, etapa_a1, comissao_de_a
):
    """FR-061 e SC-012: identidade de candidato não concede autorização na 011."""
    for rota in rotas_da_comissao(processo_a, edital_a, etapa_a1):
        resposta = sessao_de_candidato.get(rota)
        assert resposta.status_code in (302, 404), f"{rota} devolveu {resposta.status_code}"
        if resposta.status_code == 302:
            # Redirecionar para identificar-se é o mesmo que não estar autenticado ali: a sessão
            # do portal não vale como identidade institucional.
            assert "identificar" in resposta["Location"]


def test_membro_da_comissao_nao_ganha_ownership_sobre_inscricao(
    gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """FR-062 e FR-081: ownership de candidato é do candidato, e não se empresta pela comissão."""
    from processo_seletivo.inscricoes.domain.titularidade import e_titular
    from processo_seletivo.inscricoes.models import Inscricao

    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    inscricao = Inscricao(identity_subject="cpf:99999999999", edital=edital_a)

    class IdentidadeDoMembro:
        subject = "joao"

    # Ser membro da comissão do Edital não torna ninguém titular de inscrição dele: os dois
    # eixos são chaveados por coisas diferentes e não se cruzam por coincidência de pessoa.
    assert e_titular(inscricao, IdentidadeDoMembro()) is False
