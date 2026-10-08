"""A autoridade é escolhida entre as da unidade do Edital, vigentes hoje (060, FR-1125 a FR-1127).

Substitui os testes do catálogo declarado da `007` (T083, T085), que a 060 revogou. O que eles
provavam continua valendo — escolher, e não digitar; os dois fluxos de publicação; o ato que não
muda quando a autoridade sai de uso — e passa a valer contra o registro de autoridades, por unidade
e por vigência.

**São dois fluxos de publicação de Edital**, e cobrir só um deixaria a escolha antiga exatamente
onde se corrige um Edital já publicado.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade
from tests.fixtures.autoridades import (
    AUTORIDADE_DA_SUITE,
    registrar_autoridade,
    registrar_unidade,
)
from tests.fixtures.publicacao import create_retification, publish_original
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db(transaction=True)


def _hoje():
    return timezone.now().astimezone(ZONA).date()


def _visivel(corpo):
    """O texto que a pessoa lê — sem marcação, e portanto sem o `value` das opções."""
    return re.sub(r"<[^>]+>", " ", corpo)


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


def _publicar(client, edital, autoridade, chave):
    return client.post(
        reverse("interface:ato", args=[edital.id, "publicar"]),
        {"chave_idempotencia": chave, "signatario": str(autoridade)},
    )


# ---------------------------------------------------------------------------
# A escolha oferecida
# ---------------------------------------------------------------------------


def test_a_tela_oferece_so_as_vigentes_da_unidade_e_nao_mostra_o_identificador(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-1125, FR-1117, UX-148."""
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    cefor = Unidade.objects.get(codigo="cefor")
    com_portaria = registrar_autoridade(
        cefor, cargo="Reitor", nome="João Exemplo", ato_de_nomeacao="Portaria nº 7/2026"
    )
    encerrada = registrar_autoridade(
        cefor, cargo="Reitora anterior", fim=_hoje() - timedelta(days=1)
    )
    futura = registrar_autoridade(
        cefor, cargo="Reitora seguinte", inicio=_hoje() + timedelta(days=7)
    )
    de_outra_unidade = registrar_autoridade(registrar_unidade("serra"), cargo="Diretor da Serra")
    identificar(client, "carla", ["publicador"])

    corpo = client.get(reverse("interface:ato", args=[edital.id, "publicar"])).content.decode()

    assert '<select id="signatario"' in corpo
    assert f'value="{com_portaria.pk}"' in corpo
    assert "João Exemplo — Reitor · Portaria nº 7/2026" in corpo, "UX-148: o rótulo distingue"
    for fora in (encerrada, futura, de_outra_unidade):
        assert str(fora.pk) not in corpo
    assert str(com_portaria.pk) not in _visivel(corpo), "o identificador não é exibido"
    assert 'name="signatario_id"' not in corpo, "e não é digitado"


def test_sem_autoridade_vigente_a_tela_diz_por_que_e_nao_oferece_o_botao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-1127: a recusa certa é anunciada antes do clique."""
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    ontem = _hoje() - timedelta(days=1)
    AutoridadeHabilitada.objects.filter(unidade__codigo="cefor").update(
        fim_vigencia=ontem, encerrada_em=timezone.now(), encerrada_por="teste"
    )
    identificar(client, "carla", ["publicador"])

    corpo = client.get(reverse("interface:ato", args=[edital.id, "publicar"])).content.decode()

    assert "Nenhuma autoridade vigente para Cefor hoje" in corpo
    assert "permissão de gerir autoridades" in corpo
    assert "Confirmar: Publicar" not in corpo
    assert '<select id="signatario"' not in corpo


# ---------------------------------------------------------------------------
# O ato, e as recusas do domínio
# ---------------------------------------------------------------------------


def test_publicar_pela_escolha_congela_a_autoridade_e_a_unidade(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-1128: nome, cargo, ato de nomeação, identificador e a unidade como estavam no ato."""
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    autoridade = registrar_autoridade(
        Unidade.objects.get(codigo="cefor"),
        cargo="Reitora",
        nome="Maria Exemplo",
        ato_de_nomeacao="Portaria nº 1/2026",
    )
    identificar(client, "carla", ["publicador"])

    resposta = _publicar(client, edital, autoridade.pk, "ui-autoridade-1")
    assert resposta.status_code == 302, resposta.content

    publicacao = Publicacao.objects.get(edital=edital)
    assert (
        publicacao.signatory_id,
        publicacao.signatory_name,
        publicacao.signatory_role,
        publicacao.signatory_appointment,
    ) == (autoridade.pk, "Maria Exemplo", "Reitora", "Portaria nº 1/2026")
    assert (publicacao.unidade_codigo, publicacao.unidade_sigla) == ("cefor", "Cefor")
    autoridade.refresh_from_db()
    assert autoridade.usada_em is not None, "o primeiro uso fica gravado"


