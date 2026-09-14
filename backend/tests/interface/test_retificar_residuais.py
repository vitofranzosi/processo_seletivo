"""Os quatro campos que fecham a FR-304 sem exceção (026, fase 10).

Nenhum deles é canário: são o resto que o contrato, uma vez escrito, torna obrigatório. Com a
matriz aprovada **não existe "resto" para campo retificável** — a FR-304 exige caminho pela tela
para todos, e chamar os que sobram de "backlog derivado" era possível antes de a matriz existir.

`rounding/scale` e `rounding/mode` são metade do canário 4 **original**: a decisão de origem elegia
a regra classificatória como quarto canário, e a D-010 a trocou pelo sorteio. A endereçabilidade
destes dois paga parte do que a troca custou.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import MARCO, rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _campo(vigente, sufixo):
    grupos = campos_editaveis(vigente.content)
    return next(
        campo for grupo in grupos for campo in grupo["campos"] if campo["caminho"].endswith(sufixo)
    )


def campos(vigente, **alteracoes):
    grupos = campos_editaveis(vigente.content)
    do_formulario = [campo for grupo in grupos for campo in grupo["campos"]]
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{campo['referencia']}": campo["valor"] for campo in do_formulario}
    referencia = {campo["caminho"]: campo["referencia"] for campo in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def test_a_descricao_do_perfil_se_corrige(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    assert "Descrição" in corpo

    identificador = vigente.content["profiles"][0]["id"]
    campo = _campo(vigente, f"/profiles/id={identificador}/description")
    assert campo["tipo"] == "texto_longo"


def test_a_vigencia_do_fundamento_e_instante_e_nao_data(client, seletor_ligado, edital, vigente):
    """O modelo é `DateTimeField` e o snapshot grava `isoformat()`.

    A Retificação não tem tipo `DATA`; `INSTANTE` é o que já converte pelo fuso institucional, como
    o início do Evento.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    assert "Vigente desde" in corpo

    campo = _campo(vigente, "/normativeRule/effectiveFrom")
    assert campo["tipo"] == "instante"
    assert campo["valor"], "o valor publicado precisa chegar ao formulário"


def test_o_arredondamento_se_corrige_campo_a_campo(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Casas decimais da pontuação" in corpo
    assert "Como arredondar" in corpo
    assert "rounding" not in corpo, "o caminho normativo não chega ao HTML (FR-019)"

    modo = _campo(vigente, "/rounding/mode")
    assert modo["tipo"] == "referencia"
    assert [identificador for identificador, _ in modo["opcoes"]] == [
        "MEIO_PARA_CIMA",
        "MEIO_PARA_PAR",
        "TRUNCAR",
    ]


def test_corrigir_a_escala_do_arredondamento_vira_replace_por_identidade(
    client, seletor_ligado, edital, vigente
):
    """'Onde se lê duas casas, leia-se quatro' — a correção clássica da regra classificatória."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = next(p for p in vigente.content["profiles"] if p.get("classificationMilestones"))
    caminho = f"/profiles/id={perfil['id']}/classificationMilestones/id={MARCO}/rounding/scale"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "4"}),
            "justificativa": "A norma institucional exige quatro casas decimais.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-arredondamento-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    alteracao = Retificacao.objects.get().alteracoes.get(target_path=caminho)
    assert alteracao.new_value == 4
