"""Falha de acesso não é ausência de extração (021, FR-015, FR-073).

**O defeito era irreversível, e aparecia no pior instante possível.** O adaptador tratava os dois
desfechos negativos como um só: não conseguir falar com a Caixa e a Caixa dizer que não há extração
produziam a mesma `Observacao(indisponivel=True)`. Registrada, ela é linha append-only nas três
camadas — `save` recusa, a trigger recusa, o privilégio não existe — e é ela que a regra publicada
de substituição consome.

O resultado prático: cinco segundos de rede ruim durante a transmissão descartavam **para sempre** a
extração que o Edital declarou, e a cadeia avançava sozinha para a seguinte — que provavelmente
ainda não aconteceu, travando o certame até que aconteça, sem nenhum caminho de volta e sem que
ninguém tivesse decidido nada.

A correção não afrouxa a FR-015: qual ocorrência substitui continua sendo derivado, e não escolhido.
O que muda é **quem afirma** que não houve extração — a fonte, e não a rede.
"""

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from processo_seletivo.sorteios.models import OcorrenciaDaFonte
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


class FonteInalcancavel:
    """O que o adaptador devolve quando não conseguiu falar com a fonte."""

    def observar(self, *, fonte, referencia):
        return Observacao(
            falha_de_acesso=True,
            evidencia=(
                f"Concurso {referencia} de {fonte}: não foi possível falar com a fonte em "
                "3 tentativa(s). Última falha: URLError: <urlopen error timed out>"
            ),
        )


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def test_a_falha_de_acesso_nao_registra_ocorrencia_nenhuma(certame):
    """Nada gravado: a extração declarada continua sendo a que vale, e se tenta de novo."""
    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="fonte-fora-1",
            correlation_id="teste-021",
            fonte_externa=FonteInalcancavel(),
        )

    assert recusa.value.code == "source_unreachable"
    assert recusa.value.status == 502
    assert not OcorrenciaDaFonte.objects.exists(), (
        "uma falha de rede não escreve linha nenhuma — e a linha, escrita, não se apaga"
    )


def test_a_recusa_diz_que_nada_foi_registrado_e_qual_e_o_proximo_passo(certame):
    """Ao vivo, a mensagem precisa dizer o que fazer — e o que fazer é tentar de novo."""
    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="fonte-fora-2",
            correlation_id="teste-021",
            fonte_externa=FonteInalcancavel(),
        )

    detalhe = recusa.value.detail
    assert "nada foi registrado" in detalhe
    assert "observá-la de novo" in detalhe
    # A evidência do que se observou viaja junto: quem lê precisa saber o que a rede respondeu.
    assert "URLError" in detalhe


def test_depois_da_falha_a_ocorrencia_declarada_continua_sendo_a_que_vale(certame):
    """A cadeia de substituição **não** avança por causa de rede — e é o ponto inteiro."""
    with pytest.raises(DomainError):
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="fonte-fora-3",
            correlation_id="teste-021",
            fonte_externa=FonteInalcancavel(),
        )

    from processo_seletivo.sorteios.domain import substituicao

    assert substituicao.proxima_a_observar(METODO, indisponiveis=set()) == METODO["occurrence"]

    # E a segunda tentativa, com a fonte de volta, observa exatamente aquela extração.
    declarado = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="fonte-de-volta",
        correlation_id="teste-021",
    )

    assert declarado["referencia"] == METODO["occurrence"]
    assert declarado["indisponivel"] is False


def test_o_adaptador_da_loteria_separa_os_dois_desfechos():
    """A distinção nasce no adaptador, e é ele quem sabe qual das duas coisas aconteceu.

    Sem rede: a fonte respondendo sem os números é indisponibilidade — fato sobre o mundo; a
    chamada que não completa é falha de acesso — fato sobre nós.
    """
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    adaptador = LoteriaFederal()

    class RespostaVazia:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"dataApuracao": "06/09/2026", "listaDezenas": []}'

    import urllib.request as biblioteca

    original = biblioteca.urlopen
    try:
        biblioteca.urlopen = lambda *_, **__: RespostaVazia()
        sem_numeros = adaptador.observar(fonte="Loteria Federal", referencia="6098")

        def cair(*_, **__):
            raise biblioteca.URLError("timed out")

        biblioteca.urlopen = cair
        sem_rede = adaptador.observar(fonte="Loteria Federal", referencia="6098")
    finally:
        biblioteca.urlopen = original

    assert sem_numeros.indisponivel is True and sem_numeros.falha_de_acesso is False
    assert sem_rede.falha_de_acesso is True and sem_rede.indisponivel is False
    assert "não foi possível falar com a fonte" in sem_rede.evidencia


def test_a_semente_nunca_vem_do_rateio_de_premios():
    """**O material bruto é a extração, e nada que se pareça com ela** (021, FR-019, FR-076).

    O adaptador lia `listaDezenas` **ou**, faltando ela, `listaRateioPremio`. São coisas
    completamente diferentes: a primeira traz os cinco bilhetes premiados; a segunda, as faixas de
    premiação, com `valorPremio` e `numeroDeGanhadores`. Numa resposta em que a extração viesse
    vazia e o rateio não, o material bruto passava a ser a serialização daqueles dicionários, e a
    regra publicada extraía os dígitos de **valores monetários** — o sorteio de um certame semeado
    por quanto se pagou de prêmio, sem que nada acusasse a troca.

    A resposta usada aqui é a forma real do serviço da Caixa, com os campos que ele publica.
    """
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    class SoComRateio:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return (
                b'{"numero": 6098, "dataApuracao": "06/09/2026", "listaDezenas": [],'
                b' "listaRateioPremio": ['
                b'{"descricaoFaixa": "1 acertos", "faixa": 1, "numeroDeGanhadores": 1,'
                b' "valorPremio": 500000.0},'
                b'{"descricaoFaixa": "2 acertos", "faixa": 2, "numeroDeGanhadores": 1,'
                b' "valorPremio": 35000.0}]}'
            )

    import urllib.request as biblioteca

    original = biblioteca.urlopen
    try:
        biblioteca.urlopen = lambda *_, **__: SoComRateio()
        observado = LoteriaFederal().observar(fonte="Loteria Federal", referencia="6098")
    finally:
        biblioteca.urlopen = original

    assert observado.indisponivel is True, "sem extração publicada, não há material a observar"
    assert observado.material_bruto == ""
    assert "500000" not in observado.material_bruto
    assert "sem os números da extração" in observado.evidencia
