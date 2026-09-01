"""A forma canônica do endereço — conservadora por decisão, e não por descuido (D-006).

O que se testa aqui é tanto o que a função faz quanto o que ela **se recusa** a fazer. Remover
pontos ou cortar sufixo funciona no Gmail e é falso em outros servidores, e fundir dois endereços
distintos numa credencial só é distinguível de tomada de identidade depois que já aconteceu.
"""

import pytest

from processo_seletivo.identidade.domain.enderecos import canonizar, endereco_aceitavel


@pytest.mark.parametrize(
    "informado,canonico",
    [
        ("Maria@Exemplo.TEST", "maria@exemplo.test"),
        ("  maria@exemplo.test  ", "maria@exemplo.test"),
        ("MARIA@EXEMPLO.TEST", "maria@exemplo.test"),
    ],
)
def test_baixa_a_caixa_do_endereco_inteiro(informado, canonico):
    """A parte local também. É suposição declarada na spec, não fato da norma (FR-012)."""
    assert canonizar(informado) == canonico


@pytest.mark.parametrize(
    "um,outro",
    [
        ("maria.silva@exemplo.test", "mariasilva@exemplo.test"),
        ("maria+vagas@exemplo.test", "maria@exemplo.test"),
        ("maria@exemplo.test", "maria@outro.test"),
    ],
)
def test_nao_funde_enderecos_distintos(um, outro):
    """Ponto, sufixo e domínio distinguem credenciais. Fundi-los seria conceder acesso alheio."""
    assert canonizar(um) != canonizar(outro)


@pytest.mark.parametrize("valor", ["maria@exemplo.test", "a@b.co"])
def test_aceita_endereco_de_forma_utilizavel(valor):
    assert endereco_aceitavel(valor)


@pytest.mark.parametrize("valor", ["", "maria", "maria@", "@exemplo.test", "maria exemplo.test"])
def test_recusa_endereco_malformado(valor):
    """A recusa é anterior a qualquer consulta, e por isso não revela nada (contrato de acesso)."""
    assert not endereco_aceitavel(valor)
