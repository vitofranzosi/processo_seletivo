"""A apuração nasce e não muda mais — e a garantia não depende da aplicação (016, `FR-260`).

**Três camadas, e nenhuma basta sozinha.** O `save()` do modelo recusa a alteração vinda do ORM; o
gatilho recusa a que vem por `QuerySet.update()` e por `psql`; e o privilégio ausente recusa a que
viesse de qualquer código escrito depois, mesmo contornando as duas primeiras.

Aqui ficam as duas primeiras, que são de unidade. A terceira — o gatilho, atacado pelo
`QuerySet.update()` que o ORM não fiscaliza — mora em `tests/integration/ocupacao`, onde existe
apuração emitida para atacar.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao, MovimentoDeVaga


def test_a_apuracao_recusa_alteracao_pelo_orm():
    apuracao = ApuracaoDeOcupacao(id=uuid.uuid4(), emitida_em=timezone.now())
    apuracao._state.adding = False

    with pytest.raises(TypeError, match="append-only"):
        apuracao.save()


def test_a_apuracao_recusa_exclusao_pelo_orm():
    with pytest.raises(TypeError, match="append-only"):
        ApuracaoDeOcupacao(id=uuid.uuid4()).delete()


def test_o_movimento_recusa_alteracao_e_exclusao_pelo_orm():
    movimento = MovimentoDeVaga(id=uuid.uuid4())
    movimento._state.adding = False

    with pytest.raises(TypeError, match="append-only"):
        movimento.save()
    with pytest.raises(TypeError, match="append-only"):
        MovimentoDeVaga(id=uuid.uuid4()).delete()


def test_faltando_e_derivado_e_nunca_negativo():
    """`faltando` é propriedade, e não coluna — de propósito (016, `R-006`).

    O piso em zero existe porque a fronteira do empate pode levar a faixa a mais gente que o alvo.
    """
    assert ApuracaoDeOcupacao(efetivas=35, ocupadas=13).faltando == 22
    assert ApuracaoDeOcupacao(efetivas=10, ocupadas=12).faltando == 0


def test_o_modelo_nao_tem_coluna_de_vigencia_nem_de_obsolescencia():
    """**A ausência é a regra, e este teste a prende.**

    Manter uma flag `vigente` ou `obsoleto` exigiria `UPDATE`, operação proibida nesta tabela. Quem
    acrescentar a coluna não é barrado ao criá-la — é barrado quando tentar atualizá-la, que é o
    modo de falha mais tardio possível. Aqui o erro aparece no lugar mais cedo que existe.
    """
    colunas = {campo.name for campo in ApuracaoDeOcupacao._meta.get_fields()}
    assert not colunas & {"vigente", "obsoleto", "obsoleta", "esta_vigente"}
