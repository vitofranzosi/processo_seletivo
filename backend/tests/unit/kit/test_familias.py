"""O registro de famílias do kit e a declaração de cada uma (119, FR-3802–FR-3805, FR-3808, D-014).

Lê o registro, e não uma lista de famílias escrita aqui: uma família nova passa por estes casos
sem ninguém lembrar de acrescentá-la (a armadilha da varredura de vocabulário com lista literal).
"""

import dataclasses
import hashlib
import re
from pathlib import Path

import pytest
from django.conf import settings

from processo_seletivo.interface import kit_familias, kit_fontes, kit_peca
from processo_seletivo.interface.kit_familias import (
    OMITIR,
    PAPEIS,
    PODEM_OMITIR,
    RECUSAR,
    institucional,
)
from processo_seletivo.interface.kit_formatos import FORMATOS

REFERENCIAS = Path(__file__).resolve().parents[2] / "fixtures" / "kit_referencias"
COR = re.compile(r"#[0-9a-f]{6}")

FAMILIAS = list(kit_familias.REGISTRO.values())
TEMPLATES = list(kit_familias.templates())


def _id(objeto):
    return getattr(objeto, "identificador", None) or objeto.chave


@pytest.mark.parametrize("familia", FAMILIAS, ids=_id)
def test_a_familia_declara_os_campos_do_data_model(familia):
    assert familia.chave in settings.FAMILIAS_DO_KIT
    assert familia.nome and familia.versao >= 1
    assert set(familia.fontes) <= set(PAPEIS)
    assert set(familia.fontes.values()) <= set(kit_fontes.FONTES)
    assert familia.paleta and all(COR.fullmatch(cor) for cor in familia.paleta.values())
    assert familia.frases and all(isinstance(f, str) and f for f in familia.frases.values())
    assert familia.templates and set(familia.templates) <= set(FORMATOS)
    assert 0 <= len(familia.imagens) <= 6
    # Só a Institucional vale para todas as unidades (FR-3805).
    assert bool(familia.unidades) == (familia.chave != institucional.CHAVE)


@pytest.mark.parametrize("familia", FAMILIAS, ids=_id)
def test_todo_ativo_e_imagem_citados_existem_com_o_resumo_registrado(familia):
    for nome, ativo in familia.ativos.items():
        caminho = familia.pasta_dos_ativos / ativo.arquivo
        assert caminho.is_file(), f"{familia.chave}: falta o ativo {nome} ({ativo.arquivo})"
        assert hashlib.sha256(caminho.read_bytes()).hexdigest() == ativo.sha256, nome
    for imagem in familia.imagens:
        assert set(imagem.arquivos) == set(familia.templates), imagem.chave
        for formato, (arquivo, resumo) in imagem.arquivos.items():
            caminho = familia.pasta_dos_ativos / arquivo
            assert caminho.is_file(), f"{familia.chave}: falta {arquivo}"
            assert hashlib.sha256(caminho.read_bytes()).hexdigest() == resumo, arquivo
            # Reduzida ao tamanho de uso, no máximo 400 kB (FR-3826, SC-1138).
            assert caminho.stat().st_size <= 400 * 1024, arquivo
            assert formato in familia.templates
        assert imagem.descricao and imagem.licenca and imagem.origem


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_o_template_declara_o_que_o_compositor_le(template):
    familia = kit_familias.familia(template.familia)
    assert template.formato.chave in settings.FORMATOS_DO_KIT
    assert template.composicao in kit_peca.COMPOSITORES
    assert template.versao >= 1
    assert template.forma_do_periodo in {"ate", "de-a"}
    assert set(template.ativos_posicionados) <= set(familia.ativos)
    campos = [caixa.campo for caixa in template.caixas]
    assert len(campos) == len(set(campos)), "caixa declarada duas vezes"
    assert re.fullmatch(r"[0-9a-f]{64}", template.resumo_das_referencias)


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_toda_caixa_tem_corpos_validos_e_so_titulo_e_contato_omitem(template):
    familia = kit_familias.familia(template.familia)
    minimo = template.formato.corpo_minimo
    for caixa in template.caixas:
        nome = f"{template.identificador}, caixa {caixa.campo}"
        assert caixa.corpos, nome
        assert all(corpo >= minimo for corpo in caixa.corpos), f"{nome}: corpo abaixo do mínimo"
        assert list(caixa.corpos) == sorted(caixa.corpos, reverse=True), f"{nome}: fora de ordem"
        assert all(linhas >= 1 for _, linhas in caixa.medidas()), nome
        assert caixa.fonte in familia.fontes, f"{nome}: papel de fonte não declarado"
        assert caixa.cor in familia.paleta and caixa.fundo in familia.paleta, nome
        assert caixa.alinhamento in {"start", "end", "middle"}, nome
        assert caixa.ao_nao_caber in {RECUSAR, OMITIR}, nome
        if caixa.ao_nao_caber == OMITIR:
            assert caixa.campo in PODEM_OMITIR, f"{nome}: só título e contato podem omitir"


def test_a_institucional_vale_para_qualquer_unidade():
    for codigo in ("cefor", "campus-serra", ""):
        assert institucional.FAMILIA in kit_familias.familias_da_unidade(codigo)


