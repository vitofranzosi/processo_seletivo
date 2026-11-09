"""A mensagem de convocação de verdade, pelo envio: HTML e texto, inicial e da correção (121).

`FR-3882` a `FR-3890`, `SC-1155`, `SC-1159`, `SC-1160`, `SC-1161`. O envio passa pelo `locmem`, e
a falha é provocada por um *backend* que devolve `0` — o mesmo caminho de `entregues == 0` em
`comunicar.py`, que é a falha mais silenciosa que existe.

**Os cenários da D-008 por extenso** (plano, seção *Os cenários da D-008*): a mensagem da correção
cita a última mensagem **enviada com sucesso** na cadeia, e não a da imediatamente anterior. A
reconstrução, no fim, chama a mesma função de escolha só com os registros relidos do banco
(FR-3889).
"""

import html as html_lib
import re
from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings as django_settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import comunicar as modulo_do_envio
from processo_seletivo.convocacao.application.comunicar import comunicar as emitir
from processo_seletivo.convocacao.application.comunicar import escolha_de
from processo_seletivo.convocacao.domain.mensagem import CORRECAO, INICIAL
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from tests.fixtures import jornada_do_convocado as jornada
from tests.integration.convocacao.test_correcao_da_convocacao import chamar, corrigir

pytestmark = pytest.mark.django_db(transaction=True)

BASE = "http://testserver/selecoes/inscricoes/"
PROIBIDOS_NA_CORRECAO = ("recebeu", "recebida", "novo prazo", "prorrogação", "motivo")
HH_MM = re.compile(r"\b\d{2}:\d{2}\b")


class CorreioQueGuardaEFalha:
    """Aceita a chamada, guarda o que recebeu, e devolve zero: a mensagem não saiu."""

    guardadas = []

    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, mensagens):
        CorreioQueGuardaEFalha.guardadas.extend(mensagens)
        return 0


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    CorreioQueGuardaEFalha.guardadas = []
    return mail.outbox


