"""A sala de um polo atrás de um NAT esbarra no teto da origem — e precisa ler a verdade (FR-031c).

O achado A-12 da auditoria de 31/10, reproduzido antes da correção: quarenta candidatos distintos,
a mesma origem de rede, a mesma hora. Trinta recebiam código; os outros dez caíam na tela do código
lendo "Enviado para", "o pedido anterior foi há pouco" — nenhum deles tinha pedido antes — e, junto
do botão, "pode pedir outro código agora", com o bloqueio valendo por uma hora inteira. Cada um
clicava de novo, recebia a mesma tela, e concluía que o e-mail não chegava. Nenhuma linha de
registro técnico: uma sala recusada era indistinguível de correio caído.

O teto continua, e continua trinta. O que este arquivo guarda é a resposta a quem passa dele: que é
a rede, e não o e-mail; por quanto tempo de fato; o que resolve; e o rastro para a equipe.
"""

import json
import logging
import re
from datetime import timedelta

import pytest
from django.core import mail
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao, mensagem
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.shared.observability import JsonFormatter

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR
# O endereço público do NAT de um polo — da faixa reservada a documentação (RFC 5737).
POLO = "203.0.113.50"
CONHECIDO = "conhecida@exemplo.test"
DESCONHECIDO = "ninguem@exemplo.test"


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    settings.PORTAL_ATENDIMENTO = "selecao@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def registro_tecnico():
    """O que os loggers da aplicação emitiram, já como a linha JSON que a produção grava.

    `caplog` não serve: `propagate` é falso no logger da aplicação.
    """

    class Coletor(logging.Handler):
        def __init__(self):
            super().__init__(level=logging.DEBUG)
            self.setFormatter(JsonFormatter())
            self.linhas = []

        def emit(self, registro):
            self.linhas.append(self.format(registro))

        def eventos(self, code):
            return [
                evento
                for evento in (json.loads(linha) for linha in self.linhas)
                if evento.get("code") == code
            ]

    coletor = Coletor()
    logger = logging.getLogger("processo_seletivo")
    anterior = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(coletor)
    yield coletor
    logger.removeHandler(coletor)
    logger.setLevel(anterior)


def candidato_no_polo(endereco, origem=POLO, **cabecalhos):
    """Um navegador por pessoa — cada uma com a sua sessão, todas pela mesma rede."""
    cliente = Client(REMOTE_ADDR=origem)
    cliente.post(reverse("portal:acesso"), {"email": endereco}, **cabecalhos)
    return cliente


def tela(cliente, **cabecalhos):
    return cliente.get(reverse("portal:acesso-codigo"), **cabecalhos).content.decode()


def esgotar_a_origem(origem=POLO):
    for indice in range(servico.LIMITE_POR_ORIGEM):
        _, codigo = servico.solicitar(
            email_canonico=f"sala{indice}@exemplo.test", finalidade=ENTRAR, origem=origem
        )
        assert codigo


def esgotar_o_endereco(endereco):
    """Cinco pedidos espaçados além da espera, cada um de uma rede — isola o teto do endereço."""
    for indice in range(servico.LIMITE_POR_ENDERECO):
        _, codigo = servico.solicitar(
            email_canonico=endereco, finalidade=ENTRAR, origem=f"198.51.100.{indice}"
        )
        assert codigo
        DesafioDeAcesso.objects.filter(email_canonico=endereco).update(
            criado_em=timezone.now() - timedelta(seconds=120)
        )


def recuar(minutos, **filtro):
    DesafioDeAcesso.objects.filter(**filtro).update(
        criado_em=timezone.now() - timedelta(minutes=minutos)
    )


# --- O cenário do achado ----------------------------------------------------------------------


