"""Os valores declarados, ditos em palavras — e só eles (070, `FR-1435`, `R-009`).

**Não são as frases do documento.** O compositor do PDF escreve a regra inteira ("Havendo empate na
última posição, ..."), e essa frase muda com o código: a `067` e a `068` a reescreveram, e a `069`
vai reescrevê-la de novo. Aqui fica só o nome do valor que o Edital declarou, na grafia da
conferência da gestão (`interface/revisao.py`), que lê o que foi escolhido e não o que o documento
afirma. A frase, se o leitor precisar dela, está no documento do ato, que o cartão leva a abrir.
"""

RESERVA = {
    "NONE": "não há",
    "LIMITED": "limitado",
    "UNLIMITED": "sem limite de quantidade",
}

REVERSAO = {
    "ON_EXHAUSTION": "só quando a lista reservada esgota",
    "ON_BALANCE": "a quantidade que ficou sem preencher",
}

FORMA_DE_CONVOCACAO = {
    "PUBLICATION": "por publicação",
    "INDIVIDUAL_MESSAGE": "por mensagem individual",
}

MOMENTO_DO_REQUERIMENTO = {
    "AT_ENROLLMENT": "no ato da inscrição",
    "AT_CALL": "quando o candidato for convocado",
}

FORMA_DA_ORDEM = {
    "POR_PONTUACAO": "por pontuação",
    "POR_SORTEIO": "por sorteio",
}

OPERACAO = {
    "SOMA_PONDERADA": "soma ponderada das Etapas",
    "MEDIA_PONDERADA": "média ponderada das Etapas",
}

NORMALIZACAO = {
    "NENHUMA": "nenhuma",
    "PELA_SOMA_DOS_PESOS": "pela soma dos pesos",
}

ARREDONDAMENTO = {
    "MEIO_PARA_CIMA": "meio para cima",
    "MEIO_PARA_PAR": "meio para par",
    "TRUNCAR": "truncamento",
}

ESPECIE_DO_ALVO = {
    "FIXED": "uma quantidade fixa",
    "FROM_VACANCY_TABLE": "quantas vagas o quadro publicar",
}

EMPATE_NO_CORTE = {
    "ADMITS_SURPLUS": "os empatados na última posição progridem todos",
    "STRICT": "a quantidade não é excedida por empate",
}

#: Sem "faixa", que é vocabulário interno da gestão (`test_vocabulario_da_composicao.py`): esta
#: resposta é a base do que o candidato vai ler.
CONTINUACAO = {
    "ALLOWED": "admite chamar, nesta ordem, além dos que o corte publicar",
    "NONE": "só os que o corte publicar",
}

TIPO_DO_CRITERIO = {
    "MAIOR_PONTUACAO_NA_ETAPA": "maior pontuação na Etapa",
    "MAIOR_VALOR_DE_FATO": "maior valor declarado de",
    "MENOR_VALOR_DE_FATO": "menor valor declarado de",
}

QUANDO_FALTA = {
    "ULTIMO_NO_CRITERIO": "sem o valor, fica por último neste critério",
    "CRITERIO_NAO_SE_APLICA": "sem o valor, o critério não se aplica",
}

FORMA_DA_ETAPA = {
    "PONTUADA": "pontuada",
    "DECISORIA": "decisória (favorável ou desfavorável)",
}

UNIDADE_DO_PRAZO = {
    "DIAS_CORRIDOS": "dias corridos",
}


def em_palavras(tabela, valor):
    """O valor na tabela, ou ele mesmo entre aspas — nunca um valor inventado.

    Um valor declarado que a tabela não conhece é dito como está, e não traduzido por aproximação:
    traduzir o que não se conhece é afirmar o que o Edital não diz.
    """
    if valor is None:
        return "não declarado"
    return tabela.get(valor, f"“{valor}”")
