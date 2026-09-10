"""O que uma Retificação alterou, dito em linguagem do domínio (024, FR-130, D-005).

**Por que existe.** `AlteracaoNormativa.target_path` é endereçamento estrutural —
`/profiles/id=<uuid>/immediateVacancies`. É a forma certa para o sistema localizar o que mudou, e
a forma errada para dizer a alguém o que mudou: é vocabulário nosso, não do domínio, e o Princípio I
manda que a página fale a língua do Edital.

**O que este módulo devolve, e o que ele recusa devolver.** Devolve *onde* — a entidade alterada,
pelo rótulo que ela tem no conteúdo-base — e *qual campo*. **Não** devolve valor anterior nem valor
novo: quem quer o texto exato do ato abre o documento da Retificação, que está na mesma linha do
histórico. A tela de homologação da gestão precisa do antes e do depois, porque quem aprova
confere valores; quem se candidata precisa saber **que** as vagas daquele Perfil mudaram.

**Caminho não reconhecido não produz linha.** É a `D-009` aplicada ao caso mais fácil de errar:
inventar um rótulo genérico para um caminho que não se sabe ler afirmaria algo sobre o Edital. Uma
alteração a menos na lista é honesta; uma linha que diz a coisa errada, não.
"""

from processo_seletivo.publicacoes.domain.changes import ABSENT, resolve_path

# A posição de acréscimo da gramática: `/attachments/-` é "no fim desta coleção".
ACRESCIMO = "-"

OPERACOES = {"ADD": "acrescentado", "REPLACE": "alterado", "REMOVE": "removido"}

# Como cada coleção normativa se chama numa página pública, e por qual campo cada elemento dela se
# reconhece. O nome do elemento vem do **conteúdo-base** — é o que aquela versão dizia, que é o que
# quem lê precisa reconhecer.
COLECOES = {
    "profiles": ("Perfil", "name"),
    "schedule": ("Evento do cronograma", "description"),
    "stages": ("Etapa", "name"),
    "sections": ("Seção", "title"),
    "attachments": ("Anexo", "label"),
    "documentRequirements": ("Documento exigido", "name"),
    "competitionModalities": ("Modalidade de concorrência", "name"),
    "declaredFacts": ("Fato declarado", "type"),
    "classificationMilestones": ("Marco de classificação", "name"),
    "tiebreakers": ("Critério de desempate", "name"),
}

# Os campos, por coleção. O que não estiver aqui não vira linha — ver a docstring do módulo.
CAMPOS = {
    "profiles": {
        "code": "Código",
        "name": "Denominação",
        "description": "Descrição",
        "requirements": "Requisitos",
        "immediateVacancies": "Vagas imediatas",
        "reserveType": "Cadastro reserva",
        "reserveLimit": "Limite do cadastro reserva",
        "locality": "Localidade",
        "duties": "Atribuições",
        "workload": "Carga horária",
        "compensation": "Remuneração",
    },
    "schedule": {
        "type": "Tipo",
        "description": "Descrição",
        "startAt": "Início",
        "endAt": "Término",
        "order": "Ordem",
        "location": "Local",
        "isRegistrationPeriod": "Período de inscrições",
    },
    "stages": {
        "name": "Denominação",
        "order": "Ordem",
        "weight": "Peso",
        "eliminatory": "Caráter eliminatório",
        "classificatory": "Caráter classificatório",
        "minimumScore": "Nota mínima",
        "maximumScore": "Nota máxima",
        "forma": "Forma de conclusão",
        "evaluationsPerRegistration": "Avaliações por inscrição",
        "rotuloFavoravel": "Rótulo favorável",
        "rotuloDesfavoravel": "Rótulo desfavorável",
    },
    "sections": {"title": "Título", "content": "Texto", "order": "Ordem"},
    "attachments": {
        "label": "Rótulo",
        "order": "Ordem editorial",
        "artifactId": "Arquivo",
        # A conferência anda junto do arquivo e não é decisão própria. Mostrá-la como linha
        # separada diria duas vezes a mesma substituição, uma delas em SHA-256 — é a correção que
        # a `020` já fez na tela da gestão, e que não vale a pena refazer aqui.
        "artifactHash": None,
    },
    "documentRequirements": {
        "name": "Nome",
        "instructions": "Instruções",
        "required": "Obrigatoriedade",
        "order": "Ordem",
        "attachmentId": "Modelo",
    },
    "competitionModalities": {"code": "Código", "name": "Denominação"},
}

