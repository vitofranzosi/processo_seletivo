"""Cada linha de "Minhas atividades" é uma célula SUA do Centro (160, SC-2271, FR-6859, FR-6860).

**A página não tem regra própria** (D-005 da `160`). Se ela divergir do "O que fazer agora" do
Edital, é ela que está errada — e é este arquivo que diz qual linha. Três sentidos:

- toda linha da página é uma providência que o Centro daquele Edital marca como sua, com o mesmo ato
  e o mesmo link;
- toda providência sua do Centro cuja base é a presidência ou a alocação, fora das famílias que a
  nota de cobertura nomeia, está na página;
- o GET de cada link, com a identidade da pessoa, mostra o controle do ato (o SC-1230 da `127`).

A avaliação é conferida pela Etapa e pelo link: o número é o da Mesa (D-010 da `160`).
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import atividades as at
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.interface.conftest import identificar
from tests.interface.test_andamento_coerencia import marcador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def abrir_a_pagina(client):
    resposta = client.get(reverse("interface:minhas-etapas"))
    assert resposta.status_code == 200
    return resposta.context["atividades"]


def suas_no_centro(client, edital):
    resposta = client.get(reverse("interface:pagina-anterior", args=[edital.id]))
    assert resposta.status_code == 200
    return [item for item in resposta.context["nivel_1"].itens if item.sua]


def linhas_da_pagina(atividades):
    return [linha for grupo in atividades.para_fazer for linha in grupo.linhas]


def conferir(client, editais, *, presididos, alguma=True):
    """Os três sentidos, para a identidade que está na sessão do `client`."""
    atividades = abrir_a_pagina(client)
    linhas = linhas_da_pagina(atividades)
    if alguma:
        assert linhas, "o cenário deveria ter ao menos uma atividade da pessoa"
    por_edital = {edital.id: suas_no_centro(client, edital) for edital in editais}

    for linha in linhas:
        item = linha.providencia
        centro = por_edital.get(linha.edital.id)
        assert centro is not None, f"'{item.ato}' veio de um Edital fora do cenário"
        if item.natureza == a.AVALIAR:
            assert any(c.natureza == a.AVALIAR and c.url == item.url for c in centro), item.ato
        else:
            assert any(c.ato == item.ato and c.url == item.url for c in centro), (
                f"'{item.ato}' está na página e não é sua no Centro do Edital"
            )
        tela = client.get(item.url)
        assert tela.status_code == 200, (item.ato, item.url, tela.status_code)
        assert marcador(item) in tela.content.decode(), (
            f"'{item.ato}' está na página, e {item.url} não oferece o ato"
        )

    na_pagina = {(li.edital.id, li.providencia.ato, li.providencia.url) for li in linhas}
    for edital in presididos:
        for item in por_edital[edital.id]:
            if item.responsavel not in at.RESPONSAVEIS_DA_PRESIDENCIA:
                continue
            if item.natureza in at.FORA_DA_PAGINA:
                continue
            assert (edital.id, item.ato, item.url) in na_pagina, (
                f"'{item.ato}' é sua no Centro e não está na página"
            )
    return atividades


@pytest.fixture
def base(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return gestor, api_client, manager_headers, process_payload


def test_s1_a_presidencia(client, base):
    certame = certame_s1(*base)
    identificar(client, "maria", [])
    atividades = conferir(client, [certame["edital"]], presididos=[certame["edital"]])
    assert all(grupo.base == at.PRESIDENCIA for grupo in atividades.para_fazer)


@pytest.mark.parametrize("subject", ["maria", "joao"], ids=["presidencia", "avaliador"])
def test_p1_a_presidencia_e_o_avaliador(client, base, subject):
    certame = certame_p1(*base)
    identificar(client, subject, [])
    presididos = [certame["edital"]] if subject == "maria" else []
    conferir(client, [certame["edital"]], presididos=presididos)


def test_a_convocacao_da_presidencia(client, base):
    edital, _, _ = montar_cenario_da_convocacao(*base, prefixo="coerencia-160-conv")
    identificar(client, "maria", [])
    atividades = conferir(client, [edital], presididos=[edital])
    assert any(grupo.providencia.natureza == a.CONVOCACAO for grupo in atividades.para_fazer)


def test_o_gestor_que_nao_preside_nao_tem_linha_de_conducao(client, base):
    """O Centro diz "sua" toda a condução ao Gestor; a página não a lê (D-002 da `160`)."""
    certame = certame_s1(*base)
    identificar(client, "carlos", ["gestor"])
    assert suas_no_centro(client, certame["edital"]), "o Centro deveria dizer sua ao Gestor"
    atividades = conferir(client, [certame["edital"]], presididos=[], alguma=False)
    assert atividades.para_fazer == []
    assert atividades.gestor
