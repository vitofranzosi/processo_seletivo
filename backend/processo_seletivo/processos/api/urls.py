from django.urls import path

from processo_seletivo.processos.api.views import (
    ActivateProcessView,
    EditalCollectionView,
    ProcessCollectionView,
)

urlpatterns = [
    path("processos", ProcessCollectionView.as_view(), name="process-create"),
    path(
        "processos/<uuid:processo_id>/editais", EditalCollectionView.as_view(), name="edital-create"
    ),
    path(
        "processos/<uuid:processo_id>/ativacoes",
        ActivateProcessView.as_view(),
        name="process-activate",
    ),
]
