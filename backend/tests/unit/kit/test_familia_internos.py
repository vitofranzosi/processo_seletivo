"""O que é só da família Internos (119, T051, EC-19, cenário 23).

As regras gerais dos templates rodam nela pelo registro (`test_peca_das_familias.py`,
`test_familias.py`, `test_referencias.py`); aqui fica o que a declaração dela tem de próprio: as
duas variantes, cuja chamada é a única diferença de texto, e a recusa da variante fora da lista.
"""

import pytest

from processo_seletivo.interface import kit_peca
from processo_seletivo.interface.kit_familias import internos
from tests.unit.kit import geometria
from tests.unit.kit.test_peca_das_familias import _uma

TEMPLATES = [internos.POST, internos.STORY, internos.BANNER]


def _compor(template, variante, imagem="servidores", ficha=None):
    escolha = kit_peca.Escolha(variante=variante, imagem=imagem)
    peca = kit_peca.compor_template(ficha or _uma(), template, escolha)
    assert geometria.problemas(peca) == [], template.identificador
    return peca


def _sem_a_chamada(peca):
    return [(t.campo, t.conteudo, t.x, t.y) for t in peca.textos if t.campo != "chamada"]


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
def test_a_variante_muda_so_a_chamada(template):
    """EC-19: a chamada fixa é a única diferença de texto, e o resto fica no mesmo lugar."""
    servidores = _compor(template, "servidores")
    estudantes = _compor(template, "estudantes")
    assert [t.conteudo for t in servidores.textos if t.campo == "chamada"] == [
        "Seleção para servidores"
    ]
    assert [t.conteudo for t in estudantes.textos if t.campo == "chamada"] == [
        "Seleção para estudantes"
    ]
    assert _sem_a_chamada(servidores) == _sem_a_chamada(estudantes)
    assert "Seleção para servidores." in servidores.alternativo
    assert "Seleção para estudantes." in estudantes.alternativo


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
@pytest.mark.parametrize("variante", [None, "alunos", "pos-lato-sensu"])
def test_variante_ausente_ou_fora_da_lista_e_recusada(template, variante):
    """EC-9: a família com variantes não tem uma padrão, e o motor não escolhe por quem gera."""
    with pytest.raises(kit_peca.EscolhaInvalida, match="variante"):
        kit_peca.compor_template(
            _uma(), template, kit_peca.Escolha(variante=variante, imagem="servidores")
        )


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
def test_variante_e_imagem_se_escolhem_em_separado(template):
    """A foto não amarra o público: a variante dos servidores sai com a arte dos estudantes."""
    peca = _compor(template, "servidores", imagem="estudantes")
    chamada = [t.conteudo for t in peca.textos if t.campo == "chamada"]
    assert chamada == ["Seleção para servidores"]
    assert internos.IMAGENS[1].descricao in peca.alternativo


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.formato.chave)
def test_tudo_em_branco_alinhado_a_esquerda_e_sem_ofertas(template):
    """Os slides de orientação: "Mantenha alinhado à esquerda"; e os slides não trazem vagas."""
    peca = _compor(template, "estudantes")
    assert {t.cor for t in peca.textos} == {internos.PALETA["branco"]}
    assert {t.ancora for t in peca.textos} == {"start"}
    assert not template.tem_ofertas
    por_campo = {t.campo: t for t in peca.textos}
    assert por_campo["identificacao"].fonte == "unbounded-negrito"
    assert por_campo["periodo_curto"].fonte == "unbounded-negrito"
    assert por_campo["chamada"].fonte == "unbounded-regular"
    assert por_campo["hora"].fonte == "inter-regular"


def test_as_familias_sem_variante_ignoram_a_escolha_dela():
    """O motor só lê a variante onde a família as declara: as outras não mudam de desenho."""
    from processo_seletivo.interface.kit_familias import libras

    sem = kit_peca.compor_template(_uma(), libras.POST, kit_peca.Escolha(imagem="grupo"))
    com = kit_peca.compor_template(
        _uma(), libras.POST, kit_peca.Escolha(imagem="grupo", variante="servidores")
    )
    assert kit_peca.svg(sem, _uma()) == kit_peca.svg(com, _uma())
