"""O mascaramento simples do piloto, e o que ele não é (071, `R-015`, `FR-1509`)."""

from processo_seletivo.duvidas.domain.mascara import (
    mascarar,
    mascarar_resposta,
    tem_padrao_pessoal,
)


def test_os_tres_padroes_sao_mascarados():
    texto = "Meu CPF é 123.456.789-09, e-mail maria@exemplo.test, telefone (27) 99999-1234."

    assert mascarar(texto) == "Meu CPF é [CPF], e-mail [e-mail], telefone [telefone]."


def test_cpf_sem_pontuacao_tambem():
    assert mascarar("cpf 12345678909") == "cpf [CPF]"


def test_nome_por_extenso_passa_e_por_isso_nao_e_anonimizacao():
    """O limite declarado: o que não é um dos três padrões chega inteiro ao registro."""
    texto = "Sou Maria da Silva, moro na Rua das Flores, e fui eliminada."

    assert mascarar(texto) == texto
    assert not tem_padrao_pessoal(texto)


def test_datas_e_numeros_do_edital_nao_sao_telefone():
    texto = "As inscrições vão até 04/11/2026, às 23h59; são 45 vagas no Edital 91/2026."

    assert mascarar(texto) == texto


def test_a_resposta_so_mascara_o_cpf():
    """E-mail e telefone numa resposta conferida estão numa fonte citada: são o canal publicado."""
    resposta = "Escreva para selecao.demo@exemplo.ifes.edu.br; não informe o CPF 123.456.789-09."

    assert mascarar_resposta(resposta) == (
        "Escreva para selecao.demo@exemplo.ifes.edu.br; não informe o CPF [CPF]."
    )
