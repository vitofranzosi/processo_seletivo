"""A reconciliação preserva — e preservar é a única coisa que ela faz com o que já existia.

Os testes chamam a função da migração diretamente, com o registro real de modelos. Exercer a
lógica sem encenar o executor é o que interessa aqui; o executor já é exercido por
`test_migrations.py`, que aplica tudo do zero e a partir da versão anterior.

O que se prova: o identificador estável é **copiado**, nunca atribuído (FR-042); nenhum endereço
histórico vira credencial (FR-043); e o nome vem da inscrição mais recente do grupo (FR-041).
"""

import importlib
import uuid
from datetime import timedelta

import pytest
from django.apps import apps
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE, PERFIL_TECNICO

reconciliacao = importlib.import_module(
    "processo_seletivo.identidade.migrations.0002_reconciliacao"
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF_DE_MARIA = "12345678909"


def inscricao(selecao, *, subject, cpf, nome, email, perfil=PERFIL_DOCENTE, quando=None):
    return Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome=nome,
        cpf=cpf,
        cpf_normalizado=cpf,
        email=email,
        created_at=quando or timezone.now(),
    )


def test_preserva_o_identificador_estavel_da_inscricao(selecao):
    """O ponto inteiro da migração: o dono de ontem continua sendo o dono de hoje."""
    inscricao(selecao, subject=MARIA.subject, cpf=CPF_DE_MARIA, nome="Maria Silva", email="m@ex.br")

    reconciliacao.reconciliar(apps, None)

    identidade = CandidateIdentity.objects.get(cpf_normalizado=CPF_DE_MARIA)
    assert identidade.subject == MARIA.subject
    assert Inscricao.objects.get().identity_subject == MARIA.subject


def test_nao_reescreve_nenhuma_inscricao(selecao):
    registro = inscricao(
        selecao, subject=MARIA.subject, cpf=CPF_DE_MARIA, nome="Maria", email="m@ex.br"
    )
    antes = (registro.identity_subject, registro.revision, registro.status)

    reconciliacao.reconciliar(apps, None)

    registro.refresh_from_db()
    assert (registro.identity_subject, registro.revision, registro.status) == antes


def test_nao_marca_endereco_algum_como_verificado(selecao):
    """Endereço digitado numa inscrição é indício. Quem prova controle é o desafio (FR-015)."""
    inscricao(
        selecao, subject=MARIA.subject, cpf=CPF_DE_MARIA, nome="Maria", email="maria@ex.br"
    )

    reconciliacao.reconciliar(apps, None)

    assert CandidateEmail.objects.count() == 0


def test_traz_o_nome_da_inscricao_mais_recente(selecao):
    agora = timezone.now()
    inscricao(
        selecao,
        subject=MARIA.subject,
        cpf=CPF_DE_MARIA,
        nome="Maria Silva",
        email="m@ex.br",
        quando=agora - timedelta(days=10),
    )
    inscricao(
        selecao,
        subject=MARIA.subject,
        cpf=CPF_DE_MARIA,
        nome="Maria S. Silva",
        email="m@ex.br",
        perfil=PERFIL_TECNICO,
        quando=agora,
    )

    reconciliacao.reconciliar(apps, None)

    assert CandidateIdentity.objects.get().nome == "Maria S. Silva"


def test_uma_identidade_por_cpf_e_nao_uma_por_inscricao(selecao):
    inscricao(selecao, subject=MARIA.subject, cpf=CPF_DE_MARIA, nome="Maria", email="m@ex.br")
    inscricao(
        selecao,
        subject=MARIA.subject,
        cpf=CPF_DE_MARIA,
        nome="Maria",
        email="m@ex.br",
        perfil=PERFIL_TECNICO,
    )

    reconciliacao.reconciliar(apps, None)

    assert CandidateIdentity.objects.count() == 1


def test_base_sem_inscricao_alguma_nao_cria_nada(selecao):
    reconciliacao.reconciliar(apps, None)
    assert CandidateIdentity.objects.count() == 0
