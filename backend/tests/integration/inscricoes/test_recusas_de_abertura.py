"""O que impede abrir ou preencher uma inscrição — e o que a revisão da entrega 3 revelou.

Sete defeitos foram encontrados depois que a entrega 3 já estava commitada, e os cinco que valem
regressão estão aqui. O que eles têm em comum é o modo de falhar: nenhum quebra nada visível, e
todos produzem uma inscrição que parece válida.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.identidade import IdentidadeDoCandidato, subject_de
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import actor_headers, identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

CPF = "123.456.789-09"
MARIA = IdentidadeDoCandidato(subject_de(CPF), "Maria Silva", CPF, "m@ex.br")
PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)
MODALIDADE_AC = identificador(403, 0)
MODALIDADE_PPP = identificador(404, 0)


def _publicar(api_client, manager_headers, process_payload, *, ajustar=None):
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    if ajustar:
        ajustar(rascunho)
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


# ---------------------------------------------------------------------------
# O identificador do candidato não carrega o documento dele
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_subject_nao_contem_o_cpf(api_client, manager_headers, process_payload):
    """FR-078: o identificador que existe para não depender de dado pessoal não é feito dele.

    A primeira redação usava `demo:<cpf>`, e o `subject` vai para `actor_subject` em cada registro
    de auditoria — o CPF completo ficava gravado em todo ato praticado pela pessoa.
    """
    edital = _publicar(api_client, manager_headers, process_payload)

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    registro = RegistroAuditoria.objects.get(aggregate_id=inscricao.id)
    for lugar in (registro.actor_subject, MARIA.subject):
        assert "12345678909" not in lugar
        assert CPF not in lugar
    assert registro.actor_subject == MARIA.subject


def test_o_subject_e_estavel_para_a_mesma_pessoa():
    assert subject_de("123.456.789-09") == subject_de("12345678909")
    assert subject_de("123.456.789-09") != subject_de("987.654.321-00")


# ---------------------------------------------------------------------------
# Consultável e recebendo inscrição são decisões diferentes
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_edital_cancelado_nao_recebe_inscricao(
    client, settings, api_client, manager_headers, process_payload
):
    """A página continua legível — o ato publicado não se apaga — e não convida mais ninguém."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/cancelamentos",
        {"reason": "Perda de objeto"},
        format="json",
        **{
            **actor_headers("gestor-a", ["edital:cancelar"], key="cancelamento-insc-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=edital.pk).revision}"',
        },
    )

    pagina = client.get(reverse("portal:selecao", args=[edital.id]))

    assert pagina.status_code == 200, "continua consultável"
    assert "Inscrever-se nesta vaga" not in pagina.content.decode()
    with pytest.raises(DomainError) as recusa:
        abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    assert recusa.value.code == "registration_closed"
    assert Inscricao.objects.count() == 0


# ---------------------------------------------------------------------------
# A modalidade decide quais documentos serão pedidos, e por isso não fica em branco
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_com_duas_modalidades_a_escolha_e_obrigatoria(
    client, settings, api_client, manager_headers, process_payload
):
    """Deixar em branco pareceria inofensivo: o candidato deixaria de receber o que a modalidade
    dele exige, e nada acusaria (FR-040)."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    sessao = client.session
    sessao["portal_identidade"] = MARIA.__dict__
    sessao.save()

    resposta = client.post(reverse("portal:inscricao", args=[inscricao.id]), {"modalidade": ""})

    assert "Escolha como você concorre" in resposta.content.decode()
    inscricao.refresh_from_db()
    assert inscricao.modality_id is None, "e nada foi guardado como se estivesse completo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_com_uma_modalidade_publicada_ela_e_assumida_sem_pergunta(
    client, settings, api_client, manager_headers, process_payload
):
    """Uma modalidade só não é escolha — e deixá-la em branco tiraria documentos da lista."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_TECNICO)

    assert str(inscricao.modality_id) == identificador(407, 0)
    sessao = client.session
    sessao["portal_identidade"] = MARIA.__dict__
    sessao.save()
    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert "<select" not in corpo, "não se pergunta o que não é escolha"
    assert "Ampla concorrência" in corpo, "mas se informa qual é"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_perfil_sem_modalidade_publicada_fica_sem_modalidade(
    api_client, manager_headers, process_payload
):
    def sem_modalidades(rascunho):
        rascunho["profiles"][1]["competitionModalities"] = []

    edital = _publicar(api_client, manager_headers, process_payload, ajustar=sem_modalidades)

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_TECNICO)

    assert inscricao.modality_id is None


# ---------------------------------------------------------------------------
# Recusa indistinguível, e abertura que não quebra sob concorrência
# ---------------------------------------------------------------------------


