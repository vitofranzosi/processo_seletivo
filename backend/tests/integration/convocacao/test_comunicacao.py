"""A comunicação da convocação: na forma declarada, e o que o sistema afirma sobre ela (019).

**O sistema registra que enviou, e nunca que chegou** (`FR-288a`, `UX-039`). A distância entre o
envio e o recebimento é real, e é ela que o Edital resolve dando prazo em dias úteis a partir do
recebimento — não o sistema, que não tem como saber.

**A falha não apaga o ato** (`FR-269a`). A convocação continua praticada; o que se registra é que a
emissão não completou, e o recorte exibe *"convocado, prazo não iniciado"* até que uma emissão
tenha sucesso. Sem essa distinção, uma queda de SMTP fica indistinguível do silêncio da pessoa — e
o desfecho que decorre de silêncio é perda de vaga.
"""

import threading
from datetime import timedelta

import pytest
from django.core import mail
from django.db import connection
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

        declarado = comunicar(
            edital,
            gestor,
            convocada["id"],
            chave="pub-comunicar",
            referencia_da_publicacao="Site do Cefor, 13/09/2026, item 7.2 do Edital 69/2026.",
        )

        assert declarado["forma"] == FORMA_POR_PUBLICACAO
        assert declarado["resultado"] == "ENVIADA"
        assert caixa == [], "publicar não põe mensagem em caixa de entrada nenhuma"
        emitida = ComunicacaoEmitida.objects.get(id=declarado["id"])
        assert emitida.destinatario == ""
        assert "Site do Cefor" in emitida.referencia_da_publicacao

    def test_a_publicacao_sem_referencia_e_recusada(self, cenario_por_publicacao, gestor, caixa):
        """**O sistema não publica no site do certame**, e a `R-007` não lhe deu essa capacidade.

        Gravar `ENVIADA` sem dizer onde se publicou iniciaria o prazo do item 7.2 do 69/2026 contra
        alguém que não teve como saber — e o registro é append-only: não haveria como desfazê-lo.
        """
        edital, _, _ = cenario_por_publicacao
        convocada = convocar(
            edital, gestor, primeiro_chamavel(edital), idempotency_key="pub-sem-ref-conv"
        )

        with pytest.raises(DomainError) as erro:
            comunicar(edital, gestor, convocada["id"], chave="pub-sem-ref")

        assert erro.value.code == nomes.REFERENCIA_DA_PUBLICACAO_OBRIGATORIA
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 0

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


class CorreioQueObservaATransacao:
    """Registra se o envio aconteceu **dentro** de uma transação aberta."""

    dentro_da_transacao = None

    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, mensagens):
        from django.db import connection as conexao

        CorreioQueObservaATransacao.dentro_da_transacao = conexao.in_atomic_block
        return len(mensagens)


def test_o_envio_acontece_fora_da_transacao_que_trava_o_processo(cenario, gestor, settings):
    """**A regra que `inscricoes/application/mensagem.py` escreve com todas as letras.**

    `comando_de_comissao` trava o Processo com `select_for_update`. Um SMTP lento dentro dela
    paralisaria **todos** os comandos daquele certame; e um `rollback` posterior desfaria o registro
    sem desfazer a mensagem — o candidato ficaria com uma convocação na caixa de entrada que o
    sistema esqueceu de ter enviado.

    A ordem certa é a que `exigir_base_de_comissao` existe para permitir: autorizar, ir à rede, e só
    então abrir a transação que grava e audita.
    """
    settings.EMAIL_BACKEND = (
        "tests.integration.convocacao.test_comunicacao.CorreioQueObservaATransacao"
    )
    CorreioQueObservaATransacao.dentro_da_transacao = None
    edital, _, _ = cenario
    convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="tx-conv")

    declarado = comunicar(edital, gestor, convocada["id"], chave="tx-comunicar")

    assert declarado["resultado"] == "ENVIADA"
    assert CorreioQueObservaATransacao.dentro_da_transacao is False, (
        "o envio correu dentro da transação que trava o Processo"
    )


def test_o_ator_sem_base_nao_faz_o_sistema_ir_a_rede(cenario, sem_nada, gestor, settings):
    """**Autorizar antes de trabalhar** (Princípio III).

    Com o envio fora da transação, a tentação é conferir autoridade só ao gravar — e aí quem não
    pode nada já teria feito o sistema entregar a mensagem.
    """
    settings.EMAIL_BACKEND = (
        "tests.integration.convocacao.test_comunicacao.CorreioQueObservaATransacao"
    )
    CorreioQueObservaATransacao.dentro_da_transacao = None
    edital, _, _ = cenario
    convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="aut-conv")

    with pytest.raises(DomainError) as erro:
        comunicar(edital, sem_nada, convocada["id"], chave="aut-comunicar")

    assert erro.value.code == "not_found"
    assert CorreioQueObservaATransacao.dentro_da_transacao is None, "nada foi enviado"


class CorreioQueEspera:
    """Um backend que avisa quando o envio começou e só termina quando alguém o libera.

    Existe para tornar a concorrência **determinística**: sem ele, "duas requisições ao mesmo
    tempo" seria uma corrida que passa ou falha conforme a máquina.
    """

    chegou = threading.Event()
    liberado = threading.Event()
    entregas = 0

    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, mensagens):
        CorreioQueEspera.entregas += len(mensagens)
        CorreioQueEspera.chegou.set()
        CorreioQueEspera.liberado.wait(timeout=10)
        return len(mensagens)


