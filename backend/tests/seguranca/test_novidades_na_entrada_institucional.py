"""As Novidades pela entrada institucional e pela troca de unidade (168, FR-7411, FR-7415, FR-7417).

O seletor de demonstração não percorre estes dois caminhos: só a entrada pelo provedor cria a pessoa
`pessoa-<uuid>` e permite trocar de unidade. São eles que provam que a contagem nasce na camada de
identidade, e não numa view da demonstração.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.novidades import leitura
from processo_seletivo.novidades.models import LeituraDasNovidades
from tests.interface.test_novidades import TRES, notas  # noqa: F401 — a fixture do arquivo do caso
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = pytest.mark.django_db

SO_DO_GESTOR = (
    '[[nota]]\nid = "vg"\ndata = 2026-10-01\ncategoria = "novidade"\nrelevancia = "relevante"\n'
    'titulo = "Título vg"\nresumo = "R."\nprs = [9]\nspecs = []\n'
    'para_capacidade = "visao:consultar"\n'
)


def _contagem(client):
    barra = client.get(reverse("interface:lista")).content.decode()
    achado = re.search(r'contagem-de-novidades"><span aria-hidden="true">([^<]+)<', barra)
    return achado.group(1) if achado else None


def test_a_entrada_institucional_conta_pela_pessoa(client, provedor, notas):  # noqa: F811
    """A identidade é `pessoa-<uuid>`, e a contagem nasce na entrada, sem a view da demonstração."""
    notas(*TRES)
    paula = pessoa("paula-novidades")
    vincular(paula, "cefor", "gestor")
    entrar(client, "paula-novidades")

    assert client.session[leitura.NAO_VISTAS] == ["c", "b", "a"]
    assert _contagem(client) == "3"
    client.get(reverse("interface:novidades"))
    assert LeituraDasNovidades.objects.get(subject=paula.username).vistas == ["a", "b", "c"]
    assert _contagem(client) is None


def test_trocar_de_unidade_reconta_e_o_bloco_da_visita_continua(
    client,
    provedor,
    campus_a,
    notas,  # noqa: F811
):
    """Na outra unidade a pessoa tem outras capacidades: a nota do Gestor passa a contar, e o que
    chegou desde a última visita continua no topo, com ela acrescentada."""
    notas(*TRES, SO_DO_GESTOR)
    paula = pessoa("paula-troca")
    vincular(paula, "campus-a", "elaborador")
    vincular(paula, "cefor", "gestor")
    LeituraDasNovidades.objects.create(
        subject=paula.username, vistas=["a"], ultima_visita=timezone.now()
    )
    entrar(client, "paula-troca")  # entra em campus-a, a primeira em ordem de código
    assert _contagem(client) == "2"

    bloco = client.get(reverse("interface:novidades")).content.decode()
    assert "Título vg" not in bloco

    assert client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"}).status_code == 302
    assert _contagem(client) == "1"

    corpo = client.get(reverse("interface:novidades")).content.decode()
    topo = corpo.split('class="desde-a-ultima-visita"')[1].split("</section>")[0]
    assert re.findall(r'#(\w+)">Título', topo) == ["c", "b", "vg"]
