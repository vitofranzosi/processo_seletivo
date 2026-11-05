"""A família FIC: os templates da comunicação, em post, story e banner (119, US1, US2, T047).

**Os números vêm dos arquivos da comunicação** (`Editais FIC - {Posts,Story,Site}`): as fontes, as
cores, a faixa vermelha de ponta a ponta, o balão roxo e a bolha branca do número são os dos slides,
convertidos para px (o banner, ao dobro do arquivo; `D-007`). As áreas que não recebem texto — o
megafone, a ilustração e o rodapé com os perfis de rede e a marca — foram medidas nas quatro imagens
de fundo de cada formato, e o obstáculo declarado é a união delas: o texto fica no mesmo lugar com
qualquer imagem (FR-3827).

**A imagem do banco é o fundo inteiro do slide** (P-1, decisão do responsável pelo produto em
04/11/2026), com duas exceções, registradas no `ORIGEM.md` da família. O contato do Cefor, que os
slides trazem desenhado ("Dúvidas? selecaoextensao…"), foi pintado com o amarelo do fundo: o contato
da peça é o da ficha (FR-3810, FR-3820), e o desenhado diria um canal que a unidade pode não ter
declarado. E a bolha branca muda de lugar de uma foto para outra; o número do Edital não pode, e a
bolha saiu do fundo para voltar como ativo fixo.

**O que os slides dizem e a peça não diz.** "INSCRIÇÕES ABERTAS", "GRATUITA E 100% A DISTÂNCIA" e
"FORMAÇÃO INICIAL E CONTINUADA" ficam de fora (T-1, T-3, FR-3814): o período sai com ano e hora, e
nenhuma frase fixa afirma estado, gratuidade, modalidade ou tipo de curso. No lugar da categoria, o
título do Edital, na mesma Archivo Black. "ATENÇÃO!! EDITAL PRORROGADO" vira "ATENÇÃO! PRAZO
PRORROGADO": o que a Retificação comprova é a prorrogação do prazo, e é o que as outras famílias
dizem.

**As ofertas ficam direto sobre o fundo**, como nos slides: o painel não tem cor, e só empilha.
"Nome — carga horária" sai inteiro (FR-3817); a FIC não está na exceção da FR-3836, e a lista que
não cabe recusa o formato.
"""

import math

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Ativo, Caixa, Familia, Imagem, Template

CHAVE = "fic"
#: A unidade da família (FR-3805): os Editais FIC dos templates são do Cefor.
UNIDADES = frozenset({"cefor"})

PALETA = {
    "roxo": "#5027ad",
    "roxo_do_balao": "#4f1778",
    "vermelho": "#cb0000",
    "branco": "#ffffff",
    # O amarelo liso do fundo das imagens, lido do pixel: todo texto fora da faixa, do balão e da
    # bolha é medido contra ele (D-011).
    "fundo": "#fbc502",
}
FONTES = {
    "titulo": "archivo-black",
    "corpo": "barlow-semi-condensed-medio",
    "destaque": "barlow-semi-condensed-negrito",
    "rotulo": "space-mono-negrito",
}
# As frases fixas (FR-3814). Nenhuma fala de modalidade, gratuidade ou estado do momento.
FRASES = {
    "ate": "Inscrições até",
    "a_partir": "Inscrições a partir de",
    "inicio": "Início em",
    "horario": "(horário de Brasília)",
    "prorrogado": "ATENÇÃO! PRAZO PRORROGADO",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "todas": "Confira todas na página oficial",
    # Desenhados no rodapé das imagens de fundo, e registrados aqui para a varredura os ler.
    "na_imagem": "ifescefor · Ifes Cefor",
}

