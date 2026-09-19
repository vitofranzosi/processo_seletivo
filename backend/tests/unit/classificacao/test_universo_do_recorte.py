"""O universo de cada recorte: quem é ordenado onde, e por quê (034, FR-492, FR-503, D-001).

**Não é uma partição — é uma sobreposição.** O universo da ampla concorrência é o Perfil inteiro, e
quem se autodeclarou numa Modalidade reservada **continua nele**. A cota preenche o que a ampla não
preencheu, e é a ocupação que desconta da cota quem já ocupou pela ampla — o item 8.9 do 28/2026,
que `ocupacao/application/emissao.py` já implementa e que o `D-001` pressupõe.

Ler isso ao contrário — tirar o autodeclarado da ampla — mudaria a ordem de todo Edital com cota do
acervo, tornaria a reversão de vaga sem sentido, e nenhum teste de recorte reservado acusaria.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import (
    MODALIDADE_AMPLA_DECLARADA,
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    montar_cenario_7_1_2,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario_7_1_2(gestor, api_client, manager_headers, process_payload):
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="universo-034",
    )


def protocolos(proposta):
    """Quem está no universo — com posição ou sem ela, porque o universo é o conjunto inteiro."""
    return {item["protocolo"] for item in proposta["posicoes"] + proposta["sem_posicao"]}


def ordem(proposta):
    return [item["protocolo"] for item in proposta["posicoes"]]


def calcular(edital, lista_id):
    return calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id)


def test_a_ampla_contem_todos_inclusive_os_autodeclarados(cenario_7_1_2):
    """`D-001` visto do lado da ampla, e é a contraprova que o `quickstart` manda conferir.

    Se os autodeclarados não estiverem aqui, a decisão foi implementada ao contrário.
    """
    edital, _, inscricoes = cenario_7_1_2

    ampla = calcular(edital, None)

    assert protocolos(ampla) == {item.protocolo for item in inscricoes}


def test_o_recorte_reservado_contem_so_quem_se_autodeclarou_nele(cenario_7_1_2):
    """`FR-492`: o universo do recorte reservado é quem declarou **aquela** Modalidade."""
    edital, _, inscricoes = cenario_7_1_2

    ppi = calcular(edital, MODALIDADE_PPI)
    pcd = calcular(edital, MODALIDADE_PCD)

    assert protocolos(ppi) == {inscricoes[2].protocolo, inscricoes[4].protocolo}
    assert protocolos(pcd) == {inscricoes[1].protocolo}


def test_o_autodeclarado_aparece_nas_duas_ordens(cenario_7_1_2):
    """A sobreposição, dita como afirmação e não como consequência de duas listas separadas."""
    edital, _, inscricoes = cenario_7_1_2
    da_ppi = inscricoes[2].protocolo

    assert da_ppi in ordem(calcular(edital, None))
    assert da_ppi in ordem(calcular(edital, MODALIDADE_PPI))


def test_quem_nao_se_autodeclarou_aparece_so_na_ampla(cenario_7_1_2):
    """O nulo de `modality_id` é o caso normal, e ele não pertence a recorte reservado nenhum."""
    edital, _, inscricoes = cenario_7_1_2
    sem_declaracao = inscricoes[0].protocolo

    assert sem_declaracao in protocolos(calcular(edital, None))
    assert sem_declaracao not in protocolos(calcular(edital, MODALIDADE_PPI))
    assert sem_declaracao not in protocolos(calcular(edital, MODALIDADE_PCD))


def test_a_ordem_do_recorte_reservado_preserva_a_ordem_relativa_da_ampla(cenario_7_1_2):
    """A cota não muda **como** se pontua — só de quem é a lista (contrato da ordem, «Regra»).

    As autodeclarações do cenário são entremeadas de propósito: se elas fossem as últimas
    colocadas, uma implementação que ordenasse o recorte pelo universo inteiro produziria a mesma
    lista e este teste passaria sem provar nada.
    """
    edital, _, _ = cenario_7_1_2

    da_ampla = ordem(calcular(edital, None))
    da_ppi = ordem(calcular(edital, MODALIDADE_PPI))

    assert da_ppi == [item for item in da_ampla if item in set(da_ppi)]
    assert da_ppi[0] != da_ampla[0], "a premissa: o primeiro da ampla não é autodeclarado em PPI"


def test_a_posicao_do_recorte_reservado_e_a_daquele_recorte(cenario_7_1_2):
    """Quem é terceiro na ampla pode ser primeiro na cota — é o que a cota existe para fazer."""
    edital, _, inscricoes = cenario_7_1_2
    primeiro_de_ppi = inscricoes[2].protocolo

    posicoes = {
        item["protocolo"]: item["posicao"] for item in calcular(edital, MODALIDADE_PPI)["posicoes"]
    }
    na_ampla = {item["protocolo"]: item["posicao"] for item in calcular(edital, None)["posicoes"]}

    assert posicoes[primeiro_de_ppi] == 1
    assert na_ampla[primeiro_de_ppi] == 3


def test_a_modalidade_declarada_como_ampla_nao_e_recorte_e_cai_na_ampla(
    gestor, api_client, manager_headers, process_payload
):
    """`FR-503`: pedir por ela devolve o universo inteiro, e não um recorte de ninguém.

    É o apelido que o corte já pratica com a linha do quadro. Tratá-la como recorte próprio
    produziria uma ordem vazia — com nome de Modalidade — que a ocupação não teria linha para
    consumir.
    """
    edital, _, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="universo-034-ampla",
        com_ampla_declarada=True,
    )

    pela_declarada = calcular(edital, MODALIDADE_AMPLA_DECLARADA)

    assert protocolos(pela_declarada) == {item.protocolo for item in inscricoes}
    assert pela_declarada["lista_id"] is None


def test_recorte_alheio_ao_perfil_e_objeto_inexistente(cenario_7_1_2):
    """`FR-499` na porta do cálculo — e não só na tela, porque o comando passa por aqui."""
    edital, _, _ = cenario_7_1_2

    with pytest.raises(DomainError) as recusa:
        calcular(edital, "cccccccc-0000-4000-8000-0000000003ff")

    assert recusa.value.status == 404


def test_recorte_sem_nenhum_autodeclarado_produz_universo_vazio_e_nao_recusa(
    gestor, api_client, manager_headers, process_payload
):
    """`FR-492a`: a ordem vazia é calculável — o que ela não é, é automática.

    "Ninguém concorreu por esta cota" e "ainda não emitiram" precisam ser distinguíveis, e a
    diferença entre as duas é quem tem trabalho a fazer.
    """
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="universo-034-vazio",
        autodeclarar=False,
    )

    vazio = calcular(edital, MODALIDADE_PCD)

    assert vazio["posicoes"] == []
    assert vazio["sem_posicao"] == []
    assert vazio["lista_id"] == MODALIDADE_PCD
