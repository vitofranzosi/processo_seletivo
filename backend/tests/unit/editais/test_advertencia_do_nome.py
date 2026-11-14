"""A advertência do nome da Etapa restrita com termo técnico (168, FR-7336; research T-009).

Contextual e não impeditiva: nomeia o termo, diz que o candidato lê o nome, e não sugere nome — a
Etapa restrita pode ser a verificação da autodeclaração ou a perícia de pessoa com deficiência.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    NOME_DA_ETAPA_RESTRITA_COM_TERMO_TECNICO,
    Severity,
    _nome_da_restrita_com_termo_tecnico,
)


def etapa(nome, *, restrita=True):
    return {"id": "e1", "name": nome, "modalityCodes": ["PPI"] if restrita else None}


def achados(*etapas, ato=ATO_DE_PUBLICACAO):
    return _nome_da_restrita_com_termo_tecnico({"stages": list(etapas)}, ato=ato)


@pytest.mark.parametrize(
    ("nome", "termo"),
    [
        ("Heteroidentificação", "heteroidentificação"),
        ("Banca de HETEROIDENTIFICACAO", "heteroidentificação"),
        ("Análise fenotípica", "fenótipo"),
        ("Aferição da autodeclaração", "aferição"),
    ],
)
def test_adverte_e_nomeia_o_termo(nome, termo):
    (achado,) = achados(etapa(nome))
    assert achado.severity == Severity.WARNING
    assert achado.code == NOME_DA_ETAPA_RESTRITA_COM_TERMO_TECNICO
    assert f"«{termo}»" in achado.message
    assert "acompanhamento" in achado.message
    assert achado.path.endswith("/name")


def test_nao_sugere_nome_que_pressuponha_o_procedimento():
    """Ajuste 1 do usuário: a perícia não se chama «Verificação da autodeclaração»."""
    (achado,) = achados(etapa("Heteroidentificação"))
    assert "Verificação da autodeclaração" not in achado.message


@pytest.mark.parametrize("nome", ["Verificação da autodeclaração", "Perícia médica", ""])
def test_nome_neutro_nao_adverte(nome):
    assert achados(etapa(nome)) == []


def test_so_a_etapa_restrita_e_so_na_publicacao():
    assert achados(etapa("Heteroidentificação", restrita=False)) == []
    assert achados(etapa("Heteroidentificação"), ato="retificacao") == []
