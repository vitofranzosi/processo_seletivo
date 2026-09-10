"""A tela de Retificação alcança o quadro de vagas (025, US3, T068).

O Princípio VI diz que capacidade que nenhuma interface alcança não está entregue. Duas metades:
alterar a linha que já existe, e **acrescentar** a que não existe — esta última é a que faz o
acervo inteiro poder ganhar quadro, porque todo Edital publicado antes desta feature tem a coleção
vazia, e alterar linha existente não alcança quem não tem linha nenhuma.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERFIL = "00000000-0000-0000-0000-000000000401"
PPI = "00000000-0000-0000-0000-0000002501b1"
GERAL = "00000000-0000-0000-0000-000000252001"
LINHA_PPI = "00000000-0000-0000-0000-000000252003"


def rascunho_com_quadro():
    dados = complete_draft()
    perfil = dados["profiles"][0]
    perfil["immediateVacancies"] = 80
    perfil["competitionModalities"] = [
        {"id": PPI, "code": "PPI", "name": "Pretos, pardos e indígenas"}
    ]
    perfil["vacancyTable"] = [
        {"id": GERAL, "modalityId": None, "immediateVacancies": 60},
        {"id": LINHA_PPI, "modalityId": PPI, "immediateVacancies": 20},
    ]
    return dados


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_quadro()
    )


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


def test_a_tela_oferece_a_colecao_do_quadro_com_a_modalidade_como_escolha(
    client, seletor_ligado, edital, vigente
):
    """`modalityId` aparece como escolha entre as Modalidades, e nunca como UUID digitado.

    Digitar UUID à mão faria um erro de digitação mudar em silêncio o que a linha significa —
    transformar a linha da PPI na linha da PcD é publicar outra repartição (FR-170, FR-171).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Linha do quadro de vagas" in corpo
    assert "Ampla concorrência" in corpo
    assert "Pretos, pardos e indígenas" in corpo
    # E o caminho normativo continua fora do HTML: a tela entrega referência opaca (FR-019).
    assert "vacancyTable" not in corpo

    grupos = campos_editaveis(vigente.content)
    da_linha = next(g for g in grupos if g["tipo"] == "Linha do quadro de vagas")
    modalidade = next(c for c in da_linha["campos"] if c["caminho"].endswith("/modalityId"))
    assert modalidade["tipo"] == "referencia"
    assert [identificador for identificador, _ in modalidade["opcoes"]] == [PPI]
    # E a opção vazia diz o que ela **é** (E2E25-006). "Sem restrição" — o rótulo genérico do
    # Documento Exigido — diria que a linha não se restringe a lista nenhuma, quando ela é
    # precisamente a lista de que todos participam.
    assert modalidade["rotulo_do_vazio"] == "Ampla concorrência"
    assert "Sem restrição" not in corpo[corpo.index("Linha do quadro de vagas") :]


def test_alterar_a_quantidade_pela_tela_vira_replace_por_identidade(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    quantidade = f"/profiles/id={PERFIL}/vacancyTable/id={LINHA_PPI}/immediateVacancies"
    total = f"/profiles/id={PERFIL}/immediateVacancies"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{quantidade: "18", total: "78"}),
            "justificativa": "Redução da reserva",
            "confirmar": "1",
            "chave_idempotencia": "retificar-quadro-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    retificacao = Retificacao.objects.get()
    caminhos = {alteracao.target_path for alteracao in retificacao.alteracoes.all()}
    assert quantidade in caminhos
    assert total in caminhos


