"""A demonstração de segurança do §25 da spec — condição de conclusão, e não anexo.

O maior risco introduzido por esta feature não é visual: é a tomada de identidade. Cada caso aqui
é um dos seis que a spec exige, na ordem em que ela os lista, e cada um afirma o desfecho que a
pessoa legítima observa.
"""

import re
import uuid

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import (
    CandidateEmail,
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal import identidade as identidade_do_candidato
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

CPF_DE_MARIA = "12345678909"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def enviar(identidade, selecao, chave):
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
        idempotency_key=chave,
    )


def codigo(canal):
    return re.search(r"\b(\d{6})\b", canal[-1].body).group(1)


# ---------------------------------------------------------------------------
# Caso 1 — endereçamento direto
# ---------------------------------------------------------------------------


def test_caso_1_trocar_o_identificador_nao_alcanca_nada_de_outro(client, selecao):
    de_joao = enviar(JOAO, selecao, "demo-seguranca-joao")
    identificar(client, MARIA)

    for endereco in (
        reverse("portal:inscricao", args=[de_joao.id]),
        reverse("portal:acompanhamento", args=[de_joao.id]),
        reverse("portal:comprovante", args=[de_joao.id]),
        reverse("portal:documento-do-candidato", args=[de_joao.id, DOCUMENTO_DE_TODOS]),
    ):
        assert client.get(endereco).status_code == 404, endereco


# ---------------------------------------------------------------------------
# Caso 2 — endereço arbitrário com CPF conhecido
# ---------------------------------------------------------------------------


def test_caso_2_conhecer_o_cpf_alheio_nao_da_acesso(client, canal, selecao):
    de_maria = enviar(MARIA, selecao, "demo-seguranca-maria")

    client.post(reverse("portal:acesso"), {"email": "atacante@exemplo.test"})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" in corpo
    assert str(de_maria.id) not in corpo
    do_atacante = CandidateEmail.objects.get(
        email_canonico="atacante@exemplo.test"
    ).identidade
    assert do_atacante.cpf_normalizado == "", "nenhum vínculo com o CPF de ninguém"
    assert client.get(reverse("portal:inscricao", args=[de_maria.id])).status_code == 404


# ---------------------------------------------------------------------------
# Caso 3 — precedência
# ---------------------------------------------------------------------------


def test_caso_3_agir_antes_nao_reserva_o_cpf_alheio(client, canal, selecao):
    """E a inscrição legítima **não** é recusada por causa do CPF que o terceiro declarou."""
    do_terceiro = CandidateIdentity.objects.create(
        subject=novo_subject(), nome="Terceiro Qualquer", cpf_normalizado=CPF_DE_MARIA,
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=do_terceiro.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Terceiro Qualquer",
        cpf=CPF_DE_MARIA,
        cpf_normalizado=CPF_DE_MARIA,
        email="terceiro@exemplo.test",
        created_at=timezone.now(),
    )

    de_maria = enviar(MARIA, selecao, "demo-seguranca-precedencia")

    assert de_maria.status == Inscricao.Status.SUBMETIDA, "a legítima não é recusada"
    assert de_maria.identity_subject == MARIA.subject


# ---------------------------------------------------------------------------
# Caso 4 — endereço reciclado
# ---------------------------------------------------------------------------


def test_caso_4_quem_controla_a_caixa_hoje_entra_na_propria_identidade(client, canal, selecao):
    """Maria digitou por engano um endereço que hoje é de outra pessoa."""
    legada = CandidateIdentity.objects.create(
        subject=novo_subject(), nome="Maria", cpf_normalizado=CPF_DE_MARIA,
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=legada.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria",
        cpf=CPF_DE_MARIA,
        cpf_normalizado=CPF_DE_MARIA,
        email="joao@reciclado.test",
        created_at=timezone.now(),
    )

    client.post(reverse("portal:acesso"), {"email": "joao@reciclado.test"})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" in corpo
    legada.refresh_from_db()
    assert Inscricao.objects.get(identity_subject=legada.subject), "a legada segue intacta"


# ---------------------------------------------------------------------------
# Caso 5 — engano no convite
# ---------------------------------------------------------------------------


def test_caso_5_recusar_por_engano_e_retomar(client, canal, selecao):
    legada = CandidateIdentity.objects.create(
        subject=novo_subject(), nome="Maria", cpf_normalizado=CPF_DE_MARIA,
        created_at=timezone.now(),
    )
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=legada.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria",
        cpf=CPF_DE_MARIA,
        cpf_normalizado=CPF_DE_MARIA,
        email="maria@antiga.test",
        created_at=timezone.now(),
    )

    client.post(reverse("portal:acesso"), {"email": "maria@antiga.test"})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})
    client.post(reverse("portal:acesso-reconciliar"), {"acao": "continuar"})

    client.post(reverse("portal:acesso-retomar"))
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})
    client.post(
        reverse("portal:acesso-reconciliar"), {"acao": "confirmar", "cpf": "123.456.789-09"}
    )

    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert "Você ainda não possui inscrições" not in corpo
    assert CandidateEmail.objects.get(email_canonico="maria@antiga.test").identidade_id == (
        legada.pk
    )


# ---------------------------------------------------------------------------
# Caso 6 — fixação de sessão
# ---------------------------------------------------------------------------


def test_caso_6_a_sessao_conhecida_nao_vale_depois_do_acesso(client, canal):
    from processo_seletivo.portal.views import CHAVE_DO_ENDERECO

    sessao = client.session
    sessao[CHAVE_DO_ENDERECO] = "alguem@exemplo.test"
    sessao.save()
    client.cookies["sessionid"] = sessao.session_key
    conhecida = sessao.session_key

    from processo_seletivo.identidade.application import desafio as servico

    _, valor = servico.solicitar(
        email_canonico="alguem@exemplo.test", finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    client.post(reverse("portal:acesso-codigo"), {"codigo": valor})

    assert client.session.session_key != conhecida
    assert identidade_do_candidato.CHAVE_SESSAO in client.session
