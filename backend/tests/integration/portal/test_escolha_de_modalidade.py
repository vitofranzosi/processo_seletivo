"""A escolha da modalidade é guardada quando é feita, e a lista de documentos acompanha.

A tela promete que "a escolha decide quais documentos serão pedidos a você" — e a promessa não valia
no instante em que a escolha era feita. Escolher a modalidade reservada não mudava nada: a lista
continuava com dois documentos e o aviso verde continuava dizendo "todos os obrigatórios foram
enviados". O terceiro só aparecia na revisão, quando a pessoa já se considerava pronta. E a escolha
não era gravada até ali: quem saía e voltava reencontrava o campo em branco.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MODALIDADE_PPP = "00000000-0000-0000-0000-000000000404"


def guardar(client, inscricao, modalidade):
    """O que o campo faz ao mudar: submete o formulário que já existe, com `acao=guardar`."""
    return client.post(
        reverse("portal:inscricao", args=[inscricao.id]),
        {"modalidade": modalidade, "telefone": "", "acao": "guardar"},
        follow=True,
    )


def test_escolher_guarda_na_hora_e_traz_o_documento_da_modalidade(client, inscricao_de_maria):
    identificar(client, MARIA)

    corpo = guardar(client, inscricao_de_maria, MODALIDADE_PPP).content.decode()

    assert "Autodeclaração étnico-racial" in corpo, "o terceiro documento aparece agora"
    assert "Faltam <strong>3</strong>\n  de 3 documento" in corpo.replace("\r\n", "\n")
    inscricao_de_maria.refresh_from_db()
    assert str(inscricao_de_maria.modality_id) == MODALIDADE_PPP


def test_a_escolha_sobrevive_a_sair_e_voltar(client, inscricao_de_maria):
    identificar(client, MARIA)
    guardar(client, inscricao_de_maria, MODALIDADE_PPP)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert f'value="{MODALIDADE_PPP}" selected' in corpo


def test_o_aviso_verde_deixa_de_mentir(client, inscricao_de_maria):
    """Dois documentos enviados e a modalidade reservada escolhida: não está tudo enviado."""
    identificar(client, MARIA)
    for requisito in (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL):
        anexar_documento(
            identidade=MARIA,
            inscricao=inscricao_de_maria,
            requirement_id=requisito,
            arquivo=pdf(),
        )

    corpo = guardar(client, inscricao_de_maria, MODALIDADE_PPP).content.decode()

    assert "Falta <strong>1</strong>" in corpo
    assert "Todos os" not in corpo, "o aviso verde dizia que estava tudo enviado — e não estava"


def test_guardar_volta_para_a_inscricao_e_avancar_vai_para_a_revisao(client, inscricao_de_maria):
    identificar(client, MARIA)

    guardou = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_AC, "telefone": "", "acao": "guardar"},
    )
    avancou = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_AC, "telefone": ""},
    )

    assert guardou["Location"] == reverse("portal:inscricao", args=[inscricao_de_maria.id])
    assert avancou["Location"] == reverse("portal:revisao", args=[inscricao_de_maria.id])


def test_a_confirmacao_de_descarte_devolve_para_onde_a_pessoa_estava(client, inscricao_de_maria):
    """Trocar de modalidade descartando documento continua perguntando antes — e, confirmado, a
    pessoa volta para a tela em que estava, e não é empurrada para a revisão."""
    identificar(client, MARIA)
    guardar(client, inscricao_de_maria, MODALIDADE_PPP)
    anexar_documento(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        requirement_id=DOCUMENTO_DA_MODALIDADE,
        arquivo=pdf("autodeclaracao.pdf"),
    )

    pergunta = guardar(client, inscricao_de_maria, MODALIDADE_AC)
    assert "descarta documentos" in pergunta.content.decode()
    assert 'name="acao" value="guardar"' in pergunta.content.decode()

    confirmou = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {
            "modalidade": MODALIDADE_AC,
            "telefone": "",
            "confirmar_descarte": "1",
            "acao": "guardar",
        },
    )

    assert confirmou["Location"] == reverse("portal:inscricao", args=[inscricao_de_maria.id])


def test_sem_javascript_nada_muda(client, inscricao_de_maria):
    """O caminho antigo continua inteiro: escolher e clicar em "Revisar inscrição"."""
    identificar(client, MARIA)

    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_PPP, "telefone": ""},
    )

    inscricao_de_maria.refresh_from_db()
    assert str(inscricao_de_maria.modality_id) == MODALIDADE_PPP
    assert resposta["Location"] == reverse("portal:revisao", args=[inscricao_de_maria.id])
