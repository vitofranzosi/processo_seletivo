"""T021a — idempotência dos cinco comandos, e o que ela **não** é.

Três coisas diferentes, e o contrato as separa: repetir o mesmo pedido devolve o resultado
original; repetir a chave com outro conteúdo é conflito de idempotência; e dois pedidos distintos
querendo criar o mesmo vínculo é conflito de unicidade.
"""

import pytest

from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.application.comissao import (
    adicionar_membro,
    alterar_funcao,
    remover_membro,
)
from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import alocar_em

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_incluir_duas_vezes_com_a_mesma_chave(gestor, processo_a):
    primeiro, _ = adicionar_membro(
        actor=gestor,
        processo_id=processo_a.id,
        identity_subject="joao",
        funcao="MEMBRO",
        idempotency_key="k",
        correlation_id="c",
    )
    segundo, status = adicionar_membro(
        actor=gestor,
        processo_id=processo_a.id,
        identity_subject="joao",
        funcao="MEMBRO",
        idempotency_key="k",
        correlation_id="c",
    )

    assert segundo.pk == primeiro.pk and status == 201
    assert MembroComissao.objects.count() == 1


def test_mesma_chave_com_conteudo_diferente_e_conflito(gestor, processo_a):
    adicionar_membro(
        actor=gestor,
        processo_id=processo_a.id,
        identity_subject="joao",
        funcao="MEMBRO",
        idempotency_key="k",
        correlation_id="c",
    )

    with pytest.raises(DomainError) as recusa:
        adicionar_membro(
            actor=gestor,
            processo_id=processo_a.id,
            identity_subject="ana",
            funcao="MEMBRO",
            idempotency_key="k",
            correlation_id="c",
        )

    assert recusa.value.code == "idempotency_conflict"


def test_alocar_duas_vezes_com_a_mesma_chave(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    """FR-065: repetir a ação de alocar não produz registros ativos duplicados."""
    primeira = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1, chave="k")
    segunda = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1, chave="k")

    assert segunda.pk == primeira.pk
    assert AlocacaoEtapa.objects.count() == 1


def test_alterar_funcao_e_idempotente(gestor, processo_a, comissao_de_a):
    for _ in range(2):
        alterar_funcao(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["joao"].id,
            funcao="PRESIDENTE",
            idempotency_key="k",
            correlation_id="c",
        )

    comissao_de_a["joao"].refresh_from_db()
    assert comissao_de_a["joao"].funcao == "PRESIDENTE"


def test_remover_membro_e_idempotente(gestor, processo_a, comissao_de_a):
    for _ in range(2):
        remover_membro(
            actor=gestor,
            processo_id=processo_a.id,
            membro_id=comissao_de_a["joao"].id,
            idempotency_key="k",
            correlation_id="c",
        )

    comissao_de_a["joao"].refresh_from_db()
    assert comissao_de_a["joao"].ativo is False


def test_remover_alocacao_e_idempotente(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocacao = alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    for _ in range(2):
        remover_alocacao(
            actor=gestor,
            processo_id=processo_a.id,
            alocacao_id=alocacao.id,
            idempotency_key="k",
            correlation_id="c",
        )

    alocacao.refresh_from_db()
    assert alocacao.ativo is False


def test_a_reserva_acontece_depois_da_autorizacao(processo_a):
    """D-016: reservar antes de autorizar faria a repetição responder a quem perdeu a base."""
    from processo_seletivo.auditoria.models import IdempotencyRecord
    from tests.conftest import ator_institucional

    with pytest.raises(DomainError):
        adicionar_membro(
            actor=ator_institucional("estranho"),
            processo_id=processo_a.id,
            identity_subject="joao",
            funcao="MEMBRO",
            idempotency_key="k",
            correlation_id="c",
        )

    assert IdempotencyRecord.objects.filter(actor_subject="estranho").count() == 0


def test_lote_sem_nada_a_criar_fecha_a_reserva(gestor, processo_a, comissao_de_a):
    """Sem fechar, a repetição refazia consulta e laço inteiros para chegar ao mesmo nada."""
    from processo_seletivo.auditoria.models import IdempotencyRecord
    from processo_seletivo.comissoes.application.comissao import adicionar_varios

    entradas = [("joao", ""), ("maria", "")]
    adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=entradas,
        funcao="MEMBRO",
        idempotency_key="k-vazio",
        correlation_id="c",
    )

    reserva = IdempotencyRecord.objects.get(key="k-vazio")
    assert reserva.response_status is not None

    criados, _ = adicionar_varios(
        actor=gestor,
        processo_id=processo_a.id,
        entradas=entradas,
        funcao="MEMBRO",
        idempotency_key="k-vazio",
        correlation_id="c",
    )
    assert criados == []
