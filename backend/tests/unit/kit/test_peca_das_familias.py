"""As regras de composição dos templates das famílias, sobre fichas montadas à mão (119).

FR-3815 a FR-3821, FR-3824, FR-3825, FR-3827; EC-10, EC-11, EC-12, EC-17, EC-18. Cada caso roda em
todo template de família da comunicação, e confere a geometria (SC-1132) junto.
"""

import dataclasses

import pytest

from processo_seletivo.interface import kit_familias, kit_peca
from processo_seletivo.portal.ficha import NEUTRO, SEM_MATERIAL
from tests.unit.kit import geometria
from tests.unit.kit.test_peca import _titulo
from tests.unit.kit.test_textos import _ficha, _oferta

TEMPLATES = [t for t in kit_familias.templates() if t.familia != "institucional"]


def _id(template):
    return template.identificador


def _compor(ficha, template, **escolha):
    familia = kit_familias.familia(template.familia)
    escolha.setdefault("imagem", familia.imagens[0].chave if familia.imagens else None)
    peca = kit_peca.compor_template(ficha, template, kit_peca.Escolha(**escolha))
    assert geometria.problemas(peca) == [], template.identificador
    return peca


def _campo(peca, campo):
    return " ".join(t.conteudo for t in peca.textos if t.campo == campo)


UMA = (
    dataclasses.replace(_oferta("1", "Especialização em Docência", "", 40), carga_horaria="360h"),
)


def _uma(**mudar):
    return _ficha(ofertas=UMA, nomes_iguais=False, total_de_vagas=40, **mudar)


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_periodo_ate_com_ano_hora_e_inicio_no_mesmo_bloco(template):
    """FR-3815: "Inscrições até DD/MM/AAAA", a hora com o fuso, e o início com ano."""
    peca = _compor(_uma(), template)
    assert _campo(peca, "periodo_curto") == "Inscrições até 21/11/2026"
    assert _campo(peca, "hora") == "às 23h59 (horário de Brasília)"
    assert _campo(peca, "inicio") == "Início em 04/11/2026"


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_sem_termino_a_partir_de_e_neutro_sem_inscricao(template):
    """EC-17 e EC-10: as formas da `111` para período sem término e modo neutro."""
    sem_fim = _uma(fim=None, fim_data="", fim_hora="", periodo_curto="a partir de 04/11/2026")
    peca = _compor(sem_fim, template)
    assert _campo(peca, "periodo_curto") == "Inscrições a partir de 04/11/2026"
    assert _campo(peca, "hora") == "às 09h00 (horário de Brasília)"
    neutro = _compor(
        _uma(modo=NEUTRO, inicio=None, fim=None, inicio_data="", fim_data=""), template
    )
    assert "Inscrições" not in " ".join(t.conteudo for t in neutro.textos)
    assert "EDITAL PUBLICADO" in _campo(neutro, "fixo")


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_prorrogacao_comprovada_tem_o_selo(template):
    peca = _compor(_uma(prorrogado=True), template)
    assert "PRAZO PRORROGADO" in _campo(peca, "fixo")


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_numero_busca_chamada_e_selo_em_todo_formato(template):
    """FR-3816, FR-3819, FR-3821."""
    peca = _compor(_uma(), template)
    assert _campo(peca, "identificacao") == "Edital nº 91/2026"
    assert _campo(peca, "busca") == "busque por 91/2026 – Cefor"
    assert _campo(peca, "chamada_a_acao") == template.formato.chamada_a_acao
    assert _campo(peca, "selo").startswith("Versão vigente desde 31/10/2026")


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_oferta_com_carga_horaria_so_onde_ha_bloco_de_ofertas(template):
    """FR-3817 e EC-6: "Nome — carga horária"; o banner não tem bloco de ofertas."""
    peca = _compor(_uma(), template)
    oferta = _campo(peca, "oferta:1")
    if template.tem_ofertas:
        assert oferta == "Especialização em Docência — 360h: 40 vagas"
    else:
        assert oferta == "" and "vagas" not in " ".join(t.conteudo for t in peca.textos)


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_titulo_que_nao_cabe_sai_omitido_e_a_manchete_so_onde_nenhum_oficial_cabe(template):
    """FR-3818, EC-18: o título resolvido por formato; a manchete vale só onde falta o oficial."""
    longo = _uma(titulo_sem_numero=_titulo(600), titulo_do_processo=_titulo(600))
    sem = _compor(longo, template)
    assert sem.titulo == "" and sem.omissao == kit_peca.SEM_TITULO
    assert any(template.formato.chave in aviso for aviso in sem.avisos)
    com = _compor(longo, template, manchete=0, manchete_texto="Especialização em Docência")
    assert com.titulo == "manchete" and _campo(com, "manchete") == "Especialização em Docência"
    curto = _compor(_uma(), template, manchete=0, manchete_texto="Especialização em Docência")
    assert curto.titulo == "titulo_sem_numero"  # o oficial cabe: a manchete não entra


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_sem_material_e_host_local_nao_geram_peca(template):
    """EC-11, EC-12."""
    with pytest.raises(kit_peca.PecaRecusada):
        kit_peca.compor_template(
            _uma(modo=SEM_MATERIAL, motivo="Edital cancelado."), template, kit_peca.Escolha()
        )
    with pytest.raises(kit_peca.PecaRecusada, match="endereço público"):
        kit_peca.compor_template(_uma(caminho_curto=None), template, kit_peca.Escolha())


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_mesma_escolha_mesmo_svg_e_a_imagem_muda_so_o_fundo(template):
    """FR-3827, SC-1134; FR-3825: o alternativo descreve a imagem escolhida."""
    familia = kit_familias.familia(template.familia)
    primeira, segunda = familia.imagens[0], familia.imagens[1]
    uma = _compor(_uma(), template, imagem=primeira.chave)
    outra = _compor(_uma(), template, imagem=primeira.chave)
    assert kit_peca.svg(uma, _uma()) == kit_peca.svg(outra, _uma())
    trocada = _compor(_uma(), template, imagem=segunda.chave)
    assert primeira.descricao in uma.alternativo and segunda.descricao in trocada.alternativo
    textos = [(t.campo, t.conteudo, t.x, t.y) for t in uma.textos]
    assert textos == [(t.campo, t.conteudo, t.x, t.y) for t in trocada.textos]


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_imagem_fora_do_banco_e_recusada(template):
    with pytest.raises(kit_peca.EscolhaInvalida):
        kit_peca.compor_template(_uma(), template, kit_peca.Escolha(imagem="praia"))


