"""A família Institucional: a peça do feed da `111`, declarada como dados (119, D-002, FR-3804).

**Nada aqui é desenho novo.** As cores, as faixas, os corpos, as recaídas, a marca e o rodapé são as
constantes que `kit_peca.py` tinha até a `119`, com os mesmos valores, e os SVG de referência da
`111` provam que a peça não mudou um byte (SC-1133). O identificador continua
`feed-1080x1350 · 1`: ele está no manifesto e na trilha de cada exportação já feita, e mudá-lo sem
mudar a peça registraria uma diferença que não existe.

**As cores são os tokens do produto** (`shared/static/shared/tokens.css`), e não uma paleta
inventada para a peça. Todas passam AA sobre o fundo em que são desenhadas, e o teste confere par a
par.

**O compositor é o de fluxo**: as caixas não têm retângulo fixo, e o compositor as empilha na ordem
do conteúdo, desce o título de corpo antes de ceder a vez ao do Processo e centra o corpo na folga
(FR-3434 da `111`). As medidas desse fluxo que não são caixa estão em `DIMENSOES`.

**A marca é a oficial** (FR-3432 da `111`, `kit_ativos/ORIGEM.md`): a do Cefor, que tem a sua no
pacote do Ifes, e a do Ifes com a sigla escrita para as demais unidades.
"""

from processo_seletivo.interface import kit_formatos
from processo_seletivo.interface.kit_familias import OMITIR, Ativo, Caixa, Familia, Template

CHAVE = "institucional"

#: O resumo da versão 1, congelado (FR-3835, D-010): a chave da `111` libera esta versão, e só ela.
#: Mudar a declaração, um ativo, uma fonte ou as referências muda o resumo e reprova a suíte; a
#: mudança vira versão 2, liberada pela chave nova depois da aprovação.
RESUMO_CONGELADO_V1 = "d7ab660ea7551a1bd905985dba6a0a1e4800c1531a2d9a9ff256cc9a60e13128"
#: O resumo dos SVG de referência da `111` (`tests/fixtures/kit_referencias/*.svg`).
RESUMO_DAS_REFERENCIAS_V1 = "923ff2c2256174f4117d39f270181c72bd882bc0b9c1d86cf00c4978dc2d56ed"

PALETA = {
    "verde_escuro": "#0b5a2a",
    "verde_texto": "#146c37",
    "verde_claro": "#e7f5ec",
    "branco": "#ffffff",
    "texto": "#1c1c1c",
    "texto_fraco": "#555555",
    "borda": "#d4d4d4",
    "amarelo": "#8a5300",
    "amarelo_fundo": "#fdf5e5",
}

FONTES = {
    "corpo": "edital-sans-regular",
    "titulo": "edital-sans-negrito",
    "destaque": "edital-sans-negrito",
}

# As frases fixas do template. A conferência aceita só estas, além dos valores da ficha e da
# manchete da lista fechada (FR-3423 da `111`). Nomeadas, para a varredura de vocabulário as ler.
FRASES = {
    "chamada": "PROCESSO SELETIVO",
    "inscricoes": "INSCRIÇÕES",
    "prorrogado": "PRAZO PRORROGADO",
    "publicado": "EDITAL PUBLICADO",
    "consulte": "Consulte as condições na página oficial",
    "oferta": "OFERTA",
    "todas": "Confira todas na página oficial",
    "rodape": "Condições, documentos e cronograma:",
}
HORARIO = "(horário de Brasília)"

ATIVOS = {
    "marca-cefor": Ativo(
        "cefor-horizontal-branco.png",
        "1f436a9e697431200cad18be19625d41d79b691132d8a912365794a177b14bb4",
        "Marca do Instituto Federal do Espírito Santo, Centro de Referência em Formação e em "
        "Educação a Distância",
        (0.0597, 0.2396, 0.9389, 0.7569),
    ),
    "marca-ifes": Ativo(
        "ifes-horizontal-branco.png",
        "40dff3ef48f32793f4761e5ad6b25510bf8874a34e34c36c16735b1f34a8bfd5",
        "Marca do Instituto Federal do Espírito Santo",
        (0.0597, 0.1944, 0.9389, 0.8021),
    ),
}
#: A sigla da unidade → a marca que o pacote oficial tem para ela; as demais recebem a do Ifes.
MARCA_DA_UNIDADE = {"Cefor": "marca-cefor", "Ifes": "marca-ifes"}
MARCA_PADRAO = "marca-ifes"

