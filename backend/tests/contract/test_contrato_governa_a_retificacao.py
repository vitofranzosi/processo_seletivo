"""O contrato governa o **ato**, e não só a tela (026, FR-298, achado da revisão do PR #114).

A primeira entrega ligou o contrato à interface e deixou a API para trás: `colecoes` continuava
com um literal de um item só, e `REPLACE /number` era aceito apesar de o contrato dizer que o
número do Edital não se corrige. Fonte única que governa um canal e não o outro não é fonte única.

**Foi este teste que expôs a contradição sobre `operation`.** Ao derivar a lista do contrato, a
suíte da `015` caiu: existe decisão escrita e teste passando dizendo que retificar a operação é
legítimo, com a obsolescência do ato como consequência tratada. A matriz estava errada, e a
classificação foi restaurada.
"""

import pytest

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.changes import CampoNaoRetificavel, apply_change

PERFIL = "00000000-0000-0000-0000-000000002601"
BASE_DO_MARCO = f"/profiles/id={PERFIL}/classificationMilestones"
MARCO = "00000000-0000-0000-0000-000000002602"
MODALIDADE = "00000000-0000-0000-0000-000000002603"
EVENTO = "00000000-0000-0000-0000-000000002604"


def _conteudo():
    return {
        "number": "26",
        "year": 2026,
        "title": "Edital",
        "profiles": [
            {
                "id": PERFIL,
                "reserveType": "NONE",
                "name": "Perfil",
                "classificationMilestones": [
                    {"id": MARCO, "operation": "SOMA_PONDERADA", "drawMethod": None, "stages": []}
                ],
                "competitionModalities": [{"id": MODALIDADE, "normativeRule": None}],
            }
        ],
        "schedule": [{"id": EVENTO, "type": "PROVA", "location": ""}],
    }


@pytest.mark.contract
def test_a_lista_do_ato_vem_do_contrato_e_nao_de_um_literal():
    """Toda exclusão do contrato chega à gramática de endereçamento."""
    do_contrato = {
        (colecao, caminho)
        for (colecao, caminho), decisao in CONTRATO.items()
        if decisao.natureza is Natureza.NAO_RETIFICAVEL
    }
    # Menos os que já têm recusa mais específica em outro lugar — a escolha é **onde**, não **se**.
    assert len(colecoes.CAMPOS_NAO_RETIFICAVEIS) == len(
        do_contrato - colecoes.RECUSADOS_EM_OUTRO_LUGAR
    )
    assert "/number" in colecoes.CAMPOS_NAO_RETIFICAVEIS
    assert "/profiles/*/reserveType" in colecoes.CAMPOS_NAO_RETIFICAVEIS


@pytest.mark.contract
@pytest.mark.parametrize(
    ("caminho", "valor"),
    [
        ("/number", "27"),
        ("/year", 2027),
        (f"/profiles/id={PERFIL}/reserveType", "LIMITED"),
        (f"/schedule/id={EVENTO}/type", "ENTREVISTA"),
        (f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/stages", []),
    ],
)
def test_a_api_recusa_campo_que_o_contrato_nao_admite(caminho, valor):
    """O que a tela não oferece, o ato não aceita — e por escrito, com a razão."""
    with pytest.raises(CampoNaoRetificavel):
        apply_change(
            _conteudo(), {"targetPath": caminho, "operation": "REPLACE", "newValue": valor}
        )


@pytest.mark.contract
def test_a_api_continua_aceitando_o_que_o_contrato_admite():
    """A recusa precisa ser estreita: retificável é retificável.

    `operation` está aqui de propósito. A `015` decidiu que retificar a regra é legítimo, e o ato
    de ordenação fica obsoleto e recomputável — a consequência é tratada, e não silenciosa.
    """
    conteudo = _conteudo()
    apply_change(conteudo, {"targetPath": "/title", "operation": "REPLACE", "newValue": "Outro"})
    assert conteudo["title"] == "Outro"

    apply_change(
        conteudo,
        {
            "targetPath": f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}/operation",
            "operation": "REPLACE",
            "newValue": "MEDIA_PONDERADA",
        },
    )
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    assert marco["operation"] == "MEDIA_PONDERADA"


