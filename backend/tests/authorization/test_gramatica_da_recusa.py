"""A gramática da negativa na gestão, e as duas garantias que ela não pode perder (033).

Este arquivo nasce **antes** da mudança de gramática, e é de propósito: ele prende o que a `033`
promete **não** mexer. A recusa é superfície de segurança, e o modo de falha desta feature não é
esquecer de trocar um status — é trocar um que não devia.

Duas garantias, e nenhuma delas é sobre o status que a feature vai mudar:

- **`FR-480` e `FR-487`** · objeto de outro escopo institucional responde "não encontrado", e
  responde **mesmo a quem tem a capacidade que a tela exige**. O que protege não é a ordem de
  avaliação — é o filtro por escopo **na própria consulta**, que torna objeto de outra unidade
  indistinguível de objeto inexistente. Um teste de status sozinho não pega quem remover esse
  filtro: pega-se dando ao ator tudo **menos** o escopo.
- **`FR-482`** · a URL montada à mão recebe a mesma recusa que a tela daria. Retirar o link é
  conveniência; a fronteira é o servidor.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def cenario(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return inscrever(edital_a, 2)


def _telas(edital, etapa_id, processo):
    """Uma tela por porta de autorização da gestão, com o papel que a satisfaz.

    O papel é o que **basta** para aquela tela: é isso que faz o caso valer. Se o ator chegasse
    sem a capacidade, o 404 poderia vir da recusa de autorização, e o teste passaria sem nunca
    ter exercitado o filtro por escopo — que é o que ele existe para prender.
    """
    return {
        "distribuicao": (
            reverse("interface:distribuicao", args=[edital.id, etapa_id]),
            ["gestor"],
        ),
        "gestao-do-processo": (
            reverse("interface:comissao", args=[processo.id]),
            ["gestor"],
        ),
        "consulta-de-etapa": (
            reverse("interface:trilha-da-avaliacao", args=[edital.id, etapa_id]),
            ["auditor"],
        ),
        "supervisao": (
            reverse("interface:supervisao", args=[processo.id]),
            ["gestor"],
        ),
    }


@pytest.mark.parametrize(
    "tela",
    ["distribuicao", "gestao-do-processo", "consulta-de-etapa", "supervisao"],
)
def test_escopo_alheio_e_inexistente_mesmo_para_quem_tem_a_capacidade(
    client, seletor_ligado, edital_a, etapa_a1, processo_a, cenario, tela
):
    """`FR-480` e `FR-487`: o que protege é o filtro na consulta, não a ordem de avaliação.

    O ator desta vez **tem** a capacidade que a tela exige. Se a resposta deixar de ser "não
    encontrado", a consulta parou de filtrar por escopo — e o produto passou a dizer, a quem não
    alcança, que o Edital de outra unidade existe.
    """
    caminho, papeis = _telas(edital_a, etapa_a1, processo_a)[tela]
    identificar(client, "carlos", papeis, escopo="outra-unidade")

    assert client.get(caminho).status_code == 404


@pytest.mark.parametrize(
    "tela",
    ["distribuicao", "gestao-do-processo", "consulta-de-etapa", "supervisao"],
)
def test_a_capacidade_certa_no_escopo_certo_continua_abrindo(
    client, seletor_ligado, edital_a, etapa_a1, processo_a, cenario, tela
):
    """A contraprova sem a qual o caso acima passaria por acidente.

    Um erro de rota, de `fixture` ou de papel responderia 404 para tudo, e o teste do escopo
    ficaria verde sem ter provado nada. Este caso é o que separa "recusou pelo escopo" de
    "recusou por qualquer motivo".
    """
    caminho, papeis = _telas(edital_a, etapa_a1, processo_a)[tela]
    identificar(client, "carlos", papeis)

    assert client.get(caminho).status_code == 200


def test_a_url_montada_a_mao_recebe_a_mesma_recusa_que_a_tela(
    client, seletor_ligado, edital_a, etapa_a1, cenario
):
    """`FR-482`: esconder o link não é a proteção, e o POST prova isso.

    A asserção é de **igualdade**, e não de valor: qual status a recusa carrega é o que a `US2`
    decide, e prender o número aqui faria este arquivo brigar com a feature que ele protege. O
    que não pode mudar nunca é que o caminho de agir recuse igual ao de olhar — e que nada tenha
    sido gravado.
    """
    tela = reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])
    # João atua na Etapa e não a organiza: a tela não lhe oferece caminho nenhum até aqui.
    identificar(client, "joao", [])

    olhar = client.get(tela)
    agir = client.post(tela, {"acao": "distribuir", "inscricao_id": [str(cenario[0].id)]})

    assert olhar.status_code >= 400, "a tela abriu para quem ela não deveria alcançar"
    assert agir.status_code == olhar.status_code
    assert Atribuicao.objects.count() == 0


# ---------------------------------------------------------------------------
# A porta do marco e a da divulgação pendem de um certame com ato **emitido**, que é outro Edital
# e outra fixture. Ficam separadas por isso, e não por serem de outra natureza: a garantia que
# elas prendem é a mesma.
# ---------------------------------------------------------------------------


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    from tests.fixtures.divulgacao import montar_ato_publicavel

    return montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=33, codigo="0733"
    )


def _telas_do_certame(certame):
    return {
        "marco": (
            reverse("interface:ordenacao", args=[certame["edital"].id, certame["marco"]]),
            ["gestor"],
        ),
        "divulgacao": (
            reverse(
                "interface:previa-de-publicacao",
                args=[certame["edital"].id, certame["marco"], certame["ato"].id],
            ),
            ["publicador"],
        ),
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("tela", ["marco", "divulgacao"])
def test_escopo_alheio_e_inexistente_tambem_no_marco_e_na_divulgacao(
    client, seletor_ligado, certame, tela
):
    """As mesmas `FR-480` e `FR-487`, nas duas portas que dependem de ato emitido.

    A da divulgação entra aqui **porque já está certa**: ela recusa a falta de capacidade com 403
    e o escopo alheio com 404, e é o precedente de que a `033` se declara continuação. Se ela
    regredir, a feature perdeu o modelo que copiou.
    """
    caminho, papeis = _telas_do_certame(certame)[tela]
    identificar(client, "carlos", papeis, escopo="outra-unidade")

    assert client.get(caminho).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("tela", ["marco", "divulgacao"])
def test_no_escopo_certo_o_marco_e_a_divulgacao_abrem(client, seletor_ligado, certame, tela):
    """A contraprova, pela mesma razão de antes — e ela já pagou por si.

    Na primeira escrita deste arquivo a rota do marco recebeu um identificador de Etapa no lugar
    do marco. Todo caso de escopo ficou verde; foi esta contraprova que reprovou.
    """
    caminho, papeis = _telas_do_certame(certame)[tela]
    identificar(client, "carlos", papeis)

    assert client.get(caminho).status_code == 200
