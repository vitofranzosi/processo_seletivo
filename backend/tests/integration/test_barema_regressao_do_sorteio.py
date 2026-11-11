"""O Edital de sorteio não é tocado pelo barema (146, T024, FR-5231, SC-1624).

Ele não tem Etapa avaliada pela Mesa, e o que muda no conteúdo publicado é só a lista vazia que o
degrau 21 escreve em cada Etapa. A Mesa sem barema está em `interface/test_mesa_com_barema.py`, e
o PDF sem barema em `interface/test_barema_no_pdf.py`.
"""

import pytest

from processo_seletivo.avaliacoes.domain.barema import tem_barema
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.sorteio import certame_de_sorteio

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_o_edital_de_sorteio_publica_so_a_lista_vazia(
    gestor, api_client, manager_headers, process_payload
):
    certame = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)

    etapas = effective_version(edital_id=certame["edital"].id).content["stages"]

    assert etapas
    assert all(etapa["criteria"] == [] for etapa in etapas)
    assert not any(tem_barema(etapa) for etapa in etapas)
