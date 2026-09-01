"""As funções da comissão, e o invariante de governança que depende delas.

A V1 tem duas funções e nenhuma taxonomia aberta (FR-011). A presidência não é papel do sistema:
é vínculo, e vive na linha do membro (D-011).
"""

from processo_seletivo.comissoes.models import Funcao, MembroComissao

PRESIDENTE = Funcao.PRESIDENTE
MEMBRO = Funcao.MEMBRO


def presidentes_ativos(processo, *, exceto=None):
    consulta = MembroComissao.objects.filter(
        processo=processo, ativo=True, funcao=Funcao.PRESIDENTE
    )
    return consulta.exclude(pk=exceto.pk) if exceto is not None else consulta


def tem_presidente(processo, *, exceto=None):
    return presidentes_ativos(processo, exceto=exceto).exists()


def tem_alocacao_ativa(processo, *, exceto=None):
    """Se a comissão distribuiu trabalho. É o que torna a presidência exigível (FR-030)."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    consulta = AlocacaoEtapa.objects.filter(membro__processo=processo, ativo=True)
    if exceto is not None:
        consulta = consulta.exclude(membro=exceto)
    return consulta.exists()
