"""Os invariantes que a persistência sustenta — e o que ela deliberadamente **não** exige.

O primeiro é exclusividade de credencial, e ela precisa ser do banco: verificar antes de gravar
perde a corrida entre duas confirmações simultâneas, e o que se perde nessa corrida é a
exclusividade de uma credencial (FR-011).

O segundo é condicional, e a distinção importa: uma identidade **que tenha credencial** tem
exatamente uma principal. Exigir que toda identidade tenha credencial seria contradizer a própria
reconciliação, que materializa identidades históricas sem verificar endereço nenhum.
"""

import uuid

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    novo_subject,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def identidade(**campos):
    return CandidateIdentity.objects.create(
        subject=campos.pop("subject", novo_subject()), created_at=timezone.now(), **campos
    )


def credencial(dona, endereco, *, principal=False):
    return CandidateEmail.objects.create(
        id=uuid.uuid4(),
        identidade=dona,
        email_canonico=endereco,
        email_como_informado=endereco,
        principal=principal,
        verified_at=timezone.now(),
        created_at=timezone.now(),
    )


def test_o_endereco_canonico_pertence_a_uma_unica_identidade():
    credencial(identidade(), "maria@exemplo.test", principal=True)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            credencial(identidade(), "maria@exemplo.test", principal=True)


def test_a_recusa_e_do_banco_e_nao_da_consulta_previa():
    """É o que sobrevive a duas confirmações simultâneas do mesmo endereço (SC-015)."""
    dona = identidade()
    credencial(dona, "maria@exemplo.test", principal=True)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            # Nem sequer consulta antes: é exatamente o que uma corrida faria.
            credencial(dona, "maria@exemplo.test")


def test_identidade_com_credencial_tem_exatamente_uma_principal():
    dona = identidade()
    credencial(dona, "primeira@exemplo.test", principal=True)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            credencial(dona, "segunda@exemplo.test", principal=True)


def test_duas_identidades_podem_ter_cada_uma_a_sua_principal():
    credencial(identidade(), "maria@exemplo.test", principal=True)
    credencial(identidade(), "joao@exemplo.test", principal=True)
    assert CandidateEmail.objects.filter(principal=True).count() == 2


def test_o_cpf_nao_e_unico_entre_identidades():
    """Duas identidades podem declarar o mesmo CPF (FR-064).

    A regra intuitiva — um CPF, uma identidade — recriaria na primeira inscrição o sequestro que
    esta feature eliminou no acesso: quem vinculasse primeiro um CPF alheio bloquearia o titular
    para sempre, sem rota de recuperação. A coincidência é assinalada onde importa.
    """
    identidade(cpf_normalizado="12345678909")
    identidade(cpf_normalizado="12345678909")
    assert CandidateIdentity.objects.filter(cpf_normalizado="12345678909").count() == 2
