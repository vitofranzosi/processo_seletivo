"""As leituras dos avisos: histórico, estado de cada destinatário, linha de estado e alerta (066).

**Consultas constantes no número de destinatários** (`R-015`, `test_orcamento_do_aviso.py`). O
estado de cada um é derivado em Python a partir de três leituras — destinatários, tentativas,
resultados —, e não de uma consulta por linha: um aviso de quinhentas pessoas que perguntasse uma a
uma pagaria quinhentas consultas para desenhar uma tabela.

**"Aceita pelo servidor de correio", e nunca "entregue"** (`UX-172`). O vocabulário dos estados mora
em `avisos/domain/nomes.py::ROTULO_DO_ESTADO`, e a tela só o lê.
"""

from datetime import timedelta

from django.conf import settings
from django.db.models import Count, Prefetch, Q

from processo_seletivo.avisos.domain import estado as estado_
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso, TentativaDeEnvio
from processo_seletivo.shared.api.problems import DomainError


def aviso_do_ator(actor, aviso_id):
    """O aviso, se o ator o alcança pelo escopo; o de outra unidade é inexistente (`FR-1276`)."""
    aviso = (
        Aviso.objects.filter(pk=aviso_id, institution_scope=getattr(actor, "institution_scope", ""))
        .select_related("edital__processo", "modelo", "aviso_anterior")
        .first()
        if actor is not None
        else None
    )
    if aviso is None:
        raise DomainError(nomes.AVISO_NAO_ENCONTRADO, "Aviso não encontrado.", 404)
    return aviso


def _destinatarios_com_tentativas(aviso):
    return list(
        DestinatarioDoAviso.objects.filter(aviso=aviso)
        .select_related("inscricao")
        .prefetch_related(
            Prefetch(
                "tentativas",
                queryset=TentativaDeEnvio.objects.select_related("resultado").order_by("numero"),
            )
        )
        .order_by("inscricao__protocolo", "id")
    )


def tentativas_de(destinatario):
    return [
        estado_.Tentativa(
            tentativa.numero,
            tentativa.iniciada_em,
            getattr(getattr(tentativa, "resultado", None), "resultado", None),
            getattr(getattr(tentativa, "resultado", None), "registrado_em", None),
        )
        for tentativa in destinatario.tentativas.all()
    ]


def estados_do_aviso(aviso, *, agora):
    """`[(destinatario, estado, tentativas)]`, na ordem do protocolo."""
    interrompido = _tem_interrupcao(aviso)
    linhas = []
    for destinatario in _destinatarios_com_tentativas(aviso):
        tentativas = tentativas_de(destinatario)
        linhas.append(
            (
                destinatario,
                estado_.estado_do_destinatario(
                    elegibilidade=destinatario.elegibilidade,
                    endereco=destinatario.endereco,
                    tentativas=tentativas,
                    interrompido=interrompido,
                    solicitado_em=aviso.solicitado_em,
                    agora=agora,
                    max_tentativas=settings.AVISOS_MAX_TENTATIVAS,
                    janela_horas=settings.AVISOS_JANELA_DE_DESPACHO_HORAS,
                ),
                tentativas,
            )
        )
    return linhas


def _tem_interrupcao(aviso):
    from processo_seletivo.avisos.models import InterrupcaoDoAviso

    try:
        return aviso.interrupcao is not None
    except InterrupcaoDoAviso.DoesNotExist:
        return False


def contagens(estados):
    """Quantos destinatários em cada estado, com o rótulo da tela (`UX-172`)."""
    por_estado = {}
    for _, estado, _ in estados:
        por_estado[estado] = por_estado.get(estado, 0) + 1
    return [
        {"estado": estado, "rotulo": nomes.ROTULO_DO_ESTADO[estado], "quantos": quantos}
        for estado, quantos in sorted(por_estado.items(), key=lambda par: _ORDEM.index(par[0]))
    ]


