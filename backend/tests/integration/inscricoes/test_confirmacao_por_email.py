"""A confirmação da inscrição sai uma vez, e cada tentativa deixa rastro (181).

O comando, sem tela: `confirmacao.confirmar`. A jornada pela tela está em
`tests/integration/portal/test_confirmacao_de_inscricao.py`.

**O que mudou, e por quê.** Antes da `181`, a falha ia ao log sem dizer de qual inscrição, o
servidor que não aceitava sem levantar erro passava por sucesso, e o duplo clique simultâneo mandava
duas mensagens. Cada caso abaixo é um desses defeitos fechado, ou uma garantia que o fechamento não
podia quebrar.
"""

import logging
import threading
from datetime import timedelta

import pytest
from django.core import mail
from django.db import connection, connections, transaction

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.inscricoes.application import confirmacao
from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    ator_do_candidato,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.concurrency import travar_consultivamente
from tests.fixtures import correio
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, PERFIL_TECNICO, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="A corrida é entre conexões; em sqlite a escrita já é serializada e ela não existe.",
)

DADOS = {
    "protocolo": "2026-0001-0001",
    "verificacao": "AAAA-BBBB",
    "selecao": "Especialização\nEdital 1/2026",
    "edital": "1/2026",
    "perfil": "Docente",
    "modalidade": "Ampla concorrência",
    "quando": "18/11/2026 às 10:00",
    "documentos": [{"requisito": "RG", "arquivo": "rg.pdf"}],
    "endereco": "http://testserver/selecoes/inscricoes/x/comprovante",
    "assinatura": "Cefor/Ifes",
}


#: O servidor que não responde: a exceção que o SMTP levanta. A resposta `0` é o que aceita a
#: conexão e não aceita a mensagem, sem erro.
FORA_DO_AR = ConnectionRefusedError("servidor de correio fora do ar")
LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def registro_tecnico():
    """O que o logger da inscrição escreveu. Ele não propaga à raiz — tem o próprio formatador em
    JSON —, e por isso o `caplog` não o vê: o handler vai direto nele."""
    linhas = []

    class Guardar(logging.Handler):
        def emit(self, record):
            linhas.append(record.getMessage())

    logger = logging.getLogger("processo_seletivo.inscricoes")
    handler = Guardar(level=logging.ERROR)
    logger.addHandler(handler)
    yield linhas
    logger.removeHandler(handler)


@pytest.fixture
def sem_intervalo(monkeypatch):
    """A nova tentativa sem o minuto de espera (FR-8363), para os casos que a fazem em seguida."""
    monkeypatch.setattr(confirmacao, "INTERVALO_ENTRE_TENTATIVAS", timedelta(0))


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = LOCMEM
    mail.outbox.clear()
    return mail.outbox


def _pronta(edital, perfil=PERFIL_DOCENTE):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    exigidos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if perfil == PERFIL_DOCENTE:
        exigidos.append((DOCUMENTO_DO_PERFIL, "diploma.pdf"))
    for requisito, nome in exigidos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviada(edital, perfil=PERFIL_DOCENTE):
    inscricao = _pronta(edital, perfil)
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key=f"envio-{inscricao.id}",
    )


def _confirmar(inscricao):
    return confirmacao.confirmar(
        inscricao=inscricao,
        ator=ator_do_candidato(MARIA, inscricao.edital),
        montar_dados=lambda: DADOS,
        correlation_id="teste-181",
    )


def _trilha(inscricao):
    return list(
        RegistroAuditoria.objects.filter(
            aggregate_type="Inscricao", aggregate_id=inscricao.id, operation=confirmacao.OPERACAO
        ).order_by("occurred_at")
    )


# --- FR-8350: só a enviada ----------------------------------------------------------------------


def test_o_rascunho_nao_recebe_confirmacao(caixa, selecao):
    rascunho = _pronta(selecao)
    assert rascunho.status == Inscricao.Status.RASCUNHO

    assert _confirmar(rascunho) is None
    assert caixa == []
    assert _trilha(rascunho) == []


def test_a_enviada_recebe_e_a_tentativa_fica_na_trilha(caixa, selecao):
    enviada = _enviada(selecao)

    tentativa = _confirmar(enviada)

    assert tentativa.numero == 1 and tentativa.enviada
    (mensagem,) = caixa
    assert mensagem.to == [enviada.email]
    (registro,) = _trilha(enviada)
    assert registro.detalhe == {"tentativa": 1, "resultado": "ENVIADA"}
    assert registro.actor_subject == MARIA.subject
    assert registro.institution_scope == enviada.edital.institution_scope
    assert confirmacao.ultima(enviada) == tentativa


