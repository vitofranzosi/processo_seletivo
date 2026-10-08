"""A publicação de Resultado confere a autoridade como as do Edital (060, FR-1125 a FR-1128).

Os dois fluxos de Edital estão em `tests/interface/test_escolha_da_autoridade.py`, pela tela; aqui o
terceiro, pelo comando, e a corrida que só a trava da linha resolve — encerrar entre a tela e a
confirmação.
"""

import json
import threading
import time
from datetime import timedelta

import pytest
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
    publicar_resultado,
)
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.conftest import encerrar_conexoes_da_thread
from tests.fixtures.autoridades import registrar_autoridade, registrar_unidade
from tests.fixtures.divulgacao import ator_publicador, montar_ato_publicavel

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=66,
        codigo="0766",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1401,
    )


def _hoje():
    return timezone.now().astimezone(ZONA).date()


def _publicar(cenario, autoridade, chave="publicar-0766"):
    ato = cenario["ato"]
    return publicar_resultado(
        actor=ator_publicador(),
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        marco_id=cenario["marco"],
        ato_id=ato.id,
        natureza="PRELIMINAR",
        autoridade=str(autoridade),
        confirmacao_da_previa=assinatura_da_previa(
            ato=ato, publicacao_anterior=None, projecao=compor(ato)
        ),
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_o_resultado_congela_autoridade_ato_de_nomeacao_e_unidade(cenario):
    """FR-1128: a Publicação de Resultado passa a guardar o ato de nomeação, antes ausente."""
    autoridade = registrar_autoridade(
        Unidade.objects.get(codigo="cefor"),
        cargo="Diretora-Geral",
        nome="Maria Exemplo",
        ato_de_nomeacao="Portaria nº 3/2026",
    )

    publicacao = _publicar(cenario, autoridade.pk)

    assert (
        publicacao.signatario_id,
        publicacao.signatario_nome,
        publicacao.signatario_ato_de_nomeacao,
        publicacao.unidade_sigla,
    ) == (autoridade.pk, "Maria Exemplo", "Portaria nº 3/2026", "Cefor")
    cabecalho = json.loads(bytes(publicacao.conteudo_publico).decode())["cabecalho"]
    assert cabecalho["signatario_ato_de_nomeacao"] == "Portaria nº 3/2026"
    assert cabecalho["unidade"]["cabecalho"] == [
        "Centro de Referência em Formação",
        "e em Educação a Distância",
    ]


@pytest.mark.parametrize(
    "caso, codigo",
    [
        ("de outra unidade", "autoridade_indisponivel"),
        ("encerrada ontem", "autoridade_fora_de_vigencia"),
        ("vazia", "signatario_obrigatorio"),
    ],
)
def test_o_resultado_recusa_como_o_edital(cenario, caso, codigo):
    """FR-1125, FR-1126: a mesma regra nos três fluxos, e nada gravado na recusa."""
    escolhida = {
        "de outra unidade": lambda: registrar_autoridade(registrar_unidade("serra")).pk,
        # Gravada direto, e não pelo comando: o comando recusa o fim de ontem (FR-1120), e este
        # teste precisa do estado, e não do ato que o produziria.
        "encerrada ontem": lambda: registrar_autoridade(
            Unidade.objects.get(codigo="cefor"), fim=_hoje() - timedelta(days=1)
        ).pk,
        "vazia": lambda: "",
    }[caso]()

    with pytest.raises(DomainError) as recusa:
        _publicar(cenario, escolhida, chave=f"publicar-0766-{codigo[:10]}")

    assert recusa.value.code == codigo
    assert not PublicacaoResultado.objects.exists()


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="A serialização é do banco; em sqlite não há duas transações concorrentes.",
)
def test_encerrar_enquanto_a_publicacao_espera_e_visto_por_ela(cenario):
    """FR-1126, R-005: a encerrada entre a abertura da tela e a confirmação é recusada.

    A interleaving perigosa é **forçada**, como em `test_concorrencia.py` da 017: a manutenção toma
    a linha da autoridade e a segura; publicar parte e fica esperando; a manutenção grava o fim e
    libera. Sem a trava, publicar teria lido a autoridade ainda vigente e assinado com ela.
    """
    autoridade = registrar_autoridade(Unidade.objects.get(codigo="cefor"), cargo="Reitora")
    desfecho = {}
    comecou = threading.Event()

    def publicar():
        try:
            comecou.set()
            desfecho["publicar"] = _publicar(cenario, autoridade.pk, chave="publicar-0766-corrida")
        except Exception as exc:  # noqa: BLE001 — avaliado no corpo do teste
            desfecho["publicar"] = exc
        finally:
            encerrar_conexoes_da_thread()

    thread = threading.Thread(target=publicar)
    with transaction.atomic():
        AutoridadeHabilitada.objects.select_for_update().get(pk=autoridade.pk)
        thread.start()
        assert comecou.wait(timeout=10)
        time.sleep(1.0)
        assert thread.is_alive(), "publicar não esperou a linha da autoridade"
        AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(
            fim_vigencia=_hoje() - timedelta(days=1),
            encerrada_em=timezone.now(),
            encerrada_por="manutencao",
        )

    thread.join(timeout=60)
    assert not thread.is_alive()
    recusa = desfecho["publicar"]
    assert isinstance(recusa, DomainError), f"publicar devia recusar, e devolveu {recusa!r}"
    assert recusa.code == "autoridade_fora_de_vigencia"
    assert not PublicacaoResultado.objects.exists()
