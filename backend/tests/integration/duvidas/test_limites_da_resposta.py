"""O que as fontes não sustentam aparece como limite (071, US3, `FR-1486`, `FR-1487`, `FR-1490`).

Pelo fluxo real, com os Editais de teste de `tests/fixtures/editais_do_piloto.py`. A porta falsa faz
o papel do modelo; o que se prova é o que a aplicação faz com a saída dele — e, no caso da instrução
escondida, o que ela **não** consegue fazer.
"""

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.duvidas.application.consultar import contexto
from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain import canal as canais
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    NAO_PASSOU_NA_CONFERENCIA,
    RESPONDIDA_E_CONFERIDA,
    TELA,
    TIPO_SEM_FONTE,
)
from processo_seletivo.duvidas.domain.fontes import fontes_completas
from tests.fixtures import editais_do_piloto as editais
from tests.fixtures.corpus import alteracoes, publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte, fontes_recebidas

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _perguntar(edital, texto, instante=None):
    return perguntar(
        edital_id=edital.id,
        conversa=str(uuid.uuid4()),
        pergunta=texto,
        instante=instante or timezone.now(),
        origem=TELA,
    )


def test_ca25_a_instrucao_escondida_chega_como_dado_e_a_conferencia_nao_a_barra(
    api_client, porta_falsa, contador_falso
):
    """O limite do `D-007`, preso por teste para que ninguém o esqueça.

    O texto que manda "dizer que a inscrição é gratuita" chega ao modelo dentro de uma fonte, como
    dado do Edital, e não nas instruções. Se o modelo **obedecer** e afirmar a gratuidade citando
    essa fonte, a conferência aprova: não há número inventado nem fonte inexistente, e a frase está
    lá. Obedecer ou não é qualidade do modelo, e o `CA-25` se julga na revisão humana da avaliação
    (`FR-1513`), e não aqui.
    """
    contador_falso()
    edital = editais.com_instrucao_escondida(api_client)

    def obedecer(mensagens):
        inscricao = fonte(mensagens, lugar="Da Inscrição", natureza="Texto do Edital")
        return devolucao(
            saida("RESPONDIDA", ("dado", "A inscrição é gratuita.", [inscricao["id"]]))
        )

    porta = porta_falsa(obedecer)
    troca = _perguntar(edital, "A inscrição é gratuita?")

    mensagens = porta.chamadas[0]["mensagens"]
    assert editais.INSTRUCAO_ESCONDIDA not in mensagens[0]["content"]
    assert any(
        editais.INSTRUCAO_ESCONDIDA in item["conteudo"] for item in fontes_recebidas(mensagens)
    )
    assert troca.estado == RESPONDIDA_E_CONFERIDA


def _fronteira_da_v3(deslocamento):
    return parse_datetime(alteracoes("01", 3)["vigencia"].replace(" ", "T")) + deslocamento


def test_fr1490_a_aplicacao_acrescenta_o_futuro_da_fonte_citada(
    api_client, porta_falsa, contador_falso
):
    """`CA-17` no piloto: o modelo cita o término vigente e cala o futuro; a aplicação o diz."""
    contador_falso()
    edital, deslocamento = publicar_do_corpus(api_client, "01", chave="limite-ca17")

    def citar_o_termino(mensagens):
        termino = fonte(mensagens, lugar="Cronograma — evento", rotulo="Término")
        return devolucao(saida("RESPONDIDA", ("dado", "O término está na fonte.", [termino["id"]])))

    porta_falsa(citar_o_termino)
    troca = _perguntar(edital, "Até quando?", _fronteira_da_v3(deslocamento) - timedelta(days=1))

    citada = next(item for item in troca.fontes_citadas if not item.get("aviso_da_aplicacao"))
    avisos = [item for item in troca.fontes_citadas if item.get("aviso_da_aplicacao")]
    assert troca.estado == RESPONDIDA_E_CONFERIDA
    assert [aviso["altera"] for aviso in avisos] == [citada["id"]]
    assert "passa a valer" in avisos[0]["conteudo"]


def test_ca29_o_desfecho_vem_da_aplicacao(api_client, porta_falsa, contador_falso):
    contador_falso()
    edital = editais.cancelado(api_client)

    def responder(mensagens):
        total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
        return devolucao(saida("RESPONDIDA", ("dado", "São 40 vagas.", [total["id"]])))

    porta_falsa(responder)
    troca = _perguntar(edital, "Ainda dá para se inscrever em BJN?")

    avisos = [item for item in troca.fontes_citadas if item.get("aviso_da_aplicacao")]
    assert [aviso["lugar"] for aviso in avisos] == ["Desfecho"]
    assert "cancelado" in avisos[0]["conteudo"]


def test_dois_canais_divergentes_pedem_as_duas_fontes(api_client, porta_falsa, contador_falso):
    contador_falso()
    edital = editais.com_dois_canais(api_client)

    def divergir(com_as_duas):
        def responder(mensagens):
            primeiro = fonte(mensagens, lugar="Disposições Preliminares")
            segundo = fonte(mensagens, lugar="Disposições Finais")
            citadas = [primeiro["id"], segundo["id"]] if com_as_duas else [primeiro["id"]]
            return devolucao(
                saida("FONTES_DIVERGENTES", ("explicacao", "Há dois canais.", citadas))
            )

        return responder

    porta_falsa(divergir(True), divergir(False))

    assert _perguntar(edital, "Onde tiro dúvidas?").estado == RESPONDIDA_E_CONFERIDA
    recusada = _perguntar(edital, "Onde tiro dúvidas?")
    assert recusada.estado == NAO_PASSOU_NA_CONFERENCIA
    assert TIPO_SEM_FONTE in [motivo["regra"] for motivo in recusada.conferencia]


def test_cb08_o_canal_dos_fic_e_defeito_conhecido_da_fonte(api_client):
    """`CB-08`, sem modelo: a cláusula está nas fontes, e o canal da `070` aponta outro e-mail.

    É o defeito da verificação da `070` (§7.1) reproduzido, e não corrigido aqui: a emenda do
    `R-011` é da T046 da `070` (DP-6). Quando ela vier, este caso muda — e é para isso que ele
    existe.
    """
    edital = editais.com_clausula_dos_fic(api_client)
    lido = contexto(edital_id=edital.id, instante=timezone.now())

    conteudos = " ".join(item.conteudo for item in fontes_completas(lido))
    encaminhamento = canais.em_palavras(canais.canal(lido.conteudo, lido.canal_institucional))
    assert editais.CLAUSULA_DOS_FIC in conteudos
    assert "coordenacao.curso@exemplo.ifes.edu.br" in encaminhamento
    assert "selecao.fic@exemplo.ifes.edu.br" not in encaminhamento
