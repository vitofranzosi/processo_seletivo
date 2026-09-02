"""A preservação de FR-094 é **consultável**, ou não é preservação (FR-091).

Reabrir devolve a Avaliação a rascunho e a esvazia de pontuação, versão e instante. O que aquela
pessoa havia concluído antes continua íntegro no registro append-only do domínio — e precisava de
uma porta, porque "está gravado em algum lugar" não é resposta a quem responde a um recurso.

A trilha não serve para isto, e é de propósito: ela guarda que o ato aconteceu, e nunca a
pontuação nem o parecer (FR-054).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.avaliacao import reabrir
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Avaliacao
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=21, codigo="CP")


@pytest.fixture
def concluida(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=2100)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="cp")
    avaliacao = concluir_como(
        cenario, "joao", inscricao, pontuacao="87.5", parecer="Atende com folga."
    )
    return {"inscricao": inscricao, "avaliacao": avaliacao}


def pagina(cenario, **filtros):
    base = reverse(
        "interface:conclusoes-preservadas", args=[cenario["edital"].id, cenario["etapa"]]
    )
    if not filtros:
        return base
    return base + "?" + "&".join(f"{chave}={valor}" for chave, valor in filtros.items())


def test_o_que_foi_concluido_antes_da_reabertura_continua_legivel(
    client, seletor_ligado, cenario, gestor, concluida
):
    """A pergunta que um recurso faz: o que ela havia registrado, quando e sob qual versão."""
    reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=concluida["avaliacao"].id,
        motivo="Recurso deferido.",
        expected_revision=concluida["avaliacao"].revision,
        idempotency_key="cp-reab",
        correlation_id="teste",
    )
    # A Avaliação corrente já não responde por nada disso: ela voltou a ser trabalho pendente.
    corrente = Avaliacao.objects.get(pk=concluida["avaliacao"].pk)
    assert corrente.estado == Avaliacao.Estado.RASCUNHO
    assert corrente.versao_id is None and corrente.concluida_em is None

    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario)).content.decode()

    assert "87,5" in corpo
    assert "Atende com folga." in corpo
    assert "Substituída por reabertura" in corpo
    assert "vigente desde" in corpo


def test_a_conclusao_tornada_inelegivel_aparece_como_preservada(
    client, seletor_ligado, cenario, gestor, concluida
):
    """Preservar não é o mesmo que continuar valendo, e a tela precisa dizer qual dos dois é."""
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=concluida["inscricao"].id,
        motivo="Parentesco.",
        idempotency_key="cp-imp",
        correlation_id="teste",
    )

    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario)).content.decode()

    assert "Preservada e inelegível" in corpo
    assert "87,5" in corpo


def test_a_conclusao_em_vigor_nao_e_anunciada_como_perdida(
    client, seletor_ligado, cenario, concluida
):
    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario)).content.decode()

    assert "Em vigor" in corpo
    assert "Preservada e inelegível" not in corpo


def test_a_porta_e_a_presidencia_ou_a_auditoria(client, seletor_ligado, cenario, concluida):
    """A mesma porta da trilha: são os dois que respondem a recurso (FR-091)."""
    for subject, papeis in (("maria", []), ("carlos", ["gestor"]), ("bianca", ["auditor"])):
        identificar(client, subject, papeis)
        assert client.get(pagina(cenario)).status_code == 200, subject

    identificar(client, "joao", [])  # avaliador: trabalha na Etapa, não a audita
    assert client.get(pagina(cenario)).status_code == 404


def test_o_filtro_aceita_o_protocolo_da_tabela(client, seletor_ligado, cenario, concluida):
    """O protocolo é o que a tabela mostra — e era o que o filtro recusava."""
    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario, inscricao=concluida["inscricao"].protocolo)).content.decode()

    assert "87,5" in corpo


def test_protocolo_desconhecido_no_filtro_e_recusa_de_formulario(
    client, seletor_ligado, cenario, concluida
):
    """Errar o que se digita não pode ser erro de servidor."""
    identificar(client, "maria", [])
    resposta = client.get(pagina(cenario, inscricao="não-existe"))

    assert resposta.status_code == 200
    assert "Não há inscrição com este protocolo" in resposta.content.decode()


def test_a_tela_nao_e_armazenavel_pelo_navegador(client, seletor_ligado, cenario, concluida):
    """FR-056: resposta com pontuação e parecer não fica no cache do navegador."""
    identificar(client, "maria", [])

    assert "no-store" in client.get(pagina(cenario))["Cache-Control"]


def test_a_situacao_e_dita_por_extenso_e_nao_por_cor(client, seletor_ligado, cenario, concluida):
    """Quem lê em escala de cinza precisa distinguir preservada de em vigor."""
    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario)).content.decode()

    assert "Em vigor" in corpo
    assert "<caption" in corpo
    assert "tabela-rolavel" in corpo


def test_a_presidencia_reabre_a_partir_desta_pagina(client, seletor_ligado, cenario, concluida):
    """A reabertura mora onde se lê o que foi concluído — e não na tela de distribuição.

    Na tela de distribuição ela ocupava uma linha e um formulário por avaliação concluída, sem
    paginar: numa Etapa de 600 inscritos com dupla avaliação, 1.200 formulários acima da área de
    trabalho. Aqui a página é paginada e cada linha mostra o que se precisa saber antes de decidir.
    """
    identificar(client, "maria", [])
    resposta = client.post(
        reverse("interface:reabrir-avaliacao", args=[cenario["edital"].id, cenario["etapa"]]),
        {
            "avaliacao_id": str(concluida["avaliacao"].id),
            "expected_revision": concluida["avaliacao"].revision,
            "motivo": "Recurso deferido pela banca.",
            "chave_idempotencia": "reab-tela",
        },
        follow=True,
    )
    corpo = resposta.content.decode()

    assert Avaliacao.objects.get(pk=concluida["avaliacao"].pk).estado == Avaliacao.Estado.RASCUNHO
    assert "Avaliação reaberta" in corpo
    assert "Substituída por reabertura" in corpo


def test_a_auditoria_le_a_pagina_e_nao_reabre(client, seletor_ligado, cenario, concluida):
    """Consultar é de dois; reabrir é de um (FR-091, FR-036)."""
    identificar(client, "bianca", ["auditor"])
    corpo = client.get(pagina(cenario)).content.decode()
    assert "87,5" in corpo
    assert "Motivo da reabertura" not in corpo

    recusa = client.post(
        reverse("interface:reabrir-avaliacao", args=[cenario["edital"].id, cenario["etapa"]]),
        {
            "avaliacao_id": str(concluida["avaliacao"].id),
            "expected_revision": concluida["avaliacao"].revision,
            "motivo": "Sem base para isto.",
        },
    )

    assert recusa.status_code == 404
    assert Avaliacao.objects.get(pk=concluida["avaliacao"].pk).estado == Avaliacao.Estado.CONCLUIDA


def test_so_a_conclusao_em_vigor_oferece_reabertura(
    client, seletor_ligado, cenario, gestor, concluida
):
    """Reabrir o que já foi substituído não traria nada de volta."""
    reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=concluida["avaliacao"].id,
        motivo="Primeira reabertura.",
        expected_revision=concluida["avaliacao"].revision,
        idempotency_key="cp-uma",
        correlation_id="teste",
    )

    identificar(client, "maria", [])
    corpo = client.get(pagina(cenario)).content.decode()

    assert "Substituída por reabertura" in corpo
    assert "Motivo da reabertura" not in corpo
