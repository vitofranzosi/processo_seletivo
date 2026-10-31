"""A consulta: lê do banco o que a resposta pode usar, e nada além (070, `R-003`, `R-017`, `R-019`).

**Uma função sem requisição** (`FR-1448`). Recebe valores e devolve a resposta; não toca sessão,
`request` nem configuração de tela. É a porta pela qual a Fase B poderá chamar a mesma consulta de
outro processo — isolada, com a inferência, da capacidade que serve as páginas públicas — sem
refatorar nada. Nenhuma chave de configuração, nenhum cache, nenhuma rota além da tela da gestão.

**Só lê o publicado** (`FR-1412`). A versão consolidada vigente no instante, as futuras já
publicadas, as publicações que elas aplicam, a proveniência, o desfecho e o canal da implantação.
Nunca o rascunho, nunca Retificação não publicada, nunca as tabelas de elaboração — que depois da
publicação guardam o estado do dia dela, e não o vigente —, nunca dado de candidato. Nunca os bytes
de documento ou de anexo.

**Um número fixo de consultas** (`R-019`): o Edital; a versão vigente e a proveniência dela; as
versões futuras; as publicações aplicadas. E, só quando há o que ler: a proveniência das futuras, a
versão anterior informada e o ato do desfecho. O número não cresce com Perfis, documentos ou
Retificações.
"""

from __future__ import annotations

import json

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.duvidas.domain import respostas, revisao
from processo_seletivo.duvidas.domain.estruturas import (
    ORIGINAL,
    RETIFICACAO,
    AtoPublicado,
    Contexto,
    Desfecho,
    VersaoConsultada,
    VersaoFutura,
)
from processo_seletivo.duvidas.domain.origem import acrescimos, colecoes_acrescidas
from processo_seletivo.processos.application.selectors import desfechos
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    ProvenienciaConteudo,
    VersaoConsolidada,
)
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import identificacao

#: O que a resposta lê das versões futuras. `canonical_content` são os mesmos dados em bytes. A
#: vigente vem inteira de `effective_version`, que é a leitura de todas as telas.
CAMPOS_DA_VERSAO = (
    "id",
    "edital_id",
    "valid_from",
    "materialized_at",
    "content",
    "content_hash",
    "applied_publications",
    "source_publication_id",
)


class SemVersaoVigente(Exception):
    """O Edital não tinha versão publicada vigente no instante (`FR-1413`)."""


def _atos(publicacoes_por_id, identificadores, original):
    """A original e os atos aplicados, na ordem de aplicação — `(effective_at, publication_order)`.

    **A original entra sempre, e primeiro.** A versão materializada por uma Retificação guarda em
    `applied_publications` só as Retificações (`_materialize_affected_versions`); a versão da
    publicação original guarda a original. Lida sem ela, a regra "sem registro de proveniência,
    vale a original" (`R-004`) cairia na primeira Retificação — e o cartão de um valor que nunca
    mudou levaria ao documento errado. Achado na verificação pelo navegador, em 12/10.
    """
    atos = [
        publicacoes_por_id[str(identificador)]
        for identificador in identificadores
        if str(identificador) in publicacoes_por_id and str(identificador) != original
    ]
    em_ordem = sorted(atos, key=lambda ato: (ato.vigente_desde, ato.ordem))
    return tuple(
        ([publicacoes_por_id[original]] if original in publicacoes_por_id else []) + em_ordem
    )


def _ato(publicacao, original) -> AtoPublicado:
    retificacao = getattr(publicacao, "retificacao", None)
    if retificacao is None:
        ato, contem = ORIGINAL, (str(publicacao.id),)
    else:
        # **O documento da Retificação contém a original, a base dela e ela** (`R-005`), e não o
        # vigente: é a diferença que o achado de 12/10 reproduziu. A original vem à parte porque a
        # base materializada por Retificação não a lista.
        base = [str(item) for item in retificacao.base_snapshot.applied_publications or []]
        anteriores = [original] + [item for item in base if item != original]
        ato, contem = RETIFICACAO, (*anteriores, str(publicacao.id))
    return AtoPublicado(
        publicacao_id=str(publicacao.id),
        ato=ato,
        ordem=publicacao.publication_order,
        publicado_em=publicacao.published_at,
        vigente_desde=publicacao.effective_at,
        documento=reverse("public-document", args=[publicacao.id]),
        contem=contem,
    )


