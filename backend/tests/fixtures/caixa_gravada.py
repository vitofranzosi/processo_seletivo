"""A Caixa da suíte: a conferência da referência sem rede (116, FR-3651, SC-1099).

**Por que o padrão não é a Caixa gravada.** Em 03/11/2026 o último concurso realizado era o 6114, e
a suíte declara `5900`, `5901` e `6113` em dezenas de casos que nada têm com esta feature — o Edital
72/2026, os métodos de exemplo. Com a gravação no padrão, todos eles passariam a ser recusados por
"concurso já realizado", e a suíte mediria a fixture. O padrão é, por isso, o **concurso 1, de
15/09/1962**, que é verdadeiro (`caixa/federal_1.json`) e anterior a toda referência que a suíte
declara: toda conferência responde "ainda não realizado", que é o que a FR-3651 pede. Quem testa a
conferência pede a gravação, ou outra situação, explicitamente.

**Duas camadas.** `consultar_ultimo` e `consultar_data` do adaptador são substituídos, e contam as
chamadas — a carga é requisito (FR-3631). E `urlopen` para `caixa.gov.br` é recusado, para o caso
que restaurar o adaptador real sem dizer o que ele vai responder: um caso esquecido iria à rede.
"""

import json
import os
import pathlib
import urllib.request
from datetime import date
from urllib.parse import urlsplit

import pytest

from processo_seletivo.sorteios.domain import conferencia as dominio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import LoteriaFederal

PASTA = pathlib.Path(__file__).parent / "caixa"
FONTE_REAL = "SORTEIO_E2E_FONTE_REAL"


def gravada(nome):
    """A resposta gravada em 03/11/2026: `{"status": ..., "corpo": ...}`."""
    return json.loads((PASTA / f"federal_{nome}.json").read_text(encoding="utf-8"))


def _dia(texto):
    dia, mes, ano = (int(parte) for parte in texto.split("/"))
    return date(ano, mes, dia)


PRIMEIRO = dominio.UltimoConcurso(numero=1, em=date(1962, 9, 15), proximo=2)


class CaixaDaSuite:
    """O que a conferência ouve da Loteria Federal enquanto o caso roda."""

    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._metodos = pytest.MonkeyPatch()
        self.ultimo = PRIMEIRO
        self.motivo = ""
        self.datas = {1: PRIMEIRO.em}
        self.chamadas_ao_ultimo = 0
        self.chamadas_por_numero = []

    # --- o que ela responde ------------------------------------------------------------------

    def usar_gravacao(self):
        """A Caixa de 03/11/2026: último 6114, de 01/11/2026, e as datas das respostas 200."""
        corpo = gravada("ultimo")["corpo"]
        self.ultimo = dominio.UltimoConcurso(
            numero=corpo["numero"],
            em=_dia(corpo["dataApuracao"]),
            proximo=corpo["numeroConcursoProximo"],
        )
        self.motivo = ""
        for arquivo in PASTA.glob("federal_*.json"):
            resposta = json.loads(arquivo.read_text(encoding="utf-8"))
            if resposta["status"] == 200:
                self.datas[resposta["corpo"]["numero"]] = _dia(resposta["corpo"]["dataApuracao"])
        return self

    def realizado_ate(self, numero, em, *, proximo=None):
        """A Caixa passa a registrar `numero` como o último realizado (cenários C e H)."""
        self.ultimo = dominio.UltimoConcurso(numero=numero, em=em, proximo=proximo)
        self.datas[numero] = em
        self.motivo = ""
        return self

    def fora_do_ar(self, motivo=dominio.SEM_RESPOSTA_A_TEMPO):
        self.ultimo = None
        self.motivo = motivo
        return self

    @property
    def chamadas(self):
        return self.chamadas_ao_ultimo + len(self.chamadas_por_numero)

    # --- a substituição ----------------------------------------------------------------------

    def instalar(self):
        caixa = self

        def consultar_ultimo(_adaptador):
            caixa.chamadas_ao_ultimo += 1
            return dominio.ConsultaDoUltimo(caixa.ultimo, caixa.motivo)

        def consultar_data(_adaptador, numero):
            caixa.chamadas_por_numero.append(numero)
            return caixa.datas.get(numero)

        self._metodos.setattr(LoteriaFederal, "consultar_ultimo", consultar_ultimo)
        self._metodos.setattr(LoteriaFederal, "consultar_data", consultar_data)
        if not os.environ.get(FONTE_REAL):
            self._monkeypatch.setattr(urllib.request, "urlopen", _vigiado(urllib.request.urlopen))
        return self

    def pela_rede(self, urlopen=None):
        """O adaptador real de volta, com `urlopen` substituído — ou recusado, sem ele.

        É o que os casos de falha de acesso usam: o parse do adaptador e a classificação dos motivos
        rodam de verdade, sobre as respostas gravadas, e nada sai da máquina.
        """
        self._metodos.undo()
        if urlopen is not None:
            self._monkeypatch.setattr(urllib.request, "urlopen", urlopen)
        return self

    def desinstalar(self):
        self._metodos.undo()


def _vigiado(original):
    def urlopen(url, *args, **kwargs):
        endereco = url.full_url if isinstance(url, urllib.request.Request) else str(url)
        if (urlsplit(endereco).hostname or "").endswith("caixa.gov.br"):
            # `pytest.fail` e não uma exceção comum: o adaptador captura as de rede e as
            # transformaria em "inconclusivo", e o caso esquecido passaria verde.
            pytest.fail(
                f"A suíte não chama a Caixa (FR-3651): {endereco}. Peça a situação ao `caixa` "
                f"do conftest, ou ligue {FONTE_REAL}=1 para o E2E contra a fonte real.",
                pytrace=False,
            )
        return original(url, *args, **kwargs)

    return urlopen
