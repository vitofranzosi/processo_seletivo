"""A data de nascimento no núcleo da identidade (180, histórias 1 e 2).

Nome, CPF e data numa tela só, pedidos uma vez (FR-8300, FR-8301); o cadastro de antes da `180` a
informa na próxima vaga, sem redigitar nome e CPF (FR-8302, UX-1001); e a data congela com o CPF —
mas só a que existe (FR-8309, D-001, R2 da pesquisa).
"""

from datetime import date

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import credenciais as nucleo
from processo_seletivo.identidade.models import CandidateIdentity, novo_subject
from processo_seletivo.inscricoes.domain.pessoais import RECUSA_INEXISTENTE, RECUSA_VAZIA
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF = "123.456.789-09"


def _entrar(client, identidade):
    sessao = client.session
    sessao["portal_identidade"] = str(identidade.pk)
    sessao.save()


@pytest.fixture
def nova(client):
    identidade = associacao.criar_identidade_com("nova@exemplo.test", "nova@exemplo.test")
    _entrar(client, identidade)
    return identidade


@pytest.fixture
def antiga(client):
    """Nome e CPF de antes da `180`, e nenhuma data."""
    identidade = CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome="Maria Silva",
        cpf_normalizado="12345678909",
        created_at=timezone.now(),
    )
    associacao.associar_credencial(identidade, "antiga@exemplo.test", "antiga@exemplo.test")
    _entrar(client, identidade)
    return identidade


def _campo(corpo, nome):
    inicio = corpo.index(f'id="{nome}"')
    return corpo[corpo.rindex("<input", 0, inicio) : corpo.index(">", inicio)]


# --- História 1 ------------------------------------------------------------------------------


def test_a_tela_pede_nome_cpf_e_data(client, nova):
    corpo = client.get(reverse("portal:meus-dados")).content.decode()

    for campo in ("nome", "cpf", "data_nascimento"):
        assert f'name="{campo}"' in corpo
    data = _campo(corpo, "data_nascimento")
    # Texto, e não o seletor do celular (UX-1000); o navegador pode preencher.
    assert 'type="text"' in data
    assert 'autocomplete="bday"' in data
    assert 'inputmode="numeric"' in data


def test_a_tela_diz_para_que_serve_a_data(client, nova):
    """A finalidade, no ponto da coleta (FR-8314)."""
    corpo = client.get(reverse("portal:meus-dados")).content.decode()
    assert "confirmar sua identidade em caso de dúvida" in corpo


def test_sem_data_a_identidade_falta_o_nucleo(nova):
    CandidateIdentity.objects.filter(pk=nova.pk).update(nome="Maria Silva", cpf_normalizado="1")
    nova.refresh_from_db()
    assert nucleo.falta_o_nucleo(nova)


def test_data_vazia_e_recusada_sem_perder_o_resto(client, nova):
    resposta = client.post(
        reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": ""}
    )
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert RECUSA_VAZIA in corpo
    assert 'value="Maria Silva"' in corpo
    assert f'value="{CPF}"' in corpo
    assert 'aria-invalid="true"' in _campo(corpo, "data_nascimento")
    nova.refresh_from_db()
    assert nova.data_nascimento is None


def test_data_impossivel_e_recusada_e_volta_como_digitada(client, nova):
    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": "31/02/2000"},
    )
    corpo = resposta.content.decode()

    assert RECUSA_INEXISTENTE in corpo
    assert 'value="31/02/2000"' in corpo


def test_os_tres_validos_sao_gravados_e_voltam_a_vaga(client, nova, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    assert client.post(vaga)["Location"] == reverse("portal:meus-dados")

    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": "07/03/1998"},
    )

    nova.refresh_from_db()
    assert nova.data_nascimento == date(1998, 3, 7)
    assert reverse("portal:selecao", args=[selecao.id]) in resposta["Location"]


# --- História 2 ------------------------------------------------------------------------------


def test_o_cadastro_antigo_vai_a_seus_dados_na_proxima_vaga(client, antiga, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    assert client.post(vaga)["Location"] == reverse("portal:meus-dados")
    assert not Inscricao.objects.exists()


def test_o_cadastro_antigo_ve_nome_e_cpf_preenchidos_e_o_foco_na_data(client, antiga):
    corpo = client.get(reverse("portal:meus-dados")).content.decode()

    assert 'value="Maria Silva"' in _campo(corpo, "nome")
    assert f'value="{CPF}"' in _campo(corpo, "cpf")
    assert "autofocus" in _campo(corpo, "data_nascimento")
    assert "autofocus" not in _campo(corpo, "nome")


def test_informada_a_data_o_cadastro_antigo_segue_para_a_vaga(client, antiga, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    client.post(vaga)
    client.post(
        reverse("portal:meus-dados"),
        {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": "07/03/1998"},
    )

    resposta = client.post(vaga)

    assert reverse("portal:meus-dados") not in resposta["Location"]
    assert Inscricao.objects.count() == 1


# --- Congelamento (D-001, R2) ----------------------------------------------------------------


def _com_inscricao_enviada(identidade, edital):
    """Uma enviada pelo caminho mais curto: rascunho criado e promovido, como na `010`."""
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    rascunho = Inscricao.objects.create(
        identity_subject=identidade.subject,
        edital=edital,
        profile_id=PERFIL_DOCENTE,
        nome=identidade.nome,
        cpf=CPF,
        cpf_normalizado="12345678909",
        created_at=timezone.now(),
    )
    Inscricao.objects.filter(pk=rascunho.pk).update(
        status=Inscricao.Status.SUBMETIDA,
        submitted_at=timezone.now(),
        declaracoes_aceitas_em=timezone.now(),
        versao_aceita=VersaoConsolidada.objects.filter(edital_id=edital.id).first(),
        protocolo="INS-2027-AAAA1111",
    )


def test_a_data_congela_com_o_cpf(client, antiga, selecao):
    CandidateIdentity.objects.filter(pk=antiga.pk).update(data_nascimento=date(1998, 3, 7))
    _com_inscricao_enviada(antiga, selecao)

    corpo = client.get(reverse("portal:meus-dados")).content.decode()
    assert "readonly" in _campo(corpo, "data_nascimento")
    assert "Você já enviou uma inscrição com esta data" in corpo

    client.post(
        reverse("portal:meus-dados"),
        {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": "01/01/1990"},
    )
    antiga.refresh_from_db()
    assert antiga.data_nascimento == date(1998, 3, 7)


def test_quem_ja_se_inscreveu_sem_data_pode_informa_la_uma_vez(client, antiga, selecao):
    """Sem esta exceção, o cadastro de antes da `180` ficaria preso fora de toda vaga (R2)."""
    _com_inscricao_enviada(antiga, selecao)
    antiga.refresh_from_db()
    assert nucleo.data_editavel(antiga)

    client.post(
        reverse("portal:meus-dados"),
        {"nome": "Maria Silva", "cpf": CPF, "data_nascimento": "07/03/1998"},
    )

    antiga.refresh_from_db()
    assert antiga.data_nascimento == date(1998, 3, 7)
    assert not nucleo.data_editavel(antiga)
