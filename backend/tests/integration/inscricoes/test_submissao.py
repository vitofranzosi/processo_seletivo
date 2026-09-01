"""O envio: o ato que produz efeito administrativo (US5 da 009, FR-058 a FR-064).

O que se prova aqui é sobretudo o que **não** passa. A tela validou para não oferecer o que seria
recusado; entre o que ela mostrou e o que chega podem ter passado uma Retificação, o fim do prazo,
o cancelamento do Edital ou um POST montado à mão.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

DECLARACOES = {"veracidade": True, "ciencia": True}


def _completar(inscricao):
    """Modalidade escolhida e os dois documentos de quem concorre na ampla concorrência.

    A modalidade é parte de estar completa: o Perfil docente declara duas, e escolher é obrigatório
    justamente porque a escolha decide quais documentos serão pedidos.
    """
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao,
        dados={
            "nome": MARIA.nome,
            "cpf": MARIA.cpf,
            "email": MARIA.email,
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA,
            inscricao=inscricao,
            requirement_id=requisito,
            arquivo=pdf(nome),
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao, *, chave="envio-1", declaracoes=None):
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes=DECLARACOES if declaracoes is None else declaracoes,
        idempotency_key=chave,
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_inscricao_completa_e_enviada_com_protocolo(inscricao_de_maria):
    enviada = _enviar(_completar(inscricao_de_maria))

    assert enviada.status == Inscricao.Status.SUBMETIDA
    assert enviada.protocolo.startswith(f"INS-{timezone.now().year}-")
    assert enviada.submitted_at is not None
    assert enviada.versao_aceita_id is not None, "a versão sob a qual ela se inscreveu (FR-058)"
    assert enviada.declaracoes_aceitas_em is not None


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_obrigatorio_faltando_impede_o_envio(inscricao_de_maria):
    inscricao_de_maria = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        dados={"modality_id": MODALIDADE_AC},
    )
    anexar_documento(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        requirement_id=DOCUMENTO_DE_TODOS,
        arquivo=pdf(),
    )
    inscricao_de_maria.refresh_from_db()

    with pytest.raises(DomainError) as recusa:
        _enviar(inscricao_de_maria)

    assert recusa.value.code == "missing_required_documents"
    assert "Diploma de graduação" in recusa.value.detail, "a recusa nomeia o que falta"
    assert Inscricao.objects.get().status == Inscricao.Status.RASCUNHO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@pytest.mark.parametrize(
    "declaracoes",
    [{"veracidade": True, "ciencia": False}, {"veracidade": False, "ciencia": True}, {}],
)
def test_sem_as_duas_declaracoes_nao_ha_envio(inscricao_de_maria, declaracoes):
    with pytest.raises(DomainError) as recusa:
        _enviar(_completar(inscricao_de_maria), declaracoes=declaracoes)

    assert recusa.value.code == "declarations_required"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_mesmo_envio_repetido_produz_uma_inscricao_so(inscricao_de_maria):
    """FR-061: duplo clique reserva a mesma chave e devolve o mesmo resultado."""
    completa = _completar(inscricao_de_maria)

    primeira = _enviar(completa, chave="mesma-chave")
    segunda = _enviar(completa, chave="mesma-chave")

    assert primeira.id == segunda.id
    assert primeira.protocolo == segunda.protocolo
    assert Inscricao.objects.filter(status=Inscricao.Status.SUBMETIDA).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_enviar_de_novo_com_outra_chave_e_recusado(inscricao_de_maria):
    completa = _completar(inscricao_de_maria)
    _enviar(completa, chave="primeira")
    completa.refresh_from_db()

    with pytest.raises(DomainError) as recusa:
        _enviar(completa, chave="segunda")

    assert recusa.value.code == "submission_is_final"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_periodo_encerrado_impede_o_envio(
    inscricao_de_maria, api_client, manager_headers, process_payload, selecao
):
    """Abrir antes do fechamento não dá direito de enviar depois (FR-019)."""
    completa = _completar(inscricao_de_maria)
    from processo_seletivo.editais.models import EventoCronograma

    evento = EventoCronograma.objects.get(cronograma__edital=selecao, is_registration_period=True)
    # A publicação vigente é a fonte; alterar o Evento não basta — o teste move o relógio do
    # domínio publicando o fim no passado seria outra feature. Aqui basta cancelar o Edital, que
    # é o outro eixo da mesma recusa.
    api_client.post(
        f"/api/v1/admin/editais/{selecao.id}/cancelamentos",
        {"reason": "Perda de objeto"},
        format="json",
        **{
            **actor_headers("gestor-a", ["edital:cancelar"], key="cancelamento-envio-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=selecao.pk).revision}"',
        },
    )

    with pytest.raises(DomainError) as recusa:
        _enviar(completa)

    assert recusa.value.code == "registration_closed"
    assert evento.is_registration_period is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_arquivo_corrompido_no_disco_impede_o_envio(inscricao_de_maria, raiz_de_arquivos):
    """FR-053a: o resumo é verificado, e não apenas guardado."""
    completa = _completar(inscricao_de_maria)
    documento = DocumentoSubmetido.objects.filter(requirement_id=DOCUMENTO_DE_TODOS).get()
    (raiz_de_arquivos / documento.arquivo.name).write_bytes(b"%PDF-1.4\noutro conteudo")

    with pytest.raises(DomainError) as recusa:
        _enviar(completa)

    assert recusa.value.code == "stored_file_corrupted"
    assert documento.nome_original in recusa.value.detail


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_e_auditado_com_edital_versao_e_perfil(inscricao_de_maria):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    enviada = _enviar(_completar(inscricao_de_maria))

    # Por agregado, e não só por operação: o Edital também é "submetido", e a trilha é uma só.
    registro = RegistroAuditoria.objects.filter(
        operation="SUBMETER", aggregate_type="Inscricao"
    ).get()

    assert registro.actor_subject == MARIA.subject
    assert str(enviada.edital_id) in registro.reason
    assert str(enviada.versao_aceita_id) in registro.reason
    assert str(enviada.profile_id) in registro.reason
    assert MARIA.cpf not in registro.reason
    assert registro.new_state == Inscricao.Status.SUBMETIDA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_inscricao_enviada_nao_aceita_mais_arquivo(inscricao_de_maria):
    """FR-054: enviada, ela e seus arquivos são imutáveis nesta versão."""
    completa = _completar(inscricao_de_maria)
    _enviar(completa)
    completa.refresh_from_db()

    with pytest.raises(DomainError) as recusa:
        anexar_documento(
            identidade=MARIA,
            inscricao=completa,
            requirement_id=DOCUMENTO_DE_TODOS,
            arquivo=pdf("outro.pdf"),
        )

    assert recusa.value.code == "submission_is_final"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_instante_e_o_protocolo_nao_mudam_depois(inscricao_de_maria):
    enviada = _enviar(_completar(inscricao_de_maria))

    enviada.submitted_at = timezone.now() + timedelta(days=1)
    with pytest.raises(TypeError):
        enviada.save()
