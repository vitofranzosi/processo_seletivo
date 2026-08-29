"""Apresentação de valores do domínio. Nenhuma regra aqui — só como o dado é lido."""

from django import template

register = template.Library()

# Edital e Processo usam a forma masculina; Retificação, a feminina. Sem as duas, a trilha
# de auditoria mistura "Em revisão → HOMOLOGADA" com o código cru na tela.
SITUACOES = {
    "EM_ELABORACAO": "Em elaboração",
    "EM_REVISAO": "Em revisão",
    "HOMOLOGADO": "Homologado",
    "HOMOLOGADA": "Homologada",
    "PUBLICADO": "Publicado",
    "PUBLICADA": "Publicada",
    "ENCERRADO": "Encerrado",
    "CANCELADO": "Cancelado",
    "CANCELADA": "Cancelada",
    "ATIVO": "Ativo",
}


@register.filter
def situacao(valor):
    return SITUACOES.get(valor, valor)


@register.filter
def dicionario(dados, chave):
    """Lê `campo:<caminho>` do que foi enviado, para reexibir sem perder o digitado."""
    return dados.get(f"campo:{chave}", "") if dados else ""


@register.filter
def plural(quantidade, formas):
    """Plural em português não se resolve com sufixo: Edital vira Editais, não Editalis."""
    singular, _, plural_ = str(formas).partition(",")
    return singular if quantidade == 1 else (plural_ or singular)
