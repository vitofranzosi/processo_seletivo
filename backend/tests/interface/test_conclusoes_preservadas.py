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

    assert "87.5000" in corpo
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
    assert "87.5000" in corpo


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


def test_identificador_malformado_no_filtro_e_recusa_de_formulario(
    client, seletor_ligado, cenario, concluida
):
    """Errar o identificador digitado não pode ser erro de servidor."""
    identificar(client, "maria", [])
    resposta = client.get(pagina(cenario, inscricao="não-é-uuid"))

    assert resposta.status_code == 200
    assert "não tem forma de identificador" in resposta.content.decode()
