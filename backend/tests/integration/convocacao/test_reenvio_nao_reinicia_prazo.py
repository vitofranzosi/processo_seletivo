"""O reenvio da comunicação não reinicia o prazo da convocação (019, `FR-269a`, `FR-269b`).

**A suspeita era razoável, e é por isso que ela virou teste.** `envio_de` toma o envio
bem-sucedido **mais recente**, e a tela oferece "Emitir a comunicação de novo". Se o prazo fosse
contado do envio, cada reenvio devolveria à pessoa o prazo inteiro — e o desfecho de não
atendimento, que pressupõe prazo decorrido, ficaria adiado por um gesto operacional, sem regra nem
decisão que o fundamentasse.

**Não é assim porque o vencimento é data absoluta**, informada ao convocar (`R-004`: o sistema não
calcula dias úteis). O envio decide **se** o prazo corre, e não **até quando**. Estes casos
prendem essa leitura: quem um dia mudar o vencimento para "N dias a partir do envio" verá os três
falharem, e terá de decidir por escrito o que um reenvio faz com o prazo — em vez de descobrir pela
pessoa que perdeu a vaga, ou pela que ganhou dias que o Edital não dava.

A hipótese foi levantada e descartada na auditoria de 09/10/2026 sobre os avisos aos candidatos.
Os dois resíduos de redação que ela deixou estão em
`doc/achado-reenvio-da-convocacao-sugere-prazo-novo.md`.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import comunicar
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
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


@pytest.fixture
def relogio(monkeypatch):
    """Avança o relógio da aplicação, para chegar à véspera e passar do vencimento.

    `comando_de_comissao` e `comunicar` leem `timezone.now()` na hora do ato, e é esse instante que
    as recusas comparam com o vencimento: não há outro modo de praticar um ato "dois dias depois".
    """
    real = timezone.now

    def avancar(**intervalo):
        monkeypatch.setattr(timezone, "now", lambda: real() + timedelta(**intervalo))

    return avancar


def _convocar_com_vencimento(edital, gestor, vencimento, chave):
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    return convocar(
        edital, gestor, contexto["fila"][0], vencimento=vencimento, idempotency_key=chave
    )


def _emitir(edital, gestor, convocacao_id, chave):
    return comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        idempotency_key=chave,
        correlation_id="teste-reenvio-019",
    )


def _dar_por_nao_atendida(edital, gestor, convocacao_id, chave):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=nomes.NAO_ATENDIMENTO,
        fundamento="Prazo decorrido sem manifestação.",
        idempotency_key=chave,
        correlation_id="teste-reenvio-019",
    )


def _carregar(convocacao_id):
    return Convocacao.objects.prefetch_related("desfechos", "comunicacoes").get(id=convocacao_id)


def _prazo_da_mensagem(mensagem):
    return mensagem.body.split("Prazo para atender:")[1].split(",")[0]


def test_o_reenvio_nao_move_o_vencimento_nem_o_estado(cenario, gestor, caixa):
    """Dois envios, um vencimento: o segundo muda o "enviada em", e só ele.

    **O "enviada em" passa a ser o do reenvio**, e é exatamente isso que fazia suspeitar. O que
    decide o estado é o vencimento, que nenhum envio toca.
    """
    edital, _, _ = cenario
    vencimento = timezone.now() + timedelta(days=2)
    convocada = _convocar_com_vencimento(edital, gestor, vencimento, "reenvio-conv")

    primeira = _emitir(edital, gestor, convocada["id"], "reenvio-1")
    segunda = _emitir(edital, gestor, convocada["id"], "reenvio-2")

    assert primeira["resultado"] == segunda["resultado"] == "ENVIADA"
    assert ComunicacaoEmitida.objects.filter(convocacao_id=convocada["id"]).count() == 2
    convocacao = _carregar(convocada["id"])
    assert convocacao.vencimento == vencimento
    assert selectors.envio_de(convocacao).isoformat() == segunda["enviadaEm"]
    assert (
        selectors.estado_de(convocacao, agora=vencimento + timedelta(minutes=1))
        == nomes.CONVOCADO_VENCIMENTO_DECORRIDO
    )
    assert _prazo_da_mensagem(caixa[0]) == _prazo_da_mensagem(caixa[1]), (
        "as duas mensagens trazem a mesma data-limite"
    )


def test_depois_do_vencimento_o_reenvio_e_recusado(cenario, gestor, caixa, relogio):
    """Vencido o prazo, não há reenvio que o reabra (`FR-269b`), e o não atendimento segue livre."""
    edital, _, _ = cenario
    vencimento = timezone.now() + timedelta(days=2)
    convocada = _convocar_com_vencimento(edital, gestor, vencimento, "vencido-conv")
    _emitir(edital, gestor, convocada["id"], "vencido-1")

    relogio(days=3)
    with pytest.raises(DomainError) as erro:
        _emitir(edital, gestor, convocada["id"], "vencido-2")

    assert erro.value.code == nomes.VENCIMENTO_ANTERIOR_AO_ENVIO
    assert len(caixa) == 1, "nada sai depois do vencimento"
    _dar_por_nao_atendida(edital, gestor, convocada["id"], "vencido-desfecho")
    assert selectors.desfecho_de(_carregar(convocada["id"])) is not None


def test_o_reenvio_na_vespera_nao_adia_o_nao_atendimento(cenario, gestor, caixa, relogio):
    """O caso que mais custaria: reenviar na véspera e, com isso, empurrar a porta para depois.

    Cinco minutos depois do vencimento **original**, o não atendimento é aceito: o reenvio da
    véspera não deu à pessoa um dia a mais que o Edital não dava.
    """
    edital, _, _ = cenario
    vencimento = timezone.now() + timedelta(days=2)
    convocada = _convocar_com_vencimento(edital, gestor, vencimento, "vespera-conv")
    _emitir(edital, gestor, convocada["id"], "vespera-1")

    relogio(days=1, hours=23)
    _emitir(edital, gestor, convocada["id"], "vespera-2")

    relogio(days=2, minutes=5)
    _dar_por_nao_atendida(edital, gestor, convocada["id"], "vespera-desfecho")
    assert selectors.desfecho_de(_carregar(convocada["id"])) is not None
