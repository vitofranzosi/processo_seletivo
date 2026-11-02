"""A peça dos cenários de referência, pelo fluxo real, contra o SVG versionado (111, D-016, T026).

**Mudar o template muda os arquivos**, e o diff de `tests/fixtures/kit_referencias/` é o que a
revisão olha: cada texto numa linha, com o campo e a posição. Para regerar, depois de conferir a
mudança: `KIT_REGERAR_REFERENCIAS=1`, e o teste reescreve os arquivos e falha, para o diff não
passar calado.

**As datas voltam ao calendário do corpus.** O corpus é publicado a partir de hoje, deslocado em
dias inteiros, e as datas da ficha andam a cada dia. Normalizá-las no SVG não bastaria: na virada do
ano o período passa a escrever o ano duas vezes, e o corpo dele muda. A ficha lida recebe de volta
as datas do corpus, fixas, e o resto da composição é a do fluxo real.

**O que é sorteado sai antes da comparação**: a referência da impressão e o campo da oferta levam a
identidade dos Perfis. A marca é binária, e o resumo dela já é conferido em `test_peca.py`.

O teste geométrico (FR-3429) roda nos mesmos cenários.
"""

import dataclasses
import os
import re
from pathlib import Path

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.interface import kit_peca
from processo_seletivo.portal import ficha as fichas
from tests.fixtures import kit
from tests.unit.kit import geometria

pytestmark = pytest.mark.django_db

PASTA = Path(__file__).resolve().parents[2] / "fixtures" / "kit_referencias"
CENARIOS = {
    "91-quatro-polos": ("91", 1, None),
    "91-prorrogado": ("91", 2, None),
    "01-cadastro-reserva": ("01", 1, None),
    "92-titulo-longo": ("92", 1, None),
    "91-sem-localidade": ("91", 1, kit.sem_localidade),
    "91-um-perfil": ("91", 1, kit.so_um_perfil),
    "91-neutro": ("91", None, kit.sem_periodo),
}


VIGENCIA = "08/10/2026, 12h00"


def no_calendario_do_corpus(ficha):
    """A ficha com as datas do corpus, sem o deslocamento até hoje: as horas são as mesmas."""
    menos = kit.deslocamento()

    def instante(iso):
        return parse_datetime(iso) - menos if iso else None

    inicio, fim = instante(ficha.inicio), instante(ficha.fim)
    return dataclasses.replace(
        ficha,
        inicio_data=fichas._data(inicio),
        inicio_hora=fichas._hora(inicio),
        fim_data=fichas._data(fim),
        fim_hora=fichas._hora(fim),
        periodo_curto=fichas._periodo_curto(inicio, fim),
        # A vigência é o instante da publicação no teste, e não data do corpus: sem deslocamento que
        # a devolva, ela fica fixa, ou o selo mudaria de dia conforme a hora em que a suíte roda.
        versao_desde_texto=VIGENCIA,
    )


def normalizar(svg):
    svg = re.sub(r"ref\. [0-9a-f]{8}", "ref. IMPRESSAO", svg)
    svg = re.sub(r"data:image/png;base64,[A-Za-z0-9+/=]+", "data:image/png;base64,MARCA", svg)
    # Os campos da oferta levam a identidade do Perfil, sorteada a cada publicação.
    svg = re.sub(r"(oferta_(?:rotulo|quantidade)):[0-9a-f-]{36}", r"\1:PERFIL", svg)
    return svg.replace("><", ">\n<") + "\n"


@pytest.mark.parametrize("nome", CENARIOS)
def test_a_peca_do_cenario_e_a_referencia(api_client, nome):
    corpus, ate, mudar = CENARIOS[nome]
    edital = kit.publicar(api_client, corpus, ate=ate, mudar=mudar, chave=f"referencia-{nome}")
    ficha = no_calendario_do_corpus(fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE))
    peca = kit_peca.compor(ficha)

    assert geometria.problemas(peca) == []
    obtido = normalizar(kit_peca.svg(peca, ficha))
    arquivo = PASTA / f"{nome}.svg"
    if os.environ.get("KIT_REGERAR_REFERENCIAS") == "1":
        arquivo.write_text(obtido, encoding="utf-8")
        pytest.fail(f"Referência regerada: {arquivo.name}. Confira o diff e rode de novo.")
    assert arquivo.exists(), f"Falta a referência {arquivo.name}: KIT_REGERAR_REFERENCIAS=1"
    assert obtido == arquivo.read_text(encoding="utf-8")