def test_a_trilha_nao_guarda_endereco_nome_nem_protocolo(caixa, selecao):
    """FR-8358: o número, o instante e o resultado bastam para achar o resto."""
    enviada = _enviada(selecao)

    _confirmar(enviada)

    (registro,) = _trilha(enviada)
    gravado = f"{registro.reason} {registro.detalhe} {registro.previous_state} {registro.new_state}"
    for dado in (enviada.email, MARIA.nome, enviada.protocolo, MARIA.cpf):
        assert dado not in gravado


# --- FR-8351: uma vez só --------------------------------------------------------------------------


def test_a_segunda_chamada_nao_envia_nem_registra(caixa, selecao):
    """A repetição idempotente do envio, a aba antiga, o botão apertado de novo."""
    enviada = _enviada(selecao)
    _confirmar(enviada)

    assert _confirmar(enviada) is None
    assert len(caixa) == 1
    assert len(_trilha(enviada)) == 1


def test_montar_os_dados_so_quando_ha_envio(caixa, selecao):
    """A repetição não lê o comprovante inteiro para não mandar nada."""
    enviada = _enviada(selecao)
    _confirmar(enviada)
    chamadas = []

    confirmacao.confirmar(
        inscricao=enviada,
        ator=ator_do_candidato(MARIA, enviada.edital),
        montar_dados=lambda: chamadas.append(1) or DADOS,
    )

    assert chamadas == []


@SOMENTE_POSTGRES
def test_duas_requisicoes_simultaneas_mandam_uma_mensagem(caixa, selecao):
    """O defeito que a 181 fecha: as duas chegavam juntas e as duas mandavam."""
    enviada = _enviada(selecao)
    barreira = threading.Barrier(2, timeout=10)
    resultados = []

    def confirmar_em_paralelo():
        try:
            barreira.wait()
            resultados.append(_confirmar(Inscricao.objects.get(pk=enviada.pk)))
        finally:
            connections.close_all()

    fios = [threading.Thread(target=confirmar_em_paralelo) for _ in range(2)]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=20)

    assert len(caixa) == 1
    assert sorted(r is None for r in resultados) == [False, True]
    assert [r.detalhe for r in _trilha(enviada)] == [{"tentativa": 1, "resultado": "ENVIADA"}]


# --- FR-8352, FR-8360, FR-8361: a falha -----------------------------------------------------------


@pytest.mark.parametrize("resposta", [FORA_DO_AR, 0], ids=["fora-do-ar", "nao-aceita"])
def test_a_falha_e_registrada_como_nao_enviada(settings, selecao, resposta):
    enviada = _enviada(selecao)
    correio.usar(settings, resposta)

    tentativa = _confirmar(enviada)

    assert tentativa.numero == 1 and not tentativa.enviada
    (registro,) = _trilha(enviada)
    assert registro.detalhe == {"tentativa": 1, "resultado": "NAO_ENVIADA"}
    enviada.refresh_from_db()
    assert enviada.status == Inscricao.Status.SUBMETIDA, "a falha não toca a inscrição"


def test_depois_da_falha_a_nova_tentativa_envia_e_e_a_segunda(settings, selecao, sem_intervalo):
    """FR-8363 e SC-2925: a trilha responde quantas tentativas, quando e com que resultado."""
    enviada = _enviada(selecao)
    correio.usar(settings, FORA_DO_AR)
    caixa = mail.outbox
    _confirmar(enviada)

    tentativa = _confirmar(enviada)

    assert tentativa.numero == 2 and tentativa.enviada
    assert len(caixa) == 1
    lidas = confirmacao.tentativas(enviada)
    assert [(t.numero, t.resultado) for t in lidas] == [(1, "NAO_ENVIADA"), (2, "ENVIADA")]
    assert lidas[0].em <= lidas[1].em
    assert _confirmar(enviada) is None, "e, aceita, não sai uma terceira"


