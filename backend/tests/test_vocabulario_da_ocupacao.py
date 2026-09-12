"""Nenhuma superfície da `016` afirma que alguém foi convocado, aceitou ou se matriculou.

**Por que existe.** A fronteira com a `019` é a frase mais fácil de atravessar sem perceber. A
ocupação diz **quantas vagas estão ocupadas**; quem foi chamado, quem aceitou e quem se matriculou
são fatos que esta feature não tem e não pode inventar — ela conta quem está na faixa e habilitado,
e nada mais. Uma legenda escrita com pressa transforma "ocupou" em "foi convocado", e quem lê a tela
lê a palavra, não a spec.

É o irmão simétrico de `test_vocabulario_do_corte.py`: lá a `014` não pode falar de ocupação; aqui a
`016` não pode falar de convocação. As duas varreduras juntas guardam as duas fronteiras do arco.

**Comentário não é afirmação.** Explicar por que uma palavra está proibida exige escrevê-la, e por
isso a varredura lê o texto **sem** comentário e sem docstring — o mesmo critério do precedente.

**A proibição estrutural da `FR-257` não mora aqui.** Varredura de texto prova que a tela não *diz*
que ordenou; não prova que nenhum caminho *ordena*. Isso é prova de import, e está em
`test_dependencia_da_ocupacao.py`.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"

# A tela da feature, e os módulos que produzem o que ela e a API dizem.
DA_016 = [
    TEMPLATES / "ocupacao.html",
    RAIZ / "ocupacao/application/emissao.py",
    RAIZ / "ocupacao/application/movimento.py",
    RAIZ / "ocupacao/application/selectors.py",
    RAIZ / "ocupacao/application/causar_faixa.py",
    RAIZ / "ocupacao/domain/apuracao.py",
    RAIZ / "ocupacao/domain/reversao.py",
]

# Cada termo com o que ele afirmaria indevidamente. A mensagem entra na falha, para que quem a
# receba entenda a fronteira em vez de só remover a palavra.
PROIBIDOS = {
    r"convoca[çc]": "convocar e comunicar é da 019; esta feature só conta vaga",
    r"convocad": "idem — e o particípio é o mais fácil de escrever sem perceber",
    r"\baceite\b": "aceite é fato da 019, e a ocupação não o conhece",
    r"matr[íi]cul": "matrícula é fato da 019",
    r"desist[êe]nci": "desistência é fato da 019 — e é o que torna metade do 8.8 do 28/2026 "
    "inalcançável hoje",
    r"chamada de suplente": "suplência e chamada são da 019",
}

SEM_COMENTARIO = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}|^\s*#.*$|\"\"\".*?\"\"\"",
    re.S | re.M,
)


def visivel(caminho):
    """O arquivo sem comentário e sem docstring: o que ele de fato afirma a quem o lê na tela."""
    return SEM_COMENTARIO.sub(" ", caminho.read_text())


@pytest.mark.parametrize("caminho", DA_016, ids=lambda item: item.name)
def test_nenhuma_superficie_da_016_afirma_o_que_ela_nao_conhece(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]
    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_varredura_enxerga_um_termo_proibido():
    """Uma expressão que deixa de casar não falha: ela aprova tudo, calada."""
    corpo = "a tela dizia que o candidato foi convocado".lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == [r"convocad"]


def test_a_varredura_descarta_comentario_e_docstring(tmp_path):
    """Sem isto, a prosa que explica a fronteira reprovaria a si própria."""
    arquivo = tmp_path / "sintetico.py"
    arquivo.write_text(
        '"""A convocação é da 019."""\n'
        "# matrícula também é dela\n"
        "def contar():\n"
        "    return 'vagas a ocupar'\n"
    )

    corpo = visivel(arquivo).lower()

    assert [termo for termo in PROIBIDOS if re.search(termo, corpo)] == []
