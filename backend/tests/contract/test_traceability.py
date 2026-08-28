"""T093 — a matriz de rastreabilidade só vale enquanto suas referências forem verdadeiras.

Uma matriz que cita teste inexistente é pior que nenhuma: afirma cobertura que ninguém tem.
Estes testes falham quando um teste citado é renomeado ou removido, e quando a matriz deixa de
cobrir algum FR, cenário ou critério da especificação vigente.
"""

import re
from pathlib import Path

import pytest

SPEC_DIR = Path(__file__).resolve().parents[3] / "specs" / "001-processo-seletivo-editais"
MATRIX = SPEC_DIR / "traceability.md"
SPEC = SPEC_DIR / "spec.md"
TESTS_ROOT = Path(__file__).resolve().parents[1]

TEST_REFERENCE = re.compile(r"`(tests/[\w/]+\.py)::(\w+)`")
FR_IN_MATRIX = re.compile(r"^\| (FR-\d{3}) \|", re.MULTILINE)
SC_IN_MATRIX = re.compile(r"^\| (SC-\d{3}) \|", re.MULTILINE)
FR_IN_SPEC = re.compile(r"\*\*(FR-\d{3})(?: \(deferred\))?\*\*")
SC_IN_SPEC = re.compile(r"\*\*(SC-\d{3})(?: \(deferred\))?\*\*")


@pytest.fixture(scope="module")
def matrix():
    assert MATRIX.exists(), "T093 exige specs/001-processo-seletivo-editais/traceability.md"
    return MATRIX.read_text(encoding="utf-8")


def test_every_referenced_test_exists(matrix):
    """Cada `arquivo::teste` citado precisa existir com esse nome."""
    ausentes = []
    for arquivo, nome in TEST_REFERENCE.findall(matrix):
        caminho = TESTS_ROOT.parent / arquivo
        if not caminho.exists():
            ausentes.append(f"{arquivo} (arquivo inexistente)")
            continue
        if not re.search(rf"^def {re.escape(nome)}\(", caminho.read_text(encoding="utf-8"), re.M):
            ausentes.append(f"{arquivo}::{nome}")
    assert not ausentes, f"a matriz cita testes que não existem: {sorted(set(ausentes))}"


def test_matrix_covers_every_requirement_of_the_current_spec(matrix):
    especificados = set(FR_IN_SPEC.findall(SPEC.read_text(encoding="utf-8")))
    listados = set(FR_IN_MATRIX.findall(matrix))
    assert especificados, "nenhum FR encontrado na especificação"
    assert not especificados - listados, f"FRs fora da matriz: {sorted(especificados - listados)}"
    assert not listados - especificados, (
        f"FRs inexistentes na spec: {sorted(listados - especificados)}"
    )


def test_matrix_covers_every_success_criterion_of_the_current_spec(matrix):
    especificados = set(SC_IN_SPEC.findall(SPEC.read_text(encoding="utf-8")))
    listados = set(SC_IN_MATRIX.findall(matrix))
    assert especificados, "nenhum SC encontrado na especificação"
    assert not especificados - listados, f"SCs fora da matriz: {sorted(especificados - listados)}"


def test_matrix_marks_the_deferred_items_as_deferred(matrix):
    """FR-037 e SC-002/009/010 não integram os critérios de aceite deste incremento."""
    for identificador in ("FR-037", "SC-002", "SC-009", "SC-010"):
        linha = next(
            line for line in matrix.splitlines() if line.startswith(f"| {identificador} |")
        )
        assert "Diferido" in linha, f"{identificador} deveria constar como diferido"


def test_matrix_declares_a_situation_for_every_row(matrix):
    """Nenhuma linha pode ficar sem veredito — é o que separa a matriz de uma lista de links."""
    situacoes = {"Coberto", "Parcial", "Diferido"}
    sem_veredito = [
        line
        for line in matrix.splitlines()
        if re.match(r"^\| (?:FR|SC)-\d{3} \|", line)
        and not any(situacao in line.rsplit("|", 2)[-2] for situacao in situacoes)
    ]
    assert not sem_veredito, f"linhas sem situação declarada: {sem_veredito}"
