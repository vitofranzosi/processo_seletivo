"""O código: seis dígitos de verdade, guardado sem volta, conferido sem vazar.

FR-022, FR-023 e FR-027.
"""

from processo_seletivo.identidade.domain import codigo as codigo_de_acesso


def test_tem_sempre_seis_digitos_inclusive_com_zeros_a_esquerda():
    for _ in range(200):
        valor = codigo_de_acesso.gerar()
        assert len(valor) == 6 and valor.isdigit()


def test_cobre_o_intervalo_inteiro():
    """Um gerador que nunca produz valores baixos entrega menos de um milhão de possibilidades."""
    valores = {codigo_de_acesso.gerar() for _ in range(400)}
    assert len(valores) > 300, "repetição demais para um intervalo de um milhão"
    assert min(valores) < "500000" and max(valores) > "500000"


def test_o_resumo_nao_carrega_o_codigo():
    valor = codigo_de_acesso.gerar()
    resumo = codigo_de_acesso.resumir(valor)
    assert valor not in resumo
    assert resumo != codigo_de_acesso.resumir(valor), "sem sal, dois resumos iguais denunciam"


def test_confere_o_codigo_certo_e_recusa_o_errado():
    valor = "012345"
    resumo = codigo_de_acesso.resumir(valor)
    assert codigo_de_acesso.confere(valor, resumo)
    assert not codigo_de_acesso.confere("012346", resumo)


def test_aceita_o_codigo_colado_com_separadores():
    """A pessoa cola como está na mensagem; recusar por causa de um espaço é erro nosso (UX-005)."""
    assert codigo_de_acesso.formato_aceitavel("012 345")
    assert codigo_de_acesso.normalizar("012-345") == "012345"
    assert not codigo_de_acesso.formato_aceitavel("01234")
    assert not codigo_de_acesso.formato_aceitavel("abcdef")
