"""O total da Etapa com barema, parcela a parcela (146, T016).

A função é uma só para a Mesa e para a correção por recurso (D-005), e por isso as regras se provam
aqui, sem banco: as duas formas de pontuar, o limite, as quatro casas, os pendentes nomeados, o
critério desconhecido ou repetido, a ordem indiferente, o zero sem justificativa e a reconciliação
do rascunho reaberto com o barema vigente.
"""

from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.domain import barema
from processo_seletivo.shared.api.problems import DomainError


def _criterio(chave, nome, maxima, pontos=None, unidade=None):
    return {
        "id": chave,
        "name": nome,
        "description": "",
        "maximumScore": maxima,
        "pointsPerUnit": pontos,
        "unitLabel": unidade,
        "documentRequirementId": None,
    }


DOUTORADO = _criterio("c-dout", "Doutorado", "10.0000", "10.0000", "diploma")
MESTRADO = _criterio("c-mest", "Mestrado", "6.0000", "6.0000", "diploma")
ESPECIALIZACAO = _criterio("c-esp", "Especialização", "3.0000", "3.0000", "certificado")
#: Cenário 1 (SC-1620): títulos por quantidade, máxima igual ao valor — o barema publica 19.
TITULOS = [DOUTORADO, MESTRADO, ESPECIALIZACAO]

#: Cenário 2 (SC-1621): 2 pontos por ano, máxima 10.
EXPERIENCIA = _criterio("c-exp", "Experiência", "10.0000", "2.0000", "ano")
ENTREVISTA = _criterio("c-ent", "Entrevista", "15.0000")


def _linha(criterio, quantidade=None, pontos=None, justificativa=""):
    return {
        "criterionId": criterio["id"],
        "quantidade": quantidade,
        "pontos": pontos,
        "justificativa": justificativa,
    }


def test_cenario_1_mestrado_e_especializacao_dao_9():
    linhas, total = barema.calcular(
        TITULOS,
        [_linha(DOUTORADO, 0), _linha(MESTRADO, 1), _linha(ESPECIALIZACAO, 1)],
        exigir=True,
    )

    assert total == Decimal("9.0000")
    assert [linha["parcela"] for linha in linhas] == ["0.0000", "6.0000", "3.0000"]


@pytest.mark.parametrize(
    ("anos", "parcela", "limitada"),
    [(3, "6.0000", False), (7, "10.0000", True), (5, "10.0000", False), (0, "0.0000", False)],
    ids=["3-anos", "7-anos-no-teto", "5-anos-exato", "zero"],
)
def test_cenario_2_experiencia_limitada_ao_maximo(anos, parcela, limitada):
    linhas, total = barema.calcular([EXPERIENCIA], [_linha(EXPERIENCIA, anos)], exigir=True)

    assert (linhas[0]["parcela"], linhas[0]["limitada"]) == (parcela, limitada)
    assert total == Decimal(parcela)


def test_quantidade_alem_do_teto_e_aceita_e_marcada():
    """ "52 meses" num critério de 1 por mês até 40 é resposta legítima (FR-5216)."""
    docencia = _criterio("c-doc", "Docência", "40.0000", "1.0000", "mês")

    linhas, total = barema.calcular([docencia], [_linha(docencia, "52")], exigir=True)

    assert linhas[0] == {
        "criterionId": "c-doc",
        "quantidade": 52,
        "pontos": None,
        "parcela": "40.0000",
        "limitada": True,
        "justificativa": "",
    }
    assert total == Decimal("40.0000")


@pytest.mark.parametrize("exigir", [True, False], ids=["conclusao", "rascunho"])
def test_pontos_acima_da_maxima_sao_recusados_nomeando_o_criterio(exigir):
    with pytest.raises(DomainError) as recusa:
        barema.calcular([ENTREVISTA], [_linha(ENTREVISTA, pontos="16")], exigir=exigir)

    assert recusa.value.code == barema.CRITERIO_INVALIDO
    assert "Entrevista" in recusa.value.detail
    assert "15" in recusa.value.detail
    assert recusa.value.campo == "criterio-c-ent"


def test_pontos_com_quatro_casas_e_virgula():
    linhas, total = barema.calcular(
        [ENTREVISTA], [_linha(ENTREVISTA, pontos="12,3456")], exigir=True
    )

    assert (linhas[0]["pontos"], total) == ("12.3456", Decimal("12.3456"))


@pytest.mark.parametrize("bruto", ["1.23456", "-1", "abc", "Infinity", "NaN"])
def test_pontos_malformados_sao_recusados(bruto):
    with pytest.raises(DomainError) as recusa:
        barema.calcular([ENTREVISTA], [_linha(ENTREVISTA, pontos=bruto)], exigir=False)

    assert recusa.value.code == barema.CRITERIO_INVALIDO


@pytest.mark.parametrize("bruta", ["1.5", "-1", "10000", "dois"])
def test_quantidade_malformada_e_recusada(bruta):
    with pytest.raises(DomainError) as recusa:
        barema.calcular([EXPERIENCIA], [_linha(EXPERIENCIA, bruta)], exigir=False)

    assert recusa.value.code == barema.CRITERIO_INVALIDO


def test_campo_da_outra_forma_e_recusado():
    with pytest.raises(DomainError):
        barema.calcular([EXPERIENCIA], [_linha(EXPERIENCIA, pontos="4")], exigir=False)
    with pytest.raises(DomainError):
        barema.calcular([ENTREVISTA], [_linha(ENTREVISTA, quantidade=2)], exigir=False)


