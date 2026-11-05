"""Carga horária e contato nos textos e na conferência automática (119, FR-3813, FR-3812)."""

import dataclasses

from processo_seletivo.interface import kit_peca, kit_textos
from tests.unit.kit.test_textos import QUATRO_POLOS, _ficha, _oferta

TRES_CURSOS = (
    dataclasses.replace(_oferta("1", "Assistente Administrativo", "", 30), carga_horaria="180h"),
    _oferta("2", "Auxiliar de Biblioteca", "", 30),
    dataclasses.replace(_oferta("3", "Libras Básico", "", 30), carga_horaria="60 horas"),
)


def _com_cursos(**mudar):
    return _ficha(ofertas=TRES_CURSOS, nomes_iguais=False, total_de_vagas=90, **mudar)


def test_cada_opcao_listada_traz_a_carga_declarada_e_so_ela():
    linhas = kit_textos.linhas_da_oferta(_com_cursos())
    assert linhas == [
        "Assistente Administrativo — 180h: 30 vagas",
        "Auxiliar de Biblioteca: 30 vagas",
        "Libras Básico — 60 horas: 30 vagas",
    ]
    textos = kit_textos.compor(_com_cursos())
    assert "• Assistente Administrativo — 180h: 30 vagas" in textos["legenda"]
    assert (
        "Carga horária: Assistente Administrativo — 180h; Libras Básico — 60 horas."
        in (textos["texto_para_mensagem"])
    )


def test_opcao_unica_leva_a_carga_na_frase_da_oferta():
    ficha = _ficha(ofertas=TRES_CURSOS[:1], nomes_iguais=False, total_de_vagas=30)
    assert "Oferta: Assistente Administrativo — 180h: 30 vagas." in _tudo(ficha)


def test_sem_carga_declarada_nada_e_acrescentado():
    textos = kit_textos.compor(_ficha())
    assert "Carga horária" not in "\n".join(textos.values())
    assert all(" — " not in linha for linha in kit_textos.linhas_da_oferta(_ficha()))
    assert QUATRO_POLOS[0].carga_horaria == ""


def test_contato_na_legenda_na_mensagem_e_na_conferencia_quando_declarado():
    ficha = _ficha(contato="cefor@ifes.example — (27) 3333-0000")
    textos = kit_textos.compor(ficha)
    assert "Dúvidas? cefor@ifes.example — (27) 3333-0000" in textos["legenda"]
    assert textos["texto_para_mensagem"].endswith("Dúvidas? cefor@ifes.example — (27) 3333-0000")
    (linha,) = [x for x in kit_textos.conferencia(ficha) if x.startswith("Contato:")]
    assert "cadastro da unidade" in linha


def test_sem_contato_nenhuma_linha_de_contato():
    assert "Dúvidas?" not in _tudo(_ficha())
    assert not [x for x in kit_textos.conferencia(_ficha()) if x.startswith("Contato:")]


def _tudo(ficha):
    return "\n".join(kit_textos.compor(ficha).values())


@dataclasses.dataclass(frozen=True)
class _Peca:
    textos: tuple


def _texto(campo, conteudo):
    return kit_peca.Texto(0, 0, conteudo, 24, "edital-sans-regular", campo, "#000000", "#ffffff")


def test_a_conferencia_cobre_carga_e_contato_da_peca():
    ficha = _com_cursos(contato="cefor@ifes.example")
    textos = kit_textos.compor(ficha)
    coerente = _Peca(
        (
            _texto("carga_horaria:1", "180h"),
            _texto("contato", "Dúvidas? cefor@ifes.example"),
        )
    )
    assert kit_peca.fora_dos_textos(coerente, textos) == []
    incoerente = _Peca((_texto("carga_horaria:9", "999h"), _texto("contato", "Dúvidas? x@y")))
    assert kit_peca.fora_dos_textos(incoerente, textos) == ["999h", "x@y"]