# Os campos de topo do Edital: alterados sem passar por coleção nenhuma.
CAMPOS_DO_EDITAL = {
    "title": "Título do Edital",
    "description": "Descrição do Edital",
    "number": "Número",
    "year": "Ano",
    "processoTitle": "Título do Processo",
    "processoCode": "Código do Processo",
}


def alteracao_legivel(conteudo_base, alteracao):
    """Uma alteração dita em português, ou `None` quando não se sabe lê-la.

    `alteracao` é qualquer objeto com `target_path` e `operation` — a `AlteracaoNormativa`
    persistida serve, e um par simples também, o que mantém o módulo testável sem banco.
    """
    caminho = (getattr(alteracao, "target_path", "") or "").strip()
    operacao = OPERACOES.get(getattr(alteracao, "operation", ""), "alterado")
    if not caminho.startswith("/"):
        return None

    segmentos = caminho.strip("/").split("/")
    colecao = segmentos[0]

    if len(segmentos) == 1:
        rotulo = CAMPOS_DO_EDITAL.get(colecao)
        if rotulo is None:
            return None
        return {"onde": "O Edital", "campo": rotulo, "operacao": operacao}

    if colecao not in COLECOES:
        return None

    onde = _nome_da_entidade(conteudo_base, segmentos[:2], colecao)
    resto = segmentos[2:]

    # A coleção inteira: o elemento entrou ou saiu do Edital.
    if not resto:
        return {"onde": onde, "campo": "", "operacao": operacao}

    # Coleção aninhada — a Modalidade dentro do Perfil, o desempate dentro do marco. Nomeia-se a
    # entidade de fora e a de dentro: "Perfil «Professor» — Modalidade de concorrência «PPP»".
    if resto[0] in COLECOES and len(resto) >= 2:
        interna = _nome_da_entidade(
            resolve_path(conteudo_base, "/" + "/".join(segmentos[:2])), resto[:2], resto[0]
        )
        campo = _rotulo_do_campo(resto[0], resto[2]) if len(resto) > 2 else ""
        if campo is None:
            return None
        return {"onde": f"{onde} — {interna}", "campo": campo, "operacao": operacao}

    campo = _rotulo_do_campo(colecao, resto[0])
    if campo is None:
        return None
    return {"onde": onde, "campo": campo, "operacao": operacao}


def alteracoes_legiveis(conteudo_base, alteracoes):
    """As que se sabe ler, na ordem em que o ato as declarou."""
    lidas = (alteracao_legivel(conteudo_base, item) for item in alteracoes)
    return [item for item in lidas if item is not None]


def _rotulo_do_campo(colecao, campo):
    """`None` significa "não vira linha" — tanto o campo desconhecido quanto o deliberadamente
    omitido. Os dois casos têm a mesma consequência na tela, e distingui-los aqui só serviria para
    o chamador ter de tratar dois."""
    return CAMPOS.get(colecao, {}).get(campo)


def _nome_da_entidade(conteudo, segmentos, colecao):
    """`Perfil «Professor de Informática»`, lido do conteúdo-base.

    O rótulo vem daquela versão, e não do banco: é o que o Edital dizia quando a Retificação foi
    escrita, que é o que quem lê o histórico precisa reconhecer. Sem nome legível — porque o
    elemento está sendo acrescentado agora, ou porque o conteúdo-base não o tem — devolve só o
    tipo, que já diz mais do que um UUID.
    """
    rotulo, campo_do_nome = COLECOES[colecao]
    if segmentos[1] == ACRESCIMO:
        return rotulo
    if not isinstance(conteudo, dict):
        return rotulo
    valor = resolve_path(conteudo, "/" + "/".join(segmentos))
    if valor is ABSENT or not isinstance(valor, dict):
        return rotulo
    nome = (valor.get(campo_do_nome) or "").strip()
    return f"{rotulo} “{nome}”" if nome else rotulo
