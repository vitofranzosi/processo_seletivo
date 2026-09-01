"""O que se aceita como documento, e como se recusa o que não se aceita (US4, FR-045 a FR-047).

O teste que importa aqui não é o do PDF válido: é o da recusa. Um "arquivo inválido" seco manda a
pessoa adivinhar, e o caso mais provável de todos — a foto que o celular tirou do documento — tem
uma explicação de uma frase que resolve o problema.
"""

import io

import pytest

from processo_seletivo.inscricoes.domain.arquivos import aceitar, resumo
from processo_seletivo.shared.api.problems import DomainError

LIMITE = 10 * 1024 * 1024


class Arquivo(io.BytesIO):
    """O mínimo que a camada usa de um upload: conteúdo, tamanho e nome."""

    def __init__(self, conteudo, nome="documento.pdf"):
        super().__init__(conteudo)
        self.size = len(conteudo)
        self.name = nome


def pdf(corpo=b"conteudo do documento"):
    return Arquivo(b"%PDF-1.4\n" + corpo)


def test_pdf_com_extensao_correta_passa():
    aceitar(pdf(), nome_original="diploma.pdf", limite_em_bytes=LIMITE)


def test_arquivo_acima_do_limite_diz_o_tamanho_e_o_limite():
    grande = Arquivo(b"%PDF-1.4\n" + b"x" * 2048, "diploma.pdf")

    with pytest.raises(DomainError) as recusa:
        aceitar(grande, nome_original="diploma.pdf", limite_em_bytes=1024)

    assert recusa.value.code == "file_too_large"
    assert "limite" in recusa.value.detail


def test_o_limite_vem_da_configuracao_e_nao_do_codigo():
    """FR-046: mudar o limite não pode ser mexer em código."""
    arquivo = Arquivo(b"%PDF-1.4\n" + b"x" * 500, "diploma.pdf")

    aceitar(arquivo, nome_original="diploma.pdf", limite_em_bytes=10_000)
    with pytest.raises(DomainError):
        aceitar(arquivo, nome_original="diploma.pdf", limite_em_bytes=100)


def test_arquivo_vazio_e_recusado():
    with pytest.raises(DomainError) as recusa:
        aceitar(Arquivo(b"", "vazio.pdf"), nome_original="vazio.pdf", limite_em_bytes=LIMITE)

    assert recusa.value.code == "file_empty"


@pytest.mark.parametrize(
    ("cabecalho", "formato"),
    [
        (b"\xff\xd8\xff\xe0" + b"0" * 20, "JPEG"),
        (b"\x89PNG\r\n\x1a\n" + b"0" * 20, "PNG"),
        (b"\x00\x00\x00\x18ftypheic" + b"0" * 20, "HEIC"),
    ],
)
def test_imagem_renomeada_para_pdf_recebe_recusa_que_ensina(cabecalho, formato):
    """FR-047: é o que o celular produz, e é o caso que precisa de instrução, não de diagnóstico."""
    with pytest.raises(DomainError) as recusa:
        aceitar(
            Arquivo(cabecalho, "documento.pdf"),
            nome_original="documento.pdf",
            limite_em_bytes=LIMITE,
        )

    assert recusa.value.code == "file_is_an_image"
    assert formato in recusa.value.detail
    assert "converta" in recusa.value.detail.lower()
    assert "celular" in recusa.value.detail.lower()


def test_conteudo_que_nao_e_pdf_nem_imagem_recebe_recusa_generica():
    with pytest.raises(DomainError) as recusa:
        aceitar(
            Arquivo(b"PK\x03\x04planilha", "documento.pdf"),
            nome_original="documento.pdf",
            limite_em_bytes=LIMITE,
        )

    assert recusa.value.code == "file_not_pdf"


def test_pdf_com_extensao_errada_e_recusado_dizendo_o_que_fazer():
    """A extensão é conferida **e** o conteúdo: renomear arquivo é a coisa mais fácil do mundo."""
    with pytest.raises(DomainError) as recusa:
        aceitar(pdf(), nome_original="diploma.txt", limite_em_bytes=LIMITE)

    assert recusa.value.code == "file_extension_mismatch"
    assert "renomeie" in recusa.value.detail.lower()


def test_o_resumo_e_do_conteudo_e_nao_do_nome():
    mesmo_conteudo_outro_nome = Arquivo(b"%PDF-1.4\nigual", "outro.pdf")

    assert resumo(pdf(b"igual")) == resumo(mesmo_conteudo_outro_nome)
    assert resumo(pdf(b"igual")) != resumo(pdf(b"diferente"))


def test_a_leitura_nao_consome_o_arquivo():
    """Quem confere não pode gastar o que quem grava precisa ler."""
    arquivo = pdf()

    aceitar(arquivo, nome_original="diploma.pdf", limite_em_bytes=LIMITE)
    resumo(arquivo)

    assert arquivo.read().startswith(b"%PDF-")
