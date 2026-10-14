"""A linha de log de cada troca: o necessário ao diagnóstico, e nunca texto (071, `FR-1508`)."""

import json
import uuid

import pytest
from django.utils import timezone

from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain.estruturas_do_piloto import TELA
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, log_do_projeto, saida  # noqa: F401
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PERGUNTA = "Quantas vagas tem o polo de Bom Jesus do Norte, por favor?"


def test_a_linha_tem_os_campos_e_nenhum_texto(
    api_client,
    porta_falsa,
    contador_falso,
    log_do_projeto,  # noqa: F811
):
    contador_falso()
    edital, _ = publicar_do_corpus(api_client, "91", chave="log91")

    def responder(mensagens):
        total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
        return devolucao(
            saida("RESPONDIDA", ("dado", "Resposta que não vai ao log: 45.", [total["id"]]))
        )

    porta_falsa(responder)
    perguntar(
        edital_id=edital.id,
        conversa=str(uuid.uuid4()),
        pergunta=PERGUNTA,
        instante=timezone.now(),
        origem=TELA,
    )

    linhas = [
        linha.removeprefix("processo_seletivo.duvidas.piloto ")
        for linha in log_do_projeto
        if linha.startswith("processo_seletivo.duvidas.piloto troca_do_piloto")
    ]
    assert len(linhas) == 1
    campos = json.loads(linhas[0].removeprefix("troca_do_piloto "))
    assert set(campos) == {
        "acima_do_medido",
        "correlacao",
        "custo",
        "edital",
        "estado",
        "modelo",
        "motivos",
        "origem",
        "segundos",
        "servico",
        "tipo",
        "tokens_informados",
        "tokens_medidos",
        "versao",
    }
    assert "Bom Jesus" not in "\n".join(log_do_projeto)
    assert "Resposta que não vai ao log" not in "\n".join(log_do_projeto)
    assert "Caberá recurso" not in "\n".join(log_do_projeto), "nenhuma fonte no log"
