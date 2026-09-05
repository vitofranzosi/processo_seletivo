"""A auditoria reproduz por garantia; não existe autoridade nem rota para recalcular o passado."""

import pytest
from django.urls import NoReverseMatch, reverse


def test_nao_existe_rota_de_recalculo_do_passado():
    with pytest.raises(NoReverseMatch):
        reverse("interface:reproduzir-ato-de-ordenacao", args=["0", "0", "0"])
