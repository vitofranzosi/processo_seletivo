"""A derivação única do conjunto de recortes, e a igualdade que a `SC-172` prende (034, FR-491).

**A verificação é por igualdade das duas listas, e não por inspeção de implementação.** Duas listas
iguais hoje e derivadas em dois lugares divergem na primeira Retificação — foi assim que este
projeto ficou com três tratamentos homônimos do mesmo fato, em três módulos, discordando em
silêncio. O que se prende aqui é o resultado: a classificação e a ocupação respondem a mesma coisa
para o mesmo marco.

**São duas listas, e não três.** A do sorteio está registrada como divergente em `FR-491a` e
`D-004`; medi-la aqui reprovaria a feature por um defeito que ela não causou e não tem mandato para
corrigir.
"""

import pytest

from processo_seletivo.editais.domain.recortes import (
    ROTULO_DA_AMPLA,
    normalizar_recorte,
    recortes_do_perfil,
    rotulo_do_recorte,
)
from processo_seletivo.shared.api.problems import DomainError

PERFIL = "bbbbbbbb-0000-4000-8000-000000000341"
PCD = "bbbbbbbb-0000-4000-8000-000000000342"
PPI = "bbbbbbbb-0000-4000-8000-000000000343"
AMPLA = "bbbbbbbb-0000-4000-8000-000000000344"
ALHEIA = "bbbbbbbb-0000-4000-8000-00000000034f"


def conteudo(*, modalidades=(), ampla_declarada=None):
    perfil = {"id": PERFIL, "name": "Perfil", "competitionModalities": list(modalidades)}
    if ampla_declarada is not None:
        perfil["generalCompetitionModalityId"] = ampla_declarada
    return {"profiles": [perfil]}


def modalidade(identidade, code, name):
    return {"id": identidade, "code": code, "name": name}


AS_DUAS = (
    modalidade(PCD, "PCD", "Pessoas com deficiência"),
    modalidade(PPI, "PPI", "Pretos, pardos e indígenas"),
)


def test_a_ampla_vem_primeiro_e_e_o_recorte_sem_lista():
    """`FR-503`: a ampla concorrência é o `NULL`, e é a mesma grafia que o resto do sistema usa."""
    recortes = recortes_do_perfil(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL)

    assert recortes[0] == (None, ROTULO_DA_AMPLA)


def test_as_reservadas_vem_na_ordem_em_que_o_perfil_as_declara():
    """Obrigação 2 do contrato: ordem instável troca o recorte de lugar entre dois cliques."""
    recortes = recortes_do_perfil(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL)

    assert [lista for lista, _ in recortes] == [None, PCD, PPI]


def test_o_rotulo_carrega_o_codigo_que_o_edital_publica():
    """Obrigação 3: a `021` pagou por dois blocos homônimos e ninguém sabendo em qual agir."""
    recortes = dict(
        (rotulo, lista)
        for lista, rotulo in recortes_do_perfil(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL)
    )

    assert "Pessoas com deficiência (PCD)" in recortes
    assert "Pretos, pardos e indígenas (PPI)" in recortes


def test_a_modalidade_declarada_como_ampla_nao_produz_recorte():
    """A grafia-armadilha, e o motivo é aritmético: a quantidade dela **é** a da linha geral.

    Dar-lhe recorte próprio declararia duas vezes o mesmo número — e emitiria uma ordem que a
    ocupação não tem linha para consumir, que é um ato publicado que não leva a lugar nenhum.
    """
    com_ampla = conteudo(
        modalidades=(*AS_DUAS, modalidade(AMPLA, "AC", "Ampla concorrência")),
        ampla_declarada=AMPLA,
    )

    assert [lista for lista, _ in recortes_do_perfil(com_ampla, perfil_id=PERFIL)] == [
        None,
        PCD,
        PPI,
    ]


def test_perfil_sem_modalidade_alguma_tem_um_recorte_so():
    """O Edital normal do acervo: uma ordem, sem lista, exatamente como antes desta feature."""
    assert recortes_do_perfil(conteudo(), perfil_id=PERFIL) == [(None, ROTULO_DA_AMPLA)]


