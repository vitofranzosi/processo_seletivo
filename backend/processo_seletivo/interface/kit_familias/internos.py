"""A família Internos: os templates da comunicação, em post, story e banner (119, T051).

**Os números vêm dos arquivos da comunicação** (`Editais Internos - {Posts,Story,Site}`): o
verde, as fontes e a posição do texto são os dos slides; o resto foi medido nas duas imagens de
fundo de cada formato. Os fundos têm as fotos recortadas em losango no alto, o losango verde-claro
embaixo à esquerda, as listras à direita e as faixas de verde mais claro no pé. O texto fica no
verde escuro que sobra entre eles, uma faixa diagonal, e os obstáculos declarados são a união das
duas imagens, em degraus que acompanham a diagonal: o texto fica no mesmo lugar com qualquer foto
(FR-3827).

**Duas variantes, e não dois templates** (EC-19, cenário 23): "servidores" e "estudantes" diferem
só na chamada fixa, no alto da coluna. Os arquivos da comunicação têm uma arte para cada público, e
as duas artes diferem só nas fotos; aqui as fotos são o banco de imagens, escolhido à parte, como em
toda família. Os slides não escrevem a chamada — o público estava no título de exemplo, "Seleção de
Orientador de TCC…", "Processo seletivo: Auxílio Estudantil…" —, e a peça a escreve porque o título
é o do Edital, e o Edital não diz o público em campo publicado.

**A Helvetica Neue dos slides é a Inter** (P-2, decisão do responsável pelo produto em 05/11/2026),
como na Libras: o título em negrito, o horário e o selo na regular. O número e o prazo ficam na
Unbounded negrita, como no slide ("Edital 56/2025 / Inscrições até / 25 maio"), e a chamada e a
chamada à ação na Unbounded regular ("PARA MAIS INFORMAÇÕES, ACESSE O EDITAL").

**Tudo em branco, sobre o verde escuro, e alinhado à esquerda** ("Mantenha alinhado à esquerda",
dizem os slides de orientação). O slide põe o número e o prazo em preto dentro do losango
verde-claro, e a peça não: o losango comporta "25 maio", e não "Inscrições até DD/MM/AAAA" com a
hora e o início (T-1), que pediriam o corpo abaixo do mínimo. A coluna tem duas margens, como o
slide (título a 312 px, chamada à ação a 479 px no story): o verde escuro se estreita para baixo.

**O que os slides dizem e a peça não diz.** Os slides não trazem vagas, e a peça também não: o
painel é o período, a busca e o selo, como na UAB (EC-6). "PARA MAIS INFORMAÇÕES, ACESSE O EDITAL"
é a chamada do slide; aqui vale a do formato, como nas outras famílias.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import (
    OMITIR,
    Caixa,
    Familia,
    Imagem,
    Template,
    Variante,
)

CHAVE = "internos"
#: A unidade da família (FR-3805): os Editais internos dos templates são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "branco": "#ffffff",
    # O tom mais claro do verde escuro, lido nas seis imagens dentro das caixas de texto: o pior
    # caso do branco, que passa com 6,6:1 (D-011).
    "fundo": "#156b2e",
}
FONTES = {
    "titulo": "inter-negrito",
    "corpo": "inter-regular",
    "destaque": "unbounded-negrito",
    "rotulo": "unbounded-regular",
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
    # Desenhados no rodapé das imagens do post e do story, e registrados aqui para a varredura.
    "na_imagem": "ifescefor · Ifes Cefor",
}
#: A chamada de cada variante, frase fixa sujeita à FR-3814: verdadeira para todo Edital interno
#: dirigido àquele público, e só isso.
VARIANTES = (
    Variante("servidores", "Servidores", "Seleção para servidores"),
    Variante("estudantes", "Estudantes", "Seleção para estudantes"),
)

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais Internos), 2025"
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
        "servidores",
        "fotos em losango de uma servidora sorridente ao computador, de uma colega com um tablet e "
        "de uma sala de trabalho com computadores",
        (
            "ce0cb4aa10fef8ec87e3d38ab0437ac6452fd682409217a3823550221bd61dd6",
            "183aeabb05eb97e996eb139aa5565d808c3449923250b9b1b1a256d7b39eed19",
            "115cf684b64149c03cc8a38f106a0cb86b107767d5bd3ead7a731fe2246f6778",
        ),
    ),
    _imagem(
        "estudantes",
        "fotos em losango de estudantes sorrindo com pastas coloridas, de um estudante ao "
        "computador e de uma sala com computadores",
        (
            "ea892c6e6a410b625abfdac6ca644d8a5151d6bbabc5c8f5c0a8d1945e8d8774",
            "6c5358323a9ba61a9c862e6c36f9e090aece711c7d3560eb3f050fbfc29e657b",
            "d779e646dfc1ba21f46c675072bf2c8d88daaa113e387f352b30c6623a42bb31",
        ),
    ),
)

#: A altura de uma linha, em corpos; a mesma do compositor (`kit_peca.ENTRELINHA`). A caixa
#: tipográfica da Inter (0,969 + 0,241) e a da Unbounded (0,995 + 0,245) cabem nela.
_ENTRELINHA = 1.42


def _linhas_por_corpo(corpos, altura):
    return tuple(max(1, math.floor(altura / (corpo * _ENTRELINHA) + 0.01)) for corpo in corpos)


def _titulo(retangulo, corpos):
    return Caixa(
        "titulo",
        "titulo",
        "branco",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _posicionada(campo, fonte, corpos, retangulo):
    return Caixa(campo, fonte, "branco", "fundo", corpos, 1, retangulo=retangulo)


def _painel(periodo, linha, *, hora=None, busca=None, linhas_do_periodo=2):
    """As caixas da pilha do período, da busca e do selo, do maior ao menor corpo de cada uma.

    Os corpos são os do pior caso — prorrogado, término, hora, início, busca e selo em duas linhas —
    dentro da altura do painel: a pilha não recai de corpo pela altura, só pela
    largura. A hora tem largura fixa ("às HHhMM (horário de Brasília)"), e fica numa linha.
    """

    def caixa(campo, fonte, corpos, linhas=1):
        return Caixa(campo, fonte, "branco", "fundo", corpos, linhas)

    menor = linha[-1:]
    return (
        caixa("selo_prorrogado", "destaque", menor),
        caixa("periodo", "destaque", periodo, linhas_do_periodo),
        caixa("hora", "corpo", hora or menor),
        caixa("inicio", "corpo", linha),
        caixa("publicado", "destaque", periodo),
        caixa("consulte", "corpo", linha, 2),
        caixa("busca", "titulo", busca or linha, 2),
        caixa("selo_da_versao", "corpo", menor, 2),
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
        "itens": ("periodo", "busca", "selo_da_versao"),
    }


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "50ed7464ad21585d6ce80186f3f33567f7a3c46abde4ecbe91f644cd6b450cc9",
        "9818523a0de02e0db4c0a3025b1fc7543d48a09a07f920edecc670d295f99f71",
    ),
    ("story", 1): (
        "89686f8091fb655514a8a198f85bd88b3db993fc0f1687c237af37cc02c6a707",
        "c9737cbea0fd9b46efc0da34922f7ff6751aa1069869c16cc649ecf58b7aca81",
    ),
    ("banner", 1): (
        "2dde455fc0bf01754d5ea785fd926778d89fa61cda99b50f56d42618ce8278d1",
        "ecf22fd996e907ce26ed55e3e7aac30b96cf9085c85394d52affd234ae1fba94",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_ofertas=False,
    # Uma coluna só, a 490 px: o verde escuro acaba em 467 px à esquerda, no losango, e em 922 px
    # à direita, nas listras.
    caixas=(
        _posicionada("chamada", "rotulo", (26, 24), (490, 500, 430, 40)),
        _titulo((490, 548, 430, 196), (40, 36, 32, 30, 28, 26, 24)),
        _posicionada("numero", "destaque", (32, 30, 28, 26, 24), (490, 750, 430, 46)),
        *_painel((30, 28, 26, 24), (24,)),
        # Abaixo do painel, onde o verde escuro já se estreitou para 340 px.
        _posicionada("chamada_a_acao", "rotulo", (26, 24), (490, 1106, 340, 40)),
    ),
    dimensoes={
        "painel": _painel_sem_cor(490, 400, 1100, 798, 2),
        "obstaculos": {
            "fotos": (0, 0, 1080, 498),
            "foto_da_esquerda": (0, 498, 447, 680),
            "foto_da_direita": (941, 498, 1080, 540),
            "listras": (922, 540, 1080, 1000),
            "losango": (0, 740, 467, 1150),
            "faixa_da_direita": (927, 1000, 1080, 1100),
            "faixa_da_direita_embaixo": (834, 1100, 1080, 1150),
            "rodape": (0, 1150, 1080, 1350),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="internos/post",
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
        # A primeira margem, a 350 px, como o título do slide: abaixo das fotos, acima do losango.
        _posicionada("chamada", "rotulo", (30, 28, 26), (350, 846, 470, 44)),
        _titulo((350, 896, 470, 270), (48, 44, 40, 36, 32, 30, 28)),
        _posicionada("numero", "destaque", (38, 36, 34, 32, 30, 28), (350, 1172, 470, 56)),
        # A segunda, a 480 px, como a chamada à ação do slide: à direita do losango.
        *_painel((34, 32, 30, 28, 26, 24), (26, 24), hora=(24,), busca=(26, 24)),
        _posicionada("chamada_a_acao", "rotulo", (32, 30, 28, 26), (480, 1604, 400, 50)),
    ),
    dimensoes={
        "painel": _painel_sem_cor(480, 356, 1596, 1236, 4),
        "obstaculos": {
            "fotos": (0, 0, 1080, 840),
            "foto_da_esquerda": (0, 840, 321, 880),
            "listras": (828, 840, 1080, 1240),
            "losango": (0, 1220, 468, 1670),
            "faixa_da_direita": (840, 1240, 1080, 1360),
            "faixa_da_direita_embaixo": (900, 1360, 1080, 1600),
            "faixa_do_pe": (943, 1600, 1080, 1670),
            "rodape": (0, 1670, 1080, 1920),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="internos/story",
    resumo_das_referencias=RESUMOS[("story", 1)][0],
)

BANNER = Template(
    familia=CHAVE,
    formato=kit_formatos.BANNER,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_ofertas=False,
    # No banner as fotos e o losango ficam à esquerda, e a coluna, à direita deles, desce do alto:
    # o título do slide começa em 405 px, mas embaixo dele o verde escuro só comporta a chamada à
    # ação, e a busca e o selo sobem para o painel.
    caixas=(
        _posicionada("chamada", "rotulo", (30, 28), (810, 62, 520, 44)),
        _titulo((810, 110, 520, 130), (40, 36, 32, 30, 28)),
        _posicionada("numero", "destaque", (30, 28), (810, 244, 520, 46)),
        # O término numa linha, no 30, e só o "a partir de", mais longo, em duas: o painel não
        # comporta o término em duas linhas junto da prorrogação, da busca e do selo.
        *_painel((32, 30, 28), (28,), linhas_do_periodo=(1, 1, 2)),
        _posicionada("chamada_a_acao", "rotulo", (32, 30, 28), (810, 606, 400, 46)),
    ),
    dimensoes={
        "painel": _painel_sem_cor(810, 520, 600, 292, 4),
        "obstaculos": {
            "fotos": (0, 0, 605, 120),
            "fotos_e_losango": (0, 120, 800, 340),
            "losango": (0, 340, 773, 850),
            "listras": (1340, 0, 1500, 600),
            "faixa_da_direita": (1238, 600, 1500, 660),
            "faixas_de_baixo": (773, 660, 1500, 850),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="internos/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="Internos",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos={},
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    variantes=VARIANTES,
    pasta="internos",
)
