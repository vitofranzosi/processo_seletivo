"""A jornada demonstrável da 015: conferir, emitir, auditar e enxergar obsolescência."""

import re

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000471"


def test_percurso_inteiro_da_ordem(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    client,
    seletor_ligado,
):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="aceitacao-015",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": etapa["id"],
    }
    inscricoes = inscrever(edital, 3, primeiro=701)
    distribuir_para(contexto, gestor, ["joao"], inscricoes[:2], chave="aceitacao-lote-015")
    concluir_como(contexto, "joao", inscricoes[0], pontuacao="70.0000")
    concluir_como(contexto, "joao", inscricoes[1], pontuacao="90.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[item.id for item in inscricoes[:2]],
        idempotency_key="aceitacao-consolidar-015",
        correlation_id="aceitacao-015",
    )
    identificar(client, "maria", ["gestor"])

    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert reverse("interface:ordenacao", args=[edital.id, MARCO]) in detalhe

    url = reverse("interface:ordenacao", args=[edital.id, MARCO])
    calculada = client.get(url)
    assert calculada.status_code == 200
    assert AtoDeOrdenacao.objects.count() == 0
    confirmacao = re.search(
        r'name="confirmacao_do_calculo" value="([^"]+)"', calculada.content.decode()
    ).group(1)
    emitida = client.post(
        reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]),
        {"chave_idempotencia": "aceitacao-emissao-015", "confirmacao_do_calculo": confirmacao},
    )
    assert emitida.status_code == 302
    ato = AtoDeOrdenacao.objects.get()

    consulta = client.get(reverse("interface:ato-de-ordenacao", args=[edital.id, MARCO, ato.id]))
    corpo_do_ato = consulta.content.decode()
    assert consulta.status_code == 200
    assert "Proveniência do ato" in corpo_do_ato
    assert str(ato.versao_id) in corpo_do_ato

    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[inscricoes[2].id],
        motivo="Não compareceu à Etapa.",
        idempotency_key="aceitacao-tardio-015",
        correlation_id="aceitacao-015",
    )
    obsoleta = client.get(url).content.decode()
    assert "está obsoleto" in obsoleta
    assert "Resultados oficiais do universo mudaram" in obsoleta
