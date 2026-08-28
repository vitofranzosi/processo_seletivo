from pathlib import Path

import pytest
import yaml


@pytest.mark.contract
def test_openapi_event_contract_supports_point_and_period():
    contract = (
        Path(__file__).resolve().parents[3]
        / "specs/001-processo-seletivo-editais/contracts/openapi.yaml"
    )
    document = yaml.safe_load(contract.read_text(encoding="utf-8"))
    event = document["components"]["schemas"]["EventoInput"]
    assert {"id", "type", "description", "startAt"}.issubset(event["required"])
    assert event["properties"]["startAt"]["format"] == "date-time"
    assert event["properties"]["endAt"]["format"] == "date-time"