@pytest.mark.parametrize(
    "caso, codigo",
    [
        ("de outra unidade", "autoridade_indisponivel"),
        ("inexistente", "autoridade_indisponivel"),
        ("encerrada ontem", "autoridade_fora_de_vigencia"),
        ("futura", "autoridade_fora_de_vigencia"),
        ("vazia", "signatario_obrigatorio"),
    ],
)
def test_a_recusa_e_do_dominio_e_nada_e_gravado(
    caso, codigo, client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-1126: o formulário forjado chega ao comando, e o comando recusa."""
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    cefor = Unidade.objects.get(codigo="cefor")
    escolhida = {
        "de outra unidade": lambda: registrar_autoridade(registrar_unidade("serra")).pk,
        "inexistente": lambda: "00000000-0000-0000-0000-00000000dead",
        "encerrada ontem": lambda: registrar_autoridade(cefor, fim=_hoje() - timedelta(days=1)).pk,
        "futura": lambda: registrar_autoridade(cefor, inicio=_hoje() + timedelta(days=1)).pk,
        "vazia": lambda: "",
    }[caso]()
    identificar(client, "carla", ["publicador"])

    resposta = _publicar(client, edital, escolhida, f"ui-recusa-{codigo[:12]}")

    assert resposta.status_code == 422
    assert not Publicacao.objects.filter(edital=edital).exists()
    mensagens = {
        "autoridade_indisponivel": "não está habilitada para esta unidade",
        "autoridade_fora_de_vigencia": "não está vigente hoje",
        "signatario_obrigatorio": "Escolha a autoridade",
    }
    assert mensagens[codigo] in resposta.content.decode()


def test_a_api_recusa_nome_e_cargo_enviados_por_quem_publica(
    api_client, manager_headers, process_payload
):
    """R-014: o contrato aceita só o identificador; aceitar e ignorar seria mentir."""
    from tests.fixtures.edital import actor_headers

    edital = _ate_homologado(api_client, manager_headers, process_payload)
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": {"authorityId": str(AUTORIDADE_DA_SUITE), "name": "Outra", "role": "X"}},
        format="json",
        **actor_headers("publicador", ["edital:publicar"], if_match=4),
    )

    # 422 `invalid_payload`, como toda recusa de validação da API (`shared/api/problems.py`).
    assert resposta.status_code == 422
    assert resposta.json()["code"] == "invalid_payload"
    assert not Publicacao.objects.filter(edital=edital).exists()


def test_a_publicacao_nao_muda_quando_a_autoridade_e_encerrada_e_a_unidade_renomeada(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-1129: o registro é a origem da escolha, não a fonte de verdade do que foi assinado."""
    edital = _ate_homologado(api_client, manager_headers, process_payload)
    autoridade = registrar_autoridade(Unidade.objects.get(codigo="cefor"), cargo="Reitora")
    identificar(client, "carla", ["publicador"])
    _publicar(client, edital, autoridade.pk, "ui-autoridade-3")
    publicacao = Publicacao.objects.get(edital=edital)
    documento = bytes(publicacao.documento.bytes)

    AutoridadeHabilitada.objects.filter(pk=autoridade.pk).update(
        fim_vigencia=_hoje(), encerrada_em=timezone.now(), encerrada_por="teste"
    )
    Unidade.objects.filter(codigo="cefor").update(nome="Outro nome", sigla="Outra")

    publicacao.refresh_from_db()
    assert (publicacao.signatory_role, publicacao.unidade_sigla) == ("Reitora", "Cefor")
    assert bytes(publicacao.documento.bytes) == documento


# ---------------------------------------------------------------------------
# O segundo fluxo — a Retificação
# ---------------------------------------------------------------------------


def test_publicar_retificacao_tambem_escolhe_entre_as_da_unidade(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Corrigir um Edital publicado passa por aqui, com a mesma escolha e a mesma conferência."""
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
    de_outra_unidade = registrar_autoridade(registrar_unidade("serra"))
    identificar(client, "carla", ["publicador"])
    retificacao.refresh_from_db()
    url = reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])

    corpo = client.get(url).content.decode()
    assert '<select id="signatario"' in corpo
    assert str(de_outra_unidade.pk) not in corpo

    recusada = client.post(
        url, {"chave_idempotencia": "ui-ret-outra", "signatario": str(de_outra_unidade.pk)}
    )
    assert recusada.status_code == 422

    resposta = client.post(
        url, {"chave_idempotencia": "ui-ret-autoridade", "signatario": str(AUTORIDADE_DA_SUITE)}
    )
    assert resposta.status_code == 302, resposta.content
    publicada = Publicacao.objects.filter(retificacao=retificacao).get()
    assert publicada.signatory_id == AUTORIDADE_DA_SUITE
    assert publicada.unidade_codigo == "cefor"
