"""O envio dos documentos (US4 da 009, FR-041 a FR-053).

Três propriedades, e as três são o que separa esta feature de um formulário com anexo: o arquivo
persiste sozinho, ele fica ligado ao requisito que atende, e a recusa de um não custa os outros.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_PPP,
    identificar,
    imagem,
    pdf,
)
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)


def _enviar(client, inscricao, requisito, arquivo):
    return client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, requisito]), {"arquivo": arquivo}
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_persiste_na_hora_e_sem_salvar(client, inscricao_de_maria):
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    assert resposta.status_code == 200
    documento = DocumentoSubmetido.objects.get()
    assert str(documento.requirement_id) == DOCUMENTO_DE_TODOS
    assert documento.nome_original == "rg.pdf"
    assert documento.tamanho > 0
    assert len(documento.content_hash) == 64


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_nome_fisico_nao_e_o_nome_enviado(client, inscricao_de_maria, raiz_de_arquivos):
    """FR-052: nome de arquivo carrega dado pessoal, e viaja em log, backup e listagem."""
    identificar(client, MARIA)

    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("cpf-de-maria-silva.pdf"))

    documento = DocumentoSubmetido.objects.get()
    assert "maria" not in documento.arquivo.name.lower()
    assert documento.nome_original == "cpf-de-maria-silva.pdf"
    assert str(inscricao_de_maria.id) in documento.arquivo.name


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_contagem_conta_os_obrigatorios_que_faltam(client, inscricao_de_maria):
    identificar(client, MARIA)

    antes = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))
    assert "0 de 2" in antes.content.decode(), "ampla concorrência recebe dois pedidos"

    depois = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf())

    assert "1 de 2" in depois.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_de_um_envio_nao_derruba_os_outros(client, inscricao_de_maria):
    """FR-049: cada arquivo numa requisição própria, e é isso que preserva o que já valia."""
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    recusa = _enviar(client, inscricao_de_maria, DOCUMENTO_DO_PERFIL, imagem())

    corpo = recusa.content.decode()
    assert "imagem" in corpo and "Converta" in corpo
    assert "rg.pdf" in corpo, "o que já estava enviado continua lá"
    assert DocumentoSubmetido.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_substituir_sobrescreve_e_descarta_o_anterior(
    client, inscricao_de_maria, raiz_de_arquivos
):
    """FR-043 e FR-050: um arquivo por requisito, e fica claro qual passou a valer."""
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("primeiro.pdf"))
    caminho_antigo = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("segundo.pdf"))

    assert DocumentoSubmetido.objects.count() == 1
    documento = DocumentoSubmetido.objects.get()
    assert documento.nome_original == "segundo.pdf"
    assert "segundo.pdf" in resposta.content.decode()
    assert not caminho_antigo.exists(), "o arquivo antigo sai do disco junto"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_remover_apaga_o_registro_e_o_arquivo(client, inscricao_de_maria, raiz_de_arquivos):
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf())
    caminho = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    client.post(
        reverse("portal:remover-documento", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS])
    )

    assert DocumentoSubmetido.objects.count() == 0
    assert not caminho.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_modalidade_decide_quantos_documentos_sao_pedidos(client, inscricao_de_maria):
    """O cenário emblemático: ampla concorrência recebe dois pedidos; a reservada, três."""
    identificar(client, MARIA)
    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_PPP, "confirmar_descarte": "1"},
    )

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert "0 de 3" in corpo
    assert "Autodeclaração étnico-racial" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_e_auditado_sem_o_nome_do_arquivo(client, inscricao_de_maria):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("cpf-de-maria.pdf"))

    registro = RegistroAuditoria.objects.filter(operation="ANEXAR").get()

    assert registro.actor_subject == MARIA.subject
    assert DOCUMENTO_DE_TODOS in registro.reason
    assert "maria" not in registro.reason.lower()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_de_modalidade_nao_pedida_nao_e_aceito(client, inscricao_de_maria):
    """FR-044: o requisito da modalidade PPP não se aplica a quem concorre sem reserva."""
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DA_MODALIDADE, pdf())

    assert resposta.status_code == 404
    assert DocumentoSubmetido.objects.count() == 0
