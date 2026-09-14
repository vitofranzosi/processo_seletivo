"""Os requisitos de participação se corrigem pela tela (026, US2, FR-306).

**É o campo que decide quem pode concorrer**, e até a `026` só se corrigia por chamada de API — o
que a Constituição não admite como jornada concluída e que nenhum servidor do Cefor tem como
praticar.

É também o primeiro canário de **coleção de texto**, e não de escalar. O que ele obriga o desenho
a responder: item de lista de texto não tem identidade estável, e "o terceiro requisito" não é
endereçar — é contar. A decisão registrada no contrato é que **a lista inteira é a unidade
endereçável**, e um ato que diz "onde se lê, leia-se" nomeia a lista.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

REQUISITOS = ["Diploma de graduação", "Registro no conselho profissional"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    rascunho = complete_draft()
    rascunho["profiles"][0]["requirements"] = list(REQUISITOS)
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def campos(vigente, **alteracoes):
    grupos = campos_editaveis(vigente.content)
    do_formulario = [campo for grupo in grupos for campo in grupo["campos"]]
    enviados = {"base": str(vigente.id)}
    enviados |= {f"campo:{campo['referencia']}": campo["valor"] for campo in do_formulario}
    referencia = {campo["caminho"]: campo["referencia"] for campo in do_formulario}
    enviados.update({f"campo:{referencia[c]}": valor for c, valor in alteracoes.items()})
    return enviados


def test_a_tela_oferece_a_lista_inteira_com_um_requisito_por_linha(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Requisitos de participação" in corpo
    for requisito in REQUISITOS:
        assert requisito in corpo
    # A instrução fica **junto do campo**, e não escondida: sem ela a caixa de texto é ambígua —
    # quem escreve não sabe se a lista é um parágrafo ou uma enumeração.
    assert "Um requisito por linha" in corpo

    grupos = campos_editaveis(vigente.content)
    do_perfil = next(g for g in grupos if g["tipo"] == "Perfil")
    campo = next(c for c in do_perfil["campos"] if c["caminho"].endswith("/requirements"))
    assert campo["tipo"] == "lista_de_texto"
    assert campo["valor"] == "\n".join(REQUISITOS)


def test_corrigir_o_texto_de_um_requisito_substitui_a_lista_inteira(
    client, seletor_ligado, edital, vigente
):
    """SC-098 — e a decisão de desenho, verificada.

    O ato registra **um** `REPLACE` sobre a lista, e não dois sobre posições: a lista é a unidade
    endereçável porque o item não tem identidade a que apontar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = vigente.content["profiles"][0]
    caminho = f"/profiles/id={perfil['id']}/requirements"
    corrigidos = ["Diploma de graduação em Computação", "Registro no conselho profissional"]

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "\n".join(corrigidos)}),
            "justificativa": "A exigência de diploma estava genérica demais.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-requisitos-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    alteracoes = list(Retificacao.objects.get().alteracoes.all())
    assert [a.target_path for a in alteracoes] == [caminho], "um ato sobre a lista, e não por item"
    assert alteracoes[0].new_value == corrigidos


def test_linha_em_branco_nao_vira_requisito_vazio(client, seletor_ligado, edital, vigente):
    """`""` publicado afirmaria que existe uma exigência sem texto.

    Quem edita numa caixa de texto deixa linha em branco o tempo todo — entre itens, no fim. Engolir
    isso como requisito publicaria uma exigência que ninguém escreveu.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = vigente.content["profiles"][0]
    caminho = f"/profiles/id={perfil['id']}/requirements"

    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "Diploma de graduação\n\n  \nOutra exigência\n"}),
            "justificativa": "Acréscimo de exigência.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-requisitos-000002",
        },
    )
    alteracao = Retificacao.objects.get().alteracoes.get(target_path=caminho)
    assert alteracao.new_value == ["Diploma de graduação", "Outra exigência"]


def test_a_conferencia_nomeia_o_perfil_e_nao_o_caminho_normativo(
    client, seletor_ligado, edital, vigente
):
    """Quem homologa lê o Perfil e o que mudou, e nunca `/profiles/id=…/requirements`."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = vigente.content["profiles"][0]
    caminho = f"/profiles/id={perfil['id']}/requirements"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "Diploma de graduação em Computação"}),
            "justificativa": "Correção da exigência.",
        },
    ).content.decode()

    assert "Requisitos de participação" in corpo
    assert perfil["code"] in corpo
    assert "/profiles/id=" not in corpo


def test_editar_outro_campo_nao_mexe_na_lista(client, seletor_ligado, edital, vigente):
    """O achado da revisão: o formulário envia **todos** os campos.

    A caixa de texto não é representação reversível de qualquer lista — espaço nas pontas some,
    item que não é texto vira texto, quebra de linha dentro de um item o parte em dois. Comparando
    o convertido com o valor publicado, corrigir a denominação de um Perfil emitiria junto um
    `REPLACE` dos requisitos que ninguém pediu.

    A comparação passou a ser entre as duas **formas do formulário**: "não toquei" volta a
    significar "nada mudou".
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    perfil = vigente.content["profiles"][0]

    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{f"/profiles/id={perfil['id']}/name": "Outra denominação"}),
            "justificativa": "Correção da denominação.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-requisitos-000003",
        },
    )

    caminhos = {a.target_path for a in Retificacao.objects.get().alteracoes.all()}
    assert caminhos == {f"/profiles/id={perfil['id']}/name"}, (
        "editar a denominação levou junto outro campo"
    )


def test_lista_com_espaco_nas_pontas_nao_vira_alteracao_sozinha(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O caso concreto que a comparação crua acusaria: `['  Diploma  ']` publicado.

    A ida e volta o normaliza, e a comparação crua chamaria isso de correção. Não é: ninguém
    escreveu nada, e o ato registraria uma mudança que não houve.
    """
    rascunho = complete_draft()
    rascunho["profiles"][0]["requirements"] = ["  Diploma de graduação  "]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente),
            "justificativa": "Nada mudou.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-requisitos-000004",
        },
    )
    assert not Retificacao.objects.exists(), "uma Retificação nasceu sem ninguém ter alterado nada"


def test_a_forma_publicada_exige_que_cada_requisito_seja_texto():
    """A restrição que faltava, e que torna a caixa de texto uma representação fiel.

    Sem ela a API aceitava qualquer JSON dentro da lista — número, objeto, outra lista —, e o que
    se publicava não tinha como ser corrigido pelo canal do ator sem se corromper.
    """
    from processo_seletivo.editais.domain import validation

    campo = next(c for c in validation.PERFIL_PUBLICADO if c.nome == "requirements")
    assert campo.tipo is list
    assert campo.tipo_do_item is str
