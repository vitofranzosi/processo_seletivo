"""Quem o ato alcançou: o universo de cada origem, e a elegibilidade de cada um (`D-002`, `D-003`).

**Os destinatários saem do ato, e nunca de filtro.** No resultado, as `SituacaoDivulgada` que a
publicação gravou na mesma transação em que publicou — inclusive as sem posição. Na chamada, as
convocações cuja comunicação por publicação declarou aquela referência. Ninguém acrescenta nem tira
(`FR-1252`); a única ausência que o sistema determina é a falta de endereço e, na chamada, a
convocação que já não segue em curso.

**Só leitura.** Nada aqui grava: a prévia lê, e a confirmação relê sob a trava do Processo, para que
a lista confirmada seja a da hora da confirmação, e a assinatura diga se ela mudou desde a prévia.
"""

import json
from dataclasses import dataclass, field

from django.db.models import Prefetch

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import PublicacaoDoAviso
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.identidade.application.endereco import enderecos_das_inscricoes
from processo_seletivo.shared.api.problems import DomainError


@dataclass(frozen=True)
class Linha:
    """Uma inscrição do universo, com o que decide se a mensagem vai a ela."""

    inscricao: object
    elegibilidade: str
    endereco: str
    convocacao: object = None

    @property
    def recebe(self):
        return self.elegibilidade == nomes.ELEGIVEL and bool(self.endereco)


@dataclass
class Universo:
    """O ato citado e as linhas dele. É o que a prévia mostra e a confirmação grava."""

    origem: str
    edital: object
    perfil_id: object
    marco_id: object
    linhas: list
    natureza: str = ""
    lista_id: object = None
    publicacoes: list = field(default_factory=list)
    referencia: str = ""
    cabecalho: dict = field(default_factory=dict)
    datas_retificadas: list = field(default_factory=list)
    data_da_publicacao: object = None
    ja_avisado: bool = False

    @property
    def retificadora(self):
        return bool(self.datas_retificadas)

    @property
    def recebem(self):
        return [linha for linha in self.linhas if linha.recebe]

    def contagens(self):
        elegiveis = [linha for linha in self.linhas if linha.elegibilidade == nomes.ELEGIVEL]
        return {
            "universo": len(self.linhas),
            "com_endereco": sum(1 for linha in elegiveis if linha.endereco),
            "sem_endereco": sum(1 for linha in elegiveis if not linha.endereco),
            "nao_elegiveis": len(self.linhas) - len(elegiveis),
        }

    def inelegiveis_por_motivo(self):
        contagem = {}
        for linha in self.linhas:
            if linha.elegibilidade != nomes.ELEGIVEL:
                motivo = nomes.MOTIVO_DA_INELEGIBILIDADE[linha.elegibilidade]
                contagem[motivo] = contagem.get(motivo, 0) + 1
        return contagem


def cabecalho_de(publicacao):
    """O cabeçalho que a publicação congelou nos bytes: processo, Edital, Perfil, marco, lista."""
    return json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))["cabecalho"]


def vigentes_da_natureza(*, edital, marco_id, natureza):
    """As publicações vigentes do marco com a natureza pedida, uma por lista."""
    return list(
        PublicacaoResultado.objects.filter(
            edital=edital, marco_id=marco_id, natureza=natureza, sucessoras__isnull=True
        )
        .select_related("publicacao_anterior")
        .order_by("publicado_em", "id")
    )


def ja_avisadas(publicacoes):
    """Os ids das publicações que algum primeiro aviso já citou — em qualquer estado.

    **Interrompido e expirado também contam** (data-model §3): o aviso existiu, e avisar de novo
    sobre a mesma publicação é reenvio justificado, e não primeiro aviso (`FR-1262`).
    """
    return set(
        PublicacaoDoAviso.objects.filter(
            publicacao__in=publicacoes, aviso__motivo=nomes.PRIMEIRO_AVISO
        ).values_list("publicacao_id", flat=True)
    )


def naturezas_pendentes(*, edital, marco_id):
    """As naturezas com publicação vigente que nenhum aviso citou — o que "Avisar" oferece."""
    pendentes = []
    for natureza in (Natureza.PRELIMINAR, Natureza.DEFINITIVA):
        vigentes = vigentes_da_natureza(edital=edital, marco_id=marco_id, natureza=natureza)
        if vigentes and len(ja_avisadas(vigentes)) < len(vigentes):
            pendentes.append(str(natureza))
    return pendentes


