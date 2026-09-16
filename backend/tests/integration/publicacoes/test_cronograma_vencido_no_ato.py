"""O impedimento nos dois atos, e a ausência dele na Retificação (028, US2 e US4).

**Duas metades que se protegem mutuamente.** A primeira recusa publicar Edital cujas inscrições já
fecharam — publicá-lo é publicar um certame que ninguém pode disputar. A segunda garante que essa
recusa **não** alcança o acervo: no Edital já publicado, cronograma vencido é a condição normal, e
prender a Retificação dele bloquearia até a correção de uma vírgula.
"""

from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import (
    SIGNATORY,
    create_retification,
    encerrar_inscricoes,
    publish_original,
    retify,
    try_publish_retification,
)
from tests.fixtures.selecao import rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def rascunho(*, inicio, fim):
    conteudo = rascunho_de_selecao()
    conteudo["schedule"][0]["startAt"] = inicio.isoformat()
    conteudo["schedule"][0]["endAt"] = fim.isoformat()
    conteudo["schedule"][0]["isRegistrationPeriod"] = True
    return conteudo


def preparar(api_client, edital, conteudo, *, chave):
    """Rascunho, submissão e homologação — tudo menos publicar."""
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"], key=chave)
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        conteudo,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    edital.refresh_from_db()
    submetido = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    edital.refresh_from_db()
    homologado = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("homologador", ["edital:homologar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    edital.refresh_from_db()
    return submetido, homologado


def publicar(api_client, edital, *, chave):
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"], key=chave),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


@contextmanager
def _transacao_em(instante):
    from django.db import transaction

    with transaction.atomic():
        yield instante


def relogio(monkeypatch, instante):
    """Faz os commands de publicação enxergarem `instante` como o agora da transação.

    **Por que injetar em vez de esperar.** O conteúdo homologado não pode mudar entre a homologação
    e a publicação — mudá-lo faz a publicação recusar por divergência de revisão, que é outra
    recusa —, então só o tempo fecha o prazo. Esperá-lo de verdade custava sete segundos de CI e
    podia falhar se a submissão consumisse a janela. Substituir o relógio da transação mede a mesma
    coisa, e mede sempre.

    `command_context` é substituído no **módulo que o usa**, e não na origem: o que se troca é o
    relógio daquele ato, e nenhum outro.
    """
    from processo_seletivo.publicacoes.application import publish_edital as modulo

    monkeypatch.setattr(modulo, "command_context", lambda: _transacao_em(instante))


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


# --- T021 · a recusa alcança os dois atos (FR-346, FR-357, FR-358) ------------------------------


def test_a_submissao_e_recusada_com_o_periodo_ja_encerrado(api_client, em_elaboracao):
    agora = timezone.now()
    conteudo = rascunho(inicio=agora - timedelta(days=9), fim=agora - timedelta(hours=1))

    submetido, _ = preparar(api_client, em_elaboracao, conteudo, chave="vencido-submissao-0001")

    assert submetido.status_code == 422, submetido.content
    assert b"registration_period_closed" in submetido.content or b"encerrou em" in submetido.content


def test_a_publicacao_e_recusada_mesmo_sem_a_revisao_ter_sido_aberta(
    api_client, em_elaboracao, monkeypatch
):
    """FR-357. A conferência da publicação é independente da da submissão, e já era.

    **O rascunho não é tocado**, e é o ponto: mexer nele faria a publicação recusar por divergência
    de revisão — outra recusa, que deixaria este teste verde mesmo se a conferência da publicação
    fosse removida. O que muda é o relógio do ato, que é o que muda na vida.
    """
    agora = timezone.now()
    conteudo = rascunho(inicio=agora - timedelta(days=9), fim=agora + timedelta(days=9))
    preparar(api_client, em_elaboracao, conteudo, chave="vencido-publicacao-0001")

    relogio(monkeypatch, agora + timedelta(days=10))
    publicada = publicar(api_client, em_elaboracao, chave="vencido-publicacao-0001")

    assert publicada.status_code == 422, publicada.content
    corpo = publicada.json()
    assert corpo["code"] == "blocking_findings", corpo
    assert "encerrou em" in corpo["detail"], corpo["detail"]


def test_o_prazo_que_vence_entre_a_homologacao_e_a_publicacao_impede_publicar(
    api_client, em_elaboracao, monkeypatch
):
    """FR-358. Submissão e publicação são atos distintos, em instantes distintos.

    O Edital é submetido e homologado com o prazo correndo — a submissão **passa** —, e a publicação
    acontece depois de ele fechar. Nada no conteúdo mudou; mudou o instante do ato.
    """
    agora = timezone.now()
    conteudo = rascunho(inicio=agora - timedelta(days=9), fim=agora + timedelta(days=2))

    submetido, homologado = preparar(api_client, em_elaboracao, conteudo, chave="vencido-tempo-01")
    assert submetido.status_code < 400, "o prazo ainda corria na submissão"
    assert homologado.status_code < 400, homologado.content

    relogio(monkeypatch, agora + timedelta(days=3))
    publicada = publicar(api_client, em_elaboracao, chave="vencido-tempo-01")

    assert publicada.status_code == 422, publicada.content
    corpo = publicada.json()
    assert corpo["code"] == "blocking_findings", corpo
    assert "não receberá inscrição alguma" in corpo["detail"], corpo["detail"]
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status != Edital.Status.PUBLICADO


def test_periodo_aberto_publica_normalmente(api_client, em_elaboracao):
    """O contraponto que mede o silêncio: nada disto torna mais difícil publicar quem está certo."""
    agora = timezone.now()
    conteudo = rascunho(inicio=agora - timedelta(days=1), fim=agora + timedelta(days=9))
    preparar(api_client, em_elaboracao, conteudo, chave="vencido-aberto-0001")

    publicada = publicar(api_client, em_elaboracao, chave="vencido-aberto-0001")

    assert publicada.status_code == 201, publicada.content


# --- T026 a T028 · o acervo continua alcançável (FR-354, FR-355, FR-350) ------------------------


@pytest.fixture
def do_acervo(api_client, manager_headers, process_payload):
    """Um Edital publicado cujo cronograma inteiro já venceu — o acervo, como ele é."""
    agora = timezone.now()
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(inicio=agora - timedelta(days=60), fim=agora + timedelta(days=1)),
    )
    return encerrar_inscricoes(api_client, edital, agora - timedelta(days=30), suffix="acervo")


def test_retificar_um_edital_do_acervo_nao_produz_achado_desta_feature(api_client, do_acervo):
    """SC-115. Zero — e é o número que importa: qualquer outro faria toda Retificação de todo
    Edital antigo carregar advertência por Evento vencido, e o que se repete deixa de ser lido."""
    from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato

    base = VersaoConsolidada.objects.filter(edital=do_acervo).latest("materialized_at")
    retificacao = create_retification(
        api_client,
        do_acervo,
        [
            {
                "targetPath": "/title",
                "operation": "REPLACE",
                "newValue": "Edital com o título corrigido",
            }
        ],
        suffix="acervo-titulo",
        base=base,
    )

    codigos = {item.code for item in advertencias_do_ato(retificacao)}

    assert (
        codigos
        & {
            "schedule_event_in_past",
            "schedule_event_year_mismatch",
            "registration_period_closed",
        }
        == set()
    )


def test_a_retificacao_de_uma_frase_do_acervo_publica(api_client, do_acervo):
    """Cronograma vencido não prende Retificação nenhuma — nem a que nada tem com datas."""
    retificacao = create_retification(
        api_client,
        do_acervo,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Título retificado"}],
        suffix="acervo-frase",
    )

    publicada = try_publish_retification(api_client, retificacao, suffix="acervo-frase")

    assert publicada.status_code == 201, publicada.content


def test_antecipar_o_encerramento_das_inscricoes_nao_e_recusado(
    api_client, manager_headers, process_payload
):
    """FR-355. Encerrar ou antecipar prazo é ato normativo de quem assina o Edital, e o contrato da
    `026` já classifica `endAt` como retificável. A `028` não pode transformá-lo em impossível —
    seria fechar, pela via administrativa, a porta que ela mesma manda usar."""
    agora = timezone.now()
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(inicio=agora - timedelta(days=9), fim=agora + timedelta(days=9)),
    )
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    designado = next(e for e in versao.content["schedule"] if e.get("isRegistrationPeriod"))

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={designado['id']}/endAt",
                "operation": "REPLACE",
                "newValue": (agora - timedelta(hours=1)).isoformat(),
            }
        ],
        suffix="antecipa",
    )

    consolidada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    fechado = next(e for e in consolidada.content["schedule"] if e.get("isRegistrationPeriod"))
    assert fechado["endAt"].startswith((agora - timedelta(hours=1)).strftime("%Y-%m-%d"))


def test_a_confirmacao_da_retificacao_nao_passa_a_exibir_os_achados_desta_feature(
    api_client, do_acervo
):
    """**Guarda a decisão de não mexer em `retificacoes.py:577`.**

    Aquela linha calcula os códigos impeditivos sob o ato de **publicação**, de propósito, para
    subtraí-los da lista que a confirmação mostra. Com o impeditivo novo existindo, o conjunto
    subtraído mudou — e o resultado não pode ter mudado, porque a lista devolvida vem da conferência
    sob o ato de Retificação. É isto que este teste mede.
    """
    from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato

    retificacao = create_retification(
        api_client,
        do_acervo,
        [{"targetPath": "/description", "operation": "REPLACE", "newValue": "Nova descrição."}],
        suffix="acervo-desc",
    )

    advertencias = advertencias_do_ato(retificacao)

    assert all(
        item.code
        not in (
            "schedule_event_in_past",
            "schedule_event_year_mismatch",
            "registration_period_closed",
        )
        for item in advertencias
    ), [item.code for item in advertencias]
