"""O acesso do setor: o papel, a designação e o predicado único (117, US2, FR-3661 a FR-3668).

O papel abre a barra e a lista; a designação diz o Edital e os Perfis; o predicado decide na mesma
requisição. A revogação do papel, a da designação e a suspensão cortam o acesso na requisição
seguinte (FR-3667, SC-1110). A designação é concedida pela gestão de acessos ou, desde a revisão de
12/11 (D-025), pela presidência do Processo, sem autodesignação (FR-3663, FR-3668, FR-6700 a
FR-6707). A presidência escolhe entre quem já tem o papel, e designar não lhe dá os documentos.
"""

import threading
import uuid

import pytest
from django.db import DatabaseError, connection, transaction
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.auditoria.selectors import trilha_da_unidade, trilha_do_edital
from processo_seletivo.comissoes.models import Funcao, MembroComissao
from processo_seletivo.formalizacao.application import designar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.domain.autorizacao import pode_acessar, pode_designar
from processo_seletivo.formalizacao.models import (
    DesignacaoParaFormalizacao,
    RevogacaoDaDesignacao,
)
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.formalizacao import definir_documentos, designar_direto
from tests.integration.formalizacao.apoio import documentos_de, exportar_pessoa, verificar
from tests.interface.conftest import identificar
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

GIL = Actor("pessoa-gil", "cefor", frozenset({catalogo.GERIR, catalogo.CONSULTAR}))
#: A presidência da comissão do Processo do cenário: `maria`, como em toda a suíte. Ela não tem
#: permissão nenhuma do catálogo; a base é o vínculo com a comissão (`011`).
MARIA = Actor("maria", "cefor", frozenset())
OUTRO_PERFIL = "00000000-0000-0000-0000-00000000abcd"


def _pagina(edital):
    return reverse("interface:formalizacao-edital", args=[edital.id])


@pytest.fixture
def com_papel(db):
    """Rui, pessoa institucional com o papel Formalização no `cefor`."""
    rui = pessoa("rui", nome="Rui Registro", email="rui@ifes.edu.br")
    vincular(rui, "cefor", nomes.PAPEL)
    return rui


# --- O predicado -------------------------------------------------------------------------------


def test_sem_o_papel_a_recusa_nomeia_o_papel(cenario, gestor):
    """FR-3666: designação sem o papel é 403, e a frase diz o que falta."""
    designar_direto(cenario.edital, "carlos")
    with pytest.raises(DomainError) as recusa:
        pode_acessar(gestor, cenario.edital.id)

    assert recusa.value.status == 403
    assert "papel Formalização" in recusa.value.detail


def test_o_papel_sem_designacao_no_edital_e_inexistente(cenario, rui):
    with pytest.raises(DomainError) as recusa:
        pode_acessar(rui, cenario.edital.id)
    assert recusa.value.status == 404


def test_edital_de_outra_unidade_e_inexistente(cenario):
    designar_direto(cenario.edital, "rui")
    de_fora = Actor("rui", "outra", frozenset({nomes.CAPACIDADE}))
    with pytest.raises(DomainError) as recusa:
        pode_acessar(de_fora, cenario.edital.id)
    assert recusa.value.status == 404