@pytest.fixture
def fx(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def falhar(settings):
    settings.EMAIL_BACKEND = (
        "tests.integration.convocacao.test_mensagem_da_convocacao.CorreioQueGuardaEFalha"
    )


def entregar(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


def comunicar(edital, gestor, convocacao, chave):
    return emitir(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        idempotency_key=chave,
        correlation_id="teste-121",
        endereco_do_portal=BASE,
    )


def partes(mensagem):
    """O texto puro e o HTML da mesma mensagem."""
    html = next(conteudo for conteudo, tipo in mensagem.alternatives if tipo == "text/html")
    return mensagem.body, html


def normalizar(texto):
    return " ".join(html_lib.unescape(texto).split())


def frases_do_html(html):
    """Cada linha de texto visível do corpo do HTML: um parágrafo, um título, um item de lista."""
    corpo = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    for _, bloco in re.findall(r"<(p|h1|li)\b[^>]*>(.*?)</\1>", corpo, re.S):
        for linha in re.sub(r"<br\s*/?>", "\n", bloco).split("\n"):
            frase = normalizar(re.sub(r"<[^>]+>", " ", linha))
            if frase:
                yield frase


def prazo_de(instante):
    return apresentar(instante, timezone.now(), ZoneInfo(django_settings.TIME_ZONE))


# --- As partes e o que não pode ir (SC-1159, FR-3886) ---------------------------------------------


class TestAsDuasPartes:
    def test_o_texto_puro_contem_cada_frase_do_html(self, caixa, fx):
        """`FR-3882`, `SC-1159`: quem lê só o texto lê tudo o que o HTML diz."""
        jornada.montar("C1", fx)

        texto, html = partes(caixa[-1])
        frases = list(frases_do_html(html))

        assert len(frases) > 10
        faltam = [frase for frase in frases if frase not in normalizar(texto)]
        assert faltam == []

    def test_nada_externo_nem_dado_da_pessoa(self, caixa, fx):
        """`FR-3886`, `SC-1159`: sem imagem, sem endereço além do link e do canal, sem nome, CPF
        nem nome de documento."""
        cenario = jornada.montar("C1", fx)
        texto, html = partes(caixa[-1])
        pessoa = cenario.pessoa
        # A fixture comunica sem a base do portal: o link é o caminho (FR-3883, Assumptions).
        link = reverse("portal:convocacao", args=[pessoa.id])

        assert "src=" not in html
        assert "<style" not in html and "<link" not in html
        assert not re.findall(r"https?://", html + texto), "nenhum endereço além do link e do canal"
        assert re.findall(r'href="([^"]+)"', html) == [link]
        documentos = ("Certidão", "Histórico", "Certificado", "Comprovante de residência")
        for proibido in (pessoa.nome, pessoa.cpf, *documentos):
            if proibido:
                assert proibido not in texto and proibido not in html, proibido
        assert str(pessoa.id) not in texto.replace(link, "")

    def test_o_link_e_o_da_convocacao_da_inscricao(self, caixa, fx):
        """`FR-3883`, FR-1104 da `059`, revista: o endereço é o da convocação, por extenso."""
        cenario = jornada.montar("A", fx)

        texto, html = partes(caixa[-1])
        caminho = reverse("portal:convocacao", args=[cenario.pessoa.id])

        assert f"\n{caminho}\n" in texto, "sem base, o caminho relativo"
        assert f'href="{caminho}"' in html
        assert "Acessar minha convocação" in texto and "Acessar minha convocação" in html

    def test_com_a_base_o_link_e_absoluto(self, caixa, cenario, gestor):
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="absoluto")

        comunicar(edital, gestor, a, "absoluto-com")
        texto, _ = partes(caixa[-1])

        assert "http://testserver" + reverse("portal:convocacao", args=[a.inscricao_id]) in texto

    def test_a_identificacao_institucional_vem_da_unidade(self, caixa, fx):
        """`FR-3887`, D-012: o nome por extenso e a unidade, que o modelo não escreve."""
        jornada.montar("A", fx)

        texto, html = partes(caixa[-1])

        assert "Instituto Federal do Espírito Santo" in texto
        assert "Cefor · Seleções" in texto
        assert caixa[-1].subject.startswith("Ifes · Convocação no Edital ")


# --- O assunto e a frase das quatro variantes (FR-3884, SC-1155) ----------------------------------


class TestAsVariantes:
    @pytest.mark.parametrize(
        ("letra", "assunto", "frase"),
        [
            (
                "C1",
                ": envie seus documentos até ",
                "Esta convocação pede documentos e o Requerimento de Matrícula.",
            ),
            (
                "A",
                ": envie seus documentos até ",
                "Esta convocação pede documentos, que você envia pela sua área do candidato.",
            ),
            (
                "B",
                ": preencha o Requerimento até ",
                "Esta convocação pede o Requerimento de Matrícula, que você preenche pela sua "
                "área do candidato.",
            ),
            (
                "sem-documento-nem-requerimento",
                ": prazo até ",
                "Siga as instruções do Edital dentro do prazo. As instruções estão na sua área do "
                "candidato.",
            ),
        ],
    )
    def test_o_assunto_e_a_frase(self, caixa, fx, letra, assunto, frase):
        cenario = jornada.montar(letra, fx)
        mensagem = caixa[-1]
        texto, html = partes(mensagem)
        prazo = prazo_de(cenario.convocacao.vencimento)

        assert mensagem.subject.endswith(f"{assunto}{prazo.data_curta}")
        assert "\n" not in mensagem.subject
        assert frase in normalizar(texto) and frase in normalizar(html)
        assert f"até {prazo.por_extenso}, contado do envio desta mensagem" in texto
        assert not HH_MM.search(texto) and not HH_MM.search(html)
        assert not HH_MM.search(mensagem.subject)

    def test_a_ressalva_sem_o_requerimento_nao_fala_de_matricula(self, caixa, fx):
        """D-003: num Edital sem Requerimento, "ainda não é a matrícula" seria falso."""
        jornada.montar("A", fx)
        texto, _ = partes(caixa[-1])

        assert "Esta convocação ainda não é o resultado:" in texto
        assert "matrícula" not in texto.lower()

    def test_a_ressalva_com_o_requerimento(self, caixa, fx):
        jornada.montar("C1", fx)
        texto, _ = partes(caixa[-1])

        assert "Esta convocação ainda não é a matrícula:" in texto

    def test_sem_vencimento_o_assunto_nao_leva_data(self, caixa, fx):
        """Caso-limite: sem vencimento registrado, o prazo é o que o Edital publica."""
        c = jornada.certame(
            fx, prefixo="j121-sv", documentos=jornada.cenarios.documentos_do_aluno()
        )
        jornada.convocar(c, fx.gestor, letra="sv", vencimento_em=None)
        mensagem = caixa[-1]
        texto, _ = partes(mensagem)

        assert mensagem.subject == f"Ifes · Convocação no Edital {c[0].number}/{c[0].year}"
        assert "O prazo para atender é o que o Edital publica." in texto
        assert "contado do envio" not in texto

    def test_todos_os_obrigatorios_aproveitados_ainda_pedem_documentos(self, caixa, fx):
        """Caso-limite: a mensagem diz o que a chamada **pede**, e não o estado (FR-3884)."""
        jornada.montar("D", fx)
        texto, _ = partes(caixa[-1])

        assert "Esta convocação pede documentos" in texto


class TestARepeticao:
    def test_a_mesma_chave_nao_envia(self, caixa, cenario, gestor):
        """`FR-3888`, `SC-1161`: a repetição concluída devolve o desfecho, e nada sai."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="repete")
        comunicar(edital, gestor, a, "repete-com")
        antes = (len(caixa), ComunicacaoEmitida.objects.count())

        comunicar(edital, gestor, a, "repete-com")

        assert (len(caixa), ComunicacaoEmitida.objects.count()) == antes


# --- A cadeia de correções (D-008, SC-1160) -------------------------------------------------------


def _assunto_e_titulo_da_correcao(mensagem, edital):
    texto, html = partes(mensagem)
    numero = f"Edital {edital.number}/{edital.year}"
    assert mensagem.subject.startswith(f"Ifes · Convocação corrigida no {numero}: prazo válido até")
    assert f"Sua convocação no {numero} foi corrigida" in texto
    assert f"Sua convocação no {numero} foi corrigida" in html
    assert "Prazo válido para atender" in texto
    return texto, html


def _quadro(texto):
    return re.search(r"Esta mensagem substitui a que enviamos em [^\n]+", texto).group(0)


def _cita(texto, comunicacao):
    enviada = prazo_de(comunicacao.enviado_em)
    prazo = prazo_de(comunicacao.convocacao.vencimento)
    quadro = _quadro(texto)
    assert f"enviamos em {enviada.data}, às {enviada.hora}." in quadro
    assert f"Aquela informava prazo até {prazo.dia_da_semana}, {prazo.data}." in quadro
    return quadro


def _sem_o_que_nao_se_diz(texto, html):
    corpo = (texto + html).lower()
    for proibido in PROIBIDOS_NA_CORRECAO:
        assert proibido not in corpo, proibido


def _e_inicial(mensagem):
    texto, html = partes(mensagem)
    assert "corrigida" not in mensagem.subject
    assert "Esta mensagem substitui" not in texto
    assert "Prazo válido" not in texto and "Prazo válido" not in html
    return texto


def _comunicacao(convocacao, resultado="ENVIADA"):
    return (
        ComunicacaoEmitida.objects.select_related("convocacao")
        .filter(convocacao=convocacao, resultado=resultado)
        .order_by("enviado_em")
        .last()
    )


class TestACadeia:
    def test_a_enviada_b_falhada_c_cita_a(self, caixa, cenario, gestor, settings):
        """D-008, cenário 1: a mensagem de B não saiu, e C cita A; os dados do ato descrevem B."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="d1")
        comunicar(edital, gestor, a, "d1-com")
        falhar(settings)
        corrigir(edital, gestor, a, chave="d1-b")
        b = Convocacao.objects.get(convocacao_anterior=a)
        assert _comunicacao(b, "FALHA") is not None
        entregar(settings)

        corrigir(edital, gestor, b, chave="d1-c", vencimento=timezone.now() + timedelta(days=9))

        texto, html = _assunto_e_titulo_da_correcao(caixa[-1], edital)
        _cita(texto, _comunicacao(a))
        assert "O prazo que vale é o desta mensagem." in texto
        assert "enviamos" in _quadro(texto)
        _sem_o_que_nao_se_diz(texto, html)

    def test_a_e_b_falhadas_c_e_a_inicial(self, caixa, cenario, gestor, settings):
        """D-008, cenário 2: sem envio com sucesso na cadeia, nada há a substituir."""
        edital, _, _ = cenario
        falhar(settings)
        a = chamar(edital, gestor, chave="d2")
        comunicar(edital, gestor, a, "d2-com")
        corrigir(edital, gestor, a, chave="d2-b")
        b = Convocacao.objects.get(convocacao_anterior=a)
        entregar(settings)

        corrigir(edital, gestor, b, chave="d2-c", vencimento=timezone.now() + timedelta(days=9))

        assert len(caixa) == 1
        _e_inicial(caixa[-1])

    def test_a_e_b_enviadas_c_cita_b(self, caixa, cenario, gestor):
        """D-008, cenário 3: a correção da correção, sem falha, cita a imediatamente anterior."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="d3")
        comunicar(edital, gestor, a, "d3-com")
        corrigir(edital, gestor, a, chave="d3-b")
        b = Convocacao.objects.get(convocacao_anterior=a)

        corrigir(edital, gestor, b, chave="d3-c", vencimento=timezone.now() + timedelta(days=9))

        texto, html = _assunto_e_titulo_da_correcao(caixa[-1], edital)
        _cita(texto, _comunicacao(b))
        _sem_o_que_nao_se_diz(texto, html)

    def test_c_reenviada_depois_de_falhar_as_duas_tentativas_citam_a(
        self, caixa, cenario, gestor, settings
    ):
        """D-008, cenário 4: a escolha não depende da tentativa, só dos registros."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="d4")
        comunicar(edital, gestor, a, "d4-com")
        falhar(settings)
        corrigir(edital, gestor, a, chave="d4-c")
        c = Convocacao.objects.get(convocacao_anterior=a)
        entregar(settings)
        comunicar(edital, gestor, c, "d4-c-de-novo")

        tentativa = CorreioQueGuardaEFalha.guardadas[-1]
        primeira = _cita(_assunto_e_titulo_da_correcao(tentativa, edital)[0], _comunicacao(a))
        segunda = _cita(_assunto_e_titulo_da_correcao(caixa[-1], edital)[0], _comunicacao(a))
        assert primeira == segunda

    def test_a_por_publicacao_c_e_a_inicial(self, caixa, cenario, gestor):
        """D-008, cenário 5: a publicação não é mensagem enviada à pessoa.

        A forma é do Perfil, e a cadeia não muda de forma pela tela: a comunicação de A por
        publicação é gravada direto, como a gestão a gravaria num Edital que publica.
        """
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="d5")
        ComunicacaoEmitida.objects.create(
            convocacao=a,
            forma="PUBLICATION",
            referencia_da_publicacao="https://exemplo.test/convocacao, em 05/11/2026",
            enviado_em=timezone.now(),
            resultado="ENVIADA",
        )

        corrigir(edital, gestor, a, chave="d5-c")

        _e_inicial(caixa[-1])


