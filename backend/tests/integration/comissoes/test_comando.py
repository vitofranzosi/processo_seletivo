"""T019a — o invólucro: Processo em estado final não recebe alteração de comissão (FR-067)."""

import pytest

from processo_seletivo.comissoes.application.alocacao import alocar, remover_alocacao
from processo_seletivo.comissoes.application.comissao import (
    adicionar_membro,
    alterar_funcao,
    remover_membro,
)
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return {"membros": comissao_de_a, "alocacao": alocacao}


def encerrar(processo, status):
    ProcessoSeletivo.objects.filter(pk=processo.pk).update(status=status)
    processo.refresh_from_db()


@pytest.mark.parametrize("status", ["ENCERRADO", "CANCELADO"])
def test_os_cinco_comandos_recusam_processo_em_estado_final(
    gestor, processo_a, edital_a, cenario, etapa_a2, status
):
    encerrar(processo_a, status)
    membros, alocacao = cenario["membros"], cenario["alocacao"]

    chamadas = [
        lambda: adicionar_membro(
            actor=gestor,
            processo_id=processo_a.id,
            identity_subject="ana",
            funcao="MEMBRO",
            idempotency_key="k1",
            correlation_id="c",
        ),
        lambda: alterar_funcao(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=membros["joao"].id,
            funcao="PRESIDENTE",
            idempotency_key="k2",
            correlation_id="c",
        ),
        lambda: remover_membro(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=membros["joao"].id,
            idempotency_key="k3",
            correlation_id="c",
        ),
        lambda: alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=membros["joao"].id,
            edital_id=edital_a.id,
            etapa_id=etapa_a2,
            idempotency_key="k4",
            correlation_id="c",
        ),
        lambda: remover_alocacao(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_id=alocacao.id,
            idempotency_key="k5",
            correlation_id="c",
        ),
    ]
    for chamada in chamadas:
        with pytest.raises(DomainError) as recusa:
            chamada()
        assert recusa.value.status in (409, 422), recusa.value.code


@pytest.mark.parametrize("malformado", ["", "nao-e-uuid", "123"])
def test_identificador_malformado_responde_como_inexistente(
    gestor, processo_a, edital_a, cenario, etapa_a1, malformado
):
    """Identificador sem forma de identificador não identifica nada — e não pode virar 500.

    `filter(pk="")` levanta `ValidationError`, que não é `DomainError` e sobe até o servidor.
    O contrato promete 404 para o que o ator não alcança; 500 é resposta de defeito, não de
    autorização.
    """
    chamadas = [
        lambda: alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=malformado,
            edital_id=edital_a.id,
            etapa_id=etapa_a1,
            idempotency_key="m1",
            correlation_id="c",
        ),
        lambda: alocar(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=cenario["membros"]["joao"].id,
            edital_id=malformado,
            etapa_id=etapa_a1,
            idempotency_key="m2",
            correlation_id="c",
        ),
        lambda: remover_alocacao(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_id=malformado,
            idempotency_key="m3",
            correlation_id="c",
        ),
        lambda: alterar_funcao(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=malformado,
            funcao="PRESIDENTE",
            idempotency_key="m4",
            correlation_id="c",
        ),
        lambda: remover_membro(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=malformado,
            idempotency_key="m5",
            correlation_id="c",
        ),
    ]
    for chamada in chamadas:
        with pytest.raises(DomainError) as recusa:
            chamada()
        assert recusa.value.status == 404, recusa.value.code
