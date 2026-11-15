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

CATALOGO = catalogo.ler_catalogo(catalogo.ARQUIVO.read_text(encoding="utf-8"))
NOTAS = CATALOGO.notas

# O que denuncia o log técnico no texto que a pessoa lê (FR-7407). A referência mora em `prs` e
# `specs`; no texto visível, ela é ruído para quem opera.
JARGAO = re.compile(
    r"\b(?:PRs?|FR-\d|SC-\d|UX-\d|D-\d{3}|spec|specs|commit|branch|merge|mergead[ao]s?|migration|"
    r"endpoint|pull request|refactor|deploy)\b|#\d|\.py\b|\.html\b|\binterface:",
    re.IGNORECASE,
)


# As palavras do sistema que a diretriz de 14/11 tira do texto de quem opera (FR-7427): quem lê não
# sabe — nem precisa saber — o que é um marco, um recorte ou uma derivação.
PALAVRAS_DO_SISTEMA = re.compile(
    r"\b(?:marcos?|recortes?|deriva\w*|apura\w*|predicados?|persist\w*|renderiz\w*|idempot\w*)\b"
    r"|\b(?:RC|DP|ED|PV|A)-\d",
    re.IGNORECASE,
)


def _visivel(nota):
    return [nota.titulo, nota.resumo, nota.exemplo, nota.beneficio, nota.onde, *nota.passos]


def test_o_arquivo_tem_o_conteudo_inicial():
    """FR-7426: o histórico começa em 15/09 (`D-010`), e cresce para a frente.

    Sem teto de data: a próxima curadoria acrescenta notas mais novas no topo, e isso é o esperado.
    """
    assert len(NOTAS) >= 30
    assert NOTAS[-1].data >= datetime.date(2026, 9, 15)


@pytest.mark.parametrize("nota", NOTAS, ids=lambda n: n.id)
def test_o_texto_visivel_nao_e_log_tecnico(nota):
    """FR-7407, SC-2506."""
    for texto in _visivel(nota):
        assert not JARGAO.search(texto), f"{nota.id}: {JARGAO.search(texto).group(0)!r}"


@pytest.mark.parametrize("nota", NOTAS, ids=lambda n: n.id)
def test_a_nota_fala_a_lingua_de_quem_opera(nota):
    """FR-7427: nenhuma palavra do sistema no que a pessoa lê."""
    for texto in _visivel(nota):
        achado = PALAVRAS_DO_SISTEMA.search(texto)
        assert not achado, f"{nota.id}: {achado.group(0)!r}"


@pytest.mark.parametrize("nota", NOTAS, ids=lambda n: n.id)
def test_a_nota_e_um_anuncio_curto(nota):
    """FR-7427, UX-802: título que promete, resumo de duas frases, exemplo de uma cena."""
    assert len(nota.titulo) <= 70, nota.id
    assert len(nota.resumo) <= 300, nota.id
    assert len(nota.exemplo) <= 300, nota.id
    assert len(nota.passos) <= 4, nota.id


def test_toda_novidade_traz_um_exemplo():
    """FR-7427: a capacidade nova se mostra numa cena concreta — "Na prática"."""
    sem = [n.id for n in NOTAS if n.categoria.codigo == "novidade" and not n.exemplo]
    assert not sem, sem


def test_o_destino_e_uma_secao_da_barra():
    """FR-7412: o link segue o predicado da seção, e só seção da barra tem predicado."""
    for nota in NOTAS:
        assert not nota.destino or navegacao.secao_da_rota(nota.destino), (nota.id, nota.destino)


def test_a_ancora_existe_na_documentacao_do_sistema():
    """FR-7422: o "Saiba mais" não leva a uma seção que não existe."""
    ancoras = set(re.findall(r'\bid="([^"]+)"', DOCUMENTACAO.read_text(encoding="utf-8")))
    for nota in NOTAS:
        assert not nota.documentacao or nota.documentacao in ancoras, (nota.id, nota.documentacao)


