"""A tabela-verdade da deliberação e as frases da regra (165, research T-007).

Função pura sobre a Etapa do conteúdo publicado: três e cinco pareceres, todas as combinações, as
três regras (SC-2351).
"""

from itertools import product
from uuid import uuid4

import pytest

from processo_seletivo.resultados.domain import deliberacao as d

F, D = "FAVORAVEL", "DESFAVORAVEL"


def _etapa(**campos):
    return {
        "id": "e1",
        "name": "Heteroidentificação",
        "order": 2,
        "eliminatory": True,
        "forma": "DECISORIA",
        "evaluationsPerRegistration": 3,
        "rotuloFavoravel": "Deferido",
        "rotuloDesfavoravel": "Indeferido",
        "deliberationRule": "MAJORITY",
        **campos,
    }


def _esperado(regra, sentidos):
    favoraveis = sentidos.count(F)
    if regra == d.MAIORIA:
        return F if favoraveis > len(sentidos) / 2 else D
    if regra == d.UNANIMIDADE_PARA_O_FAVORAVEL:
        return F if favoraveis == len(sentidos) else D
    return D if favoraveis == 0 else F


@pytest.mark.parametrize("regra", d.REGRAS)
@pytest.mark.parametrize("n", [3, 5])
def test_a_tabela_verdade_inteira(regra, n):
    """SC-2351: toda combinação de sentidos, para três e para cinco pareceres."""
    for sentidos in product((F, D), repeat=n):
        assert d.deliberar(regra, sentidos) == _esperado(regra, list(sentidos)), sentidos


def test_dois_indeferidos_e_um_deferido_nas_tres_regras():
    """O exemplo da spec (US3): os mesmos pareceres, três desfechos."""
    sentidos = (D, D, F)
    assert d.deliberar(d.MAIORIA, sentidos) == D
    assert d.deliberar(d.UNANIMIDADE_PARA_O_FAVORAVEL, sentidos) == D
    assert d.deliberar(d.UNANIMIDADE_PARA_O_DESFAVORAVEL, sentidos) == F


def test_regra_desconhecida_nao_delibera():
    with pytest.raises(ValueError):
        d.deliberar("SORTEIO", (F, D, F))


def test_a_grafia_publicada_vai_e_volta():
    for regra in d.REGRAS:
        assert d.para_coluna(d.da_coluna(regra)) == regra
    assert d.da_coluna("") is None
    assert d.para_coluna(None) == ""
    assert d.para_coluna("QUALQUER") == ""


def test_colegiada_exige_decisoria_varias_e_regra():
    assert d.colegiada(_etapa())
    assert not d.colegiada(_etapa(deliberationRule=None))
    assert not d.colegiada(_etapa(evaluationsPerRegistration=1))
    assert not d.colegiada(_etapa(forma="PONTUADA"))
    assert not d.colegiada(_etapa(deliberationRule="LIXO"))


def test_publicar_so_na_decisoria_com_varias():
    """T-002: a regra escrita na pontuada ou na de uma avaliação não é gravada."""
    assert d.publicar(_etapa(), d.MAIORIA) == {"deliberationRule": "MAJORITY"}
    assert d.publicar(_etapa(), "") == {"deliberationRule": None}
    assert d.publicar(_etapa(forma="PONTUADA"), d.MAIORIA) == {"deliberationRule": None}
    assert d.publicar(_etapa(evaluationsPerRegistration=1), d.MAIORIA) == {"deliberationRule": None}


def test_o_motivo_da_maioria():
    """FR-7066, com o exemplo da própria spec."""
    deliberacao = d.Deliberacao(regra=d.MAIORIA, sentidos=(D, D, F))
    assert d.motivo(_etapa(), deliberacao) == (
        "a comissão deliberou Indeferido por maioria: 2 de 3 pareceres Indeferido"
    )


def test_o_motivo_da_unanimidade_que_se_cumpre():
    deliberacao = d.Deliberacao(regra=d.UNANIMIDADE_PARA_O_DESFAVORAVEL, sentidos=(D, D, D))
    assert d.motivo(_etapa(), deliberacao) == (
        "a comissão deliberou Indeferido por unanimidade: 3 de 3 pareceres Indeferido"
    )


