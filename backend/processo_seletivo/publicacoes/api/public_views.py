"""Endpoints de consulta pública: acesso anônimo, somente leitura, sem dados de elaboração."""

import re
import unicodedata

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.editais.models.anexos import AnexoEdital, ArtefatoAnexo
from processo_seletivo.publicacoes.api.public_serializers import (
    PublicacaoDetalheSerializer,
    RetificacaoPublicaSerializer,
    VersaoConsolidadaSerializer,
    serialize_history,
)
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError

IMMUTABLE_CACHE = "public, max-age=31536000, immutable"
REVALIDATING_CACHE = "public, max-age=60"


class PublicView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def cached(self, payload, *, etag, cache_control):
        """Devolve 304 quando o cliente já tem a mesma representação."""
        if etag and self.request.headers.get("If-None-Match") == etag:
            response = Response(status=304)
        else:
            response = Response(payload)
        if etag:
            response["ETag"] = etag
        response["Cache-Control"] = cache_control
        return response


class ArtefatoPublicoView(PublicView):
    """Os bytes de um artefato que alguma versão publicada referencia (020, FR-039, FR-041).

    **O endereço é o do artefato, e não o do par publicação-anexo**, e isso é o que faz D-011 valer
    por construção: o artefato é imutável, então este endereço nunca resolve "o vigente" — ele
    resolve o de então porque não há outro que ele pudesse resolver. Qual artefato pertence a qual
    versão é o conteúdo canônico que diz, e ele já é histórico (R-003).

    **`congelado_em` é a autorização.** Artefato não congelado é rascunho de Edital não publicado, e
    responde 404 — não 403: dizer "existe, mas não é público" já entregaria que existe, que é a
    mesma régua de `exigir_titularidade` na `009` (FR-017).

    **O nome do arquivo entregue vem do rótulo do Anexo**, e não do nome físico que quem elaborou
    enviou. Quem baixa doze anexos ficava com doze arquivos cujo nome dependia de como o autor tinha
    salvo o dele — `autodeclaracao.pdf`, `Anexo I revisado FINAL (2).pdf`. O rótulo é a identidade
    institucional, e é ele que faz sentido na pasta de quem baixou.

    A rota conhece o artefato, e o mesmo artefato pode servir a anexos de rótulos diferentes: o
    rótulo usado é o da versão **vigente** que o publica, e o `nome_original` continua sendo o
    recurso quando nenhuma versão o cita por rótulo. A FR-014 continua valendo — o nome enviado não
    decide identidade nem endereço, e aqui ele nem decide mais o nome entregue.
    """

    def get(self, request, artefato_id):
        try:
            artefato = ArtefatoAnexo.objects.get(pk=artefato_id, congelado_em__isnull=False)
        except (ArtefatoAnexo.DoesNotExist, ValidationError) as exc:
            raise DomainError("not_found", "Recurso não encontrado.", 404) from exc
        etag = f'"{artefato.document_hash}"'
        if request.headers.get("If-None-Match") == etag:
            resposta = HttpResponse(status=304)
        else:
            resposta = HttpResponse(bytes(artefato.bytes), content_type=artefato.content_type)
            resposta["Content-Disposition"] = f'attachment; filename="{_nome_do_arquivo(artefato)}"'
        resposta["ETag"] = etag
        resposta["Cache-Control"] = IMMUTABLE_CACHE
        return resposta


def _nome_do_arquivo(artefato):
    """`ANEXO I — AUTODECLARAÇÃO ÉTNICO-RACIAL` vira `ANEXO-I-AUTODECLARACAO-ETNICO-RACIAL.pdf`.

    Sem acento e sem espaço porque o nome atravessa sistemas de arquivo, cliente de e-mail e
    cabeçalho HTTP, e um deles sempre estraga o que o outro aceitava. O que se preserva é o que
    identifica: a designação e o título que o Edital usa.
    """
    rotulo = (
        AnexoEdital.objects.filter(artefato=artefato)
        .exclude(rotulo="")
        .values_list("rotulo", flat=True)
        .first()
    )
    base = rotulo or artefato.nome_original.rsplit(".", 1)[0]
    sem_acento = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    limpo = "-".join(parte for parte in re.split(r"[^A-Za-z0-9]+", sem_acento) if parte)
    return f"{limpo[:120]}.pdf" if limpo else f"{artefato.id}.pdf"


def _instant(request):
    """Instante consultado, ou None para agora.

    Sem fuso declarado não há instante, há uma leitura de relógio de parede: `2026-03-01T10:00`
    significa momentos diferentes conforme quem lê. Assumir o fuso do servidor faria a mesma
    consulta devolver versões normativas distintas conforme onde o processo roda — e a FR-030
    exige que o passado seja reproduzível. O contrato já declara `format: date-time`, que é
    RFC 3339 e exige o deslocamento; aqui isso passa a ser fiscalizado.
    """
    raw = request.query_params.get("em")
    if raw in (None, ""):
        return None
    moment = parse_datetime(raw)
    if moment is None:
        raise DomainError("invalid_instant", "O parâmetro 'em' deve ser ISO-8601.", 400)
    if timezone.is_naive(moment):
        raise DomainError(
            "invalid_instant",
            "O parâmetro 'em' deve declarar o fuso horário, como em "
            "'2026-03-01T10:00:00-03:00'. Sem ele não há instante determinado.",
            400,
        )
    return moment


class EffectiveVersionView(PublicView):
    def get(self, request, edital_id):
        version = selectors.effective_version(edital_id=edital_id, at=_instant(request))
        return self.cached(
            VersaoConsolidadaSerializer(version).data,
            etag=f'"{version.content_hash}"',
            cache_control=REVALIDATING_CACHE,
        )


class ConsolidatedVersionView(PublicView):
    def get(self, request, versao_id):
        version = selectors.consolidated_version(versao_id=versao_id)
        return self.cached(
            VersaoConsolidadaSerializer(version).data,
            etag=f'"{version.content_hash}"',
            cache_control=IMMUTABLE_CACHE,
        )


class PublicPublicationView(PublicView):
    def get(self, request, publicacao_id):
        publicacao = selectors.published_publication(publicacao_id=publicacao_id)
        return self.cached(
            PublicacaoDetalheSerializer(publicacao).data,
            etag=f'"{publicacao.content_hash}"',
            cache_control=IMMUTABLE_CACHE,
        )


class PublicRetificationView(PublicView):
    def get(self, request, retificacao_id):
        retificacao = selectors.published_retification(retificacao_id=retificacao_id)
        return self.cached(
            RetificacaoPublicaSerializer(retificacao).data,
            etag=f'"{retificacao.publication.content_hash}"',
            cache_control=IMMUTABLE_CACHE,
        )


class PublicHistoryView(PublicView):
    def get(self, request, edital_id):
        entries, next_cursor = selectors.public_history(
            edital_id=edital_id,
            cursor=request.query_params.get("cursor"),
            limit=selectors.parse_limit(request.query_params.get("limit")),
        )
        response = Response({"items": serialize_history(entries), "nextCursor": next_cursor})
        response["Cache-Control"] = REVALIDATING_CACHE
        return response
