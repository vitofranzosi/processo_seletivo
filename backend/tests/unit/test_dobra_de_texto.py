"""A dobra de acento e caixa (024, T-005).

Procurar por "informatica" e não achar "Informática" parece defeito de busca, não escolha de
sistema — e quem digita no celular quase nunca acentua.

**O que este arquivo também protege**: que a dobra continue sendo uma só. Ela já existia duas vezes
na árvore com finalidades diferentes, e a `011` registrou por escrito que duas implementações no
mesmo arquivo foram o defeito. A terceira cópia é o risco que o módulo compartilhado fecha.
"""

import pytest

from processo_seletivo.shared.texto import dobrar


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("Informática", "informatica"),
        ("INFORMÁTICA", "informatica"),
        ("informatica", "informatica"),
        ("Educação Física", "educacao fisica"),
        ("São Gonçalo do Amarante", "sao goncalo do amarante"),
        ("Técnico de Laboratório", "tecnico de laboratorio"),
        ("", ""),
    ],
)
def test_acento_e_caixa_deixam_de_distinguir(entrada, esperado):
    assert dobrar(entrada) == esperado


def test_a_dobra_e_idempotente():
    """Dobrar o que já foi dobrado não muda nada — é o que permite comparar os dois lados sem
    lembrar qual deles já passou por aqui."""
    uma_vez = dobrar("Especialização em Educação Profissional")

    assert dobrar(uma_vez) == uma_vez


def test_ausencia_nao_quebra():
    """`None` chega quando o conteúdo publicado não declarou o campo, e a busca não é lugar de
    descobrir isso por exceção."""
    assert dobrar(None) == ""
