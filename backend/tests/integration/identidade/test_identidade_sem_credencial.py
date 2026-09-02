"""Identidade sem credencial alguma é estado válido — porque é o que a reconciliação produz.

Escrever o invariante como "identidade nunca fica sem credencial" seria contradizer a migração que
materializa as identidades históricas: ela preserva o identificador estável e **não marca endereço
nenhum como verificado** (FR-043), porque endereço digitado numa inscrição é indício, não prova.

A identidade fica lá, dona das suas inscrições, esperando alguém provar o controle de uma caixa.
"""

import pytest
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity, novo_subject

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_identidade_sem_credencial_persiste():
    dona = CandidateIdentity.objects.create(subject=novo_subject(), created_at=timezone.now())
    dona.refresh_from_db()
    assert dona.credenciais.count() == 0


def test_identidade_sem_nome_e_sem_cpf_persiste():
    """É o estado de quem acabou de entrar pela primeira vez: só provou uma caixa de e-mail."""
    dona = CandidateIdentity.objects.create(subject=novo_subject(), created_at=timezone.now())
    assert dona.nome == "" and dona.cpf_normalizado == ""
