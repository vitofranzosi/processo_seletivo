"""FR-023 da 003 — a imutabilidade do histórico normativo não depende da aplicação.

`Retificacao` e `AlteracaoNormativa` mudam legitimamente enquanto o ato está em curso, então a
trigger é condicional ao estado final. `AtoAdministrativo` e `RevisaoEdital` nascem imutáveis e a
trigger é absoluta. Cada teste ataca pelo caminho que a aplicação não fiscaliza — `update()` e
`delete()` diretos no QuerySet —, que é como o histórico seria reescrito sem querer.
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.publicacoes.models import RevisaoEdital
from processo_seletivo.publicacoes.models_retificacao import AlteracaoNormativa, Retificacao
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="triggers de imutabilidade exigem PostgreSQL"
)
pytestmark = [pytest.mark.integration, postgresql_only]

ALTERACAO = [{"targetPath": caminho_perfil("name"), "operation": "REPLACE", "newValue": "Outro"}]


@pytest.fixture
def retificacao_publicada(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    return publish_retification(
        api_client, create_retification(api_client, edital, ALTERACAO), suffix="a"
    )


@pytest.mark.django_db(transaction=True)
def test_retificacao_publicada_nao_pode_ser_alterada(retificacao_publicada):
    with pytest.raises(DatabaseError, match="final state are immutable"), transaction.atomic():
        Retificacao.objects.filter(pk=retificacao_publicada.pk).update(
            justification="Reescrita indevida"
        )


@pytest.mark.django_db(transaction=True)
def test_retificacao_publicada_nao_pode_ser_apagada(retificacao_publicada):
    # O ORM apaga as Alterações em cascata primeiro, então a recusa vem da trigger delas — o que
    # importa é que nenhum dos dois caminhos leve o registro embora.
    with pytest.raises(DatabaseError, match="immutable"), transaction.atomic():
        Retificacao.objects.filter(pk=retificacao_publicada.pk).delete()
    assert Retificacao.objects.filter(pk=retificacao_publicada.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_alteracoes_de_retificacao_publicada_nao_podem_ser_alteradas(retificacao_publicada):
    recusa = pytest.raises(DatabaseError, match="final retification are immutable")
    with recusa, transaction.atomic():
        AlteracaoNormativa.objects.filter(retificacao=retificacao_publicada).update(
            new_value="Conteúdo trocado depois da Publicação"
        )


@pytest.mark.django_db(transaction=True)
def test_alteracoes_de_retificacao_publicada_nao_podem_ser_apagadas(retificacao_publicada):
    recusa = pytest.raises(DatabaseError, match="final retification are immutable")
    with recusa, transaction.atomic():
        AlteracaoNormativa.objects.filter(retificacao=retificacao_publicada).delete()


@pytest.mark.django_db(transaction=True)
def test_retificacao_cancelada_tambem_e_final(api_client, manager_headers, process_payload):
    """Cancelada preserva o registro do que se pretendeu e não pode ser reescrita depois."""
    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(api_client, edital, ALTERACAO)
    Retificacao.objects.filter(pk=retificacao.pk).update(status=Retificacao.Status.CANCELADA)

    with pytest.raises(DatabaseError, match="final state are immutable"), transaction.atomic():
        Retificacao.objects.filter(pk=retificacao.pk).update(justification="Depois do fim")


@pytest.mark.django_db(transaction=True)
def test_ato_administrativo_e_append_only(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    api_client.post(
        f"/api/v1/admin/processos/{edital.processo_id}/ativacoes",
        {"reason": "Abertura formal"},
        format="json",
        **{
            **manager_headers,
            "HTTP_IF_MATCH": f'"{edital.processo.revision}"',
            "HTTP_IDEMPOTENCY_KEY": "imutabilidade-ativacao-1",
        },
    )
    ato = AtoAdministrativo.objects.get()

    with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
        AtoAdministrativo.objects.filter(pk=ato.pk).update(reason="Outro motivo")


@pytest.mark.django_db(transaction=True)
def test_revisao_de_edital_e_append_only(api_client, manager_headers, process_payload):
    publish_original(api_client, manager_headers, process_payload)
    revisao = RevisaoEdital.objects.get()

    with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
        RevisaoEdital.objects.filter(pk=revisao.pk).update(prepared_by="outra-pessoa")


@pytest.mark.django_db(transaction=True)
def test_o_ciclo_em_curso_nao_e_bloqueado(api_client, manager_headers, process_payload):
    """A trigger não pode congelar o que ainda está sendo elaborado.

    Percorre elaborar, reeditar o rascunho — que apaga e recria as Alterações —, submeter,
    devolver, submeter de novo, homologar e publicar. Qualquer bloqueio indevido aparece aqui,
    e não em produção no meio de um ato.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.edital import actor_headers
    from tests.fixtures.publicacao import SIGNATORY

    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.get(edital=edital)
    retificacao = create_retification(api_client, edital, ALTERACAO)
    raiz = f"/api/v1/admin/retificacoes/{retificacao.id}"

    reeditada = api_client.put(
        f"{raiz}/rascunho",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Revisada antes de submeter",
            "changes": [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Outro"}],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], if_match=1),
    )
    assert reeditada.status_code == 200, reeditada.content

    def ato(caminho, corpo, subject, permissao, revision, key):
        return api_client.post(
            f"{raiz}/{caminho}",
            corpo,
            format="json",
            **actor_headers(subject, [permissao], if_match=revision, key=key),
        )

    passos = [
        ("submissoes", {}, "retificador", "retificacao:submeter", 2, "ciclo-submissao-01", 200),
        (
            "devolucoes",
            {"reason": "Corrigir"},
            "homologador",
            "retificacao:homologar",
            3,
            "ciclo-devolucao-02",
            200,
        ),
        ("submissoes", {}, "retificador", "retificacao:submeter", 4, "ciclo-submissao-03", 200),
        (
            "homologacoes",
            {"reason": "OK"},
            "homologador",
            "retificacao:homologar",
            5,
            "ciclo-homologacao-4",
            200,
        ),
        (
            "publicacoes",
            {"signatory": SIGNATORY},
            "publicador",
            "retificacao:publicar",
            6,
            "ciclo-publicacao-05",
            201,
        ),
    ]
    for caminho, corpo, subject, permissao, revision, key, esperado in passos:
        resposta = ato(caminho, corpo, subject, permissao, revision, key)
        assert resposta.status_code == esperado, (caminho, resposta.content)
    assert Retificacao.objects.get(pk=retificacao.pk).status == Retificacao.Status.PUBLICADA


@pytest.mark.django_db(transaction=True)
def test_alteracao_de_retificacao_em_curso_persiste_de_verdade(
    api_client, manager_headers, process_payload
):
    """Regressão da trigger que devolvia OLD num BEFORE UPDATE.

    Recusar é o comportamento correto para estado final; devolver a linha antiga descartaria a
    alteração legítima em silêncio, que é pior do que não ter trigger nenhuma — o `UPDATE`
    responderia sucesso e nada teria mudado.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(api_client, edital, ALTERACAO)

    AlteracaoNormativa.objects.filter(retificacao=retificacao).update(new_value="Persistido")

    assert AlteracaoNormativa.objects.get(retificacao=retificacao).new_value == "Persistido"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_tabelas_append_only_sao_exatamente_as_que_recusam_mutacao_no_modelo():
    """FR-048 e a régua da `006`: coleção nova não pode entrar por engano no histórico.

    A lista de `papeis.py` governa privilégios e triggers em produção; a recusa no modelo governa
    o processo em execução. Uma tabela em uma e não na outra é defesa pela metade — e é o modo de
    falha que uma feature que acrescenta modelos torna provável, em qualquer direção: um modelo
    novo de histórico que não recebe privilégio restrito, ou uma tabela editável que é declarada
    append-only e passa a recusar a própria gravação.

    `EtapaAvaliacao` e `SecaoEdital` nasceram nesta feature e são conteúdo em elaboração: são
    apagadas e recriadas a cada gravação do rascunho, e não podem estar aqui.
    """
    from django.apps import apps

    from processo_seletivo.editais.models.etapas import EtapaAvaliacao
    from processo_seletivo.editais.models.secoes import SecaoEdital
    from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY

    recusam_no_modelo = {
        modelo._meta.db_table for modelo in apps.get_models() if _recusa_mutacao(modelo)
    }

    # Toda recusa em código tem privilégio restrito. A volta não vale: `RevisaoEdital` é
    # append-only pela trigger e não sobrescreve `delete`, e essa assimetria é anterior a esta
    # feature — declará-la aqui como erro seria mudar uma decisão que não é desta spec.
    assert recusam_no_modelo <= set(TABELAS_APPEND_ONLY), sorted(
        recusam_no_modelo - set(TABELAS_APPEND_ONLY)
    )

    nascidas_na_006 = {EtapaAvaliacao._meta.db_table, SecaoEdital._meta.db_table}
    assert nascidas_na_006.isdisjoint(TABELAS_APPEND_ONLY)
    assert nascidas_na_006.isdisjoint(recusam_no_modelo)


def _recusa_mutacao(modelo):
    """O modelo sobrescreve `delete` para recusar? É a marca de append-only neste repositório."""
    import inspect

    try:
        fonte = inspect.getsource(modelo.delete)
    except (OSError, TypeError):
        return False
    return "append-only" in fonte
