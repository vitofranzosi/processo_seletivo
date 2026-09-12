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
from urllib import error, request

from django.conf import settings
from django.utils import timezone

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.infrastructure.fontes import FonteExterna, Observacao

ENDERECO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal/{referencia}"


class LoteriaFederal(FonteExterna):
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
        acesso = ""
        resposta_da_fonte = ""
        for _ in range(tentativas):
            try:
                with request.urlopen(
                    ENDERECO.format(referencia=referencia), timeout=limite
                ) as resposta:
                    corpo = json.loads(resposta.read().decode("utf-8"))
            except (error.URLError, TimeoutError, ValueError) as falha:
                acesso = f"{type(falha).__name__}: {falha}"
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
        return Observacao(
            falha_de_acesso=True,
            evidencia=(
                f"Concurso {referencia} de {fonte}: não foi possível falar com a fonte em "
                f"{tentativas} tentativa(s). Última falha: {acesso}"
            ),
        )


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
