"""O acesso do setor: o papel, a designação e o predicado único (117, US2, FR-3661 a FR-3668).

O papel abre a barra e a lista; a designação diz o Edital e os Perfis; o predicado decide na mesma
requisição. A revogação do papel, a da designação e a suspensão cortam o acesso na requisição
seguinte (FR-3667, SC-1110). A designação é concedida pela gestão de acessos, sem autodesignação, e
a presidência só a vê (FR-3663, FR-3668).
"""

import threading

import pytest
from django.db import DatabaseError, connection, transaction
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.auditoria.selectors import trilha_da_unidade, trilha_do_edital
from processo_seletivo.formalizacao.application import designar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.domain.autorizacao import pode_acessar
from processo_seletivo.formalizacao.models import (
    DesignacaoParaFormalizacao,
    RevogacaoDaDesignacao,
)
from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.formalizacao import definir_documentos, designar_direto
from tests.interface.conftest import identificar
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

GIL = Actor("pessoa-gil", "cefor", frozenset({catalogo.GERIR, catalogo.CONSULTAR}))
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


def test_a_presidencia_nao_designa(cenario, com_papel):
    """FR-3663, matriz: sem `acesso:gerir`, 403 — a presidência só lê as designações."""
    presidencia = Actor("maria", "cefor", frozenset())
    with pytest.raises(DomainError) as recusa:
        designar.designar(
            presidencia,
            edital_id=cenario.edital.id,
            pessoa=com_papel,
            perfis=[],
            motivo="x",
            now=timezone.now(),
        )
    assert recusa.value.status == 403


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


def test_a_presidencia_ve_as_designacoes_na_conducao_so_para_leitura(cenario, client, seletor):
    designar_direto(cenario.edital, "rui")
    identificar(client, "maria", [])
    corpo = client.get(
        reverse("interface:formalizacao-definicao", args=[cenario.edital.id])
    ).content.decode()

    assert "Quem acessa os documentos" in corpo
    assert "rui" in corpo
    assert "Revogar" not in corpo


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
