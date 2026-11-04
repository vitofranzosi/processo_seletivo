"""As fontes da peça: registro, repertório e recusa por caractere sem glifo (119, FR-3823, EC-13).

A Edital Sans é a primeira fonte do kit e é a do Edital: o caso que mede as duas métricas lado a
lado prova que a generalização não mudou a largura de nenhum caractere da peça Institucional.
"""

import hashlib
import re
from pathlib import Path

import pytest

from processo_seletivo.interface import kit_fontes, kit_peca
from processo_seletivo.publicacoes.infrastructure import fonte
from tests.unit.kit.test_textos import _ficha

ORIGEM = Path(kit_fontes.PASTA) / "ORIGEM.md"
LINHA = re.compile(r"^\| `([^`]+)` \| ([^|]+) \| (\d+) \| ([^|]+) \| [^|]+ \| `([0-9a-f]{64})` \|$")


def _registro():
    """`{arquivo: (família, peso, licença, sha256)}` da tabela do `ORIGEM.md`."""
    linhas = ORIGEM.read_text(encoding="utf-8").splitlines()
    registro = {}
    for linha in linhas:
        casou = LINHA.match(linha)
        if casou:
            arquivo, familia, peso, licenca, resumo = casou.groups()
            registro[arquivo] = (familia.strip(), int(peso), licenca.strip(), resumo)
    return registro


def test_toda_fonte_do_kit_tem_linha_no_origem_com_o_mesmo_resumo():
    registro = _registro()
    assert registro, "a tabela do ORIGEM.md não foi lida"
    for item in kit_fontes.FONTES.values():
        assert item.arquivo in registro, f"{item.arquivo} sem linha no ORIGEM.md"
        familia, peso, licenca, resumo = registro[item.arquivo]
        assert (familia, peso) == (item.familia, item.peso)
        assert licenca == "SIL OFL 1.1"
        assert resumo == item.sha256
    assert set(registro) == {item.arquivo for item in kit_fontes.FONTES.values()}


def test_os_arquivos_sao_os_registrados():
    assert kit_fontes.conferir() == {}
    for item in kit_fontes.FONTES.values():
        assert hashlib.sha256(item.caminho.read_bytes()).hexdigest() == item.sha256


@pytest.mark.parametrize("chave", kit_fontes.FONTES)
def test_cada_fonte_cobre_o_repertorio_da_grafia(chave):
    assert kit_fontes.sem_glifo("".join(kit_fontes.repertorio()), chave) == []


@pytest.mark.parametrize(
    ("chave", "recurso"),
    [("edital-sans-regular", fonte.REGULAR), ("edital-sans-negrito", fonte.NEGRITO)],
)
def test_a_edital_sans_mede_no_kit_o_que_mede_no_edital(chave, recurso):
    """Caractere a caractere, e a altura das linhas: a peça Institucional não mudou de medida."""
    do_edital = fonte.fontes()[recurso]
    do_kit = kit_fontes.medidas(chave)
    for caractere in kit_fontes.repertorio():
        assert kit_fontes.METRICA.largura(caractere, 1000, chave) == fonte.METRICA.largura(
            caractere, 1000, recurso
        ), caractere
    assert (do_kit.ascendente, do_kit.descendente) == (do_edital.ascendente, do_edital.descendente)
    assert do_kit.dados == do_edital.dados


def test_o_rasterizador_recebe_os_arquivos_da_familia():
    chaves = kit_peca.fontes_da_peca(kit_peca.compor(_ficha()))
    assert chaves == ("edital-sans-regular", "edital-sans-negrito")
    assert kit_fontes.arquivos(chaves) == tuple(
        str(fonte.PASTA / arquivo) for arquivo in fonte.ARQUIVOS.values()
    )


def test_caractere_sem_glifo_na_fonte_da_familia_recusa_nomeando_caractere_e_fonte(monkeypatch):
    """A grafia admite «é», e a fonte, numa cópia sem o glifo, não o desenha (EC-13)."""
    original = kit_fontes.medidas

    def sem_e_agudo(chave):
        medidas = original(chave)
        larguras = {c: v for c, v in medidas.larguras.items() if c != "é"}
        return kit_fontes.Medidas(medidas.dados, larguras, medidas.ascendente, medidas.descendente)

    monkeypatch.setattr(kit_fontes, "medidas", sem_e_agudo)
    with pytest.raises(kit_peca.PecaRecusada) as recusa:
        kit_peca.compor(_ficha(identificacao="Edital nº 91/2026 – Técnico"))
    assert "Edital Sans" in recusa.value.motivo
    assert "«é»" in recusa.value.motivo and "U+00E9" in recusa.value.motivo