# ---- EC-3: a carga horária longa recusa nomeando-a, e nunca some -----------------------------

LONGA = (
    "360 horas, das quais 60 presenciais e 300 a distância, com encontros quinzenais aos sábados "
    "no polo de apoio presencial e atividades síncronas pelo ambiente virtual de aprendizagem"
)


def _com_carga(*cargas):
    ofertas = tuple(
        dataclasses.replace(
            _oferta(str(i), f"Especialização em Docência {i}", "", 20), carga_horaria=carga
        )
        for i, carga in enumerate(cargas, start=1)
    )
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=20 * len(cargas))


@pytest.mark.parametrize("quantas", [1, 2])
@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_carga_horaria_longa_recusa_o_formato_nomeando_a(template, quantas):
    """EC-3: se a carga não cabe no mínimo, o formato é recusado com ela no motivo.

    A regressão que isto prende: com duas ofertas, a peça passava à contagem ("40 vagas em 2
    opções") e a carga horária sumia sem recusa nem aviso; com uma, o motivo era "1 opções".
    """
    ficha = _com_carga(*[LONGA] * quantas)
    if not template.tem_ofertas:
        _compor(ficha, template)  # EC-6: o banner não lista ofertas, e a carga não o alcança
        return
    with pytest.raises(kit_peca.PecaRecusada) as recusa:
        _compor(ficha, template)
    assert "carga horária" in recusa.value.motivo
    assert LONGA[:40] in recusa.value.motivo
    assert template.formato.chave in recusa.value.motivo


@pytest.mark.parametrize("template", [t for t in TEMPLATES if t.tem_ofertas], ids=_id)
def test_carga_horaria_vazia_numa_oferta_e_curta_noutra(template):
    """Cenário 19 (EC-2): sai só onde é declarada, e nada é completado.

    Onde o painel não tem altura para as duas opções, a peça passa ao total — e então nenhuma
    linha, nem carga, aparece (FR-3836).
    """
    peca = _compor(_com_carga("", "180h"), template)
    linhas = [_campo(peca, f"oferta:{i}") for i in ("1", "2")]
    if any(linhas):
        assert linhas == [
            "Especialização em Docência 1: 20 vagas",
            "Especialização em Docência 2 — 180h: 20 vagas",
        ]
    else:
        assert _campo(peca, "total_de_vagas") == "40 vagas em 2 opções"
        assert "180h" not in " ".join(t.conteudo for t in peca.textos)


# ---- EC-13: caractere sem glifo numa das fontes da família ---------------------------------