def test_pessoa_de_perfil_fora_da_designacao_e_inexistente(cenario, gestor, rui):
    """FR-3666: Bia, só num Perfil, não vê nem alcança a pessoa do outro (US2, cenário 5)."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui", perfis=[OUTRO_PERFIL])

    with pytest.raises(DomainError) as recusa:
        pode_acessar(rui, cenario.edital.id, perfil_id=PROFILE_ID)
    assert recusa.value.status == 404
    assert pode_acessar(rui, cenario.edital.id, perfil_id=OUTRO_PERFIL).designacao


def test_a_pagina_nao_mostra_a_pessoa_de_fora_do_perfil(cenario, gestor, client, seletor):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui", perfis=[OUTRO_PERFIL])
    identificar(client, "rui", ["formalizacao"])

    corpo = client.get(_pagina(cenario.edital)).content.decode()
    assert "Nenhuma pessoa apta" in corpo
    assert cenario.aptas[0][0].protocolo not in corpo


def test_a_revogacao_da_designacao_corta_na_requisicao_seguinte(cenario, client, seletor):
    designacao = designar_direto(cenario.edital, "rui")
    identificar(client, "rui", ["formalizacao"])
    assert client.get(_pagina(cenario.edital)).status_code == 200

    RevogacaoDaDesignacao.objects.create(
        designacao=designacao,
        motivo="Saiu do setor",
        revogado_por="gil",
        unidade_de_atuacao="cefor",
        revogado_em=timezone.now(),
    )
    assert client.get(_pagina(cenario.edital)).status_code == 404


# --- Pela entrada institucional: o papel revogado e a suspensão ---------------------------------


def test_o_papel_revogado_corta_todas_as_designacoes(cenario, client, provedor, com_papel):
    """FR-3667: revogar o papel recusa na requisição seguinte, nomeando o papel (US2, cenário 6).

    Rui tem também o vínculo de integrante, e por isso continua tendo ator na unidade: o que muda é
    a capacidade, e a recusa é a de autorização, e não a tela sem acesso.
    """
    vincular(com_papel, "cefor", catalogo.INTEGRANTE)
    designar_direto(cenario.edital, com_papel.username)
    entrar(client, "rui", nome="Rui Registro")
    assert client.get(_pagina(cenario.edital)).status_code == 200
    assert client.get(reverse("interface:formalizacao")).status_code == 200

    vinculo = acessos.vigentes().get(pessoa=com_papel, papel=nomes.PAPEL)
    acessos.revogar(GIL, vinculo=vinculo, motivo="Saiu do setor", now=timezone.now())

    resposta = client.get(_pagina(cenario.edital))
    assert resposta.status_code == 403
    assert "papel Formalização" in resposta.content.decode()
    assert client.get(reverse("interface:formalizacao")).status_code == 403


def test_a_suspensao_corta_o_acesso(cenario, client, provedor, com_papel):
    from processo_seletivo.seguranca.application import suspensao

    designar_direto(cenario.edital, com_papel.username)
    entrar(client, "rui", nome="Rui Registro")
    assert client.get(_pagina(cenario.edital)).status_code == 200

    institucional = pessoa("inst")
    vincular(institucional, catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL)
    suspensao.suspender(
        Actor(
            institucional.username,
            catalogo.ESCOPO_INSTITUCIONAL,
            frozenset({catalogo.ADMINISTRAR}),
        ),
        pessoa=com_papel,
        motivo="Afastamento",
        now=timezone.now(),
    )

    # A suspensão encerra as sessões da pessoa (107, `FR-3137`): a próxima requisição não tem ator e
    # volta à identificação — e não a uma recusa qualquer, que esconderia outro defeito.
    resposta = client.get(_pagina(cenario.edital))
    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("interface:identificar"))


# --- A designação pela gestão de acessos --------------------------------------------------------


def test_designar_grava_com_motivo_e_vai_as_duas_trilhas(cenario, com_papel):
    designacao = designar.designar(
        GIL,
        edital_id=cenario.edital.id,
        pessoa=com_papel,
        perfis=[],
        motivo="Memorando 12/2026",
        now=timezone.now(),
    )

    assert designacao.pessoa == com_papel.username
    assert designacao.designado_por == GIL.subject
    evento = RegistroAuditoria.objects.get(operation=nomes.DESIGNAR)
    assert evento.aggregate_id == designacao.id
    do_edital, _ = trilha_do_edital(actor=GIL, edital=cenario.edital, limit=100)
    assert evento in do_edital
    da_unidade, _ = trilha_da_unidade(actor=GIL, assunto="acessos", limit=100)
    assert evento in da_unidade


def test_designar_quem_nao_tem_o_papel_e_recusado_com_codigo_proprio(cenario):
    sem_papel = pessoa("ze", nome="Zé")
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            GIL,
            edital_id=cenario.edital.id,
            pessoa=sem_papel,
            perfis=[],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.code == nomes.DESIGNADO_SEM_PAPEL
    assert not DesignacaoParaFormalizacao.objects.exists()


def test_ninguem_designa_a_si_mesmo(cenario):
    gil = pessoa("gil", nome="Gil")
    vincular(gil, "cefor", nomes.PAPEL)
    o_proprio = Actor(gil.username, "cefor", frozenset({catalogo.GERIR}))
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            o_proprio,
            edital_id=cenario.edital.id,
            pessoa=gil,
            perfis=[],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.code == nomes.AUTODESIGNACAO


def _designar(ator, edital, alguem, *, motivo="Memorando 9/2026", perfis=()):
    return designar.designar(
        ator,
        edital_id=edital.id,
        pessoa=alguem,
        perfis=list(perfis),
        motivo=motivo,
        now=timezone.now(),
    )


def _presidir(processo, subject):
    """Uma presidência gravada direto: estado de partida, e não o ato de constituir."""
    return MembroComissao.objects.create(
        processo=processo,
        identity_subject=subject,
        funcao=Funcao.PRESIDENTE,
        criado_em=timezone.now(),
        criado_por="fixture",
    )


def _outro_processo():
    agora = timezone.now()
    return ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=f"OUTRO-{uuid.uuid4().hex[:6]}",
        title="Outro Processo",
        created_at=agora,
        created_by="fixture",
        last_changed_at=agora,
    )


def test_a_presidencia_designa_no_proprio_processo(cenario, com_papel):
    """FR-6700, FR-6705, SC-2200, SC-2204: grava com motivo, nas duas trilhas, com a base dela.

    **Era `test_a_presidencia_nao_designa`**, que provava a recusa da D-013 de 04/11. A revisão de
    12/11 (D-025) inverteu a regra para a presidência do Processo, e os limites dela estão nos casos
    seguintes: só a própria comissão, nunca a si mesma, nunca quem não tem o papel, e sem acesso aos
    documentos.
    """
    assert pode_designar(MARIA, cenario.edital) == "comissao:presidir"
    designacao = _designar(MARIA, cenario.edital, com_papel)

    assert designacao.designado_por == "maria"
    evento = RegistroAuditoria.objects.get(operation=nomes.DESIGNAR)
    assert evento.permission == "comissao:presidir"
    assert evento.reason == "Memorando 9/2026"
    do_edital, _ = trilha_do_edital(actor=GIL, edital=cenario.edital, limit=100)
    assert evento in do_edital
    da_unidade, _ = trilha_da_unidade(actor=GIL, assunto="acessos", limit=100)
    assert evento in da_unidade


@pytest.mark.parametrize(
    ("quem", "status"),
    [
        ("presidência de outro Processo", 403),
        ("comissao:gerir sem presidir", 403),
        ("membro da comissão", 403),
        ("auditor", 403),
        ("presidência inativa", 403),
        ("presidente rebaixada a membro", 403),
        ("presidência de outra unidade", 404),
    ],
)
def test_so_a_presidencia_do_proprio_processo_designa(cenario, com_papel, quem, status):
    """FR-6700, FR-6707, SC-2200: as demais bases são recusadas, e nenhuma grava.

    `comissao:gerir` sem presidir continua recusado: o pedido é específico sobre a presidência. A
    presidência que deixou de valer — o vínculo inativado, ou a função rebaixada a membro — também.
    """
    atores = {
        "presidência de outro Processo": Actor("lia", "cefor", frozenset()),
        "comissao:gerir sem presidir": Actor("carlos", "cefor", frozenset({"comissao:gerir"})),
        "membro da comissão": Actor("joao", "cefor", frozenset()),
        "auditor": Actor("auditora", "cefor", frozenset({"auditoria:consultar"})),
        "presidência inativa": MARIA,
        "presidente rebaixada a membro": MARIA,
        "presidência de outra unidade": Actor("maria", "outra", frozenset()),
    }
    _presidir(_outro_processo(), "lia")
    a_dela = MembroComissao.objects.filter(
        processo=cenario.edital.processo, identity_subject="maria"
    )
    if quem == "presidência inativa":
        a_dela.update(ativo=False, inativado_em=timezone.now(), inativado_por="fixture")
    elif quem == "presidente rebaixada a membro":
        a_dela.update(funcao=Funcao.MEMBRO)
    ator = atores[quem]

    with pytest.raises(DomainError) as recusa:
        _designar(ator, cenario.edital, com_papel)
    assert recusa.value.status == status
    if status == 403:
        assert "presidência deste Processo" in recusa.value.detail
        assert "acessos da unidade" in recusa.value.detail
    assert not DesignacaoParaFormalizacao.objects.exists()

    feita = _designar(GIL, cenario.edital, com_papel)
    with pytest.raises(DomainError) as recusa:
        designar.revogar(ator, designacao_id=feita.id, motivo="x", now=timezone.now())
    assert recusa.value.status == status
    assert not RevogacaoDaDesignacao.objects.exists()


def test_a_presidencia_nao_designa_a_si_mesma(cenario):
    """FR-6702, SC-2203: com o papel e a presidência, a autodesignação continua recusada."""
    ana = pessoa("ana-presidente", nome="Ana Presidente")
    vincular(ana, "cefor", nomes.PAPEL)
    _presidir(cenario.edital.processo, ana.username)
    a_propria = Actor(ana.username, "cefor", frozenset({nomes.CAPACIDADE}))

    with pytest.raises(DomainError) as recusa:
        _designar(a_propria, cenario.edital, ana)
    assert recusa.value.code == nomes.AUTODESIGNACAO
    assert not DesignacaoParaFormalizacao.objects.exists()

    feita = _designar(GIL, cenario.edital, ana)
    with pytest.raises(DomainError) as recusa:
        designar.revogar(a_propria, designacao_id=feita.id, motivo="x", now=timezone.now())
    assert recusa.value.code == nomes.AUTODESIGNACAO


def test_a_presidencia_nao_designa_quem_nao_tem_o_papel(cenario):
    """FR-6701, SC-2203: a presidência escolhe só entre quem já tem o papel."""
    sem_papel = pessoa("ze", nome="Zé")
    with pytest.raises(DomainError) as recusa:
        _designar(MARIA, cenario.edital, sem_papel)
    assert recusa.value.code == nomes.DESIGNADO_SEM_PAPEL
    assert not DesignacaoParaFormalizacao.objects.exists()
    assert sem_papel.username not in {
        v.pessoa.username for v in designar.pessoas_com_o_papel(MARIA, edital=cenario.edital)
    }


def test_designar_nao_da_a_presidencia_acesso_aos_documentos(
    cenario, com_papel, client, seletor, gestor
):
    """FR-6704, SC-2201: depois de designar, a presidência fica fora da página, dos arquivos, da
    verificação e da exportação do setor."""
    definir_documentos(cenario.edital, gestor)
    _designar(MARIA, cenario.edital, com_papel)
    inscricao, _ = cenario.aptas[0]
    documento = documentos_de(cenario.edital, inscricao)[0]

    with pytest.raises(DomainError) as recusa:
        pode_acessar(MARIA, cenario.edital.id)
    assert recusa.value.status == 403
    identificar(client, "maria", [])
    assert client.get(_pagina(cenario.edital)).status_code == 403
    arquivo = client.get(
        reverse(
            "interface:formalizacao-documento",
            args=[cenario.edital.id, inscricao.id, documento.origem, documento.objeto_id],
        )
    )
    assert arquivo.status_code == 403
    assert verificar(client, cenario.edital, alcance="todos").status_code == 403
    assert exportar_pessoa(client, cenario.edital, inscricao).status_code == 403


@pytest.mark.parametrize("comando", ["designar", "revogar"])
def test_a_base_e_reavaliada_sob_a_trava_do_processo(cenario, com_papel, monkeypatch, comando):
    """`011`: a presidência rebaixada entre a conferência de fora e a gravação é recusada.

    A troca acontece **dentro** da trava, logo antes da releitura, que é exatamente o que um gestor
    concorrente faria se tivesse feito commit antes de a trava ser obtida. A conferência de fora da
    transação já tinha aceitado a presidente; a de dentro recusa, e nada se grava.
    """
    feita = _designar(GIL, cenario.edital, com_papel) if comando == "revogar" else None
    original = designar._trancar_o_processo_e_reavaliar

    def rebaixar_e_trancar(actor, edital):
        MembroComissao.objects.filter(processo=edital.processo_id, identity_subject="maria").update(
            funcao=Funcao.MEMBRO
        )
        return original(actor, edital)

    monkeypatch.setattr(designar, "_trancar_o_processo_e_reavaliar", rebaixar_e_trancar)
    assert pode_designar(MARIA, cenario.edital) == "comissao:presidir"

    with pytest.raises(DomainError) as recusa:
        if comando == "designar":
            _designar(MARIA, cenario.edital, com_papel)
        else:
            designar.revogar(MARIA, designacao_id=feita.id, motivo="x", now=timezone.now())
    assert recusa.value.status == 403
    assert DesignacaoParaFormalizacao.objects.count() == (1 if comando == "revogar" else 0)
    assert not RevogacaoDaDesignacao.objects.exists()
    assert not RegistroAuditoria.objects.filter(
        operation__in=[nomes.DESIGNAR, nomes.REVOGAR], permission="comissao:presidir"
    ).exists()


def test_cada_base_revoga_a_designacao_da_outra(cenario, com_papel):
    """FR-6703, SC-2202: a revogação não depende de quem concedeu."""
    da_gestao = _designar(GIL, cenario.edital, com_papel)
    designar.revogar(MARIA, designacao_id=da_gestao.id, motivo="Troca", now=timezone.now())
    assert RevogacaoDaDesignacao.objects.get(designacao=da_gestao).revogado_por == "maria"

    da_presidencia = _designar(MARIA, cenario.edital, com_papel)
    designar.revogar(GIL, designacao_id=da_presidencia.id, motivo="Saiu", now=timezone.now())
    assert RevogacaoDaDesignacao.objects.get(designacao=da_presidencia).revogado_por == GIL.subject
    evento = RegistroAuditoria.objects.filter(operation=nomes.REVOGAR).order_by("occurred_at")
    assert [e.permission for e in evento] == ["comissao:presidir", catalogo.GERIR]


def test_o_encerramento_do_edital_nao_revoga_nem_impede_designar(cenario, com_papel):
    """FR-6706: encerrado, a designação continua vigente, e a presidência ainda designa."""
    feita = _designar(GIL, cenario.edital, com_papel)
    Edital.objects.filter(pk=cenario.edital.pk).update(status=Edital.Status.ENCERRADO)
    cenario.edital.refresh_from_db()

    assert not RevogacaoDaDesignacao.objects.filter(designacao=feita).exists()
    designar.revogar(MARIA, designacao_id=feita.id, motivo="Troca", now=timezone.now())
    assert _designar(MARIA, cenario.edital, com_papel).designado_por == "maria"


def test_o_perfil_de_fora_do_edital_e_recusado(cenario, com_papel):
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            GIL,
            edital_id=cenario.edital.id,
            pessoa=com_papel,
            perfis=[OUTRO_PERFIL],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.code == nomes.PERFIL_FORA_DO_EDITAL


def test_uma_designacao_vigente_por_edital_e_pessoa(cenario, com_papel):
    argumentos = {
        "edital_id": cenario.edital.id,
        "pessoa": com_papel,
        "perfis": [],
        "motivo": "x",
    }
    designar.designar(GIL, now=timezone.now(), **argumentos)
    with pytest.raises(DomainError) as recusa:
        designar.designar(GIL, now=timezone.now(), **argumentos)
    assert recusa.value.code == nomes.DESIGNACAO_JA_VIGENTE


def test_revogar_e_designar_de_novo_muda_os_perfis(cenario, com_papel):
    primeira = designar.designar(
        GIL,
        edital_id=cenario.edital.id,
        pessoa=com_papel,
        perfis=[],
        motivo="x",
        now=timezone.now(),
    )
    designar.revogar(GIL, designacao_id=primeira.id, motivo="Troca de Perfis", now=timezone.now())
    with pytest.raises(DomainError) as recusa:
        designar.revogar(GIL, designacao_id=primeira.id, motivo="De novo", now=timezone.now())
    assert recusa.value.code == nomes.DESIGNACAO_JA_REVOGADA

    segunda = designar.designar(
        GIL,
        edital_id=cenario.edital.id,
        pessoa=com_papel,
        perfis=[str(PROFILE_ID)],
        motivo="Só o Perfil",
        now=timezone.now(),
    )
    assert segunda.perfis == [str(PROFILE_ID)]
    assert RegistroAuditoria.objects.filter(operation=nomes.REVOGAR).count() == 1


def test_edital_sem_publicacao_nao_recebe_designacao(cenario, com_papel):
    """O estado do Edital é regra do comando, e não só da tela (revisão do PR #373)."""
    from processo_seletivo.processos.models import Edital

    Edital.objects.filter(pk=cenario.edital.pk).update(status=Edital.Status.CANCELADO)
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            GIL,
            edital_id=cenario.edital.id,
            pessoa=com_papel,
            perfis=[],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.code == nomes.EDITAL_SEM_PUBLICACAO
    assert not DesignacaoParaFormalizacao.objects.exists()


def test_a_pessoa_suspensa_nao_recebe_designacao(cenario, com_papel):
    com_papel.is_active = False
    com_papel.save(update_fields=["is_active"])
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            GIL,
            edital_id=cenario.edital.id,
            pessoa=com_papel,
            perfis=[],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.code == nomes.PESSOA_INDISPONIVEL


def test_a_autodesignacao_e_recusada_pelo_banco_tambem(cenario):
    from django.db import IntegrityError

    with pytest.raises(IntegrityError), transaction.atomic():
        DesignacaoParaFormalizacao.objects.create(
            edital=cenario.edital,
            pessoa="gil",
            perfis=[],
            motivo="x",
            designado_por="gil",
            unidade_de_atuacao="cefor",
            designado_em=timezone.now(),
        )


@pytest.mark.parametrize(
    "tabela", ["formalizacao_designacaoparaformalizacao", "formalizacao_revogacaodadesignacao"]
)
def test_designacao_e_revogacao_sao_append_only_por_gatilho(cenario, tabela):
    if connection.vendor != "postgresql":
        pytest.skip("gatilho só no PostgreSQL")
    designacao = designar_direto(cenario.edital, "rui")
    RevogacaoDaDesignacao.objects.create(
        designacao=designacao,
        motivo="x",
        revogado_por="gil",
        unidade_de_atuacao="cefor",
        revogado_em=timezone.now(),
    )
    with pytest.raises(DatabaseError, match="append-only"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {tabela}")


# --- A matriz pelas telas: quem designa e quem lê ------------------------------------------------


def _definicao(edital):
    return reverse("interface:formalizacao-definicao", args=[edital.id])


def test_quem_gere_a_comissao_sem_presidir_ve_as_designacoes_so_para_leitura(
    cenario, client, seletor, com_papel
):
    """FR-3668 revista, UX-700: `comissao:gerir` sem presidir lê; o POST forjado é recusado."""
    designar_direto(cenario.edital, "rui")
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(_definicao(cenario.edital)).content.decode()

    assert "Quem acessa os documentos" in corpo
    assert "rui" in corpo
    assert "só para leitura" in corpo
    assert "Revogar" not in corpo
    assert "Designar para o" not in corpo
    forjado = client.post(
        reverse("interface:formalizacao-designar", args=[cenario.edital.id]),
        {"pessoa": com_papel.username, "motivo": "x"},
    )
    assert forjado.status_code == 403
    assert DesignacaoParaFormalizacao.objects.count() == 1


def test_a_presidencia_designa_e_revoga_na_tela_da_definicao(cenario, client, seletor, com_papel):
    """UX-700, UX-702, FR-6703: a seção ganha a designação e o "Revogar"; a recusa volta a ela."""
    designar_direto(cenario.edital, "outra-pessoa")
    identificar(client, "maria", [])
    pagina = _definicao(cenario.edital)
    corpo = client.get(pagina).content.decode()
    assert "Rui Registro" in corpo
    assert "Designar para o" in corpo
    assert "Revogar" in corpo
    assert "Designar não dá a você acesso aos documentos" in corpo

    designar_url = reverse("interface:formalizacao-designar", args=[cenario.edital.id])
    sem_motivo = client.post(designar_url, {"pessoa": com_papel.username, "motivo": ""})
    assert sem_motivo.status_code == 302
    assert sem_motivo["Location"].endswith("#quem-acessa")
    assert "Informe o motivo" in client.get(pagina).content.decode()
    assert not DesignacaoParaFormalizacao.objects.filter(pessoa=com_papel.username).exists()

    feito = client.post(designar_url, {"pessoa": com_papel.username, "motivo": "Memorando 7"})
    assert feito.status_code == 302
    designacao = DesignacaoParaFormalizacao.objects.get(pessoa=com_papel.username)
    assert designacao.designado_por == "maria"
    assert "Designação gravada" in client.get(pagina).content.decode()

    revogada = client.post(
        reverse(
            "interface:formalizacao-designacao-revogar", args=[cenario.edital.id, designacao.id]
        ),
        {"motivo": "Saiu do setor"},
    )
    assert revogada.status_code == 302
    assert RevogacaoDaDesignacao.objects.filter(designacao=designacao).exists()
    # A de outra pessoa, concedida fora da tela, também se revoga daqui.
    da_gestao = DesignacaoParaFormalizacao.objects.get(pessoa="outra-pessoa")
    client.post(
        reverse(
            "interface:formalizacao-designacao-revogar", args=[cenario.edital.id, da_gestao.id]
        ),
        {"motivo": "Troca"},
    )
    assert RevogacaoDaDesignacao.objects.filter(designacao=da_gestao).exists()


def test_designacao_de_outro_edital_e_inexistente_na_tela(cenario, client, seletor, com_papel):
    """FR-6707: a URL de revogar leva o Edital, e a designação de outro não é deste."""
    designacao = designar_direto(cenario.edital, "rui")
    identificar(client, "maria", [])
    resposta = client.post(
        reverse("interface:formalizacao-designacao-revogar", args=[uuid.uuid4(), designacao.id]),
        {"motivo": "x"},
    )
    assert resposta.status_code == 404
    assert not RevogacaoDaDesignacao.objects.exists()


def test_sem_ninguem_com_o_papel_a_secao_diz_a_quem_pedir(cenario, client, seletor):
    """UX-701: sem link à tela de acessos, que a presidência não alcança."""
    identificar(client, "maria", [])
    corpo = client.get(_definicao(cenario.edital)).content.decode()

    assert "Ninguém nesta unidade tem o papel Formalização" in corpo
    assert "Peça a quem administra os acessos da unidade" in corpo
    assert reverse("interface:acessos-formalizacao") not in corpo


def test_quem_confere_nao_alcanca_a_formalizacao_e_o_setor_nao_alcanca_a_conferencia(
    cenario, client, seletor
):
    """US2, cenário 7, FR-3665: os dois predicados são disjuntos."""
    designar_direto(cenario.edital, "rui")
    identificar(client, "joao", [])
    assert client.get(_pagina(cenario.edital)).status_code == 403

    identificar(client, "rui", ["formalizacao"])
    _, convocacao = cenario.aptas[0]
    documentos = reverse(
        "interface:documentos-da-convocacao",
        args=[cenario.edital.id, convocacao.marco_id, convocacao.id],
    )
    assert client.get(documentos).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_duas_designacoes_simultaneas_gravam_uma(
    gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """A pessoa trancada serializa as duas: a segunda vê a primeira e recusa (data-model)."""
    from tests.fixtures.formalizacao import montar_cenario_da_formalizacao

    if connection.vendor != "postgresql":
        pytest.skip("trava de linha só no PostgreSQL")
    cenario = montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=0, prefixo="conc-117"
    )
    rui = pessoa("rui", nome="Rui")
    vincular(rui, "cefor", nomes.PAPEL)
    barreira = threading.Barrier(2)
    resultados = []

    def designar_em_paralelo():
        try:
            barreira.wait()
            designar.designar(
                GIL,
                edital_id=cenario.edital.id,
                pessoa=rui,
                perfis=[],
                motivo="x",
                now=timezone.now(),
            )
            resultados.append("gravou")
        except DomainError as recusa:
            resultados.append(recusa.code)
        finally:
            connection.close()

    threads = [threading.Thread(target=designar_em_paralelo) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(resultados) == sorted(["gravou", nomes.DESIGNACAO_JA_VIGENTE])
    assert DesignacaoParaFormalizacao.objects.count() == 1


def test_a_tela_de_acessos_designa_e_revoga(cenario, client, provedor, com_papel):
    """T016: a seção da gestão de acessos grava a designação e a revogação, com motivo."""
    admin = pessoa("admin-cefor", nome="Gil Acessos")
    vincular(admin, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "admin-cefor", nome="Gil Acessos")
    pagina = reverse("interface:acessos-formalizacao")

    corpo = client.get(pagina, {"edital": cenario.edital.id}).content.decode()
    assert "Rui Registro" in corpo
    assert "Designar para o" in corpo
    sem_motivo = client.post(
        pagina, {"edital": cenario.edital.id, "pessoa": com_papel.username, "motivo": ""}
    )
    assert sem_motivo.status_code == 422
    assert not DesignacaoParaFormalizacao.objects.exists()

    feito = client.post(
        pagina,
        {"edital": cenario.edital.id, "pessoa": com_papel.username, "motivo": "Memorando 7"},
    )
    assert feito.status_code == 302
    designacao = DesignacaoParaFormalizacao.objects.get()
    assert designacao.pessoa == com_papel.username
    assert "Rui Registro" in client.get(pagina).content.decode()

    revogada = client.post(
        reverse("interface:acessos-formalizacao-revogar", args=[designacao.id]),
        {"motivo": "Saiu do setor"},
    )
    assert revogada.status_code == 302
    assert RevogacaoDaDesignacao.objects.filter(designacao=designacao).exists()


def test_a_tela_de_acessos_recusa_quem_nao_administra(cenario, client, seletor):
    identificar(client, "maria", [])
    assert client.get(reverse("interface:acessos-formalizacao")).status_code == 403


# --- As telas de designar escolhem da lista que ofereceram (134, FR-6731) -----------------------


def tela_de_designar(client, edital, tela):
    """Um `postar(pessoa) -> texto da tela depois`, pela tela da presidência ou pela de acessos.

    A da presidência é a seção "Quem acessa os documentos", com `maria` pelo seletor; a de acessos
    é a da unidade, com uma pessoa institucional que administra os acessos, pela entrada
    institucional — o seletor de demonstração não oferece esse papel.
    """
    if tela == "presidencia":
        identificar(client, "maria", [])
        url = reverse("interface:formalizacao-designar", args=[edital.id])

        def postar(alguem):
            client.post(url, {"pessoa": alguem, "motivo": "Memorando 7"})
            return client.get(_definicao(edital)).content.decode()

        return postar
    gil = pessoa("gil-acessos", nome="Gil Acessos", email="gil@ifes.edu.br")
    vincular(gil, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "gil-acessos", nome="Gil Acessos")
    url = reverse("interface:acessos-formalizacao")

    def postar(alguem):
        resposta = client.post(
            url, {"edital": str(edital.id), "pessoa": alguem, "motivo": "Memorando 7"}
        )
        return resposta.content.decode() if resposta.status_code != 302 else ""

    return postar


@pytest.fixture
def pessoa_de_treino(db):
    """A pessoa que os cenários da 134 criam, com o papel na unidade: não é institucional."""
    from django.contrib.auth import get_user_model

    treino = get_user_model().objects.create(
        username="treino.formalizacao", first_name="Formalização Treinamento"
    )
    vincular(treino, "cefor", nomes.PAPEL)
    return treino


@pytest.mark.parametrize("tela", ["presidencia", "acessos"])
def test_as_telas_de_designar_aceitam_so_quem_ofereceram(
    cenario, client, seletor, provedor, com_papel, pessoa_de_treino, tela
):
    """FR-6731: a pessoa institucional com o papel continua designável pelas duas telas; a de
    treino, num Edital real, não é oferecida e é recusada; o identificador inexistente e o
    adulterado recebem a mesma recusa; e a institucional sem o papel, o código da FR-3663.
    """
    postar = tela_de_designar(client, cenario.edital, tela)
    indisponivel = "não está disponível para receber acesso"
    for fora in ("treino.formalizacao", "pessoa-inexistente", "pessoa-rui' OR '1'='1"):
        assert indisponivel in postar(fora), fora
        assert not DesignacaoParaFormalizacao.objects.filter(pessoa=fora).exists()

    sem_papel = pessoa("carla", nome="Carla", email="carla@ifes.edu.br")
    assert "não tem o papel" in postar(sem_papel.username)
    assert not DesignacaoParaFormalizacao.objects.filter(pessoa=sem_papel.username).exists()

    postar(com_papel.username)
    assert DesignacaoParaFormalizacao.objects.filter(
        edital=cenario.edital, pessoa=com_papel.username
    ).exists()
