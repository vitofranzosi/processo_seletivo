"""Perfil só de cadastro de reserva: a Revisão diz como a convocação acontece (RC-58, DP-05, 097).

Até a `097`, a Revisão avisava que a convocação desta família era feita fora do sistema: com zero
vagas imediatas não havia déficit nunca. A `DP-05` voltou à opção A em 21/10/2026, com o Edital de
remanescentes do TMD, e a vaga acrescida depois da publicação passou a destravar a chamada. **A
frase antiga deixou de ser verdade, e frase verdadeira que vira falsa é defeito maior do que frase
ausente** — o aviso continua, e diz o que é verdade agora (`FR-2474`). Continua **advertência**,
porque o Edital é legítimo.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    Severity,
    validate_for_publication,
)
from tests.unit.editais.test_invariantes_do_quadro import PPI, geral, linha, perfil, snapshot

CODIGO = "reserve_only_convocation_external"
LINHAS_RESERVADAS = "reserve_only_with_reserved_lines"


def achados(um_perfil, *, ato=ATO_DE_PUBLICACAO, codigo=CODIGO):
    return [
        item
        for item in validate_for_publication(snapshot(um_perfil), ato=ato)
        if item.code == codigo
    ]


def marco(**regra):
    corte = {
        "targetKind": "FIXED",
        "targetCount": 20,
        "surplusCount": 0,
        "tieOutcome": "STRICT",
        "governedStage": "NONE",
        "continuation": "NONE",
        **regra,
    }
    return {"id": "aaaaaaaa-0000-4000-8000-0000000005a1", "code": "M1", "cutRule": corte}


def so_reserva(**alteracoes):
    return perfil(
        **{
            "immediateVacancies": 0,
            "reserveType": "UNLIMITED",
            "vacancyTable": [geral(0)],
            **alteracoes,
        }
    )


@pytest.mark.parametrize(
    ("especie", "limite"),
    [("UNLIMITED", None), ("LIMITED", 30), ("LIMITED", 0)],
)
def test_zero_vaga_com_reserva_e_advertido(especie, limite):
    encontrados = achados(so_reserva(reserveType=especie, reserveLimit=limite))

    assert len(encontrados) == 1
    achado = encontrados[0]
    assert achado.severity == Severity.WARNING, "o Edital é legítimo; recusar diria o contrário"
    assert "'C1'" in achado.message
    assert "fora" not in achado.message, "`SC-923`: a frase do fora do sistema saiu"
    assert "vagas acrescidas depois da publicação" in achado.message
    assert "na ocupação" in achado.message
    assert achado.path.endswith("/immediateVacancies"), "o destino é a etapa dos Perfis"


def test_zero_vaga_sem_reserva_nao_e_este_aviso():
    """Oferta sem vaga e sem cadastro é outra pergunta; este aviso a responderia errado."""
    assert achados(so_reserva(reserveType="NONE")) == []


def test_oferta_com_vagas_e_reserva_nao_e_advertida():
    """A convencional convoca pelo déficit, e a reserva dela são os suplentes da faixa."""
    um_perfil = perfil(immediateVacancies=40, reserveType="UNLIMITED", vacancyTable=[geral(40)])

    assert achados(um_perfil) == []


def test_a_retificacao_nao_repete_o_aviso():
    """Dito antes de publicar; repeti-lo a cada correção de data seria ruído."""
    assert achados(so_reserva(), ato=ATO_DE_RETIFICACAO) == []


class TestOAlcanceDaFaixa:
    """`FR-2474`, `T-011`: sem continuação, a Revisão diz quantos a faixa pode alcançar."""

    def test_alvo_fixo_diz_alvo_mais_excedente(self):
        um_perfil = so_reserva(classificationMilestones=[marco(targetCount=20, surplusCount=2)])

        (achado,) = achados(um_perfil)

        assert "poderá alcançar até 22 classificados" in achado.message

    def test_alvo_do_quadro_diz_so_o_excedente_que_aqui_e_tudo(self):
        """O caso que mais engana: o alvo lido do quadro é zero, e o acréscimo não o muda."""
        um_perfil = so_reserva(
            classificationMilestones=[marco(targetKind="FROM_VACANCY_TABLE", surplusCount=3)]
        )

        (achado,) = achados(um_perfil)

        assert "poderá alcançar até 3 classificados" in achado.message

    def test_com_continuacao_admitida_nao_diz_numero(self):
        um_perfil = so_reserva(classificationMilestones=[marco(continuation="ALLOWED")])

        (achado,) = achados(um_perfil)

        assert "poderá alcançar" not in achado.message


class TestOPerfilComLinhaDeModalidade:
    """`FR-2475`: o acréscimo da `097` só alcança Perfil cujo quadro tem só a linha geral."""

    def test_e_advertido_que_o_acrescimo_nao_o_alcanca(self):
        um_perfil = so_reserva(vacancyTable=[geral(0), linha(0, PPI)])

        (achado,) = achados(um_perfil, codigo=LINHAS_RESERVADAS)

        assert achado.severity == Severity.WARNING
        assert "só a ampla concorrência" in achado.message

    def test_so_a_linha_geral_nao_e_advertido(self):
        assert achados(so_reserva(), codigo=LINHAS_RESERVADAS) == []

    def test_a_retificacao_nao_repete(self):
        um_perfil = so_reserva(vacancyTable=[geral(0), linha(0, PPI)])

        assert achados(um_perfil, ato=ATO_DE_RETIFICACAO, codigo=LINHAS_RESERVADAS) == []
