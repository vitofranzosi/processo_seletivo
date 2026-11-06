"""Adaptador de referência: a extração da Loteria Federal (021, R-005).

**Por que esta fonte é o exemplo, e não a norma.** Ela é ocorrência pública, futura, previamente
determinada por número de concurso e data, e amplamente usada como fonte de aleatoriedade em atos
administrativos brasileiros. A escolha institucional, porém, é do Edital: a spec fixa as
propriedades exigidas da fonte, não a identidade dela. Este arquivo é uma implementação da porta,
e não a definição do que a fonte deve ser.

**O que ele não faz:** não normaliza — a regra é do método —, não decide substituição e não
interpreta ausência como erro. Devolve o que a fonte publicou, ou diz que não havia nada.
"""

import json
import logging
from datetime import date, datetime
from urllib import error, request

from django.conf import settings
from django.utils import timezone

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.domain import conferencia
from processo_seletivo.sorteios.infrastructure.fontes import FonteExterna, Observacao

ENDERECO_DO_ULTIMO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal"
ENDERECO = ENDERECO_DO_ULTIMO + "/{referencia}"

logger = logging.getLogger(__name__)


class LoteriaFederal(FonteExterna):
    # A Caixa publica `dataApuracao` sem horário, e `_nao_antes_de` devolve a meia-noite (102).
    PUBLICA_SO_A_DATA = True
    # Só algarismos: a API recusa com HTTP 400 até a grafia `6106-9` do comunicado dela (116).
    FORMA_DA_REFERENCIA = conferencia.FORMA_DO_CONCURSO
    SABE_CONFERIR = True

    def consultar_ultimo(self):
        """O último concurso realizado — a única coisa que a Caixa permite afirmar (116, FR-3628).

        **Só vale a resposta inteira**: número inteiro, data no formato da Caixa e os cinco
        bilhetes. Faltando um deles não há último, e a conferência é inconclusiva — nunca "ainda
        não realizado". **Uma tentativa**, com o tempo limite da conferência, e não as três da
        observação: a conferência acrescenta espera a um clique de publicar, e a pior soma das duas
        chamadas precisa caber nos 15 segundos da SC-1097. Quem quiser saber de novo, clica de novo.
        """
        corpo, motivo = _uma_chamada(ENDERECO_DO_ULTIMO)
        if corpo is None:
            return conferencia.ConsultaDoUltimo(None, motivo)
        extracao = _extracao(corpo)
        if extracao is None:
            return conferencia.ConsultaDoUltimo(None, conferencia.SEM_O_ULTIMO)
        numero, dia = extracao
        proximo = corpo.get("numeroConcursoProximo")
        return conferencia.ConsultaDoUltimo(
            conferencia.UltimoConcurso(
                numero=numero,
                em=dia,
                proximo=proximo if _inteiro(proximo) else None,
            )
        )

    def consultar_data(self, numero):
        """O dia em que o concurso foi realizado, ou `None` — **nunca** um estado (FR-3629).

        Só é chamada para concurso já sabido realizado. A resposta de erro, qualquer que seja o
        código, quer dizer só "sem data": o 500 que a Caixa devolve ao concurso futuro é o mesmo de
        um erro do serviço, e decidir por ele seria adivinhar.
        """
        corpo, _ = _uma_chamada(ENDERECO.format(referencia=numero))
        extracao = _extracao(corpo) if corpo is not None else None
        if extracao is None or extracao[0] != numero:
            return None
        return extracao[1]

    def observar(self, *, fonte, referencia):
        """O que a fonte publicou — ou **por que** não foi possível saber.

        **Os dois desfechos negativos são distintos, e a distinção é a garantia** (021, FR-015).
        Uma resposta da fonte sem a extração é `indisponivel`: é fato sobre o mundo, e é o que
        aciona a regra de substituição publicada — em linha append-only, para sempre. Não conseguir
        falar com a fonte é `falha_de_acesso`: não afirma nada, não grava nada, e se tenta de novo.

        Antes as duas eram a mesma coisa, e o efeito aparecia no pior momento possível: um blip de
        rede durante a transmissão registrava indisponibilidade definitiva, a cadeia avançava
        sozinha para a extração seguinte, e a extração que o Edital declarou ficava descartada sem
        que ninguém tivesse decidido descartá-la.
        """
        tentativas = max(int(getattr(settings, "SORTEIO_FONTE_TENTATIVAS", 3)), 1)
        limite = float(getattr(settings, "SORTEIO_FONTE_TIMEOUT_SEGUNDOS", 10))
        motivo = ""
        falhas = []
        resposta_da_fonte = ""
        for _ in range(tentativas):
            try:
                with request.urlopen(
                    ENDERECO.format(referencia=referencia), timeout=limite
                ) as resposta:
                    corpo = json.loads(resposta.read().decode("utf-8"))
            except (error.URLError, TimeoutError, ValueError) as falha:
                motivo = _motivo_da_falha(falha)
                falhas.append(f"{type(falha).__name__}: {falha}")
                continue
            material = _bilhetes_premiados(corpo)
            quando = _nao_antes_de(corpo)
            if material and quando is not None:
                return Observacao(material_bruto=material, ocorrida_nao_antes_de=quando)
            resposta_da_fonte = (
                # Material sem data é material que não prova precedência: aceitá-lo devolveria ao
                # certame a possibilidade de congelar já sabendo o resultado (FR-016).
                "A fonte devolveu a extração sem a data em que ela ocorreu."
                if material
                else "A fonte respondeu sem os números da extração."
            )
        if resposta_da_fonte:
            # **A fonte falou.** Ela é quem diz que não há extração, e é por isso que este desfecho
            # pode consumir a cadeia de substituição.
            return Observacao(
                indisponivel=True,
                evidencia=(
                    f"Concurso {referencia} de {fonte}: {resposta_da_fonte} "
                    f"Observado em {tentativas} tentativa(s)."
                ),
            )
        # **A evidência da falha de acesso só existe na mensagem**, porque nada se grava — e a
        # mensagem é lida por quem conduz o sorteio, com a transmissão aberta (124, FR-3961). Ela
        # dizia "Última falha: URLError: <urlopen error timed out>": nome de exceção que quem opera
        # não tem o que fazer com ele, quando a conferência da mesma fonte já traduzia a mesma falha
        # em palavras dele (116, FR-3641). O detalhe técnico tem valor para quem mantém o sistema, e
        # vai para o log, com o nome da fonte e da referência para a busca (FR-3962).
        logger.warning(
            "observacao_sem_acesso_a_fonte %s",
            json.dumps(
                {"fonte": fonte, "referencia": referencia, "falhas": falhas},
                ensure_ascii=False,
                sort_keys=True,
            ),
        )
        return Observacao(
            falha_de_acesso=True,
            evidencia=f"Concurso {referencia} de {fonte}: {motivo}, em {tentativas} tentativa(s).",
        )


