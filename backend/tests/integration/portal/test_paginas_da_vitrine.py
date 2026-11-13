"""O histórico em páginas, na página (ver `tests/unit/portal/test_paginas_da_vitrine.py`).

Três seleções publicadas com o prazo aberto e lidas trinta dias depois: é como uma seleção encerra
de verdade — o tempo passa —, sem Retificação nenhuma. O tamanho da página encolhe para dois, para
que três seleções já sejam mais de uma página.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.portal import leitura
from tests.integration.portal.test_consulta_da_vitrine import lista, publicar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Os dias de prazo de cada uma, na ordem em que são publicadas: a do meio fecha por último.
PRAZOS = {1: 3, 2: 9, 3: 6}


@pytest.fixture
def catalogo(api_client, manager_headers, process_payload, monkeypatch):
    monkeypatch.setattr(leitura, "POR_PAGINA", 2)
    agora = timezone.now()
    for numero, prazo in PRAZOS.items():

        def ajustar(rascunho, prazo=prazo, numero=numero):
            rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=prazo)).isoformat()
            rascunho["profiles"][0]["name"] = f"Cargo {numero}"

        publicar(
            api_client,
            manager_headers,
            process_payload,
            numero=numero,
            seed=numero,
            ajustar=ajustar,
        )
    return agora


@pytest.fixture
def um_mes_depois(catalogo, monkeypatch):
    depois = catalogo + timedelta(days=30)
    monkeypatch.setattr(timezone, "now", lambda: depois)


def ver(client, **parametros):
    return client.get(reverse("portal:vitrine"), parametros).content.decode()


def cargos(corpo):
    return re.findall(r"Cargo \d", lista(corpo))


def test_o_que_fechou_as_inscricoes_esta_em_andamento_e_em_paginas(client, um_mes_depois):
    """Nenhum dos três foi encerrado por ato: fecharam as inscrições, e seguem."""
    primeira = ver(client)
    segunda = ver(client, pagina="2")

    assert '<h2 class="secao-vitrine">Em andamento</h2>' in primeira
    assert "Seleções encerradas" not in primeira and "Edital encerrado" not in primeira
    assert lista(primeira).count(">Em andamento</p>") == 2
    # Sem nada publicado, o que fechou as inscrições por último vem primeiro.
    assert cargos(primeira) == ["Cargo 2", "Cargo 3"]
    assert cargos(segunda) == ["Cargo 1"]
    assert "Mostrando 1–2 de 3 seleções em andamento ou encerradas" in primeira
    assert "Mostrando 3 de 3 seleções em andamento ou encerradas" in segunda
    assert 'href="/selecoes/?pagina=2#fora-do-prazo" rel="next"' in primeira
    assert 'href="/selecoes/#fora-do-prazo" rel="prev"' in segunda
    assert 'aria-current="page">Página 2 de 2<' in segunda
    assert 'rel="next"' not in segunda


def test_em_andamento_e_encerradas_sao_uma_sequencia_so(client, um_mes_depois):
    """A frase antes do primeiro grupo visível, a navegação depois do último — e o grupo sem
    cartão na página não aparece. O "Cargo 2", que viria primeiro em andamento, foi encerrado por
    ato: vai para o histórico, depois dos dois que seguem."""
    from processo_seletivo.processos.models import Edital
    from tests.integration.portal.test_desfecho_publico import encerrar

    encerrar(Edital.objects.get(number="82"))

    primeira = ver(client)
    segunda = ver(client, pagina="2")

    assert cargos(primeira) == ["Cargo 3", "Cargo 1"]
    assert '<h2 class="secao-vitrine">Em andamento</h2>' in primeira
    assert '<h2 class="secao-vitrine">Seleções encerradas</h2>' not in primeira
    assert primeira.count('class="paginacao"') == 1

    assert cargos(segunda) == ["Cargo 2"]
    assert '<h2 class="secao-vitrine">Em andamento</h2>' not in segunda
    assert segunda.index("Seleções encerradas</h2>") < segunda.index('id="fora-do-prazo"')
    assert "Mostrando 3 de 3 seleções em andamento ou encerradas" in segunda
    assert "Edital encerrado" in lista(segunda)
    assert segunda.count('class="paginacao"') == 1


def test_as_abertas_ficam_inteiras_e_sem_navegacao(client, catalogo):
    """Só o histórico se folheia: três abertas num tamanho de página de dois continuam três."""
    corpo = ver(client, pagina="2")

    assert sorted(cargos(corpo)) == ["Cargo 1", "Cargo 2", "Cargo 3"]
    assert 'class="paginacao"' not in corpo


def test_com_filtro_a_lista_unica_se_reparte_e_o_filtro_segue(client, um_mes_depois):
    corpo = ver(client, situacao="em-andamento", pagina="2")

    assert cargos(corpo) == ["Cargo 1"]
    assert "<strong>3</strong>" in corpo and "Mostrando 3." in corpo
    assert 'href="/selecoes/?situacao=em-andamento#resultado" rel="prev"' in corpo
    # O cartão leva a página junto: a volta da seleção cai onde a pessoa estava.
    assert "?situacao=em-andamento&amp;pagina=2" in lista(corpo)


def test_a_pagina_alem_da_ultima_mostra_a_ultima_e_o_cartao_diz_qual(client, um_mes_depois):
    corpo = ver(client, pagina="99")

    assert cargos(corpo) == ["Cargo 1"]
    assert '/?pagina=2"' in lista(corpo) and "pagina=99" not in corpo


def test_busca_sem_resultado_nao_tem_paginas(client, um_mes_depois):
    corpo = ver(client, busca="inexistente", pagina="2")

    assert "Nenhuma seleção encontrada" in corpo
    assert 'class="paginacao"' not in corpo
