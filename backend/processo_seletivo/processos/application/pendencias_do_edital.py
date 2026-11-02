"""O que está pendente num Edital publicado, dito por tipo (113, FR-3528 a FR-3536).

**Uma regra para duas leituras.** O relatório do Edital (`099`) chama de *providências* o que
ainda falta depois de encerrar; o encerramento (`113`) pergunta o que impede encerrar e o que só se
adverte. As duas perguntas leem os mesmos fatos, e por isso os tipos moram aqui, e não no relatório:
uma lista própria da confirmação divergiria do relatório na primeira mudança (D-004 da `113`).

**Mora em `processos`, e lê `recursos`, `divulgacao` e `publicacoes`.** É o sentido contrário ao de
sempre — essas apps importam `processos.models` —, e foi escolhido: quem aplica a regra é o
encerramento, que é deste app (R-001 da `113`). Para que carregar `processos` não puxe as outras
apps, os imports delas ficam **dentro das funções**.

Nada aqui é gravado: as situações são derivadas no instante em que se pergunta.
"""

from dataclasses import dataclass
from datetime import datetime

IMPEDIMENTO = "IMPEDIMENTO"
ADVERTENCIA = "ADVERTENCIA"

# Os tipos que a `099` já tinha, com o mesmo nome — o relatório os importa daqui.
RESULTADO_NAO_DIVULGADO = "RESULTADO_NAO_DIVULGADO"
DEFINITIVO_NAO_PUBLICADO = "DEFINITIVO_NAO_PUBLICADO"
REAVALIACAO_PENDENTE = "REAVALIACAO_PENDENTE"
PROVIDENCIA_PENDENTE = "PROVIDENCIA_PENDENTE"
APURACAO_DESATUALIZADA = "APURACAO_DESATUALIZADA"
CONVOCACAO_AGUARDANDO = "CONVOCACAO_AGUARDANDO"
CONVOCACAO_VENCIDA = "CONVOCACAO_VENCIDA"
RECURSO_AGUARDANDO = "RECURSO_AGUARDANDO"

# Os que a `113` acrescenta.
PERIODO_EM_CURSO = "PERIODO_EM_CURSO"
PERIODO_POR_ABRIR = "PERIODO_POR_ABRIR"
PERIODO_SEM_TERMINO = "PERIODO_SEM_TERMINO"
PRAZO_RECURSAL_EM_CURSO = "PRAZO_RECURSAL_EM_CURSO"
PRAZO_RECURSAL_NAO_DECLARADO = "PRAZO_RECURSAL_NAO_DECLARADO"
RETIFICACAO_HOMOLOGADA = "RETIFICACAO_HOMOLOGADA"
RETIFICACAO_EM_CURSO = "RETIFICACAO_EM_CURSO"
RASCUNHOS_NAO_ENVIAVEIS = "RASCUNHOS_NAO_ENVIAVEIS"


@dataclass(frozen=True)
class Situacao:
    especie: str
    tipo: str
    quantidade: int = 1
    #: O nome publicado do marco, nas situações de prazo, resultado e recurso.
    marco: str = ""
    #: O id do marco, para a tela levar até a condução dele (R-006).
    marco_id: str = ""
    #: O fim do período, do prazo recursal, ou o vencimento mais distante.
    ate: datetime | None = None
    retificacao_id: object = None
    #: A Retificação em curso não tem número: é identificada pela data de criação, como na `103`.
    criada_em: datetime | None = None
    #: Só nas Retificações em curso: `EM_ELABORACAO` ou `EM_REVISAO`.
    situacao_da_retificacao: str = ""