class TestAIdempotenciaDaEmissao:
    """A chave é reservada **antes** do envio (`FR-288`).

    **Tirar o SMTP de dentro da transação deixou a idempotência depois dele.** Um duplo clique, ou
    o retry de um proxy, entregava a segunda mensagem e só então descobria que o ato já havia
    terminado — e a pessoa recebia duas convocações para a mesma vaga, com dois instantes de envio
    diferentes brigando pelo início do prazo.
    """

    def test_a_repeticao_concluida_devolve_o_desfecho_sem_enviar_de_novo(
        self, cenario, gestor, caixa
    ):
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="id-conv")

        primeira = comunicar(edital, gestor, convocada["id"], chave="id-mesma")
        segunda = comunicar(edital, gestor, convocada["id"], chave="id-mesma")

        assert primeira == segunda
        assert len(caixa) == 1, "a repetição não põe uma segunda mensagem na caixa"
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 1

    def test_a_chave_nova_emite_de_novo(self, cenario, gestor, caixa):
        """A repetição é da **chave**, e não do ato: reemitir depois de uma falha é legítimo."""
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="id-nova")

        comunicar(edital, gestor, convocada["id"], chave="id-uma")
        comunicar(edital, gestor, convocada["id"], chave="id-outra")

        assert len(caixa) == 2
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 2

    def test_a_reserva_pendente_nao_reenvia_e_pede_reconciliacao(self, cenario, gestor, caixa):
        """**O caso da falha entre o envio e a gravação.**

        A reserva foi criada e nunca concluída: ou o envio está em curso, ou ele saiu e o registro
        não entrou. As duas hipóteses têm a mesma aparência daqui, e reenviar entregaria a mesma
        convocação duas vezes.
        """
        from processo_seletivo.shared.idempotency import reservar

        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="id-pend")
        # A reserva que uma tentativa anterior deixou para trás, com a mesma carga.
        reservar(
            actor=gestor,
            operation="convocacao:comunicar",
            key="id-orfa",
            payload={"convocacao": convocada["id"]},
        )

        with pytest.raises(DomainError) as erro:
            comunicar(edital, gestor, convocada["id"], chave="id-orfa")

        assert erro.value.code == nomes.EMISSAO_EM_ESTADO_INDETERMINADO
        assert "pode ter saído" in erro.value.detail
        assert caixa == [], "nada é enviado sobre uma reserva pendente"

    def test_a_falha_na_gravacao_depois_do_envio_deixa_o_estado_indeterminado(
        self, cenario, gestor, caixa, monkeypatch
    ):
        """O percurso inteiro do caso: envia, a gravação falha, e a retentativa **não** reenvia."""
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="id-falha")

        def explodir(self, *args, **kwargs):
            raise RuntimeError("o disco sumiu entre o envio e a gravação")

        monkeypatch.setattr(ComunicacaoEmitida, "save", explodir)
        with pytest.raises(RuntimeError):
            comunicar(edital, gestor, convocada["id"], chave="id-falha-chave")
        monkeypatch.undo()

        assert len(caixa) == 1, "a mensagem saiu"
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 0

        with pytest.raises(DomainError) as erro:
            comunicar(edital, gestor, convocada["id"], chave="id-falha-chave")

        assert erro.value.code == nomes.EMISSAO_EM_ESTADO_INDETERMINADO
        assert len(caixa) == 1, "e a retentativa não põe uma segunda na caixa"

    def test_duas_requisicoes_simultaneas_entregam_uma_mensagem_so(self, cenario, gestor, settings):
        """A concorrência de verdade: a segunda chega enquanto a primeira ainda está na rede.

        **É o duplo clique**, e o `UNIQUE` da reserva é quem o resolve — não a duração de transação
        nenhuma.
        """
        settings.EMAIL_BACKEND = "tests.integration.convocacao.test_comunicacao.CorreioQueEspera"
        CorreioQueEspera.chegou.clear()
        CorreioQueEspera.liberado.clear()
        CorreioQueEspera.entregas = 0
        edital, _, _ = cenario
        convocada = convocar(edital, gestor, primeiro_chamavel(edital), idempotency_key="id-conc")
        desfecho = {}

        def emitir():
            try:
                desfecho["primeira"] = comunicar(
                    edital, gestor, convocada["id"], chave="id-simultanea"
                )
            finally:
                connection.close()

        thread = threading.Thread(target=emitir)
        thread.start()
        try:
            assert CorreioQueEspera.chegou.wait(timeout=10), "a primeira não chegou à rede"
            with pytest.raises(DomainError) as erro:
                comunicar(edital, gestor, convocada["id"], chave="id-simultanea")
        finally:
            CorreioQueEspera.liberado.set()
            thread.join(timeout=10)

        assert erro.value.code == nomes.EMISSAO_EM_ESTADO_INDETERMINADO
        assert CorreioQueEspera.entregas == 1, "uma mensagem, e não duas"
        assert desfecho["primeira"]["resultado"] == "ENVIADA"
        assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 1