def test_quarenta_candidatos_atras_do_mesmo_nat(caixa):
    """Trinta recebem, dez não — e os dez sabem por quê, sem a contagem fictícia de sessenta
    segundos."""
    telas = []
    for indice in range(40):
        telas.append(tela(candidato_no_polo(f"candidato{indice}@exemplo.test")))

    assert len(caixa) == servico.LIMITE_POR_ORIGEM
    assert DesafioDeAcesso.objects.count() == servico.LIMITE_POR_ORIGEM
    recusadas = telas[servico.LIMITE_POR_ORIGEM :]
    for corpo in recusadas:
        assert "A rede de onde você está acessando atingiu o limite" in corpo
        assert "não tem relação com o seu e-mail" in corpo
        assert "Use outra conexão" in corpo
        assert "cerca de 60 minutos" in corpo
        assert "selecao@exemplo.test" in corpo, "o atendimento aparece para quem tem prazo"
    for corpo in telas[: servico.LIMITE_POR_ORIGEM]:
        assert "atingiu o limite" not in corpo, "quem recebeu não lê a recusa"
        assert "Enviado para" in corpo
    # Quem completou os trinta recebeu o código; o teto que passou a valer é do pedido seguinte.
    assert (
        "Outro pedido por esta conexão só será possível daqui a cerca de 60 minutos"
        in (telas[servico.LIMITE_POR_ORIGEM - 1])
    )


def test_a_tela_recusada_nao_mente_sobre_o_que_aconteceu(caixa):
    esgotar_a_origem()
    corpo = tela(candidato_no_polo("trigesimo-primeiro@exemplo.test"))

    assert "Pode pedir outro código agora" not in corpo
    assert "o pedido anterior foi há pouco" not in corpo, "ela nunca tinha pedido"
    assert "Enviado para" not in corpo, "nada foi enviado"
    assert "E-mail informado" in corpo
    # Nada de contagem regressiva para um bloqueio de uma hora: ela é só da espera de reenvio.
    assert 'data-espera="0"' in corpo
    assert not re.search(r"\d+ segundos", corpo)


def test_reenviar_no_teto_repete_a_explicacao_e_nao_envia(caixa):
    esgotar_a_origem()
    cliente = candidato_no_polo("insiste@exemplo.test")
    cliente.post(reverse("portal:acesso"), {"email": "insiste@exemplo.test"})

    assert len(caixa) == 0
    assert "A rede de onde você está acessando atingiu o limite" in tela(cliente)


def test_outra_conexao_resolve(caixa):
    """É a saída que a frase indica, e ela precisa funcionar."""
    esgotar_a_origem()
    tela(candidato_no_polo("candidata@exemplo.test"))

    corpo = tela(candidato_no_polo("candidata@exemplo.test", origem="192.0.2.77"))

    assert len(caixa) == 1
    assert "atingiu o limite" not in corpo


def test_o_codigo_recebido_antes_do_teto_continua_valendo(caixa):
    """A frase diz que o código dos últimos minutos vale — e vale."""
    cliente = candidato_no_polo("adiantada@exemplo.test")
    codigo = re.search(r"\b(\d{6})\b", caixa[0].body).group(1)
    for indice in range(servico.LIMITE_POR_ORIGEM - 1):
        servico.solicitar(
            email_canonico=f"sala{indice}@exemplo.test", finalidade=ENTRAR, origem=POLO
        )
    cliente.post(reverse("portal:acesso"), {"email": "adiantada@exemplo.test"})
    assert "atingiu o limite" in tela(cliente)

    resposta = cliente.post(reverse("portal:acesso-codigo"), {"codigo": codigo})

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricoes")


# --- O tempo anunciado é o efetivo ------------------------------------------------------------


def test_o_tempo_vem_do_pedido_que_sai_da_janela():
    """A janela desliza: a sala cujos pedidos se espalharam pela hora espera minutos, não uma
    hora."""
    esgotar_a_origem()
    recuar(50, origem_hash=servico._resumir_origem(POLO))

    recibo, codigo = servico.solicitar(
        email_canonico="depois@exemplo.test", finalidade=ENTRAR, origem=POLO
    )

    assert not codigo
    assert recibo.bloqueio.motivo == servico.TETO_DA_ORIGEM
    assert 9 * 60 <= recibo.proxima_tentativa_em <= 10 * 60


