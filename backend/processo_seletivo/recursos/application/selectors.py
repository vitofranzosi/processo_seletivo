"""A leitura dos recursos — e a situação de cada um, que é **derivada** e não coluna.

O `Recurso` não tem estado persistido (D-010). O que aconteceu com uma peça é a existência dos atos
que a alcançaram, e a situação exibida se lê deles:

```text
sem juízo de admissibilidade      →  aguardando admissibilidade
juízo negativo                    →  inadmitido (terminal)
admitido, sem decisão             →  aguardando julgamento
decisão existente                 →  decidido, e a espécie diz o efeito
```

Uma coluna seria estado a manter coerente onde a existência de linha já responde — o mesmo idioma
de `PENDENTE`/`CONSOLIDADO` na 013 e da vigência na 015 e na 017. E o primeiro lugar onde ela
apareceria é justamente aqui, por conveniência de uma tela de listagem.

**A espécie chega ao candidato em texto institucional**, nunca como enum: quem lê "Recurso deferido
— o resultado foi corrigido" entende; quem lê `CORRECAO_FIXADA`, não (FR-048, SC-021).
"""

from processo_seletivo.recursos.models import DecisaoRecurso, Recurso

AGUARDANDO_ADMISSIBILIDADE = "aguardando_admissibilidade"
INADMITIDO = "inadmitido"
AGUARDANDO_JULGAMENTO = "aguardando_julgamento"
DECIDIDO = "decidido"

SITUACOES = {
    AGUARDANDO_ADMISSIBILIDADE: "Aguardando análise de admissibilidade",
    INADMITIDO: "Recurso não admitido",
    AGUARDANDO_JULGAMENTO: "Admitido, aguardando julgamento",
    DECIDIDO: "Julgado",
}

# O que a decisão diz a **quem recorreu**. O enum descreve o efeito para o domínio; estas frases
# descrevem o que aconteceu com a pessoa, que é outra coisa e é a que a tela mostra.
ESPECIES = {
    DecisaoRecurso.Especie.INDEFERIDO: "Recurso indeferido",
    DecisaoRecurso.Especie.CORRECAO_FIXADA: "Recurso deferido — o resultado foi corrigido",
    DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA: ("Recurso deferido — a etapa será reavaliada"),
    DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE: (
        "Recurso deferido — a instituição praticará o ato corretivo"
    ),
}


def recursos_do_titular(inscricao):
    """Os recursos da Inscrição, do mais recente para o mais antigo.

    Duas consultas e não uma por peça: `prefetch_related` traz juízos e decisões em bloco. Uma
    listagem que fizesse uma leitura por recurso pareceria rápida com uma peça e sumiria com dez —
    e é o defeito que a 010 já encontrou na listagem de inscrições.
    """
    peças = (
        Recurso.objects.filter(inscricao=inscricao)
        .prefetch_related("juizos", "decisoes")
        .order_by("-interposto_em")
    )
    return [resumo(peca) for peca in peças]


def resumo(peca):
    """A peça como o titular a lê: protocolo, objeto, situação e, havendo, a decisão."""
    juizo = next(iter(peca.juizos.all()), None)
    decisao = next(iter(peca.decisoes.all()), None)
    return {
        "recurso": peca,
        "protocolo": peca.protocolo,
        "interposto_em": peca.interposto_em,
        "fundamentacao": peca.fundamentacao,
        "objeto": _objeto(peca),
        "situacao": _situacao(juizo, decisao),
        "situacao_rotulo": SITUACOES[_situacao(juizo, decisao)],
        "admissibilidade": (
            {"admitido": juizo.admitido, "motivo": juizo.motivo, "quando": juizo.decidido_em}
            if juizo is not None
            else None
        ),
        "decisao": (
            {
                "especie_rotulo": ESPECIES[decisao.especie],
                "motivacao": decisao.motivacao,
                "quando": decisao.decidido_em,
            }
            if decisao is not None
            else None
        ),
    }


def _situacao(juizo, decisao):
    if juizo is None:
        return AGUARDANDO_ADMISSIBILIDADE
    if not juizo.admitido:
        return INADMITIDO
    return DECIDIDO if decisao is not None else AGUARDANDO_JULGAMENTO


def _objeto(peca):
    """O objeto atacado, nomeado em linguagem institucional e nunca por identificador.

    O candidato precisa reconhecer **o que** ele contestou: "o resultado divulgado" e "o meu
    resultado da Etapa X" são coisas diferentes, e a peça vale por nomear qual das duas.
    """
    if peca.publicacao_atacada_id is not None:
        return "o resultado divulgado"
    return "o meu resultado de etapa"
