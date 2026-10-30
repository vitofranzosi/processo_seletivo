"""O que o `speckit-converge` da 103 achou faltando: o desfazer pela tela e o custo por Edital.

Ficam num arquivo à parte porque precisam de outro Edital de partida — com Anexo, para que haja o
que remover — e de mais de um Edital, para medir a Lista.
"""

from uuid import uuid4

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import atos_retificacao
from processo_seletivo.publicacoes.application.retificacoes import alteracoes_declaradas
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.publicacao import publish_original
from tests.interface.test_auditoria_passagem_da_retificacao import (
    LINHA_GERAL,
    VAGAS,
    compor,
    sessao,
)
from tests.interface.test_jornada_da_retificacao import abrir_edicao, campos_da_edicao

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("seletor_ligado"),
]


@pytest.fixture
def com_anexo(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload, anexos=1)
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_a_remocao_declarada_se_desfaz_pela_edicao(com_anexo):
    """FR-2719: a entidade removida não está no proposto, e o caminho de volta é a lista."""
    edital, vigente = com_anexo
    ana = sessao("ana.elaboradora", ["elaborador"])
    url = reverse("interface:retificar", args=[edital.id])
    tela = ana.get(url)
    anexo = next(g for g in tela.context["grupos"] if g["caminho"].startswith("/attachments/id="))
    campos = {
        f"campo:{c['referencia']}": c["valor"] for g in tela.context["grupos"] for c in g["campos"]
    }
    referencia = {
        c["caminho"]: c["referencia"] for g in tela.context["grupos"] for c in g["campos"]
    }
    resposta = ana.post(
        url,
        campos
        | {
            f"campo:{referencia[VAGAS]}": "9",
            f"campo:{referencia[LINHA_GERAL]}": "9",
            f"remover:{anexo['referencia']}": "1",
            "base": str(vigente.id),
            "justificativa": "Vagas e anexo",
            "chave_idempotencia": tela.context["chave_idempotencia"],
            "confirmar": "1",
        },
    )
    assert resposta.status_code == 302, (resposta.context or {}).get("erros")
    retificacao = Retificacao.objects.get(edital=edital)
    assert [a["operation"] for a in alteracoes_declaradas(retificacao)].count("REMOVE") == 1

    edicao_url, edicao = abrir_edicao(ana, retificacao)
    remocoes = edicao.context["edicao"]["remocoes"]
    assert len(remocoes) == 1
    assert f"Desfazer a remoção de {remocoes[0]['descricao']}" in edicao.content.decode()
    resposta = ana.post(
        edicao_url,
        campos_da_edicao(edicao)
        | {"desfazer-remocao": str(remocoes[0]["indice"]), "confirmar": "1"},
    )

    assert resposta.status_code == 302, (resposta.context or {}).get("erros")
    declaradas = alteracoes_declaradas(retificacao)
    assert "REMOVE" not in [a["operation"] for a in declaradas]
    assert {a["targetPath"] for a in declaradas} >= {VAGAS, LINHA_GERAL}


def test_as_retificacoes_em_curso_de_varios_editais_sao_uma_consulta(com_anexo):
    """SC-974, na parte que é da 103: a leitura não cresce com o número de Editais.

    A Lista já tinha custo por linha antes da 103 — as ações de cada Edital contam inscrições e
    recursos —, e por isso o critério se mede na leitura que a 103 acrescentou, e não na página. Os
    dois Editais a mais são identificadores sem Retificação: a pergunta é se a consulta é uma para
    N Editais, e o número de linhas devolvidas não muda o número de consultas.
    """
    edital, vigente = com_anexo
    ana = sessao("ana.elaboradora", ["elaborador"])
    compor(ana, edital, vigente, vagas="9")
    compor(ana, edital, vigente, vagas="8")
    ator = Actor("bruno.homologador", "cefor", frozenset({"retificacao:homologar"}))

    with CaptureQueriesContext(connection) as um:
        atos_retificacao.em_curso_por_edital([edital.id], ator)
    with CaptureQueriesContext(connection) as tres:
        por_edital = atos_retificacao.em_curso_por_edital([edital.id, uuid4(), uuid4()], ator)

    assert len(um) == len(tres) == 1
    assert [len(itens) for itens in por_edital.values()] == [2]
