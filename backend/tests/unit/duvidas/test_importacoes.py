"""A fonte de consulta não importa o compositor do documento nem o canal do candidato (`R-009`).

**Por que um guardião, e não disciplina.** As frases do compositor não estão no conteúdo publicado e
mudam com o código: a `067` e a `068` as reescreveram, e a `069` vai reescrevê-las. Uma importação
delas faria a explicação mudar junto com o PDF de amanhã, e citá-las como texto do Edital seria
afirmar sobre os documentos antigos o que eles não dizem (`FR-1434`). O `portal` é o canal do
candidato; o domínio não depende de canal (`R-007`).
"""

import ast
from pathlib import Path

PACOTE = Path(__file__).resolve().parents[3] / "processo_seletivo" / "duvidas"

PROIBIDOS = (
    "processo_seletivo.publicacoes.infrastructure.pdf",
    "processo_seletivo.publicacoes.domain.vocabulario_da_regra",
    "processo_seletivo.sorteios.domain.prosa",
    "processo_seletivo.portal",
)


def importados(fonte: str):
    nomes = []
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.Import):
            nomes.extend(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.append(no.module)
            nomes.extend(f"{no.module}.{alias.name}" for alias in no.names)
    return nomes


def proibidos_em(fonte: str):
    return sorted(
        {
            nome
            for nome in importados(fonte)
            for proibido in PROIBIDOS
            if nome == proibido or nome.startswith(proibido + ".")
        }
    )


def test_nenhum_modulo_do_pacote_importa_o_compositor_nem_o_portal():
    modulos = sorted(PACOTE.rglob("*.py"))
    assert len(modulos) >= 10, "a varredura precisa alcançar os módulos do pacote"
    achados = {str(m.relative_to(PACOTE)): proibidos_em(m.read_text()) for m in modulos}
    assert {modulo: nomes for modulo, nomes in achados.items() if nomes} == {}


def test_o_guardiao_enxerga_a_importacao_proibida():
    sintetico = (
        "from processo_seletivo.publicacoes.infrastructure import pdf\n"
        "from processo_seletivo.publicacoes.domain.vocabulario_da_regra import X\n"
        "import processo_seletivo.portal.views\n"
    )
    assert proibidos_em(sintetico) == [
        "processo_seletivo.portal.views",
        "processo_seletivo.publicacoes.domain.vocabulario_da_regra",
        "processo_seletivo.publicacoes.domain.vocabulario_da_regra.X",
        "processo_seletivo.publicacoes.infrastructure.pdf",
    ]
