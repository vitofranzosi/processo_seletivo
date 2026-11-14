"""O roteiro que rascunha as próximas notas (168, FR-7424, `D-008`), sem GitHub.

O que importa provar é o que o roteiro decide: de onde começa, como agrupa, o que marca como só
documentação, e que ele não toca o arquivo das notas.
"""

import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "rascunhar_novidades", RAIZ / "scripts" / "rascunhar_novidades.py"
)
roteiro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(roteiro)


def _pr(numero, titulo, quando, arquivos, branch=""):
    return {
        "number": numero,
        "title": titulo,
        "mergedAt": quando,
        "headRefName": branch,
        "files": [{"path": caminho} for caminho in arquivos],
    }


PRS = [
    _pr(544, "docs(implantação): referências", "2026-11-14T20:00:00Z", ["doc/x.md"]),
    _pr(545, "Spec 165: as regras", "2026-11-14T22:00:00Z", ["backend/a.py", "specs/165/spec.md"]),
    _pr(543, "Spec 164: o efeito", "2026-11-14T02:30:00Z", ["backend/b.py"]),
    _pr(542, "plano", "2026-11-13T12:00:00Z", ["specs/163/plan.md"], "claude/163-alcance"),
    _pr(530, "antigo", "2026-11-13T12:00:00Z", ["backend/c.py"]),
]


def test_comeca_depois_do_maior_pr_citado():
    assert roteiro.maior_pr_citado(roteiro.ARQUIVO.read_text(encoding="utf-8")) >= 533
    assert roteiro.maior_pr_citado("[[nota]]\nprs = [12, 540]\n[[nota]]\nprs = [7]\n") == 540
    grupos = roteiro.agrupar(PRS, 540)
    assert 530 not in {pr["number"] for prs in grupos.values() for pr in prs}


def test_agrupa_pela_spec_do_titulo_ou_da_branch():
    grupos = roteiro.agrupar(PRS, 540)
    assert list(grupos) == ["165", "sem-spec-544", "164", "163"]


def test_marca_o_que_so_toca_documentacao_e_nao_lhe_da_esqueleto():
    texto = roteiro.rascunho(roteiro.agrupar(PRS, 540), 540)
    assert "#544 (14/11) docs(implantação): referências — *só documentação" in texto
    assert "#542 (13/11) plano — *só documentação" in texto
    # O 163 só tem plano: nenhum esqueleto de nota para ele.
    secao_163 = texto.split("## spec 163")[1]
    assert "[[nota]]" not in secao_163


def test_a_data_do_esqueleto_e_a_do_ultimo_merge_em_brasilia():
    texto = roteiro.rascunho(roteiro.agrupar(PRS, 540), 540)
    # 02:30 UTC de 14/11 é 23:30 de 13/11 em Brasília.
    assert "data = 2026-11-13\n" in texto.split("## spec 164")[1]
    assert "prs = [545]" in texto
