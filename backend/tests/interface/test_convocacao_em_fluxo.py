"""A tela da convocação como fluxo: a prévia antes do botão, o gesto, e o que deixou de pedir (050).

**O que só a tela prova é o que aparece antes do ato** (`UX-100` a `UX-104`): quem será alcançado,
com que espécie, de onde veio cada valor, e que abrir a página não pratica nada.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao, DesfechoDaConvocacao
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

VENCIMENTO = (timezone.localtime() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")


@pytest.fixture
def cenario_da_tela(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas, dois titulares e uma suplente — o recorte do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="interface-050",
        geral=2,
        cut=regra(surplusCount=1),
    )


def abrir(client, edital):
    return client.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content.decode()


def previa(edital):
    return fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def postar_titulares(client, edital, assinatura, **extra):
    dados = {"alcance": assinatura, "chave": "tela-titulares", "vencimento": VENCIMENTO, **extra}
    return client.post(reverse("interface:convocar-titulares", args=[edital.id, MARCO]), dados)


def test_a_previa_declara_o_alcance_antes_do_botao_e_nao_pratica_nada(
    client, seletor_ligado, cenario_da_tela
):
    """`UX-100`, `UX-101`, `UX-102`: a contagem, a espécie com a origem, e quem fica de fora."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)

    assert "2 pessoas serão convocadas" in pagina
    assert "Convocar as 2" in pagina
    assert "da posição na fila" in pagina
    assert "é suplente. O gesto convoca só titulares" in pagina
    assert "derivado do Edital e dos atos deste recorte" in pagina
    assert Convocacao.objects.count() == 0


def test_o_gesto_convoca_e_conta_o_que_a_comunicacao_fez(client, seletor_ligado, cenario_da_tela):
    """`UX-103`: quantas nasceram e quantas comunicações saíram — e nunca "recebida"."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    resposta = postar_titulares(client, edital, previa(edital)["assinatura"])
    pagina = client.get(resposta["Location"]).content.decode()

    assert Convocacao.objects.count() == 2
    assert len(mail.outbox) == 2
    assert "2 convocações praticadas num ato só" in pagina
    assert "2 comunicações enviadas" in pagina
    for proibida in ("recebida em", "recebido em", "entregue em"):
        assert proibida not in pagina.lower()


def test_a_recusa_por_alcance_mudado_mostra_o_alcance_de_agora(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """`UX-104`: a recusa volta à tela, e a prévia recalculada está lá."""
    edital, _, _ = cenario_da_tela
    assinatura = previa(edital)["assinatura"]
    convocar(edital, gestor, previa(edital)["pessoas"][0]["id"], idempotency_key="no-meio")
    identificar(client, "carlos", ["gestor"])

    resposta = postar_titulares(client, edital, assinatura)
    pagina = client.get(resposta["Location"]).content.decode()

    assert "mudou desde que a tela foi aberta" in pagina
    assert "1 pessoa será convocada" in pagina
    assert Convocacao.objects.count() == 1


def test_a_chamada_individual_nao_pergunta_a_especie_e_ja_comunica(
    client, seletor_ligado, cenario_da_tela
):
    """`FR-867`, `FR-870`, `FR-871`: sem seletor de espécie, fundamento por extenso, e o envio."""
    edital, _, _ = cenario_da_tela
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)
    assert 'name="especie"' not in pagina.split('id="regularizar"')[0]
    assert "Fundamento, para vaga inicial" in pagina

    pessoa = previa(edital)["pessoas"][0]["id"]
    client.post(
        reverse("interface:convocar", args=[edital.id, MARCO]),
        {"inscricao": pessoa, "vencimento": VENCIMENTO, "chave": "individual"},
    )

    convocacao = Convocacao.objects.get()
    assert convocacao.especie == nomes.VAGA_INICIAL
    assert convocacao.fundamento.startswith("Convocação para vaga inicial")
    assert len(mail.outbox) == 1


def test_o_gesto_dos_vencidos_aparece_e_registra_um_por_pessoa(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """US3 na tela: a lista das vencidas, o botão com o número, e o resultado com a apuração."""
    edital, _, _ = cenario_da_tela
    fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=previa(edital)["assinatura"],
        idempotency_key="vencidos-tela",
        vencimento=timezone.now() + timedelta(hours=1),
    )
    identificar(client, "carlos", ["gestor"])
    assert "Não atendimento das convocações vencidas" not in abrir(client, edital)

    adiante = timezone.now() + timedelta(hours=2)
    with mock.patch("django.utils.timezone.now", return_value=adiante):
        pagina = abrir(client, edital)
        assert "Registrar o não atendimento das 2" in pagina
        assinatura = fluxo.previa_dos_vencidos(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
            "assinatura"
        ]
        resposta = client.post(
            reverse("interface:nao-atendimento-dos-vencidos", args=[edital.id, MARCO]),
            {"alcance": assinatura, "chave": "vencidos-post"},
        )
        pagina = client.get(resposta["Location"]).content.decode()

    assert DesfechoDaConvocacao.objects.filter(especie=nomes.NAO_ATENDIMENTO).count() == 2
    assert "2 desfechos de não atendimento registrados" in pagina
    assert "A apuração seguinte deste recorte foi emitida no mesmo ato" in pagina


def test_as_comunicacoes_que_falharam_sao_reemitidas_num_gesto(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """`FR-874`: a falha fica na lista das pendentes, e um botão as emite de novo."""
    edital, _, _ = cenario_da_tela
    with mock.patch(
        "processo_seletivo.convocacao.application.comunicar.send_mail",
        side_effect=ConnectionError("smtp"),
    ):
        fluxo.convocar_titulares(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            alcance_confirmado=previa(edital)["assinatura"],
            idempotency_key="falhou",
        )
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)
    assert "Emitir 2 comunicações" in pagina
    assinatura = fluxo.previa_das_pendentes(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "assinatura"
    ]
    resposta = client.post(
        reverse("interface:emitir-pendentes", args=[edital.id, MARCO]),
        {"alcance": assinatura, "chave": "reemitir"},
    )
    pagina = client.get(resposta["Location"]).content.decode()

    assert len(mail.outbox) == 2
    assert "2 comunicações enviadas" in pagina
    assert "Comunicações que ainda não saíram" not in pagina


def test_o_suplente_so_e_chamado_pela_chamada_individual_com_especie_derivada(
    client, seletor_ligado, cenario_da_tela, gestor
):
    """US5: a vaga que vagou é chamada um a um, com a espécie que a posição determina."""
    edital, _, _ = cenario_da_tela
    fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=previa(edital)["assinatura"],
        idempotency_key="suplente",
    )
    primeira = Convocacao.objects.order_by("criado_em").first()
    from processo_seletivo.convocacao.application.desfechar import desfechar

    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=primeira.id,
        especie=nomes.DESISTENCIA_EXPRESSA,
        fundamento="Desistiu por escrito.",
        idempotency_key="suplente-desiste",
        correlation_id="teste",
    )
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital)

    assert "Nenhum titular ainda não chamado neste recorte" in pagina
    assert "para vaga que vagou (próxima da fila)" in pagina