ATIVOS = {
    "balao": Ativo(
        "balao.png",
        "c20ef72a711ef5a591325e4e653179b6bab9afc36565dd3a9a5f892af8777c2c",
        "Balão roxo de contorno arredondado e irregular",
    ),
    "bolha": Ativo(
        "bolha.png",
        "f731add4a099d480c1adb5fd111797a8eacaac27ac7b3ff940a851b31a0f574f",
        "Balão de fala branco, com traços de movimento em volta",
    ),
    "megafone": Ativo(
        "megafone.png",
        "c6ce2da2331b878f4f0b3dae06fa2435c75b8538e6580d1a1675b52d1f72311d",
        "Ilustração de um megafone laranja e roxo",
    ),
}

_ORIGEM = "Arquivos de template da comunicação do Cefor (Editais FIC), 2025"
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
        "mesa",
        "ilustração de uma estudante sorridente estudando ao notebook, numa mesa com livros",
        (
            "8e163b0d6393287ee42e43dcb165700986802994d3c9d8994e1538e42e8f2f1d",
            "b22e7aac752aa7a4b7408c021bd1760d8b09f852798b62b4de38eaf9207837e5",
            "808489aaf2d1655a7fa70859452cdbf0146566501cc759f2a8c11657aa0745c7",
        ),
    ),
    _imagem(
        "prancheta",
        "ilustração de uma estudante ao lado de uma prancheta de tarefas, um alvo e um ímã",
        (
            "61646aca6ec1214ea58ddfe18f7c0b270d432581cfc3e2252a8b8da6b326cb0e",
            "df976cc978490ed9f0187aa91b40f18006161baef59407b89ad942078f8da20a",
            "64f8f7b5e876271f51be2244c3787f93a412ab2a3d685560be2a1f31a3be1e4c",
        ),
    ),
    _imagem(
        "poltrona",
        "ilustração de uma estudante sentada numa poltrona, com o notebook no colo",
        (
            "2c3589750558ebd5a99bc8bafd0e58ee2c08e4b392d81c44320621359feb97a2",
            "809d77f5cf7385f4a2459f15c5db115a3b9aae83bafa0644b80707f1b8bca568",
            "668a30004670dcffe27b4924f9e691c0cee95bad52c88d960f835a5c7cd1aec8",
        ),
    ),
    _imagem(
        "foguete",
        "ilustração de uma estudante ao lado de um notebook com gráficos e de um foguete",
        (
            "465f4e2b1c19ff704d23dbb36cbc77a19472a26bc8c365908974354abc4a1224",
            "9323ab8db97c5d14e9dda3a028acb24dcd6936e5e612b3bf1ccc0925108075ab",
            "021aae9adfe93d17de7b70cd396113b707e6424215437960f1575a65f47e3bb0",
        ),
    ),
)

#: A altura de uma linha, em corpos; a do compositor (`kit_peca.entrelinha`): 1,42, e a caixa da
#: Space Mono, que é maior.
_ENTRELINHA = 1.42
_ENTRELINHA_DA_SPACE_MONO = 1.481


def _linhas_por_corpo(corpos, altura, entrelinha=_ENTRELINHA):
    return tuple(max(1, math.floor(altura / (corpo * entrelinha) + 0.01)) for corpo in corpos)


def _posicionada(campo, fonte, cor, fundo, corpos, retangulo, alinhamento="start"):
    """Uma caixa de retângulo dado, com tantas linhas quantas a altura deixa em cada corpo."""
    return Caixa(
        campo,
        fonte,
        cor,
        fundo,
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        alinhamento=alinhamento,
        retangulo=retangulo,
    )


def _titulo(retangulo, corpos):
    return Caixa(
        "titulo",
        "titulo",
        "roxo",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


def _faixa(retangulo, corpos):
    return Caixa("selo_prorrogado", "rotulo", "branco", "vermelho", corpos, 1, retangulo=retangulo)


def _numero(retangulo, corpos):
    """O número do Edital na bolha branca, centrado, em até tantas linhas quantas couberem."""
    return Caixa(
        "numero",
        "rotulo",
        "roxo",
        "branco",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3], _ENTRELINHA_DA_SPACE_MONO),
        alinhamento="middle",
        retangulo=retangulo,
    )


