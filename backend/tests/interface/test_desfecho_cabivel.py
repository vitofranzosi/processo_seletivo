"""O desfecho oferece o que cabe, e o atestado só onde a inércia cabe (152, histórias 5 e 6).

O seletor "O que aconteceu" listava as sete espécies a toda chamada. Numa chamada para vaga com o
prazo em curso, ele oferecia a regularização, que a chamada nunca admite; o não atendimento, que o
comando recusa antes do vencimento; e o cancelamento por inércia, que exige atestado (achado 12 do
estudo de 11/11/2026). O comando recusava os três; a tela os oferecia.

**O oráculo é o próprio comando** (SC-1906, FR-5838). Em cada cenário montado aqui, toda espécie
de `ESPECIES_DE_DESFECHO` é tentada contra `desfechar`, numa transação desfeita: a oferecida passa
pelas guardas, e a não oferecida é recusada. Uma verificação na tela e outra no comando divergiriam
na primeira regra nova, e este é o caso que acusaria.
"""

import re
from datetime import timedelta
from html import unescape
from unittest import mock

import pytest
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.atestar import atestar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import comunicar
from tests.fixtures.edital import PROFILE_ID
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

ROTULOS = {
    nomes.ACEITE: "Aceite",
    nomes.REGULARIZACAO: "Regularização",
    nomes.INDEFERIMENTO: "Indeferimento",
    nomes.DESISTENCIA_EXPRESSA: "Desistência expressa",
    nomes.NAO_ATENDIMENTO: "Não atendimento à convocação",
    nomes.INERCIA: "Cancelamento de matrícula por inércia",
    nomes.RECLASSIFICACAO: "Reclassificação",
}
ATESTAR = "<summary>Atestar fato externo</summary>"
EM_30_DIAS = timedelta(days=30)


@pytest.fixture
def do_77(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas, faixa de três: dois titulares e uma suplente — o recorte do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="desfecho-152",
        geral=2,
        cut=regra(surplusCount=1),
    )


def _fila(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]


def _chamar(edital, gestor, inscricao, chave, *, prazo=EM_30_DIAS, **kwargs):
    declarado = convocar(
        edital,
        gestor,
        inscricao,
        idempotency_key=chave,
        vencimento=timezone.now() + prazo,
        **kwargs,
    )
    convocacao = Convocacao.objects.get(id=declarado["id"])
    comunicar(edital, gestor, convocacao, chave=f"{chave}-comunicar")
    return convocacao


def _atestar(edital, gestor, inscricao, chave):
    return atestar(
        actor=gestor,
        processo_id=edital.processo_id,
        inscricao_id=inscricao,
        especie=nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE,
        conclusao="Não houve acesso ao ambiente até o fim do prazo.",
        referencia_do_prazo="Primeira semana letiva, item 9.4 do Edital.",
        idempotency_key=chave,
        correlation_id="teste-152",
    )["id"]


def _cartao(client, edital, convocacao, *, depois=None):
    """O cartão da chamada, como texto, lido agora ou `depois` do vencimento."""
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:convocacao", args=[edital.id, MARCO])
    with mock.patch(
        "django.utils.timezone.now", return_value=timezone.now() + (depois or timedelta(0))
    ):
        resposta = client.get(url)
    assert resposta.status_code == 200
    corpo = unescape(resposta.content.decode())
    achado = re.search(rf'<article [^>]*id="convocacao-{convocacao.id}".*?</article>', corpo, re.S)
    assert achado, "a chamada não tem cartão"
    return achado.group(0)


def _seletor(cartao):
    """As opções do "O que aconteceu", em ordem, e se alguma vem pré-escolhida."""
    achado = re.search(
        r'<select id="desfecho-\d+" name="especie" required>(.*?)</select>', cartao, re.S
    )
    assert achado, "o cartão não tem o seletor do desfecho"
    assert "selected" not in achado.group(1), "um ato irreversível não tem resposta padrão"
    opcoes = re.findall(r'<option value="([A-Z_]*)">([^<]*)</option>', achado.group(1))
    assert opcoes[0] == ("", "Escolha o desfecho")
    for valor, rotulo in opcoes[1:]:
        assert ROTULOS[valor] == rotulo, "os rótulos continuam os de hoje (FR-5841)"
    return [valor for valor, _ in opcoes[1:]]


