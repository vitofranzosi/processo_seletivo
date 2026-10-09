"""O custo do aviso não cresce com o número de destinatários (066, `R-015`, SC-482).

**Uma consulta por pessoa é o modo de errar mais barato de escrever e mais caro de rodar.** Um aviso
de mil pessoas que perguntasse o endereço, o estado ou a tentativa de cada uma pagaria mil consultas
na prévia, outras mil na confirmação e mais mil no histórico. Os casos comparam o mesmo aviso com
poucos e com mil destinatários: o número de consultas tem de ser o mesmo.
"""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.avisos.application import destinatarios, selectors
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso
from processo_seletivo.divulgacao.models import SituacaoDivulgada
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.avisos import avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.performance, pytest.mark.django_db]


def _engordar(publicacao, quantos):
    """Mil inscrições consideradas na publicação, gravadas em lote: o cenário que a fixture não faz.

    São linhas novas, e não alterações: a `SituacaoDivulgada` é append-only, e acrescentar a ela é o
    que a publicação faz.
    """
    agora = timezone.now()
    inscricoes = Inscricao.objects.bulk_create(
        Inscricao(
            identity_subject=f"cand:orcamento-{indice}",
            edital=publicacao.edital,
            profile_id=publicacao.perfil_id,
            nome=f"Pessoa {indice}",
            email=f"pessoa{indice}@exemplo.test",
            protocolo=f"ORC-{indice:05d}",
            created_at=agora,
        )
        for indice in range(quantos)
    )
    SituacaoDivulgada.objects.bulk_create(
        SituacaoDivulgada(
            publicacao=publicacao,
            inscricao=inscricao,
            situacao=SituacaoDivulgada.Situacao.CLASSIFICADA,
            posicao=100 + indice,
        )
        for indice, inscricao in enumerate(inscricoes)
    )


def _cenario(gestor, api_client, manager_headers, process_payload, *, seed, codigo, primeiro):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        primeiro=primeiro,
        pontuacoes=("90.0000", "70.0000"),
    )
    cenario["publicacao"] = publicar_o_ato(cenario, chave=f"publicar-orcamento-{seed}")
    return cenario


def _consultas(funcao):
    with CaptureQueriesContext(connection) as capturadas:
        funcao()
    return len(capturadas.captured_queries)


@pytest.fixture
def pequeno_e_grande(gestor, api_client, manager_headers, process_payload):
    pequeno = _cenario(
        gestor, api_client, manager_headers, process_payload, seed=0, codigo="0661", primeiro=701
    )
    grande = _cenario(
        gestor, api_client, manager_headers, process_payload, seed=1, codigo="0662", primeiro=801
    )
    _engordar(grande["publicacao"], 1000)
    return pequeno, grande


def test_a_previa_nao_cresce_com_os_destinatarios(pequeno_e_grande):
    pequeno, grande = pequeno_e_grande

    def previa(cenario):
        return lambda: destinatarios.universo_do_resultado(
            edital=cenario["edital"],
            marco_id=cenario["publicacao"].marco_id,
            natureza=nomes.PRELIMINAR,
        )

    assert _consultas(previa(pequeno)) == _consultas(previa(grande))


def test_a_confirmacao_nao_cresce_e_responde_em_menos_de_dois_segundos(pequeno_e_grande):
    """SC-482: a confirmação grava em lote e não envia — mil pessoas não a tornam lenta."""
    pequeno, grande = pequeno_e_grande

    consultas_pequeno = _consultas(
        lambda: avisar_resultado(pequeno["edital"], pequeno["publicacao"].marco_id, chave="p")
    )
    inicio = time.perf_counter()
    consultas_grande = _consultas(
        lambda: avisar_resultado(grande["edital"], grande["publicacao"].marco_id, chave="g")
    )
    duracao = time.perf_counter() - inicio

    assert consultas_pequeno == consultas_grande
    assert duracao < 2.0, f"confirmar mil destinatários levou {duracao:.2f}s"
    assert Aviso.objects.get(idempotency_key="g").destinatarios.count() == 1002


def test_o_historico_nao_cresce_com_os_destinatarios(pequeno_e_grande):
    pequeno, grande = pequeno_e_grande
    avisar_resultado(pequeno["edital"], pequeno["publicacao"].marco_id, chave="p")
    avisar_resultado(grande["edital"], grande["publicacao"].marco_id, chave="g")
    agora = timezone.now()

    def historico(chave):
        aviso = Aviso.objects.get(idempotency_key=chave)
        return lambda: selectors.historico(aviso, agora=agora)

    assert _consultas(historico("p")) == _consultas(historico("g"))
