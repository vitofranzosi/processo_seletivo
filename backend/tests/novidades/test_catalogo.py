"""O arquivo das Novidades do GPS (168, FR-7420 a FR-7423, SC-2505, SC-2506).

O que o carregador confere é a forma; o que se confere aqui é o resto — a rota, a âncora, a
configuração, a capacidade, a spec e o vocabulário —, porque pede o sistema inteiro e roda antes do
merge. Uma nota malformada reprova a suíte dizendo qual nota e qual campo.
"""

import datetime
import re
from pathlib import Path

import pytest
from django.conf import settings

from processo_seletivo.interface import navegacao
from processo_seletivo.interface.identidade import PAPEIS
from processo_seletivo.novidades import catalogo
from processo_seletivo.seguranca.acessos import PAPEIS_DE_ACESSO, PAPEIS_INSTITUCIONAIS

REPOSITORIO = Path(__file__).resolve().parents[3]
DOCUMENTACAO = REPOSITORIO / "docs" / "visao-sistema" / "index.html"
SPECS = REPOSITORIO / "specs"

NOTAS = catalogo.ler(catalogo.ARQUIVO.read_text(encoding="utf-8"))

# O que denuncia o log técnico no texto que a pessoa lê (FR-7407). A referência mora em `prs` e
# `specs`; no texto visível, ela é ruído para quem opera.
JARGAO = re.compile(
    r"\b(?:PRs?|FR-\d|SC-\d|UX-\d|D-\d{3}|spec|specs|commit|branch|merge|mergead[ao]s?|migration|"
    r"endpoint|pull request|refactor|deploy)\b|#\d|\.py\b|\.html\b|\binterface:",
    re.IGNORECASE,
)


def _visivel(nota):
    return [nota.titulo, nota.resumo, nota.beneficio, nota.onde, *nota.passos]


def test_o_arquivo_tem_o_conteudo_inicial():
    """FR-7426: o histórico nasce de 17/10 a 14/11/2026, da mais recente para a mais antiga."""
    assert len(NOTAS) >= 30
    assert NOTAS[0].data <= datetime.date(2026, 11, 14)
    assert NOTAS[-1].data >= datetime.date(2026, 10, 17)


@pytest.mark.parametrize("nota", NOTAS, ids=lambda n: n.id)
def test_o_texto_visivel_nao_e_log_tecnico(nota):
    """FR-7407, SC-2506."""
    for texto in _visivel(nota):
        assert not JARGAO.search(texto), f"{nota.id}: {JARGAO.search(texto).group(0)!r}"


@pytest.mark.parametrize("nota", NOTAS, ids=lambda n: n.id)
def test_a_nota_cabe_num_cartao(nota):
    """UX-802: o título é curto e o resumo não vira manual — o detalhe vai para os passos."""
    assert len(nota.titulo) <= 90, nota.id
    assert len(nota.resumo) <= 520, nota.id
    assert len(nota.passos) <= 4, nota.id


def test_o_destino_e_uma_secao_da_barra():
    """FR-7412: o link segue o predicado da seção, e só seção da barra tem predicado."""
    rotas = {s.rota for s in navegacao.SECOES + navegacao.SECOES_DE_ACESSO}
    for nota in NOTAS:
        assert not nota.destino or nota.destino in rotas, (nota.id, nota.destino)


def test_a_ancora_existe_na_documentacao_do_sistema():
    """FR-7422: o "Saiba mais" não leva a uma seção que não existe."""
    ancoras = set(re.findall(r'\bid="([^"]+)"', DOCUMENTACAO.read_text(encoding="utf-8")))
    for nota in NOTAS:
        assert not nota.documentacao or nota.documentacao in ancoras, (nota.id, nota.documentacao)


def test_a_configuracao_existe_e_e_booleana():
    """FR-7410: uma configuração escrita errado esconderia a nota em todo ambiente, sem aviso."""
    for nota in NOTAS:
        if nota.requer_configuracao:
            assert isinstance(getattr(settings, nota.requer_configuracao, None), bool), nota.id


def test_a_capacidade_existe():
    """FR-7411: uma capacidade escrita errado esconderia a nota de todos, sem aviso."""
    conhecidas = {
        permissao
        for _, permissoes in [*PAPEIS.values(), *PAPEIS_DE_ACESSO.values()]
        + list(PAPEIS_INSTITUCIONAIS.values())
        for permissao in permissoes
    }
    for nota in NOTAS:
        assert not nota.para_capacidade or nota.para_capacidade in conhecidas, nota.id


def test_a_spec_citada_existe():
    pastas = {p.name.split("-")[0] for p in SPECS.iterdir() if p.is_dir()}
    for nota in NOTAS:
        for spec in nota.specs:
            assert spec in pastas, (nota.id, spec)


def test_um_pr_conta_uma_novidade_so():
    """Vários PRs viram uma nota; um PR não vira duas (Etapa D: sem duplicidade)."""
    vistos = {}
    for nota in NOTAS:
        for pr in nota.prs:
            assert pr not in vistos, f"o PR {pr} está em {vistos.get(pr)} e em {nota.id}"
            vistos[pr] = nota.id


# ---- o carregador recusa o que está malformado -----------------------------------------------

VALIDA = """
[[nota]]
id = "uma"
data = 2026-11-10
categoria = "novidade"
titulo = "Título"
resumo = "Resumo."
prs = [1]
specs = []
"""


def test_a_nota_valida_se_le():
    (nota,) = catalogo.ler(VALIDA)
    assert nota.categoria.rotulo == "Novidade"
    assert nota.data == datetime.date(2026, 11, 10)


@pytest.mark.parametrize(
    ("troca", "mensagem"),
    [
        (('categoria = "novidade"', 'categoria = "anuncio"'), "categoria 'anuncio'"),
        (("data = 2026-11-10", 'data = "10/11/2026"'), "'data' deve ser AAAA-MM-DD"),
        (('id = "uma"', 'id = "Uma Nota"'), "'id' deve ser minúsculo"),
        (("prs = [1]\n", "prs = []\n"), "'prs' deve listar"),
        (('titulo = "Título"\n', ""), "falta 'titulo'"),
        (('resumo = "Resumo."', 'resumo = "  "'), "'resumo' está vazio"),
        (("specs = []", 'specs = []\nlink = "x"'), "campo desconhecido link"),
        (("[[nota]]", "[[nota"), "não é TOML válido"),
    ],
)
def test_a_nota_malformada_e_recusada_dizendo_onde(troca, mensagem):
    """SC-2505: o erro diz qual nota e qual campo."""
    with pytest.raises(catalogo.CatalogoInvalido, match=re.escape(mensagem)):
        catalogo.ler(VALIDA.replace(*troca))


def test_id_repetido_e_recusado():
    with pytest.raises(catalogo.CatalogoInvalido, match="se repete"):
        catalogo.ler(VALIDA + VALIDA)


def test_a_ordem_e_da_mais_recente_para_a_mais_antiga():
    antiga = VALIDA.replace('"uma"', '"outra"').replace("2026-11-10", "2026-11-01")
    catalogo.ler(VALIDA + antiga)
    with pytest.raises(catalogo.CatalogoInvalido, match="da mais recente para a mais antiga"):
        catalogo.ler(antiga + VALIDA)
