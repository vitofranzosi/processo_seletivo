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

from processo_seletivo.sorteios.infrastructure.fontes import FonteExterna, Observacao

ENDERECO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal/{referencia}"


class LoteriaFederal(FonteExterna):
    def observar(self, *, fonte, referencia):
        tentativas = max(int(getattr(settings, "SORTEIO_FONTE_TENTATIVAS", 3)), 1)
        limite = float(getattr(settings, "SORTEIO_FONTE_TIMEOUT_SEGUNDOS", 10))
        ultima = ""
        for _ in range(tentativas):
            try:
                with request.urlopen(
                    ENDERECO.format(referencia=referencia), timeout=limite
                ) as resposta:
                    corpo = json.loads(resposta.read().decode("utf-8"))
            except (error.URLError, TimeoutError, ValueError) as falha:
                ultima = f"{type(falha).__name__}: {falha}"
                continue
            premios = corpo.get("listaDezenas") or corpo.get("listaRateioPremio") or []
            material = " ".join(str(item) for item in premios if str(item).strip())
            if material:
                return Observacao(material_bruto=material)
            ultima = "A fonte respondeu sem os números da extração."
        return Observacao(
            indisponivel=True,
            evidencia=(
                f"Concurso {referencia} de {fonte}: a fonte não devolveu a extração em "
                f"{tentativas} tentativa(s). Última resposta: {ultima}"
            ),
        )


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
        return Observacao(material_bruto=material)
