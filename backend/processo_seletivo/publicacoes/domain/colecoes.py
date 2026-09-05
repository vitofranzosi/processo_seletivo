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
        "/stages",
        "/sections",
        "/profiles/*/competitionModalities",
        # As duas da leva da `015`. Aninhadas no Perfil pela mesma razão que a Modalidade: a regra
        # não depende de qual Perfil é. Declará-las **antes** de o snapshot as emitir não é ordem
        # arbitrária — sem isto, `changes.py` recusaria endereçá-las por `id=` e o caminho só
        # resolveria por posição, que é o que o sistema proíbe (015, T-007).
        "/profiles/*/declaredFacts",
        "/profiles/*/classificationMilestones",
        # Os critérios são endereçados por identidade como tudo o mais, **apesar** de a ordem deles
        # ser normativa: a ordem é campo publicado de cada um, e não a posição na lista. Sem esta
        # declaração, reordenar por Retificação só resolveria por índice — que é o que o sistema
        # proíbe, e o que faria a reordenação perder os identificadores (015, FR-015).
        "/profiles/*/classificationMilestones/*/tiebreakers",
        # O Documento Exigido nasce com identidade estável e é endereçado por ela como as demais
        # (FR-009 da 009): nenhuma regra nova, nenhuma gramática nova — só mais uma coleção na
        # declaração que já existe.
        "/documentRequirements",
    }
)

# Coleção sem identificador: valor normativo atômico, substituído inteiro e nunca endereçado
# item a item (FR-011).
COLECOES_ATOMICAS = frozenset(
    {
        "/profiles/*/requirements",
        # A enumeração de Etapas de um marco é lista de **identidades**, e não de entidades: não há
        # o que endereçar item a item, e mudar quais Etapas entram é substituir a enumeração
        # inteira. Foi o guarda de endereçamento sobre snapshot publicado que a encontrou — sem
        # esta declaração ela seria coleção sem chave, que é o que o sistema recusa (015, T-007).
        "/profiles/*/classificationMilestones/*/stages",
    }
)

# Controle interno da Versão Consolidada. Não é conteúdo normativo e nenhuma Alteração o
# endereça, em forma alguma (FR-013).
LISTAS_DE_CONTROLE = frozenset({"applied_publications"})

# Campos que **identificam** o conteúdo publicado. Nenhuma Retificação os endereça (FR-004).
#
# A exposição é anterior à `007` — `/editalId`, `/processoId` e `/schemaVersion` já eram
# endereçáveis, e só `applied_publications` era recusado. Mas é a `007` que a **ativa**: até aqui o
# UUID do Processo não identificava nada para quem lê o documento; a partir de `processoTitle`, ele
# é o nome que o Edital dá ao Processo a que pertence. Sem esta recusa, uma Retificação faria o
# documento publicado nomear outro Processo. Herdar uma exposição é aceitável; ativá-la e deixá-la
# aberta, não.
#
# **Fora daqui, de propósito**: `title` e `description`, retificáveis por desenho e oferecidos pela
# tela; e `number` e `year`, que são identidade mas já eram impressos no cabeçalho antes desta
# feature e não são ativados por ela. Ficam como questão aberta, registrada em `research.md` D-003.1
# — não como omissão.
CAMPOS_DE_IDENTIDADE = frozenset(
    {"editalId", "processoId", "processoCode", "processoTitle", "schemaVersion"}
)


def escapar(token):
    """Devolve o token à grafia do RFC 6901, para que a forma seja comparável ao declarado."""
    return token.replace("~", "~0").replace("/", "~1")


def tem_chave(forma):
    return forma in COLECOES_COM_CHAVE


def e_atomica(forma):
    return forma in COLECOES_ATOMICAS


def e_controle_interno(token):
    return token in LISTAS_DE_CONTROLE


def e_campo_de_identidade(token):
    return token in CAMPOS_DE_IDENTIDADE


def e_elemento_de_colecao_com_chave(forma):
    """A forma designa o **elemento** de uma coleção com chave, e não a coleção?

    `/profiles/*` sim; `/profiles` é a coleção. Já `normativeRule` é um objeto que por acaso tem
    `id`, e esse `id` não endereça nada — continua sendo conteúdo comum.
    """
    return forma.endswith(f"/{CURINGA}") and tem_chave(forma[: -len(CURINGA) - 1])


def colecoes_com_chave(conteudo):
    """Cada coleção com chave presente em `conteudo`, como pares (forma, lista).

    A mesma forma aparece uma vez por contêiner: três Perfis com Modalidades produzem três
    pares `/profiles/*/competitionModalities`, porque a unicidade da chave é exigida dentro de
    cada coleção e não entre coleções distintas.
    """
    achadas = []
    _percorrer(conteudo, "", achadas)
    return achadas


def identidades(conteudo):
    """Caminho concreto de cada entidade endereçável do conteúdo.

    `/profiles/id=…0501` e `/profiles/id=…0501/competitionModalities/id=…0541` — a topologia das
    identidades, e não só o conjunto de chaves: é ela que precisa mudar apenas quando o ato
    **endereça** a coleção em que a mudança acontece.

    Coleção sem chave não é percorrida: nenhuma coleção declarada mora dentro de uma, e sem
    identificador não haveria caminho concreto a registrar.
    """
    achadas = set()
    _percorrer_identidades(conteudo, "", "", achadas)
    return achadas


def _percorrer_identidades(valor, forma, caminho, achadas):
    if isinstance(valor, dict):
        for chave, sub in valor.items():
            escapada = escapar(chave)
            _percorrer_identidades(sub, f"{forma}/{escapada}", f"{caminho}/{escapada}", achadas)
    elif isinstance(valor, list) and tem_chave(forma):
        for elemento in valor:
            chave = elemento.get(CAMPO_CHAVE) if isinstance(elemento, dict) else None
            if not isinstance(chave, str):
                continue
            concreto = f"{caminho}/{CAMPO_CHAVE}={chave}"
            achadas.add(concreto)
            _percorrer_identidades(elemento, f"{forma}/{CURINGA}", concreto, achadas)


def declaradas_que_nao_sao_lista(conteudo):
    """Coleções declaradas que, no conteúdo dado, deixaram de ser lista.

    A declaração de `colecoes.py` é a premissa de FR-012 e da gramática inteira. Uma alteração que
    trocasse `/profiles` por um objeto tornaria a declaração falsa em silêncio: nada percorreria a
    coleção, nenhum elemento seria verificado, e o caminho por chave deixaria de resolver sem que
    ninguém fosse avisado.
    """
    fora = []
    _percorrer_declaradas(conteudo, "", fora)
    return sorted(set(fora))


def _percorrer_declaradas(valor, forma, fora):
    if (tem_chave(forma) or e_atomica(forma)) and not isinstance(valor, list):
        fora.append(forma)
        return
    if isinstance(valor, dict):
        for chave, sub in valor.items():
            _percorrer_declaradas(sub, f"{forma}/{escapar(chave)}", fora)
    elif isinstance(valor, list):
        for item in valor:
            _percorrer_declaradas(item, f"{forma}/{CURINGA}", fora)


def _percorrer(valor, forma, achadas):
    if isinstance(valor, dict):
        for chave, sub in valor.items():
            _percorrer(sub, f"{forma}/{escapar(chave)}", achadas)
    elif isinstance(valor, list):
        if tem_chave(forma):
            achadas.append((forma, valor))
        for item in valor:
            _percorrer(item, f"{forma}/{CURINGA}", achadas)
