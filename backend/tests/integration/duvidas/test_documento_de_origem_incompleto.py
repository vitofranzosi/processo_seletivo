"""Os dois cenários do achado de 12/10, pelo fluxo real (070, `R-004`, `R-005`, `SC-535`).

O documento que a página pública chama de "Edital completo" pode não conter uma Retificação em
vigor (`doc/achado-documento-ligado-nao-contem-a-versao-vigente.md`). A fonte de consulta não
corrige isso — é dependência da abertura pública —, mas também não depende dele:

- cada cartão leva ao documento do ato que **fixou** o valor, e esse documento sempre o contém;
- o ponto para revisão nomeia o documento incompleto e os atos que faltam nele.
"""

import json
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import consultar, pontos_para_revisao
from processo_seletivo.duvidas.domain.estruturas import (
    PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO,
    TEXTO,
)
from processo_seletivo.duvidas.domain.respostas import no_item
from processo_seletivo.publicacoes.domain.changes import resolve_path
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.publicacao import create_retification, publish_retification

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _evento_de_inscricao(versao):
    return next(e for e in versao.content["schedule"] if e["isRegistrationPeriod"])["id"]


def _mudar(evento, campo, texto):
    return [
        {"targetPath": f"/schedule/id={evento}/{campo}", "operation": "REPLACE", "newValue": texto}
    ]


def _cenario_vigencia_futura(api_client, chave):
    """R1 com vigência em +10 dias; depois R2 imediata. As duas sobre a versão original."""
    edital, _ = publicar_do_corpus(api_client, "91", ate=1, chave=chave)
    original = VersaoConsolidada.objects.get(edital=edital)
    evento = _evento_de_inscricao(original)
    futuro = timezone.now() + timedelta(days=10)
    r1 = create_retification(
        api_client,
        edital,
        _mudar(evento, "description", "Descrição de R1"),
        effective_at=futuro.isoformat(),
        base=original,
        suffix=f"{chave}-r1",
    )
    publish_retification(api_client, r1, suffix=f"{chave}-r1")
    r2 = create_retification(
        api_client,
        edital,
        _mudar(evento, "location", "Local de R2"),
        base=original,
        suffix=f"{chave}-r2",
    )
    publish_retification(api_client, r2, suffix=f"{chave}-r2")
    r1.refresh_from_db()
    r2.refresh_from_db()
    return edital, futuro + timedelta(days=1), r1, r2


def _cenario_mesma_base(api_client, chave):
    """R1 e R2 elaboradas sobre a versão original e publicadas nessa ordem."""
    edital, _ = publicar_do_corpus(api_client, "91", ate=1, chave=chave)
    original = VersaoConsolidada.objects.get(edital=edital)
    evento = _evento_de_inscricao(original)
    r1 = create_retification(
        api_client,
        edital,
        _mudar(evento, "description", "Descrição de R1"),
        base=original,
        suffix=f"{chave}-r1",
    )
    r2 = create_retification(
        api_client,
        edital,
        _mudar(evento, "location", "Local de R2"),
        base=original,
        suffix=f"{chave}-r2",
    )
    publish_retification(api_client, r1, suffix=f"{chave}-r1")
    publish_retification(api_client, r2, suffix=f"{chave}-r2")
    r1.refresh_from_db()
    r2.refresh_from_db()
    return edital, timezone.now() + timedelta(minutes=1), r1, r2


@pytest.fixture(params=["vigencia_futura", "mesma_base"])
def cenario(request, api_client):
    montar = _cenario_vigencia_futura if request.param == "vigencia_futura" else _cenario_mesma_base
    return montar(api_client, f"achado-{request.param}")


def test_cada_cartao_leva_ao_documento_do_ato_que_fixou_o_valor(cenario):
    edital, instante, r1, r2 = cenario
    resposta = consultar(edital_id=edital.id, instante=instante, pergunta="P-01")
    por_rotulo = {r.rotulo: r for r in resposta.referencias if r.natureza == TEXTO}

    assert por_rotulo["Descrição"].conteudo == "Descrição de R1"
    assert [o.publicacao_id for o in por_rotulo["Descrição"].origens] == [str(r1.publication_id)]
    assert por_rotulo["Local"].conteudo == "Local de R2"
    assert [o.publicacao_id for o in por_rotulo["Local"].origens] == [str(r2.publication_id)]


def test_valor_que_nunca_mudou_leva_a_publicacao_original(cenario):
    """Regressão de 12/10: a versão materializada por Retificação não lista a original.

    `applied_publications` dessa versão traz só as Retificações. Sem a original entre os atos, o
    início das inscrições — que nenhuma Retificação tocou — levava ao documento da primeira delas.
    """
    edital, instante, _r1, _r2 = cenario
    original = Publicacao.objects.get(edital=edital, retificacao__isnull=True)
    resposta = consultar(edital_id=edital.id, instante=instante, pergunta="P-01")
    inicio = next(r for r in resposta.referencias if r.rotulo == "Início")
    assert [o.publicacao_id for o in inicio.origens] == [str(original.id)]
    assert [o.ato for o in inicio.origens] == ["ORIGINAL"]


def test_sc535_o_documento_de_cada_origem_contem_o_valor_citado(cenario):
    edital, instante, _r1, _r2 = cenario
    resposta = consultar(edital_id=edital.id, instante=instante, pergunta="P-01")
    conferidos = 0
    for referencia in resposta.referencias:
        for origem in referencia.origens:
            publicado = json.loads(
                bytes(Publicacao.objects.get(pk=origem.publicacao_id).canonical_content)
            )
            valor = no_item(resolve_path(publicado, referencia.caminho), referencia.posicao)
            if referencia.natureza == TEXTO:
                assert valor == referencia.conteudo, (referencia.rotulo, origem.publicacao_id)
            conferidos += 1
            assert origem.documento.endswith(f"/publicacoes/{origem.publicacao_id}/documento")
    assert conferidos >= 4


def test_o_ponto_para_revisao_nomeia_o_documento_incompleto(cenario):
    edital, instante, _r1, _r2 = cenario
    pontos = pontos_para_revisao(edital_id=edital.id, instante=instante)
    incompleto = next(p for p in pontos if p.tipo == PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO)
    assert "não contém a Retificação publicada em" in incompleto.descricao

    p12 = consultar(edital_id=edital.id, instante=instante, pergunta="P-12")
    assert any(a.tipo == PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO for a in p12.avisos)
    assert "Edital completo" not in p12.explicacao.conteudo


def test_uma_retificacao_so_nao_gera_o_ponto(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="achado-uma-so")
    pontos = pontos_para_revisao(edital_id=edital.id, instante=timezone.now())
    assert PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO not in [p.tipo for p in pontos]
