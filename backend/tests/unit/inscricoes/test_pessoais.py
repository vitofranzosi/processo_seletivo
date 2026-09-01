"""CPF e telefone — o que é aceito, e por quê."""

import pytest

from processo_seletivo.inscricoes.domain.pessoais import (
    cpf_valido,
    formatar_cpf,
    formatar_telefone,
    telefone_valido,
)


@pytest.mark.parametrize("valor", ["123.456.789-09", "12345678909", "987.654.321-00"])
def test_cpf_com_verificadores_corretos_e_aceito(valor):
    assert cpf_valido(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "11111111111",
        "00000000000",
        "99999999999",
        "12345678900",
        "123",
        "",
        "abcdefghijk",
    ],
)
def test_cpf_inventado_e_recusado(valor):
    """Contar onze dígitos aceitava qualquer número.

    Sequências de dígito repetido passam no cálculo dos verificadores e nunca foram atribuídas a
    ninguém — por isso são recusadas à parte.
    """
    assert not cpf_valido(valor)


def test_o_cpf_e_guardado_numa_forma_so():
    assert formatar_cpf("12345678909") == "123.456.789-09"
    assert formatar_cpf("123.456.789-09") == "123.456.789-09"
    assert formatar_cpf("123 456 789 09") == "123.456.789-09"


@pytest.mark.parametrize("valor", ["", "  ", "27999990000", "(27) 99999-0000", "2733334444"])
def test_telefone_vazio_ou_com_ddd_e_aceito(valor):
    assert telefone_valido(valor)


@pytest.mark.parametrize("valor", ["28934", "9" * 200, "999999999"])
def test_o_que_nao_e_telefone_e_recusado(valor):
    assert not telefone_valido(valor)


def test_o_telefone_e_guardado_numa_forma_so():
    assert formatar_telefone("27999990000") == "(27) 99999-0000"
    assert formatar_telefone("2733334444") == "(27) 3333-4444"


def test_o_codigo_de_verificacao_muda_quando_o_comprovante_muda():
    """O código responde por **este** papel.

    Um comprovante é um HTML impresso: qualquer pessoa edita a página antes de imprimir e troca o
    nome, o protocolo ou a lista de documentos. Se o código não mudasse junto, não provaria nada.
    """
    from types import SimpleNamespace

    from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao

    def inscricao(protocolo="INS-2026-AAAA1111", modalidade="m1"):
        return SimpleNamespace(
            protocolo=protocolo,
            identity_subject="demo:abc",
            submitted_at=None,
            edital_id="e1",
            profile_id="p1",
            modality_id=modalidade,
        )

    documento = SimpleNamespace(requirement_id="r1", content_hash="a" * 64)
    outro = SimpleNamespace(requirement_id="r1", content_hash="b" * 64)
    base = codigo_de_verificacao(inscricao(), [documento])

    assert base == codigo_de_verificacao(inscricao(), [documento]), "mesmo fato, mesmo código"
    assert base != codigo_de_verificacao(inscricao(protocolo="INS-2026-BBBB2222"), [documento])
    assert base != codigo_de_verificacao(inscricao(modalidade="m2"), [documento])
    assert base != codigo_de_verificacao(inscricao(), [outro]), "trocar o arquivo muda o código"
    assert len(base) == 19 and base.count("-") == 3, "legível para transcrição humana"