def recurso_pendente_do_marco(*, edital, marco):
    """`(reavaliação pendente, providência pendente)` do marco — as perguntas da publicabilidade.

    Só para marco com resultado publicado: sem publicação não há decisão de recurso a cumprir.
    Extraído do relatório da `099` (`_pendencias_de_recurso`), que passa a chamá-lo.
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application import selectors as recursos

    marco_id = str(marco["id"])
    publicacoes = list(
        PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id).values_list(
            "id", flat=True
        )
    )
    if not publicacoes:
        return False, False
    reavaliacao = bool(recursos.reavaliacoes_pendentes_do_marco(edital=edital, marco=marco))
    providencia = bool(
        recursos.providencias_pendentes_do_marco(
            edital=edital, marco_id=marco_id, marco=marco, publicacoes_do_marco=publicacoes
        )
    )
    return reavaliacao, providencia


def situacoes(edital, *, agora, ato="encerrar", com_advertencias=False):
    """As situações pendentes do Edital publicado, no instante `agora` (113).

    `ato="encerrar"` separa impedimento de advertência (FR-3528 a FR-3534); `ato="cancelar"`
    devolve as mesmas situações, todas como advertência, mais as inscrições em preenchimento
    (FR-3536). Sem `com_advertencias`, só os impedimentos — que é o que o comando confere, sob as
    travas, sem pagar a leitura do resto.

    As advertências da `099` (convocação, resultado, apuração) **não** saem daqui: são do relatório,
    e a confirmação as lê dele (FR-3535). Aqui ficam só as que a `113` acrescenta.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version

    conteudo = effective_version(edital_id=edital.id, at=agora).content
    marcos = _marcos_do_conteudo(conteudo)
    achadas = []
    achadas.extend(_do_periodo(conteudo, agora, com_advertencias=com_advertencias))
    achadas.extend(_dos_prazos_recursais(edital, marcos, agora, com_advertencias=com_advertencias))
    achadas.extend(_dos_recursos(edital, marcos))
    achadas.extend(_das_retificacoes(edital, com_advertencias=com_advertencias))
    if ato == "cancelar":
        if com_advertencias:
            achadas.extend(_dos_rascunhos(edital, conteudo, agora))
        return [_como_advertencia(situacao) for situacao in achadas]
    return achadas if com_advertencias else [s for s in achadas if s.especie == IMPEDIMENTO]


def impedimentos(edital, *, agora):
    """Só o que impede encerrar — a pergunta do comando (FR-3528)."""
    return situacoes(edital, agora=agora)


def _como_advertencia(situacao):
    if situacao.especie == ADVERTENCIA:
        return situacao
    return Situacao(**{**situacao.__dict__, "especie": ADVERTENCIA})


def _marcos_do_conteudo(conteudo):
    """`{id do marco: marco}` do conteúdo vigente — o nome publicado e a declaração de recurso."""
    return {
        str(marco["id"]): marco
        for perfil in conteudo.get("profiles") or []
        for marco in perfil.get("classificationMilestones") or []
        if marco.get("id")
    }


def _do_periodo(conteudo, agora, *, com_advertencias):
    """FR-3529. Por abrir e em curso com término impedem; sem término só adverte (D-008 da `113`).

    **Sem término declarado o período recebe para sempre** — a régua do recebimento não inventa
    prazo —, e impedir por ele tornaria o encerramento impossível. O Edital que não fixou o fim
    tem no encerramento o ato que põe fim ao recebimento, e a confirmação diz isso.
    """
    from processo_seletivo.inscricoes.domain import periodo as periodo_do_edital

    periodo = periodo_do_edital.periodo_de_inscricoes(conteudo, agora)
    if periodo.estado == periodo_do_edital.FUTURO:
        return [Situacao(IMPEDIMENTO, PERIODO_POR_ABRIR, ate=periodo.inicio)]
    if periodo.estado != periodo_do_edital.ABERTO:
        return []
    if periodo.fim is not None:
        return [Situacao(IMPEDIMENTO, PERIODO_EM_CURSO, ate=periodo.fim)]
    return [Situacao(ADVERTENCIA, PERIODO_SEM_TERMINO)] if com_advertencias else []


