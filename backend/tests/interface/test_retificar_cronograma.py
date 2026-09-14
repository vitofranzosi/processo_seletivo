"""O local de uma prova publicada se corrige pela tela (026, US1, FR-305).

**O achado que a feature encontrou no seu canário mais simples.** `location` é emitido no conteúdo
publicado por `publicacoes/application/publish_edital`, e até a `026` não estava declarado em
`EVENTO_PUBLICADO` — nenhum teste acusava, porque o guarda da forma confere **coleções** e não
campos. O campo existe no conteúdo, governa onde a pessoa comparece, e não tinha nem forma
declarada nem decisão de mutabilidade.

A `021` tem como critério de aceitação uma Retificação que altera o local; a tela não tinha o campo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain import validation
from processo_seletivo.interface.retificacao import campos_editaveis
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

LOCAL_PUBLICADO = "Campus Serra — Auditório"


def rascunho_com_local():
    """Dois Eventos: um com local declarado, e um sem.

    Os dois são necessários, e é o segundo cenário de aceitação da US1 que os exige: informar local
    onde não havia precisa ser distinguível de corrigir o que estava lá.
    """
    dados = complete_draft()
    dados["schedule"][0]["location"] = LOCAL_PUBLICADO
    segundo = dict(dados["schedule"][0])
    segundo["id"] = "00000000-0000-0000-0000-000000026001"
    segundo["type"] = "PROVA"
    segundo["description"] = "Prova objetiva"
    segundo["order"] = dados["schedule"][0]["order"] + 1
    segundo.pop("location", None)
    segundo["isRegistrationPeriod"] = False
    dados["schedule"].append(segundo)
    return dados


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_local()
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


def test_a_forma_publicada_declara_o_local_do_evento():
    """O campo é emitido e precisa ser declarado — é o achado, antes de ser a correção.

    Sem `admite_nulo`: `cronograma.Evento.location` é `CharField(blank=True, default="")` e
    `shared/canonical` registra que vazio significa **não declarado** — nunca `null`, nunca chave
    omitida. É a convenção que `duties` e `workload` do Perfil já seguem, e uma segunda convenção
    para texto faria a versão canônica admitir mais de uma forma.
    """
    local = next(campo for campo in validation.EVENTO_PUBLICADO if campo.nome == "location")
    assert local.tipo is str
    assert not local.admite_nulo


def test_a_tela_de_retificacao_oferece_o_local_do_evento(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Local" in corpo
    assert LOCAL_PUBLICADO in corpo
    # E o caminho normativo continua fora do HTML: a tela entrega referência opaca (FR-019).
    assert "/schedule/id=" not in corpo

    grupos = campos_editaveis(vigente.content)
    do_evento = next(g for g in grupos if g["tipo"] == "Evento")
    local = next(c for c in do_evento["campos"] if c["caminho"].endswith("/location"))
    assert local["tipo"] == "texto"
    assert local["valor"] == LOCAL_PUBLICADO


def test_corrigir_o_local_pela_tela_vira_replace_por_identidade(
    client, seletor_ligado, edital, vigente
):
    """SC-097 — a correção que hoje só se faz por chamada de API."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    evento = vigente.content["schedule"][0]
    caminho = f"/schedule/id={evento['id']}/location"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "Campus Vitória — Sala 204"}),
            "justificativa": "A sala da prova mudou.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-local-000001",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    retificacao = Retificacao.objects.get()
    alteracao = retificacao.alteracoes.get(target_path=caminho)
    assert alteracao.new_value == "Campus Vitória — Sala 204"


def test_a_conferencia_exibe_o_local_em_portugues(client, seletor_ligado, edital, vigente):
    """Quem homologa confere em português, e não em JSON Pointer (FR-019).

    `publicacoes/domain/alteracoes` já traduz `location` como "Local"; o que este teste confere é
    que o caminho de conferência realmente passa por ali, e não que o dicionário existe.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    evento = vigente.content["schedule"][0]
    caminho = f"/schedule/id={evento['id']}/location"

    corpo = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "Campus Vitória — Sala 204"}),
            "justificativa": "A sala da prova mudou.",
        },
    ).content.decode()

    assert "Local" in corpo
    assert "Campus Vitória — Sala 204" in corpo
    assert "location" not in corpo, "o nome técnico do campo não chega a quem confere"


def test_informar_local_onde_nao_havia_e_alteracao_de_valor_e_nao_acrescimo(
    client, seletor_ligado, edital, vigente
):
    """O segundo cenário de aceitação da US1, respondido pelo contrato.

    Com `location` **sempre presente** como `""` — a convenção que `publish_edital` documenta —,
    informar um local onde não havia é alteração de valor, e não acréscimo de campo. Não há caminho
    inexistente a endereçar, e por isso a gramática da `004` não precisa de regra nova.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    sem_local = vigente.content["schedule"][1]
    assert sem_local["location"] == "", "o Evento sem local publica string vazia, e nunca ausência"
    caminho = f"/schedule/id={sem_local['id']}/location"

    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{caminho: "Campus Serra — Sala 12"}),
            "justificativa": "Divulgação do local da segunda prova.",
            "confirmar": "1",
            "chave_idempotencia": "retificar-local-000002",
        },
    )
    assert resposta.status_code in (200, 302), resposta.content

    alteracao = Retificacao.objects.get().alteracoes.get(target_path=caminho)
    assert alteracao.operation == "REPLACE", "alteração de valor, e não acréscimo de campo"
