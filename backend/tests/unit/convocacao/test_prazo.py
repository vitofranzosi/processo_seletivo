"""O prazo da convocação: vencimento informado, envio, e o decurso que não decide nada (019).

**O sistema não calcula dias úteis** (`R-004`). Os Editais contam em dias úteis a partir do
recebimento, e sem calendário de expediente calcular "2 dias úteis" seria inventar feriado — errar
por um dia num prazo que decide vaga não tem conserto depois.

O que fica verificável sem calendário nenhum é o que este arquivo prende: que o prazo não corre sem
envio, que o vencimento não precede o envio, e que o decurso **não produz desfecho**.
"""

from datetime import UTC, datetime, timedelta

from processo_seletivo.convocacao.domain import nomes, prazo

ENVIO = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)
DEPOIS = ENVIO + timedelta(days=2)
ANTES = ENVIO - timedelta(days=2)


class TestOPrazoNaoCorreSemEnvio:
    """`FR-269a`: é o envio que inicia o relógio, e não o ato de convocar."""

    def test_sem_envio_o_prazo_nao_corre(self):
        assert prazo.prazo_corre(enviado_em=None) is False

    def test_com_envio_o_prazo_corre(self):
        assert prazo.prazo_corre(enviado_em=ENVIO) is True

    def test_o_estado_sem_envio_e_prazo_nao_iniciado(self):
        """**Sem este estado, falha de infraestrutura vira silêncio da pessoa** (`R-009`).

        E o desfecho que decorre de silêncio é perda de vaga — por um servidor de SMTP fora do ar.
        """
        assert (
            prazo.estado(tem_desfecho=False, enviado_em=None, vencimento=DEPOIS, agora=DEPOIS)
            == nomes.CONVOCADO_PRAZO_NAO_INICIADO
        )

    def test_vencimento_antigo_sem_envio_nao_esta_decorrido(self):
        """Um prazo que nunca começou não pode ter vencido, por mais antiga que seja a data."""
        assert prazo.decorrido(vencimento=ANTES, enviado_em=None, agora=DEPOIS) is False


class TestOVencimentoNaoPrecedeOEnvio:
    """`FR-269b`, `vencimento_anterior_ao_envio`: prazo que vence antes de a pessoa poder saber."""

    def test_vencimento_anterior_ao_envio_e_recusado(self):
        assert prazo.vencimento_precede_o_envio(vencimento=ANTES, enviado_em=ENVIO) is True

    def test_vencimento_igual_ao_envio_tambem_e_recusado(self):
        """**Igual não é prazo curto, é prazo nenhum.**

        Produziria desfecho de não atendimento contra alguém que nunca teve como atender.
        """
        assert prazo.vencimento_precede_o_envio(vencimento=ENVIO, enviado_em=ENVIO) is True

    def test_vencimento_posterior_passa(self):
        assert prazo.vencimento_precede_o_envio(vencimento=DEPOIS, enviado_em=ENVIO) is False

    def test_sem_vencimento_nao_ha_o_que_conferir(self):
        """O Edital que não publicou prazo não ganha um aqui."""
        assert prazo.vencimento_precede_o_envio(vencimento=None, enviado_em=ENVIO) is False


class TestODecursoNaoProduzDesfecho:
    """`FR-274`, e é a `D-003` confirmada pelo usuário: nenhum relógio tira vaga de ninguém.

    **A leitura mostra o vencimento passado; o desfecho continua faltando.** Quem desfecha é uma
    pessoa, com fundamento — e é isso que distingue *não atendimento à convocação* de um `cron`.
    """

    def test_vencimento_decorrido_e_estado_de_leitura_e_nao_desfecho(self):
        estado = prazo.estado(
            tem_desfecho=False,
            enviado_em=ENVIO,
            vencimento=ENVIO + timedelta(days=1),
            agora=DEPOIS,
        )

        assert estado == nomes.CONVOCADO_VENCIMENTO_DECORRIDO
        assert estado not in nomes.ESPECIES_DE_DESFECHO

    def test_nenhum_estado_de_leitura_e_uma_especie_de_desfecho(self):
        """A fronteira dita por forma: os quatro estados e os sete desfechos não se encontram."""
        estados = {
            nomes.CONVOCADO_PRAZO_NAO_INICIADO,
            nomes.CONVOCADO_PRAZO_EM_CURSO,
            nomes.CONVOCADO_VENCIMENTO_DECORRIDO,
            nomes.DESFECHADO,
        }

        assert not estados & set(nomes.ESPECIES_DE_DESFECHO)

    def test_o_prazo_em_curso_nao_vira_decorrido_antes_da_hora(self):
        assert (
            prazo.estado(tem_desfecho=False, enviado_em=ENVIO, vencimento=DEPOIS, agora=ENVIO)
            == nomes.CONVOCADO_PRAZO_EM_CURSO
        )

    def test_desfecho_registrado_encerra_a_leitura_do_prazo(self):
        """Registrado o desfecho, o prazo deixa de ser a pergunta — inclusive se já decorreu."""
        assert (
            prazo.estado(tem_desfecho=True, enviado_em=ENVIO, vencimento=ANTES, agora=DEPOIS)
            == nomes.DESFECHADO
        )

    def test_edital_sem_prazo_publicado_nao_decorre_nunca(self):
        """Vencimento nulo é "este Edital não publicou prazo", e não "venceu agora"."""
        assert prazo.decorrido(vencimento=None, enviado_em=ENVIO, agora=DEPOIS) is False
        assert (
            prazo.estado(tem_desfecho=False, enviado_em=ENVIO, vencimento=None, agora=DEPOIS)
            == nomes.CONVOCADO_PRAZO_EM_CURSO
        )