def test_a_configuracao_existe_e_e_booleana_ou_lista():
    """FR-7410: uma configuração escrita errado esconderia a nota em todo ambiente, sem aviso. A
    lista vale pela presença de item — a dos modelos aprovados do kit, vazia em produção."""
    for item in (*NOTAS, *CATALOGO.capacidades):
        if item.requer_configuracao:
            valor = getattr(settings, item.requer_configuracao, None)
            assert isinstance(valor, bool | tuple | list), item.id


def test_a_capacidade_existe():
    """FR-7411: uma capacidade escrita errado esconderia a nota de todos, sem aviso."""
    conhecidas = {
        permissao
        for _, permissoes in [*PAPEIS.values(), *PAPEIS_DE_ACESSO.values()]
        + list(PAPEIS_INSTITUCIONAIS.values())
        for permissao in permissoes
    }
    for nota in NOTAS:
        for capacidade in nota.para_capacidade:
            assert capacidade in conhecidas, (nota.id, capacidade)


def test_a_spec_citada_existe():
    pastas = {p.name.split("-")[0] for p in SPECS.iterdir() if p.is_dir()}
    for nota in NOTAS:
        for spec in nota.specs:
            assert spec in pastas, (nota.id, spec)


def test_o_registro_da_curadoria_da_a_cada_pr_um_destino_so():
    """FR-7424: o PR deixado sem nota tem motivo, aparece uma vez, e não é também citado."""
    import tomllib

    registro = tomllib.loads((catalogo.ARQUIVO.parent / "curadoria.toml").read_text("utf-8"))
    assert isinstance(registro["inicio"], datetime.date)
    assert registro["inicio"] <= NOTAS[-1].data
    citados = {pr for nota in NOTAS for pr in nota.prs}
    vistos = set()
    for grupo in registro["sem_nota"]:
        assert grupo["motivo"].strip(), grupo
        for pr in grupo["prs"]:
            assert isinstance(pr, int) and pr not in vistos, pr
            assert pr not in citados, f"o PR {pr} tem nota e está dispensado"
            vistos.add(pr)


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
relevancia = "relevante"
titulo = "Título"
resumo = "Resumo."
prs = [1]
specs = []
"""


def test_a_nota_valida_se_le():
    (nota,) = catalogo.ler(VALIDA)
    assert nota.categoria.rotulo == "Nova funcionalidade"
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


def test_o_publico_e_uma_capacidade_ou_uma_lista():
    (uma,) = catalogo.ler(VALIDA + 'para_capacidade = "acesso:consultar"\n')
    assert uma.para_capacidade == ("acesso:consultar",)
    (lista,) = catalogo.ler(VALIDA + 'para_capacidade = ["a:b", "c:d"]\n')
    assert lista.para_capacidade == ("a:b", "c:d")
    with pytest.raises(catalogo.CatalogoInvalido, match="'para_capacidade' deve ser"):
        catalogo.ler(VALIDA + "para_capacidade = [1]\n")


def test_a_falha_de_leitura_se_guarda_ate_o_arquivo_mudar(tmp_path, monkeypatch):
    """A barra não reinterpreta um arquivo inválido a cada tela."""
    arquivo = tmp_path / "novidades.toml"
    arquivo.write_text("[[nota]]\nid = 'x'\n", encoding="utf-8")
    monkeypatch.setattr(catalogo, "ARQUIVO", arquivo)
    catalogo._LIDO.clear()
    lidas = []
    original = catalogo.ler_catalogo
    monkeypatch.setattr(catalogo, "ler_catalogo", lambda texto: lidas.append(1) or original(texto))
    for _ in range(3):
        with pytest.raises(catalogo.CatalogoInvalido):
            catalogo.notas()
    assert len(lidas) == 1
    catalogo._LIDO.clear()


def test_id_repetido_e_recusado():
    with pytest.raises(catalogo.CatalogoInvalido, match="se repete"):
        catalogo.ler(VALIDA + VALIDA)


def test_a_ordem_e_da_mais_recente_para_a_mais_antiga():
    antiga = VALIDA.replace('"uma"', '"outra"').replace("2026-11-10", "2026-11-01")
    catalogo.ler(VALIDA + antiga)
    with pytest.raises(catalogo.CatalogoInvalido, match="da mais recente para a mais antiga"):
        catalogo.ler(antiga + VALIDA)


# ---- as capacidades: o que o GPS já faz (FR-7601 a FR-7606) -----------------------------------

BASE = Path(catalogo.__file__).resolve().parents[1] / "interface" / "templates" / "interface"


def test_toda_nota_tem_relevancia_e_ha_de_cada_peso():
    """FR-7601: a relevância é medida pelo benefício, e as três aparecem no histórico."""
    assert {nota.relevancia for nota in NOTAS} == set(catalogo.RELEVANCIAS)


def test_a_vitrine_tem_no_maximo_dez_capacidades():
    """FR-7602, UX-821: destaque que vira lista longa deixa de destacar."""
    assert 1 <= len(CATALOGO.capacidades) <= 10


@pytest.mark.parametrize("capacidade", CATALOGO.capacidades, ids=lambda c: c.id)
def test_a_capacidade_fala_a_lingua_de_quem_opera(capacidade):
    """FR-7605: o que agora é possível e por que importa, em poucas linhas e sem jargão."""
    assert len(capacidade.titulo) <= 70, capacidade.id
    assert len(capacidade.resumo) <= 240, capacidade.id
    assert len(capacidade.passos) <= 3, capacidade.id
    for texto in (
        capacidade.titulo,
        capacidade.resumo,
        capacidade.como_comecar,
        *capacidade.passos,
    ):
        for regra in (JARGAO, PALAVRAS_DO_SISTEMA):
            achado = regra.search(texto)
            assert not achado, f"{capacidade.id}: {achado.group(0)!r}"


@pytest.mark.parametrize("capacidade", CATALOGO.capacidades, ids=lambda c: c.id)
def test_o_icone_e_o_destino_da_capacidade_existem(capacidade):
    simbolos = (BASE / "base.html").read_text("utf-8") + (BASE / "novidades.html").read_text(
        "utf-8"
    )
    assert f'<symbol id="{capacidade.icone}"' in simbolos, capacidade.id
    assert not capacidade.destino or navegacao.secao_da_rota(capacidade.destino), capacidade.id
    ancoras = set(re.findall(r'\bid="([^"]+)"', DOCUMENTACAO.read_text(encoding="utf-8")))
    assert not capacidade.documentacao or capacidade.documentacao in ancoras, capacidade.id


CAPACIDADE = """
[[capacidade]]
id = "cap"
ordem = 1
icone = "i-pasta"
titulo = "Título"
resumo = "Resumo."
notas = ["uma"]
"""


def test_a_capacidade_valida_se_le_na_ordem():
    outra = CAPACIDADE.replace('"cap"', '"outra"').replace("ordem = 1", "ordem = 0")
    lido = catalogo.ler_catalogo(
        VALIDA
        + CAPACIDADE
        + outra.replace('["uma"]', '["uma-b"]')
        + VALIDA.replace('"uma"', '"uma-b"').replace("2026-11-10", "2026-11-01")
    )
    assert [c.id for c in lido.capacidades] == ["outra", "cap"]
    assert lido.capacidade_da_nota() == {"uma": lido.capacidades[1], "uma-b": lido.capacidades[0]}


@pytest.mark.parametrize(
    ("texto", "mensagem"),
    [
        (CAPACIDADE.replace('["uma"]', '["inexistente"]'), "a nota 'inexistente' não existe"),
        (
            CAPACIDADE + CAPACIDADE.replace('"cap"', '"outra"').replace("ordem = 1", "ordem = 2"),
            "uma nota pertence a uma capacidade só",
        ),
        (CAPACIDADE.replace('icone = "i-pasta"', 'icone = "pasta"'), "'icone' deve ser"),
        (CAPACIDADE.replace("ordem = 1\n", ""), "falta 'ordem'"),
    ],
)
def test_a_capacidade_malformada_e_recusada(texto, mensagem):
    with pytest.raises(catalogo.CatalogoInvalido, match=re.escape(mensagem)):
        catalogo.ler_catalogo(VALIDA + texto)


def test_relevancia_desconhecida_e_recusada():
    with pytest.raises(catalogo.CatalogoInvalido, match="relevância 'enorme'"):
        catalogo.ler(VALIDA.replace('relevancia = "relevante"', 'relevancia = "enorme"'))
