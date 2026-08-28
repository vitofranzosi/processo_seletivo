from django.urls import path

from processo_seletivo.processos.api.finalizacao import (
    CancelEditalView,
    CancelProcessView,
    CloseEditalView,
    CloseProcessView,
)
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
    path(
        "processos/<uuid:processo_id>/encerramentos",
        CloseProcessView.as_view(),
        name="process-close",
    ),
    path(
        "processos/<uuid:processo_id>/cancelamentos",
        CancelProcessView.as_view(),
        name="process-cancel",
    ),
    path(
        "editais/<uuid:edital_id>/encerramentos",
        CloseEditalView.as_view(),
        name="edital-close",
    ),
    path(
        "editais/<uuid:edital_id>/cancelamentos",
        CancelEditalView.as_view(),
        name="edital-cancel",
    ),
]