def _no_balao(campo, fonte, corpos, retangulo):
    return Caixa(campo, fonte, "branco", "roxo_do_balao", corpos, 1, "middle", retangulo=retangulo)


def _no_fundo(campo, fonte, corpos, linhas=1):
    """Um item do painel: o painel da FIC não tem cor, e o texto fica sobre o amarelo."""
    return Caixa(campo, fonte, "roxo", "fundo", corpos, linhas)


def _painel(periodo, linha):
    """As caixas do painel, do maior ao menor corpo de cada uma.

    `selo_prorrogado` não está aqui: na FIC, a prorrogação é a faixa do alto.
    """
    return (
        _no_fundo("periodo", "destaque", periodo),
        _no_fundo("hora", "corpo", linha, 2),
        _no_fundo("inicio", "corpo", linha),
        _no_fundo("publicado", "destaque", periodo),
        _no_fundo("consulte", "corpo", linha, 2),
        _no_fundo("total", "destaque", linha),
        _no_fundo("oferta", "destaque", linha, 2),
        _no_fundo("contagem", "destaque", periodo),
        _no_fundo("todas", "corpo", linha, 2),
    )


def _contato(retangulo, corpos):
    return Caixa(
        "contato",
        "corpo",
        "roxo",
        "fundo",
        corpos,
        linhas_maximas=_linhas_por_corpo(corpos, retangulo[3]),
        # EC-4: o atendimento que não cabe sai da peça, e a tela diz; os textos o mantêm.
        ao_nao_caber=OMITIR,
        retangulo=retangulo,
    )


