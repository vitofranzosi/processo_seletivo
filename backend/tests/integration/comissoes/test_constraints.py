"""T010 — as invariantes que o banco recusa, e não o código.

Constraint parcial é o que faz EC-001 e EC-002 serem impossíveis mesmo sob corrida — conferir em
Python deixaria a janela entre a leitura e a gravação.
"""

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def novo_membro(processo, subject="joao", ativo=True):
    agora = timezone.now()
    return MembroComissao.objects.create(
        processo=processo,
        identity_subject=subject,
        funcao="MEMBRO",
        ativo=ativo,
        criado_em=agora,
        criado_por="carlos",
        inativado_em=None if ativo else agora,
        inativado_por="" if ativo else "carlos",
    )


def test_dois_vinculos_ativos_da_mesma_pessoa_sao_recusados(processo_a):
    novo_membro(processo_a)

    with pytest.raises(IntegrityError), transaction.atomic():
        novo_membro(processo_a)


def test_readicionar_quem_saiu_cria_linha_nova(processo_a):
    """A unicidade é parcial de propósito: o histórico sobrevive à recomposição da comissão."""
    novo_membro(processo_a, ativo=False)
    novo_membro(processo_a, ativo=True)

    assert MembroComissao.objects.filter(processo=processo_a).count() == 2


def test_inativo_sem_instante_de_inativacao_e_recusado(processo_a):
    with pytest.raises(IntegrityError), transaction.atomic():
        MembroComissao.objects.create(
            processo=processo_a,
            identity_subject="ana",
            funcao="MEMBRO",
            ativo=False,
            criado_em=timezone.now(),
            criado_por="carlos",
        )


def test_duas_alocacoes_ativas_equivalentes_sao_recusadas(processo_a, edital_a, etapa_a1):
    membro = novo_membro(processo_a)
    agora = timezone.now()
    AlocacaoEtapa.objects.create(
        membro=membro, edital=edital_a, etapa_id=etapa_a1, criado_em=agora, criado_por="carlos"
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        AlocacaoEtapa.objects.create(
            membro=membro,
            edital=edital_a,
            etapa_id=etapa_a1,
            criado_em=agora,
            criado_por="carlos",
        )


def test_o_mesmo_membro_pode_estar_em_etapas_diferentes(processo_a, edital_a, etapa_a1, etapa_a2):
    """FR-037: várias Etapas por pessoa, sem duplicar o vínculo de comissão."""
    membro = novo_membro(processo_a)
    agora = timezone.now()
    for etapa in (etapa_a1, etapa_a2):
        AlocacaoEtapa.objects.create(
            membro=membro, edital=edital_a, etapa_id=etapa, criado_em=agora, criado_por="carlos"
        )

    assert membro.alocacoes.filter(ativo=True).count() == 2
    assert MembroComissao.objects.filter(processo=processo_a, ativo=True).count() == 1
