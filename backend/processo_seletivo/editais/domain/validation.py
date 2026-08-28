from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING_ERROR = "BLOCKING_ERROR"


@dataclass(frozen=True)
class ValidationFinding:
    severity: Severity
    code: str
    message: str
    path: str = ""


def validate_for_publication(snapshot: dict) -> list[ValidationFinding]:
    findings = []
    if not snapshot.get("title"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR, "title_required", "Título obrigatório.", "title"
            )
        )
    if not snapshot.get("profiles"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                "profiles_required",
                "Ao menos um Perfil é obrigatório.",
                "profiles",
            )
        )
    if not snapshot.get("schedule"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                "schedule_required",
                "Ao menos um Evento é obrigatório.",
                "schedule",
            )
        )
    if not snapshot.get("description"):
        findings.append(
            ValidationFinding(
                Severity.WARNING,
                "description_missing",
                "O Edital não possui descrição.",
                "description",
            )
        )
    return findings


def blocking_findings(findings):
    return [item for item in findings if item.severity == Severity.BLOCKING_ERROR]
