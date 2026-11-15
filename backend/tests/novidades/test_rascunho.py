"""O roteiro que rascunha as próximas notas (168, FR-7424, `D-008`), sem GitHub.

O que importa provar é o que o roteiro decide: o que é pendente — pela data do merge, e não pelo
número —, como agrupa, o que reconhece como só documentação, e que nenhum PR da janela fica sem
destino.
"""

import datetime
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "rascunhar_novidades", RAIZ / "scripts" / "rascunhar_novidades.py"
)
roteiro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(roteiro)

INICIO = datetime.date(2026, 11, 13)


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
    # Aberto antes, mergeado depois de todos: o caso que o corte pelo número perdia.
    _pr(530, "fix(portal): o antigo", "2026-11-14T23:00:00Z", ["backend/c.py"]),
    # Mergeado antes da janela: fora, qualquer que seja o número.
    _pr(546, "fora da janela", "2026-11-12T12:00:00Z", ["backend/d.py"]),
]


def _pendentes(citados=frozenset(), sem_nota=frozenset()):
    return roteiro.separar(PRS, INICIO, set(citados), set(sem_nota))


def test_o_pr_antigo_mergeado_depois_continua_pendente():
    """O defeito da primeira versão: o corte pelo maior número citado perdia o 530."""
    pendentes, _ = _pendentes(citados={545})
    assert 530 in {pr["number"] for pr in pendentes}


def test_a_janela_e_pela_data_do_merge_em_brasilia():
    pendentes, _ = _pendentes()
    numeros = {pr["number"] for pr in pendentes}
    assert 546 not in numeros
    # 02:30 UTC de 14/11 é 23:30 de 13/11 em Brasília: dentro da janela que começa em 13/11.
    assert 543 in numeros


def test_o_decidido_sai_do_rascunho_e_o_documental_e_contado_a_parte():
    pendentes, documentais = _pendentes(citados={545}, sem_nota={543})
    assert {pr["number"] for pr in pendentes} == {530}
    assert {pr["number"] for pr in documentais} == {542, 544}


def test_agrupa_pela_spec_da_branch_ou_do_titulo():
    pendentes, _ = _pendentes()
    assert list(roteiro.agrupar(pendentes)) == ["sem-spec-530", "165", "164"]


def test_numero_solto_no_titulo_nao_e_spec():
    assert roteiro.spec_do_pr({"title": "fix(ui): a ficha a 375 px", "headRefName": ""}) == ""
    assert roteiro.spec_do_pr({"title": "feat(152): o atalho", "headRefName": ""}) == "152"
    assert roteiro.spec_do_pr({"title": "143 — a convocação", "headRefName": ""}) == "143"
    pr = {"title": "Moldura dos e-mails", "headRefName": "claude/160-x"}
    assert roteiro.spec_do_pr(pr) == "160"


def test_lista_cheia_de_arquivos_nao_se_afirma_documental():
    assert not roteiro.so_documentacao(_pr(1, "x", "2026-11-13T12:00:00Z", ["doc/a.md"] * 100))


def test_o_esqueleto_leva_a_data_do_ultimo_merge_em_brasilia():
    pendentes, _ = _pendentes()
    texto = roteiro.rascunho(roteiro.agrupar(pendentes), INICIO, documentais=2)
    assert "data = 2026-11-13\n" in texto.split("## spec 164")[1]
    assert "prs = [545]" in texto
    assert "Só de documentação, fora do rascunho: 2." in texto


def test_avisa_quando_o_github_devolve_o_limite():
    assert roteiro.talvez_cortado(PRS, limite=len(PRS))
    assert not roteiro.talvez_cortado(PRS, limite=1000)
    texto = roteiro.rascunho({}, INICIO, cortado=True)
    assert texto.startswith("> **Atenção: a lista pode estar incompleta.**")
    assert "Nada pendente" in texto


def test_o_registro_real_se_le():
    inicio, citados, sem_nota = roteiro.ler_registro(
        roteiro.NOTAS.read_text(encoding="utf-8"), roteiro.REGISTRO.read_text(encoding="utf-8")
    )
    assert inicio == datetime.date(2026, 9, 15)
    assert citados and sem_nota
    assert not citados & sem_nota, "PR citado por nota e dispensado ao mesmo tempo"