# --- A reconstrução (FR-3889) ---------------------------------------------------------------------


class TestAReconstrucao:
    def test_a_escolha_se_refaz_so_com_o_banco(self, caixa, cenario, gestor, settings):
        """Depois do envio, a mesma função, chamada só com os registros relidos, devolve o mesmo
        modelo, a mesma variante e a mesma citada."""
        edital, _, _ = cenario
        a = chamar(edital, gestor, chave="r1")
        comunicar(edital, gestor, a, "r1-com")
        falhar(settings)
        corrigir(edital, gestor, a, chave="r1-b")
        b = Convocacao.objects.get(convocacao_anterior=a)
        entregar(settings)
        corrigir(edital, gestor, b, chave="r1-c", vencimento=timezone.now() + timedelta(days=9))
        c = Convocacao.objects.get(convocacao_anterior=b)

        for convocacao, modelo in ((a, INICIAL), (c, CORRECAO)):
            enviada = _comunicacao(convocacao)
            relida = Convocacao.objects.get(id=convocacao.id)
            escolha = escolha_de(relida, instante=enviada.enviado_em)
            assert escolha.modelo == modelo
            assert enviada.modelo_da_mensagem.startswith(f"{modelo}:sha256:")
        escolha_de_c = escolha_de(Convocacao.objects.get(id=c.id), instante=timezone.now())
        assert escolha_de_c.citada.enviado_em == _comunicacao(a).enviado_em
        assert escolha_de_c.citada.vencimento == a.vencimento

    def test_sem_anterior_nao_le_a_cadeia(self, caixa, cenario, gestor, django_assert_num_queries):
        """A primeira chamada é a inicial sem consultar a cadeia: só a lista da chamada é lida."""
        edital, _, _ = cenario
        a = Convocacao.objects.select_related("versao").get(id=chamar(edital, gestor, chave="q").id)

        with django_assert_num_queries(1):
            escolha = escolha_de(a, instante=timezone.now())

        assert escolha.modelo == INICIAL

    def test_a_variante_se_refaz(self, caixa, fx):
        cenario = jornada.montar("C1", fx)
        enviada = _comunicacao(cenario.convocacao)
        relida = Convocacao.objects.get(id=cenario.convocacao.id)

        escolha = escolha_de(relida, instante=enviada.enviado_em)

        assert (escolha.modelo, escolha.variante) == (INICIAL, "documento_e_requerimento")


def test_o_envio_da_convocacao_continua_em_comunicar():
    """`SC-1161`: o envio continua em `comunicar.py`, e nenhum módulo novo envia.

    A `134` acrescentou a quinta situação no despacho da `066`, e não aqui: a contagem é dela.
    """
    from tests.test_situacoes_de_mensagem import (
        MODULOS_DAS_SITUACOES,
        SITUACOES,
        modulos_que_enviam,
    )

    assert len(SITUACOES) == 5
    assert modulos_que_enviam() <= MODULOS_DAS_SITUACOES
    assert modulo_do_envio.__name__.endswith("convocacao.application.comunicar")
