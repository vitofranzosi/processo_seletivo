from django.urls import path

from processo_seletivo.publicacoes.api.views import PublishedDocumentView

urlpatterns = [
    path("publicacoes/<uuid:publicacao_id>/documento", PublishedDocumentView.as_view()),
]
