"""O que a reconciliação faz quando não consegue reconciliar — e a assimetria entre os dois casos.

**Inscrição enviada sem CPF utilizável interrompe** (FR-046). A restrição que a migração seguinte
instala não caberia sobre ela, e prosseguir exigiria escolher um número por conta própria — que é
exatamente o que a FR-047 proíbe. Falhar aqui é falhar onde alguém está olhando, com a lista do
que precisa de tratamento.

**Rascunho sem CPF utilizável apenas relata** (FR-045). Ele não impede a restrição de existir, e
não há nada a decidir: fica intacto, não reconciliado.

E nada disso menciona CPF no registro técnico (FR-009): o relatório fala por identificador.
"""

import importlib
import logging
import uuid

import pytest
from django.apps import apps
from django.db import connection
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

reconciliacao = importlib.import_module(
    "processo_seletivo.identidade.migrations.0002_reconciliacao"
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF_DE_MARIA = "12345678909"


@pytest.fixture
def relato():
    """O que a migração registrou.

    `caplog` não serve: o logger `processo_seletivo` tem `propagate: False`, e o coletor do pytest
    escuta a raiz. Escutar o logger diretamente é o que enxerga o que a implantação enxergaria.
    """

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__()
            self.linhas = []

        def emit(self, registro):
            self.linhas.append(registro.getMessage())

        @property
        def texto(self):
            return "\n".join(self.linhas)

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo.identidade.reconciliacao")
    logger.addHandler(coletor)
    yield coletor
    logger.removeHandler(coletor)


@pytest.fixture
def sem_a_restricao_de_cpf():
    """A linha malformada precisa existir **antes** da restrição, como existiria na realidade.

    Em produção a ordem é essa: a base já tem o que tem, e a restrição só entra depois que a
    reconciliação verificou. No teste, as migrações já rodaram todas — então a restrição sai por
    um instante, para que se possa encenar a base que a implantação vai encontrar.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE inscricoes_inscricao DROP CONSTRAINT ck_inscricao_submetida_com_cpf"
        )
    yield


def inscricao(selecao, *, subject, cpf, status="RASCUNHO", perfil=PERFIL_DOCENTE, **campos):
    registro = Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome=campos.get("nome", "Maria Silva"),
        cpf=cpf,
        cpf_normalizado=cpf,
        email=campos.get("email", "m@ex.br"),
        created_at=timezone.now(),
    )
    if status != "RASCUNHO":
        # Direto no banco: a guarda de `save()` recusa alterar enviada, e o que se quer aqui é
        # justamente a linha malformada que uma carga manual produziria. Enviada de verdade —
        # instante, protocolo, versão aceita e declarações —, e só o CPF fora do lugar: é assim
        # que o problema chega, e não como uma linha pela metade.
        from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

        Inscricao.objects.filter(pk=registro.pk).update(
            status=status,
            submitted_at=timezone.now(),
            declaracoes_aceitas_em=timezone.now(),
            versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
            protocolo=f"INS-{uuid.uuid4().hex[:8].upper()}",
        )
        registro.refresh_from_db()
    return registro


def test_inscricao_enviada_sem_cpf_interrompe_a_implantacao(selecao, sem_a_restricao_de_cpf):
    registro = inscricao(selecao, subject="demo:um", cpf="", status="SUBMETIDA")

    with pytest.raises(RuntimeError) as recusa:
        reconciliacao.reconciliar(apps, None)

    assert str(registro.id) in str(recusa.value)
    assert CandidateIdentity.objects.count() == 0, "nada é criado antes de a verificação passar"


def test_inscricao_enviada_com_cpf_invalido_tambem_interrompe(selecao, sem_a_restricao_de_cpf):
    """Onze dígitos que não fecham nos verificadores não são CPF, e a restrição não os pega."""
    inscricao(selecao, subject="demo:um", cpf="11111111111", status="SUBMETIDA")

    with pytest.raises(RuntimeError):
        reconciliacao.reconciliar(apps, None)


def test_rascunho_sem_cpf_fica_intacto_e_nao_reconciliado(selecao, relato):
    registro = inscricao(selecao, subject="demo:um", cpf="")

    reconciliacao.reconciliar(apps, None)

    registro.refresh_from_db()
    assert registro.identity_subject == "demo:um", "intacto"
    assert CandidateIdentity.objects.count() == 0, "não reconciliado"
    assert str(registro.id) in relato.texto, "relatado"


def test_grupo_com_dois_identificadores_relata_sem_interromper(selecao, relato):
    """Só acontece se a chave secreta tiver rotacionado durante a vigência da `009`."""
    uma = inscricao(selecao, subject="demo:antes", cpf=CPF_DE_MARIA)
    outra = inscricao(selecao, subject="demo:depois", cpf=CPF_DE_MARIA, perfil=PERFIL_TECNICO)

    reconciliacao.reconciliar(apps, None)

    assert CandidateIdentity.objects.count() == 0, "não escolhe um dos dois donos"
    for registro in (uma, outra):
        registro.refresh_from_db()
    assert (uma.identity_subject, outra.identity_subject) == ("demo:antes", "demo:depois")
    assert "demo:antes" in relato.texto and "demo:depois" in relato.texto


def test_o_relatorio_nao_menciona_cpf(selecao, relato):
    """O identificador existe para não carregar dado pessoal.

    Ele não pode voltar pelo registro técnico (FR-009).
    """
    inscricao(selecao, subject="demo:antes", cpf=CPF_DE_MARIA)
    inscricao(selecao, subject="demo:depois", cpf=CPF_DE_MARIA, perfil=PERFIL_TECNICO)

    reconciliacao.reconciliar(apps, None)

    assert CPF_DE_MARIA not in relato.texto
    assert "123.456.789-09" not in relato.texto


def test_um_grupo_irreconciliavel_nao_impede_os_demais(selecao, relato):
    inscricao(selecao, subject="demo:antes", cpf=CPF_DE_MARIA)
    inscricao(selecao, subject="demo:depois", cpf=CPF_DE_MARIA, perfil=PERFIL_TECNICO)
    inscricao(selecao, subject="demo:joao", cpf="98765432100", perfil=PERFIL_TECNICO)

    reconciliacao.reconciliar(apps, None)

    assert [identidade.subject for identidade in CandidateIdentity.objects.all()] == ["demo:joao"]
