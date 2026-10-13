"""Nenhum módulo dos avisos abre conexão de correio por conta própria (066, `FR-1281`, SC-488).

**É o que garante que a suíte nunca alcança servidor real.** O Django troca o mecanismo de correio
pelo de memória em `setup_test_environment`, e o despacho é alcançado por essa troca porque abre a
conexão por `get_connection()` — o mecanismo configurado. Um `smtplib.SMTP(...)` direto, um
`get_connection(backend=...)` ou um backend instanciado à mão escapariam dela: a suíte passaria
a mandar e-mail de verdade, e o primeiro sinal seria a caixa de alguém.

**A varredura lê a árvore sintática, e não o texto**: o `smtplib` é importado de propósito em
`avisos/domain/resposta.py`, para classificar as exceções dele, e citar é diferente de conectar.
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
MODULOS = sorted((RAIZ / "avisos").rglob("*.py")) + [RAIZ / "interface/avisos.py"]

#: Chamadas que abrem conexão de correio fora do mecanismo configurado.
CONEXAO_DIRETA = {"SMTP", "SMTP_SSL", "LMTP"}


def _nome(funcao):
    if isinstance(funcao, ast.Attribute):
        return funcao.attr
    if isinstance(funcao, ast.Name):
        return funcao.id
    return ""


def conexoes_proprias(codigo):
    """As chamadas do código que contornariam o mecanismo de correio configurado."""
    achados = []
    for no in ast.walk(ast.parse(codigo)):
        if not isinstance(no, ast.Call):
            continue
        nome = _nome(no.func)
        if nome in CONEXAO_DIRETA:
            achados.append(f"{nome}(...) na linha {no.lineno}")
        elif nome == "get_connection" and (
            no.args or any(chave.arg == "backend" for chave in no.keywords)
        ):
            achados.append(f"get_connection com backend escolhido na linha {no.lineno}")
        elif nome.endswith("EmailBackend"):
            achados.append(f"{nome}(...) instanciado na linha {no.lineno}")
    return achados


def test_os_modulos_dos_avisos_usam_so_o_mecanismo_configurado():
    achados = {
        str(modulo.relative_to(RAIZ)): conexoes_proprias(modulo.read_text(encoding="utf-8"))
        for modulo in MODULOS
    }

    assert {modulo: lista for modulo, lista in achados.items() if lista} == {}


def test_a_varredura_enxerga_o_que_procura():
    """A prova de que o detector ainda funciona — sem escrever o padrão em código de produção."""
    assert conexoes_proprias("import smtplib\nsmtplib.SMTP('x', 25)\n")
    assert conexoes_proprias("get_connection(backend='django.core.mail.backends.smtp.X')\n")
    assert conexoes_proprias("get_connection('django.core.mail.backends.smtp.EmailBackend')\n")
    assert conexoes_proprias("EmailBackend(host='x')\n")
    assert not conexoes_proprias("import smtplib\nerro = smtplib.SMTPDataError(451, b'x')\n")
    assert not conexoes_proprias("conexao = get_connection()\n")


def test_o_despacho_abre_pelo_mecanismo_configurado():
    codigo = (RAIZ / "avisos/application/despacho.py").read_text(encoding="utf-8")

    assert "get_connection()" in codigo
