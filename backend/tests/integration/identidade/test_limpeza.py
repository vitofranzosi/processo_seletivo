"""Desafio terminal não é dado permanente de domínio (FR-033, T094).

E a limpeza nomeia o **estado**, não a idade: apagar tudo o que fosse mais velho que uma hora
coincidia com o resultado certo só porque validade e reconciliação pendente cabem em dez minutos —
e esses prazos são constantes editáveis.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


def envelhecer(**campos):
    DesafioDeAcesso.objects.update(criado_em=timezone.now() - timedelta(hours=2), **campos)


def test_apaga_o_consumido(desafio_consumido):
    envelhecer()
    assert servico.limpar_terminais() == 1
    assert not DesafioDeAcesso.objects.exists()


def test_apaga_o_expirado():
    servico.solicitar(email_canonico="a@exemplo.test", finalidade=ENTRAR)
    envelhecer(expira_em=timezone.now() - timedelta(hours=1))

    assert servico.limpar_terminais() == 1


def test_apaga_o_morto_por_tentativas():
    servico.solicitar(email_canonico="a@exemplo.test", finalidade=ENTRAR)
    envelhecer(tentativas_codigo=5)

    assert servico.limpar_terminais() == 1


def test_preserva_o_desafio_vivo():
    """Vivo é vivo, por mais velho que esteja: o filtro fala de estado, não de idade."""
    servico.solicitar(email_canonico="a@exemplo.test", finalidade=ENTRAR)
    envelhecer(expira_em=timezone.now() + timedelta(hours=1))

    assert servico.limpar_terminais() == 0
    assert DesafioDeAcesso.objects.exists()


def test_preserva_a_reconciliacao_pendente(desafio_consumido):
    """O desafio consumido pode estar portando o convite: apagá-lo tiraria a retomada de alguém."""
    alvo = associacao.criar_identidade_com("alvo@exemplo.test", "alvo@exemplo.test")
    associacao.abrir_reconciliacao(desafio_consumido, [alvo])
    envelhecer(reconciliacao_ate=timezone.now() + timedelta(minutes=5))

    assert servico.limpar_terminais() == 0
    assert DesafioDeAcesso.objects.exists()


def test_nao_apaga_o_recente_ainda_que_terminal(desafio_consumido):
    """A janela existe para que a investigação de um acesso recente ainda encontre o rastro."""
    assert servico.limpar_terminais() == 0
