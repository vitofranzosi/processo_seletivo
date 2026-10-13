"""A cópia do corpus é a que o LEIA-ME diz (070, T003).

O resumo de cada `pubN-canonico.json` é o `content_hash` que o documento publicado imprime: conferir
o arquivo é conferir que o teste roda sobre o conteúdo que o fluxo real publicou, e não sobre uma
versão editada à mão.
"""

import hashlib
import re

import pytest

from tests.fixtures.corpus import PASTA

RESUMOS = dict(
    re.findall(r"\| `([^`]+\.json)` \| `([0-9a-f]{64})` \|", (PASTA / "LEIA-ME.md").read_text())
)


def test_o_leia_me_lista_todo_arquivo_do_corpus():
    arquivos = sorted(str(p.relative_to(PASTA)) for p in PASTA.glob("*/*.json"))
    assert arquivos == sorted(RESUMOS)


@pytest.mark.parametrize("arquivo", sorted(RESUMOS))
def test_o_arquivo_e_o_publicado(arquivo):
    assert hashlib.sha256((PASTA / arquivo).read_bytes()).hexdigest() == RESUMOS[arquivo]