def universo_do_resultado(*, edital, marco_id, natureza, reenvio=False):
    """O universo do aviso de resultado (`FR-1246`, `FR-1247`, `D-002`).

    **Primeiro aviso**: as vigentes da natureza que nenhum aviso citou. Na primeira vez, todas as
    listas do marco; depois de uma retificação, só a sucessora, e o aviso alcança quem ela
    considerou. **Reenvio justificado** (`reenvio=True`): todas as vigentes da natureza.

    **Uma linha por inscrição** (`FR-1249`): quem concorre na ampla e numa reserva aparece nas duas
    publicações e recebe um aviso só.
    """
    if natureza not in nomes.NATUREZAS:
        raise DomainError(nomes.AVISO_SEM_ATO, "Natureza de resultado desconhecida.", 404)
    vigentes = vigentes_da_natureza(edital=edital, marco_id=marco_id, natureza=natureza)
    if not vigentes:
        raise DomainError(
            nomes.AVISO_SEM_ATO,
            "Não há resultado desta natureza publicado neste marco: não há ato a avisar.",
            404,
        )
    avisadas = ja_avisadas(vigentes)
    publicacoes = vigentes if reenvio else [p for p in vigentes if p.id not in avisadas]
    linhas = []
    if publicacoes:
        situacoes = (
            SituacaoDivulgada.objects.filter(publicacao__in=publicacoes)
            .select_related("inscricao")
            .order_by("inscricao__protocolo", "inscricao_id")
        )
        inscricoes = {}
        for situacao in situacoes:
            inscricoes.setdefault(situacao.inscricao_id, situacao.inscricao)
        enderecos = enderecos_das_inscricoes(inscricoes.values())
        linhas = [
            Linha(inscricao, nomes.ELEGIVEL, enderecos.get(inscricao.id, ""))
            for inscricao in inscricoes.values()
        ]
    referencia = publicacoes[0] if publicacoes else vigentes[0]
    return Universo(
        origem=nomes.RESULTADO,
        edital=edital,
        perfil_id=referencia.perfil_id,
        marco_id=marco_id,
        natureza=natureza,
        publicacoes=publicacoes,
        linhas=linhas,
        cabecalho=cabecalho_de(referencia),
        datas_retificadas=[
            p.publicacao_anterior.publicado_em for p in publicacoes if p.publicacao_anterior_id
        ],
        data_da_publicacao=max((p.publicado_em for p in publicacoes), default=None),
        ja_avisado=bool(avisadas),
    )


# --- A chamada comunicada por publicação (D-003) ---------------------------------------------


def _comunicacoes_da_referencia(*, edital, marco_id, lista_id, referencia):
    from processo_seletivo.convocacao.models import ComunicacaoEmitida
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO

    return ComunicacaoEmitida.objects.filter(
        convocacao__edital=edital,
        convocacao__marco_id=marco_id,
        convocacao__lista_id=lista_id,
        forma=FORMA_POR_PUBLICACAO,
        resultado="ENVIADA",
        referencia_da_publicacao=referencia,
    )


