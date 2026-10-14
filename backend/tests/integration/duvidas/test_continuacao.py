"""A conversa continua, e a versão é conferida a cada pergunta (071, US2, `FR-1494`, `FR-1495`).

O histórico que o modelo recebe é o que o servidor gravou, da mesma versão vigente, e só com as
respostas conferidas. Os casos de versão atravessam a fronteira de vigência e uma Retificação
publicada entre duas perguntas, pelo fluxo real — por isso transacionais, como os da `070`.
"""

import threading
import uuid
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.duvidas.application import perguntar as aplicacao
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    NAO_PASSOU_NA_CONFERENCIA,
    RESPONDIDA_E_CONFERIDA,
    TELA,
)
from processo_seletivo.duvidas.models import TrocaDoPiloto
from tests.fixtures.corpus import alteracoes, publicar_do_corpus, retificar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _perguntar(edital, conversa, texto, instante=None):
    return aplicacao.perguntar(
        edital_id=edital.id,
        conversa=conversa,
        pergunta=texto,
        instante=instante or timezone.now(),
        origem=TELA,
    )


def _vagas(perfil, valor):
    def responder(mensagens):
        total = fonte(mensagens, lugar=perfil, rotulo="Vagas imediatas")
        return devolucao(saida("RESPONDIDA", ("dado", f"São {valor} vagas.", [total["id"]])))

    return responder


def _termino(mensagens):
    termino = fonte(mensagens, lugar="Cronograma — evento", rotulo="Término")
    return devolucao(saida("RESPONDIDA", ("dado", "O término está na fonte.", [termino["id"]])))


def test_cb01_a_continuacao_leva_o_par_anterior(api_client, porta_falsa, contador_falso):
    contador_falso()
    edital, _ = publicar_do_corpus(api_client, "91", chave="cont-cb01")
    conversa = str(uuid.uuid4())
    porta = porta_falsa(_vagas("INF-BJN", 45), _vagas("INF-IUN", 40))

    primeira = _perguntar(edital, conversa, "Quantas vagas tem o polo de Bom Jesus do Norte?")
    segunda = _perguntar(edital, conversa, "E no polo de Iúna?")

    assert primeira.estado == segunda.estado == RESPONDIDA_E_CONFERIDA
    enviadas = porta.chamadas[1]["mensagens"]
    assert [m["role"] for m in enviadas] == ["system", "user", "user", "assistant", "user"]
    assert enviadas[2]["content"] == "Quantas vagas tem o polo de Bom Jesus do Norte?"
    assert enviadas[3]["content"] == "São 45 vagas."
    assert segunda.historico_desde == primeira.ordem
    assert segunda.fontes_citadas[0]["lugar"].startswith("Perfil INF-IUN")


def _fronteira_da_v3(deslocamento):
    return parse_datetime(alteracoes("01", 3)["vigencia"].replace(" ", "T")) + deslocamento


def test_cb04_ca19_a_fronteira_entre_turnos_corta_o_historico(
    api_client, porta_falsa, contador_falso
):
    """Sem ato novo naquele dia: só a vigência chegou. O turno da versão anterior não vai."""
    contador_falso()
    edital, deslocamento = publicar_do_corpus(api_client, "01", chave="cont-cb04")
    fronteira = _fronteira_da_v3(deslocamento)
    conversa = str(uuid.uuid4())
    porta = porta_falsa(_termino, _termino)

    antes = _perguntar(
        edital, conversa, "Até quando posso me inscrever?", fronteira - timedelta(minutes=5)
    )
    depois = _perguntar(
        edital, conversa, "Então tenho até o dia 31?", fronteira + timedelta(minutes=5)
    )

    assert antes.versao != depois.versao
    assert [m["role"] for m in porta.chamadas[1]["mensagens"]] == ["system", "user", "user"]
    assert depois.historico_desde is None


def test_cb03_ca18_a_retificacao_entre_turnos_corta_o_historico(
    api_client, porta_falsa, contador_falso
):
    contador_falso()
    edital, deslocamento = publicar_do_corpus(api_client, "91", ate=1, chave="cont-cb03")
    conversa = str(uuid.uuid4())
    porta = porta_falsa(_vagas("INF-BJN", 40), _vagas("INF-BJN", 45))

    antes = _perguntar(edital, conversa, "Quantas vagas tem o polo de Bom Jesus do Norte?")
    retificar_do_corpus(api_client, edital, "91", 2, deslocamento, chave="cont-cb03")
    depois = _perguntar(edital, conversa, "E quantas são agora?")

    assert antes.versao != depois.versao
    assert depois.estado == RESPONDIDA_E_CONFERIDA
    assert len(porta.chamadas[1]["mensagens"]) == 3


def test_o_turno_recusado_nao_entra_no_historico(api_client, porta_falsa, contador_falso):
    contador_falso()
    edital, _ = publicar_do_corpus(api_client, "91", chave="cont-recusa")
    conversa = str(uuid.uuid4())
    inventada = devolucao(saida("RESPONDIDA", ("dado", "São 999 vagas.", ["F9999"])))
    porta = porta_falsa(inventada, _vagas("INF-BJN", 45))

    recusada = _perguntar(edital, conversa, "Quantas vagas?")
    _perguntar(edital, conversa, "E em Bom Jesus do Norte?")

    assert recusada.estado == NAO_PASSOU_NA_CONFERENCIA
    assert len(porta.chamadas[1]["mensagens"]) == 3


def test_duas_abas_gravam_em_ordens_distintas(api_client):
    """Duas gravações da mesma conversa, juntas, em duas conexões: a trava da conversa as ordena."""
    edital, _ = publicar_do_corpus(api_client, "91", chave="cont-abas")
    conversa = str(uuid.uuid4())
    largada = threading.Barrier(2)
    falhas = []

    def gravar():
        try:
            troca = TrocaDoPiloto(
                conversa=conversa,
                edital_id=edital.id,
                instante=timezone.now(),
                origem=TELA,
                pergunta="Quantas vagas?",
                servico="ollama",
                modelo_configurado="modelo/de-teste",
                versao_das_instrucoes="1",
            )
            largada.wait()
            aplicacao._gravar(troca, NAO_PASSOU_NA_CONFERENCIA, 0.0, "")
        except Exception as erro:  # noqa: BLE001 — o caso quer ver qualquer falha
            falhas.append(erro)
        finally:
            connection.close()

    linhas = [threading.Thread(target=gravar) for _ in range(2)]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join()

    assert falhas == []
    assert sorted(
        TrocaDoPiloto.objects.filter(conversa=conversa).values_list("ordem", flat=True)
    ) == [
        1,
        2,
    ]
