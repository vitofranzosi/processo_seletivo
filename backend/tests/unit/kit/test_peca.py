"""A peça do feed sobre fichas montadas à mão: geometria, coerência e regras (111, T020).

Os casos sintéticos são os do limite da D-016: título de 60, 120 e 210 caracteres, rótulo de opção
de 90, endereço de 60, e 4, 5 e 66 opções. Cada um ou compõe sem nenhum problema geométrico, ou é
recusado com o motivo — e o teste diz qual dos dois espera.
"""

import dataclasses
import re

import pytest

from processo_seletivo.interface import kit_peca, kit_textos
from processo_seletivo.interface.kit_peca import FIXOS, PecaRecusada, Texto
from processo_seletivo.portal.ficha import NEUTRO, SEM_MATERIAL
from tests.unit.kit import geometria
from tests.unit.kit.test_textos import QUATRO_POLOS, _ficha, _oferta


def _titulo(caracteres):
    """Um título de `caracteres` caracteres, em palavras de tamanho realista."""
    palavras = "Curso de Pós-graduação Lato Sensu em Informática na Educação Profissional".split()
    texto, i = "", 0
    while len(texto) < caracteres:
        texto = f"{texto} {palavras[i % len(palavras)]}".strip()
        i += 1
    return texto[:caracteres].rstrip()


def _opcoes(quantas, nome="Especialização em Informática na Educação"):
    return tuple(_oferta(f"{i:03}", nome, f"Polo {i}", 10) for i in range(quantas))


def _por_campo(peca, campo):
    return [t.conteudo for t in peca.textos if t.campo == campo]


def _compoe_bem(ficha, **kwargs):
    peca = kit_peca.compor(ficha, **kwargs)
    assert geometria.problemas(peca) == []
    return peca


# ---- Geometria, nos casos do limite (FR-3428, FR-3429, D-016) -------------------------------


SINTETICOS = {
    "quatro polos": {},
    "prorrogado": dict(
        prorrogado=True, fim_original_texto="21/11/2026", fim_vigente_texto="26/11/2026"
    ),
    "neutro": dict(modo=NEUTRO, inicio=None, fim=None, inicio_data="", fim_data=""),
    "título de 60": dict(titulo_sem_numero=_titulo(60)),
    "título de 120": dict(titulo_sem_numero=_titulo(120)),
    "título de 210": dict(titulo_sem_numero=_titulo(210)),
    "endereço de 60": dict(
        caminho_curto="gps-processos-seletivos-e-editais.cefor.ifes.edu.br/selecoes"
    ),
    "cinco opções": dict(ofertas=_opcoes(5), total_de_vagas=50),
    "66 opções": dict(ofertas=_opcoes(66), total_de_vagas=660),
    "uma opção": dict(ofertas=QUATRO_POLOS[:1], total_de_vagas=40),
    "virada de ano": dict(
        periodo_curto="15/12/2026 a 10/01/2027", inicio_data="15/12/2026", fim_data="10/01/2027"
    ),
    "sem término": dict(fim=None, fim_data="", fim_hora="", periodo_curto="a partir de 04/11/2026"),
}


@pytest.mark.parametrize("nome", SINTETICOS)
def test_geometria_dos_casos_no_limite(nome):
    _compoe_bem(_ficha(**SINTETICOS[nome]))


def test_endereco_de_60_caracteres_inteiro_numa_linha():
    caminho = SINTETICOS["endereço de 60"]["caminho_curto"]
    assert len(caminho) == 60
    peca = _compoe_bem(_ficha(caminho_curto=caminho))
    assert _por_campo(peca, "caminho_curto") == [caminho]


def test_rotulo_de_90_caracteres_empilha_a_quantidade():
    rotulo = _titulo(90)
    ofertas = (_oferta("x", "Curso", rotulo, 40), *QUATRO_POLOS[1:3])
    peca = _compoe_bem(_ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=120))
    linhas = _por_campo(peca, "oferta_rotulo:x")
    assert " ".join(linhas) == f"Curso — {rotulo}"
    quantidade = [t for t in peca.textos if t.campo == "oferta_quantidade:x"][0]
    assert quantidade.y > [t for t in peca.textos if t.campo == "oferta_rotulo:x"][0].y


