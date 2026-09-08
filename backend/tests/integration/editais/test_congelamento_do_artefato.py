"""FR-010 e FR-010a da 020 — o artefato publicado é imutável, e o do rascunho não é.

A trigger é condicional ao estado, como a de `Retificacao`: o que muda enquanto o ato corre não
pode ser congelado por completo, e o que já produziu efeito não pode mudar. Cada teste ataca pelo
caminho que a aplicação não fiscaliza — `update()` e `delete()` diretos no QuerySet —, que é como
um artefato publicado seria reescrito sem querer.
"""

import pytest
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from processo_seletivo.editais.models import ArtefatoAnexo
from tests.fixtures.anexos import criar_artefato, pdf_de_teste

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a trigger de congelamento exige PostgreSQL"
)
pytestmark = [pytest.mark.integration, postgresql_only]


@pytest.mark.django_db(transaction=True)
def test_o_artefato_do_rascunho_pode_ser_trocado():
    artefato = criar_artefato(marca="A")

    ArtefatoAnexo.objects.filter(pk=artefato.pk).update(nome_original="outro.pdf")

    assert ArtefatoAnexo.objects.get(pk=artefato.pk).nome_original == "outro.pdf"


@pytest.mark.django_db(transaction=True)
def test_o_artefato_do_rascunho_pode_ser_apagado():
    artefato = criar_artefato(marca="A")

    ArtefatoAnexo.objects.filter(pk=artefato.pk).delete()

    assert not ArtefatoAnexo.objects.filter(pk=artefato.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_congelar_e_a_transicao_admitida():
    """A transição que *congela* parte de nulo, e por isso a trigger não a alcança."""
    artefato = criar_artefato(marca="A")
    agora = timezone.now()

    ArtefatoAnexo.objects.filter(pk=artefato.pk).update(congelado_em=agora)

    assert ArtefatoAnexo.objects.get(pk=artefato.pk).publicado


@pytest.mark.django_db(transaction=True)
def test_o_artefato_congelado_nao_pode_ser_alterado():
    artefato = criar_artefato(marca="A", congelado=True)

    with pytest.raises(DatabaseError, match="artifacts are immutable"), transaction.atomic():
        ArtefatoAnexo.objects.filter(pk=artefato.pk).update(nome_original="outro.pdf")


@pytest.mark.django_db(transaction=True)
def test_os_bytes_do_artefato_congelado_nao_podem_ser_trocados():
    """O ataque que mais importa: trocar o conteúdo mantendo a linha e o resumo antigo."""
    artefato = criar_artefato(marca="A", congelado=True)

    with pytest.raises(DatabaseError, match="artifacts are immutable"), transaction.atomic():
        ArtefatoAnexo.objects.filter(pk=artefato.pk).update(bytes=pdf_de_teste("B"))


@pytest.mark.django_db(transaction=True)
def test_o_artefato_congelado_nao_pode_ser_apagado():
    artefato = criar_artefato(marca="A", congelado=True)

    with pytest.raises(DatabaseError, match="artifacts are immutable"), transaction.atomic():
        ArtefatoAnexo.objects.filter(pk=artefato.pk).delete()


@pytest.mark.django_db(transaction=True)
def test_descongelar_tambem_e_recusado():
    """Sem isto, zerar a coluna reabriria a escrita — a trigger olha o valor **antigo**."""
    artefato = criar_artefato(marca="A", congelado=True)

    with pytest.raises(DatabaseError, match="artifacts are immutable"), transaction.atomic():
        ArtefatoAnexo.objects.filter(pk=artefato.pk).update(congelado_em=None)
