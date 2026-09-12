"""A relação e o seu resumo, em JSON, no canal público e sem autenticação (021, FR-011).

**Mesma projeção da página, e não outra.** O conteúdo devolvido aqui é exatamente o conteúdo
canônico cujo `canonical_sha256` **é** o resumo publicado: quem baixa este JSON recalcula o número
sem intermediário e sem precisar raspar HTML. Uma segunda projeção — mais rica "porque é API" —
faria o resumo deixar de fechar, e a promessa da feature morreria numa conveniência.

`immutable` no cache porque a relação publicada é imutável por construção: o endereço é o da
identidade, e a identidade não muda de conteúdo.
"""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from processo_seletivo.sorteios.application.selectors import relacao_publica
from processo_seletivo.sorteios.domain import projecao

IMMUTABLE_CACHE = "public, max-age=31536000, immutable"


class RelacaoPublicaView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, relacao_id):
        relacao = relacao_publica(relacao_id)
        if relacao is None:
            from django.http import Http404

            raise Http404
        participantes = [
            (p.numero_publico, p.inscricao)
            for p in relacao.participantes.select_related("inscricao").order_by("numero_publico")
        ]
        conteudo = projecao.conteudo_canonico(
            relacao_id=relacao.id,
            edital_id=relacao.edital_id,
            versao_id=relacao.versao_id,
            perfil_id=relacao.perfil_id,
            marco_id=relacao.marco_id,
            lista_id=relacao.lista_id,
            metodo_hash=relacao.metodo_hash,
            criterio_publicado=relacao.criterio_de_projecao,
            participantes=participantes,
        )
        etag = f'"{relacao.resumo}"'
        if request.headers.get("If-None-Match") == etag:
            resposta = Response(status=304)
        else:
            resposta = Response(
                {
                    **conteudo,
                    # Publicado ao lado do conteúdo, e não em vez dele: o leitor confere que o
                    # resumo que recebeu é o do conteúdo que recebeu.
                    "relationHash": relacao.resumo,
                    "publishedAt": relacao.publicada_em.isoformat(),
                    "count": relacao.quantidade,
                    "supersededBy": (
                        str(relacao.sucessoras.first().id) if relacao.sucessoras.all() else None
                    ),
                }
            )
        resposta["ETag"] = etag
        resposta["Cache-Control"] = IMMUTABLE_CACHE
        return resposta