def _nota(cartao):
    """As linhas de "Ainda não cabem nesta chamada", ou `[]` quando a nota não aparece."""
    achado = re.search(
        r"<strong>Ainda não cabem nesta chamada</strong></p>\s*<ul class=\"nota\">(.*?)</ul>",
        cartao,
        re.S,
    )
    if achado is None:
        return []
    return [
        re.sub(r"<[^>]+>", "", item).strip()
        for item in re.findall(r"<li>(.*?)</li>", achado.group(1), re.S)
    ]


class _Desfaz(Exception):
    """Desfaz o desfecho que o comando aceitou: o oráculo pergunta, e não registra."""


def _o_comando_aceita(edital, gestor, convocacao, especie, *, atestado_id):
    try:
        with transaction.atomic():
            desfechar(
                actor=gestor,
                processo_id=edital.processo_id,
                convocacao_id=convocacao.id,
                especie=especie,
                fundamento="Oráculo da 152.",
                atestado_id=atestado_id if especie == nomes.INERCIA else None,
                idempotency_key=f"oraculo-152-{convocacao.id}-{especie}",
                correlation_id="teste-152",
            )
            raise _Desfaz
    except _Desfaz:
        return True
    except DomainError:
        return False


def _oraculo(edital, gestor, convocacao, oferecidas, *, atestado_id=None, depois=None):
    """SC-1906: oferecida ⇔ aceita pelo comando, para as sete espécies."""
    agora = timezone.now() + (depois or timedelta(0))
    with mock.patch("django.utils.timezone.now", return_value=agora):
        aceitas = [
            especie
            for especie in nomes.ESPECIES_DE_DESFECHO
            if _o_comando_aceita(edital, gestor, convocacao, especie, atestado_id=atestado_id)
        ]
    assert aceitas == oferecidas


def test_alice_ve_quatro_opcoes_e_a_nota_nomeia_duas(client, seletor_ligado, gestor, do_77):
    """Cenários 1 e 2 e SC-1905: vaga inicial, nada por conferir, prazo em curso, sem atestado."""
    edital, _, _ = do_77
    alice = _chamar(edital, gestor, _fila(edital)[0], "alice-152")

    cartao = _cartao(client, edital, alice)
    oferecidas = _seletor(cartao)
    nota = _nota(cartao)

    assert oferecidas == [
        nomes.ACEITE,
        nomes.INDEFERIMENTO,
        nomes.DESISTENCIA_EXPRESSA,
        nomes.RECLASSIFICACAO,
    ]
    vencimento = timezone.localtime(alice.vencimento).strftime("%d/%m/%Y %H:%M")
    assert nota == [
        "Não atendimento à convocação: O vencimento informado nesta convocação ainda não passou: "
        f"a pessoa está dentro do prazo dela. Cabe a partir de {vencimento}.",
        "Cancelamento de matrícula por inércia: O cancelamento de matrícula por inércia exige "
        "atestado de fato externo: registre quem atestou e o que concluiu.",
    ]
    # FR-5837: a espécie que a chamada nunca admite não aparece no seletor nem na nota.
    assert "Regularização" not in cartao
    _oraculo(edital, gestor, alice, oferecidas)


def test_com_atestado_a_inercia_cabe(client, seletor_ligado, gestor, do_77):
    """Com atestado registrado e a pessoa ocupando, o cancelamento por inércia vai ao seletor."""
    edital, _, _ = do_77
    titular = _fila(edital)[0]
    chamada = _chamar(edital, gestor, titular, "atestada-152")
    atestado = _atestar(edital, gestor, titular, "atestada-152-atestado")

    cartao = _cartao(client, edital, chamada)
    oferecidas = _seletor(cartao)

    assert nomes.INERCIA in oferecidas
    assert [linha.split(":")[0] for linha in _nota(cartao)] == ["Não atendimento à convocação"]
    _oraculo(edital, gestor, chamada, oferecidas, atestado_id=atestado)


def test_vencido_o_nao_atendimento_vai_ao_seletor(client, seletor_ligado, gestor, do_77):
    """Cenário 5: com o vencimento decorrido, o não atendimento cabe."""
    edital, _, _ = do_77
    # Um minuto de prazo, e a tela lida dois dias depois: a sessão da gestão não dura um mês.
    chamada = _chamar(edital, gestor, _fila(edital)[0], "vencida-152", prazo=timedelta(minutes=1))
    depois = timedelta(days=2)

    cartao = _cartao(client, edital, chamada, depois=depois)
    oferecidas = _seletor(cartao)

    assert nomes.NAO_ATENDIMENTO in oferecidas
    assert [linha.split(":")[0] for linha in _nota(cartao)] == [
        "Cancelamento de matrícula por inércia"
    ]
    _oraculo(edital, gestor, chamada, oferecidas, depois=depois)


