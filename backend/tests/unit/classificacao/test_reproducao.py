"""A reprodução interpreta o vocabulário do Edital, não uma enumeração interna inventada."""

from datetime import date

from processo_seletivo.classificacao.application.reproducao import _fatos_da_proveniencia


def test_reconstroi_os_dois_tipos_de_fato_publicados():
    fato_data = "00000000-0000-4000-8000-000000000501"
    fato_inteiro = "00000000-0000-4000-8000-000000000502"
    criterio_data = "00000000-0000-4000-8000-000000000511"
    criterio_inteiro = "00000000-0000-4000-8000-000000000512"
    marco = {
        "tiebreakers": [
            {"id": criterio_data, "parameters": {"factId": fato_data}},
            {"id": criterio_inteiro, "parameters": {"factId": fato_inteiro}},
        ]
    }
    fatos_publicados = {
        fato_data: {"id": fato_data, "type": "DATA"},
        fato_inteiro: {"id": fato_inteiro, "type": "INTEIRO"},
    }
    proveniencia = [
        {"criterionId": criterio_data, "value": "1990-05-21"},
        {"criterionId": criterio_inteiro, "value": "17"},
    ]

    assert _fatos_da_proveniencia(proveniencia, marco, fatos_publicados) == {
        fato_data: date(1990, 5, 21),
        fato_inteiro: 17,
    }
