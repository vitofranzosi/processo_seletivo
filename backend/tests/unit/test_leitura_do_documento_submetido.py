"""O sistema não lê o conteúdo do que o candidato devolve (020, FR-047; 009, recusa original).

É um teste **estrutural**, e não de comportamento, porque a garantia é uma ausência: um teste de
comportamento mostraria que a leitura não acontece **naquele** fluxo, e a recusa vale para todos.

**É um guarda, e não uma demonstração.** Ele pega a implementação óbvia — a biblioteca importada, o
módulo que conhece os dois lados — e não pega uma leitura montada por abstrações espalhadas. Quem
quisesse burlá-lo conseguiria; o que ele impede é que alguém o faça **sem perceber**, que é como
uma recusa declarada costuma morrer.

O que é legítimo, e por isso não conta: abrir para **entregar** — a mesa e o titular recebem os
bytes — e calcular o resumo do que chegou, que é integridade e não leitura de conteúdo.
"""

import ast
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2] / "processo_seletivo"

# O que caracterizaria leitura de conteúdo: extrair texto, reconhecer caracteres, interpretar o
# PDF. Nenhuma dessas bibliotecas é dependência do projeto, e é isso que este teste trava.
LEITURA_DE_CONTEUDO = (
    "pypdf",
    "PyPDF2",
    "pdfminer",
    "pdfplumber",
    "fitz",
    "pytesseract",
    "PIL",
    "cv2",
)


@pytest.mark.contract
def test_nenhum_modulo_importa_biblioteca_de_leitura_de_pdf():
    culpados = []
    for arquivo in RAIZ.rglob("*.py"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
        for no in ast.walk(arvore):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [alias.name for alias in no.names]
            elif isinstance(no, ast.ImportFrom) and no.module:
                nomes = [no.module]
            for nome in nomes:
                if nome.split(".")[0] in LEITURA_DE_CONTEUDO:
                    culpados.append(f"{arquivo.relative_to(RAIZ)}: {nome}")
    assert culpados == [], (
        "leitura do conteúdo do documento do candidato é recusa declarada da `009`, e a `020` a "
        f"herda: {culpados}"
    )


@pytest.mark.contract
def test_o_documento_submetido_nao_e_comparado_com_o_modelo():
    """A comparação seria a porta de entrada da conformidade automática, que a D-004 recusa.

    Procura pelo par que só existiria se alguém a tivesse escrito: um módulo que conheça ao mesmo
    tempo o artefato do Anexo e os bytes do documento submetido.
    """
    suspeitos = []
    for arquivo in RAIZ.rglob("*.py"):
        texto = arquivo.read_text(encoding="utf-8")
        if "ArtefatoAnexo" in texto and "DocumentoSubmetido" in texto:
            suspeitos.append(str(arquivo.relative_to(RAIZ)))
    assert suspeitos == [], (
        "nenhum módulo precisa conhecer o modelo e o devolvido ao mesmo tempo — conformidade é "
        f"juízo da banca, e não do sistema: {suspeitos}"
    )
