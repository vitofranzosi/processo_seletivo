"""A limpeza enxuta do `tests/conftest.py` deixa o banco como a do Django deixaria.

O que ela promete é equivalência, e equivalência não se vê no caso seguinte: a suíte em paralelo
distribui os casos entre workers, e "o próximo caso" não é um só. Por isso estes casos chamam a
limpeza no meio do próprio corpo e conferem o banco logo depois — o que só é possível num caso
transacional, que é justamente o que ela limpa.
"""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from tests.conftest import (
    _TABELAS_DE_REFERENCIA,
    _impressao_das_tabelas_de_referencia,
    _limpar_so_o_que_mudou,
    _preparar_limpeza,
)
from tests.fixtures.autoridades import garantir_o_cefor

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _tabelas_com_linha():
    preparo = _preparar_limpeza(connection)
    with connection.cursor() as cursor:
        cursor.execute(preparo["sujas"])
        return {linha[0] for linha in cursor.fetchall()}


def test_nao_sobra_linha_fora_das_tabelas_de_referencia():
    # O Cefor é gravado pela fixture `autouse`, e a Unidade é referenciada por boa parte do
    # esquema: é o fecho de chaves estrangeiras que o `TRUNCATE` exige.
    preparo = _preparar_limpeza(connection)
    garantir_o_cefor()
    assert _tabelas_com_linha() - _TABELAS_DE_REFERENCIA

    assert _limpar_so_o_que_mudou(connection, preparo, "default")

    assert _tabelas_com_linha() == set(_TABELAS_DE_REFERENCIA)


def test_as_tabelas_de_referencia_intactas_ficam_como_estavam():
    preparo = _preparar_limpeza(connection)
    ids = set(ContentType.objects.values_list("id", flat=True))

    assert _limpar_so_o_que_mudou(connection, preparo, "default")

    # Os mesmos ids: não foram truncadas e recriadas, que é o que poupa o `post_migrate`.
    assert set(ContentType.objects.values_list("id", flat=True)) == ids
    with connection.cursor() as cursor:
        assert _impressao_das_tabelas_de_referencia(cursor) == preparo["impressao"]


def test_a_tabela_de_referencia_alterada_e_recriada_pelo_post_migrate():
    preparo = _preparar_limpeza(connection)
    tipos = ContentType.objects.count()
    ContentType.objects.filter(app_label="auth", model="group").update(model="adulterado")

    assert _limpar_so_o_que_mudou(connection, preparo, "default")

    assert not ContentType.objects.filter(model="adulterado").exists()
    assert ContentType.objects.count() == tipos
    assert _tabelas_com_linha() == set(_TABELAS_DE_REFERENCIA)


def test_depois_de_repovoar_a_limpeza_seguinte_nao_repovoa_de_novo():
    preparo = _preparar_limpeza(connection)
    ContentType.objects.filter(app_label="auth", model="group").update(model="adulterado")
    assert _limpar_so_o_que_mudou(connection, preparo, "default")
    ids = set(ContentType.objects.values_list("id", flat=True))

    assert _limpar_so_o_que_mudou(connection, preparo, "default")

    # Ids iguais: a segunda limpeza reconheceu as tabelas como intactas e não as recriou.
    assert set(ContentType.objects.values_list("id", flat=True)) == ids
