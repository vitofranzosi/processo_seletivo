"""O que a família UAB/bolsista tem de seu (119, T049).

As regras comuns — período, número, busca, chamada à ação, selo, título omitido, geometria — rodam
nela pelo registro, em `test_peca_das_familias.py`. Aqui fica só o que a distingue das outras: a
chamada fixa "Seleção de bolsista", desenhada direto no fundo, sem painel de cor nem balão, e a
peça sem vagas.
"""

import pytest

from processo_seletivo.interface import kit_peca
from processo_seletivo.interface.kit_familias import uab
from processo_seletivo.interface.kit_peca import Figura, Retangulo
from tests.unit.kit import geometria
from tests.unit.kit.test_peca_das_familias import _campo, _uma

TEMPLATES = list(uab.FAMILIA.templates.values())


def _compor(template, imagem="atendente", **mudar):
    peca = kit_peca.compor_template(_uma(**mudar), template, kit_peca.Escolha(imagem=imagem))
    assert geometria.problemas(peca) == [], template.identificador
    return peca


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.identificador)
def test_a_chamada_aprovada_sai_em_duas_cores_e_no_alternativo(template):
    peca = _compor(template)
    chamada = [t for t in peca.textos if t.campo == "chamada"]
    assert [t.conteudo for t in chamada] == ["SELEÇÃO DE", "BOLSISTA"]
    assert [t.cor for t in chamada] == [uab.PALETA["marrom"], uab.PALETA["magenta"]]
    assert all(t.fonte == "anton-regular" for t in chamada)
    assert "Seleção de bolsista." in peca.alternativo


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.identificador)
def test_sem_painel_de_cor_sem_balao_e_sem_vagas(template):
    """O texto fica direto no fundo, como nos slides; a única figura é a imagem do banco."""
    peca = _compor(template)
    assert not [e for e in peca.elementos if isinstance(e, Retangulo)]
    assert [e.campo for e in peca.elementos if isinstance(e, Figura)] == ["imagem"]
    assert "vagas" not in " ".join(t.conteudo for t in peca.textos)
    assert _campo(peca, "chamada_a_acao") == template.formato.chamada_a_acao


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda t: t.identificador)
def test_o_pior_caso_da_pilha_cabe(template):
    """Prorrogado, término, hora e início no maior corpo: a pilha não recai de corpo pela altura."""
    peca = _compor(template, imagem="escritorio", prorrogado=True)
    assert _campo(peca, "fixo") == "PRAZO PRORROGADO"
    assert _campo(peca, "inicio")
