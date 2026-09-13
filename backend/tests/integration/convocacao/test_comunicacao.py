"""A comunicação da convocação: na forma declarada, e o que o sistema afirma sobre ela (019).

**O sistema registra que enviou, e nunca que chegou** (`FR-288a`, `UX-039`). A distância entre o
envio e o recebimento é real, e é ela que o Edital resolve dando prazo em dias úteis a partir do
recebimento — não o sistema, que não tem como saber.

**A falha não apaga o ato** (`FR-269a`). A convocação continua praticada; o que se registra é que a
emissão não completou, e o recorte exibe *"convocado, prazo não iniciado"* até que uma emissão
tenha sucesso. Sem essa distinção, uma queda de SMTP fica indistinguível do silêncio da pessoa — e
o desfecho que decorre de silêncio é perda de vaga.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import comunicar as emitir
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def primeiro_chamavel(edital):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return contexto["fila"][0]


def comunicar(edital, gestor, convocacao_id, chave="comunicar", **kwargs):
    return emitir(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
        **kwargs,
    )


def estado(edital, convocacao_id):
    convocacao = Convocacao.objects.prefetch_related("desfechos", "comunicacoes").get(
        id=convocacao_id
    )
    return selectors.estado_de(convocacao, agora=timezone.now())


class TestAFormaDeclarada:
    def test_sem_declaracao_a_emissao_e_recusada(self, cenario_sem_forma, gestor):
        """**A ausência não é a publicação** (`FR-287`).

        O Edital que não disse como convoca não passa a convocar por publicação: o sistema recusa
        emitir, e quem conduz o certame declara a forma por Retificação antes.
        """
        edital, _, _ = cenario_sem_forma
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="sf-conv")

        with pytest.raises(DomainError) as erro:
            comunicar(edital, gestor, convocada["id"], chave="sf-comunicar")

        assert erro.value.code == nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA

    def test_a_mensagem_individual_vai_para_a_credencial_da_pessoa(self, cenario, gestor, caixa):
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="mi-conv")

        declarado = comunicar(edital, gestor, convocada["id"], chave="mi-comunicar")

        assert declarado["forma"] == FORMA_POR_MENSAGEM_INDIVIDUAL
        assert declarado["resultado"] == "ENVIADA"
        assert len(caixa) == 1

    def test_a_publicacao_nao_tem_destinatario_individual(
        self, cenario_por_publicacao, gestor, caixa
    ):
        """A forma do 69/2026: não há caixa de entrada envolvida, e nenhuma é inventada.

        Gravar um destinatário aqui faria a trilha afirmar um endereçamento que não houve.
        """
        edital, _, _ = cenario_por_publicacao
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="pub-conv")

        declarado = comunicar(edital, gestor, convocada["id"], chave="pub-comunicar")

        assert declarado["forma"] == FORMA_POR_PUBLICACAO
        assert declarado["resultado"] == "ENVIADA"
        assert caixa == [], "publicar não põe mensagem em caixa de entrada nenhuma"
        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])
        assert emitida.destinatario == ""

    def test_a_forma_lida_e_a_da_versao_que_a_convocacao_citou(self, cenario, gestor):
        """**Da versão citada, e não da vigente.**

        A convocação congelou a norma que valia quando foi praticada; uma Retificação posterior não
        pode mudar por qual canal aquela chamada foi feita.
        """
        from processo_seletivo.convocacao.application.comunicar import forma_declarada

        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="vc-conv")
        convocacao = Convocacao.objects.select_related("versao").get(id=convocada["id"])

        assert forma_declarada(convocacao) == FORMA_POR_MENSAGEM_INDIVIDUAL


class TestOPrazoCorreDoEnvio:
    def test_antes_do_envio_o_estado_e_prazo_nao_iniciado(self, cenario, gestor):
        """`R-009`: o ato existe e a mensagem não partiu — e isso tem nome próprio."""
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="pi-conv")

        assert estado(edital, convocada["id"]) == nomes.CONVOCADO_PRAZO_NAO_INICIADO

    def test_depois_do_envio_o_prazo_corre(self, cenario, gestor, caixa):
        edital, _, _ = cenario
        convocada = convocar(
            edital,
            gestor,
            primeiro_chamavel(edital),
            vencimento=timezone.now() + timedelta(days=5),
            idempotency_key="pc-conv",
        )

        comunicar(edital, gestor, convocada["id"], chave="pc-comunicar")

        assert estado(edital, convocada["id"]) == nomes.CONVOCADO_PRAZO_EM_CURSO

    def test_vencimento_anterior_ao_envio_e_recusado(self, cenario, gestor, caixa):
        """`FR-269b`: prazo que vence antes de a pessoa poder saber não é prazo.

        **A conferência é na emissão, e não na convocação**, porque é o envio que inicia o relógio:
        no instante de convocar ainda não existe envio com que comparar.
        """
        edital, _, _ = cenario
        convocada = convocar(
            edital,
            gestor,
            primeiro_chamavel(edital),
            vencimento=timezone.now() - timedelta(days=1),
            idempotency_key="va-conv",
        )

        with pytest.raises(DomainError) as erro:
            comunicar(edital, gestor, convocada["id"], chave="va-comunicar")

        assert erro.value.code == nomes.VENCIMENTO_ANTERIOR_AO_ENVIO
        assert caixa == [], "nada é enviado quando o prazo já nasceria vencido"


class TestAFalhaNaoDesfazOAto:
    @pytest.fixture
    def correio_quebrado(self, settings):
        settings.EMAIL_BACKEND = "tests.unit.convocacao.test_mensagem.CorreioQueFalha"

    def test_a_falha_e_registrada_e_a_convocacao_continua_praticada(
        self, cenario, gestor, correio_quebrado
    ):
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="fa-conv")

        declarado = comunicar(edital, gestor, convocada["id"], chave="fa-comunicar")

        assert declarado["resultado"] == "FALHA"
        assert declarado["enviadaEm"] is None
        assert Convocacao.objects.filter(id=convocada["id"]).exists()

    def test_a_falha_nao_inicia_o_prazo(self, cenario, gestor, correio_quebrado):
        """**É a metade que importa** (`FR-269a`).

        Sem ela, a pessoa perderia a vaga por um servidor de SMTP fora do ar — e a trilha diria que
        ela não atendeu.
        """
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="fp-conv")

        comunicar(edital, gestor, convocada["id"], chave="fp-comunicar")

        assert estado(edital, convocada["id"]) == nomes.CONVOCADO_PRAZO_NAO_INICIADO

    def test_a_reemissao_depois_da_falha_inicia_o_prazo(self, cenario, gestor, settings, caixa):
        """A emissão seguinte cria linha nova — a falha continua legível, e o prazo parte dali."""
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="re-conv")
        settings.EMAIL_BACKEND = "tests.unit.convocacao.test_mensagem.CorreioQueFalha"
        comunicar(edital, gestor, convocada["id"], chave="re-falha")
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

        comunicar(edital, gestor, convocada["id"], chave="re-sucesso")

        assert estado(edital, convocada["id"]) == nomes.CONVOCADO_PRAZO_EM_CURSO
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 2

    def test_o_detalhe_tecnico_nao_carrega_dado_pessoal(self, cenario, gestor, correio_quebrado):
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="dt-conv")

        declarado = comunicar(edital, gestor, convocada["id"], chave="dt-comunicar")
        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])

        assert emitida.detalhe_tecnico
        assert "@" not in emitida.detalhe_tecnico


def test_nenhum_campo_da_comunicacao_afirma_recebimento(cenario, gestor, caixa):
    """`UX-039`: o sistema afirma o envio, e não afirma o recebimento.

    O campo que não existe é a metade da garantia; a outra é a varredura sobre as telas, porque
    prosa mente sem precisar de coluna.
    """
    edital, _, _ = cenario
    convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="uc-conv")
    declarado = comunicar(edital, gestor, convocada["id"], chave="uc-comunicar")

    assert "enviadaEm" in declarado
    assert not {"recebidaEm", "lidaEm", "entregueEm"} & set(declarado)
