"""A família TMD (Técnico em Multimeios Didáticos): post, story e banner (119, T052).

**Os números vêm dos arquivos da comunicação** (`Editais TMD - {Posts,Story,Site}`): o roxo, o
dourado, o branco e as fontes são os dos slides, e as caixas seguem a disposição deles, em px (o
banner, ao dobro do arquivo; `D-007`): o título em Archivo Black dourado, alinhado à esquerda, no
alto; o prazo centrado em leve; a chamada dourada na barra roxa com o elo.

**A Helvetica Neue dos slides é a Inter** (P-2, decisão do responsável pelo produto em 05/11/2026):
a leve no prazo, como o "Até o dia 30 de abril" do slide, e a regular no resto. O slide escreve
"INSCRIÇÕES ABERTAS" em negrito acima do prazo; a peça não afirma que as inscrições estão abertas
(T-1), e o negrito não tem onde entrar.

**Sem banco de imagens** (EC-20): a família não pede imagem, e a peça sai com o fundo fixo de cada
formato (`dimensoes["fundo_fixo"]`). O fundo dos slides traz uma ilustração plana de banco — a
pessoa diante do tablet —, de licença não conferida; o daqui é desenho próprio, só formas
geométricas, feito por `scripts/desenhar_fundo_do_tmd.py`, nas cores e na disposição do slide. Os
obstáculos abaixo são as medidas daquele roteiro: a ilustração no alto à direita e a colina lilás
embaixo, com a barra da chamada como vão. Todo texto fica sobre o roxo liso: o branco sobre o lilás
da colina dá 4,48, abaixo do AA (D-011).

**O que os slides dizem e a peça não diz.** "CURSO TÉCNICO EM MULTIMEIOS DIDÁTICOS" é o título do
slide; aqui, o título sai como o Edital o escreveu (FR-3814, T-3). "acesse o link na bio e
inscreva-se" é a chamada do formato.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Ativo, Caixa, Familia, Template

CHAVE = "tmd"
#: A unidade da família (FR-3805): os Editais do TMD dos templates são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "dourado": "#d6d58e",
    "branco": "#ffffff",
    # O roxo liso do fundo, o dos slides lido do pixel: todo texto é medido contra ele (D-011).
    "fundo": "#5d299c",
}
FONTES = {
    "titulo": "archivo-black",
    "corpo": "inter-regular",
    "destaque": "inter-leve",
}
# As frases fixas (FR-3814). Nenhuma fala de modalidade, gratuidade ou estado do momento.
FRASES = {
    "ate": "Inscrições até",
    "a_partir": "Inscrições a partir de",
    "inicio": "Início em",
    "horario": "(horário de Brasília)",
    "prorrogado": "PRAZO PRORROGADO",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "todas": "Confira todas na página oficial",
    # Desenhados no rodapé do fundo do post e do story, e registrados aqui para a varredura os ler.
    "na_imagem": "ifescefor · Ifes Cefor",
}

_FUNDO = (
    "Fundo roxo com uma colina lilás, asteriscos turquesa, a barra da chamada com um elo dourado e "
    "a ilustração de um tablet com uma aula em vídeo e uma lâmpada"
)
ATIVOS = {
    "fundo_post": Ativo(
        "fundo-post.png",
        "042402bbfd6a749f937157da80d56be6728e859ccae4404617231dddf007c764",
        f"{_FUNDO}; no rodapé, os perfis de rede e a marca do Cefor",
    ),
    "fundo_story": Ativo(
        "fundo-story.png",
        "4a43c5a0a44e6f0a161ea3428d241d7b655410c22dbc5ba5ec1968c093d838e6",
        f"{_FUNDO}; no rodapé, os perfis de rede e a marca do Cefor",
    ),
    "fundo_banner": Ativo(
        "fundo-banner.png",
        "06adfd4812793ca7779beb577ce90832ec1d478bc66f8b6f79422a2ad8d643f7",
        _FUNDO,
    ),
}

#: A altura de uma linha, em corpos; a mesma do compositor (`kit_peca.ENTRELINHA`).
_ENTRELINHA = 1.42


def _linhas_por_corpo(corpos, altura):
    return tuple(max(1, math.floor(altura / (corpo * _ENTRELINHA) + 0.01)) for corpo in corpos)


def _titulo(retangulo, corpos):
    return Caixa(
        "titulo",
        "titulo",
        "dourado",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        alinhamento="start",
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _posicionada(campo, fonte, cor, corpos, retangulo, alinhamento="start"):
    return Caixa(campo, fonte, cor, "fundo", corpos, 1, alinhamento, retangulo=retangulo)


def _no_fundo(campo, fonte, corpos, linhas=1):
    """Um item do painel: sem cor, centrado em branco sobre o roxo, como o prazo do slide."""
    return Caixa(campo, fonte, "branco", "fundo", corpos, linhas, "middle")


def _painel(periodo, linha, menor):
    return (
        _no_fundo("selo_prorrogado", "corpo", menor),
        _no_fundo("periodo", "destaque", periodo),
        _no_fundo("hora", "corpo", linha, 2),
        _no_fundo("inicio", "corpo", linha),
        _no_fundo("publicado", "destaque", periodo),
        _no_fundo("consulte", "corpo", linha, 2),
        _no_fundo("total", "corpo", linha),
        _no_fundo("oferta", "corpo", linha, 2),
        _no_fundo("contagem", "corpo", linha),
        _no_fundo("todas", "corpo", menor, 2),
        _no_fundo("busca", "corpo", menor),
        _no_fundo("selo_da_versao", "corpo", menor, 2),
    )


def _painel_sem_cor(x, largura, base, topo_minimo, espaco):
    return {
        "x": x,
        "largura": largura,
        "base": base,
        "recuo": 0,
        "recuo_em_baixo": 0,
        "topo_minimo": topo_minimo,
        "espaco": espaco,
        "raio": 0,
        "cor": None,
        "itens": ("periodo", "ofertas", "busca", "selo_da_versao"),
    }


def _colina(topo, barra, base):
    """A colina e a barra da chamada como vão: quatro retângulos em volta da barra."""
    x, y, largura, altura = barra
    return {
        "colina_em_cima": (0, topo, base[0], y),
        "colina_a_esquerda": (0, y, x, y + altura),
        "colina_a_direita": (x + largura, y, base[0], y + altura),
        "colina_embaixo": (0, y + altura, base[0], base[1]),
    }


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "aea020b1f1e440d17cc79af0f07f89b2cb02fba0aaa1363b377e2247ea2d28e6",
        "9a544f2f3d142da84b24348e29cfb7f1103ae83d243afc14463aaa9d3c950345",
    ),
    ("story", 1): (
        "e38f9b75280c7479657cf09dc5d3c6e23bad0df32c44f1907c2eb6add9d92c54",
        "82ecc2986f9870eedce31f0a09d14b9af0e787fe757aabb8baf932f460d5c2e7",
    ),
    ("banner", 1): (
        "7c3cba1a688c99c0895627762fbdccf1f448b6f31a5249b67179434bdd12e660",
        "19a61ab2cb538beee245bb71d03385588d65cf2f70d6d4cc57af8a244de8434b",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        # À esquerda da ilustração, como o título do slide.
        _titulo((80, 80, 560, 330), (64, 60, 56, 52, 48, 44, 40, 36, 32, 30, 28)),
        _posicionada("numero", "destaque", "branco", (36, 34, 32, 30, 28), (80, 420, 560, 52)),
        *_painel((40, 36, 32, 30, 28, 26, 24), (28, 26, 24), (24,)),
        # Na barra roxa, depois do elo, como no slide.
        _posicionada("chamada_a_acao", "corpo", "dourado", (32, 30, 28), (300, 1108, 570, 56)),
    ),
    dimensoes={
        "fundo_fixo": "fundo_post",
        "painel": _painel_sem_cor(80, 920, 975, 540, 4),
        "obstaculos": {
            "ilustracao": (650, 70, 1080, 530),
            "elo": (205, 1100, 285, 1172),
            **_colina(985, (190, 1095, 700, 82), (1080, 1350)),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="tmd/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        _titulo((80, 270, 540, 360), (72, 64, 60, 56, 52, 48, 44, 40, 36, 32, 28)),
        _posicionada("numero", "destaque", "branco", (44, 40, 36, 32, 28), (80, 650, 540, 62)),
        *_painel((52, 48, 44, 40, 36, 32, 28, 26, 24), (32, 30, 28, 26, 24), (28, 26, 24)),
        _posicionada("chamada_a_acao", "corpo", "dourado", (36, 32, 30, 28), (290, 1556, 600, 58)),
    ),
    dimensoes={
        "fundo_fixo": "fundo_story",
        "painel": _painel_sem_cor(80, 920, 1440, 740, 6),
        "obstaculos": {
            "ilustracao": (630, 255, 1080, 740),
            "elo": (185, 1545, 265, 1625),
            **_colina(1455, (170, 1540, 740, 90), (1080, 1920)),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="tmd/story",
    resumo_das_referencias=RESUMOS[("story", 1)][0],
)

BANNER = Template(
    familia=CHAVE,
    formato=kit_formatos.BANNER,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    # O banner não tem bloco de ofertas (EC-6): nele, nenhuma quantidade nem carga horária.
    tem_ofertas=False,
    caixas=(
        _titulo((60, 60, 880, 200), (64, 60, 56, 52, 48, 44, 40, 36, 32, 28)),
        _posicionada("numero", "destaque", "branco", (40, 36, 32, 28), (60, 270, 880, 54)),
        *_painel((44, 40, 36, 32, 28), (30, 28), (28,)),
        _posicionada("chamada_a_acao", "corpo", "dourado", (34, 32, 30, 28), (540, 718, 500, 54)),
    ),
    dimensoes={
        "fundo_fixo": "fundo_banner",
        "painel": _painel_sem_cor(60, 880, 650, 336, 6),
        "obstaculos": {
            "ilustracao": (990, 80, 1460, 545),
            "elo": (455, 710, 530, 780),
            **_colina(655, (440, 705, 620, 80), (1500, 850)),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="tmd/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="TMD",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos=ATIVOS,
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    pasta="tmd",
)
