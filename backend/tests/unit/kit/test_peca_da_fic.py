"""O que é só da família FIC: a faixa da prorrogação, o contato e as ofertas com carga (119, T047).

As regras comuns a toda família — período, número, busca, selo, título, carga longa — rodam em
`test_peca_das_familias.py`, que já lê a FIC do registro. Aqui fica o desenho que a FIC declara e
as outras não: a prorrogação como faixa de ponta a ponta, e não item do painel; o "Dúvidas?" que sai
da peça quando não cabe (EC-4); e os cenários 18 e 19 sobre fichas montadas à mão.
"""

import dataclasses

import pytest

from processo_seletivo.interface import kit_peca, kit_textos
from processo_seletivo.interface.kit_familias import fic
from processo_seletivo.interface.kit_peca import Retangulo
from tests.unit.kit import geometria
from tests.unit.kit.test_textos import _ficha, _oferta

TEMPLATES = list(fic.FAMILIA.templates.values())
COM_CONTATO = [t for t in TEMPLATES if t.tem_contato]
ATENDIMENTO = "selecaoextensao.cefor@ifes.edu.br, (27) 3198-0925 (seg. a sex., das 8h às 16h)"


def _id(template):
    return template.identificador


def _tres(**mudar):
    """Cenário 18: três cursos, cada um com a carga horária publicada."""
    cursos = (
        ("Assistente Administrativo", 30, "180h"),
        ("Assistente de Secretaria Escolar", 30, "180h"),
        ("Inglês Básico", 40, "60h"),
    )
    ofertas = tuple(
        dataclasses.replace(_oferta(str(i), nome, "", vagas), carga_horaria=carga)
        for i, (nome, vagas, carga) in enumerate(cursos, start=1)
    )
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=100, **mudar)


def _compor(ficha, template, imagem="mesa"):
    peca = kit_peca.compor_template(ficha, template, kit_peca.Escolha(imagem=imagem))
    assert geometria.problemas(peca) == [], template.identificador
    return peca


def _campo(peca, campo):
    return " ".join(t.conteudo for t in peca.textos if t.campo == campo)


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_a_prorrogacao_e_a_faixa_de_ponta_a_ponta_e_nao_item_do_painel(template):
    sem = _compor(_tres(), template)
    com = _compor(_tres(prorrogado=True), template)
    faixa = template.dimensoes["faixa"]
    vermelho = fic.PALETA["vermelho"]
    assert not [e for e in sem.elementos if isinstance(e, Retangulo) and e.cor == vermelho]
    (desenhada,) = [e for e in com.elementos if isinstance(e, Retangulo) and e.cor == vermelho]
    assert desenhada.caixa[0] == 0 and desenhada.largura == template.formato.largura
    assert (desenhada.x, desenhada.y, desenhada.largura, desenhada.altura) == faixa["retangulo"]
    (selo,) = [t for t in com.textos if t.conteudo == fic.FRASES["prorrogado"]]
    assert selo.fundo == vermelho and geometria._dentro(selo.caixa, desenhada.caixa)
    # O resto da peça não se move: a faixa ocupa o alto, que o template deixa livre para ela.
    posicoes = {(t.campo, t.conteudo, t.x, t.y) for t in sem.textos}
    assert posicoes <= {(t.campo, t.conteudo, t.x, t.y) for t in com.textos}


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_sem_periodo_a_prorrogacao_nao_tem_faixa(template):
    from processo_seletivo.portal.ficha import NEUTRO

    neutro = _tres(modo=NEUTRO, inicio=None, fim=None, inicio_data="", fim_data="", prorrogado=True)
    peca = _compor(neutro, template)
    assert fic.FRASES["prorrogado"] not in " ".join(t.conteudo for t in peca.textos)


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_tres_ofertas_com_a_carga_horaria_de_cada_uma(template):
    """Cenário 18 (FR-3817): "Nome — carga: vagas", na ordem do Edital, nos três formatos."""
    peca = _compor(_tres(), template)
    assert [_campo(peca, f"oferta:{i}") for i in "123"] == [
        "Assistente Administrativo — 180h: 30 vagas",
        "Assistente de Secretaria Escolar — 180h: 30 vagas",
        "Inglês Básico — 60h: 40 vagas",
    ]
    assert _campo(peca, "total_de_vagas") == "100 vagas em 3 opções"


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_carga_vazia_numa_oferta_sai_so_o_nome(template):
    """Cenário 19 (EC-2): nada é completado na oferta que não declara a carga."""
    ficha = _tres()
    ofertas = (dataclasses.replace(ficha.ofertas[0], carga_horaria=""), *ficha.ofertas[1:])
    peca = _compor(dataclasses.replace(ficha, ofertas=ofertas), template)
    assert _campo(peca, "oferta:1") == "Assistente Administrativo: 30 vagas"


