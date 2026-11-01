"""O que o kit de divulgação não diz, lido do material **gerado** (111, FR-3414, FR-3416, D-017).

A varredura não lê módulo nem template: a frase nasce da combinação de forma fixa com valor, e só o
material composto mostra o que sai. Ela roda nos cenários de referência, pelo fluxo real.

**Valor oficial literal não reprova** (EC-26). O título, o nome do Perfil e a localidade entram como
o Edital os publicou. Um "São Marcos" ou uma "faixa etária" ficam, e a conferência os aponta. Por
isso os literais saem do texto antes da varredura, e o que sobra é o que o kit escreveu.
"""

import re
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.interface import kit_textos
from processo_seletivo.portal import ficha as fichas
from tests.fixtures import kit
from tests.portal.test_acompanhamento_pela_situacao import PROIBIDAS

pytestmark = pytest.mark.django_db


def _sem_literais(texto, ficha):
    literais = [ficha.titulo, ficha.titulo_sem_numero, ficha.titulo_do_processo]
    literais += [oferta.nome for oferta in ficha.ofertas]
    literais += [oferta.localidade for oferta in ficha.ofertas]
    for literal in sorted(filter(None, literais), key=len, reverse=True):
        texto = texto.replace(literal, "«valor»")
    return texto


def _material(ficha):
    textos = kit_textos.compor(ficha)
    notas = kit_textos.notas_para_quem_divulga(ficha)
    return "\n".join([*textos.values(), *notas])


def _proibicoes(texto):
    achados = fichas.termos_proibidos(texto)
    achados += [padrao for padrao in PROIBIDAS if re.search(padrao, texto)]
    return achados


@pytest.mark.parametrize(
    ("nome", "ate", "mudar", "dias"),
    [
        ("91", 1, None, 0),
        ("91", 1, None, 3),
        ("91", None, None, 3),
        ("01", 1, None, 0),
        ("92", 1, None, 0),
        ("91", None, kit.sem_localidade, 0),
        ("91", None, kit.so_um_perfil, 0),
    ],
)
def test_o_material_nao_diz_o_que_a_ficha_nao_comprova(api_client, nome, ate, mudar, dias):
    edital = kit.publicar(api_client, nome, ate=ate, mudar=mudar, chave=f"vocab-{nome}-{dias}")
    ficha = fichas.ler(edital, agora=timezone.now() + timedelta(days=dias), base_url=kit.BASE)
    assert ficha.modo == fichas.COM_PERIODO
    assert _proibicoes(_sem_literais(_material(ficha), ficha)) == []


def test_modo_neutro_sem_inscricao(api_client):
    edital = kit.publicar(api_client, chave="vocab-neutro", mudar=kit.sem_periodo)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE)
    textos = "\n".join(kit_textos.compor(ficha).values())
    assert ficha.modo == fichas.NEUTRO
    assert not re.search(r"inscri", _sem_literais(textos, ficha), re.IGNORECASE)


def test_valor_literal_nao_reprova(api_client):
    edital = kit.publicar(api_client, chave="vocab-termo", mudar=kit.termo_no_titulo)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE)
    material = _material(ficha)
    assert "São Marcos" in material
    assert ficha.termos_em_valor_oficial
    assert _proibicoes(_sem_literais(material, ficha)) == []


def test_as_frases_fixas_nao_tem_termo_proibido():
    fixas = [
        kit_textos.RESSALVA,
        kit_textos.CHAMADA_A_PAGINA,
        kit_textos.BUSCA,
        *kit_textos.TITULOS.values(),
    ]
    assert _proibicoes("\n".join(fixas)) == []
