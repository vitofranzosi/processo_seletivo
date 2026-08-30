from django.urls import path

from processo_seletivo.auditoria.api import AuditoriaView

urlpatterns = [path("auditoria", AuditoriaView.as_view(), name="auditoria")]
