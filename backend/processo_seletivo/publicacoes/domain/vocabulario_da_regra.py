"""A regra classificatória publicada, dita em português — e num lugar só.

O conteúdo publicado guarda a regra como o sistema a grava: `MAIOR_VALOR_DE_FATO`, e o `factId`
que ela compara. Duas leituras precisam da mesma frase e chegavam a ela por caminhos diferentes:
o documento oficial do Edital, que a 017 corrigiu (E2E15-004), e a tabela de desempate do ato de
ordenação, que continuava imprimindo o enum (E2E15-006). Ter a grafia em dois lugares faria as
duas divergirem no primeiro critério novo — e são exatamente as duas peças que a instituição põe
lado a lado para responder a um recurso.

Mora em `publicacoes` porque a regra é do **conteúdo publicado**, e é a direção que já existe:
`classificacao` lê `publicacoes`, nunca o contrário.

**A frase é sobre a regra, não sobre quem a lê.** O que muda entre os dois destinos é o que
acompanha a frase — o documento nunca imprime identificador (FR-017), e a página do ato o mantém
como âncora de auditoria —, e por isso essa decisão fica com cada chamador, e não aqui.

**As frases têm versão** (069, R-004, FR-1397). A redação 1 é a de antes da `069`, congelada; a 2 é
a da `069`, na voz do candidato. O documento publicado guarda os bytes da sua, mas a página do ato
de ordenação **reconstrói** a frase na hora de exibir — e um ato publicado antes da `069` não pode
passar a dizer, na tela, uma frase que nunca publicou. Por isso cada função recebe a redação, e a
`Publicacao` registra com qual o documento foi composto (`redacao_do_documento`). O padrão é a
vigente: a Revisão, o portal e a proposta de ordenação descrevem a regra da versão aplicável, e
podem dizê-la na redação nova (FR-1397).
"""

# As redações das frases geradas. A 1 nunca muda: é a que os atos publicados antes da `069` dizem.
REDACAO_1 = 1
REDACAO_2 = 2
REDACAO_VIGENTE = REDACAO_2

# `{alvo}` já vem com o substantivo que o antecede — "Etapa Prova didática", "Meses de
# experiência" —, porque é o que permite à mesma frase servir ao alvo resolvido e ao ausente sem
# que uma das duas leituras fique torta.
CRITERIO_DE_DESEMPATE = {
    "MAIOR_PONTUACAO_NA_ETAPA": "maior pontuação na {alvo}",
    "MAIOR_VALOR_DE_FATO": "maior valor declarado em {alvo}",
    "MENOR_VALOR_DE_FATO": "menor valor declarado em {alvo}",
}
QUANDO_AUSENTE = {
    "ULTIMO_NO_CRITERIO": "sem o valor, fica por último neste critério",
    "CRITERIO_NAO_SE_APLICA": "sem o valor, o critério não se aplica",
}

# **A redação 2 do desempate** (069, T1 a T7 do contrato de redação). O fato é dito pelo próprio
# nome e pelo tipo declarado — a data "mais antiga" ou "mais recente", o número "maior" ou
# "menor" —, e nunca pelo valor abstrato ("valor declarado em"). **Forma genérica sempre** (D-006):
# o sistema não deduz "maior idade" comparando o rótulo com "Data de nascimento". O rótulo é texto
# de quem elabora, e a dedução trocaria a regra declarada por outra que o sistema supõe
# equivalente.
_SENTIDO_DA_DATA = {"MENOR_VALOR_DE_FATO": "mais antiga", "MAIOR_VALOR_DE_FATO": "mais recente"}
_SENTIDO_DO_NUMERO = {"MENOR_VALOR_DE_FATO": "menor", "MAIOR_VALOR_DE_FATO": "maior"}
# A ausência concorda com o que falta: "a" data, "o" número, "a" pontuação.
QUANDO_AUSENTE_2 = {
    "ULTIMO_NO_CRITERIO": "quem não {artigo} {verbo} fica em último lugar neste critério",
    "CRITERIO_NAO_SE_APLICA": "para quem não {artigo} tiver, o critério não se aplica",
}

ETAPA_NAO_IDENTIFICADA = "Etapa não identificada neste Edital"
FATO_NAO_IDENTIFICADO = "dado não identificado neste Edital"

# --- A forma de comunicar a convocação (019, R-007) ---------------------------------------------
# **Vocabulário do conteúdo publicado, e é por isso que mora aqui e não em `convocacao`.** A `019`
# lê estes valores do Perfil publicado; escrevê-los também lá seriam duas grafias do mesmo valor em
# módulos diferentes — e é assim que uma delas fica para trás numa renomeação. Aqui a renomeação
# seria uma Retificação, e o outro lado nem saberia.
#
# **As duas são normais, e a amostra tem as duas.** O 69/2026 (7.2) convoca por publicação; o
# 77/2026, o 58 e o 59 (8.3) por mensagem individual, com o prazo contado do recebimento. Inferir
# qual pelo texto do Edital é o erro que a `R-006` da `025` recusou por escrito para a ampla
# concorrência: quem declara é o Edital.
#
# **A ausência não é padrão.** Perfil que não declarou `callForm` não convoca por publicação "por
# omissão" — ele simplesmente não declarou, e a `019` recusa emitir com
# `forma_de_comunicacao_nao_declarada`.
FORMA_POR_PUBLICACAO = "PUBLICATION"
FORMA_POR_MENSAGEM_INDIVIDUAL = "INDIVIDUAL_MESSAGE"
FORMAS_DE_CONVOCACAO = (FORMA_POR_PUBLICACAO, FORMA_POR_MENSAGEM_INDIVIDUAL)

