"""A prévia mede o fecho pelas autoridades vigentes da unidade, e não as imprime (096, FR-2420).

A autoridade é escolhida no ato, entre as vigentes, e a prévia não a conhece. Ela recebe as mesmas
que a tela de publicação oferece, mede o fecho de cada uma e reserva o mais alto (D-012, D-013).
"""

from datetime import date, timedelta

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.contexto_do_ato import fechos_previstos
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import registrar_autoridade
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

HOJE = date(2026, 10, 21)


def test_as_previstas_sao_as_vigentes_na_data():
    cefor = Unidade.objects.get(codigo="cefor")
    registrar_autoridade(cefor, cargo="Encerrada", fim=HOJE - timedelta(days=1))
    registrar_autoridade(cefor, cargo="Futura", inicio=HOJE + timedelta(days=1))
    registrar_autoridade(
        cefor, cargo="Vigente", nome="Nome Vigente", ato_de_nomeacao="Portaria nº 9"
    )

    previstas = fechos_previstos(cefor, HOJE)
    cargos = {prevista.cargo for prevista in previstas}

    assert "Vigente" in cargos
    assert not cargos & {"Encerrada", "Futura"}
    assert all(isinstance(prevista, pdf.AutoridadeSignataria) for prevista in previstas)
    vigente = next(prevista for prevista in previstas if prevista.cargo == "Vigente")
    assert (vigente.nome, vigente.ato_de_nomeacao) == ("Nome Vigente", "Portaria nº 9")


def test_a_tela_da_previa_mede_pelas_vigentes_e_nao_as_imprime(
    client, seletor_ligado, api_client, manager_headers, process_payload, monkeypatch
):
    from tests.interface.conftest import identificar

    cefor = Unidade.objects.get(codigo="cefor")
    registrar_autoridade(
        cefor, cargo="Cargo Que Não Sai", nome="Nome Que Não Sai", ato_de_nomeacao="Ato Que Não Sai"
    )
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    medidas = []
    original = pdf._reservar_o_fecho

    def registrando(composicao, medir, previstos):
        medidas.append(previstos)
        return original(composicao, medir, previstos)

    monkeypatch.setattr(pdf, "_reservar_o_fecho", registrando)
    identificar(client, "auditor", ["auditor"])

    resposta = client.get(reverse("interface:previa-documento", args=[edital.id]))

    assert resposta.status_code == 200
    assert medidas, "a prévia reservou o fecho"
    assert "Nome Que Não Sai" in {prevista.nome for prevista in medidas[-1]}
    texto = texto_de(resposta.content)
    assert pdf.FECHO_NA_PUBLICACAO in texto
    for impresso in ("Nome Que Não Sai", "Cargo Que Não Sai", "Ato Que Não Sai"):
        assert impresso not in texto
