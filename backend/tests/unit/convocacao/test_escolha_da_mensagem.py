"""A escolha da mensagem e a identificação do modelo, sem banco (121, R-002, R-009).

`SC-1160`, `FR-3884`, `FR-3885`, `FR-3889`. As sete linhas da tabela da R-002 são a regra da D-008
— decidida pelo usuário — inteira: a mensagem da correção cita a **última enviada com sucesso** na
cadeia, e não a da imediatamente anterior. A linha que motivou a decisão é a segunda: A enviada, B
falhada, C sucessora de B — C cita A.
"""

import re
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from processo_seletivo.convocacao.domain import mensagem
from processo_seletivo.convocacao.domain.mensagem import (
    CORRECAO,
    DOCUMENTO_E_REQUERIMENTO,
    INICIAL,
    NENHUM,
    SO_DOCUMENTO,
    SO_REQUERIMENTO,
    escolha_da_mensagem,
    identificacao_do_modelo,
)

T0 = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)
ENVIO_DE_C = T0 + timedelta(days=3)


def comunicacao(resultado, quando=None, forma="INDIVIDUAL_MESSAGE"):
    return SimpleNamespace(
        resultado=resultado,
        forma=forma,
        enviado_em=quando if resultado == "ENVIADA" else None,
    )


def elo(vencimento_em_dias, *comunicacoes):
    return SimpleNamespace(
        vencimento=T0 + timedelta(days=vencimento_em_dias), comunicacoes=list(comunicacoes)
    )


def item(situacao="OBRIGATORIO", gravada_em=T0):
    return SimpleNamespace(situacao=situacao, gravada_em=gravada_em)


def escolher(anteriores, *, itens=(), requerimento=False, instante=ENVIO_DE_C):
    return escolha_da_mensagem(
        itens=list(itens),
        instante=instante,
        requerimento_na_chamada=requerimento,
        anteriores=anteriores,
    )


A_ENVIADA = T0 + timedelta(hours=1)
B_ENVIADA = T0 + timedelta(days=1)


class TestACadeia:
    """A tabela da R-002, linha a linha. `anteriores` vai da imediatamente anterior à raiz."""

    def test_a_enviada_c_cita_a(self):
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA))

        escolha = escolher([a])

        assert escolha.modelo == CORRECAO
        assert escolha.citada.enviado_em == A_ENVIADA
        assert escolha.citada.vencimento == a.vencimento

    def test_a_enviada_b_falhada_c_cita_a(self):
        """A linha que motivou a D-008: a mensagem de B não saiu, e a pessoa só recebeu A."""
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA))
        b = elo(8, comunicacao("FALHA"))

        escolha = escolher([b, a])

        assert escolha.modelo == CORRECAO
        assert escolha.citada.enviado_em == A_ENVIADA
        assert escolha.citada.vencimento == a.vencimento, "o prazo de A, e não o de B"

    def test_a_e_b_enviadas_c_cita_b(self):
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA))
        b = elo(8, comunicacao("ENVIADA", B_ENVIADA))

        escolha = escolher([b, a])

        assert escolha.citada.enviado_em == B_ENVIADA
        assert escolha.citada.vencimento == b.vencimento

    def test_a_e_b_falhadas_c_e_a_inicial(self):
        """Sem envio com sucesso na cadeia, nada há a substituir (D-008)."""
        a = elo(5, comunicacao("FALHA"))
        b = elo(8, comunicacao("FALHA"))

        escolha = escolher([b, a])

        assert escolha.modelo == INICIAL
        assert escolha.citada is None

    def test_a_sem_comunicacao_c_e_a_inicial(self):
        assert escolher([elo(5)]).modelo == INICIAL

    def test_a_por_publicacao_c_e_a_inicial(self):
        """A publicação não é mensagem à pessoa (FR-287 da 019)."""
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA, forma="PUBLICATION"))

        assert escolher([a]).modelo == INICIAL

    def test_b_falhada_e_depois_enviada_c_cita_o_envio_de_b(self):
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA))
        b = elo(8, comunicacao("FALHA"), comunicacao("ENVIADA", B_ENVIADA))

        escolha = escolher([b, a])

        assert escolha.citada.enviado_em == B_ENVIADA

    def test_sem_anterior_e_a_inicial(self):
        assert escolher([]).modelo == INICIAL

    def test_envio_posterior_ao_instante_nao_conta(self):
        """A reconstrução lê os registros até o instante do envio, e nada gravado depois."""
        a = elo(5, comunicacao("ENVIADA", ENVIO_DE_C + timedelta(minutes=1)))

        assert escolher([a]).modelo == INICIAL


