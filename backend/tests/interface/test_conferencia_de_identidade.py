"""A equipe confere CPF e data de nascimento por ato, com motivo e trilha (180, história 3, D-002).

FR-8312 (a ação no detalhe da enviada, e o CPF mascarado fora dela), FR-8315 (sem motivo, nada é
revelado), FR-8316 (a trilha recebe quem, quando, qual inscrição e o motivo, e nunca os valores),
FR-8317 (a porta é a do detalhe) e SC-2906 (toda conferência aparece na trilha de quem audita).

**A recusa de quem não tem a permissão é a do detalhe**: 403 explicado, e não "não encontrado". O
404 fica com o que não existe e com a outra unidade, que é a gramática que a `033` fixou.
"""

from datetime import date

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.application import consulta
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import CPF_MARIA, MARIA, MODALIDADE_AC, NASCIMENTO_PADRAO, pdf
from tests.fixtures.comissao import sem_imutabilidade_da_enviada
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

MOTIVO = "Dois cadastros com o mesmo CPF no processo 23148.000123/2026-11."
DATA = NASCIMENTO_PADRAO.strftime("%d/%m/%Y")
#: Todas as formas em que o CPF e a data poderiam ter escapado para um registro ou para uma tela.
FORMAS_DO_CPF = (CPF_MARIA, "12345678909")
FORMAS_DA_DATA = (DATA, NASCIMENTO_PADRAO.isoformat())


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-conferencia",
    )


@pytest.fixture
def gestor(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "bruno.gestor", ["gestor"])
    return client


def _detalhe(inscricao):
    return reverse("interface:inscricao-recebida", args=[inscricao.id])


def _conferir(client, inscricao, motivo=MOTIVO):
    return client.post(
        reverse("interface:conferir-identidade", args=[inscricao.id]), {"motivo": motivo}
    )


def _conferencias():
    return RegistroAuditoria.objects.filter(operation=consulta.CONFERIR_IDENTIDADE)


def _sem_os_valores(texto):
    return not any(forma in texto for forma in (*FORMAS_DO_CPF, *FORMAS_DA_DATA))


# --- O detalhe ---------------------------------------------------------------------------------


def test_o_detalhe_da_enviada_oferece_a_acao_e_continua_mascarado(gestor, enviada):
    """FR-8312: fora da ação, o CPF continua mascarado e a data não aparece."""
    corpo = gestor.get(_detalhe(enviada)).content.decode()

    assert "Conferir identidade" in corpo
    assert reverse("interface:conferir-identidade", args=[enviada.id]) in corpo
    assert "Não escreva CPF nem data aqui" in corpo
    assert "***.456.789-**" in corpo
    assert _sem_os_valores(corpo)


def test_o_rascunho_nao_oferece_a_acao(gestor, inscricao_de_maria):
    """Rascunho não é ato: o que ele mostraria é o cadastro de agora."""
    corpo = gestor.get(_detalhe(inscricao_de_maria)).content.decode()

    assert "Conferir identidade" not in corpo
    assert reverse("interface:conferir-identidade", args=[inscricao_de_maria.id]) not in corpo


# --- A conferência -----------------------------------------------------------------------------


def test_com_motivo_revela_o_cpf_completo_e_a_data(gestor, enviada):
    resposta = _conferir(gestor, enviada)
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert CPF_MARIA in corpo
    assert DATA in corpo
    assert "Maria Silva" in corpo
    assert MOTIVO in corpo, "a página diz sob qual motivo a revelação foi registrada"
    assert _detalhe(enviada) in corpo, "o caminho de volta é o dossiê"


def test_a_pagina_da_conferencia_nao_e_guardada_pelo_navegador(gestor, enviada):
    resposta = _conferir(gestor, enviada)

    assert "no-store" in resposta.headers["Cache-Control"]


def test_a_conferencia_nao_tem_endereco_que_se_abra_por_get(gestor, enviada):
    """A revelação não fica no histórico nem se repete por um clique."""
    resposta = gestor.get(reverse("interface:conferir-identidade", args=[enviada.id]))

    assert resposta.status_code == 405
    assert not _conferencias().exists()