def _dos_prazos_recursais(edital, marcos, agora, *, com_advertencias):
    """FR-3530. A janela é a que a interposição aplica, e por isso a conta é a da publicabilidade.

    **Só o prazo declarado e computável impede** (D-002 da `113`): sem prazo, a interposição é
    aceita para sempre, e impedir por isso tornaria o encerramento impossível. Esse caso é
    advertência — recursos continuam podendo chegar —, salvo quando o Edital declarou que o marco
    **não** admite recurso, que é norma, e não silêncio.

    Percorre os recortes que têm resultado divulgado, e não os marcos do conteúdo: o marco que uma
    Retificação tirou do conteúdo continua com a publicação dele, e a interposição continua lendo a
    norma que o ato citou.
    """
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.publicabilidade import janela_aberta_ate
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application.selectors import conteudo_citado
    from processo_seletivo.recursos.domain.janela import (
        admite_recurso,
        declaracao_aplicavel,
        declaracao_do_marco,
        janela_da_publicacao,
    )

    recortes = (
        PublicacaoResultado.objects.filter(edital=edital)
        .values_list("marco_id", "lista_id")
        .distinct()
    )
    em_curso = {}
    nao_declarados = {}
    for marco_id, lista_id in recortes:
        marco_id = str(marco_id)
        marco = marcos.get(marco_id)
        nome = (marco or {}).get("name") or ""
        fecha = janela_aberta_ate(
            edital=edital, marco_id=marco_id, marco=marco, at=agora, lista_id=lista_id
        )
        if fecha is not None:
            # Duas listas do mesmo marco são um prazo só para quem lê: vale o que fecha por último.
            if marco_id not in em_curso or fecha > em_curso[marco_id][1]:
                em_curso[marco_id] = (nome, fecha)
            continue
        if not com_advertencias or marco_id in nao_declarados:
            continue
        vigente = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
        declaracao = declaracao_aplicavel(
            declaracao_do_marco(conteudo_citado(vigente), marco_id),
            (marco or {}).get("appealWindow"),
        )
        if (
            janela_da_publicacao(vigente, declaracao) is None
            and admite_recurso(declaracao) is not False
        ):
            nao_declarados[marco_id] = nome
    achadas = [
        Situacao(IMPEDIMENTO, PRAZO_RECURSAL_EM_CURSO, marco=nome, marco_id=marco_id, ate=fecha)
        for marco_id, (nome, fecha) in em_curso.items()
    ]
    achadas.extend(
        Situacao(ADVERTENCIA, PRAZO_RECURSAL_NAO_DECLARADO, marco=nome, marco_id=marco_id)
        for marco_id, nome in nao_declarados.items()
        if marco_id not in em_curso
    )
    return achadas


def _dos_recursos(edital, marcos):
    """FR-3531 e FR-3532 — as peças sem decisão e as decisões sem cumprimento."""
    from processo_seletivo.recursos.application.selectors import aguardando_decisao

    achadas = []
    aguardando = aguardando_decisao().filter(inscricao__edital=edital).count()
    if aguardando:
        achadas.append(Situacao(IMPEDIMENTO, RECURSO_AGUARDANDO, quantidade=aguardando))
    for marco_id, marco in marcos.items():
        reavaliacao, providencia = recurso_pendente_do_marco(edital=edital, marco=marco)
        nome = marco.get("name") or ""
        if reavaliacao:
            achadas.append(
                Situacao(IMPEDIMENTO, REAVALIACAO_PENDENTE, marco=nome, marco_id=marco_id)
            )
        if providencia:
            achadas.append(
                Situacao(IMPEDIMENTO, PROVIDENCIA_PENDENTE, marco=nome, marco_id=marco_id)
            )
    return achadas


def _das_retificacoes(edital, *, com_advertencias):
    """FR-3533 e FR-3534. A homologada impede; em elaboração e em revisão só se advertem (D-003)."""
    from processo_seletivo.publicacoes.models_retificacao import Retificacao

    em_curso = Retificacao.objects.filter(
        edital=edital,
        status__in=(
            Retificacao.Status.HOMOLOGADA,
            Retificacao.Status.EM_REVISAO,
            Retificacao.Status.EM_ELABORACAO,
        ),
    ).order_by("created_at", "id")
    achadas = []
    for retificacao in em_curso:
        if retificacao.status == Retificacao.Status.HOMOLOGADA:
            achadas.append(
                Situacao(
                    IMPEDIMENTO,
                    RETIFICACAO_HOMOLOGADA,
                    retificacao_id=retificacao.id,
                    criada_em=retificacao.created_at,
                )
            )
        elif com_advertencias:
            achadas.append(
                Situacao(
                    ADVERTENCIA,
                    RETIFICACAO_EM_CURSO,
                    retificacao_id=retificacao.id,
                    criada_em=retificacao.created_at,
                    situacao_da_retificacao=retificacao.status,
                )
            )
    return achadas


def _dos_rascunhos(edital, conteudo, agora):
    """FR-3536 — as inscrições em preenchimento que o cancelamento impede de enviar."""
    from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes
    from processo_seletivo.inscricoes.models import Inscricao

    if not periodo_de_inscricoes(conteudo, agora).aberto:
        return []
    quantos = Inscricao.objects.filter(edital=edital, status=Inscricao.Status.RASCUNHO).count()
    return [Situacao(ADVERTENCIA, RASCUNHOS_NAO_ENVIAVEIS, quantidade=quantos)] if quantos else []


