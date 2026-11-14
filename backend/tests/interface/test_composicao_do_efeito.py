"""A composição e o documento dizem o efeito do desfecho (164, US1, UX-740, UX-741, FR-7023).

A divisão do trabalho é a do alcance da `163`: **a folha esconde, o servidor descarta**. Sem `:has`,
o grupo do efeito aparece sempre, e uma opção marcada nele não declara efeito na Etapa que não o
tem. O documento ganha a frase só na Etapa que declara, e por isso o acervo se recompõe idêntico.
"""

import re
from pathlib import Path

import pytest

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.interface.relatorio_do_edital import LinhaDaEtapa
from processo_seletivo.interface.relatorio_pdf import _eliminadas
from processo_seletivo.interface.views import _por_consequencia
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import REDACAO_1, Composicao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import etapa, etapas_form, eventos, perfis

FOLHA = (
    Path(__file__).resolve().parents[2]
    / "processo_seletivo/interface/static/interface/gestao/telas.css"
)
RETIRA = (
    "O candidato com resultado desfavorável ou que não comparecer deixa de concorrer pela reserva "
    "de vagas e continua concorrendo pela ampla concorrência."
)


@pytest.fixture
def elaborando(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    return edital


def _gravada():
    return EtapaAvaliacao.objects.order_by("order").first()


@pytest.mark.django_db
@pytest.mark.integration
def test_a_etapa_restrita_nasce_retirando_da_reserva(client, elaborando):
    """UX-740, UX-741, FR-7001: o grupo existe, e as opções padrão vêm marcadas."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "RESTRITA", "etapa-0-modalityCodes": ["PCD"]}),
    )
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()

    assert "O que acontece com quem tem desfecho desfavorável nesta Etapa?" in corpo
    assert re.search(r'name="etapa-0-efeitoDesfavoravel" value="RESERVE_REMOVAL"\s+checked', corpo)
    assert re.search(r'name="etapa-0-efeitoDaAusencia" value=""\s+checked', corpo)
    assert 'style="' not in corpo.split("O que acontece com quem")[1][:3000]


@pytest.mark.django_db
@pytest.mark.integration
def test_a_escolha_elimina_e_gravada(client, elaborando):
    """FR-7000: a segunda opção grava "elimina", e a ausência diferente também."""
    form = etapas_form(
        **{
            "etapa-0-alcance": "RESTRITA",
            "etapa-0-modalityCodes": ["PCD"],
            "etapa-0-efeitoDesfavoravel": "ELIMINATION",
            "etapa-0-efeitoDaAusencia": "RESERVE_REMOVAL",
        }
    )
    resposta = client.post(etapa(elaborando, "etapas"), form)

    assert resposta.status_code == 302, resposta.content
    gravada = _gravada()
    assert gravada.eliminatory
    assert gravada.efeito_desfavoravel == "ELIMINA"
    assert gravada.efeito_da_ausencia == "RETIRA_DA_RESERVA"


@pytest.mark.django_db
@pytest.mark.integration
def test_a_etapa_para_todas_descarta_o_efeito(client, elaborando):
    """FR-7002: sem `:has`, o grupo aparece, e a opção marcada não vale na Etapa para todas."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "TODAS", "etapa-0-efeitoDesfavoravel": "ELIMINATION"}),
    )

    assert _gravada().efeito_desfavoravel == ""


def test_a_folha_esconde_o_grupo_fora_da_etapa_restrita_e_eliminatoria():
    """UX-740: as regras existem, e só escondem quando outra opção está marcada."""
    folha = FOLHA.read_text(encoding="utf-8")

    assert ".so-eliminatoria" in folha
    assert 'input[name$="-eliminatory"]:not(:checked)) .so-eliminatoria' in folha


def _snapshot(**efeito):
    return {
        "profiles": [
            {
                "id": "perfil",
                "code": "C1",
                "competitionModalities": [{"id": "m", "code": "PPI", "name": "Pretos e pardos"}],
            }
        ],
        "stages": [
            {
                "id": "hetero",
                "name": "Heteroidentificação",
                "order": 1,
                "eliminatory": True,
                "classificatory": False,
                "forma": "DECISORIA",
                "rotuloFavoravel": "Confirmada",
                "rotuloDesfavoravel": "Não confirmada",
                "criteria": [],
                "modalityCodes": ["PPI"],
                "unfavorableOutcomeEffect": None,
                "absenceEffect": None,
                **efeito,
            }
        ],
        "documentRequirements": [],
        "schedule": [],
    }


def _textos(snapshot, redacao=None):
    composicao = Composicao(**({"redacao": redacao} if redacao is not None else {}))
    pdf._etapas(composicao, snapshot, 6, pdf._Numerador())
    return [item[1] for item in composicao.itens if item[0] == "texto"]


def test_o_documento_diz_o_efeito_declarado():
    """FR-7023: na redação vigente, a frase; na redação 1, o par "Efeito"."""
    # As linhas vêm quebradas na largura da página: a frase se confere no texto corrido.
    assert RETIRA in " ".join(_textos(_snapshot(unfavorableOutcomeEffect="RESERVE_REMOVAL")))
    textos = _textos(_snapshot(unfavorableOutcomeEffect="RESERVE_REMOVAL"), REDACAO_1)
    corrido = " ".join(textos)
    assert "Efeito" in corrido
    assert "deixa de concorrer pela reserva" in corrido


@pytest.mark.parametrize("redacao", [None, REDACAO_1], ids=["vigente", "redacao-1"])
def test_o_acervo_sem_declaracao_lido_como_elimina_nao_ganha_frase_nova(redacao):
    """SC-2330: o nulo do acervo é "elimina", e o documento que ele compunha não muda."""
    com_nulo = _snapshot()
    sem_chaves = _snapshot()
    del sem_chaves["stages"][0]["unfavorableOutcomeEffect"]
    del sem_chaves["stages"][0]["absenceEffect"]

    textos = _textos(com_nulo, redacao)
    assert textos == _textos(sem_chaves, redacao)


def test_a_confirmacao_da_consolidacao_diz_cada_efeito_pelo_nome():
    """UX-743: antes de confirmar, quantas serão retiradas e quantas eliminadas."""
    assert _por_consequencia({"HABILITADA": 3, "RETIRADA_DA_RESERVA": 1, "ELIMINADA": 2}) == [
        "3 habilitadas",
        "1 retirada da reserva",
        "2 eliminadas",
    ]


def test_o_relatorio_conta_a_retirada_a_parte():
    """FR-7025: sem retirada, a célula de antes; com ela, ao lado, e nunca somada."""
    base = {
        "nome": "Hetero",
        "regra": "",
        "avaliadas": 3,
        "habilitadas": 1,
        "eliminadas": 1,
        "por_ocorrencia": 0,
        "elimina": True,
        "registrada": True,
    }
    assert _eliminadas(LinhaDaEtapa(**base)) == "1"
    assert _eliminadas(LinhaDaEtapa(**base, retiradas=2)) == "1; 2 retiradas da reserva"
