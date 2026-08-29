"""Quais coleções normativas têm chave estável — declarado, e não descoberto.

Detectar em tempo de execução ("o elemento é dict e tem `id`") acerta hoje e falha em silêncio
no dia em que uma coleção nova nascer sem identificador: o pressuposto de que `requirements` é a
única coleção atômica passaria a ser falso sem que nada acusasse. A declaração abaixo é
verificada por teste contra um snapshot real, de modo que esse dia vire falha de suíte (FR-012).

**Forma de coleção**: o caminho da coleção com `*` no lugar de cada segmento de lista já
atravessado. `/profiles/*/competitionModalities` vale para as Modalidades de qualquer Perfil,
porque a regra não depende de qual Perfil é.
"""

CAMPO_CHAVE = "id"
CURINGA = "*"

# Coleções cujos elementos carregam identificador estável: endereçadas por `id=<uuid>`, nunca
# por posição (FR-001, FR-007).
COLECOES_COM_CHAVE = frozenset(
    {
        "/profiles",
        "/schedule",
        "/profiles/*/competitionModalities",
    }
)

# Coleção sem identificador: valor normativo atômico, substituído inteiro e nunca endereçado
# item a item (FR-011).
COLECOES_ATOMICAS = frozenset({"/profiles/*/requirements"})

# Controle interno da Versão Consolidada. Não é conteúdo normativo e nenhuma Alteração o
# endereça, em forma alguma (FR-013).
LISTAS_DE_CONTROLE = frozenset({"applied_publications"})


def escapar(token):
    """Devolve o token à grafia do RFC 6901, para que a forma seja comparável ao declarado."""
    return token.replace("~", "~0").replace("/", "~1")


def tem_chave(forma):
    return forma in COLECOES_COM_CHAVE


def e_atomica(forma):
    return forma in COLECOES_ATOMICAS


def e_controle_interno(token):
    return token in LISTAS_DE_CONTROLE


def colecoes_com_chave(conteudo):
    """Cada coleção com chave presente em `conteudo`, como pares (forma, lista).

    A mesma forma aparece uma vez por contêiner: três Perfis com Modalidades produzem três
    pares `/profiles/*/competitionModalities`, porque a unicidade da chave é exigida dentro de
    cada coleção e não entre coleções distintas.
    """
    achadas = []
    _percorrer(conteudo, "", achadas)
    return achadas


def _percorrer(valor, forma, achadas):
    if isinstance(valor, dict):
        for chave, sub in valor.items():
            _percorrer(sub, f"{forma}/{escapar(chave)}", achadas)
    elif isinstance(valor, list):
        if tem_chave(forma):
            achadas.append((forma, valor))
        for item in valor:
            _percorrer(item, f"{forma}/{CURINGA}", achadas)
