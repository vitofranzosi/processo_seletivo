"""O que a revisão do PR 221 encontrou nas superfícies, e o polish que veio junto (28/09/2026).

Cada caso nomeia o defeito que a revisão viu, porque é ele que o teste impede de voltar:

- a pendência de seção ia inteira para a etapa Conteúdo, inclusive os impeditivos de topologia que
  ela não corrige;
- o período cancelado era "Encerrada" no cartão e "Inscrições encerradas" na gestão, e
  "cancelado" na página do mesmo Edital.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from django.template.loader import render_to_string

from processo_seletivo.inscricoes.domain.periodo import ENCERRADO, periodo_de_inscricoes
from processo_seletivo.interface import views
from processo_seletivo.interface.visao_geral import situacao_do_periodo
from processo_seletivo.portal import leitura

AGORA = datetime(2026, 10, 7, 12, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
SECAO = "/sections/id=00000000-0000-4000-8000-000000000001"


# --- A pendência de seção vai aonde se corrige ------------------------------------------------


@pytest.mark.parametrize("codigo", ["attachment_cited_without_label", "section_universal_empty"])
def test_os_dois_avisos_do_texto_da_secao_levam_ao_conteudo(codigo):
    assert views._destino(SECAO, codigo) == ("conteudo", "#conteudo-titulo", True)
    assert views._destino("/sections", codigo) == ("conteudo", "#conteudo-titulo", True)


@pytest.mark.parametrize(
    ("caminho", "codigo"),
    [
        ("/sections", "field_required"),
        ("/sections", "field_constraint_violated"),
        (f"{SECAO}/title", "field_constraint_violated"),
        (f"{SECAO}/order", "field_constraint_violated"),
        (f"{SECAO}/content", "field_required"),
    ],
)
def test_a_topologia_do_catalogo_continua_sem_destino_inventado(caminho, codigo):
    """A etapa Conteúdo não recria seção nem troca título ou ordem: oferecê-la seria falso."""
    assert views._destino(caminho, codigo) == (None, "", False)


def test_o_aviso_do_rc21_fora_da_secao_segue_o_caminho_dele():
    assert views._destino("description", "attachment_cited_without_label")[0] == "identificacao"
    assert (
        views._destino("/documentRequirements/id=d-1", "attachment_cited_without_label")[0]
        == "inscricao"
    )


def test_o_periodo_cancelado_se_desfaz_na_etapa_inscricao():
    caminho = "/schedule/id=00000000-0000-4000-8000-0000000000c1/status"
    assert views._destino(caminho, "registration_period_cancelled")[0] == "inscricao"


# --- O período cancelado é dito cancelado em toda superfície ----------------------------------


def _conteudo(status):
    return {
        "schedule": [
            {
                "id": "periodo",
                "startAt": (AGORA - timedelta(days=1)).isoformat(),
                "endAt": (AGORA + timedelta(days=5)).isoformat(),
                "status": status,
                "isRegistrationPeriod": True,
            }
        ]
    }


def test_o_cartao_da_vitrine_diz_periodo_cancelado_e_o_grupo_continua_o_das_encerradas():
    periodo = periodo_de_inscricoes(_conteudo("CANCELADO"), AGORA)

    assert leitura.situacao_publica(periodo, None) == (ENCERRADO, "Período cancelado")
    assert leitura.estado_na_vitrine(periodo, None) == ENCERRADO
    # O que não foi cancelado continua com a etiqueta de sempre.
    aberto = periodo_de_inscricoes(_conteudo("PLANEJADO"), AGORA)
    assert leitura.situacao_publica(aberto, None) == ("aberto", "Aberta")


def test_a_linha_da_visao_geral_diz_periodo_cancelado():
    situacao = situacao_do_periodo(_conteudo("CANCELADO"), AGORA)
    assert situacao.encerrado and situacao.cancelado

    edital = SimpleNamespace(
        id=uuid4(), number="88", year=2026, status="PUBLICADO", processo=SimpleNamespace(title="P")
    )
    linha = SimpleNamespace(periodo=situacao, edital=edital)
    html = render_to_string("interface/_linha_do_edital.html", {"linha": linha})
    assert "Período de inscrições cancelado" in html
    assert "Inscrições encerradas" not in html
    # O término publicado não é prazo de um período que não recebe.
    assert "até " not in html.split("Período de inscrições cancelado")[1].split("</td>")[0]


def test_o_pulso_do_processo_diz_periodo_cancelado_e_nao_inscricoes_ate():
    from processo_seletivo.interface.supervisao import periodo_do_edital

    periodo, ausencia = periodo_do_edital(_conteudo("CANCELADO"), AGORA)
    assert ausencia == "" and periodo.cancelado and periodo.restante is None
