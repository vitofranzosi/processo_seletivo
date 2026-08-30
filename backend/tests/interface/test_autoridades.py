"""T083 e T085 — a autoridade signatária é escolhida, não digitada (FR-039, FR-044).

Era o campo mais hostil do produto: um UUID de trinta e seis caracteres, à mão, no ato de maior
consequência do sistema — e nome e cargo redigitados a cada publicação.

**São dois fluxos de publicação**, e cobrir só um deixaria o UUID digitado exatamente onde se
corrige um Edital já publicado.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.domain import autoridades
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.publicacao import create_retification, publish_original
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db(transaction=True)

ESCOLHIDA = autoridades.POR_CHAVE["reitoria"]


# ---------------------------------------------------------------------------
# O catálogo, e o que ele não pode conter
# ---------------------------------------------------------------------------


def test_o_catalogo_guarda_nome_cargo_e_identificador_e_nada_alem():
    """FR-044: o identificador é necessário — `Publicacao.signatory_id` o exige — e é o teto."""
    campos = {campo for autoridade in autoridades.CATALOGO for campo in vars(autoridade)}

    assert campos == {"chave", "identificador", "nome", "cargo"}
    for proibido in ("cpf", "matricula", "email", "telefone", "endereco", "foto"):
        assert proibido not in campos


def test_o_catalogo_nao_e_entidade_persistida():
    """FR-039: sem modelo, sem migration, sem tela de gestão, sem permissão nova."""
    from django.apps import apps

    nomes = {modelo.__name__.lower() for modelo in apps.get_models()}
    assert "autoridade" not in nomes
    assert "autoridadesignataria" not in nomes


def test_chave_fora_do_catalogo_nao_resolve():
    assert autoridades.escolher("inexistente") is None
    assert autoridades.escolher("") is None
    assert autoridades.escolher(None) is None


# ---------------------------------------------------------------------------
# Fluxo 1 — publicação do Edital
# ---------------------------------------------------------------------------


def _ate_homologado(api_client, manager_headers, process_payload):
    from tests.fixtures.edital import actor_headers, complete_draft

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparer = actor_headers("ana", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("bruno", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    return Edital.objects.get(pk=edital.pk)


def test_a_tela_de_publicar_oferece_escolha_e_nao_pede_uuid(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    identificar(client, "carla", ["publicador"])

    corpo = client.get(reverse("interface:ato", args=[edital.id, "publicar"])).content.decode()

    assert '<select id="signatario"' in corpo
    assert ESCOLHIDA.nome in corpo
    assert 'name="signatario_id"' not in corpo, "o UUID não é digitado"
    assert str(ESCOLHIDA.identificador) not in corpo, "o UUID não é sequer exibido"
    assert "formato UUID" not in corpo


def test_publicar_pela_escolha_registra_nome_cargo_e_identificador(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    identificar(client, "carla", ["publicador"])

    resposta = client.post(
        reverse("interface:ato", args=[edital.id, "publicar"]),
        {"chave_idempotencia": "ui-autoridade-1", "signatario": ESCOLHIDA.chave},
    )
    assert resposta.status_code == 302, resposta.content

    publicacao = Publicacao.objects.get(edital=edital)
    assert publicacao.signatory_name == ESCOLHIDA.nome
    assert publicacao.signatory_role == ESCOLHIDA.cargo
    assert str(publicacao.signatory_id) == str(ESCOLHIDA.identificador)


def test_autoridade_fora_do_catalogo_nao_e_aceita_em_novo_ato(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    identificar(client, "carla", ["publicador"])

    resposta = client.post(
        reverse("interface:ato", args=[edital.id, "publicar"]),
        {"chave_idempotencia": "ui-autoridade-2", "signatario": "autoridade-retirada"},
    )

    assert resposta.status_code == 422
    assert "Escolha a Autoridade Signatária" in resposta.content.decode()
    assert not Publicacao.objects.filter(edital=edital).exists()


def test_publicacao_ja_praticada_permanece_integra_se_a_autoridade_sair_do_catalogo(
    client, seletor_ligado, api_client, manager_headers, process_payload, monkeypatch
):
    """FR-046: o catálogo é a origem da escolha, não a fonte de verdade do que foi assinado.

    O ato persiste nome, cargo e identificador no momento em que ocorre, e é imutável.
    """
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    identificar(client, "carla", ["publicador"])
    client.post(
        reverse("interface:ato", args=[edital.id, "publicar"]),
        {"chave_idempotencia": "ui-autoridade-3", "signatario": ESCOLHIDA.chave},
    )

    # A autoridade é retirada do catálogo depois do ato.
    monkeypatch.setattr(autoridades, "POR_CHAVE", {})
    monkeypatch.setattr(autoridades, "CATALOGO", ())

    publicacao = Publicacao.objects.get(edital=edital)
    assert publicacao.signatory_name == ESCOLHIDA.nome
    assert publicacao.signatory_role == ESCOLHIDA.cargo


# ---------------------------------------------------------------------------
# Fluxo 2 — publicação da Retificação
# ---------------------------------------------------------------------------


def test_publicar_retificacao_tambem_escolhe_a_autoridade(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O fluxo que a análise cruzada encontrou fora da correção.

    Corrigir um Edital publicado passa por aqui: deixá-lo de fora manteria o UUID digitado
    exatamente onde a correção acontece.
    """
    from tests.fixtures.edital import actor_headers, caminho_perfil

    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = create_retification(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": caminho_perfil("name"), "newValue": "Outro"}],
    )
    # As transições exigem `If-Match` e chave de idempotência de ao menos 16 caracteres.
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers("ana", ["retificacao:submeter"], key="retificacao-autoridade-0002"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("bruno", ["retificacao:homologar"], key="retificacao-autoridade-0003"),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    identificar(client, "carla", ["publicador"])
    retificacao.refresh_from_db()

    corpo = client.get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    ).content.decode()
    assert '<select id="signatario"' in corpo
    assert 'name="signatario_id"' not in corpo

    resposta = client.post(
        reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"]),
        {"chave_idempotencia": "ui-ret-autoridade", "signatario": ESCOLHIDA.chave},
    )
    assert resposta.status_code == 302, resposta.content

    publicada = Publicacao.objects.filter(retificacao=retificacao).get()
    assert publicada.signatory_name == ESCOLHIDA.nome
    assert str(publicada.signatory_id) == str(ESCOLHIDA.identificador)
