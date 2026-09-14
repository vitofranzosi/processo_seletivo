"""A janela nova vale para o que vier, e o recurso já interposto fica intacto (026, US3).

A fronteira é o que importa: retificar o prazo não pode mover a janela de quem já recorreu — o
recurso gravou a sua, e é sob ela que a tempestividade dele foi julgada.
"""

import pytest

from processo_seletivo.editais.domain.perfis import ProfileValidationError, _validar_janela_recursal
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    retify,
)
from tests.fixtures.snapshot import MARCO, rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


def _base_do_marco(conteudo):
    perfil = next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))
    return f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}"


def test_o_prazo_corrigido_vigora_e_a_versao_anterior_continua_legivel(api_client, edital):
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"{_base_do_marco(original.content)}/appealWindow/durationDays"
    marco = original.content["profiles"][0]["classificationMilestones"][0]
    assert marco["appealWindow"]["durationDays"] == 5

    retify(api_client, edital, [{"operation": "REPLACE", "targetPath": caminho, "newValue": 10}])

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    novo = vigente.content["profiles"][0]["classificationMilestones"][0]
    assert novo["appealWindow"]["durationDays"] == 10
    assert novo["appealWindow"]["unit"] == "DIAS_CORRIDOS", "a contagem atravessa intacta"
    assert novo["appealWindow"]["admits"] is True

    original.refresh_from_db()
    antes = original.content["profiles"][0]["classificationMilestones"][0]
    assert antes["appealWindow"]["durationDays"] == 5, (
        "a janela sob a qual alguém recorreu foi reescrita — publicação é ato imutável"
    )


def test_prazo_de_zero_dias_nao_e_prazo(api_client, edital):
    """A regra existia e alcançava um caminho só — este teste é o outro caminho.

    `validate_classification_milestones` recusa a janela incomputável na **elaboração** do Perfil,
    e a publicação nunca a conferia: uma Retificação com `durationDays: 0` publicava sem recusa
    alguma, e o candidato leria um prazo de zero dias. Quem descobriu foi este canário, ao levar o
    campo para a tela — oferecer um número que ninguém confere é publicar, pela via
    administrativa, o que a via de elaboração recusa.

    Com o achado no lugar, a recusa acontece **na criação** da Retificação: é ali que
    `retificacoes` confere o conteúdo resultante, e é o mais cedo que ela pode acontecer.
    """
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"{_base_do_marco(original.content)}/appealWindow/durationDays"

    problema = create_retification(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": caminho, "newValue": 0}],
        esperar=422,
    )
    assert "prazo de zero dias não é prazo" in problema["detail"]

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    marco = vigente.content["profiles"][0]["classificationMilestones"][0]
    assert marco["appealWindow"]["durationDays"] == 5, "o prazo publicado não foi tocado"


def test_contagem_que_o_calculo_nao_interpreta_e_recusada_na_retificacao(api_client, edital):
    """A outra metade da mesma regra, pelo mesmo caminho.

    Dias úteis exigiriam o calendário de dias sem expediente, que o Edital não publica — e
    contá-los sem ele produziria um prazo errado com aparência de exato.
    """
    original = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"{_base_do_marco(original.content)}/appealWindow/unit"

    problema = create_retification(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": caminho, "newValue": "DIAS_UTEIS"}],
        esperar=422,
    )
    assert "dias corridos" in problema["detail"]


def test_a_regra_da_janela_e_a_mesma_dos_dois_lados():
    """O domínio é o dono da coerência, e a interface não reescreve a regra.

    **A regra é permissiva num ponto, e registrá-lo importa**: marco que declara não admitir
    recurso e ainda assim traz duração **não é recusado** — `_validar_janela_recursal` retorna
    antes de olhar a duração. O comentário do domínio chama isso de contradição, e a validação não
    a impede.

    Este teste não inventa a recusa que falta: ele fixa o comportamento real, para que uma
    mudança futura seja decisão e não acidente. Endurecer a regra é decisão normativa — vale para
    a elaboração também, e não só para a Retificação.
    """
    _validar_janela_recursal({"admits": False, "durationDays": 5, "unit": "DIAS_CORRIDOS"})

    with pytest.raises(ProfileValidationError, match="prazo de zero dias não é prazo"):
        _validar_janela_recursal({"admits": True, "durationDays": 0, "unit": "DIAS_CORRIDOS"})
    with pytest.raises(ProfileValidationError, match="dias corridos"):
        _validar_janela_recursal({"admits": True, "durationDays": 5, "unit": "DIAS_UTEIS"})
    with pytest.raises(ProfileValidationError, match="não é computável"):
        _validar_janela_recursal({"admits": True, "unit": "DIAS_CORRIDOS"})
