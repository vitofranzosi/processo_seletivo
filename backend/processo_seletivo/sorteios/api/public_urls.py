from django.urls import path

from processo_seletivo.sorteios.api.public_views import RelacaoPublicaView

urlpatterns = [
    path(
        "sorteio/relacoes/<uuid:relacao_id>",
        RelacaoPublicaView.as_view(),
        name="public-relacao-de-habilitados",
    ),
]