def test_o_motivo_da_unanimidade_que_falta():
    """Sob "confirma só por unanimidade", dois Deferido e um Indeferido dão Indeferido."""
    deliberacao = d.Deliberacao(regra=d.UNANIMIDADE_PARA_O_FAVORAVEL, sentidos=(F, F, D))
    assert d.motivo(_etapa(), deliberacao) == (
        "a comissão deliberou Indeferido por não haver unanimidade Deferido: "
        "1 de 3 pareceres Indeferido"
    )


def test_o_motivo_sem_rotulos():
    deliberacao = d.Deliberacao(regra=d.MAIORIA, sentidos=(F, F, D))
    etapa = _etapa(rotuloFavoravel=None, rotuloDesfavoravel=None)
    assert d.motivo(etapa, deliberacao) == (
        "a comissão deliberou favorável por maioria: 2 de 3 pareceres favorável"
    )


def test_o_motivo_nunca_nomeia_quem_deu_o_parecer():
    """Os pareceres viajam como identidades; o motivo não tem por onde carregar autoria."""
    ids = tuple(str(uuid4()) for _ in range(3))
    deliberacao = d.Deliberacao(regra=d.MAIORIA, sentidos=(D, D, F), pareceres=ids)
    motivo = d.motivo(_etapa(), deliberacao)
    assert not any(identidade in motivo for identidade in ids)


def test_a_deliberacao_se_le_como_conclusao():
    deliberacao = d.Deliberacao(regra=d.MAIORIA, sentidos=(D, F, F))
    assert deliberacao.forma == "DECISORIA"
    assert deliberacao.pontuacao is None
    assert deliberacao.sentido == F
    assert (deliberacao.favoraveis, deliberacao.desfavoraveis) == (2, 1)


def test_a_linha_da_conferencia():
    """UX-752."""
    deliberacao = d.Deliberacao(regra=d.MAIORIA, sentidos=(D, D, F))
    assert d.linha_da_conferencia(_etapa(), deliberacao) == (
        "Indeferido — 2 de 3 pareceres Indeferido, por maioria"
    )


@pytest.mark.parametrize(
    "publicada, trecho",
    [
        ("MAJORITY", "O resultado é «Deferido» quando a maioria dos pareceres é «Deferido»"),
        ("UNANIMOUS_FOR_FAVORABLE", "O resultado é «Deferido» só quando todos os pareceres"),
        ("UNANIMOUS_FOR_UNFAVORABLE", "O resultado é «Indeferido» só quando todos os pareceres"),
    ],
)
def test_a_frase_do_documento(publicada, trecho):
    """FR-7075."""
    frase = d.frase_da_regra(_etapa(deliberationRule=publicada))
    assert frase.startswith("Cada inscrição recebe 3 pareceres, registrados por membros da")
    assert trecho in frase


def test_sem_regra_nao_ha_frase():
    """SC-2350: a frase vazia é o que recompõe o acervo."""
    assert d.frase_da_regra(_etapa(deliberationRule=None)) == ""
    assert d.frase_da_regra(_etapa(evaluationsPerRegistration=1)) == ""
    assert d.frase_da_regra({}) == ""


def test_as_opcoes_da_composicao():
    """UX-750: escritas com os rótulos digitados."""
    opcoes = dict(d.opcoes_da_regra("Deferido", "Indeferido"))
    assert (
        opcoes["MAJORITY"] == "Resultado «Deferido» quando a maioria dos pareceres for «Deferido»"
    )
    assert opcoes["UNANIMOUS_FOR_UNFAVORABLE"] == (
        "Resultado «Indeferido» só quando todos os pareceres forem «Indeferido»"
    )
    sem_rotulo = dict(d.opcoes_da_regra())
    assert sem_rotulo["MAJORITY"] == (
        "Resultado favorável quando a maioria dos pareceres for favorável"
    )
