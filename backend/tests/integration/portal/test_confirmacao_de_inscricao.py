"""Enviar a inscrição deixa recibo na caixa de entrada.

A `010` original enviava um e-mail só, o do código de acesso, e a `FR-084` dizia isso com todas as
letras. O percurso no navegador mostrou o custo: a pessoa conclui o ato mais importante do ano dela,
o comprovante aparece na tela, e a caixa de entrada não registra nada. Fechada a aba antes de baixar
o PDF, ela fica sem o protocolo — que é justamente o que a página manda guardar.

A mensagem não repete o comprovante: ela dá o protocolo, o código de verificação, o que foi
recebido, e o caminho de volta. **Sem CPF e sem telefone**, que não ajudam quem lê e viajam para
onde a mensagem for encaminhada.

**A `181` revisou a mensagem e o que a cerca.** O assunto nomeia o Edital e diz "enviada" — a
palavra da área do candidato —, o link leva ao comprovante e não à vitrine, e a tela do comprovante
diz o que aconteceu com a mensagem e deixa a titular tentar de novo quando ela não saiu. O comando,
sem tela, está em `tests/integration/inscricoes/test_confirmacao_por_email.py`.
"""

import re
import uuid
from urllib.parse import unquote

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.inscricoes.application import confirmacao
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import JOAO, MARIA, MODALIDADE_AC, identificar, pdf
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
    assert pronta.protocolo in mensagem.body
    (html,) = [conteudo for conteudo, tipo in mensagem.alternatives if tipo == "text/html"]
    assert f"Protocolo: {pronta.protocolo}" in html, "no preheader, ao lado do assunto na caixa"


def test_a_mensagem_traz_o_que_a_pessoa_precisa_guardar(client, caixa, pronta):
    identificar(client, MARIA)

    enviar(client, pronta)
    corpo = caixa[0].body
    pronta.refresh_from_db()

    assert "Código de verificação:" in corpo
    assert "Perfil de vaga:" in corpo
    assert "rg.pdf" in corpo and "diploma.pdf" in corpo, "diz o que foi recebido"
    assert "Enviada não quer dizer aceita" in corpo, "enviar não é ser aceito"
    assert "O que acontece agora" in corpo
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

    monkeypatch.setattr(mensagem, "entregar", explodir)
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


# --- 181: o assunto, as palavras e o link ---------------------------------------------------------


def test_o_assunto_diz_enviada_e_nomeia_o_edital(client, caixa, pronta):
    """FR-8353, FR-8354: quem se inscreve em duas seleções distingue as mensagens pelo assunto."""
    identificar(client, MARIA)

    enviar(client, pronta)

    edital = pronta.edital
    assert caixa[0].subject == f"Sua inscrição foi enviada — Edital {edital.number}/{edital.year}"


def test_a_mensagem_nao_usa_as_palavras_de_outros_degraus(client, caixa, pronta):
    """FR-8354: "recebida" é o degrau da relação publicada (148); aceita e homologada vêm depois."""
    identificar(client, MARIA)

    enviar(client, pronta)
    mensagem = caixa[0]
    (html,) = [conteudo for conteudo, tipo in mensagem.alternatives if tipo == "text/html"]

    for texto in (mensagem.subject, mensagem.body, html):
        minusculo = texto.lower()
        for palavra in (
            "recebida",
            "recebemos",
            "deferimento",
            "deferida",
            "homolog",
            "confirmada",
        ):
            assert palavra not in minusculo, palavra
        # "aceita" só na frase que diz que enviada **não** é aceita.
        assert minusculo.count("aceita") == minusculo.count("não quer dizer aceita")


def test_sem_anexo_e_sem_link_que_autentica(client, caixa, pronta):
    """FR-8356, D-001: o comprovante vai por link, e o link só leva — quem entra é o código."""
    identificar(client, MARIA)

    enviar(client, pronta)
    mensagem = caixa[0]

    assert mensagem.attachments == []
    enderecos = set(re.findall(r"https?://\S+", mensagem.body))
    assert enderecos == {f"http://testserver/selecoes/inscricoes/{pronta.id}/comprovante"}


def test_o_link_leva_ao_comprovante_de_quem_esta_com_sessao(client, caixa, pronta):
    identificar(client, MARIA)
    enviar(client, pronta)
    link = re.search(r"https?://testserver(\S+)", caixa[0].body).group(1)

    resposta = client.get(link)

    assert resposta.status_code == 200
    assert pronta.protocolo in resposta.content.decode()


def test_o_link_sem_sessao_leva_ao_acesso_e_volta_ao_comprovante(client, caixa, pronta):
    """FR-8357: o link não autentica; sem sessão, o acesso, e o destino guardado."""
    identificar(client, MARIA)
    enviar(client, pronta)
    link = re.search(r"https?://testserver(\S+)", caixa[0].body).group(1)
    client.logout()

    resposta = client.get(link)

    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("portal:acesso") + "?destino=")
    client.get(resposta["Location"])
    assert client.session["portal_acesso_destino"] == link


def test_sem_sessao_o_identificador_inventado_recebe_o_mesmo_redirecionamento(client, pronta):
    """FR-8357: a resposta sem sessão não diz se a inscrição existe."""
    inventado = reverse("portal:comprovante", args=[uuid.uuid4()])
    real = reverse("portal:comprovante", args=[pronta.id])

    para_o_inventado = client.get(inventado)
    para_o_real = client.get(real)

    assert para_o_inventado.status_code == para_o_real.status_code == 302
    assert unquote(para_o_inventado["Location"]).replace(inventado, real) == unquote(
        para_o_real["Location"]
    )


