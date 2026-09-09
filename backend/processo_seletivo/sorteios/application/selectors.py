"""Leitura pública e de gestão do sorteio. Nenhuma escrita, e nenhuma recomposição."""

from processo_seletivo.sorteios.models import RelacaoDeHabilitados


def relacao_publica(relacao_id):
    """A relação publicada, por identidade. `None` quando não existe.

    Sem filtro de vigência: **relação sucedida continua respondendo no mesmo endereço**, dizendo
    que foi sucedida. Um endereço que deixasse de responder quebraria toda citação já publicada —
    manifesto, documento de resultado, ofício —, e é o precedente que a divulgação da `017` fixou.
    """
    return (
        RelacaoDeHabilitados.objects.filter(pk=relacao_id)
        .select_related("edital", "versao")
        .prefetch_related("sucessoras")
        .first()
    )


def relacao_vigente(*, edital, perfil_id, marco_id, lista_id=None):
    """A relação sem sucessora do recorte. Há **uma**, por constraint (FR-070)."""
    return (
        RelacaoDeHabilitados.objects.filter(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            sucessoras__isnull=True,
        )
        .order_by("-publicada_em")
        .first()
    )


__all__ = ["relacao_publica", "relacao_vigente"]
