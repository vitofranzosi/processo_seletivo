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

**A `119` generalizou o motor sem mudar estes arquivos** (FR-3804, SC-1133): a peça é a família
Institucional, composta pela declaração, e o identificador continua `feed-1080x1350 · 1`. Um diff
nesta pasta numa mudança do motor é regressão, e não referência a regerar.
"""

import dataclasses
import os
import re
from pathlib import Path

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.interface import kit_familias, kit_peca
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
    # No story o selo quebra em duas linhas, e a referência pode abrir a segunda.
    svg = re.sub(r'(data-campo="selo">(?:ref\. )?)[0-9a-f]{8}<', r"\1IMPRESSAO<", svg)
    svg = re.sub(r"data:image/png;base64,[A-Za-z0-9+/=]+", "data:image/png;base64,MARCA", svg)
    # A imagem do banco e o balão: o resumo deles é conferido em `test_familias.py`.
    svg = re.sub(r"data:image/jpeg;base64,[A-Za-z0-9+/=]+", "data:image/jpeg;base64,IMAGEM", svg)
    # Os campos da oferta levam a identidade do Perfil, sorteada a cada publicação.
    svg = re.sub(r"(oferta_(?:rotulo|quantidade)):[0-9a-f-]{36}", r"\1:PERFIL", svg)
    return svg.replace("><", ">\n<") + "\n"


@pytest.mark.parametrize("nome", CENARIOS)
def test_a_peca_do_cenario_e_a_referencia(api_client, nome):
    corpus, ate, mudar = CENARIOS[nome]
    edital = kit.publicar(api_client, corpus, ate=ate, mudar=mudar, chave=f"referencia-{nome}")
    ficha = no_calendario_do_corpus(fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE))
    peca = kit_peca.compor(ficha)
    # O motor generalizado, pela entrada geral e com o template lido do registro, desenha a mesma
    # peça que `compor` (119, FR-3804, SC-1133).
    template = kit_familias.template("institucional", "post")
    pela_declaracao = kit_peca.compor_template(ficha, template, kit_peca.Escolha())
    assert pela_declaracao.template.identificador == "feed-1080x1350 · 1" == kit_peca.TEMPLATE
    assert kit_peca.svg(pela_declaracao, ficha) == kit_peca.svg(peca, ficha)

    assert geometria.problemas(peca) == []
    obtido = normalizar(kit_peca.svg(peca, ficha))
    arquivo = PASTA / f"{nome}.svg"
    if os.environ.get("KIT_REGERAR_REFERENCIAS") == "1":
        arquivo.write_text(obtido, encoding="utf-8")
        pytest.fail(f"Referência regerada: {arquivo.name}. Confira o diff e rode de novo.")
    assert arquivo.exists(), f"Falta a referência {arquivo.name}: KIT_REGERAR_REFERENCIAS=1"
    assert obtido == arquivo.read_text(encoding="utf-8")


# ---- Os templates das famílias da comunicação (119, FR-3831, T041) -------------------------

#: Os cenários da `111` e o 17 da `119`, em todo template de família da comunicação.
CENARIOS_DAS_FAMILIAS = {**CENARIOS, "17-lato-uma-oferta": ("91", 1, kit.lato_uma_oferta)}
TEMPLATES_DAS_FAMILIAS = [
    template for template in kit_familias.templates() if template.familia != "institucional"
]


def _comparar(arquivo, obtido):
    if os.environ.get("KIT_REGERAR_REFERENCIAS") == "1":
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        for velho in arquivo.parent.glob(f"{arquivo.stem}.*"):
            velho.unlink()
        arquivo.write_text(obtido, encoding="utf-8")
        return f"Referência regerada: {arquivo.relative_to(PASTA)}."
    assert arquivo.exists(), f"Falta a referência {arquivo.relative_to(PASTA)}"
    assert obtido == arquivo.read_text(encoding="utf-8"), arquivo.name
    return ""


@pytest.mark.parametrize("nome", CENARIOS_DAS_FAMILIAS)
def test_a_peca_de_cada_template_das_familias_e_a_referencia(api_client, nome):
    """A peça, ou a recusa com o motivo, de cada template no cenário (SC-1132, SC-1134).

    A imagem é a primeira do banco: a peça muda de fundo com a escolha, e de mais nada.
    """
    corpus, ate, mudar = CENARIOS_DAS_FAMILIAS[nome]
    edital = kit.publicar(api_client, corpus, ate=ate, mudar=mudar, chave=f"familias-{nome}")
    ficha = no_calendario_do_corpus(fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE))
    regeradas = []
    for template in TEMPLATES_DAS_FAMILIAS:
        familia = kit_familias.familia(template.familia)
        escolha = kit_peca.Escolha(imagem=familia.imagens[0].chave if familia.imagens else None)
        pasta = PASTA / template.pasta_das_referencias
        try:
            peca = kit_peca.compor_template(ficha, template, escolha)
        except kit_peca.PecaRecusada as recusa:
            regeradas.append(_comparar(pasta / f"{nome}.recusa", recusa.motivo + "\n"))
            continue
        assert geometria.problemas(peca) == [], template.identificador
        regeradas.append(_comparar(pasta / f"{nome}.svg", normalizar(kit_peca.svg(peca, ficha))))
    if any(regeradas):
        pytest.fail(" ".join(filter(None, regeradas)) + " Confira o diff e rode de novo.")
