"""A restrição de uma inscrição por identidade, Edital e Perfil continua intacta (FR-062).

Ela é o que sustenta a idempotência de abertura desde a `009`: dois cliques, duas abas, e uma só
inscrição. A `010` acrescentou restrição sobre CPF em inscrição enviada; **acrescentou**, e não
substituiu — e este teste existe para que a diferença não se perca.
"""

import pytest
from django.db.utils import IntegrityError

from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_abrir_duas_vezes_produz_uma_inscricao(selecao):
    primeira = abrir_inscricao(
        identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE
    )
    segunda = abrir_inscricao(
        identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE
    )
    assert primeira.id == segunda.id
    assert Inscricao.objects.count() == 1


def test_a_restricao_existe_no_banco(selecao):
    import uuid

    from django.db import transaction
    from django.utils import timezone

    abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Inscricao.objects.create(
                id=uuid.uuid4(),
                identity_subject=MARIA.subject,
                edital_id=selecao.id,
                profile_id=PERFIL_DOCENTE,
                nome=MARIA.nome,
                cpf=MARIA.cpf,
                cpf_normalizado="12345678909",
                email=MARIA.email,
                created_at=timezone.now(),
            )
