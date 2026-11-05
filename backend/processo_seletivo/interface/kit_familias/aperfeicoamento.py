"""A família Aperfeiçoamento: os templates da comunicação, em post, story e banner (119, T050).

**Os números vêm dos arquivos da comunicação** (`Editais Pós Aperfeiçoamento - Posts Intagram`,
`Pós Aperfeiçoamento - Story Intagram`, `Editais de Aperfeiçoamento - Site Cefor`): a foto presa por
clipe, o selo "PROCESSO SELETIVO", a fila de pílulas, o botão com o contorno e o rodapé são do
fundo, medidos nas imagens; as caixas de texto seguem as dos slides, convertidas para px (o banner,
ao dobro do arquivo; `D-007`).

**Onde cada texto vai, e por quê.** O slide tem um cabeçalho em Lexend sobre faixas azul-escuras,
que sobem por cima do pé da foto; a lista dos cursos em Unbounded verde; o número e o prazo nas
pílulas; e "Acesse o link na Bio" no contorno ao lado do botão. Aqui:

- o **título** do Edital é o cabeçalho, em Lexend, à esquerda da foto;
- o **painel** do motor é a faixa azul-escura, de largura inteira, presa pela base acima das
  pílulas: o prazo em Lexend, as ofertas em Unbounded verde — a lista do slide. Quando cresce, sobe
  por cima do pé da foto, como as faixas do cabeçalho;
- o **número** vai na pílula da esquerda, como no slide, e a **busca** na da direita, onde o slide
  punha o prazo, que no motor é do painel. No banner a busca não cabe na pílula no corpo mínimo, e
  entra no painel;
- a **chamada à ação** vai no contorno, e o botão verde "SE INTERESSOU?" é um ativo: o texto é o do
  render da comunicação, colado no botão vazio do fundo (`compor_chamada_do_aperfeicoamento.py`).

**A imagem do banco é o fundo inteiro do slide** (P-1, como na Pós Lato Sensu): a foto com o clipe,
o papel rasgado, o selo, as pílulas, o botão e o rodapé vêm juntos. Cada uma das cinco fotos tem um
arquivo por formato.

**O que os arquivos dizem e a peça não diz.** "modalidade a distância" (FR-3814, T-3), "Inscrições
até 16/06" sem ano (T-1) e o cabeçalho "Edital Unificado / CURSO APERFEIÇOAMENTO" ficam de fora: o
tipo de curso não é dado publicado, e o título sai como o Edital o escreveu. A lista sai da ficha.

**Sem resumo por falta de espaço.** A FR-3836 admite o resumo das opções só na Pós Lato Sensu
(`kit_peca.RESUMO_POR_ESPACO`); aqui, a lista que não cabe no corpo mínimo recusa o formato,
nomeando o motivo. É o caso das quatro opções no post.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Ativo, Caixa, Familia, Imagem, Template

CHAVE = "aperfeicoamento"
#: A unidade da família (FR-3805): os Editais de Aperfeiçoamento são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "verde": "#dbff61",
    "branco": "#ffffff",
    # As faixas do cabeçalho dos slides, e o painel aqui.
    "azul_escuro": "#004aad",
    # O tom mais claro da textura do fundo azul, fora das manchas isoladas: o contraste se mede
    # contra ele, o pior caso de todo texto desenhado direto sobre o fundo (D-011).
    "fundo": "#2062b8",
}
FONTES = {
    "titulo": "lexend-extranegrito",
    "corpo": "poppins-regular",
    "destaque": "unbounded-regular",
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
    # Desenhadas no fundo e no ativo da chamada, e registradas aqui para a varredura as ler.
    "na_imagem": "PROCESSO SELETIVO",
    "no_botao": "SE INTERESSOU?",
}

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais de Aperfeiçoamento), 2025"
_LICENCA = "Não verificada: adotada pelo responsável pelo produto em 04/11/2026 (P-1)"


def _chamada_ativo(formato, resumo):
    return Ativo(
        f"chamada-{formato}.png",
        resumo,
        "Botão verde com a pergunta «SE INTERESSOU?» e o contorno ao lado dele",
    )


ATIVOS = {
    "chamada_post": _chamada_ativo(
        "post", "16409a2ed440ae97edf811a675d7eed6fc53b66ca9efc92a61e828e990ae59ee"
    ),
    "chamada_story": _chamada_ativo(
        "story", "419f12c611b3d316e7262da3643b87b7739f66e688e1374265bdb26ae14b7b20"
    ),
    "chamada_banner": _chamada_ativo(
        "banner", "e52d8188848db4a6821c8db7d452903d2999a7c9433a05f6a6106bee6ed8f2a4"
    ),
}


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
        "blazer",
        "foto de uma mulher sorridente, de blazer, digitando diante do computador",
        (
            "ed8042b04ea467840f101a71676d34ddf0e7db766ec36e74dc6358daba103bf9",
            "25476589859c4c7aa01692f6dfd2d434712f32c0ec975003a733d7e24d878031",
            "25fc6f4f8acfb68fd910b5f4449390f51eb53c0f2b09d371d0edd0268d5c91bd",
        ),
    ),
    _imagem(
        "cachos",
        "foto de uma mulher de cabelos cacheados, sorridente, diante do notebook",
        (
            "5a51cb36f1fa30c1eca1a238c0fc782440afce46af2a1ba31e78aee679ae7407",
            "3860a8a03db8541cab93fcbfaa4f68e36d96f8c0e269c772f89bd52e7d81d669",
            "15d4fecb8b9a990d809c37936038bc7a1f162db9f23e16e06df21f82dcc33ba5",
        ),
    ),
    _imagem(
        "camisa",
        "foto de um homem de óculos e camisa, trabalhando no notebook",
        (
            "115f4870000598b86e19eee3b21f9872bf50592a02567747d33bd3a0e621b26f",
            "b758c65bf2b634ca892f3a13dba0c61f156947f881624d8d721e196bdbce6067",
            "2351d93728edd2b03374354cff5f61588eebc7026412d3f49286edc1d82d3b1b",
        ),
    ),
    _imagem(
        "fone-preto",
        "foto de um homem de óculos e fone de ouvido, pensativo diante do notebook",
        (
            "9d3376037aa8dce6693cc3743d8744707f96342cc0a0eea6124585ea3021a344",
            "c3697054dbf37a51bcc27714d7c85312fddd1830053045dbbba9516a041bc756",
            "bd8f8349239b7cd5c13fc1bc8391bd6047d1ff4c5d571279dda39394831ae383",
        ),
    ),
    _imagem(
        "fone-branco",
        "foto de uma mulher de óculos e fone de ouvido branco, fazendo anotações",
        (
            "f2223e371a498bd96b974835399dfe8d01ee1f89ade0154dc775f5996b1bd1dc",
            "0afc4ce741cb989aeab0ac67ed64481f09014e55dcc7ea2bff374c80b2475c30",
            "878080036bf04b246df59e533a46fc9a2956913d77b302b36bce02541c9127a3",
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
        "branco",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _na_pilula(campo, corpos, retangulo, cor="verde", alinhamento="middle"):
    """Texto direto sobre o fundo: dentro das pílulas, no vão do selo, no contorno da chamada."""
    return Caixa(campo, "corpo", cor, "fundo", corpos, 1, alinhamento, retangulo=retangulo)


def _no_painel(campo, fonte, cor, corpos, linhas=1):
    return Caixa(campo, fonte, cor, "azul_escuro", corpos, linhas)


def _painel(periodo, linha, menor):
    """As caixas do painel, do maior ao menor corpo de cada uma."""
    return (
        _no_painel("selo_prorrogado", "titulo", "verde", menor),
        _no_painel("periodo", "titulo", "branco", periodo),
        _no_painel("hora", "corpo", "branco", linha, 2),
        _no_painel("inicio", "corpo", "branco", linha),
        _no_painel("publicado", "titulo", "branco", periodo),
        _no_painel("consulte", "corpo", "branco", linha, 2),
        _no_painel("total", "titulo", "verde", linha),
        _no_painel("oferta", "destaque", "verde", linha, 3),
        _no_painel("contagem", "titulo", "verde", periodo),
        _no_painel("todas", "corpo", "branco", menor, 2),
    )


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "6bd53285b809da6da5ef75ce7796a50a2254e3bd8380e2ad2d92af51661b0f55",
        "973b8dd70eb1bf9816f52f36605b91000136ab967ebf3825bb41990a83ee0f8b",
    ),
    ("story", 1): (
        "5419314ab0d62102fd125ef2a4276803ebe04ffe7ef75bfd4fc300db558aa1ce",
        "089ea18ee6e7c8a5a2199c3d704a445409f2731f32748a81ae080c88a80293bc",
    ),
    ("banner", 1): (
        "54fff4826df875d74aa18718f700f83ab4af88c714da8825ce846caa87b958e8",
        "4f26004ae0ba0508ef93e8d9073e93f240ff0662e8f4484ea05282d21a0b7baa",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        _titulo((80, 356, 470, 176), (44, 40, 36, 32, 30, 28, 26, 24)),
        _na_pilula("numero", (32, 30, 28, 26, 24), (124, 896, 388, 46)),
        *_painel((34, 32, 30, 28, 26, 24), (26, 24), (24,)),
        _na_pilula("chamada_a_acao", (34, 32, 30, 28, 26, 24), (495, 1121, 390, 48)),
        _na_pilula("busca", (28, 26, 24), (567, 898, 385, 42)),
        _na_pilula("selo_da_versao", (24,), (80, 985, 920, 34), cor="branco"),
    ),
    dimensoes={
        "painel": {
            # De largura inteira, para a lista caber; sobe por cima do pé da foto, como as faixas
            # do cabeçalho dos slides, mas não passa do título.
            "x": 80,
            "largura": 920,
            "base": 872,
            "recuo": 18,
            "recuo_em_baixo": 18,
            "topo_minimo": 540,
            "espaco": 5,
            "raio": 18,
            "cor": "azul_escuro",
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "chamada_post", "retangulo": (156, 1066, 764, 154)},
        "obstaculos": {
            "barra": (180, 0, 216, 162),
            "selo": (104, 148, 292, 348),
            "foto": (560, 0, 1080, 692),
            "pilula_da_esquerda": (0, 884, 90, 954),
            "pilula_da_direita": (986, 884, 1080, 954),
            "rodape": (150, 1258, 930, 1318),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(560, 0, 1080, 692),
    pasta_das_referencias="aperfeicoamento/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        _titulo((80, 456, 470, 236), (52, 48, 44, 40, 36, 32, 28, 26, 24)),
        _na_pilula("numero", (36, 32, 30, 28, 26, 24), (124, 1190, 388, 52)),
        *_painel((44, 40, 36, 32, 28, 26, 24), (30, 28, 26, 24), (28, 26, 24)),
        _na_pilula("chamada_a_acao", (40, 36, 32, 30, 28), (485, 1570, 470, 58)),
        _na_pilula("busca", (30, 28, 26, 24), (564, 1192, 388, 44)),
        _na_pilula("selo_da_versao", (24,), (80, 1380, 920, 34), cor="branco"),
    ),
    dimensoes={
        "painel": {
            "x": 80,
            "largura": 920,
            "base": 1166,
            "recuo": 20,
            "recuo_em_baixo": 20,
            # O pé da foto: o painel não a cobre no story, que tem altura para a lista inteira.
            "topo_minimo": 700,
            "espaco": 6,
            "raio": 22,
            "cor": "azul_escuro",
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "chamada_story", "retangulo": (86, 1523, 906, 152)},
        "obstaculos": {
            "barra": (180, 0, 216, 262),
            "selo": (104, 248, 292, 448),
            "foto": (560, 0, 1080, 700),
            "pilula_da_esquerda": (0, 1178, 90, 1250),
            "pilula_da_direita": (986, 1178, 1080, 1250),
            "rodape": (150, 1778, 930, 1838),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(560, 0, 1080, 700),
    pasta_das_referencias="aperfeicoamento/story",
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
        _titulo((250, 66, 790, 224), (56, 52, 48, 44, 40, 36, 32, 28)),
        _na_pilula("numero", (32, 30, 28), (100, 688, 312, 46)),
        *_painel((40, 36, 32, 28), (30, 28), (28,)),
        _na_pilula("chamada_a_acao", (32, 30, 28), (1145, 688, 255, 46)),
        _no_painel("busca", "corpo", "verde", (30, 28)),
        _no_painel("selo_da_versao", "corpo", "branco", (28,)),
    ),
    dimensoes={
        "painel": {
            "x": 250,
            "largura": 790,
            "base": 648,
            "recuo": 24,
            "recuo_em_baixo": 24,
            "topo_minimo": 300,
            "espaco": 6,
            "raio": 20,
            "cor": "azul_escuro",
            "itens": ("periodo", "busca", "selo_da_versao"),
        },
        "balao": {"ativo": "chamada_banner", "retangulo": (816, 657, 608, 112)},
        "obstaculos": {
            "barra": (148, 0, 176, 142),
            "selo": (92, 126, 236, 276),
            "foto": (1044, 0, 1500, 642),
            "pilula_da_esquerda": (0, 664, 78, 754),
            "pilula_do_meio": (438, 664, 806, 754),
            "pilula_da_direita": (1430, 664, 1500, 756),
        },
        "fundo": "fundo",
    },
    area_da_imagem=(1044, 0, 1500, 642),
    pasta_das_referencias="aperfeicoamento/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="Aperfeiçoamento",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos=ATIVOS,
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    pasta="aperfeicoamento",
)
