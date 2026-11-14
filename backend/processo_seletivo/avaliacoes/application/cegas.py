"""O parecer às cegas e a exposição (165, FR-7056 a FR-7058, FR-7082, FR-7083, research T-013).

**No servidor, e não na tela.** Esconder no template deixaria o dado no contexto, no fragmento e no
link direto. Aqui, a linha que vai à tela já sai sem o sentido, sem a nota, sem o parecer e sem a
ficha — e o que não sai não tem como vazar.

**Só na Etapa colegiada.** Na Etapa de uma avaliação não há pares: o que esta regra protege é a
independência entre membros que deliberam sobre a mesma inscrição. Aplicá-la ali mudaria telas de
hoje sem proteger nada.

**Duas perguntas, e as duas são de inscrição × Etapa.** Quem tem parecer pendente sobre a inscrição
não recebe o dos outros (a pendência); e quem já recebeu não avalia mais aquela inscrição ali, nem
tem o próprio parecer reaberto (a exposição, D-010). O fato que decide a segunda é a **entrega**, e
não o papel: quem só tem a permissão de ver, e não viu, não está exposto.
"""

from django.utils import timezone

from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, ExposicaoAoParecer
from processo_seletivo.resultados.domain import deliberacao

OCULTO = "Oculto: você ainda tem parecer pendente sobre esta inscrição."


def colegiada(etapa) -> bool:
    """A Etapa vigente é colegiada? Recebe o dicionário do conteúdo publicado."""
    return deliberacao.colegiada(etapa)


def pendentes(subject, edital, etapa_id) -> set:
    """As inscrições sobre as quais esta pessoa tem parecer pendente nesta Etapa, numa consulta.

    Pendente é Atribuição **ativa** sem conclusão vigente: a que nunca concluiu, e a reaberta, que
    voltou a ser trabalho (FR-7058).
    """
    if not subject:
        return set()
    return set(
        Atribuicao.objects.filter(
            membro__identity_subject=subject,
            edital=edital,
            etapa_id=etapa_id,
            ativo=True,
        )
        .exclude(avaliacao__estado=Avaliacao.Estado.CONCLUIDA)
        .values_list("inscricao_id", flat=True)
    )


def _autor(linha):
    membro = linha.get("membro")
    return getattr(membro, "identity_subject", None)


def ocultar(linhas, subject, pendentes_):
    """Esvazia, nas linhas de **outros** autores sobre as inscrições pendentes, o que é conteúdo.

    A linha continua existindo — quem preside precisa saber que há conclusão ali, e de quem —, mas
    sem o sentido, a nota, o parecer e a ficha. `conclusao_exibivel` vira a frase que diz por quê,
    e é ela que a tela mostra no lugar da conclusão.
    """
    for linha in linhas:
        inscricao = linha.get("inscricao")
        if getattr(inscricao, "id", None) in pendentes_ and _autor(linha) != subject:
            linha["oculta"] = True
            linha["conclusao_exibivel"] = OCULTO
            linha["ficha"] = None
    return linhas


def entregues(linhas, subject) -> set:
    """As inscrições cujo parecer de **outro** autor estas linhas entregam, sem ocultação."""
    return {
        linha["inscricao"].id
        for linha in linhas
        if not linha.get("oculta") and _autor(linha) and _autor(linha) != subject
    }


def registrar_exposicao(subject, edital, etapa_id, inscricao_ids, *, agora=None):
    """Grava o fato da entrega, uma linha por inscrição, sem repetir a que já existe (FR-7082).

    `ON CONFLICT DO NOTHING` não é `UPDATE`, e por isso passa pelo gatilho append-only: a segunda
    entrega da mesma inscrição à mesma pessoa não diz nada que a primeira não tenha dito.
    """
    ids = {identidade for identidade in inscricao_ids if identidade}
    if not subject or not ids:
        return
    agora = agora or timezone.now()
    ExposicaoAoParecer.objects.bulk_create(
        [
            ExposicaoAoParecer(
                edital=edital,
                etapa_id=etapa_id,
                inscricao_id=identidade,
                pessoa=subject,
                registrada_em=agora,
            )
            for identidade in ids
        ],
        ignore_conflicts=True,
    )


def proteger_linhas(linhas, *, subject, edital, etapa, etapa_id):
    """O às cegas e a exposição de uma tela que entrega conclusões: ocultar, e registrar o resto.

    Chamada pelas views, depois do seletor e antes de renderizar: a linha oculta não é exposição, e
    a entregue é. Fora da Etapa colegiada não faz nada.
    """
    if not colegiada(etapa):
        return linhas
    ocultar(linhas, subject, pendentes(subject, edital, etapa_id))
    registrar_exposicao(subject, edital, etapa_id, entregues(linhas, subject))
    return linhas


def pares_expostos(edital_id, etapa_id, pessoas, inscricao_ids) -> set:
    """`{(pessoa, inscricao_id)}` expostos entre estas pessoas e inscrições, numa consulta.

    A leitura única da exposição: a distribuição a pergunta para o lote, e a reabertura para um par
    (FR-7082, FR-7083).
    """
    pessoas = {pessoa for pessoa in pessoas if pessoa}
    inscricao_ids = [identidade for identidade in inscricao_ids if identidade]
    if not pessoas or not inscricao_ids:
        return set()
    return set(
        ExposicaoAoParecer.objects.filter(
            edital_id=edital_id,
            etapa_id=etapa_id,
            pessoa__in=pessoas,
            inscricao_id__in=inscricao_ids,
        ).values_list("pessoa", "inscricao_id")
    )


__all__ = [
    "OCULTO",
    "colegiada",
    "entregues",
    "ocultar",
    "pares_expostos",
    "pendentes",
    "proteger_linhas",
    "registrar_exposicao",
]