# --- A redação ------------------------------------------------------------------------------------
#
# **A frase mora com a regra**, e não na tela: a recusa do comando e a confirmação dizem o mesmo
# texto (FR-3528, `contracts/encerramento.md`), e duas redações divergiriam. As advertências da
# `099` não estão aqui — a confirmação usa a frase do relatório para elas (FR-3535).


def _instante(momento):
    from processo_seletivo.shared.tempo import ZONA

    return momento.astimezone(ZONA).strftime("%d/%m/%Y às %H:%M")


def _dia(momento):
    from processo_seletivo.shared.tempo import ZONA

    return momento.astimezone(ZONA).strftime("%d/%m/%Y")


def _plural(n, singular, plural):
    return singular if n == 1 else plural


def frase(situacao, ato="encerrar"):
    """A frase da situação, sem pessoa nenhuma (FR-3540).

    **No cancelamento, o que é atingido, e não o que fazer antes.** "Altere o período ou cancele o
    Edital" na tela de cancelar mandaria fazer o próprio ato; ali a frase diz o efeito. As aspas são
    as da `099` (“ ”), que divide a mesma tela.
    """
    n = situacao.quantidade
    tipo = situacao.tipo
    if ato == "cancelar":
        no_cancelamento = _frase_no_cancelamento(situacao)
        if no_cancelamento:
            return no_cancelamento
    if tipo == PERIODO_EM_CURSO:
        return (
            f"O período de inscrições vai até {_instante(situacao.ate)}. Encerrar antes disso não "
            "é conclusão regular: altere o período por Retificação ou cancele o Edital"
        )
    if tipo == PERIODO_POR_ABRIR:
        return (
            f"O período de inscrições ainda não começou (abre em {_instante(situacao.ate)}). Para "
            "desistir do Edital, cancele-o"
        )
    if tipo == PERIODO_SEM_TERMINO:
        return (
            "O Edital não declarou o término das inscrições: o encerramento põe fim ao recebimento"
        )
    if tipo == PRAZO_RECURSAL_EM_CURSO:
        return f"O prazo de recurso contra “{situacao.marco}” vai até {_instante(situacao.ate)}"
    if tipo == PRAZO_RECURSAL_NAO_DECLARADO:
        return (
            f"O Edital não declarou prazo de recurso contra “{situacao.marco}”: recursos continuam "
            "podendo ser interpostos depois do encerramento"
        )
    if tipo == RECURSO_AGUARDANDO:
        return f"{n} {_plural(n, 'recurso aguarda', 'recursos aguardam')} decisão"
    if tipo == REAVALIACAO_PENDENTE:
        return f"Reavaliação determinada em recurso ainda não concluída em “{situacao.marco}”"
    if tipo == PROVIDENCIA_PENDENTE:
        return f"Providência determinada em recurso ainda não cumprida em “{situacao.marco}”"
    if tipo == RETIFICACAO_HOMOLOGADA:
        return (
            f"A Retificação de {_dia(situacao.criada_em)} foi homologada e não publicada. "
            "Publique-a ou devolva-a"
        )
    if tipo == RETIFICACAO_EM_CURSO:
        from processo_seletivo.publicacoes.models_retificacao import Retificacao

        em_revisao = situacao.situacao_da_retificacao == Retificacao.Status.EM_REVISAO
        estado = "em revisão" if em_revisao else "em elaboração"
        return f"A Retificação de {_dia(situacao.criada_em)}, {estado}, não poderá mais prosseguir"
    if tipo == RASCUNHOS_NAO_ENVIAVEIS:
        return (
            f"{n} {_plural(n, 'inscrição em preenchimento', 'inscrições em preenchimento')} "
            f"{_plural(n, 'não poderá ser enviada', 'não poderão ser enviadas')}"
        )
    raise ValueError(tipo)


def _frase_no_cancelamento(situacao):
    tipo = situacao.tipo
    if tipo == PERIODO_EM_CURSO:
        return (
            f"O período de inscrições iria até {_instante(situacao.ate)}: o cancelamento põe fim "
            "ao recebimento agora"
        )
    if tipo == PERIODO_POR_ABRIR:
        return f"O período de inscrições abriria em {_instante(situacao.ate)}, e não abrirá"
    if tipo == RETIFICACAO_HOMOLOGADA:
        return (
            f"A Retificação de {_dia(situacao.criada_em)} foi homologada e não poderá ser publicada"
        )
    return ""
