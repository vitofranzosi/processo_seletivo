"""Leitura pública e de gestão do sorteio. Nenhuma escrita, e nenhuma recomposição."""

from processo_seletivo.sorteios.models import RelacaoDeHabilitados


def relacao_publica(relacao_id):
    """A relação publicada, por identidade. `None` quando não existe.

    Sem filtro de vigência: **relação sucedida continua respondendo no mesmo endereço**, dizendo
    que foi sucedida. Um endereço que deixasse de responder quebraria toda citação já publicada —
    manifesto, documento de resultado, ofício —, e é o precedente que a divulgação da `017` fixou.
    """
    return (
        RelacaoDeHabilitados.objects.filter(pk=relacao_id)
        .select_related("edital", "versao")
        .prefetch_related("sucessoras")
        .first()
    )


def relacao_vigente(*, edital, perfil_id, marco_id, lista_id=None):
    """A relação sem sucessora do recorte. Há **uma**, por constraint (FR-070)."""
    return (
        RelacaoDeHabilitados.objects.filter(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            sucessoras__isnull=True,
        )
        .order_by("-publicada_em")
        .first()
    )


def sorteios_do_edital(edital, conteudo):
    """O estado público de cada sorteio do Edital, para a página que qualquer pessoa abre.

    **É o passo que faltava para a promessa desta feature ser visível** (021, FR-011, FR-048). A
    relação congelada é pública, imutável e anterior à semente — e só respondia no endereço da
    própria identidade: página nenhuma do portal a apontava. Quem se inscreveu não descobria que
    participava de um sorteio, com que número, nem que a lista já estava fechada; e a garantia
    central do certame — *a lista fechou antes de existirem os números* — só era observável **depois
    do fato**, por quem chegasse à divulgação do resultado.

    **Duas consultas, e o custo não cresce com o número de recortes**: as relações vigentes do
    Edital e os sorteios vigentes dele, casados em memória pelo recorte. É a mesma regra de derivada
    zero que a `024` fixou para esta página.

    Só o que é **vigente** aparece. A relação sucedida continua consultável no endereço dela — e
    anunciá-la aqui ofereceria como atual um universo que já não é o comprometido.
    """
    from processo_seletivo.sorteios.models import Sorteio

    relacoes = list(
        RelacaoDeHabilitados.objects.filter(edital=edital, sucessoras__isnull=True).order_by(
            "publicada_em"
        )
    )
    if not relacoes:
        return []
    sorteios = {
        (str(s.perfil_id), str(s.marco_id), str(s.lista_id or "")): s
        for s in Sorteio.objects.filter(edital=edital, sucessores__isnull=True)
    }
    nomes = _nomes_dos_recortes(conteudo)
    return [
        {
            "relacao": relacao,
            "sorteio": sorteios.get(
                (str(relacao.perfil_id), str(relacao.marco_id), str(relacao.lista_id or ""))
            ),
            **nomes(relacao),
        }
        for relacao in relacoes
    ]


def _nomes_dos_recortes(conteudo):
    """Como o Edital nomeia perfil, marco e lista — para que o bloco não fale por identificador.

    Do conteúdo **vigente**, que é o que a pessoa está lendo nesta página. Não encontrando o nome —
    uma Retificação pode ter removido o item —, o rótulo simplesmente não aparece: inventar um seria
    afirmar uma denominação que o Edital não publica.
    """
    indice = {}
    for perfil in conteudo.get("profiles") or []:
        marcos = {
            str(marco.get("id")): marco.get("name") or ""
            for marco in perfil.get("classificationMilestones") or []
        }
        listas = {
            str(modalidade.get("id")): modalidade.get("name") or ""
            for modalidade in perfil.get("competitionModalities") or []
        }
        indice[str(perfil.get("id"))] = (perfil.get("name") or "", marcos, listas)

    def nomear(relacao):
        perfil_nome, marcos, listas = indice.get(str(relacao.perfil_id), ("", {}, {}))
        return {
            "perfil": perfil_nome,
            "marco": marcos.get(str(relacao.marco_id), ""),
            "lista": listas.get(str(relacao.lista_id), "") if relacao.lista_id else "",
        }

    return nomear


__all__ = ["relacao_publica", "relacao_vigente", "sorteios_do_edital"]