def test_o_log_diz_a_inscricao_e_nao_o_endereco(settings, selecao, registro_tecnico):
    """FR-8361: o identificador acha a falha na trilha; o endereço não tem por que estar no log."""
    enviada = _enviada(selecao)
    correio.usar(settings, 0)

    _confirmar(enviada)

    registrado = "\n".join(registro_tecnico)
    assert str(enviada.id) in registrado
    assert enviada.email not in registrado


def test_a_trilha_que_falha_nao_derruba_quem_pediu(caixa, selecao, monkeypatch, registro_tecnico):
    """A mensagem já saiu: a falha da trilha vai ao log, e a chamada volta sem tentativa."""
    enviada = _enviada(selecao)

    def recusar(**_):
        raise RuntimeError("trilha fora do ar")

    monkeypatch.setattr(confirmacao, "record_event", recusar)
    assert _confirmar(enviada) is None

    assert len(caixa) == 1
    assert any("não foi gravada" in linha for linha in registro_tecnico)


# --- FR-8368: cada inscrição tem a sua --------------------------------------------------------


def test_duas_inscricoes_da_mesma_pessoa_tem_cada_uma_a_sua(settings, selecao, sem_intervalo):
    docente = _enviada(selecao, PERFIL_DOCENTE)
    tecnico = _enviada(selecao, PERFIL_TECNICO)
    correio.usar(settings, 1, FORA_DO_AR)

    _confirmar(docente)
    _confirmar(tecnico)

    assert len(mail.outbox) == 1
    assert confirmacao.ultima(docente).enviada
    assert not confirmacao.ultima(tecnico).enviada
    assert _confirmar(tecnico).numero == 2, "a confirmação da outra não conta para esta"
    assert len(mail.outbox) == 2


def test_sem_tentativa_a_ultima_e_nenhuma(selecao):
    """A inscrição anterior à 181, ou a do cenário de treinamento: a tela não afirma nada."""
    assert confirmacao.ultima(_enviada(selecao)) is None


# --- Revisão de 18/11: o intervalo, a trava que não espera, o endereço e a contenção -------------


def test_dentro_do_intervalo_a_nova_tentativa_nao_sai(settings, selecao):
    """FR-8363: o clique repetido não vira carga sobre um servidor de correio fora do ar."""
    enviada = _enviada(selecao)
    correio.usar(settings, FORA_DO_AR)
    _confirmar(enviada)

    assert _confirmar(enviada) is None
    assert mail.outbox == []
    assert len(_trilha(enviada)) == 1
    espera = confirmacao.espera_para_tentar_de_novo(confirmacao.ultima(enviada))
    assert timedelta(0) < espera <= confirmacao.INTERVALO_ENTRE_TENTATIVAS


@SOMENTE_POSTGRES
def test_com_outra_tentativa_em_curso_volta_sem_esperar_e_sem_enviar(caixa, selecao):
    """A trava não espera: a outra tentativa registra o que acontecer, e esta não enfileira."""
    enviada = _enviada(selecao)
    tomada, liberar = threading.Event(), threading.Event()

    def segurar_a_trava():
        try:
            with transaction.atomic():
                travar_consultivamente(f"inscricao:confirmar:{enviada.pk}")
                tomada.set()
                liberar.wait(timeout=10)
        finally:
            connections.close_all()

    fio = threading.Thread(target=segurar_a_trava)
    fio.start()
    try:
        assert tomada.wait(timeout=10)
        assert _confirmar(enviada) is None
    finally:
        liberar.set()
        fio.join(timeout=10)

    assert caixa == []
    assert _trilha(enviada) == []


def test_sem_endereco_nao_tenta_nem_registra(caixa, selecao):
    """Uma falha que nenhuma nova tentativa resolve não vira botão na tela (FR-8362)."""
    enviada = _enviada(selecao)
    enviada.email = ""

    assert _confirmar(enviada) is None
    assert caixa == []
    assert _trilha(enviada) == []


def test_nenhuma_falha_do_caminho_escapa_de_confirmar(caixa, selecao, registro_tecnico):
    """FR-8352: a inscrição já está gravada; o que falhar aqui vai ao registro técnico."""
    enviada = _enviada(selecao)

    def faltou_um_dado():
        raise KeyError("Edital")

    assert (
        confirmacao.confirmar(
            inscricao=enviada,
            ator=ator_do_candidato(MARIA, enviada.edital),
            montar_dados=faltou_um_dado,
        )
        is None
    )
    assert caixa == []
    assert any("não foi tentada até o fim" in linha for linha in registro_tecnico)
