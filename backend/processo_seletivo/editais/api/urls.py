from django.urls import path

from processo_seletivo.editais.api.views import EditalDraftView

urlpatterns = [
    path("editais/<uuid:edital_id>/rascunho", EditalDraftView.as_view(), name="edital-draft"),
]
