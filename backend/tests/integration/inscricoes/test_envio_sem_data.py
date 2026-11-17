"""O envio exige a data de nascimento e a congela na inscrição (180, história 2).

FR-8303 (recusa do comando), FR-8308 (congela no ato, com a data do cadastro naquele instante), o
gatilho da enviada alcançando a coluna nova, e a premissa de que o comprovante não mostra a data.
"""

import dataclasses
from datetime import date

import pytest
from django.db import DatabaseError, transaction
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEM_DATA = dataclasses.replace(MARIA, data_nascimento=None)


def _pronta(inscricao):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao, identidade=MARIA, chave="envio-180"):
    return enviar_inscricao(
        identidade=identidade,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=chave,
    )


def test_sem_data_o_envio_e_recusado(inscricao_de_maria):
    inscricao = _pronta(inscricao_de_maria)

    with pytest.raises(DomainError) as recusa:
        _enviar(inscricao, identidade=SEM_DATA)

    assert recusa.value.code == "birth_date_required"
    assert "Seus dados" in str(recusa.value.detail)
    inscricao.refresh_from_db()
    assert inscricao.status == Inscricao.Status.RASCUNHO


def test_o_envio_congela_a_data_do_cadastro(inscricao_de_maria):
    enviada = _enviar(_pronta(inscricao_de_maria))
    assert enviada.data_nascimento == MARIA.data_nascimento


def test_corrigir_o_cadastro_antes_do_envio_muda_o_que_e_congelado(inscricao_de_maria):
    """O rascunho acompanha o cadastro até o envio (FR-8308)."""
    corrigida = dataclasses.replace(MARIA, data_nascimento=date(1998, 3, 7))
    enviada = _enviar(_pronta(inscricao_de_maria), identidade=corrigida)
    assert enviada.data_nascimento == date(1998, 3, 7)


def test_a_data_da_enviada_nao_muda_pelo_banco(inscricao_de_maria):
    """O gatilho da `inscricoes/0007` alcança a coluna nova: a enviada é ato."""
    enviada = _enviar(_pronta(inscricao_de_maria))

    with pytest.raises(DatabaseError, match="submitted enrollments are immutable"):
        with transaction.atomic():
            Inscricao.objects.filter(pk=enviada.pk).update(data_nascimento=date(1990, 1, 1))

    enviada.refresh_from_db()
    assert enviada.data_nascimento == MARIA.data_nascimento


def test_o_comprovante_nao_mostra_a_data(client, inscricao_de_maria):
    """Minimização: o comprovante já identifica por nome e CPF (premissa da spec)."""
    enviada = _enviar(_pronta(inscricao_de_maria))
    identificar(client, MARIA)

    pagina = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert "Maria Silva" in pagina
    assert MARIA.data_nascimento.strftime("%d/%m/%Y") not in pagina
    assert "nascimento" not in pagina.lower()
