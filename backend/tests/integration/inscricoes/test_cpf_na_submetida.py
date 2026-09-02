"""A restrição de CPF sobre inscrição enviada — e o que ela consegue e não consegue afirmar.

Ela existe porque a `010` precisa **ler** aquele CPF: a reconciliação agrupa por ele e a marcação
de coincidência compara por ele. Uma coluna vazia numa inscrição enviada tornaria as duas coisas
silenciosamente incompletas (FR-063).

O que ela afirma são onze dígitos. Os dígitos verificadores não cabem numa restrição declarativa, e
continuam onde já estavam: na captura, e na verificação que a implantação faz antes de instalar a
restrição (D-017). Este teste também fixa esse limite — para que ninguém leia a garantia como
maior do que ela é.
"""

import uuid

import pytest
from django.db import DataError, IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def rascunho(selecao, *, cpf, perfil=PERFIL_DOCENTE):
    return Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=f"cand:{uuid.uuid4().hex}",
        edital_id=selecao.id,
        profile_id=perfil,
        nome="Maria Silva",
        cpf=cpf,
        cpf_normalizado=cpf,
        email="m@ex.br",
        created_at=timezone.now(),
    )


def enviar(selecao, registro):
    return Inscricao.objects.filter(pk=registro.pk).update(
        status="SUBMETIDA",
        submitted_at=timezone.now(),
        declaracoes_aceitas_em=timezone.now(),
        versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
        protocolo=f"INS-{uuid.uuid4().hex[:8].upper()}",
    )


@pytest.mark.parametrize("cpf", ["", "1234567890", "1234567890a"])
def test_o_banco_recusa_inscricao_enviada_sem_onze_digitos(selecao, cpf):
    registro = rascunho(selecao, cpf=cpf)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            enviar(selecao, registro)


def test_mais_de_onze_digitos_nem_chega_na_restricao(selecao):
    """A largura da coluna recusa antes, e em qualquer estado — inclusive rascunho.

    São dois mecanismos, e vale conhecer os dois: a restrição fala do ato de enviar, a largura fala
    da coluna. A garantia resultante é a mesma — o valor não entra.
    """
    with pytest.raises(DataError):
        with transaction.atomic():
            rascunho(selecao, cpf="123456789012")


def test_o_banco_aceita_inscricao_enviada_com_onze_digitos(selecao):
    registro = rascunho(selecao, cpf="12345678909")
    assert enviar(selecao, registro) == 1


def test_o_rascunho_pode_ficar_sem_cpf(selecao):
    """Rascunho é intenção, e a pessoa ainda não informou nada.

    A restrição é do ato de enviar, e não do começo.
    """
    assert rascunho(selecao, cpf="").pk is not None


def test_a_restricao_nao_confere_os_digitos_verificadores(selecao):
    """O limite do que uma restrição declarativa consegue, dito em teste.

    `11111111111` tem onze dígitos e não é CPF de ninguém. O banco aceita, e quem recusa é o
    domínio — na captura, e na verificação da implantação. Fixar isto aqui impede que a garantia
    seja lida como maior do que é.
    """
    registro = rascunho(selecao, cpf="11111111111")
    assert enviar(selecao, registro) == 1
