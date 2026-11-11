"""O que a página do Processo da 147 acrescenta em consultas, e que isso não cresce (SC-1663).

A página já lia o pulso, os sinais, os atos e os Editais pendentes — e isso cresce com os Editais,
como antes. O que a 147 acrescenta é `pagina_do_processo.compor`: as Retificações em curso (uma
consulta) e a faixa da 104. **É ela que se mede aqui**, com 1 e com 8 Editais, para cada papel cuja
faixa consulta: o número precisa ser o mesmo.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import pagina_do_processo
from processo_seletivo.processos.application.commands import add_edital
from tests.conftest import ator_institucional
from tests.interface.conftest import edital, identificar  # noqa: F401 — fixture

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

#: O teto das consultas de `compor`: as Retificações e o que a faixa lê para estes papéis.
TETO = 3


@pytest.fixture
def medido(monkeypatch):
    """Envolve `compor` e guarda quantas consultas cada chamada fez."""
    contagens = []
    original = pagina_do_processo.compor

    def medir(**argumentos):
        with CaptureQueriesContext(connection) as consultas:
            resultado = original(**argumentos)
        contagens.append(len(consultas))
        return resultado

    monkeypatch.setattr(pagina_do_processo, "compor", medir)
    return contagens


def acrescentar(processo, quantos):
    gestao = ator_institucional("gestao.orcamento", "edital:criar")
    for indice in range(quantos):
        add_edital(
            actor=gestao,
            processo_id=processo.id,
            data={"number": f"{60 + indice}", "year": 2026, "title": f"Acrescido {indice}"},
            idempotency_key=f"orcamento-147-{indice}-000000",
            correlation_id="orcamento-147",
        )


@pytest.mark.parametrize(
    ("subject", "papeis"),
    [
        ("marcia.gestora", ["gestor"]),
        ("ana.elaboradora", ["elaborador"]),
        ("bruno.homologador", ["homologador"]),
        ("paula.publicadora", ["publicador"]),
        ("ana.julgadora", ["julgador"]),
    ],
)
def test_a_composicao_custa_o_mesmo_com_1_e_com_8_editais(
    client,
    seletor_ligado,
    edital,  # noqa: F811
    medido,
    subject,
    papeis,
):
    identificar(client, subject, papeis)
    url = reverse("interface:processo-detalhe", args=[edital.processo.id])

    assert client.get(url).status_code == 200
    acrescentar(edital.processo, 7)
    assert client.get(url).status_code == 200

    um, oito = medido
    assert um == oito, f"{subject}: {um} consultas com 1 Edital, {oito} com 8"
    assert oito <= TETO, f"{subject}: {oito} consultas"