#: `(formato, versão)` → `(resumo das referências, resumo do template)`, fixados por versão e
#: conferidos pela suíte (FR-3833, `D-014`).
RESUMOS = {
    ("post", 1): (
        "8f5fa5e2dc2eeebdae61226f7567c62d934cbfa795f0ec0a15a41b4176b09aeb",
        "48c8b8c71eb326f17ca7bfc9cc388d9ee8ccbcd2e35dcdfeacc074600b84a0eb",
    ),
    ("story", 1): (
        "61289d458c466881b7a9fc6baf240c6490843e65b69b2edb41043f7362314e1a",
        "795eb249d0c1f88ed624be7576c2fc1f0f847a5ee0fc313e2778ff5da7d3e64c",
    ),
    ("banner", 1): (
        "5a074c75838497a3d050505be8f827b3bce050a5e7615800d98562355ab3e185",
        "dedce5f305362ea96caf016ac126970d12ad859d408fe9a3451af7949303946b",
    ),
}

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_contato=True,
    caixas=(
        _faixa((80, 82, 920, 60), (40, 36, 32, 28)),
        _titulo((80, 175, 860, 195), (60, 56, 52, 48, 44, 40, 36, 32, 28)),
        _numero((800, 784, 200, 100), (32, 30, 28, 26, 24)),
        *_painel((44, 40, 36, 32), (30, 28, 26, 24)),
        _no_balao("chamada_a_acao", "destaque", (40, 36, 32, 28), (130, 866, 400, 58)),
        _no_balao("busca", "corpo", (30, 28, 26, 24), (130, 934, 400, 44)),
        _posicionada("selo_da_versao", "corpo", "roxo", "fundo", (24,), (80, 1066, 520, 36)),
        _contato((80, 1110, 520, 108), (28, 26, 24)),
    ),
    ativos_posicionados={"bolha": (789, 760, 240, 163)},
    dimensoes={
        "faixa": {"retangulo": (0, 66, 1080, 92), "cor": "vermelho"},
        "painel": {
            "x": 80,
            "largura": 660,
            "base": 790,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 385,
            "espaco": 8,
            "raio": 0,
            "cor": None,
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "balao", "retangulo": (80, 805, 500, 249), "cor": "roxo_do_balao"},
        "opacos": {"bolha": "branco"},
        "obstaculos": {
            "megafone": (768, 374, 1028, 622),
            "ilustracao": (615, 940, 1080, 1350),
            "rodape": (34, 1226, 618, 1310),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="fic/post",
    resumo_das_referencias=RESUMOS[("post", 1)][0],
)

STORY = Template(
    familia=CHAVE,
    formato=kit_formatos.STORY,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    tem_contato=True,
    caixas=(
        _faixa((80, 276, 920, 60), (40, 36, 32, 28)),
        _titulo((80, 370, 670, 230), (64, 60, 56, 52, 48, 44, 40, 36, 32, 28)),
        _numero((775, 1128, 225, 120), (36, 34, 32, 30, 28)),
        *_painel((48, 44, 40, 36, 32), (34, 32, 30, 28, 26, 24)),
        _no_balao("chamada_a_acao", "destaque", (40, 36, 32, 28), (120, 1126, 400, 58)),
        _no_balao("busca", "corpo", (30, 28, 26, 24), (120, 1192, 400, 44)),
        _posicionada("selo_da_versao", "corpo", "roxo", "fundo", (24,), (80, 1328, 360, 72)),
        _contato((80, 1405, 360, 165), (28, 26, 24)),
    ),
    ativos_posicionados={"bolha": (754, 1103, 295, 201)},
    dimensoes={
        "faixa": {"retangulo": (0, 260, 1080, 92), "cor": "vermelho"},
        "painel": {
            "x": 80,
            "largura": 660,
            "base": 1070,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 610,
            "espaco": 10,
            "raio": 0,
            "cor": None,
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "balao", "retangulo": (80, 1080, 480, 239), "cor": "roxo_do_balao"},
        "opacos": {"bolha": "branco"},
        "obstaculos": {
            "megafone": (764, 504, 1010, 742),
            "ilustracao": (445, 1335, 1080, 1920),
            "rodape": (20, 1575, 445, 1920),
        },
        "fundo": "fundo",
    },
    pasta_das_referencias="fic/story",
    resumo_das_referencias=RESUMOS[("story", 1)][0],
)

BANNER = Template(
    familia=CHAVE,
    formato=kit_formatos.BANNER,
    versao=1,
    composicao="caixas",
    forma_do_periodo="ate",
    # O slide do site não traz contato, e o banner não o ganha.
    tem_contato=False,
    caixas=(
        _faixa((100, 66, 1300, 56), (36, 32, 28)),
        _titulo((100, 148, 820, 128), (48, 44, 40, 36, 32, 28)),
        _numero((1200, 186, 225, 100), (32, 30, 28)),
        *_painel((36, 32, 28), (30, 28)),
        _no_balao("chamada_a_acao", "destaque", (36, 32, 28), (150, 668, 320, 50)),
        _no_balao("busca", "corpo", (28,), (150, 724, 320, 40)),
        _posicionada("selo_da_versao", "corpo", "roxo", "fundo", (28,), (540, 700, 380, 82)),
    ),
    ativos_posicionados={"bolha": (1183, 161, 258, 175), "megafone": (960, 175, 200, 193)},
    dimensoes={
        "faixa": {"retangulo": (0, 52, 1500, 86), "cor": "vermelho"},
        "painel": {
            "x": 100,
            "largura": 800,
            "base": 615,
            "recuo": 0,
            "recuo_em_baixo": 0,
            "topo_minimo": 280,
            "espaco": 6,
            "raio": 0,
            "cor": None,
            "itens": ("periodo", "ofertas"),
        },
        "balao": {"ativo": "balao", "retangulo": (100, 620, 420, 209), "cor": "roxo_do_balao"},
        "opacos": {"bolha": "branco"},
        "obstaculos": {"ilustracao": (945, 420, 1500, 850)},
        "fundo": "fundo",
    },
    pasta_das_referencias="fic/banner",
    resumo_das_referencias=RESUMOS[("banner", 1)][0],
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="FIC",
    versao=1,
    unidades=UNIDADES,
    paleta=PALETA,
    fontes=FONTES,
    ativos=ATIVOS,
    frases=FRASES,
    templates={"post": POST, "story": STORY, "banner": BANNER},
    imagens=IMAGENS,
    pasta="fic",
)
