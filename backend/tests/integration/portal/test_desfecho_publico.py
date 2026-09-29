"""O Edital que acabou diz que acabou (047, US1, `FR-760` a `FR-764`, `FR-776`, `D-003`).

Até a 047 a página pública lia só o período de inscrições. Um Edital cancelado dentro do prazo
continuava anunciando *"Aberta — faltam 19 dias"*, só sem o botão, e o encerrado não dizia nada —
reproduzido pela tela em `specs/047-situacao-publica-do-edital/antes-da-047.md`.

Os atos são praticados pelo command da finalização, como a tela da gestão os pratica.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.application.finalizacao import (
    cancel_edital,
    cancel_process,
    close_edital,
    close_process,
)
from processo_seletivo.processos.domain import finalizacao as finalizacao_do_processo
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.selecao import identificador, publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GESTORA = Actor(
    "gestora.desfecho",
    "cefor",
    frozenset({"processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"}),
)
MOTIVO = "Motivo interno que o público não lê: ata 12/2026 da comissão."


def rascunho_com_periodo(agora, *, inicio_em_dias=-2, termino_em_dias=10):
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = [
        {
            "id": identificador(480, 0),
            "type": "Inscrições",
            "description": "Período de inscrições",
            "startAt": (agora + timedelta(days=inicio_em_dias)).isoformat(),
            "endAt": (agora + timedelta(days=termino_em_dias)).isoformat(),
            "order": 0,
            "isRegistrationPeriod": True,
        },
        {
            "id": identificador(481, 0),
            "type": "Resultado",
            "description": "Resultado preliminar",
            "startAt": (agora + timedelta(days=termino_em_dias + 5)).isoformat(),
            "order": 1,
        },
    ]
    return rascunho


def publicar(api_client, manager_headers, process_payload, **periodo):
    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_com_periodo(timezone.now(), **periodo),
    )


def cancelar(edital):
    edital.refresh_from_db()
    cancel_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason=MOTIVO,
        idempotency_key=f"cancelar-{edital.id}",
        correlation_id="047-desfecho",
    )


def encerrar(edital):
    edital.refresh_from_db()
    close_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason=MOTIVO,
        idempotency_key=f"encerrar-{edital.id}",
        correlation_id="047-desfecho",
    )


def encerrar_processo(edital):
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    close_process(
        actor=GESTORA,
        processo_id=processo.id,
        expected_revision=processo.revision,
        reason=MOTIVO,
        idempotency_key=f"encerrar-processo-{processo.id}",
        correlation_id="047-desfecho",
    )


def pagina(client, edital):
    return client.get(reverse("portal:selecao", args=[edital.id])).content.decode()


def cabecalho(corpo):
    inicio = corpo.index('<header class="cabecalho-da-selecao">')
    return corpo[inicio : corpo.index("</header>", inicio)]


def data_do_ato(agregado_id, operacao):
    ato = AtoAdministrativo.objects.get(aggregate_id=agregado_id, operation=operacao)
    return timezone.localtime(ato.occurred_at).strftime("%d/%m/%Y")


def cartao(corpo, edital):
    for trecho in re.findall(r'<li class="selecao.*?</li>', corpo, flags=re.S):
        if str(edital.id) in trecho:
            return trecho
    return None


def grupo_do_cartao(corpo, edital):
    """O título do grupo da vitrine sob o qual o cartão aparece."""
    posicao = corpo.index(f"/selecoes/{edital.id}/")
    titulos = [(m.start(), m.group(1)) for m in re.finditer(r"<h2[^>]*>([^<]+)</h2>", corpo)]
    anteriores = [titulo for inicio, titulo in titulos if inicio < posicao]
    return anteriores[-1].strip() if anteriores else None


# --- O cancelado -------------------------------------------------------------------------------


def test_cancelado_dentro_do_periodo_diz_o_cancelamento_e_nao_aberta(
    client, api_client, manager_headers, process_payload
):
    """O fato 1 da spec: `FR-760`, `FR-761`."""
    edital = publicar(api_client, manager_headers, process_payload)
    assert "Faltam" in cabecalho(pagina(client, edital)), "o teste pressupõe prazo correndo"

    cancelar(edital)
    topo = cabecalho(pagina(client, edital))

    assert "Edital cancelado" in topo
    assert data_do_ato(edital.id, "CANCELAR") in topo
    assert "Aberta" not in topo
    assert "Faltam" not in topo
    assert "Inscrições abertas" not in topo


def test_cancelado_com_periodo_por_abrir_nao_diz_em_breve(
    client, api_client, manager_headers, process_payload
):
    edital = publicar(
        api_client, manager_headers, process_payload, inicio_em_dias=5, termino_em_dias=15
    )
    cancelar(edital)
    topo = cabecalho(pagina(client, edital))

    assert "Edital cancelado" in topo
    assert "Em breve" not in topo
    assert "começam em" not in topo


def test_cancelado_continua_fora_da_vitrine_e_alcancavel_pelo_endereco(
    client, api_client, manager_headers, process_payload
):
    edital = publicar(api_client, manager_headers, process_payload)
    cancelar(edital)

    assert cartao(client.get(reverse("portal:vitrine")).content.decode(), edital) is None
    assert client.get(reverse("portal:selecao", args=[edital.id])).status_code == 200


def test_com_desfecho_o_registro_continua_na_pagina(
    client, api_client, manager_headers, process_payload
):
    """Preservar não é anunciar: cronograma e documentos continuam como registro (`FR-760`)."""
    edital = publicar(api_client, manager_headers, process_payload)
    cancelar(edital)
    corpo = pagina(client, edital)

    assert "Período de inscrições" in corpo
    assert "Resultado preliminar" in corpo
    assert "Ler o Edital completo (PDF)" in corpo


# --- O encerrado -------------------------------------------------------------------------------


def test_encerrado_diz_encerrado_na_pagina_e_no_cartao_distinto_da_encerrada(
    client, api_client, manager_headers, process_payload
):
    """`FR-763`: o cartão do Edital encerrado não se confunde com o de inscrições encerradas."""
    edital = publicar(api_client, manager_headers, process_payload)
    encerrar(edital)

    topo = cabecalho(pagina(client, edital))
    assert "Edital encerrado" in topo
    assert data_do_ato(edital.id, "ENCERRAR") in topo

    vitrine = client.get(reverse("portal:vitrine")).content.decode()
    trecho = cartao(vitrine, edital)
    assert trecho is not None, "o encerrado continua na vitrine"
    assert "Edital encerrado" in trecho
    assert "Ver vagas e inscrever-se" not in trecho


def test_encerrado_com_periodo_em_curso_fica_entre_as_encerradas(
    client, api_client, manager_headers, process_payload
):
    edital = publicar(api_client, manager_headers, process_payload)
    encerrar(edital)

    vitrine = client.get(reverse("portal:vitrine")).content.decode()

    assert grupo_do_cartao(vitrine, edital) == "Inscrições encerradas"


def test_encerrado_com_periodo_por_abrir_nunca_vai_para_as_proximas(
    client, api_client, manager_headers, process_payload
):
    edital = publicar(
        api_client, manager_headers, process_payload, inicio_em_dias=5, termino_em_dias=15
    )
    encerrar(edital)

    vitrine = client.get(reverse("portal:vitrine")).content.decode()

    assert grupo_do_cartao(vitrine, edital) == "Inscrições encerradas"


def test_o_filtro_de_abertas_nao_devolve_o_encerrado(
    client, api_client, manager_headers, process_payload
):
    edital = publicar(api_client, manager_headers, process_payload)
    encerrar(edital)

    vitrine = client.get(reverse("portal:vitrine"), {"situacao": "aberto"}).content.decode()

    assert cartao(vitrine, edital) is None


# --- O Processo --------------------------------------------------------------------------------


def test_encerrar_o_processo_com_edital_publicado_e_recusado(
    api_client, manager_headers, process_payload
):
    """RC-118, decidido pelo usuário em 28/09: encerrar exige os Editais em estado final.

    Era o caminho pelo qual o Edital de um Processo encerrado continuava recebendo inscrição. A
    recusa diz o que falta, por quê e o que fazer, e o Processo continua ativo.
    """
    edital = publicar(api_client, manager_headers, process_payload)

    with pytest.raises(DomainError) as recusa:
        encerrar_processo(edital)

    assert recusa.value.code == "editais_pendentes"
    assert recusa.value.status == 409
    assert f"{edital.number}/{edital.year}" in recusa.value.detail
    assert "continuaria recebendo inscrição" in recusa.value.detail
    assert "Encerre ou cancele cada Edital" in recusa.value.detail
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    assert processo.status == ProcessoSeletivo.Status.ATIVO


def test_processo_encerrado_com_edital_aberto_diz_o_fato_e_continua_recebendo(
    client, api_client, manager_headers, process_payload, monkeypatch
):
    """A regressão da revisão do #193: o Processo encerrado não fecha o Edital publicado.

    **Desde 28/09 este estado só existe no acervo** (RC-118): encerrar o Processo passou a exigir
    os Editais em estado final, e o teste acima prende a recusa. O Processo encerrado antes disso,
    com Edital publicado, continua existindo, e a página continua precisando dizê-lo — por isso o
    cenário é montado com o encerramento como era, sem a exigência.

    `recebe_inscricoes` lê o status do Edital: dentro do período, o sistema continua recebendo
    inscrição. A primeira versão da US1 dizia *"Processo seletivo encerrado… Não recebe
    inscrições"* e tirava o Edital das abertas — a página afirmava o que o sistema não faz. Agora
    ela diz o fato e a data (`FR-760`), e o Edital segue o próprio estado e período (`FR-761`,
    `FR-763`).
    """
    edital = publicar(api_client, manager_headers, process_payload)
    monkeypatch.setattr(
        finalizacao_do_processo,
        "ensure_processo_can_be_closed",
        lambda processo, pendentes=(): None,
    )
    encerrar_processo(edital)
    monkeypatch.undo()
    assert Edital.objects.get(pk=edital.id).status == Edital.Status.PUBLICADO

    corpo = pagina(client, edital)
    topo = cabecalho(corpo)

    assert "Processo seletivo encerrado" in topo
    assert data_do_ato(edital.processo_id, "ENCERRAR") in topo
    assert "Não recebe inscrições" not in topo
    assert "Aberta" in topo, "a marca continua sendo a do período"
    assert "Faltam" in topo
    assert "Inscrever-se nesta vaga" in corpo, "o sistema recebe inscrição, e a página o oferece"

    vitrine = client.get(reverse("portal:vitrine")).content.decode()
    assert grupo_do_cartao(vitrine, edital) == "Inscrições abertas"
    abertas = client.get(reverse("portal:vitrine"), {"situacao": "aberto"}).content.decode()
    assert cartao(abertas, edital) is not None


def test_o_desfecho_do_edital_vence_o_do_processo(
    client, api_client, manager_headers, process_payload
):
    """`D-003`: o Edital encerrado de um Processo depois cancelado diz o desfecho do Edital."""
    edital = publicar(api_client, manager_headers, process_payload)
    encerrar(edital)
    processo = ProcessoSeletivo.objects.get(pk=edital.processo_id)
    cancel_process(
        actor=GESTORA,
        processo_id=processo.id,
        expected_revision=processo.revision,
        reason=MOTIVO,
        idempotency_key=f"cancelar-processo-{processo.id}",
        correlation_id="047-desfecho",
    )

    topo = cabecalho(pagina(client, edital))

    assert "Edital encerrado" in topo
    assert "Processo cancelado" not in topo


# --- O que não se diz --------------------------------------------------------------------------


def test_nem_o_motivo_nem_o_autor_do_ato_aparecem(
    client, api_client, manager_headers, process_payload
):
    """`FR-764` e `FR-776`: o desfecho e a data, e nada além."""
    edital = publicar(api_client, manager_headers, process_payload)
    cancelar(edital)
    corpo = pagina(client, edital)

    assert "ata 12/2026" not in corpo
    assert GESTORA.subject not in corpo