def test_composicao_que_nao_cabe_e_recusada_com_o_motivo():
    longos = tuple(
        _oferta(str(i), f"Curso {i}", _titulo(90), 40) for i in range(kit_textos.TETO_DE_OPCOES)
    )
    ficha = _ficha(
        titulo_sem_numero=_titulo(120), ofertas=longos, nomes_iguais=False, total_de_vagas=160
    )
    with pytest.raises(PecaRecusada, match="não cabe"):
        kit_peca.compor(ficha)


def test_endereco_longo_demais_e_recusado():
    caminho = "processos-seletivos-e-editais-do-centro-de-referencia-em-formacao.cefor.ifes.edu.br"
    caminho += "/selecoes"
    with pytest.raises(PecaRecusada, match="endereço"):
        kit_peca.compor(_ficha(caminho_curto=caminho))


# ---- Título (FR-3426, EC-13, EC-14) ---------------------------------------------------------


def test_titulo_do_edital_sem_o_numero():
    peca = _compoe_bem(_ficha())
    assert peca.titulo == "titulo_sem_numero"
    assert " ".join(_por_campo(peca, "titulo_sem_numero")) == (
        "Curso de Pós-graduação em Informática na Educação"
    )
    assert not any("91/2026 –" in t.conteudo for t in peca.textos if t.campo.startswith("titulo"))


def test_titulo_longo_cede_ao_do_processo_sem_truncar():
    titulo = _titulo(210)
    peca = _compoe_bem(_ficha(titulo_sem_numero=titulo))
    assert peca.titulo == "titulo_do_processo"
    assert " ".join(_por_campo(peca, "titulo_do_processo")) == "Processo Seletivo de Alunos"
    assert not any("…" in t.conteudo or "..." in t.conteudo for t in peca.textos)


def test_titulo_desce_de_corpo_antes_de_ceder():
    """Quatro polos e um título de três linhas: o corpo menor deixa a oferta inteira."""
    titulo = _titulo(120)
    maior, _ = kit_peca.medidas_do_titulo(titulo)[0]
    peca = _compoe_bem(_ficha(titulo_sem_numero=titulo))
    assert peca.titulo == "titulo_sem_numero"
    (tamanho,) = {t.tamanho for t in peca.textos if t.campo == "titulo_sem_numero"}
    assert tamanho < maior


def test_sem_titulo_que_caiba_a_peca_diz_a_omissao():
    peca = _compoe_bem(
        _ficha(titulo_sem_numero=_titulo(400), titulo_do_processo=_titulo(400), ofertas=())
    )
    assert peca.titulo == ""
    assert peca.omissao == kit_peca.SEM_TITULO


# ---- Oferta (FR-3425, EC-11, EC-12, EC-23) --------------------------------------------------


def test_ate_quatro_opcoes_listadas_com_a_quantidade():
    peca = _compoe_bem(_ficha())
    for oferta in QUATRO_POLOS:
        assert _por_campo(peca, f"oferta_rotulo:{oferta.perfil_id}") == [oferta.localidade]
        assert _por_campo(peca, f"oferta_quantidade:{oferta.perfil_id}") == ["40 vagas"]


def test_total_sempre_com_o_numero_de_opcoes():
    peca = _compoe_bem(_ficha())
    assert _por_campo(peca, "total_de_vagas") == ["160 vagas em 4 opções"]
    sem_total = _compoe_bem(_ficha(total_de_vagas=None))
    assert _por_campo(sem_total, "total_de_vagas") == []


@pytest.mark.parametrize("quantas", [5, 66])
def test_acima_do_teto_a_peca_conta(quantas):
    peca = _compoe_bem(_ficha(ofertas=_opcoes(quantas), total_de_vagas=10 * quantas))
    assert _por_campo(peca, "contagem") == [f"{quantas} opções"]
    assert not any(t.campo.startswith("oferta_rotulo") for t in peca.textos)
    assert FIXOS["todas"] in _por_campo(peca, "fixo")


def test_rotulos_indistintos_contam():
    iguais = tuple(dataclasses.replace(o, localidade="") for o in QUATRO_POLOS)
    peca = _compoe_bem(_ficha(ofertas=iguais))
    assert _por_campo(peca, "contagem") == ["4 opções"]


