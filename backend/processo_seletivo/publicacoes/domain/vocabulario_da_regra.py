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
"""

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

ETAPA_NAO_IDENTIFICADA = "Etapa não identificada neste Edital"
FATO_NAO_IDENTIFICADO = "dado não identificado neste Edital"


def por_identificador(itens):
    return {str(item.get("id")): item for item in itens or [] if isinstance(item, dict)}


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


def criterio_por_extenso(criterio, etapas, fatos):
    """A frase do critério: o que ele faz e sobre o que — "maior pontuação na Etapa Prova didática".

    Tipo que não está no mapa não vira grafia impressa: sobra o alvo, que é a metade legível.
    Só existem três, e escrever `MAIOR_VALOR_DE_FATO` seria trocar a frase que falta pelo nome
    interno que ninguém de fora lê.
    """
    alvo = alvo_do_criterio(criterio, etapas, fatos)
    tipo = criterio.get("type") or ""
    return CRITERIO_DE_DESEMPATE[tipo].format(alvo=alvo) if tipo in CRITERIO_DE_DESEMPATE else alvo


def criterio_com_a_ausencia(criterio, etapas, fatos):
    """A frase acrescida do que fazer quando o valor não existe.

    Sem ela, dois candidatos em que um não tem o dado continuariam inseparáveis no papel: a regra
    de ausência é parte da regra, e não nota de rodapé (E2E15-004).
    """
    frase = criterio_por_extenso(criterio, etapas, fatos)
    ausencia = QUANDO_AUSENTE.get(criterio.get("whenMissing"))
    return f"{frase}; {ausencia}" if ausencia else frase


__all__ = [
    "CRITERIO_DE_DESEMPATE",
    "ETAPA_NAO_IDENTIFICADA",
    "FATO_NAO_IDENTIFICADO",
    "QUANDO_AUSENTE",
    "alvo_do_criterio",
    "criterio_com_a_ausencia",
    "criterio_por_extenso",
    "por_identificador",
]
