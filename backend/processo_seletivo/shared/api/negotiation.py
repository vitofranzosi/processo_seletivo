"""Negociação de conteúdo que sempre entrega o tipo declarado no contrato.

A API serve exclusivamente `application/json`. Sem isto, um navegador — que pede
`text/html` — receberia `406`, status que o contrato não declara, numa consulta pública
que precisa ser aberta por qualquer cidadão. Entregar JSON é mais útil e mais fiel ao
contrato do que recusar.
"""

from rest_framework.negotiation import DefaultContentNegotiation


class JsonAlwaysNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix=None):
        try:
            return super().select_renderer(request, renderers, format_suffix)
        except Exception:  # noqa: BLE001 — NotAcceptable e afins caem no renderer único
            renderer = renderers[0]
            return renderer, renderer.media_type
