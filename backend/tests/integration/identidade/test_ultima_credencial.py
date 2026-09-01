"""A última credencial não sai: removê-la é apagar o próprio acesso (FR-018).

E a conferência é do servidor. A tela não oferece o botão quando há só uma, mas esconder não é
fronteira de segurança — quem montar a requisição à mão encontra a mesma recusa.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

UNICO = "unico@exemplo.test"


@pytest.fixture
def com_uma_so(client):
    identidade = associacao.criar_identidade_com(UNICO, UNICO)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def test_a_tela_nao_oferece_remover_quando_ha_uma_so(client, com_uma_so):
    corpo = client.get(reverse("portal:conta")).content.decode()
    assert "conta/emails" in corpo, "a tela existe e mostra a credencial"
    assert "/remover" not in corpo


def test_o_servidor_recusa_mesmo_assim(client, com_uma_so):
    credencial = CandidateEmail.objects.get(identidade=com_uma_so)

    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    assert CandidateEmail.objects.filter(pk=credencial.pk).exists()
    corpo = client.get(reverse("portal:conta")).content.decode()
    assert "não pode remover seu último e-mail" in corpo


def test_a_identidade_com_credencial_nunca_fica_sem_principal(client, com_uma_so):
    credencial = CandidateEmail.objects.get(identidade=com_uma_so)
    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    assert CandidateEmail.objects.get(identidade=com_uma_so).principal is True
