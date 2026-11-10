"""O corte espera o prazo recursal, como recomendação, nas telas (133, FR-4542, FR-4544, FR-4545).

O CV-02 do estudo de convergência de 07/11/2026: com a preliminar publicada e o prazo aberto, o
cartão mandava "Emitir o corte". Agora o cartão diz que o corte espera, com a marca em texto, e a
tela do corte diz a consequência antes do botão — que continua lá, e o comando aceita.
"""

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import Corte
from tests.fixtures import marco_intermediario as m900
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(client, gestor, api_client, manager_headers, process_payload, seletor_ligado):
    cenario = m900.ate_a_preliminar_m1(
        m900.montar(gestor, api_client, manager_headers, process_payload)
    )
    identificar(client, "carlos", ["gestor"])
    return cenario


def test_o_cartao_mostra_o_corte_em_espera_com_a_marca_de_recomendacao(client, cenario):
    corpo = client.get(
        reverse("interface:pagina-anterior", args=[cenario["edital"].id])
    ).content.decode()
    cartao = corpo[corpo.index('id="acoes-titulo"') : corpo.index('id="participantes-titulo"')]

    assert 'class="marca-recomendacao"' in cartao
    assert "Emitir o corte" in cartao
    assert "obsoleto" in cartao


def test_a_tela_do_corte_diz_a_consequencia_antes_do_botao_e_o_botao_continua(client, cenario):
    edital = cenario["edital"]
    corpo = client.get(reverse("interface:corte", args=[edital.id, m900.MARCO_1])).content.decode()

    aviso = corpo.index("Recomendação: aguarde.")
    assert aviso < corpo.index('<button type="submit" class="botao">Emitir corte</button>')
    assert "obsoleto" in corpo


def test_emitir_o_corte_na_espera_continua_aceito(client, cenario):
    edital = cenario["edital"]
    m900._cortar(cenario, m900.MARCO_1)

    assert Corte.objects.filter(edital=edital, marco_id=m900.MARCO_1).count() == len(m900.LISTAS)
