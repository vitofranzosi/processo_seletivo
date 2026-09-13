"""O conteúdo da mensagem de convocação: o mínimo necessário, e nada além (019, `FR-290`).

**A mensagem viaja.** Ela é encaminhada, fica em caixa compartilhada, aparece em notificação de
celular na mesa de outra pessoa. O que não ajuda quem lê não tem por que estar nela — e CPF,
telefone, pontuação e posição na ordem não ajudam ninguém a atender a uma convocação.

**E ela não afirma direito à vaga** (`FR-292c`). A convocação chama para cumprir uma etapa; o que
decide a vaga é o que a pessoa fizer dentro do prazo. Uma mensagem que diga o contrário cria
expectativa que o Edital não sustenta, e o desmentido vem depois — quando já não tem conserto.

**Nenhum link que autentica** (P-001 da `010`): a mensagem manda a pessoa à área dela, e a entrada
continua sendo por código digitado. Um link assim viaja no histórico do navegador, no
encaminhamento da mensagem e no cabeçalho de origem.
"""

from datetime import UTC, datetime

import pytest
from django.core import mail

from processo_seletivo.convocacao.application.comunicar import enviar_mensagem_de_convocacao

VENCIMENTO = datetime(2026, 9, 20, 17, 0, tzinfo=UTC)

# O que **não** pode estar na mensagem, e por quê: dados da pessoa que a mensagem não precisa para
# cumprir a sua função, e a frase que promete o que a convocação não decide.
PROIBIDOS = (
    "123.456.789-00",
    "27999990000",
    "90.0000",
    "direito à vaga",
    "recebido em",
    "lido em",
    "entregue em",
)


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def enviar(caixa, **overrides):
    dados = {
        "edital": "Edital 77/2026",
        "vencimento": VENCIMENTO,
        "endereco": "https://selecoes.exemplo.test/portal/minhas-inscricoes",
        "atendimento": "selecao@exemplo.test",
    }
    dados.update(overrides)
    detalhe = enviar_mensagem_de_convocacao(para="candidata@exemplo.test", dados=dados)
    assert detalhe == "", "o caminho feliz não devolve detalhe técnico"
    return caixa[-1]


class TestOQueAMensagemDiz:
    def test_diz_o_que_fazer_o_prazo_e_o_canal_de_atendimento(self, caixa):
        """As três coisas da `FR-290`, e é por elas que a mensagem existe."""
        mensagem = enviar(caixa)

        assert "20/09/2026" in mensagem.body, "até quando"
        assert "acesse a sua área" in mensagem.body, "o que fazer"
        assert "selecao@exemplo.test" in mensagem.body, "com quem falar"

    def test_o_assunto_nomeia_o_edital(self, caixa):
        """Quem recebe precisa saber de qual certame se trata antes de abrir."""
        mensagem = enviar(caixa)

        assert mensagem.subject == "Convocação — Edital 77/2026"

    def test_o_prazo_diz_de_que_referencia_corre(self, caixa):
        """`UX-038`: um prazo sem referência é uma data solta.

        O prazo corre do **envio** (`D-009`), e não do ato de convocar nem do recebimento — e é o
        envio que a mensagem nomeia, porque é o único instante que o sistema conhece.
        """
        mensagem = enviar(caixa)

        assert "contado do envio desta mensagem" in mensagem.body

    def test_edital_sem_prazo_publicado_nao_ganha_um(self, caixa):
        """Vencimento nulo é "este Edital não publicou prazo", e a mensagem não o inventa."""
        mensagem = enviar(caixa, vencimento=None)

        assert "O prazo para atender é o que o Edital publica." in mensagem.body
        assert "contado do envio" not in mensagem.body


class TestOQueAMensagemNaoDiz:
    @pytest.mark.parametrize("proibido", PROIBIDOS)
    def test_nao_carrega_dado_que_nao_ajuda_quem_le(self, caixa, proibido):
        mensagem = enviar(caixa)

        assert proibido not in mensagem.body
        assert proibido not in mensagem.subject

    def test_nao_afirma_direito_a_vaga(self, caixa):
        """`FR-292c`: convocar é chamar para cumprir uma etapa, e não entregar a vaga."""
        mensagem = enviar(caixa)

        for frase in ("direito à vaga", "vaga garantida", "você foi aprovada"):
            assert frase.lower() not in mensagem.body.lower()

    def test_nao_carrega_link_que_autentica(self, caixa):
        """P-001 da `010`: o endereço é a porta da área, e a entrada continua sendo por código."""
        mensagem = enviar(caixa)

        for marca in ("token=", "code=", "acesso=", "?t="):
            assert marca not in mensagem.body


class TestAFalhaNaoInterrompe:
    def test_a_falha_devolve_detalhe_tecnico_sem_o_endereco(self, settings):
        """**A falha não apaga o ato** (`FR-269a`), e o detalhe técnico não leva dado pessoal.

        Ele vai para o registro do servidor e para a tela de quem conduz o certame, e o endereço de
        alguém não tem por que estar em nenhum dos dois.
        """
        settings.EMAIL_BACKEND = "tests.unit.convocacao.test_mensagem.CorreioQueFalha"

        detalhe = enviar_mensagem_de_convocacao(
            para="candidata@exemplo.test",
            dados={
                "edital": "Edital 77/2026",
                "vencimento": VENCIMENTO,
                "endereco": "https://selecoes.exemplo.test/portal",
                "atendimento": "selecao@exemplo.test",
            },
        )

        assert detalhe
        assert "candidata@exemplo.test" not in detalhe


class CorreioQueFalha:
    """Um backend de correio que sempre falha, para exercitar o caminho da falha de emissão."""

    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, mensagens):
        raise OSError("conexão recusada pelo servidor de SMTP")


def test_o_prazo_e_dito_em_data_e_hora_locais(caixa):
    """`UX-038`: a pessoa lê o prazo no relógio dela, e não em ISO com fuso.

    Um vencimento escrito `2026-09-20T17:00:00+00:00` é tecnicamente exato e ilegível — e a
    diferença entre 17h e 14h decide se alguém perde a vaga.
    """
    mensagem = enviar(caixa)

    assert "20/09/2026 às 17:00" in mensagem.body
    assert "2026-09-20T17:00" not in mensagem.body
