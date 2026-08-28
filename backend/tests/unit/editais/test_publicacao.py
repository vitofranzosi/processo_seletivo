from processo_seletivo.editais.domain.validation import Severity, validate_for_publication


def test_blocking_findings_prevent_incomplete_edital():
    findings = validate_for_publication({"title": "Edital", "profiles": [], "schedule": []})
    assert any(item.severity == Severity.BLOCKING_ERROR for item in findings)


def test_warning_does_not_make_complete_edital_invalid():
    findings = validate_for_publication(
        {
            "title": "Edital",
            "description": "",
            "profiles": [{"code": "P1", "immediateVacancies": 1}],
            "schedule": [{"type": "INSCRICAO"}],
        }
    )
    assert not any(item.severity == Severity.BLOCKING_ERROR for item in findings)
    assert any(item.severity == Severity.WARNING for item in findings)