def test_com_o_teto_ultrapassado_o_tempo_e_o_do_pedido_que_o_desfaz():
    """Pedidos simultâneos podem passar do teto em alguns (`test_limite_concorrente`); com dois a
    mais, são três os que precisam sair da janela, e o tempo é o do terceiro mais antigo."""
    agora = timezone.now()
    for indice in range(servico.LIMITE_POR_ORIGEM + 2):
        DesafioDeAcesso.objects.create(
            email_canonico=f"sala{indice}@exemplo.test",
            finalidade=ENTRAR,
            codigo_hash="x",
            origem_hash=servico._resumir_origem(POLO),
            expira_em=agora,
            criado_em=agora - timedelta(minutes=50 - indice),
        )

    bloqueio = servico.bloqueio_atual(
        email_canonico="depois@exemplo.test", finalidade=ENTRAR, origem=POLO
    )

    assert bloqueio.motivo == servico.TETO_DA_ORIGEM
    assert 11 * 60 < bloqueio.segundos <= 12 * 60


def test_esvaziada_a_janela_a_origem_volta_a_receber(caixa):
    esgotar_a_origem()
    assert (
        servico.solicitar(email_canonico="cedo@exemplo.test", finalidade=ENTRAR, origem=POLO)[1]
        == ""
    )

    recuar(61, origem_hash=servico._resumir_origem(POLO))

    recibo, codigo = servico.solicitar(
        email_canonico="cedo@exemplo.test", finalidade=ENTRAR, origem=POLO
    )
    assert codigo
    assert recibo.bloqueio is None


def test_basta_sair_um_pedido_para_abrir_uma_vaga():
    esgotar_a_origem()
    mais_antigo = DesafioDeAcesso.objects.order_by("criado_em").first()
    DesafioDeAcesso.objects.filter(pk=mais_antigo.pk).update(
        criado_em=timezone.now() - timedelta(minutes=61)
    )

    _, primeiro = servico.solicitar(
        email_canonico="vaga@exemplo.test", finalidade=ENTRAR, origem=POLO
    )
    _, segundo = servico.solicitar(
        email_canonico="sem-vaga@exemplo.test", finalidade=ENTRAR, origem=POLO
    )

    assert primeiro and not segundo


def test_a_tela_recalcula_o_tempo_a_cada_leitura(caixa):
    esgotar_a_origem()
    cliente = candidato_no_polo("espera@exemplo.test")
    assert "cerca de 60 minutos" in tela(cliente)

    recuar(45, origem_hash=servico._resumir_origem(POLO))

    assert "cerca de 15 minutos" in tela(cliente)


def test_no_ultimo_minuto_o_texto_fica_no_singular(caixa):
    esgotar_a_origem()
    cliente = candidato_no_polo("quase@exemplo.test")
    DesafioDeAcesso.objects.filter(origem_hash=servico._resumir_origem(POLO)).update(
        criado_em=timezone.now() - timedelta(minutes=59, seconds=30)
    )

    assert "cerca de 1 minuto." in tela(cliente)


# --- A proteção por endereço continua -----------------------------------------------------------


def test_o_teto_do_endereco_vale_mesmo_vindo_de_redes_distintas():
    esgotar_o_endereco("alvo@exemplo.test")

    recibo, codigo = servico.solicitar(
        email_canonico="alvo@exemplo.test", finalidade=ENTRAR, origem="192.0.2.200"
    )

    assert not codigo
    assert recibo.bloqueio.motivo == servico.TETO_DO_ENDERECO
    assert recibo.proxima_tentativa_em > 60


