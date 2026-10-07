"""US3 da 060 — trocar a autoridade da unidade sem mudar o sistema (SC-432, SC-433).

O percurso inteiro, pelos comandos que a tela chama: cadastrar, publicar com ela, encerrar,
cadastrar outra, publicar de novo. A primeira Publicação continua dizendo a primeira autoridade; a
partir de amanhã só a nova é oferecida.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.application.autoridades import cadastrar, encerrar
from processo_seletivo.unidades.application.selectors import autoridades_vigentes
from tests.conftest import ator_institucional
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]


def _hoje():
    return timezone.now().astimezone(ZONA).date()


def test_trocar_a_diretora_geral_sem_mudar_o_sistema(api_client, manager_headers, process_payload):
    gestor = ator_institucional("gabriel", "autoridade:gerir")
    primeira = cadastrar(
        actor=gestor,
        cargo="Diretora-Geral",
        nome="Primeira Diretora",
        inicio_vigencia=_hoje() - timedelta(days=100),
        idempotency_key="troca-cadastro-1",
        correlation_id="troca",
    )
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        signatory={"authorityId": str(primeira.pk)},
    )

    encerrar(
        actor=gestor,
        autoridade_id=primeira.pk,
        fim_vigencia=_hoje(),
        idempotency_key="troca-encerrar-1",
        correlation_id="troca",
    )
    segunda = cadastrar(
        actor=gestor,
        cargo="Diretora-Geral",
        nome="Segunda Diretora",
        inicio_vigencia=_hoje() + timedelta(days=1),
        idempotency_key="troca-cadastro-2",
        correlation_id="troca",
    )

    publicacao = Publicacao.objects.get(edital=edital)
    assert publicacao.signatory_name == "Primeira Diretora", "SC-433: o ato não muda"

    amanha = _hoje() + timedelta(days=1)
    oferecidas = {a.pk for a in autoridades_vigentes("cefor", amanha)}
    assert segunda.pk in oferecidas and primeira.pk not in oferecidas
    hoje = {a.pk for a in autoridades_vigentes("cefor", _hoje())}
    assert primeira.pk in hoje and segunda.pk not in hoje, "o fim é inclusivo"

    operacoes = set(
        RegistroAuditoria.objects.filter(institution_scope="cefor").values_list(
            "operation", flat=True
        )
    )
    assert {"CADASTRAR_AUTORIDADE", "ENCERRAR_AUTORIDADE"} <= operacoes
