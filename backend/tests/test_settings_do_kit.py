"""As chaves da peça do kit (111, FR-3432, EC-21, D-010; 119, D-010, FR-3808, FR-3835).

Desligada por padrão, e é produção quem herda o padrão; ligada em desenvolvimento e na suíte. Ao
contrário do assistente na página (074), produção **não** recusa subir com ela ligada: a peça não
expõe nada que o Edital publicado não diga, e ligá-la é decisão de produto, depois da aprovação do
template pela comunicação (SC-1054).
"""

import importlib

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from tests.test_configuracao_producao import _carregar


@pytest.fixture(autouse=True)
def restaurar_configuracao():
    yield
    importlib.reload(importlib.import_module("config.settings.base"))


def test_desligada_em_producao_por_padrao():
    assert _carregar().KIT_DE_DIVULGACAO_PECA is False


def test_producao_sobe_com_a_chave_ligada():
    assert _carregar(KIT_DE_DIVULGACAO_PECA="true").KIT_DE_DIVULGACAO_PECA is True


def test_ligada_na_suite_e_em_desenvolvimento():
    assert settings.KIT_DE_DIVULGACAO_PECA is True
    desenvolvimento = importlib.import_module("config.settings.development")
    assert desenvolvimento.KIT_DE_DIVULGACAO_PECA is True


# ---- A liberação por template (119) -------------------------------------------------------------


def test_liberacao_vazia_em_producao_por_padrao():
    assert _carregar().KIT_DE_DIVULGACAO_TEMPLATES == ()


def test_liberacao_lida_do_ambiente_por_versao_e_resumo_curto():
    producao = _carregar(
        KIT_DE_DIVULGACAO_TEMPLATES=(
            " pos-lato-sensu/post@1#3f9a0c2b71de, fic/story@12#a01b7c55e940 "
        )
    )
    assert producao.KIT_DE_DIVULGACAO_TEMPLATES == (
        ("pos-lato-sensu", "post", 1, "3f9a0c2b71de"),
        ("fic", "story", 12, "a01b7c55e940"),
    )
    # A chave da `111` não muda com a nova.
    assert producao.KIT_DE_DIVULGACAO_PECA is False


@pytest.mark.parametrize(
    "entrada",
    [
        "pos-lato-sensu/post",  # sem versão nem resumo
        "pos-lato-sensu/post@1",  # sem resumo: a regravação herdaria a aprovação (D-010)
        "pos-lato-sensu/post#3f9a0c2b71de",  # sem versão
        "pos-lato-sensu/post@0#3f9a0c2b71de",
        "pos-lato-sensu/post@1#3f9a0c2b",  # resumo curto demais
        "pos-lato-sensu/post@1#3F9A0C2B71DE",
        "desconhecida/post@1#3f9a0c2b71de",
        "pos-lato-sensu/reels@1#3f9a0c2b71de",
    ],
)
def test_entrada_malformada_ou_desconhecida_recusa_a_subida(entrada):
    with pytest.raises(ImproperlyConfigured, match="KIT_DE_DIVULGACAO_TEMPLATES"):
        _carregar(KIT_DE_DIVULGACAO_TEMPLATES=entrada)


def test_suite_e_desenvolvimento_liberam_o_registro():
    """A lista exata é conferida contra o registro em `tests/unit/kit/test_familias.py`."""
    desenvolvimento = importlib.import_module("config.settings.development")
    assert settings.KIT_DE_DIVULGACAO_TEMPLATES
    assert desenvolvimento.KIT_DE_DIVULGACAO_TEMPLATES == settings.KIT_DE_DIVULGACAO_TEMPLATES
