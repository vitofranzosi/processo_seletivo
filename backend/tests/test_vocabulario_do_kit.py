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

from processo_seletivo.interface import kit_peca, kit_textos
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


def _texto_da_peca(ficha):
    """Os nós da peça, um campo por linha, e o texto alternativo (T027, FR-3414, FR-3416).

    As linhas de um mesmo campo voltam a ser uma frase: o título quebrado em três nós é o literal
    inteiro de novo, e `_sem_literais` o reconhece.
    """
    try:
        peca = kit_peca.compor(ficha)
    except kit_peca.PecaRecusada:
        return ""
    por_campo = {}
    for texto in peca.textos:
        por_campo.setdefault(texto.campo, []).append(texto.conteudo)
    return "\n".join([*(" ".join(partes) for partes in por_campo.values()), peca.alternativo])


def _material(ficha):
    textos = kit_textos.compor(ficha)
    notas = kit_textos.notas_para_quem_divulga(ficha)
    return "\n".join([*textos.values(), *notas, _texto_da_peca(ficha)])


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
    assert _texto_da_peca(ficha)
    assert _proibicoes(_sem_literais(_material(ficha), ficha)) == []


def test_modo_neutro_sem_inscricao(api_client):
    edital = kit.publicar(api_client, chave="vocab-neutro", mudar=kit.sem_periodo)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE)
    textos = "\n".join([*kit_textos.compor(ficha).values(), _texto_da_peca(ficha)])
    assert ficha.modo == fichas.NEUTRO
    assert _texto_da_peca(ficha)
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
        *kit_peca.FIXOS.values(),
        kit_peca.HORARIO,
        kit_peca.HOST_LOCAL,
        kit_peca.SEM_TITULO,
        kit_peca.ESCOLHA_A_MANCHETE,
        *(marca.descricao for marca in kit_peca.MARCAS.values()),
    ]
    assert _proibicoes("\n".join(fixas)) == []


# ---- As famílias da comunicação (119, FR-3814, D-013, SC-1131, EC-21) ----------------------

#: Os termos que a FR-3814 veda às frases fixas enquanto nenhum dado publicado os comprova (T-3).
VEDADOS_ATE_HAVER_DADO = (
    r"\binscrições abertas\b",
    r"\bgratuit[oa]s?\b",
    r"\ba distância\b",
    r"\bpresencia(?:l|is)\b",
    r"\bremanescentes?\b",
)


def _frases_das_familias(com_os_ativos=True):
    """Toda frase fixa de toda família registrada, lida do registro e não de uma lista literal.

    A descrição dos ativos fica fora da vedação da FR-3814: a da marca do Cefor é o nome oficial
    da unidade, "Centro de Referência em Formação e em Educação a Distância", e não afirmação de
    modalidade. Ela continua na lista da FR-3414.
    """
    from processo_seletivo.interface import kit_familias
    from processo_seletivo.interface.kit_formatos import FORMATOS

    for familia in kit_familias.REGISTRO.values():
        yield from (f"{familia.chave}: {frase}" for frase in familia.frases.values())
        yield from (f"{familia.chave}: {v.chamada}" for v in familia.variantes)
        yield from (f"{familia.chave}: {i.descricao}" for i in familia.imagens)
        if com_os_ativos:
            yield from (f"{familia.chave}: {a.descricao}" for a in familia.ativos.values())
    yield from (formato.chamada_a_acao for formato in FORMATOS.values())


def test_as_frases_de_todas_as_familias_passam_as_duas_listas():
    assert _proibicoes("\n".join(_frases_das_familias())) == []
    frases = "\n".join(_frases_das_familias(com_os_ativos=False))
    vedados = [p for p in VEDADOS_ATE_HAVER_DADO if re.search(p, frases, re.IGNORECASE)]
    assert vedados == []


def test_a_varredura_le_familia_nova_sem_lista(monkeypatch):
    """Uma família registrada depois desta suíte entra na varredura sozinha (D-013)."""
    import dataclasses

    from processo_seletivo.interface import kit_familias
    from processo_seletivo.interface.kit_familias import institucional

    nova = dataclasses.replace(institucional.FAMILIA, chave="tmd", frases={"x": "Curso gratuito"})
    monkeypatch.setitem(kit_familias.REGISTRO, "tmd", nova)
    frases = "\n".join(_frases_das_familias())
    assert any(re.search(p, frases, re.IGNORECASE) for p in VEDADOS_ATE_HAVER_DADO)


def _titulo_vedado(conteudo):
    conteudo["profiles"] = conteudo["profiles"][:1]
    conteudo["profiles"][0]["name"] = "Curso gratuito de Libras"
    conteudo["title"] = "Edital nº 91/2026 – Especialização a distância em Educação"
    kit._podar_referencias(conteudo)


def test_valor_oficial_com_termo_vedado_entra_literal_e_e_apontado(api_client):
    """EC-21: a vedação é das frases fixas, e não do que o Edital publicou."""
    from processo_seletivo.interface import kit_familias

    edital = kit.publicar(api_client, chave="vocab-ec21", mudar=_titulo_vedado)
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=kit.BASE)
    for template in kit_familias.familia("pos-lato-sensu").templates.values():
        peca = kit_peca.compor_template(
            ficha, template, kit_peca.Escolha(imagem="fone", manchete_texto=None)
        )
        desenhado = " ".join(t.conteudo for t in peca.textos)
        assert "Especialização a distância em Educação" in desenhado
        if template.tem_ofertas:
            assert "Curso gratuito de Libras" in desenhado
    textos = "\n".join(kit_textos.compor(ficha).values())
    assert "Curso gratuito de Libras" in textos
    apontados = " ".join(kit_textos.conferencia(ficha))
    assert "Especialização a distância em Educação" in apontados
