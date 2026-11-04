"""A família Pós Lato Sensu: os templates da comunicação, em post, story e banner (119, US1).

**Os números vêm dos arquivos da comunicação** (`Editais Pós Lato Sensu - {Posts,Story,Site}`):
a posição e o corpo do título, do número, do retângulo amarelo de altura variável e do balão da
chamada são os dos slides, convertidos para px (o banner, ao dobro do arquivo; `D-007`). As áreas
que não recebem texto — a foto, o "CURSO", os pontos, as barras e o rodapé — foram medidas nas
imagens de fundo, e entram como obstáculos do teste geométrico.

**A imagem do banco é o fundo inteiro do slide** (P-1, decisão do responsável pelo produto em
04/11/2026: "o mais próximo do template possível"): o padrão em chevron, a foto, o "CURSO" e o
rodapé com os perfis de rede vêm juntos, como a comunicação os montou. Cada uma das cinco fotos tem
um arquivo por formato.

**O que os arquivos dizem e a peça não diz.** "Modalidade a distância", "Vagas remanescentes" e
"Inscrições até 09/11" sem ano ficam de fora (T-1, T-3, FR-3814): o período sai com ano, hora e
início, e nenhuma frase fixa afirma modalidade. O título sai como o Edital o escreveu, e não em
maiúsculas.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Ativo, Caixa, Familia, Imagem, Template

CHAVE = "pos-lato-sensu"
#: A unidade da família (FR-3805): os Editais de Pós Lato Sensu são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "amarelo": "#f3b514",
    "roxo": "#450460",
    "roxo_da_chamada": "#5d299c",
    "branco": "#ffffff",
    # O tom mais claro do padrão em chevron do fundo: o contraste se mede contra ele, que é o
    # pior caso de todo texto desenhado direto sobre o fundo (D-011).
    "fundo": "#662f7d",
}
FONTES = {
    "titulo": "poppins-negrito",
    "corpo": "poppins-regular",
    "destaque": "poppins-negrito",
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
    # Desenhada na imagem de fundo, e registrada aqui para a varredura a ler.
    "na_imagem": "CURSO",
}

ATIVOS = {
    "balao": Ativo(
        "balao.png",
        "77f6a444715f41bfa7d13ddfe414e65342c1e309027f26640b60befaf26f1cdc",
        "Balão de fala com contorno roxo e fundo branco",
    ),
}

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais Pós Lato Sensu), 2025"
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
        "fone",
        "foto de uma estudante sorridente, de fone de ouvido, escrevendo diante do notebook",
        (
            "7fa5bceb7993ecdf64deadd4da222a0b75f2a4b68e0b90eecbac00c9cd5fafce",
            "a5e0d9124d474b89b49ec20c1d4f1b4753ca356b721d178aa4818786bd97d870",
            "c8fbeef29c67a4eab16dd9affb3c9725cda27c208d3855f99e2fecfb1b9fc635",
        ),
    ),
    _imagem(
        "grupo",
        "foto de um grupo de estudantes reunidos em volta de um notebook",
        (
            "d110cd89930961f673226b3cb0208ba9c7185cee16f9a36d93df32e543a4aff1",
            "cee2fb6b4fdb6328d8bb53a26bd618e1d9e54e3d2e12c4f84578bde9d191bd2f",
            "4ac01dcfc80df75e7e0c98cc10ef1fed533ba327d49ef17e0caba927eefd13b3",
        ),
    ),
    _imagem(
        "fone-anotando",
        "foto de um estudante de fone de ouvido fazendo anotações diante do computador",
        (
            "08904140721322e1d041f216240de1dc52ea8d07f2ef6a21dabc626349c6d65d",
            "dfbded50b43c2182e3ad16b08e1d6e426d1b9b96be0966a940a8aaea0d416ac1",
            "20e70781c915436d8bea6fe2cf0248f1fa173c0994e07104eb4291f72db3c913",
        ),
    ),
    _imagem(
        "biblioteca",
        "foto de um estudante sorridente lendo num tablet, em frente a estantes de livros",
        (
            "5064c796e6996c42aa0a6d7cb481d076fa412cb7aedecfb80716449902e41942",
            "c9958c65d16a358285350af45b37cd76a165ae0f3cbd6926c5921ea25593f051",
            "881a4bbde344c36d6abbb806435618f9bdec82ab48787161bb4b525e5e66c384",
        ),
    ),
    _imagem(
        "escrevendo",
        "foto de uma estudante escrevendo num caderno, com o notebook ao lado",
        (
            "c36ae77ef4f23aa30dc26e7030d03f093e7ff7526b175ed0de45b54cacb5a2c0",
            "e8e70417eab9caa6580ea06ae9abae9f2d23e39850e48d8ad059e27805400c71",
            "74291d1466f5b9c801e2fe7fa940c9beb03b9c90c80dd7f365b897a864531470",
        ),
    ),
)

#: A altura de uma linha, em corpos; a mesma do compositor (`kit_peca.ENTRELINHA`).
_ENTRELINHA = 1.42


def _linhas_por_corpo(corpos, altura):
    return tuple(max(1, math.floor(altura / (corpo * _ENTRELINHA) + 0.01)) for corpo in corpos)


def _titulo(retangulo, corpos):
    return Caixa(
        "titulo",
        "titulo",
        "amarelo",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _no_fundo(campo, fonte, corpos, retangulo, alinhamento="start"):
    return Caixa(campo, fonte, "branco", "fundo", corpos, 1, alinhamento, retangulo=retangulo)


def _no_painel(campo, fonte, corpos, linhas=1):
    return Caixa(campo, fonte, "roxo", "amarelo", corpos, linhas)


def _chamada(retangulo, corpos):
    return Caixa(
        "chamada_a_acao",
        "destaque",
        "roxo_da_chamada",
        "branco",
        corpos,
        1,
        "middle",
        retangulo=retangulo,
    )


def _painel(periodo, linha, menor):
    """As caixas do painel, do maior ao menor corpo de cada uma."""
    return (
        _no_painel("selo_prorrogado", "destaque", menor),
        _no_painel("periodo", "destaque", periodo),
        _no_painel("hora", "corpo", linha, 2),
        _no_painel("inicio", "corpo", linha),
        _no_painel("publicado", "destaque", periodo),
        _no_painel("consulte", "corpo", linha, 2),
        _no_painel("total", "destaque", linha),
        _no_painel("oferta", "corpo", linha, 3),
        _no_painel("contagem", "destaque", periodo),
        _no_painel("todas", "corpo", menor, 2),
    )


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "10e136b683d699424e3f5967f2837f556d86893a8592e25211cbee3f7d7f0a6c",
        "bfcb25490b8e4861ae2fef63aae010561049edb2a6da8531513545b72282dc54",
    ),
    # A 2 lista as opções no corpo mínimo antes de resumir (FR-3836): o story de dois polos, que
    # na 1 saía com o total, passou a listá-los. Post e banner não mudaram de peça.
    ("story", 2): (
        "f4e16a2cf434cd62b03b3be9f76ccbf84c9ec6959d1f931fdf3225b4f26ab297",
        "8a16aef0abbdd69d76215765ba54d785cd46e69496e0f541902eba7287101e4d",
    ),
    ("banner", 1): (
        "57cbd239100d5068f5602682e3f78259931fd6f0c2faedf7d6238ce4da2a04f3",
        "1badbdf0cb9309eea6119c21d5c4b8511ded17db677fb8ecc33049130607c001",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        _titulo((285, 117, 715, 328), (57, 52, 48, 44, 40, 36, 32)),
        _no_fundo("numero", "corpo", (39, 36, 32, 28, 24), (86, 640, 420, 60)),
        *_painel((37, 34, 32, 30, 28), (26, 24), (24,)),
        _chamada((184, 1080, 381, 60), (32, 30, 28, 26, 24)),
        _no_fundo("busca", "destaque", (26, 24), (86, 1170, 780, 37)),
        _no_fundo("selo_da_versao", "corpo", (24,), (86, 1208, 780, 34)),
    ),
    dimensoes={
        "painel": {
            "x": 98,
            "largura": 587,
            "base": 1129,
            "recuo": 30,
            # O balão cobre o pé do painel, como nos slides: o texto termina antes dele.
            "recuo_em_baixo": 114,
            "topo_minimo": 710,
            "espaco": 6,
            "raio": 28,
            "cor": "amarelo",
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "balao", "retangulo": (120, 1027, 533, 137)},
        "obstaculos": {
            "barras_do_alto": (127, 0, 194, 180),
            "curso": (111, 287, 249, 316),
            "pontos": (112, 361, 236, 477),
            "foto": (510, 454, 1080, 1145),
            "barras_de_baixo": (882, 1175, 944, 1350),
            "rodape": (109, 1258, 821, 1311),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(510, 454, 1080, 1145),
    pasta_das_referencias="pos-lato-sensu/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=2,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        _titulo((318, 253, 682, 380), (66, 60, 56, 52, 48, 44, 40, 36, 32)),
        _no_fundo("numero", "corpo", (39, 36, 32, 28, 24), (119, 870, 380, 55)),
        *_painel((47, 44, 40, 36, 32, 28), (32, 30, 28, 26, 24), (28, 26, 24)),
        _chamada((221, 1520, 476, 80), (39, 36, 32, 28)),
        _no_painel("busca", "destaque", (28, 26, 24)),
        _no_painel("selo_da_versao", "corpo", (24,)),
    ),
    dimensoes={
        "painel": {
            # Mais largo que o do slide (119 a 763): o selo da versão tem de caber numa linha com
            # qualquer referência — "a" é o dígito hexadecimal mais largo da Poppins, e oito dele
            # medem 592 px a 24 px; quebrar ou não conforme a impressão mudaria a peça de altura.
            "x": 100,
            "largura": 680,
            "base": 1580,
            "recuo": 32,
            "recuo_em_baixo": 140,
            "topo_minimo": 945,
            "espaco": 8,
            "raio": 32,
            "cor": "amarelo",
            "itens": ("periodo", "ofertas", "busca", "selo_da_versao"),
        },
        "balao": {"ativo": "balao", "retangulo": (171, 1456, 592, 168)},
        "obstaculos": {
            "curso": (112, 421, 247, 449),
            "pontos": (112, 496, 234, 697),
            "foto": (510, 670, 1080, 1356),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(510, 670, 1080, 1356),
    pasta_das_referencias="pos-lato-sensu/story",
    resumo_das_referencias=RESUMOS[("story", 2)][0],
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
        _titulo((286, 60, 620, 260), (51, 48, 44, 40, 36, 32, 28)),
        _no_fundo("numero", "corpo", (32, 30, 28), (286, 328, 290, 46)),
        *_painel((36, 32, 28), (28,), (28,)),
        _chamada((615, 385, 290, 46), (30, 28)),
        _no_painel("busca", "destaque", (28,)),
        _no_painel("selo_da_versao", "corpo", (28,)),
    ),
    dimensoes={
        "painel": {
            "x": 102,
            "largura": 780,
            "base": 812,
            "recuo": 24,
            "recuo_em_baixo": 24,
            "topo_minimo": 470,
            "espaco": 6,
            "raio": 24,
            "cor": "amarelo",
            "itens": ("periodo", "busca", "selo_da_versao"),
        },
        "balao": {"ativo": "balao", "retangulo": (580, 350, 360, 110)},
        "obstaculos": {
            "barras_do_alto": (98, 0, 190, 170),
            "curso": (109, 236, 207, 259),
            "pontos": (111, 289, 196, 429),
            "foto": (948, 98, 1500, 716),
            "barras_de_baixo": (1304, 724, 1380, 850),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(948, 98, 1500, 716),
    pasta_das_referencias="pos-lato-sensu/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="Pós Lato Sensu",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos=ATIVOS,
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    pasta="pos-lato-sensu",
)
