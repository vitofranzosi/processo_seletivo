"""O corte nasce e não muda mais — e a garantia não depende da aplicação (014, FR-223).

**Três camadas, e nenhuma delas basta sozinha.** O `save()` do modelo recusa a alteração vinda do
ORM; a trigger recusa a que vem por `QuerySet.update()` e por `psql`; e o privilégio ausente recusa
a que viesse de qualquer código escrito depois, mesmo que ele contorne as duas primeiras.

A trigger é **absoluta**, e não condicional como a do artefato congelado: o corte nasce imutável.
Sucessão e continuação criam linha nova, e não existe transição legítima que altere uma existente.

Aqui ficam as duas primeiras camadas, que são de unidade. A terceira — a trigger, atacada pelo
`QuerySet.update()` que o ORM não fiscaliza — mora em `tests/integration/classificacao`, onde existe
um corte emitido para atacar.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.classificacao.models import Corte, ItemDoCorte


def test_o_corte_recusa_alteracao_pelo_orm():
    corte = Corte(id=uuid.uuid4(), emitido_em=timezone.now())
    corte._state.adding = False

    with pytest.raises(TypeError, match="append-only"):
        corte.save()


def test_o_corte_recusa_exclusao_pelo_orm():
    with pytest.raises(TypeError, match="append-only"):
        Corte(id=uuid.uuid4()).delete()


def test_o_item_recusa_alteracao_e_exclusao_pelo_orm():
    item = ItemDoCorte(id=uuid.uuid4())
    item._state.adding = False

    with pytest.raises(TypeError, match="append-only"):
        item.save()
    with pytest.raises(TypeError, match="append-only"):
        ItemDoCorte(id=uuid.uuid4()).delete()


def test_a_raiz_efetiva_e_a_propria_linha_quando_ela_e_a_raiz():
    """Vigência não é coluna: quem pergunta pela geração pergunta pela raiz."""
    raiz = Corte(id=uuid.uuid4())
    continuacao = Corte(id=uuid.uuid4(), raiz=raiz)

    assert raiz.raiz_id_efetiva == raiz.id
    assert continuacao.raiz_id_efetiva == raiz.id
