"""Os dados fictícios e os atores do gerador de cenários (134, FR-4630 a FR-4632, FR-4642)."""

import pytest

from processo_seletivo.inscricoes.domain.pessoais import cpf_valido
from processo_seletivo.interface.identidade import PAPEIS
from processo_seletivo.treinamento import construcao, identificadores
from processo_seletivo.treinamento.catalogo import CENARIOS


def test_o_cpf_gerado_e_valido_comeca_por_000_e_nao_se_repete_entre_cenarios():
    gerados = {
        identificadores.cpf(cenario.codigo, rodada, ordem)
        for cenario in CENARIOS
        for rodada in (1, 2)
        for ordem in range(1, 13)
    }
    assert len(gerados) == len(CENARIOS) * 2 * 12
    for numero in gerados:
        assert cpf_valido(numero), numero
        assert numero.startswith("000.")


def test_a_pessoa_ficticia_se_denuncia_no_nome_e_no_e_mail_reservado():
    pessoa = identificadores.pessoa("C07", 1, 3)
    assert "Treinamento" in pessoa["nome"]
    assert pessoa["email"].endswith(".test")
    assert pessoa["subject"].startswith("cand:treinamento-")


def test_remapear_troca_so_os_identificadores_do_molde_e_distingue_as_rodadas():
    molde = {"id": identificadores.do_molde("b1"), "outro": "00000000-0000-0000-0001-0000000000b1"}
    primeira = identificadores.remapear(molde, "C07", 1)
    segunda = identificadores.remapear(molde, "C07", 2)
    assert primeira["outro"] == molde["outro"], "identificador que não é do molde fica"
    assert primeira["id"] != molde["id"]
    assert primeira["id"] != segunda["id"], "cada rodada tem o seu espaço"
    assert primeira == identificadores.remapear(molde, "C07", 1), "e é estável"


def test_o_pdf_ficticio_e_pdf_e_carrega_a_marca_de_treinamento():
    corpo = construcao.pdf_ficticio("Identificação")
    assert corpo.startswith(b"%PDF-1.4")
    assert corpo.rstrip().endswith(b"%%EOF")
    assert b"TREINAMENTO - DADO" in corpo, "o travessão não sai como interrogação"


# A equipe do gerador e o papel do seletor a que cada um corresponde. Presidir e avaliar não são
# papéis — a base é a comissão —, e por isso esses três não têm permissão nenhuma.
PAPEL_DE = {
    construcao.GESTAO: "gestor",
    construcao.ELABORACAO: "elaborador",
    construcao.HOMOLOGACAO: "homologador",
    construcao.PUBLICACAO: "publicador",
}


@pytest.mark.parametrize("subject", construcao.EQUIPE)
def test_nenhum_ator_do_gerador_tem_permissao_que_o_papel_dele_nao_da(subject):
    """FR-4642: o gerador não amplia capacidade — quem publica não homologa, e assim por diante."""
    permissoes = set(construcao._PERMISSOES[subject])
    if subject not in PAPEL_DE:
        assert permissoes == set()
        return
    assert permissoes <= set(PAPEIS[PAPEL_DE[subject]][1])


def test_nenhum_ator_do_gerador_tem_o_formato_do_identificador_institucional():
    assert not any(subject.startswith("pessoa-") for subject in construcao.EQUIPE)


def test_toda_ficha_do_catalogo_tem_os_campos_da_especificacao():
    codigos = [cenario.codigo for cenario in CENARIOS]
    assert codigos == sorted(set(codigos))
    for cenario in CENARIOS:
        for campo in (
            "nome",
            "objetivo",
            "tipo_de_selecao",
            "metodo",
            "estado_inicial",
            "proxima_acao",
            "resultado_esperado",
            "restauracao",
        ):
            assert getattr(cenario, campo), (cenario.codigo, campo)
        assert cenario.papeis, cenario.codigo


def test_os_atores_do_gerador_nao_sao_sugeridos_a_equipe_na_pagina_de_acesso():
    """Sem isto, quinze cenários punham "Publicador como treino.publicacao" na entrada."""
    from processo_seletivo.interface import demonstracao

    assert all(subject.startswith(demonstracao._FORA_DA_EQUIPE) for subject in construcao.EQUIPE)
