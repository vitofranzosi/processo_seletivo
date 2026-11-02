"""A chave da peça do kit (111, FR-3432, EC-21, D-010).

Desligada por padrão, e é produção quem herda o padrão; ligada em desenvolvimento e na suíte. Ao
contrário do assistente na página (074), produção **não** recusa subir com ela ligada: a peça não
expõe nada que o Edital publicado não diga, e ligá-la é decisão de produto, depois da aprovação do
template pela comunicação (SC-1054).
"""

import importlib

import pytest
from django.conf import settings

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
