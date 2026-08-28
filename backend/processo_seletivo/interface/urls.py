from django.urls import path

from processo_seletivo.interface import views

app_name = "interface"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("identificar", views.identificar, name="identificar"),
    path("sair", views.sair, name="sair"),
]
