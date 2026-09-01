"""Nenhum candidato alcança inscrição ou documento de outro — e a recusa não enumera.

`404` e não `403`, pelo mesmo motivo que a `009` já adotara: dizer "existe, mas não é seu" já
entrega que existe. Numa seleção, a lista de quem se inscreveu é justamente o que ninguém de fora
pode montar por tentativa.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import (
    JOAO,
    MARIA,
    MODALIDADE_AC,
    PERFIL_DOCENTE,
    identificar,
    pdf,
)
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.authorization]

INEXISTENTE = "00000000-0000-0000-0000-0000000009ff"


def enviar(identidade, selecao):
    inscricao = abrir_inscricao(
        identidade=identidade, edital_id=selecao.id, profile_id=PERFIL_DOCENTE
    )
    inscricao = gravar_dados(
        identidade=identidade, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "d.pdf")):
        anexar_documento(
            identidade=identidade, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=identidade,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=f"envio-{identidade.subject[-6:]}",
    )


@pytest.fixture
def do_joao(selecao):
    return enviar(JOAO, selecao)


def test_a_inscricao_de_outro_responde_404(client, do_joao):
    identificar(client, MARIA)
    assert client.get(reverse("portal:inscricao", args=[do_joao.id])).status_code == 404


def test_o_documento_de_outro_responde_404(client, do_joao):
    identificar(client, MARIA)
    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[do_joao.id, DOCUMENTO_DE_TODOS])
    )
    assert resposta.status_code == 404


def test_baixar_o_documento_de_outro_tambem_responde_404(client, do_joao):
    identificar(client, MARIA)
    endereco = reverse("portal:documento-do-candidato", args=[do_joao.id, DOCUMENTO_DE_TODOS])
    assert client.get(f"{endereco}?baixar=1").status_code == 404


def test_o_comprovante_de_outro_responde_404(client, do_joao):
    identificar(client, MARIA)
    for rota in ("portal:comprovante", "portal:comprovante-pdf"):
        assert client.get(reverse(rota, args=[do_joao.id])).status_code == 404, rota


def _sem_csrf(corpo: bytes) -> bytes:
    """O token muda a cada renderização e não diz nada sobre quem existe."""
    import re

    return re.sub(rb'value="[A-Za-z0-9]{32,}"', b'value="TOKEN"', corpo)


def test_a_recusa_e_indistinguivel_da_inexistente(client, do_joao):
    """Mesmo status **e** mesmo corpo: um corpo diferente continua dizendo qual id existe."""
    identificar(client, MARIA)

    alheia = client.get(reverse("portal:inscricao", args=[do_joao.id]))
    inexistente = client.get(reverse("portal:inscricao", args=[INEXISTENTE]))

    assert alheia.status_code == inexistente.status_code == 404
    assert _sem_csrf(alheia.content) == _sem_csrf(inexistente.content)


def test_sem_sessao_nada_e_alcancavel(client, do_joao):
    for rota, args in (
        ("portal:inscricao", [do_joao.id]),
        ("portal:comprovante", [do_joao.id]),
    ):
        assert client.get(reverse(rota, args=args)).status_code == 404, rota
