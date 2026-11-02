"""Retificação em curso de um Edital encerrado ou cancelado (A-09, auditoria de prontidão de 31/10).

**O defeito.** Os atos da Retificação conferiam só o Processo (`ensure_processo_accepts_changes`); o
Edital, nunca. Uma Retificação homologada antes do encerramento continuava publicável depois dele,
e o Edital em estado final ganhava versão normativa nova — o contrário do que a tela de encerrar
promete ("Nenhuma Retificação poderá ser publicada depois disso") e do que a `103` já dizia: com o
Edital encerrado, "os atos continuam sendo recusados pelo servidor com a razão dele".

**A trava já existia.** `_retificacao` lê a Retificação com `select_for_update()` e
`select_related("edital__processo")`, sem `of=`; no PostgreSQL o `FOR UPDATE` sem `OF` tranca as
linhas de todas as tabelas do `FROM`, e a do Edital vem junto. O encerramento tranca a mesma linha
(`_lock_edital`). A correção é só conferir o estado sob essa trava — os casos de concorrência abaixo
provam que a conferência enxerga o encerramento confirmado por outra transação, e que o encerramento
espera a publicação que já começou.
"""

import threading
import time

import pytest
from django.db import connection, connections, transaction
from django.db.models import F
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.retificacoes import (
    _retificacao,
    edit_retification,
    publish_retification,
    transition_retification,
)
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.edital import actor_headers
from tests.fixtures.encerramento import encerrar_antes_da_113
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import publish_original
from tests.interface.test_auditoria_passagem_da_retificacao import sessao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="trava e privilégio exigem PostgreSQL"
)

ELABORADOR = Actor("ana", "cefor", frozenset({"retificacao:elaborar", "retificacao:submeter"}))
HOMOLOGADOR = Actor("bruno", "cefor", frozenset({"retificacao:homologar"}))
PUBLICADOR = Actor("carla", "cefor", frozenset({"retificacao:publicar"}))
GESTOR = Actor("gabi", "cefor", frozenset({"edital:encerrar", "edital:cancelar"}))


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def criar(api_client, edital, titulo="Título retificado"):
    base = VersaoConsolidada.objects.get(edital=edital)
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Correção",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": titulo}],
        },
        format="json",
        **actor_headers("ana", ["retificacao:elaborar"]),
    )
    assert resposta.status_code == 201, resposta.content
    return Retificacao.objects.get(pk=resposta.json()["id"])


def transitar(retificacao, acao, ator, motivo=""):
    retificacao.refresh_from_db()
    return transition_retification(
        actor=ator,
        retificacao_id=retificacao.id,
        expected_revision=retificacao.revision,
        action=acao,
        reason=motivo,
        idempotency_key=f"{acao}-{retificacao.revision}-chave-a09",
        correlation_id="a09",
    )


def levar_a(retificacao, situacao):
    if situacao in (Retificacao.Status.EM_REVISAO, Retificacao.Status.HOMOLOGADA):
        transitar(retificacao, "submeter", ELABORADOR)
    if situacao == Retificacao.Status.HOMOLOGADA:
        transitar(retificacao, "homologar", HOMOLOGADOR, "Conferida")
    retificacao.refresh_from_db()
    assert retificacao.status == situacao
    return retificacao


def publicar(retificacao, chave="publicar-chave-a09-0001"):
    retificacao.refresh_from_db()
    return publish_retification(
        actor=PUBLICADOR,
        retificacao_id=retificacao.id,
        expected_revision=retificacao.revision,
        autoridade_id=AUTORIDADE_DA_SUITE,
        idempotency_key=chave,
        correlation_id="a09",
    )


