"""A varredura das superfícies: **nenhuma** aceita semente, em nenhum verbo (SC-003, FR-017).

O `test_semente.py` afirma sobre as assinaturas dos comandos. Este afirma sobre as **superfícies** —
rotas e formulários —, que é o outro caminho por onde um valor entraria. A diferença importa: um
comando fechado com um formulário aberto continuaria deixando a semente entrar, e o defeito só
apareceria no dia do sorteio, ao vivo.

**A varredura é declarativa e derivada**, e não uma lista escrita à mão: ela percorre as rotas
registradas e os templates do módulo. Uma rota nova que aceite semente aparece aqui sozinha, sem
que ninguém se lembre de acrescentá-la.
"""

import inspect
import pathlib
import re

import pytest
from django.urls import get_resolver

from processo_seletivo.sorteios.infrastructure.fontes import FonteExterna

pytestmark = [pytest.mark.integration]

PROIBIDOS = re.compile(
    r"\b(semente|seed|chave_do_participante|ordem_manual|posicao_manual)\b", re.I
)
RAIZ = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo"


def _rotas_do_sorteio():
    """Toda rota cujo destino mora no módulo do sorteio, ou que fale de sorteio no nome."""
    encontradas = []
    for padrao in get_resolver().url_patterns:
        encontradas.extend(_descer(padrao, ""))
    return [
        (rota, destino)
        for rota, destino in encontradas
        if "sorteio" in rota or "sorteios" in getattr(destino, "__module__", "")
    ]


def _descer(padrao, prefixo):
    caminho = prefixo + str(getattr(padrao, "pattern", ""))
    if hasattr(padrao, "url_patterns"):
        saida = []
        for filho in padrao.url_patterns:
            saida.extend(_descer(filho, caminho))
        return saida
    return [(caminho, padrao.callback)]


def test_existem_rotas_de_sorteio_a_varrer():
    """Sem esta linha, uma varredura que não encontrasse nada passaria em silêncio."""
    assert _rotas_do_sorteio(), "a varredura não encontrou rota alguma do sorteio"


@pytest.mark.parametrize("caso", _rotas_do_sorteio(), ids=lambda caso: caso[0])
def test_nenhuma_rota_do_sorteio_nomeia_semente(caso):
    rota, destino = caso

    assert not PROIBIDOS.search(rota), rota
    fonte = inspect.getsource(destino) if inspect.isfunction(destino) else ""
    for linha in fonte.splitlines():
        # Comentário e docstring falam de semente o tempo todo — e devem falar. O que não pode
        # existir é **leitura de entrada** com esse nome.
        if "request." in linha or "POST" in linha or "GET" in linha:
            assert not PROIBIDOS.search(linha), linha.strip()


def test_nenhum_template_do_sorteio_tem_campo_de_semente():
    templates = [
        *(RAIZ / "interface" / "templates" / "interface").glob("sorteio*.html"),
        *(RAIZ / "portal" / "templates" / "portal").glob("*sorteio*.html"),
        *(RAIZ / "portal" / "templates" / "portal").glob("relacao*.html"),
    ]
    assert templates, "a varredura não encontrou template algum do sorteio"

    for template in templates:
        marcacao = template.read_text(encoding="utf-8")
        for entrada in re.findall(r'<(?:input|select|textarea)[^>]*name="([^"]+)"', marcacao):
            assert not PROIBIDOS.search(entrada), f"{template.name}: {entrada}"


def test_a_porta_da_fonte_devolve_material_bruto_e_nao_semente():
    """Nem o adaptador escolhe a semente: normalizar é regra do método (D-016)."""
    from processo_seletivo.sorteios.infrastructure.fontes import Observacao

    assert set(Observacao.__dataclass_fields__) == {
        "material_bruto",
        "indisponivel",
        "evidencia",
    }
    assert set(inspect.signature(FonteExterna.observar).parameters) == {
        "self",
        "fonte",
        "referencia",
    }