def test_a_tela_acrescenta_linha_ao_quadro_de_um_perfil_que_nao_tem(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A metade que faz o acervo poder ganhar quadro: todo Edital anterior tem a coleção vazia."""
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert base.content["profiles"][0]["vacancyTable"] == [], "o Edital nasce sem quadro"

    identificar(client, "ana.elaboradora", ["elaborador"])
    fragmento = client.get(
        reverse("interface:fragmento-retificacao-linha-do-quadro", args=[edital.id]),
        {"indice": "7"},
    )
    assert fragmento.status_code == 200
    marcacao = fragmento.content.decode()
    assert 'name="novo-linha-do-quadro-7-profileId"' in marcacao
    assert 'name="novo-linha-do-quadro-7-modalityId"' in marcacao
    assert "<select" in marcacao, "as duas referências são escolha, e não UUID digitado"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(base),
            "novo-linha-do-quadro-7-profileId": str(base.content["profiles"][0]["id"]),
            "novo-linha-do-quadro-7-modalityId": "",
            "novo-linha-do-quadro-7-immediateVacancies": "1",
            "justificativa": "Publicação do quadro de vagas",
            "confirmar": "1",
            "chave_idempotencia": "retificar-quadro-000002",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content
    assert Retificacao.objects.exists(), resposta.content.decode()[-3000:]

    retificacao = Retificacao.objects.get()
    acrescimo = retificacao.alteracoes.get(operation="ADD")
    perfil_id = base.content["profiles"][0]["id"]
    assert acrescimo.target_path == f"/profiles/id={perfil_id}/vacancyTable/-"
    assert acrescimo.new_value["modalityId"] is None, "vazio é a linha geral"
    assert acrescimo.new_value["immediateVacancies"] == 1
    assert re.fullmatch(r"[0-9a-f-]{36}", acrescimo.new_value["id"]), "nasce com identidade própria"


def test_a_linha_acrescentada_sem_quantidade_e_recusada_e_nao_vira_zero(
    client, seletor_ligado, edital, vigente
):
    """Em branco é "não declarado", e nunca zero — **também** no acréscimo (FR-159, D-006).

    Aqui a linha só existe porque alguém clicou para acrescentá-la, e por isso a regra difere da
    composição: engolir o vazio como `0` publicaria "este recorte tem zero vagas", que é afirmação
    normativa que ninguém fez; descartá-la em silêncio faria o acréscimo pedido não acontecer sem
    dizer por quê. A resposta certa é a recusa que ensina o que fazer.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente),
            "novo-linha-do-quadro-4-profileId": str(PERFIL),
            "novo-linha-do-quadro-4-modalityId": "",
            "novo-linha-do-quadro-4-immediateVacancies": "",
            "justificativa": "Acréscimo sem número",
            "confirmar": "1",
            "chave_idempotencia": "retificar-quadro-branco-01",
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Vagas imediatas: a linha do quadro precisa dizer quantas vagas" in corpo
    assert "digite 0" in corpo
    assert not Retificacao.objects.exists(), "nenhum ato nasce de uma linha pela metade"


def test_a_linha_acrescentada_com_zero_declara_zero(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Quem quer dizer zero digita zero, e aí o zero **é** a declaração (D-006).

    O Perfil deste Edital não declarava quadro e oferece uma vaga. A Retificação declara a linha
    geral com `0` **e** reduz o total a `0` no mesmo ato — os dois movimentos que a FR-161 amarra —,
    e o `0` atravessa como quantidade declarada, e não como ausência.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil_id = base.content["profiles"][0]["id"]

    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(base, **{f"/profiles/id={perfil_id}/immediateVacancies": "0"}),
            "novo-linha-do-quadro-4-profileId": str(perfil_id),
            "novo-linha-do-quadro-4-modalityId": "",
            "novo-linha-do-quadro-4-immediateVacancies": "0",
            "justificativa": "Ampla concorrência declarada como zero",
            "confirmar": "1",
            "chave_idempotencia": "retificar-quadro-zero-0001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content
    assert Retificacao.objects.exists(), resposta.content.decode()[-2000:]

    acrescimo = Retificacao.objects.get().alteracoes.get(operation="ADD")
    assert acrescimo.new_value["immediateVacancies"] == 0, "zero digitado é zero declarado"
    assert acrescimo.new_value["modalityId"] is None


def test_desistir_do_acrescimo_nao_e_recusa(client, seletor_ligado, edital, vigente):
    """A linha em branco por inteiro é a que a pessoa acrescentou e desistiu de preencher."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente),
            "novo-linha-do-quadro-4-profileId": "",
            "novo-linha-do-quadro-4-modalityId": "",
            "novo-linha-do-quadro-4-immediateVacancies": "",
            "justificativa": "Nada a acrescentar",
        },
    )

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "a linha do quadro precisa dizer" not in corpo