def finalizar(edital, desfecho):
    edital.refresh_from_db()
    # Encerrar com Retificação homologada é recusado desde a `113` (FR-3533). O que este arquivo
    # prova — a guarda do A-09 — continua valendo para os Editais encerrados antes dela, e é esse
    # estado que se monta aqui (`tests/fixtures/encerramento.py`).
    comando = encerrar_antes_da_113 if desfecho == Edital.Status.ENCERRADO else cancel_edital
    comando(
        actor=GESTOR,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Etapas concluídas",
        idempotency_key=f"{desfecho.lower()}-chave-a09-0001",
        correlation_id="a09",
    )
    edital.refresh_from_db()
    assert edital.status == desfecho


def retrato(edital, retificacao):
    """O que uma recusa não pode ter mudado: atos publicados, documentos, versões e trilha."""
    retificacao.refresh_from_db()
    return (
        Publicacao.objects.filter(edital=edital).count(),
        DocumentoPublicado.objects.filter(publicacao__edital=edital).count(),
        VersaoConsolidada.objects.filter(edital=edital).count(),
        RegistroAuditoria.objects.filter(aggregate_id=retificacao.id).count(),
        retificacao.status,
        retificacao.revision,
    )


def recusado(ato):
    with pytest.raises(DomainError) as exc:
        ato()
    assert (exc.value.code, exc.value.status) == ("invalid_state", 409)
    assert "Edital em estado final" in exc.value.detail


# ---------------------------------------------------------------------------------------------
# Publicação
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize("desfecho", [Edital.Status.ENCERRADO, Edital.Status.CANCELADO])
def test_retificacao_homologada_nao_se_publica_depois_do_estado_final(api_client, edital, desfecho):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    finalizar(edital, desfecho)
    antes = retrato(edital, retificacao)

    recusado(lambda: publicar(retificacao))

    assert retrato(edital, retificacao) == antes
    edital.refresh_from_db()
    assert edital.status == desfecho
    assert edital.next_publication_order == 2


def test_retificacao_homologada_de_edital_publicado_continua_publicavel(api_client, edital):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)

    publicacao, status = publicar(retificacao)

    assert status == 201
    assert publicacao.publication_order == 2
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.PUBLICADA


def test_repetir_a_publicacao_concluida_devolve_o_ato_mesmo_depois_do_encerramento(
    api_client, edital
):
    """Idempotência não é autorização: a repetição devolve o ato que já existia, e nenhum outro."""
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    revisao = retificacao.revision
    publicacao, _ = publicar(retificacao)
    finalizar(edital, Edital.Status.ENCERRADO)

    repetida, status = publish_retification(
        actor=PUBLICADOR,
        retificacao_id=retificacao.id,
        expected_revision=revisao,
        autoridade_id=AUTORIDADE_DA_SUITE,
        idempotency_key="publicar-chave-a09-0001",
        correlation_id="a09",
    )

    assert (repetida.pk, status) == (publicacao.pk, 201)
    assert Publicacao.objects.filter(edital=edital).count() == 2


# ---------------------------------------------------------------------------------------------
# Transições e edição
# ---------------------------------------------------------------------------------------------

TRANSICOES = [
    (Retificacao.Status.EM_ELABORACAO, "submeter", ELABORADOR, ""),
    (Retificacao.Status.EM_ELABORACAO, "cancelar", ELABORADOR, "Abandonada"),
    (Retificacao.Status.EM_REVISAO, "homologar", HOMOLOGADOR, "Conferida"),
    (Retificacao.Status.EM_REVISAO, "devolver", HOMOLOGADOR, "Refazer"),
    (Retificacao.Status.HOMOLOGADA, "devolver", HOMOLOGADOR, "Refazer"),
]


@pytest.mark.parametrize("desfecho", [Edital.Status.ENCERRADO, Edital.Status.CANCELADO])
@pytest.mark.parametrize(("situacao", "acao", "ator", "motivo"), TRANSICOES)
def test_transicoes_sao_recusadas_depois_do_estado_final(
    api_client, edital, desfecho, situacao, acao, ator, motivo
):
    if acao == "cancelar":
        ator = Actor("ana", "cefor", frozenset({"retificacao:cancelar"}))
    retificacao = levar_a(criar(api_client, edital), situacao)
    finalizar(edital, desfecho)
    antes = retrato(edital, retificacao)

    recusado(lambda: transitar(retificacao, acao, ator, motivo))

    assert retrato(edital, retificacao) == antes


