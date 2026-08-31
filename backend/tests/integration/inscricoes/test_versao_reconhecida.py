"""Retificação durante o preenchimento (US5 da 009, FR-058, FR-059, FR-059a).

O envio não acontece em silêncio depois de o Edital mudar — e o aviso não se repete depois de a
pessoa confirmar. Sem a versão reconhecida, um dos dois defeitos é certo: ou o aviso nunca aparece,
ou aparece para sempre.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.publicacao import create_retification, publish_retification
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

DECLARACOES = {"veracidade": True, "ciencia": True}


def _completar(inscricao):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _retificar(api_client, edital, sufixo="ret", texto="Descrição retificada."):
    """Uma alteração normativa qualquer: o que importa é passar a vigorar outra versão.

    O texto muda a cada chamada porque a Retificação recusa alteração sem efeito — e é justamente
    isso que a segunda retificação deste arquivo precisa produzir: outra versão, não a mesma.
    """
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": "/description",
                "operation": "REPLACE",
                "newValue": texto,
                "expectedPreviousHash": "",
            }
        ],
        suffix=sufixo,
    )
    return publish_retification(api_client, retificacao, suffix=sufixo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_retificacao_impede_o_envio_silencioso(inscricao_de_maria, api_client, selecao):
    completa = _completar(inscricao_de_maria)
    _retificar(api_client, selecao)

    with pytest.raises(DomainError) as recusa:
        enviar_inscricao(
            identidade=MARIA,
            inscricao=completa,
            declaracoes=DECLARACOES,
            idempotency_key="envio-apos-retificacao",
        )

    assert recusa.value.code == "edital_updated"
    assert "Revise" in recusa.value.detail
    assert Inscricao.objects.get().status == Inscricao.Status.RASCUNHO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_os_dados_e_arquivos_sobrevivem_a_retificacao(inscricao_de_maria, api_client, selecao):
    """FR-059: preservar o que continua aplicável — a pessoa não recomeça do zero."""
    completa = _completar(inscricao_de_maria)
    _retificar(api_client, selecao)

    completa.refresh_from_db()
    assert completa.modality_id is not None
    assert DocumentoSubmetido.objects.filter(inscricao=completa).count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmada_a_alteracao_o_envio_acontece(client, inscricao_de_maria, api_client, selecao):
    completa = _completar(inscricao_de_maria)
    _retificar(api_client, selecao)
    identificar(client, MARIA)

    aviso = client.get(reverse("portal:revisao", args=[completa.id]))
    assert "O Edital foi atualizado" in aviso.content.decode()

    client.post(reverse("portal:revisao", args=[completa.id]), {"reconhecer_versao": "1"})
    enviada = client.post(
        reverse("portal:revisao", args=[completa.id]),
        {"veracidade": "on", "ciencia": "on"},
    )

    assert enviada.status_code == 302
    assert Inscricao.objects.get().status == Inscricao.Status.SUBMETIDA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_aviso_nao_se_repete_depois_de_confirmado(
    client, inscricao_de_maria, api_client, selecao
):
    """Confirmar vale até que **outra** versão passe a vigorar (FR-059a)."""
    completa = _completar(inscricao_de_maria)
    _retificar(api_client, selecao, sufixo="um")
    identificar(client, MARIA)

    client.post(reverse("portal:revisao", args=[completa.id]), {"reconhecer_versao": "1"})
    depois = client.get(reverse("portal:revisao", args=[completa.id]))

    assert "O Edital foi atualizado" not in depois.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_uma_segunda_retificacao_volta_a_avisar(client, inscricao_de_maria, api_client, selecao):
    completa = _completar(inscricao_de_maria)
    _retificar(api_client, selecao, sufixo="um")
    identificar(client, MARIA)
    client.post(reverse("portal:revisao", args=[completa.id]), {"reconhecer_versao": "1"})

    _retificar(api_client, selecao, sufixo="dois", texto="Descrição retificada outra vez.")
    de_novo = client.get(reverse("portal:revisao", args=[completa.id]))

    assert "O Edital foi atualizado" in de_novo.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_versao_aceita_e_a_vigente_no_ato(inscricao_de_maria, api_client, selecao):
    """FR-058: sob qual regra a pessoa se inscreveu — o que a Constituição exige responder."""
    completa = _completar(inscricao_de_maria)

    enviada = enviar_inscricao(
        identidade=MARIA,
        inscricao=completa,
        declaracoes=DECLARACOES,
        idempotency_key="envio-versao",
    )

    vigente = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")
    assert enviada.versao_aceita_id == vigente.pk
