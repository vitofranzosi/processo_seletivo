"""Dois CPFs iguais no mesmo Perfil: aceitos, e assinalados (FR-064, FR-065, SC-027).

A `009` impedia isso por acidente — o identificador derivava do CPF, então o mesmo CPF era sempre o
mesmo titular. A `010` desacoplou os dois, e a tentação era repor a regra como restrição. Não foi:
ela transformaria o certame num "primeiro a submeter vence", e como validar dígitos não prova
titularidade, quem conhecesse o CPF alheio poderia submeter primeiro e recusar a inscrição legítima
no envio, com o prazo correndo. O invariante ainda não tem consumidor; o bloqueio teria vítima.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.application.consulta import consulta_de_inscricoes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CPF = "12345678909"


def todas_as_linhas(selecao):
    """As duas seções juntas: a coincidência é assinalada na linha, e rascunho também tem linha."""
    consulta = consulta_de_inscricoes(actor=gestor(), edital_id=selecao.id)
    return [*consulta["recebidas"], *consulta["em_preenchimento"]]


def enviada(selecao, subject, *, cpf=CPF, perfil=PERFIL_DOCENTE):
    registro = Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome="Maria Silva",
        cpf=cpf,
        cpf_normalizado=cpf,
        email=f"{subject}@exemplo.test",
        created_at=timezone.now(),
    )
    Inscricao.objects.filter(pk=registro.pk).update(
        status="SUBMETIDA",
        submitted_at=timezone.now(),
        declaracoes_aceitas_em=timezone.now(),
        versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
        protocolo=f"INS-{uuid.uuid4().hex[:8].upper()}",
    )
    registro.refresh_from_db()
    return registro


def gestor():
    return Actor("bruno.gestor", "cefor", frozenset({"inscricao:consultar"}))


def test_duas_inscricoes_com_o_mesmo_cpf_sao_aceitas(selecao):
    enviada(selecao, "cand:um")
    enviada(selecao, "cand:dois")

    assert Inscricao.objects.filter(cpf_normalizado=CPF).count() == 2


def test_a_coincidencia_e_assinalada_na_consulta(selecao):
    """Não basta ser visível: a listagem exibe CPF mascarado, e comparar máscaras não é detecção."""
    enviada(selecao, "cand:um")
    enviada(selecao, "cand:dois")

    linhas = todas_as_linhas(selecao)

    assert all(linha["cpf_coincidente"] for linha in linhas)


def test_sem_coincidencia_nada_e_assinalado(selecao):
    enviada(selecao, "cand:um")
    enviada(selecao, "cand:dois", cpf="98765432100")

    linhas = todas_as_linhas(selecao)

    assert not any(linha["cpf_coincidente"] for linha in linhas)


def test_o_mesmo_cpf_em_perfis_diferentes_nao_e_coincidencia(selecao):
    """A regra é por Perfil: concorrer a duas vagas distintas é legítimo (Constituição)."""
    enviada(selecao, "cand:um")
    enviada(selecao, "cand:dois", perfil=PERFIL_TECNICO)

    linhas = todas_as_linhas(selecao)

    assert not any(linha["cpf_coincidente"] for linha in linhas)


def test_rascunho_nao_conta_como_coincidencia(selecao):
    """A regra fala do ato de enviar; rascunho é intenção, e rascunho alheio não marca ninguém."""
    enviada(selecao, "cand:um")
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject="cand:tres",
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria Silva",
        cpf=CPF,
        cpf_normalizado=CPF,
        email="tres@exemplo.test",
        created_at=timezone.now(),
    )

    linhas = todas_as_linhas(selecao)

    assert not any(linha["cpf_coincidente"] for linha in linhas)