def test_o_teto_do_endereco_diz_que_e_o_endereco_e_nao_a_rede(caixa):
    esgotar_o_endereco("alvo@exemplo.test")

    corpo = tela(candidato_no_polo("alvo@exemplo.test", origem="192.0.2.200"))

    assert "Não é possível enviar outro código para este e-mail agora" in corpo
    assert "Use o código mais recente que chegou" in corpo
    assert "A rede de onde você está acessando" not in corpo
    assert "Pode pedir outro código agora" not in corpo
    assert len(caixa) == 0


def test_com_os_dois_tetos_vale_o_mais_longo():
    """Anunciar o teto da rede quando o do endereço dura mais mandaria trocar de conexão à toa."""
    esgotar_o_endereco("alvo@exemplo.test")
    esgotar_a_origem()
    recuar(40, origem_hash=servico._resumir_origem(POLO))

    recibo, _ = servico.solicitar(
        email_canonico="alvo@exemplo.test", finalidade=ENTRAR, origem=POLO
    )

    assert recibo.bloqueio.motivo == servico.TETO_DO_ENDERECO


def test_a_espera_de_reenvio_continua_em_segundos(caixa):
    cliente = candidato_no_polo("apressada@exemplo.test")
    cliente.post(reverse("portal:acesso"), {"email": "apressada@exemplo.test"})
    corpo = tela(cliente)

    assert len(caixa) == 1
    assert "Ainda não enviamos outro código" in corpo
    assert re.search(r"daqui a \d+ segundos", corpo)
    assert "atingiu o limite" not in corpo


# --- Equivalência: o teto não revela quem existe ------------------------------------------------


def _normalizada(corpo, endereco):
    corpo = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "TOKEN", corpo)
    return corpo.replace(endereco, "X")


def test_no_teto_da_origem_quem_existe_e_quem_nao_existe_leem_o_mesmo(caixa):
    associacao.criar_identidade_com(CONHECIDO, CONHECIDO)
    esgotar_a_origem()

    com = tela(candidato_no_polo(CONHECIDO))
    sem = tela(candidato_no_polo(DESCONHECIDO))

    assert "atingiu o limite" in com
    assert _normalizada(com, CONHECIDO) == _normalizada(sem, DESCONHECIDO)


def test_o_recibo_do_teto_e_o_mesmo_para_quem_existe():
    associacao.criar_identidade_com(CONHECIDO, CONHECIDO)
    esgotar_a_origem()

    com, _ = servico.solicitar(email_canonico=CONHECIDO, finalidade=ENTRAR, origem=POLO)
    sem, _ = servico.solicitar(email_canonico=DESCONHECIDO, finalidade=ENTRAR, origem=POLO)

    assert com == sem


def test_o_contrato_http_nao_muda_no_teto(caixa):
    esgotar_a_origem()
    resposta = Client(REMOTE_ADDR=POLO).post(reverse("portal:acesso"), {"email": DESCONHECIDO})

    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso-codigo")


# --- A origem confiável -------------------------------------------------------------------------


def test_atras_de_proxy_a_tela_le_a_mesma_origem_que_o_pedido(caixa, settings):
    """Com o proxy declarado, a origem é a do cabeçalho — no pedido **e** na tela que explica.

    Ler `REMOTE_ADDR` só na tela poria todos atrás do proxy na mesma "rede", e quem vem de um polo
    sem teto leria a recusa de outro.
    """
    settings.PORTAL_ATRAS_DE_PROXY = True
    proxy = "10.0.0.1"
    esgotar_a_origem(POLO)

    no_polo = candidato_no_polo("polo@exemplo.test", origem=proxy, HTTP_X_FORWARDED_FOR=POLO)
    em_casa = candidato_no_polo(
        "casa@exemplo.test", origem=proxy, HTTP_X_FORWARDED_FOR="192.0.2.33"
    )

    assert "atingiu o limite" in tela(no_polo, HTTP_X_FORWARDED_FOR=POLO)
    assert "atingiu o limite" not in tela(em_casa, HTTP_X_FORWARDED_FOR="192.0.2.33")
    assert len(caixa) == 1


