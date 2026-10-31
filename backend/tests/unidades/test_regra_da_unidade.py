"""A regra de uma Unidade, a mesma da semente, do cadastro e da edição (110, `D-005`, FR-3318)."""

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.domain.registro import validar_campos, validar_codigo

VALIDOS = {
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho": ["Campus Serra"],
    "local": "Serra (ES)",
    "atendimento": "",
}


def _recusa(funcao, *argumentos):
    with pytest.raises(DomainError) as recusa:
        funcao(*argumentos)
    return recusa.value


@pytest.mark.parametrize("codigo", ["serra", "campus-serra", "reitoria", "c1"])
def test_codigo_no_formato_passa_como_foi_digitado(codigo):
    assert validar_codigo(codigo) == codigo


@pytest.mark.parametrize(
    "codigo",
    ["Serra", " serra", "serra ", "campus serra", "serra_campus", "-serra", "a--b", "", "serra\n"],
)
def test_caixa_e_espaco_no_codigo_sao_recusados_sem_conversao(codigo):
    """EC-1: o código é permanente, e uma conversão silenciosa decidiria por quem cadastra."""
    recusa = _recusa(validar_codigo, codigo)
    assert (recusa.code, recusa.campo) == ("codigo_invalido", "codigo")


def test_codigo_longo_demais_e_recusado():
    assert _recusa(validar_codigo, "a" * 101).code == "codigo_invalido"


def test_codigo_institucional_e_recusado():
    """FR-3317: o escopo dos vínculos institucionais não pode virar unidade."""
    recusa = _recusa(validar_codigo, "institucional")
    assert (recusa.code, recusa.campo) == ("codigo_reservado", "codigo")


def test_espacos_das_pontas_sao_aparados():
    """EC-4."""
    valores = validar_campos(
        {
            "sigla": " Serra ",
            "nome": " Campus Serra",
            "cabecalho": [" Campus Serra "],
            "local": "Serra (ES) ",
            "atendimento": " serra@ifes.edu.br ",
        }
    )
    assert valores == {
        "sigla": "Serra",
        "nome": "Campus Serra",
        "cabecalho": ["Campus Serra"],
        "local": "Serra (ES)",
        "atendimento": "serra@ifes.edu.br",
    }


@pytest.mark.parametrize(
    "campo, valor, codigo",
    [
        ("sigla", "", "campo_obrigatorio"),
        ("sigla", "x" * 31, "campo_obrigatorio"),
        ("nome", "   ", "campo_obrigatorio"),
        ("local", None, "campo_obrigatorio"),
        ("cabecalho", [], "cabecalho_invalido"),
        ("cabecalho", ["um", "dois", "três"], "cabecalho_invalido"),
        ("cabecalho", ["", "dois"], "cabecalho_invalido"),
        ("cabecalho", "Campus Serra", "cabecalho_invalido"),
        ("atendimento", "linha\noutra", "atendimento_invalido"),
        ("atendimento", "tab\tno meio", "atendimento_invalido"),
        # Nenhum campo da unidade é de várias linhas: o compositor não as divide (revisão do #352).
        ("sigla", "Se\nrra", "campo_obrigatorio"),
        ("nome", "Campus\rSerra", "campo_obrigatorio"),
        ("local", "Serra\n(ES)", "campo_obrigatorio"),
        ("cabecalho", ["Campus\nSerra"], "cabecalho_invalido"),
        ("atendimento", "x" * 256, "atendimento_invalido"),
    ],
)
def test_cada_recusa_diz_o_campo(campo, valor, codigo):
    recusa = _recusa(validar_campos, {**VALIDOS, campo: valor})
    assert (recusa.code, recusa.campo) == (codigo, campo)


def test_canal_vazio_e_nao_declarado():
    """EC-12: vazio volta ao canal da instituição, pela regra da 109."""
    assert validar_campos({**VALIDOS, "atendimento": "   "})["atendimento"] == ""
    assert (
        validar_campos({k: v for k, v in VALIDOS.items() if k != "atendimento"})["atendimento"]
        == ""
    )


def test_a_quebra_so_nas_pontas_do_canal_e_aparada():
    """Como os outros campos: o que está nas pontas é espaço, e sai antes de conferir."""
    assert validar_campos({**VALIDOS, "atendimento": "canal@ifes.edu.br\n"})["atendimento"] == (
        "canal@ifes.edu.br"
    )