_ORDEM = [
    nomes.ESTADO_ACEITA,
    nomes.PENDENTE,
    nomes.EM_ENVIO,
    nomes.ESTADO_FALHA_TEMPORARIA,
    nomes.ESTADO_FALHA_DEFINITIVA,
    nomes.ESTADO_INDETERMINADA,
    nomes.INTERROMPIDO_ANTES_DO_ENVIO,
    nomes.EXPIRADA_SEM_ENVIO,
    nomes.SEM_ENDERECO,
    nomes.NAO_ELEGIVEL,
]


def despacho_parado(aviso, estados, *, agora):
    """`FR-1272`: pendente há mais que o limite — o timer pode estar parado ou desabilitado."""
    limite = aviso.solicitado_em + timedelta(minutes=settings.AVISOS_ALERTA_DE_PENDENTE_MIN)
    return agora >= limite and any(estado == nomes.PENDENTE for _, estado, _ in estados)


def historico(aviso, *, agora):
    """O que a tela do aviso mostra (contracts/telas.md): texto, ato, contagens, linhas e alerta."""
    estados = estados_do_aviso(aviso, agora=agora)
    aceitas = sum(1 for _, estado, _ in estados if estado == nomes.ESTADO_ACEITA)
    return {
        "aviso": aviso,
        "publicacoes": list(aviso.publicacoes.select_related("publicacao").order_by("id")),
        "estados": [
            {
                "destinatario": destinatario,
                "estado": estado,
                "rotulo": nomes.ROTULO_DO_ESTADO[estado],
                "motivo": nomes.MOTIVO_DA_INELEGIBILIDADE.get(destinatario.elegibilidade, ""),
                "tentativas": len(tentativas),
            }
            for destinatario, estado, tentativas in estados
        ],
        "contagens": contagens(estados),
        "aceitas": aceitas,
        "concluido": estado_.concluido([estado for _, estado, _ in estados]),
        "interrompido": _tem_interrupcao(aviso),
        "despacho_parado": despacho_parado(aviso, estados, agora=agora),
        "reenvio_de_falhas": reenvio_de_falhas_de(aviso),
        "reenviaveis": {
            motivo: sum(1 for _, estado, _ in estados if estado in alcance)
            for motivo, alcance in nomes.ALCANCE_DO_REENVIO.items()
        },
    }


def reenvio_de_falhas_de(aviso):
    """O reenvio de falhas que este aviso já teve, ou `None` — há no máximo um (`FR-1264`)."""
    return (
        Aviso.objects.filter(aviso_anterior=aviso, motivo=nomes.REENVIO_DE_FALHAS)
        .order_by("solicitado_em")
        .first()
    )


def ultimo_aviso_das_publicacoes(publicacoes):
    """O aviso mais recente que citou alguma destas publicações, ou `None` (`UX-175`)."""
    return (
        Aviso.objects.filter(publicacoes__publicacao__in=publicacoes)
        .order_by("-solicitado_em")
        .distinct()
        .first()
    )


def linha_de_estado(aviso, *, agora):
    """A linha "Aviso de 09/10, 14:02: 128 aceitas pelo servidor…", ou `None` (`UX-175`)."""
    if aviso is None:
        return None
    return {"aviso": aviso, "contagens": contagens(estados_do_aviso(aviso, agora=agora))}


def avisos_do_edital(edital):
    """Os avisos do Edital, do mais recente ao mais antigo, com quantos tinham endereço."""
    return list(
        Aviso.objects.filter(edital=edital)
        .annotate(
            com_endereco=Count(
                "destinatarios",
                filter=Q(destinatarios__elegibilidade=nomes.ELEGIVEL)
                & ~Q(destinatarios__endereco=""),
            )
        )
        .select_related("aviso_anterior")
        .order_by("-solicitado_em")
    )


__all__ = [
    "aviso_do_ator",
    "avisos_do_edital",
    "contagens",
    "despacho_parado",
    "estados_do_aviso",
    "historico",
    "linha_de_estado",
    "reenvio_de_falhas_de",
    "tentativas_de",
    "ultimo_aviso_das_publicacoes",
]
