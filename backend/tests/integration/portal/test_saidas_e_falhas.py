"""Quando o sistema não resolve, ele diz para onde ir — e quando falha, ele diz que falhou.

Duas telas mandavam "procure o atendimento institucional" sem dizer qual: nem e-mail, nem telefone,
nem link. São os dois pontos em que a pessoa já está travada — o CPF congelado depois da primeira
inscrição enviada, e a participação anterior que ela não conseguiu confirmar.

E o envio de documento falhava sem sinal nenhum: o htmx só troca conteúdo em resposta
bem-sucedida — o que está certo —, e por isso uma resposta de erro deixava a tela exatamente como
estava. O nome do arquivo continuava ali, a contagem continuava igual, e a pessoa acreditava ter
anexado.
"""

import pathlib

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

ESTATICOS = pathlib.Path(__file__).resolve().parents[3] / "processo_seletivo/portal/static/portal"


@pytest.fixture
def com_inscricao_enviada(client, inscricao_de_maria):
    from processo_seletivo.inscricoes.application.rascunho import gravar_dados

    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito in (DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-saidas",
    )


def test_o_cpf_congelado_diz_com_quem_falar(client, settings, com_inscricao_enviada):
    settings.PORTAL_ATENDIMENTO = "selecao@cefor.ifes.edu.br"
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:meus-dados")).content.decode()

    assert "Para corrigi-lo, fale com" in corpo
    assert 'href="mailto:selecao@cefor.ifes.edu.br"' in corpo


def test_o_convite_de_reconciliacao_diz_com_quem_falar(
    client, settings, desafio_consumido, candidatos_registrados
):
    from processo_seletivo.identidade.application import associacao

    settings.PORTAL_ATENDIMENTO = "https://cefor.ifes.edu.br/atendimento"
    associacao.abrir_reconciliacao(desafio_consumido, [candidatos_registrados[0]])
    sessao = client.session
    sessao["portal_acesso_desafio"] = str(desafio_consumido.pk)
    sessao["portal_acesso_email"] = desafio_consumido.email_canonico
    sessao.save()

    corpo = client.get(reverse("portal:acesso-reconciliar")).content.decode()

    assert 'href="https://cefor.ifes.edu.br/atendimento"' in corpo
    assert "procedimento institucional de atendimento" not in corpo


def test_sem_atendimento_declarado_a_frase_generica_e_o_que_sobra(
    client, settings, com_inscricao_enviada
):
    """Em produção a variável é obrigatória; em desenvolvimento ela pode faltar, e a tela não
    quebra por isso — apenas volta a dizer o que dizia antes."""
    settings.PORTAL_ATENDIMENTO = ""
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:meus-dados")).content.decode()

    assert "o atendimento institucional" in corpo
    assert "mailto:" not in corpo


def test_a_falha_do_envio_de_documento_tem_tratador(client, inscricao_de_maria):
    """O htmx não troca nada em resposta de erro — sem tratador, a falha é invisível.

    Verificado no arquivo e na página: o script precisa existir **e** ser carregado por quem envia
    documento, que é onde a falha silenciosa acontecia.
    """
    fonte = (ESTATICOS / "envio.js").read_text(encoding="utf-8")

    assert "htmx:responseError" in fonte
    assert "htmx:sendError" in fonte, "queda de rede não emite responseError"
    assert "recusa-do-envio" in fonte

    identificar(client, MARIA)
    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert "portal/envio.js" in corpo


def test_a_mensagem_da_falha_diz_que_nada_se_perdeu(client):
    """Quem vê "não foi possível enviar" precisa saber que o resto continua lá — senão recomeça."""
    fonte = (ESTATICOS / "envio.js").read_text(encoding="utf-8")

    assert fonte.count("continua guardado") == 3, "as três falhas dizem o mesmo"
    assert "o seu acesso expirou" in fonte, "404 tem causa própria, e ela tem conserto"
