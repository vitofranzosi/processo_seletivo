"""Quem pode divulgar, quem não pode, e o que cada recusa revela (FR-024 a FR-026, FR-056).

**A capacidade não decorre de nenhuma outra**, e é isso que o primeiro grupo prende: emitir o ato
constitui a ordem; divulgá-lo a torna pública. São atos de autoridades distintas, e o presidente que
emitiu não ganha o segundo por ter praticado o primeiro (SC-014).

**As duas recusas dizem coisas diferentes de propósito.** Falta de capacidade é 403 — a recusa é
sobre o ator, e escondê-la atrás de "não encontrado" faria a tela mentir sobre por que não abre.
Escopo institucional alheio é 404: quem não alcança não deve sequer saber que aquilo existe.
"""

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.authorization, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=55,
        codigo="0755",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=601,
    )


def _previa(cenario):
    return reverse(
        "interface:previa-de-publicacao",
        args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
    )


def _confirmar(cenario):
    return reverse(
        "interface:publicar-resultado",
        args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
    )


def _historico(cenario):
    return reverse("interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]])


def test_quem_tem_a_capacidade_abre_a_previa(client, seletor_ligado, cenario):
    identificar(client, "paula.publicadora", ["publicador"])

    assert client.get(_previa(cenario)).status_code == 200


@pytest.mark.parametrize(
    ("subject", "papeis"),
    [
        # O presidente que emitiu o ato: a capacidade não decorre de tê-lo emitido (SC-014).
        ("paulo.presidente", ["gestor"]),
        ("iris", ["auditor"]),
        ("ana.elaboradora", ["elaborador"]),
        ("estranho", []),
    ],
)
def test_sem_a_capacidade_e_403_na_previa_e_no_ato(
    client, seletor_ligado, cenario, subject, papeis
):
    identificar(client, subject, papeis)

    assert client.get(_previa(cenario)).status_code == 403
    assert client.post(_confirmar(cenario), {}).status_code == 403


def test_o_presidente_que_emitiu_nao_publica_nem_por_post(client, seletor_ligado, cenario):
    """A tela esconder o botão é conveniência; a recusa é do backend (FR-002, FR-026)."""
    identificar(client, "paulo.presidente", ["gestor"])

    resposta = client.post(
        _confirmar(cenario),
        {
            "natureza": "PRELIMINAR",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": "0" * 64,
            "chave_idempotencia": "tentativa-0755",
        },
    )

    assert resposta.status_code == 403
    assert not PublicacaoResultado.objects.exists()


def test_escopo_institucional_alheio_e_404(client, seletor_ligado, cenario):
    """Quem tem a capacidade mas não alcança o Edital não descobre que ele existe (FR-026)."""
    identificar(client, "paula.publicadora", ["publicador"], escopo="outra-unidade")

    assert client.get(_previa(cenario)).status_code == 404
    assert client.get(_historico(cenario)).status_code == 404


def test_o_historico_e_de_dois_e_publicar_e_de_um(client, seletor_ligado, cenario):
    """Consultar é de quem publica **ou** de quem audita; agir é só de quem publica."""
    identificar(client, "iris", ["auditor"])
    resposta = client.get(_historico(cenario))

    assert resposta.status_code == 200
    assert client.get(_previa(cenario)).status_code == 403


def test_uma_candidata_nao_alcanca_a_situacao_de_outra(client, cenario):
    """FR-024 e a IDOR da Área: a situação divulgada pertence a quem a inscrição pertence.

    A recusa é **404 uniforme**: quem tenta não descobre pela resposta se a inscrição não existe ou
    se ela é de outra pessoa.
    """
    from tests.fixtures.candidato import MARIA
    from tests.fixtures.candidato import identificar as identificar_candidata

    publicar_o_ato(cenario, chave="publicar-0755")
    alheia = cenario["inscricoes"][0]
    identificar_candidata(client, MARIA)

    resposta = client.get(reverse("portal:acompanhamento", args=[alheia.id]))

    assert resposta.status_code == 404


def test_o_protocolo_publicado_nao_resolve_a_inscricao_sem_autenticacao(client, cenario):
    """FR-024: publicá-lo o tornou público, e ele não pode virar credencial.

    O protocolo passa a ser lido por qualquer pessoa na página do resultado. Se algum caminho não
    autenticado o aceitasse como chave, publicar teria transformado um identificador de leitura numa
    forma de entrar na Área de outra pessoa — e o dano seria proporcional ao alcance da divulgação.

    A guarda é dupla: nenhuma rota pública recebe protocolo como parâmetro, e nenhuma delas
    devolve dado da inscrição quando ele chega como consulta.
    """
    from processo_seletivo.portal import urls as rotas_do_portal

    publicacao = publicar_o_ato(cenario, chave="publicar-0755-b")
    titular = cenario["inscricoes"][0]
    assert titular.protocolo in bytes(publicacao.conteudo_publico).decode(), (
        "o teste precisa de um protocolo realmente publicado para valer"
    )

    com_protocolo = [
        str(rota.pattern)
        for rota in rotas_do_portal.urlpatterns
        if "protocolo" in str(rota.pattern)
    ]
    assert com_protocolo == [], (
        f"rota pública recebe protocolo como parâmetro: {com_protocolo} — ele identifica, e "
        "identificar não é autorizar"
    )

    for nome in ("portal:inscricoes", "portal:acesso", "portal:vitrine"):
        resposta = client.get(reverse(nome), {"protocolo": titular.protocolo}, follow=True)
        corpo = resposta.content.decode()
        assert titular.nome not in corpo, f"{nome} devolveu o nome a partir do protocolo publicado"
        assert titular.email not in corpo
        assert str(titular.id) not in corpo
