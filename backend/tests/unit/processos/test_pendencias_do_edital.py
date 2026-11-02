"""O que impede encerrar, e o que só se adverte — a regra da `113`, tipo a tipo (FR-3529 a FR-3534).

O período é conferido sobre o conteúdo, sem banco: a régua do recebimento é pura, e os casos-limite
(sem término, cancelado, não designado) são formas do Evento. O resto pede o certame de verdade —
resultado divulgado, recurso interposto, Retificação homologada —, montado pelos cenários da suíte.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.processos.application import pendencias_do_edital as p
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.fixtures.divulgacao import publicar_o_ato
from tests.fixtures.edital import actor_headers
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador
from tests.integration.portal.test_desfecho_publico import rascunho_com_periodo
from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
from tests.portal.test_prazo_recursal_publico import montar

JANELA = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


def tipos(situacoes):
    return [(s.especie, s.tipo) for s in situacoes]


# ---------------------------------------------------------------------------------------------
# O período (FR-3529; D-008)
# ---------------------------------------------------------------------------------------------


def periodo(agora, **ajuste):
    conteudo = rascunho_com_periodo(agora)
    evento = conteudo["schedule"][0]
    for campo, valor in ajuste.items():
        if valor is None:
            evento.pop(campo, None)
        else:
            evento[campo] = valor
    return p._do_periodo(conteudo, agora, com_advertencias=True)


def test_periodo_em_curso_com_termino_impede_e_diz_ate_quando():
    agora = timezone.now()
    [situacao] = periodo(agora)
    assert (situacao.especie, situacao.tipo) == (p.IMPEDIMENTO, p.PERIODO_EM_CURSO)
    assert situacao.ate is not None
    assert "Encerrar antes disso não é conclusão regular" in p.frase(situacao)


def test_periodo_por_abrir_impede():
    agora = timezone.now()
    [situacao] = periodo(agora, startAt=(agora + timedelta(days=3)).isoformat())
    assert (situacao.especie, situacao.tipo) == (p.IMPEDIMENTO, p.PERIODO_POR_ABRIR)
    assert "cancele-o" in p.frase(situacao)


def test_periodo_sem_termino_so_adverte():
    """D-008: sem término o período recebe para sempre; impedir tornaria encerrar impossível."""
    agora = timezone.now()
    assert tipos(periodo(agora, endAt=None)) == [(p.ADVERTENCIA, p.PERIODO_SEM_TERMINO)]
    assert p._do_periodo(rascunho_sem_termino(agora), agora, com_advertencias=False) == []


def rascunho_sem_termino(agora):
    conteudo = rascunho_com_periodo(agora)
    conteudo["schedule"][0].pop("endAt")
    return conteudo


def test_periodo_encerrado_nao_impede():
    agora = timezone.now()
    assert periodo(agora, endAt=(agora - timedelta(hours=1)).isoformat()) == []


def test_periodo_cancelado_nao_impede_quaisquer_que_sejam_as_datas():
    agora = timezone.now()
    assert periodo(agora, status="CANCELADO") == []


def test_sem_periodo_designado_nao_impede():
    agora = timezone.now()
    conteudo = rascunho_com_periodo(agora)
    conteudo["schedule"] = conteudo["schedule"][1:]
    assert p._do_periodo(conteudo, agora, com_advertencias=True) == []


# ---------------------------------------------------------------------------------------------
# O prazo recursal (FR-3530; D-002)
# ---------------------------------------------------------------------------------------------

pytestmark_db = pytest.mark.django_db(transaction=True)


def prazos(edital, agora):
    return p._dos_prazos_recursais(
        edital, p._marcos_do_conteudo(_conteudo(edital, agora)), agora, com_advertencias=True
    )


def _conteudo(edital, agora):
    from processo_seletivo.publicacoes.application.selectors import effective_version

    return effective_version(edital_id=edital.id, at=agora).content


@pytestmark_db
def test_prazo_declarado_em_curso_impede_e_some_quando_fecha(
    gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=31, janela=JANELA)
    publicar_o_ato(cenario, chave="publicar-113-31")
    edital = cenario["edital"]

    [situacao] = prazos(edital, timezone.now())
    assert (situacao.especie, situacao.tipo) == (p.IMPEDIMENTO, p.PRAZO_RECURSAL_EM_CURSO)
    assert situacao.marco and situacao.ate

    assert prazos(edital, timezone.now() + timedelta(days=30)) == []


@pytestmark_db
def test_prazo_nao_declarado_so_adverte(gestor, api_client, manager_headers, process_payload):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=32, janela=None)
    publicar_o_ato(cenario, chave="publicar-113-32")

    assert tipos(prazos(cenario["edital"], timezone.now())) == [
        (p.ADVERTENCIA, p.PRAZO_RECURSAL_NAO_DECLARADO)
    ]


@pytestmark_db
def test_marco_que_nao_admite_recurso_nao_impede_nem_adverte(
    gestor, api_client, manager_headers, process_payload
):
    cenario = montar(
        gestor, api_client, manager_headers, process_payload, seed=33, janela={"admits": False}
    )
    publicar_o_ato(cenario, chave="publicar-113-33")

    assert prazos(cenario["edital"], timezone.now()) == []


@pytestmark_db
def test_sem_resultado_divulgado_nao_ha_prazo(gestor, api_client, manager_headers, process_payload):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=34, janela=JANELA)
    assert prazos(cenario["edital"], timezone.now()) == []


# ---------------------------------------------------------------------------------------------
# O recurso, a reavaliação e a providência (FR-3531, FR-3532)
# ---------------------------------------------------------------------------------------------


def recursos(edital):
    return p._dos_recursos(edital, p._marcos_do_conteudo(_conteudo(edital, timezone.now())))


@pytestmark_db
def test_recurso_admitido_sem_decisao_impede(gestor, api_client, manager_headers, process_payload):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=135, codigo="1135"
    )
    [situacao] = recursos(peca["cenario"]["edital"])
    assert (situacao.tipo, situacao.quantidade) == (p.RECURSO_AGUARDANDO, 1)
    assert p.frase(situacao) == "1 recurso aguarda decisão"


@pytestmark_db
def test_recurso_sem_juizo_tambem_impede(gestor, api_client, manager_headers, process_payload):
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=136,
        codigo="1136",
        admitir_a_peca=False,
    )
    assert tipos(recursos(peca["cenario"]["edital"])) == [(p.IMPEDIMENTO, p.RECURSO_AGUARDANDO)]


@pytestmark_db
def test_recurso_indeferido_deixa_de_impedir(gestor, api_client, manager_headers, process_payload):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=137, codigo="1137"
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="Sem razão.",
        idempotency_key="indeferir-113",
    )
    assert recursos(peca["cenario"]["edital"]) == []


@pytestmark_db
def test_reavaliacao_determinada_passa_a_impedir_no_lugar_do_recurso(
    gestor, api_client, manager_headers, process_payload
):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=138, codigo="1138"
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-113",
    )
    [situacao] = recursos(peca["cenario"]["edital"])
    assert situacao.tipo == p.REAVALIACAO_PENDENTE
    assert situacao.marco


@pytestmark_db
def test_providencia_determinada_impede(gestor, api_client, manager_headers, process_payload):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=139, codigo="1139"
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato de ordenação corrigindo o critério de desempate.",
        idempotency_key="providencia-113",
    )
    assert tipos(recursos(peca["cenario"]["edital"])) == [(p.IMPEDIMENTO, p.PROVIDENCIA_PENDENTE)]


# ---------------------------------------------------------------------------------------------
# A Retificação (FR-3533, FR-3534; D-003)
# ---------------------------------------------------------------------------------------------


def criar(api_client, edital, titulo="Título retificado"):
    """Como o `criar` do A-09, com chave própria por título: lá cada teste cria uma só."""
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    base = VersaoConsolidada.objects.get(edital=edital)
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": titulo}],
        },
        format="json",
        **actor_headers("ana", ["retificacao:elaborar"], key=f"criar-113-{titulo}-0000000"),
    )
    assert resposta.status_code == 201, resposta.content
    return Retificacao.objects.get(pk=resposta.json()["id"])


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    return publish_original(api_client, manager_headers, process_payload)


@pytestmark_db
def test_homologada_impede_e_as_em_curso_so_advertem(api_client, edital):
    levar_a(criar(api_client, edital, titulo="Um"), Retificacao.Status.EM_REVISAO)
    homologada = levar_a(criar(api_client, edital, titulo="Dois"), Retificacao.Status.HOMOLOGADA)
    criar(api_client, edital, titulo="Três")

    achadas = p._das_retificacoes(edital, com_advertencias=True)

    assert tipos(achadas) == [
        (p.ADVERTENCIA, p.RETIFICACAO_EM_CURSO),
        (p.IMPEDIMENTO, p.RETIFICACAO_HOMOLOGADA),
        (p.ADVERTENCIA, p.RETIFICACAO_EM_CURSO),
    ]
    assert achadas[1].retificacao_id == homologada.id
    assert "Publique-a ou devolva-a" in p.frase(achadas[1])
    assert "em revisão" in p.frase(achadas[0]) and "em elaboração" in p.frase(achadas[2])
    assert p._das_retificacoes(edital, com_advertencias=False) == [achadas[1]]


@pytestmark_db
def test_duas_homologadas_sao_dois_impedimentos(api_client, edital):
    levar_a(criar(api_client, edital, titulo="Um"), Retificacao.Status.HOMOLOGADA)
    levar_a(criar(api_client, edital, titulo="Dois"), Retificacao.Status.HOMOLOGADA)

    assert tipos(p.impedimentos(edital, agora=timezone.now())) == [
        (p.IMPEDIMENTO, p.RETIFICACAO_HOMOLOGADA),
        (p.IMPEDIMENTO, p.RETIFICACAO_HOMOLOGADA),
    ]


# ---------------------------------------------------------------------------------------------
# O cancelamento (FR-3536)
# ---------------------------------------------------------------------------------------------


@pytestmark_db
def test_no_cancelamento_tudo_e_advertencia(api_client, edital):
    levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)

    achadas = p.situacoes(edital, agora=timezone.now(), ato="cancelar", com_advertencias=True)

    assert achadas and all(s.especie == p.ADVERTENCIA for s in achadas)
    assert p.RETIFICACAO_HOMOLOGADA in [s.tipo for s in achadas]