def test_sem_proxy_declarado_o_cabecalho_nao_tira_ninguem_do_teto(caixa):
    """O teto não se contorna forjando `X-Forwarded-For` (FR-030a) — nem a tela o lê."""
    esgotar_a_origem()
    cliente = candidato_no_polo("forja@exemplo.test", HTTP_X_FORWARDED_FOR="192.0.2.99")

    assert len(caixa) == 0
    assert "atingiu o limite" in tela(cliente, HTTP_X_FORWARDED_FOR="192.0.2.99")


# --- O rastro para a equipe ---------------------------------------------------------------------


def test_o_teto_da_origem_deixa_evento_estruturado(caixa, registro_tecnico):
    esgotar_a_origem()
    candidato_no_polo("candidata@exemplo.test")

    (evento,) = registro_tecnico.eventos(servico.TETO_DA_ORIGEM)
    assert evento["level"] == "WARNING"
    assert evento["message"] == "codigo_de_acesso_nao_enviado"
    assert evento["operation"] == "identidade.solicitar_codigo.entrar"
    assert evento["origin"] == servico._resumir_origem(POLO)[:12]
    assert evento["retryAfter"] == 3600


def test_o_evento_nao_carrega_endereco_nem_rede_em_claro(caixa, registro_tecnico):
    esgotar_a_origem()
    candidato_no_polo("candidata@exemplo.test")

    texto = "\n".join(registro_tecnico.linhas)
    assert registro_tecnico.eventos(servico.TETO_DA_ORIGEM)
    assert "candidata" not in texto
    assert "exemplo.test" not in texto
    assert POLO not in texto


def test_os_quatro_motivos_tem_codigos_distintos(caixa, registro_tecnico, monkeypatch):
    """Teto da origem, teto do endereço, espera de reenvio e correio caído: quatro `code`."""
    esgotar_a_origem()
    candidato_no_polo("na-sala@exemplo.test")
    esgotar_o_endereco("alvo@exemplo.test")
    candidato_no_polo("alvo@exemplo.test", origem="192.0.2.200")
    cliente = candidato_no_polo("apressada@exemplo.test", origem="192.0.2.201")
    cliente.post(reverse("portal:acesso"), {"email": "apressada@exemplo.test"})

    def explodir(*_args, **_kwargs):
        raise OSError("servidor de e-mail indisponível")

    monkeypatch.setattr(mensagem, "send_mail", explodir)
    candidato_no_polo("sem-correio@exemplo.test", origem="192.0.2.202")

    assert [e["level"] for e in registro_tecnico.eventos(servico.TETO_DA_ORIGEM)] == ["WARNING"]
    assert [e["level"] for e in registro_tecnico.eventos(servico.TETO_DO_ENDERECO)] == ["WARNING"]
    assert [e["level"] for e in registro_tecnico.eventos(servico.EM_ESPERA)] == ["INFO"]
    (falha,) = registro_tecnico.eventos("envio_de_codigo_falhou")
    assert falha["level"] == "ERROR"
    assert "sem-correio" not in "\n".join(registro_tecnico.linhas)


def test_quem_recebe_codigo_nao_gera_evento_de_recusa(caixa, registro_tecnico):
    candidato_no_polo("tranquila@exemplo.test")

    assert len(caixa) == 1
    assert not [linha for linha in registro_tecnico.linhas if "nao_enviado" in linha]


def test_aberto_o_teto_depois_da_recusa_a_tela_nao_finge_que_enviou(caixa):
    """O teto se abriu entre o pedido recusado e a leitura: nada foi enviado, e já se pode pedir."""
    esgotar_a_origem()
    cliente = candidato_no_polo("entre-um-e-outro@exemplo.test")
    recuar(61, origem_hash=servico._resumir_origem(POLO))

    corpo = tela(cliente)

    assert "Não enviamos código no último pedido" in corpo
    assert "Enviado para" not in corpo
    assert "Pode pedir outro código agora" in corpo
