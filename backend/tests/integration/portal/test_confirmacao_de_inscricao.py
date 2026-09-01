"""Enviar a inscrição deixa recibo na caixa de entrada.

A `010` original enviava um e-mail só, o do código de acesso, e a `FR-084` dizia isso com todas as
letras. O percurso no navegador mostrou o custo: a pessoa conclui o ato mais importante do ano dela,
o comprovante aparece na tela, e a caixa de entrada não registra nada. Fechada a aba antes de baixar
o PDF, ela fica sem o protocolo — que é justamente o que a página manda guardar.

A mensagem não repete o comprovante: ela dá o protocolo, o código de verificação, o que foi
recebido, e o caminho de volta. **Sem CPF e sem telefone**, que não ajudam quem lê e viajam para
onde a mensagem for encaminhada.
"""

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def pronta(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def enviar(client, inscricao):
    return client.post(
        reverse("portal:revisao", args=[inscricao.id]),
        {"veracidade": "on", "ciencia": "on"},
        follow=True,
    )


def test_o_envio_deixa_recibo_na_caixa_de_quem_enviou(client, caixa, pronta):
    identificar(client, MARIA)

    enviar(client, pronta)

    assert len(caixa) == 1
    mensagem = caixa[0]
    pronta.refresh_from_db()
    assert mensagem.to == [pronta.email]
    assert pronta.protocolo in mensagem.subject
    assert pronta.protocolo in mensagem.body


def test_a_mensagem_traz_o_que_a_pessoa_precisa_guardar(client, caixa, pronta):
    identificar(client, MARIA)

    enviar(client, pronta)
    corpo = caixa[0].body
    pronta.refresh_from_db()

    assert "Código de verificação:" in corpo
    assert "Perfil de vaga:" in corpo
    assert "rg.pdf" in corpo and "diploma.pdf" in corpo, "diz o que foi recebido"
    assert "não implica deferimento" in corpo, "receber não é deferir, no papel e aqui"
    assert "código de acesso a cada entrada" in corpo, "diz como voltar — e não fala em CPF"


def test_a_mensagem_nao_carrega_CPF_nem_telefone(client, caixa, pronta):
    """A caixa é credencial provada, e ainda assim: dado que não ajuda quem lê não viaja."""
    identificar(client, MARIA)
    gravar_dados(
        identidade=MARIA,
        inscricao=pronta,
        dados={"modality_id": MODALIDADE_AC, "telefone": "27999990000"},
    )

    enviar(client, pronta)
    corpo = caixa[0].body

    assert MARIA.cpf not in corpo
    assert "".join(c for c in MARIA.cpf if c.isdigit()) not in corpo
    assert "27999990000" not in corpo


def test_falha_no_envio_da_mensagem_nao_custa_a_inscricao(client, caixa, pronta, monkeypatch):
    """A inscrição é ato administrativo; a mensagem é cortesia do canal.

    Amarrar um ao outro faria uma queda de SMTP desfazer uma inscrição válida — e a pessoa perderia
    o prazo por causa de um servidor de e-mail (Princípio IV).
    """
    from processo_seletivo.inscricoes.application import mensagem

    def explodir(**_):
        raise RuntimeError("smtp fora do ar")

    monkeypatch.setattr(mensagem, "send_mail", explodir)
    identificar(client, MARIA)

    resposta = enviar(client, pronta)
    pronta.refresh_from_db()

    assert resposta.status_code == 200
    assert pronta.protocolo, "a inscrição foi enviada"
    assert pronta.protocolo in resposta.content.decode(), "e o comprovante apareceu"


def test_voltar_ao_comprovante_nao_reenvia_a_mensagem(client, caixa, pronta):
    """Uma inscrição, um recibo. Reabrir a tela não é um novo ato."""
    identificar(client, MARIA)
    enviar(client, pronta)

    client.get(reverse("portal:comprovante", args=[pronta.id]))
    client.post(reverse("portal:revisao", args=[pronta.id]), {"veracidade": "on", "ciencia": "on"})

    assert len(caixa) == 1
