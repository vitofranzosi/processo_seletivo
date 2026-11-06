"""A convocação sem comunicação enviada não aguarda resposta (126, FR-4027 a FR-4030, SC-1214).

O relatório do Edital contava pela data: sem desfecho e vencimento no futuro era "aguardando
resposta"; no passado, "prazo encerrado sem registro". O domínio diz outra coisa — o prazo só corre
do envio (`convocacao/domain/prazo`) —, e a confirmação de Encerrar, que lê o relatório, dizia
"1 convocação aguardando resposta, até 10/11" de quem nunca recebeu a comunicação.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.interface import encerramento
from processo_seletivo.interface import relatorio_consolidado as consolidado
from processo_seletivo.interface import relatorio_do_edital as rel
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def convocada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Uma convocação praticada, com vencimento em três dias, e a comunicação ainda não emitida."""
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="relatorio-126"
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    vencimento = timezone.now() + timedelta(days=3)
    declarado = convocar(
        edital, gestor, fila[0], vencimento=vencimento, idempotency_key="relatorio-126-convocar"
    )
    return edital, Convocacao.objects.get(id=declarado["id"]), vencimento


def _tipos(edital, agora):
    return {p.tipo: p for p in rel.fatos_do_edital(edital, agora=agora).pendencias}


def test_sem_comunicacao_e_especie_propria_e_nao_aguarda_resposta(convocada):
    edital, _, _ = convocada

    tipos = _tipos(edital, timezone.now())

    assert rel.CONVOCACAO_AGUARDANDO not in tipos
    pendencia = tipos[rel.CONVOCACAO_SEM_COMUNICACAO]
    assert pendencia.quantidade == 1
    assert pendencia.ate is None, "sem prazo correndo não há 'até'"
    assert rel.texto_da_pendencia(pendencia) == "1 convocação sem comunicação enviada"


def test_sem_comunicacao_com_o_vencimento_passado_nao_e_vencida(convocada):
    """FR-4030: um prazo que nunca começou não pode ter vencido (`prazo.decorrido`)."""
    edital, _, vencimento = convocada

    tipos = _tipos(edital, vencimento + timedelta(days=1))

    assert rel.CONVOCACAO_VENCIDA not in tipos
    assert rel.CONVOCACAO_SEM_COMUNICACAO in tipos


def test_o_encerrar_diz_sem_comunicacao_enviada(convocada):
    """SC-1214: a única lista do que falta no Edital, na tela de um ato irreversível."""
    edital, _, _ = convocada

    frases = [item.mensagem for item in encerramento._providencias_da_099(edital, timezone.now())]

    assert "1 convocação sem comunicação enviada." in frases
    assert not any("aguardando resposta" in frase for frase in frases)


def test_com_a_comunicacao_enviada_ela_aguarda_resposta_ate_o_vencimento(convocada, gestor):
    from tests.fixtures.documentos_da_convocacao import comunicar

    edital, convocacao, vencimento = convocada
    comunicar(edital, gestor, convocacao, chave="relatorio-126-comunicar")
    convocacao.refresh_from_db()
    assert selectors.envio_de(convocacao) is not None, "o cenário precisa do envio bem-sucedido"

    tipos = _tipos(edital, timezone.now())

    assert rel.CONVOCACAO_SEM_COMUNICACAO not in tipos
    assert tipos[rel.CONVOCACAO_AGUARDANDO].ate == vencimento
    vencida = _tipos(edital, vencimento + timedelta(days=1))
    assert rel.CONVOCACAO_VENCIDA in vencida, "enviada e vencida continua 'prazo encerrado'"


def test_o_consolidado_tem_o_rotulo_proprio():
    """FR-4029: somada entre Editais, a espécie não se mistura com 'aguardando resposta'."""
    assert consolidado.texto_do_item(rel.CONVOCACAO_SEM_COMUNICACAO, 1) == (
        "convocação sem comunicação enviada"
    )
    assert consolidado.texto_do_item(rel.CONVOCACAO_SEM_COMUNICACAO, 2) == (
        "2 convocações sem comunicação enviada"
    )
    assert rel.CONVOCACAO_SEM_COMUNICACAO in consolidado.ORDEM_DAS_PENDENCIAS
