"""A Avaliação concluída, imutável no banco salvo a reabertura (A-03; `avaliacoes/0004`).

Como a role de produção, `UPDATE avaliacoes_avaliacao SET pontuacao = pontuacao + 10` passava sobre
as concluídas. O gatilho admite **uma** transição a partir de `CONCLUIDA` — a forma exata da
reabertura —, e estes casos cobrem os dois lados: a reabertura pela presidência continua
funcionando e preservando a conclusão anterior; qualquer outra escrita, inclusive uma "reabertura"
que leve a nota junto, é recusada.

**O que eles não afirmam**: que o banco autentica quem reabre. Um `UPDATE` cru que reproduza a
forma da reabertura passa — o último caso o registra. A autorização da presidência, o motivo e a
trilha são da aplicação.
"""

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.skipif(connection.vendor != "postgresql", reason="os gatilhos são do PostgreSQL"),
]

CONCLUIDA = "concluded evaluations are immutable"
MOTIVO = "Erro material: a nota lançada não é a da ficha."


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=30, codigo="A3")


@pytest.fixture
def concluida(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=3000)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    return concluir_como(cenario, "joao", inscricao, pontuacao="60", parecer="Insuficiente")


def _reabrir(gestor, cenario, avaliacao, chave="reabrir-a03"):
    return reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo=MOTIVO,
        expected_revision=avaliacao.revision,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_concluir_e_reabrir_passam_como_producao(cenario, gestor, como_producao):  # noqa: F811
    """O ciclo inteiro sob a role: concluir, reabrir pela presidência e concluir de novo."""
    inscricao = inscricoes_de(cenario, 1, primeiro=3100)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao])
    with como_producao():
        concluida = concluir_como(cenario, "joao", inscricao, pontuacao="60", parecer="Antes")
        reaberta = _reabrir(gestor, cenario, concluida)
        de_novo = concluir_como(
            cenario, "joao", inscricao, pontuacao="75", parecer="Depois", revisao=reaberta.revision
        )

    assert reaberta.estado == Avaliacao.Estado.RASCUNHO
    assert de_novo.estado == Avaliacao.Estado.CONCLUIDA
    assert str(de_novo.pontuacao) == "75.0000"
    preservadas = list(ConclusaoAvaliacao.objects.filter(avaliacao=de_novo).order_by("ordem"))
    assert [(str(item.pontuacao), item.parecer) for item in preservadas] == [
        ("60.0000", "Antes"),
        ("75.0000", "Depois"),
    ]


def test_a_reabertura_preserva_o_conteudo_e_so_zera_a_conclusao(cenario, gestor, concluida):
    """O rascunho reaberto parte do que foi concluído; o que a governou fica no histórico."""
    reaberta = _reabrir(gestor, cenario, concluida)

    assert str(reaberta.pontuacao) == "60.0000"
    assert reaberta.parecer == "Insuficiente"
    assert (reaberta.concluida_em, reaberta.concluida_por, reaberta.versao_id) == (None, "", None)
    preservada = ConclusaoAvaliacao.objects.get(avaliacao=concluida)
    assert (str(preservada.pontuacao), preservada.concluida_por) == ("60.0000", "joao")
    assert preservada.versao_id == concluida.versao_id


@pytest.mark.parametrize(
    "campos",
    [
        {"pontuacao": "99"},
        {"parecer": "Reescrito"},
        {"concluida_por": "outra-pessoa"},
        {"identity_subject": "outra-pessoa"},
    ],
    ids=["nota", "parecer", "autoria", "avaliador"],
)
def test_a_concluida_nao_muda_pelo_queryset(concluida, como_producao, campos):  # noqa: F811
    antes = Avaliacao.objects.values().get(pk=concluida.pk)

    with como_producao(), pytest.raises(DatabaseError, match=CONCLUIDA), transaction.atomic():
        Avaliacao.objects.filter(pk=concluida.pk).update(**campos)

    assert Avaliacao.objects.values().get(pk=concluida.pk) == antes


@pytest.mark.parametrize(
    "extra",
    [{"pontuacao": "99"}, {"parecer": "Reescrito"}, {"forma": "DECISORIA", "pontuacao": None}],
    ids=["nota", "parecer", "forma"],
)
def test_reabertura_que_leva_conteudo_junto_e_recusada(concluida, como_producao, extra):  # noqa: F811
    """A forma da reabertura com mais uma coluna mudada não é reabertura: é reescrita."""
    from django.db.models import F

    with como_producao(), pytest.raises(DatabaseError, match=CONCLUIDA), transaction.atomic():
        Avaliacao.objects.filter(pk=concluida.pk).update(
            estado=Avaliacao.Estado.RASCUNHO,
            concluida_em=None,
            concluida_por="",
            versao=None,
            revision=F("revision") + 1,
            **extra,
        )


def test_a_concluida_nao_se_exclui(concluida, como_producao):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=CONCLUIDA), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM avaliacoes_avaliacao WHERE id = %s", [concluida.pk])


def test_a_concluida_nao_muda_por_sql(concluida, como_producao):  # noqa: F811
    with como_producao(), pytest.raises(DatabaseError, match=CONCLUIDA), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE avaliacoes_avaliacao SET pontuacao = pontuacao + 10 WHERE id = %s",
                [concluida.pk],
            )


def test_o_limite_o_banco_nao_autentica_quem_reabre(concluida, como_producao):  # noqa: F811
    """Registrado, e não escondido: a forma exata da reabertura passa por SQL cru.

    O gatilho garante que nenhuma escrita reescreve o **conteúdo** de uma conclusão; quem pode
    reabrir é decisão da aplicação (FR-036), que exige a presidência, o motivo e grava o ato. Se
    este caso falhar porque o banco passou a recusar, a garantia mudou — e a docstring da
    `avaliacoes/0004` precisa mudar junto.
    """
    with como_producao(), connection.cursor() as cursor:
        cursor.execute(
            "UPDATE avaliacoes_avaliacao SET estado = 'RASCUNHO', concluida_em = NULL, "
            "concluida_por = '', versao_id = NULL, revision = revision + 1 WHERE id = %s",
            [concluida.pk],
        )

    reaberta = Avaliacao.objects.get(pk=concluida.pk)
    assert reaberta.estado == Avaliacao.Estado.RASCUNHO
    assert str(reaberta.pontuacao) == "60.0000", "o conteúdo atravessou intacto"
    assert ConclusaoAvaliacao.objects.filter(avaliacao=concluida).count() == 1