def test_cadastro_reserva_entre_opcoes_com_vaga():
    ofertas = (
        _oferta("1", "Curso", "Serra", 2, reserva=True),
        _oferta("2", "Curso", "Iúna", 0, reserva=True),
    )
    peca = _compoe_bem(_ficha(ofertas=ofertas, total_de_vagas=None))
    assert _por_campo(peca, "oferta_quantidade:1") == ["2 vagas e cadastro reserva"]
    assert _por_campo(peca, "oferta_quantidade:2") == ["cadastro reserva"]
    assert _por_campo(peca, "total_de_vagas") == []


# ---- Período e neutro (FR-3424) -------------------------------------------------------------


def test_periodo_em_datas_absolutas_no_destaque():
    peca = _compoe_bem(_ficha())
    (datas,) = [t for t in peca.textos if t.campo == "periodo_curto"]
    assert datas.conteudo == "04/11 a 21/11/2026"
    assert datas.tamanho == max(t.tamanho for t in peca.textos)
    assert _por_campo(peca, "hora") == ["até as 23h59 (horário de Brasília)"]


def test_selo_de_prorrogacao_so_comprovada():
    assert FIXOS["prorrogado"] not in _por_campo(_compoe_bem(_ficha()), "fixo")
    prorrogada = _ficha(
        prorrogado=True, fim_original_texto="21/11/2026", fim_vigente_texto="26/11/2026"
    )
    assert FIXOS["prorrogado"] in _por_campo(_compoe_bem(prorrogada), "fixo")


def test_neutro_nao_fala_de_inscricao():
    peca = _compoe_bem(_ficha(**SINTETICOS["neutro"]))
    tudo = " ".join(t.conteudo for t in peca.textos) + peca.alternativo
    assert not re.search("inscri", tudo, re.IGNORECASE)
    assert FIXOS["publicado"] in _por_campo(peca, "fixo")


def test_sem_material_e_host_local_recusam():
    with pytest.raises(PecaRecusada, match="cancelado"):
        kit_peca.compor(_ficha(modo=SEM_MATERIAL, motivo="Edital cancelado."))
    with pytest.raises(PecaRecusada) as recusa:
        kit_peca.compor(_ficha(endereco=None, caminho_curto=None))
    assert recusa.value.motivo == kit_peca.HOST_LOCAL


# ---- Coerência (FR-3423) --------------------------------------------------------------------


def _valores_admitidos(peca, ficha):
    """Cada texto da peça e o valor da ficha, ou a frase fixa, de onde ele pode ter vindo."""
    rotulos = {
        f"oferta_rotulo:{o.perfil_id}": kit_textos.rotulo_da_oferta(o, ficha) for o in ficha.ofertas
    }
    quantidades = {f"oferta_quantidade:{o.perfil_id}": o.quantidade for o in ficha.ofertas}
    return {
        "identificacao": ficha.identificacao,
        "titulo_sem_numero": ficha.titulo_sem_numero,
        "titulo_do_processo": ficha.titulo_do_processo,
        "periodo_curto": ficha.periodo_curto,
        "hora": kit_peca._hora_do_periodo(ficha),
        "total_de_vagas": kit_textos.total_em_frase(ficha),
        "oferta_nome": ficha.ofertas[0].nome if ficha.ofertas else "",
        "contagem": f"{len(ficha.ofertas)} opções",
        "caminho_curto": ficha.caminho_curto,
        "busca": kit_peca.busca_na_peca(ficha),
        "selo": kit_peca.selo_da_versao(ficha),
        "assinatura": kit_textos.assinatura(ficha),
        **rotulos,
        **quantidades,
    }


@pytest.mark.parametrize("nome", SINTETICOS)
def test_a_peca_so_diz_o_que_a_ficha_diz(nome):
    ficha = _ficha(**SINTETICOS[nome])
    peca = kit_peca.compor(ficha)
    admitidos = _valores_admitidos(peca, ficha)
    por_campo = {}
    for texto in peca.textos:
        por_campo.setdefault(texto.campo, []).append(texto.conteudo)
    for campo, partes in por_campo.items():
        if campo == "fixo":
            assert set(partes) <= set(FIXOS.values())
        else:
            assert " ".join(partes) == admitidos[campo], campo
    assert kit_peca.fora_dos_textos(peca, kit_textos.compor(ficha)) == []


