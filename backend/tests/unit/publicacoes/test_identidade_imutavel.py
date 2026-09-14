"""T029 — a identidade do conteúdo publicado não é endereçável por Retificação (FR-004).

A exposição é anterior à `007`: `/editalId`, `/processoId` e `/schemaVersion` já eram endereçáveis,
e só `applied_publications` era recusado. Mas é a `007` que a **ativa** — a partir de
`processoTitle`, o documento nomeia o Processo por esse campo. Sem esta recusa, uma Retificação
faria o Edital publicado nomear outro Processo.
"""

import pytest

from processo_seletivo.publicacoes.domain import colecoes
from processo_seletivo.publicacoes.domain.changes import CaminhoInexistente, apply_change
from tests.fixtures.snapshot import conteudo_normativo


def _alteracao(caminho, valor):
    return {"operation": "REPLACE", "targetPath": caminho, "newValue": valor}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("editalId", "99999999-9999-9999-9999-999999999999"),
        ("processoId", "99999999-9999-9999-9999-999999999999"),
        ("processoCode", "PS-OUTRO-2026"),
        ("processoTitle", "Outro Processo Seletivo"),
        ("schemaVersion", 2),
    ],
)
def test_campo_de_identidade_da_raiz_e_recusado(campo, valor):
    conteudo = conteudo_normativo()

    with pytest.raises(CaminhoInexistente) as erro:
        apply_change(conteudo, _alteracao(f"/{campo}", valor))

    assert campo in str(erro.value)


def test_a_recusa_nomeia_o_campo_em_vez_de_falar_em_caminho_inexistente():
    """Quem recebe o erro precisa saber **por que** aquele caminho não se retifica."""
    conteudo = conteudo_normativo()

    with pytest.raises(CaminhoInexistente) as erro:
        apply_change(conteudo, _alteracao("/processoTitle", "Outro"))

    mensagem = str(erro.value)
    assert "identifica o conteúdo publicado" in mensagem
    assert "não pode ser alterado por Retificação" in mensagem


@pytest.mark.parametrize("campo", ["title", "description"])
def test_titulo_e_descricao_continuam_retificaveis_por_desenho(campo):
    """A proteção alcança identidade, não conteúdo. A tela oferece estes dois desde a `002`."""
    conteudo = conteudo_normativo()

    apply_change(conteudo, _alteracao(f"/{campo}", "Novo valor"))

    assert conteudo[campo] == "Novo valor"


@pytest.mark.parametrize("campo", ["number", "year"])
def test_numero_e_ano_deixaram_de_ser_endereçaveis(campo):
    """A questão aberta foi respondida, e é aqui que a resposta aparece.

    `number` e `year` são identidade e já eram impressos no cabeçalho **antes** da `007`. A redação
    anterior deste teste dizia: *"uma Retificação que corrija erro de numeração é discussão legítima
    que esta feature não precisa resolver … se alguém decidir protegê-los, é aqui que a decisão
    aparece"*.

    A `026` decidiu, e a razão está escrita no contrato de mutabilidade: o número e o ano são como o
    certame é citado em todo lugar — outros atos, ofícios, o Diário —, e trocá-los por Retificação
    faria dois documentos nomearem coisas diferentes com o mesmo nome.

    **A discussão que a redação anterior dizia legítima continua legítima**, e passou de lugar: quem
    a reabrir muda a linha do contrato, e este teste cai junto. Era exatamente o que a questão
    aberta pedia.
    """
    from processo_seletivo.publicacoes.domain.changes import CampoNaoRetificavel

    conteudo = {**conteudo_normativo(), "number": "07", "year": 2026}
    valor = "99" if campo == "number" else 2099

    with pytest.raises(CampoNaoRetificavel, match="identificam o certame|citado em todo lugar"):
        apply_change(conteudo, _alteracao(f"/{campo}", valor))

    assert conteudo[campo] == ("07" if campo == "number" else 2026)


def test_o_conjunto_declarado_e_o_que_a_recusa_consulta():
    """A regra vive no registro declarativo, não espalhada na gramática (P-005)."""
    assert colecoes.CAMPOS_DE_IDENTIDADE == frozenset(
        {"editalId", "processoId", "processoCode", "processoTitle", "schemaVersion"}
    )
    assert colecoes.e_campo_de_identidade("processoTitle")
    assert not colecoes.e_campo_de_identidade("title")


def test_o_controle_interno_continua_recusado_como_antes():
    """A condição nova não pode ter substituído a que já existia."""
    conteudo = conteudo_normativo()

    with pytest.raises(CaminhoInexistente) as erro:
        apply_change(conteudo, _alteracao("/applied_publications", []))

    assert "controle interno" in str(erro.value)
