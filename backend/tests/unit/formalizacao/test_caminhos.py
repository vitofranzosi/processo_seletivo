"""Os nomes do pacote e as células do manifesto contra nomes hostis (117, FR-3712, SC-1114).

O ZIP é aberto num computador do setor e o manifesto numa planilha: um nome que sai da pasta da
pessoa, um nome reservado do Windows ou uma célula que começa uma fórmula são o vetor, e não um caso
raro. Os casos daqui são os da spec — `../x`, `CON`, `=1+1`, controle, 300 caracteres e duas chaves
que viram o mesmo nome depois da normalização.
"""

import unicodedata
from datetime import datetime

import pytest

from processo_seletivo.formalizacao.domain import caminhos

HOSTIS = [
    "../x",
    "..",
    ".",
    "CON",
    "con.txt",
    "LPT9",
    "=1+1",
    "a\x00b\x1fc",
    "nome​com‎formatação",
    "x" * 300,
    "  . espaço e ponto .  ",
    'a/b\\c:d*e?f"g<h>i|j',
    "",
]


@pytest.mark.parametrize("texto", HOSTIS)
def test_nenhum_componente_carrega_separador_controle_ou_reservado(texto):
    nome = caminhos.componente(texto)

    assert nome
    assert len(nome) <= caminhos.LIMITE
    assert not any(c in nome for c in '/\\:*?"<>|')
    assert all(unicodedata.category(c) not in ("Cc", "Cf") for c in nome)
    assert nome not in (".", "..")
    assert not nome.startswith((".", " ")) and not nome.endswith((".", " "))
    assert nome.split(".", 1)[0].upper() not in caminhos.RESERVADOS


def test_o_vazio_e_o_ponto_viram_sem_nome():
    assert caminhos.componente("") == "sem-nome"
    assert caminhos.componente("..") == "sem-nome"
    assert caminhos.componente(None) == "sem-nome"


def test_nfc_iguala_as_duas_grafias_do_mesmo_acento():
    composto = unicodedata.normalize("NFC", "Conceição")
    decomposto = unicodedata.normalize("NFD", "Conceição")
    assert composto != decomposto
    assert caminhos.componente(composto) == caminhos.componente(decomposto)


@pytest.mark.parametrize("nome", HOSTIS)
def test_nenhuma_entrada_sai_da_pasta_da_pessoa(nome):
    pasta = caminhos.pasta_da_pessoa("INS-2026-0001", nome)
    arquivos = caminhos.arquivos_da_pessoa([("00000000-0000-0000-0000-000000000001", nome)])
    entrada = caminhos.caminho(pasta, arquivos["00000000-0000-0000-0000-000000000001"])

    partes = entrada.split("/")
    assert len(partes) == 2
    assert all(parte not in ("", ".", "..") for parte in partes)
    assert not entrada.startswith("/")
    assert "\\" not in entrada


def test_a_pasta_comeca_pelo_protocolo_mesmo_com_o_nome_cortado():
    pasta = caminhos.pasta_da_pessoa("INS-2026-0001", "Maria " * 60)
    assert pasta.startswith("INS-2026-0001 ")
    assert len(pasta) <= caminhos.LIMITE


def test_duas_chaves_que_viram_o_mesmo_nome_recebem_sufixo_na_ordem_do_requisito():
    requisitos = [
        ("00000000-0000-0000-0000-000000000003", "cpf"),
        ("00000000-0000-0000-0000-000000000001", "CPF"),
        ("00000000-0000-0000-0000-000000000002", "cpf."),
    ]
    nomes = caminhos.arquivos_da_pessoa(requisitos)

    assert nomes["00000000-0000-0000-0000-000000000001"] == "CPF.pdf"
    assert nomes["00000000-0000-0000-0000-000000000002"] == "cpf-2.pdf"
    assert nomes["00000000-0000-0000-0000-000000000003"] == "cpf-3.pdf"
    assert len({nome.casefold() for nome in nomes.values()}) == 3
    # Determinístico: a ordem da lista não muda os nomes (SC-1108).
    assert caminhos.arquivos_da_pessoa(list(reversed(requisitos))) == nomes


def test_o_sufixo_cabe_no_limite_mesmo_com_a_chave_longa():
    requisitos = [(f"00000000-0000-0000-0000-00000000000{n}", "x" * 300) for n in range(1, 4)]
    nomes = caminhos.arquivos_da_pessoa(requisitos)

    assert len(set(nomes.values())) == 3
    assert all(len(nome) <= caminhos.LIMITE for nome in nomes.values())
    assert all(nome.endswith(".pdf") for nome in nomes.values())


def test_o_download_individual_usa_protocolo_e_requisito():
    assert (
        caminhos.nome_do_download_individual("INS-2026-0001", "certificado")
        == "INS-2026-0001-certificado.pdf"
    )
    assert "/" not in caminhos.nome_do_download_individual("INS-2026-0001", "../../etc")


def test_o_nome_do_pacote_nao_tem_dado_pessoal_e_diz_parcial():
    instante = datetime(2026, 11, 4, 9, 5)
    assert caminhos.nome_do_pacote("72/2026", instante, parcial=False) == (
        "formalizacao-72-2026-20261104-0905.zip"
    )
    assert caminhos.nome_do_pacote("72/2026", instante, parcial=True).endswith("-parcial.zip")


@pytest.mark.parametrize("celula", ["=1+1", "+55", "-2", "@soma", "\tx", "\rx"])
def test_a_celula_que_comecaria_uma_formula_ganha_apostrofo(celula):
    assert caminhos.neutralizar(celula) == f"'{celula}"


@pytest.mark.parametrize("celula", ["Maria", "INS-2026-0001", "", "a=b"])
def test_a_celula_comum_nao_muda(celula):
    assert caminhos.neutralizar(celula) == celula