def _uma_chamada(endereco):
    """`(corpo, "")` de uma resposta JSON, ou `(None, motivo)` — numa tentativa, sem levantar.

    **O motivo é dito nas palavras de quem opera, e só ele sai daqui** (FR-3641, FR-3648): código
    HTTP, nome de exceção e corpo da resposta não chegam à mensagem nem ao registro. A tradução é
    `_motivo_da_falha`, a mesma da observação.
    """
    limite = float(getattr(settings, "SORTEIO_CONFERENCIA_TIMEOUT_SEGUNDOS", 5))
    try:
        with request.urlopen(endereco, timeout=limite) as resposta:
            bruto = resposta.read()
    except OSError as falha:
        return None, _motivo_da_falha(falha)
    try:
        corpo = json.loads(bruto.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None, conferencia.SEM_O_ULTIMO
    if not isinstance(corpo, dict):
        return None, conferencia.SEM_O_ULTIMO
    return corpo, ""


def _motivo_da_falha(falha):
    """A falha de uma chamada à Caixa, nas palavras de quem opera (116, FR-3641; 124, FR-3961).

    **Uma tradução só, para a conferência e para a observação.** As duas falam com a mesma fonte, e
    a mesma falha de rede não pode chegar à tela da publicação como "a Caixa não respondeu a tempo"
    e à do sorteio como `URLError`. O `HTTPError` vem antes do `URLError` porque é subclasse dele, e
    é a Caixa que respondeu, e não a rede que caiu. O `ValueError` é a resposta que não se lê como
    JSON — só a observação o recebe aqui, porque a conferência decodifica fora do `try` —, e é a
    Caixa respondendo com algo que não é a extração: um erro dela, e não da rede.
    """
    if isinstance(falha, error.HTTPError):
        falha.close()
        return conferencia.COM_ERRO
    if isinstance(falha, error.URLError):
        if isinstance(falha.reason, TimeoutError):
            return conferencia.SEM_RESPOSTA_A_TEMPO
        return conferencia.SEM_CONEXAO
    if isinstance(falha, TimeoutError):
        return conferencia.SEM_RESPOSTA_A_TEMPO
    if isinstance(falha, ValueError):
        return conferencia.COM_ERRO
    return conferencia.SEM_CONEXAO


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _extracao(corpo):
    """`(numero, dia)` de uma resposta que traz a extração **inteira**, ou `None` (FR-3628).

    Inteira quer dizer número inteiro, data `dd/mm/aaaa` e os cinco bilhetes. A resposta sem os
    bilhetes não prova realização, pela mesma razão que `_bilhetes_premiados` recusa sucedâneo, e um
    `numero` que chega como texto é resposta de outra forma, e não o concurso.
    """
    numero = corpo.get("numero")
    try:
        dia = datetime.strptime(str(corpo.get("dataApuracao") or ""), "%d/%m/%Y").date()
    except ValueError:
        return None
    bilhetes = [item for item in corpo.get("listaDezenas") or [] if str(item).strip()]
    if not _inteiro(numero) or len(bilhetes) != 5:
        return None
    return numero, dia


def _bilhetes_premiados(corpo):
    """Os cinco bilhetes premiados da extração, na ordem dos prêmios — e **nada além deles**.

    `listaDezenas` é o nome que a Caixa dá ao campo, e o nome engana: não são dezenas, são os cinco
    números de bilhete, de seis dígitos cada, do 1º ao 5º prêmio. É esse o material bruto que a
    regra `DIGITOS_EM_SEQUENCIA` transforma em semente.

    **O `or corpo.get("listaRateioPremio")` que morava aqui era uma porta para semente inventada.**
    O rateio é outra coisa inteiramente: são as faixas de premiação, com `valorPremio: 500000.0` e
    `numeroDeGanhadores`. Numa resposta 200 em que a extração viesse vazia e o rateio não, o
    material bruto passaria a ser a serialização Python daqueles dicionários, a regra publicada
    extrairia os dígitos de **valores monetários**, e o sorteio de um certame seria semeado por
    quanto se pagou de prêmio — sem que nada, em lugar nenhum, acusasse a troca.

    Um campo, e a ausência dele é ausência de extração. Fonte que responde sem o que se foi buscar
    não devolve um sucedâneo: devolve nada, e quem decide o que fazer com isso é a regra publicada.
    """
    bilhetes = corpo.get("listaDezenas") or []
    return " ".join(str(item) for item in bilhetes if str(item).strip())


def _nao_antes_de(corpo):
    """O instante **mais cedo** em que a extração pode ter acontecido, conforme a fonte publica.

    A Caixa publica `dataApuracao: "11/09/2024"` — uma data, sem horário. A versão anterior desta
    função carimbava `20:00`, e isso era invenção: uma relação congelada no mesmo dia passava ou
    falhava por causa de um horário que a fonte nunca disse. O limite inferior verdadeiro de uma
    data é o **início do dia**, e é ele que se devolve.

    A consequência é deliberada e conservadora: para provar precedência, a relação precisa ter sido
    congelada **antes do dia** da extração. Onde a fonte publicar o horário, o limite inferior é o
    próprio horário e a garantia fica mais apertada — sem que nada aqui mude de forma.
    """
    from datetime import datetime, time

    from django.utils.dateparse import parse_date, parse_datetime

    bruto = corpo.get("dataApuracao") or corpo.get("data") or ""
    if not bruto:
        return None
    instante = parse_datetime(str(bruto))
    if instante is None:
        dia = parse_date(str(bruto)) or _dia_brasileiro(str(bruto))
        if dia is None:
            return None
        instante = datetime.combine(dia, time.min)
    if timezone.is_naive(instante):
        instante = timezone.make_aware(instante, ZONA)
    return instante


def _dia_brasileiro(texto):
    from datetime import datetime

    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None


class FonteDeTeste(FonteExterna):
    """Falso de teste, declarado no código de produção e usado só por configuração.

    Mora aqui, e não no diretório de testes, porque é o `settings` que o seleciona: um falso que só
    existisse sob `tests/` não poderia ser apontado por variável de ambiente, e o roteiro do
    `quickstart.md` não teria como rodar sem rede.
    """

    MATERIAL = {"indisponivel": ""}
    # Devolve o instante corrente, que uma fonte com horário diria de uma extração recém-publicada.
    PUBLICA_SO_A_DATA = False

    # **A conferência por tabela, sem rede** (116, FR-3650): é o que deixa ver as três mensagens em
    # desenvolvimento. A forma continua a de hoje (`None`, FR-3625), e por isso o último é o próprio
    # 5000, e não o 6114 da Caixa: a suíte declara `5900`, `5901` e `6113` com esta fonte, e com o
    # 6114 a tabela diria "ainda não realizado, −1 concurso adiante" do 6113. Com o 5000 a tabela é
    # coerente com a regra — menor ou igual ao último é realizado —, e só o 9998 foge dela, de
    # propósito, para reproduzir a advertência.
    SABE_CONFERIR = True
    ULTIMO = conferencia.UltimoConcurso(numero=5000, em=date(2015, 8, 26), proximo=5001)
    REALIZADAS = {5000: date(2015, 8, 26)}
    INCONCLUSIVA = "9998"

    def conferir_referencias(self, referencias, *, fonte, agora):
        import re

        situacoes = {}
        for referencia in referencias:
            if str(referencia) == self.INCONCLUSIVA:
                situacoes[referencia] = conferencia.inconclusiva(
                    fonte=fonte,
                    referencia=referencia,
                    consultada_em=agora,
                    motivo=conferencia.SEM_RESPOSTA_A_TEMPO,
                )
                continue
            # A forma é livre aqui: "Concurso 5900" é o 5900, pelo número final que a regra de
            # substituição também lê.
            final = re.search(r"(\d+)$", str(referencia))
            numero = int(final.group(1)) if final else None
            realizada = numero is not None and numero <= self.ULTIMO.numero
            situacoes[referencia] = conferencia.Situacao(
                conferencia.REALIZADO if realizada else conferencia.AINDA_NAO_REALIZADO,
                fonte,
                str(referencia),
                agora,
                ultimo=self.ULTIMO.numero,
                ultimo_em=self.ULTIMO.em,
                realizada_em=self.REALIZADAS.get(numero) if realizada else None,
                proximo=self.ULTIMO.proximo,
            )
        return situacoes

    def observar(self, *, fonte, referencia):
        material = self.MATERIAL.get(str(referencia), "12345 67890 11223 44556 77889")
        if not material:
            return Observacao(
                indisponivel=True,
                evidencia=f"Concurso {referencia} de {fonte}: sem extração publicada.",
            )
        # O falso reporta o limite inferior como **agora**, que é o que uma fonte real diria de uma
        # extração recém-publicada com horário. Sem isso ele não serviria para semear sorteio, e o
        # teste estaria exercitando um caminho que a produção recusa.
        return Observacao(material_bruto=material, ocorrida_nao_antes_de=timezone.now())


class FonteDeTesteSoData(FonteDeTeste):
    """O falso que publica só a data, como a Caixa (102, FR-2665, D-007).

    **Por que existe.** A `FonteDeTeste` responde "agora", e com ela todo congelamento é anterior à
    ocorrência, inclusive no mesmo dia: a recusa do Edital 72/2026 nunca aparecia em
    desenvolvimento. Esta devolve o **início do dia corrente**, que é o que a Loteria Federal
    devolve para a extração publicada hoje. Por construção, uma relação congelada hoje é sempre
    recusada com ela, e uma congelada ontem sorteia — o roteiro local mostra os dois sem rede.

    Ela não lê o `occurrenceAt` declarado, e é de propósito: levar o instante declarado ao
    adaptador mudaria a porta inteira por causa de um falso.
    """

    PUBLICA_SO_A_DATA = True

    def observar(self, *, fonte, referencia):
        from datetime import datetime, time

        observacao = super().observar(fonte=fonte, referencia=referencia)
        if observacao.indisponivel:
            return observacao
        hoje = timezone.localdate(timezone.now(), ZONA)
        return Observacao(
            material_bruto=observacao.material_bruto,
            ocorrida_nao_antes_de=datetime.combine(hoje, time.min, tzinfo=ZONA),
        )
