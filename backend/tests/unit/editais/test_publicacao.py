"""As condições de raiz que decidem se um Edital pode ser publicado.

A verificação por entidade que a `005` acrescentou não substitui estas: um Edital com Perfis bem
formados e sem título continua sendo recusado, e um sem Perfil nenhum também.
"""

from processo_seletivo.editais.domain.validation import Severity, validate_for_publication
from tests.fixtures.snapshot import conteudo_normativo


def test_blocking_findings_prevent_incomplete_edital():
    findings = validate_for_publication({"title": "Edital", "profiles": [], "schedule": []})
    assert any(item.severity == Severity.BLOCKING_ERROR for item in findings)


def test_warning_does_not_make_complete_edital_invalid():
    """A fixture precisou virar um Edital de verdade.

    Ela era `{"code": "P1", "immediateVacancies": 1}` — dois dos doze campos que um Perfil publicado
    carrega. Passava porque nada olhava a forma das entidades, e é justamente o Perfil mutilado que
    a `005` recusa. Trocar a fixture é reconhecer que ela nunca descreveu um Edital completo.
    """
    findings = validate_for_publication({**conteudo_normativo(), "description": ""})

    assert not any(item.severity == Severity.BLOCKING_ERROR for item in findings)
    assert any(item.severity == Severity.WARNING for item in findings)


def test_root_conditions_still_hold_over_well_formed_entities():
    """As duas perguntas são independentes: entidades íntegras não dispensam a raiz."""
    findings = validate_for_publication({**conteudo_normativo(), "title": ""})

    impeditivos = [item.code for item in findings if item.severity == Severity.BLOCKING_ERROR]
    assert impeditivos == ["title_required"]
