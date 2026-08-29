"""Apresentação de valores do domínio. Nenhuma regra aqui — só como o dado é lido."""

from django import template

register = template.Library()

SITUACOES = {
    "EM_ELABORACAO": "Em elaboração",
    "EM_REVISAO": "Em revisão",
    "HOMOLOGADO": "Homologado",
    "PUBLICADO": "Publicado",
    "ENCERRADO": "Encerrado",
    "CANCELADO": "Cancelado",
    "ATIVO": "Ativo",
}


@register.filter
def situacao(valor):
    return SITUACOES.get(valor, valor)


@register.filter
def dicionario(dados, chave):
    """Lê `campo:<caminho>` do que foi enviado, para reexibir sem perder o digitado."""
    return dados.get(f"campo:{chave}", "") if dados else ""