class TestAVariante:
    """`FR-3884`: o que a chamada pede de fato, e *documento* é documento obrigatório (D-007)."""

    @pytest.mark.parametrize(
        ("itens", "requerimento", "variante"),
        [
            ([item()], True, DOCUMENTO_E_REQUERIMENTO),
            ([item()], False, SO_DOCUMENTO),
            ([], True, SO_REQUERIMENTO),
            ([], False, NENHUM),
            # Só facultativo: a chamada não pede documento (D-007).
            ([item("FACULTATIVO")], True, SO_REQUERIMENTO),
            ([item("FACULTATIVO"), item("NAO_SE_APLICA")], False, NENHUM),
        ],
    )
    def test_as_quatro_variantes(self, itens, requerimento, variante):
        assert escolher([], itens=itens, requerimento=requerimento).variante == variante

    def test_a_mesma_variante_na_correcao(self):
        a = elo(5, comunicacao("ENVIADA", A_ENVIADA))

        escolha = escolher([a], itens=[item()], requerimento=True)

        assert (escolha.modelo, escolha.variante) == (CORRECAO, DOCUMENTO_E_REQUERIMENTO)

    def test_o_item_gravado_depois_do_envio_nao_conta(self):
        depois = item(gravada_em=ENVIO_DE_C + timedelta(seconds=1))

        assert escolher([], itens=[depois]).variante == NENHUM


class TestAIdentificacaoDoModelo:
    """`R-009`, `FR-3889`: determinística, sensível a cada caractere e ao arquivo de cada trecho."""

    HTML = "<p>Você foi convocado.</p>\n"
    TEXTO = "Você foi convocado.\n"
    ESTILOS = '{"texto": "color:#1c1c1c;"}\n'

    def test_o_formato(self):
        valor = identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=self.ESTILOS)

        assert re.fullmatch(r"inicial:sha256-com-estilos:[0-9a-f]{64}", valor)

    def test_o_mesmo_par_da_o_mesmo_valor(self):
        assert identificacao_do_modelo("correcao", self.HTML, self.TEXTO, estilos=self.ESTILOS) == (
            identificacao_do_modelo("correcao", self.HTML, self.TEXTO, estilos=self.ESTILOS)
        )

    @pytest.mark.parametrize("qual", ["html", "texto"])
    def test_um_caractere_muda_o_valor(self, qual):
        original = identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=self.ESTILOS)
        html = self.HTML.replace("convocado", "convocada") if qual == "html" else self.HTML
        texto = self.TEXTO.replace(".", "!") if qual == "texto" else self.TEXTO

        assert identificacao_do_modelo("inicial", html, texto, estilos=self.ESTILOS) != original

    def test_uma_cor_do_mapa_de_estilos_muda_o_valor(self):
        """Revisão de 13/11 da R-009: o mapa decide o HTML que sai, e entra no resumo."""
        original = identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=self.ESTILOS)
        outra_cor = self.ESTILOS.replace("#1c1c1c", "#000000")

        assert identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=outra_cor) != (
            original
        )

    def test_um_trecho_movido_do_texto_para_os_estilos_muda_o_valor(self):
        assert identificacao_do_modelo(
            "inicial", self.HTML, "ab", estilos="c"
        ) != identificacao_do_modelo("inicial", self.HTML, "a", estilos="bc")

    def test_mover_um_trecho_de_arquivo_muda_o_valor(self):
        """Os rótulos impedem que a mesma concatenação, partida em outro lugar, coincida."""
        assert identificacao_do_modelo(
            "inicial", "ab", "c", estilos=self.ESTILOS
        ) != identificacao_do_modelo("inicial", "a", "bc", estilos=self.ESTILOS)

    def test_a_composicao_e_a_da_r_009(self):
        """A regra escrita, recalculada aqui sem a função: é ela que a conferência pelo Git usa."""
        import hashlib

        esperado = hashlib.sha256(
            b"html\0"
            + self.HTML.encode()
            + b"\0texto\0"
            + self.TEXTO.encode()
            + b"\0estilos\0"
            + self.ESTILOS.encode()
        ).hexdigest()

        assert identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=self.ESTILOS) == (
            f"inicial:sha256-com-estilos:{esperado}"
        )

    def test_le_a_fonte_do_modelo_compilado(self):
        """A fonte que o motor entregou, e não um arquivo relido do disco (R-009)."""
        html = SimpleNamespace(template=SimpleNamespace(source=self.HTML))
        texto = SimpleNamespace(template=SimpleNamespace(source=self.TEXTO))

        assert mensagem.identificacao_do_modelo("inicial", html, texto, estilos=self.ESTILOS) == (
            identificacao_do_modelo("inicial", self.HTML, self.TEXTO, estilos=self.ESTILOS)
        )