def test_conferencia_acusa_o_numero_que_os_textos_nao_dizem():
    ficha = _ficha()
    peca = kit_peca.compor(ficha)
    textos = dict(kit_textos.compor(ficha))
    textos = {chave: valor.replace("23h59", "--") for chave, valor in textos.items()}
    assert kit_peca.fora_dos_textos(peca, textos) == ["23h59"]


# ---- Grafia (FR-3430, EC-15) ----------------------------------------------------------------


def test_caractere_sem_grafia_recusa_nomeando():
    with pytest.raises(PecaRecusada, match="U\\+2265"):
        kit_peca.compor(_ficha(titulo_sem_numero="Curso para idade ≥ 18 anos"))


def test_texto_desenhado_e_o_normalizado():
    peca = kit_peca.compor(_ficha(titulo_sem_numero="Curso​ de Pós"))
    desenhado = " ".join(_por_campo(peca, "titulo_sem_numero"))
    assert "​" not in desenhado
    for texto in peca.textos:
        assert isinstance(texto, Texto)
        assert texto.largura == kit_peca.largura(texto.conteudo, texto.tamanho, texto.fonte)


# ---- Texto alternativo (FR-3433) e espaço livre (FR-3434) -----------------------------------


def test_texto_alternativo_em_frases_na_ordem_da_peca():
    alternativo = kit_peca.compor(_ficha()).alternativo
    ordem = [
        "Peça de divulgação do Cefor/Ifes",
        "Edital nº 91/2026: Curso de Pós-graduação em Informática na Educação.",
        "Inscrições de 04/11 a 21/11/2026, até as 23h59 (horário de Brasília).",
        "160 vagas em 4 opções.",
        "Polo Bom Jesus do Norte: 40 vagas.",
        "Polo Vargem Alta: 40 vagas.",
        "busque por 91/2026 – Cefor.",
    ]
    posicoes = [alternativo.index(trecho) for trecho in ordem]
    assert posicoes == sorted(posicoes)
    assert alternativo.endswith(".")


def test_texto_alternativo_conta_o_que_a_peca_conta():
    alternativo = kit_peca.compor(_ficha(ofertas=_opcoes(66), total_de_vagas=660)).alternativo
    assert "66 opções" in alternativo
    assert "Polo 1:" not in alternativo


def test_espaco_livre_desce_35_por_cento_da_folga():
    curta = _ficha(ofertas=QUATRO_POLOS[:1], total_de_vagas=40)
    peca = _compoe_bem(curta)
    fundo = max(kit_peca._base(e) for e in peca.corpo)
    limite = kit_peca.RODAPE - kit_peca.FOLGA_DO_RODAPE
    folga = limite - (fundo - peca.deslocamento)
    assert peca.deslocamento > 0
    assert abs(peca.deslocamento - 0.35 * folga) <= 0.5
    assert limite - fundo <= 0.65 * folga + 0.5


# ---- Marca (FR-3432) ------------------------------------------------------------------------


def test_marca_oficial_da_unidade_ou_do_ifes_com_a_sigla():
    cefor = kit_peca.compor(_ficha())
    assert _por_campo(cefor, "assinatura") == []
    (marca,) = [e for e in cefor.elementos if isinstance(e, kit_peca.Imagem)]
    assert marca.marca.arquivo == "cefor-horizontal-branco.png"

    serra = kit_peca.compor(_ficha(unidade_sigla="Campus Serra"))
    assert _por_campo(serra, "assinatura") == ["Campus Serra/Ifes"]
    (marca,) = [e for e in serra.elementos if isinstance(e, kit_peca.Imagem)]
    assert marca.marca.arquivo == "ifes-horizontal-branco.png"


def test_os_arquivos_da_marca_sao_os_registrados():
    assert kit_peca.conferir_marcas() == {}


def test_oferta_sem_nome_comum_nem_total_abre_a_primeira_frase():
    ofertas = (
        _oferta("1", "Professor de Informática", "Serra", 3, reserva=True),
        _oferta("2", "Técnico de Laboratório", "Vitória", 0, reserva=True),
    )
    alternativo = kit_peca.compor(
        _ficha(ofertas=ofertas, nomes_iguais=False, total_de_vagas=None)
    ).alternativo
    assert "Oferta." not in alternativo
    assert "Oferta: Professor de Informática — Serra: 3 vagas e cadastro reserva." in alternativo
    assert "Técnico de Laboratório — Vitória: cadastro reserva." in alternativo