@pytest.mark.parametrize("template", COM_CONTATO, ids=_id)
def test_o_contato_da_ficha_sai_no_lugar_do_dos_slides(template):
    """US2, FR-3820: "Dúvidas? <canal>", e o texto alternativo o diz."""
    ficha = _tres(contato=ATENDIMENTO)
    peca = _compor(ficha, template)
    assert _campo(peca, "contato") == f"Dúvidas? {ATENDIMENTO}"
    assert ATENDIMENTO in peca.alternativo and not peca.avisos
    assert kit_textos.duvidas(ficha) in "\n".join(kit_textos.compor(ficha).values())


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_sem_atendimento_nenhum_contato_sai(template):
    """US2, cenário 2: nenhum outro canal substitui o que a unidade não declarou."""
    peca = _compor(_tres(contato=""), template)
    assert not _campo(peca, "contato") and "Dúvidas" not in peca.alternativo


@pytest.mark.parametrize("template", COM_CONTATO, ids=_id)
def test_atendimento_que_nao_cabe_sai_da_peca_e_a_tela_diz_o_formato(template):
    """EC-4, cenário 22: 255 caracteres não cabem; a peça sai sem ele, e com o aviso."""
    longo = ((ATENDIMENTO + " — ") * 4)[:255]
    peca = _compor(_tres(contato=longo), template)
    assert not _campo(peca, "contato")
    assert peca.avisos == (kit_peca.SEM_CONTATO_EM.format(formatos=template.formato.chave),)
    assert longo in "\n".join(kit_textos.compor(_tres(contato=longo)).values())


def test_o_banner_nao_tem_contato_como_o_slide_do_site():
    peca = _compor(_tres(contato=ATENDIMENTO), fic.BANNER)
    assert not _campo(peca, "contato") and not peca.avisos


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_o_numero_fica_na_bolha_e_a_chamada_no_balao(template):
    peca = _compor(_tres(), template)
    bolha = next(e for e in peca.elementos if getattr(e, "campo", "") == "bolha")
    balao = next(e for e in peca.elementos if getattr(e, "campo", "") == "balao")
    for texto in peca.textos:
        if texto.campo == "identificacao":
            assert geometria._dentro(texto.caixa, bolha.caixa) and texto.fundo == "#ffffff"
        if texto.campo in {"chamada_a_acao", "busca"}:
            assert geometria._dentro(texto.caixa, balao.caixa)
            assert texto.fundo == fic.PALETA["roxo_do_balao"] == balao.cor


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_o_texto_fica_no_mesmo_lugar_com_qualquer_imagem(template):
    """FR-3827: a bolha saiu do fundo para que o número não mude de lugar com a foto."""
    posicoes = {
        imagem.chave: [(t.campo, t.x, t.y) for t in _compor(_tres(), template, imagem.chave).textos]
        for imagem in fic.IMAGENS
    }
    assert len({tuple(p) for p in posicoes.values()}) == 1
