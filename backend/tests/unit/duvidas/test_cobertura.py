"""Todo campo do conteúdo publicado é mostrado, ou excluído com o motivo (070, `SC-533`, `R-015`).

Um campo novo, de feature futura, faz esta conferência falhar até ser classificado em
`duvidas/domain/cobertura.py`: pelo conteúdo do corpus, pelos esquemas declarados ou pela versão do
esquema, que toda feature que muda o conteúdo publicado precisa subir.
"""

import glob
import json
import re

import pytest

from processo_seletivo.duvidas.domain import cobertura
from processo_seletivo.editais.domain import validation
from processo_seletivo.shared.canonical import SCHEMA_VERSION
from tests.fixtures.corpus import PASTA
from tests.unit.duvidas.conftest import varrer


def _folhas(valor, caminho="", *, so_preenchidas=False):
    if isinstance(valor, dict):
        if not valor and not so_preenchidas:
            yield caminho
        for chave, item in valor.items():
            yield from _folhas(item, f"{caminho}/{chave}", so_preenchidas=so_preenchidas)
    elif isinstance(valor, list):
        if not valor or not isinstance(valor[0], dict | list):
            if valor or not so_preenchidas:
                yield caminho
        else:
            for item in valor:
                yield from _folhas(item, f"{caminho}/*", so_preenchidas=so_preenchidas)
    elif not so_preenchidas or valor not in (None, ""):
        yield caminho


def folhas_do_corpus(*, so_preenchidas=False):
    caminhos = set()
    for arquivo in glob.glob(str(PASTA / "*" / "pub*-canonico.json")):
        with open(arquivo) as aberto:
            caminhos.update(_folhas(json.load(aberto), so_preenchidas=so_preenchidas))
    return caminhos


ESQUEMAS = {
    "/profiles/*": validation.PERFIL_PUBLICADO,
    "/profiles/*/vacancyTable/*": validation.LINHA_DO_QUADRO_PUBLICADA,
    "/schedule/*": validation.EVENTO_PUBLICADO,
    "/documentRequirements/*": validation.DOCUMENTO_EXIGIDO_PUBLICADO,
    "/stages/*": validation.ETAPA_PUBLICADA,
    "/sections/*": validation.SECAO_PUBLICADA,
    "/attachments/*": validation.ANEXO_PUBLICADO,
}


def test_a_tabela_e_a_desta_versao_do_esquema():
    assert SCHEMA_VERSION == cobertura.VERSAO_DO_ESQUEMA, (
        "O conteúdo publicado mudou de versão: classifique o campo novo em "
        "duvidas/domain/cobertura.py e suba VERSAO_DO_ESQUEMA."
    )


def test_todo_caminho_do_corpus_esta_classificado():
    soltos = sorted(c for c in folhas_do_corpus() if cobertura.classe(c) is None)
    assert soltos == []


@pytest.mark.parametrize("base", sorted(ESQUEMAS))
def test_todo_campo_dos_esquemas_declarados_esta_classificado(base):
    soltos = [
        campo.nome
        for campo in ESQUEMAS[base]
        if cobertura.classe(f"{base}/{campo.nome}") is None
        and not any(chave.startswith(f"{base}/{campo.nome}/") for chave in cobertura.COBERTURA)
    ]
    assert soltos == []


def test_toda_exclusao_tem_motivo():
    for padrao, classe in cobertura.COBERTURA.items():
        if isinstance(classe, tuple) and classe and classe[0] == "EXCLUIDO":
            assert len(classe[1]) > 20, padrao


def _generalizar(caminho):
    return re.sub(r"id=[^/]+", "*", caminho)


def _cobre(cartao, padrao):
    base = padrao[:-3] if padrao.endswith("/**") else padrao
    return cartao == base or cartao.startswith(base + "/") or base.startswith(cartao + "/")


def test_o_que_a_tabela_diz_que_uma_pergunta_mostra_alguma_resposta_mostra():
    mostrados = {}
    for _nome, _instante, _contexto, resposta in varrer():
        for referencia in resposta.referencias:
            if referencia.caminho:
                mostrados.setdefault(resposta.pergunta, set()).add(_generalizar(referencia.caminho))
    # Só o que o corpus preenche: campo vazio ou nulo não sai em cartão, por regra (`FR-1426`).
    presentes = folhas_do_corpus(so_preenchidas=True)
    faltando = []
    for padrao, classe in cobertura.COBERTURA.items():
        if not isinstance(classe, tuple) or not classe or classe[0] == "EXCLUIDO":
            continue
        if padrao in cobertura.CONDICIONAIS:
            continue
        base = padrao[:-3] if padrao.endswith("/**") else padrao
        if not any(p == base or p.startswith(base + "/") for p in presentes):
            continue
        cartoes = set().union(*(mostrados.get(pergunta, set()) for pergunta in classe))
        if not any(_cobre(cartao, padrao) for cartao in cartoes):
            faltando.append((padrao, classe))
    assert faltando == [], faltando
