"""O atalho do indeferimento só onde há pendência (152, história 1, SC-1900, SC-1910).

**O atalho segue o que a pessoa deixou de cumprir, e não o que impede o aceite** (D-001). Antes, a
tela o oferecia pela lista do aceite, que inclui o documento ainda no prazo e o enviado à espera da
comissão: Alice, sem nada enviado e com 30 dias de prazo, via "Indeferir pelas pendências de
documento" com um fundamento que dizia que ela não atendeu (achado 04 do estudo de 11/11/2026).

Com o prazo vencido e nada apresentado, o cartão aponta o não atendimento (FR-5809, D-011): quem
não respondeu não atendeu à convocação, e o indeferimento pelas pendências é de quem respondeu com
falta.
"""

import re
from datetime import timedelta
from html import unescape
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    apresentar,
    comunicar,
    conferir,
    convocar_primeira,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

ATALHO = "Indeferir pelas pendências de documento"
INICIO = "Documentação exigida na convocação não atendida — "
NADA_APRESENTADO = "sem nenhum documento apresentado"

#: Um facultativo pedido na convocação, para o caso em que só ele chega.
FACULTATIVO = cenarios.identificador(1159, 0)


@pytest.fixture
def montar(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    """Monta o cenário com os documentos do caso e devolve `(cenario, convocar)`."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True

    def _montar(documentos=None, documentos_da_inscricao=None, prefixo="atalho-152"):
        cenario = cenarios.montar(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            documentos=documentos or cenarios.documentos_do_aluno(),
            documentos_da_inscricao=documentos_da_inscricao,
            prefixo=prefixo,
        )
        return cenario

    return _montar


def _convocar(cenario, gestor, *, vencimento):
    edital, _, _ = cenario
    pessoa, convocacao = convocar_primeira(cenario, gestor, vencimento=vencimento)
    comunicar(edital, gestor, convocacao)
    return edital, pessoa, convocacao


def _cartao(client, edital, *, depois=None):
    """O cartão da única chamada do recorte, como texto, lido agora ou `depois` do vencimento."""
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:convocacao", args=[edital.id, MARCO])
    if depois is None:
        resposta = client.get(url)
    else:
        with mock.patch("django.utils.timezone.now", return_value=timezone.now() + depois):
            resposta = client.get(url)
    assert resposta.status_code == 200
    return unescape(resposta.content.decode())


def _fundamento_do_atalho(corpo):
    """O texto pré-redigido do textarea do atalho."""
    achado = re.search(r'id="fundamento-indeferimento-\d+"[^>]*>([^<]*)</textarea>', corpo)
    assert achado, "o atalho não tem o fundamento pré-redigido"
    return achado.group(1)


def _passo(corpo):
    achado = re.search(r'<p class="passo-da-chamada">(.*?)</p>', corpo, re.S)
    assert achado
    return re.sub(r"<[^>]+>", "", achado.group(1))


def test_nada_enviado_com_o_prazo_em_curso_nao_oferece_o_atalho(montar, gestor, client):
    """Cenário 1 e SC-1900: Alice — nada enviado, prazo em curso."""
    edital, _, _ = _convocar(montar(), gestor, vencimento=timezone.now() + timedelta(days=30))

    corpo = _cartao(client, edital)

    assert ATALHO not in corpo
    assert "Registrar desfecho" in corpo


def test_o_fundamento_cita_o_pendente_com_o_motivo_e_nao_o_conforme(montar, gestor, client):
    """Cenário 2: o pendente com o motivo registrado; o conforme não aparece."""
    edital, pessoa, convocacao = _convocar(
        montar(), gestor, vencimento=timezone.now() + timedelta(days=30)
    )
    apresentar(pessoa, convocacao, CERTIDAO)
    apresentar(pessoa, convocacao, HISTORICO)
    conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="c1")
    conferir(gestor, convocacao, HISTORICO, "PENDENTE", chave="c2", motivo="Falta a página 2.")

    corpo = _cartao(client, edital)

    assert ATALHO in corpo
    assert _fundamento_do_atalho(corpo) == (
        INICIO + "Histórico escolar do ensino médio: Falta a página 2."
    )


def test_o_que_aguarda_conferencia_e_nomeado_e_nao_entra_no_fundamento(montar, gestor, client):
    """Cenário 3 e FR-5802: o recebido sem conferência fica fora do fundamento, e o formulário diz
    que o indeferimento o deixa sem conferir."""
    edital, pessoa, convocacao = _convocar(
        montar(), gestor, vencimento=timezone.now() + timedelta(days=30)
    )
    apresentar(pessoa, convocacao, CERTIDAO)
    apresentar(pessoa, convocacao, HISTORICO)
    conferir(gestor, convocacao, CERTIDAO, "PENDENTE", chave="c1", motivo="Ilegível.")

    corpo = _cartao(client, edital)

    assert _fundamento_do_atalho(corpo) == (
        INICIO + "Certidão de nascimento ou casamento: Ilegível."
    )
    aviso = (
        "Aguarda conferência: Histórico escolar do ensino médio. O indeferimento o deixa sem "
        "conferir."
    )
    # Nos dois formulários: o atalho e o desfecho geral.
    assert corpo.count(aviso) == 2


def test_vencido_com_algo_apresentado_o_atalho_cita_o_que_nao_chegou(montar, gestor, client):
    """Cenário 4 e SC-1910: o obrigatório nunca apresentado, depois do vencimento."""
    edital, pessoa, convocacao = _convocar(
        montar(), gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    apresentar(pessoa, convocacao, CERTIDAO)
    apresentar(pessoa, convocacao, HISTORICO)
    apresentar(pessoa, convocacao, CERTIFICADO_DO_MEDIO)
    conferir(gestor, convocacao, CERTIDAO, "CONFORME", chave="c1")
    conferir(gestor, convocacao, HISTORICO, "CONFORME", chave="c2")
    conferir(gestor, convocacao, CERTIFICADO_DO_MEDIO, "CONFORME", chave="c3")

    corpo = _cartao(client, edital, depois=timedelta(days=2))

    assert ATALHO in corpo
    assert _fundamento_do_atalho(corpo) == (
        INICIO + "Comprovante de residência: não apresentado no prazo."
    )
    assert NADA_APRESENTADO not in corpo


def test_so_enviados_sem_conferencia_nao_oferecem_o_atalho(montar, gestor, client):
    """Cenário 5: o que espera a comissão não é falta da pessoa; o passo continua conferir."""
    edital, pessoa, convocacao = _convocar(
        montar(), gestor, vencimento=timezone.now() + timedelta(days=30)
    )
    for requisito in (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA):
        apresentar(pessoa, convocacao, requisito)

    corpo = _cartao(client, edital)

    assert ATALHO not in corpo
    assert _passo(corpo).strip().startswith("Próximo passo Conferir 4 documentos recebidos.")


def test_vencido_sem_nada_apresentado_aponta_o_nao_atendimento(montar, gestor, client):
    """Cenário 6, FR-5809, UX-535 e SC-1910: o passo diz o vencimento e aponta o não atendimento,
    e o indeferimento continua no desfecho geral."""
    edital, _, convocacao = _convocar(
        montar(), gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )

    corpo = _cartao(client, edital, depois=timedelta(days=2))

    assert ATALHO not in corpo
    passo = _passo(corpo)
    assert NADA_APRESENTADO in passo
    assert timezone.localtime(convocacao.vencimento).strftime("%d/%m/%Y %H:%M") in passo
    assert "não atendimento à convocação" in passo
    assert "O formulário do desfecho está aberto abaixo." in passo
    assert "Registrar desfecho" in corpo
    assert '<option value="INDEFERIMENTO">' in corpo


def test_so_um_facultativo_apresentado_conta_como_resposta(montar, gestor, client):
    """Caso-limite: a pessoa respondeu, e o que falta são os obrigatórios (FR-5800)."""
    documentos = [
        cenarios._documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        cenarios._documento(
            CERTIDAO, "certidao", "Certidão de nascimento ou casamento", 2, momento="AT_CALL"
        ),
        cenarios._documento(
            FACULTATIVO,
            "carta",
            "Carta de apresentação",
            3,
            momento="AT_CALL",
            obrigatorio=False,
        ),
    ]
    edital, pessoa, convocacao = _convocar(
        montar(documentos=documentos, prefixo="facultativo-152"),
        gestor,
        vencimento=timezone.now() + timedelta(minutes=1),
    )
    apresentar(pessoa, convocacao, FACULTATIVO)

    corpo = _cartao(client, edital, depois=timedelta(days=2))

    assert ATALHO in corpo
    # Só o obrigatório: o facultativo não decide desfecho (FR-3592 da `115`).
    assert _fundamento_do_atalho(corpo) == (
        INICIO + "Certidão de nascimento ou casamento: não apresentado no prazo."
    )
    assert NADA_APRESENTADO not in _passo(corpo)


def test_o_aproveitado_da_inscricao_nao_conta_como_apresentado(montar, gestor, client):
    """D-011: o aproveitado não é resposta à convocação — o sistema o gravou ao convocar."""
    edital, _, convocacao = _convocar(
        montar(
            documentos=cenarios.documentos_do_certificado(),
            documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
            prefixo="aproveitado-152",
        ),
        gestor,
        vencimento=timezone.now() + timedelta(minutes=1),
    )
    leitura = cenarios.servico.leitura_da_chamada(convocacao)
    assert leitura.pedidos and all(lido.aproveitada for lido in leitura.pedidos)

    corpo = _cartao(client, edital, depois=timedelta(days=2))

    assert ATALHO not in corpo
    assert NADA_APRESENTADO in _passo(corpo)
