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

import logging
from urllib import error

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.domain import conferencia
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
                f"Concurso {referencia} de {fonte}: a Caixa não respondeu a tempo, "
                "em 3 tentativa(s)."
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
    # A evidência do que se observou viaja junto: quem lê precisa saber por que não deu certo — nas
    # palavras dele, e não nas da biblioteca de rede (124, FR-3961).
    assert "a Caixa não respondeu a tempo, em 3 tentativa(s)" in detalhe


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
    assert conferencia.SEM_CONEXAO in sem_rede.evidencia


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


# ------------------------------------------------ a mensagem é de quem opera (124)


def _fonte_que_falha(monkeypatch, falha):
    """A Caixa de verdade, com `urlopen` trocado por uma chamada que sempre falha assim."""

    def cair(*_args, **_kwargs):
        if isinstance(falha, bytes):
            return _Resposta(falha)
        raise falha

    monkeypatch.setattr("urllib.request.urlopen", cair)


class _Resposta:
    def __init__(self, corpo):
        self.corpo = corpo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.corpo


FALHAS = [
    pytest.param(
        error.URLError(TimeoutError("timed out")), conferencia.SEM_RESPOSTA_A_TEMPO, id="url-tempo"
    ),
    pytest.param(TimeoutError("timed out"), conferencia.SEM_RESPOSTA_A_TEMPO, id="tempo"),
    pytest.param(error.URLError("Name or service not known"), conferencia.SEM_CONEXAO, id="rede"),
    pytest.param(
        error.HTTPError("https://caixa", 503, "Service Unavailable", {}, None),
        conferencia.COM_ERRO,
        id="http",
    ),
    pytest.param(b"<html>manutencao</html>", conferencia.COM_ERRO, id="nao-json"),
]


@pytest.mark.parametrize(("falha", "motivo"), FALHAS)
def test_a_observacao_diz_o_motivo_com_as_palavras_da_conferencia(monkeypatch, falha, motivo):
    """`FR-3961` — a mesma falha, a mesma frase, na publicação e no sorteio.

    A conferência da `116` já traduzia a falha de rede para os quatro motivos; a observação, que
    fala com a mesma Caixa, guardava `URLError: <urlopen error timed out>`. São os mesmos motivos,
    e não uma tradução nova: duas maneiras de dizer a mesma falha divergem na primeira mudança.
    """
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    _fonte_que_falha(monkeypatch, falha)
    observado = LoteriaFederal().observar(fonte="Loteria Federal", referencia="6098")

    assert observado.falha_de_acesso is True and observado.indisponivel is False
    assert motivo in observado.evidencia
    assert type(falha).__name__ not in observado.evidencia


@pytest.mark.parametrize(("falha", "motivo"), FALHAS)
def test_a_recusa_nao_traz_nome_de_excecao_nem_asteriscos(certame, monkeypatch, falha, motivo):
    """`FR-3961`, `FR-3963` — o que a tela imprime por `{{ erro.detalhe }}`, ao vivo.

    O caso passa pelo adaptador de verdade, e não pelo falso do início deste arquivo: a evidência
    crua nascia no adaptador, e um falso que escrevesse a frase certa provaria só o falso. E a tela
    não interpreta Markdown: `**nada foi registrado**` chegava com os asteriscos.
    """
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    _fonte_que_falha(monkeypatch, falha)
    with pytest.raises(DomainError) as recusa:
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte="Loteria Federal",
            referencia="6098",
            idempotency_key="fonte-fora-124",
            correlation_id="teste-124",
            fonte_externa=LoteriaFederal(),
        )

    detalhe = recusa.value.detail
    assert recusa.value.code == "source_unreachable"
    assert motivo in detalhe
    assert "nada foi registrado" in detalhe
    assert "**" not in detalhe, detalhe
    for cru in (
        "URLError",
        "HTTPError",
        "TimeoutError",
        "JSONDecodeError",
        "Error:",
        "<urlopen",
        "503",
    ):
        assert cru not in detalhe, (cru, detalhe)
    assert not OcorrenciaDaFonte.objects.exists()


class _Coletor(logging.Handler):
    def __init__(self):
        super().__init__()
        self.registros = []

    def emit(self, record):
        self.registros.append(record)


def test_o_detalhe_tecnico_vai_para_o_log(monkeypatch):
    """`FR-3962` — o que saiu da mensagem não se perde: quem mantém o sistema o lê no log."""
    from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

    _fonte_que_falha(monkeypatch, error.URLError(TimeoutError("timed out")))
    # O logger do projeto não propaga até o `caplog`; o coletor se pendura nele direto.
    logger = logging.getLogger("processo_seletivo.sorteios.infrastructure.fontes.loteria_federal")
    coletor = _Coletor()
    logger.addHandler(coletor)
    try:
        LoteriaFederal().observar(fonte="Loteria Federal", referencia="6098")
    finally:
        logger.removeHandler(coletor)

    (registro,) = [
        r.getMessage()
        for r in coletor.registros
        if r.getMessage().startswith("observacao_sem_acesso_a_fonte")
    ]
    assert "URLError" in registro
    assert '"referencia": "6098"' in registro
