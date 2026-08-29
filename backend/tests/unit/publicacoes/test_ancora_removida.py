"""SC-007: a âncora saiu inteira, e não parcialmente.

Mecanismo sem função é armadilha: alguém volta a preenchê-lo achando que protege algo, ou
alguém lê o campo no modelo e conclui que a verificação ainda existe. Este teste procura o que
sobrou — no esquema, no código e no vocabulário de erros.

`migrations/` é história e fica de fora por construção: a `0005` criou a coluna e a `0006` a
preencheu, e reescrever migration aplicada é o que a Constituição proíbe.
"""

from pathlib import Path

import pytest
from django.apps import apps

from processo_seletivo.publicacoes.domain import conflicts

RAIZ = Path(__file__).resolve().parents[3] / "processo_seletivo"
VESTIGIOS = ("expected_anchors", "expectedAnchors", "target_identity_mismatch", "path_anchors")


def vestigios_em(raiz, vestigio):
    """Onde `vestigio` aparece, fora de `migrations/`, como `arquivo:linha`."""
    return [
        f"{caminho.relative_to(raiz)}:{numero}"
        for caminho in sorted(raiz.rglob("*.py"))
        if "migrations" not in caminho.parts and "__pycache__" not in caminho.parts
        for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1)
        if vestigio in linha
    ]


@pytest.mark.parametrize("vestigio", VESTIGIOS)
def test_no_source_outside_migrations_mentions_the_anchor(vestigio):
    assert vestigios_em(RAIZ, vestigio) == []


def test_the_field_is_gone_from_the_model():
    modelo = apps.get_model("publicacoes", "AlteracaoNormativa")
    assert "expected_anchors" not in {campo.name for campo in modelo._meta.get_fields()}


def test_the_domain_no_longer_exports_the_anchor_vocabulary():
    ausentes = {"ANCHOR_MISMATCH", "path_anchors", "_identity", "_anchor_conflicts"}
    assert ausentes.isdisjoint(dir(conflicts))


def test_the_hash_precondition_stayed():
    """FR-014: o que ficou tinha de ficar.

    Sem esta verificação, os testes acima passariam com o módulo inteiro apagado.
    """
    assert conflicts.HASH_MISMATCH == "expected_hash_mismatch"
    assert callable(conflicts.derive_preconditions)


def test_the_guard_catches_a_relapse_and_ignores_migrations(tmp_path):
    """O guarda serve para alguma coisa — e ignora exatamente o que deve ignorar."""
    (tmp_path / "migrations").mkdir()
    (tmp_path / "migrations" / "0005_ancoras.py").write_text("expected_anchors\n", encoding="utf-8")
    (tmp_path / "dominio.py").write_text("x = 1\nexpected_anchors = {}\n", encoding="utf-8")

    assert vestigios_em(tmp_path, "expected_anchors") == ["dominio.py:2"]
