"""A reabilitação por recurso aparece **nomeada** nas telas da operação.

Mostrar sem explicar transformaria a reabilitação em erro aparente: quem vê alguém eliminada
reaparecer habilitada precisa saber que houve deferimento, qual recurso e quando — e a data é a da
decisão, que é por onde se procura (FR-077).

E a tela do marco diz a causa da obsolescência em vez de "algo mudou": sem a causa, quem lê sai
procurando o quê (FR-078).
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.domain.universo import REINGRESSO, SUPERACAO
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.conftest import ator_institucional
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def deferida(gestor, api_client, manager_headers, process_payload):
    """Eliminada na Etapa 1, com a Etapa 2 encerrada e o ato final **já emitido** — e só então
    reabilitada por deferimento.

    A ordem é o que torna o caso real: quando o recurso é deferido, quem organizou a Etapa seguinte
    já a deu por encerrada e já emitiu o ato do marco. É esse ato que a reabilitação torna obsoleto.
    """
    from tests.fixtures.divulgacao import emitir
    from tests.fixtures.mesa import concluir_como, distribuir_para

    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=122,
        codigo="0822",
        pontuacoes=("55.0000", "90.0000"),
        na_primeira_etapa=True,
    )
    cenario = peca["cenario"]
    outra = cenario["inscricoes"][1]
    contexto = {**cenario, "etapa": cenario["segunda"]}
    distribuir_para(contexto, _gestor(), ["joao"], [outra], chave="lote-0822-segunda")
    concluir_como(contexto, "joao", outra, pontuacao="80.0000")
    _consolidar(cenario, cenario["segunda"], [outra], chave="consolidar-0822-segunda")
    cenario["ato_final"] = emitir(cenario, _gestor(), chave="emitir-0822-final")

    decisao, sucessor = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A análise documental não considerou o diploma juntado.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-reabilitacao",
    )
    return {**peca, "decisao": decisao, "sucessor": sucessor}


def conteudo(resposta):
    corpo = resposta.content.decode()
    achado = re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL)
    return achado.group(1) if achado else corpo


def test_a_mesa_nomeia_a_linha_reaberta(client, seletor_ligado, deferida):
    """Sem o aviso, ela entraria na lista como mais uma pendente."""
    identificar(client, "carlos", ["gestor"])
    cenario = deferida["cenario"]

    corpo = conteudo(
        client.get(
            reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["segunda"]])
        )
    )

    assert "Reabilitada por recurso" in corpo
    assert deferida["recurso"].protocolo in corpo


def test_o_painel_da_etapa_nomeia_a_linha_reaberta(client, seletor_ligado, deferida):
    identificar(client, "carlos", ["gestor"])
    cenario = deferida["cenario"]

    corpo = conteudo(
        client.get(
            reverse(
                "interface:resultados-da-etapa",
                args=[cenario["edital"].id, cenario["etapa_do_recurso"]],
            )
        )
    )

    assert "Reabilitada por recurso" in corpo
    assert deferida["recurso"].protocolo in corpo


def test_sem_reabilitacao_a_tela_nao_avisa_nada(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """O aviso que aparece sempre é o aviso que ninguém lê."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=123, codigo="0823"
    )
    identificar(client, "carlos", ["gestor"])
    cenario = peca["cenario"]

    corpo = conteudo(
        client.get(reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["etapa"]]))
    )

    assert "Reabilitada por recurso" not in corpo


def test_a_tela_do_marco_diz_a_causa_da_divergencia(client, seletor_ligado, deferida):
    """`participante reingressou` — e não "o conjunto de participantes mudou" (FR-078).

    Aqui a reabilitação acontece na Etapa 1 e o marco final enumera a Etapa 2: quem voltou passa a
    **participar** do marco, e é essa a divergência que a tela precisa nomear.
    """
    cenario = deferida["cenario"]

    identificar(client, "carlos", ["gestor"])
    corpo = conteudo(
        client.get(reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]]))
    )

    assert REINGRESSO in corpo or SUPERACAO in corpo


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


def _consolidar(cenario, etapa_id, inscricoes, *, chave):
    from processo_seletivo.resultados.application.consolidacao import consolidar

    return consolidar(
        actor=_gestor(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa_id,
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=chave,
        correlation_id="reabilitacao",
    )