def test_edicao_do_rascunho_e_recusada_depois_do_encerramento(api_client, edital):
    retificacao = criar(api_client, edital)
    finalizar(edital, Edital.Status.ENCERRADO)
    antes = retrato(edital, retificacao)

    recusado(
        lambda: edit_retification(
            actor=ELABORADOR,
            retificacao_id=retificacao.id,
            expected_revision=retificacao.revision,
            data={
                "baseSnapshotId": str(retificacao.base_snapshot_id),
                "justification": "Outra",
                "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Outro"}],
            },
        )
    )

    assert retrato(edital, retificacao) == antes


@pytest.mark.parametrize(("situacao", "acao", "ator", "motivo"), TRANSICOES)
def test_transicoes_seguem_valendo_antes_do_encerramento(
    api_client, edital, situacao, acao, ator, motivo
):
    if acao == "cancelar":
        ator = Actor("ana", "cefor", frozenset({"retificacao:cancelar"}))
    retificacao = levar_a(criar(api_client, edital), situacao)

    item, status = transitar(retificacao, acao, ator, motivo)

    assert status == 200
    assert item.status != situacao


# ---------------------------------------------------------------------------------------------
# Unidade e permissão: a recusa nova não muda a ordem das antigas
# ---------------------------------------------------------------------------------------------


def test_outra_unidade_continua_recebendo_404_e_nao_a_razao_do_estado(api_client, edital):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    finalizar(edital, Edital.Status.ENCERRADO)
    estranho = Actor("zeca", "outra-unidade", frozenset({"retificacao:publicar"}))

    with pytest.raises(DomainError) as exc:
        publish_retification(
            actor=estranho,
            retificacao_id=retificacao.id,
            expected_revision=retificacao.revision,
            autoridade_id=AUTORIDADE_DA_SUITE,
            idempotency_key="estranho-chave-a09-0001",
            correlation_id="a09",
        )

    assert (exc.value.code, exc.value.status) == ("not_found", 404)


def test_sem_permissao_continua_403_antes_do_estado(api_client, edital):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    finalizar(edital, Edital.Status.ENCERRADO)

    with pytest.raises(DomainError) as exc:
        publish_retification(
            actor=HOMOLOGADOR,
            retificacao_id=retificacao.id,
            expected_revision=retificacao.revision,
            autoridade_id=AUTORIDADE_DA_SUITE,
            idempotency_key="sem-permissao-chave-a09",
            correlation_id="a09",
        )

    assert exc.value.status == 403


# ---------------------------------------------------------------------------------------------
# A tela
# ---------------------------------------------------------------------------------------------


@pytest.mark.usefixtures("seletor_ligado")
def test_o_post_da_tela_responde_409_com_a_razao(api_client, edital):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    finalizar(edital, Edital.Status.ENCERRADO)
    cliente = sessao("carla.publicadora", ["publicador"])
    url = reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    confirmacao = cliente.get(url)

    resposta = cliente.post(
        url,
        {
            "chave_idempotencia": confirmacao.context["chave_idempotencia"],
            "signatario": str(AUTORIDADE_DA_SUITE),
        },
    )

    assert resposta.status_code == 409
    assert "Edital em estado final não admite alteração." in resposta.content.decode()
    assert Publicacao.objects.filter(edital=edital).count() == 1


# ---------------------------------------------------------------------------------------------
# Privilégios de produção e concorrência
# ---------------------------------------------------------------------------------------------


@postgresql_only
def test_a_leitura_da_retificacao_tranca_a_linha_do_edital(api_client, edital):
    """A premissa da correção: o `FOR UPDATE` da leitura não leva `OF`, e alcança o Edital."""
    retificacao = criar(api_client, edital)
    with transaction.atomic(), CaptureQueriesContext(connection) as consultas:
        _retificacao(ELABORADOR, retificacao.id)
    sql = next(q["sql"] for q in consultas.captured_queries if "FOR UPDATE" in q["sql"])
    assert '"processos_edital"' in sql
    assert sql.rstrip().endswith("FOR UPDATE")


