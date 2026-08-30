"""T091 — camada HTTP da observabilidade: health, readiness e métricas.

Separada de `shared/observability.py` porque aquele módulo é carregado pelas settings, antes do
DRF. Fica fora de `/api/v1` por não ser contrato institucional.
"""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.observability import METRICS_PERMISSION, logger, metrics


class IndexView(APIView):
    """Documento de serviço: quem abre a raiz precisa descobrir o que existe."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "service": "Processo Seletivo e Editais — Cefor/IFES",
                "publicApi": "/api/v1/public",
                "adminApi": "/api/v1/admin",
                "operational": {
                    "health": "/health",
                    "readiness": "/readiness",
                    "metrics": "/metrics",
                },
                "publicEndpoints": {
                    "versaoVigente": "/api/v1/public/editais/{editalId}/versao-vigente?em={iso}",
                    "historico": "/api/v1/public/editais/{editalId}/historico",
                    "publicacao": "/api/v1/public/publicacoes/{publicacaoId}",
                    "documento": "/api/v1/public/publicacoes/{publicacaoId}/documento",
                    "retificacao": "/api/v1/public/retificacoes/{retificacaoId}",
                    "versaoConsolidada": "/api/v1/public/versoes/{versaoId}",
                },
                "editaisPublicados": [
                    {
                        "editalId": str(item["edital_id"]),
                        "versaoVigente": (
                            f"/api/v1/public/editais/{item['edital_id']}/versao-vigente"
                        ),
                        "historico": f"/api/v1/public/editais/{item['edital_id']}/historico",
                    }
                    for item in VersaoConsolidada.objects.values("edital_id").distinct()[:20]
                ],
            }
        )


class HealthView(APIView):
    """Liveness: responde sem tocar em dependência externa."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ReadinessView(APIView):
    """Readiness: só está pronto quando o banco responde e não há migration pendente."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        verificacoes = {"database": self._database(), "migrations": self._migrations()}
        pronto = all(verificacoes.values())
        return Response(
            {"status": "ready" if pronto else "not_ready", "checks": verificacoes},
            status=200 if pronto else 503,
        )

    def _database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
        except Exception:  # noqa: BLE001 — readiness reporta indisponibilidade, não propaga
            logger.exception("readiness_database_indisponivel")
            return False

    def _migrations(self):
        try:
            executor = MigrationExecutor(connection)
            return not executor.migration_plan(executor.loader.graph.leaf_nodes())
        except Exception:  # noqa: BLE001 — idem
            logger.exception("readiness_migrations_indisponivel")
            return False


class MetricsView(APIView):
    """Métricas de conflito exigem permissão, como qualquer leitura administrativa."""

    def get(self, request):
        require_permission(request.user, METRICS_PERMISSION)
        return Response(metrics.snapshot())
