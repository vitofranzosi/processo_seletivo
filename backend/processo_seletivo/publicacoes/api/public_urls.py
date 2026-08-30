from django.urls import path

from processo_seletivo.publicacoes.api.public_views import (
    ConsolidatedVersionView,
    EffectiveVersionView,
    PublicHistoryView,
    PublicPublicationView,
    PublicRetificationView,
)
from processo_seletivo.publicacoes.api.views import PublishedDocumentView

urlpatterns = [
    path(
        "editais/<uuid:edital_id>/versao-vigente",
        EffectiveVersionView.as_view(),
        name="public-effective-version",
    ),
    path(
        "editais/<uuid:edital_id>/historico",
        PublicHistoryView.as_view(),
        name="public-history",
    ),
    path(
        "publicacoes/<uuid:publicacao_id>",
        PublicPublicationView.as_view(),
        name="public-publication",
    ),
    path(
        "publicacoes/<uuid:publicacao_id>/documento",
        PublishedDocumentView.as_view(),
        name="public-document",
    ),
    path(
        "retificacoes/<uuid:retificacao_id>",
        PublicRetificationView.as_view(),
        name="public-retification",
    ),
    path("versoes/<uuid:versao_id>", ConsolidatedVersionView.as_view(), name="public-version"),
]
