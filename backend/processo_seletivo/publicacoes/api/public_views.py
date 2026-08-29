"""Endpoints de consulta pública: acesso anônimo, somente leitura, sem dados de elaboração."""

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
