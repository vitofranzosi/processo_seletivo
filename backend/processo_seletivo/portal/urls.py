from django.urls import path

from processo_seletivo.portal import views

app_name = "portal"

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("<uuid:edital_id>/", views.selecao, name="selecao"),
]
