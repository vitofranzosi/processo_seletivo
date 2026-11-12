"""Convocar e publicar num gesto só (159): uma confirmação, as três consequências.

O que se prende aqui é a fronteira entre o que a confirmação pratica junto e o que pratica depois:
no GPS, convocar e publicar são uma transação — a recusa não deixa convocação nenhuma —; por
mensagem, a relação sai depois dos envios, só com as comunicadas, e a falha dela não desfaz nada.
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    Convocacao,
    ConvocacaoPublicada,
    PublicacaoDeConvocados,
)
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

AUTORIDADE = str(AUTORIDADE_DO_RESULTADO)
#: Fixo, para a repetição com a mesma chave levar o mesmo conteúdo.
VENCIMENTO = (timezone.now() + timedelta(days=5)).replace(microsecond=0)
VEICULO = "item 7.2 do Edital"


@pytest.fixture(autouse=True)
def caixa_de_saida(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def fixtures(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return gestor, api_client, manager_headers, process_payload


def dois_titulares(fixtures, *, forma, prefixo):
    """O 77/2026: duas vagas, dois titulares que o gesto alcança juntos."""
    gestor, api_client, manager_headers, process_payload = fixtures
    edital, _, _ = montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        forma=forma,
        geral=2,
        cut=regra(surplusCount=1),
    )
    return edital


def titulares(edital, gestor, *, chave, assinatura=None, **kwargs):
    """O gesto pela confirmação; a repetição leva a assinatura do formulário, como a tela leva."""
    assinatura = (
        assinatura
        or fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
            "assinatura"
        ]
    )
    return fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=assinatura,
        idempotency_key=chave,
        vencimento=VENCIMENTO,
        **kwargs,
    )


def contagem():
    return (
        Convocacao.objects.count(),
        ComunicacaoEmitida.objects.count(),
        PublicacaoDeConvocados.objects.count(),
    )


# --- Por mensagem individual (FR-6805 a FR-6807) -------------------------------------------------


def test_por_mensagem_uma_confirmacao_convoca_envia_e_publica(fixtures, gestor, caixa_de_saida):
    """SC-2251: a relação na página pública sem abrir a página de publicação."""
    edital = dois_titulares(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="g159-msg")

    resultado = titulares(edital, gestor, chave="g159-msg", autoridade=AUTORIDADE)

    assert resultado["enviadas"] == 2 and len(caixa_de_saida) == 2
    ato = PublicacaoDeConvocados.objects.get(id=resultado["publicacao"]["id"])
    vinculos = ConvocacaoPublicada.objects.filter(publicacao=ato)
    assert {v.efeito for v in vinculos} == {"DIVULGA"} and vinculos.count() == 2
    assert ato.declaracao_do_veiculo == "", "a relação informativa não declara veículo"


def test_a_mensagem_que_falhou_fica_fora_e_o_reenvio_publica_a_que_saiu(fixtures, gestor):
    """SC-2252, FR-6806, FR-6807."""
    from processo_seletivo.convocacao.application import comunicar

    edital = dois_titulares(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="g159-falha")
    original = comunicar.destinatario_de
    primeira = {}

    def sem_endereco_para_uma(convocacao):
        primeira.setdefault("id", convocacao.inscricao_id)
        return "" if convocacao.inscricao_id == primeira["id"] else original(convocacao)

    with mock.patch.object(comunicar, "destinatario_de", sem_endereco_para_uma):
        resultado = titulares(edital, gestor, chave="g159-falha", autoridade=AUTORIDADE)

    assert (resultado["enviadas"], resultado["falhas"]) == (1, 1)
    [vinculo] = ConvocacaoPublicada.objects.filter(publicacao_id=resultado["publicacao"]["id"])
    falhou = Convocacao.objects.get(inscricao_id=primeira["id"])
    assert vinculo.convocacao_id != falhou.id, "a que falhou não está na relação"

    previa = fluxo.previa_das_pendentes(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    reenvio = fluxo.emitir_pendentes(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=previa["assinatura"],
        idempotency_key="g159-falha-reenvio",
        autoridade=AUTORIDADE,
    )

    assert reenvio["enviadas"] == 1
    assert ConvocacaoPublicada.objects.get(convocacao=falhou).publicacao.numero == 2


def test_a_falha_da_publicacao_nao_desfaz_a_convocacao_e_a_repeticao_a_completa(fixtures, gestor):
    """FR-6812, FR-6813: a relação que não saiu sai na repetição, sem convocar nem reenviar."""
    from processo_seletivo.convocacao.application import publicar

    edital = dois_titulares(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="g159-pub")
    recusa = DomainError("qualquer", "a publicação não pôde ser gravada", 409)
    formulario = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "assinatura"
    ]

    with mock.patch.object(publicar, "gravar_publicacao", side_effect=recusa):
        resultado = titulares(
            edital, gestor, chave="g159-pub", assinatura=formulario, autoridade=AUTORIDADE
        )

    assert resultado["publicacao"] is None
    assert resultado["publicacaoRecusa"] == "a publicação não pôde ser gravada"
    antes = contagem()
    assert antes == (2, 2, 0)

    repetido = titulares(
        edital, gestor, chave="g159-pub", assinatura=formulario, autoridade=AUTORIDADE
    )

    assert repetido["publicacao"]["numero"] == 1
    assert contagem() == (2, 2, 1), "nem convocação nem mensagem de novo — só a publicação"
    terceira = titulares(
        edital, gestor, chave="g159-pub", assinatura=formulario, autoridade=AUTORIDADE
    )
    assert terceira["publicacao"] == repetido["publicacao"], "SC-2255: a terceira não grava nada"
    assert contagem() == (2, 2, 1)


# --- Por publicação no GPS (FR-6808, FR-6809) ----------------------------------------------------


def test_no_gps_convocar_e_publicar_sao_um_instante(fixtures, gestor, caixa_de_saida):
    """SC-2253: convocação, publicação e comunicação no mesmo instante; nenhuma mensagem."""
    edital = dois_titulares(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="g159-gps")

    resultado = titulares(
        edital,
        gestor,
        chave="g159-gps",
        veiculo=fluxo.VEICULO_GPS,
        autoridade=AUTORIDADE,
        declaracao_do_veiculo=VEICULO,
    )

    assert resultado["noGps"] and resultado["enviadas"] == 2
    ato = PublicacaoDeConvocados.objects.get(id=resultado["publicacao"]["id"])
    assert ato.declaracao_do_veiculo == VEICULO
    for convocacao in Convocacao.objects.filter(edital=edital):
        [emitida] = ComunicacaoEmitida.objects.filter(convocacao=convocacao)
        assert emitida.enviado_em == ato.publicado_em == convocacao.criado_em
        assert ConvocacaoPublicada.objects.get(convocacao=convocacao).efeito == "CONVOCA"
    assert caixa_de_saida == []


def test_no_gps_sem_declaracao_nada_e_convocado(fixtures, gestor):
    edital = dois_titulares(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="g159-gps-sem")

    with pytest.raises(DomainError) as erro:
        titulares(
            edital, gestor, chave="g159-gps-sem", veiculo=fluxo.VEICULO_GPS, autoridade=AUTORIDADE
        )

    assert erro.value.code == "veiculo_nao_declarado"
    assert contagem() == (0, 0, 0), "a recusa da publicação desfaz a convocação"


def test_sem_veiculo_a_forma_por_publicacao_nao_presume_o_gps(fixtures, gestor):
    """D-006: sem veículo escolhido, o gesto convoca e aguarda o registro, como antes."""
    edital = dois_titulares(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="g159-sem-veiculo")

    resultado = titulares(edital, gestor, chave="g159-sem-veiculo", autoridade=AUTORIDADE)

    assert resultado["aguardandoPublicacao"] == 2
    assert contagem() == (2, 0, 0)


# --- Por publicação externa (FR-6810, FR-6811) ---------------------------------------------------


def test_o_registro_externo_tambem_divulga_e_o_prazo_corre_do_registro(fixtures, gestor):
    """SC-2254."""
    edital = dois_titulares(fixtures, forma=FORMA_POR_PUBLICACAO, prefixo="g159-ext")
    titulares(edital, gestor, chave="g159-ext", veiculo=fluxo.VEICULO_EXTERNO)
    previa = fluxo.previa_das_pendentes(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    resultado = fluxo.emitir_pendentes(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=previa["assinatura"],
        idempotency_key="g159-ext-registro",
        referencia_da_publicacao="site do Cefor, 12/11/2026",
        autoridade=AUTORIDADE,
    )

    ato = PublicacaoDeConvocados.objects.get(id=resultado["publicacao"]["id"])
    for vinculo in ConvocacaoPublicada.objects.filter(publicacao=ato):
        assert vinculo.efeito == "DIVULGA"
        assert vinculo.comunicacao.referencia_da_publicacao == "site do Cefor, 12/11/2026"
        assert vinculo.comunicacao.enviado_em < ato.publicado_em, "o prazo corre do registro"
    assert "site do Cefor, 12/11/2026" in bytes(ato.conteudo_publico).decode()


# --- Suplente e correção (FR-6816, FR-6817) ------------------------------------------------------


def test_a_suplente_chamada_por_mensagem_sai_numa_publicacao(fixtures, gestor):
    """SC-2256, primeira metade: a chamada individual publica na mesma confirmação."""
    from processo_seletivo.convocacao.application import selectors

    gestor_, api_client, manager_headers, process_payload = fixtures
    edital, _, _ = montar_cenario_da_convocacao(
        gestor_,
        api_client,
        manager_headers,
        process_payload,
        prefixo="g159-sup",
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]

    resultado = fluxo.convocar_e_comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        inscricao_id=fila[0],
        idempotency_key="g159-sup",
        correlation_id="teste-159",
        vencimento=timezone.now() + timedelta(days=5),
        autoridade=AUTORIDADE,
    )

    assert resultado["enviadas"] == 1
    vinculo = ConvocacaoPublicada.objects.get(convocacao_id=resultado["convocacao"]["id"])
    assert vinculo.publicacao_id == __import__("uuid").UUID(resultado["publicacao"]["id"])


def test_a_correcao_publicada_no_gps_sai_marcada(fixtures, gestor):
    """SC-2256, segunda metade: a correção de convocação publicada, publicada no GPS e marcada."""
    import json

    from processo_seletivo.convocacao.application import selectors
    from tests.integration.convocacao.test_correcao_da_convocacao import previa_de

    gestor_, api_client, manager_headers, process_payload = fixtures
    edital, _, _ = montar_cenario_da_convocacao(
        gestor_,
        api_client,
        manager_headers,
        process_payload,
        prefixo="g159-cor",
        forma=FORMA_POR_PUBLICACAO,
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    comum = {
        "actor": gestor,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "perfil_id": PROFILE_ID,
        "marco_id": MARCO,
        "inscricao_id": fila[0],
        "correlation_id": "teste-159",
        "veiculo": fluxo.VEICULO_GPS,
        "autoridade": AUTORIDADE,
        "declaracao_do_veiculo": VEICULO,
    }
    primeira = fluxo.convocar_e_comunicar(
        **comum, idempotency_key="g159-cor-1", vencimento=timezone.now() + timedelta(days=3)
    )
    raiz = Convocacao.objects.get(id=primeira["convocacao"]["id"])

    corrigida = fluxo.convocar_e_comunicar(
        **comum,
        idempotency_key="g159-cor-2",
        vencimento=timezone.now() + timedelta(days=6),
        motivo="O prazo saiu curto; é dado de novo.",
        correcao={
            "convocacao_id": str(raiz.id),
            "assinatura": previa_de(edital, raiz.id)["assinatura"],
        },
    )

    segunda = PublicacaoDeConvocados.objects.get(id=corrigida["publicacao"]["id"])
    [grupo] = json.loads(bytes(segunda.conteudo_publico).decode())["grupos"]
    assert grupo["efeito"] == "CONVOCA" and grupo["pessoas"][0]["corrige"] == 1
    sucessora = Convocacao.objects.get(convocacao_anterior=raiz)
    assert ComunicacaoEmitida.objects.get(convocacao=sucessora).enviado_em == segunda.publicado_em


# --- O que a revisão do #504 achou ---------------------------------------------------------------


def test_por_mensagem_sem_autoridade_o_resultado_diz_que_nao_publicou(fixtures, gestor):
    """D-010: sem autoridade não há publicação — mas o botão prometeu publicar, e a tela diz."""
    edital = dois_titulares(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="g159-sem-aut")

    resultado = titulares(edital, gestor, chave="g159-sem-aut")

    assert resultado["publicacao"] is None
    assert "nenhuma autoridade" in resultado["publicacaoRecusa"]
    assert contagem() == (2, 2, 0)


def test_a_mesma_chave_com_o_outro_veiculo_e_outro_pedido(fixtures, gestor):
    """D-006: a mesma chave, agora no GPS, não devolve o gesto que não publicou."""
    from processo_seletivo.convocacao.application import selectors

    gestor_, api_client, manager_headers, process_payload = fixtures
    edital, _, _ = montar_cenario_da_convocacao(
        gestor_,
        api_client,
        manager_headers,
        process_payload,
        prefixo="g159-chave",
        forma=FORMA_POR_PUBLICACAO,
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    comum = {
        "actor": gestor,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "perfil_id": PROFILE_ID,
        "marco_id": MARCO,
        "inscricao_id": fila[0],
        "correlation_id": "teste-159",
        "idempotency_key": "g159-chave",
        "vencimento": VENCIMENTO,
        "autoridade": AUTORIDADE,
        "declaracao_do_veiculo": VEICULO,
    }
    fluxo.convocar_e_comunicar(**comum, veiculo=fluxo.VEICULO_EXTERNO)

    with pytest.raises(DomainError) as erro:
        fluxo.convocar_e_comunicar(**comum, veiculo=fluxo.VEICULO_GPS)

    assert erro.value.code == "idempotency_conflict"
    assert PublicacaoDeConvocados.objects.count() == 0


def test_a_repeticao_da_publicacao_nao_depende_da_lista_relida(fixtures, gestor):
    """A segunda tentativa do mesmo clique nas pendentes relê outra lista, e recebe o que já foi."""
    from processo_seletivo.convocacao.application import publicar

    edital = dois_titulares(fixtures, forma=FORMA_POR_MENSAGEM_INDIVIDUAL, prefixo="g159-relida")
    titulares(edital, gestor, chave="g159-relida")
    ids = list(Convocacao.objects.filter(edital=edital).values_list("id", flat=True))
    comum = {
        "actor": gestor,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "autoridade": AUTORIDADE,
        "idempotency_key": "g159-relida:publicar",
        "correlation_id": "teste-159",
    }

    primeira = publicar.publicar_do_gesto(**comum, convocacoes=ids)
    segunda = publicar.publicar_do_gesto(**comum, convocacoes=ids[:1])

    assert segunda == primeira and PublicacaoDeConvocados.objects.count() == 1