@postgresql_only
def test_a_recusa_cabe_nos_privilegios_de_producao(
    api_client,
    edital,
    como_producao,  # noqa: F811
):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    finalizar(edital, Edital.Status.ENCERRADO)

    with como_producao():
        recusado(lambda: publicar(retificacao))

    assert Publicacao.objects.filter(edital=edital).count() == 1


@postgresql_only
def test_a_publicacao_cabe_nos_privilegios_de_producao(
    api_client,
    edital,
    como_producao,  # noqa: F811
):
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)

    with como_producao():
        _, status = publicar(retificacao)

    assert status == 201


@postgresql_only
def test_encerramento_primeiro_a_publicacao_espera_e_recusa(api_client, edital):
    """O encerramento tranca o Edital e confirma; a publicação, que esperava, vê o estado final.

    Sem a trava, a publicação leria o Edital ainda publicado — a janela entre conferir e gravar que
    uma conferência fora da transação deixaria aberta.
    """
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    trancado = threading.Event()
    falhas = []

    def encerrar_segurando_a_trava():
        try:
            with transaction.atomic():
                Edital.objects.select_for_update().get(pk=edital.id)
                trancado.set()
                time.sleep(0.5)
                Edital.objects.filter(pk=edital.id).update(
                    status=Edital.Status.ENCERRADO, revision=F("revision") + 1
                )
        except Exception as exc:  # noqa: BLE001 — repassado para o corpo do teste
            falhas.append(exc)
        finally:
            connections.close_all()

    linha = threading.Thread(target=encerrar_segurando_a_trava)
    linha.start()
    assert trancado.wait(timeout=5)

    inicio = time.monotonic()
    recusado(lambda: publicar(retificacao))
    esperou = time.monotonic() - inicio

    linha.join(timeout=10)
    assert not falhas, falhas
    assert esperou >= 0.2, "a publicação não esperou a trava do Edital"
    assert Publicacao.objects.filter(edital=edital).count() == 1
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.HOMOLOGADA


@postgresql_only
def test_publicacao_primeiro_o_encerramento_espera_e_conclui(api_client, edital, monkeypatch):
    """A publicação já começou e segura o Edital; o encerramento espera e conclui depois dela.

    A publicação legitimamente iniciada termina, e o Edital se encerra com ela publicada — a ordem
    em que os dois atos aparecem na trilha é a ordem em que aconteceram.
    """
    from processo_seletivo.publicacoes.application import retificacoes

    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    trancado = threading.Event()
    original = retificacoes._materialize_affected_versions

    def materializar_devagar(*args, **kwargs):
        trancado.set()
        time.sleep(0.5)
        return original(*args, **kwargs)

    monkeypatch.setattr(retificacoes, "_materialize_affected_versions", materializar_devagar)
    resultado = []

    def publicar_em_paralelo():
        try:
            resultado.append(publicar(retificacao)[1])
        except Exception as exc:  # noqa: BLE001 — repassado para o corpo do teste
            resultado.append(exc)
        finally:
            connections.close_all()

    linha = threading.Thread(target=publicar_em_paralelo)
    linha.start()
    assert trancado.wait(timeout=30)

    inicio = time.monotonic()
    edital_antes = Edital.objects.get(pk=edital.id)
    close_edital(
        actor=GESTOR,
        edital_id=edital.id,
        expected_revision=edital_antes.revision,
        reason="Etapas concluídas",
        idempotency_key="encerrar-chave-a09-corrida",
        correlation_id="a09",
    )
    esperou = time.monotonic() - inicio

    linha.join(timeout=30)
    assert resultado == [201], resultado
    assert esperou >= 0.2, "o encerramento não esperou a publicação em curso"
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO
    assert Publicacao.objects.filter(edital=edital).count() == 2