DIMENSOES = {
    "faixa": 210,  # a faixa da marca, no topo
    "bloco_do_periodo": 236,
    "bloco_do_neutro": 200,
    "raio_do_bloco": 28,
    "recuo_do_bloco": 40,
    "rodape": 1100,  # a linha do rodapé; o selo termina antes da margem de baixo
    "folga_do_rodape": 30,
    # A parte da folga que vai para cima do corpo (FR-3434 da `111`): com duas opções, o vazio
    # inteiro embaixo fazia a peça parecer cortada. Só desloca — nada muda de tamanho nem de ordem.
    "parte_da_folga_em_cima": 0.35,
    "largura_da_marca": 340,
    "proporcao_da_marca": 720 / 288,
}


def _caixa(campo, fonte, cor, fundo, corpos, **resto):
    return Caixa(campo, fonte, cor, fundo, tuple(corpos), **resto)


CAIXAS = (
    _caixa("assinatura", "destaque", "branco", "verde_escuro", (36,), alinhamento="end"),
    _caixa("chamada", "destaque", "verde_texto", "branco", (28,)),
    _caixa("identificacao", "corpo", "texto_fraco", "branco", (32,)),
    # O título, do maior ao menor corpo admitido, e o número de linhas em cada um. Nenhum oficial
    # cabendo, a manchete; sem ela, a peça sai sem título e diz a omissão (FR-3426 da `111`).
    _caixa(
        "titulo",
        "titulo",
        "texto",
        "branco",
        (52, 46, 40, 36),
        linhas_maximas=(3, 3, 4, 4),
        ao_nao_caber=OMITIR,
    ),
    _caixa("inscricoes", "destaque", "branco", "verde_escuro", (30,)),
    _caixa("selo_prorrogado", "destaque", "amarelo", "amarelo_fundo", (24,), alinhamento="end"),
    _caixa("periodo", "destaque", "branco", "verde_escuro", range(88, 55, -4)),
    _caixa("hora", "corpo", "verde_claro", "verde_escuro", (30,)),
    _caixa("publicado", "destaque", "branco", "verde_escuro", (60,)),
    _caixa("consulte", "corpo", "verde_claro", "verde_escuro", (30,)),
    _caixa("rotulo_da_oferta", "destaque", "verde_texto", "branco", (26,)),
    _caixa("total_de_vagas", "destaque", "verde_texto", "branco", (26,), alinhamento="end"),
    _caixa("oferta_nome", "destaque", "texto", "branco", (32,), linhas_maximas=2),
    _caixa("contagem", "destaque", "texto", "branco", (40,)),
    _caixa("todas", "corpo", "texto_fraco", "branco", (28,)),
    _caixa("oferta_rotulo", "corpo", "texto", "branco", (30,), linhas_maximas=2),
    _caixa("oferta_quantidade", "destaque", "texto", "branco", (30,), alinhamento="end"),
    _caixa("rodape", "corpo", "texto_fraco", "branco", (26,)),
    # O endereço é da implantação, e o seu comprimento não se conhece de antemão: desce de corpo até
    # o mínimo, e se nem assim couber numa linha, a peça é recusada — partir o endereço mudaria o
    # destino.
    _caixa("caminho_curto", "destaque", "verde_texto", "branco", range(34, 23, -2)),
    _caixa("busca", "destaque", "verde_texto", "branco", (28,)),
    _caixa("selo_da_versao", "corpo", "texto_fraco", "branco", (kit_formatos.POST.corpo_minimo,)),
)

POST = Template(
    familia=CHAVE,
    formato=kit_formatos.POST,
    versao=1,
    composicao="fluxo-institucional",
    caixas=CAIXAS,
    identificador="feed-1080x1350 · 1",
    dimensoes=DIMENSOES,
    resumo_das_referencias=RESUMO_DAS_REFERENCIAS_V1,
    pasta_das_referencias="",
)

FAMILIA = Familia(
    chave=CHAVE,
    nome="Institucional",
    versao=1,
    unidades=frozenset(),
    paleta=PALETA,
    fontes=FONTES,
    ativos=ATIVOS,
    frases={**FRASES, "horario": HORARIO},
    templates={"post": POST},
)
