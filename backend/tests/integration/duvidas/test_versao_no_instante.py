"""A resposta é sempre da versão vigente no instante, e nunca mistura versões (070, US2).

Pelo fluxo real (`R-016`): os Editais do corpus republicados com as datas deslocadas, e as
Retificações aplicadas pela API. Os casos prendem o que só existe no banco — a versão no instante,
a fronteira de vigência sem ato novo, a Retificação pendente que não conta — e a varredura do
`SC-531`, com a guarda de rede do `SC-536`.
"""

import socket
import urllib.request
from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.duvidas.application.consultar import (
    SemVersaoVigente,
    consultar,
    contexto,
)
from processo_seletivo.duvidas.domain import catalogo, leitura
from processo_seletivo.duvidas.domain.estruturas import DADO, EXPLICACAO
from processo_seletivo.duvidas.domain.respostas import responder
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.corpus import (
    alteracoes,
    conteudo,
    publicar_do_corpus,
    retificar_do_corpus,
)
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import create_retification

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _termino(resposta):
    return next(r for r in resposta.referencias if r.natureza == DADO and r.rotulo == "Término")


def _vigencia_da_v3(deslocamento):
    vigencia = alteracoes("01", 3)["vigencia"].replace(" ", "T")
    return parse_datetime(vigencia) + deslocamento


def _esperado(valor_do_corpus, deslocamento):
    return leitura.instante_legivel(parse_datetime(valor_do_corpus) + deslocamento)


def test_ca17_pelo_banco_antes_e_depois_da_fronteira(api_client):
    edital, deslocamento = publicar_do_corpus(api_client, "01", chave="v-ca17")
    fronteira = _vigencia_da_v3(deslocamento)
    termino_v2 = next(e for e in conteudo("01", 2)["schedule"] if e["isRegistrationPeriod"])[
        "endAt"
    ]
    termino_v3 = next(e for e in conteudo("01", 3)["schedule"] if e["isRegistrationPeriod"])[
        "endAt"
    ]

    antes = consultar(edital_id=edital.id, instante=fronteira - timedelta(days=1), pergunta="P-01")
    assert _termino(antes).conteudo == _esperado(termino_v2, deslocamento)
    assert [valor.valor for valor in _termino(antes).futuro] == [
        _esperado(termino_v3, deslocamento)
    ]

    depois = consultar(edital_id=edital.id, instante=fronteira + timedelta(days=1), pergunta="P-01")
    assert _termino(depois).conteudo == _esperado(termino_v3, deslocamento)
    assert depois.versao.vigente_desde == fronteira


def test_retificacao_publicada_depois_do_instante_nao_e_antecipada(api_client):
    """ "Só os atos já publicados contam" vale para o instante da consulta, e não para agora.

    A Retificação publicada depois do instante tem vigência posterior a ele, e era lida como
    "futura já publicada": a consulta ao passado dizia um ato que ainda não existia (revisão de
    12/10). O filtro é `materialized_at`.
    """
    edital, deslocamento = publicar_do_corpus(api_client, "01", ate=2, chave="v-antecipada")
    antes = timezone.now()
    retificar_do_corpus(api_client, edital, "01", 3, deslocamento, chave="v-antecipada")

    no_passado = contexto(edital_id=edital.id, instante=antes)
    assert no_passado.futuras == ()
    resposta = responder(no_passado, "P-01")
    assert "RETIFICACAO_FUTURA" not in [aviso.tipo for aviso in resposta.avisos]
    assert not [valor for r in resposta.referencias for valor in r.futuro]

    agora = contexto(edital_id=edital.id, instante=timezone.now())
    assert len(agora.futuras) == 1


def test_ca18_a_retificacao_publicada_entre_duas_consultas_gera_o_aviso(api_client):
    edital, deslocamento = publicar_do_corpus(api_client, "91", ate=1, chave="v-ca18")
    primeira = consultar(
        edital_id=edital.id, instante=timezone.now(), pergunta="P-03", perfil="INF-BJN"
    )
    assert primeira.mudanca is None

    retificar_do_corpus(api_client, edital, "91", 2, deslocamento, chave="v-ca18")
    segunda = consultar(
        edital_id=edital.id,
        instante=timezone.now(),
        pergunta="P-03",
        perfil="INF-BJN",
        versao_anterior=primeira.versao.id,
    )
    assert segunda.mudanca is not None
    assert len(segunda.mudanca.atos) == 1
    assert next(r for r in segunda.referencias if r.rotulo == "Vagas imediatas").conteudo == "45"


def test_ca19_so_a_fronteira_passa_e_o_aviso_vem_mesmo_sem_ato_novo(api_client):
    edital, deslocamento = publicar_do_corpus(api_client, "01", chave="v-ca19")
    fronteira = _vigencia_da_v3(deslocamento)
    antes = consultar(
        edital_id=edital.id, instante=fronteira - timedelta(minutes=1), pergunta="P-01"
    )
    depois = consultar(
        edital_id=edital.id,
        instante=fronteira + timedelta(minutes=1),
        pergunta="P-01",
        versao_anterior=antes.versao.id,
    )
    assert depois.versao.id != antes.versao.id
    assert depois.mudanca is not None


