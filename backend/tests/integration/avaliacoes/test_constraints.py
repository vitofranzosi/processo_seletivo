"""As garantias que moram no banco, e não na tela que grava.

Três, e cada uma protege uma promessa diferente:

- a **unicidade parcial** da Atribuição ativa: redistribuir depois de remover cria linha nova, e o
  histórico permanece (FR-003);
- o **índice único parcial** da conclusão: no máximo uma por pessoa, inscrição e Etapa — a
  invariante que impede a 013 de contar duas vezes, e que cai se for ancorada no vínculo (FR-074);
- a **trigger** da conclusão preservada: reabrir não destrói o que foi concluído, inclusive para
  quem chegue por fora da aplicação (FR-094).

Marcados `postgresql_only` porque é disso que se trata: em SQLite a trigger não existe, e o teste
que a exercita passaria sem exercitar nada.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, ConclusaoAvaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import constituir

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a garantia é do banco, e exige PostgreSQL"
)
pytestmark = [pytest.mark.django_db, pytest.mark.integration, postgresql_only]


@pytest.fixture
def inscricao(edital_a):
    return Inscricao.objects.create(
        created_at=timezone.now(),
        identity_subject="cpf:11144477735",
        edital=edital_a,
        profile_id="00000000-0000-0000-0000-000000000401",
        nome="Candidata Fulana",
        cpf="111.444.777-35",
        cpf_normalizado="11144477735",
        email="fulana@exemplo.br",
    )


@pytest.fixture
def membro(gestor, processo_a):
    return constituir(gestor, processo_a, [("joao", Funcao.MEMBRO)])["joao"]


def atribuir(membro, edital, etapa_id, inscricao, *, ativo=True):
    agora = timezone.now()
    return Atribuicao.objects.create(
        membro=membro,
        edital=edital,
        etapa_id=etapa_id,
        inscricao=inscricao,
        ativo=ativo,
        criado_em=agora,
        criado_por="presidente",
        inativado_em=None if ativo else agora,
        inativado_por="" if ativo else "presidente",
    )


def concluir(atribuicao, versao, *, identity="joao"):
    return Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject=identity,
        etapa_id=atribuicao.etapa_id,
        inscricao_id=atribuicao.inscricao_id,
        estado=Avaliacao.Estado.CONCLUIDA,
        pontuacao=Decimal("80.0000"),
        parecer="Atende",
        versao=versao,
        concluida_em=timezone.now(),
        concluida_por=identity,
    )


@pytest.fixture
def versao(edital_a):
    return VersaoConsolidada.objects.filter(edital=edital_a).latest("materialized_at")


def test_a_atribuicao_ativa_e_unica(membro, edital_a, etapa_a1, inscricao):
    atribuir(membro, edital_a, etapa_a1, inscricao)

    with pytest.raises(IntegrityError), transaction.atomic():
        atribuir(membro, edital_a, etapa_a1, inscricao)


def test_a_unicidade_e_parcial_e_o_historico_permanece(membro, edital_a, etapa_a1, inscricao):
    """Remover é inativar; redistribuir cria linha nova. As duas convivem."""
    atribuir(membro, edital_a, etapa_a1, inscricao, ativo=False)

    atribuir(membro, edital_a, etapa_a1, inscricao)

    assert Atribuicao.objects.filter(inscricao=inscricao).count() == 2


def test_uma_conclusao_por_pessoa_inscricao_e_etapa(membro, edital_a, etapa_a1, inscricao, versao):
    """O contorno que a restrição fecha: remover, reatribuir e concluir de novo.

    A âncora é a **identidade estável**, e não o vínculo — se fosse o vínculo, remover a pessoa da
    comissão e readicioná-la liberaria a segunda conclusão (FR-074).
    """
    primeira = atribuir(membro, edital_a, etapa_a1, inscricao)
    concluir(primeira, versao)
    Atribuicao.objects.filter(pk=primeira.pk).update(
        ativo=False, inativado_em=timezone.now(), inativado_por="presidente"
    )
    segunda = atribuir(membro, edital_a, etapa_a1, inscricao)

    with pytest.raises(IntegrityError), transaction.atomic():
        concluir(segunda, versao)


def test_rascunho_nao_disputa_a_unicidade(membro, edital_a, etapa_a1, inscricao, versao):
    """A restrição é parcial: dois rascunhos convivem, e é a conclusão que é única."""
    primeira = atribuir(membro, edital_a, etapa_a1, inscricao)
    Avaliacao.objects.create(
        atribuicao=primeira,
        identity_subject="joao",
        etapa_id=etapa_a1,
        inscricao_id=inscricao.id,
    )
    Atribuicao.objects.filter(pk=primeira.pk).update(
        ativo=False, inativado_em=timezone.now(), inativado_por="presidente"
    )
    segunda = atribuir(membro, edital_a, etapa_a1, inscricao)

    Avaliacao.objects.create(
        atribuicao=segunda,
        identity_subject="joao",
        etapa_id=etapa_a1,
        inscricao_id=inscricao.id,
    )

    assert Avaliacao.objects.filter(inscricao_id=inscricao.id).count() == 2


def test_concluida_sem_pontuacao_nao_e_alcancavel(membro, edital_a, etapa_a1, inscricao):
    atribuicao = atribuir(membro, edital_a, etapa_a1, inscricao)

    with pytest.raises(IntegrityError), transaction.atomic():
        Avaliacao.objects.create(
            atribuicao=atribuicao,
            identity_subject="joao",
            etapa_id=etapa_a1,
            inscricao_id=inscricao.id,
            estado=Avaliacao.Estado.CONCLUIDA,
            concluida_em=timezone.now(),
            concluida_por="joao",
        )


@pytest.fixture
def conclusao(membro, edital_a, etapa_a1, inscricao, versao):
    avaliacao = concluir(atribuir(membro, edital_a, etapa_a1, inscricao), versao)
    return ConclusaoAvaliacao.objects.create(
        avaliacao=avaliacao,
        ordem=1,
        pontuacao=Decimal("80.0000"),
        parecer="Atende",
        versao=versao,
        concluida_em=timezone.now(),
        concluida_por="joao",
    )


def test_a_conclusao_preservada_recusa_alteracao_no_modelo(conclusao):
    conclusao.parecer = "Outro"

    with pytest.raises(TypeError):
        conclusao.save()


def test_a_conclusao_preservada_recusa_remocao_no_modelo(conclusao):
    with pytest.raises(TypeError):
        conclusao.delete()


def test_a_trigger_recusa_update_direto_no_banco(conclusao):
    """O que sustenta FR-094 não pode depender de todo caminho futuro lembrar de conferir."""
    with pytest.raises(Exception, match="append-only"), transaction.atomic():
        ConclusaoAvaliacao.objects.filter(pk=conclusao.pk).update(parecer="Reescrito")


def test_a_trigger_recusa_delete_direto_no_banco(conclusao):
    with pytest.raises(Exception, match="append-only"), transaction.atomic():
        ConclusaoAvaliacao.objects.filter(pk=conclusao.pk).delete()


def test_a_ordem_da_conclusao_e_unica(conclusao, versao):
    with pytest.raises(IntegrityError), transaction.atomic():
        ConclusaoAvaliacao.objects.create(
            avaliacao=conclusao.avaliacao,
            ordem=1,
            pontuacao=Decimal("90.0000"),
            versao=versao,
            concluida_em=timezone.now() + timedelta(minutes=1),
            concluida_por="joao",
        )