def test_a_pagina_da_conferencia_nao_repete_a_revelacao(gestor, enviada):
    """Nenhum link nem formulário na página leva de novo à conferência."""
    corpo = _conferir(gestor, enviada).content.decode()

    assert reverse("interface:conferir-identidade", args=[enviada.id]) not in corpo


@pytest.mark.parametrize("motivo", ["", "   ", "\n\t "])
def test_sem_motivo_recusa_e_nada_e_revelado(gestor, enviada, motivo):
    """FR-8315: a recusa volta o dossiê, com o CPF mascarado como sempre."""
    resposta = _conferir(gestor, enviada, motivo=motivo)
    corpo = resposta.content.decode()

    assert resposta.status_code == 422
    assert "Escreva o motivo da conferência." in corpo
    assert "***.456.789-**" in corpo
    assert _sem_os_valores(corpo)
    assert "no-store" in resposta.headers["Cache-Control"]
    assert not _conferencias().exists(), "sem revelação não há conferência a registrar"


def test_a_trilha_guarda_quem_qual_inscricao_e_o_motivo_sem_os_valores(gestor, enviada):
    """FR-8316: o registro diz que alguém viu, e não o que viu."""
    _conferir(gestor, enviada)

    registro = _conferencias().get()
    assert registro.actor_subject == "bruno.gestor"
    assert registro.aggregate_type == "Inscricao"
    assert str(registro.aggregate_id) == str(enviada.id)
    assert registro.permission == consulta.CONSULTAR
    assert registro.institution_scope == "cefor"
    assert MOTIVO in registro.reason
    assert enviada.protocolo in registro.reason, "a tela da trilha não mostra o identificador"
    tudo = f"{registro.reason} {registro.detalhe} {registro.previous_state} {registro.new_state}"
    assert _sem_os_valores(tudo)
    assert "Maria" not in tudo


def test_cada_revelacao_e_uma_conferencia(gestor, enviada):
    """Sem idempotência de propósito: quem viu duas vezes, viu duas vezes."""
    _conferir(gestor, enviada)
    _conferir(gestor, enviada, motivo="Segunda conferência, a pedido da comissão.")

    assert _conferencias().count() == 2


def test_o_motivo_vira_uma_linha_de_ate_trezentos_caracteres(gestor, enviada):
    _conferir(gestor, enviada, motivo="  dúvida\n\nna  matrícula  " + "x" * 400)

    registro = _conferencias().get()
    motivo = registro.reason.split(": ", 1)[1]
    assert motivo.startswith("dúvida na matrícula x")
    assert len(motivo) == consulta.TAMANHO_DO_MOTIVO


def test_a_enviada_antes_da_180_diz_que_a_data_nao_foi_informada(gestor, enviada):
    """FR-8304 e o cenário 5 da história 3: a inscrição antiga fica como está, e a tela o diz.

    O desvio do gatilho é o único caminho: desde a `180` o envio recusa quem não tem data, e uma
    enviada sem ela é estado que o produto não produz mais.
    """
    with sem_imutabilidade_da_enviada():
        Inscricao.objects.filter(pk=enviada.pk).update(data_nascimento=None)

    resposta = _conferir(gestor, enviada)
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert CPF_MARIA in corpo
    assert "Não informada nesta inscrição" in corpo
    assert DATA not in corpo, "a data do cadastro não é apresentada como se fosse daquele envio"


def test_os_valores_sao_os_da_inscricao_e_nao_os_do_cadastro(gestor, enviada):
    """O que a pessoa declarou no envio é o que está congelado no ato (FR-8308, FR-8312)."""
    CandidateIdentity.objects.filter(subject=MARIA.subject).update(
        data_nascimento=date(1990, 5, 17)
    )

    corpo = _conferir(gestor, enviada).content.decode()

    assert DATA in corpo
    assert "17/05/1990" not in corpo


# --- A porta ------------------------------------------------------------------------------------


