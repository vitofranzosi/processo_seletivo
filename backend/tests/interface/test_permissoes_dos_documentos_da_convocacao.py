"""A matriz de permissões da spec, linha a linha, pelas rotas da gestão (115, US5, SC-1087).

Fora do alcance (escopo alheio, inexistente, Perfil fora da alocação) é **404**; no escopo e sem
base nenhuma é **403**, como a condução já responde (FR-3599). O membro alocado à conferência só
confere: o desfecho continua com a base atual (FR-3596, D-010, aprovada).
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.domain import nomes
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import CERTIDAO, apresentar, item
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def chamada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    """Uma convocação com a certidão apresentada, e as três rotas que ela tem."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="matriz-115",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    feita = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    return {
        "edital": edital,
        "convocacao": convocacao,
        "pagina": reverse(
            "interface:documentos-da-convocacao", args=[edital.id, MARCO, convocacao.id]
        ),
        "arquivo": reverse(
            "interface:documento-da-convocacao", args=[edital.id, MARCO, convocacao.id, feita.id]
        ),
        "conferir": reverse(
            "interface:conferir-documento",
            args=[edital.id, MARCO, convocacao.id, item(convocacao, CERTIDAO).id],
        ),
        "conducao": reverse("interface:convocacao", args=[edital.id, MARCO]),
        "desfecho": reverse("interface:desfechar", args=[edital.id, MARCO, convocacao.id]),
        "apresentacao": feita,
    }


def _alocar(chamada, gestor, *, perfil=None):
    from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia
    from processo_seletivo.comissoes.models import MembroComissao

    edital = chamada["edital"]
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        perfil_id=perfil,
        idempotency_key=f"matriz-{perfil}",
        correlation_id="teste-115",
    )


def _respostas(client, chamada):
    return {
        "pagina": client.get(chamada["pagina"]).status_code,
        "arquivo": abrir_arquivo(client, chamada["arquivo"]).status_code,
        "conferir": client.post(
            chamada["conferir"],
            {"resultado": "PENDENTE", "motivo": "Ilegível.", "chave": "matriz"},
        ).status_code,
        "conducao": client.get(chamada["conducao"]).status_code,
    }


def test_o_gestor_e_a_presidencia_abrem_conferem_e_conduzem(chamada, client):
    for subject, papeis in (("carlos", ["gestor"]), ("maria", [])):
        identificar(client, subject, papeis)
        assert _respostas(client, chamada) == {
            "pagina": 200,
            "arquivo": 200,
            "conferir": 302,
            "conducao": 200,
        }, subject


def test_o_membro_alocado_confere_e_nao_desfecha(chamada, client, gestor):
    _alocar(chamada, gestor)
    identificar(client, "joao", [])

    assert _respostas(client, chamada) == {
        "pagina": 200,
        "arquivo": 200,
        "conferir": 302,
        "conducao": 200,
    }
    desfecho = client.post(
        chamada["desfecho"], {"especie": nomes.INDEFERIMENTO, "fundamento": "Sem base."}
    )
    assert desfecho.status_code == 403
    assert "Registrar desfecho" not in client.get(chamada["conducao"]).content.decode()


def test_o_membro_alocado_a_outro_perfil_recebe_inexistente(chamada, client, gestor):
    from tests.integration.comissoes.test_alocacao_a_conferencia import _alocar_a_outro_perfil

    _alocar_a_outro_perfil(chamada["edital"], "joao")
    identificar(client, "joao", [])

    assert _respostas(client, chamada) == {
        "pagina": 404,
        "arquivo": 404,
        "conferir": 404,
        "conducao": 404,
    }


@pytest.mark.parametrize(
    "subject, papeis, conducao",
    [
        ("joao", [], 403),  # membro só alocado a Etapa
        ("auditora", ["auditor"], 200),  # vê a condução, não abre arquivo
        ("exportadora", ["exportador"], 403),  # servidor da unidade sem base
    ],
)
def test_quem_nao_confere_nao_abre_o_arquivo(chamada, client, subject, papeis, conducao):
    identificar(client, subject, papeis)

    assert _respostas(client, chamada) == {
        "pagina": 403,
        "arquivo": 403,
        "conferir": 403,
        "conducao": conducao,
    }