# **Na redação 2, "por publicação", sem "no endereço eletrônico do certame"** (V4). O lugar da
# publicação é texto de quem elabora, e o sistema não tem o endereço — o domínio congelado e a rota
# legível são outra feature.
FORMA_DE_CONVOCACAO_POR_REDACAO = {
    REDACAO_1: {
        FORMA_POR_PUBLICACAO: "por publicação no endereço eletrônico do certame",
        FORMA_POR_MENSAGEM_INDIVIDUAL: "por mensagem individual à pessoa convocada",
    },
    REDACAO_2: {
        FORMA_POR_PUBLICACAO: "por publicação",
        FORMA_POR_MENSAGEM_INDIVIDUAL: "por mensagem individual à pessoa convocada",
    },
}
# A forma na redação vigente — a que o documento, o portal e a Revisão dizem agora.
FORMA_DE_CONVOCACAO_POR_EXTENSO = FORMA_DE_CONVOCACAO_POR_REDACAO[REDACAO_VIGENTE]
FORMA_DE_CONVOCACAO_NAO_DECLARADA = "forma de convocação não declarada neste Edital"
# A frase inteira da redação 2 (V4, V5). As duas têm sujeitos diferentes — "dos classificados" sai
# da individual, que é sempre a uma pessoa —, e por isso não são a forma encaixada numa moldura
# comum.
FRASE_DA_CONVOCACAO_2 = {
    FORMA_POR_PUBLICACAO: "A convocação dos classificados será feita por publicação.",
    FORMA_POR_MENSAGEM_INDIVIDUAL: (
        "A convocação será feita por mensagem individual à pessoa convocada."
    ),
}


def forma_de_convocacao_por_extenso(forma, *, redacao=REDACAO_VIGENTE):
    """A frase da forma declarada, ou a que nomeia a ausência — nunca o enum, nunca um padrão.

    Imprimir `INDIVIDUAL_MESSAGE` no documento oficial repetiria o defeito `E2E15-006`, em que a
    tabela de desempate saía com o nome interno. E devolver a frase da publicação para um Perfil
    que não declarou nada afirmaria norma que o Edital não tem.
    """
    return FORMA_DE_CONVOCACAO_POR_REDACAO[redacao].get(forma) or FORMA_DE_CONVOCACAO_NAO_DECLARADA


def frase_da_convocacao(forma, *, redacao=REDACAO_VIGENTE):
    """A frase que o documento imprime para a forma declarada, ou `""` sem declaração (V4, V5).

    Sem declaração, nada — nem "não declarou": é a disciplina da `025` e da `016` (019, D-009).
    """
    if redacao == REDACAO_1:
        extenso = FORMA_DE_CONVOCACAO_POR_REDACAO[REDACAO_1].get(forma)
        return f"A convocação dos classificados será feita {extenso}." if extenso else ""
    return FRASE_DA_CONVOCACAO_2.get(forma, "")


def por_identificador(itens):
    return {str(item.get("id")): item for item in itens or [] if isinstance(item, dict)}


def inicial_minuscula(texto):
    """O texto com a primeira letra em minúscula, salvo quando a primeira palavra é sigla (069).

    "Data de nascimento" entra numa frase como "data de nascimento"; "CPF do responsável" e "EaD"
    continuam como foram escritos — a caixa de uma sigla é parte dela (FR-1377).
    """
    texto = str(texto or "")
    primeira = texto.split(" ", 1)[0]
    letras = [caractere for caractere in primeira if caractere.isalpha()]
    if not letras or sum(caractere.isupper() for caractere in letras) > 1:
        return texto
    return texto[:1].lower() + texto[1:]


def alvo_do_criterio(criterio, etapas, fatos):
    """O que o critério compara, resolvido para o **nome publicado** (E2E15-004).

    `parameters` carrega `stageId` ou `factId` conforme o tipo, e era descartado: o documento
    imprimia "2º maior valor declarado" sem dizer *de quê*. O desempate aplicado pelo sistema não
    era o que o Edital deixava reconstituir — e um candidato, ou um juiz, lendo só o documento
    oficial não chegava à mesma ordem.

    **O identificador não sai daqui em nenhuma hipótese.** Alvo que o conteúdo não resolve é dito
    como ausente, não como UUID: quem quiser exibir o identificador o tem em mãos e decide isso no
    seu próprio lugar.
    """
    parametros = criterio.get("parameters") or {}
    if criterio.get("type") == "MAIOR_PONTUACAO_NA_ETAPA":
        etapa = etapas.get(str(parametros.get("stageId"))) or {}
        return f"Etapa {etapa['name']}" if etapa.get("name") else ETAPA_NAO_IDENTIFICADA
    fato = fatos.get(str(parametros.get("factId"))) or {}
    return fato.get("label") or FATO_NAO_IDENTIFICADO


