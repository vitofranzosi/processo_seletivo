"""O barema na comparação entre a norma da conclusão e a vigente — tudo menos a ordem (146, T022).

A comparação é conservadora (D-006, FR-5221): a descrição é onde mora a condição material, e o
sistema não distingue redação de regra. A recusa custa reabrir e concluir de novo com a ficha já
preenchida; o contrário custaria um Resultado consolidado sob regra que não é a publicada.
"""

import pytest

from processo_seletivo.resultados.domain.compatibilidade import NORMA_DIVERGENTE, incompatibilidade

ETAPA = "11111111-1111-1111-1111-111111111146"


def criterio(chave, **campos):
    return {
        "id": chave,
        "name": f"Critério {chave}",
        "description": "",
        "maximumScore": "10.0000",
        "pointsPerUnit": "5.0000",
        "unitLabel": "certificado",
        "documentRequirementId": "doc-1",
        **campos,
    }


def etapa(criterios):
    return {
        "id": ETAPA,
        "name": "Prova de Títulos",
        "eliminatory": False,
        "minimumScore": None,
        "maximumScore": "20.0000",
        "criteria": criterios,
    }


def comparar(antes, depois):
    return incompatibilidade(
        conteudo={"stages": [etapa(antes)]}, etapa_id=ETAPA, etapa_vigente=etapa(depois)
    )


BAREMA = [criterio("a"), criterio("b")]


def test_o_mesmo_barema_e_compativel():
    assert comparar(BAREMA, [dict(c) for c in BAREMA]) is None


def test_reordenar_os_criterios_nao_bloqueia():
    """Só a ordem fica de fora: ela muda onde a linha aparece, e não quanto ela vale."""
    assert comparar(BAREMA, list(reversed(BAREMA))) is None


def test_decimal_em_outra_grafia_e_o_mesmo_barema():
    assert comparar(BAREMA, [criterio("a", maximumScore="10"), criterio("b")]) is None


@pytest.mark.parametrize(
    "mudanca",
    [
        {"maximumScore": "12.0000"},
        {"pointsPerUnit": "4.0000"},
        {"pointsPerUnit": None, "unitLabel": None},
        {"unitLabel": "diploma"},
        {"name": "Outro nome"},
        {"description": "Só em cursos EaD."},
        {"documentRequirementId": "doc-2"},
    ],
    ids=["maxima", "pontos", "forma", "unidade", "nome", "descricao", "documento"],
)
def test_qualquer_campo_do_criterio_bloqueia(mudanca):
    codigo, frase = comparar(BAREMA, [criterio("a", **mudanca), criterio("b")])

    assert codigo == NORMA_DIVERGENTE
    assert "barema" in frase


@pytest.mark.parametrize(
    "depois",
    [[criterio("a")], [*BAREMA, criterio("c")], [criterio("a"), criterio("c")]],
    ids=["removido", "acrescentado", "trocado"],
)
def test_o_conjunto_dos_criterios_bloqueia(depois):
    assert comparar(BAREMA, depois)[0] == NORMA_DIVERGENTE


def test_sem_barema_dos_dois_lados_nada_muda():
    """A Etapa sem barema, e a do acervo sem a chave, são o mesmo conjunto vazio (FR-5231)."""
    sem_chave = {"stages": [{k: v for k, v in etapa([]).items() if k != "criteria"}]}

    assert incompatibilidade(conteudo=sem_chave, etapa_id=ETAPA, etapa_vigente=etapa([])) is None
