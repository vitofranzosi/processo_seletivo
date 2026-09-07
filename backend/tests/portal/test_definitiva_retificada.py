"""A definitiva que corrige outra — apresentada pela **causa**, e sem natureza nova.

`DEFINITIVA_RETIFICADA` seria um terceiro valor no enum: três pares a decidir na regra de não
regressão, mais um valor em `uq_publicacao_por_ato_natureza`, e toda leitura de natureza mudando —
tudo para dizer o que a cadeia já diz. Vigência e natureza **derivam da cadeia**, e não de estado
duplicado (FR-087).

E a publicação vigente passa a dizer que é a vigente. Antes, só a sucedida dizia algo sobre a
cadeia: quem abria a vigente não tinha como saber se estava lendo o que vale ou um histórico — a
oportunidade nº 3 do relatório da E2E-017 (FR-090).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, publicar_o_ato
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def retificada(gestor, api_client, manager_headers, process_payload):
    """Uma providência determinada, cumprida por ato citante, e a definitiva publicada sobre ele."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=129, codigo="0829"
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato corrigindo o critério de desempate.",
        idempotency_key="providencia-retificada",
    )
    cenario = peca["cenario"]
    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-retificada",
        motivo="Cumprimento da decisão.",
        decisoes=[str(decisao.id)],
    )
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-retificada",
        ato=citante,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisao": decisao, "nova": nova}


def abrir(client, publicacao):
    resposta = client.get(reverse("portal:resultado", args=[publicacao.id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_a_natureza_continua_sendo_uma_das_duas(retificada):
    """Nenhum valor novo no enum — a causa é derivada, e não gravada (FR-087)."""
    assert retificada["nova"].natureza == "DEFINITIVA"
    assert set(PublicacaoResultado.objects.values_list("natureza", flat=True)) <= {
        "PRELIMINAR",
        "DEFINITIVA",
    }


def test_a_definitiva_que_corrige_e_apresentada_pela_causa(client, retificada):
    """ "Retificado em razão do julgamento do recurso X" — o fato, e não um rótulo (FR-088)."""
    corpo = abrir(client, retificada["nova"])

    assert "retificado em" in corpo.lower()
    assert retificada["recurso"].protocolo in corpo
    assert "DEFINITIVA_RETIFICADA" not in corpo


def test_a_vigente_diz_que_e_a_vigente(client, retificada):
    """Quem abre a vigente precisa saber que está lendo o que vale (FR-090)."""
    corpo = abrir(client, retificada["nova"])

    assert "Este é o resultado vigente deste marco." in corpo


def test_a_sucedida_continua_dizendo_que_foi_sucedida(client, retificada):
    """A cadeia responde nas duas pontas, e o endereço da sucedida continua respondendo."""
    corpo = abrir(client, retificada["publicacao"])

    assert "foi sucedido" in corpo
    assert "Este é o resultado vigente deste marco." not in corpo


def test_a_primeira_publicacao_do_marco_nao_diz_que_corrige(
    client, gestor, api_client, manager_headers, process_payload
):
    """Sem publicação anterior não há o que corrigir — e o aviso não pode aparecer sempre."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=130, codigo="0830"
    )

    corpo = abrir(client, peca["publicacao"])

    assert "retificado em" not in corpo.lower()
    assert "Este é o resultado vigente deste marco." in corpo


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")