def universo_da_chamada(*, edital, marco_id, lista_id, comunicacao_id, agora):
    """O universo do aviso de chamada: histórico, com a elegibilidade de agora ao lado (`FR-1251`).

    **O universo não muda com o tempo.** São todas as convocações do recorte cuja comunicação por
    publicação enviada traz a referência da comunicação âncora — inclusive as que depois tiveram
    desfecho, foram sucedidas ou venceram. **A elegibilidade muda**, e é lida dos seletores da
    `019`, sem reescrever regra de convocação nenhuma.
    """
    from processo_seletivo.convocacao.application.comunicar import forma_declarada
    from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
        FORMA_POR_MENSAGEM_INDIVIDUAL,
        FORMA_POR_PUBLICACAO,
    )

    ancora = (
        ComunicacaoEmitida.objects.filter(
            id=comunicacao_id,
            convocacao__edital=edital,
            convocacao__marco_id=marco_id,
            convocacao__lista_id=lista_id,
        )
        .select_related("convocacao__versao")
        .first()
    )
    if ancora is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    if forma_declarada(ancora.convocacao) == FORMA_POR_MENSAGEM_INDIVIDUAL:
        raise DomainError(
            nomes.AVISO_CHAMADA_POR_MENSAGEM_INDIVIDUAL,
            "Este Perfil convoca por mensagem individual: a pessoa já recebeu a comunicação que "
            "conta, e um segundo e-mail sobre a mesma chamada a faria perguntar qual vale.",
            409,
        )
    if ancora.forma != FORMA_POR_PUBLICACAO or ancora.resultado != "ENVIADA":
        raise DomainError(
            nomes.AVISO_SEM_ATO,
            "Esta comunicação não é uma chamada publicada: não há ato a avisar.",
            404,
        )
    referencia = ancora.referencia_da_publicacao
    ids = (
        _comunicacoes_da_referencia(
            edital=edital, marco_id=marco_id, lista_id=lista_id, referencia=referencia
        )
        .values_list("convocacao_id", flat=True)
        .distinct()
    )
    convocacoes = list(
        Convocacao.objects.filter(id__in=list(ids))
        .select_related("inscricao")
        .prefetch_related(
            "desfechos",
            "comunicacoes",
            Prefetch("sucessoras", queryset=Convocacao.objects.only("id", "convocacao_anterior")),
        )
        .order_by("inscricao__protocolo", "inscricao_id", "criado_em")
    )
    por_inscricao = {}
    for convocacao in convocacoes:
        por_inscricao.setdefault(convocacao.inscricao_id, convocacao)
    enderecos = enderecos_das_inscricoes(c.inscricao for c in por_inscricao.values())
    linhas = []
    for convocacao in por_inscricao.values():
        elegibilidade = elegibilidade_da_convocacao(convocacao, agora=agora)
        linhas.append(
            Linha(
                convocacao.inscricao,
                elegibilidade,
                enderecos.get(convocacao.inscricao_id, ""),
                convocacao=convocacao,
            )
        )
    datas = _comunicacoes_da_referencia(
        edital=edital, marco_id=marco_id, lista_id=lista_id, referencia=referencia
    ).values_list("enviado_em", flat=True)
    from processo_seletivo.classificacao.domain.nomes import edital_por_extenso

    perfil = _perfil_da_versao(ancora.convocacao)
    return Universo(
        origem=nomes.CHAMADA,
        edital=edital,
        perfil_id=ancora.convocacao.perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        referencia=referencia,
        linhas=linhas,
        cabecalho={
            "processo": edital.processo.title,
            "edital": edital_por_extenso(ancora.convocacao.versao.content or {}, edital),
            "perfil": (perfil or {}).get("name", "") or "",
        },
        data_da_publicacao=max(datas, default=None),
        ja_avisado=_chamada_ja_avisada(edital, marco_id, lista_id, referencia),
    )


def elegibilidade_da_convocacao(convocacao, *, agora):
    """A convocação segue em curso? Lido dos seletores da `019`, sem reescrever regra (`D-003`).

    Espera a convocação com `desfechos`, `comunicacoes` e `sucessoras` pré-carregados.
    """
    from processo_seletivo.convocacao.application.selectors import desfecho_de, estado_de
    from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao

    if convocacao.sucessoras.all():
        return nomes.NAO_ELEGIVEL_SUCEDIDA
    if desfecho_de(convocacao) is not None:
        return nomes.NAO_ELEGIVEL_DESFECHO
    decorrido = nomes_da_convocacao.CONVOCADO_VENCIMENTO_DECORRIDO
    if estado_de(convocacao, agora=agora) == decorrido:
        return nomes.NAO_ELEGIVEL_VENCIDA
    return nomes.ELEGIVEL


