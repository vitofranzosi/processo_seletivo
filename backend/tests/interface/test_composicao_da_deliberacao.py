"""A composição e o documento dizem a regra de deliberação (165, US1, UX-750, FR-7050, FR-7075).

A divisão do trabalho é a do efeito da `164`: **a folha esconde, o servidor descarta**. Sem `:has`,
o grupo aparece sempre, e uma opção marcada nele não declara regra na Etapa que não a usa. O
documento ganha a frase só na Etapa colegiada, e por isso o acervo se recompõe idêntico (SC-2350).
"""

import re
from pathlib import Path

import pytest

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.interface.forms import etapas_persistidas
from processo_seletivo.interface.revisao import _etapa as linhas_da_revisao
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import REDACAO_1, Composicao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import etapa, etapas_form, eventos, perfis

FOLHA = (
    Path(__file__).resolve().parents[2]
    / "processo_seletivo/interface/static/interface/gestao/telas.css"
)
DECISORIA = {
    "etapa-0-forma": "DECISORIA",
    "etapa-0-caraterPorForma": "1",
    "etapa-0-eliminatoryDecisoria": "on",
    "etapa-0-rotuloFavoravel": "Deferido",
    "etapa-0-rotuloDesfavoravel": "Indeferido",
    "etapa-0-minimumScore": "",
}


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
def test_a_pergunta_aparece_sem_opcao_marcada(client, elaborando):
    """UX-750, D-002: três opções, com os rótulos digitados, e nenhuma marcada."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**DECISORIA, **{"etapa-0-evaluationsPerRegistration": "3"}),
    )
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()

    assert "Como a comissão chega ao resultado?" in corpo
    assert "«Deferido» quando a maioria dos pareceres for «Deferido»" in corpo
    assert "«Indeferido» só quando todos os pareceres forem «Indeferido»" in corpo
    assert not re.search(r'name="etapa-0-regraDeDeliberacao" value="[A-Z_]+"\s+checked', corpo)
    assert _gravada().regra_de_deliberacao == ""


@pytest.mark.django_db
@pytest.mark.integration
def test_a_escolha_e_gravada_e_relida(client, elaborando):
    """FR-7050: a regra é gravada, relida pelo cartão e pelas outras etapas do assistente."""
    form = etapas_form(
        **DECISORIA,
        **{
            "etapa-0-evaluationsPerRegistration": "3",
            "etapa-0-regraDeDeliberacao": "UNANIMOUS_FOR_FAVORABLE",
        },
    )
    resposta = client.post(etapa(elaborando, "etapas"), form)

    assert resposta.status_code == 302, resposta.content
    assert _gravada().regra_de_deliberacao == "UNANIMIDADE_PARA_O_FAVORAVEL"
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()
    assert re.search(
        r'name="etapa-0-regraDeDeliberacao" value="UNANIMOUS_FOR_FAVORABLE"\s+checked', corpo
    )
    assert etapas_persistidas(elaborando)[0]["deliberationRule"] == "UNANIMOUS_FOR_FAVORABLE"


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    "campos",
    [
        {"etapa-0-evaluationsPerRegistration": "1", **DECISORIA},
        {"etapa-0-evaluationsPerRegistration": "3"},
    ],
    ids=["uma avaliação", "pontuada"],
)
def test_fora_da_colegiada_a_escolha_e_descartada(client, elaborando, campos):
    """FR-7053: sem `:has`, o grupo aparece, e a opção marcada não vale onde a regra não se usa."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**campos, **{"etapa-0-regraDeDeliberacao": "MAJORITY"}),
    )

    assert _gravada().regra_de_deliberacao == ""


def test_a_folha_esconde_o_grupo_fora_da_colegiada():
    """UX-750: a regra existe, e esconde com o número vazio, que é uma avaliação."""
    folha = FOLHA.read_text(encoding="utf-8")

    assert 'input[name$="-evaluationsPerRegistration"]:placeholder-shown) .so-colegiada' in folha


def _snapshot(**campos):
    return {
        "profiles": [],
        "stages": [
            {
                "id": "hetero",
                "name": "Heteroidentificação",
                "order": 1,
                "eliminatory": True,
                "classificatory": False,
                "forma": "DECISORIA",
                "evaluationsPerRegistration": 3,
                "rotuloFavoravel": "Deferido",
                "rotuloDesfavoravel": "Indeferido",
                "criteria": [],
                "modalityCodes": None,
                "unfavorableOutcomeEffect": None,
                "absenceEffect": None,
                "deliberationRule": None,
                **campos,
            }
        ],
        "documentRequirements": [],
        "schedule": [],
    }


def _textos(snapshot, redacao=None):
    composicao = Composicao(**({"redacao": redacao} if redacao is not None else {}))
    pdf._etapas(composicao, snapshot, 6, pdf._Numerador())
    return " ".join(item[1] for item in composicao.itens if item[0] == "texto")


def test_o_documento_diz_a_regra_nas_duas_redacoes():
    """FR-7075: na redação vigente, a frase; na redação 1, o par "Deliberação"."""
    snapshot = _snapshot(deliberationRule="MAJORITY")
    vigente = _textos(snapshot)
    assert "Cada inscrição recebe 3 pareceres" in vigente
    assert "maioria dos pareceres" in vigente
    redacao_1 = _textos(snapshot, REDACAO_1)
    assert "Deliberação" in redacao_1
    assert "maioria dos pareceres" in redacao_1


@pytest.mark.parametrize("redacao", [None, REDACAO_1], ids=["vigente", "redacao-1"])
def test_o_acervo_sem_regra_nao_ganha_frase(redacao):
    """SC-2350: o nulo do acervo, e a ausência da chave, compõem o mesmo documento."""
    com_nulo = _snapshot()
    sem_chave = _snapshot()
    del sem_chave["stages"][0]["deliberationRule"]

    assert _textos(com_nulo, redacao) == _textos(sem_chave, redacao)
    assert "pareceres" not in _textos(com_nulo, redacao)


def test_a_revisao_diz_a_regra_com_as_palavras_do_documento():
    """FR-7075."""
    snapshot = _snapshot(deliberationRule="UNANIMOUS_FOR_UNFAVORABLE")
    linhas = linhas_da_revisao(snapshot["stages"][0], snapshot)["linhas"]
    deliberacao = [linha for linha in linhas if getattr(linha, "rotulo", "") == "Deliberação"]

    assert len(deliberacao) == 1
    assert "«Indeferido» só quando todos os pareceres são «Indeferido»" in deliberacao[0].valor
