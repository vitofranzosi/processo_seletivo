from django.urls import include, path

from config.urls import urlpatterns as rotas_do_sistema

urlpatterns = [
    path("gestao/prototipo-centro/", include("vistas_do_prototipo")),
    *rotas_do_sistema,
]