def _publicacoes(edital_id, identificadores, *, com_conteudo=False):
    """As publicações citadas e a original do Edital, numa consulta só (`R-019`).

    Com `com_conteudo`, também o conteúdo de cada ato — só quando alguma Retificação acrescentou a
    uma coleção (ver `origem.acrescimos`). Devolve `(atos por id, original, conteúdos por id)`.
    """
    campos = [
        "id",
        "publication_order",
        "published_at",
        "effective_at",
        "retificacao__id",
        "retificacao__base_snapshot__id",
        "retificacao__base_snapshot__applied_publications",
    ]
    if com_conteudo:
        campos.append("canonical_content")
    consulta = (
        Publicacao.objects.filter(
            Q(pk__in=identificadores) | Q(edital_id=edital_id, retificacao__isnull=True)
        )
        .select_related("retificacao__base_snapshot")
        .only(*campos)
    )
    linhas = list(consulta)
    original = next(
        (str(linha.id) for linha in linhas if getattr(linha, "retificacao", None) is None), ""
    )
    conteudos = (
        {str(linha.id): json.loads(bytes(linha.canonical_content)) for linha in linhas}
        if com_conteudo
        else {}
    )
    return {str(linha.id): _ato(linha, original) for linha in linhas}, original, conteudos


def _desfecho(edital, instante):
    """O desfecho que já havia ocorrido no instante (`R-006`).

    Sem data, vale só para o presente: dizê-lo num instante passado afirmaria um cancelamento que
    pode ser posterior. "Presente" é o minuto corrente, que é a precisão do campo da tela.
    """
    encontrado = desfechos([edital]).get(edital.id)
    if encontrado is None:
        return None
    if encontrado.em is not None and encontrado.em > instante:
        return None
    if encontrado.em is None and instante < timezone.now().replace(second=0, microsecond=0):
        return None
    return Desfecho(
        alcance=encontrado.alcance,
        operacao=encontrado.operacao,
        em=encontrado.em,
        do_edital=encontrado.do_edital,
    )


