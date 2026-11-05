"""A família UAB/bolsista: os templates da comunicação, em post, story e banner (119, US1, T049).

**Os números vêm dos arquivos da comunicação** (`Editais UAB - {Posts,Story,Site}`): a coluna de
texto à direita da foto, a chamada "Seleção de bolsista" em Anton, o título em Poppins, o período
em Anton e o número do Edital embaixo. As áreas que não recebem texto — a foto, o rabisco, o
cabeçalho, a linha e o rodapé — foram medidas nas imagens de fundo, e entram como obstáculos do
teste geométrico.

**A imagem do banco é o fundo inteiro do slide** (P-1, como na Pós Lato Sensu): o fundo ondulado,
a foto, o rabisco, o endereço do Cefor e o rodapé com os perfis de rede vêm juntos. Dos cinco
exemplos, entram os dois de fundo claro com o rabisco magenta. Os outros três ficam de fora: o de
rabisco verde e o de tom rosa pediriam a chamada numa cor que não passa o contraste AA sobre o fundo
(3,0:1), e os de foto no alto, escuro e mostarda, são outro desenho, com o texto noutra posição e
noutra cor — seriam outro template.

**A chamada é frase fixa aprovada da família** (FR-3814): "Seleção de bolsista", em duas caixas
de uma linha — "SELEÇÃO DE" em marrom e "BOLSISTA" em magenta, como nos slides. A caixa tipográfica
da Anton mede 1,5 corpo, mais que a entrelinha do compositor, e por isso nenhuma caixa em Anton tem
mais de uma linha.

**O que os arquivos dizem e a peça não diz.** "Inscrições até 09 de abril", sem ano, sai como
"Inscrições até DD/MM/AAAA", com a hora e o início (T-1). Os slides não trazem vagas, e a peça
também não: o painel é só o período, como no banner da Pós (EC-6). O título vai em Poppins Bold, e
não na SemiBold dos slides: é o peso do título das famílias da comunicação, e a SemiBold não
mudaria nada que a Bold não mostre.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Caixa, Familia, Imagem, Template

CHAVE = "uab"
#: A unidade da família (FR-3805): as seleções de bolsista da UAB são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "marrom": "#3b2204",
    "magenta": "#bf247a",
    # O tom mais escuro do fundo claro, nas duas imagens: o contraste se mede contra ele, que é
    # o pior caso de todo texto desenhado direto sobre o fundo (D-011). O magenta passa com 4,66:1.
    "fundo": "#eaeaea",
}
FONTES = {
    "titulo": "poppins-negrito",
    "corpo": "poppins-regular",
    "destaque": "anton-regular",
}
# As frases fixas (FR-3814). Nenhuma fala de modalidade, gratuidade ou estado do momento.
FRASES = {
    # A chamada aprovada, "Seleção de bolsista", em duas linhas de cor diferente.
    "chamada": "SELEÇÃO DE",
    "chamada_destaque": "BOLSISTA",
    "ate": "Inscrições até",
    "a_partir": "Inscrições a partir de",
    "inicio": "Início em",
    "horario": "(horário de Brasília)",
    "prorrogado": "PRAZO PRORROGADO",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "todas": "Confira todas na página oficial",
}

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais UAB), 2025"
_LICENCA = "Não verificada: adotada pelo responsável pelo produto em 04/11/2026 (P-1)"


def _imagem(chave, descricao, resumos):
    return Imagem(
        chave=chave,
        descricao=descricao,
        licenca=_LICENCA,
        origem=_ORIGEM,
        arquivos={
            formato: (f"{chave}-{formato}.jpg", resumo)
            for formato, resumo in zip(("post", "story", "banner"), resumos, strict=True)
        },
    )


IMAGENS = (
    _imagem(
        "atendente",
        "foto de um homem sorridente, de fone de ouvido, diante do notebook",
        (
            "990840de22f388547e2d65375b1311c2b15ad41fa9698eed5f3ce389257e8489",
            "9bce5e0af6b8426d5376d9686393e310d8cf2d52b32c16ea3a232b6e4da0a42d",
            "2ff49c9c18cdae56875bb139aa981fb506a0fed14befbf88ad311ef4ee4258b1",
        ),
    ),
    _imagem(
        "escritorio",
        "foto de uma mulher sorridente trabalhando ao computador, num escritório",
        (
            "9869e8aa1e71a11d257d5feab78d08f8710ae7bc3124653799a00197e155faf0",
            "4401ce54f86d5fec374f260707deed1d06276839dbbd636675226dd7acf14a3a",
            "707358a6e0c1496f2ab8608a2550c6758391cdba190d3860cbf6ef6478a4e7f1",
        ),
    ),
)

#: A altura de uma linha, em corpos; a mesma do compositor (`kit_peca.ENTRELINHA`).
_ENTRELINHA = 1.42


def _linhas_por_corpo(corpos, altura):
    return tuple(max(1, math.floor(altura / (corpo * _ENTRELINHA) + 0.01)) for corpo in corpos)


def _chamada(campo, cor, corpo, retangulo):
    return Caixa(campo, "destaque", cor, "fundo", (corpo,), 1, retangulo=retangulo)


def _titulo(retangulo, corpos, alinhamento="start"):
    return Caixa(
        "titulo",
        "titulo",
        "marrom",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        alinhamento=alinhamento,
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _fixa(campo, fonte, corpos, retangulo, alinhamento="start"):
    return Caixa(campo, fonte, "marrom", "fundo", corpos, 1, alinhamento, retangulo=retangulo)


def _painel(destaque, linha, selo, alinhamento="start"):
    """As caixas da pilha do período, do maior ao menor corpo de cada uma.

    Os corpos são os do pior caso — prorrogado, término, hora e início — dentro da altura da pilha:
    a pilha não recai de corpo pela altura, só pela largura.
    """

    def caixa(campo, fonte, corpos, cor="marrom", linhas=1):
        return Caixa(campo, fonte, cor, "fundo", corpos, linhas, alinhamento)

    return (
        caixa("selo_prorrogado", "destaque", selo, cor="magenta"),
        caixa("periodo", "destaque", destaque),
        caixa("hora", "corpo", linha),
        caixa("inicio", "corpo", linha),
        caixa("publicado", "destaque", destaque),
        caixa("consulte", "corpo", linha, linhas=2),
    )


#: As frases fixas que o compositor escreve nas caixas de mesmo nome.
_FRASES_POSICIONADAS = {"chamada": "chamada", "chamada_destaque": "chamada_destaque"}

#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "6590150a267c5accf0ad37b41463d991ed891f2f2ef9d1e3ee33aabc25ecbb85",
        "fefb76c4a72b100e93f66b48306d5e68d9e1987a67b8647da9072c13b63d61e9",
    ),
    ("story", 1): (
        "e098ca4d6231f5c0c4d4000655ac262d397dd9b493affddfcddb1814e10114bc",
        "540d91d5260bfecac255bf578f883e0d64caaed4b15cf9e8e7a57768db12c281",
    ),
    ("banner", 1): (
        "1b22abb4d5255f0a5daa47963d9fe351f6b7a371178fec1580b9146df07504be",
        "0a742699553adfb710fdcf885d72ac912c8c651daad7a22d9eddf806311fac8b",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_ofertas=False,
    caixas=(
        _chamada("chamada", "marrom", 112, (340, 240, 660, 170)),
        _chamada("chamada_destaque", "magenta", 112, (340, 410, 660, 170)),
        _titulo((340, 616, 660, 170), (42, 40, 36, 32, 30, 28)),
        *_painel((46, 42, 38, 34), (28, 26, 24), (30, 28)),
        _fixa("numero", "corpo", (30, 28, 26, 24), (340, 1006, 660, 44)),
        _fixa("chamada_a_acao", "titulo", (28, 26, 24), (340, 1054, 660, 42)),
        _fixa("busca", "titulo", (24,), (340, 1098, 660, 36)),
        _fixa("selo_da_versao", "corpo", (24,), (340, 1136, 660, 36)),
    ),
    dimensoes={
        "painel": {
            "x": 340,
            "largura": 660,
            "base": 1000,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 786,
            "espaco": 8,
            "raio": 0,
            "cor": None,
            "itens": ("periodo",),
        },
        "frases_posicionadas": _FRASES_POSICIONADAS,
        "obstaculos": {
            "cabecalho": (108, 85, 975, 155),
            "foto": (0, 200, 300, 1030),
            "rabisco": (870, 495, 1080, 612),
            "rodape": (108, 1210, 975, 1310),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="uab/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_ofertas=False,
    caixas=(
        _chamada("chamada", "marrom", 110, (510, 470, 490, 160)),
        _chamada("chamada_destaque", "magenta", 110, (510, 640, 490, 160)),
        _titulo((120, 1000, 840, 215), (50, 46, 42, 38, 34, 30, 28), "middle"),
        *_painel((54, 50, 46, 42), (32, 30, 28), (36, 32), "middle"),
        _fixa("numero", "corpo", (34, 32, 30, 28), (120, 1490, 840, 50), "middle"),
        _fixa("chamada_a_acao", "titulo", (30, 28), (120, 1544, 840, 44), "middle"),
        _fixa("busca", "titulo", (24,), (120, 1590, 840, 36), "middle"),
        _fixa("selo_da_versao", "corpo", (24,), (120, 1628, 840, 36), "middle"),
    ),
    dimensoes={
        "painel": {
            "x": 120,
            "largura": 840,
            "base": 1480,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 1225,
            "espaco": 10,
            "raio": 0,
            "cor": None,
            "itens": ("periodo",),
        },
        "frases_posicionadas": _FRASES_POSICIONADAS,
        "obstaculos": {
            "foto": (0, 245, 480, 995),
            "rabisco": (780, 850, 1080, 990),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="uab/story",
    resumo_das_referencias=RESUMOS[("story", 1)][0],
)

BANNER = Template(
    familia=CHAVE,
    formato=kit_formatos.BANNER,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_ofertas=False,
    caixas=(
        # Numa linha só, como no site: "BOLSISTA" começa onde "SELEÇÃO DE " termina na Anton.
        _chamada("chamada", "marrom", 80, (640, 60, 360, 124)),
        _chamada("chamada_destaque", "magenta", 80, (1000, 60, 300, 124)),
        _titulo((640, 196, 800, 130), (40, 36, 32, 30, 28)),
        *_painel((44, 40, 36, 32), (28,), (34, 30)),
        _fixa("numero", "corpo", (30, 28), (640, 606, 800, 44)),
        _fixa("chamada_a_acao", "titulo", (28,), (640, 652, 400, 42)),
        _fixa("busca", "titulo", (28,), (1040, 652, 400, 42), "end"),
        _fixa("selo_da_versao", "corpo", (28,), (640, 696, 800, 42)),
    ),
    dimensoes={
        "painel": {
            # Mais estreito que a coluna: o rabisco desce até 446 px a partir de x = 1144.
            "x": 640,
            "largura": 490,
            "base": 600,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 340,
            "espaco": 6,
            "raio": 0,
            "cor": None,
            "itens": ("periodo",),
        },
        "frases_posicionadas": _FRASES_POSICIONADAS,
        "obstaculos": {
            "foto": (0, 110, 605, 725),
            "rabisco": (1140, 350, 1500, 450),
            "linha": (68, 758, 885, 772),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="uab/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="UAB/bolsista",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos={},
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    pasta="uab",
)