@pytest.mark.contract
def test_a_api_recusa_criar_declaracao_que_o_contrato_proibe():
    """FR-313, aplicada e não só declarada.

    **A lista tem um item, e o que ficou de fora é o achado.** A matriz propunha recusar também o
    método do sorteio, e a `021` decide o contrário com uma razão que a matriz não considerou: todo
    Edital publicado antes do degrau 10 carrega `drawMethod` nulo, e recusar o acréscimo deixaria o
    acervo inteiro sem caminho para declará-lo.

    Modalidade sem regra normativa é outra coisa: acrescentá-la depois é criar reserva que o Edital
    publicado não tinha.
    """
    with pytest.raises(CampoNaoRetificavel, match="não pode nascer"):
        apply_change(
            _conteudo(),
            {
                "targetPath": f"/profiles/id={PERFIL}/competitionModalities/id={MODALIDADE}"
                "/normativeRule",
                "operation": "REPLACE",
                "newValue": {"foundation": "Lei"},
            },
        )


@pytest.mark.contract
def test_corrigir_objeto_que_ja_existe_continua_admitido():
    """A distinção é o valor vigente, e não a operação: a `004` grafa as duas como `REPLACE`."""
    conteudo = _conteudo()
    conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] = {"algorithm": "x"}
    apply_change(
        conteudo,
        {
            "targetPath": f"{BASE_DO_MARCO}/id={MARCO}/drawMethod/algorithm",
            "operation": "REPLACE",
            "newValue": "IFES-SORTEIO-SHA256-v1",
        },
    )
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    assert marco["drawMethod"]["algorithm"] == "IFES-SORTEIO-SHA256-v1"


@pytest.mark.contract
def test_a_exclusao_das_secoes_e_recusada_no_lugar_mais_especifico():
    """Duas recusas para a mesma coisa, e a melhor delas vence.

    Título, ordem e espécie da seção são não retificáveis no contrato — o catálogo é institucional,
    e não escolha deste Edital. A recusa, porém, já existia em `validation._topologia_das_secoes`,
    com uma mensagem que nomeia a regra ("diverge do catálogo") e que alcança mais casos do que a
    gramática de endereçamento alcançaria.

    Duplicá-la na gramática trocaria essa mensagem por uma genérica, e criaria a segunda regra a
    envelhecer. O que este teste guarda é que a escolha foi **onde**, e não **se**.
    """
    for caminho in ("title", "order", "type"):
        decisao = CONTRATO[("sections", caminho)]
        assert decisao.natureza is Natureza.NAO_RETIFICAVEL
        assert ("sections", caminho) in colecoes.RECUSADOS_EM_OUTRO_LUGAR
    assert not any(forma.startswith("/sections/") for forma in colecoes.CAMPOS_NAO_RETIFICAVEIS)


@pytest.mark.contract
def test_a_recusa_diz_a_razao_daquele_campo():
    """A mensagem era fixa e falava do tipo do fato declarado — o único campo que a lista tinha.

    Com 25 campos derivados do contrato, ela passou a dizer "mudar o tipo de um fato declarado cria
    fato novo" para o número do Edital. A razão agora vem do contrato, que já a guarda escrita.
    """
    with pytest.raises(CampoNaoRetificavel, match="citado em todo lugar"):
        apply_change(
            _conteudo(), {"targetPath": "/number", "operation": "REPLACE", "newValue": "9"}
        )
    with pytest.raises(CampoNaoRetificavel, match="cadastro reserva"):
        apply_change(
            _conteudo(),
            {
                "targetPath": f"/profiles/id={PERFIL}/reserveType",
                "operation": "REPLACE",
                "newValue": "LIMITED",
            },
        )
