"""A lista exigida não se altera nem se apaga — e só nasce do envio (044, FR-715, D-004).

Cada garantia na sua camada: o gatilho recusa até quem tem privilégio; o privilégio ausente é
conferido, para toda tabela da lista, por `test_database_permissions`; o modelo recusa antes de o
banco precisar. O que o banco **não** garante — que a lista nasceu durante o envio — é provado
pela varredura do código, no fim (R-005).
"""

import pathlib
import re

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.inscricoes.models import Inscricao, ItemDaListaExigida
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY
from tests.integration.inscricoes.test_lista_exigida import _enviada

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="as garantias da lista moram no PostgreSQL"
)
TABELA = ItemDaListaExigida._meta.db_table


def test_a_tabela_esta_entre_as_append_only():
    assert TABELA in TABELAS_APPEND_ONLY


@SOMENTE_POSTGRES
@pytest.mark.parametrize(
    "comando",
    [f"UPDATE {TABELA} SET situacao = 'FACULTATIVO'", f"DELETE FROM {TABELA}"],
)
def test_o_gatilho_recusa_mudar_ou_apagar(selecao, candidatos_registrados, comando):
    _enviada(selecao)

    with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(comando)


def test_o_modelo_recusa_antes_do_banco(selecao, candidatos_registrados):
    item = ItemDaListaExigida.objects.filter(inscricao=_enviada(selecao)).first()

    with pytest.raises(TypeError, match="append-only"):
        item.save()
    with pytest.raises(TypeError, match="append-only"):
        item.delete()


def _copia(item, **campos):
    return ItemDaListaExigida(
        inscricao_id=item.inscricao_id,
        versao_id=item.versao_id,
        requisito_id="00000000-0000-0000-0000-00000000fe01",
        chave="outra",
        situacao=item.situacao,
        forma_do_recorte="TODOS",
        gravada_em=item.gravada_em,
        **campos,
    )


@SOMENTE_POSTGRES
def test_nao_se_grava_lista_de_rascunho(selecao, candidatos_registrados):
    enviada = _enviada(selecao)
    item = ItemDaListaExigida.objects.filter(inscricao=enviada).first()
    Inscricao.objects.filter(pk=enviada.pk).update(status=Inscricao.Status.RASCUNHO)

    with pytest.raises(DatabaseError, match="not submitted"), transaction.atomic():
        _copia(item).save()


@SOMENTE_POSTGRES
def test_nao_se_grava_lista_de_outra_versao_nem_de_outro_instante(selecao, candidatos_registrados):
    from datetime import timedelta

    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    item = ItemDaListaExigida.objects.filter(inscricao=_enviada(selecao)).first()
    outra = VersaoConsolidada.objects.exclude(pk=item.versao_id).first()
    copia = _copia(item)

    if outra is not None:
        copia.versao_id = outra.pk
        with pytest.raises(DatabaseError, match="did not accept"), transaction.atomic():
            copia.save()
        copia = _copia(item)

    copia.gravada_em = item.gravada_em + timedelta(seconds=1)
    with pytest.raises(DatabaseError, match="another instant"), transaction.atomic():
        copia.save()


def test_so_o_envio_e_a_semente_gravam_a_lista():
    """O que o gatilho não alcança — o preenchimento retroativo — a varredura prende (D-004)."""
    raiz = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo"
    chamadores = {
        arquivo.relative_to(raiz).as_posix()
        for arquivo in raiz.rglob("*.py")
        if re.search(r"\bgravar_lista_exigida\(", arquivo.read_text(encoding="utf-8"))
        and arquivo.name != "lista_exigida.py"
    }

    assert "inscricoes/application/submissao.py" in chamadores
    assert chamadores <= {
        "inscricoes/application/submissao.py",
        "processos/management/commands/seed_demo.py",
    }
    assert not any("migrations" in caminho for caminho in chamadores)