@pytest.mark.parametrize("papel", ["elaborador", "homologador", "publicador", "auditor"])
def test_papel_sem_a_permissao_nao_ve_a_acao_nem_alcanca_a_conferencia(
    client, settings, enviada, papel
):
    """FR-8317: a recusa é a do detalhe, e o endereço montado à mão não revela nada."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, f"pessoa.{papel}", [papel])

    detalhe = client.get(_detalhe(enviada))
    conferencia = _conferir(client, enviada)

    assert detalhe.status_code == 403
    assert conferencia.status_code == detalhe.status_code
    assert "Conferir identidade" not in detalhe.content.decode()
    assert _sem_os_valores(conferencia.content.decode())
    assert not _conferencias().exists()


def test_inscricao_de_outra_unidade_e_inexistente(client, settings, enviada):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "gestor.de.outro", ["gestor"], escopo="outra-unidade")

    resposta = _conferir(client, enviada)

    assert resposta.status_code == 404
    assert _sem_os_valores(resposta.content.decode())
    assert not _conferencias().exists()


def test_rascunho_nao_tem_o_que_conferir(gestor, inscricao_de_maria):
    resposta = _conferir(gestor, inscricao_de_maria)

    assert resposta.status_code == 404
    assert _sem_os_valores(resposta.content.decode())
    assert not _conferencias().exists()


def test_inscricao_que_nao_existe_e_inexistente(gestor, enviada):
    resposta = gestor.post(
        reverse("interface:conferir-identidade", args=["00000000-0000-4000-8000-000000000000"]),
        {"motivo": MOTIVO},
    )

    assert resposta.status_code == 404


def test_sem_sessao_a_conferencia_pede_identificacao(client, settings, enviada):
    settings.INTERFACE_SELETOR_IDENTIDADE = True

    resposta = _conferir(client, enviada)

    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta["Location"]
    assert not _conferencias().exists()


# --- A trilha de quem audita -------------------------------------------------------------------


def test_a_trilha_do_edital_mostra_a_conferencia_com_o_motivo(gestor, client, selecao, enviada):
    """SC-2906: a conferência aparece na tela de quem audita, e não só no banco."""
    _conferir(gestor, enviada)
    identificar(client, "aline.auditora", ["auditor"])

    corpo = client.get(reverse("interface:auditoria", args=[selecao.id])).content.decode()

    assert "Conferência de identidade de inscrição" in corpo
    assert MOTIVO in corpo
    assert enviada.protocolo in corpo
    assert "bruno.gestor" in corpo
    assert _sem_os_valores(corpo)


def test_a_trilha_do_edital_nao_traz_o_resto_do_que_e_auditado_sob_a_inscricao(
    gestor, client, selecao, enviada
):
    """Só a conferência: os atos do candidato e as aberturas do dossiê continuam fora desta tela."""
    gestor.get(_detalhe(enviada))
    _conferir(gestor, enviada)
    sob_a_inscricao = set(
        RegistroAuditoria.objects.filter(aggregate_id=enviada.id).values_list(
            "operation", flat=True
        )
    )
    assert {"CONSULTAR_DOSSIE", consulta.CONFERIR_IDENTIDADE} <= sob_a_inscricao
    identificar(client, "aline.auditora", ["auditor"])

    corpo = client.get(reverse("interface:auditoria", args=[selecao.id])).content.decode()

    assert "Conferência de identidade de inscrição" in corpo
    assert "Consulta ao dossiê da inscrição" not in corpo


def test_a_conferencia_de_outro_edital_nao_aparece_nesta_trilha(
    gestor, client, selecao, enviada, edital_b
):
    """`edital_b`, e não `edital_a`: este cria o Processo pela mesma chave da `selecao`."""
    _conferir(gestor, enviada)
    identificar(client, "aline.auditora", ["auditor"])

    corpo = client.get(reverse("interface:auditoria", args=[edital_b.id])).content.decode()

    assert "Conferência de identidade de inscrição" not in corpo
    assert MOTIVO not in corpo
