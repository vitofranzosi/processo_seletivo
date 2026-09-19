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


def divulgacao_do_ato(*, edital, marco_id, ato, lista_id=None, historico=None):
    """Se o que está divulgado corresponde **àquele** ato, ou `None` quando não há ato.

    "Emitir" e "publicar" são atos distintos, em telas distintas, e essa é a distinção que o
    operador mais precisa trazer de fora. Esta derivação é o que permite ao sistema dizê-la.

    **Vivia dentro de `interface/views.py`, num ajudante privado** (`038`, `R-6`, `FR-557`). Saiu
    de lá porque a Supervisão passou a precisar da mesma resposta, e reescrevê-la no sinal seria a
    segunda verdade que este projeto vem removendo: a tela mandaria divulgar e o painel diria que
    está tudo divulgado, ou o contrário, e nada ficaria vermelho. `atos_publicados`, em
    `publicacoes`, **não** responde isto — ela responde os atos *do Edital*, abertura e
    Retificações.

    **Um ato por recorte** (`034`, `FR-490`). Sem o filtro por lista, a divulgação da ordem da
    ampla apareceria como defasada ao se abrir o recorte de PPI — e a tela mandaria divulgar de
    novo um ato que já está divulgado.

    **As duas formas de não estar divulgado** são devolvidas separadas porque se resolvem no mesmo
    lugar e se leem diferente: `nunca_divulgado` é o ato que ninguém publicou, e `defasadas` são as
    publicações vigentes de um ato anterior — o resultado que o público lê não é o que vale.

    `historico` entra pronto quando quem chama já o leu. A Supervisão percorre os recortes de um
    marco em sequência e a cadeia é **do marco**, não do recorte: relê-la por recorte custaria uma
    consulta por lista para devolver as mesmas linhas.
    """
    if ato is None:
        return None
    if historico is None:
        historico = historico_do_marco(edital=edital, marco_id=marco_id)
    vigentes = [
        linha["publicacao"]
        for linha in historico
        if linha["vigente"] and str(linha["publicacao"].ato.lista_id or "") == str(lista_id or "")
    ]
    defasadas = [publicacao for publicacao in vigentes if str(publicacao.ato_id) != str(ato.id)]
    return {"nunca_divulgado": not vigentes, "defasadas": defasadas}


__all__ = [
    "divulgacao_do_ato",
    "documento_do_resultado",
    "historico_do_marco",
    "publicacao_por_id",
    "situacoes_do_candidato",
    "vigente_do_marco",
    "vigentes_do_edital",
]
