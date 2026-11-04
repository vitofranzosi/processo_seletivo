"""Conferir na Caixa antes de agir — sob demanda, e nunca a cada renderização (116, US6).

**FR-3644 e FR-3645.** O botão está junto do campo do concurso, no método do marco e no comum, e na
tela do sorteio antes de congelar. O resultado vem no lugar, com a mesma mensagem que o ato daria,
nada é gravado, e abrir as três telas não consulta a fonte. A conferência é leitura, e não ato: a
permissão é a de ver a tela de onde ela é pedida.
"""

import copy
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from tests.fixtures.sorteio import METODO, certame_de_sorteio
from tests.interface.conftest import identificar
from tests.interface.test_compor import PERFIL
from tests.interface.test_compor_classificacao import marco_form

pytestmark = [pytest.mark.integration]

URL = "interface:fragmento-conferir-referencia"


def _compor_com_sorteio(client, edital, **extra):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]),
        marco_form(**{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **extra}),
    )
    assert resposta.status_code == 302, resposta.content
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
    ).content.decode()


def _conferir_na_composicao(client, edital, prefixo, ocorrencia, fonte="Loteria Federal"):
    return client.get(
        reverse(URL),
        {
            "edital": str(edital.id),
            "prefixo": prefixo,
            f"{prefixo}-source": fonte,
            f"{prefixo}-occurrence": ocorrencia,
            f"{prefixo}-occurrenceAt": "2026-12-06T19:00:00-03:00",
        },
    )


@pytest.mark.django_db
def test_o_botao_esta_no_metodo_do_marco_e_no_comum(client, com_etapas, caixa):
    corpo = _compor_com_sorteio(client, com_etapas)

    url = reverse(URL)
    assert corpo.count(f'hx-get="{url}?edital={com_etapas.id}&amp;prefixo=') == 2
    assert f'id="conferencia-marco-{PERFIL}-0-draw"' in corpo
    assert 'id="conferencia-edital-draw"' in corpo
    assert "Conferir na Caixa" in corpo


@pytest.mark.django_db
def test_renderizar_as_tres_telas_nao_consulta_a_fonte(
    client, seletor_ligado, com_etapas, gestor, api_client, manager_headers, process_payload, caixa
):
    """FR-3644: a composição do marco, a do comum e a tela do sorteio, abertas sem clique."""
    _compor_com_sorteio(client, com_etapas)
    client.get(reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]))
    metodo = copy.deepcopy(METODO)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": "6116",
            "occurrenceAt": (timezone.now() + timedelta(days=10)).isoformat(),
        }
    )
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    chamadas_da_publicacao = caixa.chamadas
    identificar(client, "maria", [])
    corpo = client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()

    assert "Conferir na Caixa" in corpo
    assert caixa.chamadas == chamadas_da_publicacao


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("ocorrencia", "classe", "frase"),
    [
        ("5000", "impede", "já foi realizado, em 26/08/2015"),
        ("6113", "impede", "já foi realizado, em 28/10/2026"),
        ("6116", "informa", "ainda não realizado na consulta de"),
        ("6106-9", "impede", "informe só o número do concurso"),
    ],
)
def test_a_resposta_diz_a_situacao_no_lugar(client, com_etapas, caixa, ocorrencia, classe, frase):
    caixa.usar_gravacao()
    prefixo = f"marco-{PERFIL}-0-draw"

    resposta = _conferir_na_composicao(client, com_etapas, prefixo, ocorrencia)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert f'class="resultado-da-conferencia {classe}"' in corpo
    assert frase in corpo


@pytest.mark.django_db
def test_inconclusivo_adverte(client, com_etapas, caixa):
    caixa.fora_do_ar()
    corpo = _conferir_na_composicao(client, com_etapas, "edital-draw", "6116").content.decode()
    assert 'class="resultado-da-conferencia adverte"' in corpo
    assert "a Caixa não respondeu a tempo" in corpo


@pytest.mark.django_db
def test_vale_as_mesmas_chamadas_do_ato(client, com_etapas, caixa):
    caixa.usar_gravacao()
    _conferir_na_composicao(client, com_etapas, "edital-draw", "6113")
    assert (caixa.chamadas_ao_ultimo, caixa.chamadas_por_numero) == (1, [6113])


@pytest.mark.django_db
def test_nada_e_gravado(client, com_etapas, caixa):
    revisao = com_etapas.revision
    registros = RegistroAuditoria.objects.count()

    _conferir_na_composicao(client, com_etapas, "edital-draw", "6116")

    com_etapas.refresh_from_db()
    assert com_etapas.revision == revisao
    assert RegistroAuditoria.objects.count() == registros


@pytest.mark.django_db
def test_fonte_que_nao_confere_diz_que_nao_ha_o_que_conferir(client, com_etapas, caixa):
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    with pytest.MonkeyPatch.context() as sem_conferencia:
        sem_conferencia.setattr(LoteriaFederal, "SABE_CONFERIR", False)
        corpo = _conferir_na_composicao(client, com_etapas, "edital-draw", "6116").content.decode()
    assert "não é conferida antes dos atos" in corpo
    assert caixa.chamadas == 0


@pytest.mark.django_db
def test_permissao_negada_por_padrao(client, seletor_ligado, edital, caixa):
    """Quem não compõe não confere pela composição, e o Edital alheio é 404."""
    identificar(client, "auditor", ["auditor"])
    resposta = _conferir_na_composicao(client, edital, "edital-draw", "6116")
    assert resposta.status_code == 403
    assert caixa.chamadas == 0


@pytest.mark.django_db
def test_sem_sessao_nao_confere(client, seletor_ligado, edital, caixa):
    resposta = _conferir_na_composicao(client, edital, "edital-draw", "6116")
    assert resposta.status_code in (302, 403, 404)
    assert caixa.chamadas == 0


@pytest.mark.django_db
def test_prefixo_que_nao_e_do_formulario_e_recusado(client, com_etapas, caixa):
    resposta = client.get(reverse(URL), {"edital": str(com_etapas.id), "prefixo": "x\n-draw"})
    assert resposta.status_code == 404
    assert caixa.chamadas == 0


@pytest.mark.django_db(transaction=True)
def test_na_tela_do_sorteio_le_o_metodo_publicado(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, caixa
):
    metodo = copy.deepcopy(METODO)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": "6113",
            "occurrenceAt": (timezone.now() + timedelta(days=10)).isoformat(),
        }
    )
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    identificar(client, "maria", [])
    caixa.usar_gravacao()

    resposta = client.get(
        reverse(URL), {"edital": str(certame["edital"].id), "marco": str(certame["marco"])}
    )

    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "Não é possível congelar a relação: o concurso 6113" in corpo
