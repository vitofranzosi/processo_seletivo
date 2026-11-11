"""O documento diz ao candidato o que comprova no barema (146, T025, FR-5224).

"Títulos acadêmicos — Comprova: Diploma de Doutorado (até 20); …": é com isso que o candidato
decide o que juntar no arquivo único. Lido do barema publicado na versão que a inscrição vê; o
documento que não comprova critério nenhum continua como era.
"""

import pytest
from django.template.loader import render_to_string

from processo_seletivo.portal.views import _documentos
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.barema import montar_mesa_com_barema
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("raiz_de_arquivos")]

SEED = 149


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_mesa_com_barema(gestor, api_client, manager_headers, seed=SEED, codigo="P149")


def test_a_linha_do_documento_lista_os_criterios_e_as_maximas(cenario):
    inscricao = inscrever(cenario["edital"], 1, primeiro=4901)[0]
    conteudo = (
        VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at").content
    )

    documentos = _documentos(conteudo, inscricao)
    por_nome = {linha["nome"]: linha["comprova"] for linha in documentos["linhas"]}

    assert por_nome["Títulos acadêmicos"] == [
        "Diploma de Doutorado (até 20)",
        "Diploma de Mestrado (até 15)",
        "Especialização (até 10)",
        "Curso de formação de orientadores (até 15)",
    ]
    assert por_nome["Declaração de exercício de docência"] == [
        "Exercício de docência em EaD (até 40)"
    ]
    # O documento sem critério ligado continua como era.
    assert all(
        comprova == []
        for nome, comprova in por_nome.items()
        if nome not in ("Títulos acadêmicos", "Declaração de exercício de docência")
    )

    html = render_to_string(
        "portal/_documentos.html", {"documentos": documentos, "inscricao": inscricao}
    )
    assert "Comprova: Exercício de docência em EaD (até 40)." in html
    assert "Comprova: Diploma de Doutorado (até 20); Diploma de Mestrado (até 15);" in html
