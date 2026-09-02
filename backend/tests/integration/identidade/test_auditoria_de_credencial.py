"""Os atos de credencial na trilha existente — e o que fica de fora dela (FR-088, FR-089).

Código inválido não é ato de negócio: transformar cada tentativa numa linha de auditoria encheria
a trilha de ruído e apagaria o sinal que ela existe para guardar.

E a limitação está declarada, não escondida: o evento não tem escopo institucional, porque não
pertence a Edital nenhum — e por isso não aparece na consulta administrativa, que filtra por escopo
(D-012).
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MEU = "meu@exemplo.test"
NOVO = "novo@exemplo.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(MEU, MEU)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def atos():
    return list(
        RegistroAuditoria.objects.filter(aggregate_type="CandidateIdentity").values_list(
            "operation", flat=True
        )
    )


def test_associar_credencial_e_auditado(client, dentro, canal):
    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    client.post(
        reverse("portal:acesso-codigo"),
        {"codigo": re.search(r"\b(\d{6})\b", canal[-1].body).group(1)},
    )

    assert atos() == ["ASSOCIAR_CREDENCIAL"]


def test_remover_credencial_e_auditado(client, dentro):
    associacao.associar_credencial(dentro, NOVO, NOVO)
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)

    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    assert atos() == ["REMOVER_CREDENCIAL"]


def test_o_ato_registra_o_ator_opaco_e_a_identidade(client, dentro):
    associacao.associar_credencial(dentro, NOVO, NOVO)
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)
    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    registro = RegistroAuditoria.objects.get(aggregate_type="CandidateIdentity")
    assert registro.actor_subject == dentro.subject
    assert registro.aggregate_id == dentro.pk
    assert registro.occurred_at is not None


def test_o_ato_nao_carrega_endereco_nem_cpf(client, dentro):
    associacao.associar_credencial(dentro, NOVO, NOVO)
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)
    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    tudo = " ".join(
        str(valor)
        for valor in RegistroAuditoria.objects.filter(
            aggregate_type="CandidateIdentity"
        ).values().first().values()
    )
    assert NOVO not in tudo and "12345678909" not in tudo


def test_o_escopo_e_vazio_e_a_consequencia_esta_declarada(client, dentro):
    """Não pertence a Edital nenhum — e por isso não aparece na consulta por escopo (D-012)."""
    associacao.associar_credencial(dentro, NOVO, NOVO)
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)
    client.post(reverse("portal:conta-remover", args=[credencial.id]))

    registro = RegistroAuditoria.objects.get(aggregate_type="CandidateIdentity")
    assert registro.institution_scope == ""
    assert not RegistroAuditoria.objects.filter(institution_scope="cefor").filter(
        aggregate_type="CandidateIdentity"
    ).exists()


def test_codigo_invalido_nao_vira_ato_de_negocio(client, dentro, canal):
    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    for _ in range(3):
        client.post(reverse("portal:acesso-codigo"), {"codigo": "000000"})

    assert atos() == []


def test_o_ato_e_o_registro_commitam_juntos(client, dentro, monkeypatch):
    """Auditoria dentro da transação do ato (revisão, Princípio IV).

    A primeira versão gravava a credencial, comitava, e só então escrevia na trilha. Uma falha
    entre as duas deixaria a credencial existindo sem evento nenhum que a explicasse. Aqui a falha
    é forçada no registro: se as duas coisas estiverem na mesma transação, nem a credencial fica.
    """
    from processo_seletivo.identidade.application import credenciais as nucleo

    def explodir(*_args, **_kwargs):
        raise RuntimeError("trilha indisponível")

    monkeypatch.setattr(nucleo, "registrar_ato", explodir)

    with pytest.raises(RuntimeError):
        nucleo.adicionar(dentro, email_canonico=NOVO, email_como_informado=NOVO)

    assert not CandidateEmail.objects.filter(email_canonico=NOVO).exists(), (
        "a credencial não pode sobreviver ao registro que a explica"
    )


def test_a_remocao_tambem_desfaz_quando_a_trilha_falha(client, dentro, monkeypatch):
    from processo_seletivo.identidade.application import credenciais as nucleo

    associacao.associar_credencial(dentro, NOVO, NOVO)
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=NOVO)

    def explodir(*_args, **_kwargs):
        raise RuntimeError("trilha indisponível")

    monkeypatch.setattr(nucleo, "registrar_ato", explodir)

    with pytest.raises(RuntimeError):
        nucleo.remover(dentro, credencial.pk)

    assert CandidateEmail.objects.filter(pk=credencial.pk).exists()
