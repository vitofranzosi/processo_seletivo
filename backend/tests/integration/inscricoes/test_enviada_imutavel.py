"""A Inscrição enviada e os documentos dela, imutáveis no banco (A-03; `inscricoes/0007`).

Antes da `0007`, só `Inscricao.save` e `DocumentoSubmetido.save/delete` recusavam: como a role de
produção, um `QuerySet.update()` ou um `UPDATE` cru reescrevia nome, CPF, Modalidade e status da
enviada. Estes casos mostram as duas metades: o que passou a ser recusado, e o que continua
passando — rascunho, anexo, substituição, remoção e o próprio envio —, tudo **como a role de
produção**, porque é ela que os gatilhos precisam deixar trabalhar.

A corrida entre o envio e uma escrita de documento é exercitada nas duas ordens, com a mesma
conferência: nenhum documento muda depois do envio, e nenhuma das duas trava a outra para sempre.
"""

import threading
import time

import pytest
from django.db import DatabaseError, connection, connections, transaction
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    anexar_documento,
    gravar_dados,
    remover_documento,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, pdf
from tests.fixtures.comissao import anexar
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(connection.vendor != "postgresql", reason="os gatilhos são do PostgreSQL"),
]

DECLARACOES = {"veracidade": True, "ciencia": True}
ENVIADA = "submitted enrollment"


def _preenchida(inscricao, *, documentos=(DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL)):
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao,
        dados={
            "nome": MARIA.nome,
            "cpf": MARIA.cpf,
            "email": MARIA.email,
            "modality_id": MODALIDADE_AC,
        },
    )
    for requisito in documentos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao, chave="envio-a03"):
    return enviar_inscricao(
        identidade=MARIA, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key=chave
    )


def _documento_cru(inscricao, requisito):
    """Um documento gravado por fora do comando — `bulk_create` não passa por `save`."""
    return DocumentoSubmetido(
        inscricao_id=inscricao.pk,
        requirement_id=requisito,
        arquivo=f"inscricoes/{inscricao.pk}/por-fora.pdf",
        nome_original="por-fora.pdf",
        tamanho=10,
        content_hash="0" * 64,
        uploaded_at=timezone.now(),
    )


@pytest.fixture
def enviada(inscricao_de_maria):
    return _enviar(_preenchida(inscricao_de_maria))


# ---------------------------------------------------------------------------
# O que continua passando
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_rascunho_anexo_substituicao_remocao_e_envio_passam_como_producao(
    inscricao_de_maria,
    como_producao,  # noqa: F811
):
    with como_producao():
        rascunho = _preenchida(inscricao_de_maria, documentos=(DOCUMENTO_DE_TODOS,))
        rascunho = gravar_dados(
            identidade=MARIA,
            inscricao=rascunho,
            dados={"modality_id": MODALIDADE_AC, "telefone": "(27) 99999-0000"},
        )
        anexar_documento(
            identidade=MARIA,
            inscricao=rascunho,
            requirement_id=DOCUMENTO_DO_PERFIL,
            arquivo=pdf("primeiro.pdf"),
        )
        # Substituir é sobrescrever o registro do mesmo requisito (FR-043).
        anexar_documento(
            identidade=MARIA,
            inscricao=rascunho,
            requirement_id=DOCUMENTO_DO_PERFIL,
            arquivo=pdf("segundo.pdf"),
        )
        remover_documento(identidade=MARIA, inscricao=rascunho, requirement_id=DOCUMENTO_DE_TODOS)
        anexar_documento(
            identidade=MARIA,
            inscricao=rascunho,
            requirement_id=DOCUMENTO_DE_TODOS,
            arquivo=pdf("rg.pdf"),
        )
        rascunho.refresh_from_db()
        registro = _enviar(rascunho)

    assert registro.status == Inscricao.Status.SUBMETIDA
    assert registro.telefone == "(27) 99999-0000"
    nomes = set(
        DocumentoSubmetido.objects.filter(inscricao=registro).values_list(
            "nome_original", flat=True
        )
    )
    assert nomes == {"segundo.pdf", "rg.pdf"}


