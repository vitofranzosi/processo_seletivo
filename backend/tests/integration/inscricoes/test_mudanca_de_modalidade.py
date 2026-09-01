"""Mudar de modalidade descarta o que deixou de ser exigido — depois de dizer o quê (FR-031).

Os dois erros simétricos são descartar em silêncio e reaproveitar em silêncio. Enumerar antes de
descartar evita os dois, e é a única coisa que a spec pede aqui: nenhuma reconciliação, nenhum
mecanismo — uma lista e uma confirmação.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, MODALIDADE_PPP, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DA_MODALIDADE, DOCUMENTO_DE_TODOS


def _escolher_ppp(client, inscricao):
    return client.post(
        reverse("portal:inscricao", args=[inscricao.id]),
        {"modalidade": MODALIDADE_PPP, "confirmar_descarte": "1"},
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_mudanca_que_nao_descarta_nada_nao_pede_confirmacao(client, inscricao_de_maria):
    identificar(client, MARIA)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("rg.pdf")},
    )

    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]), {"modalidade": MODALIDADE_PPP}
    )

    assert resposta.status_code == 302, "avançar leva à revisão, sem parada de confirmação"
    assert reverse("portal:revisao", args=[inscricao_de_maria.id]) in resposta["Location"]
    assert DocumentoSubmetido.objects.count() == 1, "o documento de todos continua exigido"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_mudanca_que_descarta_enumera_antes(client, inscricao_de_maria):
    identificar(client, MARIA)
    _escolher_ppp(client, inscricao_de_maria)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao_de_maria.id, DOCUMENTO_DA_MODALIDADE]),
        {"arquivo": pdf("autodeclaracao.pdf")},
    )

    # De volta para a ampla concorrência — que este Edital declara, e por isso é escolhida como
    # qualquer outra: a autodeclaração deixa de ser exigida.
    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]), {"modalidade": MODALIDADE_AC}
    )

    corpo = resposta.content.decode()
    assert "serão removidos" in corpo
    assert "Autodeclaração étnico-racial" in corpo
    assert "autodeclaracao.pdf" in corpo
    assert DocumentoSubmetido.objects.count() == 1, "nada foi descartado ainda"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmada_a_mudanca_o_documento_e_descartado(
    client, inscricao_de_maria, raiz_de_arquivos
):
    identificar(client, MARIA)
    _escolher_ppp(client, inscricao_de_maria)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao_de_maria.id, DOCUMENTO_DA_MODALIDADE]),
        {"arquivo": pdf("autodeclaracao.pdf")},
    )
    caminho = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_AC, "confirmar_descarte": "1"},
    )

    inscricao_de_maria.refresh_from_db()
    assert str(inscricao_de_maria.modality_id) == MODALIDADE_AC
    assert DocumentoSubmetido.objects.count() == 0
    assert not caminho.exists(), "o arquivo sai do disco, e não só o registro"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_descarte_e_auditado(client, inscricao_de_maria):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    identificar(client, MARIA)
    _escolher_ppp(client, inscricao_de_maria)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao_de_maria.id, DOCUMENTO_DA_MODALIDADE]),
        {"arquivo": pdf("autodeclaracao.pdf")},
    )

    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_AC, "confirmar_descarte": "1"},
    )

    assert RegistroAuditoria.objects.filter(operation="REMOVER").exists()
