"""O quadro atravessa a Retificação por identidade, e a Retificação o protege (025, US3).

Duas provas de naturezas opostas, como no marco. A primeira é a que a `D-008` cobra por extenso:
**remover a Modalidade sem remover a linha que a aponta não publica** — e remover as duas no mesmo
ato passa. A segunda é a que a `FR-161` amarra: **reduzir a linha sem reduzir o total não publica**,
e os dois movimentos no mesmo ato passam.

As duas saem do mesmo mecanismo, e é isso que as torna baratas: `validate_for_publication` roda
sobre o conteúdo que a Retificação **produziria**, e não sobre cada operação. Uma verificação que
olhasse a operação teria de entender que outra operação do mesmo ato a conserta, que é o modo de
falha mais caro possível.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PERFIL = "00000000-0000-0000-0000-000000000401"
PCD = "00000000-0000-0000-0000-0000002501cd"
PPI = "00000000-0000-0000-0000-0000002501b1"
LINHA = {
    "GERAL": "00000000-0000-0000-0000-000000252001",
    "PCD": "00000000-0000-0000-0000-000000252002",
    "PPI": "00000000-0000-0000-0000-000000252003",
}
BASE = f"/profiles/id={PERFIL}"


def rascunho():
    """O quadro do `57/2026`, na escala do teste: `AC 56`, `PcD 4`, `PPI 20`, total 80."""
    dados = complete_draft()
    perfil = dados["profiles"][0]
    assert perfil["id"] == PERFIL
    perfil["immediateVacancies"] = 80
    perfil["competitionModalities"] = [
        {"id": PCD, "code": "PCD", "name": "Pessoa com deficiência"},
        {"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"},
    ]
    perfil["vacancyTable"] = [
        {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
        {"id": LINHA["PCD"], "modalityId": PCD, "immediateVacancies": 4},
        {"id": LINHA["PPI"], "modalityId": PPI, "immediateVacancies": 20},
    ]
    return dados


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content


def quadro(edital):
    return vigente(edital)["profiles"][0]["vacancyTable"]


def hashes_publicados(edital):
    return {
        str(versao.id): versao.content_hash
        for versao in VersaoConsolidada.objects.filter(edital=edital)
    }


# --- T062 · alterar a quantidade de uma linha por identidade (FR-170, FR-173) ----------------


def test_alterar_a_quantidade_de_uma_linha_nao_toca_as_demais(api_client, edital):
    antes = hashes_publicados(edital)

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"{BASE}/vacancyTable/id={LINHA['PPI']}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 18,
                },
                # O total acompanha, e é a `FR-161` que os amarra: reduzir a vaga reservada sem
                # reduzir o total publicaria um quadro que não fecha (SC-049).
                {
                    "targetPath": f"{BASE}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 78,
                },
            ],
        ),
    )

    assert quadro(edital) == [
        {"id": LINHA["GERAL"], "modalityId": None, "immediateVacancies": 56},
        {"id": LINHA["PCD"], "modalityId": PCD, "immediateVacancies": 4},
        {"id": LINHA["PPI"], "modalityId": PPI, "immediateVacancies": 18},
    ]
    # O conteúdo anterior permanece legível e intocado: a Retificação materializa versão nova.
    assert all(
        antes[chave] == valor
        for chave, valor in hashes_publicados(edital).items()
        if chave in antes
    )


# --- T063 · acrescentar linha com identidade própria (FR-171) --------------------------------


def test_acrescentar_linha_nasce_com_identidade_alcancavel_na_retificacao_seguinte(
    api_client, edital
):
    nova = "00000000-0000-0000-0000-000000252009"
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"{BASE}/competitionModalities/-",
                    "operation": "ADD",
                    "newValue": {
                        "id": "00000000-0000-0000-0000-0000002501aa",
                        "code": "Q",
                        "name": "Quilombola",
                        "description": "",
                        "normativeRule": None,
                    },
                },
                {
                    "targetPath": f"{BASE}/vacancyTable/-",
                    "operation": "ADD",
                    "newValue": {
                        "id": nova,
                        "modalityId": "00000000-0000-0000-0000-0000002501aa",
                        "immediateVacancies": 0,
                    },
                },
            ],
        ),
        suffix="a",
    )

    assert [linha["id"] for linha in quadro(edital)][-1] == nova

    # E é alcançável na Retificação seguinte pela identidade com que nasceu — que é o que separa
    # esta feature de uma coluna a mais numa tabela (FR-170, FR-171).
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"{BASE}/vacancyTable/id={nova}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 6,
                },
                # O total acompanha: a Q entrou com linha, o quadro está completo, e 56+4+20+6=86.
                {
                    "targetPath": f"{BASE}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 86,
                },
            ],
            suffix="b",
        ),
        suffix="b",
    )

    assert quadro(edital)[-1] == {
        "id": nova,
        "modalityId": "00000000-0000-0000-0000-0000002501aa",
        "immediateVacancies": 6,
    }


# --- T064 · remover a linha, inclusive a única linha geral ------------------------------------


def test_remover_a_unica_linha_geral_e_aceito_e_o_quadro_passa_a_ser_parcial(api_client, edital):
    """O quadro passa a ser parcial, e a conferência de igualdade deixa de rodar (D-006)."""
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [{"targetPath": f"{BASE}/vacancyTable/id={LINHA['GERAL']}", "operation": "REMOVE"}],
        ),
    )

    assert [linha["id"] for linha in quadro(edital)] == [LINHA["PCD"], LINHA["PPI"]]
    assert vigente(edital)["profiles"][0]["immediateVacancies"] == 80, "o total não é recalculado"


# --- T065 · a recusa da D-008 (FR-172) -------------------------------------------------------


def test_remover_so_a_modalidade_e_recusado_nomeando_a_linha_que_impede(api_client, edital):
    """A recusa chega **na criação** do ato, e não na publicação — e é melhor assim.

    `_assert_well_formed` roda sobre o conteúdo que a Retificação produziria já quando ela é
    criada: quem retifica descobre o impedimento enquanto ainda está compondo, e não depois de
    atravessar submissão e homologação.
    """
    corpo = create_retification(
        api_client,
        edital,
        [{"targetPath": f"{BASE}/competitionModalities/id={PPI}", "operation": "REMOVE"}],
        esperar=422,
    )

    assert corpo["code"] == "blocking_findings"
    assert "modalidade que não existe neste Perfil" in corpo["detail"]
    assert quadro(edital)[2]["immediateVacancies"] == 20, "nada foi apagado"


def test_remover_a_modalidade_e_a_linha_no_mesmo_ato_passa(api_client, edital):
    """ "Remover as duas é um ato só", e quem retifica declara os dois movimentos (D-008)."""
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {"targetPath": f"{BASE}/competitionModalities/id={PPI}", "operation": "REMOVE"},
                {"targetPath": f"{BASE}/vacancyTable/id={LINHA['PPI']}", "operation": "REMOVE"},
                # E o total acompanha: sem a PPI, o quadro volta a ser **completo** — a PcD é a
                # única Modalidade que sobra e tem linha —, e a igualdade da FR-161 volta a rodar.
                # 56 + 4 = 60, e um total de 80 publicaria um quadro que não fecha.
                {
                    "targetPath": f"{BASE}/immediateVacancies",
                    "operation": "REPLACE",
                    "newValue": 60,
                },
            ],
        ),
    )

    assert [linha["id"] for linha in quadro(edital)] == [LINHA["GERAL"], LINHA["PCD"]]


# --- T066 · endereçamento por posição é recusado (FR-170) ------------------------------------


def test_enderecar_a_linha_por_posicao_e_recusado(api_client, edital):
    """Coleção com chave não resolve por índice: é o que a declaração em `COLECOES_COM_CHAVE` faz.

    Sem ela, o primeiro Edital publicado com quadro nasceria endereçável só por posição — e
    endereço de retificação não se conserta depois, porque publicação é ato imutável.
    """
    corpo = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"{BASE}/vacancyTable/0/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 55,
            }
        ],
        esperar=422,
    )

    assert corpo["code"] == "positional_addressing_refused", corpo


# --- T067 · a conferência da soma roda na Retificação (FR-161, UX-023) ----------------------


def test_reduzir_so_a_linha_e_recusado_com_os_tres_numeros(api_client, edital):
    """Um quadro que fecha não pode ser retificado para um que não fecha (FR-161).

    E a mensagem diz os três números — o que soma, o que foi declarado e a diferença —, porque
    "não fecha" sozinho obrigaria quem retifica a somar à mão o que o sistema acabou de somar.
    """
    corpo = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"{BASE}/vacancyTable/id={LINHA['PPI']}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 18,
            }
        ],
        esperar=422,
    )

    detalhe = corpo["detail"]
    assert "78" in detalhe and "80" in detalhe and "diferença de 2" in detalhe