# ---------------------------------------------------------------------------
# A Inscrição enviada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "campos",
    [
        {"nome": "Outra Pessoa"},
        {"cpf": "000.000.000-00", "cpf_normalizado": "00000000000"},
        {"email": "outra@exemplo.test"},
        {"modality_id": None},
        {"profile_id": "00000000-0000-0000-0000-000000000999"},
        {"submitted_at": timezone.now()},
    ],
    ids=["nome", "cpf", "email", "modalidade", "perfil", "instante"],
)
def test_a_enviada_nao_muda_pelo_queryset(enviada, como_producao, campos):  # noqa: F811
    antes = Inscricao.objects.values().get(pk=enviada.pk)

    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        Inscricao.objects.filter(pk=enviada.pk).update(**campos)

    assert Inscricao.objects.values().get(pk=enviada.pk) == antes


@pytest.mark.django_db
def test_a_enviada_nao_volta_a_rascunho(enviada, como_producao):  # noqa: F811
    """Devolver a `RASCUNHO` sem nome, CPF e e-mail passava — e reabria a inscrição inteira."""
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        Inscricao.objects.filter(pk=enviada.pk).update(
            status=Inscricao.Status.RASCUNHO,
            protocolo="",
            submitted_at=None,
            versao_aceita=None,
            declaracoes_aceitas_em=None,
        )

    assert Inscricao.objects.get(pk=enviada.pk).status == Inscricao.Status.SUBMETIDA


@pytest.mark.django_db
@pytest.mark.parametrize(
    "comando",
    [
        "UPDATE inscricoes_inscricao SET nome = 'Outra' WHERE id = %s",
        "UPDATE inscricoes_inscricao SET status = 'RASCUNHO' WHERE id = %s",
        "DELETE FROM inscricoes_inscricao WHERE id = %s",
    ],
    ids=["nome", "status", "exclusao"],
)
def test_a_enviada_nao_muda_por_sql(enviada, como_producao, comando):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(comando, [enviada.pk])


@pytest.mark.django_db
def test_o_rascunho_continua_mudando_pelo_queryset(inscricao_de_maria, como_producao):  # noqa: F811
    """O gatilho é condicional: a mesma escrita que a enviada recusa, o rascunho aceita."""
    with como_producao():
        Inscricao.objects.filter(pk=inscricao_de_maria.pk).update(nome="Maria Rascunho")

    assert Inscricao.objects.get(pk=inscricao_de_maria.pk).nome == "Maria Rascunho"


# ---------------------------------------------------------------------------
# Os documentos da enviada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_documento_da_enviada_nao_muda_pelo_queryset(enviada, como_producao):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        DocumentoSubmetido.objects.filter(inscricao=enviada).update(nome_original="trocado.pdf")


@pytest.mark.django_db
def test_documento_da_enviada_nao_sai_pelo_queryset(enviada, como_producao):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        DocumentoSubmetido.objects.filter(inscricao=enviada).delete()

    assert DocumentoSubmetido.objects.filter(inscricao=enviada).count() == 2


@pytest.mark.django_db
def test_documento_nao_entra_na_enviada(enviada, como_producao):  # noqa: F811
    """Acrescentar muda o que a comissão abre tanto quanto substituir."""
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        DocumentoSubmetido.objects.bulk_create(
            [_documento_cru(enviada, "00000000-0000-0000-0000-00000000a003")]
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "comando",
    [
        "UPDATE inscricoes_documentosubmetido SET content_hash = repeat('f', 64) "
        "WHERE inscricao_id = %s",
        "DELETE FROM inscricoes_documentosubmetido WHERE inscricao_id = %s",
    ],
    ids=["resumo", "exclusao"],
)
def test_documento_da_enviada_nao_muda_por_sql(enviada, como_producao, comando):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(comando, [enviada.pk])


@pytest.mark.django_db
def test_documento_nao_se_muda_para_a_enviada(enviada, selecao, como_producao):  # noqa: F811
    """O gatilho olha `OLD` **e** `NEW`: mover um documento de rascunho para a enviada também muda
    o que a comissão abre."""
    outra = Inscricao.objects.create(
        created_at=timezone.now(),
        identity_subject="cand:outra-a03",
        edital=selecao,
        profile_id=PERFIL_DOCENTE,
    )
    DocumentoSubmetido.objects.bulk_create(
        [_documento_cru(outra, "00000000-0000-0000-0000-00000000a003")]
    )

    with como_producao(), pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        DocumentoSubmetido.objects.filter(inscricao=outra).update(inscricao=enviada)


# ---------------------------------------------------------------------------
# A corrida entre o envio e uma escrita de documento
# ---------------------------------------------------------------------------