def test_com_documento_por_conferir_o_aceite_vai_para_a_nota(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload,
    raiz_de_arquivos,
):  # fmt: skip
    """Cenário 3: o aceite sai do seletor, e a nota diz o que falta, com a frase do comando.

    A chamada ainda não comunicada também diz por que o não atendimento não cabe: o prazo nem
    começou a correr, e não há data a partir da qual caiba.
    """
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="desfecho-docs-152",
    )
    edital, _, _ = cenario
    _, chamada = cenarios.convocar_primeira(cenario, gestor, vencimento=timezone.now() + EM_30_DIAS)

    cartao = _cartao(client, edital, chamada)
    oferecidas = _seletor(cartao)
    nota = _nota(cartao)

    assert nomes.ACEITE not in oferecidas
    assert nota[0].startswith(
        "Aceite: Para registrar este desfecho, todo documento obrigatório da convocação precisa "
        "estar conferido como conforme"
    )
    assert "Falta: " in nota[0]
    assert nota[1].startswith("Não atendimento à convocação: ")
    assert "Cabe a partir de" not in nota[1]
    # A nota antiga virou a linha do aceite: a mesma falta não é dita duas vezes.
    assert "são recusados enquanto faltar conferir" not in cartao
    _oraculo(edital, gestor, chamada, oferecidas)


@pytest.fixture
def com_indeferidos(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Dois indeferidos na faixa: o recorte do item 8.2 do 77/2026."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="regularizar-desfecho-152",
        indeferidas=(0, 1),
    )


def test_a_chamada_para_regularizar_nao_oferece_aceite_inercia_nem_atestado(
    client, seletor_ligado, gestor, com_indeferidos
):
    """Cenário 4 da história 5 e história 6 (FR-5837, FR-5840)."""
    edital, _, _ = com_indeferidos
    indeferido = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["regularizaveis"][0]
    # Um atestado da Inscrição, para provar que nem o seletor do atestado aparece aqui.
    atestado = _atestar(edital, gestor, indeferido, "regularizar-152-atestado")
    chamada = _chamar(edital, gestor, indeferido, "regularizar-152", especie=nomes.PARA_REGULARIZAR)

    cartao = _cartao(client, edital, chamada)
    oferecidas = _seletor(cartao)

    assert oferecidas == [
        nomes.REGULARIZACAO,
        nomes.INDEFERIMENTO,
        nomes.DESISTENCIA_EXPRESSA,
        nomes.RECLASSIFICACAO,
    ]
    assert [linha.split(":")[0] for linha in _nota(cartao)] == ["Não atendimento à convocação"]
    assert "Aceite</" not in cartao
    assert "inércia" not in cartao
    assert ATESTAR not in cartao
    assert 'name="atestado"' not in cartao
    _oraculo(edital, gestor, chamada, oferecidas, atestado_id=atestado)


def test_o_atestado_aparece_na_vaga_inicial_e_na_suplencia(client, seletor_ligado, gestor, do_77):
    """História 6: o gesto continua nas duas espécies que admitem a inércia (FR-5840).

    A suplente chamada não ocupa vaga ainda, e a nota diz isso com a frase do comando, mesmo com
    atestado registrado: é a razão que o comando diria primeiro.
    """
    edital, _, _ = do_77
    fila = _fila(edital)
    titular = _chamar(edital, gestor, fila[0], "t1-152")
    desistente = _chamar(edital, gestor, fila[1], "t2-152")
    cenarios.desfechar(edital, gestor, desistente, nomes.DESISTENCIA_EXPRESSA, "t2-152-desiste")
    apurar(edital, gestor, chave="suplencia-152-apurar", motivo="Desistência")
    suplente = _chamar(edital, gestor, fila[2], "suplente-152", especie=nomes.SUPLENCIA)
    atestado = _atestar(edital, gestor, fila[2], "suplente-152-atestado")

    assert ATESTAR in _cartao(client, edital, titular)
    cartao = _cartao(client, edital, suplente)
    assert ATESTAR in cartao
    oferecidas = _seletor(cartao)
    assert nomes.INERCIA not in oferecidas
    assert [linha for linha in _nota(cartao) if linha.startswith("Cancelamento")] == [
        "Cancelamento de matrícula por inércia: Esta Inscrição não consta ocupando vaga neste "
        "recorte: não há matrícula a cancelar por inércia. Quem foi chamado e não respondeu tem "
        "desfecho próprio — não atendimento à convocação."
    ]
    _oraculo(edital, gestor, suplente, oferecidas, atestado_id=atestado)
