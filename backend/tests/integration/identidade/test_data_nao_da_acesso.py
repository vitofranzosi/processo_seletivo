"""Quem sabe o CPF e a data de nascimento de outra pessoa não alcança nada dela (180, FR-8310).

O caso-limite da spec, pelo lado de quem tentaria: uma segunda pessoa entra com o próprio e-mail e
declara o nome, o CPF e a data de Maria. O sistema aceita a declaração — CPF e data são declarados,
nunca provados, e duas identidades podem declarar o mesmo (a FR-064 da `010`) —, e é justamente por
isso que ela não pode abrir porta nenhuma.

A varredura de `tests/unit/identidade/test_data_nao_decide_identidade.py` prende que nenhum caminho
de acesso lê a coluna; este arquivo mostra o efeito, que é o que a pessoa de fato tentaria.
"""

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import CPF_MARIA, MARIA, MODALIDADE_AC, NASCIMENTO_PADRAO, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def de_maria(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-de-maria",
    )


@pytest.fixture
def outra_pessoa(de_maria):
    """Entrou pelo próprio e-mail, e declara os três dados de Maria em "Seus dados"."""
    identidade = associacao.criar_identidade_com("outra@exemplo.test", "outra@exemplo.test")
    client = Client()
    sessao = client.session
    sessao["portal_identidade"] = str(identidade.pk)
    sessao.save()
    resposta = client.post(
        reverse("portal:meus-dados"),
        {
            "nome": MARIA.nome,
            "cpf": CPF_MARIA,
            "data_nascimento": NASCIMENTO_PADRAO.strftime("%d/%m/%Y"),
        },
    )
    assert resposta.status_code == 302, resposta.content
    identidade.refresh_from_db()
    assert identidade.data_nascimento == NASCIMENTO_PADRAO, "a declaração é aceita: não é prova"
    return client, identidade


def test_declarar_cpf_e_data_de_outra_pessoa_nao_funde_os_cadastros(outra_pessoa):
    """A coincidência não decide a quem pertence um cadastro: continuam sendo dois."""
    _client, identidade = outra_pessoa
    de_maria_mesma = CandidateIdentity.objects.get(subject=MARIA.subject)

    assert identidade.pk != de_maria_mesma.pk
    assert CandidateIdentity.objects.filter(cpf_normalizado="12345678909").count() == 2
    assert not identidade.credenciais.filter(email_canonico=MARIA.email).exists()


def test_declarar_cpf_e_data_de_outra_pessoa_nao_abre_as_inscricoes_dela(outra_pessoa, de_maria):
    client, _identidade = outra_pessoa

    lista = client.get(reverse("portal:inscricoes")).content.decode()
    comprovante = client.get(reverse("portal:comprovante", args=[de_maria.id]))
    acompanhamento = client.get(reverse("portal:acompanhamento", args=[de_maria.id]))

    assert de_maria.protocolo not in lista
    assert comprovante.status_code == 404
    assert acompanhamento.status_code == 404


def test_a_entrada_continua_sendo_so_pelo_codigo_do_email(de_maria):
    """Nenhuma tela de acesso pede ou aceita a data: quem não provou o e-mail não entra."""
    anonimo = Client()

    tela = anonimo.get(reverse("portal:acesso")).content.decode()
    tentativa = anonimo.post(
        reverse("portal:acesso"),
        {
            "cpf": CPF_MARIA,
            "data_nascimento": NASCIMENTO_PADRAO.strftime("%d/%m/%Y"),
            "nome": MARIA.nome,
        },
    )

    assert "nascimento" not in tela.lower()
    assert "portal_identidade" not in anonimo.session
    assert de_maria.protocolo not in tentativa.content.decode()
    assert anonimo.get(reverse("portal:inscricoes")).status_code == 302
