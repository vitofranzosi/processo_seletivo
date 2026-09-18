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


# ---------------------------------------------------------------------------
# A recusa por base de autorização (033, US2). O que muda daqui para baixo é **como a negativa se
# apresenta**; quem atravessa cada porta é exatamente quem atravessava.
# ---------------------------------------------------------------------------

NADA_FOI_ALTERADO = "Nenhuma alteração foi feita"


def _corpo(resposta):
    return resposta.content.decode()


@pytest.mark.parametrize(
    "tela",
    ["distribuicao", "gestao-do-processo", "consulta-de-etapa"],
)
def test_quem_nao_satisfaz_base_nenhuma_le_a_recusa_e_nao_o_inexistente(
    client, seletor_ligado, edital_a, etapa_a1, processo_a, cenario, tela
):
    """`FR-478`: a recusa é sobre o ator, e "não encontrado" mentia sobre por que a tela não abre.

    As quatro portas erradas fazem a **mesma** pergunta que a camada de segurança não sabia
    responder — uma base composta —, e cada uma improvisou o seu `raise Http404`. Improvisaram
    igual porque o buraco era o mesmo.
    """
    caminho, _ = _telas(edital_a, etapa_a1, processo_a)[tela]
    identificar(client, "estranho", [])

    resposta = client.get(caminho)

    assert resposta.status_code == 403
    assert NADA_FOI_ALTERADO in _corpo(resposta)


def test_a_recusa_nomeia_as_duas_bases_que_teriam_servido(
    client, seletor_ligado, edital_a, etapa_a1, cenario
):
    """`FR-481` e `FR-479`: nomear uma só manda a pessoa pedir metade do que resolve.

    A porta da distribuição aceita a permissão de gerir a comissão **ou** a presidência daquele
    Processo, cada uma suficiente sozinha. Quem não tem nenhuma das duas não falhou num eixo:
    falhou em **duas alternativas**, e a recusa honesta nomeia as duas.
    """
    identificar(client, "estranho", [])

    corpo = _corpo(client.get(reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])))

    assert "gerir a comissão" in corpo
    assert "presidência deste Processo" in corpo
    assert NADA_FOI_ALTERADO in corpo


def test_a_porta_do_marco_diz_coisas_diferentes_nos_seus_dois_modos(
    client, seletor_ligado, certame
):
    """`FR-489`, primeiro par: o conjunto de bases é de **quem chama**, não da porta.

    `_edital_para_classificar` tem dois modos. Na consulta, a capacidade de auditoria serve; na
    emissão — `somente_gestao=True`, que é a maioria das chamadas — ela **não** serve. Uma recusa
    que assuma conjunto fixo mente em metade dos casos: ou manda pedir auditoria a quem ela não
    resolveria, ou esconde a alternativa de quem ela resolveria.

    Se as duas frases forem iguais, o conjunto virou constante. É por isso que a asserção é de
    **diferença**, e não de conteúdo.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "estranho", [])

    consulta = _corpo(client.get(reverse("interface:ordenacao", args=[edital.id, marco])))
    emissao = _corpo(
        client.post(
            reverse("interface:emitir-ordenacao", args=[edital.id, marco]),
            {"chave_idempotencia": "estranho-033"},
        )
    )

    assert "consultar auditoria" in consulta, "no modo de consulta a auditoria serviria, e é base"
    assert "consultar auditoria" not in emissao, (
        "com somente_gestao a auditoria não serve, e nomeá-la manda pedir o que não resolve"
    )


def test_a_porta_da_divulgacao_diz_coisas_diferentes_nos_seus_dois_modos(
    client, seletor_ligado, certame
):
    """`FR-489`, segundo par — e é a porta que **já estava certa**.

    O status dela nunca esteve errado, e a mensagem genérica de hoje nunca mentiu porque não
    nomeia nada. **É justamente ao nomear que ela passa a poder mentir**: com `consulta=True` a
    capacidade de auditoria serve, e sem ele não serve. A única porta que não precisava de
    conserto é a que esta mudança pode quebrar.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "estranho", [])

    agir = _corpo(
        client.get(
            reverse("interface:previa-de-publicacao", args=[edital.id, marco, certame["ato"].id])
        )
    )
    consultar = _corpo(
        client.get(reverse("interface:publicacoes-do-marco", args=[edital.id, marco]))
    )

    assert "publicar resultado" in agir
    assert "consultar auditoria" not in agir, (
        "divulgar não admite auditoria como alternativa, e nomeá-la mandaria pedir o que não abre"
    )
    assert "consultar auditoria" in consultar


def test_na_distribuicao_o_escopo_alheio_continua_inexistente_e_a_falta_de_vinculo_nao(
    client, seletor_ligado, edital_a, etapa_a1, cenario
):
    """`FR-488`: a porta travada, e a prova de que as duas condições foram separadas.

    Ela decidia escopo-ou-inexistente e falta de base no **mesmo `if`**:

        if edital is None or pode_gerir_comissao(ator, edital.processo) is None:

    Trocar o status ali sem separar antes responderia recusa explicada também para Edital de outra
    unidade — que é vazamento, e não melhoria. Este é o único caso que distingue "separou" de
    "trocou o número", e ele precisa dos dois lados no mesmo teste: um só passaria com a porta
    ainda travada.
    """
    tela = reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])

    identificar(client, "carlos", ["gestor"], escopo="outra-unidade")
    de_fora = client.get(tela)

    identificar(client, "estranho", [])
    de_dentro = client.get(tela)

    assert de_fora.status_code == 404, "a existência de Edital de outra unidade voltou a vazar"
    assert de_dentro.status_code == 403


def test_a_supervisao_continua_inexistente_porque_ficou_fora_do_escopo(
    client, seletor_ligado, processo_a, edital_a, cenario
):
    """A decisão de escopo da `T004`, tornada falsificável — e não deixada como prosa.

    O inventário contou **onze** recusas de autorização em `interface/views.py`; quatro são as
    portas desta feature, e **sete** ficam fora. A supervisão é uma delas: ela pergunta pela mesma
    base composta que a gestão do Processo — `pode_supervisionar` devolve literalmente
    `pode_gerir_comissao` —, e responde "não encontrado" citando requisito e critério da `022` por
    identificador.

    Mudá-la aqui contradiria doutrina escrita de outra spec, e a decisão de quem governa o backlog
    foi mantê-la. Este caso existe para que a decisão **quebre** se alguém a desfizer de passagem:
    a supervisão e a gestão do Processo são vizinhas no mesmo arquivo e fazem a mesma pergunta, e
    é exatamente assim que uma correção de escopo vaza para fora dele.
    """
    identificar(client, "estranho", [])

    assert client.get(reverse("interface:supervisao", args=[processo_a.id])).status_code == 404, (
        "a supervisão saiu do 404 — se isso foi deliberado, a decisão de escopo da T004 mudou e "
        "o inventário precisa registrar a nova"
    )
