"""Leitura das publicações: a vigente de um marco, uma pela identidade, o histórico e a da pessoa.

**Vigente é a publicação que ninguém sucedeu** — `sucessoras__isnull=True`, derivado da cadeia
append-only. Não há coluna de vigência a alternar, e por isso não há estado a manter coerente
(T-002).
"""

from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    PublicacaoResultado,
    SituacaoDivulgada,
)


def vigente_do_marco(*, edital, marco_id, lista_id=None):
    """A publicação sem sucessora **daquele recorte**, ou `None` quando nada foi divulgado ainda.

    **`lista_id` entra com a 021** (D-015, FR-068). Desde que três listas de concorrência produzem
    três atos raiz no mesmo marco, "a vigente do marco" deixou de ser pergunta com uma resposta:
    sem o filtro, a cadeia de uma lista seria lida como a de outra, e suceder a publicação da PPI
    apareceria como suceder a da ampla concorrência.

    O padrão `None` é a ampla concorrência, que é o que toda publicação anterior à 021 é: quem
    chamava sem o argumento continua recebendo exatamente a publicação que recebia.
    """
    return (
        PublicacaoResultado.objects.filter(
            edital=edital, marco_id=marco_id, lista_id=lista_id, sucessoras__isnull=True
        )
        .order_by("-publicado_em")
        .first()
    )


def publicacao_por_id(publicacao_id):
    """Uma publicação pela identidade, com a cadeia que diz se ela ainda é a vigente.

    `sucessoras` vem por `prefetch_related` porque é o que a página pública pergunta em seguida — e
    porque é a diferença entre um número **constante** de consultas e uma por publicação lida.
    """
    return (
        PublicacaoResultado.objects.filter(pk=publicacao_id)
        .select_related("edital")
        .prefetch_related("sucessoras")
        .first()
    )


def documento_do_resultado(publicacao_id):
    """Os bytes gravados do documento oficial, ou `None` quando ele não existe."""
    return DocumentoDoResultado.objects.filter(publicacao_id=publicacao_id).first()


def historico_do_marco(*, edital, marco_id):
    """A cadeia inteira do marco, da mais recente para a mais antiga (FR-068).

    Cada linha diz natureza, instante, autor, autoridade e **situação** — vigente ou sucedida —,
    que é a pergunta que o histórico existe para responder.
    """
    linhas = list(
        PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id)
        .select_related("ato")
        .prefetch_related("sucessoras")
        .order_by("-publicado_em")
    )
    return [
        {
            "publicacao": publicacao,
            "natureza_rotulo": publicacao.get_natureza_display(),
            "vigente": not publicacao.sucessoras.all(),
            "ato": publicacao.ato,
        }
        for publicacao in linhas
    ]


def situacoes_do_candidato(inscricao):
    """**Todas** as situações vigentes da Inscrição, uma por marco divulgado (FR-057, FR-061).

    Todas, e não a mais recente. Um Edital pode ter vários marcos classificatórios, e cada um é ato
    pleno: publicados o intermediário e o final, a Inscrição tem duas linhas vigentes, e as duas são
    da pessoa. Escolher uma seria o sistema decidindo qual ato administrativo lhe interessa.

    A ordem é a de `cabecalho.marco_codigo`, congelado em cada publicação — a mesma por que a 015
    emite os marcos, e portanto a ordem normativa em que eles se sucedem no certame. **Não** é a
    ordem em que a instituição divulgou: publicar o marco final antes do intermediário é possível,
    e a Área não deve inverter a sequência do certame por causa disso (FR-058).

    O `marco_codigo` sai dos bytes já congelados, e não de uma releitura da versão do ato: essa é
    leitura que a fronteira pública não faz, e refazê-la aqui devolveria a ordem de hoje a uma
    publicação histórica.
    """
    import json

    linhas = (
        SituacaoDivulgada.objects.filter(inscricao=inscricao, publicacao__sucessoras__isnull=True)
        .select_related("publicacao")
        .order_by("publicacao__publicado_em")
    )
    resumos = []
    for linha in linhas:
        conteudo = json.loads(bytes(linha.publicacao.conteudo_publico).decode("utf-8"))
        cabecalho = conteudo.get("cabecalho") or {}
        resumos.append(
            {
                "publicacao": linha.publicacao,
                "marco": cabecalho.get("marco", ""),
                "marco_codigo": cabecalho.get("marco_codigo", ""),
                "natureza_rotulo": cabecalho.get("natureza_rotulo", ""),
                "situacao": linha.situacao,
                "classificada": linha.situacao == SituacaoDivulgada.Situacao.CLASSIFICADA,
                "posicao": linha.posicao,
                "compartilhada": linha.compartilhada,
                "pontuacao": linha.pontuacao,
                "motivo": linha.motivo,
            }
        )
    return sorted(resumos, key=lambda item: (item["marco_codigo"], item["marco"]))


def vigentes_do_edital(edital):
    """As publicações vigentes dos marcos do Edital — a descobribilidade pela vitrine (FR-050)."""
    linhas = list(
        PublicacaoResultado.objects.filter(edital=edital, sucessoras__isnull=True).order_by(
            "publicado_em"
        )
    )
    return [
        {
            "publicacao": publicacao,
            "natureza_rotulo": publicacao.get_natureza_display(),
            **_rotulos(publicacao),
        }
        for publicacao in linhas
    ]


def _rotulos(publicacao):
    import json

    conteudo = json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))
    cabecalho = conteudo.get("cabecalho") or {}
    return {
        "marco": cabecalho.get("marco", ""),
        "marco_codigo": cabecalho.get("marco_codigo", ""),
        "titulo": cabecalho.get("titulo", ""),
    }


__all__ = [
    "documento_do_resultado",
    "historico_do_marco",
    "publicacao_por_id",
    "situacoes_do_candidato",
    "vigente_do_marco",
    "vigentes_do_edital",
]
