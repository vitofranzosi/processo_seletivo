"""A família Libras: os templates da comunicação, em post, story e banner (119, T048).

**Os números vêm dos arquivos da comunicação** (`Editais Libras - {Posts,Story,Site}`): o amarelo, o
preto e as fontes são os dos slides; as caixas de texto seguem as deles, convertidas para px (o
banner, ao dobro do arquivo; `D-007`). A foto recortada em círculo, o ícone das mãos, os dois traços
que ladeiam a chamada e o rodapé com os perfis de rede e a marca foram medidos nas duas imagens de
fundo de cada formato, e o obstáculo declarado é a união delas: o texto fica no mesmo lugar com
qualquer foto (FR-3827). O círculo entra como dois retângulos em degrau, e não como o retângulo que
o envolve, que tomaria o canto livre à esquerda do pé da foto — o lugar do título no slide.

**A Helvetica Neue dos slides é a Inter** (P-2, decisão do responsável pelo produto em 05/11/2026):
a Helvetica Neue é proprietária e não se embute no SVG exportado. O título, em negrito como o
"PROCESSO SELETIVO / CURSO FIC DE LIBRAS" do slide; o horário, as ofertas e o selo, na regular. As
informações — número e prazo — ficam na Unbounded negrita, como no slide, e a chamada na Unbounded
regular.

**A imagem do banco é o fundo inteiro do slide** (P-1, como nas outras famílias): a foto em círculo,
as mãos, os traços e o rodapé vêm juntos, e nenhum deles traz texto que a peça precise trocar.

**O que os slides dizem e a peça não diz.** "PROCESSO SELETIVO / CURSO FIC DE LIBRAS BÁSICO" é o
cabeçalho do slide; aqui, o título sai como o Edital o escreveu, e o tipo de curso não é dado
publicado (FR-3814, T-3). "Acesse o link na Bio e inscreva-se" é a chamada do formato: a peça não
afirma que as inscrições estão abertas (T-1).

**Tudo centrado, menos o título do post** ("Mantenha centralizado", diz o slide de orientação). No
post, o título fica no canto livre à esquerda do pé da foto, alinhado à esquerda como no slide de
orientação: centrado na largura inteira, ele empurraria o painel para baixo do corpo mínimo, e o
selo da versão desce para baixo da chamada pela mesma razão. O painel não tem cor, e só empilha,
direto sobre o amarelo, como na FIC; a lista que não cabe recusa o formato (a Libras não está na
exceção da FR-3836).
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Caixa, Familia, Imagem, Template

CHAVE = "libras"
#: A unidade da família (FR-3805): os Editais de Libras dos templates são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "preto": "#000000",
    # O amarelo liso do fundo das imagens, lido do pixel: todo texto é medido contra ele (D-011).
    "fundo": "#ffde59",
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
    # Desenhados no rodapé das imagens de fundo, e registrados aqui para a varredura os ler.
    "na_imagem": "ifescefor · Ifes Cefor",
}

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais Libras), 2025"
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
        "grupo",
        "foto em círculo de três pessoas sentadas conversando em Libras",
        (
            "1c9064fa09ee18c5e59dac2ed5e40a0c449facc5d6552380b5975bcb1aa2168f",
            "44f4bd5a0f4c5ae4b058c4cfa8789ab481526da6fd63fe47761a4d537ab69a90",
            "d0590a7f5803ab23421c0fbb26605620ffdd79672a47cb4b2d0ff7c3593a1399",
        ),
    ),
    _imagem(
        "sinal",
        "foto em círculo de um homem de óculos, sorridente, fazendo um sinal em Libras",
        (
            "b1de16299b13dd2248295279c7e47d807e10908911809bafb96ce561807ade8d",
            "47a4d0935e15d0e5f0d132c16eb6eee1c51194d45a13a7c077ef09dea6a67674",
            "59de29d4d97b3518d41074213c1aed62a24b4c035a59c9deb7a6465284ce3bb9",
        ),
    ),
)

#: A altura de uma linha, em corpos; a mesma do compositor (`kit_peca.ENTRELINHA`). A caixa
#: tipográfica da Inter (0,969 + 0,242) e a da Unbounded cabem nela.
_ENTRELINHA = 1.42


def _linhas_por_corpo(corpos, altura):
    return tuple(max(1, math.floor(altura / (corpo * _ENTRELINHA) + 0.01)) for corpo in corpos)


def _titulo(retangulo, corpos, alinhamento="start"):
    return Caixa(
        "titulo",
        "titulo",
        "preto",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        alinhamento=alinhamento,
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _posicionada(campo, fonte, corpos, retangulo, alinhamento="middle"):
    return Caixa(campo, fonte, "preto", "fundo", corpos, 1, alinhamento, retangulo=retangulo)


def _no_fundo(campo, fonte, corpos, linhas=1):
    """Um item do painel: o painel não tem cor, e o texto fica centrado sobre o amarelo."""
    return Caixa(campo, fonte, "preto", "fundo", corpos, linhas, "middle")


def _painel(periodo, linha, menor, *, com_selo=True):
    """As caixas do painel, do maior ao menor corpo; sem o selo quando ele é posicionado."""
    selo = (_no_fundo("selo_da_versao", "corpo", menor, 2),) if com_selo else ()
    return (
        _no_fundo("selo_prorrogado", "destaque", menor),
        _no_fundo("periodo", "destaque", periodo),
        _no_fundo("hora", "corpo", linha, 2),
        _no_fundo("inicio", "corpo", linha),
        _no_fundo("publicado", "destaque", periodo),
        _no_fundo("consulte", "corpo", linha, 2),
        _no_fundo("total", "titulo", linha),
        _no_fundo("oferta", "corpo", linha, 2),
        _no_fundo("contagem", "titulo", linha),
        _no_fundo("todas", "corpo", menor, 2),
        _no_fundo("busca", "corpo", menor),
        *selo,
    )


def _painel_sem_cor(x, largura, base, topo_minimo, espaco, itens=("busca", "selo_da_versao")):
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
        "itens": ("periodo", "ofertas", *itens),
    }


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "e4c4971216bf258e9acd58707b78e0e9d020d9a769f4420c58db489815b427c5",
        "db26f4737c4b0252c7c19d16d789d6853d983f1d54866f73ea6dcca41a5f5ddd",
    ),
    ("story", 1): (
        "cb12b3301b7d29e5cff8e57de1dcb034f093235f244f48eb0499777fc5a5880e",
        "6d699167abba5cf298352e69cd117a2fd60c253e0ccc579a814078b6e74bf856",
    ),
    ("banner", 1): (
        "080be5fafa0b97790c310c2873f35986e02bf287b82e43ddcb1bff39139c26fd",
        "a9ad7cba0bd6428f33ed98716965e5a840850fa1c6de3a2e020460970f1fa13c",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        # O canto à esquerda do pé da foto, abaixo das mãos: o lugar do título no slide.
        _titulo((80, 538, 420, 150), (44, 40, 36, 34, 32, 30, 28, 26, 24)),
        _posicionada("numero", "destaque", (34, 32, 30, 28, 26, 24), (80, 692, 920, 50)),
        *_painel((32, 30, 28, 26, 24), (26, 24), (24,), com_selo=False),
        # Entre os dois traços do fundo, como no slide.
        _posicionada("chamada_a_acao", "rotulo", (30, 28, 26, 24), (236, 1068, 608, 64)),
        # O selo desce para baixo da chamada, no vão até o rodapé: no painel, tomaria a altura de
        # que as ofertas precisam.
        _posicionada("selo_da_versao", "corpo", (24,), (80, 1136, 920, 40)),
    ),
    dimensoes={
        "painel": _painel_sem_cor(80, 920, 1066, 748, 3, itens=("busca",)),
        "obstaculos": {
            "foto_em_cima": (380, 0, 1080, 530),
            "foto_embaixo": (512, 530, 1080, 690),
            "maos": (103, 240, 380, 535),
            "traco_da_esquerda": (29, 1100, 222, 1104),
            "traco_da_direita": (858, 1100, 1051, 1104),
            "rodape": (0, 1185, 1080, 1350),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="libras/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    caixas=(
        # No story o canto à esquerda da foto é das mãos; o título vem abaixo do círculo, centrado
        # como nos slides 2 e 3.
        _titulo((80, 818, 920, 182), (60, 56, 52, 48, 44, 40, 36, 32, 28), "middle"),
        _posicionada("numero", "destaque", (46, 44, 40, 36, 32, 28, 26, 24), (80, 1006, 920, 66)),
        *_painel((44, 40, 36, 32, 30, 28, 26, 24), (32, 30, 28, 26, 24), (28, 26, 24)),
        _posicionada("chamada_a_acao", "rotulo", (32, 30, 28, 26, 24), (204, 1600, 680, 68)),
    ),
    dimensoes={
        "painel": _painel_sem_cor(80, 920, 1590, 1080, 5),
        "obstaculos": {
            "foto_em_cima": (252, 0, 1080, 520),
            "maos": (103, 500, 330, 795),
            "foto_embaixo": (330, 520, 1080, 810),
            "traco_da_esquerda": (29, 1635, 192, 1640),
            "traco_da_direita": (888, 1635, 1051, 1640),
            "rodape": (0, 1755, 1080, 1920),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="libras/story",
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
        _titulo((60, 110, 690, 200), (56, 52, 48, 44, 40, 36, 32, 28), "middle"),
        _posicionada("numero", "destaque", (40, 36, 32, 28), (60, 330, 690, 58)),
        *_painel((40, 36, 32, 28), (30, 28), (28,)),
        # À direita do traço preto do fundo, alinhada à esquerda, como no slide.
        _posicionada("chamada_a_acao", "rotulo", (32, 30, 28), (248, 736, 500, 54), "start"),
    ),
    dimensoes={
        "painel": _painel_sem_cor(60, 690, 712, 400, 6),
        "obstaculos": {
            "foto": (772, 0, 1500, 712),
            "maos": (776, 575, 968, 800),
            "traco": (0, 750, 224, 784),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="libras/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="Libras",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos={},
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    pasta="libras",
)