def _fato_do_criterio(criterio, fatos):
    return fatos.get(str((criterio.get("parameters") or {}).get("factId"))) or {}


def _criterio_na_redacao_2(criterio, etapas, fatos):
    """T1 a T5: a Etapa entre aspas, a data pelo sentido, o número pelo tamanho — e "informado na
    inscrição", que é de onde o valor vem e o que diz ao candidato que o dado é dele."""
    tipo = criterio.get("type") or ""
    parametros = criterio.get("parameters") or {}
    if tipo == "MAIOR_PONTUACAO_NA_ETAPA":
        etapa = etapas.get(str(parametros.get("stageId"))) or {}
        if not etapa.get("name"):
            return f"maior pontuação na {ETAPA_NAO_IDENTIFICADA}"
        return f"maior pontuação na Etapa “{etapa['name']}”"
    fato = _fato_do_criterio(criterio, fatos)
    rotulo = inicial_minuscula(fato.get("label")) or FATO_NAO_IDENTIFICADO
    if tipo not in _SENTIDO_DO_NUMERO:
        return rotulo
    if fato.get("type") == "DATA":
        return f"{rotulo} {_SENTIDO_DA_DATA[tipo]}, informada na inscrição"
    if fato.get("type") == "INTEIRO":
        return f"{_SENTIDO_DO_NUMERO[tipo]} número de {rotulo}, informado na inscrição"
    # Fato sem tipo, ou sem fato: o sentido e o alvo, e nada que o dado não diga.
    return f"{_SENTIDO_DO_NUMERO[tipo]} valor de {rotulo}, informado na inscrição"


def criterio_por_extenso(criterio, etapas, fatos, *, redacao=REDACAO_VIGENTE):
    """A frase do critério: o que ele faz e sobre o que — "maior pontuação na Etapa Prova didática".

    Tipo que não está no mapa não vira grafia impressa: sobra o alvo, que é a metade legível.
    Só existem três, e escrever `MAIOR_VALOR_DE_FATO` seria trocar a frase que falta pelo nome
    interno que ninguém de fora lê.

    `redacao` é a do documento em que o critério foi publicado (069, R-004): a página de um ato de
    ordenação já publicado passa a do ato, e o resto do sistema usa a vigente.
    """
    if redacao != REDACAO_1:
        return _criterio_na_redacao_2(criterio, etapas, fatos)
    alvo = alvo_do_criterio(criterio, etapas, fatos)
    tipo = criterio.get("type") or ""
    return CRITERIO_DE_DESEMPATE[tipo].format(alvo=alvo) if tipo in CRITERIO_DE_DESEMPATE else alvo


def criterio_com_a_ausencia(criterio, etapas, fatos, *, redacao=REDACAO_VIGENTE):
    """A frase acrescida do que fazer quando o valor não existe.

    Sem ela, dois candidatos em que um não tem o dado continuariam inseparáveis no papel: a regra
    de ausência é parte da regra, e não nota de rodapé (E2E15-004).
    """
    frase = criterio_por_extenso(criterio, etapas, fatos, redacao=redacao)
    quando = criterio.get("whenMissing")
    if redacao == REDACAO_1:
        ausencia = QUANDO_AUSENTE.get(quando)
        return f"{frase}; {ausencia}" if ausencia else frase
    if quando not in QUANDO_AUSENTE_2:
        return frase
    if criterio.get("type") == "MAIOR_PONTUACAO_NA_ETAPA":
        # A pontuação na Etapa não se informa: tem-se ou não se tem.
        artigo, verbo = "a", "tiver"
    else:
        artigo = "o" if _fato_do_criterio(criterio, fatos).get("type") == "INTEIRO" else "a"
        verbo = "informar"
    return f"{frase}; {QUANDO_AUSENTE_2[quando].format(artigo=artigo, verbo=verbo)}"


__all__ = [
    "CRITERIO_DE_DESEMPATE",
    "ETAPA_NAO_IDENTIFICADA",
    "FATO_NAO_IDENTIFICADO",
    "FORMAS_DE_CONVOCACAO",
    "FORMA_DE_CONVOCACAO_NAO_DECLARADA",
    "FORMA_DE_CONVOCACAO_POR_EXTENSO",
    "FORMA_DE_CONVOCACAO_POR_REDACAO",
    "FORMA_POR_MENSAGEM_INDIVIDUAL",
    "FORMA_POR_PUBLICACAO",
    "QUANDO_AUSENTE",
    "REDACAO_1",
    "REDACAO_2",
    "REDACAO_VIGENTE",
    "alvo_do_criterio",
    "criterio_com_a_ausencia",
    "criterio_por_extenso",
    "forma_de_convocacao_por_extenso",
    "frase_da_convocacao",
    "inicial_minuscula",
    "por_identificador",
]