def _submeter_e_homologar(api_client, retificacao, sufixo):
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers(
                "retificador", ["retificacao:submeter"], key=f"pendente-{sufixo}-chave-0002"
            ),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    resposta = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers(
                "homologador-r", ["retificacao:homologar"], key=f"pendente-{sufixo}-chave-0003"
            ),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    assert resposta.status_code < 400, resposta.content


def test_sc532_retificacao_em_elaboracao_ou_homologada_nao_muda_resposta(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", ate=1, chave="v-sc532")
    agora = timezone.now()

    def todas():
        lido = contexto(edital_id=edital.id, instante=agora)
        return [
            responder(
                lido,
                pergunta.codigo,
                perfil="INF-BJN" if pergunta.parametros else None,
                modalidade="PPI" if catalogo.MODALIDADE in pergunta.parametros else None,
            ).como_dict()
            for pergunta in catalogo.oferecidas(lido.conteudo)
        ]

    antes = todas()
    perfil = conteudo("91", 1)["profiles"][0]
    linha_ampla = next(linha for linha in perfil["vacancyTable"] if linha["modalityId"] is None)
    mudanca = [
        {
            "targetPath": f"/profiles/id={perfil['id']}/immediateVacancies",
            "operation": "REPLACE",
            "newValue": 99,
        },
        {
            "targetPath": f"/profiles/id={perfil['id']}/vacancyTable/id={linha_ampla['id']}"
            "/immediateVacancies",
            "operation": "REPLACE",
            "newValue": 87,
        },
    ]
    create_retification(api_client, edital, mudanca, suffix="pendente-a")
    homologada = create_retification(api_client, edital, mudanca, suffix="pendente-b")
    _submeter_e_homologar(api_client, homologada, "b")

    assert todas() == antes


def test_edital_sem_versao_vigente_nao_tem_consulta(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", ate=1, chave="v-sem")
    primeira = VersaoConsolidada.objects.filter(edital=edital).order_by("valid_from").first()
    with pytest.raises(SemVersaoVigente):
        consultar(
            edital_id=edital.id,
            instante=primeira.valid_from - timedelta(seconds=1),
            pergunta="P-01",
        )


@pytest.fixture
def sem_rede(monkeypatch):
    """Toda tentativa de rede é registrada e falha (`SC-536`, `FR-1447`)."""
    tentativas = []

    def recusar(*argumentos, **nomeados):
        tentativas.append(argumentos)
        raise OSError("a Fase A não sai da aplicação")

    monkeypatch.setattr(socket.socket, "connect", recusar)
    monkeypatch.setattr(socket, "create_connection", recusar)
    monkeypatch.setattr(urllib.request, "urlopen", recusar)
    return tentativas


def test_a_guarda_de_rede_enxerga_uma_chamada(sem_rede):
    with pytest.raises(OSError):
        urllib.request.urlopen("http://exemplo.invalid/")
    assert len(sem_rede) == 1


def _instantes_em_volta(edital):
    instantes = []
    for versao in VersaoConsolidada.objects.filter(edital=edital).order_by("valid_from"):
        instantes += [
            versao.valid_from - timedelta(seconds=1),
            versao.valid_from + timedelta(seconds=1),
        ]
    return [instante for instante in instantes if instante >= instantes[1]]


def test_sc531_e_sc536_a_varredura_toda_na_mesma_versao_e_sem_rede(api_client, sem_rede):
    respostas = 0
    for nome in ("01", "91", "92"):
        edital, _ = publicar_do_corpus(api_client, nome, chave=f"v-varredura-{nome}")
        for instante in _instantes_em_volta(edital):
            lido = contexto(edital_id=edital.id, instante=instante)
            vigente = effective_version(edital_id=edital.id, at=instante)
            # A original entra sempre: a versão materializada por Retificação não a lista.
            original = Publicacao.objects.get(edital=edital, retificacao__isnull=True)
            aplicados = {str(item) for item in vigente.applied_publications} | {str(original.id)}
            for pergunta in catalogo.oferecidas(lido.conteudo):
                perfis = [None]
                if catalogo.PERFIL in pergunta.parametros:
                    perfis = [codigo for codigo, _ in catalogo.opcoes_de_perfil(lido.conteudo)][:3]
                for perfil in perfis:
                    resposta = responder(
                        lido,
                        pergunta.codigo,
                        perfil=perfil,
                        modalidade="nenhuma" if perfil else None,
                    )
                    respostas += 1
                    assert resposta.versao.id == str(vigente.id)
                    for referencia in resposta.referencias:
                        if referencia.natureza == EXPLICACAO:
                            continue
                        origens = {origem.publicacao_id for origem in referencia.origens}
                        assert origens <= aplicados, (nome, pergunta.codigo, referencia.caminho)
    assert respostas > 100
    assert sem_rede == []
