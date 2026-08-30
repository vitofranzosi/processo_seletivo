"""T091 — logs estruturados, health/readiness e métricas de conflito.

Este módulo guarda as primitivas — formatter, contadores e o registro de recusas. A camada
HTTP correspondente fica em `shared/api/operacional.py`, porque o formatter é carregado junto
com as settings, antes do DRF estar disponível.

Os endpoints vivem fora de `/api/v1`: não são API institucional e não entram no `openapi.yaml`.

O princípio V da Constituição exige diagnóstico sem exposição indevida. Nenhum campo aqui
carrega token, credencial ou conteúdo normativo: o log identifica a operação e a correlação,
e quem precisa do conteúdo consulta a auditoria, que é autorizada.
"""

import json
import logging
import threading
import time

logger = logging.getLogger("processo_seletivo")

METRICS_PERMISSION = "observabilidade:consultar"
# Status que representam disputa por um recurso, e não erro de quem chamou.
CONFLICT_STATUSES = frozenset({409, 412, 428})


class ConflictMetrics:
    """Contadores em processo, sem dependência externa.

    Reiniciam a cada processo; servem para leitura por scraping e para o teste de carga de
    T092 comparar disputa observada com disputa esperada. Não substituem a auditoria, que é a
    fonte durável.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._conflicts = {}
        self._rejections = {}
        self._started_at = time.monotonic()

    def record(self, *, code: str, status: int) -> None:
        destino = self._conflicts if status in CONFLICT_STATUSES else self._rejections
        with self._lock:
            destino[code] = destino.get(code, 0) + 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptimeSeconds": round(time.monotonic() - self._started_at, 3),
                "conflicts": dict(sorted(self._conflicts.items())),
                "conflictTotal": sum(self._conflicts.values()),
                "rejections": dict(sorted(self._rejections.items())),
                "rejectionTotal": sum(self._rejections.values()),
            }

    def reset(self) -> None:
        with self._lock:
            self._conflicts.clear()
            self._rejections.clear()


metrics = ConflictMetrics()


class JsonFormatter(logging.Formatter):
    """Uma linha JSON por evento, com a correlação que liga log e auditoria."""

    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for campo in ("correlationId", "code", "status", "operation", "actor"):
            valor = getattr(record, campo, None)
            if valor is not None:
                payload[campo] = valor
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def log_domain_rejection(*, code, status, correlation_id, actor_subject=""):
    """Registra a recusa sem repetir o detalhe, que pode conter dado do Edital."""
    metrics.record(code=code, status=status)
    logger.warning(
        "operacao_recusada",
        extra={
            "correlationId": correlation_id,
            "code": code,
            "status": status,
            "actor": actor_subject or "anonimo",
        },
    )
