"""A recusa **de escrita**, pelo canal do ator — a metade que a suíte não cobrava.

**Por que existe.** FR-043 diz que as duas condições são verificadas "em toda rota", e a suíte
provava isso por GET: `test_mesa.py` demonstra a conjunção abrindo e fechando telas. As rotas que
**gravam** — a avaliação, a remoção de atribuição, o impedimento, a reabertura — eram exercitadas
só pelo caminho feliz, ou pela camada de aplicação, onde o payload não passa por formulário nenhum.

A assimetria importava porque é justamente nos POSTs que `expected_revision` e
`versao_reconhecida` viajam: um teste que recusa um corpo vazio não prova autorização, prova
validação. Por isso cada recusa aqui manda o payload que **seria aceito** — e cada rota tem o seu
controle positivo, que é o que impede este arquivo de passar por acidente no dia em que o
formulário mudar de nome de campo.

Toda recusa é 404: a existência de uma inscrição, de uma Etapa ou de um Processo não é
enumerável por quem não os alcança (FR-044).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import (
    Atribuicao,
    Avaliacao,
    ConclusaoAvaliacao,
    Impedimento,
)
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import distribuir_para, montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    """Maria preside; joao e ana estão alocados. Só joao recebe atribuição."""
    montado = montar_banca(
        gestor,
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0044"},
        seed=44,
        codigo="44",
    )
    inscricoes = inscrever(montado["edital"], 2)
    distribuir_para(montado, gestor, ["joao"], inscricoes[:1], chave="para-joao-44")
    return {**montado, "inscricoes": inscricoes, "atribuida": inscricoes[0], "livre": inscricoes[1]}


def rota(nome, cenario, *extra):
    return reverse(nome, args=[cenario["edital"].id, cenario["etapa"], *extra])


def gravar_em(cenario, inscricao):
    return rota("interface:mesa-avaliacao-gravar", cenario, inscricao.id)


def concluir_em(cenario, inscricao):
    return rota("interface:mesa-avaliacao-concluir", cenario, inscricao.id)


def corpo_da_avaliacao(cenario, *, concluir=False):
    """O payload que o formulário da Mesa envia — o mesmo que seria aceito."""
    dados = {"pontuacao": "80", "parecer": "Atende ao exigido.", "expected_revision": "1"}
    if concluir:
        versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
        dados["versao_reconhecida"] = str(versao.id)
    return dados


# Quem tenta, e por que a tentativa é plausível. `escopo` distingue a mesma pessoa noutra unidade.
ALHEIOS = [
    pytest.param("ana", [], None, id="alocada-sem-atribuicao"),
    pytest.param("estranho", [], None, id="sem-vinculo-nenhum"),
    pytest.param("carlos", ["gestor"], None, id="quem-gere-a-comissao"),
    pytest.param("joao", [], "outra-unidade", id="o-atribuido-de-outro-escopo"),
]


@pytest.mark.parametrize(("subject", "papeis", "escopo"), ALHEIOS)
def test_gravar_avaliacao_alheia_e_recusado(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    """Gerir a comissão não é atuar nela, e estar na Etapa não é ter a inscrição (D-005, FR-055)."""
    identificar(client, subject, papeis, escopo=escopo)

    resposta = client.post(gravar_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario))

    assert resposta.status_code == 404
    assert not Avaliacao.objects.filter(identity_subject=subject).exists()


@pytest.mark.parametrize(("subject", "papeis", "escopo"), ALHEIOS)
def test_concluir_avaliacao_alheia_e_recusado(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    identificar(client, subject, papeis, escopo=escopo)

    resposta = client.post(
        concluir_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario, concluir=True)
    )

    assert resposta.status_code == 404
    assert Avaliacao.objects.count() == 0
    assert ConclusaoAvaliacao.objects.count() == 0


def test_o_atribuido_nao_alcanca_a_inscricao_que_nao_recebeu(client, seletor_ligado, cenario):
    """FR-045: trocar o identificador na URL não alcança inscrição não atribuída."""
    identificar(client, "joao", [])

    resposta = client.post(gravar_em(cenario, cenario["livre"]), corpo_da_avaliacao(cenario))

    assert resposta.status_code == 404
    assert not Avaliacao.objects.filter(inscricao_id=cenario["livre"].id).exists()


def test_o_mesmo_corpo_e_aceito_de_quem_tem_a_atribuicao(client, seletor_ligado, cenario):
    """O controle positivo, sem o qual as recusas acima não provariam autorização.

    Um payload que o servidor rejeitaria por forma produziria 404 nenhum e recusa nenhuma — e o
    arquivo inteiro passaria medindo a validação em vez da autorização.
    """
    identificar(client, "joao", [])

    resposta = client.post(gravar_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario))

    assert resposta.status_code == 302
    assert Avaliacao.objects.filter(identity_subject="joao").count() == 1


def test_concluir_com_o_mesmo_corpo_e_aceito_de_quem_tem_a_atribuicao(
    client, seletor_ligado, cenario
):
    identificar(client, "joao", [])

    resposta = client.post(
        concluir_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario, concluir=True)
    )

    assert resposta.status_code == 302
    assert Avaliacao.objects.get(identity_subject="joao").estado == Avaliacao.Estado.CONCLUIDA


# ---------------------------------------------------------------------------
# Os atos da presidência: distribuir, impedir e reabrir. Aqui a porta é a de **gestão** da
# comissão, e quem apenas atua na Etapa não a atravessa (FR-067).
# ---------------------------------------------------------------------------

SEM_GESTAO = [
    pytest.param("joao", [], None, id="quem-apenas-atua-na-etapa"),
    pytest.param("estranho", [], None, id="sem-vinculo-nenhum"),
    pytest.param("iris", ["auditor"], None, id="quem-so-audita"),
    pytest.param("carlos", ["gestor"], "outra-unidade", id="gestor-de-outra-unidade"),
]


@pytest.mark.parametrize(("subject", "papeis", "escopo"), SEM_GESTAO)
def test_remover_atribuicao_por_post_e_recusado(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    """A recusa é do servidor, e não da tela que esconde o botão."""
    identificar(client, subject, papeis, escopo=escopo)
    atribuicao = Atribuicao.objects.get(inscricao=cenario["atribuida"], ativo=True)

    resposta = client.post(
        rota("interface:distribuicao-remover", cenario),
        {"chave_idempotencia": "remocao-alheia", "atribuicao_id": [str(atribuicao.id)]},
    )

    assert resposta.status_code == 404
    assert Atribuicao.objects.get(pk=atribuicao.pk).ativo is True


@pytest.mark.parametrize(("subject", "papeis", "escopo"), SEM_GESTAO)
def test_registrar_impedimento_por_post_e_recusado(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    """FR-039: impedir é ato da presidência, e a recusa vem antes de o motivo ser lido."""
    identificar(client, subject, papeis, escopo=escopo)

    resposta = client.post(
        rota("interface:impedimentos", cenario),
        {
            "identity_subject": "joao",
            "inscricao_id": str(cenario["atribuida"].id),
            "motivo": "Parentesco declarado.",
            "confirmar": "1",
            "alcance": "qualquer",
            "chave_idempotencia": "impedimento-alheio",
        },
    )

    assert resposta.status_code == 404
    assert not Impedimento.objects.exists()
    assert Atribuicao.objects.filter(ativo=True).count() == 1


@pytest.mark.parametrize(("subject", "papeis", "escopo"), SEM_GESTAO)
def test_a_tela_de_impedimentos_nao_e_alcancavel(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    identificar(client, subject, papeis, escopo=escopo)

    assert client.get(rota("interface:impedimentos", cenario)).status_code == 404


@pytest.mark.parametrize(("subject", "papeis", "escopo"), SEM_GESTAO)
def test_reabrir_avaliacao_por_post_e_recusado(
    client, seletor_ligado, cenario, subject, papeis, escopo
):
    """FR-036: reabrir é ato da presidência, e o que foi concluído continua concluído."""
    identificar(client, "joao", [])
    client.post(
        concluir_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario, concluir=True)
    )
    avaliacao = Avaliacao.objects.get(identity_subject="joao")
    identificar(client, subject, papeis, escopo=escopo)

    resposta = client.post(
        rota("interface:reabrir-avaliacao", cenario),
        {
            "avaliacao_id": str(avaliacao.id),
            "expected_revision": avaliacao.revision,
            "motivo": "Quero reabrir.",
            "chave_idempotencia": "reabertura-alheia",
        },
    )

    assert resposta.status_code == 404
    assert Avaliacao.objects.get(pk=avaliacao.pk).estado == Avaliacao.Estado.CONCLUIDA


def test_a_etapa_de_outro_edital_nao_e_alcancavel_nem_por_post(
    client, seletor_ligado, cenario, etapa_b1
):
    """FR-045 na fronteira do Edital: o identificador trocado na URL não atravessa."""
    identificar(client, "maria", [])

    resposta = client.post(
        reverse(
            "interface:mesa-avaliacao-gravar",
            args=[cenario["edital"].id, etapa_b1, cenario["atribuida"].id],
        ),
        corpo_da_avaliacao(cenario),
    )

    assert resposta.status_code == 404
    assert Avaliacao.objects.count() == 0


def test_sem_sessao_nenhum_post_grava(client, seletor_ligado, cenario):
    """Sem identidade a resposta é outra — a identificação —, e o efeito continua sendo nenhum."""
    resposta = client.post(gravar_em(cenario, cenario["atribuida"]), corpo_da_avaliacao(cenario))

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:identificar")
    assert Avaliacao.objects.count() == 0