def universo_do_reenvio(anterior, *, motivo, agora):
    """O universo do aviso filho: os destinatários do anterior no estado que o motivo alcança.

    **O ato citado é o do anterior**, e não o vigente de hoje: reenviar é terminar de entregar, ou
    mandar de novo, o aviso daquele ato (`R-011`). O endereço é relido, porque a pessoa pode ter
    corrigido a credencial desde a falha; e, na chamada, a elegibilidade também — avisar "você está
    entre as convocadas" a quem desistiu depois do primeiro aviso induziria ao erro que a `D-003`
    existe para evitar.
    """
    from processo_seletivo.avisos.application.selectors import estados_do_aviso
    from processo_seletivo.convocacao.models import Convocacao

    alcance = nomes.ALCANCE_DO_REENVIO[motivo]
    escolhidos = [
        destinatario
        for destinatario, estado, _ in estados_do_aviso(anterior, agora=agora)
        if estado in alcance
    ]
    enderecos = enderecos_das_inscricoes(d.inscricao for d in escolhidos)
    convocacoes = {}
    if anterior.origem == nomes.CHAMADA:
        convocacoes = {
            c.id: c
            for c in Convocacao.objects.filter(
                id__in=[d.convocacao_id for d in escolhidos if d.convocacao_id]
            ).prefetch_related("desfechos", "comunicacoes", "sucessoras")
        }
    linhas = []
    for destinatario in escolhidos:
        convocacao = convocacoes.get(destinatario.convocacao_id)
        elegibilidade = (
            elegibilidade_da_convocacao(convocacao, agora=agora)
            if convocacao is not None
            else nomes.ELEGIVEL
        )
        linhas.append(
            Linha(
                destinatario.inscricao,
                elegibilidade,
                enderecos.get(destinatario.inscricao_id, ""),
                convocacao=convocacao,
            )
        )
    publicacoes = [
        item.publicacao
        for item in anterior.publicacoes.select_related("publicacao__publicacao_anterior")
    ]
    if publicacoes:
        cabecalho = cabecalho_de(publicacoes[0])
        data = max(p.publicado_em for p in publicacoes)
    else:
        cabecalho = _cabecalho_da_chamada(anterior, convocacoes)
        enviadas = _comunicacoes_da_referencia(
            edital=anterior.edital,
            marco_id=anterior.marco_id,
            lista_id=anterior.lista_id,
            referencia=anterior.referencia_da_publicacao,
        ).values_list("enviado_em", flat=True)
        data = max(enviadas, default=None)
    return Universo(
        origem=anterior.origem,
        edital=anterior.edital,
        perfil_id=anterior.perfil_id,
        marco_id=anterior.marco_id,
        lista_id=anterior.lista_id,
        natureza=anterior.natureza,
        referencia=anterior.referencia_da_publicacao,
        publicacoes=publicacoes,
        linhas=linhas,
        cabecalho=cabecalho,
        datas_retificadas=[
            p.publicacao_anterior.publicado_em for p in publicacoes if p.publicacao_anterior_id
        ],
        data_da_publicacao=data,
        ja_avisado=True,
    )


def _cabecalho_da_chamada(anterior, convocacoes):
    from processo_seletivo.classificacao.domain.nomes import edital_por_extenso
    from processo_seletivo.convocacao.models import Convocacao

    convocacao = next(iter(convocacoes.values()), None) or (
        Convocacao.objects.filter(avisos__aviso=anterior).select_related("versao").first()
    )
    conteudo = (convocacao.versao.content or {}) if convocacao is not None else {}
    perfil = _perfil_da_versao(convocacao) if convocacao is not None else None
    return {
        "processo": anterior.edital.processo.title,
        "edital": edital_por_extenso(conteudo, anterior.edital),
        "perfil": (perfil or {}).get("name", "") or "",
    }


def _perfil_da_versao(convocacao):
    from processo_seletivo.classificacao.domain.universo import por_identidade

    return por_identidade((convocacao.versao.content or {}).get("profiles"), convocacao.perfil_id)


def _chamada_ja_avisada(edital, marco_id, lista_id, referencia):
    from processo_seletivo.avisos.models import Aviso

    return Aviso.objects.filter(
        edital=edital,
        origem=nomes.CHAMADA,
        marco_id=marco_id,
        lista_id=lista_id,
        referencia_da_publicacao=referencia,
        motivo=nomes.PRIMEIRO_AVISO,
    ).exists()


__all__ = [
    "Linha",
    "elegibilidade_da_convocacao",
    "universo_do_reenvio",
    "Universo",
    "cabecalho_de",
    "ja_avisadas",
    "naturezas_pendentes",
    "universo_da_chamada",
    "universo_do_resultado",
    "vigentes_da_natureza",
]