def test_de_outra_unidade_tudo_e_inexistente(chamada, client):
    identificar(client, "carlos", ["gestor"], escopo="campus-alegre")

    assert _respostas(client, chamada) == {
        "pagina": 404,
        "arquivo": 404,
        "conferir": 404,
        "conducao": 404,
    }


def test_a_abertura_fica_na_trilha_sem_o_nome_do_arquivo(chamada, client):
    """FR-3603, FR-3604, SC-1088: ator, unidade e agregado, e nada do arquivo nem do motivo."""
    identificar(client, "carlos", ["gestor"])
    client.get(chamada["pagina"])
    abrir_arquivo(client, chamada["arquivo"])

    pagina = RegistroAuditoria.objects.get(operation="CONSULTAR_DOCUMENTOS_DA_CONVOCACAO")
    arquivo = RegistroAuditoria.objects.get(operation="CONSULTAR_DOCUMENTO_DA_CONVOCACAO")
    assert pagina.actor_subject == "carlos" and pagina.institution_scope == "cefor"
    assert str(arquivo.aggregate_id) == str(chamada["apresentacao"].id)
    assert chamada["apresentacao"].nome_original not in (arquivo.reason or "")


def test_abrir_o_dossie_da_inscricao_deixa_rastro(chamada, client):
    """O A-07 da auditoria de 31/10, resolvido (FR-3604)."""
    identificar(client, "carlos", ["gestor"])
    inscricao = chamada["convocacao"].inscricao

    resposta = client.get(reverse("interface:inscricao-recebida", args=[inscricao.id]))

    assert resposta.status_code == 200
    registro = RegistroAuditoria.objects.get(operation="CONSULTAR_DOSSIE")
    assert str(registro.aggregate_id) == str(inscricao.id)
    assert registro.actor_subject == "carlos"
    assert inscricao.nome not in (registro.reason or "")


def test_a_conducao_mostra_o_resumo_e_o_caminho_dos_documentos(chamada, client):
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(chamada["conducao"]).content.decode()

    assert "Documentos para conferir" in corpo
    assert "1 para conferir" in corpo
    assert chamada["pagina"] in corpo
    # Um documento à espera da comissão e o prazo correndo não são falta da pessoa: o atalho do
    # indeferimento só aparece com pendência registrada (152, FR-5800).
    assert "Indeferir pelas pendências de documento" not in corpo


def test_a_linha_nova_de_documento_oferece_o_aproveitamento(chamada, client):
    """Revisão do #369: o fragmento da linha nova não trazia os documentos já gravados."""
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(
        reverse("interface:fragmento-documento", args=[chamada["edital"].id])
    ).content.decode()

    assert "Atendido pelo documento da inscrição" in corpo
    assert ">Documento de identificação</option>" in corpo


def test_com_o_processo_em_estado_final_a_pagina_nao_oferece_conferir(chamada, client):
    """Revisão do #369: o comando recusa conferir com o Processo encerrado, e a página oferecia o
    formulário assim mesmo — o mesmo convite a um ato que não existe que o portal já deixou de
    fazer."""
    from processo_seletivo.processos.models import ProcessoSeletivo

    identificar(client, "carlos", ["gestor"])
    assert "Registrar conferência" in client.get(chamada["pagina"]).content.decode()

    ProcessoSeletivo.objects.filter(pk=chamada["edital"].processo_id).update(
        status=ProcessoSeletivo.Status.ENCERRADO
    )
    corpo = client.get(chamada["pagina"]).content.decode()

    assert "Registrar conferência" not in corpo
    assert "Abrir" in corpo, "o arquivo continua acessível para leitura"


def test_a_pendencia_sem_arquivo_nao_pede_motivo_de_revisao(chamada, client, gestor):
    """Revisão do #369: sem arquivo, a conferência e a versão vigente eram ambas nulas, e a página
    pedia "por que mudar a conferência desta versão" de uma versão que não existe — pedido que o
    comando nem cobra."""
    from tests.fixtures.documentos_da_convocacao import HISTORICO, conferir

    conferir(
        gestor, chamada["convocacao"], HISTORICO, "PENDENTE", chave="sem-arquivo", motivo="Falta."
    )
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(chamada["pagina"]).content.decode()

    assert "Por que mudar a conferência desta versão" not in corpo
