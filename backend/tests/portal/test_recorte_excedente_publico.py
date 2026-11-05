"""O canal público do acervo excedente não muda (122, FR-3905, FR-3915; SC-1170; D-005).

A verificação pública confirma que o registro é o que foi publicado, e não o qualifica: a
explicação "fora da operação atual" é devida a quem opera, e mora na gestão. O que se prova aqui é
que as quatro páginas continuam respondendo para o acervo, sem a marca da gestão. A igualdade byte a
byte com o estado anterior é garantida por construção — a `122` não toca `portal/` —, e a matriz
de rastreabilidade registra o `git diff` que o mostra.
"""

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.fixtures.recorte_excedente import LISTA_AC, certame_com_ac, divulgar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MARCA_DA_GESTAO = "fora da operação"


@pytest.fixture
def acervo(gestor, api_client, manager_headers, process_payload):
    certame = certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="pub"
    )
    divulgar(certame, LISTA_AC, chave="divulgar-ac-publico", recusa_desligada=True)
    return certame


def _paginas(certame):
    filtro = {"edital": certame["edital"], "lista_id": LISTA_AC}
    relacao = RelacaoDeHabilitados.objects.get(**filtro)
    sorteio = Sorteio.objects.get(**filtro)
    publicacao = PublicacaoResultado.objects.get(**filtro)
    return {
        "relacao": reverse("portal:relacao-de-habilitados", args=[relacao.id]),
        "sorteio": reverse("portal:verificar-sorteio", args=[sorteio.id]),
        "resultado": reverse("portal:resultado", args=[publicacao.id]),
        "selecao": reverse("portal:selecao", args=[certame["edital"].id]),
    }


@pytest.mark.parametrize("pagina", ["relacao", "sorteio", "resultado", "selecao"])
def test_a_pagina_publica_do_acervo_responde_sem_a_marca_da_gestao(client, acervo, pagina):
    resposta = client.get(_paginas(acervo)[pagina])

    assert resposta.status_code == 200
    assert MARCA_DA_GESTAO not in resposta.content.decode().lower()