def contexto(*, edital_id, instante, versao_anterior=None) -> Contexto:
    """Tudo o que uma resposta deste Edital, neste instante, pode usar.

    Levanta `SemVersaoVigente` quando não havia publicação vigente no instante.
    """
    edital = (
        Edital.objects.select_related("processo")
        .annotate(canal_da_unidade=identificacao.canal_da_unidade_por_escopo())
        .get(pk=edital_id)
    )
    try:
        versao = effective_version(edital_id=edital_id, at=instante)
    except DomainError as erro:
        if erro.code == "no_effective_version":
            raise SemVersaoVigente from erro
        raise
    # **Só as já publicadas no instante** (`materialized_at`): numa consulta ao passado, uma
    # Retificação publicada depois tem vigência posterior ao instante e passaria por "futura já
    # publicada" — antecipando um ato que ainda não existia. Pela mesma razão, a fronteira
    # rematerializada depois do instante fica de fora, e vale a materialização conhecida nele.
    futuras_linhas = list(
        VersaoConsolidada.objects.filter(
            edital_id=edital_id, valid_from__gt=instante, materialized_at__lte=instante
        )
        .only(*CAMPOS_DA_VERSAO)
        .order_by("valid_from", "-materialized_at")
    )
    # A mais recente de cada fronteira: uma fronteira pode ter sido rematerializada.
    futuras_por_fronteira = {}
    for linha in futuras_linhas:
        futuras_por_fronteira.setdefault(linha.valid_from, linha)
    futuras_linhas = list(futuras_por_fronteira.values())
    proveniencias_futuras = {}
    if futuras_linhas:
        for registro in ProvenienciaConteudo.objects.filter(
            versao_id__in=[linha.id for linha in futuras_linhas]
        ).only("versao_id", "target_path", "publicacao_id"):
            proveniencias_futuras.setdefault(registro.versao_id, []).append(
                (registro.target_path, str(registro.publicacao_id))
            )

    proveniencias = tuple(
        sorted(
            (registro.target_path, str(registro.publicacao_id))
            for registro in versao.proveniencias.all()
        )
    )
    anteriores = ()
    if versao_anterior and str(versao_anterior) != str(versao.id):
        encontrada = (
            VersaoConsolidada.objects.filter(pk=versao_anterior, edital_id=edital_id)
            .values_list("applied_publications", flat=True)
            .first()
        )
        if encontrada is None:
            versao_anterior = None
        else:
            anteriores = tuple(str(item) for item in encontrada)

    identificadores = {str(item) for item in versao.applied_publications or []}
    identificadores.add(str(versao.source_publication_id))
    for linha in futuras_linhas:
        identificadores.update(str(item) for item in linha.applied_publications or [])
    identificadores.update(anteriores)
    acrescentou = colecoes_acrescidas(proveniencias) or any(
        colecoes_acrescidas(registros) for registros in proveniencias_futuras.values()
    )
    publicacoes, original_id, conteudos_dos_atos = _publicacoes(
        edital_id, identificadores, com_conteudo=acrescentou
    )

    atos = _atos(publicacoes, versao.applied_publications or [], original_id)
    proveniencias += acrescimos(proveniencias, versao.content, atos, conteudos_dos_atos)
    retificacoes = tuple(
        (ato.publicado_em, ato.vigente_desde) for ato in atos if ato.ato == RETIFICACAO
    )
    original = next((ato for ato in atos if ato.ato == ORIGINAL), atos[0] if atos else None)
    return Contexto(
        edital_id=str(edital.id),
        numero=str(edital.number),
        ano=edital.year,
        titulo=edital.title,
        instante=instante,
        versao=VersaoConsultada(
            id=str(versao.id),
            identificador_curto=versao.content_hash[:12],
            vigente_desde=versao.valid_from,
            publicada_em=original.publicado_em if original else versao.valid_from,
            retificacoes=retificacoes,
        ),
        conteudo=versao.content,
        atos=atos,
        proveniencias=proveniencias,
        fonte_da_versao=publicacoes.get(str(versao.source_publication_id)),
        futuras=tuple(
            _futura(linha, publicacoes, original_id, proveniencias_futuras, conteudos_dos_atos)
            for linha in futuras_linhas
        ),
        desfecho=_desfecho(edital, instante),
        # O da unidade do Edital, e o da instituição na falta (109, FR-3213). O do próprio Edital
        # continua primeiro: é o domínio que o acha no texto, e este é só o que vem depois dele.
        canal_institucional=edital.canal_da_unidade or identificacao.canal_institucional(),
        pagina_publica=reverse("portal:selecao", args=[edital.id]),
        anexos_publicos={
            str(anexo.get("artifactId")): reverse("public-anexo", args=[anexo.get("artifactId")])
            for anexo in versao.content.get("attachments") or []
            if anexo.get("artifactId")
        },
        versao_anterior=str(versao_anterior) if versao_anterior else None,
        # A versão anterior também aplicava a original, mesmo quando não a lista (ver `_atos`).
        atos_da_versao_anterior=_atos(publicacoes, anteriores, original_id) if anteriores else (),
    )


def _futura(linha, publicacoes, original_id, proveniencias_futuras, conteudos_dos_atos):
    atos = _atos(publicacoes, linha.applied_publications or [], original_id)
    proveniencias = tuple(sorted(proveniencias_futuras.get(linha.id, [])))
    return VersaoFutura(
        vigente_desde=linha.valid_from,
        conteudo=linha.content,
        atos=atos,
        proveniencias=proveniencias
        + acrescimos(proveniencias, linha.content, atos, conteudos_dos_atos),
    )


def consultar(*, edital_id, instante, pergunta, perfil=None, modalidade=None, versao_anterior=None):
    """A resposta à pergunta sugerida, toda ela da versão vigente no instante (`FR-1411`)."""
    lido = contexto(edital_id=edital_id, instante=instante, versao_anterior=versao_anterior)
    return respostas.responder(lido, pergunta, perfil=perfil, modalidade=modalidade)


def pontos_para_revisao(*, edital_id, instante):
    """Os pontos para revisão da versão vigente, derivados e não gravados (`FR-1443`, `FR-1444`)."""
    return revisao.pontos_para_revisao(contexto(edital_id=edital_id, instante=instante))
