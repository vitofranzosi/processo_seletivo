"""O acompanhamento desenha os pareceres da deliberação (165, FR-7076, FR-7077, UX-753).

O template, renderizado com o que o seletor do titular entrega: cada parecer desfavorável num
parágrafo, à parte do motivo, sem autoria; e o ramo de um parecer só, como era.
"""

from types import SimpleNamespace
from uuid import uuid4

from django.template.loader import render_to_string

MOTIVO = "a comissão deliberou Indeferido por maioria: 2 de 3 pareceres Indeferido"


def _render(parecer, *, motivo=MOTIVO):
    identidade = uuid4()
    return render_to_string(
        "portal/acompanhamento.html",
        {
            "inscricao": SimpleNamespace(id=uuid4(), pk=1, protocolo="1"),
            "edital": SimpleNamespace(id=uuid4()),
            "resultados_das_etapas": [
                {
                    "id": identidade,
                    "nome": "Heteroidentificação",
                    "habilitada": False,
                    "retirada": True,
                    "motivo": motivo,
                }
            ],
            "parecer_por_resultado": {identidade: parecer},
        },
    )


def test_cada_parecer_desfavoravel_num_paragrafo_a_parte_do_motivo():
    corpo = _render(
        {
            "estado": "visivel",
            "textos": ["Fenótipo não constatado.", "Não há traços fenotípicos."],
            "texto": "Fenótipo não constatado.\n\nNão há traços fenotípicos.",
        }
    )

    assert "Fundamentação dos pareceres que decidiram o resultado" in corpo
    assert corpo.count('class="texto-do-parecer"') == 2
    assert MOTIVO in corpo
    # UX-753: a comissão decidiu, e não "quem avaliou".
    assert "Fundamentação escrita por quem avaliou" not in corpo


def test_o_parecer_unico_continua_como_era():
    corpo = _render({"estado": "visivel", "texto": "Nota abaixo da mínima."}, motivo="")

    assert "Fundamentação escrita por quem avaliou" in corpo
    assert corpo.count('class="texto-do-parecer"') == 1
