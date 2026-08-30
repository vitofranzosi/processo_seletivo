import re
import uuid

# Imprimível ASCII e no tamanho da coluna `RegistroAuditoria.correlation_id`. O valor é gravado
# na auditoria e ecoado num cabeçalho de resposta: sem limite, o excesso estoura no PostgreSQL
# como erro interno, e uma quebra de linha viraria `BadHeaderError` na resposta.
ACEITAVEL = re.compile(r"[\x20-\x7e]{1,100}\Z")


class CorrelationIdMiddleware:
    header = "HTTP_X_CORRELATION_ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = self.identificador(request.META.get(self.header))
        response = self.get_response(request)
        response["X-Correlation-ID"] = request.correlation_id
        return response

    def identificador(self, declarado):
        """O declarado quando é utilizável; um novo quando não.

        Recusar a requisição inteira por causa de um cabeçalho de diagnóstico seria
        desproporcional — ele é opcional. Substituir em silêncio também não é: a resposta sempre
        ecoa `X-Correlation-ID`, então o cliente que enviou um valor inutilizável vê de volta um
        diferente e descobre que a correlação dele não vale.
        """
        if declarado and ACEITAVEL.fullmatch(declarado):
            return declarado
        return str(uuid.uuid4())
