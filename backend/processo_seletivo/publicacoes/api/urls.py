from django.urls import path

from processo_seletivo.publicacoes.api.views import (
    CancelRetificationView,
    CreateRetificationView,
    EditRetificationView,
    HomologateEditalView,
    HomologateRetificationView,
    PublishEditalView,
    PublishRetificationView,
    ReturnEditalView,
    ReturnRetificationView,
    RevokeHomologationView,
    SubmitEditalView,
    SubmitRetificationView,
)

urlpatterns = [
    path("editais/<uuid:edital_id>/submissoes", SubmitEditalView.as_view()),
    path("editais/<uuid:edital_id>/homologacoes", HomologateEditalView.as_view()),
    path("editais/<uuid:edital_id>/devolucoes", ReturnEditalView.as_view()),
    path("editais/<uuid:edital_id>/revogacoes-homologacao", RevokeHomologationView.as_view()),
    path("editais/<uuid:edital_id>/publicacoes", PublishEditalView.as_view()),
    path("editais/<uuid:edital_id>/retificacoes", CreateRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/rascunho", EditRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/submissoes", SubmitRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/homologacoes", HomologateRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/publicacoes", PublishRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/devolucoes", ReturnRetificationView.as_view()),
    path("retificacoes/<uuid:retificacao_id>/cancelamentos", CancelRetificationView.as_view()),
]