def test_envio_recusado_nao_manda_mensagem(client, caixa, pronta):
    """FR-8350: sem as declarações, o envio é recusado, e nada sai."""
    identificar(client, MARIA)

    client.post(reverse("portal:revisao", args=[pronta.id]), {"veracidade": "on"})

    pronta.refresh_from_db()
    assert pronta.status == Inscricao.Status.RASCUNHO
    assert caixa == []
    assert confirmacao.tentativas(pronta) == []


# --- 181: a tela do comprovante e a nova tentativa
# -------------------------------------------------


FORA_DO_AR = "tests.integration.inscricoes.test_confirmacao_por_email.CorreioForaDoAr"


def test_o_comprovante_diz_inscricao_enviada_e_para_onde_foi_a_mensagem(client, caixa, pronta):
    """FR-8362, FR-8365: a mesma palavra da mensagem, e o endereço que recebeu."""
    identificar(client, MARIA)

    corpo = enviar(client, pronta).content.decode()

    assert "✓ Inscrição enviada" in corpo
    assert "Inscrição realizada" not in corpo
    assert f"Enviamos a confirmação para <strong>{pronta.email}</strong>" in corpo
    assert "caixa de spam" in corpo
    assert "Enviar a confirmação de novo" not in corpo


def test_falhou_a_tela_avisa_e_a_titular_tenta_de_novo(client, caixa, pronta, settings):
    """FR-8362, FR-8363, D-003: a falha é visível e tratável por quem está na tela."""
    settings.EMAIL_BACKEND = FORA_DO_AR
    identificar(client, MARIA)

    corpo = enviar(client, pronta).content.decode()

    pronta.refresh_from_db()
    assert pronta.status == Inscricao.Status.SUBMETIDA, "a inscrição foi enviada do mesmo jeito"
    assert f"Não conseguimos enviar a confirmação para {pronta.email}." in corpo
    assert "Enviar a confirmação de novo" in corpo
    assert "Enviamos a confirmação" not in corpo

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    resposta = client.post(reverse("portal:comprovante-confirmacao", args=[pronta.id]), follow=True)

    assert len(caixa) == 1
    corpo = resposta.content.decode()
    assert f"Enviamos a confirmação para <strong>{pronta.email}</strong>" in corpo
    assert "Enviar a confirmação de novo" not in corpo
    assert [t.numero for t in confirmacao.tentativas(pronta)] == [1, 2]


def test_a_aba_antiga_nao_manda_a_segunda(client, caixa, pronta):
    """FR-8351: o botão de uma tela velha, depois de a confirmação ter saído."""
    identificar(client, MARIA)
    enviar(client, pronta)

    resposta = client.post(reverse("portal:comprovante-confirmacao", args=[pronta.id]))

    assert resposta.status_code == 302
    assert len(caixa) == 1
    assert len(confirmacao.tentativas(pronta)) == 1


def test_nova_tentativa_so_da_titular_e_da_enviada(client, caixa, pronta, settings):
    """FR-8364: sem sessão, outra pessoa ou rascunho — a resposta de inexistente, e nada sai."""
    endereco = reverse("portal:comprovante-confirmacao", args=[pronta.id])

    assert client.post(endereco).status_code == 404, "sem sessão"
    identificar(client, MARIA)
    assert client.post(endereco).status_code == 404, "rascunho"

    settings.EMAIL_BACKEND = FORA_DO_AR
    enviar(client, pronta)
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    identificar(client, JOAO)
    assert client.post(endereco).status_code == 404, "outra pessoa"
    inventado = reverse("portal:comprovante-confirmacao", args=[uuid.uuid4()])
    assert client.post(inventado).status_code == 404, "inexistente"
    assert client.get(endereco).status_code == 405

    assert caixa == []
    assert len(confirmacao.tentativas(pronta)) == 1


def test_sem_tentativa_o_comprovante_nao_fala_da_mensagem(client, caixa, pronta, monkeypatch):
    """FR-8362: a inscrição anterior à 181 — o sistema não sabe, e não afirma."""
    from processo_seletivo.portal import views

    monkeypatch.setattr(views, "_confirmar_por_email", lambda *a, **k: None)
    identificar(client, MARIA)

    corpo = enviar(client, pronta).content.decode()

    assert "✓ Inscrição enviada" in corpo
    assert "confirmação para" not in corpo


def test_o_aviso_da_mensagem_fica_fora_do_papel(client, caixa, pronta, settings):
    """FR-8366: o aviso é da tela; o PDF não muda quando a confirmação muda."""
    settings.EMAIL_BACKEND = FORA_DO_AR
    identificar(client, MARIA)
    corpo = enviar(client, pronta).content.decode()
    aviso = re.search(r'<div class="([^"]*)" role="status">\s*<p><strong>Não conseguimos', corpo)
    assert "nao-imprime" in aviso.group(1).split()
    pdf_com_a_falha = client.get(reverse("portal:comprovante-pdf", args=[pronta.id])).content

    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    client.post(reverse("portal:comprovante-confirmacao", args=[pronta.id]))
    pdf_com_a_mensagem = client.get(reverse("portal:comprovante-pdf", args=[pronta.id])).content

    assert pdf_com_a_falha == pdf_com_a_mensagem