def test_rascunho_aceita_pendentes_e_soma_o_respondido():
    linhas, total = barema.calcular(TITULOS, [_linha(DOUTORADO, 1)], exigir=False)

    assert total == Decimal("10.0000")
    assert [linha["parcela"] for linha in linhas] == ["10.0000", None, None]


def test_rascunho_sem_resposta_nenhuma_nao_tem_total():
    assert barema.calcular(TITULOS, [], exigir=False)[1] is None


def test_conclusao_nomeia_cada_pendente():
    with pytest.raises(DomainError) as recusa:
        barema.calcular(TITULOS, [_linha(DOUTORADO, 1)], exigir=True)

    assert recusa.value.code == barema.CRITERIOS_PENDENTES
    assert "Mestrado" in recusa.value.detail
    assert "Especialização" in recusa.value.detail
    assert "Doutorado" not in recusa.value.detail


def test_zero_sem_justificativa_conclui():
    """O arquivo comum não reivindica todos os critérios que ele pode comprovar (FR-5218)."""
    linhas, total = barema.calcular(
        TITULOS,
        [_linha(DOUTORADO, 1), _linha(MESTRADO, 0), _linha(ESPECIALIZACAO, 0)],
        exigir=True,
    )

    assert total == Decimal("10.0000")
    assert all(linha["justificativa"] == "" for linha in linhas)


def test_a_justificativa_escrita_acompanha_a_parcela():
    linhas, _ = barema.calcular(
        [ESPECIALIZACAO],
        [_linha(ESPECIALIZACAO, 0, justificativa="  Certificado fora da área.  ")],
        exigir=True,
    )

    assert linhas[0]["justificativa"] == "Certificado fora da área."


def test_criterio_desconhecido_e_recusado():
    with pytest.raises(DomainError) as recusa:
        barema.calcular(TITULOS, [{"criterionId": "outro", "quantidade": 1}], exigir=False)

    assert recusa.value.code == barema.CRITERIO_INVALIDO


def test_criterio_repetido_e_recusado():
    with pytest.raises(DomainError):
        barema.calcular(TITULOS, [_linha(DOUTORADO, 1), _linha(DOUTORADO, 0)], exigir=False)


def test_a_ordem_das_linhas_nao_muda_o_total():
    """SC-1629: o mesmo detalhamento, em qualquer ordem, dá o mesmo total com quatro casas."""
    terco = _criterio("c-t", "Terço", "1.0000")
    criterios = [terco, ENTREVISTA, EXPERIENCIA]
    respostas = [
        _linha(terco, pontos="0.3333"),
        _linha(ENTREVISTA, pontos="7.1111"),
        _linha(EXPERIENCIA, 3),
    ]

    totais = {
        barema.calcular(criterios, ordem, exigir=True)[1]
        for ordem in (respostas, list(reversed(respostas)), respostas[1:] + respostas[:1])
    }

    assert totais == {Decimal("13.4444")}
    # E as linhas saem sempre na ordem do barema, e não na do envio.
    linhas, _ = barema.calcular(criterios, list(reversed(respostas)), exigir=True)
    assert [linha["criterionId"] for linha in linhas] == ["c-t", "c-ent", "c-exp"]


def test_o_barema_da_versao_e_o_da_etapa_naquele_conteudo():
    conteudo = {"stages": [{"id": "e1", "criteria": TITULOS}, {"id": "e2", "criteria": []}]}

    assert barema.barema_da_versao(conteudo, "e1") == TITULOS
    assert barema.barema_da_versao(conteudo, "e2") == []
    assert barema.barema_da_versao(conteudo, "e3") == []
    assert barema.barema_da_versao(None, "e1") == []
    # O acervo, sem a chave, é a Etapa sem barema.
    assert barema.barema_da_versao({"stages": [{"id": "e1"}]}, "e1") == []


def test_reconciliar_mantem_o_que_continua_descarta_o_removido_e_deixa_o_novo_pendente():
    """FR-5222: a ficha reaberta pelo barema vigente."""
    anterior = [
        {**_linha(DOUTORADO, 1, justificativa="Diploma conferido."), "parcela": "10.0000"},
        {**_linha(MESTRADO, 0), "parcela": "0.0000"},
    ]
    novo = _criterio("c-novo", "Livro publicado", "5.0000", "1.0000", "livro")
    vigente = [{**DOUTORADO, "maximumScore": "12.0000"}, novo]

    reconciliado = barema.reconciliar(anterior, vigente)

    assert reconciliado == [
        {
            "criterionId": "c-dout",
            "quantidade": 1,
            "pontos": None,
            "justificativa": "Diploma conferido.",
        },
        {"criterionId": "c-novo", "quantidade": None, "pontos": None, "justificativa": ""},
    ]
    # E o cálculo refaz a parcela contra a máxima nova, e cobra o novo na conclusão.
    with pytest.raises(DomainError) as recusa:
        barema.calcular(vigente, reconciliado, exigir=True)
    assert "Livro publicado" in recusa.value.detail


def test_reconciliar_descarta_o_valor_quando_a_forma_do_criterio_mudou():
    anterior = [_linha(DOUTORADO, 1)]
    direto = {**DOUTORADO, "pointsPerUnit": None, "unitLabel": None}

    assert barema.reconciliar(anterior, [direto])[0]["quantidade"] is None


def test_parcela_exibivel_nao_recusa():
    assert barema.parcela_exibivel(ENTREVISTA, {"pontos": "99"}) == (None, False)
    assert barema.parcela_exibivel(EXPERIENCIA, {"quantidade": 7}) == ("10.0000", True)
