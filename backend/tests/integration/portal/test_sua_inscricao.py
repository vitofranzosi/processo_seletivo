"""A tela `Sua inscrição` (US3 da 009, FR-034 a FR-041).

Duas propriedades, e as duas são de produto: o que a identidade forneceu não é pedido de novo, e o
que não se aplica não aparece. A terceira é de persistência: ninguém precisa entender que existe
um rascunho para não perder o que fez.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)
MODALIDADE_PPP = identificador(404, 0)
MODALIDADE_DE_OUTRO_PERFIL = identificador(407, 0)


@pytest.fixture
def selecao_aberta(settings, api_client, manager_headers, process_payload):
    settings.PORTAL_IDENTIDADE_DEMO = True
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


def _abrir(client, edital, perfil=PERFIL_DOCENTE):
    client.post(
        reverse("portal:identificar"),
        {"nome": "Maria Silva", "cpf": "123.456.789-09", "email": "maria@exemplo.br"},
    )
    resposta = client.post(reverse("portal:inscrever", args=[edital.id, perfil]))
    return resposta["Location"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_os_dados_da_identidade_aparecem_como_informacao(client, selecao_aberta):
    """FR-037: informação, e não campo desabilitado sem explicação."""
    corpo = client.get(_abrir(client, selecao_aberta)).content.decode()

    assert "Maria Silva" in corpo
    assert "maria@exemplo.br" in corpo
    assert 'name="nome"' not in corpo, "o nome não é pedido de novo"
    assert 'name="cpf"' not in corpo
    assert 'name="email"' not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_contexto_da_vaga_fica_visivel(client, selecao_aberta):
    """FR-035: para qual Edital e qual vaga, o tempo todo."""
    corpo = client.get(_abrir(client, selecao_aberta)).content.decode()

    assert "Professor de Informática" in corpo
    assert "Processo Seletivo 2026" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_perfil_com_modalidade_pergunta_a_concorrencia(client, selecao_aberta):
    corpo = client.get(_abrir(client, selecao_aberta)).content.decode()

    assert "Concorrência" in corpo
    assert "Pessoas pretas, pardas e indígenas" in corpo
    assert "Ampla concorrência" in corpo, "a do Edital, e não uma inventada pelo sistema"
    assert corpo.count("Ampla concorrência") == 1, (
        "o sistema não acrescenta uma segunda ampla concorrência ao lado da declarada (FR-039)"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_perfil_sem_modalidade_declarada_nao_pergunta_nada(
    client, settings, api_client, manager_headers, process_payload
):
    """FR-038 e FR-039: sem escolha relevante, nenhuma pergunta — e nenhuma entidade inventada."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    # O Perfil técnico passa a não declarar modalidade nenhuma: é o caso em que a pergunta não
    # deve existir, e não o caso em que ela aparece com uma opção só.
    rascunho["profiles"][1]["competitionModalities"] = []
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)

    corpo = client.get(_abrir(client, edital, perfil=PERFIL_TECNICO)).content.decode()

    assert "Concorrência" not in corpo
    assert "Ampla concorrência" not in corpo, "nenhuma modalidade é inventada"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_telefone_e_a_modalidade_sao_guardados_sem_botao_salvar(client, selecao_aberta):
    endereco = _abrir(client, selecao_aberta)

    assert "Salvar" not in client.get(endereco).content.decode(), "avançar é o que guarda (P-005)"

    resposta = client.post(endereco, {"telefone": "(27) 99999-0000", "modalidade": MODALIDADE_PPP})

    assert resposta.status_code == 302, "e avançar leva à revisão"
    inscricao = Inscricao.objects.get()
    assert inscricao.telefone == "(27) 99999-0000"
    assert str(inscricao.modality_id) == MODALIDADE_PPP


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_volta_encontra_o_que_deixou(client, selecao_aberta):
    """SC-008: sair e voltar não custa nada — e ninguém precisou salvar."""
    endereco = _abrir(client, selecao_aberta)
    client.post(endereco, {"telefone": "(27) 99999-0000", "modalidade": MODALIDADE_PPP})

    corpo = client.get(endereco).content.decode()

    assert "(27) 99999-0000" in corpo
    assert Inscricao.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_modalidade_de_outro_perfil_e_recusada_no_servidor(client, selecao_aberta):
    """A tela só oferece as do Perfil; isto responde ao POST forjado."""
    endereco = _abrir(client, selecao_aberta)

    resposta = client.post(endereco, {"modalidade": MODALIDADE_DE_OUTRO_PERFIL})

    assert resposta.status_code == 200
    assert "não é deste Perfil" in resposta.content.decode()
    assert Inscricao.objects.get().modality_id is None


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_da_inscricao_nao_e_armazenavel_pelo_navegador(client, selecao_aberta):
    resposta = client.get(_abrir(client, selecao_aberta))

    assert "no-store" in resposta.headers["Cache-Control"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_endereco_da_inscricao_nao_carrega_dado_pessoal(client, selecao_aberta):
    """FR-073: nem CPF, nem nome, nem e-mail no endereço."""
    endereco = _abrir(client, selecao_aberta)

    assert "12345678909" not in endereco
    assert "maria" not in endereco.lower()