def _titulo_sem_u_agudo(monkeypatch, template):
    """A fonte do título da família, numa cópia sem «ú»; as outras continuam inteiras.

    Lida da família, e não fixada: na Pós Lato Sensu é a Poppins Bold, na Aperfeiçoamento a Lexend.
    """
    from processo_seletivo.interface import kit_fontes

    familia = kit_familias.familia(template.familia)
    chave = familia.fonte(template.caixa("titulo").fonte)
    original = kit_fontes.medidas

    def medidas(pedida):
        lidas = original(pedida)
        if pedida != chave:
            return lidas
        larguras = {c: v for c, v in lidas.larguras.items() if c != "ú"}
        return kit_fontes.Medidas(lidas.dados, larguras, lidas.ascendente, lidas.descendente)

    monkeypatch.setattr(kit_fontes, "medidas", medidas)
    return kit_fontes.FONTES[chave].familia


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_caractere_sem_glifo_so_na_fonte_de_titulo(template, monkeypatch):
    """Cenário 25: recusa nomeando caractere e fonte; o mesmo caractere no corpo continua."""
    nome_da_fonte = _titulo_sem_u_agudo(monkeypatch, template)
    no_titulo = _uma(titulo_sem_numero="Curso de Gestão Pública", titulo_do_processo="Gestão")
    with pytest.raises(kit_peca.PecaRecusada) as recusa:
        _compor(no_titulo, template)
    assert nome_da_fonte in recusa.value.motivo and "«ú»" in recusa.value.motivo
    if template.tem_ofertas:
        # «ú» no nome da oferta, que é de outra fonte da família, não é recusa.
        ofertas = (dataclasses.replace(UMA[0], nome="Especialização em Gestão Pública"),)
        _compor(_ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=40), template)


# ---- FR-3836: o resumo por falta de espaço ----------------------------------------------------


def _opcoes(quantas, nome="Docência"):
    ofertas = tuple(
        dataclasses.replace(_oferta(str(i), nome, f"Polo {i}", 20), carga_horaria="360h")
        for i in range(1, quantas + 1)
    )
    return _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=20 * quantas)


def _listou(peca):
    return any(t.campo.startswith("oferta:") for t in peca.textos)


STORY = next(t for t in TEMPLATES if t.formato.chave == "story")
POST = next(t for t in TEMPLATES if t.formato.chave == "post")


def test_a_lista_no_corpo_minimo_vem_antes_do_resumo():
    """Passo 2: três opções curtas cabem no story só com as ofertas no corpo mínimo."""
    peca = _compor(_opcoes(3), STORY)
    assert _listou(peca) and not peca.avisos
    minimo = STORY.caixa("oferta").corpos[-1]
    assert {t.tamanho for t in peca.textos if t.campo.startswith("oferta:")} == {minimo}


@pytest.mark.parametrize("template", [POST, STORY], ids=_id)
def test_o_resumo_traz_o_total_o_convite_e_o_aviso_do_formato(template):
    """Passo 4: o total e o convite à página, e o aviso que a tela junta por formato."""
    peca = _compor(_opcoes(4), template)
    assert not _listou(peca)
    assert _campo(peca, "total_de_vagas") == "80 vagas em 4 opções"
    assert _campo(peca, "fixo").endswith("Confira todas na página oficial")
    assert peca.avisos == (kit_peca.RESUMO_EM.format(formatos=template.formato.chave),)
    # Os textos continuam com as opções completas, com a carga horária.
    from processo_seletivo.interface import kit_textos

    legenda = kit_textos.compor(_opcoes(4))["legenda"]
    assert all(f"Docência — Polo {i} — 360h" in legenda for i in range(1, 5))


def test_sem_vaga_imediata_o_resumo_e_a_contagem():
    """A regra do total da FR-3425 vale no resumo: sem vaga imediata em toda opção, a contagem."""
    ofertas = tuple(
        dataclasses.replace(_oferta(str(i), "Docência", f"Polo {i}", 0), carga_horaria="360h")
        for i in range(1, 5)
    )
    peca = _compor(_ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=None), POST)
    assert _campo(peca, "contagem") == "4 opções" and not _campo(peca, "total_de_vagas")


def test_familia_fora_da_fr_3836_recusa_em_vez_de_resumir(monkeypatch):
    """A exceção é da Pós Lato Sensu; outra família recusa o formato, como a FR-3425 diz."""
    monkeypatch.setattr(kit_peca, "RESUMO_POR_ESPACO", frozenset())
    with pytest.raises(kit_peca.PecaRecusada):
        kit_peca.compor_template(_opcoes(4), POST, kit_peca.Escolha(imagem="fone"))