def _sem_csrf(corpo: bytes) -> bytes:
    return re.sub(rb'value="[A-Za-z0-9]{32,}"', b'value="TOKEN"', corpo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_inexistente_e_alheia_produzem_a_mesma_resposta(
    client, settings, api_client, manager_headers, process_payload
):
    """Mesmo status não basta: dois corpos diferentes continuam dizendo qual id existe."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)
    alheia = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    outro = IdentidadeDoCandidato(subject_de("98765432100"), "João", "987.654.321-00", "j@ex.br")
    sessao = client.session
    sessao["portal_identidade"] = outro.__dict__
    sessao.save()

    de_outro = client.get(reverse("portal:inscricao", args=[alheia.id]))
    inexistente = client.get(
        reverse("portal:inscricao", args=["00000000-0000-0000-0000-0000000009ff"])
    )

    assert de_outro.status_code == inexistente.status_code == 404
    # O token CSRF do `Sair` no cabeçalho é aleatório a cada render e não distingue uma resposta
    # da outra — compará-lo seria comparar ruído, não conteúdo.
    assert _sem_csrf(de_outro.content) == _sem_csrf(inexistente.content)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_abrir_apos_a_criacao_concorrente_devolve_a_mesma_inscricao(
    api_client, manager_headers, process_payload
):
    """FR-029 promete retomada, e não erro de servidor quando duas abas chegam juntas.

    A corrida real é difícil de encenar; o que se prova aqui é o caminho que ela percorre — a
    violação de unicidade é absorvida e a inscrição vencedora é devolvida, em vez de subir como
    erro 500.
    """
    edital = _publicar(api_client, manager_headers, process_payload)
    primeira = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    segunda = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert primeira.id == segunda.id
    assert Inscricao.objects.count() == 1


# ---------------------------------------------------------------------------
# Entrada grande demais é recusa legível, não erro de banco
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize(
    ("campo", "valor"),
    [("nome", "M" * 300), ("email", "a" * 250 + "@exemplo.br"), ("cpf", "1" * 40)],
)
def test_campo_maior_que_a_coluna_e_recusado_com_explicacao(client, settings, campo, valor):
    settings.PORTAL_IDENTIDADE_DEMO = True
    dados = {"nome": "Maria", "cpf": "123.456.789-09", "email": "m@ex.br"}
    dados[campo] = valor

    resposta = client.post(reverse("portal:identificar"), dados)

    assert resposta.status_code == 200, "recusa legível, e não erro de servidor"
    corpo = resposta.content.decode()
    assert any(frase in corpo for frase in ("máximo", "apenas com números", "11 dígitos"))
    assert 'class="recusa"' in corpo, "a recusa aparece junto do campo que a causou"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_telefone_que_nao_e_telefone_e_recusado_em_vez_de_estourar(
    client, settings, api_client, manager_headers, process_payload
):
    """Recusado, e não aparado.

    Aparar duzentos noves produzia um telefone de trinta dígitos gravado como se fosse válido — e
    um número errado custa a vaga: a comissão liga, não encontra ninguém e conclui que a pessoa
    desistiu. O que a pessoa digitou volta ao campo (SC-UX-007).
    """
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_TECNICO)
    sessao = client.session
    sessao["portal_identidade"] = MARIA.__dict__
    sessao.save()

    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao.id]), {"telefone": "9" * 200}
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Informe o telefone com DDD" in corpo
    assert "9" * 200 in corpo, "o que foi digitado volta ao campo"
    inscricao.refresh_from_db()
    assert inscricao.telefone == "", "nada de meio-telefone no banco"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_telefone_e_guardado_numa_forma_so(
    client, settings, api_client, manager_headers, process_payload
):
    """`27999990000`, `(27) 99999-0000` e `27 99999 0000` são o mesmo telefone."""
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_TECNICO)
    sessao = client.session
    sessao["portal_identidade"] = MARIA.__dict__
    sessao.save()

    client.post(reverse("portal:inscricao", args=[inscricao.id]), {"telefone": "27999990000"})

    inscricao.refresh_from_db()
    assert inscricao.telefone == "(27) 99999-0000"


# ---------------------------------------------------------------------------
# A página da seleção deixa de ser genérica quando fala de quem lê
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_selecao_e_privada_para_quem_ja_se_inscreveu(
    client, settings, api_client, manager_headers, process_payload
):
    settings.PORTAL_IDENTIDADE_DEMO = True
    edital = _publicar(api_client, manager_headers, process_payload)

    anonima = client.get(reverse("portal:selecao", args=[edital.id]))
    assert "no-store" not in anonima.headers.get("Cache-Control", "")

    abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    sessao = client.session
    sessao["portal_identidade"] = MARIA.__dict__
    sessao.save()

    identificada = client.get(reverse("portal:selecao", args=[edital.id]))

    assert "Continuar inscrição" in identificada.content.decode()
    assert "no-store" in identificada.headers["Cache-Control"]