def test_registrar_recusa_familia_repetida_e_template_fora_do_lugar():
    with pytest.raises(ValueError, match="duas vezes"):
        kit_familias.registrar(institucional.FAMILIA)
    deslocada = dataclasses.replace(
        institucional.FAMILIA, chave="tmd", templates={"story": institucional.POST}
    )
    with pytest.raises(ValueError, match="fora do lugar"):
        kit_familias.registrar(deslocada)
    assert "tmd" not in kit_familias.REGISTRO


# ---- O resumo do template (FR-3833, D-014) e a liberação (FR-3808, FR-3835, D-010) -------------


def resumo_das_referencias(template):
    """O SHA-256 da lista `nome resumo` dos SVG de referência do template, em ordem de nome."""
    pasta = REFERENCIAS / template.pasta_das_referencias
    # As peças e as recusas: a referência de um cenário que o template recusa é o motivo.
    arquivos = sorted([*pasta.glob("*.svg"), *pasta.glob("*.recusa")])
    assert arquivos, f"{template.identificador}: nenhuma referência em {pasta}"
    linhas = "".join(
        f"{arquivo.name} {hashlib.sha256(arquivo.read_bytes()).hexdigest()}\n"
        for arquivo in arquivos
    )
    return hashlib.sha256(linhas.encode()).hexdigest()


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_o_resumo_das_referencias_fixado_e_o_dos_svg(template):
    """Regerar uma referência sem atualizar o resumo fixado reprova aqui (SC-1133)."""
    assert template.resumo_das_referencias == resumo_das_referencias(template)


def test_o_identificador_e_o_resumo_da_institucional_v1_estao_congelados():
    assert institucional.POST.identificador == "feed-1080x1350 · 1" == kit_peca.TEMPLATE
    assert kit_familias.resumo(institucional.POST) == institucional.RESUMO_CONGELADO_V1


def test_o_resumo_muda_com_a_declaracao():
    original = kit_familias.resumo(institucional.POST)
    caixas = list(institucional.POST.caixas)
    caixas[0] = dataclasses.replace(caixas[0], corpos=(38,))
    mudado = dataclasses.replace(institucional.POST, caixas=tuple(caixas))
    assert kit_familias.resumo(mudado) != original


def test_a_suite_libera_todo_o_registro_com_a_versao_e_o_resumo_do_codigo():
    esperado = {
        (t.familia, t.formato.chave, t.versao, kit_familias.resumo(t)[: kit_familias.RESUMO_CURTO])
        for t in TEMPLATES
    }
    assert set(settings.KIT_DE_DIVULGACAO_TEMPLATES) == esperado


def test_a_chave_da_111_rege_a_institucional_v1(settings):
    settings.KIT_DE_DIVULGACAO_PECA = True
    assert institucional.POST in kit_familias.liberados()
    settings.KIT_DE_DIVULGACAO_PECA = False
    # Listada na chave nova, a versão 1 continua da chave da `111`.
    assert institucional.POST not in kit_familias.liberados()


def test_versao_ou_resumo_divergente_do_nomeado_fica_indisponivel(settings, monkeypatch):
    """Fora do resumo congelado, a Institucional passa à chave nova, que nomeia versão e resumo."""
    monkeypatch.setattr(institucional, "RESUMO_CONGELADO_V1", "0" * 64)
    settings.KIT_DE_DIVULGACAO_PECA = True
    curto = kit_familias.resumo(institucional.POST)[: kit_familias.RESUMO_CURTO]
    settings.KIT_DE_DIVULGACAO_TEMPLATES = (("institucional", "post", 1, curto),)
    assert institucional.POST in kit_familias.liberados()
    settings.KIT_DE_DIVULGACAO_TEMPLATES = (("institucional", "post", 1, "0" * 12),)
    assert institucional.POST not in kit_familias.liberados()
    settings.KIT_DE_DIVULGACAO_TEMPLATES = (("institucional", "post", 2, curto),)
    assert institucional.POST not in kit_familias.liberados()


def _modulo(familia):
    import importlib

    return importlib.import_module(
        f"processo_seletivo.interface.kit_familias.{familia.chave.replace('-', '_')}"
    )


@pytest.mark.parametrize("template", TEMPLATES, ids=_id)
def test_o_resumo_de_cada_versao_e_o_fixado_no_modulo(template):
    """Esquecer de atualizar o resumo, ou regravá-lo, reprova aqui (FR-3833, EC-22, SC-1140)."""
    modulo = _modulo(kit_familias.familia(template.familia))
    if template.familia == institucional.CHAVE:
        assert kit_familias.resumo(template) == institucional.RESUMO_CONGELADO_V1
        return
    referencias, resumo = modulo.RESUMOS[(template.formato.chave, template.versao)]
    assert template.resumo_das_referencias == referencias
    assert kit_familias.resumo(template) == resumo


@pytest.mark.parametrize("familia", FAMILIAS, ids=_id)
def test_trocar_um_byte_de_ativo_muda_o_resumo(familia, monkeypatch):
    """Uma cópia em memória com um byte trocado: o resumo do template muda (EC-22)."""
    template = next(iter(familia.templates.values()))
    antes = kit_familias.resumo(template)
    original = kit_familias._resumo_de_arquivo

    def trocado(caminho):
        resumo = original(caminho)
        return ("0" if resumo[0] != "0" else "1") + resumo[1:]

    monkeypatch.setattr(kit_familias, "_resumo_de_arquivo", trocado)
    assert kit_familias.resumo(template) != antes