def _esperar_a_trava(pid, *, prazo=10):
    """Até a outra conexão estar **esperando** uma trava — `pg_locks` é lido ao vivo.

    `pg_stat_activity` não serve aqui: dentro de uma transação ele devolve sempre a mesma foto.
    """
    limite = time.monotonic() + prazo
    while time.monotonic() < limite:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_locks WHERE pid = %s AND NOT granted", [pid])
            if cursor.fetchone():
                return
        time.sleep(0.05)
    raise AssertionError("a outra conexão não chegou a esperar a trava")


def _pid():
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_backend_pid()")
        return cursor.fetchone()[0]


@pytest.mark.django_db(transaction=True)
def test_escrita_que_chega_durante_o_envio_espera_e_e_recusada(
    inscricao_de_maria,
    como_producao,  # noqa: F811
):
    """O envio primeiro: a escrita por fora espera o `FOR SHARE`, relê `SUBMETIDA` e recusa.

    Sem o `FOR SHARE`, a trava da chave estrangeira não conflitaria com o `UPDATE` do envio, e o
    documento entraria na inscrição que acabou de ser enviada — sem que o envio o tivesse visto.
    """
    rascunho = _preenchida(inscricao_de_maria)
    pronto = threading.Event()
    desfecho = {}

    def escrever_por_fora():
        try:
            desfecho["pid"] = _pid()
            pronto.set()
            with como_producao():
                DocumentoSubmetido.objects.bulk_create(
                    [_documento_cru(rascunho, "00000000-0000-0000-0000-00000000a003")]
                )
            desfecho["escrita"] = "gravada"
        except DatabaseError as exc:
            desfecho["escrita"] = str(exc)
        finally:
            connections.close_all()

    fio = threading.Thread(target=escrever_por_fora)
    with transaction.atomic():
        _enviar(rascunho)
        fio.start()
        assert pronto.wait(10)
        _esperar_a_trava(desfecho["pid"])
    fio.join(timeout=30)

    assert not fio.is_alive(), "a escrita ficou presa depois do envio"
    assert "documents of a submitted enrollment are immutable" in desfecho["escrita"], desfecho
    assert DocumentoSubmetido.objects.filter(inscricao=rascunho).count() == 2


@pytest.mark.django_db(transaction=True)
def test_envio_que_chega_durante_a_escrita_espera_e_ve_o_documento(
    inscricao_de_maria,
    como_producao,  # noqa: F811
):
    """A escrita primeiro: o envio espera o `FOR SHARE` dela e confere o que ela gravou.

    O diploma falta ao rascunho e é a escrita concorrente que o grava. O envio só passa porque o
    lê depois de esperar — e passa sem impasse, porque os dois disputam uma linha só.
    """
    rascunho = _preenchida(inscricao_de_maria, documentos=(DOCUMENTO_DE_TODOS,))
    pronto = threading.Event()
    desfecho = {}

    def enviar():
        try:
            desfecho["pid"] = _pid()
            pronto.set()
            desfecho["envio"] = _enviar(rascunho, "envio-a03-corrida").status
        except Exception as exc:  # noqa: BLE001 — o desfecho é conferido abaixo, qualquer que seja
            desfecho["envio"] = repr(exc)
        finally:
            connections.close_all()

    fio = threading.Thread(target=enviar)
    with como_producao(), transaction.atomic():
        # Com arquivo de verdade, e não `_documento_cru`: o envio confere o resumo do que leu.
        anexar(rascunho, DOCUMENTO_DO_PERFIL)
        fio.start()
        assert pronto.wait(10)
        _esperar_a_trava(desfecho["pid"])
    fio.join(timeout=30)

    assert not fio.is_alive(), "o envio ficou preso depois da escrita"
    assert desfecho["envio"] == Inscricao.Status.SUBMETIDA, desfecho
    assert DocumentoSubmetido.objects.filter(inscricao=rascunho).count() == 2


@pytest.mark.django_db
def test_o_desvio_dos_testes_religa_os_gatilhos(enviada):
    """`sem_imutabilidade_da_enviada` vale só pelo bloco: depois dele, a recusa volta."""
    from tests.fixtures.comissao import sem_imutabilidade_da_enviada

    with sem_imutabilidade_da_enviada():
        Inscricao.objects.filter(pk=enviada.pk).update(telefone="(27) 3333-0000")

    with pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        Inscricao.objects.filter(pk=enviada.pk).update(telefone="(27) 4444-0000")
    with pytest.raises(DatabaseError, match=ENVIADA), transaction.atomic():
        DocumentoSubmetido.objects.filter(inscricao=enviada).update(nome_original="x.pdf")