def test_pedir_a_modalidade_declarada_como_ampla_devolve_a_ampla():
    """O apelido é **aceito** e nunca oferecido — é o que o corte já faz com a linha do quadro.

    Recusá-lo criaria uma segunda gramática para a mesma coisa, que é o que a `FR-491` proíbe; e
    tratá-lo como recorte próprio emitiria o ato que a apuração não enxerga.
    """
    com_ampla = conteudo(modalidades=(*AS_DUAS,), ampla_declarada=AMPLA)

    assert normalizar_recorte(com_ampla, perfil_id=PERFIL, lista_id=AMPLA) is None


def test_recorte_que_nao_e_modalidade_do_perfil_e_objeto_inexistente():
    """`FR-499`: "não existe" e "existe e está vazio" são coisas diferentes.

    Confundi-las esconde erro de digitação — e a `FR-492a` fez da ordem vazia um estado legítimo
    justamente para que a distinção exista.
    """
    with pytest.raises(DomainError) as recusa:
        normalizar_recorte(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL, lista_id=ALHEIA)

    assert recusa.value.status == 404


def test_o_recorte_pedido_volta_na_grafia_canonica():
    assert normalizar_recorte(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL, lista_id=PPI) == PPI
    assert (
        normalizar_recorte(conteudo(modalidades=AS_DUAS), perfil_id=PERFIL, lista_id=None) is None
    )


def test_o_rotulo_sai_da_mesma_derivacao_que_os_oferece():
    """Um segundo lugar para nomear o recorte divergiria do primeiro na primeira Retificação."""
    com_as_duas = conteudo(modalidades=AS_DUAS)

    assert rotulo_do_recorte(com_as_duas, perfil_id=PERFIL, lista_id=None) == ROTULO_DA_AMPLA
    assert (
        rotulo_do_recorte(com_as_duas, perfil_id=PERFIL, lista_id=PCD)
        == "Pessoas com deficiência (PCD)"
    )


# --- A igualdade que a `SC-172` mede -----------------------------------------------------------
#
# **Compara listas, e não implementações.** O teste continua valendo — e continua sendo o guarda —
# no dia em que alguém reintroduzir uma derivação própria na ocupação: é o resultado que ele afirma,
# e não de onde ele veio.


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_classificacao_e_a_ocupacao_derivam_a_mesma_lista(
    gestor, api_client, manager_headers, process_payload
):
    """`SC-172`: 100% dos recortes coincidem, para o mesmo marco, nas duas pontas do mesmo ato."""
    from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.recortes import montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="recortes-034-igualdade",
        com_ampla_declarada=True,
    )

    da_classificacao = recortes_do_perfil(
        effective_version(edital_id=edital.id).content, perfil_id=PROFILE_ID
    )
    da_ocupacao = recortes_do_marco(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert [lista for lista, _ in da_classificacao] == [item["listaId"] for item in da_ocupacao]
    assert [rotulo for _, rotulo in da_classificacao] == [item["rotulo"] for item in da_ocupacao]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_modalidade_declarada_como_ampla_nao_entra_em_nenhuma_das_duas(
    gestor, api_client, manager_headers, process_payload
):
    """A contraprova da igualdade: elas coincidem **e** coincidem no lugar certo.

    Duas derivações que concordassem em incluir a Modalidade declarada como ampla também passariam
    no teste acima — e emitiriam, as duas, para um recorte que declara duas vezes o mesmo número.
    """
    from processo_seletivo.ocupacao.application.selectors import recortes_do_marco
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID
    from tests.fixtures.recortes import MODALIDADE_AMPLA_DECLARADA, montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="recortes-034-ampla",
        com_ampla_declarada=True,
    )

    da_ocupacao = recortes_do_marco(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert MODALIDADE_AMPLA_DECLARADA not in [item["listaId"] for item in da_ocupacao]
    assert len(da_ocupacao) == 3, "a ampla e as duas reservadas, e não uma quarta linha"
